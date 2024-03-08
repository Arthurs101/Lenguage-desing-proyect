from graphviz import Digraph
epsi = 'ε'

class AFNnodo:
    contador_estado = 0  # Variable estática para asignar nombres únicos a los estados
    def __init__(self):
        self.nombre = f'q{AFNnodo.contador_estado}'
        AFNnodo.contador_estado += 1
        self.transiciones = {}  # Diccionario de transiciones (entrada: conjunto de estados)
        self.isAceptacion = False

    def agregar_transicion(self, entrada, estado_destino):
        if entrada not in self.transiciones:
            self.transiciones[entrada] = set()
        self.transiciones[entrada].add(estado_destino)

def reset_contador():
    AFNnodo.contador_estado = 0
    
def createAFNF(nodo=None, father = None, isStart = False):
    estado_inicial = None
    estado_final = None
    
    if not nodo:
        return None, None  # Retorna None para ambos estados si el nodo es None

    if nodo.valor in ['*', '.', '|']:
        if nodo.valor == '|':
            if father:
                estado_inicial = father
            else:
                estado_inicial = AFNnodo()

            estado_inicial_izq, estado_final_izq = createAFNF(nodo.izquierda)
            estado_inicial_der, estado_final_der = createAFNF(nodo.derecha)
            
            estado_final = AFNnodo()
            if isStart:
                estado_final.isAceptacion = True

            estado_inicial.agregar_transicion(epsi, estado_inicial_izq)
            estado_inicial.agregar_transicion(epsi, estado_inicial_der)

            estado_final_izq.agregar_transicion(epsi, estado_final)
            estado_final_der.agregar_transicion(epsi, estado_final)

        
        elif nodo.valor == '*':

            if father:
                estado_inicial = father
            else:
                estado_inicial = AFNnodo()

            estado_intermedio_Inicial,estado_intermedio_Final = createAFNF(nodo.derecha,isStart)
            
            estado_final = AFNnodo()

            if isStart:
                estado_final.isAceptacion = True

            estado_inicial.agregar_transicion(epsi, estado_final)
            estado_inicial.agregar_transicion(epsi, estado_intermedio_Inicial)
            
            estado_intermedio_Final.agregar_transicion(epsi,estado_intermedio_Inicial)
            estado_intermedio_Final.agregar_transicion(epsi,estado_final)

        elif nodo.valor == '.':
            if father:
                iz_init, iz_end = createAFNF(nodo=nodo.izquierda,father=father,isStart=False)
            else:
                iz_init, iz_end = createAFNF(nodo=nodo.izquierda,isStart=False)
        
            d_init, d_end = createAFNF(nodo=nodo.derecha,father=iz_end,isStart=False)
            
            estado_inicial = iz_init
            estado_final = d_end

            if isStart:
                estado_final.isAceptacion = True
    else:
        if father:
            estado_inicial = father
        else:
            estado_inicial = AFNnodo()

        estado_final = AFNnodo()
        estado_inicial.agregar_transicion(nodo.valor,estado_final)

        if isStart:
            estado_final.isAceptacion = True

    return estado_inicial, estado_final

def renderAfn(estado_inicial,end):
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')  # Establecer la orientación horizontal
    visited = set()  # Crear un conjunto para llevar un registro de estados visitados
    dot.node('_start', shape='point')
    dot.edge('_start', estado_inicial.nombre)
    _renderAfn(dot, estado_inicial,visited,end)
    return dot

def _renderAfn(dot, estado , visited,end):
    if estado:
        if estado in visited:
            return

        visited.add(estado)

        if estado.nombre == end :
            dot.node(estado.nombre, label=estado.nombre, shape='doublecircle')
        else:
            dot.node(estado.nombre, label=estado.nombre, shape='circle')

        for entrada, destinos in estado.transiciones.items():
            for destino in destinos:
                dot.edge(estado.nombre, destino.nombre, label=entrada)

        for entrada, destinos in estado.transiciones.items():
            for destino in destinos:
                _renderAfn(dot, destino, visited,end)

def reconocer_cadena_afn(afn, alphabet , cadena):
    estados_actuales = [afn[0]]  # Estado inicial
    estados_actuales = _buscar_transiciones_epsilones([afn[0]])  # Estado inicial
    for simbolo in cadena:
        if simbolo in alphabet or simbolo == '':
            nuevos_estados = []
            for estado in estados_actuales:
                if simbolo in estado.transiciones:
                    nuevos_estados.extend(estado.transiciones[simbolo])
            estados_actuales = _buscar_transiciones_epsilones(nuevos_estados)
        else:
            print(f'AFN {simbolo} no válido para el lenguaje actual')

    for estado in estados_actuales:
        if estado.nombre == afn[1].nombre:
            return True

    return False



def reconocer_cadena(afd,alphabet ,cadena):
    estado_actual = afd  # Estado inicial
    for simbolo in cadena:
        if simbolo in alphabet:
            if simbolo in estado_actual.transiciones:
                estado_actual = estado_actual.transiciones[simbolo][0]
        else:
            print(f'{simbolo} no válido para el lenguaje actual')
            break
   
    if estado_actual.isAceptacion:
        return True

    return False

def _buscar_transiciones_epsilones(estados):
    nuevos_estados = estados.copy()
    visitados = set()  # Keep track of visited states to avoid infinite loops

    while nuevos_estados:
        estado = nuevos_estados.pop()
        if estado not in visitados:
            visitados.add(estado)
            if epsi in estado.transiciones:
                nuevos_estados.extend(estado.transiciones[epsi])

    return list(visitados)

#evaluar los strings
def evaluateString(language,estado_inicial, estado_final,afd,alphabet):
    string = input(f'''
se encuentra en el lenguaje conformado por
{language}
ingrese una cadena que desea evaluar.
para salir ingrese -1
''')
    string = str(string.rstrip())
    while(string != '-1'):
        isValid = reconocer_cadena_afn((estado_inicial, estado_final),alphabet,string)
        isValidAFD=reconocer_cadena(afd,alphabet,string)
        if isValid and isValidAFD:
            print('la cadena pertnece al lenguaje')
        else:
            if not isValid and not isValidAFD:
                print('la cadena no pertenece al lenguaje debido a ambas validaciones (AFN Y AFD)')
            elif not isValid:
                print('la cadena no pertenece al lenguaje debido a la validación del AFN')
            else:
                print('la cadena no pertenece al lenguaje debido a la validación del AFD')
        string = input(f'''
se encuentra en el lenguaje conformado por
{language}
ingrese una cadena que desea evaluar.
para salir ingrese -1
''')
        string = str(string.rstrip())







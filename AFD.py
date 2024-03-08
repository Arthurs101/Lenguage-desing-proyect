'''Implementacion para conversión a AFD a partir del AFN'''
from collections import deque
from AFN import AFNnodo
from AST import NodoAST
from graphviz import Digraph
import ast

epsi = 'ε'


#clase representatnte del nodo
class AFDNode:
    contador = 0
    def __init__(self, subset = set()):
        self.nombre = f's{AFDNode.contador}'
        self.transiciones = {}
        self.isAceptacion = False
        self.subset = subset
        AFDNode.contador += 1

    def agregar_transicion(self, simbolo, estado_destino):
        if simbolo in self.transiciones.keys():
            if estado_destino not in self.transiciones[simbolo]:    
                self.transiciones[simbolo].append(estado_destino)
        else:
            self.transiciones[simbolo] = [estado_destino]

'''metodo que recibe de input los estados finales e iniciales del AFN
    estado_inical, estado_final nodos AFN
    simbolos = simbolos del alfabeto para la gramatica
'''

class AFD(object):
    def __init__(self,root,alfabeto):
        self.root = root
        self.alfabeto = alfabeto
        self.header = self.root
    def step(self,char):
        is_valid = False
        is_transition = False
        if char in self.header.transiciones:
            self.header = self.header.transiciones[char][0]
            is_transition = True
        if self.header.isAceptacion:
            is_valid =  True
        return (False)
    def reset(self):
        self.header = self.root
        

'''obtenner la cerradura epsilon del estado s0'''

def afd_directo(nodo_ast:NodoAST):
    AFDNode.contador = 0
    followPosTable = NodoAST.followPos
    indexDict = NodoAST.posdict
    States = list() 
    acceptances = []
    #obtener el pos final
    for pos , _set in followPosTable.items():
        if len(_set) == 0:
            acceptances.append(pos)


    #crear el primer estado a partir del top en follow pos
    S0 = AFDNode(nodo_ast.firstPos)
    if NodoAST.index_pos in S0.subset:
        S0.isAceptacion = True
    States.append(S0)
    
    for D in States:
        #recorrer con cada symbolo
        for symbol , indexes in indexDict.items():
            U = set()
            _S = set(indexes)

            #obtener las pos mediante intersección de conjuntos
            occurences = D.subset & _S 
            if len(occurences) > 0:
                for pos in occurences:
                    #obtetenr todos los follow pos relacionados al simbolo
                    U = U.union(followPosTable[str(pos)])
                
                #verificar si existe
                if any(state.subset == U for state in States):
                    for state in States:
                        if state.subset == U:
                            if symbol != '#':
                                if '\\' in symbol:  # Si hay barras invertidas en el símbolo
                                    cleaned_symbol = symbol.replace('\\', '')  
                                    if cleaned_symbol and cleaned_symbol not in ['n', 't', 'w']: 
                                        D.agregar_transicion(cleaned_symbol, state)
                                    elif cleaned_symbol in ['n', 't', 'w']:
                                        D.agregar_transicion(f'\{cleaned_symbol}', state)
                                    elif not cleaned_symbol:  
                                        D.agregar_transicion(symbol[0], state)
                                else:  
                                    D.agregar_transicion(symbol, state)
                else:
                    #crear uno nuevo
                    _U = AFDNode(U)
                    if NodoAST.index_pos - 1 in U:
                        _U.isAceptacion = True
                    States.append(_U)
                    if symbol != '#':
                        if '\\' in symbol:
                            cleaned_symbol = symbol.replace('\\', '')  
                            if cleaned_symbol and cleaned_symbol not in ['n', 't', 'w']: 
                                D.agregar_transicion(symbol.replace('\\',''),_U)
                            elif cleaned_symbol in ['n', 't', 'w']:
                                D.agregar_transicion(f'\{cleaned_symbol}',_U)
                            elif not cleaned_symbol:
                                D.agregar_transicion(symbol[0],_U)
                        else:
                            D.agregar_transicion(symbol,_U)

    return S0

def ceraddura_e(S):
    e = set()
    for state in S:
        e = e.union(_cerradure_e(state))
    return e

def _cerradure_e(estado:AFNnodo,checked = None):
    if checked is None:
        checked = set()
    if estado in checked:
        return
    
    checked.add(estado)

    if epsi in estado.transiciones.keys():
        for next in estado.transiciones[epsi]:
            _cerradure_e(next,checked)
    
    return checked

def get_symbol_transitions(estados, simbolo):
    visited = set()
    #obtener los estados con el simbolo 
    for estado in estados:
        if simbolo in estado.transiciones.keys():
            visited = visited.union(estado.transiciones[simbolo])
    
    #aplicar cerradura lambda
    return visited
        
def get_simbolos(afn_node: AFNnodo,simbolos_entrada= set(), estados_visitados= []):
    if afn_node and afn_node.nombre not in estados_visitados:
        estados_visitados.append(afn_node.nombre)
        for simbolo in afn_node.transiciones:
            if simbolo != 'ε' and simbolo not in simbolos_entrada:  # Exclude epsilon transitions
                simbolos_entrada.add(simbolo)
            for estado in afn_node.transiciones[simbolo]:
                get_simbolos(estado,simbolos_entrada,estados_visitados)
    return simbolos_entrada

def convertir_afn_a_afd(afn_node_inicial, afn_node_final):
    AFDNode.contador = 0 #colocar el contador siempre en 0
    simbolos_entrada = get_simbolos(afn_node_inicial) 
    estados_afd = []
    accepted_afd = []
    s0 = ceraddura_e(set({afn_node_inicial}))
    S0 = AFDNode(s0)

    if any(node.nombre == afn_node_final.nombre for node in s0):
        S0.isAceptacion = True
    estados_afd.append(S0)
    
    for estado in estados_afd:
        for entrada in simbolos_entrada:
            subc = ceraddura_e(get_symbol_transitions(estado.subset, entrada))
            
            if any(set(estado_afd.subset) == set(subc) for estado_afd in estados_afd):
                for estado_afd in estados_afd:
                    if set(estado_afd.subset) == set(subc):
                        estado.agregar_transicion(entrada, estado_afd)
                        break
            else:
                if len(subc) > 0:
                    new_subc = AFDNode(subc)
                    estado.agregar_transicion(entrada, new_subc)
                    if any(node.nombre == afn_node_final.nombre for node in subc):
                        new_subc.isAceptacion = True
                        accepted_afd.append(new_subc)
                    estados_afd.append(new_subc)

    return {"root" : estados_afd[0] , "alfabeto" : simbolos_entrada,"estados":set(estados_afd),"acceptance":set(accepted_afd)}

def renderAfd(root):
    dot = Digraph(name="afd-direct",format="pdf")
    dot.attr(rankdir='LR')  # Establecer la orientación horizontal
    visited = set()  # Crear un conjunto para llevar un registro de estados visitados
    dot.node('_start', shape='point')
    dot.edge('_start', root.nombre,)
    _renderAfd(dot, root ,visited)
    return dot

def _renderAfd(dot, estado, visited):
    if estado:
        if estado in visited:
            return

        visited.add(estado)

        nombre_escapado = estado.nombre.replace('\\', '\\\\').replace('"', '\\"')
        if estado.isAceptacion:
            label = nombre_escapado if estado.nombre != '\\' else f"\\{nombre_escapado}"
            dot.node(estado.nombre, label=label, shape='doublecircle')
        else:
            label = nombre_escapado if estado.nombre != '\\' else f"\\{nombre_escapado}"
            dot.node(estado.nombre, label=label, shape='circle')

        for entrada, destinos in estado.transiciones.items():
            for dest in destinos:
                entrada_escapada = entrada.replace('\\', '\\\\').replace('"', '\\"')
                label_escapado = entrada_escapada if entrada_escapada != '\\' else f"\\{entrada_escapada}"
                dot.edge(estado.nombre, dest.nombre, label=label_escapado)

                # Renderizar los destinos recursivamente
                _renderAfd(dot, dest, visited)

def afd_min(afd:dict):
    #particiones iniciales
    #p0 : estados de aceptacion , p1: no aceptacion
    partitions = [afd["acceptance"],afd["estados"]-afd["acceptance"]]
    
    isNewpartition = True
    
    #REALIZAR PARTICIONES
    #realizar iteraciones en búsqueda de particion
    #detener si la nueva particion es igual a la inical
    while isNewpartition:
        next_partitions = [] #siguientes particiones 
        for partition in partitions:
            next_partition = {} #subgrupos de la siguiente iteracion
            for state in partition: #hallar transiciones de los estados por token
                state_transitions = []
                for token in afd["alfabeto"]:
                    token_transition = state.transiciones.get(token ,[]) #todos los estados que hay desde el token, si no existe, dar lista vacía
                    found_grupo = False
                    #ver a cual grupo pertenece cada estado de transicion
                    for s in partitions:
                        for token_s in token_transition:
                            if token_s in s:
                                found_grupo = True
                                state_transitions.append((token, tuple(s))) #añadir como tupla el token y estados de trancision hallados
                                #se halló el grupo de pertenencia
                                break
                        #se halló el grupo, no revisar los siguientes
                        if found_grupo:
                            break

                    #no existe el grupo  a trancisionar
                    if not found_grupo:
                        state_transitions.append((token, None))
                #convertir a tupla , donde si mismo es llave y valor, 
                #esto para las demás iteraciones poder accesarlo como si fuese llave el subconjunto
                state_transitions = tuple(state_transitions)
                #agregar el subconjunto
                next_partition.setdefault(state_transitions, set()).add(state)
            next_partitions.extend(next_partition.values()) #solo los valores ( el subconjunto es llave y valor)
        if next_partitions == partitions:
            break
        else:
            partitions = next_partitions
    
    #BUSCAR LAS TRANCISIONES PARA CADA ESTADO
    AFDNode.contador = 0

    state_transitions = {}

    min_states = []
    min_root = None
    for sub in partitions:
        sub_state = AFDNode(sub)
        
        #si alguno del subconjunto es aceptacion , todo el conjunto lo es
        if any(state.isAceptacion for state in sub):
            sub_state.isAceptacion = True

        #si el inicial está en el conjunto, el conjunto es el inicial
        if afd["root"] in sub:
            min_root = sub_state

        min_states.append(sub_state)
        
        #relacionar cada elemento con el nuevo
        for state in sub:
            state_transitions[state] = sub_state

    #recorrer cada nodo afd para relacionar los elementos de cada uno
    for state,min_state in state_transitions.items():
        #revisar cada transición 
        for token, destination in state.transiciones.items():
            for dest in destination:
                min_state.agregar_transicion(token,state_transitions[dest])

    return min_root

def reconocer_cadena(afd, cadena, rm= False):
    root = afd
    estado_actual = afd  # Estado inicial
    indice_ultimo_aceptado = -1
    indice_inicio = -1
    coincidences = []
    for indice, simbolo in enumerate(cadena):
        raw_test = simbolo.replace('\n', '\\n').replace('\t', '\\t')
        if  simbolo in estado_actual.transiciones:
            if estado_actual.nombre == root.nombre and indice_inicio == -1:
                indice_inicio = indice
            estado_actual = estado_actual.transiciones[simbolo][0]
            if estado_actual.isAceptacion:
                indice_ultimo_aceptado = indice
        elif  raw_test in estado_actual.transiciones.keys():
            if estado_actual.nombre == root.nombre and indice_inicio == -1:
                indice_inicio = indice
            estado_actual = estado_actual.transiciones[raw_test][0]
            if estado_actual.isAceptacion:
                indice_ultimo_aceptado = indice
        else:
            #reset not valid symbol
            if indice_inicio != -1 and indice_ultimo_aceptado != -1: #si realmente es válida la cadena reconocida de momento
                coincidences.append(cadena[indice_inicio:indice_ultimo_aceptado +1])
            indice_ultimo_aceptado = -1
            indice_inicio = -1
            estado_actual = afd


        # Detenerse si no hay más transiciones desde el estado actual
        if len(estado_actual.transiciones) == 0:
            if indice_inicio != -1 and indice_ultimo_aceptado != -1: #si realmente es válida la cadena
                coincidences.append(cadena[indice_inicio:indice_ultimo_aceptado +1])
                indice_ultimo_aceptado = -1
                indice_inicio = -1
            #reiniciar afd pues estaba en estado trampa
            estado_actual = afd
    if indice_inicio != -1 and indice_ultimo_aceptado != -1: #en caso de toda ser válida desde cierto punto y se agotó el for
        coincidences.append(cadena[indice_inicio:indice_ultimo_aceptado +1])
    if rm:
        for found in coincidences:
            cadena = cadena.replace(found, '')
        return coincidences, cadena
    return coincidences

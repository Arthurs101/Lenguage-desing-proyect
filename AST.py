from graphviz import Digraph
epsi = 'ε'

class NodoAST:
    index_pos = 1
    posdict = {}
    followPos = {}
    def __init__(self, valor):
        self.valor = valor
        self.izquierda = None
        self.derecha = None
        self.nullable = False
        self.firstPos = set()
        self.lastPos = set()
        self.index_pos = None
        
    def set_index_pos(self):
        self.index_pos = NodoAST.index_pos
        self.lastPos = set({self.index_pos})
        self.firstPos = set({self.index_pos})
        if self.valor not in NodoAST.posdict.keys():
            NodoAST.posdict[self.valor] = [NodoAST.index_pos]
        else:
            NodoAST.posdict[self.valor].append(NodoAST.index_pos)
        NodoAST.index_pos += 1

def obtener_alfabeto(nodo_ast):
    alfabeto = set()

    # Función auxiliar para recorrer el árbol recursivamente
    def recorrer_arbol(nodo):
        if nodo.valor not in {'*', '|', '.', '\\'} and nodo.valor not in alfabeto and nodo.valor != epsi:
            # Si es un nodo hoja y no es un operador especial como '*', '|', '.', '\\'
            alfabeto.add(nodo.valor)
        else:
            # Si no es un nodo hoja, seguir recorriendo los hijos
            if nodo.izquierda:
                recorrer_arbol(nodo.izquierda)
            if nodo.derecha:
                recorrer_arbol(nodo.derecha)

    # Comenzar el recorrido desde el nodo raíz
    recorrer_arbol(nodo_ast)

    return alfabeto

#prepare ast for direct construction
def evaluate_tree(root:NodoAST):
    alfabeto = obtener_alfabeto(root)
    def check_nullable(node:NodoAST): 
       if node.izquierda:
           check_nullable(node.izquierda)
       if node.derecha:
           check_nullable(node.derecha)

       #en caso de no tener hijos, ver si es un epsilon, pues es anulable
       if not node.izquierda and not node.derecha:
           if node.valor == epsi:
               node.nullable = True
       else:
         #revisar resto de operadores
            if node.valor == '|':
               node.nullable = node.derecha.nullable or node.izquierda.nullable
            elif node.valor == '*':
                node.nullable = True
            elif node.valor == '.':
                node.nullable = node.derecha.nullable and node.izquierda.nullable

    def set_pos(node:NodoAST,alfabeto):
        if node.izquierda:
           set_pos(node.izquierda,alfabeto)
        if node.derecha:
            set_pos(node.derecha,alfabeto)
        #check if is a valid pos node
        if not node.izquierda and not node.derecha:
           if node.valor != epsi and node.valor in alfabeto:
               node.set_index_pos()
        return 

    def handle_pos_sets(node:NodoAST):
        if node.izquierda:
            handle_pos_sets(node.izquierda)
        if node.derecha:
            handle_pos_sets(node.derecha)
        if node.valor == '|':
            node.firstPos = node.izquierda.firstPos.union(node.derecha.firstPos)
            node.lastPos = node.izquierda.lastPos.union(node.derecha.lastPos)
        elif node.valor == '.':
            ## firts pos
            if node.izquierda.nullable:
                node.firstPos = node.izquierda.firstPos.union(node.derecha.firstPos)
            else:
                node.firstPos = node.izquierda.firstPos
            #last pos:
            if node.derecha.nullable:
                node.lastPos = node.izquierda.lastPos.union(node.derecha.lastPos)
            else:
                node.lastPos = node.derecha.lastPos
        elif node.valor == '*':
            node.lastPos = node.derecha.lastPos
            node.firstPos = node.derecha.firstPos
        return

    def handle_followpos(node: NodoAST):
        def _examine(node:NodoAST,index):
            if node.derecha:
                _examine(node.derecha,index)
            if node.izquierda:
                _examine(node.izquierda,index)
            if node.valor in ['.','*']:
                if node.valor == '.':
                    #must have children c1, c2
                    if node.izquierda and node.derecha:
                        # si pos está en c1 last pos ,todos los first pos de c2 son follow
                        if index in node.izquierda.lastPos:
                           NodoAST.followPos[str(index)]= set.union(NodoAST.followPos[str(index)],node.derecha.firstPos)
                elif node.valor == '*':
                    #si index está en last pos, first pos son follow
                    if index in node.lastPos:
                        NodoAST.followPos[str(index)] = set.union(NodoAST.followPos[str(index)],node.firstPos)
            #terminar proceso
            return
        #create the key for each one:
        for key,item in NodoAST.posdict.items():
            for index in item:
                NodoAST.followPos[str(index)] = set()

        for key,item in NodoAST.posdict.items():
            for index in item:
                _examine(node,index)
    
    check_nullable(root)
    set_pos(root,alfabeto)
    handle_pos_sets(root)
    handle_followpos(root)
    return alfabeto

def construir_arbol_postfix(expresion) -> NodoAST:
    pila = []
    i = 0
    while i < len(expresion):
        caracter = expresion[i]
        if caracter in ['*', '+', '?', '.', '|']:
            nodo = NodoAST(caracter)
            nodo.derecha = pila.pop()
            if caracter != '*':
                nodo.izquierda = pila.pop()
            pila.append(nodo)
        else:
            if caracter == '\\':
                # Handle escape sequence
                if i + 1 < len(expresion):
                    i += 1  # Move to the next character
                    escape_sequence = caracter + expresion[i]
                    nodo = NodoAST(escape_sequence)
            else:
                nodo = NodoAST(caracter)
            pila.append(nodo)

        i += 1  # Move to the next character
    return pila[0] if pila else None

def graficar_pos(nodo):
    dot = Digraph(name="tree-pos",format='png')
    _graficar_pos(dot, nodo)
    dot.view() 
def _graficar_pos(dot,nodo):
    if nodo:
        firstPos= "{" + ','.join(str(pos) for pos in nodo.firstPos) + "}"
        lastPos = "{" + ','.join(str(pos) for pos in nodo.lastPos) + "}"
        both = "("+firstPos+","+lastPos+ ")"
        both = str(both)
        dot.node(str(id(nodo)), label=both)
        if nodo.izquierda:
            firstPos= "{" + ','.join(str(pos) for pos in nodo.izquierda.firstPos) + "}"
            lastPos = "{" + ','.join(str(pos) for pos in nodo.izquierda.lastPos) + "}"
            both = "("+firstPos+","+lastPos+ ")"
            both = str(both)
            dot.node(str(id(nodo.izquierda)), label=both)
            dot.edge(str(id(nodo)), str(id(nodo.izquierda)))
            _graficar_pos(dot, nodo.izquierda)
        if nodo.derecha:
            firstPos= "{" + ','.join(str(pos) for pos in nodo.derecha.firstPos) + "}"
            lastPos = "{" + ','.join(str(pos) for pos in nodo.derecha.lastPos) + "}"
            both = "("+firstPos+","+lastPos+ ")"
            both = str(both)
            dot.node(str(id(nodo.derecha)), label=both)
            dot.edge(str(id(nodo)), str(id(nodo.derecha)))
            _graficar_pos(dot, nodo.derecha)


# Función para mostrar el árbol utilizando Graphviz
def graficar_arbol(nodo):
    dot = Digraph(name="tree",format='pdf')
    _graficar_arbol(dot, nodo)
    dot.view()

def _graficar_arbol(dot, nodo):
    if nodo:
        nodo.firstPos = ' '.join(nodo.firstPos)
        nodo.lastPos = ' '.join(nodo.lastPos)
        dot.node(str(id(nodo)), label=nodo.valor)
        if nodo.izquierda:
            dot.node(str(id(nodo.izquierda)), label=nodo.izquierda.valor)
            dot.edge(str(id(nodo)), str(id(nodo.izquierda)))
            _graficar_arbol(dot, nodo.izquierda)
        if nodo.derecha:
            dot.node(str(id(nodo.derecha)), label=nodo.derecha.valor)
            dot.edge(str(id(nodo)), str(id(nodo.derecha)))
            _graficar_arbol(dot, nodo.derecha)


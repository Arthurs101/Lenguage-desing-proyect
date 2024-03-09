from AST import construir_arbol_postfix, graficar_arbol,evaluate_tree
from Posfix import PostFix
from AFD import afd_directo,reconocer_cadena,AFD
tokens = {}
content = ""
AFDs = {}
AFDl = ["Coment","Variable","Rules"]
with open("./PostfixData.txt",encoding="utf-8") as f:
    for i, line in enumerate(f):
        expresion_infix = line.strip()
        expresion_infix_direct = "(" + expresion_infix + ')#'
        #afd directo
        expresion_postfix_direct = PostFix(expresion_infix_direct)
        
        arbol_root_direct = construir_arbol_postfix(expresion_postfix_direct)
        # graficar_arbol(arbol_root_direct)
        alfabeto = evaluate_tree(arbol_root_direct)
        # graficar_pos(arbol_root_direct)
        afd_direct = afd_directo(arbol_root_direct)
        AFDs[AFDl[i]] = AFD(afd_direct,alfabeto)
# Función para tokenizar una entrada
def tokenizar(entrada, variables):
    # Ordenar las claves del diccionario por longitud, de mayor a menor
    sorted_variables = sorted(variables.keys(), key=len, reverse=True)
    
    # Tokenizar la entrada
    tokens = []
    while entrada:
        encontrado = False
        for variable in sorted_variables:
            if entrada.startswith(variable):
                tokens.append(variable)
                entrada = entrada[len(variable):]
                encontrado = True
                break
        if not encontrado:
            tokens.append(entrada[0])
            entrada = entrada[1:]
    return tokens

def generate_tree_from_yalex(filename):
    with open(filename,encoding="utf-8") as f:
        content = f.read().rstrip("\n")

    for name , afd in AFDs.items():
        #consume and remove the contents for the next afd
        tokens[name] , content  = reconocer_cadena(afd.root ,content,True) 
    
    variables = {}

    for var in tokens["Variable"]:
        id, statement = map(str.strip, var.split("="))
        id = id.split()[1]  # Siempre toma el segundo elemento después de dividir
        variables[id] = statement.strip().rstrip()
    for var in list(variables.keys()):
        _t = tokenizar(variables[var], variables)
        new_t = []
        for symbol in _t:
            if symbol in variables:
                new_t.extend(variables[symbol])
            else:
                new_t.append(symbol)
        variables[var] = new_t

    #Process the rules recursively
    statement_rules = tokens["Rules"][0].strip().rstrip().split('=', 1)[1].strip().rstrip().replace('\n','').split('|')
    rgx = []
    for rule in statement_rules:
        r = rule.strip().rstrip().split('{')
        rgx.append(r[0].strip().rstrip())
    for i in range(len(rgx)):
        if rgx[i] in variables:
            rgx[i] = variables[rgx[i]]
    for i in range(len(rgx)):
        gen = rgx[i]

    universe_set = [chr(i) for i in range(33,127)]
    universe_set.extend([' ',"\n","\t"])
    for item in rgx:
        statement_rule = ""
        if type(item) is list:
            op = ""
            hastostack = False
            stack = []
            i = 0
            while i < len(item):
                p = item[i]
                if p == "[":
                    stack.append(p)
                    hastostack = True
                elif p == "]":
                    op += "("
                    hastostack = False
                    operation = ""
                    while stack[-1]!='[':
                        operation+=stack.pop()
                    stack.pop()

                    if "-" in operation:
                        peers = []
                        for char in operation:
                            if char != '-':
                                peers.append(char)
                        #ir en parejas de los statments
                        for z in range(0,2,len(peers)):
                            if ord(peers[z])> ord(peers[z+1]):
                                for j in range(ord(peers[z+1]), ord(peers[z]) + 1):
                                    if j <=  ord(peers[z]) - 1:
                                        op += chr(j)+"|"
                                    else: 
                                        op += chr(j)
                            else:
                                for j in range(ord(peers[z]), ord(peers[z+1]) + 1):
                                    if j <=  ord(peers[z+1]) - 1:
                                        op += chr(j)+"|"
                                    else: 
                                        op += chr(j)
                    elif "^" in operation:
                        peers = []
                        range_to_ignonre =  []
                        if "-" in operation:
                            for char in operation:
                                if char != '-':
                                    peers.append(char)
                            #ir en parejas de los statments
                            for z in range(0,2,len(peers)):
                                if ord(peers[z])> ord(peers[z+1]):
                                    for j in range(ord(peers[z+1]), ord(peers[z]) + 1):
                                        if j <=  ord(peers[z]) - 1:
                                            range_to_ignonre.append(chr(j))
                                else:
                                    for j in range(ord(peers[z]), ord(peers[z+1]) + 1):
                                            range_to_ignonre.append(chr(j))
                        else:
                            operation.replace("~$_escaped_minus_here_$~",'-')
                            t = 0
                            while t < len(operation):
                                if operation[t] != '"':
                                    if operation[t] == '\\':
                                        range_to_ignonre.append(operation[t] + operation[t+1])
                                        t +=1
                                    else: range_to_ignonre.append(operation[t])
                            t += 1
                        #substact the as sets
                        regrex_C = set(universe_set) - set(range_to_ignonre)
                        regrex_C = list(regrex_C)
                        op+= '(' + '|'.join(regrex_C[:-1]) + '|' + regrex_C[-1] + ')'
                    else:
                        operation.replace("~$_escaped_minus_here_$~",'-')
                        t = 0
                        while t < len(operation):
                            if operation[t] != '"':
                                if operation[t] == '\\':
                                    op+= operation[t] + operation[t+1]
                                    t +=1
                                else: op+= operation[t]
                                if t <len(operation)-1 and operation[t+1] != '"':
                                    op+= "|"
                            t += 1
                    op += ")"
                else:
                    if p == "'": #buscar el cierre del index
                        c = ""
                        if (i +1 ) < len(item):
                            next = i +1
                            while next < len(item) and item[next] != "'":
                                c += item[next]
                                next += 1
                            if c in ['|','?','+','*','.','(',')']:
                                c = '\\' + c
                            elif c == '-':
                                c = "~$_escaped_minus_here_$~"
                            if hastostack:
                                stack.append(c)
                            else:
                                op += c
                            i += next - i
                    elif p == "\\": 
                        if (i +1 ) < len(item):
                            if hastostack:
                                stack.append(p+item[i+1]) 
                            else:
                                op += p+item[i+1]
                            i+=1
                    else: 
                        if p in ['.']:
                            p = '\\' + p
                        if p == '_': #universe option
                            special_chars = ['|', '?', '+', '*', '.', '(', ')','#']
                            result = ['\\' + char if char in special_chars or char != '' else char for char in universe_set]
                            p = "(" + '|'.join(result[:-1]) + '|' + result[-1] + ')'
                        if hastostack:
                            stack.append(p) 
                        else:
                            op += p
                i += 1
            if len(stack) > 0 :
                statement_rule += "".join(stack)
            statement_rule += op
        else:
            if "'" in item:
                if item.replace("'",'') in ['|','?','+','*','.','(',')']:
                    statement_rule += '\\' + item.replace("'",'')
                else:
                    statement_rule += item.replace("'",'')
            elif '"' in item:
                if item.replace('"','') in ['|','?','+','*','.','(',')']:
                    statement_rule += '\\' + item.replace('"','')
                else:
                    statement_rule += item.replace('"','')

    statement_rules[rgx.index(item)] = statement_rule
    rule_str_infix = '(' + "|".join(statement_rules) + ')' + '#'
    #afd directo
    infix_rule_tree_post = PostFix(rule_str_infix)
    arbol_root_direct = construir_arbol_postfix(infix_rule_tree_post)
    return arbol_root_direct

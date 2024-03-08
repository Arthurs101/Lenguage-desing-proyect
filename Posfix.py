def getPrecedence(c):
    if c=='(':
        return 1
    elif c=='|':
        return 2
    elif c=='.':
        return 3
    elif c=='?':
        return 4
    elif c=='*':
        return 4
    elif c=='+':
        return 4

def AmplifyExpression(regrex):
    regrex = regrex.replace('\+',"ESCPEDPLUS")
    regrex = regrex.replace('\?',"ESCPEDOPTIONAL")
    while '+' in regrex:
        index = regrex.index('+') #obtener posicion del operador 
        if regrex[index-1] != ')': #verificar que su antecesor no sea una expreiosn (..)
            regrex = regrex.replace(regrex[index-1] + '+', regrex[index-1] + regrex[index-1] + '*')  #reemplazar cualquier a+ por aa*
        elif regrex[index-1] == ')': #en caso sea una de cerradura , revisar el interior de la expresion
            interior = index -2
            _agrupacion = 0 # todas las agrupaciones de ((..))
            #lo siguiente se realiza hasta poder salir agrupacion por parentesis ((..))
            while (regrex[interior] != '(' or _agrupacion != 0)and interior>= 0: #siempre que no haya apertura o no hayan agrupaciones pendientes y no sea un negativo
                if regrex[interior] == ')':
                    _agrupacion += 1 #hay otra agrupacion dentro (..) pendiente
                elif  regrex[interior] == '(':
                    _agrupacion -= 1 #se cierra la agrupacion 
                interior -= 1
            if regrex[interior] == '(' and _agrupacion==0:#finalmente se está hasta afuera de las expresiones es decir hasta el () más externo
                expression = regrex[interior:index] #recuperar la expresion interna desde apertura hasta antes del cierre
                regrex = regrex.replace(expression + '+', expression + expression + '*')
    #el siguiente proceso realiza lo mismo solo que para ? reemplazandolo por a|ε
    while '?' in regrex:
        index = regrex.index('?') #obtener posicion del operador
        if regrex[index-1] != ')': #verificar que su antecesor no sea una apertura de ()
            regrex = regrex.replace(regrex[index-1] + '?',"("+ regrex[index-1] + '|ε)')  #reemplazar cualquier a? por (a|ε)
        elif regrex[index-1] == ')': #en caso sea una de cerradura , revisar el interior de la expresion
            interior = index -2
            _agrupacion = 0 # todas las agrupaciones de ((..))
            #lo siguiente se realiza hasta poder salir agrupacion por parentesis ((..))
            while (regrex[interior] != '(' or _agrupacion != 0)and interior>= 0: #siempre que no haya apertura o no hayan agrupaciones pendientes y no sea un negativo
                if regrex[interior] == ')':
                    _agrupacion += 1 #hay otra agrupacion dentro (..) pendiente
                elif  regrex[interior] == '(':
                    _agrupacion -= 1 #se cierra la agrupacion 
                interior -= 1
            if regrex[interior] == '(' and _agrupacion==0:#finalmente se está hasta afuera de las expresiones es decir hasta el () más externo
                expression = regrex[interior:index] #recuperar la expresion interna desde apertura hasta antes del cierre
                regrex = regrex.replace(expression + '?', '(' + expression + '|ε)')
    regrex = regrex.replace("ESCPEDPLUS",'\+')
    regrex = regrex.replace("ESCPEDOPTIONAL",'\?')
    return regrex

def formatRegEx(regex):
    regex = AmplifyExpression(regex) #realizar las respectivas conversiones a+ -> aa* y a? -> a | 𝜀
    allOperators = ['|','?','+','*']
    binaryOperators = ['|']
    res = ''
    i=0
    while i<len(regex):
        c1 = regex[i]
        if i+1<len(regex):
            c2 = regex[i+1]
            if c1=='\\':
                c1+=c2
                if i+2<len(regex):
                    c2 = regex[i+2]
                else:
                    c2 = ''
                i+=1
            elif c1=='[':
                j=i+1
                while j<len(regex) and regex[j]!=']':
                    c1+=regex[j]
                    j+=1
                c1+=regex[j]
                i=j
                if i+1<len(regex):
                    c2 = regex[i+1]
                else:
                    c2 = ''
            res+=c1
            if c2!='' and c1!='(' and c2!=')' and c2 not in allOperators and c1 not in binaryOperators:
                res+='.'
        else:
            res+=c1
        i+=1
    return res
def PostFix(expression):
    postfix = ''
    operators = ['|','?','+','*','.']
    stack = []
    formattedRegEx = formatRegEx(expression)
    i=0
    while i<len(formattedRegEx):
        c = formattedRegEx[i]
        if c=='\\':
            if i+1<len(formattedRegEx):
                if formattedRegEx[i+1] in operators or formattedRegEx[i+1]in ['\\','#','n', 't', 'w']:
                    postfix += c
                postfix+=formattedRegEx[i+1]
                i+=1
        elif c=='(':
            stack.append(c)
        elif c==')':
            while stack[-1]!='(':
                postfix+=stack.pop()
            stack.pop()
        elif c in operators:
            while len(stack)>0:
                peekedChar = stack[-1]
                peekedCharPrecedence = getPrecedence(peekedChar)
                currentCharPrecedence = getPrecedence(c)
                if peekedCharPrecedence>=currentCharPrecedence:
                    postfix+=stack.pop()
                else:
                    break
            stack.append(c)
        else:
            postfix+=c
        i+=1    
    while len(stack)>0:
        postfix+=stack.pop()
    return postfix
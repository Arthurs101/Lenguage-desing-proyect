import YalConstants as ylc
from AST import construir_arbol_postfix, graficar_arbol,obtener_alfabeto,evaluate_tree,graficar_pos
from Posfix import PostFix
from AFD import afd_directo,reconocer_cadena,AFD,renderAfd

yalfile = ""
with open("./slr-4.yal",encoding="utf-8") as f:
    yalfile = f.read().rstrip("\n")

#create automatas
commentAFD = afd_directo(evaluate_tree(construir_arbol_postfix(PostFix(ylc.comment))))

comments , yalfile = reconocer_cadena(commentAFD,yalfile,True)

print ('comments found')
for comment in comments:
    print (comment)
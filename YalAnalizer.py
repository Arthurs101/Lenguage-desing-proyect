import YalConstants as ylc
from AST import construir_arbol_postfix,evaluate_tree
from Posfix import PostFix
from AFD import afd_directo,reconocer_cadena

#create automatas
commentAFD = afd_directo(evaluate_tree(construir_arbol_postfix(PostFix(ylc.comment))))
# print(PostFix(ylc.let))
varAFD = afd_directo(evaluate_tree(construir_arbol_postfix(PostFix(ylc.let))))


def check_syntax(token_list, type_checking):
    '''Check syntax of all the obtained sections of a yalex file
    comment: check comment syntax
    variable: check variable syntax
    doesn't return anything but if it has bad syntax, it will raise an exception
    '''
    if type_checking == 'comment':
        for token in token_list:
            reconocer_cadena(commentAFD,token,True,error_handler=True)
    elif type_checking == 'variable':
        for token in token_list:
            reconocer_cadena(varAFD,token,True,error_handler=True)
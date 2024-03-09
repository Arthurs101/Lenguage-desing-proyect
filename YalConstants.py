import string

def exclude_chars(array, to_exclude):
    return [a for a in array if a not in to_exclude ]

punctuations = list(string.punctuation)
universe_set = [chr(i) for i in range(33,127)]
universe_set.extend([' ',"\n","\t"])
numeric_values = [chr(i) for i in range(48,58)]
letters = [chr(i) for i in range(97,124)] + [chr(i) for i in range(65,91)] + ['á','é','í','ó','ú','Á','É','Í','Ó','Ú']
#regrex used to analyze the sets
operators_extended = ['|','?','+','*','.','(',')','#']
regx_operators = ['|','?','+','*','.','#']

#estrucutra de comentarios
_c = [c if c not in regx_operators + ['\\'] else '\\' + c for c in letters + exclude_chars(punctuations, ['(', ')','*'])] + [' '] + numeric_values
comment = "\(\*(" + "(" + "|".join(_c[:-1]) + "|" + _c[-1] +")|'(\(|\)|\*)'"+ ")*\*\)"
comment = '(' + comment + ')' + '#'
import string

def exclude_chars(array, to_exclude):
    return [a for a in array if a not in to_exclude ]

punctuations = list(string.punctuation)
universe_set = [chr(i) for i in range(33,127)]
universe_set.extend([' ',"\n","\t"])
numeric_values = [chr(i) for i in range(48,58)]
letters = [chr(i) for i in range(97,123)] + [chr(i) for i in range(65,91)] + ['á','é','í','ó','ú','Á','É','Í','Ó','Ú']
#regrex used to analyze the sets
operators_extended = ['|','?','+','*','.','(',')','#']
regx_operators = ['|','?','+','*','#','.']

#estrucutra de comentarios
_c = [c if c not in regx_operators + ['\\'] else '\\' + c for c in letters + exclude_chars(punctuations, ['(', ')','*'])] + [' '] + numeric_values
comment = "\(\*(" + "(" + "|".join(_c[:-1]) + "|" + _c[-1] +")|'(\(|\)|\*)'"+ ")*\*\)"
comment = '(' + comment + ')' + '#'

#estructura de varaibles
let = "let( )+"
# identifier of variable, must be any letter only the first one
let += '(' +"|".join(letters[:-1]) +"|" + letters[-1] + ')'
#rest of toknes alphanumeric and underscore characters
let += '(' +"|".join(letters) +"|" +"|".join(numeric_values) + '|' + '_' ')*'
#spacing before the eq and after
let += '( )+=( )+'

#declaration of the values char structure '_c'
any_val_char= [c if c not in operators_extended + ['\\'] else '\\' + c for c in letters + exclude_chars(punctuations,["'"]) + [' ','\n','\t'] + numeric_values]
any_string_val =  [c if c not in operators_extended + ['\\'] else '\\' + c for c in letters + exclude_chars(punctuations,['"']) + [' ','\n','\t'] + numeric_values]
espacping_seq = "(\\\\(n|t))"
espacping_seq_char = "(\\\\(n|t|'))"
espacping_seq_str = '(\\\\(n|t|"))'

#declaration of a range using char -> [char-char]
singel_char = "('(" + "|".join(any_val_char)+ '|' + espacping_seq_char + ")')"
string_constant = f'("({"|".join(any_string_val)})+")'
range_chars = f"({singel_char}-{singel_char})+"
multiple_chars = f"({singel_char})+"

#identity_char
ident = '('
ident += '(' +"|".join(letters[:-1]) +"|" + letters[-1] + ')'
ident += '(' +"|".join(letters) +"|" +"|".join(numeric_values) + '|' + '_'+')*'
ident += ')'

#char sequences
rgx_sequence ='('
rgx_sequence += '\\['
rgx_sequence += "(^)?" #could be a negation of the simbol 
rgx_sequence += f"({range_chars}|{multiple_chars}|{string_constant})"
rgx_sequence += '\\]'
rgx_sequence += ')'


operatorr_sequence = '('+ "|".join(['\\' + c for c in regx_operators[:-1]])+ ')' #the dot is not operator for yalex
enclosed_regrex = f"(\((({rgx_sequence}|{ident}|{string_constant}|{singel_char}|_)({operatorr_sequence})?)+\)({operatorr_sequence})?)"
# left side of let could be a regx sequence,identity, string or char with operator at least once or a encapsulated rgx sequence
let += '('
let += f"(({rgx_sequence}|{ident}|{enclosed_regrex}|{string_constant}|{singel_char}|_)({operatorr_sequence})?)+({operatorr_sequence})?( )*(\\n)" #every declaration must be per line, must end in new line
let += ')'
#regrex declarations

let = '(' + let + ')' + '#'


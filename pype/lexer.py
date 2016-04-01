import ply.lex

reserved = {  # pattern : token-name
    'input': 'INPUT',
    'output': 'OUTPUT',
    'import': 'IMPORT'
}
# 'tokens' is a special word in ply's lexers.
tokens = [
    'LPAREN',
    'RPAREN',  # Individual parentheses
    'LBRACE',
    'RBRACE',  # Individual braces
    'OP_ADD',
    'OP_SUB',
    'OP_MUL',
    'OP_DIV',  # the four basic arithmetic symbols
    'STRING',  # Anything enclosed by double quotes
    'ASSIGN',  # The two characters :=
    'NUMBER',  # An arbitrary number of digits
    'ID'  # a sequence of letters, numbers, and underscores. Must not start with a number.
] + list(reserved.values())

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_OP_ADD = r'\+' 
t_OP_SUB = r'\-'
t_OP_MUL = r'\*'
t_OP_DIV = r'\/'
t_STRING = r'["].*["]'  # note: this matches "", which might not be desired behavior
t_ASSIGN = r'[:][=]'
t_NUMBER = r'[\-]?[0-9]'


def t_ID(t):
    r'[a-zA-Z_][0-9a-zA-Z_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Ignore whitespace.
t_ignore = r'[ ]+'

# Ignore comments. Comments in PyPE are just like in Python. Section 4.5.
def t_COMMENT(t):
    r'\#.*'
    pass  # comments are ignored

# Rule for newlines that track line numbers. Section 4.6.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error-handling routine. It should print both line and column numbers.
def t_error(t):
    col = find_column(t.lexer.lexdata, t)
    print("Error at line {}, column {}".format(t.lexer.lineno, col))
    t.lexer.skip(1)

# Column finder from PLY documentation
def find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr)
    return column

# This actually builds the lexer.
lexer = ply.lex.lex()  # take out the debug=True once it's working

# # Test it out
# data = '''
# 3 + 4 * 10
#   + -20 *2
#   input output import
#   _abc 9 9_abc &
# '''

# # Give the lexer some input
# lexer.input(data)

# # Tokenize
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(tok)
# for tok in lexer:
#     print(tok)

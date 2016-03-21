import ply.yacc

from .lexer import tokens, reserved
from .ast import *

# Here's an example production rule which constructs an AST node
def p_program(p):
    r'program : statement_list'
    p[0] = ASTProgram(p[1])

# Here's an example production rule which simply aggregates lists of AST nodes.
def p_statement_list(p):
    r'''statement_list : statement_list component
                       | statement_list import_statement
                       | import_statement
                       | component'''
    if len(p) > 2:
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_import_statement(p):
    r'import_statement : LPAREN IMPORT ID RPAREN'
    p[0] = ASTImport(p[3])

def p_component(p):
    r'''component : LBRACE ID expression_list RBRACE'''
    p[0] = ASTComponent(p[2], p[3])

def p_expression_list(p):
    r'''expression_list : expression_list expression
                      | expression'''
    expressions = []
    for expression in p[1]:
        p_expression(expression)  # DO I NEED TO DO THIS OR IS IT AUTOMATIC?
        expressions.append(expression)  # This should append ASTNodes from line ^
    p[0] = expressions

def p_input_expression(p):
    r'''expression : LPAREN INPUT declaration_list RPAREN
                 | LPAREN INPUT RPAREN'''
    if len(p) == 5:
        p[0] = ASTInputExpr(p[3])
    else:
        p[0] = ASTInputExpr([])

    # TODO
    r'''expression : LPAREN OUTPUT declaration_list RPAREN
                 | LPAREN OUTPUT RPAREN'''
    # TODO
    r'''declaration_list : declaration_list declaration
                       | declaration'''
    # TODO
    r'''declaration : LPAREN type ID RPAREN
                  | ID'''
    # TODO
    r'''type : ID'''
    # TODO
    r'''expression : LPAREN ASSIGN ID expression RPAREN'''
    # TODO
    r'''expression : LPAREN ID parameter_list RPAREN
                 | LPAREN ID RPAREN'''
    # TODO
    r'''expression : LPAREN OP_ADD parameter_list RPAREN'''
    # TODO
    r'''expression : LPAREN OP_SUB parameter_list RPAREN'''
    # TODO
    r'''expression : LPAREN OP_MUL parameter_list RPAREN'''
    # TODO
    r'''expression : LPAREN OP_DIV parameter_list RPAREN'''
    # TODO
    r'''expression : ID'''
    # TODO
    r'''expression : NUMBER'''
    # TODO
    r'''expression : STRING'''
    # TODO
    r'''parameter_list : parameter_list expression
                     | expression'''

# TODO: Write an error handling function. You should attempt to make the error
#       message sensible. For instance, print out the line and column numbers to
#       help find your error.
# NOTE: You do NOT need to write production rules with error tokens in them.
#       If you're interested, read section 6.8, but it requires a fairly deep
#       understanding of LR parsers and the language specification.


def p_error(p):
    pass


start = 'program'
parser = ply.yacc.yacc(debug=True)  # To get more information, add debug=True

import ply.yacc

from .lexer import tokens, reserved
from .ast import *


def p_program(p):
    r'program : statement_list'
    p[0] = ASTProgram(p[1])


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
    p[0] = ASTComponent(ASTID(p[2]), p[3])


def p_expression_list(p):
    r'''expression_list : expression_list expression
                      | expression'''
    if len(p) > 2:
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = [p[1]]


def p_input_expression(p):
    r'''expression : LPAREN INPUT declaration_list RPAREN
                 | LPAREN INPUT RPAREN'''
    if len(p) == 5:
        p[0] = ASTInputExpr(p[3])
    else:
        p[0] = ASTInputExpr([])


def p_output_expression(p):
    r'''expression : LPAREN OUTPUT declaration_list RPAREN
                 | LPAREN OUTPUT RPAREN'''
    if len(p) == 5:
        p[0] = ASTOutputExpr(p[3])
    else:
        p[0] = ASTOutputExpr([])


def p_declaration_list(p):
    r'''declaration_list : declaration_list declaration
                       | declaration'''
    if len(p) > 2:
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = [p[1]]


def p_declaration(p):
    r'''declaration : LPAREN type ID RPAREN
                  | ID'''
    if len(p) == 5:
        p[0] = ASTID(p[3], p[2])
    else:
        p[0] = ASTID(p[1])


def p_type(p):
    r'''type : ID'''
    p[0] = ASTID(p[1])


def p_assign_expression(p):
    r'''expression : LPAREN ASSIGN ID expression RPAREN'''
    p[0] = ASTAssignmentExpr(ASTID(p[3]), p[4])


def p_parameter_list_expression(p):
    r'''expression : LPAREN ID parameter_list RPAREN
                 | LPAREN ID RPAREN'''
    if len(p) == 4:
        p[0] = ASTEvalExpr(ASTID(p[2]))
    else:
        p[0] = ASTEvalExpr(ASTID(p[2]), p[3])


def p_op_add_expression(p):
    r'''expression : LPAREN OP_ADD parameter_list RPAREN'''
    p[0] = ASTEvalExpr(ASTID(name='__add__'), p[3])


def p_op_sub_expression(p):
    r'''expression : LPAREN OP_SUB parameter_list RPAREN'''
    p[0] = ASTEvalExpr(ASTID(name='__sub__'), p[3])


def p_op_mul_expression(p):
    r'''expression : LPAREN OP_MUL parameter_list RPAREN'''
    p[0] = ASTEvalExpr(ASTID(name='__mul__'), p[3])


def p_op_div_expression(p):
    r'''expression : LPAREN OP_DIV parameter_list RPAREN'''
    p[0] = ASTEvalExpr(ASTID(name='__truediv__'), p[3])


def p_id(p):
    r'''expression : ID'''
    p[0] = ASTID(p[1])


def p_number(p):
    r'''expression : NUMBER'''
    p[0] = ASTLiteral(p[1])


def p_string(p):
    r'''expression : STRING'''
    p[0] = ASTLiteral(p[1])


def p_parameter_list(p):
    r'''parameter_list : parameter_list expression
                     | expression'''
    if len(p) > 2:
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = [p[1]]


def p_error(p):
    print("Syntax error at line " + str(p.lineno) + ": " + p.value)
    quit()


start = 'program'
parser = ply.yacc.yacc(debug=True)  # To get more information, add debug=True

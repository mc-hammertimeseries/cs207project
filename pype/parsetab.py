
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = 'A4271323C5F0D308FC393DC2BBD9B0AA'
    
_lr_action_items = {'RPAREN':([12,13,15,17,20,22,25,29,30,31,32,34,35,36,37,38,39,40,41,42,44,45,48,49,50,51,52,53,54,55,56,57,58,],[-28,-27,-26,28,31,36,41,44,-17,-13,-15,-30,48,-21,50,51,52,53,-11,54,-12,-14,-22,-29,-20,-24,-23,-10,-25,57,58,-19,-16,]),'ASSIGN':([14,],[27,]),'STRING':([9,11,12,13,15,16,19,21,22,23,24,26,31,34,35,36,37,38,39,41,42,43,44,48,49,50,51,52,53,54,57,],[12,12,-28,-27,-26,-9,-8,12,12,12,12,12,-13,-30,12,-21,12,12,12,-11,12,12,-12,-22,-29,-20,-24,-23,-10,-25,-19,]),'IMPORT':([6,],[10,]),'OUTPUT':([14,],[20,]),'RBRACE':([11,12,13,15,16,19,31,36,41,44,48,50,51,52,53,54,57,],[18,-28,-27,-26,-9,-8,-13,-21,-11,-12,-22,-20,-24,-23,-10,-25,-19,]),'LBRACE':([0,1,3,4,7,8,18,28,],[5,-4,5,-5,-3,-2,-7,-6,]),'LPAREN':([0,1,3,4,7,8,9,11,12,13,15,16,18,19,20,21,22,23,24,25,26,28,29,30,31,32,34,35,36,37,38,39,40,41,42,43,44,45,48,49,50,51,52,53,54,57,58,],[6,-4,6,-5,-3,-2,14,14,-28,-27,-26,-9,-7,-8,33,14,14,14,14,33,14,-6,33,-17,-13,-15,-30,14,-21,14,14,14,33,-11,14,14,-12,-14,-22,-29,-20,-24,-23,-10,-25,-19,-16,]),'ID':([5,9,10,11,12,13,14,15,16,19,20,21,22,23,24,25,26,27,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,57,58,],[9,15,17,15,-28,-27,22,-26,-9,-8,30,15,15,15,15,30,15,43,30,-17,-13,-15,46,-30,15,-21,15,15,15,30,-11,15,15,-12,-14,-18,56,-22,-29,-20,-24,-23,-10,-25,-19,-16,]),'$end':([1,2,3,4,7,8,18,28,],[-4,0,-1,-5,-3,-2,-7,-6,]),'OP_ADD':([14,],[21,]),'OP_MUL':([14,],[23,]),'OP_SUB':([14,],[24,]),'NUMBER':([9,11,12,13,15,16,19,21,22,23,24,26,31,34,35,36,37,38,39,41,42,43,44,48,49,50,51,52,53,54,57,],[13,13,-28,-27,-26,-9,-8,13,13,13,13,13,-13,-30,13,-21,13,13,13,-11,13,13,-12,-22,-29,-20,-24,-23,-10,-25,-19,]),'OP_DIV':([14,],[26,]),'INPUT':([14,],[25,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'import_statement':([0,3,],[1,7,]),'declaration_list':([20,25,],[29,40,]),'expression':([9,11,21,22,23,24,26,35,37,38,39,42,43,],[16,19,34,34,34,34,34,49,49,49,49,49,55,]),'expression_list':([9,],[11,]),'program':([0,],[2,]),'statement_list':([0,],[3,]),'component':([0,3,],[4,8,]),'declaration':([20,25,29,40,],[32,32,45,45,]),'type':([33,],[47,]),'parameter_list':([21,22,23,24,26,],[35,37,38,39,42,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> statement_list','program',1,'p_program','parser.py',10),
  ('statement_list -> statement_list component','statement_list',2,'p_statement_list','parser.py',17),
  ('statement_list -> statement_list import_statement','statement_list',2,'p_statement_list','parser.py',18),
  ('statement_list -> import_statement','statement_list',1,'p_statement_list','parser.py',19),
  ('statement_list -> component','statement_list',1,'p_statement_list','parser.py',20),
  ('import_statement -> LPAREN IMPORT ID RPAREN','import_statement',4,'p_import_statement','parser.py',29),
  ('component -> LBRACE ID expression_list RBRACE','component',4,'p_component','parser.py',34),
  ('expression_list -> expression_list expression','expression_list',2,'p_expression_list','parser.py',39),
  ('expression_list -> expression','expression_list',1,'p_expression_list','parser.py',40),
  ('expression -> LPAREN INPUT declaration_list RPAREN','expression',4,'p_input_expression','parser.py',49),
  ('expression -> LPAREN INPUT RPAREN','expression',3,'p_input_expression','parser.py',50),
  ('expression -> LPAREN OUTPUT declaration_list RPAREN','expression',4,'p_output_expression','parser.py',58),
  ('expression -> LPAREN OUTPUT RPAREN','expression',3,'p_output_expression','parser.py',59),
  ('declaration_list -> declaration_list declaration','declaration_list',2,'p_declaration_list','parser.py',67),
  ('declaration_list -> declaration','declaration_list',1,'p_declaration_list','parser.py',68),
  ('declaration -> LPAREN type ID RPAREN','declaration',4,'p_declaration','parser.py',77),
  ('declaration -> ID','declaration',1,'p_declaration','parser.py',78),
  ('type -> ID','type',1,'p_type','parser.py',86),
  ('expression -> LPAREN ASSIGN ID expression RPAREN','expression',5,'p_assign_expression','parser.py',91),
  ('expression -> LPAREN ID parameter_list RPAREN','expression',4,'p_parameter_list_expression','parser.py',96),
  ('expression -> LPAREN ID RPAREN','expression',3,'p_parameter_list_expression','parser.py',97),
  ('expression -> LPAREN OP_ADD parameter_list RPAREN','expression',4,'p_op_add_expression','parser.py',105),
  ('expression -> LPAREN OP_SUB parameter_list RPAREN','expression',4,'p_op_sub_expression','parser.py',110),
  ('expression -> LPAREN OP_MUL parameter_list RPAREN','expression',4,'p_op_mul_expression','parser.py',115),
  ('expression -> LPAREN OP_DIV parameter_list RPAREN','expression',4,'p_op_div_expression','parser.py',120),
  ('expression -> ID','expression',1,'p_id','parser.py',125),
  ('expression -> NUMBER','expression',1,'p_number','parser.py',130),
  ('expression -> STRING','expression',1,'p_string','parser.py',135),
  ('parameter_list -> parameter_list expression','parameter_list',2,'p_parameter_list','parser.py',140),
  ('parameter_list -> expression','parameter_list',1,'p_parameter_list','parser.py',141),
]

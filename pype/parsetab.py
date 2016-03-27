
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = '8B184828847846774CD153CEF0204C26'
    
_lr_action_items = {'RPAREN':([11,12,16,17,23,26,27,30,31,32,33,34,35,36,37,38,39,40,42,43,44,45,46,47,48,49,50,51,52,55,56,57,58,],[-27,-26,-28,28,33,37,42,-30,45,47,-21,48,49,50,-11,-17,51,-15,-13,55,56,-23,-29,-24,-20,-25,-22,-10,-14,-12,-19,58,-16,]),'ASSIGN':([14,],[20,]),'$end':([1,2,3,5,7,8,18,28,],[0,-1,-5,-4,-2,-3,-7,-6,]),'OP_SUB':([14,],[21,]),'OP_MUL':([14,],[22,]),'ID':([4,9,10,11,12,13,14,15,16,19,20,21,22,23,24,25,26,27,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,45,46,47,48,49,50,51,52,53,54,55,56,58,],[9,12,17,-27,-26,12,23,-9,-28,-8,29,12,12,12,12,12,38,38,12,-30,12,12,-21,12,12,12,-11,-17,38,-15,53,-13,38,-23,-29,-24,-20,-25,-22,-10,-14,-18,57,-12,-19,-16,]),'RBRACE':([11,12,13,15,16,19,33,37,42,45,47,48,49,50,51,55,56,],[-27,-26,18,-9,-28,-8,-21,-11,-13,-23,-24,-20,-25,-22,-10,-12,-19,]),'LPAREN':([0,2,3,5,7,8,9,11,12,13,15,16,18,19,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,42,43,45,46,47,48,49,50,51,52,55,56,58,],[6,6,-5,-4,-2,-3,14,-27,-26,14,-9,-28,-7,-8,14,14,14,14,14,41,41,-6,14,-30,14,14,-21,14,14,14,-11,-17,41,-15,-13,41,-23,-29,-24,-20,-25,-22,-10,-14,-12,-19,-16,]),'NUMBER':([9,11,12,13,15,16,19,21,22,23,24,25,29,30,31,32,33,34,35,36,37,42,45,46,47,48,49,50,51,55,56,],[11,-27,-26,11,-9,-28,-8,11,11,11,11,11,11,-30,11,11,-21,11,11,11,-11,-13,-23,-29,-24,-20,-25,-22,-10,-12,-19,]),'OP_ADD':([14,],[25,]),'OP_DIV':([14,],[24,]),'LBRACE':([0,2,3,5,7,8,18,28,],[4,4,-5,-4,-2,-3,-7,-6,]),'INPUT':([14,],[26,]),'OUTPUT':([14,],[27,]),'IMPORT':([6,],[10,]),'STRING':([9,11,12,13,15,16,19,21,22,23,24,25,29,30,31,32,33,34,35,36,37,42,45,46,47,48,49,50,51,55,56,],[16,-27,-26,16,-9,-28,-8,16,16,16,16,16,16,-30,16,16,-21,16,16,16,-11,-13,-23,-29,-24,-20,-25,-22,-10,-12,-19,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'program':([0,],[1,]),'expression':([9,13,21,22,23,24,25,29,31,32,34,35,36,],[15,19,30,30,30,30,30,44,46,46,46,46,46,]),'declaration':([26,27,39,43,],[40,40,52,52,]),'statement_list':([0,],[2,]),'component':([0,2,],[3,7,]),'type':([41,],[54,]),'parameter_list':([21,22,23,24,25,],[31,32,34,35,36,]),'expression_list':([9,],[13,]),'declaration_list':([26,27,],[39,43,]),'import_statement':([0,2,],[5,8,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> statement_list','program',1,'p_program','parser.py',8),
  ('statement_list -> statement_list component','statement_list',2,'p_statement_list','parser.py',13),
  ('statement_list -> statement_list import_statement','statement_list',2,'p_statement_list','parser.py',14),
  ('statement_list -> import_statement','statement_list',1,'p_statement_list','parser.py',15),
  ('statement_list -> component','statement_list',1,'p_statement_list','parser.py',16),
  ('import_statement -> LPAREN IMPORT ID RPAREN','import_statement',4,'p_import_statement','parser.py',24),
  ('component -> LBRACE ID expression_list RBRACE','component',4,'p_component','parser.py',28),
  ('expression_list -> expression_list expression','expression_list',2,'p_expression_list','parser.py',32),
  ('expression_list -> expression','expression_list',1,'p_expression_list','parser.py',33),
  ('expression -> LPAREN INPUT declaration_list RPAREN','expression',4,'p_input_expression','parser.py',41),
  ('expression -> LPAREN INPUT RPAREN','expression',3,'p_input_expression','parser.py',42),
  ('expression -> LPAREN OUTPUT declaration_list RPAREN','expression',4,'p_output_expression','parser.py',49),
  ('expression -> LPAREN OUTPUT RPAREN','expression',3,'p_output_expression','parser.py',50),
  ('declaration_list -> declaration_list declaration','declaration_list',2,'p_declaration_list','parser.py',57),
  ('declaration_list -> declaration','declaration_list',1,'p_declaration_list','parser.py',58),
  ('declaration -> LPAREN type ID RPAREN','declaration',4,'p_declaration','parser.py',66),
  ('declaration -> ID','declaration',1,'p_declaration','parser.py',67),
  ('type -> ID','type',1,'p_type','parser.py',74),
  ('expression -> LPAREN ASSIGN ID expression RPAREN','expression',5,'p_assign_expression','parser.py',78),
  ('expression -> LPAREN ID parameter_list RPAREN','expression',4,'p_parameter_list_expression','parser.py',82),
  ('expression -> LPAREN ID RPAREN','expression',3,'p_parameter_list_expression','parser.py',83),
  ('expression -> LPAREN OP_ADD parameter_list RPAREN','expression',4,'p_op_add_expression','parser.py',90),
  ('expression -> LPAREN OP_SUB parameter_list RPAREN','expression',4,'p_op_sub_expression','parser.py',94),
  ('expression -> LPAREN OP_MUL parameter_list RPAREN','expression',4,'p_op_mul_expression','parser.py',98),
  ('expression -> LPAREN OP_DIV parameter_list RPAREN','expression',4,'p_op_div_expression','parser.py',102),
  ('expression -> ID','expression',1,'p_id','parser.py',106),
  ('expression -> NUMBER','expression',1,'p_number','parser.py',110),
  ('expression -> STRING','expression',1,'p_string','parser.py',114),
  ('parameter_list -> parameter_list expression','parameter_list',2,'p_parameter_list','parser.py',118),
  ('parameter_list -> expression','parameter_list',1,'p_parameter_list','parser.py',119),
]
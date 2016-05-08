
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = '8B184828847846774CD153CEF0204C26'
    
_lr_action_items = {'NUMBER':([10,12,13,14,16,17,19,20,22,24,26,27,29,30,31,32,33,36,39,40,42,43,44,45,46,48,51,53,54,55,56,],[12,-27,-9,-28,-26,12,12,12,12,12,12,-8,-30,12,12,12,12,-13,-21,12,-11,12,-29,-24,-25,-22,-12,-20,-10,-23,-19,]),'OP_SUB':([15,],[26,]),'RPAREN':([11,12,14,16,23,24,25,29,30,31,33,35,36,37,38,39,40,41,42,43,44,45,46,47,48,51,52,53,54,55,56,57,58,],[18,-27,-28,-26,36,39,42,-30,45,46,48,51,-13,-17,-15,-21,53,54,-11,55,-29,-24,-25,56,-22,-12,-14,-20,-10,-23,-19,58,-16,]),'OP_MUL':([15,],[19,]),'OP_DIV':([15,],[20,]),'$end':([1,3,5,6,7,8,18,28,],[-1,-4,0,-5,-3,-2,-6,-7,]),'ASSIGN':([15,],[21,]),'LPAREN':([0,1,3,6,7,8,10,12,13,14,16,17,18,19,20,22,23,24,25,26,27,28,29,30,31,32,33,35,36,37,38,39,40,41,42,43,44,45,46,48,51,52,53,54,55,56,58,],[2,2,-4,-5,-3,-2,15,-27,-9,-28,-26,15,-6,15,15,15,34,15,34,15,-8,-7,-30,15,15,15,15,34,-13,-17,-15,-21,15,34,-11,15,-29,-24,-25,-22,-12,-14,-20,-10,-23,-19,-16,]),'OP_ADD':([15,],[22,]),'IMPORT':([2,],[9,]),'OUTPUT':([15,],[23,]),'RBRACE':([12,13,14,16,17,27,36,39,42,45,46,48,51,53,54,55,56,],[-27,-9,-28,-26,28,-8,-13,-21,-11,-24,-25,-22,-12,-20,-10,-23,-19,]),'ID':([4,9,10,12,13,14,15,16,17,19,20,21,22,23,24,25,26,27,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,48,49,50,51,52,53,54,55,56,58,],[10,11,16,-27,-9,-28,24,-26,16,16,16,32,16,37,16,37,16,-8,-30,16,16,16,16,49,37,-13,-17,-15,-21,16,37,-11,16,-29,-24,-25,-22,-18,57,-12,-14,-20,-10,-23,-19,-16,]),'INPUT':([15,],[25,]),'STRING':([10,12,13,14,16,17,19,20,22,24,26,27,29,30,31,32,33,36,39,40,42,43,44,45,46,48,51,53,54,55,56,],[14,-27,-9,-28,-26,14,14,14,14,14,14,-8,-30,14,14,14,14,-13,-21,14,-11,14,-29,-24,-25,-22,-12,-20,-10,-23,-19,]),'LBRACE':([0,1,3,6,7,8,18,28,],[4,4,-4,-5,-3,-2,-6,-7,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'statement_list':([0,],[1,]),'import_statement':([0,1,],[3,7,]),'type':([34,],[50,]),'expression':([10,17,19,20,22,24,26,30,31,32,33,40,43,],[13,27,29,29,29,29,29,44,44,47,44,44,44,]),'parameter_list':([19,20,22,24,26,],[30,31,33,40,43,]),'declaration':([23,25,35,41,],[38,38,52,52,]),'expression_list':([10,],[17,]),'program':([0,],[5,]),'declaration_list':([23,25,],[35,41,]),'component':([0,1,],[6,8,]),}

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
  ('import_statement -> LPAREN IMPORT ID RPAREN','import_statement',4,'p_import_statement','parser.py',25),
  ('component -> LBRACE ID expression_list RBRACE','component',4,'p_component','parser.py',30),
  ('expression_list -> expression_list expression','expression_list',2,'p_expression_list','parser.py',35),
  ('expression_list -> expression','expression_list',1,'p_expression_list','parser.py',36),
  ('expression -> LPAREN INPUT declaration_list RPAREN','expression',4,'p_input_expression','parser.py',45),
  ('expression -> LPAREN INPUT RPAREN','expression',3,'p_input_expression','parser.py',46),
  ('expression -> LPAREN OUTPUT declaration_list RPAREN','expression',4,'p_output_expression','parser.py',54),
  ('expression -> LPAREN OUTPUT RPAREN','expression',3,'p_output_expression','parser.py',55),
  ('declaration_list -> declaration_list declaration','declaration_list',2,'p_declaration_list','parser.py',63),
  ('declaration_list -> declaration','declaration_list',1,'p_declaration_list','parser.py',64),
  ('declaration -> LPAREN type ID RPAREN','declaration',4,'p_declaration','parser.py',73),
  ('declaration -> ID','declaration',1,'p_declaration','parser.py',74),
  ('type -> ID','type',1,'p_type','parser.py',82),
  ('expression -> LPAREN ASSIGN ID expression RPAREN','expression',5,'p_assign_expression','parser.py',87),
  ('expression -> LPAREN ID parameter_list RPAREN','expression',4,'p_parameter_list_expression','parser.py',92),
  ('expression -> LPAREN ID RPAREN','expression',3,'p_parameter_list_expression','parser.py',93),
  ('expression -> LPAREN OP_ADD parameter_list RPAREN','expression',4,'p_op_add_expression','parser.py',101),
  ('expression -> LPAREN OP_SUB parameter_list RPAREN','expression',4,'p_op_sub_expression','parser.py',106),
  ('expression -> LPAREN OP_MUL parameter_list RPAREN','expression',4,'p_op_mul_expression','parser.py',111),
  ('expression -> LPAREN OP_DIV parameter_list RPAREN','expression',4,'p_op_div_expression','parser.py',116),
  ('expression -> ID','expression',1,'p_id','parser.py',121),
  ('expression -> NUMBER','expression',1,'p_number','parser.py',126),
  ('expression -> STRING','expression',1,'p_string','parser.py',131),
  ('parameter_list -> parameter_list expression','parameter_list',2,'p_parameter_list','parser.py',136),
  ('parameter_list -> expression','parameter_list',1,'p_parameter_list','parser.py',137),
]

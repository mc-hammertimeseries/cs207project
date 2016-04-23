
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = 'EFB8CF1353CF3C09DEAB2CE24795587E'
    
_lr_action_items = {'$end':([2,3,4,6,8,9,18,28,],[-4,0,-1,-5,-3,-2,-7,-6,]),'ID':([1,7,10,11,12,13,14,15,16,19,20,21,22,23,24,25,26,27,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,52,53,54,55,57,58,],[7,12,17,12,-26,-27,-9,20,-28,-8,12,12,34,38,12,12,34,12,12,-21,-30,12,34,-17,-11,-15,50,12,12,12,-13,34,12,-20,-29,-23,-10,-14,56,-18,-25,-22,-12,-24,-19,-16,]),'LBRACE':([0,2,4,6,8,9,18,28,],[1,-4,1,-5,-3,-2,-7,-6,]),'OP_SUB':([15,],[21,]),'IMPORT':([5,],[10,]),'INPUT':([15,],[22,]),'RPAREN':([12,13,16,17,20,22,26,29,30,31,32,33,34,35,36,39,40,41,42,43,44,45,46,47,48,51,52,53,54,55,56,57,58,],[-26,-27,-28,28,30,35,41,44,-21,-30,46,47,-17,-11,-15,52,53,-13,54,55,-20,-29,-23,-10,-14,57,-25,-22,-12,-24,58,-19,-16,]),'RBRACE':([11,12,13,14,16,19,30,35,41,44,46,47,52,53,54,55,57,],[18,-26,-27,-9,-28,-8,-21,-11,-13,-20,-23,-10,-25,-22,-12,-24,-19,]),'ASSIGN':([15,],[23,]),'OP_DIV':([15,],[24,]),'NUMBER':([7,11,12,13,14,16,19,20,21,24,25,27,29,30,31,32,35,38,39,40,41,43,44,45,46,47,52,53,54,55,57,],[13,13,-26,-27,-9,-28,-8,13,13,13,13,13,13,-21,-30,13,-11,13,13,13,-13,13,-20,-29,-23,-10,-25,-22,-12,-24,-19,]),'OP_ADD':([15,],[25,]),'OUTPUT':([15,],[26,]),'OP_MUL':([15,],[27,]),'LPAREN':([0,2,4,6,7,8,9,11,12,13,14,16,18,19,20,21,22,24,25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,41,42,43,44,45,46,47,48,52,53,54,55,57,58,],[5,-4,5,-5,15,-3,-2,15,-26,-27,-9,-28,-7,-8,15,15,37,15,15,37,15,-6,15,-21,-30,15,37,-17,-11,-15,15,15,15,-13,37,15,-20,-29,-23,-10,-14,-25,-22,-12,-24,-19,-16,]),'STRING':([7,11,12,13,14,16,19,20,21,24,25,27,29,30,31,32,35,38,39,40,41,43,44,45,46,47,52,53,54,55,57,],[16,16,-26,-27,-9,-28,-8,16,16,16,16,16,16,-21,-30,16,-11,16,16,16,-13,16,-20,-29,-23,-10,-25,-22,-12,-24,-19,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'import_statement':([0,4,],[2,8,]),'expression_list':([7,],[11,]),'program':([0,],[3,]),'parameter_list':([20,21,24,25,27,],[29,32,39,40,43,]),'expression':([7,11,20,21,24,25,27,29,32,38,39,40,43,],[14,19,31,31,31,31,31,45,45,51,45,45,45,]),'statement_list':([0,],[4,]),'type':([37,],[49,]),'declaration':([22,26,33,42,],[36,36,48,48,]),'declaration_list':([22,26,],[33,42,]),'component':([0,4,],[6,9,]),}

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

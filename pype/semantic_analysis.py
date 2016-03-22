from .ast import *

class PrettyPrint(ASTVisitor):
    def __init__(self):
        super().__init__()
    def visit(self, node):
        print(node.__class__.__name__)

class CheckSingleAssignment(ASTVisitor):
    def __init__(self):
        super().__init__()
        self._component_frames = {}
        self._curr_component = None
    def visit(self, node):
        if isinstance(node, ASTComponent):
            self._curr_component = node.name.name
            self._component_frames[node.name.name] = set()
        elif isinstance(node, ASTAssignmentExpr):
            if node.binding.name in self._component_frames[self._curr_component]:
                raise ValueError("Trying to assign a variable twice: " + node.binding.name)
            else:
                self._component_frames[self._curr_component].add(node.binding.name)

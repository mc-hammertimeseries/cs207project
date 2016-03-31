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


class CheckSingleIOExpression(ASTVisitor):

    def __init__(self):
        self.component = None
        self.component_has_input = False
        self.component_has_output = False

    def visit(self, node):
        if isinstance(node, ASTComponent):
            self.component = node.name.name
            self.component_has_input = False
            self.component_has_output = False
        elif isinstance(node, ASTInputExpr):
            if self.component_has_input:
                raise PypeSyntaxError('Component ' + str(self.component) +
                                      ' has multiple input expressions')
            self.component_has_input = True
        elif isinstance(node, ASTOutputExpr):
            if self.component_has_output:
                raise PypeSyntaxError('Component ' + str(self.component) +
                                      ' has multiple output expressions')
            self.component_has_output = True


class CheckUndefinedVariables(ASTVisitor):

    def __init__(self, symtab):
        self.symtab = symtab
        self.scope = None

    def visit(self, node):
        if isinstance(node, ASTComponent):
            self.scope = node.name.name
        elif isinstance(node, ASTID):
            if self.symtab.lookupsym(node.name, scope=self.scope) is None:
                raise PypeSyntaxError('Undefined variable: ' + str(node.name))

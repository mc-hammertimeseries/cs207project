class ASTVisitor():
    def visit(self, astnode):
        'A read-only function which looks at a single AST node.'
        pass
    def return_value(self):
        return None

class ASTNode(object):

    def __init__(self):
        self.parent = None
        self._children = []

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        self._children = children
        for child in children:
            child.parent = self

    def pprint(self, indent=''):
        '''Recursively prints a formatted string representation of the AST.'''
        print(indent + self.__class__.__name__)
        for child in self._children:
            child.pprint(indent + "  ")

    def walk(self, visitor):
        '''Traverses an AST, calling visitor.visit() on every node.

        This is a depth-first, pre-order traversal. Parents will be visited before
        any children, children will be visited in order, and (by extension) a node's
        children will all be visited before its siblings.
        The visitor may modify attributes, but may not add or delete nodes.'''
        visitor.visit(self)
        for child in self._children:
            child.walk(visitor)
        return visitor.return_value()


class ASTProgram(ASTNode):

    def __init__(self, statements):
        super().__init__()
        self.children = statements


class ASTImport(ASTNode):
    def __init__(self, mod):
        super().__init__()
        self.mod = mod

    @property
    def module(self):
        return self.mod


class ASTComponent(ASTNode):

    def __init__(self, name, statements):
        super().__init__()
        self.children = [name] + statements

    @property
    def name(self):
        return self.children[0]

    @property
    def expressions(self):
        return self.children[1:]


class ASTInputExpr(ASTNode):
    def __init__(self, declarations):
        super().__init__()
        self.children = declarations


class ASTOutputExpr(ASTNode):  # TODO
    def __init__(self, declarations):
        super().__init__()
        self.children = declarations


class ASTAssignmentExpr(ASTNode):  # TODO
    def __init__(self, name, expression):
        super().__init__()
        self.children = [name] + [expression]

    @property
    def binding(self):  # TODO
        return self.children[0]

    @property
    def value(self):  # TODO
        return self.children[1:]


class ASTEvalExpr(ASTNode):  # TODO
    def __init__(self, op, parameters):
        super().__init__()
        self.children = [op] + parameters

    @property
    def op(self):
        return self.children[0]

    @property
    def args(self):
        return self.children[1:]

# These are already complete.
class ASTID(ASTNode):

    def __init__(self, name, typedecl=None):
        super().__init__()
        self.name = name
        self.type = typedecl


class ASTLiteral(ASTNode):

    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type = 'Scalar'

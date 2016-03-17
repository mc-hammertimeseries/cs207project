class ASTVisitor():

    def visit(self, astnode):
        'A read-only function which looks at a single AST node.'
        pass


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
        # TODO
        print(indent + self.__class__.__name__)
        for child in self._children:
            child.pprint("   ")

    def walk(self, visitor):
        '''Traverses an AST, calling visitor.visit() on every node.

        This is a depth-first, pre-order traversal. Parents will be visited before
        any children, children will be visited in order, and (by extension) a node's
        children will all be visited before its siblings.
        The visitor may modify attributes, but may not add or delete nodes.'''
        # TODO
        visitor.visit(self)
        for child in self._children:
            child.walk(visitor)


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


class ASTComponent(ASTNode):  # TODO

    @property
    def name(self):  # TODO return an element of self.children
        pass

    @property
    def expressions(self):  # TODO return one or more children
        pass


class ASTInputExpr(ASTNode):  # TODO
    pass


class ASTOutputExpr(ASTNode):  # TODO
    pass


class ASTAssignmentExpr(ASTNode):  # TODO
    pass

    @property
    def binding(self):  # TODO
        pass

    @property
    def value(self):  # TODO
        pass


class ASTEvalExpr(ASTNode):  # TODO
    pass

    @property
    def op(self):  # TODO
        return self.children[0]

    @property
    def args(self):  # TODO
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

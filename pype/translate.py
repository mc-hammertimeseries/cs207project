from .ast import *
from .symtab import *
from .lib_import import LibraryImporter

class SymbolTableVisitor(ASTVisitor):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self._current_component = None
        self._component_dict = {}

    def return_value(self):
        return self.symbol_table

    def visit(self, node):
        if isinstance(node, ASTImport):
            # Import statements make library functions available to PyPE
            imp = LibraryImporter(node.module)
            imp.add_symbols(self.symbol_table)

        # TODO
        # Add symbols for the following types of names:
        #   inputs: anything in an input expression
        #     the SymbolType should be input, and the ref can be None
        #     the scope should be the enclosing component
        #   assigned names: the bound name in an assignment expression
        #     the SymbolType should be var, and the ref can be None
        #     the scope should be the enclosing component
        #   components: the name of each component
        #     the SymbolType should be component, and the ref can be None
        #     the scope sould be *global*

        # Note, you'll need to track scopes again for some of these.
        # You may need to add class state to handle this.
        if isinstance(node, ASTComponent):
            self._current_component = node.name.name
            self._component_dict[self._current_component] = set()
            self.symbol_table.addsym(Symbol(node.name.name, SymbolType.component, None))
        if isinstance(node, ASTAssignmentExpr):
            if node.binding.name in self._component_dict[self._current_component]:
                raise ValueError("Trying to assign a variable twice: " + node.binding.name)
            else:
                self._component_dict[self._current_component].add(node.binding.name)
                self.symbol_table.addsym(Symbol(node.binding.name, SymbolType.var, None), self._current_component)
        if isinstance(node, ASTInputExpr):
            for declaration in node.children:
                self.symbol_table.addsym(Symbol(declaration.name, SymbolType.input, None), self._current_component)


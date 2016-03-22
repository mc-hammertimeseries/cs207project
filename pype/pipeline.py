from .lexer import lexer
from .parser import parser
from .ast import *
from .semantic_analysis import CheckSingleAssignment,PrettyPrint
from .translate import SymbolTableVisitor

class Pipeline(object):
    def __init__(self, source):
        with open(source) as f:
            self.compile(f)

    def compile(self, file):
        input = file.read()
        # Lexing, parsing, AST construction
        ast = parser.parse(input, lexer=lexer)
        # Semantic analysis
        # This just checks if something in a component is assigned twice
        ast.walk( CheckSingleAssignment() )
        # Get output similar to samples/example0.ast
        ast.pprint('')
        # Translation
        syms = ast.walk( SymbolTableVisitor() )
        # Get output similar to samples/example0.symtab
        syms.pprint()
        return syms

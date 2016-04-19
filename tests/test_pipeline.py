from pytest import raises
# from .. import pype
import sys
from io import StringIO

from ..pype.lexer import lexer
from ..pype.parser import parser
from ..pype.ast import *
from ..pype.semantic_analysis import CheckSingleAssignment,PrettyPrint
from ..pype.translate import SymbolTableVisitor

class TestPipeline(object):
    def __init__(self, source):
        with open(source) as f:
            self.syms, self.ast = self.compile(f)

    def compile(self, file):
        input = file.read()
        # Lexing, parsing, AST construction
        ast = parser.parse(input, lexer=lexer)
        # Semantic analysis
        # This just checks if something in a component is assigned twice
        ast.walk( CheckSingleAssignment() )
        # Translation
        syms = ast.walk( SymbolTableVisitor() )
        return syms, ast

# Load each sample output into a list of strings
with open ('tests/samples/example0.ast') as f:
    ast_example_0 = f.read()

with open ('tests/samples/example1.ast') as f:
    ast_example_1 = f.read()

with open ('tests/samples/example2.ast') as f:
    ast_example_2 = f.read()

def test_ast():
    test_0 = TestPipeline(source='tests/samples/example0.ppl')
    test_1 = TestPipeline(source='tests/samples/example1.ppl')
    test_2 = TestPipeline(source='tests/samples/example2.ppl')

    # Redirect standard output to mystdout
    # Code taken from http://stackoverflow.com/a/1218951
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    # Test AST examples
    test_0.ast.pprint()
    assert mystdout.getvalue() == ast_example_0
    # Clear IO
    sys.stdout = mystdout = StringIO()
    test_1.ast.pprint()
    assert mystdout.getvalue() == ast_example_1

    sys.stdout = mystdout = StringIO()
    test_2.ast.pprint()
    assert mystdout.getvalue() == ast_example_2
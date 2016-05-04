from pytest import raises
# from .. import pype
import sys
from io import StringIO

from ..pype.lexer import lexer
from ..pype.parser import parser
from ..pype.ast import *
from ..pype.semantic_analysis import CheckSingleAssignment, CheckSingleIOExpression, CheckUndefinedVariables
from ..pype.translate import SymbolTableVisitor, LoweringVisitor
from ..pype.optimize import *

class TestPipeline(object):
    def __init__(self, source):
        with open(source) as f:
            self.syms, self.ast = self.compile(f)

    def compile(self, file):
        input = file.read()
        ast = parser.parse(input, lexer=lexer)

        # Semantic analysis
        ast.walk( CheckSingleAssignment() )
        ast.walk( CheckSingleIOExpression() )
        syms = ast.walk( SymbolTableVisitor() )
        ast.walk( CheckUndefinedVariables(syms) )

        # Translation
        ir = ast.mod_walk( LoweringVisitor(syms) )

        # Optimization
        ir.flowgraph_pass( AssignmentEllision() )
        ir.flowgraph_pass( DeadCodeElimination() )
        ir.topological_flowgraph_pass( InlineComponents() )

        # Ensure that all component nodes were eliminated
        for component in ir.graphs.values():
            for n in component.nodes.values():
                assert n.type != FGNodeType.component, 'component nodes remain in graph'
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

    # Put back
    sys.stdout = old_stdout

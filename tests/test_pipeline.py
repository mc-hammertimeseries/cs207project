from pytest import raises
import sys
from io import StringIO
import numpy as np
from multiprocessing import Process
from timeseries import TimeSeries
from ..pype.lexer import lexer
from ..pype.parser import parser
from ..pype.ast import *
from ..pype.semantic_analysis import CheckSingleAssignment, CheckSingleIOExpression, CheckUndefinedVariables
from ..pype.translate import SymbolTableVisitor, LoweringVisitor
from ..pype.optimize import *
from ..pype.pipeline import Pipeline


# Load each sample output into a list of strings
with open('tests/samples/example0.ast') as f:
    ast_example_0 = f.read()

with open('tests/samples/example1.ast') as f:
    ast_example_1 = f.read()

with open('tests/samples/example2.ast') as f:
    ast_example_2 = f.read()

def test_ast():
    """
    Uses a modified Pipeline to test various pype operations.
    """

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

def test_pipeline():
    # Test the actual Pipeline function
    def execute_test():
        ts = TimeSeries([1, 2, 3, 4, 5], np.linspace(0, 1, 5))

        test_0 = Pipeline('tests/samples/example0.ppl')
        test_1 = Pipeline('tests/samples/example2.ppl')

        # Check that pcodes are as they should be
        assert set(test_0.pcodes) == set('standardize')
        assert set(test_1.pcodes) == set('mul', 'dist', 'dist2')

        # Test that standardizing workds
        value = test_0['standardize'].run(ts)
        assert np.isclose(value.mean(), 0)
        assert np.isclose(value.std(), 1)

    test_process = Process(target=execute_test)
    test_process.start()
    test_process.join()
 
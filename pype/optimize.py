from .fgir import *
from .error import *

# Optimization pass interfaces


class Optimization(object):

    def visit(self, obj): pass


class FlowgraphOptimization(Optimization):
    '''Called on each flowgraph in a FGIR.
    May modify the flowgraph by adding or removing nodes (return a new Flowgraph).
    If you modify nodes, make sure inputs, outputs, and variables are all updated.
    May NOT add or remove flowgraphs.'''
    pass


class NodeOptimization(Optimization):
    '''Called on each node in a FGIR.
    May modify the node (return a new Node object, and it will be assigned).
    May NOT remove or add nodes (use a component pass).'''
    pass


class TopologicalNodeOptimization(NodeOptimization):
    pass

# Optimization pass implementations


class PrintIR(TopologicalNodeOptimization):
    'A simple "optimization" pass which can be used to debug topological sorting'

    def visit(self, node):
        print(str(node))


class AssignmentEllision(FlowgraphOptimization):
    '''Eliminates all assignment nodes.
    Assignment nodes are useful for the programmer to reuse the output of an
    expression multiple times, and the lowering transformation generates explicit
    flowgraph nodes for these expressions. However, they are not necessary for
    execution, as they simply forward their value. This removes them and connects
    their pre- and post-dependencies.'''

    def visit(self, flowgraph):
        nodeids = flowgraph.topological_sort()
        print(nodeids)
        for nodeid in nodeids:
            node = flowgraph.nodes[nodeid]
            if node.type == FGNodeType.assignment:
                inputs = flowgraph.pre(nodeid)
                outputs = flowgraph.post(nodeid)
                for outputid in outputs:
                    output_node = flowgraph.nodes[outputid]
                    output_node.inputs.remove(nodeid)
                    output_node.inputs.extend(inputs)
                for name, node_id in flowgraph.variables.items():
                    if node_id == nodeid:
                        flowgraph.variables[name] = inputs[0]
        return flowgraph


class DeadCodeElimination(FlowgraphOptimization):
    '''Eliminates unreachable expression statements.
    Statements which never affect any output are effectively useless, and we call
    these "dead code" blocks. This optimization removes any expressions which can
    be shown not to affect the output.
    NOTE: input statements *cannot* safely be removed, since doing so would change
    the call signature of the component. For example, it might seem that the input
    x could be removed:
      { component1 (input x y) (output y) }
    but imagine this component1 was in a file alongside this one:
      { component2 (input a b) (:= c (component a b)) (output c) }
    By removing x from component1, it could no longer accept two arguments. So in
    this instance, component1 will end up unmodified after DCE.'''

    def visit(self, flowgraph):
        nodeids = set(flowgraph.topological_sort() + flowgraph.inputs)
        all_nodes = set(flowgraph.nodes.keys())
        nodes_to_remove = all_nodes - nodeids
        for node_id in nodes_to_remove:
            del flowgraph.nodes[node_id]
        new_variables = {}
        for name, node_id in flowgraph.variables.items():
            if node_id not in nodes_to_remove:
                new_variables[name] = node_id
        flowgraph.variables = new_variables
        return flowgraph

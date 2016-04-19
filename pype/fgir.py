import enum

FGNodeType = enum.Enum('FGNodeType','component libraryfunction librarymethod input output assignment literal forward unknown')


class FGNode(object):

    def __init__(self, nodeid, nodetype, ref=None, inputs=[]):
        self.nodeid = nodeid
        self.type = nodetype
        self.ref = ref
        self.inputs = inputs

    def __repr__(self):
        return '<' + str(self.type) + ' ' + str(self.nodeid) + '<=' + ','.join(map(str, self.inputs)) + ' : ' + str(self.ref) + '>'


class Flowgraph(object):

    def __init__(self, name='?'):
        self.name = name
        self.variables = {}  # { str -> nodeid }
        self.nodes = {}  # { nodeid -> Node }
        self.inputs = []  # [ nodeid, ... ]
        self.outputs = []  # [ nodeid, ... ]
        self._id_counter = 0

    def new_node(self, nodetype, ref=None):
        nid = '@N' + str(self._id_counter)
        self._id_counter += 1
        node = FGNode(nid, nodetype, ref, [])
        self.nodes[nid] = node
        return node

    def get_var(self, name):
        return self.variables.get(name, None)

    def set_var(self, name, nodeid):
        self.variables[name] = nodeid

    def add_input(self, nodeid):
        self.inputs.append(nodeid)

    def add_output(self, nodeid):
        self.outputs.append(nodeid)

    def dotfile(self):
        s = ''
        s += 'digraph ' + self.name + ' {\n'
        for (src, node) in self.nodes.items():
            for dst in node.inputs:
                s += '  "' + str(dst) + '" -> "' + str(src) + '"\n'
        for (var, nid) in self.variables.items():
            s += '  "' + str(nid) + '" [ label = "' + str(var) + '" ]\n'
        for nid in self.inputs:
            s += '  "' + str(nid) + '" [ color = "green" ]\n'
        for nid in self.outputs:
            s += '  "' + str(nid) + '" [ color = "red" ]\n'
        s += '}\n'
        return s

    def pre(self, nodeid):
        return self.nodes[nodeid].inputs

    def post(self, nodeid):
        return [i for (i, n) in self.nodes.items() if nodeid in self.nodes[i].inputs]

    def topological_sort(self):
        # Helper function
        def visit(nodeid):
            if len(self.nodes[nodeid].inputs) == 0:
                return [nodeid]
            else:
                ret_list = []
                for n in self.pre(nodeid):
                    ret_list += visit(n)
                return ret_list + [nodeid]
        sorted_list = []
        for nodeid in self.outputs:
            sorted_list += visit(nodeid)

        final = []
        for node in sorted_list:
            if node not in final:
                final.append(node)
        return final # should return a list of node ids in sorted order


class FGIR(object):

    def __init__(self):
        self.graphs = {}  # { component_name:str => Flowgraph }

    def __getitem__(self, component):
        return self.graphs[component]

    def __setitem__(self, component, flowgraph):
        self.graphs[component] = flowgraph

    def __iter__(self):
        for component in self.graphs:
            yield component

    def flowgraph_pass(self, flowgraph_optimizer):
        for component in self.graphs:
            fg = flowgraph_optimizer.visit(self.graphs[component])
            if fg is not None:
                self.graphs[component] = fg

    def node_pass(self, node_optimizer, topological=False, *args):
        for component in self.graphs:
            fg = self.graphs[component]
            if topological:
                node_order = fg.topological_sort()
            else:
                node_order = fg.nodes.keys()
            for node in node_order:
                n = node_optimizer.visit(fg.nodes[node])
                if n is not None:
                    fg.nodes[node] = n

    def topological_node_pass(self, topo_optimizer):
        self.node_pass(topo_optimizer, topological=True)

    def _topo_helper(self, name, deps, order=[]):
        for dep in deps[name]:
            if dep not in order:
                order = self._topo_helper(dep, deps, order)
        return order+[name]

    def topological_flowgraph_pass(self, topo_flowgraph_optimizer):
        deps = {}
        for (name,fg) in self.graphs.items():
            deps[name] = [n.ref for n in fg.nodes.values() if n.type==FGNodeType.component]
        order = []
        for name in self.graphs:
            order = self._topo_helper(name, deps, order)
        for name in order:
            fg = topo_flowgraph_optimizer.visit(self.graphs[name])
            if fg is not None:
                self.graphs[name] = fg

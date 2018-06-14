from ortools.graph import pywrapgraph
from strategy import RandomStrategy


class FlowVertex:
    """
    Represents a vertex in a network flow graph.

        self.idx: a unique id for this vertex (auto-incrementing)
        self.name: a unique name for this vertex
        self.supply: the amount of flow generated by this vertex
        self.in_arcs: a list of FlowArcs coming into this vertex
        self.out_arcs: a list of FlowArcs going out of this vertex
    """
    _idx = 0
    _objects = {}

    def __init__(self, name, supply):
        # make sure names are unique
        assert name not in FlowVertex._objects

        self.idx = FlowVertex._idx

        self.name = name
        self.supply = supply

        self.in_arcs = []
        self.out_arcs = []

        # ensure vertex indices are unique
        FlowVertex._idx += 1
        FlowVertex._objects[self.name] = self

    def __str__(self):
        return '%s (supply: %d)' % (self.name, self.supply)

    def get_flowin(self):
        return sum([_.flow for _ in self.in_arcs])

    def get_flowout(self):
        return sum([_.flow for _ in self.out_arcs])

    @staticmethod
    def get_vertex(name):
        return FlowVertex._objects[name]

class FlowArc:
    """
    Represents a directed arc in a network flow graph.

        self.idx: a unique id for this arc (auto-incrementing)
        self.source_vert: the source vertex of the arc
        self.dest_vert: the destination vertex of the arc
        self.min_cap: the minimum capacity allowed over this arc
        self.max_cap: the maximum capacity allowed over this arc
        self.cost: the cost of pushing a single unit of flow over this arc
        self.flow: the amount of flow assigned to this arc
            Note: self.min_cap <= self.flow <= self.max_cap must hold
        self.fixed_cost: a flag signifying whether the cost on this arc can be adjusted
    """
    _idx = 0

    def __init__(self, source_vert, dest_vert, min_cap, max_cap, cost, fixed_cost=False):
        self.idx = FlowArc._idx

        self.source_vert = source_vert
        self.dest_vert = dest_vert
        self.min_cap = min_cap
        self.max_cap = max_cap
        self.cost = cost
        self.flow = min_cap
        self.fixed_cost = fixed_cost

        self.source_vert.out_arcs.append(self)
        self.dest_vert.in_arcs.append(self)

        FlowArc._idx += 1

    def __str__(self):
        return '%s -> %s (%d): \t %d <= [%d] <= %d' % (
            self.source_vert.name,
            self.dest_vert.name,
            self.cost,
            self.min_cap,
            self.flow,
            self.max_cap
        )

    def reset_flow(self):
        self.flow = self.min_cap


class FlowNetwork:
    """
    Represents the whole flow network with vertices and arcs.

        self.vertices: a list of all vertices in this network
        self.arcs: a list of all arcs in this network
    """

    def __init__(self, vertices=[], arcs=[], strategy=None):
        self.vertices = vertices
        self.arcs = arcs
        self._mcf = None
        # initialize the given strategy with this network
        if strategy: self.set_strategy(strategy)

        self._regenerate_mcf()

    def set_strategy(self, strategy):
        self.strategy = strategy
        self.strategy.set_network(self)

    def add_vertex(self, vertex):
        if (vertex not in self.vertices):
            self.vertices.append(vertex)

    def add_arc(self, arc):
        if (arc not in self.arcs):
            self.arcs.append(arc)

    def solve(self, iterations=5):
        i = 0
        while i < iterations:
            self.strategy.adjustCosts()
            self.reset()
            self._regenerate_mcf()
            ret = self._mcf.Solve()

            if ret == self._mcf.OPTIMAL:
                # update flows, readjusting each flow for lower bounds
                for arc in self.arcs:
                    arc.flow = self._mcf.Flow(arc.idx) + arc.min_cap

            i += 1

    def reset(self):
        for arc in self.arcs:
            arc.reset_flow()

    def _regenerate_mcf(self):
        """
        Convert this FlowNetwork with lower bounds into a regular Flow
        Network and populate _mcf object
        """
        self._mcf = pywrapgraph.SimpleMinCostFlow()
        # need to adjust arc capacities to accomodate lower bounds
        # i.e.: cap(u->v) = max_cap(u->v) - min_cap(u->v)
        for arc in self.arcs:
            self._mcf.AddArcWithCapacityAndUnitCost(
                arc.source_vert.idx,
                arc.dest_vert.idx,
                arc.max_cap - arc.min_cap,
                arc.cost
            )

        # need to adjust vertex supply to accomodate lower bounds
        # i.e.: d'(v) = d(v) - (f_in(v) - f_out(v))
        # which means that:
        # s'(v) = -d'(v) = (f_in(v) - f_out(v)) - d(v)
        for vert in self.vertices:
            self._mcf.SetNodeSupply(
                vert.idx,
                (vert.get_flowin() - vert.get_flowout()) - vert.supply
            )

    def __str__(self):
        flowSum = 0
        for arc in self.arcs:
            if arc.flow > 0:
                print(arc)
            flowSum += arc.flow * arc.cost
        return 'cost(flow) = %d\n' % flowSum

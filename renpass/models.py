# -*- coding: utf-8 -*-
"""
"""
import logging
import pyomo.environ as po
import components
from pyomo.opt import SolverFactory


class DispatchModel(po.ConcreteModel):
    """
    """
    def __init__(self, es, *args, **kwargs):
        super().__init__()

        self.nodes = es.nodes

        self.timeindex = es.timeindex[0:4]

        self.edges = po.Set(initialize=es.flows().keys(), dimen=2)

        self.flow = po.Var(self.edges, self.timeindex)

        self.hubbalance_constraint()

        self.generator_constraint()

        self.demand_constraint()

        self.storage_constraint()

        self.objective_function()


    def demand_constraint(self):
        """
        """
        self.demands = [n for n in self.nodes
                   if isinstance(n, components.Demand)]


        for d in self.demands:
            if d.amount is None:
                raise AttributeError(
                    ("Missing attribute `amount` for " +
                     " demand object {}!").format(d.label))
            else:
                for i in d.inputs:
                    for t in self.timeindex:
                        self.flow[i, d, t].value = d.amount * d.profile[0]
                        self.flow[i, d, t].fix()

    def storage_constraint(self):
        """
        """
        self.storages = [n for n in self.nodes
                    if isinstance(n, components.Storage)]

        def _capacity_bounds(m, s, t):
            return (0, s.capacity)

        self.storage_capacity = po.Var(
            self.storages, self.timeindex, bounds=_capacity_bounds)

        def _storage_balance(m):
            for s in self.storages:
                for t in m.timeindex:
                    if t == m.timeindex[0]:
                        expr = (m.storage_capacity[s, t] ==
                                m.storage_capacity[s, m.timeindex[-1]])
                    else:
                        lhs = 0
                        lhs += m.storage_capacity[s, t]
                        lhs += - m.storage_capacity[s, t-1]
                        lhs += - m.flow[s.input, s, t] +  m.flow[s, s.output, t]
                        expr = (lhs == 0)
                    m.storage_balance.add((s, t), expr)
        self.storage_balance = po.Constraint(self.storages, self.timeindex,
                                             noruleinit=True)
        self.storage_balance_build = po.BuildAction(rule=_storage_balance)

    def generator_constraint(self):
        """
        """
        self.generators = [n for n in self.nodes
                      if isinstance(n, components.Generator)]

        for g in self.generators:
            if g.capacity is None:
                raise AttributeError(
                    ("Missing attribute `capacity` for " +
                     " generator object {}!").format(g.label))
            else:
                for o in g.outputs:
                    for t in self.timeindex:
                        self.flow[g, o, t].setub(g.capacity)
                        if g.dispatchable == False:
                            self.flow[g, o, t].value = g.capacity * g.profile[0]
                            self.flow[g, o, t].fix()

    def hubbalance_constraint(self):
        """
        """
        hubs = [h for h in self.nodes if isinstance(h, components.Hub)]

        I = {}
        O = {}
        for h in hubs:
            I[h] = [i for i in h.inputs]
            O[h] = [o for o in h.outputs]

        def _hubbalance(m):
            for t in m.timeindex:
                for h in hubs:
                    lhs = sum(m.flow[i, h, t] for i in I[h])
                    rhs = sum(m.flow[h, o, t] for o in O[h])
                    expr = (lhs == rhs)
                    # no inflows no outflows yield: 0 == 0 which is True
                    if expr is not True:
                        m.hubbalance.add((h, t), expr)
        self.hubbalance = po.Constraint(hubs, self.timeindex, noruleinit=True)
        self.hubbalance_build = po.BuildAction(rule=_hubbalance)

    def objective_function(self):
        """
        """
        def _objective_function(self):
            return sum(
                g.marginal_cost * self.flow[g, g.output, t]
                for g in self.generators
                for t in self.timeindex)
        self.objective_function = po.Objective(rule=_objective_function)

    def solve(self, solver='cbc', solver_io='lp', **kwargs):
        r""" Takes care of communication with solver to solve the model.

        Parameters
        ----------
        solver : string
            solver to be used e.g. "glpk","gurobi","cplex"
        solver_io : string
            pyomo solver interface file format: "lp","python","nl", etc.
        \**kwargs : keyword arguments
            Possible keys can be set see below:

        Other Parameters
        ----------------
        solve_kwargs : dict
            Other arguments for the pyomo.opt.SolverFactory.solve() method
            Example : {"tee":True}
        cmdline_options : dict
            Dictionary with command line options for solver e.g.
            {"mipgap":"0.01"} results in "--mipgap 0.01"
            {"interior":" "} results in "--interior"
            Gurobi solver takes numeric parameter values such as
            {"method": 2}

        """
        solve_kwargs = kwargs.get('solve_kwargs', {})
        solver_cmdline_options = kwargs.get("cmdline_options", {})

        opt = SolverFactory(solver, solver_io=solver_io)
        # set command line options
        options = opt.options
        for k in solver_cmdline_options:
            options[k] = solver_cmdline_options[k]

        results = opt.solve(self, **solve_kwargs)

        status = results["Solver"][0]["Status"].key
        termination_condition = \
            results["Solver"][0]["Termination condition"].key

        if status == "ok" and termination_condition == "optimal":
            logging.info("Optimization successful...")
            self.solutions.load_from(results)
        elif status == "ok" and termination_condition == "unknown":
            logging.warning("Optimization with unknown termination condition."
                            " Writing output anyway...")
            self.solutions.load_from(results)
        elif status == "warning" and termination_condition == "other":
            logging.warning("Optimization might be sub-optimal."
                            " Writing output anyway...")
            self.solutions.load_from(results)
        else:

            logging.error(
                "Optimization failed with status %s and terminal condition %s"
                % (status, termination_condition))

        return results

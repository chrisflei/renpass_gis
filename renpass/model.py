# -*- coding: utf-8 -*-
"""
"""
import pyomo.environ as po
import components
from pyomo.opt import SolverFactory


class Model(po.ConcreteModel):
    """
    """
    def __init__(self, es, *args, **kwargs):
        super().__init__()

        self.nodes = es.nodes

        self.timeindex = es.timeindex[0:4]

        self.edges = po.Set(initialize=es.flows().keys(), dimen=2)

        self.flow = po.Var(self.edges, self.timeindex)

        self.hubbalance_constraint()



    def generator_constraint(self):
        """
        """
        generators = [n for n in self.nodes
                      if isinstance(n, components.Generator)]


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

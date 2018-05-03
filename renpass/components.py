# -*- coding: utf-8 -*-
"""
"""
from oemof.network import Source, Sink, Transformer, Bus
from oemof.solph.plumbing import sequence

class Reservoir():
    pass

class ExtractionTurbine():
    pass


class Backpressure():
    pass

class Connection():
    pass

class Conversion():
    pass

class RunOfRiver():
    pass

class Excess():
    pass

class ElectricalLine():
    pass

class Facade:
    """
    """
    required = []
    def __init__(self, *args, **kwargs):
        """
        """
        self.subnodes = []

    def _investment(self):
        if self.capacity is None:
            if self.investment_cost is None:
                msg = ("If you don't set `capacity`, you need to set attribute " +
                       "`investment_cost` of component {}!")
                raise ValueError(msg.format(self.label))
            else:
                # TODO: calculate ep_costs from specific capex
                investment = Investment(ep_costs=self.investment_cost)
        else:
            investment = None

        return investment


class Hub(Bus, Facade):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Generator(Source, Facade):
    """ Generator unit with one output, e.g. gas-turbine, wind-turbine, etc.

    Parameters
    ----------
    bus: oemof.solph.Bus
        An oemof bus instance where the generator is connected to
    capacity: numeric
        The capacity of the generator (e.g. in MW).
    dispatchable: boolean
        If False the generator will be must run based on the specified
        `profile` and (default is True).
    profile: array-like
        Profile of the output such that profile[t] * capacity yields output for
        timestep t
    marginal_cost: numeric
        Marginal cost for one unit of produced output
        E.g. for a powerplant:
        marginal cost =fuel cost + operational cost + co2 cost (in Euro / MWh)
        if timestep length is one hour.
    investment_cost: numeric
        Investment costs per unit of capacity (e.g. Euro / MW) .
        If capacity is not set, this value will be used for optimizing the
        generators capacity.
    """
    required = ['bus']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bus = kwargs.get('bus')

        self.profile = kwargs.get('profile')

        self.capacity = kwargs.get('capacity')

        self.dispatchable = kwargs.get('dispatchable', True)

        self.marginal_cost = kwargs.get('marginal_cost', 0)

        self.investment_cost = kwargs.get('investment_cost')

        self.output = self.bus

        self.outputs.update({self.bus: None})


class Demand(Sink, Facade):
    """ Demand object with one input

     Parameters
     ----------
     bus: oemof.solph.Bus
         An oemof bus instance where the demand is connected to.
     amount: numeric
         The total amount for the timehorzion (e.g. in MWh)
     profile: array-like
          Demand profile with normed values such that `profile[t] * amount`
          yields the demand in timestep t (e.g. in MWh)
    """
    required = ['bus', 'amount', 'profile']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.amount = kwargs.get('amount')

        self.bus = kwargs.get('bus')

        self.profile = kwargs.get('profile')

        self.inputs.update({self.bus: None})


class Connection(Transformer, Facade):
    """ Bi-direction connection for two buses (e.g. to model transshipment)

    Parameters
    ----------
    from_bus: oemof.solph.Bus
        An oemof bus instance where the connection unit is connected to with
        its input.
    to_bus: oemof.solph.Bus
        An oemof bus instance where the connection unit is connected to with
        its output.
    capacity: numeric
        The maximal capacity (output side each) of the unit. If not set, attr
        `investment_cost` needs to be set.
    loss:
        Relative loss through the connection (default: 0)
    investment_cost: numeric
        Investment costs per unit of output capacity.
        If capacity is not set, this value will be used for optimizing the
        chp capacity.
    """
    required = ['from_bus', 'to_bus']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.from_bus = kwargs.get('from_bus')

        self.capacity = kwargs.get('capacity')

        self.to_bus = kwargs.get('to_bus')

        self.loss = kwargs.get('loss', 0)

        self.investment_cost = kwargs.get('investment_cost')

        self.inputs.update({self.from_bus: None})

        self.outputs.update({self.to_bus: None})


class Storage(Source, Facade):
    """ Storage unit

    Parameters
    ----------
    bus: oemof.solph.Bus
        An oemof bus instance where the storage unit is connected to.
    capacity: numeric
        The total capacity of the storage (e.g. in MWh)
    power: numeric
        Max in/out power of storage. Either set this attribute OR `c_rate`.
        If you do not specify `capacity` and set `investment_cost`, use
        `c_rate` instead of power
    ep_ratio: numeric (optional)
        Ratio between energy and power output of the storage. Needs to be
        set if attr `investment_cost` is set.
    investment_cost: numeric
        Investment costs for the storage unit e.g in €/MWh-capacity
    """
    required = ['bus']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.capacity = kwargs.get('capacity')

        self.power = kwargs.get('power')

        self.nominal_capacity = self.capacity

        self.investment_cost = kwargs.get('investment_cost')

        self.loss = kwargs.get('loss', 0)

        self.efficiency = kwargs.get('efficiency', 1)

        self.bus = kwargs.get('bus')

        self.outputs.update({self.bus: None})

from nose.tools import (assert_almost_equal, assert_equal, assert_is_instance, 
                        assert_true)
from numpy import isclose
from toolchest import pyomoio
import pyomo.environ
import pyomo.core as pyomo

def transp_setup():
    """Setup function for pyomoio tests"""
    m = pyomo.ConcreteModel()
    m.name = 'Transport'
    
    plant_capacities = {'Seattle': 350,
                        'San-Diego': 600}
                        
    market_demands = {'New-York': 325,
                      'Chicago': 300,
                      'Topeka': 275}
                        
    distances = {('Seattle', 'New-York'): 2.5,
                 ('Seattle', 'Chicago'): 1.7,
                 ('Seattle', 'Topeka'): 1.8,
                 ('San-Diego', 'New-York'): 2.5,
                 ('San-Diego', 'Chicago'): 1.8,
                 ('San-Diego', 'Topeka'): 1.4}
                 
    freight_cost = 90.0  # in dollars per unit per 1000 miles

    m.plants = pyomo.Set(initialize=plant_capacities.keys())
    m.markets = pyomo.Set(initialize=market_demands.keys())
    
    m.capacity = pyomo.Param(m.plants, initialize=plant_capacities)
    m.demand = pyomo.Param(m.markets, initialize=market_demands)
    m.distance = pyomo.Param(m.plants, m.markets, initialize=distances)
    m.transport_cost = pyomo.Param(m.plants, m.markets, initialize={
        (i,j): (distances[i,j] * freight_cost / 1000) 
        for (i,j) in distances})
    
    m.x = pyomo.Var(m.plants, m.markets, within=pyomo.NonNegativeReals)
    
    def cost_rule(model):
        return pyomo.summation(model.transport_cost, model.x)
        
    def supply_rule(model, this_plant):
        return sum(model.x[this_plant, j] 
                   for j in model.markets) <= model.capacity[this_plant]
        
    def demand_rule(model, this_market):
        return sum(model.x[i, this_market]
                   for i in model.plants) >= model.demand[this_market]
        
    m.obj_cost = pyomo.Objective(rule=cost_rule, sense=pyomo.minimize)
    m.con_supply = pyomo.Constraint(m.plants, rule=supply_rule)
    m.con_demand = pyomo.Constraint(m.markets, rule=demand_rule)
    return m

def test_transp_setup():
    assert_is_instance(transp_setup(), pyomo.ConcreteModel)
    
    
def test_list_entities_set():
    m = transp_setup()
    assert_equal(set(pyomoio.list_entities(m, 'set').index),
                 set(['markets', 'plants']))

    
def test_list_entities_param():
    m = transp_setup()
    assert_equal(set(pyomoio.list_entities(m, 'par').index),
                 set(['capacity', 'demand', 'distance', 'transport_cost']))


def test_get_entity_param():
    m = transp_setup()
    sum_of_distances = pyomoio.get_entity(m, 'distance').sum()
    assert_true(isclose(sum_of_distances, 11.7))

def test_get_entities_param():
    m = transp_setup()
    capacity_and_demand = pyomoio.get_entities(m, ['capacity', 'demand'])
    assert_almost_equal(dict(capacity_and_demand.sum(axis=0)),
                        {'capacity': 950.0, 'demand': 900.0})


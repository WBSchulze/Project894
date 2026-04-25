#! /usr/env/bin python

import pulp


# print(pulp.COIN_CMD().available())

ingredients = [ "CHICKEN", "BEEF", "MUTTON", "RICE", "WHEAT", "GEL" ]

costs = { 
    "CHICKEN": 0.013,
    "BEEF": 0.008,
    "MUTTON": 0.010,
    "RICE": 0.002,
    "WHEAT": 0.005,
    "GEL": 0.001, 
    }

proteinPercent = { 
    "CHICKEN": 0.1,
    "BEEF": 0.2,
    "MUTTON": 0.15,
    "RICE": 0.0,
    "WHEAT": 0.04,
    "GEL": 0.00, 
    }

fatPercent = { 
    "CHICKEN": 0.08,
    "BEEF": 0.1,
    "MUTTON": 0.11,
    "RICE": 0.01,
    "WHEAT": 0.01,
    "GEL": 0.00, 
    }

fiberPercent = { 
    "CHICKEN": 0.001,
    "BEEF": 0.005,
    "MUTTON": 0.003,
    "RICE": 0.100,
    "WHEAT": 0.1500,
    "GEL": 0.00, 
    }

saltPercent = { 
    "CHICKEN": 0.002,
    "BEEF": 0.005,
    "MUTTON": 0.007,
    "RICE": 0.002,
    "WHEAT": 0.008,
    "GEL": 0.00, 
    }

prob = pulp.LpProblem( "The Whiskas Problem", pulp.LpMinimize )

ingredient_vars = {i: pulp.LpVariable( i, 0, None, pulp.LpContinuous ) for i in ingredients }
print( ingredient_vars )
prob.addVariables( ingredient_vars.values() )

# ingredient_vars = prob.addVariables( "Ingr", 
#                                          (ingredients,),
#                                          0,
#                                          None,
#                                          pulp.LpContinuous)

prob += pulp.lpSum([costs[i] * ingredient_vars[i] for i in ingredients]), "Total Cost of Ingredients per Can"
prob += pulp.lpSum([ingredient_vars[i] for i in ingredients]) == 100, "PercentagesSum"
prob += pulp.lpSum([proteinPercent[i] * ingredient_vars[i] for i in ingredients]) >= 8.0, "ProteinRequirement"
prob += pulp.lpSum([fatPercent[i] * ingredient_vars[i] for i in ingredients]) >= 6.0, "FatRequirement"
prob += pulp.lpSum([fiberPercent[i] * ingredient_vars[i] for i in ingredients]) <= 2.0, "FiberRequirement"
prob += pulp.lpSum([saltPercent[i] * ingredient_vars[i] for i in ingredients]) <= 0.4, "SaltRequirement"

prob.writeLP( "WhiskasModel.lp" )

prob.solve()

print( "Status:", pulp.LpStatus[prob.status] )
for v in prob.variables():
    print( v.name, "-", v.varValue )

print( "Total cost of ingredients per can: ", pulp.value( prob.objective ) )
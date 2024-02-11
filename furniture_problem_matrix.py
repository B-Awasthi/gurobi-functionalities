import numpy as np
import gurobipy as gp
from gurobipy import GRB

# product data
price = np.array([80, 45])  # table, chair

# resources data
availability = np.array([400, 450])  # mahogany, labour

# rescources required by each product (bills of material)
bom = np.array([[20, 5], [15, 10]])

model = gp.Model("furniture")

make = model.addMVar(shape=2, name="make")

model.addConstr(bom @ make <= availability)

objective_function = make @ price

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

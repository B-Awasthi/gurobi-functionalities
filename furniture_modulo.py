import itertools
import gurobipy as gp
from gurobipy import GRB

# product data
products, price = gp.multidict({"table": 95, "chair": 45, "bed": 100, "study_table": 75})

# resources data
resources, availability = gp.multidict({"mahogany": 1000, "labour": 1000})

# rescources required by each product (bills of material)
bom = {
    ("mahogany", "chair"): 5,
    ("mahogany", "table"): 20,
    ("mahogany", "bed"): 20,
    ("mahogany", "study_table"): 15,
    ("labour", "chair"): 10,
    ("labour", "table"): 15,
    ("labour", "bed"): 15,
    ("labour", "study_table"): 15,
}

model = gp.Model("furniture")

make = model.addVars(products, vtype=GRB.INTEGER, name="make", lb=10, ub=30)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

# =============================================================================
# all quantities produced should be multiple of 3
# =============================================================================

make_multiple = model.addVars(products, vtype=GRB.INTEGER, name="make", lb=0, ub=30)

model.addConstrs(make[p] == 3 * make_multiple[p] for p in products)

# =============================================================================

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()


names_to_retrieve = [f"make[{p}]" for p in products]
variables = [model.getVarByName(name) for name in names_to_retrieve]

# display solution
for v in variables:
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

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
    ("mahogany", "study_table"): 10,
    ("labour", "chair"): 10,
    ("labour", "table"): 15,
    ("labour", "bed"): 15,
    ("labour", "study_table"): 10,
}

model = gp.Model("furniture")

make = model.addVars(products, name="make", lb=10)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

# =============================================================================
# out of 4 products, atleast 3 products have quantity == 12 or 18
# =============================================================================
signs = ["lt", "ge", "eq"]
values = [12, 18]

dic = {}
for p in products:
    for v in values:
        for s in signs:
            dic[(p, v, s)] = model.addVar(vtype=GRB.BINARY)

prod_bool = model.addVars(products, vtype=GRB.BINARY)

for p in products:
    for v in values:
        for s in signs:
            if s == "lt":
                model.addGenConstrIndicator(dic[(p, v, s)], 1, make[p] <= v)
            elif s == "ge":
                model.addGenConstrIndicator(dic[(p, v, s)], 1, make[p] >= v)
            elif s == "eq":
                model.addGenConstrIndicator(dic[(p, v, s)], 1, make[p] == v)
        model.addConstr(gp.quicksum(dic[(p, v, s)] for s in signs) == 1)

for p in products:
    model.addGenConstrOr(prod_bool[p], [dic[(p, v, "eq")] for v in values])

model.addConstr(gp.quicksum(prod_bool) >= 3)

# =============================================================================

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# names_to_retrieve = [varb for varb in model.getVars() if "make" in varb.VarName]
names_to_retrieve = [f"make[{p}]" for p in products]
variables = [model.getVarByName(name) for name in names_to_retrieve]

# display solution
for v in variables:
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

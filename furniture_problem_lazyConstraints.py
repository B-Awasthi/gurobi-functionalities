import gurobipy as gp
from gurobipy import GRB

# product data
products, price = gp.multidict({"table": 80, "chair": 45})

# resources data
resources, availability = gp.multidict({"mahogany": 400, "labour": 450})

# rescources required by each product (bills of material)
bom = {
    ("mahogany", "chair"): 5,
    ("mahogany", "table"): 20,
    ("labour", "chair"): 10,
    ("labour", "table"): 15,
}

model = gp.Model("furniture")

make = model.addVars(products, name="make", vtype=GRB.INTEGER)

res = model.addConstrs(
    gp.quicksum(bom[r, p] * make[p] for p in products) <= availability[r]
    for r in resources
)

objective_function = make.prod(price)

model.setObjective(objective_function, sense=GRB.MAXIMIZE)


# if total number of tables and chairs > 30,
# then sum of ables and chairs <= 25
def mycallback(model, where):
    if where == GRB.Callback.MIPSOL:
        sol = model.cbGetSolution([model._vars[s] for s in products])
        if sum(sol) > 30:
            model.cbLazy(model._vars.sum() <= 25)


model._vars = make

model.params.LazyConstraints = 1

model.optimize(mycallback)

# display solution
for v in model.getVars():
    if abs(v.X) > 0.001:
        print(v.varName, v.X)

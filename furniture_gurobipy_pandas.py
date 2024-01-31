import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import gurobipy_pandas as gppd

# product data
product_df = pd.DataFrame({"product": ["table", "chair"], "price": [80, 45]}).set_index(
    ["product"]
)

# resources data
resources_df = pd.DataFrame(
    {"resources": ["mahogany", "labour"], "availability": [400, 450]}
).set_index(["resources"])


bom_df = pd.DataFrame(
    {
        "resources": ["mahogany", "mahogany", "labour", "labour"],
        "product": ["chair", "table", "chair", "table"],
        "requirement": [5, 20, 10, 15],
    }
).set_index(["resources", "product"])

model = gp.Model("furniture")

make = gppd.add_vars(model, product_df, name="make")
bom_df = bom_df.merge(make, how="left", left_index=True, right_index=True)

gppd.add_constrs(
    model,
    (bom_df["requirement"] * bom_df["make"]).groupby("resources").agg(gp.quicksum),
    GRB.LESS_EQUAL,
    resources_df["availability"],
    name="c1",
)

objective_function = (product_df["price"] * make).agg(gp.quicksum)  # .sum()

model.setObjective(objective_function, sense=GRB.MAXIMIZE)

model.optimize()

# display solution
make.gppd.X

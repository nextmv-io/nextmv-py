import json

from nextmv_sklearn.tree import DecisionTreeRegressorOptions

dum_opt = DecisionTreeRegressorOptions()
n_dum_opt = dum_opt.to_nextmv()
got = n_dum_opt.parameters_dict()

with open("expected_decision_tree_options.json", "w") as f:
    json.dump(got, f, indent=2)

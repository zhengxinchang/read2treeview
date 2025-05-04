import csv
import json
from collections import defaultdict
from logging import root

input_file = "./phylo_data_H5N1_influenzaA.csv"

nodes = {}
children_map = defaultdict(list)

with open(input_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        node_id = row["node"]
        parent_id = row["parent"]


        meta = {
            k: row[k]
            for k in row
            if k not in ["parent", "node", "branch.length", "new_label"]
        }


        if row["branch.length"] == "NA":
            brlen = 0.0
        else:
            brlen = float(row["branch.length"])
        nodes[node_id] = {
            "id": node_id,
            "name": row["new_label"],
            "branch_length": brlen,
            "meta": meta,
            "children": []
        }

        if parent_id != node_id:
            children_map[parent_id].append(node_id)
        else:
            root_id = node_id


def build_tree(node_id):
    node = nodes[node_id]
    node["children"] = [build_tree(child_id) for child_id in children_map.get(node_id, [])]
    return node


tree = build_tree(root_id)


with open("tree_output.json", "w") as f:
    json.dump(tree, f, indent=2)

tree_str = json.dumps(tree)

with open("index4.html", "r") as f:
    with open("index4_out.html", "w") as f2:
        template = f.read()
        f2.write(template.replace("[/*inject_data*/]", tree_str))
import csv
import json
from collections import defaultdict
from logging import root

input_file = "/wkspace/projects/read2treeview/phylo_data_H5N1_influenzaA.csv"

nodes = {}
children_map = defaultdict(list)

with open(input_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        node_id = row["node"]
        parent_id = row["parent"]

        # 解析元数据字段
        meta = {
            k: row[k]
            for k in row
            if k not in ["parent", "node", "branch.length", "new_label"]
        }

        # print(row)

        # 构建节点
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

# 基于 parent_id == node_id 找根节点
# root_id = next(node_id for node_id in nodes if node_id not in children_map or node_id == nodes[node_id]["id"])

# 递归构建树
def build_tree(node_id):
    node = nodes[node_id]
    node["children"] = [build_tree(child_id) for child_id in children_map.get(node_id, [])]
    return node

# 构建整棵树
tree = build_tree(root_id)

# 保存 JSON
with open("tree_output.json", "w") as f:
    json.dump(tree, f, indent=2)

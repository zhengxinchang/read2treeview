import csv
import json
import argparse
from collections import defaultdict
from typing import Dict, Any


def parse_csv_to_tree(input_file: str) -> Dict[str, Any]:
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

            brlen = 0.0 if row["branch.length"] == "NA" else float(row["branch.length"])

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

    def build_tree(node_id: str) -> Dict[str, Any]:
        node = nodes[node_id]
        node["children"] = [build_tree(child_id) for child_id in children_map.get(node_id, [])]
        return node

    return build_tree(root_id)


def inject_tree_into_html(tree: Dict[str, Any], template_path: str, output_path: str):
    tree_str = json.dumps(tree)
    with open(template_path, "r") as f:
        template = f.read()
    with open(output_path, "w") as f2:
        f2.write(template.replace("[/*inject_data*/]", tree_str))


def main(input_file: str, json_output: str, html_template: str, html_output: str):
    tree = parse_csv_to_tree(input_file)
    with open(json_output, "w") as f:
        json.dump(tree, f, indent=2)
    inject_tree_into_html(tree, html_template, html_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert phylogenetic CSV to JSON tree and inject into HTML.")
    parser.add_argument("input_file", help="Path to input CSV file")
    parser.add_argument("json_output", help="Path to output JSON file")
    parser.add_argument("html_template", help="Path to input HTML template")
    parser.add_argument("html_output", help="Path to output HTML file with injected data")

    args = parser.parse_args()
    main(args.input_file, args.json_output, args.html_template, args.html_output)

def build_process_tree(processes):
    process_map = {proc['pid']: {**proc, "children": []} for proc in processes}
    root_nodes = []

    for proc in processes:
        parent = process_map.get(proc["ppid"])
        if parent:
            parent["children"].append(process_map[proc["pid"]])
        else:
            root_nodes.append(process_map[proc["pid"]])

    return root_nodes
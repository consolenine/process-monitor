import re
from datetime import timedelta
from django.utils import timezone

def apply_time_range_filter(qs, time_range):
    if not time_range:
        return qs

    now = timezone.now()
    match = re.match(r'^(?P<value>\d+)(?P<unit>[smhdw])$', time_range)
    if match:
        value = int(match.group("value"))
        unit = match.group("unit")

        delta_args = {
            's': {'seconds': value},
            'm': {'minutes': value},
            'h': {'hours': value},
            'd': {'days': value},
            'w': {'weeks': value},
        }

        if unit in delta_args:
            delta = timedelta(**delta_args[unit])
            return qs.filter(timestamp__gte=now - delta)

    return qs  # fallback if time_range is invalid

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
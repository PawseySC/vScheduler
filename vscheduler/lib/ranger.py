# import re

# def parse_node_range(node_range_str):
#     # Remove brackets and spaces
#     node_range_str = node_range_str.strip("[]").replace(" ", "")
#     nodes = []
#     for part in node_range_str.split(","):
#         if "-" in part:
#             start, end = map(int, part.split("-"))
#             nodes.extend(range(start, end + 1))
#         else:
#             nodes.append(int(part))
#     return nodes


# import re

# def parse_node_range(node_range_str):
#     match = re.match(r"([a-zA-Z]+)\[(.+)\]", node_range_str)
#     if not match:
#         return [node_range_str]
#     prefix, ranges = match.groups()
#     nodes = []
#     for part in ranges.split(","):
#         part = part.strip()
#         if "-" in part:
#             start, end = map(int, part.split("-"))
#             for i in range(start, end + 1):
#                 nodes.append(f"{prefix}{i:02d}")
#         else:
#             nodes.append(f"{prefix}{int(part):02d}")
#     return nodes

import re

def parse_node_range(node_range_str):
    match = re.match(r"([^\[]+)\[(.+)\]", node_range_str)
    if not match:
        return [node_range_str]
    prefix, ranges = match.groups()
    nodes = []
    for part in ranges.split(","):
        part = part.strip()
        if "-" in part:
            start, end = map(int, part.split("-"))
            for i in range(start, end + 1):
                nodes.append(f"{prefix}{i:02d}")
        else:
            nodes.append(f"{prefix}{int(part):02d}")
    return nodes


def nodes_to_range(node_list):
    import re
    from itertools import groupby

    # Extract prefix and numbers
    nodes_by_prefix = {}
    for node in node_list:
        m = re.match(r"([a-zA-Z0-9\-]+)(\d+)", node)
        if m:
            prefix, num = m.group(1), int(m.group(2))
            nodes_by_prefix.setdefault(prefix, []).append(num)

    result = []
    for prefix, nums in nodes_by_prefix.items():
        nums = sorted(nums)
        ranges = []
        for _, group in groupby(enumerate(nums), lambda x: x[1] - x[0]):
            group = list(group)
            start = group[0][1]
            end = group[-1][1]
            if start == end:
                ranges.append(f"{start:02d}")
            else:
                ranges.append(f"{start:02d}-{end:02d}")
        result.append(f"{prefix}[{','.join(ranges)}]")
    return ', '.join(result)
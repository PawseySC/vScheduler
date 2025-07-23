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
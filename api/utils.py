from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count


def get_paths(bids):
    histories = create_histories(bids)
    paths = []
    for history in histories:
        path = [{"id": bid[1], "bid": bid[0], "comment": bid[2]}
                for bid in zip(history[0][::-1], history[1][::-1], history[2][::-1])
                ]
        paths.append(path)
    return paths


def create_histories(bids):
    histories = list(
        bids.annotate(closure=Count("closure_ancestor", distinct=True),
                      history=ArrayAgg(
                          "closure_descendants__ancestor__name",
                          ordering="closure_descendants__depth"),
                      history_id=ArrayAgg(
                          "closure_descendants__ancestor__id",
                          ordering="closure_descendants__depth"),
                      comments=ArrayAgg(
                          "closure_descendants__ancestor__comment",
                          ordering="closure_descendants__depth")
                      )
        .filter(closure=1)
        .values_list("history", "history_id", "comments")
    )
    return histories


def create_tree(bids):
    histories = create_histories(bids)
    used_nodes = {}
    trees = []

    for history in histories:
        add_branch(zip(*history), used_nodes, trees)
    return trees


def add_branch(history, used_nodes, trees):
    current_node = None
    new_node = None
    for node in history:
        if node[1] in used_nodes:
            tree = trees[used_nodes[node[1]]]
            extend_existing_tree(tree, node[1], current_node)
            return
        if current_node is None:
            new_node = {"id": node[1], "name": node[0], "comment": node[2],
                        "children": []}
        else:
            new_node = {"id": node[1], "name": node[0], "comment": node[2],
                        "children": [current_node]}
        used_nodes.update({node[1]: len(trees)})
        current_node = new_node
    trees.append(new_node)


def extend_existing_tree(tree, pk, branch):
    if tree["id"] == pk:
        tree["children"].append(branch)
        return
    for node in tree["children"]:
        extend_existing_tree(node, pk, branch)

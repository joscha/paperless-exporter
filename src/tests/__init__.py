from pathlib import Path
from rich.tree import Tree
from rich import print
from io import StringIO


def get_tree_string_from_path(path: Path) -> str:
    tree = build_tree_from_path(path)
    buffer = StringIO()
    print(tree, file=buffer)
    return buffer.getvalue()


def build_tree_from_path(path: Path) -> Tree:
    if not path.is_dir():
        raise ValueError(f"Path must be a directory, got: {path}")

    root = Tree(f"[bold blue]{path.name}/[/]")

    def add_node(tree_node: Tree, current_path: Path):
        for entry in sorted(
            current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())
        ):
            label = f"[bold]{entry.name}/[/]" if entry.is_dir() else entry.name
            child_node = tree_node.add(label)
            if entry.is_dir():
                add_node(child_node, entry)

    add_node(root, path)
    return root

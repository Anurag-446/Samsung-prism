"""Graph traversal and navigation logic."""
from typing import Dict, List, Optional
from fixgraph.navigation.hierarchy import HierarchyNode, HierarchyParser
from pathlib import Path

class NavigationGraph:
    def __init__(self, hierarchy_path: Path):
        self.root, self.nodes = HierarchyParser.parse(hierarchy_path)

    def is_ancestor(self, ancestor_id: str, descendant_id: str) -> bool:
        if ancestor_id not in self.nodes:
            return False
            
        node = self.nodes[ancestor_id]
        if descendant_id in node.children:
            return True
            
        for child_id in node.children:
            if self.is_ancestor(child_id, descendant_id):
                return True
        return False
        
    def get_children(self, node_id: str) -> List[str]:
        if node_id in self.nodes:
            return self.nodes[node_id].children
        return []

    def is_root(self, node_id: str) -> bool:
        return self.root == node_id

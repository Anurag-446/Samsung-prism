"""Hierarchy parsing for Samsung Settings."""
import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel

class HierarchyNode(BaseModel):
    id: str
    name: str
    children: List[str]

class HierarchyParser:
    @staticmethod
    def parse(path: Path) -> (Optional[str], Dict[str, HierarchyNode]):
        if not path.exists():
            return None, {}
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        root = data.get("root")
        nodes = {}
        for node_id, node_data in data.get("nodes", {}).items():
            nodes[node_id] = HierarchyNode(**node_data)
            
        return root, nodes

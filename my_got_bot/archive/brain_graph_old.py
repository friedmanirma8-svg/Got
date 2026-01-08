"""
Graph-based reasoning structure for Tree-of-Thoughts.
Allows branching, backtracking, and parallel exploration.

This module implements a tree structure for thoughts, enabling:
- Multiple reasoning paths (branching)
- Scoring and pruning of paths
- Backtracking to explore alternatives
- Finding the best reasoning chain
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class NodeState(Enum):
    """State of a thought node in the tree."""
    PENDING = "pending"      # Not yet explored
    ACTIVE = "active"        # Currently being developed
    COMPLETED = "completed"  # Reasoning finished
    PRUNED = "pruned"        # Dead end, low score


@dataclass
class ThoughtNode:
    """
    A single node in the thought tree.
    
    Represents one reasoning step or thought branch.
    """
    id: str
    content: str                    # The actual thought/reasoning text
    parent_id: Optional[str]        # Parent node ID (None for root)
    children_ids: List[str] = field(default_factory=list)  # Child node IDs
    state: NodeState = NodeState.PENDING
    score: float = 0.5              # Quality/confidence score (0-1)
    depth: int = 0                  # Distance from root
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)  # Extra data


class BrainGraph:
    """
    Tree-of-Thoughts reasoning structure.
    
    Supports:
    - Branching: Explore multiple reasoning paths
    - Scoring: Evaluate quality of each thought
    - Pruning: Remove low-quality branches
    - Best path: Find highest-scored reasoning chain
    
    Example:
        brain = BrainGraph(max_depth=4, max_branches=3)
        root = brain.create_root("User asks: What is AI?")
        
        # Branch 1: Define AI
        c1 = brain.add_child(root, "AI is artificial intelligence...", score=0.8)
        
        # Branch 2: Give history
        c2 = brain.add_child(root, "AI started in the 1950s...", score=0.6)
        
        # Continue best branch
        best_leaf = brain.get_best_leaf()
        path = brain.get_path_to_node(best_leaf.id)
    """
    
    def __init__(
        self, 
        max_depth: int = 4, 
        max_branches: int = 3,
        prune_threshold: float = 0.2
    ):
        """
        Initialize tree structure.
        
        Args:
            max_depth: Maximum tree depth (prevents infinite recursion)
            max_branches: Max children per node (controls breadth)
            prune_threshold: Score below which to prune branches
        """
        self.nodes: Dict[str, ThoughtNode] = {}
        self.root_id: Optional[str] = None
        self.max_depth = max_depth
        self.max_branches = max_branches
        self.prune_threshold = prune_threshold
        
        print(f"🌳 BrainGraph initialized")
        print(f"   Max depth: {max_depth}")
        print(f"   Max branches per node: {max_branches}")
        print(f"   Prune threshold: {prune_threshold}")
    
    def create_root(self, content: str, score: float = 1.0) -> str:
        """
        Create root thought node.
        
        Args:
            content: Initial thought (usually user query)
            score: Initial score (default 1.0 for root)
        
        Returns:
            Root node ID
        """
        node_id = str(uuid.uuid4())
        self.root_id = node_id
        
        self.nodes[node_id] = ThoughtNode(
            id=node_id,
            content=content,
            parent_id=None,
            children_ids=[],
            state=NodeState.COMPLETED,
            score=score,
            depth=0
        )
        
        print(f"🌱 Root created: {content[:50]}...")
        return node_id
    
    def add_child(
        self, 
        parent_id: str, 
        content: str, 
        score: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add a child thought to a parent node.
        
        Args:
            parent_id: Parent node ID
            content: Thought content
            score: Quality score (0-1)
            metadata: Optional extra data
        
        Returns:
            New child node ID
        
        Raises:
            ValueError: If branching limits exceeded
        """
        if parent_id not in self.nodes:
            raise ValueError(f"Parent node {parent_id} not found")
        
        parent = self.nodes[parent_id]
        
        # Check branching limit
        if len(parent.children_ids) >= self.max_branches:
            raise ValueError(
                f"Parent already has {self.max_branches} children. "
                f"Cannot add more (max_branches limit)."
            )
        
        # Check depth limit
        if parent.depth >= self.max_depth:
            raise ValueError(
                f"Max depth {self.max_depth} reached. "
                f"Cannot add deeper nodes."
            )
        
        # Create new node
        node_id = str(uuid.uuid4())
        self.nodes[node_id] = ThoughtNode(
            id=node_id,
            content=content,
            parent_id=parent_id,
            children_ids=[],
            state=NodeState.ACTIVE,
            score=score,
            depth=parent.depth + 1,
            metadata=metadata or {}
        )
        
        # Link to parent
        parent.children_ids.append(node_id)
        
        print(f"🌿 Child added at depth {parent.depth + 1}: {content[:50]}... (score: {score:.2f})")
        return node_id
    
    def get_node(self, node_id: str) -> Optional[ThoughtNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)
    
    def update_score(self, node_id: str, new_score: float):
        """Update node score (e.g., after evaluation)."""
        if node_id in self.nodes:
            self.nodes[node_id].score = new_score
            print(f"📊 Updated score for node {node_id[:8]}... to {new_score:.2f}")
    
    def get_children(self, node_id: str) -> List[ThoughtNode]:
        """Get all children of a node."""
        if node_id not in self.nodes:
            return []
        return [self.nodes[cid] for cid in self.nodes[node_id].children_ids]
    
    def get_leaves(self, exclude_pruned: bool = True) -> List[ThoughtNode]:
        """
        Get all leaf nodes (nodes with no children).
        
        Args:
            exclude_pruned: If True, exclude pruned nodes
        
        Returns:
            List of leaf nodes
        """
        leaves = [
            node for node in self.nodes.values()
            if not node.children_ids
        ]
        
        if exclude_pruned:
            leaves = [n for n in leaves if n.state != NodeState.PRUNED]
        
        return leaves
    
    def get_best_leaf(self) -> Optional[ThoughtNode]:
        """
        Find the highest-scored leaf node.
        
        This represents the best reasoning path endpoint.
        
        Returns:
            ThoughtNode with highest score, or None if tree is empty
        """
        leaves = self.get_leaves(exclude_pruned=True)
        if not leaves:
            return None
        
        best = max(leaves, key=lambda n: n.score)
        print(f"⭐ Best leaf: score={best.score:.2f}, depth={best.depth}")
        return best
    
    def get_path_to_node(self, node_id: str) -> List[ThoughtNode]:
        """
        Get full path from root to a specific node.
        
        This gives you the complete reasoning chain.
        
        Args:
            node_id: Target node ID
        
        Returns:
            List of nodes from root to target (ordered)
        """
        if node_id not in self.nodes:
            return []
        
        path = []
        current_id = node_id
        
        while current_id:
            node = self.nodes[current_id]
            path.insert(0, node)  # Prepend to maintain root-to-leaf order
            current_id = node.parent_id
        
        return path
    
    def get_best_path(self) -> List[ThoughtNode]:
        """
        Get the full reasoning path to the best leaf.
        
        Returns:
            List of nodes representing the best reasoning chain
        """
        best_leaf = self.get_best_leaf()
        if not best_leaf:
            return []
        return self.get_path_to_node(best_leaf.id)
    
    def prune_low_scoring(self, threshold: Optional[float] = None):
        """
        Prune branches below score threshold.
        
        Args:
            threshold: Score threshold (uses self.prune_threshold if None)
        """
        if threshold is None:
            threshold = self.prune_threshold
        
        pruned_count = 0
        for node in self.nodes.values():
            if node.score < threshold and node.state != NodeState.PRUNED:
                node.state = NodeState.PRUNED
                pruned_count += 1
        
        print(f"✂️  Pruned {pruned_count} low-scoring nodes (threshold: {threshold:.2f})")
    
    def get_stats(self) -> Dict:
        """
        Get tree statistics.
        
        Returns:
            Dict with node counts, depth, scores, etc.
        """
        if not self.nodes:
            return {"total_nodes": 0}
        
        states_count = {}
        for state in NodeState:
            states_count[state.value] = sum(
                1 for n in self.nodes.values() if n.state == state
            )
        
        scores = [n.score for n in self.nodes.values()]
        
        return {
            "total_nodes": len(self.nodes),
            "max_depth_reached": max(n.depth for n in self.nodes.values()),
            "leaf_nodes": len(self.get_leaves(exclude_pruned=False)),
            "states": states_count,
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
        }
    
    def visualize(self, max_width: int = 80) -> str:
        """
        ASCII tree visualization.
        
        Args:
            max_width: Max character width for node content
        
        Returns:
            Multi-line string with tree structure
        """
        if not self.root_id:
            return "Empty tree"
        
        def _truncate(text: str, width: int) -> str:
            """Truncate text to width."""
            if len(text) <= width:
                return text
            return text[:width-3] + "..."
        
        def _render_node(node_id: str, prefix: str = "", is_last: bool = True) -> List[str]:
            """Recursively render node and children."""
            node = self.nodes[node_id]
            lines = []
            
            # Node line with connector
            connector = "└── " if is_last else "├── "
            
            # Score indicator (stars)
            stars = "⭐" * int(node.score * 5)
            
            # State emoji
            state_emoji = {
                NodeState.PENDING: "⏳",
                NodeState.ACTIVE: "🔄",
                NodeState.COMPLETED: "✅",
                NodeState.PRUNED: "✂️"
            }
            
            # Format node line
            content_short = _truncate(node.content, max_width - len(prefix) - 20)
            node_line = (
                f"{prefix}{connector}"
                f"{state_emoji[node.state]} {content_short} "
                f"[{stars} {node.score:.2f}]"
            )
            lines.append(node_line)
            
            # Render children
            new_prefix = prefix + ("    " if is_last else "│   ")
            for i, child_id in enumerate(node.children_ids):
                is_last_child = (i == len(node.children_ids) - 1)
                lines.extend(_render_node(child_id, new_prefix, is_last_child))
            
            return lines
        
        header = f"Tree-of-Thoughts (depth={self.max_depth}, branches={self.max_branches})"
        separator = "=" * len(header)
        
        tree_lines = [separator, header, separator] + _render_node(self.root_id)
        
        # Add stats
        stats = self.get_stats()
        tree_lines.append(separator)
        tree_lines.append(f"Nodes: {stats['total_nodes']} | Leaves: {stats['leaf_nodes']} | Avg Score: {stats['avg_score']:.2f}")
        tree_lines.append(separator)
        
        return "\n".join(tree_lines)
    
    def export_chain_text(self, node_id: Optional[str] = None) -> str:
        """
        Export reasoning chain as plain text.
        
        Args:
            node_id: Target node (uses best leaf if None)
        
        Returns:
            Formatted text of reasoning steps
        """
        if node_id is None:
            best = self.get_best_leaf()
            if not best:
                return "Empty tree"
            node_id = best.id
        
        path = self.get_path_to_node(node_id)
        
        lines = ["=== REASONING CHAIN ===\n"]
        for i, node in enumerate(path):
            if i == 0:
                lines.append(f"🎯 Initial: {node.content}\n")
            else:
                lines.append(f"Step {i}: {node.content}")
                lines.append(f"    (score: {node.score:.2f})\n")
        
        return "\n".join(lines)


# Example usage (for testing):
if __name__ == "__main__":
    # Create tree
    brain = BrainGraph(max_depth=3, max_branches=2)
    
    # Root: User question
    root = brain.create_root("User asks: What causes climate change?")
    
    # Branch 1: Scientific explanation
    sci_branch = brain.add_child(
        root, 
        "Need to explain greenhouse effect and human activities",
        score=0.9
    )
    
    # Branch 2: Historical context
    hist_branch = brain.add_child(
        root,
        "Could give history of industrial revolution",
        score=0.6
    )
    
    # Continue scientific branch (higher score)
    detail1 = brain.add_child(
        sci_branch,
        "Greenhouse gases (CO2, CH4) trap heat. Human activities increase these.",
        score=0.85
    )
    
    detail2 = brain.add_child(
        sci_branch,
        "Could discuss deforestation impact",
        score=0.7
    )
    
    # Finalize best path
    final = brain.add_child(
        detail1,
        "Burning fossil fuels + deforestation = main causes",
        score=0.9
    )
    
    # Visualize
    print(brain.visualize())
    
    # Get best path
    print("\n" + brain.export_chain_text())
    
    # Stats
    print("\nStatistics:")
    stats = brain.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

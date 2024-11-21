import networkx as nx
import matplotlib.pyplot as plt
import random
import math
from time import sleep

DEFAULT_SIZE = 20
MINIMUM_DISTANCE_BETWEEN_NODES = 3
TEXT_OFFSET = 1.5

class Graph:
    def __init__(self, size = DEFAULT_SIZE):
        self.graph = nx.Graph()
        self.node_colors = {}
        self.edge_colors = {} 
        self.positions = {} 
        self.fig, self.ax = plt.subplots(figsize=(8,6))
        plt.ion()

        self.commands = {
            "new": self.add_node,
            "connect": self.add_edge,
            "color": self.change_color,
            "kill": self.remove_node,
            "sleep": self.wait
        }

        # Fixed canvas boundaries (20x20 grid)
        self.canvas_size = size
        self.ax.set_xlim(0, self.canvas_size)
        self.ax.set_ylim(0, self.canvas_size)
        self.ax.set_aspect('equal')

    def update(self):
        """Update the graph visualization."""
        self.ax.clear()
        #Fixed limits to avoid shifting view
        self.ax.set_xlim(0, self.canvas_size)
        self.ax.set_ylim(0, self.canvas_size)
        self.ax.set_aspect('equal')

        nx.draw(
            self.graph,
            pos=self.positions,
            with_labels=False,
            node_color=[self.node_colors.get(node, "gray") for node in self.graph.nodes()],
            ax=self.ax,
            edge_color=[self.edge_colors.get(edge, "black") for edge in self.graph.edges()],
            alpha=0.8  # Fade effect
        )
        self.__update_labels()
        plt.pause(0.5)

    def __update_labels(self):
        for node, (x, y) in self.positions.items():
            self.ax.text(
                x + TEXT_OFFSET,
                y + TEXT_OFFSET,
                node,
                fontsize=10,
                color="black",
                ha="center",
                va="center",
            )

    def add_node(self, node_id):
        """Add a new node with a random fixed position ensuring a minimum distance from other nodes."""
        if node_id in self.graph.nodes:
            return

        self.graph.add_node(node_id)
        self.node_colors[node_id] = "gray"
        
        # Start by generating a random position
        x, y = random.randint(1, self.canvas_size - 1), random.randint(1, self.canvas_size - 1)
        
        # Check if the generated position is at least 3 units away from all existing nodes
        while self.is_too_close(x, y):
            x, y = random.randint(1, self.canvas_size - 1), random.randint(1, self.canvas_size - 1)
        
        # Store the valid position
        self.positions[node_id] = (x, y)
        self.update()

    def is_too_close(self, x, y):
        """Check if the point (x, y) is at least 3 units away from all other nodes."""
        for (existing_x, existing_y) in self.positions.values():
            # Calculate Euclidean distance
            distance = math.sqrt((x - existing_x) ** 2 + (y - existing_y) ** 2)
            if distance < MINIMUM_DISTANCE_BETWEEN_NODES: 
                return True
        return False

    def add_edge(self, node1, node2, update=True):
        """Add an edge between two nodes."""
        if node1 not in self.graph.nodes or node2 not in self.graph.nodes:
            return
        self.graph.add_edge(node1, node2)
        self.edge_colors[(node1, node2)] = "black" 
        if update:
            self.update()

    def complete_edges_for(self, node_id):
        """Connect a node to all other nodes."""
        for node in self.graph.nodes:
            if node != node_id:
                self.add_edge(node, node_id, False)
        self.update()

    def change_color(self, node_id, color):
        """Change the color of nodes."""
        if node_id == "all":
            for node in self.graph.nodes:
                self.node_colors[node] = color
            self.update()
            return

        # If the node_id is 'all' but contains a node exception ("all-node1"), we need to skip that node
        if node_id.startswith("all-"):
            node_to_exclude = node_id.split('-')[1]
            for node in self.graph.nodes:
                if node != node_to_exclude:
                    self.node_colors[node] = color
            self.update()
            return

        if node_id in self.graph.nodes:
            self.node_colors[node_id] = color
            self.update()

    def remove_node(self, node_id):
        """Remove a node."""
        if node_id not in self.graph.nodes:
            return
        self.graph.remove_node(node_id)
        self.positions.pop(node_id, None)
        self.node_colors.pop(node_id, None)
        # Remove edges connected to the node
        self.edge_colors = {edge: color for edge, color in self.edge_colors.items() if node_id not in edge}
        self.update()

    def wait(self, duration):
        """Pause for a given duration."""
        sleep(int(duration))

    def execute_commands(self, filename):
        """Execute commands from a file."""
        with open(filename, "r") as file:
            commands = file.readlines()

        for command in commands:
            parts = command.strip().split()
            if not parts:
                continue

            action = parts[0]
            args = parts[1:]

            if action in self.commands:
                self.commands[action](*args)

        plt.ioff()
        plt.show()

if __name__ == "__main__":
    graph = Graph()
    graph.execute_commands("graph_commands.txt")

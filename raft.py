from graph import Graph
import random

class Raft:
    """Raft interface for reading and executing commands."""

    def __init__(self):
        self.graph = Graph(40)
        self.leader = None
        self.nodes = []

        self.commands = {
            "new": self.add_node,
            "election": self.start_election,
            "kill": self.kill_node,
            "kill_leader": self.kill_leader,
        }

    def add_node(self, node_id):
        """Add a new node to the graph and connect it to the others"""
        print("Adding node", node_id)

        if node_id in self.nodes:
            return

        self.graph.add_node(node_id)
        self.graph.complete_edges_for(node_id)
        
        self.nodes.append(node_id)

        if len(self.nodes) == 2:
            self.start_election()

    def start_election(self):
        """Start an election"""
        print("Starting election")

        if len(self.nodes) < 2:
            return

        self.graph.change_color("all", "yellow")
        self.graph.wait(1.3)

        winner = self.__pick_random_node()
        self.leader = winner

        print("Winner is", winner)

        self.graph.change_color(winner, "blue")
        self.graph.change_color(f"all-{winner}", "gray")

    def kill_node(self, node_id):
        """Kill a node"""
        print("Killing node", node_id)

        # I don't want to kill the last node
        if node_id not in self.nodes or len(self.nodes) == 1:
            return
        
        self.graph.remove_node(node_id)
        self.nodes.remove(node_id)

        if node_id == self.leader:
            self.__leader_was_killed()
        
        if self.nodes == 1:
            self.__only_one_node()

    def kill_leader(self):
        print("Killing leader: ", self.leader)
        """Kill the leader"""
        if not self.leader:
            return
        self.graph.wait(random.randint(1, 3))
        self.kill_node(self.leader)

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

        self.graph.wait(3)

    # *** Auxiliar Methods *** 

    def __leader_was_killed(self):
        """Kill the leader"""
        self.leader = None
        self.start_election()

    def __only_one_node(self):
        self.leader = self.nodes[0]
        self.graph.change_color(self.leader, "blue")

    def __pick_random_node(self):
        """Pick a random node."""
        return random.choice(self.nodes)

    def execute_random(self, num_commands, max_nodes):

        # Initial nodes
        self.add_node("node1")
        self.add_node("node2")
        self.add_node("node3")
        self.add_node("node4")

        for _ in range(num_commands):
            command, needs_argument = self.__get_random_command()
            node = "node" + str(random.randint(1, max_nodes))

            if needs_argument:
               command(node)
            else:
                command()

    def __get_random_command(self):
        # Available commands, because election is triggered, not called
        available_commands = {
            "new": (0.5, self.add_node),
            "kill": (0.3, self.kill_node),
            "kill_leader": (0.2, self.kill_leader),
        }

        commands = list(available_commands.keys())
        probabilities = list(map(lambda x: x[0], list(available_commands.values())))
        selected_command = random.choices(commands, probabilities, k=1)[0]
        return (available_commands[selected_command][1], self.__method_needs_argument(selected_command))

    def __method_needs_argument(self, method):
        return method in ["new", "kill"]
        

if __name__ == "__main__":
    raft = Raft()
    #raft.execute_commands("raft_commands.txt")

    raft.execute_random(50, 10)

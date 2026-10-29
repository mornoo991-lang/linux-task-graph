import csv
import tkinter as tk
from tkinter import messagebox

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


PROC_FILE = "/proc/task_graph"


def read_processes():
    processes = []

    with open(PROC_FILE, "r") as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) != 4:
                continue

            try:
                pid = int(row[0])
                ppid = int(row[1])
            except ValueError:
                continue

            processes.append({
                "pid": pid,
                "ppid": ppid,
                "name": row[2],
                "state": row[3]
            })

    return processes


class TaskGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Task Graph")
        self.root.geometry("1100x750")

        self.title = tk.Label(
            root,
            text="Linux Process Task Graph",
            font=("Arial", 20, "bold")
        )
        self.title.pack(pady=10)

        self.refresh_button = tk.Button(
            root,
            text="Refresh Processes",
            command=self.draw_graph
        )
        self.refresh_button.pack(pady=5)

        self.figure, self.ax = plt.subplots(figsize=(11, 7))

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=root
        )
        self.canvas.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True
        )

        self.draw_graph()

    def draw_graph(self):
        try:
            processes = read_processes()
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return

        graph = nx.DiGraph()

        # Хэт олон процесс харуулахад граф уншихад
        # хүндрэлтэй тул эхний 60 процессыг харуулна.
        for process in processes[:60]:
            pid = process["pid"]
            ppid = process["ppid"]

            graph.add_node(pid)
            graph.add_edge(ppid, pid)

        self.ax.clear()

        positions = nx.spring_layout(
            graph,
            seed=42
        )

        nx.draw(
            graph,
            positions,
            ax=self.ax,
            with_labels=True,
            node_color="skyblue",
            node_size=650,
            font_size=8,
            arrows=True
        )

        self.ax.set_title(
            f"Process Parent-Child Graph ({len(processes)} processes)"
        )

        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGraphApp(root)
    root.mainloop()

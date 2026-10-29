import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")

import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


PROC_FILE = "/proc/task_graph"
REFRESH_INTERVAL = 5000


def read_processes():
    processes = {}

    with open(PROC_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) != 4:
                continue

            try:
                pid = int(row[0])
                ppid = int(row[1])
            except ValueError:
                continue

            processes[pid] = {
                "pid": pid,
                "ppid": ppid,
                "name": row[2],
                "state": row[3]
            }

    return processes


class TaskGraphApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Linux Kernel Task Graph")
        self.root.geometry("1400x850")

        self.processes = {}
        self.selected_pid = None
        self.auto_refresh = tk.BooleanVar(value=True)
        self.search_var = tk.StringVar()
        self.state_var = tk.StringVar(value="All")

        self.setup_ui()
        self.refresh_data()
        self.schedule_refresh()

    def setup_ui(self):

        title = ttk.Label(
            self.root,
            text="Linux Kernel Process Task Graph",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=10)

        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill="x", padx=15, pady=5)

        ttk.Label(toolbar, text="Search:").pack(side="left")

        search_entry = ttk.Entry(
            toolbar,
            textvariable=self.search_var,
            width=25
        )
        search_entry.pack(side="left", padx=5)

        self.search_var.trace_add(
            "write",
            lambda *_: self.update_table()
        )

        ttk.Label(toolbar, text="State:").pack(
            side="left",
            padx=(15, 5)
        )

        self.state_combo = ttk.Combobox(
            toolbar,
            textvariable=self.state_var,
            values=["All"],
            width=12,
            state="readonly"
        )
        self.state_combo.pack(side="left")

        self.state_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.update_table()
        )

        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh_data
        ).pack(side="left", padx=10)

        ttk.Checkbutton(
            toolbar,
            text="Auto Refresh (5s)",
            variable=self.auto_refresh
        ).pack(side="left", padx=10)

        ttk.Button(
            toolbar,
            text="Export PNG",
            command=self.export_png
        ).pack(side="right")

        self.status_label = ttk.Label(
            self.root,
            text="Loading processes..."
        )
        self.status_label.pack(anchor="w", padx=15, pady=5)

        main_frame = ttk.PanedWindow(
            self.root,
            orient=tk.HORIZONTAL
        )
        main_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        left_frame = ttk.Frame(main_frame)
        right_frame = ttk.Frame(main_frame)

        main_frame.add(left_frame, weight=1)
        main_frame.add(right_frame, weight=2)

        # Process table

        columns = ("pid", "ppid", "name", "state")

        self.tree = ttk.Treeview(
            left_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("pid", text="PID")
        self.tree.heading("ppid", text="PPID")
        self.tree.heading("name", text="Process Name")
        self.tree.heading("state", text="State")

        self.tree.column("pid", width=65)
        self.tree.column("ppid", width=65)
        self.tree.column("name", width=170)
        self.tree.column("state", width=65)

        scrollbar = ttk.Scrollbar(
            left_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_process_select
        )

        # Graph

        self.figure = Figure(
            figsize=(8, 6),
            dpi=100
        )

        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=right_frame
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        self.details_label = ttk.Label(
            right_frame,
            text="Select a process from the table.",
            font=("Arial", 11)
        )
        self.details_label.pack(pady=10)

    def refresh_data(self):

        try:
            self.processes = read_processes()
        except OSError as error:
            messagebox.showerror(
                "Kernel Module Error",
                f"Cannot read {PROC_FILE}\n\n{error}"
            )
            return

        states = sorted({
            process["state"]
            for process in self.processes.values()
        })

        self.state_combo["values"] = ["All"] + states

        if self.state_var.get() not in ["All"] + states:
            self.state_var.set("All")

        self.update_table()

        if self.selected_pid in self.processes:
            self.draw_graph(self.selected_pid)
        else:
            self.selected_pid = None
            self.ax.clear()
            self.ax.set_title("Select a process")
            self.canvas.draw()
            self.details_label.config(
                text="Select a process from the table."
            )

    def update_table(self):

        selected = self.selected_pid

        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_var.get().strip().lower()
        selected_state = self.state_var.get()

        visible_count = 0

        for pid in sorted(self.processes):
            process = self.processes[pid]

            if search:
                if (
                    search not in str(pid)
                    and search not in process["name"].lower()
                ):
                    continue

            if selected_state != "All":
                if process["state"] != selected_state:
                    continue

            self.tree.insert(
                "",
                "end",
                iid=str(pid),
                values=(
                    process["pid"],
                    process["ppid"],
                    process["name"],
                    process["state"]
                )
            )

            visible_count += 1

        self.status_label.config(
            text=(
                f"Total Processes: {len(self.processes)}"
                f"  |  Visible: {visible_count}"
            )
        )

        if selected is not None:
            if self.tree.exists(str(selected)):
                self.tree.selection_set(str(selected))

    def on_process_select(self, event):

        selection = self.tree.selection()

        if not selection:
            return

        pid = int(selection[0])

        self.selected_pid = pid
        self.draw_graph(pid)

    def draw_graph(self, pid):

        if pid not in self.processes:
            return

        process = self.processes[pid]

        graph = nx.DiGraph()

        # Selected process
        graph.add_node(pid)

        # Parent process
        ppid = process["ppid"]

        if ppid != pid:
            graph.add_edge(ppid, pid)

        # Direct child processes
        for child in self.processes.values():
            if child["ppid"] == pid and child["pid"] != pid:
                graph.add_edge(pid, child["pid"])

        self.ax.clear()

        positions = nx.spring_layout(
            graph,
            seed=42
        )

        labels = {}

        for node in graph.nodes():
            if node in self.processes:
                name = self.processes[node]["name"]
                labels[node] = f"{node}\n{name}"
            else:
                labels[node] = str(node)

        colors = [
            "#ffb347" if node == pid else "#87ceeb"
            for node in graph.nodes()
        ]

        nx.draw_networkx(
            graph,
            positions,
            labels=labels,
            ax=self.ax,
            node_color=colors,
            node_size=1500,
            font_size=8,
            arrows=True,
            arrowsize=15,
            edge_color="#555555"
        )

        self.ax.set_title(
            f"Task Graph - PID {pid}: {process['name']}"
        )

        self.ax.axis("off")

        self.figure.tight_layout()
        self.canvas.draw()

        child_count = sum(
            1
            for child in self.processes.values()
            if child["ppid"] == pid and child["pid"] != pid
        )

        self.details_label.config(
            text=(
                f"PID: {pid}  |  "
                f"PPID: {ppid}  |  "
                f"Name: {process['name']}  |  "
                f"State: {process['state']}  |  "
                f"Children: {child_count}"
            )
        )

    def export_png(self):

        if self.selected_pid is None:
            messagebox.showwarning(
                "No Process",
                "Please select a process first."
            )
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialfile=f"task_graph_{self.selected_pid}.png"
        )

        if filename:
            try:
                self.figure.savefig(
                    filename,
                    dpi=200,
                    bbox_inches="tight"
                )
            except OSError as error:
                messagebox.showerror(
                    "Export Error",
                    str(error)
                )
                return

            messagebox.showinfo(
                "Export Complete",
                f"Graph saved:\n{filename}"
            )

    def schedule_refresh(self):

        if self.auto_refresh.get():
            self.refresh_data()

        self.root.after(
            REFRESH_INTERVAL,
            self.schedule_refresh
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGraphApp(root)
    root.mainloop()
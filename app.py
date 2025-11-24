import heapq
import itertools
import tkinter as tk
from tkinter import ttk, messagebox
from graphics import BridgeGraphics

def min_crossing_with_path(times, max_group):
    n = len(times)
    ALL = (1 << n) - 1
    start = (ALL, 0)
    target = (0, 1)
    pq = [(0, start)]
    dist = {start: 0}
    prev = {}
    while pq:
        cost, (mask, side) = heapq.heappop(pq)
        if dist.get((mask, side), float('inf')) < cost:
            continue
        if (mask, side) == target:
            path = []
            cur = target
            while cur != start:
                p = prev[cur]
                path.append(p[1])
                cur = p[0]
            path.reverse()
            steps = []
            cur_mask = ALL
            cur_side = 0
            for group in path:
                t = max(times[i] for i in group)
                direction = "->" if cur_side == 0 else "<-"
                participants = [i for i in group]
                steps.append((participants, direction, t))
                for i in group:
                    cur_mask ^= (1 << i)
                cur_side = 1 - cur_side
            return dist[target], steps
        torch_side_people = []
        for i in range(n):
            on_start = ((mask >> i) & 1) == 1
            if (side == 0 and on_start) or (side == 1 and not on_start):
                torch_side_people.append(i)
        for k in range(1, min(max_group, len(torch_side_people)) + 1):
            for group in itertools.combinations(torch_side_people, k):
                t = max(times[i] for i in group)
                new_mask = mask
                for i in group:
                    new_mask ^= (1 << i)
                new_side = 1 - side
                new_state = (new_mask, new_side)
                new_cost = cost + t
                if new_cost < dist.get(new_state, float('inf')):
                    dist[new_state] = new_cost
                    prev[new_state] = ((mask, side), group)
                    heapq.heappush(pq, (new_cost, new_state))
    return None, []

class App:
    def __init__(self, root):
        self.root = root
        root.title("Bridge & Torch — Animated")
        frm = ttk.Frame(root, padding=10)
        frm.grid(sticky="nw")
        ttk.Label(frm, text="Enter total number of people:").grid(column=0, row=0, sticky="w")
        self.entry_total = ttk.Entry(frm, width=20)
        self.entry_total.grid(column=0, row=1, sticky="w", pady=(0,6))
        ttk.Label(frm, text="Enter times (comma-separated):").grid(column=0, row=2, sticky="w")
        self.entry_times = ttk.Entry(frm, width=40)
        self.entry_times.grid(column=0, row=3, sticky="w", pady=(0,6))
        ttk.Label(frm, text="Max people crossing at once:").grid(column=0, row=4, sticky="w")
        self.entry_max = ttk.Entry(frm, width=20)
        self.entry_max.grid(column=0, row=5, sticky="w", pady=(0,6))
        compute_btn = ttk.Button(frm, text="Compute & Animate", command=self.on_compute)
        compute_btn.grid(column=1, row=3, padx=8)
        self.result_var = tk.StringVar(value="")
        ttk.Label(frm, textvariable=self.result_var, font=("Segoe UI", 10, "bold")).grid(column=0, row=6, columnspan=2, sticky="w", pady=(8,0))
        self.steps_text = tk.Text(frm, width=60, height=8, state="disabled")
        self.steps_text.grid(column=0, row=7, columnspan=2, pady=(6,0))
        self.graphics = BridgeGraphics(root)

    def on_compute(self):
        if self.graphics.animation_in_progress:
            messagebox.showinfo("Please wait", "Animation in progress. Wait for it to finish.")
            return
        try:
            total_people = int(self.entry_total.get().strip())
            if total_people <= 0:
                raise ValueError
        except:
            messagebox.showerror("Input error", "Enter a valid number of people.")
            return
        s = self.entry_times.get().strip()
        if not s:
            messagebox.showerror("Input error", "Enter times.")
            return
        try:
            times = [int(x.strip()) for x in s.split(",") if x.strip() != ""]
            if len(times) != total_people:
                messagebox.showerror("Input error", "Times count must equal total number of people.")
                return
        except:
            messagebox.showerror("Input error", "Enter comma-separated integers for times.")
            return
        try:
            max_group = int(self.entry_max.get().strip())
            if max_group < 1 or max_group > total_people:
                raise ValueError
        except:
            messagebox.showerror("Input error", "Enter a valid max crossing size.")
            return
        total, steps = min_crossing_with_path(times, max_group)
        if total is None:
            self.result_var.set("No solution.")
            return
        self.result_var.set(f"Minimal total time: {total}")
        self.steps_text.config(state="normal")
        self.steps_text.delete("1.0", "end")
        for i, (group, direction, t) in enumerate(steps, 1):
            participants = ", ".join(f"P{g+1}({times[g]})" for g in group)
            self.steps_text.insert("end", f"Step {i}: {participants} {direction} time {t}\n")
        self.steps_text.config(state="disabled")
        self.graphics.prepare_canvas(times)
        self.root.after(300, lambda: self.graphics.animate_steps(steps, times))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

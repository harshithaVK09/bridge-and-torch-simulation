import heapq
import itertools
import tkinter as tk
from tkinter import ttk, messagebox

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

class BridgeTorchApp:
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

        self.canvas = tk.Canvas(root, width=900, height=360, bg="#f5f5f5")
        self.canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.people_items = {}
        self.torch_item = None
        self.animation_in_progress = False

    def on_compute(self):
        if self.animation_in_progress:
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
        self.prepare_canvas(times)
        self.root.after(300, lambda: self.animate_steps(steps, times))

    def prepare_canvas(self, times):
        self.canvas.delete("all")
        n = len(times)
        left_x = 120
        right_x = 780
        y_gap = 40
        # bridge centered vertically
        bridge_y = 180
        # place people rows centered on bridge so movement stays on bridge
        y_start = bridge_y - (n - 1) * y_gap / 2 if n > 0 else bridge_y
        radius = 18

        # draw bridge first (so people render on top)
        self.canvas.create_rectangle(300, bridge_y-36, 600, bridge_y+36, fill="#d2b48c", outline="#7a5230")
        self.canvas.create_text(450, bridge_y-60, text="BRIDGE", font=("Segoe UI", 10, "bold"))

        self.positions = {}
        self.side = {i: 0 for i in range(n)}
        for i in range(n):
            y = y_start + i * y_gap
            x = left_x
            pid = self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill="#87ceeb", outline="#333")
            txt = self.canvas.create_text(x, y, text=f"P{i+1}", font=("Segoe UI", 10, "bold"))
            tlabel = self.canvas.create_text(x, y+22, text=str(times[i]), font=("Segoe UI", 9))
            self.people_items[i] = (pid, txt, tlabel)
            self.positions[i] = (x, y)

        torch_x = left_x + 40
        torch_y = bridge_y - 10
        self.torch_item = self.canvas.create_rectangle(torch_x-10, torch_y-10, torch_x+10, torch_y+10, fill="#ff8c00", outline="#333")
        self.torch_pos = (torch_x, torch_y)

        self.left_x = left_x
        self.right_x = right_x
        self.bridge_y = bridge_y

        for i in range(n):
            self.update_person_pos(i, left=True, instant=True)

    def update_person_pos(self, idx, left=True, instant=False):
        if left:
            tx = self.left_x
        else:
            tx = self.right_x
        ty = self.positions[idx][1]
        pid, txt, tlabel = self.people_items[idx]
        if instant:
            self.canvas.coords(pid, tx-18, ty-18, tx+18, ty+18)
            self.canvas.coords(txt, tx, ty)
            self.canvas.coords(tlabel, tx, ty+22)
        else:
            self.canvas.coords(pid, tx-18, ty-18, tx+18, ty+18)
            self.canvas.coords(txt, tx, ty)
            self.canvas.coords(tlabel, tx, ty+22)

    def animate_steps(self, steps, times):
        self.animation_in_progress = True
        seq = list(steps)

        def run_step(i):
            if i >= len(seq):
                self.animation_in_progress = False
                return

            group, direction, t = seq[i]

            # animation speed: 700 ms per time unit (clamped)
            duration = max(1000, min(9000, t * 700))
            frames = max(10, int(duration / 30))

            # For each person use their row (y) so movement is straight horizontal along that y
            if direction == "->":
                start_positions = {g: (self.left_x, self.positions[g][1]) for g in group}
                end_x = self.right_x
            else:
                start_positions = {g: (self.right_x, self.positions[g][1]) for g in group}
                end_x = self.left_x

            # torch will be centered vertically on the group's average y
            group_ys = [self.positions[g][1] for g in group]
            if group_ys:
                torch_y = sum(group_ys) / len(group_ys)
            else:
                torch_y = self.bridge_y - 10

            torch_start = (self.torch_pos[0], self.torch_pos[1])
            if direction == "->":
                torch_end = (end_x - 40, torch_y)
            else:
                torch_end = (end_x + 40, torch_y)

            deltas = {g: (end_x - start_positions[g][0]) for g in group}
            torch_dx = (torch_end[0] - torch_start[0])

            frame = 0

            def animate_frame():
                nonlocal frame
                if frame >= frames:
                    # place people exactly at final x (their own y row)
                    for g in group:
                        self.side[g] = 0 if direction == "<-" else 1
                        self.update_person_pos(g, left=(self.side[g] == 0), instant=True)

                    # update torch final position
                    self.torch_pos = (torch_end[0], torch_end[1])
                    self.canvas.coords(self.torch_item, torch_end[0]-10, torch_end[1]-10, torch_end[0]+10, torch_end[1]+10)

                    # short pause then next step
                    self.root.after(400, lambda: run_step(i + 1))
                    return

                p = frame / frames

                for g in group:
                    sx, sy = start_positions[g]
                    dx = deltas[g]
                    nx = sx + dx * p
                    ny = sy  # straight horizontal line at person's row

                    pid, txt, tlabel = self.people_items[g]
                    self.canvas.coords(pid, nx - 18, ny - 18, nx + 18, ny + 18)
                    self.canvas.coords(txt, nx, ny)
                    self.canvas.coords(tlabel, nx, ny + 22)

                # torch moves horizontally and stays at group's vertical center
                tnx = torch_start[0] + torch_dx * p
                tny = torch_y
                self.torch_pos = (tnx, tny)
                self.canvas.coords(self.torch_item, tnx-10, tny-10, tnx+10, tny+10)

                frame += 1
                self.root.after(30, animate_frame)

            animate_frame()

        run_step(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = BridgeTorchApp(root)
    root.mainloop()

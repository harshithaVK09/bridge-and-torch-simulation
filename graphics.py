import tkinter as tk

class BridgeGraphics:
    def __init__(self, parent, width=900, height=360):
        self.canvas = tk.Canvas(parent, width=width, height=height, bg="#f5f5f5")
        self.canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.people_items = {}
        self.torch_item = None
        self.animation_in_progress = False

    def prepare_canvas(self, times):
        self.canvas.delete("all")
        n = len(times)
        left_x = 120
        right_x = 780
        y_gap = 40
        bridge_y = 180
        y_start = bridge_y - (n - 1) * y_gap / 2 if n > 0 else bridge_y
        radius = 18
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
            duration = max(1000, min(9000, t * 700))
            frames = max(10, int(duration / 30))
            if direction == "->":
                start_positions = {g: (self.left_x, self.positions[g][1]) for g in group}
                end_x = self.right_x
            else:
                start_positions = {g: (self.right_x, self.positions[g][1]) for g in group}
                end_x = self.left_x
            group_ys = [self.positions[g][1] for g in group]
            torch_y = sum(group_ys) / len(group_ys) if group_ys else self.bridge_y - 10
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
                    for g in group:
                        self.side[g] = 0 if direction == "<-" else 1
                        self.update_person_pos(g, left=(self.side[g] == 0), instant=True)
                    self.torch_pos = (torch_end[0], torch_end[1])
                    self.canvas.coords(self.torch_item, torch_end[0]-10, torch_end[1]-10, torch_end[0]+10, torch_end[1]+10)
                    self.canvas.update()
                    self.canvas.after(400, lambda: run_step(i + 1))
                    return
                p = frame / frames
                for g in group:
                    sx, sy = start_positions[g]
                    dx = deltas[g]
                    nx = sx + dx * p
                    ny = sy
                    pid, txt, tlabel = self.people_items[g]
                    self.canvas.coords(pid, nx - 18, ny - 18, nx + 18, ny + 18)
                    self.canvas.coords(txt, nx, ny)
                    self.canvas.coords(tlabel, nx, ny + 22)
                tnx = torch_start[0] + torch_dx * p
                tny = torch_y
                self.torch_pos = (tnx, tny)
                self.canvas.coords(self.torch_item, tnx-10, tny-10, tnx+10, tny+10)
                frame += 1
                self.canvas.after(30, animate_frame)
            animate_frame()
        run_step(0)

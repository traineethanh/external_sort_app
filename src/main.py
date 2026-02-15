import tkinter as tk
from tkinter import messagebox, filedialog
import os
import utils
from algorithms import ExternalSort

class FinalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("External Sort Simulation - Quang Thanh")
        self.canvas = tk.Canvas(root, width=800, height=550, bg="white")
        self.canvas.pack()
        
        self.init_ui()
        self.sorter = ExternalSort()
        self.run_objs = {} 

    def init_ui(self):
        # Nhan trang thai
        self.status = tk.Label(self.root, text="San sang...", font=("Arial", 10))
        self.status.pack(pady=5)
        
        # Nut dieu khien
        btn_frame = tk.Frame(self.root)
        btn_frame.pack()
        tk.Button(btn_frame, text="TAO FILE NGAU NHIEN", command=self.gen_data).pack(side="left", padx=5)
        self.btn_start = tk.Button(btn_frame, text="BAT DAU", command=self.start, state="disabled", bg="#0078D7", fg="white")
        self.btn_start.pack(side="left", padx=5)

        # Ve khung vung nho [cite: 43, 44, 45]
        self.draw_layout()

    def draw_layout(self):
        self.canvas.delete("all")
        # Output Disk
        self.canvas.create_rectangle(50, 20, 750, 150, outline="green", width=2)
        self.canvas.create_text(400, 10, text="Buffer Disk (Output)", font=("Arial", 10, "bold"))
        # RAM [cite: 18]
        self.canvas.create_rectangle(200, 190, 600, 310, outline="blue", width=2)
        self.canvas.create_text(400, 175, text="Main Memory (RAM)", font=("Arial", 10, "bold"))
        # Input Disk
        self.canvas.create_rectangle(50, 380, 750, 510, outline="black", width=2)
        self.canvas.create_text(400, 365, text="Input Disk", font=("Arial", 10, "bold"))

    def create_block(self, x, y, val):
        """Tao block xam dam chu vang cam nhu anh mau."""
        r = self.canvas.create_rectangle(x, y, x+75, y+40, fill="#4A4A4A", outline="#707070", width=2)
        t = self.canvas.create_text(x+37, y+20, text=f"{val:.1f}", fill="#FFCC00", font=("Arial", 9, "bold"))
        return r, t

    def move_item(self, obj, tx, ty, callback=None):
        """Di chuyen block muot ma qua 15 buoc nho."""
        r_id, t_id = obj
        curr = self.canvas.coords(r_id)
        if not curr: return
        steps = 15
        dx, dy = (tx - curr[0]) / steps, (ty - curr[1]) / steps
        def anim(step):
            if step < steps:
                self.canvas.move(r_id, dx, dy); self.canvas.move(t_id, dx, dy)
                self.root.after(20, lambda: anim(step + 1))
            elif callback: callback()
        anim(0)

    def run_steps(self, steps_list):
        if not steps_list:
            self.status.config(text="HOAN TAT!", fg="blue"); return
        
        s = steps_list.pop(0)
        self.status.config(text=s['desc'])

        if s['act'] == 'INIT_DISK':
            self.data_objs = []
            for i, v in enumerate(s['values']):
                self.data_objs.append(self.create_block(65 + (i%8)*85, 400 + (i//8)*50, v))
            self.root.after(1000, lambda: self.run_steps(steps_list))

        elif s['act'] == 'READ':
            self.ram_objs = []
            for i in range(len(s['values'])):
                obj = self.data_objs[s['idx'] + i]
                self.move_item(obj, 220 + i*90, 220)
                self.ram_objs.append(obj)
            self.root.after(1200, lambda: self.run_steps(steps_list))

        elif s['act'] == 'SORT':
            for i, obj in enumerate(self.ram_objs):
                self.canvas.itemconfig(obj[1], text=f"{s['values'][i]:.1f}")
                self.canvas.itemconfig(obj[0], fill="#3498DB")
            self.root.after(800, lambda: self.run_steps(steps_list))

        elif s['act'] == 'WRITE_RUN':
            idx = s['run_idx']; self.run_objs[idx] = []
            for obj in self.ram_objs:
                tx = 60 + idx*230 + len(self.run_objs[idx])*40
                self.move_item(obj, tx, 50); self.run_objs[idx].append(obj)
            self.root.after(1200, lambda: self.run_steps(steps_list))

        elif s['act'] == 'LOAD_FOR_MERGE':
            self.ram_objs = self.run_objs[s['r1_idx']] + self.run_objs[s['r2_idx']]
            for i, obj in enumerate(self.ram_objs):
                self.move_item(obj, 210 + i*45, 220)
                self.canvas.itemconfig(obj[0], fill="#E74C3C")
            self.root.after(1500, lambda: self.run_steps(steps_list))

        elif s['act'] == 'SAVE_MERGED':
            for i, obj in enumerate(self.ram_objs):
                self.canvas.itemconfig(obj[1], text=f"{s['values'][i]:.1f}")
                self.move_item(obj, 100 + i*50, 50)
                self.canvas.itemconfig(obj[0], fill="#2ECC71")
            self.run_objs = {0: self.ram_objs}
            self.root.after(1500, lambda: self.run_steps(steps_list))
        
        else: self.root.after(500, lambda: self.run_steps(steps_list))

    def gen_data(self):
        self.input_file = utils.create_random_input()
        self.status.config(text="Da tao file 12 so ngau nhien", fg="green")
        self.btn_start.config(state="normal")

    def start(self):
        self.draw_layout(); self.run_objs = {}
        target = getattr(self, 'input_file', 'input_test.bin')
        steps = self.sorter.get_full_animation_steps(target)
        self.run_steps(steps)

if __name__ == "__main__":
    root = tk.Tk(); app = FinalApp(root); root.mainloop()
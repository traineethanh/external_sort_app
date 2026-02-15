import tkinter as tk
from tkinter import messagebox, filedialog
import os
import utils
from algorithms import ExternalSort

class FinalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UIT - External Sort Animation")
        self.canvas = tk.Canvas(root, width=800, height=550, bg="white")
        self.canvas.pack()
        
        self.setup_ui()
        self.sorter = ExternalSort()
        self.run_objs = {} # Luu cac block theo tung Run

    def setup_ui(self):
        # Ve bo cuc co dinh: Disk - RAM - Disk 
        self.canvas.create_rectangle(50, 20, 750, 150, outline="green", width=2) # Output
        self.canvas.create_text(400, 10, text="BUFFER DISK (OUTPUT)", font=("Arial", 10, "bold"), fill="green")
        
        self.canvas.create_rectangle(200, 190, 600, 310, outline="blue", width=2) # RAM
        self.canvas.create_text(400, 175, text="MAIN MEMORY (RAM BUFFER)", font=("Arial", 10, "bold"), fill="blue")
        
        self.canvas.create_rectangle(50, 380, 750, 510, outline="black", width=2) # Input
        self.canvas.create_text(400, 365, text="INPUT DISK (STORAGE)", font=("Arial", 10, "bold"))

        self.status = tk.Label(self.root, text="San sang...", font=("Arial", 11))
        self.status.pack(pady=5)

        # Thanh dieu khien
        frame = tk.Frame(self.root)
        frame.pack()
        tk.Button(frame, text="TAO 12 SO NGAU NHIEN", command=self.gen_data).pack(side="left", padx=5)
        self.btn_start = tk.Button(frame, text="BAT DAU MO PHONG", command=self.start, state="disabled", bg="#0078D7", fg="white")
        self.btn_start.pack(side="left", padx=5)

    def create_block(self, x, y, val):
        # Style: Block xam dam, chu vang theo mau ban gui 
        r = self.canvas.create_rectangle(x, y, x+75, y+40, fill="#4A4A4A", outline="#707070", width=2)
        t = self.canvas.create_text(x+37, y+20, text=f"{val:.1f}", fill="#FFCC00", font=("Arial", 9, "bold"))
        return r, t

    def move_item(self, obj, tx, ty, callback=None):
        r_id, t_id = obj
        curr = self.canvas.coords(r_id)
        if not curr: return
        steps = 15
        dx, dy = (tx - curr[0]) / steps, (ty - curr[1]) / steps
        def anim(count):
            if count < steps:
                self.canvas.move(r_id, dx, dy); self.canvas.move(t_id, dx, dy)
                self.root.after(20, lambda: anim(count + 1))
            elif callback: callback()
        anim(0)

    def run_steps(self, steps):
        if not steps:
            self.status.config(text="MO PHONG HOAN TAT!", fg="blue"); return
        
        s = steps.pop(0)
        self.status.config(text=s['desc'])

        if s['act'] == 'INIT_DISK':
            self.data_objs = []
            for i, v in enumerate(s['values']):
                start_x, start_y = 65 + (i % 8) * 85, 400 + (i // 8) * 50
                self.data_objs.append(self.create_block(start_x, start_y, v))
            self.root.after(1000, lambda: self.run_steps(steps))

        elif s['act'] == 'READ':
            self.ram_objs = []
            for i in range(len(s['values'])):
                obj = self.data_objs[s['idx'] + i]
                self.move_item(obj, 220 + i*90, 220)
                self.ram_objs.append(obj)
            self.root.after(1200, lambda: self.run_steps(steps))

        elif s['act'] == 'WRITE_RUN':
            idx = s['run_idx']; self.run_objs[idx] = []
            for obj in self.ram_objs:
                tx = 60 + idx*230 + len(self.run_objs[idx])*40
                self.move_item(obj, tx, 50)
                self.run_objs[idx].append(obj)
            self.root.after(1200, lambda: self.run_steps(steps))

        elif s['act'] == 'LOAD_FOR_MERGE':
            self.ram_objs = self.run_objs[s['r1_idx']] + self.run_objs[s['r2_idx']]
            for i, obj in enumerate(self.ram_objs):
                self.move_item(obj, 210 + i*45, 220)
                self.canvas.itemconfig(obj[0], fill="#E74C3C") # Doi mau khi dang tron
            self.root.after(1500, lambda: self.run_steps(steps))

        elif s['act'] == 'SAVE_MERGED':
            for i, obj in enumerate(self.ram_objs):
                self.canvas.itemconfig(obj[1], text=f"{s['values'][i]:.1f}")
                self.move_item(obj, 150 + i*50, 50)
                self.canvas.itemconfig(obj[0], fill="#2ECC71") # Xanh la khi xong
            self.run_objs = {0: self.ram_objs}
            self.root.after(1500, lambda: self.run_steps(steps))
        
        else: self.root.after(600, lambda: self.run_steps(steps))

    def gen_data(self):
        self.input_file = utils.create_random_input()
        self.status.config(text="Da tao file 12 so ngau nhien. Bam 'BAT DAU'!", fg="blue")
        self.btn_start.config(state="normal")

    def start(self):
        self.canvas.delete("all"); self.setup_ui(); self.run_objs = {}
        target = getattr(self, 'input_file', 'input_test.bin')
        steps = self.sorter.get_full_animation_steps(target)
        self.run_steps(steps)

if __name__ == "__main__":
    root = tk.Tk(); app = FinalApp(root); root.mainloop()
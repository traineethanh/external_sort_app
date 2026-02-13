import tkinter as tk
from tkinter import messagebox
import utils
from algorithms import ExternalSort

class FinalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UIT - External Sort Full Process")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        self.setup_ui()
        self.sorter = ExternalSort()
        self.run_objs = {} # Luu cac khoi theo Run

    def setup_ui(self):
        self.canvas.create_rectangle(50, 20, 750, 150, outline="green", width=2) # Output [cite: 111]
        self.canvas.create_rectangle(200, 200, 600, 320, outline="blue", width=2) # RAM [cite: 104]
        self.canvas.create_rectangle(50, 450, 750, 580, outline="black", width=2) # Input [cite: 106]
        self.status = tk.Label(self.root, text="San sang...", font=("Arial", 11))
        self.status.pack()
        tk.Button(self.root, text="BAT DAU QUY TRINH", command=self.start).pack()

    def move_item(self, item_id, tx, ty, callback=None):
        c = self.canvas.coords(item_id)
        if not c: return
        dx, dy = (tx - c[0]) / 10, (ty - c[1]) / 10
        def anim(step):
            if step < 10:
                self.canvas.move(item_id, dx, dy); self.root.after(20, lambda: anim(step+1))
            elif callback: callback()
        anim(0)

    def run_steps(self, steps):
        if not steps:
            self.status.config(text="CHUC MUNG! DA XONG HOAN TOAN.")
            return
        
        s = steps.pop(0)
        self.status.config(text=s['desc'])

        if s['act'] == 'INIT_DISK':
            self.data_objs = []
            for i, v in enumerate(s['values']):
                r = self.canvas.create_rectangle(70+i*55, 480, 115+i*55, 525, fill="#FFD700")
                t = self.canvas.create_text(92+i*55, 502, text=str(int(v)))
                self.data_objs.append((r, t))
            self.root.after(800, lambda: self.run_steps(steps))

        elif s['act'] == 'WRITE_RUN':
            idx = s['run_idx']; self.run_objs[idx] = []
            for i, (r, t) in enumerate(self.ram_objs):
                tx = 60 + idx*230 + i*45
                self.move_item(r, tx, 50); self.move_item(t, tx+20, 72)
                self.run_objs[idx].append((r, t))
            self.root.after(1000, lambda: self.run_steps(steps))

        elif s['act'] == 'LOAD_FOR_MERGE':
            # Keo 2 run ve RAM de tron [cite: 119]
            self.ram_objs = self.run_objs[s['r1_idx']] + self.run_objs[s['r2_idx']]
            for i, (r, t) in enumerate(self.ram_objs):
                self.move_item(r, 210+i*40, 220); self.move_item(t, 232+i*40, 242)
                self.canvas.itemconfig(r, fill="#FF6347")
            self.root.after(1500, lambda: self.run_steps(steps))

        elif s['act'] == 'SAVE_MERGED':
            # Ghi ket qua dải màu xanh lá 
            for i, (r, t) in enumerate(self.ram_objs):
                self.canvas.itemconfig(t, text=str(int(s['values'][i])))
                tx = 80 + i*48
                self.move_item(r, tx, 50); self.move_item(t, tx+22, 72)
                self.canvas.itemconfig(r, fill="#32CD32")
            # Cap nhat lai danh sach run moi de Pass sau co the dung
            self.run_objs = {0: self.ram_objs} 
            self.root.after(1500, lambda: self.run_steps(steps))
        
        else: # READ, SORT, SKIP_LE
            self.root.after(800, lambda: self.run_steps(steps))

    def start(self):
        self.canvas.delete("all"); self.setup_ui(); self.run_objs = {}
        utils.create_sample_binary()
        steps = self.sorter.get_full_animation_steps("input_test.bin")
        self.run_steps(steps)

if __name__ == "__main__":
    root = tk.Tk(); app = FinalApp(root); root.mainloop()
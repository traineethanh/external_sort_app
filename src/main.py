import tkinter as tk
from tkinter import messagebox, filedialog
import os
import utils
from algorithms import ExternalSort

class FinalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UIT - External Sort Animation - Quang Thanh")
        
        # UI Components
        self.init_control_panel()
        self.canvas = tk.Canvas(root, width=800, height=550, bg="white")
        self.canvas.pack()
        
        self.draw_layout()
        self.sorter = ExternalSort()
        self.run_objs = {} 

    def init_control_panel(self):
        self.status = tk.Label(self.root, text="Vui long tao file hoac chon file", font=("Arial", 10))
        self.status.pack(pady=5)

        frame = tk.Frame(self.root)
        frame.pack()
        
        tk.Button(frame, text="TAO FILE NGAU NHIEN", command=self.gen_file, bg="#E1E1E1").pack(side="left", padx=5)
        tk.Button(frame, text="CHON FILE NGOAI", command=self.choose_file, bg="#F0F0F0").pack(side="left", padx=5)
        self.btn_start = tk.Button(frame, text="BAT DAU SAP XEP", command=self.start, state="disabled", bg="#0078D7", fg="white")
        self.btn_start.pack(side="left", padx=5)

    def draw_layout(self):
        self.canvas.delete("all")
        # Buffer Disk (Output)
        self.canvas.create_rectangle(50, 20, 750, 150, outline="green", width=2)
        self.canvas.create_text(400, 10, text="Buffer Disk (Output)", font=("Arial", 10, "bold"), fill="green")
        
        # RAM
        self.canvas.create_rectangle(200, 190, 600, 310, outline="blue", width=2)
        self.canvas.create_text(400, 175, text="RAM / Main Memory", font=("Arial", 10, "bold"), fill="blue")
        
        # Disk (Input)
        self.canvas.create_rectangle(50, 380, 750, 510, outline="black", width=2)
        self.canvas.create_text(400, 365, text="Input Disk", font=("Arial", 10, "bold"), fill="black")

    def create_block(self, x, y, val):
        # Style: Xam dam, chu vang cam theo mau ban gui
        w, h = 75, 40
        r = self.canvas.create_rectangle(x, y, x+w, y+h, fill="#4A4A4A", outline="#707070", width=2)
        t = self.canvas.create_text(x+w/2, y+h/2, text=f"{val:.1f}", fill="#FFCC00", font=("Arial", 10, "bold"))
        return r, t

    def gen_file(self):
        self.input_file = utils.create_random_input()
        self.status.config(text="Da tao file 12 so ngau nhien", fg="blue")
        self.btn_start.config(state="normal")

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Binary", "*.bin")])
        if path:
            self.input_file = path
            self.status.config(text=f"Da chon: {os.path.basename(path)}", fg="green")
            self.btn_start.config(state="normal")

    def move_item(self, item_pair, tx, ty, callback=None):
        r_id, t_id = item_pair
        curr = self.canvas.coords(r_id)
        if not curr: return
        steps = 15
        dx, dy = (tx - curr[0]) / steps, (ty - curr[1]) / steps
        
        def anim(count):
            if count < steps:
                self.canvas.move(r_id, dx, dy)
                self.canvas.move(t_id, dx, dy)
                self.root.after(20, lambda: anim(count + 1))
            elif callback: callback()
        anim(0)

    def run_steps(self, steps):
        if not steps:
            self.status.config(text="DA XONG HOAN TOAN!", fg="blue")
            return
        
        s = steps.pop(0)
        self.status.config(text=s['desc'])

        if s['act'] == 'INIT_DISK':
            self.data_objs = []
            for i, v in enumerate(s['values']):
                start_x, start_y = 65 + (i % 8) * 85, 395 + (i // 8) * 50
                self.data_objs.append(self.create_block(start_x, start_y, v))
            self.root.after(1000, lambda: self.run_steps(steps))

        elif s['act'] == 'READ':
            self.ram_objs = []
            for i in range(len(s['values'])):
                obj = self.data_objs[s['idx'] + i]
                self.move_item(obj, 220 + i*90, 220)
                self.ram_objs.append(obj)
            self.root.after(1200, lambda: self.run_steps(steps))

        elif s['act'] == 'SORT':
            for i, obj in enumerate(self.ram_objs):
                self.canvas.itemconfig(obj[1], text=f"{s['values'][i]:.1f}")
                self.canvas.itemconfig(obj[0], fill="#3498DB") # Doi mau khi dang sort
            self.root.after(800, lambda: self.run_steps(steps))

        elif s['act'] == 'WRITE_RUN':
            idx = s['run_idx']; self.run_objs[idx] = []
            for i, obj in enumerate(self.ram_objs):
                tx = 60 + idx*230 + i*40
                self.move_item(obj, tx, 50)
                self.run_objs[idx].append(obj)
            self.root.after(1200, lambda: self.run_steps(steps))

        elif s['act'] == 'LOAD_FOR_MERGE':
            self.ram_objs = self.run_objs[s['r1_idx']] + self.run_objs[s['r2_idx']]
            for i, obj in enumerate(self.ram_objs):
                self.move_item(obj, 210 + i*45, 220)
                self.canvas.itemconfig(obj[0], fill="#E74C3C") # Mau dang tron
            self.root.after(1500, lambda: self.run_steps(steps))

        elif s['act'] == 'SAVE_MERGED':
            for i, obj in enumerate(self.ram_objs):
                self.canvas.itemconfig(obj[1], text=f"{s['values'][i]:.1f}")
                self.move_item(obj, 100 + i*50, 50)
                self.canvas.itemconfig(obj[0], fill="#2ECC71") # Mau hoan tat
            self.run_objs = {0: self.ram_objs}
            self.root.after(1500, lambda: self.run_steps(steps))
        
        else: self.root.after(600, lambda: self.run_steps(steps))

    def start(self):
        self.draw_layout()
        self.run_objs = {}
        target = getattr(self, 'input_file', 'input_test.bin')
        try:
            steps = self.sorter.get_full_animation_steps(target)
            self.run_steps(steps)
        except Exception as e:
            messagebox.showerror("Loi", str(e))

if __name__ == "__main__":
    root = tk.Tk(); app = FinalApp(root); root.mainloop()
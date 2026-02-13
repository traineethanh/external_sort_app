import tkinter as tk
from tkinter import ttk, messagebox
import utils
from algorithms import ExternalSort
import os

class SmoothAnimationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UIT - External Sort Full Motion - Quang Thanh")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        
        self.sorter = ExternalSort()
        self.setup_layout()
        self.data_objects = {}  # Luu tru cac block du lieu goc
        self.run_objects = {}   # Luu tru cac block du lieu trong cac Run

    def setup_layout(self):
        # 1. Vung Disk Goc (Duoi cung)
        self.canvas.create_rectangle(50, 450, 750, 580, outline="black", width=2)
        self.canvas.create_text(400, 435, text="INPUT DISK (DU LIEU BAN DAU)", font=("Arial", 10, "bold"))
        
        # 2. Vung RAM / Buffer (O giua)
        self.canvas.create_rectangle(200, 200, 600, 320, outline="blue", width=2, fill="#F0F8FF")
        self.canvas.create_text(400, 185, text="MAIN MEMORY (RAM BUFFER)", font=("Arial", 10, "bold"))
        
        # 3. Vung Disk Tam / Output (Tren cung)
        self.canvas.create_rectangle(50, 20, 750, 150, outline="green", width=2)
        self.canvas.create_text(400, 10, text="OUTPUT DISK (SORTED RUNS / BUFFER)", font=("Arial", 10, "bold"))
        
        # Su dung tieng Viet khong dau de tranh loi 'charmap' encode
        self.desc_label = tk.Label(self.root, text="Nhan nut de bat dau mo phong chuyen dong", font=("Arial", 11))
        self.desc_label.pack(pady=10)
        
        tk.Button(self.root, text="CHAY MO PHONG TOAN QUY TRINH", command=self.start, bg="#0078D7", fg="white", font=("Arial", 10, "bold")).pack()

    def move_item(self, item_id, tx, ty, callback=None):
        """Di chuyen vat the muot ma den toa do dich."""
        curr = self.canvas.coords(item_id)
        if not curr: return
        dx, dy = (tx - curr[0]) / 10, (ty - curr[1]) / 10
        def animate(c):
            if c < 10:
                self.canvas.move(item_id, dx, dy)
                self.root.after(20, lambda: animate(c+1))
            elif callback:
                callback()
        animate(0)

    def run_steps(self, steps):
        """Bo dieu phoi animation xu ly tung buoc 'act'."""
        if not steps: 
            self.desc_label.config(text="CHUC MUNG! DA SAP XEP XONG HOAN TOAN")
            messagebox.showinfo("Hoan tat", "Quy trinh sap xep ngoai da ket thuc!")
            return
        
        s = steps.pop(0)
        # Chuyen mo ta sang tieng Viet khong dau
        self.desc_label.config(text=s['desc'])

        if s['act'] == 'INIT_DISK':
            for i, v in enumerate(s['values']):
                rect = self.canvas.create_rectangle(70+i*55, 480, 120+i*55, 530, fill="#FFD700")
                txt = self.canvas.create_text(95+i*55, 505, text=str(int(v)))
                self.data_objects[i] = (rect, txt)
            self.root.after(1000, lambda: self.run_steps(steps))

        elif s['act'] == 'READ':
            self.current_ram_objs = []
            for i in range(len(s['values'])):
                r, t = self.data_objects[s['idx'] + i]
                self.move_item(r, 220+i*95, 220)
                self.move_item(t, 245+i*95, 245)
                self.current_ram_objs.append((r, t))
            self.root.after(1500, lambda: self.run_steps(steps))

        elif s['act'] == 'SORT':
            for i, (r, t) in enumerate(self.current_ram_objs):
                self.canvas.itemconfig(t, text=str(int(s['values'][i])))
                self.canvas.itemconfig(r, fill="#00BFFF")
            self.root.after(1000, lambda: self.run_steps(steps))

        elif s['act'] == 'WRITE_RUN':
            run_list = []
            for i, (r, t) in enumerate(self.current_ram_objs):
                tx = 60 + s['run_idx']*230 + i*50
                self.move_item(r, tx, 50)
                self.move_item(t, tx+25, 75)
                run_list.append((r, t))
            self.run_objects[s['run_idx']] = run_list
            self.root.after(1500, lambda: self.run_steps(steps))

        elif s['act'] == 'LOAD_FOR_MERGE':
            # Lay cac khoi tu 2 run bay xuong RAM [cite: 104, 118]
            objs_to_move = self.run_objects[s['r1_idx']] + self.run_objects[s['r2_idx']]
            for i, (r, t) in enumerate(objs_to_move):
                self.move_item(r, 210+i*45, 220)
                self.move_item(t, 235+i*45, 245)
                self.canvas.itemconfig(r, fill="#FF6347") 
            self.current_ram_objs = objs_to_move
            self.root.after(2000, lambda: self.run_steps(steps))

        elif s['act'] == 'SAVE_MERGED':
            # Ghi ket qua tron cuoi cung [cite: 42, 589]
            merged_objs = []
            for i, (r, t) in enumerate(self.current_ram_objs):
                self.canvas.itemconfig(t, text=str(int(s['values'][i])))
                tx = 100 + i*48
                self.move_item(r, tx, 50)
                self.move_item(t, tx+24, 75)
                self.canvas.itemconfig(r, fill="#32CD32")
                merged_objs.append((r, t))
            # Cap nhat lai run_objects de Pass sau co the dung tiep
            self.run_objects = {0: merged_objs}
            self.root.after(2000, lambda: self.run_steps(steps))

        elif s['act'] == 'SKIP_LE':
            self.root.after(800, lambda: self.run_steps(steps))

    def start(self):
        self.canvas.delete("all")
        self.data_objects = {}
        self.run_objects = {}
        self.setup_layout()
        utils.create_sample_binary() 
        try:
            # Dung logic tron den khi con 1 file duy nhat [cite: 256, 584]
            steps = self.sorter.get_full_animation_steps("input_test.bin")
            self.run_steps(steps)
        except Exception as e:
            messagebox.showerror("Loi", f"Khong the lay du lieu hoat anh: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SmoothAnimationApp(root)
    root.mainloop()
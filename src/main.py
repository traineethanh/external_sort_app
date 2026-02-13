import tkinter as tk
from tkinter import messagebox
import utils
from algorithms import ExternalSort

class FinalApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        self.setup_ui()
        self.sorter = ExternalSort()
        self.run_items = {} # Lưu trữ các block theo từng Run

    def setup_ui(self):
        # Vẽ 3 vùng: Disk Tạm (Trên), RAM (Giữa), Disk Gốc (Dưới)
        self.canvas.create_rectangle(50, 20, 750, 150, outline="green", width=2) # Output
        self.canvas.create_rectangle(200, 200, 600, 320, outline="blue", width=2) # RAM
        self.canvas.create_rectangle(50, 450, 750, 580, outline="black", width=2) # Input
        
        self.status = tk.Label(self.root, text="Sẵn sàng...", font=("Arial", 11))
        self.status.pack()
        tk.Button(self.root, text="CHẠY TOÀN QUY TRÌNH", command=self.start).pack()

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
            self.status.config(text="CHÚC MỪNG! ĐÃ XONG.")
            return
        
        s = steps.pop(0)
        self.status.config(text=s['desc'])

        if s['act'] == 'INIT_DISK':
            self.data_objs = []
            for i, v in enumerate(s['values']):
                r = self.canvas.create_rectangle(70+i*55, 480, 115+i*55, 525, fill="#FFD700")
                t = self.canvas.create_text(92+i*55, 502, text=str(int(v)))
                self.data_objs.append((r, t))
            self.root.after(1000, lambda: self.run_steps(steps))

        elif s['act'] == 'READ':
            self.ram_objs = []
            for i in range(len(s['values'])):
                r, t = self.data_objs[s['idx'] + i]
                self.move_item(r, 220+i*100, 220); self.move_item(t, 242+i*100, 242)
                self.ram_objs.append((r, t))
            self.root.after(1500, lambda: self.run_steps(steps))

        elif s['act'] == 'SORT':
            for i, (r, t) in enumerate(self.ram_objs):
                self.canvas.itemconfig(t, text=str(int(s['values'][i])))
                self.canvas.itemconfig(r, fill="#81D4FA")
            self.root.after(1000, lambda: self.run_steps(steps))

        elif s['act'] == 'WRITE_RUN':
            run_idx = s['run_idx']
            self.run_items[run_idx] = []
            for i, (r, t) in enumerate(self.ram_objs):
                tx = 60 + run_idx*230 + i*45
                self.move_item(r, tx, 50); self.move_item(t, tx+20, 72)
                self.run_items[run_idx].append((r, t))
            self.root.after(1500, lambda: self.run_steps(steps))

        elif s['act'] == 'LOAD_FOR_MERGE':
            # Kéo ngược từ Disk Tạm về RAM
            self.ram_objs = self.run_items[s['r1_idx']] + self.run_items[s['r2_idx']]
            for i, (r, t) in enumerate(self.ram_objs):
                self.move_item(r, 210+i*45, 220); self.move_item(t, 232+i*45, 242)
                self.canvas.itemconfig(r, fill="#FF6347") # Đổi sang màu trộn
            self.root.after(2000, lambda: self.run_steps(steps))

        elif s['act'] == 'SAVE_MERGED':
            # Ghi kết quả sau khi trộn lên lại Disk Tạm
            for i, (r, t) in enumerate(self.ram_objs):
                self.canvas.itemconfig(t, text=str(int(s['values'][i])))
                self.move_item(r, 150+i*50, 50); self.move_item(t, 172+i*50, 72)
                self.canvas.itemconfig(r, fill="#32CD32") # Màu thành phẩm
            self.root.after(2000, lambda: self.run_steps(steps))

    def start(self):
        self.canvas.delete("all"); self.setup_ui()
        utils.create_sample_binary()
        steps = self.sorter.get_full_animation_steps("input_test.bin")
        self.run_steps(steps)

if __name__ == "__main__":
    root = tk.Tk(); app = FinalApp(root); root.mainloop()
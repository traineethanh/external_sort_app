import tkinter as tk
from tkinter import messagebox, filedialog
import os  # Them thu vien nay de lay ten file
import utils
from algorithms import ExternalSort

class FinalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UIT - External Sort Animation")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        
        # Khoi tao cac thanh phan UI
        self.setup_ui()
        
        self.sorter = ExternalSort()
        self.run_objs = {} 

    def setup_ui(self):
        # 1. Vẽ các vùng chức năng (Vẽ trước để nằm dưới)
        self.canvas.create_rectangle(50, 20, 750, 150, outline="green", width=2)
        self.canvas.create_text(400, 10, text="Buffer Disk", font=("Arial", 12, "bold"), fill="green")
        
        self.canvas.create_rectangle(200, 200, 600, 320, outline="blue", width=2)
        self.canvas.create_text(400, 185, text="RAM", font=("Arial", 12, "bold"), fill="blue")
        
        self.canvas.create_rectangle(50, 450, 750, 580, outline="black", width=2)
        self.canvas.create_text(400, 435, text="Disk", font=("Arial", 12, "bold"), fill="black")

        # 2. Tạo Label trạng thái (Chỉ tạo 1 lần duy nhất)
        if not hasattr(self, 'status'):
            self.status = tk.Label(self.root, text="Vui long chon file nhi phan de bat dau", font=("Arial", 10))
            self.status.pack(pady=5)

        # 3. Nút chọn file
        self.btn_choose = tk.Button(self.root, text="CHON FILE TU BEN NGOAI", command=self.choose_file, bg="#F0F0F0")
        self.btn_choose.pack(pady=5)

        # 4. Nút bắt đầu (Lưu biến để có thể bật/tắt state)
        self.btn_start = tk.Button(self.root, text="BAT DAU SAP XEP", command=self.start, state="disabled", bg="#0078D7", fg="white")
        self.btn_start.pack(pady=5)

    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])
        if file_path:
            self.input_file = file_path 
            file_name = os.path.basename(file_path)
            self.status.config(text=f"Da chon: {file_name}", fg="green")
            self.btn_start.config(state="normal") # Kich hoat nut bam
        else:
            self.status.config(text="Ban chua chon file nao!", fg="red")
    
    def move_item(self, item_id, tx, ty, callback=None):
        c = self.canvas.coords(item_id)
        if not c: return
        steps_count = 15
        dx, dy = (tx - c[0]) / steps_count, (ty - c[1]) / steps_count
        
        def anim(step):
            if step < steps_count:
                self.canvas.move(item_id, dx, dy)
                self.root.after(20, lambda: anim(step + 1))
            elif callback:
                callback()
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
                r = self.canvas.create_rectangle(70+i*55, 480, 115+i*55, 525, fill="#FFD700")
                t = self.canvas.create_text(92+i*55, 502, text=str(int(v)))
                self.data_objs.append((r, t))
            self.root.after(1000, lambda: self.run_steps(steps))

        elif s['act'] == 'READ':
            self.ram_objs = []
            for i in range(len(s['values'])):
                r, t = self.data_objs[s['idx'] + i]
                self.move_item(r, 220+i*100, 220)
                self.move_item(t, 242+i*100, 242)
                self.ram_objs.append((r, t))
            self.root.after(1200, lambda: self.run_steps(steps))

        elif s['act'] == 'SORT':
            for i, (r, t) in enumerate(self.ram_objs):
                self.canvas.itemconfig(t, text=str(int(s['values'][i])))
                self.canvas.itemconfig(r, fill="#81D4FA")
            self.root.after(800, lambda: self.run_steps(steps))

        elif s['act'] == 'WRITE_RUN':
            idx = s['run_idx']; self.run_objs[idx] = []
            for i, (r, t) in enumerate(self.ram_objs):
                tx = 60 + idx*230 + i*45
                self.move_item(r, tx, 50)
                self.move_item(t, tx+20, 72)
                self.run_objs[idx].append((r, t))
            self.root.after(1200, lambda: self.run_steps(steps))

        elif s['act'] == 'LOAD_FOR_MERGE':
            # Gom cac khoi tu Disk ve RAM de tron
            self.ram_objs = self.run_objs[s['r1_idx']] + self.run_objs[s['r2_idx']]
            for i, (r, t) in enumerate(self.ram_objs):
                self.move_item(r, 210+i*40, 220)
                self.move_item(t, 232+i*40, 242)
                self.canvas.itemconfig(r, fill="#FF6347")
            self.root.after(1500, lambda: self.run_steps(steps))

        elif s['act'] == 'SAVE_MERGED':
            for i, (r, t) in enumerate(self.ram_objs):
                self.canvas.itemconfig(t, text=str(int(s['values'][i])))
                tx = 150 + i*50
                self.move_item(r, tx, 50)
                self.move_item(t, tx+22, 72)
                self.canvas.itemconfig(r, fill="#32CD32")
            self.run_objs = {0: self.ram_objs} 
            self.root.after(1500, lambda: self.run_steps(steps))
        
        else: # SKIP_LE
            self.root.after(500, lambda: self.run_steps(steps))

    def start(self):
        # Khong xoa tat ca component, chi xoa hinh ve tren canvas
        self.canvas.delete("all")
        # Ve lai cac khung Disk/RAM
        self.canvas.create_rectangle(50, 20, 750, 150, outline="green", width=2)
        self.canvas.create_text(400, 10, text="Buffer Disk", font=("Arial", 12, "bold"), fill="green")
        self.canvas.create_rectangle(200, 200, 600, 320, outline="blue", width=2)
        self.canvas.create_text(400, 185, text="RAM", font=("Arial", 12, "bold"), fill="blue")
        self.canvas.create_rectangle(50, 450, 750, 580, outline="black", width=2)
        self.canvas.create_text(400, 435, text="Disk", font=("Arial", 12, "bold"), fill="black")
        
        self.run_objs = {}
        target = getattr(self, 'input_file', 'input_test.bin')

        try:
            steps = self.sorter.get_full_animation_steps(target)
            self.run_steps(steps)
        except Exception as e:
            messagebox.showerror("Loi", f"Khong the xu ly tap tin: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FinalApp(root)
    root.mainloop()
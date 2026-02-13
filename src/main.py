import tkinter as tk
from tkinter import ttk
import utils
from algorithms import ExternalSort

class FinalAnimationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UIT - External Sort Full Process - Quang Thanh")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        
        self.sorter = ExternalSort()
        self.setup_canvas()
        self.data_objects = {} # Luu cac block du lieu tren disk goc

    def setup_canvas(self):
        # 1. Vung Disk Goc (Phia duoi cung)
        self.canvas.create_rectangle(50, 450, 750, 580, outline="black", width=2)
        self.canvas.create_text(400, 435, text="INPUT DISK (DATA BAN DAU)", font=("Arial", 10, "bold"))
        
        # 2. Vung RAM / Buffer (O giua) [cite: 45, 105]
        self.canvas.create_rectangle(200, 200, 600, 320, outline="blue", width=2, fill="#F0F8FF")
        self.canvas.create_text(400, 185, text="MAIN MEMORY (RAM BUFFER)", font=("Arial", 10, "bold"))
        
        # 3. Vung Disk Tam / Output (Phia tren cung) [cite: 43, 115]
        self.canvas.create_rectangle(50, 20, 750, 150, outline="green", width=2)
        self.canvas.create_text(400, 10, text="OUTPUT DISK (SORTED RUNS / BUFFER)", font=("Arial", 10, "bold"))
        
        self.desc_label = tk.Label(self.root, text="San sang mo phong...", font=("Arial", 11))
        self.desc_label.pack(pady=10)
        tk.Button(self.root, text="BAT DAU QUY TRINH", command=self.start).pack()

    def move_item(self, item_id, tx, ty, callback):
        curr = self.canvas.coords(item_id)
        dx, dy = (tx - curr[0]) / 15, (ty - curr[1]) / 15
        def animate(c):
            if c < 15:
                self.canvas.move(item_id, dx, dy)
                self.root.after(25, lambda: animate(c+1))
            else: callback()
        animate(0)

    def run_steps(self, steps):
        if not steps: 
            self.desc_label.config(text="CHUC MUNG! DA SAP XEP XONG HOAN TOAN")
            return
        
        s = steps.pop(0)
        self.desc_label.config(text=s['desc'])

        if s['act'] == 'WRITE_RUN':
            # Vẽ Pass 0 giống như cũ
            # ... (logic di chuyển từ RAM lên Output Disk)
            self.root.after(1500, lambda: self.run_steps(steps))

        elif s['act'] == 'LOAD_FOR_MERGE':
            # Hiệu ứng: Lấy 2 run từ đĩa trên cùng bay xuống RAM
            # Đây là lúc thuật toán "sees" các phần tử để so sánh [cite: 118]
            self.desc_label.config(text=f"Dang lay du lieu tu Disk xuong Buffer de tron...")
            # (Thêm logic di chuyển vật thể tại đây)
            self.root.after(2000, lambda: self.run_steps(steps))

        elif s['act'] == 'SAVE_MERGED':
            # Hiệu ứng: Kết quả sau khi so sánh bay ngược lên vùng lưu trữ cuối cùng
            # ... (logic di chuyển vật thể)
            self.root.after(2000, lambda: self.run_steps(steps))

    def start(self):
        self.canvas.delete("all")
        self.setup_canvas()
        utils.create_sample_binary()
        steps = self.sorter.get_animation_steps("input_test.bin")
        self.run_steps(steps)
if __name__ == "__main__":
    root = tk.Tk()
    app = FinalAnimationApp(root)
    root.mainloop()
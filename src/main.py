import tkinter as tk
from tkinter import ttk
import utils
from algorithms import ExternalSort

class SmoothAnimationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UIT - External Sort Motion - Quang Thanh")
        self.canvas = tk.Canvas(root, width=700, height=500, bg="white")
        self.canvas.pack()
        
        self.sorter = ExternalSort()
        self.setup_layout()
        self.blocks = {} # Lưu trữ các ID đối tượng trên canvas

    def setup_layout(self):
        # Vẽ RAM (Buffer) [cite: 18, 44]
        self.canvas.create_rectangle(150, 50, 550, 150, outline="blue", width=2)
        self.canvas.create_text(350, 30, text="RAM / BUFFER (3 PAGES)", font=("Arial", 10, "bold"))
        
        # Vẽ Disk [cite: 43, 115]
        self.canvas.create_rectangle(50, 300, 650, 480, outline="black", dash=(5,2))
        self.canvas.create_text(350, 280, text="DISK STORAGE", font=("Arial", 10, "bold"))
        
        self.desc_label = tk.Label(self.root, text="Nhan nut de bat dau animation", font=("Arial", 12))
        self.desc_label.pack(pady=10)
        
        tk.Button(self.root, text="CHẠY MÔ PHỎNG CHUYỂN ĐỘNG", command=self.start).pack()

    def move_element(self, obj_id, target_x, target_y, callback):
        """Di chuyển một khối dữ liệu mượt mà đến tọa độ đích."""
        curr_x, curr_y = self.canvas.coords(obj_id)[:2]
        dx = (target_x - curr_x) / 10
        dy = (target_y - curr_y) / 10
        
        def step(count):
            if count < 10:
                self.canvas.move(obj_id, dx, dy)
                self.root.after(30, lambda: step(count + 1))
            else:
                callback()
        step(0)

    def process_steps(self, steps):
        if not steps: 
            self.desc_label.config(text="Hoàn tất sắp xếp ngoại!")
            return
            
        step = steps.pop(0)
        self.desc_label.config(text=step['desc'])

        if step['act'] == 'READ':
            # Tạo các khối dữ liệu mới bay từ Disk lên RAM [cite: 585]
            self.blocks = []
            for i, val in enumerate(step['values']):
                obj = self.canvas.create_rectangle(50+(i*40), 350, 90+(i*40), 390, fill="orange")
                txt = self.canvas.create_text(70+(i*40), 370, text=str(int(val)))
                self.blocks.append((obj, txt))
                # Di chuyển lên RAM [cite: 135]
                self.move_element(obj, 180+(i*60), 70, lambda: None)
                self.move_element(txt, 200+(i*60), 90, lambda: None)
            self.root.after(1500, lambda: self.process_steps(steps))

        elif step['act'] == 'SORT':
            # Sắp xếp các khối đang có trong RAM [cite: 254, 596]
            # (Đơn giản hóa: vẽ lại đúng vị trí đã sắp xếp)
            self.root.after(1000, lambda: self.process_steps(steps))

        elif step['act'] == 'WRITE':
            # Bay từ RAM xuống vùng Run trên Disk 
            target_y = 320 + (step['run_idx'] * 40)
            for i, (obj, txt) in enumerate(self.blocks):
                self.move_element(obj, 100+(i*40), target_y, lambda: None)
                self.move_element(txt, 120+(i*40), target_y+20, lambda: None)
            self.root.after(1500, lambda: self.process_steps(steps))

    def start(self):
        utils.create_sample_binary()
        steps = self.sorter.get_animation_steps("input_test.bin")
        self.canvas.delete("all")
        self.setup_layout()
        self.process_steps(steps)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmoothAnimationApp(root)
    root.mainloop()
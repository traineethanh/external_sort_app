import tkinter as tk
from tkinter import filedialog, ttk
import utils
from algorithms import ExternalSort
import os

class AnimationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UIT - External Sort Animation - Quang Thanh")
        self.sorter = ExternalSort()
        
        # Canvas mô phỏng Disk và RAM [cite: 43, 44]
        self.canvas = tk.Canvas(root, width=600, height=450, bg="#f0f0f0")
        self.canvas.pack(pady=10)
        
        self.setup_ui()
        self.steps = []
        self.current_step = 0

    def setup_ui(self):
        # Vẽ vùng RAM [cite: 131, 132]
        self.canvas.create_rectangle(50, 50, 550, 150, fill="#e1f5fe", outline="#01579b", width=2)
        self.canvas.create_text(300, 30, text="MAIN MEMORY (BUFFER PAGES)", font=("Arial", 10, "bold"))
        
        # Vẽ vùng DISK [cite: 43, 115]
        self.canvas.create_rectangle(50, 250, 550, 420, fill="#efebe9", outline="#4e342e", width=2)
        self.canvas.create_text(300, 230, text="DISK STORAGE (RUNS)", font=("Arial", 10, "bold"))

        self.status_text = self.canvas.create_text(300, 200, text="Sẵn sàng", fill="red")

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Tạo dữ liệu & Chạy Animation", command=self.start_animation).pack(side="left", padx=10)

    def draw_step(self):
        if self.current_step >= len(self.steps):
            self.canvas.itemconfig(self.status_text, text="HOÀN TẤT SẮP XẾP NGOẠI!")
            return

        step = self.steps[self.current_step]
        self.canvas.itemconfig(self.status_text, text=step['desc'])
        
        # Xóa các phần tử cũ
        self.canvas.delete("data")

        # Vẽ dữ liệu trong Buffer [cite: 158]
        for i, val in enumerate(step['buffer']):
            x = 80 + (i * 60)
            self.canvas.create_rectangle(x, 70, x+50, 120, fill="#81d4fa", tags="data")
            self.canvas.create_text(x+25, 95, text=str(int(val)), tags="data")

        # Vẽ các Runs trên Disk [cite: 341, 427]
        for i, run_name in enumerate(step['runs']):
            y = 270 + (i * 30)
            self.canvas.create_text(100, y, text=f"Run {i}: (Da sap xep tren disk)", anchor="w", tags="data")

        self.current_step += 1
        # Tự động chuyển bước sau 1.5 giây để tạo hiệu ứng animation [cite: 509]
        self.root.after(1500, self.draw_step)

    def start_animation(self):
        utils.create_sample_binary()
        self.steps, _ = self.sorter.get_initial_runs_steps("input_test.bin")
        self.current_step = 0
        self.draw_step()

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimationApp(root)
    root.mainloop()
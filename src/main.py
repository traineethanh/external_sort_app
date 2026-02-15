import tkinter as tk
from algorithms import ExternalSortEngine
import utils

class ExternalSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("External Merge Sort Simulation - UIT")
        self.canvas = tk.Canvas(root, width=900, height=600, bg="white")
        self.canvas.pack()
        
        self.engine = ExternalSortEngine()
        self.setup_ui()

    def setup_ui(self):
        # Vẽ khung Disk [cite: 43]
        self.canvas.create_rectangle(50, 50, 400, 550, outline="blue", width=2)
        self.canvas.create_text(225, 30, text="DISK", font=("Arial", 14, "bold"))
        
        # Vẽ khung RAM [cite: 44]
        self.canvas.create_rectangle(500, 50, 850, 300, outline="green", width=2)
        self.canvas.create_text(675, 30, text="MAIN MEMORY (RAM)", font=("Arial", 14, "bold"))
        
        # Nút điều khiển
        tk.Button(self.root, text="Start Simulation", command=self.run_sim).pack()

    def create_block(self, x, y, value):
        """Tạo block màu xám đậm, chữ vàng theo style ảnh mẫu."""
        rect = self.canvas.create_rectangle(x, y, x+80, y+40, fill="#4A4A4A", outline="#707070")
        text = self.canvas.create_text(x+40, y+20, text=str(value), fill="#FFCC00", font=("Arial", 10, "bold"))
        return rect, text

    def move_block(self, block_ids, target_x, target_y, speed=5):
        """Hàm xử lý animation di chuyển block."""
        # Code xử lý di chuyển tọa độ dần dần sử dụng self.root.after()
        pass

    def run_sim(self):
        utils.create_sample_binary()
        steps = self.engine.get_simulation_steps("input.bin")
        self.execute_steps(steps)

    def execute_steps(self, steps):
        if not steps: return
        step = steps.pop(0)
        # Dựa vào act để gọi hàm animation tương ứng
        print(f"Executing: {step['act']}") 
        self.root.after(1000, lambda: self.execute_steps(steps))

if __name__ == "__main__":
    root = tk.Tk()
    app = ExternalSortApp(root)
    root.mainloop()
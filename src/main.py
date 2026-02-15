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
        # --- VÙNG CANVAS (Vẽ Disk và RAM) ---
        # Vẽ khung Disk (Input/Output Storage) [cite: 43, 63]
        self.canvas.create_rectangle(50, 50, 400, 550, outline="blue", width=2)
        self.canvas.create_text(225, 30, text="DISK STORAGE", font=("Arial", 14, "bold"))
        
        # Vẽ khung RAM (Main Memory - 3 Buffer Pages) [cite: 18, 44, 45]
        self.canvas.create_rectangle(500, 50, 850, 300, outline="green", width=2)
        self.canvas.create_text(675, 30, text="RAM (MAIN MEMORY)", font=("Arial", 14, "bold"))
        
        # --- VÙNG ĐIỀU KHIỂN (Control Panel) ---
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Hàng 1: Xử lý file
        tk.Button(control_frame, text="Chọn File (.bin)", command=self.choose_file).grid(row=0, column=0, padx=5)
        tk.Button(control_frame, text="Tạo File Ngẫu Nhiên", command=self.gen_random).grid(row=0, column=1, padx=5)
        tk.Button(control_frame, text="Reset", command=self.reset_all, bg="#FFCDD2").grid(row=0, column=2, padx=5)

        # Hàng 2: Điều hướng Animation [cite: 580]
        self.btn_back = tk.Button(control_frame, text="<< Back", command=self.step_back, state="disabled")
        self.btn_back.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_next = tk.Button(control_frame, text="Next >>", command=self.step_next, state="disabled")
        self.btn_next.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(control_frame, text="End (Xuất kết quả)", command=self.export_result, bg="#C8E6C9").grid(row=1, column=2, padx=5)

        # Hiển thị IO Cost và trạng thái [cite: 19, 359]
        self.lbl_io = tk.Label(self.root, text="IO Cost: 0", font=("Arial", 12, "bold"), fg="red")
        self.lbl_io.pack()
        self.status = tk.Label(self.root, text="Vui lòng chọn hoặc tạo file để bắt đầu", font=("Arial", 10, "italic"))
        self.status.pack()

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
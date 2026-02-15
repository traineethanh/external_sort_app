import tkinter as tk
from tkinter import filedialog, messagebox
import os
import utils
from algorithms import ExternalSortEngine

class ExternalSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("External Merge Sort Simulation - UIT")
        self.canvas = tk.Canvas(root, width=900, height=600, bg="white")
        self.canvas.pack()
        
        self.engine = ExternalSortEngine()
        self.all_steps = []
        self.current_step_idx = -1
        self.block_map = {} # Lưu trữ ID các block trên canvas
        self.io_cost = 0
        
        self.setup_ui()

    def setup_ui(self):
        # --- VÙNG CANVAS ---
        # Disk [cite: 43, 63]
        self.canvas.create_rectangle(50, 50, 400, 550, outline="blue", width=2)
        self.canvas.create_text(225, 30, text="DISK STORAGE", font=("Arial", 14, "bold"))
        
        # RAM (3 Buffer Pages) [cite: 18, 44, 45]
        self.canvas.create_rectangle(500, 50, 850, 300, outline="green", width=2)
        self.canvas.create_text(675, 30, text="RAM (MAIN MEMORY)", font=("Arial", 14, "bold"))
        
        # --- VÙNG ĐIỀU KHIỂN ---
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Hàng 1
        tk.Button(control_frame, text="Chọn File (.bin)", command=self.choose_file).grid(row=0, column=0, padx=5)
        tk.Button(control_frame, text="Tạo File Ngẫu Nhiên", command=self.gen_random).grid(row=0, column=1, padx=5)
        tk.Button(control_frame, text="Reset", command=self.reset_all, bg="#FFCDD2").grid(row=0, column=2, padx=5)

        # Hàng 2 
        self.btn_back = tk.Button(control_frame, text="<< Back", command=self.step_back, state="disabled")
        self.btn_back.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_next = tk.Button(control_frame, text="Next >>", command=self.step_next, state="disabled")
        self.btn_next.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(control_frame, text="End (Xuất kết quả)", command=self.export_result, bg="#C8E6C9").grid(row=1, column=2, padx=5)

        # Thông số [cite: 19, 359]
        self.lbl_io = tk.Label(self.root, text="IO Cost: 0", font=("Arial", 12, "bold"), fg="red")
        self.lbl_io.pack()
        self.status = tk.Label(self.root, text="Vui lòng chọn hoặc tạo file", font=("Arial", 10, "italic"))
        self.status.pack()

    # --- CÁC HÀM XỬ LÝ SỰ KIỆN ---
    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if path:
            self.load_simulation(path)

    def gen_random(self):
        path = utils.create_random_input("input_test.bin", 12)
        self.load_simulation(path)

    def load_simulation(self, path):
        self.reset_all()
        self.all_steps = self.engine.get_simulation_steps(path)
        self.current_step_idx = -1
        self.btn_next.config(state="normal")
        self.status.config(text=f"Đã nạp file: {os.path.basename(path)}")

    def step_next(self):
        if self.current_step_idx < len(self.all_steps) - 1:
            self.current_step_idx += 1
            self.apply_step(self.all_steps[self.current_step_idx])
            self.btn_back.config(state="normal")
        if self.current_step_idx == len(self.all_steps) - 1:
            self.btn_next.config(state="disabled")

    def step_back(self):
        # Logic: Reset canvas và chạy lại từ đầu đến step_idx - 1
        if self.current_step_idx >= 0:
            idx = self.current_step_idx - 1
            self.reset_canvas_only()
            self.current_step_idx = -1
            for i in range(idx + 1):
                self.step_next()
            self.current_step_idx = idx
            self.btn_next.config(state="normal")
        if self.current_step_idx < 0:
            self.btn_back.config(state="disabled")

    def apply_step(self, step):
        """Thực thi một bước và cập nhật giao diện[cite: 255, 580]."""
        self.status.config(text=step['desc'])
        self.io_cost = step.get('io_cost', self.io_cost)
        self.lbl_io.config(text=f"IO Cost: {self.io_cost}")
        
        # Ở đây bạn sẽ thêm logic vẽ block dựa trên 'act' (READ, SORT, WRITE...)
        # Ví dụ: if step['act'] == 'READ': self.animate_move(...)
        pass

    def reset_all(self):
        self.reset_canvas_only()
        self.all_steps = []
        self.io_cost = 0
        self.lbl_io.config(text="IO Cost: 0")
        self.btn_next.config(state="disabled")
        self.btn_back.config(state="disabled")

    def reset_canvas_only(self):
        self.canvas.delete("all")
        self.setup_ui()

    def export_result(self):
        messagebox.showinfo("Export", "Kết quả đã được ghi vào file output.bin")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExternalSortApp(root)
    root.mainloop()
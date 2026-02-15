import tkinter as tk
from tkinter import filedialog, messagebox
import os
import utils
from algorithms import ExternalSortEngine

class ExternalSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("External Merge Sort Simulation - UIT")
        self.canvas = tk.Canvas(root, width=900, height=550, bg="white")
        self.canvas.pack()
        
        self.engine = ExternalSortEngine()
        self.input_file_path = None # Lưu đường dẫn file riêng biệt
        self.all_steps = []
        self.current_step_idx = -1
        self.data_blocks = [] 
        self.io_cost = 0
        
        self.setup_ui()

    def setup_ui(self):
        # --- VÙNG CANVAS ---
        # Vẽ khung Disk 
        self.canvas.create_rectangle(50, 20, 400, 520, outline="blue", width=2)
        self.canvas.create_text(225, 10, text="DISK STORAGE", font=("Arial", 12, "bold"))
        # Vẽ khung RAM (3 Buffer Pages) [cite: 18, 44, 45]
        self.canvas.create_rectangle(500, 20, 850, 250, outline="green", width=2)
        self.canvas.create_text(675, 10, text="RAM (MAIN MEMORY)", font=("Arial", 12, "bold"))
        
        # --- VÙNG ĐIỀU KHIỂN ---
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Hàng 1: Hoạt động nạp dữ liệu (Riêng biệt)
        tk.Button(control_frame, text="Chọn File (.bin)", command=self.choose_file).grid(row=0, column=0, padx=5)
        tk.Button(control_frame, text="Tạo File Ngẫu Nhiên", command=self.gen_random).grid(row=0, column=1, padx=5)
        tk.Button(control_frame, text="Reset", command=self.reset_all, bg="#FFCDD2").grid(row=0, column=2, padx=5)

        # Hàng 2: Hoạt động sắp xếp (Riêng biệt)
        self.btn_start_sort = tk.Button(control_frame, text="BẮT ĐẦU SẮP XẾP", command=self.prepare_and_start, state="disabled", bg="#BBDEFB", font=("Arial", 10, "bold"))
        self.btn_start_sort.grid(row=1, column=1, padx=5, pady=5)

        self.btn_back = tk.Button(control_frame, text="<< Back", command=self.step_back, state="disabled")
        self.btn_back.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_next = tk.Button(control_frame, text="Next >>", command=self.step_next, state="disabled")
        self.btn_next.grid(row=1, column=2, padx=5, pady=5)
        
        tk.Button(control_frame, text="End (Xuất kết quả)", command=self.export_result, bg="#C8E6C9").grid(row=1, column=3, padx=5)

        self.lbl_io = tk.Label(self.root, text="IO Cost: 0", font=("Arial", 12, "bold"), fg="red")
        self.lbl_io.pack()
        self.status = tk.Label(self.root, text="Bước 1: Vui lòng nạp file dữ liệu", font=("Arial", 10, "italic"))
        self.status.pack()

    def create_block(self, x, y, value):
        rect = self.canvas.create_rectangle(x, y, x+75, y+35, fill="#4A4A4A", outline="#707070", width=2)
        text = self.canvas.create_text(x+37, y+17, text=f"{value:.1f}", fill="#FFCC00", font=("Arial", 9, "bold"))
        return rect, text

    # --- HOẠT ĐỘNG 1: NẠP FILE ---
    def load_file_only(self, path):
        self.reset_all()
        self.input_file_path = path
        data = utils.read_binary_file(path)
        
        if len(data) > 12:
            self.status.config(text=f"Dữ liệu lớn ({len(data)} số). Sẽ xuất kết quả trực tiếp khi bấm Sắp xếp.", fg="orange")
        else:
            # Hiển thị dữ liệu lên Disk ngay khi nạp file để người dùng quan sát
            self.status.config(text=f"Đã nạp {len(data)} số. Bước 2: Bấm 'BẮT ĐẦU SẮP XẾP'", fg="blue")
            for i, v in enumerate(data):
                bx, by = 70 + (i % 4) * 85, 50 + (i // 4) * 50
                self.create_block(bx, by, v)
        
        self.btn_start_sort.config(state="normal")

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if path: self.load_file_only(path)

    def gen_random(self):
        path = utils.create_random_input("input_test.bin", 12)
        self.load_file_only(path)

    # --- HOẠT ĐỘNG 2: SẮP XẾP ---
    def prepare_and_start(self):
        if not self.input_file_path: return
        
        data = utils.read_binary_file(self.input_file_path)
        if len(data) <= 12:
            # Tính toán các bước mô phỏng [cite: 359, 580]
            self.all_steps = self.engine.get_simulation_steps(self.input_file_path)
            self.current_step_idx = -1
            self.btn_next.config(state="normal")
            self.btn_start_sort.config(state="disabled") # Khóa nút nạp để tránh lỗi
            self.step_next() # Chạy bước INIT đầu tiên
        else:
            # Sắp xếp ngầm cho file lớn 
            sorted_data = sorted(data)
            utils.write_binary_file("output_result.bin", sorted_data)
            messagebox.showinfo("Thông báo", "Đã sắp xếp dữ liệu lớn và xuất file output_result.bin")

    def step_next(self):
        if self.current_step_idx < len(self.all_steps) - 1:
            self.current_step_idx += 1
            self.apply_step(self.all_steps[self.current_step_idx])
            self.btn_back.config(state="normal")

    def apply_step(self, step):
        self.status.config(text=step['desc'])
        self.io_cost = step.get('io_cost', self.io_cost) [cite: 19]
        self.lbl_io.config(text=f"IO Cost: {self.io_cost}")
        # Thêm các logic ACT xử lý READ/WRITE tại đây...

    def reset_all(self):
        self.canvas.delete("all")
        self.all_steps = []
        self.current_step_idx = -1
        self.input_file_path = None
        self.io_cost = 0
        self.lbl_io.config(text="IO Cost: 0")
        self.btn_next.config(state="disabled")
        self.btn_back.config(state="disabled")
        self.btn_start_sort.config(state="disabled")
        self.status.config(text="Bước 1: Vui lòng nạp file dữ liệu", fg="black")

    def export_result(self):
        # Giữ nguyên logic cũ
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ExternalSortApp(root)
    root.mainloop()
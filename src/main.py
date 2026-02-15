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
        self.input_file_path = None 
        self.all_steps = []
        self.current_step_idx = -1
        self.data_blocks = [] # Luu tru doi tuong hinh ve
        self.io_cost = 0
        
        self.setup_ui()

    def setup_ui(self):
        self.canvas.delete("all")
        # [cite_start]Khung Disk [cite: 43, 63]
        self.canvas.create_rectangle(50, 20, 400, 520, outline="blue", width=2)
        self.canvas.create_text(225, 10, text="DISK STORAGE", font=("Arial", 12, "bold"))
        # [cite_start]Khung RAM [cite: 18, 44, 45]
        self.canvas.create_rectangle(500, 20, 850, 250, outline="green", width=2)
        self.canvas.create_text(675, 10, text="RAM (MAIN MEMORY)", font=("Arial", 12, "bold"))
        
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Hang 1: Nap du lieu
        tk.Button(control_frame, text="Chọn File (.bin)", command=self.choose_file).grid(row=0, column=0, padx=5)
        tk.Button(control_frame, text="Tạo File Ngẫu Nhiên", command=self.gen_random).grid(row=0, column=1, padx=5)
        tk.Button(control_frame, text="Reset", command=self.reset_all, bg="#FFCDD2").grid(row=0, column=2, padx=5)

        # Hang 2: Hoat dong sap xep
        self.btn_back = tk.Button(control_frame, text="<< Back", command=self.step_back, state="disabled")
        self.btn_back.grid(row=1, column=0, padx=5, pady=5)

        self.btn_start_sort = tk.Button(control_frame, text="BẮT ĐẦU SẮP XẾP", command=self.prepare_and_start, state="disabled", bg="#BBDEFB", font=("Arial", 10, "bold"))
        self.btn_start_sort.grid(row=1, column=1, padx=5, pady=5)
        
        self.btn_next = tk.Button(control_frame, text="Next >>", command=self.step_next, state="disabled")
        self.btn_next.grid(row=1, column=2, padx=5, pady=5)
        
        tk.Button(control_frame, text="End (Xuất kết quả)", command=self.export_result, bg="#C8E6C9").grid(row=1, column=3, padx=5)

        self.lbl_io = tk.Label(self.root, text="IO Cost: 0", font=("Arial", 12, "bold"), fg="red")
        self.lbl_io.pack()
        self.status = tk.Label(self.root, text="Bước 1: Vui lòng nạp file dữ liệu", font=("Arial", 10, "italic"))
        self.status.pack()

    def create_block(self, x, y, value):
        r = self.canvas.create_rectangle(x, y, x+75, y+35, fill="#4A4A4A", outline="#707070", width=2)
        t = self.canvas.create_text(x+37, y+17, text=f"{value:.1f}", fill="#FFCC00", font=("Arial", 9, "bold"))
        return r, t

    def move_block(self, block_obj, tx, ty, callback=None):
        r_id, t_id = block_obj
        curr = self.canvas.coords(r_id)
        if not curr: return
        steps = 10
        dx, dy = (tx - curr[0]) / steps, (ty - curr[1]) / steps
        def anim(count):
            if count < steps:
                self.canvas.move(r_id, dx, dy); self.canvas.move(t_id, dx, dy)
                self.root.after(20, lambda: anim(count + 1))
            elif callback: callback()
        anim(0)

    def load_file_only(self, path):
        self.reset_all()
        self.input_file_path = path
        data = utils.read_binary_file(path)
        if len(data) <= 12:
            self.status.config(text=f"Đã nạp {len(data)} số. Bước 2: Bấm 'BẮT ĐẦU SẮP XẾP'", fg="blue")
            self.data_blocks = []
            for i, v in enumerate(data):
                bx, by = 70 + (i % 4) * 85, 50 + (i // 4) * 50
                self.data_blocks.append(self.create_block(bx, by, v))
        self.btn_start_sort.config(state="normal")

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if path: self.load_file_only(path)

    def gen_random(self):
        path = utils.create_random_input("input_test.bin", 12)
        self.load_file_only(path)

    def prepare_and_start(self):
        if not self.input_file_path: return
        self.all_steps = self.engine.get_simulation_steps(self.input_file_path)
        self.current_step_idx = -1
        self.btn_next.config(state="normal")
        self.btn_start_sort.config(state="disabled")
        self.step_next() 

    def step_next(self):
        if self.current_step_idx < len(self.all_steps) - 1:
            self.current_step_idx += 1
            self.apply_step(self.all_steps[self.current_step_idx])
            self.btn_back.config(state="normal")
        if self.current_step_idx == len(self.all_steps) - 1:
            self.btn_next.config(state="disabled")

    def step_back(self):
        if self.current_step_idx > 0:
            target_idx = self.current_step_idx - 1
            self.reset_canvas_only()
            self.current_step_idx = -1
            for i in range(target_idx + 1):
                self.apply_step(self.all_steps[i])
            self.current_step_idx = target_idx
            self.btn_next.config(state="normal")
        else:
            self.reset_all()

    def apply_step(self, step):
        self.status.config(text=step['desc'])
        self.io_cost = step.get('io_cost', self.io_cost)
        self.lbl_io.config(text=f"IO Cost: {self.io_cost}")
        
        if step['act'] == 'READ':
            for i in range(len(step['values'])):
                idx = step['idx'] + i
                self.move_block(self.data_blocks[idx], 520 + i*85, 100)
        elif step['act'] == 'WRITE_RUN':
            for i in range(len(step['values'])):
                idx = step['idx'] + i
                self.move_block(self.data_blocks[idx], 70 + (i%4)*85, 280 + step['run_idx']*50)

    def reset_all(self):
        self.canvas.delete("all")
        self.setup_ui()
        self.all_steps = []
        self.current_step_idx = -1
        self.input_file_path = None
        self.io_cost = 0
        self.lbl_io.config(text="IO Cost: 0")

    def reset_canvas_only(self):
        self.canvas.delete("all")
        # Ve lai khung nhung khong reset logic file
        self.canvas.create_rectangle(50, 20, 400, 520, outline="blue", width=2)
        self.canvas.create_rectangle(500, 20, 850, 250, outline="green", width=2)
        # Ve lai block goc tu file
        data = utils.read_binary_file(self.input_file_path)
        self.data_blocks = [self.create_block(70+(i%4)*85, 50+(i//4)*50, v) for i, v in enumerate(data)]

    def export_result(self):
        # 1. Kiểm tra xem quá trình mô phỏng đã đi đến bước cuối cùng chưa
        if self.current_step_idx < len(self.all_steps) - 1:
            messagebox.showwarning("Thông báo", "Vui lòng đợi hoặc bấm 'Next' cho đến khi sắp xếp xong hoàn toàn!")
            return

        # 2. Lấy dữ liệu đã sắp xếp từ bước cuối cùng (Final Run)
        final_step = self.all_steps[-1]
        sorted_data = final_step.get('values', [])

        if not sorted_data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu sau sắp xếp.")
            return

        # 3. Xuất file nhị phân (.bin) - Sử dụng hàm write_binary_file từ utils
        output_filename = "sorted_output.bin"
        try:
            utils.write_binary_file(output_filename, sorted_data)
        except Exception as e:
            messagebox.showerror("Lỗi Ghi File", f"Không thể ghi file: {e}")
            return

        # 4. Hiển thị kết quả lên màn hình (Dưới dạng text số)
        result_window = tk.Toplevel(self.root)
        result_window.title("Kết quả Output .bin")
        result_window.geometry("350x450")

        header = tk.Label(result_window, text=f"File: {output_filename}", font=("Arial", 11, "bold"), pady=10)
        header.pack()

        # Khung chứa văn bản danh sách số
        txt_area = tk.Text(result_window, font=("Consolas", 10), padx=10, pady=10)
        txt_area.pack(fill="both", expand=True)

        # Ghi danh sách số vào khung text
        content = "--- DANH SÁCH ĐÃ SẮP XẾP ---\n\n"
        for i, val in enumerate(sorted_data):
            content += f" [{i+1:02d}] : {val:.2f}\n" # Định dạng số thực 2 chữ số thập phân
        
        txt_area.insert("1.0", content)
        txt_area.config(state="disabled") # Khóa không cho chỉnh sửa nội dung

        messagebox.showinfo("Thành công", f"Đã xuất file {output_filename} thành công!")

if __name__ == "__main__":
    root = tk.Tk(); app = ExternalSortApp(root); root.mainloop()
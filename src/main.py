import tkinter as tk
from tkinter import filedialog, messagebox
import os
import utils
from algorithms import ExternalSortEngine

class ExternalSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("External Merge Sort Simulation - UIT")
        self.root.geometry("950x700")
        
        # Canvas hiển thị
        self.canvas = tk.Canvas(root, width=900, height=520, bg="white", highlightthickness=1, highlightbackground="#D3D3D3")
        self.canvas.pack(pady=10)
        
        self.engine = ExternalSortEngine()
        self.input_file_path = None 
        self.all_steps = []
        self.current_step_idx = -1
        self.data_blocks = [] 
        self.io_cost = 0
        
        # 1. TẠO UI CỐ ĐỊNH (Chỉ chạy 1 lần)
        self.create_controls() 
        
        # 2. VẼ CÁC KHUNG TRÊN CANVAS
        self.setup_canvas_frames()

    def create_controls(self):
        """Khởi tạo các nút bấm và nhãn - Chỉ gọi 1 lần trong __init__"""
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=5)

        # Hàng 1
        tk.Button(self.control_frame, text="Chọn File (.bin)", width=15, command=self.choose_file).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(self.control_frame, text="Tạo File Ngẫu Nhiên", width=15, command=self.gen_random).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.control_frame, text="Reset", width=15, command=self.reset_all, bg="#FFCDD2").grid(row=0, column=2, padx=5, pady=5)

        # Hàng 2
        self.btn_back = tk.Button(self.control_frame, text="<< Back", width=10, command=self.step_back, state="disabled")
        self.btn_back.grid(row=1, column=0, padx=5, pady=5)

        self.btn_start_sort = tk.Button(self.control_frame, text="BẮT ĐẦU SẮP XẾP", width=20, command=self.prepare_and_start, 
                                        state="disabled", bg="#BBDEFB", font=("Arial", 10, "bold"))
        self.btn_start_sort.grid(row=1, column=1, padx=5, pady=5)
        
        self.btn_next = tk.Button(self.control_frame, text="Next >>", width=10, command=self.step_next, state="disabled")
        self.btn_next.grid(row=1, column=2, padx=5, pady=5)
        
        tk.Button(self.control_frame, text="End (Xuất kết quả)", width=15, command=self.export_result, bg="#C8E6C9").grid(row=1, column=3, padx=5, pady=5)

        # Thông số
        self.lbl_io = tk.Label(self.root, text="Tổng Chi Phí I/O: 0", font=("Arial", 13, "bold"), fg="#D32F2F")
        self.lbl_io.pack()
        self.status = tk.Label(self.root, text="Bước 1: Vui lòng nạp file dữ liệu", font=("Arial", 10, "italic"), fg="#555")
        self.status.pack()

    def setup_canvas_frames(self):
        """Vẽ lại các khung hình chữ nhật trên Canvas (Gọi khi Reset/Back)"""
        # Xóa các hình vẽ cũ nhưng KHÔNG xóa các nút bấm ở ngoài canvas
        self.canvas.delete("all") 
        
        # Disk Storage
        self.canvas.create_rectangle(50, 30, 400, 500, outline="#0056b3", width=2)
        self.canvas.create_text(225, 15, text="DISK STORAGE", font=("Arial", 12, "bold"), fill="#0056b3")
        
        # RAM Buffer
        self.canvas.create_rectangle(500, 30, 850, 250, outline="#28a745", width=2)
        self.canvas.create_text(675, 15, text="RAM (3 BUFFER PAGES)", font=("Arial", 12, "bold"), fill="#28a745")

    def create_block(self, x, y, value):
        """Tạo block style xám chữ vàng cam."""
        rect = self.canvas.create_rectangle(x, y, x+75, y+35, fill="#4A4A4A", outline="#333", width=2)
        text = self.canvas.create_text(x+37, y+17, text=f"{value:.1f}", fill="#FFCC00", font=("Arial", 9, "bold"))
        return [rect, text]

    def move_block(self, block_obj, tx, ty, callback=None):
        """Hiệu ứng di chuyển mượt mà."""
        r_id, t_id = block_obj
        curr = self.canvas.coords(r_id)
        if not curr: return
        steps = 12
        dx, dy = (tx - curr[0]) / steps, (ty - curr[1]) / steps
        def anim(count):
            if count < steps:
                self.canvas.move(r_id, dx, dy)
                self.canvas.move(t_id, dx, dy)
                self.root.after(15, lambda: anim(count + 1))
            elif callback: callback()
        anim(0)

    # --- HOẠT ĐỘNG 1: NẠP FILE ---
    def load_file_only(self, path):
        self.reset_all()
        self.input_file_path = path
        data = utils.read_binary_file(path)
        
        if len(data) == 0:
            messagebox.showerror("Lỗi", "File không hợp lệ!")
            return

        if len(data) > 12:
            self.status.config(text=f"Dữ liệu lớn ({len(data)} số). Bấm 'BẮT ĐẦU' để xuất file.", fg="#E65100")
        else:
            self.status.config(text=f"Đã nạp {len(data)} số. Bước 2: Bấm 'BẮT ĐẦU SẮP XẾP'", fg="#0D47A1")
            self.data_blocks = []
            for i, v in enumerate(data):
                # Vị trí ban đầu trên Disk Storage
                bx, by = 70 + (i % 4) * 85, 50 + (i // 4) * 50
                self.data_blocks.append(self.create_block(bx, by, v))
        
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
        
        self.all_steps = self.engine.get_simulation_steps(self.input_file_path)

        if len(self.all_steps) > 0:
            self.current_step_idx = -1
            self.btn_next.config(state="normal") # Kích hoạt nút Next
            self.btn_start_sort.config(state="disabled") # Tắt nút Bắt đầu để tránh bấm trùng
            self.step_next()

        data = utils.read_binary_file(self.input_file_path)
        if len(data) <= 12:
            self.all_steps = self.engine.get_simulation_steps(self.input_file_path)
            self.current_step_idx = -1
            self.btn_next.config(state="normal")
            self.btn_start_sort.config(state="disabled")
            self.step_next() # Chạy bước INIT_DISK đầu tiên
        else:
            # Xử lý file lớn ngầm
            sorted_data = sorted(data)
            utils.write_binary_file("output_result.bin", sorted_data)
            messagebox.showinfo("Thành công", "Đã sắp xếp ngầm dữ liệu lớn và xuất file output_result.bin")

    def step_next(self):
        if self.current_step_idx < len(self.all_steps) - 1:
            self.current_step_idx += 1
            self.apply_step(self.all_steps[self.current_step_idx])
            self.btn_back.config(state="normal")
        if self.current_step_idx == len(self.all_steps) - 1:
            self.btn_next.config(state="disabled")

    def step_back(self):
        if self.current_step_idx >= 0:
            target_idx = self.current_step_idx - 1
            self.canvas.delete("all")
            self.setup_ui() # Vẽ lại khung
            # Nạp lại dữ liệu ban đầu
            data = utils.read_binary_file(self.input_file_path)
            self.data_blocks = []
            for i, v in enumerate(data):
                bx, by = 70 + (i % 4) * 85, 50 + (i // 4) * 50
                self.data_blocks.append(self.create_block(bx, by, v))
            
            # Chạy lại các bước đến target_idx (không dùng animation)
            old_steps = self.all_steps
            self.current_step_idx = -1
            for i in range(target_idx + 1):
                self.current_step_idx = i
                self.apply_step(old_steps[i], animate=False)
            
            self.btn_next.config(state="normal")
            if self.current_step_idx < 0: self.btn_back.config(state="disabled")

    def apply_step(self, step, animate=True):
        self.status.config(text=step['desc'])
        self.io_cost = step.get('io_cost', self.io_cost)
        self.lbl_io.config(text=f"Tổng Chi Phí I/O: {self.io_cost}")
        
        act = step['act']
        
        if act == 'INIT_DISK':
            pass

        if act == 'READ':
            for i in range(len(step['values'])):
                idx = step['idx'] + i
                tx, ty = 550 + i * 85, 100
                if animate: self.move_block(self.data_blocks[idx], tx, ty)
                else: self.canvas.coords(self.data_blocks[idx][0], tx, ty, tx+75, ty+35); self.canvas.coords(self.data_blocks[idx][1], tx+37, ty+17)

        elif act == 'SORT':
            for i, val in enumerate(step['values']):
                # Cập nhật text hiển thị số đã sort trong RAM
                self.canvas.itemconfig(self.data_blocks[i][1], text=f"{val:.1f}")
                self.canvas.itemconfig(self.data_blocks[i][0], fill="#3498DB") # Đổi sang màu xanh dương (đang xử lý)

        elif act == 'WRITE_RUN':
            for i in range(len(step['values'])):
                idx = step['idx'] + i
                # Vị trí lưu Run trên Disk (Phần dưới)
                tx, ty = 70 + (i % 4) * 85, 300 + step['run_idx'] * 50
                if animate: self.move_block(self.data_blocks[idx], tx, ty)
                else: self.canvas.coords(self.data_blocks[idx][0], tx, ty, tx+75, ty+35); self.canvas.coords(self.data_blocks[idx][1], tx+37, ty+17)
                self.canvas.itemconfig(self.data_blocks[idx][0], fill="#2ECC71") # Đổi màu xanh lá (Đã xong Run)

    def reset_all(self):
        self.canvas.delete("all")
        self.setup_ui()
        self.all_steps = []
        self.current_step_idx = -1
        self.input_file_path = None
        self.io_cost = 0
        self.lbl_io.config(text="Tổng Chi Phí I/O: 0")
        self.btn_next.config(state="disabled")
        self.btn_back.config(state="disabled")
        self.btn_start_sort.config(state="disabled")

    def export_result(self):
        if self.current_step_idx < len(self.all_steps) - 1:
            messagebox.showwarning("Chú ý", "Bạn phải hoàn thành sắp xếp trước khi xuất kết quả!")
            return
        
        final_data = self.all_steps[-1].get('values', [])
        utils.write_binary_file("sorted_output.bin", final_data)
        
        # Hiển thị kết quả trực quan
        res_win = tk.Toplevel(self.root)
        res_win.title("Dữ liệu đầu ra (.bin)")
        txt = tk.Text(res_win, font=("Consolas", 10), padx=10, pady=10)
        txt.pack()
        txt.insert("1.0", "--- KẾT QUẢ SAU KHI SẮP XẾP ---\n\n")
        for i, v in enumerate(final_data):
            txt.insert("end", f"Phần tử {i+1:02d}: {v:.2f}\n")
        txt.config(state="disabled")
        messagebox.showinfo("Thành công", "Đã xuất file sorted_output.bin")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExternalSortApp(root)
    root.mainloop()
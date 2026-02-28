import tkinter as tk
from tkinter import filedialog, messagebox
import os
import utils
from algorithms import ExternalSortEngine

class ExternalSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô phỏng External Merge Sort - UIT")
        self.root.geometry("1000x800")
        
        # Engine và biến logic
        self.engine = ExternalSortEngine(buffer_pages=3)
        self.input_file_path = None 
        self.all_steps = []
        self.current_step_idx = -1
        self.run_blocks = [] # Lưu các object (rect, text) của các Run
        self.io_cost = 0

        # Canvas hiển thị
        self.canvas = tk.Canvas(root, width=950, height=600, bg="#F5F5F5", highlightthickness=1)
        self.canvas.pack(pady=10)
        
        self.create_controls()
        self.draw_static_frames()

    def draw_rounded_rect(self, x1, y1, x2, y2, radius=15, **kwargs):
        """Vẽ hình chữ nhật bo tròn cho các Buffer"""
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def draw_static_frames(self):
        self.canvas.delete("all")
        # 1. RAM Buffer (3 Slots)
        self.canvas.create_text(200, 30, text="RAM BUFFER (3 PAGES)", font=("Arial", 11, "bold"), fill="green")
        for i in range(3):
            # Vẽ 3 ô RAM
            self.canvas.create_rectangle(50 + i*110, 50, 150 + i*110, 130, outline="green", width=2)
            self.canvas.create_text(100 + i*110, 145, text=f"Slot {i+1}", fill="green")

        # 2. Disk Area - Input (Giữa)
        self.canvas.create_text(200, 270, text="INPUT DISK AREA (Raw Data)", font=("Arial", 11, "bold"), fill="#555")
        self.canvas.create_rectangle(50, 290, 380, 420, outline="#777", dash=(5,2))

        # 3. Disk Area - Buffer F1 & F2 (Phía trên bên phải)
        self.draw_rounded_rect(450, 40, 680, 240, fill="", outline="#0056b3", width=2)
        self.canvas.create_text(565, 30, text="DISK BUFFER F1", font=("Arial", 11, "bold"), fill="#0056b3")
        
        self.draw_rounded_rect(710, 40, 940, 240, fill="", outline="#0056b3", width=2)
        self.canvas.create_text(825, 30, text="DISK BUFFER F2", font=("Arial", 11, "bold"), fill="#0056b3")

        # 4. Disk Area - Output (Phía dưới)
        self.draw_rounded_rect(450, 380, 940, 560, fill="", outline="#d32f2f", width=2)
        self.canvas.create_text(695, 370, text="OUTPUT DISK AREA (Sorted Runs)", font=("Arial", 11, "bold"), fill="#d32f2f")

    def create_run_ui_block(self, x, y, values):
        """Tạo 1 block UI đại diện cho 1 Run (chứa 2 số, cách nhau dấu phẩy)"""
        val_str = ", ".join([str(int(v)) for v in values])
        rect = self.canvas.create_rectangle(x, y, x+90, y+40, fill="#4A4A4A", outline="white", width=2)
        text = self.canvas.create_text(x+45, y+20, text=val_str, fill="#FFCC00", font=("Arial", 10, "bold"))
        return [rect, text]

    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        tk.Button(control_frame, text="Chọn File .bin", width=15, command=self.choose_file).grid(row=0, column=0, padx=5)
        tk.Button(control_frame, text="Tạo File 12 số", width=15, command=self.gen_test_file).grid(row=0, column=1, padx=5)
        tk.Button(control_frame, text="Reset", width=15, command=self.reset_all, bg="#FFCDD2").grid(row=0, column=2, padx=5)

        self.btn_next = tk.Button(control_frame, text="Next Step >>", width=15, command=self.step_next, state="disabled", bg="#BBDEFB")
        self.btn_next.grid(row=1, column=1, pady=10)

        self.lbl_io = tk.Label(self.root, text="Tổng Chi Phí I/O: 0", font=("Arial", 13, "bold"), fg="#D32F2F")
        self.lbl_io.pack()
        self.status = tk.Label(self.root, text="Vui lòng nạp file để bắt đầu", font=("Arial", 10, "italic"))
        self.status.pack()

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if path: self.load_and_init(path)

    def gen_test_file(self):
        path = utils.create_random_input("input_12.bin", 12)
        self.load_and_init(path)

    def load_and_init(self, path):
        self.reset_all()
        self.input_file_path = path
        data = utils.read_binary_file(path)
        
        if len(data) > 12:
            self.status.config(text="Dữ liệu > 12: Đã sắp xếp và xuất file sorted_output.bin")
            utils.write_binary_file("sorted_output.bin", sorted(data))
            messagebox.showinfo("Xử lý nhanh", "Số lượng phần tử lớn, hệ thống đã tự động xuất file kết quả.")
            return

        # Vẽ dữ liệu thô vào vùng Input Disk
        for i, v in enumerate(data):
            bx, by = 70 + (i % 4) * 75, 310 + (i // 4) * 35
            self.canvas.create_text(bx, by, text=str(int(v)), font=("Arial", 10), tags="raw_data")
        
        self.all_steps = self.engine.get_simulation_steps(path)
        self.current_step_idx = -1
        self.btn_next.config(state="normal")
        self.status.config(text="Đã nạp dữ liệu. Bấm 'Next Step' để xem mô phỏng Pass 0.")

    def apply_step(self, step):
        self.status.config(text=step['desc'])
        self.io_cost = step.get('io_cost', self.io_cost)
        self.lbl_io.config(text=f"Tổng Chi Phí I/O: {self.io_cost}")
        
        act = step['act']

        if act == 'LOAD_RAM':
            self.canvas.delete("raw_data") # Xóa số lẻ
            vals = step['values']
            # Chia 6 số thành 3 Blocks trong RAM
            for i in range(0, len(vals), 2):
                chunk = vals[i:i+2]
                block = self.create_run_ui_block(55 + (i//2)*110, 70, chunk)
                self.run_blocks.append(block)

        elif act == 'SORT_RAM':
            # Cập nhật nội dung các block trong RAM sau khi sort
            vals = step['values']
            for i in range(0, len(vals), 2):
                new_txt = ", ".join([str(int(v)) for v in vals[i:i+2]])
                self.canvas.itemconfig(self.run_blocks[i//2][1], text=new_txt)

        elif act == 'WRITE_F_BUFFER':
            # Di chuyển từ RAM sang F1 hoặc F2
            target = step['target']
            r_idx = step['run_idx']
            tx = 470 if target == "F1" else 730
            ty = 60 + r_idx * 55
            
            # Lấy block đầu tiên trong RAM di chuyển sang
            if self.run_blocks:
                b = self.run_blocks.pop(0)
                self.move_block_instant(b, tx, ty)

        elif act == 'FINISH':
            # Hiển thị kết quả cuối cùng tại vùng Output
            self.canvas.delete("all")
            self.draw_static_frames()
            vals = step['values']
            for i in range(0, len(vals), 2):
                chunk = vals[i:i+2]
                self.create_run_ui_block(470 + (i//2 % 4)*110, 400 + (i//8)*50, chunk)
            messagebox.showinfo("Hoàn tất", f"Sắp xếp ngoại hoàn tất!\nTổng IO: {self.io_cost}")

    def move_block_instant(self, block, tx, ty):
        """Di chuyển block đến vị trí mới ngay lập tức"""
        curr = self.canvas.coords(block[0])
        dx, dy = tx - curr[0], ty - curr[1]
        self.canvas.move(block[0], dx, dy)
        self.canvas.move(block[1], dx, dy)

    def step_next(self):
        if self.current_step_idx < len(self.all_steps) - 1:
            self.current_step_idx += 1
            self.apply_step(self.all_steps[self.current_step_idx])
        else:
            self.btn_next.config(state="disabled")

    def reset_all(self):
        self.draw_static_frames()
        self.io_cost = 0
        self.run_blocks = []
        self.current_step_idx = -1
        self.lbl_io.config(text="Tổng Chi Phí I/O: 0")
        self.btn_next.config(state="disabled")
        self.status.config(text="Hệ thống đã Reset.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExternalSortApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import filedialog, messagebox
import utils
from algorithms import ExternalSortEngine

class ExternalSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô phỏng External Merge Sort - UIT")
        self.root.geometry("1000x750")
        
        # Engine và biến logic
        self.engine = ExternalSortEngine(buffer_pages=3)
        self.input_file_path = None 
        self.all_steps = []
        self.current_step_idx = -1
        self.run_blocks = [] 
        self.io_cost = 0

        # Canvas hiển thị
        self.canvas = tk.Canvas(root, width=950, height=550, bg="white", highlightthickness=1)
        self.canvas.pack(pady=10)
        
        self.create_controls()
        self.draw_static_frames()

    def draw_static_frames(self):
        """Vẽ cấu trúc Disk và RAM với các Buffer bên trong"""
        self.canvas.delete("all")
        
        # --- KHU VỰC DISK (Bên trái) ---
        # Khung tổng Disk
        self.canvas.create_rectangle(30, 30, 450, 520, outline="#0056b3", width=2)
        self.canvas.create_text(240, 15, text="DISK STORAGE", font=("Arial", 12, "bold"), fill="#0056b3")

        # 1. Vùng Input Data (Dữ liệu thô)
        self.canvas.create_text(110, 50, text="[ Input Data Area ]", font=("Arial", 10, "italic"))
        self.canvas.create_rectangle(50, 65, 430, 180, outline="#777", dash=(5,2))

        # 2. Disk Buffer F1 (Chứa tối đa 3 run)
        self.canvas.create_text(110, 200, text="[ Disk Buffer F1 ]", font=("Arial", 10, "bold"), fill="#0056b3")
        for i in range(3):
            self.canvas.create_rectangle(50 + i*125, 215, 165 + i*125, 275, outline="#0056b3", dash=(2,2))

        # 3. Disk Buffer F2 (Chứa tối đa 3 run)
        self.canvas.create_text(110, 300, text="[ Disk Buffer F2 ]", font=("Arial", 10, "bold"), fill="#0056b3")
        for i in range(3):
            self.canvas.create_rectangle(50 + i*125, 315, 165 + i*125, 375, outline="#0056b3", dash=(2,2))

        # 4. Output Area
        self.canvas.create_text(110, 400, text="[ Output Sorted Area ]", font=("Arial", 10, "bold"), fill="#d32f2f")
        self.canvas.create_rectangle(50, 415, 430, 500, outline="#d32f2f", width=2)

        # --- KHU VỰC RAM (Bên phải) ---
        # Khung tổng RAM
        self.canvas.create_rectangle(520, 30, 920, 520, outline="#28a745", width=2)
        self.canvas.create_text(720, 15, text="RAM (3 BUFFER PAGES)", font=("Arial", 12, "bold"), fill="#28a745")

        # Các ô Buffer trong RAM
        for i in range(3):
            # Mỗi ô Buffer trong RAM
            self.canvas.create_rectangle(550, 60 + i*150, 890, 180 + i*150, outline="#28a745", width=2)
            self.canvas.create_text(720, 50 + i*150, text=f"RAM Page {i+1}", fill="#28a745", font=("Arial", 9, "bold"))

    def create_run_ui_block(self, x, y, values):
        """Tạo khối Run gồm 2 phần tử cách nhau bằng dấu phẩy"""
        val_str = ", ".join([str(int(v)) for v in values])
        # Hình chữ nhật bo tròn nhẹ (giả lập bằng polygon hoặc rect)
        rect = self.canvas.create_rectangle(x, y, x+100, y+45, fill="#4A4A4A", outline="white", width=2)
        text = self.canvas.create_text(x+50, y+22, text=val_str, fill="#FFCC00", font=("Arial", 10, "bold"))
        return [rect, text]

    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        tk.Button(control_frame, text="Nạp File (.bin)", width=15, command=self.choose_file).grid(row=0, column=0, padx=5)
        tk.Button(control_frame, text="Tạo 12 số", width=15, command=self.gen_test_file).grid(row=0, column=1, padx=5)
        tk.Button(control_frame, text="Reset", width=15, command=self.reset_all, bg="#FFCDD2").grid(row=0, column=2, padx=5)

        self.btn_next = tk.Button(control_frame, text="Bước tiếp theo >>", width=20, command=self.step_next, state="disabled", bg="#BBDEFB")
        self.btn_next.grid(row=1, column=1, pady=10)

        self.lbl_io = tk.Label(self.root, text="Tổng Chi Phí I/O: 0", font=("Arial", 13, "bold"), fg="#D32F2F")
        self.lbl_io.pack()
        self.status = tk.Label(self.root, text="Trạng thái: Sẵn sàng", font=("Arial", 10, "italic"))
        self.status.pack()

    def choose_file(self):
        path = filedialog.askopenfilename()
        if path: self.load_and_init(path)

    def gen_test_file(self):
        path = utils.create_random_input("input_12.bin", 12)
        self.load_and_init(path)

    def load_and_init(self, path):
        self.reset_all()
        self.input_file_path = path
        data = utils.read_binary_file(path)
        
        if len(data) > 12:
            self.status.config(text="Dữ liệu lớn: Đã xuất file trực tiếp.")
            utils.write_binary_file("sorted_output.bin", sorted(data))
            return

        # Sửa đổi: Lưu các ID của text để xóa dần
        self.raw_data_texts = [] 
        for i, v in enumerate(data):
            bx, by = 70 + (i % 4) * 85, 85 + (i // 4) * 35
            t_id = self.canvas.create_text(bx, by, text=str(int(v)), font=("Arial", 10, "bold"))
            self.raw_data_texts.append(t_id)
        
        self.all_steps = self.engine.get_simulation_steps(path)
        self.current_step_idx = -1
        self.btn_next.config(state="normal")

    def apply_step(self, step):
        self.status.config(text=step['desc'])
        self.io_cost = step.get('io_cost', self.io_cost)
        self.lbl_io.config(text=f"Tổng Chi Phí I/O: {self.io_cost}")
        
        act = step['act']

        if act == 'LOAD_RAM':
            # Chỉ xóa các số được nạp vào RAM, các số khác vẫn ở lại Disk
            indices_to_remove = step.get('indices', [])
            for idx in indices_to_remove:
                if self.raw_data_texts[idx] is not None:
                    self.canvas.delete(self.raw_data_texts[idx])
                    self.raw_data_texts[idx] = None # Đánh dấu đã xóa

            vals = step['values']
            for i in range(0, len(vals), 2):
                chunk = vals[i:i+2]
                block = self.create_run_ui_block(650, 85 + (i//2)*150, chunk)
                self.run_blocks.append(block)

        elif act == 'MERGE_LOAD_RAM':
            # Xóa các block cũ ở Disk (giả định lấy từ đầu danh sách hiển thị)
            # Ở đây chúng ta tạo block mới trong RAM để mô phỏng việc nạp
            b1 = self.create_run_ui_block(650, 85, step['r1']) # RAM Page 1
            b2 = self.create_run_ui_block(650, 235, step['r2']) # RAM Page 2
            self.merge_blocks = [b1, b2] # Lưu để quản lý

        elif act == 'MERGE_SORT_RAM':
            # Vẽ run kết quả vào RAM Page 3
            b_out = self.create_run_ui_block(650, 385, step['values'])
            self.merge_blocks.append(b_out)
            # Đổi màu block Page 3 để phân biệt là kết quả trộn
            self.canvas.itemconfig(b_out[0], fill="#2ECC71") 

        elif act == 'WRITE_OUTPUT':
            # Lấy block từ RAM Page 3 đưa xuống Output Disk
            if len(self.merge_blocks) > 2:
                res_block = self.merge_blocks.pop(2)
                # Tọa độ vùng Output Disk (x=50, y=420)
                self.move_block_instant(res_block, 60, 430)
                
                # Xóa 2 block nguồn trong RAM sau khi trộn xong
                for b in self.merge_blocks:
                    self.canvas.delete(b[0])
                    self.canvas.delete(b[1])
                self.merge_blocks = []

        elif act == 'FINISH':
            messagebox.showinfo("Thành công", f"Đã sắp xếp xong! Tổng I/O: {self.io_cost}")

    def move_block_instant(self, block, tx, ty):
        curr = self.canvas.coords(block[0])
        self.canvas.move(block[0], tx - curr[0], ty - curr[1])
        self.canvas.move(block[1], tx - curr[0], ty - curr[1])

    def step_next(self):
        if self.current_step_idx < len(self.all_steps) - 1:
            self.current_step_idx += 1
            self.apply_step(self.all_steps[self.current_step_idx])

    def reset_all(self):
        self.draw_static_frames()
        self.io_cost = 0
        self.run_blocks = []
        self.current_step_idx = -1
        self.btn_next.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExternalSortApp(root)
    root.mainloop()
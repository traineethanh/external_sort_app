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
        self.all_steps = []
        self.current_step_idx = -1
        self.data_blocks = []  # Lưu đối tượng (rect, text) trên canvas
        self.io_cost = 0
        self.is_auto_running = False
        
        self.setup_ui()

    def setup_ui(self):
        # --- VÙNG CANVAS (Vẽ Disk và RAM) ---
        # Vẽ khung Disk [cite: 43, 63, 263]
        self.canvas.create_rectangle(50, 20, 400, 520, outline="blue", width=2)
        self.canvas.create_text(225, 10, text="DISK STORAGE", font=("Arial", 12, "bold"))
        
        # Vẽ khung RAM (3 Buffer Pages) [cite: 18, 44, 45, 265]
        self.canvas.create_rectangle(500, 20, 850, 250, outline="green", width=2)
        self.canvas.create_text(675, 10, text="RAM (MAIN MEMORY)", font=("Arial", 12, "bold"))
        
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
        
        self.btn_start = tk.Button(control_frame, text="Bắt đầu", command=self.toggle_auto_run, state="disabled", bg="#BBDEFB")
        self.btn_start.grid(row=1, column=1, padx=5, pady=5)

        self.btn_next = tk.Button(control_frame, text="Next >>", command=self.step_next, state="disabled")
        self.btn_next.grid(row=1, column=2, padx=5, pady=5)
        
        tk.Button(control_frame, text="End (Xuất kết quả)", command=self.export_result, bg="#C8E6C9").grid(row=1, column=3, padx=5)

        # Thông số hiển thị IO Cost [cite: 19, 359]
        self.lbl_io = tk.Label(self.root, text="IO Cost: 0", font=("Arial", 12, "bold"), fg="red")
        self.lbl_io.pack()
        self.status = tk.Label(self.root, text="Vui lòng chọn hoặc tạo file để bắt đầu", font=("Arial", 10, "italic"))
        self.status.pack()

    def create_block(self, x, y, value):
        """Tạo block màu xám đậm, chữ vàng theo style đồ án."""
        rect = self.canvas.create_rectangle(x, y, x+75, y+35, fill="#4A4A4A", outline="#707070", width=2)
        text = self.canvas.create_text(x+37, y+17, text=f"{value:.1f}", fill="#FFCC00", font=("Arial", 9, "bold"))
        return rect, text

    def move_block(self, block_obj, tx, ty, callback=None):
        """Hiệu ứng di chuyển block mượt mà."""
        r_id, t_id = block_obj
        curr = self.canvas.coords(r_id)
        if not curr: return
        steps = 10
        dx, dy = (tx - curr[0]) / steps, (ty - curr[1]) / steps
        
        def anim(count):
            if count < steps:
                self.canvas.move(r_id, dx, dy)
                self.canvas.move(t_id, dx, dy)
                self.root.after(20, lambda: anim(count + 1))
            elif callback: callback()
        anim(0)

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if path: self.load_simulation(path)

    def gen_random(self):
        path = utils.create_random_input("input_test.bin", 12)
        self.load_simulation(path)

    def load_simulation(self, path):
        data = utils.read_binary_file(path)
        count = len(data)
        if count <= 12:
            self.reset_all()
            self.all_steps = self.engine.get_simulation_steps(path)
            self.current_step_idx = -1
            self.btn_next.config(state="normal")
            self.btn_start.config(state="normal")
            self.status.config(text=f"File có {count} phần tử. Sẵn sàng mô phỏng.", fg="blue")
        else:
            self.reset_all()
            self.status.config(text=f"Dữ liệu lớn ({count} số). Đang xuất kết quả...", fg="orange")
            sorted_data = sorted(data)
            utils.write_binary_file("output_result.bin", sorted_data)
            messagebox.showinfo("Thông báo", f"Dữ liệu lớn. Kết quả đã xuất ra file: output_result.bin")

    def toggle_auto_run(self):
        if not self.is_auto_running:
            self.is_auto_running = True
            self.btn_start.config(text="Dừng", bg="#FFAB91")
            self.auto_run_loop()
        else:
            self.is_auto_running = False
            self.btn_start.config(text="Bắt đầu", bg="#BBDEFB")

    def auto_run_loop(self):
        if self.is_auto_running and self.current_step_idx < len(self.all_steps) - 1:
            self.step_next()
            self.root.after(1200, self.auto_run_loop)
        else:
            self.is_auto_running = False
            self.btn_start.config(text="Bắt đầu", bg="#BBDEFB")

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
            self.reset_canvas_only()
            self.current_step_idx = -1
            for i in range(target_idx + 1):
                # Thực hiện nhanh không delay để quay lại trạng thái cũ
                self.apply_step(self.all_steps[i])
            self.current_step_idx = target_idx
            self.btn_next.config(state="normal")
        if self.current_step_idx < 0: self.btn_back.config(state="disabled")

    def apply_step(self, step):
        """Thực thi logic từng bước từ Engine[cite: 255, 580]."""
        self.status.config(text=step['desc'])
        self.io_cost = step.get('io_cost', self.io_cost)
        self.lbl_io.config(text=f"IO Cost: {self.io_cost}")

        if step['act'] == 'INIT_DISK':
            self.data_blocks = []
            for i, v in enumerate(step['values']):
                bx, by = 70 + (i % 4) * 85, 50 + (i // 4) * 50
                self.data_blocks.append(self.create_block(bx, by, v))

        elif step['act'] == 'READ':
            for i in range(len(step['values'])):
                idx = step['idx'] + i
                self.move_block(self.data_blocks[idx], 520 + i*85, 100)

        elif step['act'] == 'WRITE_RUN':
            for i in range(len(step['values'])):
                idx = step['idx'] + i
                # Di chuyển về Disk nhưng ở vị trí Run tương ứng
                self.move_block(self.data_blocks[idx], 70 + (i%4)*85, 250 + step['run_idx']*50)

    def reset_all(self):
        self.is_auto_running = False
        self.reset_canvas_only()
        self.all_steps = []
        self.io_cost = 0
        self.lbl_io.config(text="IO Cost: 0")
        self.btn_next.config(state="disabled")
        self.btn_back.config(state="disabled")
        self.btn_start.config(state="disabled")

    def reset_canvas_only(self):
        self.canvas.delete("all")
        self.setup_ui()

    def export_result(self):
        if self.current_step_idx < len(self.all_steps) - 1:
            messagebox.showwarning("Cảnh báo", "Sắp xếp chưa kết thúc!")
            return
        
        final_step = self.all_steps[-1]
        sorted_data = final_step.get('values', [])
        utils.write_binary_file("sorted_output.bin", sorted_data)
        
        res_win = tk.Toplevel(self.root)
        res_win.title("Kết quả")
        txt = tk.Text(res_win, font=("Arial", 11), width=30, height=15)
        txt.pack(padx=10, pady=10)
        txt.insert("1.0", "DANH SÁCH ĐÃ SẮP XẾP:\n" + "-"*20 + "\n")
        for i, v in enumerate(sorted_data):
            txt.insert("insert", f"{i+1}. {v:.2f}\n")
        txt.config(state="disabled")
        messagebox.showinfo("Thành công", "Đã xuất kết quả ra sorted_output.bin")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExternalSortApp(root)
    root.mainloop()
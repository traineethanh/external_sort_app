import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import utils
import struct
import random
from algorithms import ExternalSortEngine
import shutil
from tkinter import scrolledtext
import os

class OutputWindow(tk.Toplevel):
    """Cửa sổ phụ hiển thị kết quả cho file dữ liệu lớn"""
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.title("Kết quả Sắp xếp (Dữ liệu lớn)")
        self.geometry("400x500")
        
        tk.Label(self, text="Dữ liệu đã được sắp xếp hoàn tất:", font=("Arial", 11, "bold")).pack(pady=10)
        
        # Khung văn bản có thanh cuộn
        self.txt_area = scrolledtext.ScrolledText(self, width=40, height=20, font=("Courier New", 10))
        self.txt_area.pack(padx=20, pady=10)
        
        data = utils.read_binary_file(file_path)
        content = "\n".join([f"Vị trí {i+1:03d}:  {int(v)}" for i, v in enumerate(data)])
        
        self.txt_area.insert(tk.END, content)
        self.txt_area.config(state="disabled") # Chỉ cho đọc

class ExternalSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô phỏng External Merge Sort - UIT")
        self.root.geometry("1000x750")
        
        # Engine và biến logic
        self.engine = ExternalSortEngine(buffer_pages=3)
        self.input_file_path = None 
        self.is_auto = False 
        self.all_steps = []
        self.raw_data_texts = []
        self.current_step_idx = -1
        self.run_blocks = [] 
        self.io_cost = 0
        self.f1_blocks = []  # Quản lý các block ở Disk Buffer F1
        self.f2_blocks = []  # Quản lý các block ở Disk Buffer F2
        self.merge_input_blocks = [] # Quản lý block đầu vào lúc Merge trong RAM

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

    def create_run_ui_block(self, x, y, values, is_output=False):
        """Tạo khối UI linh hoạt. Nếu là output thì thu nhỏ kích thước."""
        if not values: return None
        
        # Cấu hình kích thước: RAM (100x45), Output (70x35)
        w = 70 if is_output else 100
        h = 35 if is_output else 45
        font_size = 8 if is_output else 10
        
        val_str = ", ".join([f"{float(v):.2f}" for v in values])
        
        # Vẽ block
        rect = self.canvas.create_rectangle(x, y, x + w, y + h, fill="#4A4A4A", outline="white", width=2)
        text = self.canvas.create_text(x + w/2, y + h/2, text=val_str, fill="#FFCC00", font=("Arial", font_size, "bold"))
        return [rect, text]

    def create_controls(self):
        # --- FRAME CHÍNH ---
        # Sử dụng LabelFrame để tạo các nhóm chức năng rõ ràng
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill="x", side="bottom")

        # 1. CỤM CẤU HÌNH DỮ LIỆU (Bên trái)
        data_group = tk.LabelFrame(main_frame, text=" Cấu hình dữ liệu ", padx=10, pady=10, fg="#1976D2")
        data_group.pack(side="left", padx=5, fill="y")

        # Ô nhập số lượng
        tk.Label(data_group, text="Số lượng:").grid(row=0, column=0, sticky="w")
        self.ent_count = tk.Entry(data_group, width=8, justify='center')
        self.ent_count.insert(0, "12")
        self.ent_count.grid(row=0, column=1, padx=5)

        # Nút Tạo Random (Thay thế cho nút tạo 12 số cũ)
        tk.Button(data_group, text="🎲 Tạo Random", width=15, command=self.gen_custom_file, 
                bg="#E3F2FD", cursor="hand2").grid(row=1, column=0, columnspan=2, pady=5)

        # Nút Nạp File
        tk.Button(data_group, text="📁 Nạp File .bin", width=15, command=self.choose_file,
                cursor="hand2").grid(row=2, column=0, columnspan=2)

        # 2. CỤM ĐIỀU KHIỂN CHẠY (Ở giữa - Quan trọng nhất)
        run_group = tk.LabelFrame(main_frame, text=" Thực thi thuật toán ", padx=15, pady=10, fg="#2E7D32")
        run_group.pack(side="left", padx=5, expand=True, fill="both")

        self.btn_next = tk.Button(run_group, text="BƯỚC TIẾP THEO >>", width=30, height=2, 
                                command=self.step_next, state="disabled", 
                                bg="#BBDEFB", font=("Arial", 10, "bold"), cursor="hand2")
        self.btn_next.pack(pady=2)

        self.btn_auto = tk.Button(run_group, text="CHẠY TỰ ĐỘNG ▶", width=30, 
                                command=self.toggle_auto, state="disabled", 
                                bg="#C8E6C9", cursor="hand2")
        self.btn_auto.pack(pady=2)

        # 3. CỤM TIỆN ÍCH (Bên phải)
        util_group = tk.LabelFrame(main_frame, text=" Hệ thống ", padx=10, pady=10, fg="#D32F2F")
        util_group.pack(side="left", padx=5, fill="y")

        tk.Button(util_group, text="🔄 Reset Máy", width=15, command=self.reset_all, 
                bg="#FFCDD2", cursor="hand2").pack(pady=5)
        
        tk.Button(util_group, text="💾 Xuất Kết Quả", width=15, command=self.export_file, 
                bg="#E1F5FE", cursor="hand2").pack(pady=5)

        # --- PHẦN THÔNG TIN TRẠNG THÁI (Dưới cùng) ---
        info_frame = tk.Frame(self.root)
        info_frame.pack(fill="x", side="bottom")

        self.lbl_io = tk.Label(info_frame, text="Tổng Chi Phí I/O: 0", font=("Arial", 13, "bold"), fg="#D32F2F")
        self.lbl_io.pack()

        self.status = tk.Label(info_frame, text="Trạng thái: Sẵn sàng", font=("Arial", 10, "italic"), fg="#666")
        self.status.pack(pady=(0, 10))

    def gen_custom_file(self):
        """Lấy số lượng từ Entry và tạo file test với số thực ngẫu nhiên"""
        try:
            count_str = self.ent_count.get()
            count = int(count_str)
            
            if count <= 0:
                raise ValueError("Số lượng phải lớn hơn 0")
            
            if count > 10000:
                if not messagebox.askyesno("Cảnh báo", "Dữ liệu lớn có thể làm chậm quá trình mô phỏng. Tiếp tục?"):
                    return

            # 1. Tạo danh sách số thực ngẫu nhiên (có thể trùng)
            # uniform(10, 500) tạo số thực, round(..., 2) lấy 2 chữ số thập phân
            data = [round(random.uniform(10.0, 500.0), 2) for _ in range(count)]
            
            filename = f"input_{count}.bin"
            
            # 2. Ghi trực tiếp vào file binary theo định dạng float ('f')
            # 'f' tương ứng với 4 bytes mỗi số
            with open(filename, 'wb') as f:
                f.write(struct.pack(f'{len(data)}f', *data))
            
            # 3. Nạp dữ liệu vào ứng dụng
            self.load_and_init(filename)
            messagebox.showinfo("Thành công", f"Đã tạo {count} số thực ngẫu nhiên vào file {filename}")
            
        except ValueError as e:
            messagebox.showerror("Lỗi", f"Dữ liệu nhập vào không hợp lệ: {e}")
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể tạo file: {e}")
            
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
        
        # XỬ LÝ DỮ LIỆU LỚN (> 12 số)
        if len(data) > 12:
            try:
                self.status.config(text="Dữ liệu lớn: Đang xử lý...")
                output_path = "sorted_output.bin"
                utils.write_binary_file(output_path, sorted(data))
                OutputWindow(self.root, output_path) 
            except Exception as e:
                messagebox.showerror("Lỗi dữ liệu", f"Không thể tạo file tạm: {e}")
            return

        # Nếu <= 12 số, tiếp tục vẽ lên Canvas
        self.raw_data_texts = [] 
        for i, v in enumerate(data):
            bx, by = 70 + (i % 4) * 85, 85 + (i // 4) * 35
            t_id = self.canvas.create_text(bx, by, text=str(int(v)), font=("Arial", 10, "bold"))
            self.raw_data_texts.append(t_id)
        
        self.all_steps = self.engine.get_simulation_steps(path)
        self.current_step_idx = -1
        self.btn_next.config(state="normal")
        self.btn_auto.config(state="normal") # Kích hoạt nút Auto
    def export_file(self):
        """Cho phép người dùng lưu file đã sắp xếp ra vị trí khác"""
        # 1. Xác định file nguồn (Tên file phải khớp với file bạn tạo ra trong load_and_init)
        source_path = "sorted_output.bin" 

        # KIỂM TRA FILE CÓ TỒN TẠI KHÔNG
        if not os.path.exists(source_path):
            messagebox.showwarning("Thông báo", 
                f"Không tìm thấy file '{source_path}'.\n\nBạn cần chạy sắp xếp dữ liệu lớn hoặc đợi thuật toán hoàn tất trước khi xuất.")
            return

        # 2. Mở hộp thoại lưu file
        target_path = filedialog.asksaveasfilename(
            defaultextension=".bin",
            filetypes=[("Binary files", "*.bin"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Chọn nơi lưu file kết quả"
        )

        # 3. Thực hiện copy nếu người dùng không nhấn Cancel
        if target_path:
            try:
                shutil.copy(source_path, target_path)
                messagebox.showinfo("Thành công", f"Đã xuất file thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi hệ thống", f"Lỗi khi lưu file: {e}")

    def toggle_auto(self):
        """Bật/Tắt chế độ tự động chạy"""
        if not self.is_auto:
            self.is_auto = True
            self.btn_auto.config(text="Dừng Auto ⏸", bg="#FFCC80")
            self.auto_loop()
        else:
            self.is_auto = False
            self.btn_auto.config(text="Chạy Auto ▶", bg="#C8E6C9")

    def auto_loop(self):
        """Vòng lặp chạy bước tiếp theo sau mỗi khoảng thời gian"""
        if self.is_auto and self.current_step_idx < len(self.all_steps) - 1:
            self.step_next()
            self.root.after(800, self.auto_loop) # Chạy sau 800ms
        elif self.current_step_idx >= len(self.all_steps) - 1:
            self.is_auto = False
            self.btn_auto.config(text="Chạy Auto ▶", bg="#C8E6C9", state="disabled")

    def apply_step(self, step):
        self.status.config(text=step['desc'])
        self.io_cost = step.get('io_cost', self.io_cost)
        self.lbl_io.config(text=f"Tổng Chi Phí I/O: {self.io_cost}")
        
        act = step['act']

        # --- GIAI ĐOẠN 0: TẠO RUN ---
        if act == 'LOAD_RAM':
            indices = step.get('indices', [])
            for idx in indices:
                if self.raw_data_texts[idx]:
                    self.canvas.delete(self.raw_data_texts[idx])
                    self.raw_data_texts[idx] = None
            
            vals = step['values']
            for i in range(0, len(vals), 2):
                chunk = vals[i:i+2]
                block = self.create_run_ui_block(650, 85 + (i//2)*150, chunk)
                self.run_blocks.append(block)

        elif act == 'SORT_RAM':
            vals = step['values']
            for i in range(0, len(vals), 2):
                new_txt = ", ".join([str(int(v)) for v in vals[i:i+2]])
                self.canvas.itemconfig(self.run_blocks[i//2][0], fill="#3498DB") 
                self.canvas.itemconfig(self.run_blocks[i//2][1], text=new_txt)

        elif act == 'WRITE_F_BUFFER':
            target, r_idx = step['target'], step['run_idx']
            tx, ty = 55 + r_idx*125, (220 if target == "F1" else 320)
            if self.run_blocks:
                b = self.run_blocks.pop(0)
                self.move_block(b, tx, ty)
                if target == "F1": self.f1_blocks.append(b)
                else: self.f2_blocks.append(b)

        # --- GIAI ĐOẠN 2: TRỘN (MERGE) - LOGIC REPACKING ---
        elif act == 'MERGE_LOAD_RAM':
            # Xóa triệt để các block cũ trên Disk F1/F2
            if self.f1_blocks:
                old = self.f1_blocks.pop(0)
                self.canvas.delete(old[0]); self.canvas.delete(old[1])
            if self.f2_blocks:
                old = self.f2_blocks.pop(0)
                self.canvas.delete(old[0]); self.canvas.delete(old[1])
            
            # Reset mảng quản lý RAM để đảm bảo sạch sẽ
            self.merge_input_blocks = [None, None, None]
            
            # Tạo mới trên RAM (Page 1 & 2)
            self.merge_input_blocks[0] = self.create_run_ui_block(650, 85, step['r1'])
            self.merge_input_blocks[1] = self.create_run_ui_block(650, 235, step['r2'])

        elif act == 'REPACK_RAM':
            # 1. Xóa sạch 3 ô RAM hiện tại để vẽ lại trạng thái Repack
            for b in self.merge_input_blocks:
                if b:
                    self.canvas.delete(b[0])
                    self.canvas.delete(b[1])
            
            # 2. Vẽ lại trạng thái mới (Tách số dư)
            b1 = self.create_run_ui_block(650, 85, step['p1']) if step['p1'] else None
            b2 = self.create_run_ui_block(650, 235, step['p2']) if step['p2'] else None
            b3 = self.create_run_ui_block(650, 385, step['p3']) # Page 3 luôn có dữ liệu để xuất
            
            self.canvas.itemconfig(b3[0], fill="#2ECC71") # Màu xanh lá cho Page 3
            self.merge_input_blocks = [b1, b2, b3]

        elif act == 'REPACK_SHIFT_DOWN':
            # FIX: Xóa run ở Disk khi bắt đầu Pass 1
            sources = step.get('clear_sources', [])
            for src in sources:
                if src == "F1" and self.f1_blocks:
                    b = self.f1_blocks.pop(0)
                    self.canvas.delete(b[0]); self.canvas.delete(b[1])
                elif src == "F2" and self.f2_blocks:
                    b = self.f2_blocks.pop(0)
                    self.canvas.delete(b[0]); self.canvas.delete(b[1])

            self.clear_ram_visuals() # Xóa RAM cũ
            y_coords = [85, 235, 385]
            p_data = [step.get('p1'), step.get('p2'), step.get('p3')]
            for i in range(3):
                if p_data[i]:
                    self.merge_input_blocks[i] = self.create_run_ui_block(650, y_coords[i], p_data[i])

        elif act == 'WRITE_OUTPUT':
            if self.merge_input_blocks[2]:
                res_block = self.merge_input_blocks[2]
                self.merge_input_blocks[2] = None 
                
                # Tính toán vị trí mới trong Output Area
                out_idx = step.get('output_idx', 0)
                # Khoảng cách x (dx) bây giờ nhỏ hơn (ví dụ 80 thay vì 125) để xếp vừa nhiều Run hơn
                tx = 55 + (out_idx % 5) * 75  # Chia làm 5 cột, mỗi cột cách nhau 75px
                ty = 425 + (out_idx // 5) * 40 # Nếu đầy 1 hàng thì xuống hàng tiếp theo
                
                # CẬP NHẬT KÍCH THƯỚC KHỐI KHI DI CHUYỂN
                # Vì Tkinter không cho resize rect trực tiếp dễ dàng, 
                # ta vẽ một khối mới nhỏ hơn tại vị trí đích và xóa khối cũ khi animation kết thúc.
                
                def on_move_done():
                    # Xóa khối to vừa bay tới
                    self.canvas.delete(res_block[0])
                    self.canvas.delete(res_block[1])
                    # Vẽ khối nhỏ thay thế ngay tại đó
                    new_small_block = self.create_run_ui_block(tx, ty, step['values'], is_output=True)
                    self.canvas.itemconfig(new_small_block[0], fill="#D32F2F") # Màu đỏ cho Output

                self.move_block(res_block, tx, ty, callback=on_move_done)

        elif act == 'REF_LOAD_TOP':
            # FIX: Xóa run ở Disk khi nạp thêm vào Page 1
            source = step.get('source')
            if source == "F1" and self.f1_blocks:
                b = self.f1_blocks.pop(0)
                self.canvas.delete(b[0]); self.canvas.delete(b[1])
            elif source == "F2" and self.f2_blocks:
                b = self.f2_blocks.pop(0)
                self.canvas.delete(b[0]); self.canvas.delete(b[1])

            # Vẽ lại Page 1 trong RAM
            if self.merge_input_blocks[0]:
                self.canvas.delete(self.merge_input_blocks[0][0])
                self.canvas.delete(self.merge_input_blocks[0][1])
            self.merge_input_blocks[0] = self.create_run_ui_block(650, 85, step['values'])

    def clear_ram_visuals(self):
        """Hàm xóa RAM phải nằm riêng biệt để gọi ở mỗi bước dịch chuyển"""
        if hasattr(self, 'merge_input_blocks'):
            for block in self.merge_input_blocks:
                if block:
                    self.canvas.delete(block[0])
                    self.canvas.delete(block[1])
        self.merge_input_blocks = [None, None, None]

    def move_block(self, block_obj, tx, ty, callback=None):
        """Hiệu ứng di chuyển mượt mà từ vị trí hiện tại đến (tx, ty)"""
        r_id, t_id = block_obj
        curr = self.canvas.coords(r_id)
        if not curr: return
        
        steps = 15 # Số khung hình của chuyển động
        dx = (tx - curr[0]) / steps
        dy = (ty - curr[1]) / steps

        def anim(count):
            if count < steps:
                self.canvas.move(r_id, dx, dy)
                self.canvas.move(t_id, dx, dy)
                self.root.after(20, lambda: anim(count + 1))
            else:
                if callback: callback()

        anim(0)

    def step_next(self):
        if self.current_step_idx < len(self.all_steps) - 1:
            self.current_step_idx += 1
            self.apply_step(self.all_steps[self.current_step_idx])

    def reset_all(self):
        self.draw_static_frames()
        self.io_cost = 0
        self.run_blocks = []
        self.f1_blocks = []
        self.f2_blocks = []
        self.merge_input_blocks = []
        self.current_step_idx = -1
        self.btn_next.config(state="disabled")
        self.raw_data_texts = []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExternalSortApp(root)
    root.mainloop()
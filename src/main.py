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

    def create_run_ui_block(self, x, y, values):
        """Tạo khối UI linh hoạt cho cả 1 hoặc 2 phần tử"""
        if not values: return None
        val_str = ", ".join([str(int(v)) for v in values])
        # Vẽ block
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
            # Xử lý xóa block ở Disk nếu đây là bước khởi đầu Pass 1
            sources_to_clear = step.get('clear_sources', [])
            for src in sources_to_clear:
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
                self.merge_input_blocks[2] = None # Giải phóng slot Page 3 trên logic UI
                
                out_idx = step.get('output_idx', 0)
                tx = 55 + (out_idx % 3) * 125 
                ty = 435
                self.move_block(res_block, tx, ty)
                self.canvas.itemconfig(res_block[0], fill="#D32F2F")

        elif act == 'REF_LOAD_TOP':
            # --- PHẦN FIX LỖI: Xóa block ở Disk khi nạp ---
            source = step.get('source')
            if source == "F1" and self.f1_blocks:
                b = self.f1_blocks.pop(0)
                self.canvas.delete(b[0]) # Xóa hình chữ nhật
                self.canvas.delete(b[1]) # Xóa chữ
            elif source == "F2" and self.f2_blocks:
                b = self.f2_blocks.pop(0)
                self.canvas.delete(b[0])
                self.canvas.delete(b[1])
            # ------------------------------------------

            # Xóa Page 1 cũ trong RAM và vẽ cái mới (giữ nguyên code cũ của bạn)
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
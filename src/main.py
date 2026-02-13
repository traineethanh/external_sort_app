import tkinter as tk
from tkinter import ttk, messagebox
import utils
from algorithms import ExternalSort
import os

class SmoothAnimationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UIT - External Sort Full Motion - Quang Thanh")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        
        self.sorter = ExternalSort()
        self.setup_layout()
        self.data_objects = {}  # Lưu trữ các block dữ liệu gốc
        self.run_objects = {}   # Lưu trữ các block dữ liệu trong các Run

    def setup_layout(self):
        # 1. Vùng Disk Gốc (Dưới cùng) -
        self.canvas.create_rectangle(50, 450, 750, 580, outline="black", width=2)
        self.canvas.create_text(400, 435, text="INPUT DISK (DỮ LIỆU BAN ĐẦU)", font=("Arial", 10, "bold"))
        
        # 2. Vùng RAM / Buffer (Ở giữa) -
        self.canvas.create_rectangle(200, 200, 600, 320, outline="blue", width=2, fill="#F0F8FF")
        self.canvas.create_text(400, 185, text="MAIN MEMORY (RAM BUFFER)", font=("Arial", 10, "bold"))
        
        # 3. Vùng Disk Tạm / Output (Trên cùng) -
        self.canvas.create_rectangle(50, 20, 750, 150, outline="green", width=2)
        self.canvas.create_text(400, 10, text="OUTPUT DISK (SORTED RUNS / BUFFER)", font=("Arial", 10, "bold"))
        
        self.desc_label = tk.Label(self.root, text="Nhấn nút để bắt đầu mô phỏng chuyển động", font=("Arial", 11))
        self.desc_label.pack(pady=10)
        
        tk.Button(self.root, text="CHẠY MÔ PHỎNG TOÀN QUY TRÌNH", command=self.start, bg="#0078D7", fg="white", font=("Arial", 10, "bold")).pack()

    def move_item(self, item_id, tx, ty, callback=None):
        """Di chuyển vật thể mượt mà đến tọa độ đích."""
        curr = self.canvas.coords(item_id)
        if not curr: return
        # Tính toán bước di chuyển (15 bước)
        dx, dy = (tx - curr[0]) / 15, (ty - curr[1]) / 15
        def animate(c):
            if c < 15:
                self.canvas.move(item_id, dx, dy)
                self.root.after(20, lambda: animate(c+1))
            elif callback:
                callback()
        animate(0)

    def run_steps(self, steps):
        """Bộ điều phối animation xử lý từng bước 'act'."""
        if not steps: 
            self.desc_label.config(text="CHÚC MỪNG! ĐÃ SẮP XẾP XONG HOÀN TOÀN")
            messagebox.showinfo("Hoàn tất", "Quy trình sắp xếp ngoại đã kết thúc!")
            return
        
        s = steps.pop(0)
        self.desc_label.config(text=s['desc'])

        # HÀNH ĐỘNG 1: Khởi tạo dữ liệu gốc trên Disk
        if s['act'] == 'INIT_DISK':
            for i, v in enumerate(s['values']):
                rect = self.canvas.create_rectangle(70+i*55, 480, 120+i*55, 530, fill="#FFD700")
                txt = self.canvas.create_text(95+i*55, 505, text=str(int(v)))
                self.data_objects[i] = (rect, txt)
            self.root.after(1000, lambda: self.run_steps(steps))

        # HÀNH ĐỘNG 2: READ - Đọc run từ Disk lên RAM
        elif s['act'] == 'READ':
            self.current_ram_objs = []
            for i in range(len(s['values'])):
                r, t = self.data_objects[s['idx'] + i]
                self.move_item(r, 220+i*95, 220)
                self.move_item(t, 245+i*95, 245)
                self.current_ram_objs.append((r, t))
            self.root.after(1500, lambda: self.run_steps(steps))

        # HÀNH ĐỘNG 3: SORT - Sắp xếp trong RAM
        elif s['act'] == 'SORT':
            for i, (r, t) in enumerate(self.current_ram_objs):
                self.canvas.itemconfig(t, text=str(int(s['values'][i])))
                self.canvas.itemconfig(r, fill="#00BFFF")
            self.root.after(1000, lambda: self.run_steps(steps))

        # HÀNH ĐỘNG 4: WRITE_RUN - Ghi kết quả Pass 0 lên Disk tạm
        elif s['act'] == 'WRITE_RUN':
            run_list = []
            for i, (r, t) in enumerate(self.current_ram_objs):
                tx = 60 + s['run_idx']*230 + i*50
                self.move_item(r, tx, 50)
                self.move_item(t, tx+25, 75)
                run_list.append((r, t))
            self.run_objects[s['run_idx']] = run_list
            self.root.after(1500, lambda: self.run_steps(steps))

        # HÀNH ĐỘNG 5: LOAD_FOR_MERGE - Lấy các Run về RAM để trộn
        elif s['act'] == 'LOAD_FOR_MERGE':
            # Lấy các khối từ Run 1 và Run 2 bay xuống RAM
            objs_to_move = self.run_objects[s['r1_idx']] + self.run_objects[s['r2_idx']]
            for i, (r, t) in enumerate(objs_to_move):
                self.move_item(r, 210+i*45, 220)
                self.move_item(t, 235+i*45, 245)
                self.canvas.itemconfig(r, fill="#FF6347") # Đổi màu cam khi đang trộn
            self.current_ram_objs = objs_to_move
            self.root.after(2000, lambda: self.run_steps(steps))

        # HÀNH ĐỘNG 6: SAVE_MERGED - Ghi kết quả trộn cuối cùng
        elif s['act'] == 'SAVE_MERGED':
            for i, (r, t) in enumerate(self.current_ram_objs):
                self.canvas.itemconfig(t, text=str(int(s['values'][i])))
                tx = 150 + i*50
                self.move_item(r, tx, 50)
                self.move_item(t, tx+25, 75)
                self.canvas.itemconfig(r, fill="#32CD32") # Màu xanh lá cho kết quả cuối
            self.root.after(2000, lambda: self.run_steps(steps))

    def start(self):
        self.canvas.delete("all")
        self.setup_layout()
        utils.create_sample_binary() 
        try:
            steps = self.sorter.get_full_animation_steps("input_test.bin")
            self.run_steps(steps)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy dữ liệu hoạt ảnh: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SmoothAnimationApp(root)
    root.mainloop()
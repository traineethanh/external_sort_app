import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time
import utils
from algorithms import ExternalSort

class VisualExternalSort(ExternalSort):
    """Kế thừa ExternalSort để thêm tính năng cập nhật giao diện trực quan."""
    def __init__(self, canvas, canvas_labels, buffer_size=3):
        super().__init__(buffer_size)
        self.canvas = canvas
        self.labels = canvas_labels

    def update_ui(self, stage_text, buffer_data=None, disk_runs=None):
        """Cập nhật hình ảnh mô phỏng trên Canvas."""
        self.labels['status'].config(text=f"Trạng thái: {stage_text}")
        
        # Vẽ Buffer (Main Memory) - slide 7, 8
        self.canvas.delete("buffer_items")
        if buffer_data:
            for i, val in enumerate(buffer_data):
                x = 50 + (i * 100)
                self.canvas.create_rectangle(x, 50, x+80, 100, fill="#ADD8E6", tags="buffer_items")
                self.canvas.create_text(x+40, 75, text=str(val), tags="buffer_items")

        # Vẽ các Runs trên Disk - slide 36, 37
        self.canvas.delete("disk_items")
        if disk_runs:
            for i, run in enumerate(disk_runs):
                y = 150 + (i * 30)
                self.canvas.create_text(50, y, text=f"Run {i}: {run}", anchor="w", tags="disk_items")
        
        self.canvas.update()
        time.sleep(1) # Tạm dừng để người dùng kịp quan sát giống như từng bước trong slide

def run_app():
    root = tk.Tk()
    root.title("UIT - Trực quan hóa External Merge Sort")
    root.geometry("600x600")

    # --- Khu vực hiển thị mô phỏng (Canvas) ---
    ttk.Label(root, text="MÔ PHỎNG QUY TRÌNH (GIỐNG SLIDE)", font=('Helvetica', 10, 'bold')).pack(pady=5)
    
    canvas = tk.Canvas(root, width=550, height=300, bg="white", highlightthickness=1)
    canvas.pack(pady=10)
    
    # Vẽ khung cố định cho Main Memory và Disk [cite: 43, 44]
    canvas.create_text(20, 20, text="MAIN MEMORY (BUFFER)", anchor="w", font=('Helvetica', 9, 'bold'))
    canvas.create_rectangle(10, 40, 350, 110, outline="blue") # Buffer area
    
    canvas.create_text(20, 130, text="DISK (STORAGE)", anchor="w", font=('Helvetica', 9, 'bold'))
    canvas.create_rectangle(10, 145, 540, 290, outline="brown") # Disk area

    status_label = ttk.Label(root, text="Trạng thái: Sẵn sàng", foreground="blue")
    status_label.pack()

    ui_elements = {'status': status_label}
    selected_file = tk.StringVar(value="Chưa chọn file")

    # --- Các hàm điều khiển ---
    def execute_sort():
        input_path = selected_file.get()
        if not os.path.exists(input_path):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file!")
            return

        # Khởi tạo lớp trực quan hóa
        visual_sorter = VisualExternalSort(canvas, ui_elements)
        output_path = "sorted_output.bin"
        
        try:
            # Lưu ý: Bạn cần sửa algorithms.py để gọi self.update_ui() tại các bước then chốt
            visual_sorter.sort(input_path, output_path)
            messagebox.showinfo("Xong", "Đã sắp xếp và trực quan hóa hoàn tất!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # (Các phần nút bấm Tạo dữ liệu mẫu và Chọn file giữ nguyên như cũ)
    ttk.Button(root, text="1. Tạo dữ liệu mẫu", command=lambda: utils.create_sample_binary()).pack(pady=5)
    ttk.Button(root, text="2. Chọn tập tin nguồn", command=lambda: selected_file.set(filedialog.askopenfilename())).pack(pady=5)
    tk.Button(root, text="BẮT ĐẦU MÔ PHỎNG", command=execute_sort, bg="#0078D7", fg="white", font=('bold')).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    run_app()
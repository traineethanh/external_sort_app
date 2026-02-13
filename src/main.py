import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from algorithms import ExternalSort
import utils
import os

def run_app():
    root = tk.Tk()
    root.title("UIT - External Sort Demo - Quang Thanh")
    root.geometry("500x350")
    root.configure(padx=20, pady=20)

    # Biến lưu đường dẫn file đã chọn
    selected_file = tk.StringVar(value="Chưa chọn file")

    def select_file():
        file_path = filedialog.askopenfilename(
            title="Chọn tập tin dữ liệu nguồn (.bin)",
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if file_path:
            selected_file.set(file_path)

    def execute_sort():
        input_path = selected_file.get()
        if not os.path.exists(input_path):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tập tin nguồn trước!")
            return
        
        output_path = "sorted_output.bin"
        # Khởi tạo thuật toán với 3 buffer pages theo slide [cite: 18, 230]
        sorter = ExternalSort(buffer_size=3)
        
        try:
            # Giai đoạn 1: Chia runs và Giai đoạn 2: Merge [cite: 254, 255]
            sorter.sort(input_path, output_path)
            
            # Đọc kết quả cuối cùng để hiển thị minh họa
            final_result = utils.read_binary_file(output_path)
            messagebox.showinfo("Thành công", f"Đã sắp xếp xong!\nKết quả: {final_result}")
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Đã xảy ra lỗi: {str(e)}")

    def generate_test_data():
        # Tạo 12 số thực để minh họa quá trình chia runs < 10 phần tử [cite: 360]
        test_data = [44.0, 10.0, 33.0, 12.0, 55.0, 31.0, 18.0, 22.0, 27.0, 24.0, 3.0, 1.0]
        utils.create_sample_binary("input_test.bin", test_data)
        selected_file.set(os.path.abspath("input_test.bin"))
        messagebox.showinfo("Thông báo", "Đã tạo file mẫu 'input_test.bin' thành công!")

    # --- Giao diện người dùng ---
    ttk.Label(root, text="MÔ PHỎNG SẮP XẾP NGOẠI (EXTERNAL MERGE SORT)", font=('Helvetica', 10, 'bold')).pack(pady=10)
    
    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=10, fill='x')

    ttk.Button(btn_frame, text="1. Tạo dữ liệu mẫu", command=generate_test_data).pack(side='left', padx=5, expand=True)
    ttk.Button(btn_frame, text="2. Chọn tập tin nguồn", command=select_file).pack(side='left', padx=5, expand=True)

    ttk.Label(root, text="Tập tin hiện tại:").pack(anchor='w', pady=(10, 0))
    ttk.Entry(root, textvariable=selected_file, state='readonly').pack(fill='x', pady=5)

    # NÚT SẮP XẾP CHÍNH
    btn_sort = tk.Button(
        root, 
        text="BẮT ĐẦU SẮP XẾP NGOẠI", 
        command=execute_sort,
        bg="#0078D7", 
        fg="white", 
        font=('Helvetica', 11, 'bold'),
        height=2
    )
    btn_sort.pack(fill='x', pady=20)

    ttk.Label(root, text="* Lưu ý: Kết quả sẽ lưu tại 'sorted_output.bin'", foreground="gray").pack()

    root.mainloop()

if __name__ == "__main__":
    run_app()
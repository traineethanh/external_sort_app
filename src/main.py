import tkinter as tk
from tkinter import filedialog, messagebox
from algorithms import ExternalSort
import utils
import os

def run_app():
    root = tk.Tk()
    root.title("UIT - External Sort Demo")
    root.geometry("400x200")

    def select_and_sort():
        file_path = filedialog.askopenfilename(title="Chọn file nhị phân nguồn")
        if not file_path:
            return
        
        output_path = "sorted_output.bin"
        sorter = ExternalSort(buffer_size=3)
        
        try:
            sorter.sort(file_path, output_path)
            result = utils.read_binary_file(output_path)
            messagebox.showinfo("Thành công", f"Đã sắp xếp! Kết quả: {result}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def create_test_file():
        test_data = [44.0, 10.0, 33.0, 12.0, 55.0, 31.0, 18.0, 22.0, 27.0, 24.0, 3.0, 1.0]
        utils.create_sample_binary("input_test.bin", test_data)
        messagebox.showinfo("Thông báo", "Đã tạo file input_test.bin (12 phần tử)")

    tk.Button(root, text="Tạo file mẫu (12 số thực)", command=create_test_file).pack(pady=10)
    tk.Button(root, text="Chọn file & Sắp xếp ngoại", command=select_and_sort, bg="blue", fg="white").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_app()
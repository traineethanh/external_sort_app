import customtkinter as ctk
from tkinter import filedialog, messagebox
import utils
import time

class SortApp(ctk.CTk):
    """Ứng dụng giao diện sắp xếp tập tin nhị phân và minh họa thuật toán.

    Attributes:
        file_path (str): Đường dẫn tập tin hiện đang xử lý.
        data (list): Dữ liệu số thực được load từ tập tin.
    """
    
    def __init__(self):
        """Khởi tạo giao diện người dùng và các cấu phần của ứng dụng."""
        super().__init__()
        self.title("Binary Sort Pro - Quang Thanh")
        self.geometry("600x550")
        
        self.file_path = ""
        self.data = []

        # Khởi tạo các thành phần giao diện (UI)
        self._setup_ui()

    def _setup_ui(self):
        """Thiết lập các widget trên màn hình ứng dụng."""
        self.label = ctk.CTkLabel(self, text="MINH HỌA SẮP XẾP FILE NHỊ PHÂN", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        self.btn_open = ctk.CTkButton(self, text="Chọn File Nhị Phân", command=self.open_file)
        self.btn_open.pack(pady=10)

        self.btn_gen = ctk.CTkButton(self, text="Tạo File Test Mẫu", fg_color="#2c3e50", command=self.generate_test)
        self.btn_gen.pack(pady=5)

        self.textbox = ctk.CTkTextbox(self, width=500, height=250)
        self.textbox.pack(pady=10)

        self.btn_sort = ctk.CTkButton(self, text="Bắt đầu Sắp xếp & Minh họa", state="disabled", 
                                       fg_color="#27ae60", command=self.start_sort)
        self.btn_sort.pack(pady=20)

    def open_file(self):
        """Mở hộp thoại để người dùng lựa chọn tập tin nguồn .bin."""
        path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])
        if path:
            self.file_path = path
            self.data = utils.read_binary_file(path)
            self.log(f"Đã mở file thành công.\nDữ liệu gốc: {self.data}")
            self.btn_sort.configure(state="normal")

    def log(self, message):
        """Ghi nhật ký hoạt động vào ô text trên giao diện.

        Args:
            message (str): Nội dung thông báo cần hiển thị.
        """
        self.textbox.insert("end", f"{message}\n" + "-"*40 + "\n")
        self.textbox.see("end")

    def start_sort(self):
        """Thực hiện thuật toán Bubble Sort và cập nhật giao diện để minh họa từng bước."""
        n = len(self.data)
        if n == 0:
            messagebox.showwarning("Cảnh báo", "Dữ liệu trống!")
            return

        self.log("BẮT ĐẦU MINH HỌA QUÁ TRÌNH SẮP XẾP TĂNG DẦN...")
        
        # Minh họa thuật toán Bubble Sort
        for i in range(n):
            for j in range(0, n-i-1):
                if self.data[j] > self.data[j+1]:
                    # Thực hiện hoán đổi (Swap)
                    self.data[j], self.data[j+1] = self.data[j+1], self.data[j]
                    
                    # Hiển thị trạng thái dữ liệu sau khi hoán đổi
                    self.log(f"Hoán đổi: {self.data}")
                    
                    # Cập nhật giao diện để người dùng thấy thay đổi ngay lập tức
                    self.update() 
                    time.sleep(0.4) # Tạm dừng 0.4s để minh họa rõ ràng hơn

        # Ghi lại kết quả sau khi sắp xếp xong vào file nhị phân
        utils.write_binary_file(self.file_path, self.data)
        self.log("HOÀN THÀNH: Đã lưu kết quả vào tập tin nhị phân.")
        messagebox.showinfo("Thành công", "Quá trình sắp xếp hoàn tất!")

    def generate_test(self):
        """Tạo file dữ liệu mẫu nhanh để kiểm tra tính năng sắp xếp."""
        path = "data/test_sample.bin"
        self.data = utils.generate_sample_binary(path)
        self.file_path = path
        self.log(f"Đã tạo dữ liệu mẫu tại: {path}\nDữ liệu: {self.data}")
        self.btn_sort.configure(state="normal")

if __name__ == "__main__":
    # Khởi chạy ứng dụng
    app = SortApp()
    app.mainloop()
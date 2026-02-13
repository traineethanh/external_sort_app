import customtkinter as ctk
from tkinter import filedialog, messagebox
import utils
import algorithms
import time

class SortApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Binary Sort Pro - Quang Thanh (UIT)")
        self.geometry("700x600")
        self.data = []
        self.file_path = ""
        self._setup_ui()

    def _setup_ui(self):
        self.label = ctk.CTkLabel(self, text="MINH HỌA MERGE SORT (MAX 10 PHẦN TỬ)", font=("Arial", 18, "bold"))
        self.label.pack(pady=15)

        # Khung chứa các nút điều khiển
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=10, padx=20, fill="x")

        self.btn_open = ctk.CTkButton(self.frame, text="Mở File .bin", command=self.open_file)
        self.btn_open.grid(row=0, column=0, padx=10, pady=10)

        self.btn_gen = ctk.CTkButton(self.frame, text="Tạo 10 Số Mẫu", fg_color="#34495e", command=self.generate_test)
        self.btn_gen.grid(row=0, column=1, padx=10, pady=10)

        self.textbox = ctk.CTkTextbox(self, width=650, height=350, font=("Courier New", 13))
        self.textbox.pack(pady=10)

        self.btn_sort = ctk.CTkButton(self, text="Bắt đầu Minh họa", state="disabled", 
                                       fg_color="#27ae60", command=self.start_sort)
        self.btn_sort.pack(pady=10)

    def log(self, message):
        self.textbox.insert("end", message + "\n")
        self.textbox.see("end")
        self.update()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if path:
            self.file_path = path
            raw_data = utils.read_binary_file(path)
            if len(raw_data) > 10:
                messagebox.showwarning("Lưu ý", "File có hơn 10 phần tử, app chỉ lấy 10 số đầu để minh họa.")
                self.data = raw_data[:10]
            else:
                self.data = raw_data
            
            self.textbox.delete("1.0", "end")
            self.log(f"FILE ĐƯỢC CHỌN: {path}")
            self.log(f"DỮ LIỆU GỐC (10 số): {self.data}")
            self.btn_sort.configure(state="normal")

    def generate_test(self):
        path = "data/test_10_elements.bin"
        self.data = utils.generate_sample_binary(path)
        self.file_path = path
        self.textbox.delete("1.0", "end")
        self.log(f"ĐÃ TẠO FILE MẪU: {path}")
        self.log(f"DỮ LIỆU: {self.data}")
        self.btn_sort.configure(state="normal")

    def start_sort(self):
        self.log("\n>>> BẮT ĐẦU QUÁ TRÌNH CHIA ĐỂ TRỊ")
        
        def callback(current_state, msg):
            self.log(f"{msg}: {current_state}")
            time.sleep(0.6) # Tốc độ vừa phải để thầy cô kịp đọc

        sorted_result = algorithms.merge_sort(self.data, callback)
        self.data = sorted_result
        
        utils.write_binary_file(self.file_path, self.data)
        self.log("\n>>> HOÀN THÀNH! Dữ liệu đã được sắp xếp tăng dần.")
        messagebox.showinfo("Thành công", "Đã lưu kết quả vào file nhị phân!")

if __name__ == "__main__":
    app = SortApp()
    app.mainloop()
import struct
import os

def read_binary_file(file_path):
    """
    Đọc tập tin nhị phân và chuyển đổi sang danh sách số thực (8 bytes).
    Sử dụng định dạng 'd' (double) để đảm bảo kích thước 8 bytes mỗi phần tử.
    """
    data = []
    if not os.path.exists(file_path):
        return data
    with open(file_path, 'rb') as f:
        while chunk := f.read(8):
            data.append(struct.unpack('d', chunk)[0])
    return data

def write_binary_file(file_path, data):
    """
    Ghi danh sách số thực vào tập tin dưới dạng nhị phân 8-byte.
    Đây là bước quan trọng để minh họa việc quản lý dữ liệu trên đĩa (Disk).
    """
    with open(file_path, 'wb') as f:
        for value in data:
            f.write(struct.pack('d', value))

def create_sample_binary(file_path="input_test.bin", numbers=None):
    """
    Tạo một file nhị phân sẵn có để người dùng không phải tự tạo file.
    Mặc định tạo ra 12 số thực chưa sắp xếp để minh họa việc chia runs.
    """
    if numbers is None:
        # Dữ liệu mẫu tương tự ví dụ trong slide (trang 26-33)
        numbers = [44.0, 10.0, 33.0, 12.0, 55.0, 31.0, 18.0, 22.0, 27.0, 24.0, 3.0, 1.0]
    
    write_binary_file(file_path, numbers)
    print(f"--- Đã tạo file sẵn: {file_path} ---")
    print(f"Nội dung (số thực): {numbers}")

if __name__ == "__main__":
    # Khi chạy trực tiếp file này, nó sẽ tạo ra file input_test.bin
    create_sample_binary()
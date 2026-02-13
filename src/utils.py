import struct
import os
import sys

# Đảm bảo Console hiển thị được tiếng Việt nếu chạy trực tiếp
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def read_binary_file(file_path):
    """
    Đọc tập tin nhị phân và chuyển đổi sang danh sách số thực (8 bytes). [cite: 229, 230]
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
    Ghi danh sách số thực vào tập tin dưới dạng nhị phân 8-byte. [cite: 230]
    Minh họa quản lý dữ liệu trên đĩa (Disk) với chi phí IO là 2*(M+N). 
    """
    with open(file_path, 'wb') as f:
        for value in data:
            f.write(struct.pack('d', value))

def create_sample_binary(file_path="input_test.bin", numbers=None):
    """
    Tạo file nhị phân mẫu để minh họa việc chia runs và trộn. [cite: 254, 255]
    """
    if numbers is None:
        # Dữ liệu 12 phần tử để minh họa thuật toán với các file kích thước nhỏ. [cite: 360]
        numbers = [44.0, 10.0, 33.0, 12.0, 55.0, 31.0, 18.0, 22.0, 27.0, 24.0, 3.0, 1.0]
    
    write_binary_file(file_path, numbers)
    # Loại bỏ icon để tránh lỗi 'charmap' trên một số máy Windows
    print(f"--- DA TAO FILE: {file_path} ---") 
    print(f"Noi dung (so thuc): {numbers}")
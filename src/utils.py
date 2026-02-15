import struct
import os
import random # Cần thiết để tạo số ngẫu nhiên

def read_binary_file(file_path):
    """Đọc tệp nhị phân chứa các số thực 8-byte."""
    data = []
    if not os.path.exists(file_path): return data
    with open(file_path, 'rb') as f:
        while chunk := f.read(8):
            # 'd' đại diện cho double (8-byte real number)
            data.append(struct.unpack('d', chunk)[0])
    return data

def write_binary_file(file_path, data):
    """Ghi danh sách số thực vào tệp nhị phân dưới dạng 8-byte."""
    with open(file_path, 'wb') as f:
        for value in data:
            f.write(struct.pack('d', value))

def create_random_input(file_path="input_test.bin", n=12):
    """Tạo n số thực ngẫu nhiên từ 1 đến 100 và ghi vào file."""
    # Làm tròn 2 chữ số thập phân để block hiển thị đẹp hơn trên giao diện
    numbers = [round(random.uniform(1, 100), 2) for _ in range(n)]
    write_binary_file(file_path, numbers)
    return file_path
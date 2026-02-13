import struct
import random

def read_binary_file(file_path):
    """Đọc tối đa 10 số thực 8-byte từ file nhị phân."""
    data = []
    try:
        with open(file_path, 'rb') as f:
            # Chỉ đọc tối đa 10 phần tử để đảm bảo minh họa tốt nhất
            count = 0
            while (chunk := f.read(8)) and count < 10:
                data.append(struct.unpack('d', chunk)[0])
                count += 1
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
    return data

def write_binary_file(file_path, data):
    """Ghi danh sách số thực vào file nhị phân 8-byte."""
    with open(file_path, 'wb') as f:
        for value in data:
            f.write(struct.pack('d', value))

def generate_sample_binary(file_path):
    """Tạo file mẫu với đúng 10 số thực ngẫu nhiên."""
    # Tạo 10 số thực ngẫu nhiên, làm tròn 2 chữ số thập phân cho dễ nhìn
    random_data = [round(random.uniform(1.0, 99.0), 2) for _ in range(10)]
    write_binary_file(file_path, random_data)
    return random_data
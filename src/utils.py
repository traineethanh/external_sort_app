import struct
import os
import random

def read_binary_file(file_path):
    """Đọc tệp nhị phân chứa các số thực 8-byte (double)."""
    data = []
    if not os.path.exists(file_path): return data
    with open(file_path, 'rb') as f:
        while chunk := f.read(8):
            data.append(struct.unpack('d', chunk)[0])
    return data

def write_binary_file(file_path, data):
    """Ghi dữ liệu xuống tệp nhị phân."""
    with open(file_path, 'wb') as f:
        for value in data:
            f.write(struct.pack('d', value))

def create_sample_binary(file_path="input.bin"):
    """Tạo tệp mẫu 12 số thực để minh họa (tương đương m=12 trong slide). [cite: 637]"""
    numbers = [44.0, 10.0, 33.0, 12.0, 55.0, 31.0, 18.0, 22.0, 27.0, 24.0, 3.0, 1.0]
    write_binary_file(file_path, numbers)

def create_random_input(file_path="input_test.bin", n=12):
    """Tao 12 so thuc ngau nhien (tuong ung m=12 trong slide)[cite: 637]."""
    numbers = [round(random.uniform(1, 100), 1) for _ in range(n)]
    write_binary_file(file_path, numbers)
    return file_path
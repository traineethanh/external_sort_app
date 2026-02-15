import struct
import os
import random

def read_binary_file(file_path):
    data = []
    if not os.path.exists(file_path): return data
    with open(file_path, 'rb') as f:
        while chunk := f.read(8): # 8 bytes cho mỗi số thực double
            data.append(struct.unpack('d', chunk)[0])
    return data

def write_binary_file(file_path, data):
    with open(file_path, 'wb') as f:
        for value in data:
            f.write(struct.pack('d', value))

def create_random_input(file_path="input_test.bin", n=12):
    # Tạo 12 số thực ngẫu nhiên tương ứng m=12 trong slide
    numbers = [round(random.uniform(1, 100), 1) for _ in range(n)]
    write_binary_file(file_path, numbers)
    return file_path
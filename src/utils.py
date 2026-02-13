import struct
import os

def read_binary_file(file_path):
    data = []
    if not os.path.exists(file_path): return data
    with open(file_path, 'rb') as f:
        while chunk := f.read(8):
            data.append(struct.unpack('d', chunk)[0])
    return data

def write_binary_file(file_path, data):
    with open(file_path, 'wb') as f:
        for value in data:
            f.write(struct.pack('d', value))

def create_sample_binary(file_path="input_test.bin"):
    # 12 số thực mẫu giúp minh họa rõ logic run lẻ (3 runs) [cite: 360]
    numbers = [44.0, 10.0, 33.0, 12.0, 55.0, 31.0, 18.0, 22.0, 27.0, 24.0, 3.0, 1.0]
    write_binary_file(file_path, numbers)
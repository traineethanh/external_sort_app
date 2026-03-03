import struct
import os
import random

def read_binary_file(file_path):
    data = []
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0: 
        return data
    
    size = os.path.getsize(file_path)
    
    with open(file_path, 'rb') as f:
        content = f.read()
        
        # 1. Thử nhận diện dựa trên tên file và số lượng phần tử
        # Nếu tên file có định dạng input_N.bin
        try:
            filename = os.path.basename(file_path)
            if "input_" in filename:
                count_in_name = int(filename.split('_')[1].split('.')[0])
                
                # Trường hợp đặc biệt: Số lượng ít (<=12) dùng số nguyên 4 byte
                if count_in_name <= 12 and size == count_in_name * 4:
                    return list(struct.unpack(f'{count_in_name}i', content))
                
                # Trường hợp còn lại: Dùng double 8 byte cho số thực
                if size == count_in_name * 8:
                    return list(struct.unpack(f'{count_in_name}d', content))
        except:
            pass

        # 2. Cơ chế tự động fallback dựa trên chia hết
        # Nếu file chia hết cho 8, ưu tiên đọc Double
        if size % 8 == 0:
            count = size // 8
            return list(struct.unpack(f'{count}d', content))
        # Nếu chỉ chia hết cho 4, đọc Integer
        elif size % 4 == 0:
            count = size // 4
            return list(struct.unpack(f'{count}i', content))
            
    return data

def write_binary_file(file_path, data):
    """Ghi file: <=12 số ghi kiểu 'i' (4 byte), >12 số ghi kiểu 'd' (8 byte)"""
    if not data: return
    with open(file_path, 'wb') as f:
        # Tự động chọn format dựa trên số lượng phần tử
        if len(data) <= 12:
            fmt = f'{len(data)}i' # Integer 4 byte
        else:
            fmt = f'{len(data)}d' # Double 8 byte (Yêu cầu của bạn)
        f.write(struct.pack(fmt, *data))

def create_random_input(file_path="input_test.bin", n=12):
    if n <= 12:
        numbers = [random.randint(10, 99) for _ in range(n)]
    else:
        numbers = [round(random.uniform(10.0, 999.0), 2) for _ in range(n)]
    
    return write_binary_file(file_path, numbers)
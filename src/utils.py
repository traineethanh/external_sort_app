import struct
import os
import random

def read_binary_file(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0: 
        return []
    
    size = os.path.getsize(file_path)
    
    with open(file_path, 'rb') as f:
        content = f.read()
        
        # ƯU TIÊN 1: Kiểm tra theo quy ước số lượng (Dưới 12 là int, trên 12 là double)
        # Cách này chính xác nhất với yêu cầu của bạn
        count_if_int = size // 4
        count_if_double = size // 8

        if count_if_int <= 12 and size == count_if_int * 4:
            # Nếu kích thước khớp với 12 số nguyên trở xuống
            return list(struct.unpack(f'{count_if_int}i', content))
        
        elif size == count_if_double * 8:
            # Nếu kích thước khớp với định dạng double 8-byte
            return list(struct.unpack(f'{count_if_double}d', content))
            
        # Fallback cuối cùng nếu không khớp quy ước nào
        try:
            return list(struct.unpack(f'{size // 8}d', content))
        except:
            return list(struct.unpack(f'{size // 4}i', content))

def write_binary_file(file_path, data):
    if not data: return
    with open(file_path, 'wb') as f:
        # Nếu là số nguyên và số lượng <= 12 -> ghi 4-byte (i)
        if len(data) <= 12:
            # Đảm bảo dữ liệu là int để tránh lỗi pack 'i'
            int_data = [int(x) for x in data]
            fmt = f'{len(int_data)}i'
            f.write(struct.pack(fmt, *int_data))
        else:
            # Ngược lại ghi 8-byte (d)
            fmt = f'{len(data)}d'
            f.write(struct.pack(fmt, *data))

def create_random_input(file_path="input_test.bin", n=12):
    if n <= 12:
        numbers = [random.randint(10, 99) for _ in range(n)]
    else:
        # Làm tròn 1 chữ số thập phân cho gọn
        numbers = [round(random.uniform(10.0, 999.0), 1) for _ in range(n)]
    
    write_binary_file(file_path, numbers)
    return file_path
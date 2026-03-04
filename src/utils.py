import struct
import os
import random

def read_binary_file(file_path):
    """
    Đọc dữ liệu từ file nhị phân dựa trên kích thước file.
    
    Quy ước:
    - Nếu file chứa <= 12 số (kích thước tương ứng 4-byte/số): Đọc kiểu integer ('i').
    - Nếu file chứa > 12 số (kích thước tương ứng 8-byte/số): Đọc kiểu double ('d').
    
    Args:
        file_path (str): Đường dẫn đến file nhị phân cần đọc.
        
    Returns:
        list: Danh sách các giá trị số đọc được. Trả về list trống nếu file không tồn tại.
    """
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
    """
    Ghi danh sách dữ liệu vào file nhị phân theo định dạng tùy biến.
    
    Quy tắc đóng gói:
    - Dữ liệu <= 12 phần tử: Lưu kiểu 4-byte integer ('i') nhằm tối ưu không gian thể hiện trên block.
    - Dữ liệu > 12 phần tử: Lưu kiểu 8-byte double ('d') theo yêu cầu.
    
    Args:
        file_path (str): Đường dẫn file đích.
        data (list): Danh sách các số cần ghi.
    """
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
    """
    Khởi tạo file dữ liệu ngẫu nhiên để phục vụ kiểm thử.
    
    - Nếu n <= 12: Tạo số nguyên (10-99).
    - Nếu n > 12: Tạo số thực (10.0-999.0) làm tròn 1 chữ số thập phân.
    
    Args:
        file_path (str): Tên file cần tạo.
        n (int): Số lượng phần tử.
        
    Returns:
        str: Đường dẫn file đã tạo.
    """
    if n <= 12:
        numbers = [random.randint(10, 99) for _ in range(n)]
    else:
        # Làm tròn 1 chữ số thập phân cho gọn
        numbers = [round(random.uniform(10.0, 999.0), 1) for _ in range(n)]
    
    write_binary_file(file_path, numbers)
    return file_path
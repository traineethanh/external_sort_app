import struct
import random

def read_binary_file(file_path):
    """Đọc dữ liệu từ tập tin nhị phân chứa các số thực 8-byte.

    Args:
        file_path (str): Đường dẫn đến tập tin .bin cần đọc.

    Returns:
        list[float]: Danh sách các số thực đã được giải mã từ định dạng nhị phân.
    """
    data = []
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8):
                # 'd' đại diện cho kiểu double (8-byte float) trong struct
                data.append(struct.unpack('d', chunk)[0])
    except Exception as e:
        print(f"Lỗi khi đọc file nhị phân: {e}")
    return data

def write_binary_file(file_path, data):
    """Ghi danh sách số thực vào tập tin dưới định dạng nhị phân 8-byte.

    Args:
        file_path (str): Đường dẫn đến tập tin đầu ra.
        data (list[float]): Danh sách các số thực cần lưu trữ.
    """
    with open(file_path, 'wb') as f:
        for value in data:
            f.write(struct.pack('d', value))

def generate_sample_binary(file_path, count=10):
    """Tạo tập tin nhị phân mẫu với các số thực ngẫu nhiên để phục vụ kiểm thử.

    Args:
        file_path (str): Nơi lưu trữ tập tin mẫu.
        count (int): Số lượng phần tử cần tạo. Mặc định là 10.

    Returns:
        list[float]: Danh sách dữ liệu gốc vừa được tạo.
    """
    random_data = [round(random.uniform(1.0, 100.0), 2) for _ in range(count)]
    write_binary_file(file_path, random_data)
    return random_data
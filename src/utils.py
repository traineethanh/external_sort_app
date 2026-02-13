import struct

def read_binary_file(file_path):
    """
    Đọc toàn bộ tập tin nhị phân chứa các số thực 8-byte.
    """
    data = []
    with open(file_path, 'rb') as f:
        while chunk := f.read(8):
            data.append(struct.unpack('d', chunk)[0])
    return data

def write_binary_file(file_path, data):
    """
    Ghi danh sách số thực vào tập tin nhị phân dưới dạng 8-byte (double).
    """
    with open(file_path, 'wb') as f:
        for value in data:
            f.write(struct.pack('d', value))

def create_sample_binary(file_path, numbers):
    """
    Tạo tập tin nhị phân mẫu để kiểm thử.
    """
    write_binary_file(file_path, numbers)
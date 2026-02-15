import utils

class ExternalSortEngine:
    def __init__(self, buffer_pages=3):
        self.B = buffer_pages # [cite: 18]

    def get_simulation_steps(self, input_file):
        """Tính toán và trả về danh sách các bước cần mô phỏng."""
        data = utils.read_binary_file(input_file)
        steps = []
        
        # Pass 0: Tạo các Runs ban đầu [cite: 254]
        # Ví dụ đơn giản: chia đôi dữ liệu thành 2 Runs [cite: 361]
        mid = len(data) // 2
        run1 = sorted(data[:mid])
        run2 = sorted(data[mid:])
        
        # Ghi lại bước khởi tạo Disk
        steps.append({'act': 'INIT_DISK', 'data': data})
        
        # Ghi lại bước nạp vào RAM và Sort (Pass 0) [cite: 587]
        steps.append({'act': 'LOAD_RAM', 'data': data[:mid], 'target': 'RUN1'})
        steps.append({'act': 'SORT_RAM', 'data': run1})
        steps.append({'act': 'WRITE_DISK', 'data': run1, 'slot': 'F1'})
        
        # Tiếp tục các bước Merge... [cite: 590]
        return steps
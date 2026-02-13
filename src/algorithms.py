import utils
import os

class ExternalSort:
    def __init__(self, buffer_size=3):
        self.buffer_size = buffer_size

    def get_animation_steps(self, input_file):
        """Tạo danh sách các hành động chi tiết để tạo animation."""
        data = utils.read_binary_file(input_file)
        run_size = 4 
        steps = []
        all_runs = []
        
        # Pass 0: Tạo các runs ban đầu
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            # Bước 1: Đọc dữ liệu từ Disk lên RAM
            steps.append({'act': 'READ', 'values': chunk, 'desc': f"Doc {len(chunk)} phan tu len RAM"})
            
            # Bước 2: Sắp xếp tại chỗ trong RAM
            sorted_chunk = sorted(chunk)
            steps.append({'act': 'SORT', 'values': sorted_chunk, 'desc': "Sap xep du lieu trong RAM"})
            
            # Bước 3: Ghi dữ liệu đã sắp xếp xuống Disk tạo thành Run
            run_name = f"run_{len(all_runs)}.bin"
            utils.write_binary_file(run_name, sorted_chunk)
            all_runs.append(list(sorted_chunk))
            steps.append({'act': 'WRITE', 'values': sorted_chunk, 'run_idx': len(all_runs)-1, 'desc': f"Ghi Run {len(all_runs)-1} xuong Disk"})
            
        return steps
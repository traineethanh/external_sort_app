import utils
import os

class ExternalSort:
    def __init__(self, buffer_size=3):
        self.buffer_size = buffer_size

    def get_initial_runs_steps(self, input_file):
        """Tạo các bước chia runs (Pass 0)[cite: 254, 581]."""
        data = utils.read_binary_file(input_file)
        run_size = 4 # Kích thước nhỏ để dễ quan sát [cite: 360]
        steps = []
        runs = []
        
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            sorted_chunk = sorted(chunk)
            run_name = f"run_{len(runs)}.bin"
            utils.write_binary_file(run_name, sorted_chunk)
            runs.append(run_name)
            
            # Lưu lại trạng thái để animation: dữ liệu nạp vào buffer -> ghi xuống disk
            steps.append({
                'desc': f"Pass 0: Doc {chunk} vao Buffer va sap xep",
                'buffer': sorted_chunk,
                'runs': list(runs)
            })
        return steps, runs
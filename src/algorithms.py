import utils
import os

class ExternalSort:
    def get_animation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        run_size = 4 
        steps = []
        
        # Bước 1: Hiển thị dữ liệu gốc trên Disk
        steps.append({'act': 'INIT_DISK', 'values': data, 'desc': "Du lieu ban dau tren Disk"})

        # Pass 0: Chia thanh cac Run
        all_runs = []
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            
            # READ: Lay run tu Disk dua vao RAM
            steps.append({'act': 'READ', 'values': chunk, 'idx': i, 'desc': f"Doc cac phan tu tu {i} den {i+len(chunk)-1} vao RAM"})
            
            # SORT: Sap xep trong RAM
            sorted_chunk = sorted(chunk)
            steps.append({'act': 'SORT', 'values': sorted_chunk, 'desc': "Sap xep du lieu trong RAM (Internal Sort)"})
            
            # WRITE: Dua ra buffer khac nam tren Disk (Temp Runs)
            all_runs.append(sorted_chunk)
            steps.append({
                'act': 'WRITE_RUN', 
                'values': sorted_chunk, 
                'run_idx': len(all_runs) - 1, 
                'desc': f"Ghi du lieu da sap xep xuong vung tam (Run {len(all_runs)-1})"
            })
            
        return steps
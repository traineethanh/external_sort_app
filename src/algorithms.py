import utils
import math

class ExternalSortEngine:
    def __init__(self, buffer_pages=3):
        self.B_total = buffer_pages 
        self.page_size = 2 

    def get_simulation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        steps = []
        io_cost = 0
        N = len(data)
        
        steps.append({
            'act': 'INIT_DISK', 
            'values': data, 
            'io_cost': 0, 
            'desc': "Dữ liệu thô nằm trên vùng Input của Disk."
        })

        all_runs = []
        for i in range(0, N, 6):
            chunk = data[i : i + 6]
            # Lưu lại danh sách index của các phần tử được nạp vào RAM
            chunk_indices = list(range(i, min(i + 6, N)))
            
            pages_read = math.ceil(len(chunk) / self.page_size)
            io_cost += pages_read
            
            steps.append({
                'act': 'LOAD_RAM', 
                'values': chunk, 
                'indices': chunk_indices, # Gửi index để xóa chính xác trên UI
                'io_cost': io_cost, 
                'desc': f"Nạp các phần tử từ chỉ số {i} đến {i+len(chunk)-1} vào RAM."
            })
            
            sorted_chunk = sorted(chunk)
            steps.append({
                'act': 'SORT_RAM', 
                'values': sorted_chunk, 
                'io_cost': io_cost,
                'desc': "Sắp xếp nội bộ 6 phần tử trong RAM."
            })
            
            for j in range(0, len(sorted_chunk), 2):
                run = sorted_chunk[j : j + 2]
                all_runs.append(run)
                io_cost += 1
                target_f = "F1" if len(all_runs) <= 3 else "F2"
                run_idx_in_f = (len(all_runs) - 1) % 3
                
                steps.append({
                    'act': 'WRITE_F_BUFFER', 
                    'values': run, 
                    'target': target_f, 
                    'run_idx': run_idx_in_f,
                    'io_cost': io_cost,
                    'desc': f"Ghi Run vào Disk Buffer {target_f}."
                })

        steps.append({
            'act': 'FINISH', 
            'values': sorted(data), 
            'io_cost': io_cost,
            'desc': "Hoàn tất giai đoạn tạo Run."
        })
        return steps
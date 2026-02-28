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
        
        if N > 12: return [] # Không mô phỏng nếu n > 12

        # --- PASS 0: TẠO RUN (Như cũ) ---
        all_runs_f1 = []
        all_runs_f2 = []
        for i in range(0, N, 6):
            chunk = data[i : i + 6]
            chunk_indices = list(range(i, min(i + 6, N)))
            io_cost += math.ceil(len(chunk) / self.page_size)
            
            sorted_chunk = sorted(chunk)
            steps.append({'act': 'LOAD_RAM', 'values': chunk, 'indices': chunk_indices, 'io_cost': io_cost, 'desc': "Nạp dữ liệu vào RAM."})
            
            sorted_chunk = sorted(chunk)
            steps.append({'act': 'SORT_RAM', 'values': sorted_chunk, 'io_cost': io_cost, 'desc': "Sắp xếp nội bộ."})
            
            for j in range(0, len(sorted_chunk), 2):
                run = sorted_chunk[j : j + 2]
                io_cost += 1
                if len(all_runs_f1) < 3:
                    all_runs_f1.append(run)
                    steps.append({'act': 'WRITE_F_BUFFER', 'values': run, 'target': 'F1', 'run_idx': len(all_runs_f1)-1, 'io_cost': io_cost, 'desc': "Ghi Run vào F1."})
                else:
                    all_runs_f2.append(run)
                    steps.append({'act': 'WRITE_F_BUFFER', 'values': run, 'target': 'F2', 'run_idx': len(all_runs_f2)-1, 'io_cost': io_cost, 'desc': "Ghi Run vào F2."})

        # --- PASS 1: MERGE RUNS (TRỘN) ---
        # Giả sử trộn cặp Run đầu tiên của F1 và F2
        while all_runs_f1 and all_runs_f2:
            r1 = all_runs_f1.pop(0)
            r2 = all_runs_f2.pop(0)
            
            # 1. Nạp 2 run từ Disk vào 2 ô đầu của RAM
            steps.append({
                'act': 'MERGE_LOAD_RAM',
                'r1': r1, 'r2': r2,
                'io_cost': io_cost + 2,
                'desc': "Lấy 2 Run đầu từ F1 và F2 nạp vào 2 trang đầu của RAM."
            })
            io_cost += 2

            # 2. Trộn và đưa kết quả vào ô RAM thứ 3 (ô cuối)
            merged_run = sorted(r1 + r2)
            steps.append({
                'act': 'MERGE_SORT_RAM',
                'values': merged_run,
                'io_cost': io_cost,
                'desc': "So sánh các phần tử, trộn tăng dần vào trang RAM thứ 3."
            })

            # 3. Đẩy kết quả ra Output Disk
            steps.append({
                'act': 'WRITE_OUTPUT',
                'values': merged_run,
                'io_cost': io_cost + 2,
                'desc': "Đẩy Run đã trộn từ RAM xuống vùng Output Disk."
            })
            io_cost += 2

        steps.append({'act': 'FINISH', 'values': sorted(data), 'io_cost': io_cost, 'desc': "Sắp xếp hoàn tất!"})
        return steps
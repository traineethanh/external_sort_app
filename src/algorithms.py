import utils
import math

class ExternalSortEngine:
    def __init__(self, buffer_pages=3):
        self.B_total = buffer_pages 
        self.page_size = 2 # Mỗi trang chứa 2 số

    def get_simulation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        steps = []
        io_cost = 0
        N = len(data)
        
        if N > 12: return [] # Không mô phỏng nếu n > 12

        # --- PASS 0: TẠO RUNS (Sắp xếp nội bộ) ---
        all_runs_f1 = []
        all_runs_f2 = []
        for i in range(0, N, 6):
            chunk = data[i : i + 6]
            chunk_indices = list(range(i, min(i + 6, N)))
            
            # Bước 1: Nạp RAM (Vẫn hiện số chưa sort)
            steps.append({
                'act': 'LOAD_RAM', 
                'values': chunk, 
                'indices': chunk_indices, 
                'desc': "Nạp 6 số từ Disk vào 3 trang RAM."
            })
            
            # Bước 2: SẮP XẾP NỘI BỘ (Đây là lúc các Run được sort)
            sorted_chunk = sorted(chunk)
            steps.append({
                'act': 'SORT_RAM', 
                'values': sorted_chunk, 
                'desc': "Sắp xếp nội bộ trong RAM. Các số được xếp tăng dần."
            })
            io_cost += math.ceil(len(chunk) / self.page_size)
            
            # Bước 3: Đưa các Run đã sort vào Buffer F1/F2
            for j in range(0, len(sorted_chunk), 2):
                run = sorted_chunk[j : j + 2]
                io_cost += 1
                
                # Quyết định vào F1 (buffer trên) hay F2 (buffer dưới)
                if len(all_runs_f1) < 3:
                    target = 'F1'
                    r_idx = len(all_runs_f1)
                    all_runs_f1.append(run)
                else:
                    target = 'F2'
                    r_idx = len(all_runs_f2)
                    all_runs_f2.append(run)

                steps.append({
                    'act': 'WRITE_F_BUFFER', 
                    'values': run, 
                    'target': target, 
                    'run_idx': r_idx, 
                    'io_cost': io_cost, 
                    'desc': f"Đưa Run {run} vào {target} (Xóa hình ảnh ở RAM)."
                })

        # --- PASS 1: MERGE RUNS (Trộn từng phần tử) ---
        while all_runs_f1 and all_runs_f2:
            r1 = all_runs_f1.pop(0)
            r2 = all_runs_f2.pop(0)
            
            # Bước 1: Lấy 2 run đầu của 2 buffer disk vào 2 ô đầu RAM
            steps.append({
                'act': 'MERGE_LOAD_RAM',
                'r1': r1, 'r2': r2,
                'desc': "Lấy 2 Run đầu của F1 và F2 đưa vào 2 trang đầu RAM (Xóa ở Disk)."
            })
            io_cost += 2

            # Bước 2: Trộn (Merge) 
            # Mô phỏng: So sánh các phần tử đầu của 2 trang RAM, đưa vào trang RAM thứ 3
            merged_result = sorted(r1 + r2)
            steps.append({
                'act': 'MERGE_SORT_RAM',
                'values': merged_result,
                'desc': "So sánh phần tử đầu của 2 trang RAM, đưa giá trị nhỏ nhất vào trang RAM thứ 3."
            })

            # Bước 3: Đưa kết quả vào Output
            steps.append({
                'act': 'WRITE_OUTPUT',
                'values': merged_result,
                'io_cost': io_cost + 1,
                'desc': "Đưa Run kết quả từ RAM xuống vùng Output Disk (Xóa ở RAM)."
            })
            io_cost += 1

        steps.append({'act': 'FINISH', 'values': sorted(data), 'io_cost': io_cost, 'desc': "Sắp xếp hoàn tất!"})
        return steps
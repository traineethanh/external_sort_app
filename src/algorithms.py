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

        # --- PASS 1: MERGE RUNS (Logic Repacking/Trộn từng số) ---
        # Giả sử ta có all_runs_f1 và all_runs_f2 từ Pass 0
        
        output_buffer = []
        ram_pages = [[], [], []] # RAM Page 1, 2, 3
        
        # Nạp lần đầu
        if all_runs_f1 and all_runs_f2:
            ram_pages[0] = all_runs_f1.pop(0)
            ram_pages[1] = all_runs_f2.pop(0)
            steps.append({
                'act': 'MERGE_LOAD_RAM',
                'r1': ram_pages[0], 'r2': ram_pages[1],
                'desc': "Nạp 2 Run đầu từ F1, F2 vào RAM Page 1 & 2."
            })
            io_cost += 2

        # Vòng lặp trộn cho đến khi hết dữ liệu ở Disk và RAM
        while any(ram_pages[0:2]) or all_runs_f1 or all_runs_f2:
            # 1. Gom tất cả số hiện có trong RAM (Page 1 & 2) và sắp xếp
            current_in_ram = sorted(ram_pages[0] + ram_pages[1])
            
            # 2. Lấy 2 số nhỏ nhất cho vào Page 3 (Output Buffer)
            ram_pages[2] = current_in_ram[:2]
            # 3. Các số còn lại chia vào Page 1 và 2 (Repacking)
            remaining = current_in_ram[2:]
            ram_pages[0] = remaining[:2]
            ram_pages[1] = remaining[2:4]

            steps.append({
                'act': 'REPACK_RAM',
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                'desc': "Sắp xếp RAM: 2 số nhỏ nhất vào Page 3, các số còn lại dồn về Page 1 & 2."
            })

            # 4. Đẩy Page 3 xuống Disk Output
            steps.append({
                'act': 'WRITE_OUTPUT',
                'values': ram_pages[2],
                'desc': f"Đẩy Run nhỏ nhất {ram_pages[2]} xuống Output Disk."
            })
            io_cost += 1
            ram_pages[2] = [] # Reset page 3

            # 5. Nạp thêm dữ liệu vào ô RAM đang trống (nếu có)
            if not ram_pages[0] and all_runs_f1:
                ram_pages[0] = all_runs_f1.pop(0)
                steps.append({
                    'act': 'REF_LOAD', 'target_page': 0, 'values': ram_pages[0],
                    'desc': "RAM Page 1 trống, nạp Run tiếp theo từ F1."
                })
                io_cost += 1
            elif not ram_pages[1] and all_runs_f2:
                ram_pages[1] = all_runs_f2.pop(0)
                steps.append({
                    'act': 'REF_LOAD', 'target_page': 1, 'values': ram_pages[1],
                    'desc': "RAM Page 2 trống, nạp Run tiếp theo từ F2."
                })
                io_cost += 1
            
            # Điều kiện dừng an toàn cho mô phỏng 12 số
            if not any(ram_pages[0:2]) and not all_runs_f1 and not all_runs_f2:
                break

        steps.append({'act': 'FINISH', 'values': sorted(data), 'io_cost': io_cost, 'desc': "Sắp xếp hoàn tất!"})
        return steps
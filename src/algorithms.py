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

        # --- PASS 1: MERGE RUNS (Logic Băng chuyền) ---
        output_run_count = 0 
        ram_pages = [None, None, None] # [Page 1, Page 2, Page 3]

        if all_runs_f1: ram_pages[0] = all_runs_f1.pop(0)
        if all_runs_f2: ram_pages[1] = all_runs_f2.pop(0)
        
        steps.append({
            'act': 'MERGE_LOAD_RAM',
            'r1': ram_pages[0], 'r2': ram_pages[1],
            'desc': "Nạp 2 Run đầu tiên từ Disk vào RAM Page 1 và 2."
        })

        # Vòng lặp chạy cho đến khi RAM trống rỗng và Disk cũng hết
        while any(p is not None for p in ram_pages) or all_runs_f1 or all_runs_f2:
            # Bước A: Chọn Run nhỏ nhất để dồn xuống
            idx_min = -1
            # Chỉ so sánh những trang đang có dữ liệu (Page 1 và 2)
            valid_indices = [i for i in range(2) if ram_pages[i] is not None]
            
            if len(valid_indices) == 2:
                idx_min = 0 if ram_pages[0][0] < ram_pages[1][0] else 1
            elif len(valid_indices) == 1:
                idx_min = valid_indices[0]

            if idx_min != -1:
                # 1. Lấy Run nhỏ nhất ra
                chosen_run = ram_pages.pop(idx_min)
                # 2. Chèn None vào đầu để đẩy các Run còn lại xuống
                ram_pages.insert(0, None)
                # 3. Gán Run đã chọn vào Page 3 (Vị trí cuối cùng)
                ram_pages[2] = chosen_run

                steps.append({
                    'act': 'REPACK_SHIFT_DOWN',
                    'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                    'desc': f"Run {chosen_run} nhỏ hơn được đưa xuống Page 3. Các trang khác dồn xuống."
                })

                # Bước B: Xuất Page 3
                steps.append({
                    'act': 'WRITE_OUTPUT',
                    'values': ram_pages[2],
                    'output_idx': output_run_count,
                    'desc': f"Ghi Run {ram_pages[2]} xuống Output. RAM Page 3 trống."
                })
                output_run_count += 1
                io_cost += 1
                ram_pages[2] = None # Reset Page 3 sau khi ghi

            # Bước C: Nạp mới vào Page 1 (Nếu Page 1 đang trống và Disk còn hàng)
            if ram_pages[0] is None and (all_runs_f1 or all_runs_f2):
                new_run = all_runs_f1.pop(0) if all_runs_f1 else all_runs_f2.pop(0)
                ram_pages[0] = new_run
                steps.append({
                    'act': 'REF_LOAD_TOP',
                    'values': new_run,
                    'desc': f"Nạp Run {new_run} mới vào Page 1."
                })
                io_cost += 1
            
            # Kiểm tra thoát an toàn: Nếu RAM trống và Disk hết
            if not any(ram_pages) and not all_runs_f1 and not all_runs_f2:
                break

        steps.append({'act': 'FINISH', 'values': sorted(data), 'io_cost': io_cost, 'desc': "Sắp xếp hoàn tất!"})
        return steps
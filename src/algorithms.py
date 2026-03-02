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
        # Khởi tạo RAM 3 trang trống
        ram_pages = [None, None, None] # [Page 1, Page 2, Page 3]

        # Nạp 2 Run đầu tiên vào Page 1 và 2
        if all_runs_f1: ram_pages[0] = all_runs_f1.pop(0)
        if all_runs_f2: ram_pages[1] = all_runs_f2.pop(0)
        
        steps.append({
            'act': 'MERGE_LOAD_RAM',
            'r1': ram_pages[0], 'r2': ram_pages[1],
            'desc': "Nạp 2 Run đầu tiên từ Disk vào RAM Page 1 và 2."
        })

        while any(ram_pages) or all_runs_f1 or all_runs_f2:
            # Bước A: Tìm Run nhỏ nhất trong các Run đang có ở RAM để đưa xuống Page 3
            # Giả sử ta so sánh phần tử đầu của các Run để chọn
            idx_min = -1
            if ram_pages[0] and ram_pages[1]:
                # So sánh phần tử đầu tiên của 2 Run ở Page 1 và 2
                idx_min = 0 if ram_pages[0][0] < ram_pages[1][0] else 1
            elif ram_pages[0]: idx_min = 0
            elif ram_pages[1]: idx_min = 1

            if idx_min != -1:
                # Đưa Run nhỏ nhất xuống Page 3
                ram_pages[2] = ram_pages.pop(idx_min) 
                ram_pages.insert(0, None) # Đẩy Page 1 trống để tí nữa nạp mới
                
                # Hiện tại: Page 3 là Run nhỏ, Page 2 là Run lớn hơn, Page 1 đang None
                steps.append({
                    'act': 'REPACK_SHIFT_DOWN',
                    'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                    'desc': f"Run nhỏ hơn được đưa xuống Page 3. Run còn lại dồn xuống Page 2."
                })

                # Bước B: Xuất Page 3
                steps.append({
                    'act': 'WRITE_OUTPUT',
                    'values': ram_pages[2],
                    'output_idx': output_run_count,
                    'desc': f"Ghi Run {ram_pages[2]} từ Page 3 xuống Disk Output."
                })
                output_run_count += 1
                ram_pages[2] = None # Page 3 trống sau khi ghi

            # Bước C: Nạp mới vào Page 1 (Nếu còn trống)
            if ram_pages[0] is None and (all_runs_f1 or all_runs_f2):
                new_run = all_runs_f1.pop(0) if all_runs_f1 else all_runs_f2.pop(0)
                ram_pages[0] = new_run
                steps.append({
                    'act': 'REF_LOAD_TOP',
                    'values': new_run,
                    'desc': "Nạp Run tiếp theo từ Disk vào Page 1 của RAM."
                })

            # Điều kiện dừng an toàn cho mô phỏng 12 số
            if not any(ram_pages[0:2]) and not all_runs_f1 and not all_runs_f2:
                break

        steps.append({'act': 'FINISH', 'values': sorted(data), 'io_cost': io_cost, 'desc': "Sắp xếp hoàn tất!"})
        return steps
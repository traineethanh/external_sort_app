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

        # --- PASS 1: MERGE RUNS (Logic Dồn hàng - Shifting) ---
        output_run_count = 0 
        ram_pages = [[], [], []] # Page 0 (Top), Page 1 (Mid), Page 2 (Bottom)

        # Nạp lần đầu vào Page 1 và 2 (để chuẩn bị cho logic dồn)
        if all_runs_f1: ram_pages[0] = all_runs_f1.pop(0)
        if all_runs_f2: ram_pages[1] = all_runs_f2.pop(0)
        
        steps.append({
            'act': 'MERGE_LOAD_RAM',
            'r1': ram_pages[0], 'r2': ram_pages[1],
            'desc': "Nạp dữ liệu ban đầu từ F1, F2 vào RAM."
        })

        while any(ram_pages[0:2]) or all_runs_f1 or all_runs_f2:
            # 1. Gom và sắp xếp tất cả số đang có trong RAM (trừ Page 3 đang chờ xuất)
            current_in_ram = sorted(ram_pages[0] + ram_pages[1])
            if not current_in_ram: break

            # 2. CHIA LẠI TRANG (REPACK & SHIFT DOWN)
            # Lấy 2 số nhỏ nhất đưa xuống Page 3 (Bottom) để chuẩn bị xuất
            res_page = current_in_ram[:2]
            remaining = current_in_ram[2:]
            
            # Dồn các số lớn hơn (số dư) xuống Page 2 (Mid) và Page 1 (Top)
            # Theo yêu cầu của bạn: dồn xuống dưới để trống Page 1
            ram_pages[2] = res_page  # Page 3 (Bottom)
            ram_pages[1] = [remaining[0]] if len(remaining) > 0 else [] # Page 2 (Mid)
            ram_pages[0] = [remaining[1]] if len(remaining) > 1 else [] # Page 1 (Top)

            steps.append({
                'act': 'REPACK_SHIFT_DOWN',
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                'desc': f"Trích {res_page} xuống Page 3. Dồn số dư {remaining} xuống để trống chỗ ở Page 1."
            })

            # 3. XUẤT PAGE 3 XUỐNG DISK
            steps.append({
                'act': 'WRITE_OUTPUT',
                'values': ram_pages[2],
                'output_idx': output_run_count,
                'desc': f"Ghi Run kết quả {ram_pages[2]} vào Output."
            })
            output_run_count += 1
            io_cost += 1
            ram_pages[2] = [] # Làm trống Page 3

            # 4. NẠP MỚI VÀO PAGE 1 (Ô TRỐNG TRÊN CÙNG)
            if all_runs_f1 or all_runs_f2:
                # Ưu tiên lấy từ file còn dữ liệu
                new_run = all_runs_f1.pop(0) if all_runs_f1 else all_runs_f2.pop(0)
                
                # Nạp vào Page 1 (Nếu Page 1 đang có số dư lẻ, ta gộp lại hoặc ghi đè tùy logic mô phỏng)
                # Ở đây ta gộp với số dư hiện tại của Page 1 để luôn đủ trang
                ram_pages[0] = sorted(ram_pages[0] + new_run)
                
                steps.append({
                    'act': 'REF_LOAD_TOP',
                    'values': ram_pages[0],
                    'desc': f"Nạp Run mới từ Disk vào Page 1 để tiếp tục trộn."
                })
                io_cost += 1
                
            # Điều kiện dừng an toàn cho mô phỏng 12 số
            if not any(ram_pages[0:2]) and not all_runs_f1 and not all_runs_f2:
                break

        steps.append({'act': 'FINISH', 'values': sorted(data), 'io_cost': io_cost, 'desc': "Sắp xếp hoàn tất!"})
        return steps
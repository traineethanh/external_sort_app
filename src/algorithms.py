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

        # --- PASS 1: BĂNG CHUYỀN 3 TẦNG ---
        output_idx = 0
        ram_pages = [None, None, None] # [Page 1, Page 2, Page 3]

        # 1. Khởi tạo: Nạp 2 run đầu vào Page 1 và 2
        if all_runs_f1: ram_pages[0] = all_runs_f1.pop(0)
        if all_runs_f2: ram_pages[1] = all_runs_f2.pop(0)
        
        steps.append({
            'act': 'REPACK_SHIFT_DOWN',
            'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
            'desc': "Bắt đầu Pass 1: Nạp 2 Run vào Page 1 và 2."
        })

        while any(p is not None for p in ram_pages) or all_runs_f1 or all_runs_f2:
            
            # BƯỚC 1: SORT TRONG RAM (Để tìm Run nhỏ nhất đưa xuống Page 3)
            # Ta lấy tất cả các Run hiện có trong RAM, sắp xếp chúng dựa trên giá trị phần tử đầu tiên
            current_runs_in_ram = [p for p in ram_pages if p is not None]
            current_runs_in_ram.sort(key=lambda x: x[0]) # Run có số nhỏ nhất lên đầu
            
            # Gán lại vào Page theo thứ tự: Nhỏ nhất xuống Page 3, lớn nhất lên Page 1
            new_ram = [None, None, None]
            if len(current_runs_in_ram) >= 1: new_ram[2] = current_runs_in_ram[0] # Nhỏ nhất
            if len(current_runs_in_ram) >= 2: new_ram[1] = current_runs_in_ram[1] # Lớn nhì
            if len(current_runs_in_ram) >= 3: new_ram[0] = current_runs_in_ram[2] # Lớn nhất
            ram_pages = new_ram

            steps.append({
                'act': 'REPACK_SHIFT_DOWN',
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                'desc': "Sắp xếp thứ tự các Run: Nhỏ nhất về Page 3, lớn nhất về Page 1."
            })

            # BƯỚC 2: CHUYỂN PAGE 3 QUA OUTPUT
            if ram_pages[2]:
                steps.append({
                    'act': 'WRITE_OUTPUT',
                    'values': ram_pages[2],
                    'output_idx': output_idx,
                    'desc': f"Xuất Run nhỏ nhất {ram_pages[2]} từ Page 3 ra Disk."
                })
                output_idx += 1
                ram_pages[2] = None

            # BƯỚC 3: DỊCH CHUYỂN XUỐNG (Dồn hàng)
            # Page 2 -> 3, Page 1 -> 2
            ram_pages[2] = ram_pages[1]
            ram_pages[1] = ram_pages[0]
            ram_pages[0] = None

            steps.append({
                'act': 'REPACK_SHIFT_DOWN',
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                'desc': "Dịch chuyển các Run còn lại xuống 1 tầng (Page 2->3, Page 1->2)."
            })

            # BƯỚC 4: NẠP RUN TIẾP THEO TỪ DISK VÀO PAGE 1
            if all_runs_f1 or all_runs_f2:
                # Lấy run nhỏ nhất từ đầu f1 hoặc f2 (mô phỏng việc chọn run)
                if all_runs_f1 and all_runs_f2:
                    if all_runs_f1[0][0] < all_runs_f2[0][0]:
                        new_run = all_runs_f1.pop(0)
                    else:
                        new_run = all_runs_f2.pop(0)
                else:
                    new_run = all_runs_f1.pop(0) if all_runs_f1 else all_runs_f2.pop(0)
                
                ram_pages[0] = new_run
                steps.append({
                    'act': 'REF_LOAD_TOP',
                    'values': new_run,
                    'desc': f"Nạp Run tiếp theo {new_run} từ Disk vào Page 1."
                })

        steps.append({'act': 'FINISH', 'desc': "Sắp xếp hoàn tất!", 'io_cost': 0})
        return steps
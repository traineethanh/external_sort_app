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

        # --- PASS 0: TẠO RUNS (Nạp 6 số, chia nhỏ và đổ đầy F1 trước) ---
        all_runs_f1 = []
        all_runs_f2 = []
        
        for i in range(0, N, 6):
            chunk = data[i : i + 6]
            chunk_indices = list(range(i, min(i + 6, N)))
            
            # Bước 1: Nạp 6 số vào RAM
            steps.append({
                'act': 'LOAD_RAM', 
                'values': chunk, 
                'indices': chunk_indices, 
                'desc': f"Pass 0: Nạp 6 số từ Disk vào 3 trang RAM."
            })
            
            # Bước 2: Sắp xếp nội bộ
            sorted_chunk = sorted(chunk)
            steps.append({
                'act': 'SORT_RAM', 
                'values': sorted_chunk, 
                'desc': "Sắp xếp nội bộ 6 số trong RAM."
            })
            io_cost += math.ceil(len(chunk) / self.page_size)
            
            # Bước 3: Chia nhỏ thành các Run (2 số) và phân phối vào Disk
            for j in range(0, len(sorted_chunk), 2):
                run = sorted_chunk[j : j + 2]
                io_cost += 1
                
                # LOGIC MỚI: Đổ đầy F1 (3 slot) rồi mới đến F2
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
                    'desc': f"Đưa Run {run} vào {target}."
                })

        # --- PASS 1: BĂNG CHUYỀN 3 TẦNG (REPACKING) ---
        output_idx = 0
        ram_pages = [None, None, None] # [Page 1, Page 2, Page 3]

        # Khởi tạo: Nạp 2 run đầu tiên từ Disk vào RAM (Ưu tiên lấy từ F1 vì F1 đang đầy)
        if all_runs_f1: ram_pages[0] = all_runs_f1.pop(0)
        if all_runs_f1: ram_pages[1] = all_runs_f1.pop(0)
        # Nếu F1 hết thì lấy từ F2 (trường hợp dữ liệu ít hơn 4 run)
        elif all_runs_f2: ram_pages[1] = all_runs_f2.pop(0)
        
        io_cost += 2
        steps.append({
            'act': 'REPACK_SHIFT_DOWN',
            'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
            'io_cost': io_cost,
            'desc': "Pass 1 bắt đầu: Lấy 2 Run đầu từ F1 nạp vào Page 1 & 2."
        })

        while any(p is not None for p in ram_pages) or all_runs_f1 or all_runs_f2:
            
            # BƯỚC 1: TÌM RUN NHỎ NHẤT ĐƯA XUỐNG PAGE 3
            current_runs = [p for p in ram_pages if p is not None]
            current_runs.sort(key=lambda x: x[0]) 
            
            new_ram = [None, None, None]
            if len(current_runs) >= 1: new_ram[2] = current_runs[0]
            if len(current_runs) >= 2: new_ram[1] = current_runs[1]
            if len(current_runs) >= 3: new_ram[0] = current_runs[2]
            ram_pages = new_ram

            steps.append({
                'act': 'REPACK_SHIFT_DOWN',
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                'desc': "Sắp xếp: Đưa Run nhỏ nhất hiện tại trong RAM xuống Page 3."
            })

            # BƯỚC 2: XUẤT PAGE 3
            if ram_pages[2]:
                io_cost += 1
                steps.append({
                    'act': 'WRITE_OUTPUT',
                    'values': ram_pages[2],
                    'output_idx': output_idx,
                    'io_cost': io_cost,
                    'desc': f"Xuất Run {ram_pages[2]} từ Page 3 ra Output."
                })
                output_idx += 1
                ram_pages[2] = None

            # BƯỚC 3: DỊCH CHUYỂN (SHIFT DOWN)
            ram_pages[2] = ram_pages[1]
            ram_pages[1] = ram_pages[0]
            ram_pages[0] = None

            steps.append({
                'act': 'REPACK_SHIFT_DOWN',
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                'desc': "Dịch chuyển: Đẩy các Run còn lại trong RAM xuống 1 tầng."
            })

            # BƯỚC 4: NẠP RUN MỚI VÀO PAGE 1 (Ưu tiên quét sạch F1 rồi mới tới F2)
            if all_runs_f1 or all_runs_f2:
                new_run = all_runs_f1.pop(0) if all_runs_f1 else all_runs_f2.pop(0)
                ram_pages[0] = new_run
                io_cost += 1
                steps.append({
                    'act': 'REF_LOAD_TOP',
                    'values': new_run,
                    'io_cost': io_cost,
                    'desc': f"Nạp Run tiếp theo {new_run} từ Disk vào Page 1."
                })

        steps.append({'act': 'FINISH', 'desc': "Sắp xếp hoàn tất!", 'io_cost': io_cost})
        return steps
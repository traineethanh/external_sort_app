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

        # --- PASS 0: TẠO RUNS (Giữ nguyên nạp 6 phần tử) ---
        all_runs_f1 = []
        all_runs_f2 = []
        
        for i in range(0, N, 6):
            chunk = data[i : i + 6]
            chunk_indices = list(range(i, min(i + 6, N)))
            
            # Bước 1: Nạp 6 số vào 3 trang RAM
            steps.append({
                'act': 'LOAD_RAM', 
                'values': chunk, 
                'indices': chunk_indices, 
                'desc': f"Pass 0: Nạp 6 số từ Disk vào 3 trang RAM."
            })
            
            # Bước 2: Sắp xếp nội bộ 6 số đó
            sorted_chunk = sorted(chunk)
            steps.append({
                'act': 'SORT_RAM', 
                'values': sorted_chunk, 
                'desc': "Sắp xếp nội bộ 6 số trong RAM."
            })
            io_cost += math.ceil(len(chunk) / self.page_size)
            
            # Bước 3: Chia 6 số đã sort thành 3 run (mỗi run 2 số) và đẩy vào F1/F2
            for j in range(0, len(sorted_chunk), 2):
                run = sorted_chunk[j : j + 2]
                io_cost += 1
                
                if len(all_runs_f1) <= len(all_runs_f2):
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
        # Đây là phần bạn cần: Page 3 chứa 2 số nhỏ nhất, sau đó dịch chuyển.
        output_idx = 0
        ram_pages = [None, None, None] # [Page 1, Page 2, Page 3]

        # 1. Nạp 2 run đầu tiên vào Page 1 và Page 2
        if all_runs_f1: ram_pages[0] = all_runs_f1.pop(0)
        if all_runs_f2: ram_pages[1] = all_runs_f2.pop(0)
        io_cost += 2
        
        steps.append({
            'act': 'REPACK_SHIFT_DOWN',
            'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
            'io_cost': io_cost,
            'desc': "Pass 1 bắt đầu: Nạp 2 Run vào Page 1 & 2."
        })

        while any(p is not None for p in ram_pages) or all_runs_f1 or all_runs_f2:
            
            # BƯỚC 1: SORT TRONG RAM ĐỂ ĐẨY RUN NHỎ NHẤT XUỐNG PAGE 3
            current_runs = [p for p in ram_pages if p is not None]
            # Sắp xếp các Run dựa trên số nhỏ nhất của mỗi Run
            current_runs.sort(key=lambda x: x[0]) 
            
            # Cập nhật lại các Page theo đúng ý bạn: Nhỏ nhất nằm ở Page 3
            new_ram = [None, None, None]
            if len(current_runs) >= 1: new_ram[2] = current_runs[0] # Run nhỏ nhất (2 số)
            if len(current_runs) >= 2: new_ram[1] = current_runs[1] 
            if len(current_runs) >= 3: new_ram[0] = current_runs[2]
            ram_pages = new_ram

            steps.append({
                'act': 'REPACK_SHIFT_DOWN',
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                'desc': "Sắp xếp: Run chứa 2 số nhỏ nhất được đưa xuống Page 3."
            })

            # BƯỚC 2: CHUYỂN RUN NHỎ NHẤT (PAGE 3) QUA OUTPUT
            if ram_pages[2]:
                io_cost += 1
                steps.append({
                    'act': 'WRITE_OUTPUT',
                    'values': ram_pages[2],
                    'output_idx': output_idx,
                    'io_cost': io_cost,
                    'desc': f"Chuyển run nhỏ nhất {ram_pages[2]} từ Page 3 ra Output."
                })
                output_idx += 1
                ram_pages[2] = None

            # BƯỚC 3: DỊCH CHUYỂN 2 RUN TRÊN XUỐNG DƯỚI 1 RUN
            # Page 2 -> 3, Page 1 -> 2
            ram_pages[2] = ram_pages[1]
            ram_pages[1] = ram_pages[0]
            ram_pages[0] = None

            steps.append({
                'act': 'REPACK_SHIFT_DOWN',
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                'desc': "Dịch chuyển 2 run tầng trên xuống dưới 1 bậc."
            })

            # BƯỚC 4: TIẾP TỤC LẤY RUN TỪ DISK (NẠP VÀO PAGE 1)
            if all_runs_f1 or all_runs_f2:
                # Ưu tiên lấy từ F1 rồi đến F2 để lấp đầy lối vào
                new_run = all_runs_f1.pop(0) if all_runs_f1 else all_runs_f2.pop(0)
                ram_pages[0] = new_run
                io_cost += 1
                steps.append({
                    'act': 'REF_LOAD_TOP',
                    'values': new_run,
                    'io_cost': io_cost,
                    'desc': f"Tiếp tục lấy Run {new_run} từ Disk nạp vào Page 1."
                })

        steps.append({'act': 'FINISH', 'desc': "Hoàn thành sắp xếp!", 'io_cost': io_cost})
        return steps
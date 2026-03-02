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
        if N > 12: return []

        all_runs_f1 = []
        all_runs_f2 = []
        
        # --- PASS 0: TẠO RUN VÀ ĐỔ ĐẦY F1 TRƯỚC ---
        for i in range(0, N, 6):
            chunk = data[i : i + 6]
            steps.append({'act': 'LOAD_RAM', 'values': chunk, 'indices': list(range(i, min(i+6, N))), 'desc': "Pass 0: Nạp 6 số vào RAM."})
            sorted_chunk = sorted(chunk)
            steps.append({'act': 'SORT_RAM', 'values': sorted_chunk, 'desc': "Sắp xếp nội bộ."})
            io_cost += math.ceil(len(chunk) / 2)
            
            for j in range(0, len(sorted_chunk), 2):
                run = sorted_chunk[j : j + 2]
                io_cost += 1
                if len(all_runs_f1) < 3:
                    target, r_idx = 'F1', len(all_runs_f1)
                    all_runs_f1.append(run)
                else:
                    target, r_idx = 'F2', len(all_runs_f2)
                    all_runs_f2.append(run)
                steps.append({'act': 'WRITE_F_BUFFER', 'values': run, 'target': target, 'run_idx': r_idx, 'io_cost': io_cost, 'desc': f"Ghi Run {run} vào {target}."})

        # --- PASS 1: BĂNG CHUYỀN (REPACKING) ---
        ram_pages = [None, None, None] 
        
        # Khởi tạo: Lấy mỗi file 1 Run
        if all_runs_f1: ram_pages[0] = all_runs_f1.pop(0)
        if all_runs_f2: ram_pages[1] = all_runs_f2.pop(0)
        
        io_cost += 2
        steps.append({
            'act': 'REPACK_SHIFT_DOWN', 'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': None, 
            'io_cost': io_cost, 'desc': "Khởi đầu Pass 1: Nạp Run đầu tiên của F1 và F2 vào RAM."
        })

        while any(p is not None for p in ram_pages) or all_runs_f1 or all_runs_f2:
            # 1. So sánh và đẩy Run nhỏ nhất xuống Page 3
            current = [p for p in ram_pages if p is not None]
            current.sort(key=lambda x: x[0])
            
            new_ram = [None, None, None]
            if len(current) >= 1: new_ram[2] = current[0]
            if len(current) >= 2: new_ram[1] = current[1]
            if len(current) >= 3: new_ram[0] = current[2]
            ram_pages = new_ram
            steps.append({'act': 'REPACK_SHIFT_DOWN', 'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2], 'desc': "Sắp xếp: Đưa Run nhỏ nhất trong RAM xuống Page 3."})

            # 2. Xuất Page 3 ra Disk
            if ram_pages[2]:
                io_cost += 1
                steps.append({'act': 'WRITE_OUTPUT', 'values': ram_pages[2], 'output_idx': len([s for s in steps if s['act']=='WRITE_OUTPUT']), 'io_cost': io_cost, 'desc': f"Xuất Run {ram_pages[2]} ra Disk."})
                ram_pages[2] = None

            # 3. Dịch chuyển (Shift down)
            ram_pages[2] = ram_pages[1]
            ram_pages[1] = ram_pages[0]
            ram_pages[0] = None
            steps.append({'act': 'REPACK_SHIFT_DOWN', 'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2], 'desc': "Dịch chuyển: Page 2 -> 3, Page 1 -> 2."})

            # 4. Nạp từ Disk: ƯU TIÊN CHỌN RUN NHỎ NHẤT (QUAN TRỌNG)
            if all_runs_f1 or all_runs_f2:
                # So sánh run đứng đầu của F1 và F2
                if all_runs_f1 and all_runs_f2:
                    if all_runs_f1[0][0] <= all_runs_f2[0][0]:
                        new_run = all_runs_f1.pop(0)
                        source = "F1"
                    else:
                        new_run = all_runs_f2.pop(0)
                        source = "F2"
                else:
                    new_run = all_runs_f1.pop(0) if all_runs_f1 else all_runs_f2.pop(0)
                    source = "F1" if all_runs_f1 else "F2"

                ram_pages[0] = new_run
                io_cost += 1
                steps.append({
                    'act': 'REF_LOAD_TOP', 'values': new_run, 'io_cost': io_cost, 
                    'desc': f"So sánh Disk: Run {new_run} ở {source} nhỏ hơn, nạp vào Page 1."
                })

        steps.append({'act': 'FINISH', 'desc': "Sắp xếp hoàn tất theo kịch bản Repacking!", 'io_cost': io_cost})
        return steps
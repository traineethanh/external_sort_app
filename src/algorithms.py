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
        
        # --- PASS 0: TẠO RUNS BAN ĐẦU ---
        for i in range(0, N, 6):
            chunk = data[i : i + 6]
            steps.append({'act': 'LOAD_RAM', 'values': chunk, 'indices': list(range(i, min(i+6, N))), 'desc': "Pass 0: Nạp 6 số vào RAM."})
            sorted_chunk = sorted(chunk)
            steps.append({'act': 'SORT_RAM', 'values': sorted_chunk, 'desc': "Sắp xếp nội bộ 6 số."})
            io_cost += 1
            
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

        # --- PASS 1: REPACKING THEO YÊU CẦU ---
        ram_pages = [None, None, None] # [Page 1, Page 2, Page 3]
        
        # Bước 1: Nạp 2 run đầu tiên từ F1 và F2
        if all_runs_f1: ram_pages[0] = all_runs_f1.pop(0)
        if all_runs_f2: ram_pages[1] = all_runs_f2.pop(0)
        io_cost += 2
        steps.append({
            'act': 'REPACK_SHIFT_DOWN', 
            'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': None, 
            'clear_sources': ['F1', 'F2'], # Bổ sung để UI xóa 2 run đầu ở Disk
            'desc': "Nạp 2 Run đầu từ F1, F2 vào RAM."
        })

        output_idx = 0
        while any(p is not None for p in ram_pages) or all_runs_f1 or all_runs_f2:
            # GOM TẤT CẢ PHẦN TỬ TRONG RAM ĐỂ SORT
            all_elements = []
            for p in ram_pages:
                if p: all_elements.extend(p)
            all_elements.sort()

            if not all_elements: break

            # PHÂN BỔ THEO YÊU CẦU:
            # Page 3: 2 phần tử nhỏ nhất
            # Page 2: 1 phần tử lớn tiếp theo
            # Page 1: 1 phần tử lớn nhất
            new_p3 = all_elements[:2] if len(all_elements) >= 2 else all_elements
            remaining = all_elements[2:]
            
            new_p2 = [remaining[0]] if len(remaining) >= 1 else None
            new_p1 = [remaining[1]] if len(remaining) >= 2 else None
            
            ram_pages = [new_p1, new_p2, new_p3]
            steps.append({
                'act': 'REPACK_SHIFT_DOWN', 
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2], 
                'desc': "Sort RAM: Page 3 giữ 2 số nhỏ nhất, Page 1 & 2 giữ các số lớn hơn."
            })

            # XUẤT PAGE 3
            if ram_pages[2]:
                io_cost += 1
                steps.append({'act': 'WRITE_OUTPUT', 'values': ram_pages[2], 'output_idx': output_idx, 'io_cost': io_cost, 'desc': f"Xuất Page 3 chứa {ram_pages[2]}."})
                output_idx += 1
                ram_pages[2] = None

            # DỊCH CHUYỂN XUỐNG
            ram_pages[2] = ram_pages[1]
            ram_pages[1] = ram_pages[0]
            ram_pages[0] = None
            steps.append({'act': 'REPACK_SHIFT_DOWN', 'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2], 'desc': "Dịch chuyển Page 1->2, 2->3."})

            # NẠP TIẾP TỪ DISK (Ưu tiên run có số đầu nhỏ hơn)
            if all_runs_f1 or all_runs_f2:
                if all_runs_f1 and all_runs_f2:
                    if all_runs_f1[0][0] <= all_runs_f2[0][0]:
                        new_run, source = all_runs_f1.pop(0), "F1" # Gán source
                    else:
                        new_run, source = all_runs_f2.pop(0), "F2" # Gán source
                    io_cost += 1
                else:
                    source = "F1" if all_runs_f1 else "F2"
                    new_run = all_runs_f1.pop(0) if all_runs_f1 else all_runs_f2.pop(0)
                    io_cost += 1
                
                ram_pages[0] = new_run
                steps.append({
                    'act': 'REF_LOAD_TOP', 
                    'values': new_run, 
                    'source': source, # Bổ sung để UI biết xóa ở đâu
                    'io_cost': io_cost, 
                    'desc': f"Nạp Run {new_run} từ {source} vào Page 1."
                })

        steps.append({'act': 'FINISH', 'desc': "Hoàn thành!", 'io_cost': io_cost})
        return steps
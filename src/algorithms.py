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

        # --- PASS 0: TẠO CÁC RUN NHỎ (Đúng chuẩn Repacking) ---
        # Thay vì nạp 6, ta nạp từng 2 số để tạo ra các thực thể "Run" riêng biệt trên Disk
        all_runs_f1 = []
        all_runs_f2 = []
        
        for i in range(0, N, 2):
            chunk = data[i : i + 2]
            sorted_run = sorted(chunk)
            
            # 1. Nạp vào RAM (Sử dụng Page 1 làm lối vào)
            steps.append({
                'act': 'LOAD_RAM', 
                'values': chunk, 
                'indices': list(range(i, min(i + 2, N))), 
                'desc': f"Pass 0: Nạp {chunk} vào RAM Page 1."
            })
            
            # 2. Sắp xếp nội bộ
            steps.append({
                'act': 'SORT_RAM', 
                'values': sorted_run, 
                'desc': "Sắp xếp nội bộ Run."
            })
            io_cost += 1 # 1 lần đọc
            
            # 3. Ghi ra Disk (F1 hoặc F2)
            target = 'F1' if (i // 2) % 2 == 0 else 'F2'
            r_idx = (i // 2) // 2
            if target == 'F1': all_runs_f1.append(sorted_run)
            else: all_runs_f2.append(sorted_run)
            
            io_cost += 1 # 1 lần ghi
            steps.append({
                'act': 'WRITE_F_BUFFER', 
                'values': sorted_run, 'target': target, 'run_idx': r_idx, 
                'io_cost': io_cost,
                'desc': f"Lưu Run {sorted_run} vào {target}."
            })

        # --- PASS 1: BĂNG CHUYỀN 3 TẦNG (REPACKING) ---
        output_idx = 0
        ram_pages = [None, None, None] # [Page 1, Page 2, Page 3]

        # 1. KHỞI TẠO: Nạp 2 run đầu tiên từ Disk vào RAM
        if all_runs_f1: ram_pages[0] = all_runs_f1.pop(0)
        if all_runs_f2: ram_pages[1] = all_runs_f2.pop(0)
        io_cost += 2
        
        steps.append({
            'act': 'REPACK_SHIFT_DOWN',
            'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
            'io_cost': io_cost,
            'desc': "Bắt đầu Pass 1: Nạp Run từ F1 vào Page 1, F2 vào Page 2."
        })

        # Vòng lặp điều phối Băng chuyền
        while any(p is not None for p in ram_pages) or all_runs_f1 or all_runs_f2:
            
            # BƯỚC 1: SO SÁNH VÀ SẮP XẾP THỨ TỰ TRONG RAM
            # (Tìm Run có giá trị nhỏ nhất để đưa xuống Page 3 - Cửa ra)
            current_runs = [p for p in ram_pages if p is not None]
            current_runs.sort(key=lambda x: x[0]) # Sắp xếp các khối dựa trên số đầu tiên
            
            # Phân bổ lại vị trí: Nhỏ nhất -> Page 3, Lớn nhất -> Page 1
            new_ram = [None, None, None]
            if len(current_runs) >= 1: new_ram[2] = current_runs[0] 
            if len(current_runs) >= 2: new_ram[1] = current_runs[1]
            if len(current_runs) >= 3: new_ram[0] = current_runs[2]
            ram_pages = new_ram

            steps.append({
                'act': 'REPACK_SHIFT_DOWN',
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                'desc': "So sánh: Dịch chuyển Run nhỏ nhất xuống Page 3 để chuẩn bị xuất."
            })

            # BƯỚC 2: XUẤT PAGE 3 RA OUTPUT
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
                ram_pages[2] = None # Làm trống cửa ra

            # BƯỚC 3: DỊCH CHUYỂN XUỐNG (SHIFTING)
            # Đây là bước "Dịch chuyển 2 run trên xuống dưới 1 run" như bạn yêu cầu
            ram_pages[2] = ram_pages[1]
            ram_pages[1] = ram_pages[0]
            ram_pages[0] = None

            steps.append({
                'act': 'REPACK_SHIFT_DOWN',
                'p1': ram_pages[0], 'p2': ram_pages[1], 'p3': ram_pages[2],
                'desc': "Dịch chuyển tầng: Đẩy các Run phía trên xuống dưới 1 bậc."
            })

            # BƯỚC 4: TIẾP TỤC LẤY RUN TỪ DISK (NẠP VÀO PAGE 1)
            if all_runs_f1 or all_runs_f2:
                # Chọn Run tiếp theo từ Disk để nạp vào lối vào đang trống (Page 1)
                if all_runs_f1:
                    new_run = all_runs_f1.pop(0)
                else:
                    new_run = all_runs_f2.pop(0)
                
                ram_pages[0] = new_run
                io_cost += 1
                steps.append({
                    'act': 'REF_LOAD_TOP',
                    'values': new_run,
                    'io_cost': io_cost,
                    'desc': f"Nạp Run mới {new_run} từ Disk vào Page 1 đang trống."
                })

        steps.append({'act': 'FINISH', 'desc': "Sắp xếp hoàn tất theo cơ chế Repacking!", 'io_cost': io_cost})
        return steps
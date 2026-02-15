import utils

class ExternalSortEngine:
    def __init__(self, buffer_pages=3):
        self.B = buffer_pages  # Sử dụng 3 trang buffer theo tài liệu [cite: 18, 260]

    def get_simulation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        steps = []
        io_cost = 0  # Chi phí I/O tích lũy 
        
        # --- BƯỚC 0: KHỞI TẠO DISK ---
        steps.append({
            'act': 'INIT_DISK', 
            'values': data, 
            'io_cost': 0, 
            'desc': "Khởi tạo dữ liệu gốc trên Disk (Input Disk) [cite: 261, 262]"
        })

        # --- PASS 0: TẠO CÁC RUNS (SPLIT & SORT) ---
        # Giả sử mỗi Run có kích thước bằng số trang Buffer có sẵn [cite: 254, 595]
        run_size = 4 
        all_runs = []
        
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            io_cost += len(chunk) # Mỗi số được đọc là 1 I/O [cite: 585]
            
            steps.append({
                'act': 'READ', 'values': chunk, 'idx': i, 
                'io_cost': io_cost, 'desc': f"Pass 0: Nạp {len(chunk)} số vào RAM Buffer [cite: 286]"
            })
            
            sorted_chunk = sorted(chunk)
            steps.append({
                'act': 'SORT', 'values': sorted_chunk, 
                'io_cost': io_cost, 'desc': "Sắp xếp nội bộ trong RAM (Internal Sort) [cite: 254, 587]"
            })
            
            all_runs.append(sorted_chunk)
            io_cost += len(sorted_chunk) # Mỗi số được ghi lại xuống Disk là 1 I/O [cite: 585]
            steps.append({
                'act': 'WRITE_RUN', 'values': sorted_chunk, 'run_idx': len(all_runs)-1, 
                'io_cost': io_cost, 'desc': f"Ghi Run {len(all_runs)-1} đã sắp xếp xuống Disk [cite: 341]"
            })

        # --- CÁC PASS TRỘN (MERGE PASSES) ---
        pass_idx = 1
        while len(all_runs) > 1:
            new_runs = []
            for i in range(0, len(all_runs), 2):
                if i + 1 < len(all_runs):
                    r1, r2 = all_runs[i], all_runs[i+1]
                    io_cost += (len(r1) + len(r2))
                    
                    steps.append({
                        'act': 'LOAD_FOR_MERGE', 'r1_idx': i, 'r2_idx': i+1, 
                        'io_cost': io_cost, 'desc': f"Pass {pass_idx}: Nạp Run {i} và {i+1} để trộn [cite: 135]"
                    })
                    
                    merged = sorted(r1 + r2) # Logic trộn 2 danh sách [cite: 5, 255]
                    new_runs.append(merged)
                    io_cost += len(merged)
                    
                    steps.append({
                        'act': 'SAVE_MERGED', 'values': merged, 
                        'io_cost': io_cost, 'desc': f"Hoàn tất Pass {pass_idx}. Ghi kết quả xuống Disk [cite: 589]"
                    })
                else:
                    new_runs.append(all_runs[i])
                    steps.append({
                        'act': 'SKIP_LE', 'run_idx': i, 
                        'io_cost': io_cost, 'desc': f"Run {i} lẻ, đợi trộn ở Pass sau [cite: 256]"
                    })
            all_runs = new_runs
            pass_idx += 1
            
        return steps
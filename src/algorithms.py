import utils

class ExternalSort:
    def get_full_animation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        run_size = 4 
        steps = []
        
        # --- BƯỚC 0: Khởi tạo dữ liệu gốc trên Input Disk ---
        steps.append({'act': 'INIT_DISK', 'values': data, 'desc': "Dữ liệu gốc trên Input Disk"})

        # --- PASS 0: Tạo các Initial Runs (Chia để trị) ---
        all_runs = []
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            steps.append({'act': 'READ', 'values': chunk, 'idx': i, 'desc': f"Đọc dữ liệu từ Disk vào RAM để tạo Run"})
            
            sorted_chunk = sorted(chunk)
            steps.append({'act': 'SORT', 'values': sorted_chunk, 'desc': "Sắp xếp nội bộ trong RAM"})
            
            all_runs.append(sorted_chunk)
            steps.append({'act': 'WRITE_RUN', 'values': sorted_chunk, 'run_idx': len(all_runs)-1, 'desc': f"Ghi Run {len(all_runs)-1} lên Output Disk"})

        # --- CÁC PASS MERGE: Trộn cho đến khi xong hoàn toàn ---
        pass_idx = 1
        while len(all_runs) > 1:
            new_runs = []
            for i in range(0, len(all_runs), 2):
                if i + 1 < len(all_runs):
                    r1, r2 = all_runs[i], all_runs[i+1]
                    # Trộn 2 Run: Kéo ngược từ Output Disk về RAM
                    steps.append({'act': 'LOAD_FOR_MERGE', 'r1_idx': i, 'r2_idx': i+1, 'desc': f"Pass {pass_idx}: Trộn Run {i} và {i+1}"})
                    
                    merged = sorted(r1 + r2) # Logic trộn thực tế
                    new_runs.append(merged)
                    steps.append({'act': 'SAVE_MERGED', 'values': merged, 'pass_idx': pass_idx, 'desc': f"Kết quả trộn Pass {pass_idx} đã sẵn sàng"})
                else:
                    new_runs.append(all_runs[i])
            all_runs = new_runs
            pass_idx += 1
            
        return steps
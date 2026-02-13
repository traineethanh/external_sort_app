import utils

class ExternalSort:
    def get_full_animation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        run_size = 4 # Mỗi run 4 phần tử, tổng 12 phần tử => 3 runs
        steps = []
        
        # --- BƯỚC 0: Khởi tạo dữ liệu ---
        steps.append({'act': 'INIT_DISK', 'values': data, 'desc': "Dữ liệu ban đầu trên Disk"})

        # --- PASS 0: Tạo các Runs ban đầu ---
        all_runs = []
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            sorted_chunk = sorted(chunk)
            all_runs.append(sorted_chunk)
            steps.append({'act': 'READ', 'values': chunk, 'idx': i, 'desc': "Đọc vào RAM"})
            steps.append({'act': 'SORT', 'values': sorted_chunk, 'desc': "Sắp xếp trong RAM"})
            steps.append({'act': 'WRITE_RUN', 'values': sorted_chunk, 'run_idx': len(all_runs)-1, 'desc': f"Tạo Run {len(all_runs)-1}"})

        # --- CÁC PASS MERGE: Tiếp tục đến khi chỉ còn 1 Run duy nhất ---
        pass_idx = 1
        while len(all_runs) > 1:
            new_runs = []
            i = 0
            while i < len(all_runs):
                if i + 1 < len(all_runs):
                    # Trộn cặp Run i và i+1
                    r1, r2 = all_runs[i], all_runs[i+1]
                    steps.append({'act': 'LOAD_FOR_MERGE', 'r1_idx': i, 'r2_idx': i+1, 'desc': f"Pass {pass_idx}: Trộn Run {i} và {i+1}"})
                    merged = sorted(r1 + r2)
                    new_runs.append(merged)
                    steps.append({'act': 'SAVE_MERGED', 'values': merged, 'desc': f"Ghi kết quả trộn Pass {pass_idx}"})
                    i += 2
                else:
                    # ĐÂY LÀ CHỖ QUAN TRỌNG: Xử lý Run lẻ bên phải
                    new_runs.append(all_runs[i])
                    steps.append({'act': 'SKIP_LE', 'run_idx': i, 'desc': f"Run {i} lẻ, chuyển sang Pass sau để trộn tiếp"})
                    i += 1
            all_runs = new_runs
            pass_idx += 1
            
        return steps
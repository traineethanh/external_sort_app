import utils

class ExternalSort:
    def get_full_animation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        # Sử dụng kích thước run nhỏ để dễ quan sát hoạt ảnh
        run_size = 4 
        steps = []
        
        # --- KHỞI TẠO: Dữ liệu gốc trên Input Disk ---
        steps.append({'act': 'INIT_DISK', 'values': data, 'desc': "Khoi tao du lieu goc tren Disk"})

        # --- PASS 0: Chia nhỏ thành các Initial Runs ---
        # [cite: 254, 587]
        all_runs = []
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            sorted_chunk = sorted(chunk)
            all_runs.append(sorted_chunk)
            steps.append({'act': 'READ', 'values': chunk, 'idx': i, 'desc': "Pass 0: Doc du lieu len RAM"})
            steps.append({'act': 'SORT', 'values': sorted_chunk, 'desc': "Sap xep trong RAM"})
            steps.append({'act': 'WRITE_RUN', 'values': sorted_chunk, 'run_idx': len(all_runs)-1, 'desc': f"Tao Run {len(all_runs)-1}"})

        # --- CÁC PASS MERGE: Trộn liên tục cho đến khi xong ---
        # Quy trình này lặp lại cho đến khi chỉ còn 1 file duy nhất 
        pass_idx = 1
        while len(all_runs) > 1:
            new_runs = []
            i = 0
            while i < len(all_runs):
                if i + 1 < len(all_runs):
                    # Trộn cặp Run i và i+1 theo thuật toán external merge [cite: 15, 255]
                    r1, r2 = all_runs[i], all_runs[i+1]
                    steps.append({'act': 'LOAD_FOR_MERGE', 'r1_idx': i, 'r2_idx': i+1, 'desc': f"Pass {pass_idx}: Tron Run {i} va {i+1}"})
                    merged = sorted(r1 + r2)
                    new_runs.append(merged)
                    steps.append({'act': 'SAVE_MERGED', 'values': merged, 'desc': f"Hoan tat Pass {pass_idx}"})
                    i += 2
                else:
                    # Xử lý Run lẻ (Run bên phải mà bạn gặp lỗi)
                    new_runs.append(all_runs[i])
                    steps.append({'act': 'SKIP_LE', 'run_idx': i, 'desc': f"Run {i} le, doi de tron o Pass tiep theo"})
                    i += 1
            all_runs = new_runs
            pass_idx += 1
        return steps
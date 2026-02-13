import utils

class ExternalSort:
    def get_full_animation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        run_size = 4 
        steps = []
        
        # --- INIT ---
        steps.append({'act': 'INIT_DISK', 'values': data, 'desc': "Khoi tao du lieu goc tren Disk"})

        # --- PASS 0: Tạo Initial Runs [cite: 254] ---
        all_runs = []
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            steps.append({'act': 'READ', 'values': chunk, 'idx': i, 'desc': "Doc du lieu vao RAM"})
            sorted_chunk = sorted(chunk)
            steps.append({'act': 'SORT', 'values': sorted_chunk, 'desc': "Sap xep trong RAM"})
            all_runs.append(sorted_chunk)
            steps.append({'act': 'WRITE_RUN', 'values': sorted_chunk, 'run_idx': len(all_runs)-1, 'desc': f"Tao Run {len(all_runs)-1}"})

        # --- CÁC PASS MERGE: Trộn đến khi xong  ---
        pass_idx = 1
        while len(all_runs) > 1:
            new_runs = []
            for i in range(0, len(all_runs), 2):
                if i + 1 < len(all_runs):
                    r1, r2 = all_runs[i], all_runs[i+1]
                    steps.append({'act': 'LOAD_FOR_MERGE', 'r1_idx': i, 'r2_idx': i+1, 'desc': f"Pass {pass_idx}: Tron Run {i} va {i+1}"})
                    merged = sorted(r1 + r2)
                    new_runs.append(merged)
                    steps.append({'act': 'SAVE_MERGED', 'values': merged, 'desc': f"Ghi ket qua tron Pass {pass_idx}"})
                else:
                    # Xu ly Run le (Run ben phai ban thac mac) [cite: 582]
                    new_runs.append(all_runs[i])
                    steps.append({'act': 'SKIP_LE', 'run_idx': i, 'desc': f"Run {i} le, chuyen sang Pass sau"})
            all_runs = new_runs
            pass_idx += 1
        return steps
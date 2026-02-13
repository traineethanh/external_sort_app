import utils

class ExternalSort:
    def get_full_animation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        run_size = 4 
        steps = []
        
        # --- Pass 0: Tạo Initial Runs --- [cite: 254, 587]
        all_runs = []
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            sorted_chunk = sorted(chunk)
            all_runs.append(sorted_chunk)
            steps.append({'act': 'INIT_DISK', 'values': data, 'desc': "Khoi tao du lieu goc"})
            steps.append({'act': 'READ', 'values': chunk, 'idx': i, 'desc': "Doc du lieu vao RAM"})
            steps.append({'act': 'SORT', 'values': sorted_chunk, 'desc': "Sap xep trong RAM"})
            steps.append({'act': 'WRITE_RUN', 'values': sorted_chunk, 'run_idx': len(all_runs)-1, 'desc': f"Tao Run {len(all_runs)-1}"})

        # --- Merge Passes: Tron den khi con duy nhat 1 file --- [cite: 588, 590]
        pass_idx = 1
        while len(all_runs) > 1:
            new_runs = []
            i = 0
            while i < len(all_runs):
                if i + 1 < len(all_runs):
                    # Trộn cặp run chẵn
                    r1, r2 = all_runs[i], all_runs[i+1]
                    steps.append({'act': 'LOAD_FOR_MERGE', 'r1_idx': i, 'r2_idx': i+1, 'desc': f"Pass {pass_idx}: Tron Run {i} va {i+1}"})
                    merged = sorted(r1 + r2)
                    new_runs.append(merged)
                    steps.append({'act': 'SAVE_MERGED', 'values': merged, 'desc': f"Ghi ket qua tron Pass {pass_idx}"})
                    i += 2
                else:
                    # Xu ly Run le (Run thu 3 ben phai) 
                    new_runs.append(all_runs[i])
                    steps.append({'act': 'SKIP_LE', 'run_idx': i, 'desc': f"Run {i} le, doi de tron o Pass sau"})
                    i += 1
            all_runs = new_runs
            pass_idx += 1
        return steps
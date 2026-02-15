import utils

class ExternalSort:
    def get_full_animation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        run_size = 4  # Gia su moi trang RAM chua 4 so
        steps = []
        
        steps.append({'act': 'INIT_DISK', 'values': data, 'desc': "Khoi tao du lieu goc tren Disk"})

        # --- PASS 0: Chia thanh cac Run (Sorted Chunks) [cite: 254] ---
        all_runs = []
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            steps.append({'act': 'READ', 'values': chunk, 'idx': i, 'desc': "Pass 0: Doc trang vao RAM"})
            sorted_chunk = sorted(chunk)
            all_runs.append(sorted_chunk)
            steps.append({'act': 'SORT', 'values': sorted_chunk, 'desc': "Sap xep noi bo trong RAM"})
            steps.append({'act': 'WRITE_RUN', 'values': sorted_chunk, 'run_idx': len(all_runs)-1, 'desc': f"Ghi Run {len(all_runs)-1} xuong Disk"})

        # --- MERGE PASSES: Tron cac Run [cite: 255, 256] ---
        pass_idx = 1
        while len(all_runs) > 1:
            new_runs = []
            i = 0
            while i < len(all_runs):
                if i + 1 < len(all_runs):
                    r1, r2 = all_runs[i], all_runs[i+1]
                    steps.append({'act': 'LOAD_FOR_MERGE', 'r1_idx': i, 'r2_idx': i+1, 'desc': f"Pass {pass_idx}: Tron Run {i} va {i+1}"})
                    merged = sorted(r1 + r2)
                    new_runs.append(merged)
                    steps.append({'act': 'SAVE_MERGED', 'values': merged, 'desc': f"Ket qua sau Pass {pass_idx}"})
                    i += 2
                else:
                    new_runs.append(all_runs[i])
                    steps.append({'act': 'SKIP_LE', 'run_idx': i, 'desc': "Run le, doi de tron o Pass tiep theo"})
                    i += 1
            all_runs = new_runs
            pass_idx += 1
        return steps
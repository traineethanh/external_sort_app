class ExternalSort:
    def get_full_animation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        run_size = 4 
        steps = []
        
        # --- PASS 0: Tạo các Initial Runs ---
        all_runs = []
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            sorted_chunk = sorted(chunk)
            all_runs.append(sorted_chunk)
            steps.append({
                'pass': 0, 'act': 'WRITE_RUN', 'values': sorted_chunk, 
                'run_idx': len(all_runs)-1, 'desc': f"Pass 0: Tao Run {len(all_runs)-1}"
            })

        # --- CÁC PASS TIẾP THEO: Merge các Runs ---
        pass_idx = 1
        while len(all_runs) > 1:
            new_runs = []
            for i in range(0, len(all_runs), 2):
                if i + 1 < len(all_runs):
                    # Trộn Run i và Run i+1 [cite: 363]
                    r1, r2 = all_runs[i], all_runs[i+1]
                    steps.append({
                        'pass': pass_idx, 'act': 'LOAD_FOR_MERGE', 
                        'r1_idx': i, 'r2_idx': i+1, 'desc': f"Pass {pass_idx}: Tron Run {i} va {i+1}"
                    })
                    
                    merged = []
                    p1, p2 = 0, 0
                    while p1 < len(r1) and p2 < len(r2):
                        # So sánh Min(A1, B1) để đưa vào Buffer đầu ra [cite: 22, 26]
                        if r1[p1] <= r2[p2]:
                            merged.append(r1[p1]); p1 += 1
                        else:
                            merged.append(r2[p2]); p2 += 1
                    merged.extend(r1[p1:]); merged.extend(r2[p2:])
                    
                    new_runs.append(merged)
                    steps.append({
                        'pass': pass_idx, 'act': 'SAVE_MERGED', 
                        'values': merged, 'new_idx': len(new_runs)-1, 'desc': f"Ghi ket qua tron vao Run moi"
                    })
                else:
                    new_runs.append(all_runs[i])
            all_runs = new_runs
            pass_idx += 1
            
        return steps
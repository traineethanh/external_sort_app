import utils
import os

class ExternalSort:
    def __init__(self, buffer_size=3):
        # Thuật toán yêu cầu ít nhất 3 Buffer Pages [cite: 18, 230]
        self.buffer_size = buffer_size

    def get_full_animation_steps(self, input_file):
        """
        Ghi lại mọi hành động di chuyển dữ liệu để tạo animation.
        Quy trình: Chia runs (Pass 0) -> Trộn runs (Pass 1...n)[cite: 254, 255, 256].
        """
        data = utils.read_binary_file(input_file)
        # Kích thước mỗi run nhỏ (< 10 phần tử) để dễ quan sát animation [cite: 360]
        run_size = 4 
        steps = []
        
        # --- BƯỚC 0: KHỞI TẠO ---
        steps.append({
            'act': 'INIT_DISK', 
            'values': data, 
            'desc': "Khởi tạo: Dữ liệu thực 8-byte nằm trên INPUT DISK"
        })

        # --- GIAI ĐOẠN 1: PASS 0 - TẠO CÁC INITIAL RUNS ---
        # Chia file thành các đoạn nhỏ để sắp xếp trong bộ nhớ [cite: 254, 361]
        all_runs = []
        for i in range(0, len(data), run_size):
            chunk = data[i:i + run_size]
            
            # 1. READ: Đọc từ Disk vào RAM [cite: 13, 266]
            steps.append({
                'act': 'READ', 
                'values': chunk, 
                'idx': i, 
                'desc': f"Pass 0: Đọc {len(chunk)} phần tử vào RAM"
            })
            
            # 2. SORT: Sắp xếp nội bộ trong RAM [cite: 332, 581]
            sorted_chunk = sorted(chunk)
            steps.append({
                'act': 'SORT', 
                'values': sorted_chunk, 
                'desc': "Sắp xếp nội bộ (Internal Sort) trong Buffer"
            })
            
            # 3. WRITE_RUN: Ghi xuống Output Disk làm Run tạm [cite: 341, 587]
            all_runs.append(sorted_chunk)
            steps.append({
                'act': 'WRITE_RUN', 
                'values': sorted_chunk, 
                'run_idx': len(all_runs) - 1, 
                'desc': f"Ghi Run {len(all_runs)-1} đã sắp xếp xuống OUTPUT DISK"
            })

        # --- GIAI ĐOẠN 2: CÁC PASS MERGE - TRỘN ĐẾN KHI XONG ---
        # Keep merging runs cho đến khi chỉ còn 1 file duy nhất [cite: 256, 509]
        pass_idx = 1
        while len(all_runs) > 1:
            new_runs = []
            # Trộn từng cặp Runs (2-way Merge) [cite: 223, 258]
            for i in range(0, len(all_runs), 2):
                if i + 1 < len(all_runs):
                    r1 = all_runs[i]
                    r2 = all_runs[i+1]
                    
                    # LOAD_FOR_MERGE: Đưa 2 runs từ Disk về RAM để trộn [cite: 118, 135]
                    steps.append({
                        'act': 'LOAD_FOR_MERGE', 
                        'r1_idx': i, 
                        'r2_idx': i+1, 
                        'desc': f"Pass {pass_idx}: Trộn Run {i} và {i+1} bằng Buffer"
                    })
                    
                    # Logic Merge: So sánh Min(A1, B1) [cite: 22, 26]
                    merged = sorted(r1 + r2) # Minh họa logic trộn
                    new_runs.append(merged)
                    
                    # SAVE_MERGED: Ghi kết quả trộn ngược lên Disk [cite: 215, 585]
                    steps.append({
                        'act': 'SAVE_MERGED', 
                        'values': merged, 
                        'desc': f"Ghi kết quả Pass {pass_idx} lên Disk"
                    })
                else:
                    # Nếu lẻ Run thì giữ nguyên cho Pass sau
                    new_runs.append(all_runs[i])
            
            all_runs = new_runs
            pass_idx += 1
            
        return steps
import utils
import math

class ExternalSortEngine:
    def __init__(self, buffer_pages=3):
        # Theo tài liệu, với B+1 trang buffer, ta có thể trộn B đường[cite: 216].
        # Ở đây UI hiển thị 3 trang, vậy B+1 = 3 => B = 2 (Trộn 2 đường).
        self.B_total = buffer_pages 
        self.page_size = 2  # Giả sử mỗi trang chứa 2 bản ghi để dễ quan sát [cite: 32, 38]

    def get_simulation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        steps = []
        io_cost = 0
        N = len(data) # Tổng số phần tử
        
        # --- BƯỚC 0: KHỞI TẠO ---
        steps.append({
            'act': 'INIT_DISK', 'values': data, 'io_cost': 0,
            'desc': "Khởi tạo dữ liệu gốc trên Disk. Mỗi trang chứa 2 bản ghi[cite: 262]."
        })

        # --- PASS 0: TẠO CÁC RUNS BAN ĐẦU ---
        # Sắp xếp B_total trang cùng lúc trong RAM[cite: 595, 596].
        run_size_elements = self.B_total * self.page_size # 3 trang * 2 = 6 phần tử
        all_runs = []
        
        for i in range(0, N, run_size_elements):
            chunk = data[i : i + run_size_elements]
            # Đọc vào RAM: chi phí = số trang đọc [cite: 585]
            pages_read = math.ceil(len(chunk) / self.page_size)
            io_cost += pages_read
            
            steps.append({
                'act': 'READ', 'values': chunk, 'idx': i,
                'io_cost': io_cost, 'desc': f"Pass 0: Nạp {pages_read} trang vào RAM Buffer để tạo Run[cite: 286]."
            })
            
            sorted_chunk = sorted(chunk)
            steps.append({
                'act': 'SORT', 'values': sorted_chunk, 'io_cost': io_cost,
                'desc': "Sắp xếp nội bộ trong RAM (QuickSort/Internal Sort)[cite: 254]."
            })
            
            # Ghi Run xuống Disk: chi phí = số trang ghi [cite: 585]
            all_runs.append(sorted_chunk)
            io_cost += pages_read
            steps.append({
                'act': 'WRITE_RUN', 'values': sorted_chunk, 'run_idx': len(all_runs)-1,
                'io_cost': io_cost, 'desc': f"Ghi Run {len(all_runs)-1} đã sắp xếp xuống Disk[cite: 341]."
            })

        # --- CÁC PASS TRỘN (MERGE PASSES) ---
        pass_num = 1
        while len(all_runs) > 1:
            new_runs = []
            # Trộn B = (B_total - 1) đường. Với 3 trang, ta trộn 2 đường (2-way merge)[cite: 216].
            B_merge = self.B_total - 1 
            
            for i in range(0, len(all_runs), B_merge):
                runs_to_merge = all_runs[i : i + B_merge]
                
                if len(runs_to_merge) > 1:
                    # Logic trộn 2 (hoặc B) danh sách đã sắp xếp [cite: 15, 16]
                    merged_result = self._merge_lists(runs_to_merge)
                    new_runs.append(merged_result)
                    
                    # Chi phí IO cho việc trộn: Đọc toàn bộ các trang của các Run và ghi lại kết quả [cite: 215]
                    total_elements = sum(len(r) for r in runs_to_merge)
                    total_pages = math.ceil(total_elements / self.page_size)
                    io_cost += (2 * total_pages) # 1 lần đọc, 1 lần ghi cho mỗi trang
                    
                    steps.append({
                        'act': 'MERGE_STEP', 
                        'run_indices': list(range(i, i + len(runs_to_merge))),
                        'values': merged_result,
                        'io_cost': io_cost, 
                        'desc': f"Pass {pass_num}: Trộn {len(runs_to_merge)} Runs thành 1 Run lớn hơn[cite: 255, 605]."
                    })
                else:
                    new_runs.append(runs_to_merge[0])
                    steps.append({
                        'act': 'KEEP_RUN', 'run_idx': i, 'io_cost': io_cost,
                        'desc': f"Run {i} không có cặp để trộn, giữ nguyên cho Pass sau[cite: 256]."
                    })
            
            all_runs = new_runs
            pass_num += 1

        steps.append({
            'act': 'FINISH', 'values': all_runs[0] if all_runs else [], 'io_cost': io_cost,
            'desc': f"Hoàn tất sắp xếp! Tổng chi phí: {io_cost} IOs. Công thức: $2N \times (\text{{số pass}})$[cite: 588]."
        })
        return steps

    def _merge_lists(self, lists):
        """Hàm phụ trợ trộn B danh sách đã sắp xếp."""
        import heapq
        return list(heapq.merge(*lists))
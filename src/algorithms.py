import utils
import math

class ExternalSortEngine:
    def __init__(self, buffer_pages=3):
        # UI của bạn có 3 trang RAM, mỗi trang (Page) chứa 1 Run (2 phần tử)
        self.B_total = buffer_pages 
        self.page_size = 2  # 1 Run = 2 phần tử

    def get_simulation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        steps = []
        io_cost = 0
        N = len(data)
        
        # --- BƯỚC 0: TRẠNG THÁI ĐẦU VÀO ---
        steps.append({
            'act': 'INIT_DISK', 
            'values': data, 
            'io_cost': 0, 
            'desc': "Dữ liệu thô được nạp vào vùng Input trên Disk."
        })

        # --- PASS 0: TẠO CÁC RUNS (MỖI RUN 2 SỐ) ---
        all_runs = []
        
        # Đọc tối đa 6 số vào RAM (tương ứng 3 trang RAM)
        for i in range(0, N, 6):
            chunk = data[i : i + 6]
            pages_read = math.ceil(len(chunk) / self.page_size)
            io_cost += pages_read
            
            # Bước 1: Đưa 6 số vào 3 ô RAM
            steps.append({
                'act': 'LOAD_RAM', 
                'values': chunk, 
                'idx': i,
                'io_cost': io_cost, 
                'desc': f"Nạp {len(chunk)} số vào 3 trang RAM Buffer."
            })
            
            # Bước 2: Sắp xếp nội bộ trong RAM
            sorted_chunk = sorted(chunk)
            steps.append({
                'act': 'SORT_RAM', 
                'values': sorted_chunk, 
                'io_cost': io_cost,
                'desc': "Sắp xếp các phần tử trong RAM trước khi chia Run."
            })
            
            # Bước 3: Chia thành các Run (mỗi run 2 số) và đẩy về Disk Buffer F1/F2
            for j in range(0, len(sorted_chunk), 2):
                run = sorted_chunk[j : j + 2]
                all_runs.append(run)
                io_cost += 1 # Ghi 1 trang xuống Disk
                
                # Xác định đích đến: F1 nhận 3 run đầu, F2 nhận 3 run tiếp theo
                target_f = "F1" if len(all_runs) <= 3 else "F2"
                run_idx_in_f = (len(all_runs) - 1) % 3
                
                steps.append({
                    'act': 'WRITE_F_BUFFER', 
                    'values': run, 
                    'target': target_f, 
                    'run_idx': run_idx_in_f,
                    'io_cost': io_cost,
                    'desc': f"Ghi Run [{', '.join(map(str, run))}] vào Disk Buffer {target_f}."
                })

        # --- BƯỚC CUỐI: KẾT THÚC ---
        # (Lưu ý: Logic trộn Merge Pass có thể thêm tương tự nếu muốn mô phỏng dài hơn)
        steps.append({
            'act': 'FINISH', 
            'values': sorted(data), 
            'io_cost': io_cost,
            'desc': f"Hoàn tất tạo Run. Tổng chi phí I/O hiện tại: {io_cost}."
        })
        
        return steps
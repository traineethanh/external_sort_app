import utils
import math

class ExternalSortEngine:
    def __init__(self, buffer_pages=3):
        self.B_total = buffer_pages 
        self.page_size = 2 # Mỗi Run/Page chứa 2 phần tử

    def get_simulation_steps(self, input_file):
        data = utils.read_binary_file(input_file)
        steps = []
        io_cost = 0
        N = len(data)
        
        # --- BƯỚC 0: INIT ---
        steps.append({'act': 'INIT_DISK', 'values': data, 'io_cost': 0, 'desc': "Dữ liệu ban đầu tại vùng Input Disk."})

        # --- PASS 0: TẠO RUNS ---
        all_runs = []
        # Đọc 6 số vào RAM (3 pages * 2)
        for i in range(0, N, 6):
            chunk = data[i:i+6]
            io_cost += math.ceil(len(chunk)/2)
            steps.append({'act': 'LOAD_RAM', 'values': chunk, 'idx': i, 'io_cost': io_cost, 'desc': "Nạp tối đa 6 phần tử vào RAM Buffer."})
            
            sorted_chunk = sorted(chunk)
            steps.append({'act': 'SORT_RAM', 'values': sorted_chunk, 'io_cost': io_cost, 'desc': "Sắp xếp nội bộ 6 phần tử trong RAM."})
            
            # Chia thành các Run 2 phần tử và đẩy vào Disk Buffer F1/F2
            for j in range(0, len(sorted_chunk), 2):
                run = sorted_chunk[j:j+2]
                all_runs.append(run)
                io_cost += 1
                target_f = "F1" if len(all_runs) <= 3 else "F2"
                steps.append({
                    'act': 'WRITE_F_BUFFER', 
                    'values': run, 
                    'target': target_f, 
                    'run_idx': (len(all_runs)-1) % 3,
                    'io_cost': io_cost,
                    'desc': f"Chia Run và đưa vào Disk Buffer {target_f}."
                })

        # --- MERGE PASS (TRỘN TỪ F1, F2 VÀO OUTPUT) ---
        # Ở đây mô phỏng đơn giản hóa việc trộn từ 2 buffer disk qua RAM vào Output
        f1_runs = all_runs[:3]
        f2_runs = all_runs[3:6]
        output_data = []
        
        if len(all_runs) > 1:
            steps.append({'act': 'START_MERGE', 'desc': "Bắt đầu trộn từ F1 và F2 thông qua RAM Buffer."})
            # Mô phỏng lấy từng run từ F1, F2 nạp vào 2 ô đầu RAM
            # Sau đó trộn vào ô thứ 3 của RAM và đẩy xuống Output Disk
            # (Phần này sẽ được minh họa qua act: MERGE_TO_OUTPUT trong main.py)
            final_sorted = sorted(data)
            steps.append({
                'act': 'FINISH', 
                'values': final_sorted, 
                'io_cost': io_cost + (len(data)//2) * 2, 
                'desc': "Hoàn tất trộn. Dữ liệu đã được sắp xếp tại vùng Output."
            })

        return steps
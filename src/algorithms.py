import os
import struct
import utils

class ExternalSort:
    """
    Lớp thực hiện thuật toán External Merge Sort minh họa theo slide bài giảng.
    """
    def __init__(self, buffer_size=3):
        # Mặc định sử dụng 3 Buffer Pages như slide [cite: 18]
        self.buffer_size = buffer_size

    def sort(self, input_file, output_file):
        """
        Quy trình 2 giai đoạn: 
        1. Tạo các runs đã sắp xếp (Pass 0)[cite: 254].
        2. Trộn các runs (Pass 1...n)[cite: 255, 256].
        """
        print(f"--- Bắt đầu sắp xếp ngoại cho {input_file} ---")
        runs = self._create_initial_runs(input_file)
        
        pass_count = 1
        while len(runs) > 1:
            print(f"Pass {pass_count}: Đang trộn {len(runs)} runs...")
            new_runs = []
            for i in range(0, len(runs), 2):
                if i + 1 < len(runs):
                    merged_run = self._merge_two_runs(runs[i], runs[i+1])
                    new_runs.append(merged_run)
                else:
                    new_runs.append(runs[i])
            runs = new_runs
            pass_count += 1
        
        if runs:
            os.rename(runs[0], output_file)
            print(f"Hoàn tất! Kết quả tại: {output_file}")

    def _create_initial_runs(self, input_file):
        """Pass 0: Chia file thành các runs nhỏ có thể chứa vừa trong bộ nhớ[cite: 596]."""
        runs = []
        data = utils.read_binary_file(input_file)
        # Minh họa với kích thước run nhỏ (< 10 phần tử) theo yêu cầu
        run_size = 4 
        
        for i in range(0, len(data), run_size):
            chunk = sorted(data[i:i + run_size])
            run_name = f"run_{len(runs)}.bin"
            utils.write_binary_file(run_name, chunk)
            runs.append(run_name)
            print(f"Tạo run ban đầu: {run_name} với dữ liệu {chunk}")
        return runs

    def _merge_two_runs(self, r1, r2):
        """Trộn 2 runs sử dụng logic so sánh Min(A1, B1)."""
        out_name = f"merged_{r1}_{r2}.bin"
        d1 = utils.read_binary_file(r1)
        d2 = utils.read_binary_file(r2)
        
        merged = []
        i = j = 0
        while i < len(d1) and j < len(d2):
            if d1[i] <= d2[j]:
                merged.append(d1[i])
                i += 1
            else:
                merged.append(d2[j])
                j += 1
        merged.extend(d1[i:])
        merged.extend(d2[j:])
        
        utils.write_binary_file(out_name, merged)
        print(f"  Trộn {r1} + {r2} -> {out_name}: {merged}")
        # Xóa các run tạm sau khi trộn
        os.remove(r1)
        os.remove(r2)
        return out_name
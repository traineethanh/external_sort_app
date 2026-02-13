import time

def merge_sort(data, callback, depth=0):
    """Thuật toán Merge Sort có minh họa phân cấp theo độ sâu đệ quy."""
    if len(data) <= 1:
        return data

    mid = len(data) // 2
    
    # Minh họa bước CHIA
    callback(data, f"{'  ' * depth}➡ CHIA {data[:mid]} | {data[mid:]}")
    
    left = merge_sort(data[:mid], callback, depth + 1)
    right = merge_sort(data[mid:], callback, depth + 1)

    result = _merge(left, right)
    
    # Minh họa bước TRỘN
    callback(result, f"{'  ' * depth}⬅ TRỘN XONG")
    return result

def _merge(left, right):
    """Trộn hai mảng con đã sắp xếp."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
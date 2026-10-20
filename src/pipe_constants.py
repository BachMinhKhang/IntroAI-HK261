"""
pipe_constants.py
Định nghĩa hệ thống Bitmask và các phép toán hình học cho Puzzle Pipes.

Bitmask 4 hướng:
  Bit 0: NORTH (1) - Lên
  Bit 1: EAST  (2) - Phải
  Bit 2: SOUTH (4) - Xuống
  Bit 3: WEST  (8) - Trái
"""

# Hướng cổng nối
NORTH = 1  # 0001
EAST  = 2  # 0010
SOUTH = 4  # 0100
WEST  = 8  # 1000

DIRECTIONS = [NORTH, EAST, SOUTH, WEST]

# Tọa độ dịch chuyển theo hướng (dr, dc)
DELTAS = {
    NORTH: (-1, 0),
    EAST:  (0, 1),
    SOUTH: (1, 0),
    WEST:  (0, -1)
}

# Cổng đối diện tương ứng
OPPOSITE = {
    NORTH: SOUTH,
    EAST:  WEST,
    SOUTH: NORTH,
    WEST:  EAST
}

def rotate_cw(mask: int, times: int = 1) -> int:
    """Xoay bitmask theo chiều kim đồng hồ 'times' lần 90 độ."""
    times = times % 4
    for _ in range(times):
        mask = ((mask << 1) & 0b1111) | (mask >> 3)
    return mask

def get_possible_rotations(mask: int) -> list[int]:
    """
    Trả về danh sách tất cả các cấu hình xoay duy nhất của một mảnh ống.
    - End, Turn, Tee: 4 cấu hình
    - Straight: 2 cấu hình
    - Cross, Blank: 1 cấu hình
    """
    rotations = []
    current = mask
    for _ in range(4):
        if current not in rotations:
            rotations.append(current)
        current = rotate_cw(current, 1)
    return rotations

# Phân loại hình dạng ống dựa trên số lượng cổng nối
def get_shape_type(mask: int) -> str:
    count = bin(mask & 0b1111).count('1')
    if count == 0:
        return 'BLANK'
    elif count == 1:
        return 'END'
    elif count == 2:
        if mask in (NORTH | SOUTH, EAST | WEST):
            return 'STRAIGHT'
        return 'TURN'
    elif count == 3:
        return 'TEE'
    elif count == 4:
        return 'CROSS'
    return 'UNKNOWN'


"""
pipe_constants.py
Defines the bitmask direction system and geometric utilities for Puzzle Pipes.

4-bit directional mask:
  Bit 0: NORTH (1) - Up
  Bit 1: EAST  (2) - Right
  Bit 2: SOUTH (4) - Down
  Bit 3: WEST  (8) - Left
"""

# Connection ports
NORTH = 1  # 0001
EAST  = 2  # 0010
SOUTH = 4  # 0100
WEST  = 8  # 1000

DIRECTIONS = [NORTH, EAST, SOUTH, WEST]

# Coordinate deltas for each direction (dr, dc)
DELTAS = {
    NORTH: (-1, 0),
    EAST:  (0, 1),
    SOUTH: (1, 0),
    WEST:  (0, -1)
}

# Matching opposite ports
OPPOSITE = {
    NORTH: SOUTH,
    EAST:  WEST,
    SOUTH: NORTH,
    WEST:  EAST
}

def rotate_cw(mask: int, times: int = 1) -> int:
    """Rotates a bitmask clockwise by 90 degrees 'times' times."""
    times = times % 4
    for _ in range(times):
        mask = ((mask << 1) & 0b1111) | (mask >> 3)
    return mask

def get_possible_rotations(mask: int) -> list[int]:
    """
    Returns a list of all unique rotation orientations for a pipe piece.
    - End, Turn, Tee: 4 configurations
    - Straight: 2 configurations
    - Cross, Blank: 1 configuration
    """
    rotations = []
    current = mask
    for _ in range(4):
        if current not in rotations:
            rotations.append(current)
        current = rotate_cw(current, 1)
    return rotations

def get_shape_type(mask: int) -> str:
    """Classifies pipe shape based on the number of active connection ports."""
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

#!/usr/bin/env python

import numpy as np
import sys


if len(sys.argv) != 2:
    print("Please specify a .mem file as an argument. Use the following command to make one:")
    print()
    print("    opbasm -6i <filename>.asm")
    exit(1)


instructions = []
with open(sys.argv[1]) as f:
    for line in f:
        if not line.startswith('@'):
            instructions.append(int(line, 16))


if len(instructions) > 1024:
    if any(instructions[1025:]):
        print("Warning: MEM file is longer than 1024 instructions; truncating to 1024 instructions", file=sys.stderr)
    instructions = instructions[:1024]


instructions = np.array(instructions, dtype=np.uint32)


CELL_SYMBOLS = '.ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def rle_row(cell_row):
    next_cell, last_cell = None, None
    count = 0
    arr_iter = iter(cell_row)
    result = ''
    done = False
    while not done:
        try:
            next_cell = next(arr_iter)
        except StopIteration:
            next_cell = None
            done = True
        if next_cell == last_cell:
            count += 1
        else:
            if last_cell is not None:
                if count > 1:
                    result += str(count)
                result += CELL_SYMBOLS[last_cell]
            last_cell = next_cell
            count = 1
    return result


def rle(cell_array):
    s = f'x = {cell_array.shape[1]}, y = {cell_array.shape[0]}, rule = DECA\n'
    line_endings = 0
    for cell_row in cell_array:
        trimmed_row = np.trim_zeros(cell_row, 'b')
        if trimmed_row.size:
            if line_endings:
                if line_endings > 1:
                    s += str(line_endings)
                s += '$'
            s += rle_row(trimmed_row)
            line_endings = 1
        else:
            line_endings += 1
    s += '!'
    return s


LOOP_COORDS = np.array(
    []
    + [(0, n) for n in range(35)]
    + [(1, 34)]
    + [(2, n) for n in reversed(range(35))]
    + [(1, 0)]
)

X_COUNT = 16
Y_COUNT = 64
X0 = 21
Y0 = 0
T0 = 40
DX = 40
DY = 6
ALIGNMENT_PATTERN = np.array([[0, 6, 0], [6, 6, 6], [0, 6, 0]], dtype=np.byte)

rom_pattern = np.zeros((Y0 + DY * Y_COUNT, X0 + DX * X_COUNT), dtype=np.byte)
w, h = ALIGNMENT_PATTERN.shape
rom_pattern[:h, :w] = ALIGNMENT_PATTERN


def make_instruction_pattern(instruction, time_offset):
    cells = np.zeros((DY, DX))
    for i in range(18):
        # Little-endian
        if instruction & (1 << i):
            space_offset_1 = (4 * i + time_offset) % len(LOOP_COORDS)
            space_offset_2 = space_offset_1 + 1
            space_offset_1 %= len(LOOP_COORDS)
            space_offset_2 %= len(LOOP_COORDS)
            coords = LOOP_COORDS[[space_offset_1, space_offset_2]]
            cells[tuple(coords.T)] = [1, 2]
    return cells


print("Creating pattern ...")
instr_index = 0
for x in range(X0, X0 + DX * X_COUNT, DX):
    for y in range(Y0, Y0 + DY * Y_COUNT, DY):
        instr_pattern = make_instruction_pattern(instructions[instr_index], T0 + x - y)
        rom_pattern[y:y + DY, x:x + DX] = instr_pattern
        instr_index += 1

print("Encoding RLE ...")
rom_rle = rle(rom_pattern)

print()
print(rom_rle)
print()
print("Done!")

try:
    import clipboard
    clipboard.copy(rom_rle)
except ImportError:
    pass

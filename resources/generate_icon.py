"""
Script tạo icon.png cho ứng dụng Calculator.
Vẽ icon bằng Pillow hoặc nếu không có thì tạo file PNG đơn giản thủ công.

Chạy: python resources/generate_icon.py
"""

import os
import struct
import zlib
from pathlib import Path


def create_png_icon(filepath: str, size: int = 128) -> None:
    """Tạo file PNG icon đơn giản bằng cách viết binary trực tiếp.
    
    Không cần Pillow - dùng zlib để tạo PNG hợp lệ.
    Icon là hình tròn màu xanh #0A84FF với ký tự "=" trắng.
    """
    # Tạo pixel data: hình vuông size×size
    # Pixel format: RGBA (4 bytes per pixel)
    
    pixels = []
    cx, cy = size // 2, size // 2
    r = size // 2 - 4  # Bán kính hình tròn
    
    for y in range(size):
        row = []
        for x in range(size):
            # Tính khoảng cách đến tâm
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            
            if dist <= r:
                # Màu nền: xanh #0A84FF
                row.extend([0x0A, 0x84, 0xFF, 0xFF])  # R, G, B, A
            else:
                # Transparent
                row.extend([0, 0, 0, 0])
        pixels.append(row)
    
    # Vẽ dấu "=" trắng ở giữa
    bar_height = max(3, size // 16)
    bar_width = size // 2
    bar_x = cx - bar_width // 2
    
    # Thanh trên của "="
    y1 = cy - bar_height * 2
    # Thanh dưới của "="
    y2 = cy + bar_height
    
    for y_bar in [y1, y2]:
        for dy in range(bar_height):
            for dx in range(bar_width):
                x = bar_x + dx
                y = y_bar + dy
                if 0 <= y < size and 0 <= x < size:
                    idx = x * 4
                    pixels[y][idx:idx+4] = [0xFF, 0xFF, 0xFF, 0xFF]
    
    # Encode PNG
    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        length = struct.pack(">I", len(data))
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return length + chunk_type + data + struct.pack(">I", crc)
    
    # PNG header
    png_header = b"\x89PNG\r\n\x1a\n"
    
    # IHDR chunk
    ihdr_data = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    ihdr = make_chunk(b"IHDR", ihdr_data)
    
    # IDAT chunk (pixel data)
    raw_data = b""
    for row in pixels:
        raw_data += b"\x00"  # Filter type: None
        raw_data += bytes(row)
    
    compressed = zlib.compress(raw_data, 9)
    idat = make_chunk(b"IDAT", compressed)
    
    # IEND chunk
    iend = make_chunk(b"IEND", b"")
    
    # Write file
    with open(filepath, "wb") as f:
        f.write(png_header + ihdr + idat + iend)
    
    print(f"Icon created: {filepath} ({size}x{size} px)")


if __name__ == "__main__":
    output_dir = Path(__file__).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    create_png_icon(str(output_dir / "icon.png"), size=128)

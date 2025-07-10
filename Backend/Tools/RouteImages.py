import struct
import os
import sys
from PIL import Image
import numpy as np

# Pokéwalker 4-color palette (matching pw-image-tools)
POKEWALKER_PALETTE = [
    (255, 255, 255),  # White (00)
    (168, 168, 168),  # Dark Gray (01) 
    (80, 80, 80),     # Light Gray (10)
    (0, 0, 0)         # Black (11)
]

def get_desktop_path():
    # Prefer OneDrive Desktop if it exists
    home = os.path.expanduser('~')
    onedrive_desktop = os.path.join(home, 'OneDrive', 'Desktop')
    if os.path.exists(onedrive_desktop):
        return onedrive_desktop
    # Fallback to default Desktop
    return os.path.join(home, 'Desktop')

def analyze_bin_file(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    file_size = len(data)
    num_words = file_size // 2
    possible_dimensions = []
    common_widths = [32, 24, 16, 48, 64, 96, 128]
    for width in common_widths:
        if num_words % width == 0:
            height = (num_words // width) * 8
            possible_dimensions.append((width, height))
    return possible_dimensions

def decode_route_image_row_major(bin_data, width, height):
    num_words = len(bin_data) // 2
    words = struct.unpack(f'>{num_words}H', bin_data)
    image_data = np.zeros((height, width), dtype=np.uint8)
    word_index = 0
    for row in range(0, height, 8):
        for col in range(width):
            if word_index >= len(words):
                break
            word = words[word_index]
            for row_offset in range(8):
                if row + row_offset >= height:
                    break
                pixel_bits = (word >> row_offset) & 0x0101
                if pixel_bits == 0x000:
                    palette_index = 0
                elif pixel_bits == 0x001:
                    palette_index = 1
                elif pixel_bits == 0x100:
                    palette_index = 2
                elif pixel_bits == 0x101:
                    palette_index = 3
                else:
                    palette_index = 0
                image_data[row + row_offset, col] = palette_index
            word_index += 1
    return image_data

def create_palette_image(image_data, output_path):
    height, width = image_data.shape
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            palette_index = image_data[y, x]
            if palette_index < len(POKEWALKER_PALETTE):
                rgb_image[y, x] = POKEWALKER_PALETTE[palette_index]
    image = Image.fromarray(rgb_image, 'RGB')
    image.save(output_path)
    print(f"Saved: {output_path}")

def quantize_to_pokewalker_palette(img):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    arr = np.array(img)
    quantized = np.zeros((arr.shape[0], arr.shape[1]), dtype=np.uint8)
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            pixel = arr[y, x]
            dists = [np.sum((pixel - np.array(c)) ** 2) for c in POKEWALKER_PALETTE]
            quantized[y, x] = int(np.argmin(dists))
    return quantized

def encode_image_to_bin(image_path, output_path=None):
    img = Image.open(image_path)
    quantized = quantize_to_pokewalker_palette(img)
    height, width = quantized.shape
    if height % 8 != 0:
        raise ValueError(f"Image height must be a multiple of 8 (got {height})")
    words = []
    for row in range(0, height, 8):
        for col in range(width):
            word = 0
            for row_offset in range(8):
                palette_index = quantized[row + row_offset, col]
                if palette_index == 0:
                    bits = 0x000
                elif palette_index == 1:
                    bits = 0x001
                elif palette_index == 2:
                    bits = 0x100
                elif palette_index == 3:
                    bits = 0x101
                else:
                    bits = 0x000
                word |= (bits & 0x0101) << row_offset
            words.append(word)
    bin_data = b''.join(struct.pack('>H', w) for w in words)
    if output_path is None:
        base, _ = os.path.splitext(os.path.basename(image_path))
        output_path = os.path.join(get_desktop_path(), f"{base}.bin")
    with open(output_path, 'wb') as f:
        f.write(bin_data)
    print(f"Saved: {output_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python RouteImages.py <route_file.bin|image.png|image.jpg>")
        sys.exit(1)
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found")
        sys.exit(1)
    ext = os.path.splitext(input_file)[1].lower()
    desktop = get_desktop_path()
    if ext == '.bin':
        print(f"Analyzing: {input_file}")
        possible_dimensions = analyze_bin_file(input_file)
        if not possible_dimensions:
            print("No valid dimensions found. Trying common dimensions...")
            possible_dimensions = [(32, 24), (24, 32), (16, 48)]
        with open(input_file, 'rb') as f:
            bin_data = f.read()
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        # Only use the first valid dimension (most likely correct)
        width, height = possible_dimensions[0]
        print(f"Converting using dimensions: {width}x{height}")
        image_data = decode_route_image_row_major(bin_data, width, height)
        output_path = os.path.join(desktop, f"{base_name}.png")
        create_palette_image(image_data, output_path)
        print(f"\nDone! Check your Desktop for the output image.")
    elif ext in ['.png', '.jpg', '.jpeg']:
        try:
            encode_image_to_bin(input_file)
            print(f"\nDone! Check your Desktop for the output .bin file.")
        except Exception as e:
            print(f"Error encoding image: {e}")
    else:
        print(f"Unsupported file type: {ext}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
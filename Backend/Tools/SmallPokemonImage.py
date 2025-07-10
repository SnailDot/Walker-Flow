import sys
import os
from PIL import Image
import numpy as np

# Pokéwalker 4-color palette
POKEWALKER_PALETTE = [
    (0, 0, 0),      # #000000 - Black
    (64, 64, 64),   # #404040 - Dark Gray
    (128, 128, 128), # #808080 - Light Gray
    (255, 255, 255)  # #FFFFFF - White
]

def analyze_bin_file(file_path):
    """Analyze binary file and suggest possible dimensions"""
    with open(file_path, 'rb') as f:
        data = f.read()
    
    print(f"=== Analysis of {file_path} ===")
    print(f"File size: {len(data)} bytes")
    
    # Show first few bytes
    print(f"First 16 bytes: {data[:16].hex()}")
    
    # Calculate possible dimensions for 1-bit per pixel
    total_pixels = len(data) * 8  # 8 pixels per byte
    print(f"\n1-bit per pixel: {total_pixels} pixels")
    
    # Common small sprite dimensions
    common_widths = [16, 24, 32, 48, 64, 96, 128]
    possible_dimensions = []
    
    for width in common_widths:
        if total_pixels % width == 0:
            height = total_pixels // width
            if height > 0 and height <= 768:  # Reasonable height limit
                possible_dimensions.append((width, height))
                print(f"  {width}x{height} pixels")
    
    return data, possible_dimensions

def convert_1bit_with_inversion(data, width, height):
    """Convert using 1-bit per pixel with bit inversion (like the working script)"""
    # Invert all bits (like the working script)
    inverted_data = bytes([b ^ 0b11111111 for b in data])
    
    # Create 1-bit image
    img = Image.frombytes('1', (width, height), inverted_data)
    
    return img

def unslice_image(img, animated=True):
    """Unslice the image into the final sprite format (like the working script)"""
    if img is None:
        return img

    # Convert to grayscale
    img = img.convert('L')

    # Split into left and right chunks (8x64 each)
    lchunks = [img.crop((0, img.height-((i+1)*64), 8, img.height-(i*64))) for i in range(0, 12 if animated else 6)]
    rchunks = [img.crop((8, img.height-((i+1)*64), 16, img.height-(i*64))) for i in range(0, 12 if animated else 6)]
    
    # Create output image
    out_img = Image.new('L', (48*2, 64))

    # Blend left and right chunks
    for i in range(0, 12 if animated else 6):
        out_img.paste(Image.blend(lchunks[i], rchunks[i], 2/3), (i*8, 0))
    
    # Rotate 90 degrees
    return out_img.transpose(Image.ROTATE_90)

def convert_to_pokewalker_palette(img):
    """Convert grayscale image to Pokéwalker 4-color palette"""
    # Convert to numpy array
    arr = np.array(img)
    
    # Create quantized image
    quantized = np.zeros(arr.shape, dtype=np.uint8)
    
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            pixel = arr[y, x]
            # Map grayscale to Pokéwalker palette
            if pixel < 64:
                quantized[y, x] = 0  # Black
            elif pixel < 128:
                quantized[y, x] = 1  # Dark Gray
            elif pixel < 192:
                quantized[y, x] = 2  # Light Gray
            else:
                quantized[y, x] = 3  # White
    
    # Convert back to PIL image with Pokéwalker palette
    palette_img = Image.fromarray(quantized, mode='P')
    
    # Set the Pokéwalker palette
    palette_data = []
    for color in POKEWALKER_PALETTE:
        palette_data.extend(color)
    palette_img.putpalette(palette_data)
    
    return palette_img

def get_desktop_path():
    """Get the correct desktop path, checking for OneDrive first"""
    # Check for OneDrive desktop
    onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    if os.path.exists(onedrive_desktop):
        return onedrive_desktop
    
    # Fall back to default desktop
    return os.path.join(os.path.expanduser("~"), "Desktop")

def main():
    if len(sys.argv) != 2:
        print("Usage: python SmallPokemonImage.py <sprite_file.bin>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found")
        sys.exit(1)
    
    # Analyze the binary file
    data, possible_dimensions = analyze_bin_file(input_file)
    
    if not possible_dimensions:
        print("No valid dimensions found. Using 16x768 as default.")
        possible_dimensions = [(16, 768)]
    
    # Test each dimension
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    desktop_path = get_desktop_path()
    
    for width, height in possible_dimensions[:3]:  # Test first 3 dimensions
        print(f"\n=== Testing dimensions {width}x{height} ===")
        
        try:
            # Convert using the working method
            img = convert_1bit_with_inversion(data, width, height)
            
            # Apply unslice operation (only for 16x768)
            if width == 16 and height == 768:
                print("Applying unslice operation...")
                img = unslice_image(img)
                output_path = os.path.join(desktop_path, f"{base_name}_unslice_{width}x{height}.png")
            else:
                # For other dimensions, just convert to Pokéwalker palette
                img = convert_to_pokewalker_palette(img)
                output_path = os.path.join(desktop_path, f"{base_name}_{width}x{height}.png")
            
            # Save the image
            img.save(output_path)
            print(f"Saved: {output_path}")
            
        except Exception as e:
            print(f"Error with {width}x{height}: {e}")
    
    print(f"\n=== Conversion Complete ===")
    print("Check your Desktop for the converted images!")

if __name__ == "__main__":
    main() 
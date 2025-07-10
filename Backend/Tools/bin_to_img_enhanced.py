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

# ============================================================================
# BINARY TO IMAGE FUNCTIONS
# ============================================================================

def bin_to_img(in_bin):
    """Convert binary data to image with size validation"""
    expected_size = 16 * 768 // 4  # 3072 bytes for 16x768 2-bit image (4 colors)
    actual_size = len(in_bin)
    
    print(f"Expected size: {expected_size} bytes")
    print(f"Actual size: {actual_size} bytes")
    
    if actual_size != expected_size:
        print(f"WARNING: Size mismatch! Expected {expected_size} bytes, got {actual_size} bytes")
        
        # If file is too small, pad with zeros
        if actual_size < expected_size:
            print(f"Padding with {expected_size - actual_size} zero bytes")
            in_bin = in_bin + b'\x00' * (expected_size - actual_size)
        # If file is too large, truncate
        elif actual_size > expected_size:
            print(f"Truncating to {expected_size} bytes")
            in_bin = in_bin[:expected_size]
    
    # Convert binary data to 2-bit pixel values
    # Each byte contains 4 pixels (2 bits each)
    pixels = []
    for byte in in_bin:
        # Extract 4 pixels from each byte
        pixel1 = (byte >> 6) & 0b11  # Bits 7-6
        pixel2 = (byte >> 4) & 0b11  # Bits 5-4
        pixel3 = (byte >> 2) & 0b11  # Bits 3-2
        pixel4 = byte & 0b11         # Bits 1-0
        pixels.extend([pixel1, pixel2, pixel3, pixel4])
    
    # Create image from pixel data
    img_array = np.array(pixels, dtype=np.uint8).reshape(768, 16)
    
    # Convert to PIL Image
    img = Image.fromarray(img_array, mode='P')
    
    # Set the Pokéwalker palette
    palette_data = []
    for color in POKEWALKER_PALETTE:
        palette_data.extend(color)
    img.putpalette(palette_data)
    
    return img

def unslice_image(in_img):
    """Unslice the image into the final sprite format"""
    if in_img is None:
        return in_img

    animated = True
    
    # Convert to RGB for processing
    if in_img.mode != 'RGB':
        in_img = in_img.convert('RGB')

    lchunks = [in_img.crop((0, in_img.height-((i+1)*64), 8, in_img.height-(i*64))) for i in range(0, 12 if animated else 6)]
    rchunks = [in_img.crop((8, in_img.height-((i+1)*64), 16, in_img.height-(i*64))) for i in range(0, 12 if animated else 6)]
    
    out_img = Image.new('RGB', (48*2, 64))

    for i in range(0, 12 if animated else 6):
        # Use the left chunk directly (no blending to preserve information)
        out_img.paste(lchunks[i], (i*8, 0))
    
    # Apply rotation to match Pokéwalker sprite orientation
    # This ensures the sprite appears correctly oriented when viewed
    return out_img.transpose(Image.ROTATE_90)

def analyze_bin_file(filepath):
    """Analyze binary file and provide diagnostics"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"\n=== Analysis of {filepath} ===")
    print(f"File size: {len(data)} bytes")
    print(f"Expected size: {16 * 768 // 4} bytes (4-color palette)")
    
    # Show first and last 16 bytes
    print(f"First 16 bytes: {data[:16].hex()}")
    print(f"Last 16 bytes: {data[-16:].hex()}")
    
    # Count non-zero bytes
    non_zero = sum(1 for b in data if b != 0)
    print(f"Non-zero bytes: {non_zero}/{len(data)} ({non_zero/len(data)*100:.1f}%)")
    
    return data

def convert_bin_to_image(input_filepath, output_filepath=None):
    """Convert binary file to image and return the image object"""
    # Analyze the file first
    data = analyze_bin_file(input_filepath)
    
    # Convert to image
    try:
        img = bin_to_img(data)
        final_img = unslice_image(img)
        
        # Save the image if output path is provided
        if output_filepath:
            final_img.save(output_filepath)
            print(f"\nSuccessfully converted {input_filepath} to image!")
            print(f"Saved as: {output_filepath}")
        
        return final_img
        
    except Exception as e:
        print(f"\nError converting file: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_desktop_path():
    """Get the correct desktop path, checking for OneDrive first"""
    # Check for OneDrive desktop
    onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    if os.path.exists(onedrive_desktop):
        return onedrive_desktop
    
    # Fall back to default desktop
    return os.path.join(os.path.expanduser("~"), "Desktop")

# ============================================================================
# IMAGE TO BINARY FUNCTIONS
# ============================================================================

def quantize_to_pokewalker_palette(img):
    """Quantize image to Pokéwalker's 4-color palette"""
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Create a new image with the Pokéwalker palette
    quantized_img = Image.new('P', img.size)
    
    # Set the Pokéwalker palette
    palette_data = []
    for color in POKEWALKER_PALETTE:
        palette_data.extend(color)
    quantized_img.putpalette(palette_data)
    
    # Convert to numpy array for processing
    img_array = np.array(img)
    quantized_array = np.zeros(img.size[::-1], dtype=np.uint8)  # height, width
    
    for y in range(img_array.shape[0]):
        for x in range(img_array.shape[1]):
            pixel = img_array[y, x]
            
            # Find closest color in Pokéwalker palette
            min_distance = float('inf')
            best_color_index = 0
            
            for i, palette_color in enumerate(POKEWALKER_PALETTE):
                # Calculate Euclidean distance
                distance = np.sqrt(np.sum((pixel - palette_color) ** 2))
                if distance < min_distance:
                    min_distance = distance
                    best_color_index = i
            
            quantized_array[y, x] = best_color_index  # Store palette index, not RGB
    
    # Create final image with palette indices
    quantized_img = Image.fromarray(quantized_array, mode='P')
    quantized_img.putpalette(palette_data)
    
    return quantized_img

def img_to_bin(img):
    """Convert image back to binary data with 4-color palette"""
    # Quantize to Pokéwalker palette
    quantized_img = quantize_to_pokewalker_palette(img)
    
    # Convert to numpy array - get palette indices (0-3)
    img_array = np.array(quantized_img)
    
    # Flatten the array
    pixels = img_array.flatten()
    
    # Convert pixels to binary data
    # Each byte contains 4 pixels (2 bits each)
    binary_data = bytearray()
    
    for i in range(0, len(pixels), 4):
        # Get 4 pixels (palette indices 0-3)
        pixel1 = pixels[i] if i < len(pixels) else 0
        pixel2 = pixels[i + 1] if i + 1 < len(pixels) else 0
        pixel3 = pixels[i + 2] if i + 2 < len(pixels) else 0
        pixel4 = pixels[i + 3] if i + 3 < len(pixels) else 0
        
        # Pack into one byte
        byte = (pixel1 << 6) | (pixel2 << 4) | (pixel3 << 2) | pixel4
        binary_data.append(byte)
    
    return bytes(binary_data)

def slice_image_for_bin(img):
    """Slice the image back to the format expected by the bin file"""
    if img is None:
        return img
    
    # Convert to RGB for processing
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Get dimensions
    width, height = img.size
    
    # Check if the image is already in the correct orientation (64x96)
    # This is the typical orientation for Pokéwalker sprites after rotation
    if width == 64 and height == 96:
        # Image is already in the correct orientation, reverse the rotation
        print("Image is in Pokéwalker orientation (64x96), reversing rotation")
        img = img.transpose(Image.ROTATE_270)  # Reverse the ROTATE_90 from unslice
    elif width == 96 and height == 64:
        # Image is in the expected processing format
        print("Image is in processing format (96x64)")
    else:
        # Resize to expected size
        print(f"Resizing image from {width}x{height} to (96, 64)")
        img = img.resize((96, 64), Image.Resampling.LANCZOS)
    
    # Create the 16x768 image
    output_img = Image.new('RGB', (16, 768))
    
    # Extract chunks from the image and place them back in the original positions
    for i in range(12):
        # Extract the chunk from the image
        chunk = img.crop((i*8, 0, (i+1)*8, 64))
        
        # Calculate the position in the original 16x768 image
        y_start = 768 - ((i+1)*64)
        y_end = 768 - (i*64)
        
        # Place the chunk on the left side (0-8)
        output_img.paste(chunk, (0, y_start))
        # Place the chunk on the right side (8-16)
        output_img.paste(chunk, (8, y_start))
    
    return output_img

def analyze_image(filepath):
    """Analyze image file and provide diagnostics"""
    try:
        img = Image.open(filepath)
        print(f"\n=== Analysis of {filepath} ===")
        print(f"Image size: {img.size}")
        print(f"Image mode: {img.mode}")
        print(f"Expected size: 96x64 (after unslice process)")
        print(f"Color support: 4-color Pokéwalker palette")
        
        # Check if it's close to expected size
        width, height = img.size
        if width == 96 and height == 64:
            print("✓ Image is the correct size")
        else:
            print(f"⚠ Image size differs from expected (96x64)")
        
        return img
    except Exception as e:
        print(f"Error opening image: {e}")
        return None

def save_bin_file(data, output_path):
    """Save binary data to a .bin file"""
    try:
        with open(output_path, 'wb') as f:
            f.write(data)
        print(f"✓ Saved binary file: {output_path}")
        print(f"  Size: {len(data)} bytes")
        return True
    except Exception as e:
        print(f"Error saving binary file: {e}")
        return False

def convert_image_to_bin(input_filepath, output_filepath=None):
    """Convert image file to binary and return the binary data"""
    if not os.path.exists(input_filepath):
        print(f"Error: File '{input_filepath}' does not exist")
        return None
    
    # Analyze the image
    img = analyze_image(input_filepath)
    if img is None:
        return None
    
    try:
        # Slice the image back to the bin format
        print("\nConverting image to bin format...")
        sliced_img = slice_image_for_bin(img)
        
        if sliced_img is None:
            print("Error: Failed to slice image")
            return None
        
        # Convert to binary data
        binary_data = img_to_bin(sliced_img)
        
        # Save the binary file if output path is provided
        if output_filepath:
            if save_bin_file(binary_data, output_filepath):
                print(f"\nSuccessfully converted {input_filepath} to binary format!")
                print(f"Output file: {output_filepath}")
                
                # Verify the size
                expected_size = 16 * 768 // 4  # 3072 bytes for 4-color palette
                actual_size = len(binary_data)
                if actual_size == expected_size:
                    print(f"✓ Binary file size is correct: {actual_size} bytes")
                else:
                    print(f"⚠ Binary file size mismatch: {actual_size} bytes (expected {expected_size})")
            else:
                print("Failed to save binary file")
                return None
        
        return binary_data
        
    except Exception as e:
        print(f"\nError converting image: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Correct syntax: bin_to_img_enhanced.py in-file")
        print("Supports both .bin→.png and .png/.jpg→.bin conversion")
        sys.exit()
    
    filepath = sys.argv[1]
    file_extension = os.path.splitext(filepath)[1].lower()
    
    # Get desktop path (checking for OneDrive first)
    desktop_path = get_desktop_path()
    
    if file_extension == '.bin':
        # Convert binary to image
        output_filename = os.path.splitext(os.path.basename(filepath))[0] + ".png"
        output_filepath = os.path.join(desktop_path, output_filename)
        
        # Convert the file
        final_img = convert_bin_to_image(filepath, output_filepath)
        
        if final_img:
            # Try to show the image, but don't fail if it doesn't work
            try:
                final_img.show()
            except Exception as show_error:
                print(f"Note: Could not display image automatically: {show_error}")
                print(f"Image saved as {output_filepath} - you can open it manually.")
        else:
            sys.exit(1)
    
    elif file_extension in ['.png', '.jpg', '.jpeg']:
        # Convert image to binary
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        output_path = os.path.join(desktop_path, f"{base_name}.bin")
        
        # Convert the image
        binary_data = convert_image_to_bin(filepath, output_path)
        
        if binary_data is None:
            sys.exit(1)
    
    else:
        print(f"Unsupported file type: {file_extension}")
        print("Supported types: .bin, .png, .jpg, .jpeg")
        sys.exit(1) 
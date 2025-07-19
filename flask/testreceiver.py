import requests
import base64
BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
def decode_and_unpack(b64_data, frames, width, height):
    # --- Base64 Decode ---
    b64_data = b64_data.rstrip("=")
    padding = len(b64_data) % 4
    if padding:
        b64_data += "A" * (4 - padding)
    decoded = bytearray()
    for i in range(0, len(b64_data), 4):
        n = (
            (BASE64_ALPHABET.index(b64_data[i]) << 18) +
            (BASE64_ALPHABET.index(b64_data[i+1]) << 12) +
            (BASE64_ALPHABET.index(b64_data[i+2]) << 6) +
            (BASE64_ALPHABET.index(b64_data[i+3]))
        )
        decoded.append((n >> 16) & 0xFF)
        decoded.append((n >> 8) & 0xFF)
        decoded.append(n & 0xFF)
    print('hello')
    # --- Unpack Frames ---
    data = bytes(decoded).rstrip(b'\x00')
    assert len(data) == frames * width * height * 3, "Byte length mismatch"
    
    output_frames = []
    idx = 0
    for _ in range(frames):
        unpacked_data = []
        for _ in range(height):
            row = []
            for _ in range(width):
                r = data[idx]
                g = data[idx + 1]
                b = data[idx + 2]
                row.append((r, g, b))
                idx += 3
            unpacked_data.append(row)
        output_frames.append(unpacked_data)

    return output_frames

JSON_URL = "http://192.168.68.133:5000/processed-image"

with open('compress.txt', 'r') as file:
    enc_colors = file.read()
print(enc_colors)
b64_colors = base64.b64encode(eval(enc_colors)).decode('utf-8')
colors = decode_and_unpack(b64_colors, frames=30, width=8, height=10)
with open('output.txt', 'w') as file:
    file.write(str( colors))
    file.close()
print(colors)
print('done')
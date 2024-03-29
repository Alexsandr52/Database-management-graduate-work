from PIL import Image
import io

# Кодирует изображение из файла в байтовую строку.
def encode_image_to_bytes(image_path):
    with open(image_path, 'rb') as img_file:
        img_bytes = img_file.read()
    return img_bytes

# Декодирует байтовую строку в изображение.
def decode_bytes_to_image(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    return img


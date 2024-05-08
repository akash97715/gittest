from PIL import Image, ImageFile

# Option 1: Increase the maximum image size to avoid the DecompressionBomb error
Image.MAX_IMAGE_PIXELS = None  # This removes the limit entirely. Use with caution.

# Option 2: Safely load the image, handle DecompressionBomb error
try:
    image = Image.open('path_to_your_large_image.jpg')
    image.load()  # This is where the error might be triggered
except Image.DecompressionBombError:
    print("Image too large and risky to load, skipping...")
    # Here, you can decide to skip this image or apply other logic

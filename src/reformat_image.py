from PIL import Image
import os
import pathlib
import numpy as np

from io import BytesIO

def resize_image(image_bytes, new_size: tuple = (4320, 5400), crop_margin=6):
    # Suppose image_bytes contains your raw bytes (from base64 or download)
    image = Image.open(BytesIO(image_bytes))
    width, height = image.size
    top, left = crop_margin, crop_margin

    bottom = height - crop_margin
    right = width - crop_margin

    image = np.array(image)

    image = image[top:bottom, left:right]

    image = Image.fromarray(image)
    return image.resize(new_size)

def main():
    images = os.listdir("image_outputs")

    for i in range(len(images)):
        try:
            ext = images[i][-3:]
            os.rename(pathlib.Path(f"image_outputs/{images[i]}"), f"image_outputs/summer_trend{i+45}.{ext}")
        except Exception:
            pass

    images = os.listdir("image_outputs")

    for i in range(len(images)):
        print(f"Resizing: {images[i]}")
        resized_image = Image.open(pathlib.Path(f"image_outputs/{images[i]}"))

        resized_image = resize_image(resized_image)

        resized_image.save(pathlib.Path(f"image_outputs/{images[i]}"), dpi=(300, 300))

if __name__ == "__main__":
    main()
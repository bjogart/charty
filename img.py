from PIL import Image
import numpy as np

def save_color_data(path: str, data: np.ndarray):
    # PIL expects an 8-bit integer array of shape (height, width, 3).
    # Right now the data is actually 32-bit integers of shape (width, height).
    # Let's fix that.
    #
    # First transpose the array.
    # Now it has shape (height, width).
    data = data.transpose()
    # Use shifts and bit-masking to separate each channel into a separate array of shape (height, width).
    blues = (data & 0xff).astype(np.uint8)
    greens = ((data >> 8) & 0xff).astype(np.uint8)
    reds = ((data >> 16) & 0xff).astype(np.uint8)
    # Combine all three channels by stacking them on top of each other.
    # `axis=-1` ensures the shape ends up the way we want it.
    img_data = np.stack([reds, greens, blues], axis=-1)

    img = Image.fromarray(img_data, "RGB")
    img.save(path)

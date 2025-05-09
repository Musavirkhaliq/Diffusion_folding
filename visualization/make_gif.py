from PIL import Image, ImageSequence
import os

# Folder with your PNGs
image_dir = "/home/musa/Documents/augment-projects/foldingdiff/visualization"
output_gif = os.path.join(image_dir, "clean_fast.gif")

# Get all PNGs and sort them
images = sorted([
    f for f in os.listdir(image_dir) if f.endswith(".png")
])

# Open all images
frames = [Image.open(os.path.join(image_dir, f)).convert("RGBA") for f in images]

if frames:
    # Save to GIF
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        format="GIF",
        duration=10,     # 100ms per frame = 10 fps
        loop=0,
        disposal=2        # Clear previous frame before showing next
    )
    print(f"✅ Clean fast GIF saved at: {output_gif}")
else:
    print("❌ No images found.")

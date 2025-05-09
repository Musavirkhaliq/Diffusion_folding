from moviepy.editor import ImageSequenceClip
import os

# Directory with your images
image_dir = "/home/musa/Documents/augment-projects/foldingdiff/visualization"
output_video = os.path.join(image_dir, "protein_animation.mp4")

# Sorted list of PNG images
images = sorted([
    os.path.join(image_dir, img)
    for img in os.listdir(image_dir)
    if img.endswith(".png")
])

# Create a video clip at 10 frames per second
clip = ImageSequenceClip(images, fps=10)
clip.write_videofile(output_video, codec="libx264")

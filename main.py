import bisect
import os

from PIL import Image, ImageFont, ImageDraw

# def gif_to_pngs(gif_path, output_directory):
#     with Image.open(gif_path) as img:
#         frame_number = 0
#         while True:
#             try:
#                 img.seek(frame_number)
#                 frame = img.copy()
#                 frame.save(f"{output_directory}/frame_{frame_number:03}.png", "PNG")
#                 frame_number += 1
#             except EOFError:
#                 break
#
# # Example usage
# gif_path = "/Users/cli/Downloads/snail.gif"
# output_directory = "/Users/cli/Documents/sprite-sheet-creator/pngs"
# gif_to_pngs(gif_path, output_directory)

def group_related_frames(directory_path: str) -> [[str]]:
    # Return all of files in the directory
    frame_paths = os.listdir(directory_path)

    related_animations_dict = {}

    for frame_path in frame_paths:

        # frame_path_parts[0] is the animation and frame_path_parts[1] is
        # the frame number. I.e. alert_1.png, alert is the name of the
        # animation and 1 is the frame number.

        frame_path_parts = frame_path.split("_")
        animation_name = frame_path_parts[0]

        if animation_name not in related_animations_dict:
            related_animations_dict[animation_name] = []
        related_frames = related_animations_dict[animation_name]

        # Insert the frame path and sort it
        bisect.insort(related_frames, frame_path)

    return [frame_paths for frame_paths in related_animations_dict.values()]


# def create_sprite_sheet_from_frame_paths():



def create_sprite_sheet(frames_directory, output_path, rows=1):
    frames = [Image.open(os.path.join(frames_directory, f)) for f in os.listdir(frames_directory) if f.endswith('.png')]
    if not frames:
        raise ValueError("No PNG frames found in the specified directory.")

    # Assuming all frames have the same dimensions
    frame_width, frame_height = frames[0].size
    columns = (len(frames) // rows + (len(frames) % rows > 0)) + 1 # Add one column for the animation name
    sprite_sheet_width = columns * frame_width
    sprite_sheet_height = rows * frame_height

    sprite_sheet = Image.new("RGBA", (sprite_sheet_width, sprite_sheet_height))

    # for index, frame in enumerate(frames):
    for index in range(len(frames) + 1):
        x = (index % columns) * frame_width
        y = (index // columns) * frame_height
        if index < len(frames):
            frame = frames[index]
            sprite_sheet.paste(frame, (x, y))
        else:
            # Add text to the image to indicate the animation name
            print("adding animation name")
            animation_name = "stand"
            font = ImageFont.truetype("/Users/cli/Documents/sprite-sheet-creator/Roboto-Black.ttf", 12)
            draw = ImageDraw.Draw(sprite_sheet)
            draw.text((x, y), animation_name, (255, 0, 0), font=font)

    sprite_sheet.save(output_path, "PNG")


# Usage example
frames_directory = "/Users/cli/Documents/sprite-sheet-creator/pngs"
output_path = "/Users/cli/Documents/sprite-sheet-creator/sprite_sheets/snail_sprite_sheet.png"
create_sprite_sheet(frames_directory, output_path, rows=1)
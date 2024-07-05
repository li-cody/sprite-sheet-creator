from __future__ import annotations

import bisect
import os

import PIL
from PIL import Image, ImageFont, ImageDraw


class ImageWrapper:
    def __init__(self, image: Image, file_name: str):
        self.image = image
        self.file_name = file_name

    def __lt__(self, other: ImageWrapper):
        return self.file_name < other.file_name


class UnprocessedSpriteSheet:
    def __init__(self, grouped_frames_dict: dict[str, list[ImageWrapper]], max_columns: int, max_width: int, max_height: int):
        self.grouped_frames_dict = grouped_frames_dict
        self.max_columns = max_columns
        self.max_width = max_width
        self.max_height = max_height


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

# TODO: Determine max width and height of all frames
# TODO: Return a list of images instead of list of file names?
# TODO: Create mega sprite sheet

def group_related_frames(directory_path: str) -> UnprocessedSpriteSheet:
    # Return all of files in the directory
    frame_paths = os.listdir(directory_path)

    related_animations_dict = {}
    # These values are used to set the dimensions of the sprite sheet.
    max_columns = -1
    max_width = -1
    max_height = -1

    for frame_name in frame_paths:
        if frame_name == ".DS_Store":
            continue

        # frame_path_parts[0] is the animation and frame_path_parts[1] is
        # the frame number. I.e. alert_1.png, alert is the name of the
        # animation and 1 is the frame number.

        frame_name_parts = frame_name.split("_")
        animation_name = frame_name_parts[0]

        # Create a list of ImageWrappers that are sorted by file name and the
        # subsequent list is mapped to a related animation.
        try:
            frame_image = Image.open(os.path.join(directory_path, frame_name))
        except FileNotFoundError:
            print(f"Unable to open image {frame_name} as it does not exist.")
            continue
        except PIL.UnidentifiedImageError:
            print(f"Skipping image {frame_name} as it is not a valid image.")
            continue
        except IsADirectoryError:
            print(f"Skipping {frame_name} as it is a directory.")
            continue

        if animation_name not in related_animations_dict:
            related_animations_dict[animation_name] = []
        related_frames = related_animations_dict[animation_name]

        frame_image_wrapper = ImageWrapper(frame_image, frame_image.filename)
        bisect.insort(related_frames, frame_image_wrapper)

        max_columns = max(max_columns, len(related_frames))
        max_width = max(max_width, frame_image.width)
        max_height = max(max_height, frame_image.height)

    return UnprocessedSpriteSheet(
        grouped_frames_dict=related_animations_dict,
        max_columns=max_columns,
        max_width=max_width,
        max_height=max_height
    )


def create_sprite_sheet_row(
        animation_name: str,
        grouped_frames: list[Image],
        sprite_sheet: Image,
        row_index: int,
        columns: int,
        sprite_width: int,
        sprite_height: int
):
    # For the last iteration, add the animation name
    for index in range(len(grouped_frames) + 1):
        x = (index % columns) * sprite_width  # 0,
        y = row_index * sprite_height
        if index < len(grouped_frames):
            frame = grouped_frames[index]
            sprite_sheet.paste(frame, (x, y))
        else:
            # Add text to the image to indicate the animation name
            font = ImageFont.truetype("/Users/cli/Documents/sprite-sheet-creator/Roboto-Black.ttf", 12)
            draw = ImageDraw.Draw(sprite_sheet)
            draw.text((x, y), animation_name, (255, 0, 0), font=font)


def create_sprite_sheet(unprocessed_sprite_sheet: UnprocessedSpriteSheet):
    max_columns = unprocessed_sprite_sheet.max_columns + 1  # Last column used for the animation name
    max_width = unprocessed_sprite_sheet.max_width
    max_height = unprocessed_sprite_sheet.max_height
    grouped_frames_dict = unprocessed_sprite_sheet.grouped_frames_dict
    animations = grouped_frames_dict.keys()

    # Create large sprite sheet
    sprite_sheet_width = max_columns * max_width
    sprite_sheet_height = len(animations) * max_height
    sprite_sheet = Image.new("RGBA", size=(sprite_sheet_width, sprite_sheet_height))

    for row_index, animation in enumerate(animations):
        grouped_frames = [image_wrapper.image for image_wrapper in grouped_frames_dict[animation]]
        create_sprite_sheet_row(
            animation_name=animation,
            sprite_sheet=sprite_sheet,
            grouped_frames=grouped_frames,
            row_index=row_index,
            columns=max_columns,
            sprite_width=max_width,
            sprite_height=max_height
        )

    output_path = "/Users/cli/Documents/sprite-sheet-creator/sprite_sheets/snail_sprite_sheet.png"
    sprite_sheet.save(output_path, "PNG")


# Usage example
unprocessed_sprite_sheet = group_related_frames(directory_path="/Users/cli/Downloads/CharacterSpriteSheet (2)")
create_sprite_sheet(unprocessed_sprite_sheet)
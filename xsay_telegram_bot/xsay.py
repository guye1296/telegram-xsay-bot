import argparse
import pkg_resources
import typing
import os
import enum
import random
import toml
from io import BytesIO
from singleton_decorator import singleton
from PIL import Image, ImageDraw, ImageFont


FONT_SIZE = 50
TEXT_BUBBLE_DISTANCE_FROM_BASE_WIDTH = 20
TEXT_BUBBLE_DISTANCE_FROM_BASE_HEIGHT = 20
TEXT_BUBBLE_PADDING_WIDTH = 5
TEXT_BUBBLE_PADDING_HEIGHT = 5


    
def draw_text_bubble(source_image: Image.Image, text: str, text_bubble_base: typing.Tuple[int, int], directing_right: bool = True) -> Image.Image:
    
    # 1. Get the text size
    font = ImageFont.truetype(pkg_resources.resource_filename('xsay_telegram_bot', os.path.join('resources', 'caption_font.otf')), FONT_SIZE)
    draw = ImageDraw.Draw(source_image)

    text_bound_box_coordinates = \
        draw.textbbox((0, 0), text, font, anchor='lt')

    text_height = text_bound_box_coordinates[3]
    text_width = text_bound_box_coordinates[2]

    text_width += TEXT_BUBBLE_PADDING_WIDTH * 2
    text_height += TEXT_BUBBLE_PADDING_HEIGHT * 2

    # Expand original image if required

    text_bubble_triangle_crossover_with_rectangle_width = \
        text_bubble_base[0] + (1 if directing_right else -1) * TEXT_BUBBLE_DISTANCE_FROM_BASE_WIDTH


    text_bubble_far_edge_width = text_bubble_triangle_crossover_with_rectangle_width + (1 if directing_right else -1) * text_width

    text_bubble_minimal_edge_height = text_bubble_base[1] - (text_height // 2)
    text_bubble_maximal_edge_height = text_bubble_base[1] + (text_height // 2)

    source_image_width, source_image_height = source_image.size

    new_image_width = source_image_width

    source_image_paste_width = 0
    source_image_paste_height = 0

    # We should care about the following cases:
    # 1. The far edge exceeded the image width - pad image up to that edge
    if text_bubble_far_edge_width > new_image_width:
        new_image_width = text_bubble_far_edge_width
    # 2. The far edge exceeded the image width from the left - meaning it went negative. Add the delta to the width
    elif text_bubble_far_edge_width < 0:
        new_image_width -= text_bubble_far_edge_width

    new_image_height = max(text_bubble_maximal_edge_height, source_image_height) - min(text_bubble_minimal_edge_height, 0)

    # If the textbox was behind the image - the source image should not be pasted at (0,0) - calculate the offset
    if text_bubble_minimal_edge_height < 0:
        source_image_paste_height = new_image_height - source_image_height
    if text_bubble_far_edge_width < 0:
        source_image_paste_width = new_image_width - source_image_width
    
    image = Image.new("RGBA", (new_image_width, new_image_height), (0,0,0,0))
    image.paste(source_image, (source_image_paste_width, source_image_paste_height))

    # Normalize by paste_{height, width}

    text_bubble_base = (
        text_bubble_base[0] + source_image_paste_width,
        text_bubble_base[1] + source_image_paste_height
    )

    text_bubble_minimal_edge_height += source_image_paste_height
    text_bubble_maximal_edge_height += source_image_paste_height

    text_bubble_triangle_crossover_with_rectangle_width += source_image_paste_width

    # Draw the initial rectangle and add the text
    draw = ImageDraw.Draw(image)

    text_rectangle_upper_left_corner_height = text_bubble_minimal_edge_height
    text_rectangle_lower_right_corner_height = text_bubble_maximal_edge_height

    if directing_right:
        text_rectangle_upper_left_corner_width = text_bubble_base[0] + TEXT_BUBBLE_DISTANCE_FROM_BASE_WIDTH
        text_rectangle_lower_right_corner_width = text_rectangle_upper_left_corner_width + text_width
    else:
        text_rectangle_lower_right_corner_width = text_bubble_base[0] - TEXT_BUBBLE_DISTANCE_FROM_BASE_WIDTH
        text_rectangle_upper_left_corner_width = text_rectangle_lower_right_corner_width - text_width

    text_rectangle_coordinates = (
        text_rectangle_upper_left_corner_width,
        text_rectangle_upper_left_corner_height,
        text_rectangle_lower_right_corner_width,
        text_rectangle_lower_right_corner_height,
    )
        

    draw.rounded_rectangle(text_rectangle_coordinates, radius=3, outline='black', fill='white')
    
    text_draw_start_coordinates = (
        text_rectangle_upper_left_corner_width + TEXT_BUBBLE_PADDING_WIDTH,
        text_rectangle_upper_left_corner_height + TEXT_BUBBLE_PADDING_HEIGHT,
    )

    draw.text(text_draw_start_coordinates, text, fill='black', font=font, anchor='lt')

    # Draw the triangle 
    draw.polygon(
        (
            text_bubble_base,
            (text_bubble_triangle_crossover_with_rectangle_width, text_bubble_base[1] - TEXT_BUBBLE_DISTANCE_FROM_BASE_HEIGHT),
            (text_bubble_triangle_crossover_with_rectangle_width, text_bubble_base[1] + TEXT_BUBBLE_DISTANCE_FROM_BASE_HEIGHT),
        ),
        outline='black',
        fill='white'
    )

    # Draw a white line so blend the polygon with the rectangle
    draw.line(
        (
            (text_bubble_triangle_crossover_with_rectangle_width, text_bubble_base[1] - TEXT_BUBBLE_DISTANCE_FROM_BASE_HEIGHT),
            (text_bubble_triangle_crossover_with_rectangle_width, text_bubble_base[1] + TEXT_BUBBLE_DISTANCE_FROM_BASE_HEIGHT),
        ),
        fill='white'
    )

    return image


class Direction(enum.Enum):
    Right = 0
    Left = 1
    Any = 2

    @classmethod 
    def from_string(cls, input_string: str):
        input_string = input_string.lower()

        if input_string == 'right':
            return cls.Right
        elif input_string == 'left':
            return cls.Left
        elif input_string == 'any':
            return cls.Any

        raise ValueError(f"invalid value {input_string}")
        

class ImageGenerator:
    def __init__(self, image_template_path: str, text_bubble_coordinates: typing.Tuple[int, int], bubble_direction: Direction) -> None:
        self._path = image_template_path
        self._text_bubble_coordinates = text_bubble_coordinates
        self._bubble_direction = bubble_direction


    def _should_bubble_be_facing_right(self) -> bool:
        if self._bubble_direction == Direction.Right:
            return True
        elif self._bubble_direction == Direction.Left:
            return False
        # If "Any" - pick direction at random
        return random.choice((True, False))


    def generate(self, phrase: str) -> Image.Image:
        source_image = Image.open(self._path)

        return draw_text_bubble(source_image, phrase, self._text_bubble_coordinates, self._should_bubble_be_facing_right())

    @classmethod
    def from_image_template_file_record(cls, record: dict, base_template_dir: str):
        return cls(
            os.path.join(base_template_dir, record['path']),
            tuple(record['text_bubble_coordinates']), 
            Direction.from_string(record['direction'])
        )

@singleton
class Generator:
    def __init__(self, image_templates_file_path: str, phrase_file_path: str):
        with open(phrase_file_path, 'r') as phrase_file:
            self._phrases = [phrase for phrase in phrase_file.read().splitlines() if len(phrase) > 0]
        with open(image_templates_file_path, 'r') as image_templates_file:
            image_templates_records = toml.load(image_templates_file)['images']

            image_templates_file_directory = os.path.dirname(image_templates_file_path)

            self._image_templates = [
                ImageGenerator.from_image_template_file_record(record, image_templates_file_directory) for
                record in 
                image_templates_records.values()
            ]

    
    def generate(self) -> BytesIO:
        phrase = random.choice(self._phrases)
        template = random.choice(self._image_templates)

        generated_image = template.generate(phrase)
        stream = BytesIO()
        generated_image.save(stream, format='png')
        stream.seek(0)

        return stream


def main():
    def parse_arguments() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("image_path", type=str, help="Image path")
        parser.add_argument("text", type=str, help="Text to display")
        parser.add_argument("x", type=int, help="x coordinate")
        parser.add_argument("y", type=int, help="y coordinate")
        parser.add_argument("--facing-right", action='store_false', help="display right of the character")
        return parser.parse_args()

    arguments = parse_arguments()

    image = Image.open(arguments.image_path)

    im = draw_text_bubble(
        image,
        arguments.text,
        (arguments.x, arguments.y),
        arguments.facing_right
    )

    im.show()

    return
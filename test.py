import numpy as np
from PIL import Image, ImageOps
import os
import base64

tiles = []

for tile_file in sorted(os.listdir("puzzle_images/going_somewhere/"), key=lambda x: int(x.removesuffix(".png"))):
    image_tile = np.asarray(Image.open(f"puzzle_images/going_somewhere/{tile_file}"))
    tiles.append(image_tile)
common_colors = {}

for tile in tiles:
    tile_corners = [str(tile[0][0]), str(tile[0][-1]), str(tile[-1][0]), str(tile[-1][-1])]
    if tile_corners[0] == tile_corners[1] or tile_corners[0] == tile_corners[2]:
        if tile_corners[0] in common_colors.keys():
            common_colors[tile_corners[0]] = common_colors[tile_corners[0]] + 1
        else:
            common_colors[tile_corners[0]] = 1
    elif tile_corners[3] == tile_corners[1] or tile_corners[3] == tile_corners[2]:
        if tile_corners[3] in common_colors.keys():
            common_colors[tile_corners[3]] = common_colors[tile_corners[3]] + 1
        else:
            common_colors[tile_corners[3]] = 1
    


border_color_string = list(common_colors.keys())[0]

for color in common_colors.keys():
    if common_colors[color] > common_colors[border_color_string]:
        border_color_string = color

border_color = np.asarray(border_color_string)


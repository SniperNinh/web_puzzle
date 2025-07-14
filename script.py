import numpy as np
from PIL import Image, ImageOps
import os
import base64
import math

## IMPORTANT
# The downloaded jpg/png files of the original images has to be named after the puzzle, lower case and " " -> "_"
# And they have to be downloaded to .../puzzle_images/
# 
# The puzzle htm/html files has to be downloaded to .../puzzle_html_files/


## TODO code
# - TODO; find border color (check most common first color)
# - TODO; find border size
#   1. find peice with topleft & bottomleft corners = border color
#   2. check amount of pixels = border color in top row
# - DONE; take account for border_size
#   1. crop the source image
#   2. fill the border around the image

## script step process:
# 1) download the html for the puzzle
# 2) run the html -> tiles script
# 3) get the source image 
# *) run the main script:
# 1. Inputs; 
#   - image tiling, eg. 4x4, 12x12, 32x32
#   - puzzle name (for getting the files)
# 2. find border color & size
# 3. crop source image and add border
# 4. solve the puzzle (danish wizardry)


## HTML TO PNG FILES

while True:
    html_file_name = input("input html file name for the puzzle: ")

    if not os.path.exists(f"puzzle_html_files/{html_file_name}"):
        print("html/htm file could not be found")
    else:
        break

with open(f"puzzle_html_files/{html_file_name}", "r") as f:
    puzzle_html = f.readlines()
    f.close()


puzzle_title = "puzzle_title"

tiles = []

for line in puzzle_html:
    if '<h1 id="puzzle-title">' in line:
        puzzle_title = line.split('"')[-1].strip()
        puzzle_title = puzzle_title.removesuffix("</a></h1>")
        puzzle_title = puzzle_title.removeprefix(">")
        puzzle_title = puzzle_title.lower()
        puzzle_title = puzzle_title.replace(" ", "_")
        
        if os.path.exists(f"puzzle_images/{puzzle_title}"):
            print(f"remove old directory: puzzle_images/{puzzle_title}")
            exit()
        os.mkdir(f"puzzle_images/{puzzle_title}")
        
        #very beutiafull i know
    elif '<div class="puzzle-board" id="board"' in line:
        for image_line in line[:-7].split('<img src="data:image/png;'):
            if image_line.strip().startswith('base64,'):
                base64_image = image_line.strip().removeprefix('base64,')[:image_line.find('"')-1]
                decoded_image = base64.b64decode(base64_image.encode("ascii"))
                
                image_file_name = f"{image_line.strip()[image_line.strip().find('n="')+3:-2]}.png"
                with open(f"puzzle_images/{puzzle_title}/{image_file_name}", "wb") as f:
                    f.write(decoded_image)
                    f.close()
                
                tiles.append(np.asarray(Image.open(f"puzzle_images/{puzzle_title}/{image_file_name}")))



tiles_vert = int(math.sqrt(len(tiles)))
tiles_hori = int(math.sqrt(len(tiles)))


## FIND BORDER COLOR & SIZE

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


border_size = 0
for n, tile in enumerate(tiles):
    if str(tile[0][0]) == border_color_string and str(tile[-1][0]) == border_color_string and str(tile[0][-1]) != border_color_string:
        print("scubiee", n)
        for pixel in tile[0]:
            if str(pixel) == border_color_string:
                border_size += 1
            else:
                break
        break


border_color = None

for tile in tiles:
    if str(tile[0][0]) == border_color_string:
        border_color = tile[0][0]
        break

## CROP SOURCE IMAGE AND ADD BORDER

source_image = None
if os.path.exists(f"puzzle_images/{puzzle_title}.png"):
    source_image = np.asarray(Image.open(f"puzzle_images/{puzzle_title}.png"))
elif os.path.exists(f"puzzle_images/{puzzle_title}.jpg"):
    source_image = np.asarray(Image.open(f"puzzle_images/{puzzle_title}.jpg"))
else:
    print(f"Could not find Source Image, Looked for: .../puzzle_images/{puzzle_title}.png / .jpg")
    exit()

cropped_source_image = source_image[0:int(tiles[0].shape[0]*tiles_vert-border_size*2), 0:int(tiles[0].shape[1]*tiles_hori-border_size*2),:]

bordered_source_image = np.asarray(ImageOps.expand(Image.fromarray(cropped_source_image), border_size, tuple(border_color)))

print(border_size)

#Image.fromarray(bordered_source_image).save("hummiiee.png")

## SOLVE PUZZLE
# DaWiz, aka Danish Wisard was the brains behind the solving part

indexes = [-1 for _ in range(tiles_vert*tiles_hori)]


for n,tile in enumerate(tiles):
    t_h,t_w,_ = tile.shape
    best = (None,None)
    min_val = np.inf
    for i in range(tiles_vert):
        for j in range(tiles_hori):
            diff = abs(np.sum(bordered_source_image[i*t_h:(i+1)*t_h,j*t_w:(j+1)*t_w,:3] - tile))
            if diff < min_val:
                min_val = diff
                best = (i,j)
    """if n == 3:
        print(abs(np.sum(bordered_source_image[2*t_h:(2+1)*t_h,1*t_w:(1+1)*t_w,:3] - tile)))
        Image.fromarray(bordered_source_image[2*t_h:(2+1)*t_h,1*t_w:(1+1)*t_w,:3]).save("helpppppp.png")
    print(n, ":", min_val)
    if indexes[best[0] * tiles_hori + best[1]] != -1:
        print(indexes[best[0] * tiles_hori + best[1]], "->", n, "at", best[0], ",", best[1])"""
    indexes[best[0] * tiles_hori + best[1]] = n


print(indexes)
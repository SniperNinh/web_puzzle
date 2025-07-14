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
                
                image_file_name = f"{image_line.strip()[image_line.strip().find('n=')+3:-2]}.png"
                
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

if 0.8 < tiles[0].shape[0]*tiles_vert / source_image.shape[0] and tiles[0].shape[0]*tiles_vert / source_image.shape[0] < 1.2:
    pass
else:
    print("Source image size diverts largely from expected size")
    print(f"Source size:   {source_image.shape[0]}:{source_image.shape[1]}")
    print(f"expected size: {tiles[0].shape[0]*tiles_vert}:{tiles[0].shape[1]*tiles_hori}")
    bool_resize_input = input("resize source_image to expected size? [y/N]")
    if bool_resize_input == "y":
        source_image = np.asarray(ImageOps.contain(Image.fromarray(source_image), tuple([tiles[0].shape[1]*tiles_hori, tiles[0].shape[0]*tiles_vert])))
    

cropped_source_image = source_image[0:int(tiles[0].shape[0]*tiles_vert-border_size*2), 0:int(tiles[0].shape[1]*tiles_hori-border_size*2),:]

bordered_source_image = np.asarray(ImageOps.expand(Image.fromarray(cropped_source_image), border_size, tuple(border_color)))

## 
Image.fromarray(bordered_source_image).save("bordered_test.png")

# print(border_size)



## SOLVE PUZZLE
# DaWiz, aka Danish Wisard was the big brain behind the solving part of the script, credits goes to him

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
    if n == 12:
        print(abs(np.sum(bordered_source_image[3*t_h:(3+1)*t_h,3*t_w:(3+1)*t_w,:3] - tile)))
        print(abs(np.sum(bordered_source_image[best[0]*t_h:(best[0]+1)*t_h,best[1]*t_w:(best[1]+1)*t_w,:3] - tile)))
        print("i", i, ": j", j, " index ", best[0] * tiles_vert + best[1])
        Image.fromarray(tile).save("wtffff.png")
        Image.fromarray(bordered_source_image[best[0]*t_h:(best[0]+1)*t_h,best[1]*t_w:(best[1]+1)*t_w,:3]).save("idkkkkk.png")
        Image.fromarray(bordered_source_image[3*t_h:(3+1)*t_h,3*t_w:(3+1)*t_w,:3]).save("confus.png")
    
    #print(n, ":", min_val)
    
    if indexes[best[0] * tiles_hori + best[1]] != -1:
        print(indexes[best[0] * tiles_hori + best[1]], "->", n, "at", best[0], ",", best[1])
    indexes[best[0] * tiles_vert + best[1]] = n


print(indexes)

for n, ind in enumerate(indexes):
    if ind == -1:
        print(f"missing at {n//tiles_vert}, {n%tiles_vert}")

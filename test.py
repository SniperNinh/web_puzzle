import numpy as np
from PIL import Image, ImageOps
import os
import base64

tile = np.asarray(Image.open("wtffff.png"))

best_fcking_fit = np.asarray(Image.open("idkkkkk.png"))

confus = np.asarray(Image.open("confus.png"))

print(np.sum(best_fcking_fit - tile))
print(np.sum(confus - tile))


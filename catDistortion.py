import numpy as np
# import PIL as pil
# from scipy import misc
import PIL
from PIL import Image
from glob import glob
import os
from md5 import md5
from random import choice



def randomCrop(image):
    # minHeight, minWidth are decimal values [0,1]
    minWidth = 0.5
    minHeight = 0.5

    # Make sure you leave enough room to be at least minWidth by minHeight
    # all the +/- 1 is a quick hack to avoid the random number gen giving 0 and
    # causing some problems
    left = int( min(np.random.rand()*image.size[0], image.size[0]*(1-minWidth)) )+1
    upper = int( min(np.random.rand()*image.size[1], image.size[1]*(1-minHeight)) )+1

    right = left + int( np.random.rand()*(image.size[0]-1-left) )+1
    lower = upper + int( np.random.rand()*(image.size[1]-1-left) )+1

    return image.crop( (left, upper, right, lower) )


def randomTranspose(image):
    options = [
        Image.FLIP_LEFT_RIGHT,
        Image.FLIP_TOP_BOTTOM,
        Image.ROTATE_90,
        Image.ROTATE_180,
        Image.ROTATE_270
    ]
    # Pick a transpose at random
    return image.transpose( choice(options) )

def randomResize(image):
    minWidth = 0.25
    minHeight = 0.25

    maxWidth = 2.0
    maxHeight = 2.0

    # Don't crop it down below minWidth by minHeight
    return image.resize(
        (
            int(max(np.random.rand()*maxWidth, minWidth)*image.size[0]),
            int(max(np.random.rand()*maxHeight, minHeight)*image.size[1])
        )
    )

def blackAndWhite(image):
    # L for black and white
    return image.convert("L")

def randomNoise(image):
    # Adjust noise level at will. Hihgher = more noise. I found even with
    # 150 some images were very heavily distorted.
    maxNoise = 100
    # convert to array
    arr = np.array(image)
    # Add original image to noise array
    arr = arr + np.random.poisson( np.random.rand()*maxNoise, arr.shape ).astype(np.uint8)
    return Image.fromarray( arr )

if __name__ == '__main__':
    # Get a list of images
    files = glob("images/original/*")
    # Will use this list as random options for transforming an image
    functions = [ blackAndWhite, randomTranspose, randomNoise ]
    # Extra functions are used to prefent cropping AND resizing.
    extraFunctions = [ randomResize, randomCrop ]
    numOfChildren = 5
    for f in files[:]:
        print "Opening: ",f
        for counter in range(numOfChildren):
            # Do at least ONE mutation
            numOfMutations = max(int(np.random.rand()*len(functions)), 1)
            print "Doing %d mutations"%numOfMutations
            calls = np.random.choice( functions, numOfMutations)
            nImg = Image.open(f)
            for func in calls:
                nImg = func(nImg)
            r = np.random.rand()
            if r < 0.4:
                nImg = randomResize(nImg)
            elif r < 0.8:
                nImg = randomCrop(nImg)

            nImg.save( "images/distorted/%s_%s.jpg"%( f.split("/")[-1],md5(str(counter)+f).hexdigest() ) )

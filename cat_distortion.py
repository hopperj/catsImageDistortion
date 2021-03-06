
"""Usage:
    prog [-hd] [ --cropVariance=<cropVariance> --resizeVariance=<resizeVariance> ] [ --originalDir=<folder> --croppedDir=<folder>  --resizedDir=<folder> --croppedResizedDir=<folder> ] <num_of_children>

Makes several distorted images for every one originial image.

Arguments:
  <num_of_children>             How many distorted images will be made per original image. [default: 10]

Options:
  -h --help
  -d                                   Delete exising distorted images [default: False]
  --cropVariance=<cropVariance>        How extreme the cropping variance is. Set to 0 to disable cropping. [default: 0.25]
  --resizeVariance=<resizeVariance>  How extreme the resizing will be. Set to 0 to disable resizing. [default: 0.5]
  --originalDir=<folder>            Location of images to be distorted. [default: images/original/]
  --croppedDir=<folder>            Location of the cropped images to be stored. [default: images/cropped/]
  --resizedDir=<folder>            Location of resized images to be stored. [default: images/resized/]
  --croppedResizedDir=<folder>            Location of the cropped and resized images to be stored. [default: images/cropped_resized/]

"""
import numpy as np

from glob import glob
from PIL import Image

import os
import sys

from hashlib import md5
from random import choice

from docopt import docopt








class CatContortion():
    def __init__(self, image):
        self.__raw = image
        self.__transform = image
        self.__width = self.__raw.size[0]
        self.__height = self.__raw.size[1]

    def img(self):
        return self.__transform

    def reset(self):
        self.__set_transform(self.__raw)

    def __set_transform(self, image):
        self.__transform = image
        self.__width = image.size[0]
        self.__height = image.size[1]

    def random_crop(self, variance=.5):
        width = self.__width
        height = self.__height

        left = int(width - (1 - np.random.rand() * variance) * width)
        upper = int(height - (1 - np.random.rand() * variance) * height)

        remaining_width = self.__width - 1 - left
        remaining_height = self.__height - 1 - upper

        right = left + int((1 - np.random.rand() * variance) * remaining_width)
        lower = upper + int((1 - np.random.rand() * variance) * remaining_height)

        self.__set_transform(self.__transform.crop( (left, upper, right, lower) ))


    def random_transpose(self):
        options = [
            Image.FLIP_LEFT_RIGHT,
            Image.FLIP_TOP_BOTTOM,
            Image.ROTATE_90,
            Image.ROTATE_180,
            Image.ROTATE_270
        ]
        # Pick a transpose at random
        self.__set_transform(self.__transform.transpose(choice(options)))

    def random_resize(self, variance=.5):
        min_width = 1 - variance
        min_height = 1 - variance

        width_var = 1 / (1 - variance) - min_width
        height_var = 1 / (1 - variance) - min_height

        # Don't crop it down below minWidth by minHeight
        self.__set_transform(
            self.__transform.resize((
                int((np.random.rand() * width_var + min_width) * self.__width),
                int((np.random.rand() * height_var + min_height) * self.__height)
            ))
        )

    def black_and_white(self):
        # L for black and white
        self.__set_transform(self.__image.convert('L'))

    def random_noise(self):
        # Adjust noise level at will. Hihgher = more noise. I found even with
        # 150 some images were very heavily distorted.
        maxNoise = 100
        # convert to array
        arr = np.array(self.__image)
        # Add original image to noise array
        arr = arr + np.random.poisson(np.random.rand() * maxNoise, arr.shape).astype(np.uint8)
        self.__set_transform(Image.fromarray(arr))

if __name__ == '__main__':

    arguments = docopt(__doc__)  # parse arguments based on docstring above
    # print( arguments )
    num_of_children = int(arguments['<num_of_children>'])
    # Get a list of images
    print(arguments['--originalDir'])
    files = glob(os.path.join( arguments['--originalDir'],'*'))



    # Remove old image files if flagged
    if arguments['-d']:
      print("Removing cropped images ...")
      if( os.path.exists(os.path.join(arguments['--croppedDir'],"*")) ):
        os.remove(os.path.join(arguments['--croppedDir'],"*"))

      print("Removing resized images ...")
      if( os.path.exists(os.path.join(arguments['--resizedDir'],"*")) ):
        os.remove(os.path.join(arguments['--resizedDir'],"*"))

      print("Removing cropped and resized images ...")
      if( os.path.exists(os.path.join(arguments['--croppedResizedDir'],"*")) ):
        os.remove(os.path.join(arguments['--croppedResizedDir'],"*"))


    # Create image directories as needed
    if not os.path.isdir( arguments['--croppedDir'] ):
      os.mkdir( arguments['--croppedDir'] )

    if not os.path.isdir( arguments['--resizedDir'] ):
      os.mkdir( arguments['--resizedDir'] )

    if not os.path.isdir( arguments['--croppedResizedDir'] ):
      os.mkdir( arguments['--croppedResizedDir'] )



    for f in files:
        print('Opening: ', f)
        for counter in range(num_of_children):
            nImg = Image.open(f)

            distorted = CatContortion(nImg)
            distorted.random_crop(variance=float(arguments['--cropVariance']))
            # Save the resized image
            distorted.img().save(
              os.path.join(
                arguments['--croppedDir'],
                "%s_%s.jpg"%( f.split('/')[-1].split('.')[0], md5(str(counter).encode('utf-8') + f.encode('utf-8')).hexdigest())
              )
            )


            # Save an image that has been cropped
            distorted.reset()
            distorted.random_resize(variance=float(arguments['--resizeVariance']))

            distorted.img().save(
              os.path.join(
                arguments['--resizedDir'],
                "%s_%s.jpg"%( f.split('/')[-1].split('.')[0], md5(str(counter).encode('utf-8') + f.encode('utf-8')).hexdigest())
              )
            )


            # Save an image that has been cropped and resized
            distorted.random_crop(variance=float(arguments['--cropVariance']))

            distorted.img().save(
              os.path.join(
                arguments['--croppedResizedDir'],
                "%s_%s.jpg"%( f.split('/')[-1].split('.')[0], md5(str(counter).encode('utf-8') + f.encode('utf-8')).hexdigest())
              )
            )

            distorted.reset()

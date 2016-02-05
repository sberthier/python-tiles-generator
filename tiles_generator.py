# encoding=UTF-8

# Copyright © 2015 Sébastien Berthier <sebastien.berthier@haumea.fr>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
an image tile generator accepting multiple scale level
'''

import os, getopt, sys, logging, shutil
from PIL import Image
from string import Template

CONST_OUTPUT = Template("$filename/%l/%nx/%ny.$extension")
CONST_LEVEL = 3
CONST_OUTPUT_FORMAT = "JPEG"
CONST_OUTPUT_QUALITY = 90
CONST_OUTPUT_OPTIMIZE = False
CONST_OUTPUT_PROGRESSIVE = False
CONST_TILE_SIZE = 256
CONST_RESAMPLE = "ANTIALIAS"

class Configuration:
    output = None
    level = CONST_LEVEL
    output_format = CONST_OUTPUT_FORMAT
    output_quality = CONST_OUTPUT_QUALITY
    output_optimize = CONST_OUTPUT_OPTIMIZE
    output_progressive = CONST_OUTPUT_PROGRESSIVE
    tile_size = CONST_TILE_SIZE
    resample = CONST_RESAMPLE


def print_error_and_exit(message, code=1):
    sys.stderr.write("error: " + message + "\n")
    sys.exit(code)
	

class TilesGenerator:
    image = None
    tilesWriter = None
    tile_w = CONST_TILE_SIZE
    tile_h = CONST_TILE_SIZE
    resample = CONST_RESAMPLE


    """ Constructor """
    def __init__(self, tilesWriter, tile_size=CONST_TILE_SIZE, resample=CONST_RESAMPLE):
        if tile_size < 16:
            print_error_and_exit('size ' + repr(tile_size) + " should be greater or equal to 16", 7)
        self.tile_w = tile_size
        self.tile_h = tile_size
        self.tilesWriter = tilesWriter
	self.resample = resample
        return


    """ Public """
    def process(self, level):
        if level < 0:
            print_error_and_exit('level ' + repr(level) + " should be greater or equal to 0", 6)

        self.level = level
        self._processLevel()
        while self.level > 0:
            self.level = self.level - 1
            self.image = self.image.resize((int(self.image.size[0]/2) , int(self.image.size[1]/2)), getattr(Image, self.resample));
            self._processLevel()
        return

    def open(self, filename):
        try:
            if os.path.exists(filename) == 0:
                print_error_and_exit("file " + filename + " does not exist", 3)
            self.image = Image.open(filename);
        except IOError:
            print_error_and_exit('can not open image ' + filename, 10)
        return

    def close(self):
        try:
            self.image.close()
        except IOError:
            print('error while closing  ' + filename)
        return
        

    """ Private """
    def _doTile(self, x, y, tile_w, tile_h, nx, ny):
        logging.info("doTile x=" + repr(x) + ", y=" + repr(y) + ", w=" + repr(tile_w) + ", h=" + repr(tile_h))

        tile_image = self.image.crop((x, y, x+tile_w, y+tile_h))
        self.tilesWriter.save(tile_image, x, y, self.level, nx, ny)
        return

    def _processLevel(self):
        w = int(self.image.size[0])
        h = int(self.image.size[1])
    
        logging.info("doTiles at level " + repr(self.level) + " size: " + repr(self.image.size))
        tile_w = self.tile_w
        tile_h = self.tile_h
        n_w = int(w/tile_w)
        n_h = int(h/tile_h)
    
        # tiles plein de taille 256
        for i in range(0, n_w):
            x = i * tile_w
            for j in range(0, n_h):
                y = j * tile_h
                self._doTile(x, y, tile_w, tile_h, i,j)

	small_right = w % tile_w != 0
	small_bottom = h % tile_h != 0
    
        # tiles du bas
       	y = n_h * tile_h
        last_tile_h = h - y
	if small_bottom:
        	for i in range(0, n_w):
			x = i * tile_w
            		self._doTile(x, y, tile_w, last_tile_h, i, n_h)
    
        # tiles du droite
       	x = n_w * tile_w
        last_tile_w = w - x
	if small_right:
        	for j in range(0, n_h):
            		y = j * tile_h
            		self._doTile(x, y, last_tile_w, tile_h, n_w, j)

        # tile du bas a droite
	if small_right and small_bottom:
        	y = n_h * tile_h
        	x = n_w * tile_w
        	self._doTile(x, y, last_tile_w, last_tile_h, n_w, n_h)
        return



class TilesWriter:
    format = CONST_OUTPUT_FORMAT
    filename = None
    options = {}

    """ Constructor """
    def __init__(self, output, format=CONST_OUTPUT_FORMAT, level=CONST_LEVEL, quality=CONST_OUTPUT_QUALITY, optimize=CONST_OUTPUT_OPTIMIZE, progressive=CONST_OUTPUT_PROGRESSIVE):
        if quality not in list(range(1, 100)):
            print_error_and_exit('quality ' + repr(quality) + " not between 1 and 99", 4)
        if format not in ("JPEG", "PNG"):
            print_error_and_exit('format ' + repr(format) + " not JPEG or PNG", 5)
        output = output.replace('%l', '$l')
        output = output.replace('%x', '$x')
        output = output.replace('%y', '$y')
        output = output.replace('%nx', '$nx')
        output = output.replace('%ny', '$ny')
        if level > 0:
            if '$l' not in output:
                print_error_and_exit('$l should be in output because level > 1 (=' + repr(level) + ')', 14)
        if '$x' not in output or '$y' not in output:
            if '$nx' not in output or '$ny' not in output:
                print_error_and_exit('$x and $y or/and $nx and $ny should be in output', 14)

        self.format = format
        self.filename = Template(output)

	self.options = {'quality': quality}
	if progressive:
		self.options['progressive'] = True
	if optimize:
		self.options['optimize'] = True

	logging.info("TilesWriter: " + repr(self.options))
        return


    """ Public """
    def save(self, image, x, y, level, nx, ny):

        filename = self.filename.substitute(x=x, y=y, l=level, nx=nx, ny=ny);
        dirname = os.path.dirname(filename)
        if dirname != '' and not os.path.isdir(dirname):
            os.makedirs(dirname)

        # image.save(filename, self.format, quality=self.quality, progressive=self.progressive, optimize=self.optimize);
        image.save(filename, self.format, **self.options);
        return



def readOptions(argv):
    config = Configuration()

    try:
        opts, args = getopt.getopt(argv,"ho:l:s:f:q:r:",["help","output=", 
            "level=", "size=", "format=", "quality=", "optimize", "progressive", "log=", "resample="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if len(args) == 0:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            config.output = arg
        elif opt in ("-r", "--resample"):
            if arg in ("nearest", "bilinear", "bicubic", "antialias"):
                config.resample=arg.upper()
	    else:
                print("resample " + arg + " unknown")
                sys.exit(9)
        elif opt in ("-l", "--level"):
            config.level = int(arg)
        elif opt in ("-s", "--size"):
            config.tile_size = int(arg)
        elif opt in ("-f", "--format"):
            config.output_format = arg
        elif opt in ("-q", "--quality"):
            config.output_quality = int(arg)
        elif opt in ("--optimize"):
            config.output_optimize = True 
        elif opt in ("--progressive"):
            config.output_progressive = True 
        elif opt in ("--log"):
            if arg in ("debug", "info", "warn", "error", "critical"):
                logging.basicConfig(level=arg.upper())
            else:
                print_error_and_exit("log level " + arg + " does not exist", 9)

    config.filename = args[0]
    if config.output is None:
        config.output = CONST_OUTPUT.substitute(
                filename=os.path.splitext(config.filename)[0],
                extension=config.output_format.lower())

    return config


def main(argv):
    config = readOptions(argv)
    tilesWriter = TilesWriter(config.output, config.output_format,
            config.level, config.output_quality, config.output_optimize, config.output_progressive)

    tilesGenerator = TilesGenerator(tilesWriter, config.tile_size, config.resample)
    tilesGenerator.open(config.filename)
    tilesGenerator.process(config.level)
    tilesGenerator.close()

    return

def usage():
    print('usage: ' + sys.argv[0] + ' ')
    print('    -o --output <template thar container %l level, %x and %y for crop offset')
    print('                    or %nx and %ny for num of tile  ="$filename/%l/%nx/%ny.$format>')
    print('    -l --level <produce n+1 levels   =3> ')
    print('    -r --resample <nearest, bilinear, bicubic, antialias =antialias>')
    print('    -s --size <size of the tiles   =256>')
    print('    -f --format <(JPEG, PNG)   =JPEG>')
    print('    -q --quality <quality for JPEG   =90> ')
    print('    --optimize <optimize for JPEG/PNG   =False> ')
    print('    --progressive <optimize for JPEG   =False> ')
    print('    --log <debug,info,warn,error,critical>')
    print('    <image.png>')
    return

if __name__ == "__main__":
   main(sys.argv[1:])

# vim:ts=4 sw=4 et

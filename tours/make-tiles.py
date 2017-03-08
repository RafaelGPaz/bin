#!/usr/bin/env python
import argparse
import collections
import fileinput
import glob
import logging
import os
import shutil
import subprocess
import sys
from usefulfunctions import mkdirif
from usefulfunctions import query_yes_no

def main():
    # Script only for Windows
    if sys.platform != 'win32':
        sys.exit('Script is only for Windows')

    # Script only for python3
    if sys.version_info[0] < 3:
        sys.exit('Must be using Python 3')

    parser = argparse.ArgumentParser(description='Creates tiles for cars with visualiser option.')
    parser.add_argument('-i', action='store_false', dest='ignoreunderscores', \
                              default=True, help='Skip checking 4 underscores')
    args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    logging.info("Started")

    if query_yes_no('Do you need WebVR support?'):
        webvr = "yes"
    else:
        webvr = "no"

    if query_yes_no('Do you want 1024px preview?'):
        preview1024 = "yes"
    else:
        preview1024 = "no"

    # Delete any residual files or folders
    panosdir = '.src\\panos\\'
    for root, _, _ in os.walk(panosdir):
        for filepath in glob.glob(os.path.join(root, "*.kro")):
            if os.path.isfile(filepath):
                os.remove(filepath)
        for dirpath in glob.glob(os.path.join(root, "output")):
            if os.path.isdir:
                shutil.rmtree(dirpath)

    # Check if the directory containing the panos is empty
    if not os.listdir(panosdir):
        sys.exit('ERROR: Panos directory is empty')

    # Build list 'allitems' with ALL the items inside .src/panos excluding 'output'
    allitems = []
    tours = glob.glob(panosdir + '/*')
    for item in tours:
        if os.path.isfile(item):
            allitems.append(item)
        if os.path.isdir(item):
            subtours = glob.glob(item + "/*")
            for subitem in subtours:
                allitems.append(subitem)
        if 'output' in item:
            allitems.remove('output')

    # Check there aren't duplicated items
    duplicates = []
    for i in tours:
        iname = os.path.basename(i)
        ibasename = os.path.splitext(iname)[0]
        duplicates.append(ibasename)

    repeatedcar = [item for item, count in collections.Counter(duplicates).items() if count > 1]
    if repeatedcar:
        sys.exit('ERROR: The following cars are repeated: ' + str(repeatedcar))

    # Check panorama names has 3 underscores. It can be ignored with the switch '-ignoreunderscores'
    for tourname in allitems:
        if args.ignoreunderscores != False:
            tourbasename = os.path.splitext(tourname)[0]
            underscores = len(tourbasename.split('_'))
            if underscores != 4:
                sys.exit('ERROR: File ' + tourbasename +  ' contains ' + str(underscores) \
                         + ' underscores instead of 4. Please rename it.')

    # Check if tiles are needed
    for car in allitems:
        # logging.info('car: ' + car)
        carbasename = os.path.basename(os.path.dirname(car))
        tourbasename = os.path.splitext(os.path.basename(car))[0]
        filesdir = os.path.join(tourbasename, 'files')
        scenesdir = os.path.join(tourbasename, 'files\\scenes')
        parentdir = os.path.basename(os.path.abspath('..'))
        krdir = 'E:/documents/software/virtual_tours/krpano'
        krpath = krdir +'/krpano-1.19-pr8/krpanotools64.exe'
        krtemplates = krdir +'/krpano_conf/templates'
        if webvr == "yes":
            if preview1024 == "yes":
                krconfig = '-config=' + krtemplates + '/tv_tiles_with_vr_preview_1024.config'
            else:
                krconfig = '-config=' + krtemplates + '/tv_tiles_with_vr.config'
        else:
            if preview1024 == "yes":
                krconfig = '-config=' + krtemplates + '/tv_tiles_for_cars_ipad_preview_1024.config'
            else:
                krconfig = '-config=' + krtemplates + '/tv_tiles_for_cars_ipad.config'

        krcall = [krpath, "makepano", krconfig, car]
        # Special projects
        if parentdir == 'gforces' or parentdir == 'hr_owen':
            # logging.info('case 1')
            # Visualiser
            if 'scene' in tourbasename:
                # logging.info('case 1: Visualiser')
                carbasename = os.path.basename(os.path.dirname(car))
                filesdir = os.path.join(carbasename, "files")
                scenesdir = os.path.join(carbasename, "files\\scenes")
                tilesdir = os.path.join(scenesdir, tourbasename)
                outputdir = panosdir + carbasename + '\\output'
                outputtilesdir = outputdir + '\\scenes\\' + tourbasename
                outputxmlfile = outputdir + "\\" + tourbasename + '.xml'
                replaceorigin = 'scenes/' + tourbasename
                replacedest = '%SWFPATH%/../' + carbasename + '/files/scenes/' + tourbasename
                xmlfile = carbasename + '\\files\\scenes\\' + tourbasename + '.xml'
                message = carbasename + '/' + tourbasename
            else:
                # logging.info('case 1: Other')
                carbasename = tourbasename
                filesdir = os.path.join(carbasename, "files")
                scenesdir = os.path.join(carbasename, "files\\scenes")
                tilesdir = os.path.join(scenesdir, 'tiles')
                # HROWEN cars
                if parentdir == 'hr_owen':
                    # logging.info('case 1.1: HROWEN')
                    outputdir = panosdir + carbasename + '\\output'
                    outputtilesdir = outputdir + '\\scenes\\' + tourbasename
                    outputxmlfile = outputdir + "\\" + tourbasename + '.xml'
                    replaceorigin = 'scenes/' + tourbasename
                    replacedest = '%SWFPATH%/../../' + carbasename + '/files/scenes/' + tourbasename
                    message = carbasename + '/' + tourbasename
                    xmlfile = carbasename + '\\files\\scenes\\' + tourbasename + '.xml'
                # V10 Not Visualiser
                else:
                    # logging.info('case 1.2: Not Visualiser')
                    outputdir = panosdir + '\\output'
                    outputtilesdir = outputdir + '\\scenes\\' + tourbasename
                    outputxmlfile = outputdir + "\\" + tourbasename + '.xml'
                    replaceorigin = 'scenes/' + tourbasename
                    replacedest = '%SWFPATH%/../' + tourbasename + '/files/scenes/tiles'
                    message = tourbasename + '/' + carbasename
                    xmlfile = tourbasename + '\\files\\scenes\\scene.xml'

        # Normal car
        else:
            # logging.info('case 2')
            filesdir = os.path.join(carbasename, "files")
            scenesdir = os.path.join(carbasename, "files\\scenes")
            tilesdir = os.path.join(scenesdir, "tiles")
            outputdir = panosdir + '\\' + carbasename + '\\output'
            outputtilesdir = outputdir + '\\scenes\\' + tourbasename
            outputxmlfile = outputdir + '\\' + tourbasename + '.xml'
            replaceorigin = 'scenes/' + tourbasename
            if os.path.exists('./shared/'):
                replacedest = '%SWFPATH%/../' + tourbasename + '/files/scenes/tiles'
            else:
                replacedest = '%CURRENTXML%/scenes/' + tourbasename
            tilesdir = carbasename + '\\files\\scenes\\' + tourbasename
            xmlfile = carbasename + '\\files\\scenes\\' + tourbasename + '.xml'
            message = carbasename + '/' + tourbasename

        if not os.path.exists(tilesdir):
            logging.info('[    ] Making tiles for: ' + message)
            # Create folder structure
            # logging.info("carbasename: " + carbasename)
            # logging.info("tourbasename: " + tourbasename)
            # logging.info("filesdir: " + filesdir)
            # logging.info("scenesdir: " + scenesdir)
            # logging.info("tilesdir: " + tilesdir)
            # logging.info("xmlfile: " + xmlfile)
            # logging.info("outputxmlfile: " + outputxmlfile)
            # logging.info("outputtilesdir: " + outputtilesdir)
            mkdirif(carbasename)
            mkdirif(filesdir)
            mkdirif(scenesdir)

            subprocess.call(krcall, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
            # subprocess.call(krcall)

            for line in fileinput.input(outputxmlfile, inplace=True):
                print(line.replace(replaceorigin, replacedest), end="")
                # Move the folder containing the tiles
            if os.path.exists(outputtilesdir):
                shutil.move(outputtilesdir, tilesdir)
                # Move the scene.xml file
            if os.path.exists(outputxmlfile):
                shutil.move(outputxmlfile, xmlfile)
                # Delete output folder
            if os.path.exists(outputdir):
                shutil.rmtree(outputdir)

    logging.info('Finished')

if __name__ == '__main__':
    main()

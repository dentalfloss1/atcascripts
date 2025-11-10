import glob
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("inmeas")
args = parser.parse_args()
files = args.inmeas
cwd = os.getcwd().split('/')[-1]
vis      = f'{cwd}.ms'
fitsvis      = f'{cwd}.uvfits'
print(files)
exportuvfits(vis=files,fitsfile=fitsvis,datacolumn="data")
importuvfits(fitsfile=fitsvis,vis=vis)

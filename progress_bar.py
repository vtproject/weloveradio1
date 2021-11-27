# import time, sys

# update_progress() : Displays or updates a console progress bar
# Accepts a float between 0 and 1. Any int will be converted to a float.
# A value under 0 represents a 'halt'.
# A value at 1 or bigger represents 100%
# def update_progress(progress):
    # barLength = 10 # Modify this to change the length of the progress bar
    # status = ""
    # if isinstance(progress, int):
        # progress = float(progress)
    # if not isinstance(progress, float):
        # progress = 0
        # status = "error: progress var must be float\r\n"
    # if progress < 0:
        # progress = 0
        # status = "Halt...\r\n"
    # if progress >= 1:
        # progress = 1
        # status = "Done...\r\n"
    # block = int(round(barLength*progress))
    # text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    # sys.stdout.write(text)
    # sys.stdout.flush()


# update_progress test script

# for x in range(0,50):
    # y = x/23
    # update_progress(y)
    # time.sleep(1)

import sys

def progressbar(it, prefix="", size=100, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "█"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()
    
import time
print()
for i in progressbar(range(25), "Computing: ", 40):
    time.sleep(1) # any calculation you need


# https://stackoverflow.com/questions/3160699/python-progress-bar
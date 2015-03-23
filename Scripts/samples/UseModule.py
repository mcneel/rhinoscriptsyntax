# This script uses a function defined in the CircleFromLength.py
# script file
import CircleFromLength

# call the function a few times just for fun using the
# optional parameter
length = CircleFromLength.CreateCircle()
if length is not None and length>0.0:
    for i in range(4):
        CircleFromLength.CreateCircle(length)
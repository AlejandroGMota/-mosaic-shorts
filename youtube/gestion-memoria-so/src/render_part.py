import sys
from scenes import *
render(frame, DURATION, sys.argv[3], start=float(sys.argv[1]), end=float(sys.argv[2]))


import os, sys
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base)

import hasbug.cl
hasbug.cl.run(sys.argv)

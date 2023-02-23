from virus import Virus
from data import *

import matplotlib.pyplot as plot

if __name__ == "__main__":
    virus = Virus(VIRUS_PARAMETERS)
    animation = virus.animation()
    plot.show()

# Load and run a Pinetree simulation from config

from simulation.tools import loaders
import pinetree as pt
import sys, os

conf, seed, time_limit = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
description = os.path.basename(conf).split(".yaml")[0]
sim = loaders.load_model(conf)
sim.seed(seed)
sim.simulate(time_limit=time_limit, time_step=5, output=f"../output/sim/{description}_{time_limit}_{seed}.tsv")

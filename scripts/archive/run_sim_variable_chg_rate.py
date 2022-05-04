# Load and run a Pinetree simulation from config

from simulation.tools import loaders
import pinetree as pt
import sys, os

codons = {"AAA": {"TTT": {"charged": 100, "uncharged": 0}},}

conf, seed, time_limit, chrg_rate = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]))
description = os.path.basename(conf).split(".yaml")[0]
sim = loaders.load_model(conf)
sim.seed(seed)
sim.add_trna(codons, chrg_rate)
sim.simulate(time_limit=time_limit, time_step=5, output=f"../output/phase_analysis/{description}_{time_limit}_{chrg_rate}_{seed}.tsv")

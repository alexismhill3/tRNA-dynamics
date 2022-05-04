# Generates a random (seeded) two-codon gene with a 30 nt buffer upstream and 20 nt buffer downstream
import random
import sys

perc_good, perc_bad, len = (float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]))
codons = ["AAA"] * int(len * perc_good) + ["TAT"] * int(len * perc_bad)
random.Random(4).shuffle(codons)
print("A"*30 + "".join(codons) + "A"*20)

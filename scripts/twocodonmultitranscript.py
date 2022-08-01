import sys
from trnasimtools.simulate import SimulateTwoCodonMultiTranscript

transcript_copy_numbers = [int(sys.argv[3]), int(sys.argv[4])]
ribosome_binding_rates = [float(sys.argv[7]), float(sys.argv[8])]
trna_charging_rates = [float(sys.argv[9]), float(sys.argv[10])]

simulator = SimulateTwoCodonMultiTranscript(config_file=sys.argv[1],
                                             seed=int(sys.argv[2]),
                                             transcript_copy_numbers=transcript_copy_numbers,
                                             ribosome_copy_number=int(sys.argv[5]),
                                             total_trna=int(sys.argv[6]),
                                             ribosome_binding_rates=ribosome_binding_rates,
                                             trna_charging_rates=trna_charging_rates)
simulator.simulate(sys.argv[11])

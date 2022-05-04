import yaml
import sys

perc = sys.argv[1] 
chrg_good = float(sys.argv[2])
chrg_bad = float(sys.argv[3])

in_file = f"yaml/two_codon/two_codon_fixed_transcript_{perc}_90_10_100_100_200_1200_5.0.yaml"
with open(in_file, "r") as stream:
    data = yaml.safe_load(stream)
    data["rate_constants"] = {"TTT": chrg_good, "ATA": chrg_bad}
    new_file = f"yaml/two_codon/two_codon_fixed_transcript_{perc}_90_10_{chrg_good}_{chrg_bad}_200_1200_5.0.yaml"
    with open(new_file, 'w') as outfile:
        yaml.dump(data, outfile)

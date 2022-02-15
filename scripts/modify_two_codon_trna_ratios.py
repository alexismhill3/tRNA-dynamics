import yaml
import sys

perc = sys.argv[1] 
count_good = int(sys.argv[2])
count_bad = int(sys.argv[3])

in_file = f"yaml/two_codon/two_codon_fixed_transcript_{perc}_90_10_100_100_200_1200_5.0.yaml"
with open(in_file, "r") as stream:
    data = yaml.safe_load(stream)
    data["tRNA_counts"] = {"TTT": [count_good, 0], "ATA": [count_bad, 0]}
    new_file = f"yaml/two_codon/two_codon_fixed_transcript_{perc}_{count_good}_{count_bad}_100.0_100.0_200_1200_5.0.yaml"
    print(f"writing file: {new_file}")
    with open(new_file, 'w') as outfile:
        yaml.dump(data, outfile)

from time import time
import pinetree as pt
import sys, os
import yaml

def _load_conf(config_file):
    with open(config_file, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as yaml_error:
            print(yaml_error)
        return data


def two_codon(seed, output_dir, rbs, chrg_rate, conf):

    data = _load_conf(conf)
    seq = data["seq"]

    sim = pt.Model(cell_volume=8e-16)
    sim.seed(seed)
    sim.add_ribosome(copy_number=100, speed=3, footprint=15)
    
    i = 0
    while i < data["transcripts"]:
        transcript = pt.Transcript("transcript", 350)
        transcript.add_gene(name="proteinX", start=31, stop=330,
                     rbs_start=(31 - 15), rbs_stop=31, rbs_strength=rbs)
        transcript.add_seq(seq=seq)
        sim.register_transcript(transcript)
        i += 1

    tRNA_rates = {"ATA": chrg_rate, "TTT": chrg_rate}
    sim.add_trna(data["tRNA_map"], data["tRNA_counts"], tRNA_rates)
    description = os.path.basename(conf).split(".yaml")[0]
    sim.simulate(time_limit=data["time_limit"], time_step=data["time_step"], output=f"{output_dir}/{description}_{rbs}_{chrg_rate}_{seed}.tsv")


if __name__ == "__main__":
    two_codon(int(sys.argv[1]), sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5])

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


def single_codon(seed, time_limit, output_dir, transcripts, rbs, conf):

    data = _load_conf(conf)
    seq = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAATATAAAAAAAAAAAAA"

    sim = pt.Model(cell_volume=8e-16)
    sim.seed(seed)
    sim.add_ribosome(copy_number=100, speed=3, footprint=15)
    #sim.add_polymerase(name="rnapol", copy_number=20, speed=1000, footprint=10)

    #plasmid = pt.Genome(name="plasmid", length=361)
    i = 0
    while i < transcripts:
        transcript = pt.Transcript("transcript", 361)
        transcript.add_gene(name="proteinX", start=31, stop=351,
                     rbs_start=(31 - 15), rbs_stop=31, rbs_strength=rbs)
        transcript.add_seq(seq=seq)
        sim.register_transcript(transcript)
        i += 1

    sim.add_trna(data["tRNA_map"], data["tRNA_counts"], data["rate_constants"])
    description = os.path.basename(conf).split(".yaml")[0]
    sim.simulate(time_limit=time_limit, time_step=1, output=f"{output_dir}/{description}_{transcripts}_{rbs}_{seed}.tsv")


if __name__ == "__main__":
    single_codon(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), float(sys.argv[5]), sys.argv[6])

import pinetree as pt
import sys


def single_codon(seed, charging_rate, time_limit, output_dir):

    tRNA = {"AAA": {"TTT": {"charged": 100, "uncharged": 0}},}
    seq = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    sim = pt.Model(cell_volume=8e-16)
    sim.seed(seed)
    sim.add_ribosome(copy_number=100, speed=3, footprint=15)
    #sim.add_polymerase(name="rnapol", copy_number=20, speed=1000, footprint=10)

    #plasmid = pt.Genome(name="plasmid", length=361)
    i = 0
    while i < 400:
        transcript = pt.Transcript("transcript", 361)
        transcript.add_gene(name="proteinX", start=31, stop=351,
                     rbs_start=(31 - 15), rbs_stop=31, rbs_strength=1e6)
        transcript.add_seq(seq=seq)
        sim.register_transcript(transcript)
        i += 1

    sim.add_trna(tRNA, charging_rate)
    sim.simulate(time_limit=time_limit, time_step=5, output=f"{output_dir}/fixed_transcript_400_{charging_rate}_{seed}.tsv")


if __name__ == "__main__":
    single_codon(int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4])

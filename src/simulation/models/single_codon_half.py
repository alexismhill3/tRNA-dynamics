import pinetree as pt
import sys


def single_codon_half(seed, charging_rate, time_limit, output_dir, pol_speed):

    tRNA = {"AAA": {"TTT": {"charged": 100, "uncharged": 0}},}
    seq = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    sim = pt.Model(cell_volume=8e-16)
    sim.seed(seed)
    sim.add_polymerase(name="rnapol", copy_number=10, speed=pol_speed, footprint=10)
    sim.add_ribosome(copy_number=100, speed=3, footprint=15)

    plasmid = pt.Genome(name="plasmid", length=361)

    plasmid.add_promoter(name="phi1", start=1, stop=10,
                         interactions={"rnapol": 2e7})
    plasmid.add_promoter(name="phi1", start=1, stop=10,
                         interactions={"rnapol": 2e7})
    plasmid.add_terminator(name="t1", start=360, stop=361,
                           efficiency={"rnapol": 1.0})
    plasmid.add_gene(name="proteinX", start=31, stop=351,
                     rbs_start=(31 - 15), rbs_stop=31, rbs_strength=1e6)
    plasmid.add_sequence(seq=seq)

    sim.register_genome(plasmid)

    sim.add_trna(tRNA, charging_rate)

    sim.simulate(time_limit=time_limit, time_step=5, output=f"{output_dir}/single_gene_single_codon_0.5_{charging_rate}_{pol_speed}_{seed}.tsv")


if __name__ == "__main__":
    single_codon_half(int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]))
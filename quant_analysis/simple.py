import pinetree as pt

sim = pt.Model(cell_volume=8e-16)
sim.seed(34)
sim.add_polymerase(name="rnapol", copy_number=30, speed=1, footprint=10)
#sim.add_ribosome(copy_number=100, speed=1, footprint=10)

plasmid = pt.Genome(name="plasmid", length=450,
                    transcript_degradation_rate_ext=2e-4,
                    rnase_speed=1,
                    rnase_footprint=10)

# plasmid = pt.Genome(name="plasmid", length=300)

plasmid.add_promoter(name="p1", start=1, stop=10,
                     interactions={"rnapol": 2e5})
plasmid.add_terminator(name="t1", start=449, stop=450,
                       efficiency={"rnapol": 1.0})

plasmid.add_gene(name="proteinX", start=26, stop=448,
                 rbs_start=(26 - 15), rbs_stop=26, rbs_strength=1e7)

sim.register_genome(plasmid)

sim.simulate(time_limit=50000, time_step=1,
             output="simple4.tsv")

import yaml
import pinetree as pt

def _load_conf(config_file):
    with open(config_file, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as yaml_error:
            print(yaml_error)
        return data


def load_genome(config_file):
    """
    Initialize a Genome object from a yaml config file.
    """
    data = _load_conf(config_file)
    
    constructor_args = data["genome"]
    genomes = []
    # if the simulation contains more than one phage, we'll create them all now
    for i in range(constructor_args["copy_number"]):
        if "transcript_degradation_rate_ext" in constructor_args:
            genome = pt.Genome(name = constructor_args["name"], length = constructor_args["length"], transcript_degradation_rate_ext = float(constructor_args["transcript_degradation_rate_ext"]), rnase_speed = constructor_args["rnase_speed"], rnase_footprint = constructor_args["rnase_footprint"])
        else:
            genome = pt.Genome(name = constructor_args["name"], length = constructor_args["length"])
        
        ## add elements to the genome

        if "promoters" in data:
            promoters = data["promoters"]
            for promoter in promoters:
                start = promoter["start"]
                stop = promoter["stop"]
                genome.add_promoter(name = promoter["name"], start = start, stop = stop, interactions = promoter["interactions"])
        
        if "genes" in data:
            genes = data["genes"]
            for gene in genes:
                start = gene["start"]
                genome.add_gene(name = gene["name"], start = start, stop = gene["stop"], rbs_start = start + gene["rbs"], rbs_stop = start, rbs_strength = float(gene["rbs_strength"]))

        if "terminators" in data:
            terminators = data["terminators"]
            for terminator in terminators:
                genome.add_terminator(name = terminator["name"], start = terminator["start"], stop = terminator["stop"], efficiency = terminator["interactions"])

        if "rnase_sites" in data:
            rnase_sites = data["rnase_sites"]
            for rnase_site in rnase_sites:
                genome.add_rnase_site(name = rnase_site["name"], start = rnase_site["start"], stop = rnase_site["start"] + 10, rate = float(rnase_site["rnase_strength"]))

        if "mask" in data:
            mask = data["mask"]
            genome.add_mask(start = mask["start"], interactions = mask["interactions"])
        
        if "seq" in data:
            genome.add_sequence(data["seq"])
            
        genomes.append(genome)

    return genomes


def load_model_with_genomes(config_file, genomes):
    """
    Initialize a Model object with a pre-built Genome (or Genomes). 
    """
    data = _load_conf(config_file)
    model = pt.Model(cell_volume = float(data["cell_volume"]))

    ## register genome(s) with the model
    for genome in genomes:
        model.register_genome(genome)

    ## configure model

    if "polymerases" in data:
        for polymerase in data["polymerases"]:
            model.add_polymerase(name = polymerase["name"], footprint = polymerase["footprint"], speed = polymerase["speed"], copy_number = polymerase["copy_number"])
    
    if "ribosomes" in data:
        for ribosome in data["ribosomes"]:
            model.add_ribosome(footprint = ribosome["footprint"], speed = ribosome["speed"], copy_number = ribosome["copy_number"])

    if "species" in data:
        for species_ in data["species"]:
            model.add_species(name = species_["name"], copy_number = species_["copy_number"])

    if "reactions" in data:
        for reaction in data["reactions"]:
            model.add_reaction(rate_constant = float(reaction["rate_constant"]), reactants = reaction["reactants"], products = reaction["products"])

    if "seed" in data:
        model.seed(data["seed"])
    
    if "tRNA" in data:
        tRNA = data["tRNA"]
        model.add_trna(tRNA["codons"], tRNA["charging_rate"])

    return model


def load_model(config_file):
    """
    Initialize a Model object from a yaml config file. If genome information is present in the config, this will attempt
    to build the genome (or genomes) and register those with the model. Makes no guarantees about whether or not any 
    genomes were actually registered.
    """
    data = _load_conf(config_file)
    genomes = load_genome(config_file) if "genome" in data else []
    model = load_model_with_genomes(config_file, genomes)
    return model
    

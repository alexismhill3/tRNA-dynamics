from distutils.command.config import config
import yaml
from typing import Optional, Tuple
import pinetree as pt

class TwoCodonSingleTranscriptSim():

    def __init__(self, 
                config_file: str, 
                trna_charging_rates: Optional[Tuple] = None,
                ribosome_binding_rate: Optional[float] = None,
                ribosome_copy_number: Optional[int] = None,
                transcript_copy_number: Optional[int] = None,
                total_trna: Optional[int] = None,
                ribosome_params: Optional[Tuple] = (1, 15), # speed, footprint
                cell_volume: Optional[float] = 8e-16,
                ):
        self.simulation_data = self._load_config(config_file)
        self.ribosome_params = ribosome_params
        self.model = pt.Model(cell_volume=cell_volume)
        
        self.transcript_copy_number = transcript_copy_number if transcript_copy_number \
                                 is not None else self.simulation_data["transcript_copy_number"]
        self.ribosome_binding_rate = ribosome_binding_rate if ribosome_binding_rate \
                                 is not None else self.simulation_data["ribosome_binding_rate"]
        self.total_trna = total_trna if total_trna \
                                 is not None else self.simulation_data["total_trna"]
        self.trna_charging_rates = trna_charging_rates if trna_charging_rates \
                                 is not None else self.simulation_data["trna_charging_rates"]
        self.ribosome_copy_number = ribosome_copy_number if ribosome_copy_number \
                                 is not None else self.simulation_data["ribosome_copy_number"]

    def _load_config(self, config_file):
        with open(config_file, "r") as stream:
            data = yaml.safe_load(stream)
        return data

    def _add_transcripts(self):
        ribosome_footprint = self.ribosome_params[1]
        # convert CDS length to nt and add 50 nt buffer (30 upstream, 20 downstream)
        transcript_len = self.simulation_data["transcript_len"] * 3 + 50
        i = 0
        # pinetree can only add one transcript at a time for some reason, so do this in a loop
        while i < self.transcript_copy_number:
            transcript = pt.Transcript("transcript", transcript_len)
            transcript.add_gene(name="proteinX", start=31, stop=transcript_len - 20,
                                rbs_start=(31 - ribosome_footprint), rbs_stop=31, 
                                rbs_strength=self.ribosome_binding_rate)
            transcript.add_seq(seq=self.simulation_data["transcript_seq"])
            self.model.register_transcript(transcript)
            i += 1
    
    def _add_trna(self):
        trna1_proportion = self.simulation_data["trna_odds"]["TTT"] / 100
        trna2_proportion = self.simulation_data["trna_odds"]["ATA"] / 100
        counts_map = {"TTT": [int(self.total_trna * trna1_proportion), 0], 
                      "ATA": [int(self.total_trna * trna2_proportion), 0]}
        trna_map = {"AAA": ["TTT"], "TAT": ["ATA"]}
        rates_map = {"TTT": self.charging_rates[0], "ATA": self.charging_rates[1]}
        self.model.add_trna(trna_map, counts_map, rates_map)
    
    def _add_ribosomes(self):
        speed, footprint = self.ribosome_params
        self.model.add_ribosome(copy_number=self.ribosome_copy_number, speed=speed, footprint=footprint)
    
    def _format_filename(self, seed):
        base = self.simulation_data["config_filename"].split(".yaml")[0]
        return f"{base}_{self.transcript_copy_number}_{self.ribosome_copy_number}_{self.total_trna} \
                _{self.ribosome_binding_rate}_{self.trna_charging_rates}_{seed}.tsv"

    def run(self, output_dir: str, seed: int, time_limit: Optional[int] = None, time_step: Optional[float] = None):
        if time_limit is None:
            time_limit = self.simulation_data["time_limit"]
        if time_step is None:
            time_step = self.simulation_data["time_step"]
        self.model.seed(seed)
        self._add_transcripts()
        self._add_trna()
        self._add_ribosomes()
        outfile = self._format_filename(seed)
        self.model.simulate(time_limit=time_limit, time_step=time_step, output=f"{output_dir}/{outfile}")
        
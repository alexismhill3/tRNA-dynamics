import yaml
import random
from typing import Dict, Tuple, Optional

class SerializeTwoCodonSingleTranscript():

    def __init__(self, 
                 transcript_len: int, 
                 codon_comp: Tuple, 
                 trna_proportion: Tuple, 
                 seed: Optional[int] = 4, 
                 **kwargs):
        self.transcript_len = transcript_len
        self.codon1, self.codon2 = codon_comp
        self.trna1, self.trna2 = trna_proportion
        self.seed = seed
        self.params = kwargs
        self.params["transcript_len"] = transcript_len
        self.params["trna_proportion"] = {"TTT": self.trna1, "ATA": self.trna2}
        self.params["transcript_seq"] = self._format_transcript()
        self.params["config_filename"] = self._format_filename()

    def _format_transcript(self):
        codons = ["AAA"] * int(self.transcript_len * self.codon1) \
                 + ["TAT"] * int(self.transcript_len * self.codon2)
        random.Random(self.seed).shuffle(codons)
        return "A"*30 + "".join(codons) + "A"*20

    def _format_filename(self):
        base = "two_codon_single_transcript"
        return f"{base}_{self.codon1}_{self.codon2}_{self.trna1}_{self.trna2}.yaml"
    
    def filename(self):
        return self._format_filename()

    def serialize(self, dir: str):
        with open(f"{dir}/{self._format_filename()}", "w") as stream:
            yaml.dump(self.params, stream)

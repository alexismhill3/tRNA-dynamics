#!/usr/bin/env bash

fractions=(10 25 40 50 60 75 85 90 95 99)
counts_good=(55 60 70 80 85 90 95 99)

for frac in ${fractions[@]}; do
    for count_good in ${counts_good[@]}; do
        for k in 1 2 3; do 
        count_bad=$(( 100 - count_good ))
        echo "python3 two_codon_fixed_transcript_rbs.py ""$k"" ../output/two_codon_var_trna_ratios 10000.0 yaml/two_codon/two_codon_fixed_transcript_""$frac""_""$count_good""_"""$count_bad"_100.0_100.0_200_1200_5.0.yaml" >> two_codon_var_trna_ratios.txt; 
        done; 
    done; 
done

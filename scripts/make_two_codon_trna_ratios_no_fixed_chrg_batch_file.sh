#!/usr/bin/env bash

fractions=(10 25 40 50 60 75 85 90 95 99)
counts_good=(55 60 70 80 85 90 95 99)
charging_rates=(10.0 100.0 1000.0 10000.0 100000.0 1000000.0 10000000.0)

for frac in ${fractions[@]}; do
    for count_good in ${counts_good[@]}; do
        for charging_rate in ${charging_rates[@]}; do
            for k in 1 2 3; do 
                count_bad=$(( 100 - count_good ))
                echo "python3 two_codon_fixed_transcript_rbs_chrg.py ""$k"" ../output/two_codon_var_trna_ratios_var_charg_fixed_rbs 10000.0 ""$charging_rate"" yaml/two_codon_unfixed_chrg/two_codon_fixed_transcript_""$frac""_""$count_good""_"""$count_bad"_200_1200_5.0.yaml" >> two_codon_var_trna_ratios_var_charg_fixed_rbs.txt; 
            done;
        done; 
    done; 
done

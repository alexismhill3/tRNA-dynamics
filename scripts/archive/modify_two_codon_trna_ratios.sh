#!/usr/bin/env bash

fractions=(10 25 40 50 60 75 85 90 95 99)
counts_good=(55 60 70 80 85 90 95 99)

for frac in ${fractions[@]}; do
    for count_good in ${counts_good[@]}; do
        count_bad=$(( 100 - count_good ))
        python3 modify_two_codon_trna_ratios.py $frac $count_good $count_bad
    done
done

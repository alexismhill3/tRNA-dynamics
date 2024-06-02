#!/bin/bash
#SBATCH -J trna-june-02             # job name
#SBATCH -o june-02-2024.o%j         # output and error file name (%j expands to SLURM jobID)
#SBATCH -N 5                        # number of nodes requested
#SBATCH -n 600                      # total number of tasks to run in parallel
#SBATCH -p normal                   # queue (partition) 
#SBATCH -t 10:00:00                 # run time (hh:mm:ss) 
#SBATCH -A MCB24023                 # Allocation name to charge job against

module load launcher
source /work/07227/hilla3/ls6/env/bin/activate

export LAUNCHER_WORKDIR=/work/07227/hilla3/ls6/tRNA-dynamics
export LAUNCHER_JOB_FILE=/work/07227/hilla3/ls6/tRNA-dynamics/tacc/launcher/june-02-2024.txt 

${LAUNCHER_DIR}/paramrun
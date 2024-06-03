#!/bin/bash
#SBATCH -J trna-may-28-b            # job name
#SBATCH -o may-28-2024-b.o%j        # output and error file name (%j expands to SLURM jobID)
#SBATCH -N 5                        # number of nodes requested
#SBATCH -n 600                      # total number of tasks to run in parallel
#SBATCH -p normal                   # queue (partition) 
#SBATCH -t 20:00:00                 # run time (hh:mm:ss) 
#SBATCH -A MCB24023                 # Allocation name to charge job against

module load launcher
source /work/07227/hilla3/ls6/env/bin/activate

export LAUNCHER_WORKDIR=/work/07227/hilla3/ls6/tRNA-dynamics
export LAUNCHER_JOB_FILE=/work/07227/hilla3/ls6/tRNA-dynamics/tacc/launcher/may-28-2024-b.txt 

${LAUNCHER_DIR}/paramrun
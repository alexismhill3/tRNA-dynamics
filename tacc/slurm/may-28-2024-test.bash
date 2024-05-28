#!/bin/bash
#SBATCH -J trna-may-28-test         # job name
#SBATCH -o launcher.o%j             # output and error file name (%j expands to SLURM jobID)
#SBATCH -N 1                        # number of nodes requested
#SBATCH -n 10                       # total number of tasks to run in parallel
#SBATCH -p development              # queue (partition) 
#SBATCH -t 00:30:00                 # run time (hh:mm:ss) 
#SBATCH -A MCB24023                 # Allocation name to charge job against

module load launcher
source /work/07227/hilla3/ls6/tRNA-dynamics/env/bin/activate

export LAUNCHER_WORKDIR=/work/07227/hilla3/ls6/tRNA-dynamics
export LAUNCHER_JOB_FILE=/work/07227/hilla3/ls6/tRNA-dynamics/tacc/launcher/may-28-2024-test.txt 

${LAUNCHER_DIR}/paramrun
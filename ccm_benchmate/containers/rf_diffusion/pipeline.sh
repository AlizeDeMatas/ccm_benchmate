#!/bin/bash

conda activate dl_binder_design
set -euo pipefail

pdb_path=$3
hotspots=$4
min_length=$5
max_length=$6
num_structs=$7
seq_per_struct=$8
output_dir="$9/${run_name}/"

script_dir="dl_binder_design/helper_scripts/"

contig=$(python $script_dir/get_contigs.py "$pdb_path")
bash $script_dir/rfdiffusion.sh "$run_name" "$output_dir" "$pdb_path" "$contig" "$hotspots" "$min_length" "$max_length" "$num_structs"
bash $script_dir/proteinmpnn.sh "$run_name" "$output_dir" "$seq_per_struct" "$output_dir/rfdiffusion/"
bash $script_dir/af2.sh "$run_name" "$output_dir" "$output_dir/proteinmpnn/"


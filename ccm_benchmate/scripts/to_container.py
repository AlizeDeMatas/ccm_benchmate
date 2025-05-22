import argparse
import subprocess
from pathlib import Path
import shutil

def parse_directories(dirs):
    """Parse directory argument in the format 'source:target'."""
    dir_pairs = []
    if dirs:
        for dir_pair in dirs:
            if ":" not in dir_pair:
                raise ValueError(f"Directory pair '{dir_pair}' must be in 'source:target' format")
            src, tgt = dir_pair.split(":", 1)
            src_path = Path(src).resolve()
            if not src_path.exists():
                raise FileNotFoundError(f"Source directory '{src}' does not exist")
            if not src_path.is_dir():
                raise ValueError(f"Source path '{src}' is not a directory")
            dir_pairs.append((src, tgt))
    return dir_pairs

def parse_scripts(scripts):
    """Parse script files and validate their existence."""
    script_files = []
    if scripts:
        for script in scripts:
            script_path = Path(script).resolve()
            if not script_path.exists():
                raise FileNotFoundError(f"Script file '{script}' does not exist")
            if not script_path.is_file():
                raise ValueError(f"'{script}' is not a file")
            script_files.append(script_path)
    return script_files

def generate_def_file(yaml_file, scripts, output_file, directories, runtime):
    """Generate a Singularity/Apptainer definition file."""
    yaml_path = Path(yaml_file).resolve()
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML file '{yaml_file}' does not exist")
    if not yaml_path.is_file():
        raise ValueError(f"'{yaml_file}' is not a file")

    env_name = None
    with open(yaml_path, 'r') as f:
        first_line = f.readline().strip()
        if first_line.startswith('name:'):
            env_name = first_line.split('name:')[1].strip()

    if not env_name:
        raise ValueError("Could not extract environment name from YAML file")

    def_content = [
        f"Bootstrap: docker",
        f"From: continuumio/miniconda3",
        "",
        f"%files",
        f"    {yaml_path.name} /opt/{yaml_path.name}"
    ]

    # Add scripts to %files section
    for script in scripts:
        def_content.append(f"    {script} /opt/{Path(script).name}")

    # Add directories to %files section
    for src, tgt in directories:
        def_content.append(f"    {src} {tgt}")

    def_content.extend([
        "",
        f"%post",
        f"    /opt/conda/bin/conda env create -f /opt/{yaml_path.name}",
        f"    conda init",
        "",
        f"%runscript",
        f"    exec /opt/conda/envs/{env_name}/bin/\"$@\"",
        "",
        f"%environment",
        f"    export PATH=/opt/conda/envs/{env_name}/bin:$PATH",
    ])

    # Write the definition file
    with open(output_file, 'w') as f:
        f.write("\n".join(def_content))

    print(f"Generated {runtime} definition file: {output_file}")

def build_container(runtime, def_file, container_name):
    """Build the Singularity/Apptainer container using subprocess."""
    # Check if the runtime is available
    if not shutil.which(runtime):
        raise RuntimeError(f"{runtime} not found in PATH. Please ensure it is installed.")

    # Ensure the definition file exists
    def_path = Path(def_file).resolve()
    if not def_path.exists():
        raise FileNotFoundError(f"Definition file '{def_file}' does not exist")

    # Build the container
    container_path = f"{container_name}.sif"
    build_cmd = [runtime, "build", container_path, def_file]
    print(f"Running build command: {' '.join(build_cmd)}")

    try:
        result = subprocess.run(
            build_cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"Successfully built container: {container_path}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error building container: {e.stderr}")
        raise


parser = argparse.ArgumentParser(description="Generate and optionally build a Singularity/Apptainer container from a Conda YAML.")
parser.add_argument("--yaml", required=True, help="Path to the Conda environment YAML file")
parser.add_argument("--scripts", action="append", help="Script files to include in the container")
parser.add_argument("--output", default="Singularity.def", help="Output definition file name (default: Singularity.def)")
parser.add_argument("--dirs", action="append", help="Directories to copy in 'source:target' format (e.g., /local/data:/data)")
parser.add_argument("--runtime", choices=["singularity", "apptainer"], default="singularity", help="Container runtime (default: singularity)")
parser.add_argument("--build", action="store_true", help="Build the container after generating the definition file")
parser.add_argument("--container-name", help="Name for the output container file (default: derived from YAML env name)")
args = parser.parse_args()

try:
    directories = parse_directories(args.dirs)
    scripts = parse_scripts(args.scripts)
    env_name = generate_def_file(args.yaml, scripts, args.output, directories, args.runtime)
    if args.build:
        container_name = args.container_name or env_name
        build_container(args.runtime, args.output, container_name)
except Exception as e:
    print(f"Error: {e}")
    exit(1)
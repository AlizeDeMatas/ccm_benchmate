# Container Runner Module
A module for running Singularity/Apptainer or Docker containers with support for local and SLURM cluster execution.

## Overview
The `ContainerRunner` class provides a unified interface for:
- Running containers locally
- Submitting container jobs to SLURM
- Managing bind mounts and GPU access
- Monitoring SLURM job status

## Usage
### Basic Local Container Execution
```python
from benchmate.container_runner.container_runner import ContainerRunner

# Initialize with engine + container/image
runner = ContainerRunner(
    engine="singularity",  # or "apptainer" or "docker"
    container_path="/path/to/container.sif"  # for singularity/apptainer
)

# Add bind mounts (one host path per bind)
runner.add_bind_mount(
    host_mount="/host/path1",
    container_mount="/container/path1"
)

# Enable GPU support if needed
runner.enable_gpu()

# Run command in container
result = runner.run("echo hello", check=True)
print(result.stdout)
```

### Docker Local Execution

```python
runner = ContainerRunner(
    engine="docker",
    container_path="ubuntu:latest"  # image name
)

# Add bind mounts (one host path per bind)
runner.add_bind_mount(
    host_mount="/host/path1",
    container_mount="/container/path1"
)

# Enable GPU support if needed
runner.enable_gpu()

result = runner.run("echo hello", check=True)
```
### SLURM Cluster Execution

```python
# Submit job to SLURM (Singularity/Apptainer only)
job_id = runner.run_slurm(
    command="python script.py",
    time="01:00:00",
    mem="16G",
    ntasks=1,
    cpus_per_task=4,
    gpus=1,
    additional_sbatch={"partition": "gen_gpu"}
)
```
### SLURM Job Helpers

```python
status = runner.check_slurm_job_status(job_id)
job_info = runner.get_slurm_job_info(job_id)
```
## Key Features
### Container Execution
- Supports Singularity, Apptainer, and Docker
- Configurable bind mounts (one host path per bind)
- GPU support:
  - Singularity/Apptainer: `--nv`
  - Docker: `--gpus all`
- Commands executed via `subprocess.run`
### SLURM Integration
- Submits jobs via `sbatch`
- Validates parameters using Pydantic (`SlurmParams`)
- Supports extra SBATCH parameters with `additional_sbatch`
- Job status/info helpers (`squeue`, `sacct`, `scontrol`)
### Error Handling
- Custom exception classes
- Subprocess error capturing
- SLURM job error handling
## Notes
- Singularity/Apptainer requires a `.sif` file path that exists.
- Docker requires a valid image name.
- Bind mounts require valid host paths.
- SLURM submission requires access to a SLURM cluster and valid SBATCH parameters.
- GPU support requires NVIDIA drivers and appropriate container configuration
- GPU SLURM runs require `enable_gpu()`; if you pass `gpus` without enabling GPU, an error is raised.
- SLURM job submission may require additional configuration based on the cluster setup

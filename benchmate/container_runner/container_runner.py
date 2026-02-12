#add pydantic to requirements
"""
ContainerRunner module for running Singularity/Apptainer or Docker containers locally or with SLURM.
"""

import subprocess
from pathlib import Path
import shlex
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict
import tempfile
import os

class SlurmParams(BaseModel):
    """
    Pydantic model for SLURM parameters used when submitting jobs.
    """
    model_config = ConfigDict(extra='forbid')
    job_name: str = "Container_job"
    time: str = "01:00:00"
    mem: str = "4G"
    output: str = "slurm-%j.out"
    error: str = "slurm-%j.err"
    cpus_per_task: Optional[int] = None
    ntasks: int = 1
    gpus: Optional[int] = None
    nodes: int = 1
    additional_sbatch: Optional[Dict[str, str]] = None

class ContainerError(Exception):
    """Base exception for Container-related errors."""
    pass

class ContainerSubprocessError(ContainerError):
    """Exception raised when an Container subprocess fails."""

    def __init__(self, returncode: int, stderr: str):
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"Container subprocess failed with return code {returncode}: {stderr}")

class ContainerSlurmError(ContainerError):
    """Exception raised for SLURM job-related errors."""
    pass

class ContainerRunner:
    """
    A class to run containers with various configuration options.

    Supports Singularity/Apptainer and Docker engines, with optional SLURM submission.
    """
    def __init__(self, engine, container_path):
        """
        Initialize the container runner.

        Args:
            engine: Container engine ("singularity", "apptainer", or "docker")
            container_path: Path to .sif (for singularity/apptainer) OR image name (for docker)

        Raises:
            ContainerError: If engine is invalid or container path/image is invalid.
        """
        engine = engine.strip().lower()
        if engine not in {"singularity", "docker", "apptainer"}:
            raise ContainerError(f"Unsupported engine: {engine}")
        self.engine = engine

        if engine in {"singularity", "apptainer"}:
            if not Path(container_path).exists():
                raise ContainerError(f"{container_path} does not exist")
            if Path(container_path).suffix != ".sif":
                raise ContainerError("Singularity/Apptainer requires a .sif file")
            self.container_path = container_path
        else:
            self.image_name = container_path

        self.bind_mounts = []
        self.use_gpu = False
        
    def enable_gpu(self):
        """Enable NVIDIA GPU support for the container."""
        self.use_gpu = True

    def add_bind_mount(self, host_mount, container_mount):
        """
        Add a bind mount to the container configuration.

        Args:
            host_mount: Path on the host system
            container_mount: Path inside the container

        Raises:
            ContainerError: If the host path does not exist
        """
        if not Path(host_mount).exists():
            raise ContainerError(f"Host path does not exist: {host_mount}")
        self.bind_mounts.append({"host": host_mount, "container": container_mount})
        
    
    def _build_container_command(self, command_list):
        """
        Build the container command with all configured options.

        Args:
            command_list: Command to run inside the container as a list

        Returns:
            List of command components
        """
        if self.engine in {"singularity", "apptainer"}:
            return self._build_singularity_command(command_list)
        return self._build_docker_command(command_list)
    
    def _build_docker_command(self, command_list):
        """
        Build a Docker command with configured options.

        Args:
            command_list: Command to run inside the container as a list.

        Returns:
            List of command components.
        """
        cmd = ["docker", "run"]
        for bind in self.bind_mounts:
            cmd.append(f"--volume={bind['host']}:{bind['container']}")
        if self.use_gpu:
            cmd += ["--gpus", "all"]
        cmd.append(self.image_name)
        cmd.extend(command_list)
        
        return cmd

    def _build_singularity_command(self, command_list):
        """
        Build a Singularity/Apptainer command with configured options.

        Args:
            command_list: Command to run inside the container as a list.

        Returns:
            List of command components.
        """
        if self.engine == "singularity":
            cmd = ["singularity", "exec"]
        else:
            cmd = ["apptainer", "exec"]
        if self.use_gpu:
            cmd.append("--nv")
        for bind in self.bind_mounts:
            cmd.append(f"--bind={bind['host']}:{bind['container']}")
        cmd.append(self.container_path)
        cmd.extend(command_list)
        return cmd

    def run(self, command, **subprocess_kwargs):
        """
        Run a command in the container.

        Args:
            command: Command to run (string or list).
            **subprocess_kwargs: Additional arguments for subprocess.run.

        Returns:
            CompletedProcess object.

        Raises:
            ContainerSubprocessError: If the subprocess fails.
            ContainerError: If a subprocess error occurs.
        """
        if isinstance(command, str):
            command_list = shlex.split(command)
        else:
            command_list = command
        cmd = self._build_container_command(command_list)
        try:
            result = subprocess.run(cmd, **subprocess_kwargs, capture_output=True, text=True)
            if result.returncode != 0:
                raise ContainerSubprocessError(result.returncode, result.stderr)
            return result
        except subprocess.SubprocessError as e:
            raise ContainerError(f"Subprocess error: {e}")

    def run_slurm(self, command, **slurm_kwargs):
        """
        Submit a command to run in the container as a SLURM job.

        Args:
            command: Command to run (string or list).
            **slurm_kwargs: SLURM parameters validated by SlurmParams.

        Returns:
            Job ID from sbatch submission.

        Raises:
            ContainerError: If engine is docker.
            ContainerSlurmError: If SLURM submission fails.
        """
        if self.engine == "docker":
            raise ContainerError("SLURM is not supported for Docker")
        params = SlurmParams(**slurm_kwargs)
        if isinstance(command, str):
            command_list = shlex.split(command)
        else:
            command_list = command
        container_cmd = " ".join(self._build_container_command(command_list))

        lines = ["#!/bin/bash"]

        lines.append(f"#SBATCH --job-name={params.job_name}")
        lines.append(f"#SBATCH --time={params.time}")
        lines.append(f"#SBATCH --mem={params.mem}")
        lines.append(f"#SBATCH --output={params.output}")
        lines.append(f"#SBATCH --error={params.error}")
        lines.append(f"#SBATCH --ntasks={params.ntasks}")
        lines.append(f"#SBATCH --nodes={params.nodes}")

        if params.cpus_per_task: lines.append(f"#SBATCH --cpus-per-task={params.cpus_per_task}")

        if self.use_gpu and params.gpus is None:
            lines.append(f"#SBATCH --gpus 1")
        elif self.use_gpu:
            lines.append(f"#SBATCH --gpus {params.gpus}")
        elif params.gpus != None:
            raise ContainerSlurmError(f"GPU flag is not set but gpu paramter was provided for SLURM job") 

        if params.additional_sbatch:
            for key, value in params.additional_sbatch.items():
                lines.append(f"#SBATCH --{key}={value}")

        lines.append("")
        lines.append("module load Singularity" if self.engine == "singularity" else "module load Apptainer")
        lines.append(container_cmd)

        script = "\n".join(lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            result = subprocess.run(
                ["sbatch", script_path],
                capture_output=True,
                text=True,
                check=True
            )
            job_id = result.stdout.strip().split()[-1]
            return job_id
        except subprocess.SubprocessError as e:
            raise ContainerSlurmError(f"SLURM submission failed (code {e.returncode}): {e.stderr.strip()}")
        finally:
            os.unlink(script_path)

    def check_slurm_job_status(self, job_id: str) -> str:
        """
        Check the status of a SLURM job.

        Args:
            job_id: SLURM job ID

        Returns:
            Job status (e.g., PENDING, RUNNING, COMPLETED, FAILED)

        Raises:
            ContainerSlurmError: If job status check fails
        """
        try:
            result = subprocess.run(
                ["squeue", "-j", job_id, "-h", "-o", "%t"],
                capture_output=True,
                text=True,
                check=True
            )
            status = result.stdout.strip()
            if not status:
                # Check if job is completed or failed
                result = subprocess.run(
                    ["sacct", "-j", job_id, "--format=State", "-P", "-n"],
                    capture_output=True,
                    text=True
                )
                status_lines = result.stdout.strip().split('\n')
                if status_lines and status_lines[0]:
                    return status_lines[0]
                return "COMPLETED"  # Assume completed if not found
            return status
        except subprocess.SubprocessError as e:
            raise ContainerSlurmError(f"Failed to check SLURM job status: {str(e)}")

    def get_slurm_job_info(self, job_id: str) -> Dict[str, str]:
        """
        Get detailed information about a SLURM job.

        Args:
            job_id: SLURM job ID

        Returns:
            Dictionary containing job information

        Raises:
            ContainerSlurmError: If job info retrieval fails
        """
        try:
            result = subprocess.run(
                ["scontrol", "show", "job", job_id],
                capture_output=True,
                text=True,
                check=True
            )
            job_info = {}
            for line in result.stdout.split('\n'):
                for item in line.strip().split():
                    if '=' in item:
                        key, value = item.split('=', 1)
                        job_info[key] = value
            return job_info
        except subprocess.SubprocessError as e:
            raise ContainerSlurmError(f"Failed to get SLURM job info: {str(e)}")


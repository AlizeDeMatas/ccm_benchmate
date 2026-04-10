---
layout: default
title: Launcher Usage
parent: Containerization
nav_order: 4
---

# Benchmate Container Launcher Usage

This document explains how to use the Benchmate launcher script for Docker and Singularity / Apptainer. Note this is specifically designed for the `full` version of the Benchmate Docker build, and has been partially tested with `db-cpu`. It is meant to make running PostgreSQL easier so not really helpful for the `base` and `gpu-nodb` builds.

## Get The Launcher Script

While you do not install specifc packages and dependencies, you do need the launcher script.

Download it and make it executable:

```bash
curl -L -o benchmate.sh https://github.com/ccmbioinfo/ccm_benchmate/blob/master/containerization/benchmate.sh
chmod +x benchmate.sh
```

The launcher is the normal entrypoint. It handles PostgreSQL setup automatically, reuses the same database directory across runs, and passes your command into the container.

## Docker

### Install

Install Docker Desktop or another Docker runtime that supports Linux containers.

You will also need the Benchmate image locally, for example:

```bash
docker pull rohanahkhan/ccm-benchmate:full
```

If your local image tag is different, pass it with `--container`.

### Where `PGDATA` Should Live

For Docker, choose a host directory that will hold the PostgreSQL data files and reuse the same path across runs.

Example:

```bash
mkdir -p /tmp/benchmate_pgtest
chmod 700 /tmp/benchmate_pgtest
```

The launcher mounts that host directory into the container at `/work/pgdata` by default.

### Recommended First Run

The recommended first run is an interactive shell:

```bash
./benchmate.sh --runtime docker --container rohanahkhan/ccm-benchmate:full --db-dir /tmp/benchmate_pgtest -- bash
```

What happens on the first run:

- the database directory is created if needed
- PostgreSQL is initialized if the directory is empty
- PostgreSQL starts
- the database is created if needed
- the `vector` and `rdkit` extensions are ensured
- `DATABASE_URL` is exported

On later runs, reuse the same `--db-dir`.

### Quick Docker Checks

Inside the shell, useful checks are:

```bash
echo "$DATABASE_URL"
psql -p 5544 -d benchmate -c '\dx'
psql -p 5544 -d benchmate -c "SELECT '[1,2,3]'::vector;"
psql -p 5544 -d benchmate -c "SELECT mol_to_smiles('c1ccccc1'::mol);"
```

A one-shot command also works:

```bash
./benchmate.sh --runtime docker --container rohanahkhan/ccm-benchmate:full --db-dir /tmp/benchmate_pgtest -- python -c "import os; print(os.environ['DATABASE_URL'])"
```

## Singularity / Apptainer

### Install And HPC Setup

Start an interactive allocation first, then load Singularity:

```bash
srun --cpus-per-task 4 --mem 8G --time 24:00:00 --constraint=AlmaLinux8 --pty bash
module load Singularity
```

If you want to build a local `.sif` from Docker Hub, set cache and temp directories first:

```bash
export SINGULARITY_CACHEDIR=/path/to/singularity_cache
export SINGULARITY_TMPDIR=/path/to/singularity_tmp
mkdir -p "$SINGULARITY_CACHEDIR" "$SINGULARITY_TMPDIR"
```

Then pull the image (this will take awhile):

```bash
singularity pull /hpf/largeprojects/ccmbio/students/rkhan/benchmate_package/mar19/ccm-benchmate_full.sif docker://rohanahkhan/ccm-benchmate:full
```

### Where `PGDATA` Should Live

For Singularity / Apptainer, choose a writable path on a filesystem that PostgreSQL accepts. The directory must allow final permissions of `700` or `750`.

Reuse the same `--db-dir` across runs.

### Passwd File And Runtime Notes

The launcher creates a reusable `./benchmate.passwd` file in the current working directory and binds it to `/etc/passwd`.

This is needed because Singularity runs as the invoking HPC UID, and `initdb` requires that Linux user to be resolvable inside the container.

The launcher also normalizes locale to `C.UTF-8`.

### Recommended First Run

The recommended first run is an interactive shell:

```bash
./benchmate.sh \
  --runtime singularity \
  --container /hpf/largeprojects/ccmbio/students/rkhan/benchmate_package/mar19/ccm-benchmate_full.sif \
  --db-dir /hpf/largeprojects/ccm_dccforge/dccdipg/Common/annotation_hg38/DRAGEN_genes/test/test \
  -- bash
```

Inside the shell, useful checks are:

```bash
echo "$DATABASE_URL"
psql -p 5544 -d benchmate -c '\dx'
psql -p 5544 -d benchmate -c "SELECT '[1,2,3]'::vector;"
psql -p 5544 -d benchmate -c "SELECT mol_to_smiles('c1ccccc1'::mol);"
```

A one-shot command also works:

```bash
./benchmate.sh \
  --runtime singularity \
  --container /hpf/largeprojects/ccmbio/students/rkhan/benchmate_package/mar19/ccm-benchmate_full.sif \
  --db-dir /hpf/largeprojects/ccm_dccforge/dccdipg/Common/annotation_hg38/DRAGEN_genes/test/test \
  -- python -c "import os; print(os.environ['DATABASE_URL'])"
```

## Shared Extras

### `--show-command`

Use `--show-command` when you want the launcher to print a raw runtime example of how to run the container without the launcher script. For most use cases the launcher script will get the job done, but if you need a specific invocation that can be used to launch the containers with the database, use this command.

Docker example:

```bash
./benchmate.sh --runtime docker --db-dir /tmp/benchmate_pgtest --show-command -- bash
```

Singularity example:

```bash
./benchmate.sh --runtime singularity --container /path/to/image.sif --db-dir /path/to/pgdata --show-command -- bash
```

What it means:

- for Docker, the printed command includes PostgreSQL startup logic because each `docker run` starts a fresh container
- for Singularity, the printed command is a follow-up access pattern for cases where PostgreSQL is already running

### Extra Runtime Args

Pass extra runtime flags through the launcher when needed.

Docker examples:

```bash
./benchmate.sh --runtime docker --db-dir /tmp/benchmate_pgtest --docker-arg "--gpus" --docker-arg "all" -- bash
```

```bash
./benchmate.sh --runtime docker --db-dir /tmp/benchmate_pgtest --docker-arg "-p" --docker-arg "5544:5544" -- bash
```

Singularity examples:

```bash
./benchmate.sh --runtime singularity --container /path/to/image.sif --db-dir /path/to/pgdata --singularity-arg "--nv" -- bash
```

```bash
./benchmate.sh --runtime singularity --container /path/to/image.sif --db-dir /path/to/pgdata --bind /some/extra/path:/extra/path -- bash
```

### Passing Your Own Command

Everything after `--` is passed into the container.

Examples:

```bash
./benchmate.sh --runtime docker --db-dir /tmp/benchmate_pgtest -- python myscript.py
```

```bash
./benchmate.sh --runtime singularity --container /path/to/image.sif --db-dir /path/to/pgdata -- psql -p 5544 -d benchmate -c "SELECT current_database();"
```

```bash
./benchmate.sh --runtime docker --db-dir /tmp/benchmate_pgtest -- python -c "import os; print(os.environ['DATABASE_URL'])"
```

### Suggested Quick Tests

After the first successful launcher run, these are good checks:

```bash
psql -p 5544 -d benchmate -c '\dx'
psql -p 5544 -d benchmate -c "SELECT '[1,2,3]'::vector;"
psql -p 5544 -d benchmate -c "SELECT mol_to_smiles('c1ccccc1'::mol);"
```

If you want to confirm the database directory is reused, run the launcher a second time with the same `--db-dir`.

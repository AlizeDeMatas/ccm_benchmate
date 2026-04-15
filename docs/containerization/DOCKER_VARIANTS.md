---
layout: default
title: Docker Variants
parent: Containerization
nav_order: 3
---

# Benchmate Docker Variants

This document covers the three additional Benchmate image variants beyond the existing top-level full image.

## Image Variants

- `full`: database and GPU support, built from the repo-root `Dockerfile`
- `db-cpu`: database support, no GPU stack
- `gpu-nodb`: GPU stack, no in-container PostgreSQL
- `base`: no database support and no GPU stack

## Build Commands

Build from the repo root so Docker can access the full repository as build context.

### Base

```bash
# Build
docker buildx build --no-cache --platform linux/amd64 -f containerization/docker/Dockerfile.base -t ccm-benchmate:base  --load .

# Tag
docker tag ccm-benchmate:base rohanahkhan/ccm-benchmate:base

# Push
docker push rohanahkhan/ccm-benchmate:base
```

### DB + CPU

```bash
# Build
docker buildx build --no-cache --platform linux/amd64 -f containerization/docker/Dockerfile.db-cpu -t ccm-benchmate:db-cpu  --load .

# Tag
docker tag ccm-benchmate:db-cpu rohanahkhan/ccm-benchmate:db-cpu

# Push
docker push rohanahkhan/ccm-benchmate:db-cpu
```

This image keeps compatibility with `containerization/benchmate.sh` and `containerization/benchmate-run.sh`.

### GPU + No DB

```bash
# Build
docker buildx build --no-cache --platform linux/amd64 -f containerization/docker/Dockerfile.gpu-nodb -t ccm-benchmate:gpu-nodb --load .

# Tag
docker tag ccm-benchmate:gpu-nodb rohanahkhan/ccm-benchmate:gpu-nodb

# Push
docker push rohanahkhan/ccm-benchmate:gpu-nodb
```

## Quick Binary Checks

These checks confirm that the expected executables are on `PATH` for each image.

### Base

```bash
docker run --rm --platform linux/amd64 --entrypoint /bin/bash ccm-benchmate:base -lc 'echo $PATH; command -v python; command -v blastn; command -v mmseqs; command -v foldseek'
```

### DB + CPU

```bash
docker run --rm --platform linux/amd64 --entrypoint /bin/bash ccm-benchmate:db-cpu -lc 'echo $PATH; command -v python; command -v postgres; command -v initdb; command -v pg_ctl; command -v psql'
```

### GPU + No DB

```bash
docker run --rm --platform linux/amd64 --entrypoint /bin/bash ccm-benchmate:gpu-nodb -lc 'echo $PATH; command -v python; python -c "import torch; print(torch.__version__)"'
```

## Smoke Tests

### Base

Confirm the package imports and that a core non-DB / non-GPU Benchmate module works:

```bash
docker run --rm --platform linux/amd64 \
  --entrypoint /bin/bash \
  ccm-benchmate:base \
  -lc '/opt/conda/bin/python - <<'"'"'PY'"'"'
import benchmate
from benchmate.ranges.ranges import Range
from benchmate.ranges.genomicranges import GenomicRange

print("benchmate import ok")
r1 = Range(10, 20)
r2 = Range(15, 25)
gr = GenomicRange("chr1", 10, 20, "+", {"gene": "TEST1"})

print("ranges import ok")
print("range overlap", r1.overlaps(r2, type="any"))
print("genomic range", gr)
PY'
```

### DB + CPU

Use a fresh test data directory:

```bash
rm -rf /tmp/benchmate_pgtest_db_cpu
mkdir -p /tmp/benchmate_pgtest_db_cpu
chmod 700 /tmp/benchmate_pgtest_db_cpu
```

Knowledge base schema test:

```bash
docker run --rm \
  --platform linux/amd64 \
  -v /tmp/benchmate_pgtest_db_cpu:/work/pgdata \
  --entrypoint /bin/bash \
  ccm-benchmate:db-cpu \
  -lc 'initdb -D /work/pgdata >/dev/null && pg_ctl -D /work/pgdata -l /work/pgdata/postgres.log -o "-p 5544" start >/dev/null && until pg_isready -p 5544 >/dev/null 2>&1; do sleep 1; done && createdb -p 5544 benchmate_demo && psql -p 5544 -d benchmate_demo -c "CREATE EXTENSION IF NOT EXISTS vector;" >/dev/null && psql -p 5544 -d benchmate_demo -c "CREATE EXTENSION IF NOT EXISTS rdkit;" >/dev/null && /opt/conda/bin/python - <<'"'"'PY'"'"'
from sqlalchemy import create_engine, inspect
from benchmate.knowledge_base.knowledge_base import KnowledgeBase

engine = create_engine("postgresql+psycopg2://localhost:5544/benchmate_demo")
kb = KnowledgeBase(engine)
kb._create_kb()
print(inspect(engine).get_table_names())
PY'
```

`pgvector` test:

```bash
docker run --rm \
  --platform linux/amd64 \
  -v /tmp/benchmate_pgtest_db_cpu:/work/pgdata \
  --entrypoint /bin/bash \
  ccm-benchmate:db-cpu \
  -lc 'pg_ctl -D /work/pgdata -l /work/pgdata/postgres.log -o "-p 5544" start >/dev/null || true; until pg_isready -p 5544 >/dev/null 2>&1; do sleep 1; done; /opt/conda/bin/psql -p 5544 -d benchmate_demo -c "CREATE TABLE IF NOT EXISTS items (id serial primary key, embedding vector(3)); INSERT INTO items (embedding) VALUES (\$\$[1,2,3]\$\$), (\$\$[2,3,4]\$\$); SELECT * FROM items ORDER BY embedding <-> \$\$[1,1,1]\$\$ LIMIT 2;"'
```

RDKit test:

```bash
docker run --rm \
  --platform linux/amd64 \
  -v /tmp/benchmate_pgtest_db_cpu:/work/pgdata \
  --entrypoint /bin/bash \
  ccm-benchmate:db-cpu \
  -lc 'pg_ctl -D /work/pgdata -l /work/pgdata/postgres.log -o "-p 5544" start >/dev/null || true; until pg_isready -p 5544 >/dev/null 2>&1; do sleep 1; done; /opt/conda/bin/psql -p 5544 -d benchmate_demo -c "SELECT mol_to_smiles(\$\$c1ccccc1\$\$::mol);"'
```

Launcher test:

```bash
containerization/benchmate.sh --runtime docker --container ccm-benchmate:db-cpu --db-dir /tmp/benchmate_pgtest_db_cpu_launcher -- bash
```

### GPU + No DB

Confirm the image contains the expected GPU-side Python stack and can fall back to CPU import/runtime when no GPU is exposed:

```bash
docker run --rm --platform linux/amd64 \
  --entrypoint /bin/bash \
  ccm-benchmate:gpu-nodb \
  -lc '/opt/conda/bin/python - <<'"'"'PY'"'"'
import benchmate
import torch
import transformers
import sentence_transformers
import layoutparser

print("benchmate import ok")
print("torch", torch.__version__)
print("cuda_available", torch.cuda.is_available())
print("transformers", transformers.__version__)
print("sentence_transformers", sentence_transformers.__version__)
print("layoutparser import ok")
PY'
```

If you want to confirm Docker GPU access on a host with NVIDIA runtime configured (untested):

```bash
docker run --rm --platform linux/amd64 --gpus all \
  --entrypoint /bin/bash \
  ccm-benchmate:gpu-nodb \
  -lc 'python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.device_count())"'
```

## Notes

- The repo-root `Dockerfile` remains the canonical `full` image build.
- The `db-cpu` image is the only new variant that includes PostgreSQL, `pgvector`, and `rdkit-postgresql`.
- The `base` and `gpu-nodb` images do not include the DB launcher/runtime expectations from `containerization/benchmate.sh`.
- Modules that require missing GPU or DB dependencies are expected to fail in the reduced variants.

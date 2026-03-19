# Benchmate Docker Image

This document covers how to build the Benchmate container image locally, run a few smoke tests, and optionally push the image to Docker Hub.

## 1. Build

From the repo root:

```bash
docker buildx build --no-cache --platform linux/amd64 -t ccm-benchmate:full --load .
```

`--platform linux/amd64` is recommended when building on macOS and for later Singularity/Apptainer use.

## 2. Quick Binary Check

Confirm that the expected PostgreSQL and Python executables are on `PATH`:

```bash
docker run --rm --platform linux/amd64 --entrypoint /bin/bash ccm-benchmate:full -lc 'echo $PATH; command -v python; command -v postgres; command -v initdb; command -v pg_ctl; command -v psql'
```

## 3. Smoke Tests

Use a fresh test data directory:

```bash
rm -rf /tmp/benchmate_pgtest
mkdir -p /tmp/benchmate_pgtest
chmod 700 /tmp/benchmate_pgtest
```

Interactive test:

```bash
docker run --rm -it \
  --platform linux/amd64 \
  -v /tmp/benchmate_pgtest:/work/pgdata \
  --entrypoint /bin/bash \
  ccm-benchmate:full \
  -lc 'pg_ctl -D /work/pgdata -l /work/pgdata/postgres.log -o "-p 5544" start && python'
```

Knowledge base schema test:

```bash
docker run --rm \
  --platform linux/amd64 \
  -v /tmp/benchmate_pgtest:/work/pgdata \
  --entrypoint /bin/bash \
  ccm-benchmate:full \
  -lc '/opt/conda/bin/python - <<'"'"'PY'"'"'
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
  -v /tmp/benchmate_pgtest:/work/pgdata \
  --entrypoint /bin/bash \
  ccm-benchmate:full \
  -lc '/opt/conda/bin/psql -p 5544 -d benchmate_demo -c "CREATE TABLE IF NOT EXISTS items (id serial primary key, embedding vector(3)); INSERT INTO items (embedding) VALUES (\$\$[1,2,3]\$\$), (\$\$[2,3,4]\$\$); SELECT * FROM items ORDER BY embedding <-> \$\$[1,1,1]\$\$ LIMIT 2;"'
```

RDKit test:

```bash
docker run --rm \
  --platform linux/amd64 \
  -v /tmp/benchmate_pgtest:/work/pgdata \
  --entrypoint /bin/bash \
  ccm-benchmate:full \
  -lc '/opt/conda/bin/psql -p 5544 -d benchmate_demo -c "SELECT mol_to_smiles(\$\$c1ccccc1\$\$::mol);"'
```

## 4. Launcher Test

Once the image is built, test the user-facing launcher:

```bash
containerization/benchmate.sh --runtime docker --container ccm-benchmate:full --db-dir /tmp/benchmate_pgtest_launcher -- bash
```

## 5. Push To Docker Hub

Log in first:

```bash
docker login
```

Tag the image:

```bash
docker tag ccm-benchmate:full rohanahkhan/ccm-benchmate:full
```

Push:

```bash
docker push rohanahkhan/ccm-benchmate:full
```

Adjust the repository or tag names to match the release you want to publish.

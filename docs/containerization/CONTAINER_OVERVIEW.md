---
layout: default
title: Container Overview
parent: Containerization
nav_order: 1
---

# Benchmate Container Overview

This section covers the four Benchmate container images and how to build and use them.

As of April 9, 2026, the Docker Hub images under `rohanahkhan/ccm-benchmate` are up to date with the container files in this repository.

## Image Matrix

- `full`: includes the PostgreSQL stack and the GPU Python stack
- `db-cpu`: includes PostgreSQL support but does not include the GPU stack
- `gpu-nodb`: includes the GPU stack but does not include the PostgreSQL support
- `base`: keeps the lightweight non-DB / non-GPU base install

## Build Locations

The canonical `full` image is still built from the repo-root [Dockerfile](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/Dockerfile).

The other image variants are built from the files under [containerization/docker](https://github.com/ccmbioinfo/ccm_benchmate/tree/master/containerization/docker):

- [Dockerfile.base](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/containerization/docker/Dockerfile.base)
- [Dockerfile.db-cpu](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/containerization/docker/Dockerfile.db-cpu)
- [Dockerfile.gpu-nodb](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/containerization/docker/Dockerfile.gpu-nodb)
- [environment.cpu.yaml](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/containerization/docker/environment.cpu.yaml)
- [requirements.base.txt](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/containerization/docker/requirements.base.txt)
- [requirements.db-cpu.txt](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/containerization/docker/requirements.db-cpu.txt)
- [requirements.gpu-nodb.txt](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/containerization/docker/requirements.gpu-nodb.txt)

## Pull Commands

Pull from Docker Hub repository.

```bash
# full
docker pull rohanahkhan/ccm-benchmate:full

# base
docker pull rohanahkhan/ccm-benchmate:base

# db-cpu
docker pull rohanahkhan/ccm-benchmate:db-cpu 

# gpu-nodb
docker pull rohanahkhan/ccm-benchmate:gpu-nodb
```

## Maintenance Note

If you add, remove, or reorganize dependencies for any image variant, update the matching files in [containerization/docker](https://github.com/ccmbioinfo/ccm_benchmate/tree/master/containerization/docker).

In practice that usually means checking:

- the relevant Dockerfile
- the matching `requirements*.txt`
- the matching `environment*.yaml`
- the build and smoke-test commands in these docs

## Related Pages

- [DOCKER_IMAGE.md](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/docs/containerization/DOCKER_IMAGE.md)
- [DOCKER_VARIANTS.md](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/docs/containerization/DOCKER_VARIANTS.md)
- [LAUNCHER_USAGE.md](https://github.com/ccmbioinfo/ccm_benchmate/blob/master/docs/containerization/LAUNCHER_USAGE.md)

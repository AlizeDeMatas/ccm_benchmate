#!/usr/bin/env bash

set -euo pipefail

RUNTIME="docker"
IMAGE="ccm-benchmate:full"
DB_DIR=""
DB_NAME="benchmate"
DB_PORT="5544"
CONTAINER_DB_DIR="/work/pgdata"
DOCKER_EXTRA_ARGS=()
SINGULARITY_EXTRA_ARGS=()
SHOW_COMMAND=0

usage() {
  cat <<'EOF'
Usage:
  containerization/benchmate.sh --db-dir /path/to/db [options] [-- command...]

Options:
  --runtime RUNTIME           docker or singularity (default: docker)
  --db-dir PATH               Host path to the PostgreSQL data directory (required)
  --container IMAGE_OR_SIF    Docker image name or Singularity .sif path
  --db-name NAME              PostgreSQL database name to create/reuse (default: benchmate)
  --db-port PORT              PostgreSQL port inside the container (default: 5544)
  --container-db-dir PATH     Mount point inside the container (default: /work/pgdata)
  --docker-arg ARG            Extra argument to pass to docker run (repeatable)
  --singularity-arg ARG       Extra argument to pass to singularity exec (repeatable)
  --bind SPEC                 Convenience alias that appends '--bind SPEC' to singularity exec
  --show-command              Print the fully expanded runtime command before execution
  -h, --help                  Show this message

Examples:
  containerization/benchmate.sh --runtime docker --db-dir /tmp/benchmate_pgtest -- bash
  containerization/benchmate.sh --runtime singularity --container /path/to/image.sif --db-dir /path/to/db -- python myscript.py
EOF
}

log() {
  printf '[benchmate] %s\n' "$*"
}

fail() {
  printf '[benchmate] ERROR: %s\n' "$*" >&2
  exit 1
}

# Make sure the provided database directory exists and can be used for PostgreSQL
ensure_db_dir() {
  [[ -n "${DB_DIR}" ]] || fail "--db-dir is required"

  if [[ ! -e "${DB_DIR}" ]]; then
    log "Creating database directory: ${DB_DIR}"
    mkdir -p "${DB_DIR}"
  fi

  [[ -d "${DB_DIR}" ]] || fail "${DB_DIR} exists but is not a directory"

  chmod 700 "${DB_DIR}" 2>/dev/null || true
  local mode
  mode="$(stat -c '%a' "${DB_DIR}" 2>/dev/null || true)"
  if [[ -n "${mode}" && "${mode}" != "700" && "${mode}" != "750" ]]; then
    fail "Database directory ${DB_DIR} has mode ${mode}. PostgreSQL requires 700 or 750 for PGDATA."
  fi
}

# For Singulairty we need to define Linux users so that initdb can run
# needs the current Linux user to be resolvable to a username
build_passwd_file() {
  local passwd_file="./benchmate.passwd"

  {
    printf 'root:x:0:0:root:/root:/bin/bash\n'
    printf 'mambauser:x:57439:57439::/home/mambauser:/bin/bash\n'
    printf '%s:x:%s:%s:%s:%s:/bin/bash\n' "$(id -un)" "$(id -u)" "$(id -g)" "$(id -un)" "${HOME}"
  } > "${passwd_file}"

  printf '%s' "${passwd_file}"
}

# Take a label plus a command, print the label, 
# then print the command in a shell-safe way so the user can see or reuse it
print_command() {
  local label="$1"
  shift
  printf '[benchmate] %s:\n' "${label}"
  printf '  '
  printf '%q ' "$@"
  printf '\n'
}

print_multiline_command() {
  local label="$1"
  local body="$2"
  printf '[benchmate] %s:\n' "${label}"
  printf '%s\n' "${body}"
}

# The raw command examples are runtime-specific: Docker needs startup logic
# in a fresh container, while Singularity can have a simpler follow-up
# access pattern once PostgreSQL is started.
print_next_steps() {
  local runtime_label="$1"
  shift
  log "Setup will be handled automatically each time you run this launcher with the same --db-dir."
  if [[ "${runtime_label}" == "Docker" ]]; then
    log "For Docker, a fresh container will need to start PostgreSQL before using the mounted database."
    print_multiline_command "Example Docker user command" "$1"
  else
    log "Once PostgreSQL is running, you can access it with a command like this:"
    print_multiline_command "Example ${runtime_label} access command" "$1"
  fi
}

# Build the shell snippet shown to Docker users who want to start PostgreSQL
# themselves instead of routing through benchmate-run.sh.
build_standalone_inner_cmd() {
  local quoted_user_cmd
  quoted_user_cmd="$(printf '%q ' "$@")"

  printf '%s' \
"export PATH=/opt/conda/bin:\$PATH LANG=C.UTF-8 LC_ALL=C.UTF-8; \
if ! pg_ctl -D ${CONTAINER_DB_DIR} status >/dev/null 2>&1; then \
  pg_ctl -D ${CONTAINER_DB_DIR} -l ${CONTAINER_DB_DIR}/postgres.log -o '-p ${DB_PORT}' start; \
fi; \
until pg_isready -p ${DB_PORT} >/dev/null 2>&1; do sleep 1; done; \
export DATABASE_URL=postgresql+psycopg2://localhost:${DB_PORT}/${DB_NAME}; \
${quoted_user_cmd}"
}

# Each docker run starts a fresh container with no PostgreSQL 
# server already running, so a full startup is needed.
build_docker_show_cmd() {
  local inner_cmd
  inner_cmd="$(build_standalone_inner_cmd bash)"

  printf -v DOCKER_SHOW_CMD '%s\n' \
    "docker run --rm -it --platform linux/amd64 \\" \
    "  -v ${DB_DIR}:${CONTAINER_DB_DIR} \\" \
    "  ${IMAGE} \\" \
    "  bash -lc \"${inner_cmd}\""
}

# Singularity reuse the same already-running PostgreSQL server, so
# the example here just shows how to re-enter the container context and connect.
build_singularity_show_cmd() {
  local passwd_file="$1"
  shift

  printf -v SINGULARITY_SHOW_CMD '%s\n' \
    "singularity exec \\" \
    "  --bind ${DB_DIR}:${CONTAINER_DB_DIR} \\" \
    "  --bind ${passwd_file}:/etc/passwd \\" \
    "  ${IMAGE} \\" \
    "  bash -lc 'export PATH=/opt/conda/bin:\$PATH LANG=C.UTF-8 LC_ALL=C.UTF-8; /opt/conda/bin/psql -p ${DB_PORT} -d ${DB_NAME}'"
}

run_docker() {
  # The normal Docker path always routes through benchmate-run.sh so setup,
  # reuse, and environment export happen automatically for each invocation.
  local cmd=(
    docker run --rm
    -it
    --platform linux/amd64
    -v "${DB_DIR}:${CONTAINER_DB_DIR}"
    -e "BM_DB_DIR=${CONTAINER_DB_DIR}"
    -e "BM_DB_NAME=${DB_NAME}"
    -e "BM_DB_PORT=${DB_PORT}"
  )

  if [[ ${#DOCKER_EXTRA_ARGS[@]} -gt 0 ]]; then
    cmd+=("${DOCKER_EXTRA_ARGS[@]}")
  fi

  cmd+=(
    "${IMAGE}"
    /opt/benchmate/containerization/benchmate-run.sh
    "$@"
  )

  log "Launching Docker image ${IMAGE}"
  log "Mounting ${DB_DIR} at ${CONTAINER_DB_DIR}"
  log "Using database name ${DB_NAME} on port ${DB_PORT}"
  if [[ "${SHOW_COMMAND}" -eq 1 ]]; then
    local DOCKER_SHOW_CMD=""
    build_docker_show_cmd "$@"
    print_next_steps "Docker" "${DOCKER_SHOW_CMD}"
  else
    log "Use this launcher again with the same --db-dir to reuse the database on future runs."
  fi

  exec "${cmd[@]}"
}

run_singularity() {
  local passwd_file
  passwd_file="$(build_passwd_file)"

  # Singularity runs as the invoking HPC user, so we inject a passwd entry and
  # then hand off to the same in-container script used by Docker.
  local inner_cmd
  inner_cmd="export LANG=C.UTF-8 LC_ALL=C.UTF-8 PATH=/opt/conda/bin:\$PATH BM_DB_DIR='${CONTAINER_DB_DIR}' BM_DB_NAME='${DB_NAME}' BM_DB_PORT='${DB_PORT}'; /opt/benchmate/containerization/benchmate-run.sh $(printf '%q ' "$@")"

  local cmd=(
    singularity exec
    --bind "${DB_DIR}:${CONTAINER_DB_DIR}"
    --bind "${passwd_file}:/etc/passwd"
  )

  if [[ ${#SINGULARITY_EXTRA_ARGS[@]} -gt 0 ]]; then
    cmd+=("${SINGULARITY_EXTRA_ARGS[@]}")
  fi

  cmd+=(
    "${IMAGE}"
    bash -lc "${inner_cmd}"
  )

  log "Launching Singularity image ${IMAGE}"
  log "Binding ${DB_DIR} at ${CONTAINER_DB_DIR}"
  log "Injecting passwd entry for $(id -un) so PostgreSQL can initialize as the invoking user"
  log "Using passwd file ${passwd_file}"
  log "Using database name ${DB_NAME} on port ${DB_PORT}"
  if [[ "${SHOW_COMMAND}" -eq 1 ]]; then
    local SINGULARITY_SHOW_CMD=""
    build_singularity_show_cmd "${passwd_file}" "$@"
    print_next_steps "Singularity" "${SINGULARITY_SHOW_CMD}"
  else
    log "Use this launcher again with the same --db-dir to reuse the database on future runs."
  fi

  exec "${cmd[@]}"
}

# Parse the command line options, recognize the known flags and store values in variables
while [[ $# -gt 0 ]]; do
  case "$1" in
    --runtime)
      RUNTIME="${2:-}"
      shift 2
      ;;
    --db-dir)
      DB_DIR="${2:-}"
      shift 2
      ;;
    --container|--image)
      IMAGE="${2:-}"
      shift 2
      ;;
    --db-name)
      DB_NAME="${2:-}"
      shift 2
      ;;
    --db-port)
      DB_PORT="${2:-}"
      shift 2
      ;;
    --container-db-dir)
      CONTAINER_DB_DIR="${2:-}"
      shift 2
      ;;
    --docker-arg)
      DOCKER_EXTRA_ARGS+=("${2:-}")
      shift 2
      ;;
    --singularity-arg)
      SINGULARITY_EXTRA_ARGS+=("${2:-}")
      shift 2
      ;;
    --bind)
      SINGULARITY_EXTRA_ARGS+=(--bind "${2:-}")
      shift 2
      ;;
    --show-command)
      SHOW_COMMAND=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      break
      ;;
  esac
done

ensure_db_dir

if [[ $# -eq 0 ]]; then
  set -- bash
fi

case "${RUNTIME}" in
  docker)
    run_docker "$@"
    ;;
  singularity)
    [[ -f "${IMAGE}" ]] || fail "Singularity container not found: ${IMAGE}"
    run_singularity "$@"
    ;;
  *)
    fail "Unsupported runtime: ${RUNTIME}. Use docker or singularity."
    ;;
esac

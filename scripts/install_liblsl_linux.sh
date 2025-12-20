#!/usr/bin/env bash
set -euo pipefail

# Prints the resolved liblsl path as: LIBLSL_PATH=/path/to/liblsl.so

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

common_candidates=(
  "/usr/local/lib/liblsl.so"
  "/usr/lib/liblsl.so"
  "/usr/lib/x86_64-linux-gnu/liblsl.so"
  "/usr/lib64/liblsl.so"
)

find_existing_liblsl() {
  if command -v ldconfig >/dev/null 2>&1; then
    local from_ld
    from_ld="$(ldconfig -p 2>/dev/null | awk '/liblsl\.so/{print $4; exit}')" || true
    if [[ -n "${from_ld:-}" && -f "$from_ld" ]]; then
      echo "$from_ld"
      return 0
    fi
  fi
  for p in "${common_candidates[@]}"; do
    if [[ -f "$p" ]]; then
      echo "$p"
      return 0
    fi
  done
  return 1
}

lib_path=""
if lib_path="$(find_existing_liblsl)"; then
  echo "LIBLSL_PATH=$lib_path"
  exit 0
fi

echo "liblsl not found; building from source..." >&2

if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y >&2
  sudo apt-get install -y git cmake build-essential >&2
else
  echo "Unsupported package manager; install git, cmake, build-essential manually." >&2
fi

BUILD_DIR="$REPO_ROOT/build/liblsl"
SRC_DIR="$BUILD_DIR/src"
OBJ_DIR="$BUILD_DIR/build"
mkdir -p "$BUILD_DIR"

if [[ ! -d "$SRC_DIR/.git" ]]; then
  git clone --depth 1 https://github.com/sccn/liblsl.git "$SRC_DIR" >&2
else
  git -C "$SRC_DIR" fetch --depth 1 origin >&2 || true
  git -C "$SRC_DIR" reset --hard origin/HEAD >&2 || true
fi

cmake -S "$SRC_DIR" -B "$OBJ_DIR" -DCMAKE_BUILD_TYPE=Release -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF >&2
cmake --build "$OBJ_DIR" --config Release -j"$(nproc || echo 2)" >&2

install_failed=0
if command -v sudo >/dev/null 2>&1; then
  if ! sudo cmake --install "$OBJ_DIR" >&2; then
    install_failed=1
  fi
else
  if ! cmake --install "$OBJ_DIR" >&2; then
    install_failed=1
  fi
fi

if [[ "$install_failed" -eq 0 ]]; then
  if command -v ldconfig >/dev/null 2>&1; then sudo ldconfig >&2 || true; fi
  if lib_path="$(find_existing_liblsl)"; then
    echo "LIBLSL_PATH=$lib_path"
    exit 0
  fi
fi

# Fallback: copy the built .so into repo-local dir and return that path
LOCAL_LIB_DIR="$REPO_ROOT/native/lib"
mkdir -p "$LOCAL_LIB_DIR"
built_lib="$(find "$OBJ_DIR" -type f -name 'liblsl.so*' | head -n1 || true)"
if [[ -z "${built_lib:-}" ]]; then
  echo "Failed to locate built liblsl.so artifact" >&2
  exit 1
fi
cp -f "$built_lib" "$LOCAL_LIB_DIR/liblsl.so" >&2
echo "LIBLSL_PATH=$LOCAL_LIB_DIR/liblsl.so"


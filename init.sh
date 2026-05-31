#!/usr/bin/env bash
set -euo pipefail

# Claude Scaffold - One-command AI engineering setup
# Usage: curl -fsSL https://raw.githubusercontent.com/Badboy000000/claude-scaffold/main/init.sh | bash
#    or: curl -fsSL <url> | bash -s -- [OPTIONS]

VERSION="main"
SKILLS_ONLY=false
NO_OVERWRITE=false
REPO="Badboy000000/claude-scaffold"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Spinner for long-running operations
spinner() {
  local pid=$1
  local msg=$2
  local chars='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
  local i=0
  while kill -0 "$pid" 2>/dev/null; do
    printf "\r  ${CYAN}${chars:$i:1}${NC} %s" "$msg"
    i=$(( (i + 1) % ${#chars} ))
    sleep 0.1
  done
  printf "\r"
}

# Progress bar
progress_bar() {
  local current=$1
  local total=$2
  local label=$3
  local width=30
  local pct=$((current * 100 / total))
  local filled=$((current * width / total))
  local empty=$((width - filled))
  local bar=""
  for ((i=0; i<filled; i++)); do bar+="█"; done
  for ((i=0; i<empty; i++)); do bar+="░"; done
  printf "\r  ${CYAN}[%s]${NC} %3d%% %s" "$bar" "$pct" "$label"
}

usage() {
  cat <<EOF
Usage: curl -fsSL <url> | bash -s -- [OPTIONS]

Options:
  --version <tag>   Install a specific version/tag (default: main)
  --skills-only     Only install .claude/skills/ (skip CLAUDE.md, scripts, etc.)
  --no-overwrite    Skip files that already exist in the target directory
  -h, --help        Show this help message

Environment:
  GITHUB_TOKEN      Set to access private repositories

EOF
  exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)     VERSION="$2"; shift 2 ;;
    --skills-only) SKILLS_ONLY=true; shift ;;
    --no-overwrite) NO_OVERWRITE=true; shift ;;
    -h|--help)     usage ;;
    *) error "Unknown option: $1. Use --help for usage." ;;
  esac
done

# ---------- prerequisites ----------
command -v git >/dev/null 2>&1 || error "git is required but not installed."

# ---------- repo URL (support private repos) ----------
REPO_URL="https://github.com/${REPO}.git"
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  REPO_URL="https://${GITHUB_TOKEN}@github.com/${REPO}.git"
fi

# ---------- temp dir with cleanup ----------
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo ""
echo -e "${BOLD}============================================${NC}"
echo -e "${BOLD}  Claude Scaffold Installer${NC}"
echo -e "${BOLD}============================================${NC}"
echo ""

# ---------- clone with spinner ----------
info "Cloning scaffold (version: ${VERSION})..."
info "Connecting to GitHub... (this may take a moment)"

git clone --depth 1 --branch "$VERSION" "$REPO_URL" "$TMPDIR/scaffold" 2>"$TMPDIR/git.log" &
CLONE_PID=$!
spinner $CLONE_PID "Downloading from GitHub..."

if ! wait $CLONE_PID; then
  git clone --depth 1 "$REPO_URL" "$TMPDIR/scaffold" 2>"$TMPDIR/git.log" &
  CLONE_PID=$!
  spinner $CLONE_PID "Retrying download..."
  wait $CLONE_PID || error "Failed to clone repository. Check network and GITHUB_TOKEN."
fi
ok "Repository cloned."
echo ""

SRC="$TMPDIR/scaffold/template"
DST="$(pwd)"

# ---------- count files first ----------
FILE_COUNT=$(find "$SRC" -type f | wc -l)
CURRENT=0

# ---------- copy with progress ----------
copy_file() {
  local src="$1"
  local rel="$2"
  local dst="$DST/$rel"

  if [[ "$NO_OVERWRITE" == true && -e "$dst" ]]; then
    return 1
  fi

  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  return 0
}

info "Installing to: $DST"
if [[ "$SKILLS_ONLY" == true ]]; then
  info "Mode: skills-only"
  FILE_COUNT=$(find "$SRC/.claude/skills" -type f | wc -l)
else
  info "Mode: full install"
fi
echo ""

SKIPPED=0
COPIED=0

install_files() {
  local search_dir="$1"

  find "$search_dir" -type f | while read -r file; do
    local rel="${file#$SRC/}"
    CURRENT=$((CURRENT + 1))
    progress_bar $CURRENT $FILE_COUNT "$rel"

    if copy_file "$file" "$rel"; then
      COPIED=$((COPIED + 1))
    else
      SKIPPED=$((SKIPPED + 1))
    fi
  done
}

if [[ "$SKILLS_ONLY" == true ]]; then
  install_files "$SRC/.claude/skills"
else
  install_files "$SRC"
fi

echo ""
echo ""
ok "Files installed: ${FILE_COUNT} total"
if [[ "$NO_OVERWRITE" == true ]]; then
  info "Skipped (already exist): check above for warnings"
fi
echo ""

# ---------- post-install validation ----------
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
fi

if [[ -n "$PYTHON_CMD" && -f "$DST/.claude/scripts/sync-routes.py" ]]; then
  info "Validating skill routes..."
  if $PYTHON_CMD "$DST/.claude/scripts/sync-routes.py" --dry-run 2>/dev/null; then
    ok "Route index validated."
  else
    warn "Route validation skipped (missing dependencies or API key)."
  fi
else
  warn "Python not found - skipping route validation."
fi

# ---------- done ----------
echo ""
echo -e "${BOLD}============================================${NC}"
echo -e "${GREEN}${BOLD}  Setup Complete!${NC}"
echo -e "${BOLD}============================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Configure DeepSeek API key:"
echo "     cp .claude/scripts/.env.example .claude/scripts/.env"
echo "     # Edit .env and fill in your API key"
echo ""
echo "  2. Regenerate route index (optional):"
echo "     python .claude/scripts/sync-routes.py"
echo ""
echo "  3. Create your project context:"
echo "     # Edit CONTEXT.md with your project's domain terms"
echo ""
echo "  4. Start using Claude Code with full skill routing!"
echo ""

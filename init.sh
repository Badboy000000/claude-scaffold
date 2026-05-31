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
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

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
echo "============================================"
echo "  Claude Scaffold Installer"
echo "============================================"
echo ""

# ---------- clone ----------
info "Cloning scaffold (version: ${VERSION})..."
if ! git clone --depth 1 --branch "$VERSION" "$REPO_URL" "$TMPDIR/scaffold" 2>/dev/null; then
  git clone --depth 1 "$REPO_URL" "$TMPDIR/scaffold" 2>/dev/null || \
    error "Failed to clone repository. Check network and GITHUB_TOKEN."
fi
ok "Repository cloned."

SRC="$TMPDIR/scaffold/template"
DST="$(pwd)"

# ---------- copy helpers ----------
copy_file() {
  local src="$1"
  local rel="$2"
  local dst="$DST/$rel"

  if [[ "$NO_OVERWRITE" == true && -e "$dst" ]]; then
    warn "Skip (exists): $rel"
    return
  fi

  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  ok "$rel"
}

copy_tree() {
  local src_dir="$1"

  find "$src_dir" -type f | while read -r file; do
    local rel="${file#$SRC/}"
    copy_file "$file" "$rel"
  done
}

info "Installing to: $DST"
echo ""

# ---------- install ----------
if [[ "$SKILLS_ONLY" == true ]]; then
  info "Mode: skills-only"
  copy_tree "$SRC/.claude/skills"
else
  info "Mode: full install"
  copy_tree "$SRC"
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
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
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

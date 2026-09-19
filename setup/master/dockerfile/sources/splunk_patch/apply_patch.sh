#!/bin/bash
# OSIR Splunk web patch
#  - search page bundle : "Expand JSON" switch + flag/unflag buttons on every event   (patch.js / patch.css)
#  - search page bundle : loader of the Timeline-Explorer right-click context menu   (patch_ctxmenu.js)
#  - Dashboard Studio    : same context menu on every Studio dashboard               (studio_dashboard.html)
# Idempotent per file and per fragment: a fragment whose marker is already present is skipped, so the
# script can be re-run on an image build (pristine copies) as well as on a running instance.
#
#   apply_patch.sh            patch what is not patched yet
#   apply_patch.sh --reapply  strip the fragments already present and patch again (upgrade of a
#                             running instance after the fragments changed)
#
# Splunk web keeps the static bundles in memory: after patching a running instance, restart it with
#   splunk restart splunkweb

set -euo pipefail

REAPPLY=0
[ "${1:-}" = "--reapply" ] && REAPPLY=1

PATCH_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PATCH_JS="${PATCH_JS:-$PATCH_DIR/patch.js}"
PATCH_CTXMENU="${PATCH_CTXMENU:-$PATCH_DIR/patch_ctxmenu.js}"
PATCH_CSS="${PATCH_CSS:-$PATCH_DIR/patch.css}"
PATCH_TEMPLATE="${PATCH_TEMPLATE:-$PATCH_DIR/studio_dashboard.html}"
MARKER="OSIR-SPLUNK-PATCH"
MARKER_CTXMENU="OSIR-SPLUNK-PATCH-CTXMENU"

SPLUNK_HOME="${SPLUNK_HOME:-/opt/splunk}"
EXPOSED="$SPLUNK_HOME/share/splunk/search_mrsparkle/exposed/build"

# The search page loads the bundle of the user's theme (light / dark); newer builds also ship an
# "enterprise" bundle. Patch whatever exists.
JS_FILES=(
    "$EXPOSED/pages/light/search.js"
    "$EXPOSED/pages/dark/search.js"
    "$EXPOSED/pages/enterprise/search.js"
)
CSS_FILES=(
    "$EXPOSED/css/bootstrap-light.css"
    "$EXPOSED/css/bootstrap-dark.css"
    "$EXPOSED/css/bootstrap-enterprise.css"
)
# Dashboard Studio page template: the pristine copy used to seed a new /opt/splunk/etc, and the live one.
TEMPLATE_FILES=(
    "/opt/splunk-etc/apps/splunk-dashboard-studio/appserver/templates/dashboard.html"
    "$SPLUNK_HOME/etc/apps/splunk-dashboard-studio/appserver/templates/dashboard.html"
)

SED_MATCH='<div class="pull-right jobstatus-control-grouping"></div>'
SED_REPLACE='<div class="pull-right jobstatus-control-grouping"><div class="autoexpand"><span class="autoexpandtext">Expand JSON</span><label class="switch"><input type="checkbox" checked><span class="slider round"></span></label></div></div>'

log()  { echo "  [-] $*"; }
ok()   { echo "  [✓] $*"; }
warn() { echo "  [!] $*" >&2; }
fail() { echo "  [!] $*" >&2; exit 1; }

for f in "$PATCH_JS" "$PATCH_CTXMENU" "$PATCH_CSS" "$PATCH_TEMPLATE"; do
    [ -f "$f" ] || fail "Patch fragment not found: $f"
done

patched=0

# Remove every fragment of a file: from the first marker line down to the end of file (JS / CSS),
# or the two inserted lines (Studio template).
strip_fragments() {
    local file="$1"
    grep -q "$MARKER" "$file" || return 0
    case "$file" in
        *.html) sed -i "/$MARKER/d; /osir_context_menu.js/d; /osir_studio.css/d" "$file" ;;
        *)      sed -i "/^\/\* $MARKER \*\/\$/,\$d" "$file" ;;
    esac
    log "previous fragments removed: $file"
}

# Append a fragment to a file (owner and mode are kept). $1 file, $2 fragment, $3 marker, $4 label
append_fragment() {
    local file="$1" frag="$2" marker="$3" label="$4"
    if grep -q "$marker" "$file"; then ok "$label already present: $file"; return; fi
    {
        echo ""
        echo "/* $marker */"
        cat "$frag"
    } >> "$file"
    ok "$label appended: $file"; patched=$((patched + 1))
}

patch_js() {
    local file="$1"
    [ -f "$file" ] || { log "JS bundle absent, skipped: $file"; return; }
    [ "$REAPPLY" = 1 ] && strip_fragments "$file"
    if ! grep -q "$MARKER" "$file"; then
        sed -i "s|$SED_MATCH|$SED_REPLACE|g" "$file"
    fi
    append_fragment "$file" "$PATCH_JS"      "$MARKER"         "flag patch"
    append_fragment "$file" "$PATCH_CTXMENU" "$MARKER_CTXMENU" "context menu loader"
}

patch_css() {
    local file="$1"
    [ -f "$file" ] || { log "CSS absent, skipped: $file"; return; }
    [ "$REAPPLY" = 1 ] && strip_fragments "$file"
    append_fragment "$file" "$PATCH_CSS" "$MARKER" "CSS"
}

# Insert the fragment right before the Dashboard Studio module <script>, so the context menu is
# available on every Studio dashboard (Studio has no supported hook for custom JS).
patch_template() {
    local file="$1" tmp
    [ -f "$file" ] || { log "Studio template absent, skipped: $file"; return; }
    [ "$REAPPLY" = 1 ] && strip_fragments "$file"
    if grep -q "$MARKER" "$file"; then ok "Studio template already patched: $file"; return; fi
    grep -q '<script type="module"' "$file" || { warn "Studio template anchor not found, skipped: $file"; return; }
    tmp="$(mktemp)"
    awk -v snip="$(cat "$PATCH_TEMPLATE")" '!done && /<script type="module"/ { print snip; done=1 } { print }' "$file" > "$tmp"
    cat "$tmp" > "$file"     # cat, not mv: keeps owner and mode
    rm -f "$tmp"
    ok "Studio template patched: $file"; patched=$((patched + 1))
}

log "Patching Splunk web: $EXPOSED"
found_js=0
for f in "${JS_FILES[@]}"; do [ -f "$f" ] && found_js=1; patch_js "$f"; done
[ "$found_js" = 1 ] || fail "No search bundle found under $EXPOSED/pages (Splunk image not compatible?)"
for f in "${CSS_FILES[@]}";      do patch_css "$f"; done
for f in "${TEMPLATE_FILES[@]}"; do patch_template "$f"; done
ok "Splunk patch done ($patched change(s))."

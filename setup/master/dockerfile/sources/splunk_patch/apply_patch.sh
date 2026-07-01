#!/bin/bash

set -euo pipefail

PATCH_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PATCH_JS="${PATCH_JS:-$PATCH_DIR/patch.js}"
PATCH_CSS="${PATCH_CSS:-$PATCH_DIR/patch.css}"
MARKER="OSIR-SPLUNK-PATCH"

SPLUNK_HOME="${SPLUNK_HOME:-/opt/splunk}"
EXPOSED="$SPLUNK_HOME/share/splunk/search_mrsparkle/exposed/build"

JS_FILES=(
    "$EXPOSED/pages/light/search.js"
    "$EXPOSED/pages/dark/search.js"
)

CSS_FILES=(
    "$EXPOSED/css/bootstrap-light.css"
    "$EXPOSED/css/bootstrap-dark.css"
)

SED_MATCH='<div class="pull-right jobstatus-control-grouping"></div>'
SED_REPLACE='<div class="pull-right jobstatus-control-grouping"><div class="autoexpand"><span class="autoexpandtext">Expand JSON</span><label class="switch"><input type="checkbox" checked><span class="slider round"></span></label></div></div>'

log()  { echo "  [-] $*"; }
ok()   { echo "  [✓] $*"; }
fail() { echo "  [!] $*" >&2; exit 1; }

[ -f "$PATCH_JS" ]  || fail "Fragment JS introuvable : $PATCH_JS"
[ -f "$PATCH_CSS" ] || fail "Fragment CSS introuvable : $PATCH_CSS"

# Already patched ? 
if grep -q "$MARKER" "${JS_FILES[0]}" 2>/dev/null; then
    ok "Splunk already patched ($MARKER present) - nothing to do."
    exit 0
fi

patch_js() {
    local file="$1"
    [ -f "$file" ] || fail "JS file not found : $file (Splunk image not compatible ?)"

    local owner
    owner="$(stat -c '%u:%g' "$file")"

    sed -i "s|$SED_MATCH|$SED_REPLACE|g" "$file"

    {
        echo ""
        echo "/* $MARKER */"
        cat "$PATCH_JS"
    } >> "$file"

    chown "$owner" "$file"
    ok "JS patche : $file"
}

patch_css() {
    local file="$1"
    [ -f "$file" ] || fail "Fichier CSS attendu absent : $file (image Splunk incompatible ?)"

    local owner
    owner="$(stat -c '%u:%g' "$file")"

    {
        echo ""
        echo "/* $MARKER */"
        cat "$PATCH_CSS"
    } >> "$file"

    chown "$owner" "$file"
    ok "CSS patche : $file"
}

log "Patch Splunk : $EXPOSED"
for f in "${JS_FILES[@]}";  do patch_js  "$f"; done
for f in "${CSS_FILES[@]}"; do patch_css "$f"; done
ok "Patch Splunk applique."

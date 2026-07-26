#!/bin/bash
# Loki-RS wrapper for OSIR: update the signatures, then scan.
#
# Two things this wrapper handles:
#
# 1. Loki-RS reads its rules from "./signatures", relative to the *current
#    working directory*, with no flag to point elsewhere. OSIR runs module tools
#    from the celery worker CWD, so the scanner would start with 0 rule.
#
# 2. 'loki-util update' deletes every .yar *before* downloading the new bundle.
#    Without internet the download fails and the scanner is left with no rule at
#    all - a scan that finds nothing and reports success. So the current rules
#    are copied aside and put back when the update fails.
#
# Air-gapped setup: drop your .yar files in ./signatures/yara/ (and your IOC
# lists in ./signatures/iocs/), they are used as-is. Note that an online update,
# when it does run, rebuilds ./signatures/yara from the downloaded bundle only.
#
# OSIR_LOKI_UPDATE_MAX_AGE: seconds between two update attempts (default 86400,
# 0 forces one on every scan). Keeps a 50-endpoint case from downloading the
# ruleset 50 times.
#
# The scan always runs: a failed update is a warning, never a reason to skip it.

set -u

cd "$(dirname "$(readlink -f "$0")")" || exit 1

MAX_AGE="${OSIR_LOKI_UPDATE_MAX_AGE:-86400}"
STAMP="signatures/.last_update"

rules_present() { compgen -G "signatures/yara/*.yar" > /dev/null 2>&1; }

stamp_age() {
    [ -f "$STAMP" ] || { echo "$((MAX_AGE + 1))"; return; }
    echo $(( $(date +%s) - $(stat -c %Y "$STAMP" 2>/dev/null || echo 0) ))
}

if [ "$(stamp_age)" -ge "$MAX_AGE" ] || ! rules_present; then
    backup="$(mktemp -d)"
    cp -p signatures/yara/*.yar "$backup"/ 2>/dev/null

    echo "[loki_scan] updating YARA rules..."
    timeout 300 ./loki-util update

    if ! rules_present; then
        echo "[loki_scan] WARNING: update failed (no internet?), restoring the previous rules."
        cp -p "$backup"/*.yar signatures/yara/ 2>/dev/null
    fi

    rm -rf "$backup"
    touch "$STAMP" 2>/dev/null
fi

rules_present || echo "[loki_scan] WARNING: no YARA rule installed, only IOC lists will match."

# Loki-RS opens its JSONL output in append mode: re-scanning a case would stack
# the new findings on top of the previous ones and the indexer would count them
# twice. Start from an empty file.
prev=""
for arg in "$@"; do
    [ "$prev" = "--jsonl" ] || [ "$prev" = "-j" ] && : > "$arg"
    prev="$arg"
done

exec ./loki "$@"

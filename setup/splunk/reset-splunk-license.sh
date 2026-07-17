#!/usr/bin/env bash
# =============================================================================
# reset-splunk-license.sh
#
# Reset the OSIR Splunk instance to get a fresh (Free) license, WITHOUT losing
# your data. Full cycle:
#
#   1. Export  : KV store collection(s) of the Timeline-Explorer app (verified:
#                HTTP 200 + valid JSON array, or hard abort before any wipe),
#                the app lookups (CSV), and ALL non-internal indexes (case_*).
#                In the full cycle the index dirs are MOVED (rename, O(1))
#                into the backup dir; with --backup-only they are tar'ed
#                (real copy, the live instance keeps its data).
#   2. Wipe    : stop the container (kept, not removed) and delete the content
#                of  setup/splunk/data/{etc,var}  -> fresh Splunk provisioning.
#                Refuses to run unless the backup is verified on disk.
#   3. Relaunch: recreate the container via docker compose (fresh provisioning
#                -> license usage / violation history wiped => "fresh" license).
#   4. Restore : recreate the index definitions, move the index dirs back
#                (rename; never deletes anything - freshly provisioned dirs are
#                set aside, not removed), restore the KV store in chunks and
#                verify record counts.
#
# SAFETY INVARIANT: this script never deletes the only copy of anything.
# Every destructive step is gated on a verified proof that the data is safe
# (index dirs present in the backup, KV exported with HTTP 200 + JSON array).
# Any intermediate failure leaves the data recoverable with:
#     ./reset-splunk-license.sh --restore-only --backup-dir DIR
#
# Ownership note: Splunk files inside the bind mounts are owned by uid 41812
# and some are mode 600. A normal host user can neither read nor delete them,
# so all filesystem operations are done through throwaway *root* helper
# containers (busybox) and the KV store through the REST API. mv/rename
# preserves ownership (41812) and modes end-to-end.
#
# mv vs tar: rename(2) only works inside a single mount point. Two separate
# bind mounts in the helper => EXDEV => mv silently degrades to copy+unlink.
# So the helper mounts the common parent (setup/splunk) and the backup dir
# must live under it (verified with stat %d at runtime); otherwise the script
# falls back to the tar copy.
#
# Usage:
#   ./reset-splunk-license.sh                 # full cycle (asks confirmation)
#   ./reset-splunk-license.sh --yes           # no confirmation prompt
#   ./reset-splunk-license.sh --backup-dir DIR
#   ./reset-splunk-license.sh --backup-only   # export only (tar copy), no wipe
#   ./reset-splunk-license.sh --restore-only --backup-dir DIR
#   ./reset-splunk-license.sh --no-restore    # export + wipe + relaunch, stop there
#
# Env overrides: SPLUNK_HOST (default 127.0.0.1), SPLUNK_MGMT_PORT (8089),
#                SPLUNK_USER (admin), SPLUNK_PASSWORD (else read from .env),
#                CONTAINER (master-splunk), HELPER_IMG (busybox),
#                KVSTORE_APP (Timeline-Explorer), KVSTORE_COLLECTIONS (space list),
#                KV_CHUNK (500, docs per batch_save request),
#                KV_READY_TIMEOUT (300s), KV_RETRY_DELAY (5s),
#                KV_BATCH_RETRIES (12 attempts)
# =============================================================================
set -euo pipefail

log()  { printf '\033[1;36m[%s]\033[0m %s\n' "$(date +%H:%M:%S)" "$*"; }
warn() { printf '\033[1;33m[WARN]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[FATAL]\033[0m %s\n' "$*" >&2; exit 1; }

# -----------------------------------------------------------------------------
# Configuration / path discovery
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Walk up until we find setup/master/docker-compose.yml (repo root).
REPO_ROOT=""
d="$SCRIPT_DIR"
for _ in 1 2 3 4 5 6; do
    if [[ -f "$d/setup/master/docker-compose.yml" ]]; then REPO_ROOT="$d"; break; fi
    d="$(dirname "$d")"
done
[[ -n "$REPO_ROOT" ]] || die "could not locate repo root (setup/master/docker-compose.yml)"

# data/ + apps/ live under setup/splunk (fallback OSIR/setup/splunk).
# BASE_DIR is the common parent mounted in the helper for mv/rename operations.
DATA_DIR=""; APPS_DIR=""; BASE_DIR=""
for base in "$REPO_ROOT/setup/splunk" "$REPO_ROOT/OSIR/setup/splunk"; do
    if [[ -d "$base/data" ]]; then DATA_DIR="$base/data"; APPS_DIR="$base/apps"; BASE_DIR="$base"; break; fi
done
[[ -n "$DATA_DIR" ]] || die "could not find setup/splunk/data"
ETC_DIR="$DATA_DIR/etc"
VAR_DIR="$DATA_DIR/var"
ENV_FILE="$REPO_ROOT/setup/master/.env"

CONTAINER="${CONTAINER:-master-splunk}"
HELPER_IMG="${HELPER_IMG:-busybox}"
SPLUNK_HOST="${SPLUNK_HOST:-127.0.0.1}"
SPLUNK_MGMT_PORT="${SPLUNK_MGMT_PORT:-8089}"
SPLUNK_USER="${SPLUNK_USER:-admin}"
KVSTORE_APP="${KVSTORE_APP:-Timeline-Explorer}"
KVSTORE_COLLECTIONS="${KVSTORE_COLLECTIONS:-flagged_events}"
KV_CHUNK="${KV_CHUNK:-500}"
KV_READY_TIMEOUT="${KV_READY_TIMEOUT:-300}"
KV_RETRY_DELAY="${KV_RETRY_DELAY:-5}"
KV_BATCH_RETRIES="${KV_BATCH_RETRIES:-12}"
MGMT="https://${SPLUNK_HOST}:${SPLUNK_MGMT_PORT}"

# Internal Splunk index storage dirs that must NOT be restored (they carry the
# license usage / violation history we specifically want to reset).
INTERNAL_INDEXES=" _internaldb _audit _thefishbucket _introspection _metrics _metrics_rollup _configtracker _dmc_summary _telemetrydb defaultdb historydb summarydb fishbucket kvstore persistentstorage authDb hashDb audit modinputs "

# -----------------------------------------------------------------------------
# Flags
# -----------------------------------------------------------------------------
ASSUME_YES=0; DO_EXPORT=1; DO_WIPE=1; DO_RELAUNCH=1; DO_RESTORE=1
BACKUP_DIR=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --yes|-y)       ASSUME_YES=1 ;;
        --backup-dir)   BACKUP_DIR="$2"; shift ;;
        --backup-only)  DO_WIPE=0; DO_RELAUNCH=0; DO_RESTORE=0 ;;
        --no-restore)   DO_RESTORE=0 ;;
        --restore-only) DO_EXPORT=0; DO_WIPE=0; DO_RELAUNCH=0 ;;
        --relaunch-only) DO_EXPORT=0; DO_WIPE=0; DO_RELAUNCH=1; DO_RESTORE=0 ;;
        -h|--help)      grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)              echo "Unknown arg: $1"; exit 1 ;;
    esac
    shift
done

TS="$(date +%Y%m%d-%H%M%S)"
[[ -n "$BACKUP_DIR" ]] || BACKUP_DIR="$DATA_DIR/../backups/splunk-reset-$TS"
[[ "$DO_EXPORT" == "1" ]] && mkdir -p "$BACKUP_DIR"
BACKUP_DIR="$(cd "$BACKUP_DIR" 2>/dev/null && pwd || echo "$BACKUP_DIR")"
INDEX_TAR="$BACKUP_DIR/indexes.tar.gz"       # tar mode (--backup-only / fallback)
INDEX_BAK="$BACKUP_DIR/indexes"              # mv mode (full cycle)
INDEX_LIST="$BACKUP_DIR/indexes.list"
INDEX_COUNTS="$BACKUP_DIR/indexes.counts"    # idx=totalEventCount at export time
LOOKUPS_DIR="$BACKUP_DIR/lookups"

# SAFETY: never allow the backup inside the dirs that get wiped.
case "$BACKUP_DIR" in
    "$ETC_DIR"|"$ETC_DIR"/*|"$VAR_DIR"|"$VAR_DIR"/*)
        die "BACKUP_DIR is inside etc/ or var/ - it would be destroyed by the wipe" ;;
esac

# mv (rename) only for the full cycle (--backup-only must keep a real copy on
# the live instance) and only if the backup lives under BASE_DIR (single bind
# mount in the helper => rename possible; otherwise EXDEV => degrades to copy).
MV_MODE=0
[[ "$DO_WIPE" == "1" && "$BACKUP_DIR" == "$BASE_DIR"/* ]] && MV_MODE=1
rel_var="${VAR_DIR#"$BASE_DIR"/}"
rel_bak="${INDEX_BAK#"$BASE_DIR"/}"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
PASS=""
load_password() {
    PASS="${SPLUNK_PASSWORD:-}"
    if [[ -z "$PASS" && -f "$ENV_FILE" ]]; then
        PASS="$( { grep -E '^SPLUNK_PASSWORD=' "$ENV_FILE" || true; } | head -1 | cut -d= -f2-)"
    fi
    [[ -n "$PASS" ]] || die "SPLUNK_PASSWORD not set and not found in $ENV_FILE"
}

curl_splunk() { curl -sk -u "${SPLUNK_USER}:${PASS}" "$@"; }

kv_count() {  # count records currently in a KV collection (prints a number)
    curl_splunk "$MGMT/servicesNS/nobody/${KVSTORE_APP}/storage/collections/data/${1}?output_mode=json&count=0" 2>/dev/null \
        | { grep -o '"_key"' || true; } | wc -l | tr -d ' '
}

container_running() { [[ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null)" == "true" ]]; }
container_exists()  { docker inspect "$CONTAINER" >/dev/null 2>&1; }

wait_splunkd_ready() {
    local timeout="${1:-600}" waited=0 code
    log "Waiting for splunkd management API ($MGMT) to be ready (timeout ${timeout}s)..."
    while (( waited < timeout )); do
        code="$(curl -sk -o /dev/null -w '%{http_code}' -u "${SPLUNK_USER}:${PASS}" \
                 "$MGMT/services/server/info?output_mode=json" 2>/dev/null || true)"
        if [[ "$code" == "200" ]]; then log "splunkd is ready."; return 0; fi
        sleep 5; waited=$((waited+5))
        (( waited % 30 == 0 )) && log "  ...still waiting (${waited}s, last HTTP=${code:-none})"
    done
    die "splunkd did not become ready within ${timeout}s"
}

# splunkd can return HTTP 200 on /services/server/info while the KV Store is
# still starting and returns HTTP 503. Poll the collection endpoint itself.
# $3=1 accepts HTTP 404 (valid during export when the collection is absent);
# restore requires HTTP 200 because the destination collection must exist.
wait_kvstore_ready() {
    local coll="$1" timeout="${2:-$KV_READY_TIMEOUT}" allow_missing="${3:-0}"
    local waited=0 code url
    url="$MGMT/servicesNS/nobody/${KVSTORE_APP}/storage/collections/data/${coll}?output_mode=json&count=0"
    log "Waiting for KV Store collection '$coll' (timeout ${timeout}s)..."
    while (( waited < timeout )); do
        code="$(curl -sk -o /dev/null -w '%{http_code}' -u "${SPLUNK_USER}:${PASS}" "$url" 2>/dev/null || true)"
        case "$code" in
            200)
                log "KV Store collection '$coll' is ready."
                return 0
                ;;
            404)
                if [[ "$allow_missing" == "1" ]]; then
                    log "KV Store is reachable; collection '$coll' is absent."
                    return 0
                fi
                ;;
            401|403)
                die "KV Store readiness check for '$coll' failed (HTTP $code) - check credentials"
                ;;
        esac
        sleep "$KV_RETRY_DELAY"
        waited=$((waited+KV_RETRY_DELAY))
        (( waited % 30 == 0 )) && log "  ...KV Store still unavailable (${waited}s, last HTTP=${code:-none})"
    done
    die "KV Store collection '$coll' did not become ready within ${timeout}s (last HTTP=${code:-none})"
}

# Run a command in a throwaway root container with a dir bind-mounted on /mnt.
# $1 = host path to mount, rest = sh -c command
helper() {
    local mount="$1"; shift
    docker run --rm -u 0 -v "$mount":/mnt --entrypoint sh "$HELPER_IMG" -c "$*"
}

ensure_helper_img() {
    docker image inspect "$HELPER_IMG" >/dev/null 2>&1 || { log "Pulling helper image $HELPER_IMG..."; docker pull "$HELPER_IMG"; }
}

# Recreate the Splunk container the OSIR way. A `docker start` on a wiped etc/
# does NOT re-provision this image (splunkd loops); the fresh provisioning only
# runs when the container is *recreated* via docker compose (as osir-launcher
# does: COMPOSE_PROFILES=... docker compose up -d). Env vars (SPLUNK_PASSWORD,
# SPLUNK_LICENSE_URI, ...) come from setup/master/.env via compose.
recreate_splunk() {
    log "Recreating '$CONTAINER' via docker compose (service=$SPLUNK_SERVICE, profile=$COMPOSE_PROFILE)"
    COMPOSE_PROFILES="$COMPOSE_PROFILE" docker compose \
        -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
        up -d --force-recreate --no-deps "$SPLUNK_SERVICE"
}

# -----------------------------------------------------------------------------
# Preflight
# -----------------------------------------------------------------------------
command -v docker >/dev/null || die "docker not found in PATH"
command -v curl   >/dev/null || die "curl not found in PATH"
if [[ "$DO_RESTORE" == "1" ]]; then
    command -v python3 >/dev/null || die "python3 not found in PATH (required for chunked KV store restore)"
fi
container_exists  || die "container '$CONTAINER' does not exist"
load_password
ensure_helper_img

# Figure out how to recreate the container via compose (matches osir-launcher).
COMPOSE_FILE="$REPO_ROOT/setup/master/docker-compose.yml"
[[ -f "$COMPOSE_FILE" ]] || die "compose file not found: $COMPOSE_FILE"
SPLUNK_SERVICE="${RELAUNCH_SERVICE:-$(docker inspect -f '{{ index .Config.Labels "com.docker.compose.service"}}' "$CONTAINER" 2>/dev/null || true)}"
[[ -n "$SPLUNK_SERVICE" ]] || SPLUNK_SERVICE="splunk"
case "$SPLUNK_SERVICE" in
    splunk-offline) COMPOSE_PROFILE="${RELAUNCH_PROFILE:-splunk-offline}" ;;
    *)              COMPOSE_PROFILE="${RELAUNCH_PROFILE:-splunk-online}" ;;
esac

log "Repo root     : $REPO_ROOT"
log "Compose/svc   : $COMPOSE_FILE  (service=$SPLUNK_SERVICE, profile=$COMPOSE_PROFILE)"
log "Data dir      : $DATA_DIR"
log "Backup dir    : $BACKUP_DIR  (index mode: $([[ "$MV_MODE" == "1" ]] && echo "mv/rename" || echo "tar copy"))"
log "Container     : $CONTAINER"
log "KV collections: $KVSTORE_COLLECTIONS  (app: $KVSTORE_APP)"

if [[ "$DO_WIPE" == "1" && "$ASSUME_YES" != "1" ]]; then
    echo
    warn "This will STOP '$CONTAINER' and DELETE the content of:"
    warn "    $ETC_DIR"
    warn "    $VAR_DIR"
    warn "A verified backup is taken first into: $BACKUP_DIR"
    read -r -p "Type 'yes' to continue: " ans
    [[ "$ans" == "yes" ]] || die "Aborted by user."
fi

# -----------------------------------------------------------------------------
# 1. EXPORT
# -----------------------------------------------------------------------------
if [[ "$DO_EXPORT" == "1" ]]; then
    log "=== Phase 1: EXPORT ==="
    container_running || { log "Container not running, starting it for export..."; docker start "$CONTAINER" >/dev/null; }
    wait_splunkd_ready 600

    # 1a. KV store collections -> JSON (needs splunkd up).
    #     HTTP code is checked: a 401/503/timeout must NEVER be mistaken for an
    #     empty collection - the kvstore lives in var/ and is wiped, so a bad
    #     export here means definitive loss. Hard abort before any wipe.
    for coll in $KVSTORE_COLLECTIONS; do
        out="$BACKUP_DIR/kvstore_${coll}.json"
        wait_kvstore_ready "$coll" "$KV_READY_TIMEOUT" 1
        log "Exporting KV store collection '$coll'..."
        code="$(curl -sk -u "${SPLUNK_USER}:${PASS}" -w '%{http_code}' -o "$out" \
                 "$MGMT/servicesNS/nobody/${KVSTORE_APP}/storage/collections/data/${coll}?output_mode=json&count=0" || echo 000)"
        case "$code" in
            200)
                head -c1 "$out" | grep -q '\[' \
                    || { rm -f "$out"; die "KV export '$coll': HTTP 200 but body is not a JSON array - refusing to continue"; }
                n="$( { grep -o '"_key"' "$out" || true; } | wc -l | tr -d ' ')"
                log "  -> $n record(s) saved to $(basename "$out")"
                ;;
            404)
                log "  collection '$coll' does not exist yet (404) - skipping"
                rm -f "$out"
                ;;
            *)
                rm -f "$out"
                if [[ "$DO_WIPE" == "1" ]]; then
                    die "KV export '$coll' failed (HTTP $code) - refusing to continue toward a wipe"
                fi
                warn "KV export '$coll' failed (HTTP $code)"
                ;;
        esac
    done

    # 1b. Lookups (CSV) of the app - they live in the bind-mounted app dir and
    #     survive the wipe, but we back them up anyway.
    if [[ -d "$APPS_DIR/$KVSTORE_APP/lookups" ]]; then
        mkdir -p "$LOOKUPS_DIR"
        cp -a "$APPS_DIR/$KVSTORE_APP/lookups/." "$LOOKUPS_DIR/" 2>/dev/null || warn "could not copy some lookups"
        log "Lookups backed up: $(ls -1 "$LOOKUPS_DIR" 2>/dev/null | wc -l | tr -d ' ') file(s)"
    fi

    # 1c. Enumerate non-internal index storage dirs. A silent enumeration
    #     failure must not be mistaken for "no index": a healthy var/ always
    #     contains defaultdb, use it as a sanity marker.
    raw="$(helper "$VAR_DIR" 'cd /mnt/lib/splunk 2>/dev/null && find . -mindepth 1 -maxdepth 1 -type d | sed "s|^\./||"')" \
        || die "cannot enumerate $VAR_DIR/lib/splunk via helper"
    grep -qx 'defaultdb' <<<"$raw" \
        || die "index listing looks wrong ('defaultdb' missing from $VAR_DIR/lib/splunk) - refusing to continue"
    : > "$INDEX_LIST"
    while read -r idx; do
        [[ -z "$idx" ]] && continue
        [[ "$idx" == _* ]] && continue
        case "$INTERNAL_INDEXES" in *" $idx "*) continue ;; esac
        echo "$idx" >> "$INDEX_LIST"
    done <<< "$raw"

    NIDX="$(wc -l < "$INDEX_LIST" | tr -d ' ')"
    if [[ "$NIDX" -gt 0 ]]; then
        log "Indexes to back up ($NIDX): $(paste -sd' ' "$INDEX_LIST")"
    else
        warn "No user/case index found under $VAR_DIR/lib/splunk (nothing to back up)."
    fi

    # 1d. Record totalEventCount per index while splunkd is still up, for the
    #     post-restore verification.
    : > "$INDEX_COUNTS"
    if [[ "$NIDX" -gt 0 ]]; then
        while read -r idx; do
            [[ -z "$idx" ]] && continue
            tot="$( { curl_splunk "$MGMT/services/data/indexes/$idx?output_mode=json" 2>/dev/null \
                    | grep -o '"totalEventCount":[0-9]*' || true; } | head -1 | cut -d: -f2)"
            echo "$idx=${tot:-?}" >> "$INDEX_COUNTS"
        done < "$INDEX_LIST"
    fi

    # 1e. Stop splunkd (stop the whole container) for a COLD, consistent state,
    #     then either MOVE the index dirs into the backup (full cycle: rename,
    #     instantaneous, uid 41812 preserved) or tar them (--backup-only /
    #     backup dir on another filesystem).
    if [[ "$NIDX" -gt 0 ]]; then
        log "Stopping container for a cold index backup..."
        docker stop "$CONTAINER" >/dev/null
        idx_args="$(paste -sd' ' "$INDEX_LIST")"
        if [[ "$MV_MODE" == "1" ]]; then
            mkdir -p "$INDEX_BAK"
            log "Moving index dirs (rename) -> $INDEX_BAK"
            helper "$BASE_DIR" "
                set -e
                [ \"\$(stat -c %d /mnt/$rel_var/lib/splunk)\" = \"\$(stat -c %d /mnt/$rel_bak)\" ] \
                    || { echo 'EXDEV: backup dir is on a different filesystem' >&2; exit 9; }
                cd /mnt/$rel_var/lib/splunk
                for i in $idx_args; do
                    mv -- \"\$i\" /mnt/$rel_bak/
                    if [ -e \"\$i.dat\" ]; then mv -- \"\$i.dat\" /mnt/$rel_bak/; fi
                done
            " || die "index move failed - data is still under $VAR_DIR/lib/splunk, nothing lost"
            log "  -> moved: $(ls -1 "$INDEX_BAK" 2>/dev/null | wc -l | tr -d ' ') item(s)"
        else
            log "Creating $INDEX_TAR ..."
            helper "$VAR_DIR" "
                set -e
                cd /mnt/lib/splunk
                tar_args=''
                for i in $idx_args; do
                    tar_args=\"\$tar_args \$i\"
                    if [ -e \"\$i.dat\" ]; then tar_args=\"\$tar_args \$i.dat\"; fi
                done
                tar c \$tar_args
            " | gzip > "$INDEX_TAR"
            sz="$(du -h "$INDEX_TAR" | cut -f1)"
            log "  -> index archive: $sz"
        fi
        # If we are not going to wipe (e.g. --backup-only), bring Splunk back up.
        if [[ "$DO_WIPE" != "1" ]]; then
            log "Restarting container (backup-only, was stopped for cold copy)..."
            docker start "$CONTAINER" >/dev/null
        fi
    fi
    log "Export complete: $BACKUP_DIR"
fi

# -----------------------------------------------------------------------------
# 2. WIPE
# -----------------------------------------------------------------------------
if [[ "$DO_WIPE" == "1" ]]; then
    log "=== Phase 2: WIPE ==="
    # Safety gate 1: the export must have produced something usable.
    if [[ "$DO_EXPORT" == "1" && ! -s "$INDEX_LIST" ]] && ! ls "$BACKUP_DIR"/kvstore_*.json >/dev/null 2>&1; then
        die "Backup looks empty; refusing to wipe. Check $BACKUP_DIR"
    fi
    # Safety gate 2 (mv mode): every index dir must actually be in the backup
    # before its origin gets destroyed.
    if [[ "$MV_MODE" == "1" && -s "$INDEX_LIST" ]]; then
        idx_args="$(paste -sd' ' "$INDEX_LIST")"
        helper "$BASE_DIR" "cd \"/mnt/$rel_bak\" && for i in $idx_args; do [ -d \"\$i\" ] || { echo \"missing: \$i\" >&2; exit 1; }; done" \
            || die "index backup incomplete under $INDEX_BAK - refusing to wipe"
    fi
    container_running && { log "Stopping container..."; docker stop "$CONTAINER" >/dev/null; }

    log "Deleting content of $ETC_DIR and $VAR_DIR (via root helper container)..."
    helper "$DATA_DIR" '
        set -e
        for d in etc var; do
            if [ -d "/mnt/$d" ]; then
                ( cd "/mnt/$d" && rm -rf -- ..?* .[!.]* * 2>/dev/null || true )
            fi
        done
        echo "etc entries left: $(ls -A /mnt/etc 2>/dev/null | wc -l)"
        echo "var entries left: $(ls -A /mnt/var 2>/dev/null | wc -l)"
    '
    log "Wipe complete."
fi

# -----------------------------------------------------------------------------
# 3. RELAUNCH (fresh provisioning => fresh license)
# -----------------------------------------------------------------------------
if [[ "$DO_RELAUNCH" == "1" ]]; then
    log "=== Phase 3: RELAUNCH (fresh) ==="
    log "Recreating the container fresh via compose (a wiped etc needs a real recreate, not 'docker start')..."
    recreate_splunk
    wait_splunkd_ready 900   # fresh provisioning can take a few minutes
fi

# -----------------------------------------------------------------------------
# 4. RESTORE
# -----------------------------------------------------------------------------
if [[ "$DO_RESTORE" == "1" ]]; then
    log "=== Phase 4: RESTORE ==="
    container_running || { log "Starting container for restore..."; docker start "$CONTAINER" >/dev/null; }
    wait_splunkd_ready 900

    # 4a. Recreate index definitions via REST (default paths $SPLUNK_DB/<idx>).
    if [[ -s "$INDEX_LIST" ]]; then
        while read -r idx; do
            [[ -z "$idx" ]] && continue
            code="$(curl -sk -o /dev/null -w '%{http_code}' -u "${SPLUNK_USER}:${PASS}" \
                     -d "name=$idx" "$MGMT/services/data/indexes" || true)"
            case "$code" in
                201) log "  index '$idx' created" ;;
                409) log "  index '$idx' already exists" ;;
                *)   warn "  index '$idx' create returned HTTP $code" ;;
            esac
        done < "$INDEX_LIST"

        # 4b. Put the index dirs/buckets back (root helper -> uid 41812 kept).
        if [[ -d "$INDEX_BAK" ]]; then
            # mv-mode backup: restore by rename. NEVER deletes anything - if a
            # target dir exists (freshly provisioned by the REST create, or a
            # live index on a --restore-only against a non-wiped instance), it
            # is set aside under .fresh-replaced/, not removed.
            [[ "$BACKUP_DIR" == "$BASE_DIR"/* ]] || die "mv backup outside $BASE_DIR - rename impossible"
            log "Restoring index dirs (rename)..."
            docker stop "$CONTAINER" >/dev/null
            helper "$BASE_DIR" "
                set -e
                cd \"/mnt/$rel_bak\"
                for i in *; do
                    [ -e \"\$i\" ] || continue
                    if [ -e \"/mnt/$rel_var/lib/splunk/\$i\" ]; then
                        mkdir -p \"/mnt/$rel_bak/.fresh-replaced\"
                        mv \"/mnt/$rel_var/lib/splunk/\$i\" \"/mnt/$rel_bak/.fresh-replaced/\$i\"
                    fi
                    mv -- \"\$i\" \"/mnt/$rel_var/lib/splunk/\"
                done
            " || die "index restore failed - index dirs still under $INDEX_BAK, rerun with --restore-only"
            log "Starting container so restored buckets are picked up..."
            docker start "$CONTAINER" >/dev/null
            wait_splunkd_ready 900
        elif [[ -f "$INDEX_TAR" ]]; then
            log "Restoring index buckets from $INDEX_TAR ..."
            gunzip -c "$INDEX_TAR" | docker run --rm -i -u 0 -v "$VAR_DIR":/mnt --entrypoint sh "$HELPER_IMG" \
                -c 'cd /mnt/lib/splunk && tar x'
            log "Restarting container so restored buckets are picked up..."
            docker restart "$CONTAINER" >/dev/null
            wait_splunkd_ready 900
        else
            warn "No index backup found (neither $INDEX_BAK/ nor $INDEX_TAR)."
        fi
    else
        log "No indexes to restore."
    fi

    # 4c. Restore KV store collections (splunkd up; collection auto-created by
    #     the bind-mounted app's collections.conf). batch_save is capped by
    #     limits.conf (default 1000 docs / 50 MB per request), so the backup is
    #     split into chunks of KV_CHUNK docs; the reserved _user field is
    #     stripped. Record counts are verified afterwards.
    for coll in $KVSTORE_COLLECTIONS; do
        in="$BACKUP_DIR/kvstore_${coll}.json"
        [[ -f "$in" ]] || { log "KV '$coll': no backup file (collection absent at export) - skipping"; continue; }
        if ! grep -q '"_key"' "$in" 2>/dev/null; then
            log "KV '$coll': backup is empty - nothing to restore."
            continue
        fi
        wait_kvstore_ready "$coll" "$KV_READY_TIMEOUT" 0
        log "Restoring KV store collection '$coll' (chunks of $KV_CHUNK)..."
        CHUNK_DIR="$BACKUP_DIR/.kv_chunks_$coll"
        rm -rf "$CHUNK_DIR"; mkdir -p "$CHUNK_DIR"
        total="$(python3 - "$in" "$CHUNK_DIR/chunk_" "$KV_CHUNK" <<'PY'
import json, sys
src, prefix, ch = sys.argv[1], sys.argv[2], int(sys.argv[3])
docs = json.load(open(src))
for d in docs:
    d.pop("_user", None)   # reserved field, rejected on insert by some versions
for i in range(0, len(docs), ch):
    with open(f"{prefix}{i//ch:05d}.json", "w") as f:
        json.dump(docs[i:i+ch], f)
print(len(docs))
PY
)"
        ok=1
        for chf in "$CHUNK_DIR"/chunk_*.json; do
            [[ -e "$chf" ]] || continue
            attempt=1
            while :; do
                code="$(curl -sk -o /dev/null -w '%{http_code}' -u "${SPLUNK_USER}:${PASS}" \
                         -H 'Content-Type: application/json' \
                         "$MGMT/servicesNS/nobody/${KVSTORE_APP}/storage/collections/data/${coll}/batch_save" \
                         --data-binary "@$chf" || true)"
                [[ "$code" == "200" ]] && break
                if (( attempt >= KV_BATCH_RETRIES )) || [[ "$code" != "000" && "$code" != "429" && "$code" != "503" ]]; then
                    break
                fi
                warn "  chunk $(basename "$chf"): batch_save HTTP ${code:-000}, retry $attempt/$KV_BATCH_RETRIES"
                sleep "$KV_RETRY_DELAY"
                attempt=$((attempt+1))
            done
            [[ "$code" == "200" ]] || { warn "  chunk $(basename "$chf"): batch_save failed after $attempt attempt(s), HTTP ${code:-000}"; ok=0; }
        done
        rm -rf "$CHUNK_DIR"
        now="$(kv_count "$coll")"
        if [[ "$ok" == "1" && "$now" == "$total" ]]; then
            log "  '$coll': $now/$total record(s) restored - OK"
        else
            warn "  '$coll': $now/$total record(s) present after restore - CHECK IT (backup kept: $in)"
        fi
    done

    # 4d. Lookups (CSV) already persisted via the bind-mounted app dir. Re-copy
    #     from the backup only if they went missing.
    if [[ -d "$LOOKUPS_DIR" && -d "$APPS_DIR/$KVSTORE_APP/lookups" ]]; then
        for f in "$LOOKUPS_DIR"/*; do
            [[ -e "$f" ]] || continue
            b="$(basename "$f")"
            [[ -e "$APPS_DIR/$KVSTORE_APP/lookups/$b" ]] || cp -a "$f" "$APPS_DIR/$KVSTORE_APP/lookups/" 2>/dev/null || true
        done
    fi

    # 4e. Verification: compare totalEventCount per index with the values
    #     recorded at export time.
    log "=== Verification ==="
    if [[ -s "$INDEX_LIST" ]]; then
        while read -r idx; do
            [[ -z "$idx" ]] && continue
            tot="$( { curl_splunk "$MGMT/services/data/indexes/$idx?output_mode=json" 2>/dev/null \
                    | grep -o '"totalEventCount":[0-9]*' || true; } | head -1 | cut -d: -f2)"
            want="$( { grep -E "^${idx}=" "$INDEX_COUNTS" 2>/dev/null || true; } | head -1 | cut -d= -f2)"
            if [[ -n "$want" && "$want" != "?" && "${tot:-}" == "$want" ]]; then
                log "  index $idx : totalEventCount=$tot (matches export) OK"
            elif [[ -n "$want" && "$want" != "?" ]]; then
                warn "  index $idx : totalEventCount=${tot:-?} != $want at export - CHECK IT"
            else
                log "  index $idx : totalEventCount=${tot:-?}"
            fi
        done < "$INDEX_LIST"
    fi
fi

log "DONE. Backup kept at: $BACKUP_DIR"
if [[ "$DO_RESTORE" != "1" && "$DO_WIPE" == "1" ]]; then
    cat <<EOF

To restore later, run:
    $0 --restore-only --backup-dir "$BACKUP_DIR"
EOF
fi


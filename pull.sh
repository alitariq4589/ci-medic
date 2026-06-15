#!/usr/bin/env bash
# pull.sh — pull failed CI logs into tests/fixtures/
#
# Modes:
#   ./pull.sh OWNER/REPO                 # interactive: list failed runs+jobs, pick one
#   ./pull.sh OWNER/REPO --list          # just list failed runs+jobs with IDs, no pull
#   ./pull.sh OWNER/REPO --job JOB_ID    # pull one specific job log by id
#   ./pull.sh OWNER/REPO --all [N]       # bulk: pull all failed jobs from latest N runs (default 1)
#
set -euo pipefail

REPO="${1:?usage: ./pull.sh OWNER/REPO [--list | --job ID | --all [N]]}"
MODE="${2:-interactive}"
OUTDIR="tests/fixtures"
mkdir -p "$OUTDIR"

# ---- helper: pull a single job log by id, with a name slug --------------
pull_job() {
  local JOB_ID="$1" JOB_NAME="${2:-job}" IDX="${3:-00}"
  local SLUG
  SLUG=$(echo "$JOB_NAME" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-' | cut -c1-40)
  local OUT="$OUTDIR/$(printf '%02d' "$IDX")_${SLUG}.log"
  if gh api "repos/$REPO/actions/jobs/$JOB_ID/logs" > "$OUT" 2>/dev/null; then
    echo "  saved $OUT  ($(wc -l < "$OUT") lines)"
  else
    echo "  FAILED to fetch job $JOB_ID (log may be expired)"
    rm -f "$OUT"
  fi
}

# ---- helper: list failed jobs across the latest failed runs -------------
# prints:  JOB_ID <TAB> RUN_ID <TAB> JOB_NAME
list_failed_jobs() {
  local limit="${1:-10}"
  local run_ids
  run_ids=$(gh run list -R "$REPO" -L 50 \
    --json databaseId,conclusion \
    -q "[.[] | select(.conclusion==\"failure\")] | .[0:$limit] | .[].databaseId")
  for RUN_ID in $run_ids; do
    gh api "repos/$REPO/actions/runs/$RUN_ID/jobs" --paginate \
      -q ".jobs[] | select(.conclusion==\"failure\") | \"\(.id)\t$RUN_ID\t\(.name)\""
  done
}

# ========================================================================
case "$MODE" in

  # ---- pull one specific job by id -------------------------------------
  --job)
    JOB_ID="${3:?usage: ./pull.sh OWNER/REPO --job JOB_ID}"
    echo "Pulling job $JOB_ID from $REPO ..."
    pull_job "$JOB_ID" "job-$JOB_ID" 1
    ;;

  # ---- list only, no pull ----------------------------------------------
  --list)
    echo "Failed jobs in $REPO (most recent failed runs):"
    echo
    printf "%-14s  %-12s  %s\n" "JOB_ID" "RUN_ID" "JOB_NAME"
    printf "%-14s  %-12s  %s\n" "------" "------" "--------"
    list_failed_jobs 15 | while IFS=$'\t' read -r jid rid name; do
      printf "%-14s  %-12s  %s\n" "$jid" "$rid" "$name"
    done
    echo
    echo "Pull one with:  ./pull.sh $REPO --job JOB_ID"
    ;;

  # ---- bulk: all failed jobs from latest N runs ------------------------
  --all)
    N="${3:-1}"
    echo "Pulling all failed jobs from latest $N failed run(s) ..."
    i=0
    list_failed_jobs "$N" | while IFS=$'\t' read -r jid rid name; do
      i=$((i + 1))
      echo "── $name (run $rid) ──"
      pull_job "$jid" "$name" "$i"
    done
    ;;

  # ---- interactive: list, then prompt for a job id ---------------------
  interactive)
    echo "Failed jobs in $REPO:"
    echo
    printf "%-4s  %-14s  %-12s  %s\n" "#" "JOB_ID" "RUN_ID" "JOB_NAME"
    printf "%-4s  %-14s  %-12s  %s\n" "--" "------" "------" "--------"
    # capture into arrays so the user can pick by number OR paste an id
    mapfile -t ROWS < <(list_failed_jobs 15)
    if [ "${#ROWS[@]}" -eq 0 ]; then
      echo "No failed jobs found."; exit 1
    fi
    n=0
    declare -a JOB_IDS JOB_NAMES
    for row in "${ROWS[@]}"; do
      IFS=$'\t' read -r jid rid name <<< "$row"
      n=$((n + 1))
      JOB_IDS[$n]="$jid"; JOB_NAMES[$n]="$name"
      printf "%-4s  %-14s  %-12s  %s\n" "$n" "$jid" "$rid" "$name"
    done
    echo
    read -rp "Enter # to pull (or paste a JOB_ID, or 'all'): " CHOICE

    if [ "$CHOICE" = "all" ]; then
      i=0
      for idx in $(seq 1 "$n"); do
        i=$((i + 1))
        echo "── ${JOB_NAMES[$idx]} ──"
        pull_job "${JOB_IDS[$idx]}" "${JOB_NAMES[$idx]}" "$i"
      done
    elif [[ "$CHOICE" =~ ^[0-9]+$ ]] && [ "$CHOICE" -le "$n" ] && [ "$CHOICE" -ge 1 ]; then
      # a menu number
      pull_job "${JOB_IDS[$CHOICE]}" "${JOB_NAMES[$CHOICE]}" "$CHOICE"
    else
      # treat as a raw job id
      pull_job "$CHOICE" "job-$CHOICE" 1
    fi
    ;;

  *)
    echo "Unknown mode: $MODE"
    echo "Use: --list | --job ID | --all [N] | (no flag = interactive)"
    exit 1
    ;;
esac
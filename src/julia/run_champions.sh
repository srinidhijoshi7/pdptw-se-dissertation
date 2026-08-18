#!/bin/bash
# Reproduces the three-champion vs baseline comparison from Chapter 4 of the dissertation.
# Runs MSLP on all 6 instances × 5 configurations at seed 17, mslpa=10.
# Total wall-time: ~10-15 minutes.

set -e
cd "$(dirname "$0")"
mkdir -p logs/handoff_reproduction

SEED=17
MSLPA=10
ALPHA=0.05
MAXTIME=60

INSTANCES=(
  "06R_06V_02I_04M/t1/lr101"
  "06R_06V_02I_04M/t1/lr102"
  "06R_06V_02I_04M/t1/lr103"
  "06R_06V_02I_04M/t2/lr201"
  "10R_10V_02I_04M/t1/lr101"
  "10R_10V_02I_04M/t1/lr102"
)

# Champion label : absolute-path-to-Julia-file
CHAMPIONS_DIR="$(cd ../python/llm_loop/champions && pwd)"
CHAMPIONS=(
  "Gen1:${CHAMPIONS_DIR}/first_beat_random_d1791ed1796e.jl"
  "Gen2:${CHAMPIONS_DIR}/gen2_cbbe47d2468c.jl"
  "Gen3:${CHAMPIONS_DIR}/gen3_dacd3ec6f6c7.jl"
)

echo "=========================================="
echo "Three-champion reproduction"
echo "seed=$SEED, mslpa=$MSLPA, alpha=$ALPHA"
echo "=========================================="

for INST in "${INSTANCES[@]}"; do
  NAME=$(echo "$INST" | tr '/' '_')
  echo ""
  echo ">>> Instance: $NAME"

  # --- random baseline
  LOG="logs/handoff_reproduction/${NAME}_random.txt"
  julia pdptwse.jl \
    --inst_path "../../instances/multi_island/orig_ams_fg/$INST" \
    --cut_off_machs 4 --method_type heur --method_code mslp \
    --seed $SEED --greedy_service_order "random" --alpha $ALPHA \
    --threads 1 --output_flag_grb_MSLP 0 --mslpa $MSLPA --mslpr I \
    --max_time $MAXTIME --output ./logs/ --print_sol 0 --solver_method A \
    > "$LOG" 2>&1
  BEST_RANDOM=$(grep "Best solution value:" "$LOG" | awk '{print $4}')
  echo "    random       : $BEST_RANDOM"

  # --- tightest_tw baseline
  LOG="logs/handoff_reproduction/${NAME}_tightest_tw.txt"
  julia pdptwse.jl \
    --inst_path "../../instances/multi_island/orig_ams_fg/$INST" \
    --cut_off_machs 4 --method_type heur --method_code mslp \
    --seed $SEED --greedy_service_order "tightest_tw" --alpha $ALPHA \
    --threads 1 --output_flag_grb_MSLP 0 --mslpa $MSLPA --mslpr I \
    --max_time $MAXTIME --output ./logs/ --print_sol 0 --solver_method A \
    > "$LOG" 2>&1
  BEST_TIGHTEST=$(grep "Best solution value:" "$LOG" | awk '{print $4}')
  echo "    tightest_tw  : $BEST_TIGHTEST"

  # --- three champions
  for ENTRY in "${CHAMPIONS[@]}"; do
    LABEL="${ENTRY%%:*}"
    CFILE="${ENTRY#*:}"
    LOG="logs/handoff_reproduction/${NAME}_${LABEL}.txt"
    LLM_CANDIDATE_FILE="$CFILE" julia pdptwse.jl \
      --inst_path "../../instances/multi_island/orig_ams_fg/$INST" \
      --cut_off_machs 4 --method_type heur --method_code mslp \
      --seed $SEED --greedy_service_order "llm_candidate" --alpha $ALPHA \
      --threads 1 --output_flag_grb_MSLP 0 --mslpa $MSLPA --mslpr I \
      --max_time $MAXTIME --output ./logs/ --print_sol 0 --solver_method A \
      > "$LOG" 2>&1
    BEST=$(grep "Best solution value:" "$LOG" | awk '{print $4}')
    echo "    $LABEL         : $BEST"
  done
done

echo ""
echo "=========================================="
echo "All runs complete."
echo "Individual outputs: src/julia/logs/handoff_reproduction/"
echo "=========================================="

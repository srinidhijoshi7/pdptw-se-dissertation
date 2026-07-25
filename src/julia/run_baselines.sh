#!/bin/bash
# Baseline runner: runs both greedy_service_order rules across selected instances
# Saves each run's output to logs/baseline_runs/<instance>_<rule>.txt for later inspection

set -e
cd "$(dirname "$0")"
mkdir -p logs/baseline_runs

INSTANCES=(
  "06R_06V_02I_04M/t1/lr101"
  "06R_06V_02I_04M/t1/lr102"
  "06R_06V_02I_04M/t1/lr103"
  "06R_06V_02I_04M/t2/lr201"
  "10R_10V_02I_04M/t1/lr101"
  "10R_10V_02I_04M/t1/lr102"
)

RULES=("random" "tightest_tw")

for INST in "${INSTANCES[@]}"; do
  for RULE in "${RULES[@]}"; do
    NAME=$(echo "$INST" | tr '/' '_')
    LOG="logs/baseline_runs/${NAME}_${RULE}.txt"
    echo "=========================================="
    echo "Running: $INST | $RULE"
    echo "Log: $LOG"
    echo "=========================================="
    julia pdptwse.jl \
      --inst_path "../../instances/multi_island/orig_ams_fg/$INST" \
      --cut_off_machs 4 \
      --method_type heur \
      --method_code mslp \
      --seed 17 \
      --greedy_service_order "$RULE" \
      --alpha 0.05 \
      --threads 1 \
      --output_flag_grb_MSLP 0 \
      --mslpa 100 \
      --mslpr I \
      --max_time 60 \
      --output ./logs/ \
      --print_sol 0 \
      --solver_method A > "$LOG" 2>&1
    BEST=$(grep "Best solution value:" "$LOG" | awk '{print $4}')
    echo ">>> Best: $BEST"
    echo ""
  done
done

echo "=========================================="
echo "All runs done. Summary:"
echo "=========================================="
for INST in "${INSTANCES[@]}"; do
  for RULE in "${RULES[@]}"; do
    NAME=$(echo "$INST" | tr '/' '_')
    LOG="logs/baseline_runs/${NAME}_${RULE}.txt"
    BEST=$(grep "Best solution value:" "$LOG" | awk '{print $4}')
    echo "$INST | $RULE | $BEST"
  done
done
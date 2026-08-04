#!/bin/bash
# Injection test: verifies that llm_candidate with a random-replica candidate
# produces the same cost as --greedy_service_order random at the same seed.
#
# Success criterion: BEST_A == BEST_B (identical costs)

set -e
cd "$(dirname "$0")"
mkdir -p logs/injection_test

INST="06R_06V_02I_04M/t1/lr101"
SEED=17

# Absolute path to the candidate file (Julia needs the full path)
CANDIDATE_FILE="$(cd ../python/llm_loop/candidates && pwd)/current.jl"

echo "=========================================="
echo "Injection test on $INST (seed $SEED)"
echo "Candidate file: $CANDIDATE_FILE"
echo "=========================================="

# ---------- Run A: baseline (--greedy_service_order random) ----------
LOG_A="logs/injection_test/A_random.txt"
echo ""
echo ">>> Run A: --greedy_service_order random"
julia pdptwse.jl \
  --inst_path "../../instances/multi_island/orig_ams_fg/$INST" \
  --cut_off_machs 4 \
  --method_type heur \
  --method_code mslp \
  --seed $SEED \
  --greedy_service_order "random" \
  --alpha 0.05 \
  --threads 1 \
  --output_flag_grb_MSLP 0 \
  --mslpa 100 \
  --mslpr I \
  --max_time 60 \
  --output ./logs/ \
  --print_sol 0 \
  --solver_method A > "$LOG_A" 2>&1

BEST_A=$(grep "Best solution value:" "$LOG_A" | awk '{print $4}')
echo ">>> Run A best: $BEST_A"

# ---------- Run B: injection (--greedy_service_order llm_candidate) ----------
LOG_B="logs/injection_test/B_llm_candidate.txt"
echo ""
echo ">>> Run B: --greedy_service_order llm_candidate (via injection)"
LLM_CANDIDATE_FILE="$CANDIDATE_FILE" julia pdptwse.jl \
  --inst_path "../../instances/multi_island/orig_ams_fg/$INST" \
  --cut_off_machs 4 \
  --method_type heur \
  --method_code mslp \
  --seed $SEED \
  --greedy_service_order "llm_candidate" \
  --alpha 0.05 \
  --threads 1 \
  --output_flag_grb_MSLP 0 \
  --mslpa 100 \
  --mslpr I \
  --max_time 60 \
  --output ./logs/ \
  --print_sol 0 \
  --solver_method A > "$LOG_B" 2>&1

BEST_B=$(grep "Best solution value:" "$LOG_B" | awk '{print $4}')
echo ">>> Run B best: $BEST_B"

# ---------- Compare ----------
echo ""
echo "=========================================="
echo "RESULT"
echo "=========================================="
echo "Run A (random)        best: $BEST_A"
echo "Run B (llm_candidate) best: $BEST_B"
if [ "$BEST_A" = "$BEST_B" ]; then
  echo "✅ MATCH — injection mechanism works correctly."
else
  echo "❌ MISMATCH — injection is not reproducing random. Check current.jl and env var."
fi
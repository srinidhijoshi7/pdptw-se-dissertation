"""
Configuration for the LLM evolution driver.

All tunable settings live here so experiments are reproducible from a single file.
"""
from pathlib import Path

# ---------- Paths ----------
# Everything is anchored relative to this file's location for robustness.
LLM_LOOP_DIR = Path(__file__).resolve().parent          # .../src/python/llm_loop
REPO_ROOT    = LLM_LOOP_DIR.parents[2]                  # .../pdptw-se
JULIA_DIR    = REPO_ROOT / "src" / "julia"              # where pdptwse.jl lives

PROMPT_FILE       = LLM_LOOP_DIR / "prompts" / "seed.md"
CANDIDATE_FILE    = LLM_LOOP_DIR / "candidates" / "current.jl"
CANDIDATES_LOG    = LLM_LOOP_DIR / "logs" / "candidates.jsonl"

# ---------- Gemini ----------
GEMINI_MODEL = "gemini-3.6-flash"

# ---------- MSLP evaluation ----------
# The instance and parameters used to evaluate every candidate.
# Match run_baselines.sh for direct comparability with baselines.
INSTANCE_REL_PATH = "../../instances/multi_island/orig_ams_fg/06R_06V_02I_04M/t1/lr101"
SEED              = 17
MAX_TIME          = 60      # seconds per MSLP run
MSLP_ITERS        = 100     # --mslpa
ALPHA             = 0.05
JULIA_TIMEOUT     = 180     # kill Julia process if it hangs beyond this (seconds)
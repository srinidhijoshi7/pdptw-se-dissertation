"""
Configuration for the LLM evolution driver.

All tunable settings live here so experiments are reproducible from a single file.
"""
from pathlib import Path

# ---------- Paths ----------
LLM_LOOP_DIR = Path(__file__).resolve().parent          # .../src/python/llm_loop
REPO_ROOT    = LLM_LOOP_DIR.parents[2]                  # .../pdptw-se
JULIA_DIR    = REPO_ROOT / "src" / "julia"              # where pdptwse.jl lives

PROMPT_FILE       = LLM_LOOP_DIR / "prompts" / "seed.md"
EVOLVE_PROMPT_FILE = LLM_LOOP_DIR / "prompts" / "evolve.md"
DIVERSIFY_PROMPT_FILE = LLM_LOOP_DIR / "prompts" / "diversify.md"
CANDIDATE_FILE    = LLM_LOOP_DIR / "candidates" / "current.jl"
CANDIDATES_LOG    = LLM_LOOP_DIR / "logs" / "candidates.jsonl"
GENERATIONS_LOG   = LLM_LOOP_DIR / "logs" / "generations.jsonl"
# Optional: if this file exists, gen 0 loads it as the champion instead of
# calling Gemini with the seed prompt. Lets us continue evolution across days.
CHAMPION_SEED_FILE = LLM_LOOP_DIR / "champions" / "champion_seed.jl"
BASELINES_FILE    = LLM_LOOP_DIR / "baselines.json"

GEMINI_MODEL = "gemini-3.6-flash"

# ---------- Instance grid ----------
# The full 6-instance grid used by baselines. Ratio to random on each instance
# defines the fitness of a candidate.
INSTANCE_GRID_FULL = [
    "06R_06V_02I_04M/t1/lr101",
    "06R_06V_02I_04M/t1/lr102",
    "06R_06V_02I_04M/t1/lr103",
    "06R_06V_02I_04M/t2/lr201",
    "10R_10V_02I_04M/t1/lr101",
    "10R_10V_02I_04M/t1/lr102",
]

# Single-instance grid for fast iteration while developing the loop mechanics.
INSTANCE_GRID_DEV = [
    "10R_10V_02I_04M/t1/lr101",
]

# ---------- Mode ----------
# "dev"  = single instance, fast turnaround, use while debugging loop mechanics
# "full" = 6 instances, real experiment, use for final runs
MODE = "dev"

INSTANCE_GRID = INSTANCE_GRID_DEV if MODE == "dev" else INSTANCE_GRID_FULL

# ---------- MSLP evaluation ----------
INSTANCE_BASE_PATH = "../../instances/multi_island/orig_ams_fg/"
SEED               = 17
MAX_TIME           = 60      # seconds per MSLP run
MSLP_ITERS         = 10     # --mslpa
ALPHA              = 0.05
JULIA_TIMEOUT      = 180     # kill Julia process if it hangs beyond this

# ---------- Evolution ----------
LAMBDA             = 2       # candidates generated per generation
NUM_GENERATIONS    = 8       # for first real run
STAGNATION_THRESHOLD = 2     # generations without improvement -> use diversify prompt
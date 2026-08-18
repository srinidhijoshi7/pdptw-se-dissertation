# Chapter 3 — Research Methodology

*[Target: ~2500–3500 words.]*

## 3.1 Problem statement and evaluation setup

## 3.2 The MSLP baseline (Barbosa, Tiwari and Melo, 2026)

Barbosa, Tiwari and Melo (2026) propose a Multi-Start LP-Improvement (MSLP)
heuristic for the PDPTW-SE, set out in their Algorithm 1. MSLP first builds an
initial solution with a greedy insertion procedure, then enters a multi-start
loop in which a semi-greedy insertion is run repeatedly to produce diverse
candidate solutions. Whenever a construction returns a feasible solution, an
LP-based improvement step re-optimises its schedule, and the best solution
across all restarts is retained. The two phases — construction and LP
improvement — together with the multi-start wrapper that governs restarts and
stopping are unpacked in the paragraphs that follow.

The construction phase inserts pickup–delivery request pairs sequentially into
a partially built solution, with the order of insertion determined by a
service-order rule. Barbosa et al. (2026) define two: `tightest_tw`, which
sorts pickup nodes in nondecreasing order of time-window width (l_i − e_i) and
is used by the initial deterministic greedy construction (their Algorithm 2);
and `random`, a uniformly random shuffle used by the semi-greedy restarts in
the multi-start loop (their Algorithm 4). At each pickup, the semi-greedy
variant builds a list of feasible insertion candidates across all vehicles and
route positions, restricts it to those within a quality threshold α of the
best insertion cost, and selects one at random (their
`CHOOSE_CANDIDATE_BY_QUALITY` procedure). Tiwari's Julia implementation
exposes both service-order rules as configurable options through a shared
dispatcher, `get_service_order`; this dispatcher is the surface this
dissertation modifies (§3.3).

After each feasible construction, MSLP invokes an LP-based schedule
improvement procedure, `LP_SCHEDULE` (Algorithm 1, lines 5 and 9). Taking the
routing decisions and the sequences of machine traversals from the constructed
solution as fixed, this step re-optimises the continuous timing variables —
vehicle departure times and machine travel start times — via a linear
programme derived from the scheduling part of the paper's MIP formulation. The
impact is substantial: the authors report that the LP improvement alone
reduces solution values by at least 5% on average, and foreground it as one of
MSLP's key contributions.

The construction and LP steps are wrapped in a multi-start loop (Algorithm 1,
lines 6–11): each restart runs the semi-greedy insertion, and the best-so-far
solution is retained. In Barbosa et al.'s (2026) experiments, the stopping
criterion is 60,000 iterations or 3,600 seconds per instance, and α is fixed
at 0.05 following the preliminary tuning reported in their Appendix I. This
dissertation retains α at 0.05 but departs on the restart budget, exposing the
iteration count through the `--mslpa` flag in Tiwari's Julia implementation
and fixing it at 10; the rationale is developed in §3.4.

## 3.3 The injection point: `get_service_order`

In Tiwari's Julia implementation of MSLP, the choice of service-order rule is
centralised in a single dispatcher function,
`get_service_order(inst::InstanceData, params::ParameterData)::Vector{Int64}`,
defined in `src/julia/modules/Multistart/src/heuristic/init_solution.jl`. The
function returns the ordered list of pickup-node indices to be inserted in the
current construction pass. Both rules described in §3.2 (`random` and
`tightest_tw`, following Barbosa et al., 2026) are implemented as branches
inside this dispatcher and selected at runtime through the
`--greedy_service_order` command-line flag. The dispatcher is the sole point
at which this dissertation modifies the baseline heuristic.

A third branch, `llm_candidate`, was added to the dispatcher, delegating to a
companion function `llm_candidate_order` defined in the same file. It reads a
Julia source file whose path is supplied through the environment variable
`LLM_CANDIDATE_FILE`, includes its contents into the Multistart module's
namespace, and invokes the loaded function on the current `InstanceData` and
`ParameterData`. The Python evolution driver described in §3.5 writes each
generated candidate to that path before launching Julia, so a single
command-line invocation always evaluates the current candidate. A module-level
cache keyed on file path avoids redundant re-inclusion across MSLP restarts
within a run.

This runtime loading raises a Julia-specific subtlety. The language is
just-in-time compiled, and its method-dispatch tables carry a monotonically
increasing world-age counter: functions compiled at world-age N cannot call
methods defined at any later world age unless the call site explicitly
consults the current method table. A candidate loaded via `include` is
registered at a strictly later world age than the MSLP entry point that
dispatches to it, causing direct calls to fail with a `MethodError` on the
second and subsequent restarts. Wrapping the dispatched call in
`Base.invokelatest(...)` forces resolution against the current method table;
together with the cache, this gives one file load per run and negligible
dispatch cost per restart.

An A/B test verified that the injection mechanism itself is not a source of
variance. MSLP was run twice on instance `lr101_t1_6R` at seed 17: once with
`--greedy_service_order random`, and once with `llm_candidate` pointing at a
file whose contents replicated the random rule exactly. Both configurations
returned solution cost 763.79 — bit-for-bit identical — confirming that the
wrapper introduces no deviation from the baseline execution path. This test
is checked into the repository as `src/julia/test_injection.sh` and is re-run
whenever the injection code is modified.

### 3.4 The evaluation harness

Every candidate produced by the evolutionary loop (§3.5) is scored by a single
scalar **fitness**, computed by installing the candidate as the `llm_candidate`
branch of `get_service_order`, running MSLP on a fixed grid of six benchmark
instances, and averaging the per-instance ratios of candidate cost to a
same-seed `random` baseline:

$$
\text{fitness} \;=\; \frac{1}{|G|}\sum_{i \in G}
                     \frac{c_i^{\text{cand}}}{c_i^{\text{base}}}
$$

where lower is better and 1.0 denotes parity with the random rule. Absolute
per-instance costs on the grid span roughly 450 to 1,300 units, so a
ratio-based fitness prevents the largest instances from dominating the mean.

MSLP is stochastic through its inner semi-greedy insertion, which combines a
random pickup shuffle with α-quality candidate selection; comparing a
candidate at one seed against a baseline at another would therefore conflate
algorithmic performance with random-number-generator variance. To prevent this,
the harness fixes the seed across both the candidate and its baseline on every
instance, so that every ratio in the fitness sum shares its numerator and
denominator seed. Baseline costs are computed once per instance per seed and
cached in `baselines.json`, then reused across all subsequent candidate
evaluations.

During evolution (§3.5), fitness is evaluated at a single seed (17) for
tractability, since each generation requires λ candidate evaluations and
Gemini free-tier quota is capped at 20 calls per day. After the evolutionary
loop terminates, the resulting champions are re-evaluated on a wider seed
grid, {17, 42, 100, 200, 500}, to distinguish genuine algorithmic
improvement from single-seed artefacts. Chapter 4 reports both the
evolution-time fitness values and the multi-seed re-evaluation results, and
§5 draws on the latter to bound the strength of the empirical claims.

The instance grid comprises six instances from the multi-island family of the
Barbosa et al. (2026) benchmark: `lr101`, `lr102`, `lr103` and `lr201` from
the 6-request, 4-machine configuration, and `lr101`, `lr102` from the
10-request configuration. Two request-count classes probe scale sensitivity;
within the 6-request subset, `lr201` provides the sole long-horizon instance,
complementing the short-horizon `lr1xx` cases to probe time-window tightness.
Six instances yield a per-candidate wall-time near one minute at the
parameters set out below, keeping the evolutionary loop tractable within the
Gemini free-tier quota. Multi-floor instances and larger request counts are
deferred as stretch scope (§3.5, §5).

Every MSLP invocation runs with `--mslpa 10` (ten restarts), `--alpha 0.05`
(the value tuned by Barbosa et al., 2026), `--max_time 60`, and `--threads 1`
for deterministic execution. Barbosa et al. (2026) use 60,000 restarts for
benchmarking; this dissertation uses ten because MSLP saturates at high
restart budgets on small instances, converging to the same near-optimal
solution regardless of the initial insertion order. Piloting at `--mslpa 100`
produced fitness values that collapsed to three discrete points,
{1.0000, 1.0006, 1.0032}, erasing the discriminative signal the evolutionary
loop needs. Reducing to ten restarts restores sensitivity to the initial
ordering — the object this dissertation actually evolves — while holding
per-candidate evaluation under a minute. This is a deliberate trade-off: the
fitness values reported in Chapter 4 measure the effect of ordering under a
modest multi-start budget, not on saturated MSLP.

## 3.5 The evolutionary loop

The outer optimisation follows a (1+λ) evolutionary strategy in the classical
sense of Rechenberg (1973), applied here to LLM-generated Julia functions in
the paradigm of LLM-driven code discovery introduced by FunSearch
(Romera-Paredes et al., 2024): a single incumbent champion is maintained
throughout the run; each generation produces λ offspring by prompting an LLM;
every offspring is scored by the fitness harness of §3.4; and the best
offspring replaces the incumbent if and only if it strictly improves on its
fitness. The offspring count is fixed at λ = 2. This is a quota-driven rather
than a principled choice: at Gemini's free-tier ceiling of twenty API calls
per day, λ = 2 fits eight generations within a single day's allowance. A
larger λ would exhaust the quota inside three or four generations, foreclosing
the trajectory.

Generation zero is initialised in one of two ways. The default path issues a
seed prompt (§3.6) that asks the LLM to synthesise a candidate scoring
function from scratch, given only a description of the problem and the Julia
interface contract; the resulting candidate is evaluated and becomes the
generation-zero champion. The alternative path loads a champion-seed file,
`champions/champion_seed.jl`, which if present at run-start is treated as the
generation-zero champion directly and bypasses the seed prompt. The
champion-seed mechanism enables cross-session continuation: the terminal
champion of one session can be archived and used as the starting point for the
next. This proved material in practice — the sixteen-generation trajectory
reported in Chapter 4 was assembled from two eight-generation sessions by this
mechanism.

Selection is strictly elitist: an offspring displaces the champion only if its
fitness is strictly lower, and ties are broken in favour of the incumbent so
that identical-fitness offspring are logged but not promoted. A stagnation
counter increments in every generation that fails to improve the champion and
resets on any generation that does. When the counter reaches
`STAGNATION_THRESHOLD = 2`, the next generation switches from the standard
evolve prompt to a diversify prompt (§3.6) that asks the LLM for a
structurally different candidate rather than a local refinement of the
incumbent. The counter continues to accumulate across diversify firings, so
repeated stagnation triggers repeated diversification until the champion is
improved.

The loop terminates on a fixed generation budget, `NUM_GENERATIONS = 8` by
default; no in-loop convergence test is applied, since the empirical fitness
plateau is identified post hoc by inspecting the trajectory. In practice a
subsequent session extended the trajectory to sixteen generations in total,
to test whether the plateau observed in the first session was terminal or a
local flat region; Chapter 4 reports the outcome. Two logs are written per
run: `candidates.jsonl` records every offspring with its full source code, its
content hash, its parent's hash, the prompt type used to generate it, and its
per-instance and mean fitness; `generations.jsonl` records the
champion-of-generation trajectory. Both are committed to the repository at run
end, giving a complete replayable record of every candidate the loop produced.

### 3.6 Prompt cascade: seed, evolve, diversify

The evolutionary loop uses three distinct prompt templates, each addressing a
different role in the search: **seed** generates a candidate from scratch at
generation zero, **evolve** produces a local refinement of the current
champion, and **diversify** requests a structurally different candidate when
the search stagnates. This three-way split follows the Evolution of Heuristics
(EoH) framework of Liu et al. (2024), which separates the LLM's role into
exploration prompts (their e1, e2, which construct candidates by different
strategies) and modification prompts (their m1, m2, which refine existing
candidates); the design here reduces EoH's four-prompt taxonomy to three by
collapsing exploration into a single seed prompt and treating diversify as a
stagnation-triggered exploration relaunch. The full templates are provided in
Appendix B.

The seed prompt fires only at generation zero, and only when no champion-seed
file is present (§3.5). It contains a natural-language description of the
PDPTW-SE, a functional specification of the required Julia function (name,
argument types, return type), a summary of the `random` and `tightest_tw`
baseline rules as reference points, a documented layout of the `InstanceData`
and `Job` structs the candidate may read, and a common-mistakes section
warning against several failure modes observed in piloting — defining helper
functions at module scope, using `hasproperty` reflection to guess field
names, returning the wrong type, and mutating `inst.V_p`. The prompt closes
by asking for a single self-contained Julia function that returns a
permutation of pickup-node indices.

The evolve prompt is issued in every non-stagnating generation from the first
onward. It inherits the problem description, interface specification, struct
layout, and common-mistakes content from the seed prompt, and adds two
further elements: the source code of the current champion and its fitness
value, templated into the prompt via `{{BEST_CODE}}` and `{{BEST_FITNESS}}`
placeholders. This presentation of code-plus-fitness as prompt context
follows FunSearch (Romera-Paredes et al., 2024), which conditions each
generation on the best programmes seen so far and their scores. The prompt
asks for a refinement that preserves the champion's strong properties while
addressing its weaknesses, and closes with an anti-fallback clause added
after early candidates trivially returned `copy(inst.V_p)` — prohibiting any
candidate that reduces to the natural pickup order.

The diversify prompt replaces the evolve prompt in any generation where the
stagnation counter has reached `STAGNATION_THRESHOLD = 2`. It contains the
same problem, interface, and struct-layout content as the other two, but
replaces the "refine the champion" instruction with a request for a
structurally different construction strategy, and names five candidate
families the LLM may draw from: lexicographic scoring, cluster-then-order
(regional grouping followed by intra-cluster ordering), greedy
nearest-in-time, reverse construction from tight-deadline requests, and
pair-tightness scoring weighted by pickup–delivery slack. The five families
were chosen to span the ordering paradigms represented in the PDPTW
insertion-heuristic literature. In the full-grid run, diversify fired at
generation three and produced the winning candidate; the substantive
interpretation of this outcome is deferred to Chapter 5.

## 3.7 LLM configuration and reproducibility

Candidate generation uses Google's `gemini-3.6-flash` model, accessed through
the official `google-genai` Python SDK (version 2.16.0). The choice is
deliberate: the free-tier quota (twenty requests per day) is sufficient for
the (1+λ = 2) evolutionary budget described in §3.5, and preliminary tests on
the lighter-weight `gemini-3.6-flash-lite` model found it inadequate — its
candidates violated the Julia interface contract in the majority of
generations, whereas `gemini-3.6-flash` produced compilable candidates on
essentially every call. Higher-tier Gemini models were not evaluated: they
sit outside the free-tier quota, and the aim of this dissertation is to
establish whether LLM-driven heuristic evolution is feasible under a
low-cost, publicly available model, not to benchmark model quality.

Sampling parameters are left at the SDK defaults; no temperature, top-p, or
top-k overrides are applied, and no system prompt is used. Reproducibility of
LLM outputs is deliberately not assumed: even with fixed sampling parameters,
repeated calls to the API do not return bit-identical completions, so the
evolutionary trajectory reported in Chapter 4 is one realisation of a
stochastic process rather than a deterministic sequence. This is a first-class
methodological limitation and is treated as such in Chapter 5. In contrast,
the *evaluation* half of the pipeline (§3.4) is deterministic: fixing the
random seed, MSLP restart budget, and injected candidate produces bit-identical
costs across repeated Julia invocations on the same machine.

The full software stack is: Julia 1.11.3 (installed via `juliaup`); Python
3.10.14 (installed via `pyenv`); Gurobi 12.0.3 with a WLS Academic licence
(expiring October 2026); `google-genai` 2.16.0 and `python-dotenv` 1.2.2 as
the only Python dependencies. The Julia package versions match those specified
by Barbosa, Tiwari and Melo (2026): `JuMP` 1.23.6, `Gurobi` 1.5.0, and
`Gurobi_jll` 12.0.2. All hardware runs used a MacBook Air (Apple Silicon,
arm64 macOS 14).

Every artefact needed to reproduce the results is committed to the
`srinidhi-dissertation` branch of a private GitHub repository. Each candidate
generated by the loop is content-hashed and appended to `logs/candidates.jsonl`
alongside its source code, prompt type, parent hash, and per-instance and
mean fitness values; each generation writes a row to `logs/generations.jsonl`
recording the champion of that generation and its lineage. The three
champions themselves are archived as standalone Julia files under
`src/python/llm_loop/champions/`, each with a metadata header giving its
generation index, content hash, fitness, and parent. All evaluation results —
the three-champion grid comparison, the multi-seed variance data across seeds
{17, 42, 100, 200, 500}, and the Gen 9–16 plateau confirmation — are retained
as JSON artefacts under `results/`. Reproduction of the central Chapter 4
table on a fresh machine takes approximately twenty minutes and requires only
Julia and Gurobi; a shell script and step-by-step instructions are provided
at the repository root. This reproduction has been verified cross-machine.

## 3.8 Ethical considerations
 
 ### 3.8 Ethical considerations

This dissertation is a computational study using publicly available secondary
data; it involves no human participants, no primary data collection, no
personally identifying information, and no commercially sensitive data. The
benchmark instances used throughout (§3.4) derive from the pickup and
delivery problem instances of Li and Lim (2001), which are themselves
constructed from Solomon's (1987) vehicle-routing benchmarks by paired
sampling; the PDPTW-SE adaptation used here is the multi-island (Type 1)
instance family released by Barbosa, Tiwari and Melo (2026) alongside their
paper.

Ethical approval was obtained through the University of Bristol Business
School Research Ethics Committee under reference 2026-33062-34847 (submitted
27 June 2026). The original application specified a study of the classical
Capacitated Vehicle Routing Problem (CVRP) using publicly available benchmark
sets; during the project, and in consultation with the supervisor, the scope
was refined to the PDPTW-SE benchmark family described above. The supervisor
confirmed in writing that this refinement remains within the scope of the
original approval, as it involves no change of data-collection method, no
introduction of human subjects, and no departure from the secondary-data
framing under which the application was granted. The original ethics approval
form and the supervisor's written confirmation are included in Appendix A.

The dissertation uses a large language model (Google `gemini-3.6-flash`,
§3.7) as a generator of candidate scoring functions inside the evolutionary
loop. All LLM-generated code was inspected before evaluation and is
committed to the repository as an auditable record of every candidate the
model produced. No LLM-generated content appears in the dissertation prose
itself; all writing is the author's own.
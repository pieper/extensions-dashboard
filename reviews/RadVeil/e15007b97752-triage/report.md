# AI review: RadVeil

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/rAum/SlicerRadVeil.git at commit `e15007b9775233acda4bc1c20975b932252e1de7`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:13:23Z; cost $0.09

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | minor | ok | minor |
| packaging | ok | ok | unknown |
| license | ok | ok | ok |
| soundness | minor | ok | minor |
| utility | ok | ok | ok |
| **overall** | minor issues | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer scripted module ("RadVeil Defacing", Utilities) that anonymizes the face and ears of head MRI/CT volumes by calling the external `radveil` Python package, then re-runs a face detector to verify the result and shows a linked before/after 3D review. It is aimed at researchers and imaging staff who need to share de-identified head scans.
- **flash-lite**: RadVeil is a 3D Slicer scripted extension for face and ear anonymization (defacing) of MRI and CT head volumes, verified via a face detector.
- **haiku**: RadVeil Defacing is a Slicer scripted module that removes the face and optionally the ears from MRI/CT head volumes, using the separately distributed `radveil` PyPI package, and lets the user review the result in linked 3D views. It is for researchers and clinicians who need a de-identification aid before sharing head scans.

## Findings from some reviewers

### Environment variable silently forces a non-anonymizing mock backend
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`RadVeil/RadVeilLib/backend.py:21`](https://github.com/rAum/SlicerRadVeil/blob/e15007b9775233acda4bc1c20975b932252e1de7/RadVeil/RadVeilLib/backend.py#L21): backend.load() returns the mock module whenever RADVEIL_SLICER_MOCK is set, regardless of the Developer-mode checkbox. The mock 'does NOT anonymize' (mock_radveil.py docstring), yet Anonymize still writes an 'Anonymized volume' and a report. The UI does show 'mock backend active' and the button suffix, but a user who inherited that variable from the environment could release unprotected data believing it was defaced. Scripted runs have no such warning.
  ```
  def mock_requested():
      return os.environ.get("RADVEIL_SLICER_MOCK", "").strip().lower() in ("1", "true", "yes", "on")
  ```
  Suggestion: Limit the mock to explicit developer use (e.g. require Developer mode for the env var too), and make the run fail or show a red verdict when the mock backend is active in an Anonymize run.

### Transitive dependencies of the radveil wheel not inspected
minor; environment; raised by haiku
- **haiku** (minor, low confidence, quote verified) [`RadVeil/RadVeilLib/backend.py:17`](https://github.com/rAum/SlicerRadVeil/blob/e15007b9775233acda4bc1c20975b932252e1de7/RadVeil/RadVeilLib/backend.py#L17): The module installs radveil>=0.1,<0.2 into Slicer's Python. The README says no ML framework is needed, but I could not check the wheel's dependency closure for pins or downgrades of packages Slicer bundles (for example numpy) or for PyTorch pulled from PyPI.
  ```
  REQUIREMENT = "radveil>=0.1,<0.2"
  ```
  Suggestion: Verify radveil's Requires-Dist metadata on PyPI for abi3 wheels and state in the review that its dependency tree is compatible with Slicer's bundled packages.

### Catalog revision 'release' existence could not be verified
info; packaging; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`RadVeil.json:6`](https://github.com/rAum/SlicerRadVeil/blob/e15007b9775233acda4bc1c20975b932252e1de7/RadVeil.json#L6): The entry relies on the 'release' branch, which RELEASING.md says is only created by tagging v0.1.0 through the release workflow. If the branch does not exist yet, the index cannot build the extension. I could not check the remote repository from here.
  ```
  "scm_revision": "release",
  ```
  Suggestion: Confirm that rAum/SlicerRadVeil has a 'release' branch pointing at a tagged v0.1.0 commit before merging, and record the commit examined.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): minor issues
Reviewed the extension source at the catalogued entry (branch `release`). The module code is clean: no telemetry, no data egress, no eval/pickle, heavy imports are lazy, the `radveil` package is installed only after a user action, and saved reports deliberately drop node/series names. Apache-2.0 with NOTICE and third-party attribution; CMake lists every shipped Python file and agrees with the catalog entry. Main caveats: the actual anonymization engine is an external PyPI wheel I could not inspect, and a user-selected segmentation node is wiped without confirmation. 🟢 Recommend merge — the three admission requirements appear met; remaining items are non-blocking.

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
SlicerRadVeil is a well-structured and meticulously implemented 3D Slicer extension for defacing MRI and CT head volumes using RadVeil. It follows Slicer conventions, provides extensive unit tests and a mock backend for offline use, adheres to safe dependency installation practices, and includes clear disclaimers. 🟢 Recommend merge.
Not checked: Full execution of tests inside a running 3D Slicer instance against the real PyPI radveil package

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
I found no malicious, concealed, or data-exfiltrating behavior in the files read. Network use is limited to a user-confirmed pip install of radveil>=0.1,<0.2 and an optional user-chosen wheel. Main concerns are soundness and verification: a global environment variable can silently switch the anonymizer to a non-anonymizing mock, and the catalog's "release" branch cannot be confirmed from the repository. The mock finding is minor, and the release-branch check is incomplete. Overall I would call this minor issues, pending the release-branch check.
Not checked: Remote repository at https://github.com/rAum/SlicerRadVeil.git: the 'release' branch, the commit it points to, and the v0.1.0 tag were not resolved.; The radveil PyPI package contents, dependency metadata, licenses, and bundled model weights (MediaPipe, SynthStrip) were not inspected.; docs/images/radveil, the test files under tests/, and the remaining tools (make_graphics, compose_screenshot content beyond the shown code) were not fully read, apart from the files listed in the prompt.; CI results were not available; I did not run any check or Slicer instance.; conversion.py lines 121 onward (report_to_json) and the full README tail were not read.
Questions for the author: Should RADVEIL_SLICER_MOCK be honored in Anonymize runs outside Developer mode, given that it produces unanonymized output?; Does the 'release' branch exist and point to the v0.1.0 tag at the time of index submission?; What does radveil 0.1.x declare as dependencies, and does any dependency pin or bring Slicer-bundled packages?


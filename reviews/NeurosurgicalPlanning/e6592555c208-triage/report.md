# AI review: NeurosurgicalPlanning

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/giakoum/SlicerNeurosurgicalPlanning.git at commit `e6592555c208e4a7eff545008263c1ad95edc4c8`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:31:01Z; cost $0.02

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | ok | ok | ok |
| packaging | minor | ok | minor |
| license | ok | ok | ok |
| soundness | concern | ok | minor |
| utility | minor | ok | minor |
| **overall** | minor issues | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: NeurosurgicalPlanning (module name SurgicalPlanning) is a scripted 3D Slicer module for preoperative neurosurgical planning: MRI/CT registration (BRAINSFit, optional Elastix/ANTs), skull/brain extraction (optional HD-BET, Wrap Solidify), tumor/ventricle/vessel segmentation, vesselness filtering (optional SlicerVMTK) and interactive 3D planning views. It targets neurosurgeons and researchers preparing multimodal neuroimaging.
- **flash-lite**: NeurosurgicalPlanning is a 3D Slicer extension providing multimodal preoperative neurosurgical planning tools, including registration, segmentation, vascular reconstruction, and 3D visualization.
- **haiku**: SurgicalPlanning is a scripted 3D Slicer module (packaged as the NeurosurgicalPlanning extension) for preoperative neurosurgical planning: MRI/CT registration, skull stripping, tumor and vascular segmentation, and 3D review. It targets neurosurgery researchers and planners who use Slicer.

## Disagreements (start here)

### D1. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### Author's own checklist states a real CMake/CPack build has not been performed
minor; packaging; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`docs/EXTENSION_SUBMISSION.md:21`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/docs/EXTENSION_SUBMISSION.md#L21): The committed CMake files look conventional (slicerMacroBuildScriptedModule with the .py and .ui listed), but the author documents that only a mock configuration was run, so it is unverified that the package builds and that the module loads from the installed package.
  ```
  1. Perform a **real** CMake extension configuration, build and CPack packaging using an installed matching Slicer SDK/build tree or the Slicer extension build infrastructure. The mock configuration does **not** prove that Slicer can build and package this extension.
  ```
  Suggestion: Confirm a successful extension build/package (or CI build) before merge and update the checklist accordingly.
- **haiku** (minor, medium confidence, quote verified) [`docs/EXTENSION_SUBMISSION.md:21`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/docs/EXTENSION_SUBMISSION.md#L21): The submission checklist states that only a mock CMake configuration was run, and that a real Slicer-SDK build and package are still required. The entry may therefore fail to build in the index infrastructure.
  ```
  1. Perform a **real** CMake extension configuration, build and CPack packaging using an installed matching Slicer SDK/build tree or the Slicer extension build infrastructure. The mock configuration does **not** prove that Slicer can build and package this extension.
  ```
  Suggestion: Rely on the index's CI build results for the PR; confirm the build passes before merge.

### Catalog entry tracks a moving branch instead of a pinned revision
minor; packaging; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`docs/ExtensionsIndex/NeurosurgicalPlanning.json:5`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/docs/ExtensionsIndex/NeurosurgicalPlanning.json#L5): scm_revision is 'main', so the built extension can change without a catalog update. The reviewed source is therefore not fixed. The policy allows branch references, but a tagged release revision would make the reviewed build reproducible.
  ```
  "scm_revision": "main",
  ```
  Suggestion: Pin scm_revision to a tagged release or commit hash for the reviewed baseline (v0.6.84).

### HD-BET and vesselness run synchronously on the GUI thread with processEvents
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified, other lines) [`SurgicalPlanning/SurgicalPlanning.py:2267`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/SurgicalPlanning/SurgicalPlanning.py#L2267): run_hd_bet(...) is called directly from the button handler (line 13439) and can take minutes on CPU. Because processEvents() is pumped before the call, the UI stays interactive and the user can trigger other module actions (segmentation edits, scene changes) while the input volume is being written and read back, which can produce inconsistent results or re-entrant state. The same pattern applies to the vesselness and Wrap Solidify paths.
  ```
  slicer.app.setOverrideCursor(qt.Qt.WaitCursor)
              slicer.app.processEvents()
  ```
  Suggestion: Move HD-BET and full-volume vesselness into a slicer.util.ProgressDialog / CLI-style worker or a background thread, disable the relevant controls while running, and report progress instead of pumping the event loop.

### No automated tests in the extension
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote no quote) [`SurgicalPlanning/SurgicalPlanning.py:1`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/SurgicalPlanning/SurgicalPlanning.py#L1): A search for 'ScriptedLoadableModuleTest' and 'def runTest' over the repository returned no matches, so none of the registration, segmentation or 3D-view logic is covered by Slicer's extension test harness. Regressions in a 24k-line single file will only be caught manually.
  Suggestion: Add a minimal ScriptedLoadableModuleTest that loads the module, creates a synthetic volume and exercises at least one non-optional workflow.

### README asserts the extension is already accepted into the Extensions Index
minor; utility; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`README.md:22`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/README.md#L22): The README tells users the extension is already published and installable from the Extension Manager, which pre-empts the outcome of this review and cannot be verified from the repository. If the entry is not merged, users following the installation instructions will not find the package.
  ```
  The extension was accepted into the official [3D Slicer Extensions Index](https://github.com/Slicer/ExtensionsIndex/blob/main/NeurosurgicalPlanning.json) when [PR #2413](https://github.com/Slicer/ExtensionsIndex/pull/2413) was merged on **October 16, 2026**.
  ```
  Suggestion: Reword to describe the submission as pending until the catalog entry is actually merged, or state the claim only after merge.

### Silent exception swallowing during temp-file cleanup
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`SurgicalPlanning/SurgicalPlanning.py:13511`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/SurgicalPlanning/SurgicalPlanning.py#L13511): In the HD-BET finally block, errors from os.remove are caught and discarded, so a failed cleanup of patient-derived temporary NIfTI files in the temp directory goes unreported. This is low-impact, but it hides cleanup failures.
  ```
  for path in (inputFile, outputFile, maskFile):
                  try:
                      if path and os.path.exists(path):
                          os.remove(path)
                  except Exception:
                      pass
  ```
  Suggestion: Log the exception with logging.warning, or narrow it to OSError.

### HD-BET dependency setup is delegated to the HDBrainExtraction extension on user action
info; environment; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`SurgicalPlanning/SurgicalPlanning.py:13379`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/SurgicalPlanning/SurgicalPlanning.py#L13379): This call can install Python packages (including PyTorch via that extension's PyTorchUtils path) into Slicer's environment. It is only reached when the user presses the HD-BET button and the installation logic belongs to the HDBrainExtraction extension, so it is not a violation of the PyTorch policy, but users should be told that pressing the button may install packages.
  ```
  from HDBrainExtractionTool import HDBrainExtractionToolLogic
                  dependencyLogic = HDBrainExtractionToolLogic()
                  dependencyLogic.setupPythonRequirements()
  ```
  Suggestion: Mention in the UI/README that the first HD-BET run may install Python packages through the HDBrainExtraction extension.

### Large binary screenshots committed to the repository
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote no quote) [`Documentation/Images/NeurosurgicalPlanning_Workflow.png:1`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/Documentation/Images/NeurosurgicalPlanning_Workflow.png#L1): Three PNGs of roughly 0.45-1.6 MB each (~3.5 MB total) are committed. This is acceptable for documentation but inflates every clone of the extension source.
  Suggestion: Optionally downscale the screenshots or host them outside the source tree.

### Large single-file module and long GUI-thread operations
info; soundness; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`SurgicalPlanning/SurgicalPlanning.py:13439`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/SurgicalPlanning/SurgicalPlanning.py#L13439): SurgicalPlanning.py is about 24,000 lines in one file. HD-BET and Wrap Solidify run synchronously on the GUI thread, with only processEvents calls for progress. This affects maintainability and responsiveness, not safety.
  ```
  run_hd_bet(
                  [inputFile],
                  [outputFile],
                  mode,
                  configFile,
                  device,
  ```
  Suggestion: Consider splitting the module and running heavy inference off the GUI thread with progress reporting.

### Single 1 MB / 24k-line module file
info; soundness; raised by deepseek
- **deepseek** (info, high confidence, quote no quote) [`SurgicalPlanning/SurgicalPlanning.py:1`](https://github.com/giakoum/SlicerNeurosurgicalPlanning/blob/e6592555c208e4a7eff545008263c1ad95edc4c8/SurgicalPlanning/SurgicalPlanning.py#L1): All logic, UI wiring and algorithms live in one file of 24357 lines, which makes review, testing and maintenance difficult and increases the chance that unrelated workflows break together.
  Suggestion: Consider splitting logic into separate modules (registration, segmentation, vesselness, 3D view) in a future release.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): minor issues
I read the catalog entry, CMake files, README, DEPENDENCIES.md, docs/EXTENSION_SUBMISSION.md, LICENSE/NOTICE and large parts of the 24k-line SurgicalPlanning.py, and searched it for network, subprocess, deserialization, pip-install and sys.path patterns. I found no network access, no telemetry, no subprocess/eval/pickle, no package installation by this extension (PyTorch is only imported, and HD-BET setup is delegated to the HDBrainExtraction extension on an explicit button press), and temp files are written to Slicer's temp directory and removed. Licensing is Apache-2.0 with NOTICE. Main issues are non-blocking: long HD-BET/vesselness work runs on the GUI thread with processEvents, no tests, and the README asserts the extension is already accepted into the index.
Not checked: The exact filename of the single file under SurgicalPlanning/Resources/UI/ was not listed; I could not confirm it is SurgicalPlanning.ui as referenced by SurgicalPlanning/CMakeLists.txt line 8.; I did not read the whole 24357-line SurgicalPlanning.py; roughly the first 120 lines, lines 13020-13760 and 23260-23360 were read in full, plus targeted regex searches for network, subprocess, deserialization, pip, sys.path and file-write patterns.; Observer removal in cleanup()/onClose() and parameter-node GUI observer handling were not verified line by line.; The referenced commit e6592555c208e4a7eff545008263c1ad95edc4c8 and the upstream repository state (including whether PR #​2413 was merged) could not be verified; the catalog entry pins scm_revision 'main', so the reviewed source is the snapshot provided here.; No build, packaging or runtime test was performed; the extension was not loaded in Slicer.; The three PNG screenshots were not inspected for embedded patient metadata (binary files not readable with the available tools).
Questions for the author: Can you confirm a successful real CMake/CPack build of the extension (not only the mock configuration) and that the module loads from the installed package?; Is the README statement that the extension is already accepted into the Extensions Index accurate at the time of this review?; Would you consider moving HD-BET and full-volume vesselness off the GUI thread to avoid re-entrancy during long runs?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The NeurosurgicalPlanning extension is well-structured, follows 3D Slicer scripted module conventions, includes proper licensing under Apache 2.0, avoids any unauthorized environment modifications or unsafe code patterns, and is fully ready for acceptance.
Not checked: Execution of interactive UI workflows in a live 3D Slicer session

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
I found no network, subprocess, pip, eval/exec, pickle, or deserialization calls in the module by search, and no package installation at import or startup. Optional features (HD-BET, Wrap Solidify, Elastix, ANTs) delegate installs to their own extensions and are guarded at runtime. The file is about 24k lines, so I read only the flagged regions. Packaging is minimal and consistent (EXTENSION_DEPENDS NA, build_dependencies empty, CMake installs the one .py and the .ui). The entry tracks the "main" branch rather than a fixed revision, which I note but do not treat as a security defect. No blocking issues found from the inspected parts.
Not checked: Most of SurgicalPlanning.py (about 24k lines) was not read; the review relied on keyword searches and targeted reads.; The HDBrainExtraction extension's setupPythonRequirements behaviour (whether it installs packages or PyTorch) was not inspected.; The scm_url repository at revision main was not fetched; the actual commit and any changes since v0.6.84 were not verified.; The real Slicer build, CPack packaging, and loading in Slicer were not run.; Binary image files (banner, icon, 3D and workflow screenshots) were not inspected.; The remote SurfaceWrapSolidify, SlicerElastix, SlicerANTs, and SlicerVMTK dependencies were not inspected.


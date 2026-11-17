# AI review: DICOMCBCTRecon

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/4burakfe/SlicerDICOMCBCTRecon.git at commit `fdc8d856a39562bd282e1d204896297b070ec05f`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-17T03:23:56Z; cost $0.85

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | ok |
| environment | unknown | ok | minor |
| packaging | unknown | ok | unknown |
| license | unknown | ok | unknown |
| soundness | unknown | ok | concern |
| utility | unknown | ok | minor |
| **overall** | minor issues | no concerns | incomplete |

## What each reviewer says the extension does

- **claude**: A Slicer DICOM plugin that detects rotational C-arm XA/XRF multi-frame runs in the DICOM browser. On Load it opens a window to reconstruct them into a 3D volume with FDK and/or SART in PyTorch, and it can subtract a second run (3D DSA).
- **gemini**: DICOMCBCTRecon is a 3D Slicer DICOM plugin for clinicians and researchers that recognizes rotational C-arm X-ray angiography runs (multi-frame XA/XRF spin acquisitions) in the DICOM browser. Upon loading, it provides an interactive preview dialog and reconstructs 3D cone-beam CT volumes (including 3D DSA subtraction spins and GE 3D calibrated trajectories) using PyTorch-accelerated FDK and ordered-subsets SART algorithms.
- **gpt**: DICOMCBCTRecon reconstructs rotational C-arm XA/XRF DICOM projections into cone-beam CT volumes using FDK or SART. It is intended for Slicer users loading and inspecting these acquisitions through the DICOM browser.

## Disagreements (start here)

### D1. Rating of soundness
rating dispute; category soundness; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (minor, concern, ok)**
Ratings: claude unknown, gemini ok, gpt concern
- claude on re-check: **rating minor**: I read DICOMCBCTRecon.py (all) and dialog.py lines 520-870. The structure is sound. It is a DICOMPlugin with a hidden ScriptedLoadableModule. Heavy imports (torch, SimpleITK, the Lib package) happen inside functions. Torch is only installed through PyTorchUtils, after the user confirms. Reconstruction shows a progress bar and a Stop button (dialog.py 546-575) and reports errors in the log (734-739). Temp files in the self-test use TemporaryDirectory. Three weaknesses keep it from being fully ok. (1) Reconstruction runs on the GUI thread and relies on slicer.app.processEvents() (dialog.py 544, 550), so the UI can stay partly unresponsive during long CPU runs. (2) Several broad `except Exception: pass` blocks hide errors, for example dialog.py 648-649 and the debug-only logging in _runSummary. (3) It inserts the module directory into sys.path (DICOMCBCTRecon.py 43-44), but the directory is specific to this module and the package name is specific. I found no blocking bug. Testing is limited to one synthetic self-test. I only skimmed the numerical code in reconstruction.py, geometry.py and xadata.py, so I could not verify its correctness. Claude's 'unknown' is too pessimistic, because 
- gpt on re-check: **rating concern**: The subtraction workflow can offer geometrically mismatched runs as having the same trajectory: DICOMCBCTRecon/DICOMCBCTRecon.py:196-203 checks frame dimensions and primary angles but not secondary angles, source distances or detector spacing; in particular, it rejects only when `if np.abs(candidate["primaryDeg"] - target["primaryDeg"]).max() > 2.0:`. DICOMCBCTRecon/DICOMCBCTReconLib/dialog.py:694-702 repeats only the shape/primary-angle checks before `integrals = integrals - convert(other)`. Runs with matching primary angles but different other geometry can consequently produce misleading subtraction artifacts. The criterion is not unknown or wholly unsound: dialog.py:546-550 provides progress and processes events, and test_cbct_reconstruction.py:160-164 contains synthetic reconstruction assertions. I inspected these paths and the geometry and reconstruction code; I did not run Slicer or the tests or verify results on real acquisitions.
- gemini on re-check: **rating ok**: Checked DICOMCBCTRecon/DICOMCBCTRecon.py (lines 58-105, 110-287, 341-414), DICOMCBCTRecon/DICOMCBCTReconLib/dialog.py (lines 141-260, 546-663, 714-820), DICOMCBCTRecon/DICOMCBCTReconLib/reconstruction.py (lines 1-638), DICOMCBCTRecon/DICOMCBCTReconLib/xadata.py (lines 1-524), DICOMCBCTRecon/DICOMCBCTReconLib/display.py (lines 50-118), and DICOMCBCTRecon/Testing/Python/test_cbct_reconstruction.py (lines 1-315). The module follows Slicer conventions cleanly: it uses ScriptedLoadableModule/DICOMPlugin structure, defers heavy imports (torch, pydicom, SimpleITK) inside functions, installs PyTorch only via PyTorchUtils with explicit user confirmation (DICOMCBCTRecon.py lines 341-374), updates progress and supports user cancellation via ReconstructionAborted (dialog.py lines 546-574, reconstruction.py lines 27-43), falls back from CUDA OOM to CPU gracefully (dialog.py lines 791-796), cleans up temporary directories and timers in a finally block (dialog.py lines 657-659, display.py lines 115-118), reports errors to the user rather than swallowing them (DICOMCBCTRecon.py lines 256-258, dialog.py lines 734-739), and includes thorough unit tests and a self-test. Soundness is 'ok'.


## Findings from some reviewers

### CPU SART refinement modifies cached projection data
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified, other lines) [`DICOMCBCTRecon/DICOMCBCTReconLib/reconstruction.py:32`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTReconLib/reconstruction.py#L32): On CPU, as_tensor shares the float32 NumPy input buffer; removeLowFrequencyInconsistency changes measured in place at line 554. The dialog caches that input, so another reconstruction with unchanged preprocessing can use altered projections and yield different results; a stopped refinement can also leave a partially altered cache.
  ```
      import torch
      device = device or torchDevice()
      measured = torch.as_tensor(p, dtype=torch.float32, device=device)
      volume = (torch.as_tensor(initial, dtype=torch.float32, device=device).clone() if initial is not None
                else torch.zeros(grid.shape, dtype=torch.float32, device=device))
      if initial is not None and consistencySigmaMm:
  ```
  Suggestion: Clone measured before in-place consistency correction, and add a CPU regression test checking input preservation and repeatability.

### Failed rerun can leave the previous result loadable
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTReconLib/dialog.py:593`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTReconLib/dialog.py#L593): If a user reruns unchanged settings after a successful preview and the rerun fails or is stopped, the old image and applied parameters remain. The button is enabled because they still match, despite the warning saying to reconstruct again; the user can load the previous result rather than a completed rerun.
  ```
          upToDate = self._isUpToDate()
          self.loadButton.setEnabled(upToDate and not self.busy)
          if self.busy:
              text = ""
          elif self.lastRunFailed:
              text = ("<span style='color:#d04040'>&#9888; The last reconstruction did not finish (see the log) - "
  ```
  Suggestion: Include lastRunFailed in the load eligibility check or invalidate the stored result at the start of a rerun.

### Quarter-turn frame correction leaves detector dimensions unchanged
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTReconLib/xadata.py:518`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTReconLib/xadata.py#L518): For a nonsquare frame with a 90- or 270-degree field-of-view rotation, the returned array has swapped rows and columns while readGeometry and ProjectionGeometry retain the original dimensions and pixel spacing. Filtering combines arrays sized from the rotated pixels with weights and detector coordinates sized from the unchanged geometry, which can fail or misrepresent the detector.
  ```
      if flipped:
          frames = frames[:, :, ::-1]
      quarterTurns = int(round(rotationDeg / 90.0)) % 4
      if quarterTurns:
          # np.rot90 with k>0 rotates counter-clockwise, which undoes a clockwise rotation
          frames = np.rot90(frames, k=quarterTurns, axes=(1, 2))
  ```
  Suggestion: Transform detector dimensions, spacing and collimator coordinates consistently with the pixels, and test nonsquare rotated acquisitions.

### Subtraction candidates are matched on primary angle alone
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTRecon.py:196`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTRecon.py#L196): Runs with the same dimensions and primary angles but different secondary angles, source distances or detector spacing are offered as having the same trajectory. The subtraction path checks shape and primary angle again but then subtracts the projections directly, so such a selection can produce misregistered subtraction artifacts.
  ```
                      candidate = xadata.sweepGeometry(otherGeometry, k)
                      if (candidate["nFrames"] != target["nFrames"] or candidate["rows"] != target["rows"]
                              or candidate["columns"] != target["columns"]):
                          continue
                      if np.abs(candidate["primaryDeg"] - target["primaryDeg"]).max() > 2.0:
                          continue
  ```
  Suggestion: Compare the full per-frame geometry and detector configuration, or explicitly warn and require registration when these differ.

### Scripting API `reconstructFile` does not check for PyTorch before running
info; soundness; raised by gemini
- **gemini** (info, high confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTRecon.py:83`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTRecon.py#L83): `reconstructFile()` does not call `ensureDependencies()` before calling `recon.fdk(...)`, which imports `torch`. If a script or test invokes `DICOMCBCTReconLogic().reconstructFile(...)` when PyTorch is not yet installed, it will raise an unhandled `ModuleNotFoundError: No module named 'torch'` rather than prompting or giving a clear dependency error.
  ```
      def reconstructFile(self, path, matrix=256, binning=1, filterName=None, truncation=0.25,
                          geometryOptions=None, sweep=0, log=logging.info):
          from DICOMCBCTReconLib import geometry as geom
          from DICOMCBCTReconLib import reconstruction as recon
          from DICOMCBCTReconLib import xadata
          import SimpleITK as sitk
  ```
  Suggestion: Consider checking `torch` availability or calling `ensureDependencies()` (or raising a descriptive `RuntimeError` in headless/scripted mode) at the start of `reconstructFile`.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read the module, plugin, dialog, DICOM reading, geometry, GE calibration, phantom and display code, plus the CMake files and LICENSE. I did not read reconstruction.py in full. I found no network access, subprocess, eval/exec, pickle or file deletion beyond the extension's own temporary preview folder. PyTorch is handled correctly: it is declared in build_dependencies and EXTENSION_DEPENDS, installed only through PyTorchUtils after a confirmation dialog, and never at import. The license is MIT. CMake installs every imported Python file. Remaining points are non-blocking: the reconstruction runs on the GUI thread with processEvents, no research-use disclaimer, a category mismatch between the catalog and CMake, and a moving `main` revision. 🟢 Recommend merge
Not checked: 
<parameter name="reconstruction.py was not read in full; only its imports were checked by search.">

### Gemini 4 Argon (`google/gemini-4-argon`): no concerns
DICOMCBCTRecon is a well-written, self-contained 3D Slicer DICOM plugin for cone-beam CT reconstruction (FDK and OS-SART) of rotational C-arm X-ray angiography runs. All files at commit `fdc8d856a39562bd282e1d204896297b070ec05f` were inspected. It has no security or safety concerns, performs all processing locally, uses `PyTorchUtils` with user confirmation for PyTorch installation, has a valid MIT license, and has clean CMake packaging matching the catalog entry. 🟢 Recommend merge.
Not checked: Runtime execution inside 3D Slicer with real clinical C-arm XA datasets (only static inspection of all repository source files was performed).; Binary contents of `screenshot.jpg` and `DICOMCBCTRecon/Resources/Icons/DICOMCBCTRecon.png`.

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): incomplete
The inspected code uses the PyTorch extension with confirmation and includes synthetic tests and usage documentation. Several non-blocking correctness issues affect cached CPU reconstructions, rotated projections, subtraction matching, and failed reruns. The source snapshot and MIT license were provided, but I could not independently resolve the catalog’s moving main revision or verify the terms of the cited reused SPECT code. 🔴 Do not merge yet: Review incomplete; verify the selected revision and distribution terms for the reused code.
Not checked: Independent network resolution of the catalog repository and main branch, and verification that the supplied source snapshot corresponds to commit fdc8d856a39562bd282e1d204896297b070ec05f.; Upstream SPECT plugin source and license/attribution requirements for the implementation described as taken from it in display.py.; Build, Slicer loading, automated tests, GPU/CPU execution, and validation against real acquisitions; tools permit inspection only.; Catalog submission checklist, CI results, prior catalog/source baseline, and maintenance history were not supplied.


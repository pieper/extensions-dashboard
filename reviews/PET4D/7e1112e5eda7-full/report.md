# AI review: PET4D

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/4burakfe/SlicerPET4D.git at commit `7e1112e5eda734cfa1c3e975a3e77c5416b1df12`
- Context: pull request 2449 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-14T17:20:48Z; cost $0.85

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | ok | minor |
| packaging | unknown | ok | unknown |
| license | unknown | ok | unknown |
| soundness | unknown | ok | concern |
| utility | unknown | ok | ok |
| **overall** | minor issues | no concerns | needs fixes |

## What each reviewer says the extension does

- **claude**: PET4D is a Slicer extension for dynamic, gated and static PET. It adds a DICOM plugin that loads PT series as sequences with SUV or Bq/ml values. It also provides modules for frame review and editing, motion correction, PET-to-CT/MR registration, and kinetic modelling (1TC, 2TC, Patlak, Logan, SRTM, SUVR). It is aimed at nuclear medicine researchers.
- **gemini**: PET4D provides a DICOM plugin for loading ECG-gated, dynamic, and static PET series into 3D Slicer as sequences or volumes in SUV (SUVbw, SUVlbm, SUVbsa) or Bq/ml while preserving frame timing, tracer, and decay metadata. It also provides interactive modules for nuclear medicine researchers and clinicians to review/edit dynamic frames, perform frame-by-frame motion correction, register dynamic PET to CT/MR, and perform regional and voxel-wise kinetic modeling (1TC, 2TC, Patlak, Logan, SRTM, SUVR).
- **gpt**: PET4D loads gated, dynamic and static PET DICOM series into Slicer and provides review, editing, motion correction, registration and kinetic modeling. It is intended for researchers working with PET images and time-activity data.

## Disagreements (start here)

### D1. Export silently overwrites a separate companion CSV
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DICOMGatedDynamicPET/DynamicPETModeling.py:394`](https://github.com/4burakfe/SlicerPET4D/blob/7e1112e5eda734cfa1c3e975a3e77c5416b1df12/DICOMGatedDynamicPET/DynamicPETModeling.py#L394): The save dialog selects the results filename, but exporting results.csv also truncates an existing results_TACs.csv without asking about that separate file. A user can lose unrelated existing data even when the selected results filename was new.
  ```
                      curves[f"{analysis.name(segmentId)} fit ({modelKey})"] = result["fitted"]
              tacPath = os.path.splitext(path)[0] + "_TACs.csv"
              with open(tacPath, "w", encoding="utf-8", newline="") as stream:
                  stream.write(kin.tacCsv(analysis.frames, curves, analysis.units))
  ```
  Suggestion: Check both output paths before writing and explicitly confirm replacement of each existing file, or let the user choose a non-conflicting companion filename.
- claude on re-check: **real: yes, minor**: DynamicPETModeling.py:395-397 writes <name>_TACs.csv without a separate overwrite prompt, and the QFileDialog at 1887 only confirms the main file. But the button tooltip (line 1150) and README (line 447) document the companion file, it is a user-initiated export into a user-chosen folder, and the result label (line 1895) lists both files. It is a small usability issue, not a blocking safety problem.
- gpt on re-check: **real: yes, blocking**: DICOMGatedDynamicPET/DynamicPETModeling.py:1882-1893 selects only the results path and directly calls exportCsv. Lines 395-397 then do `tacPath = os.path.splitext(path)[0] + "_TACs.csv"` and `with open(tacPath, "w", encoding="utf-8", newline="") as stream:` without checking or confirming the companion. Even if the selected CSV is new, a pre-existing companion is truncated; this is concrete unintended loss of user files. README.md:445-447 documents that two files are produced, but not that an existing companion is overwritten. Confirm each final destination before writing, including the derived companion.
- gemini on re-check: **real: yes, minor**: In DICOMGatedDynamicPET/DynamicPETModeling.py:1886-1895, `onExport()` prompts via `qt.QFileDialog.getSaveFileName` for `path` (which only checks overwrite for `path` itself), and then calls `self.logic.exportCsv(path, ...)` at lines 384-399 which unconditionally writes both `path` and `tacPath = os.path.splitext(path)[0] + "_TACs.csv"` with `"w"` mode. While real, writing a companion `<stem>_TACs.csv` file alongside a user-chosen export path is advertised behavior (DynamicPETModeling.py:91, 385) and is a minor UX/file-handling detail, not a blocking safety issue.

### D2. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **real: yes, info**: I found no network access, subprocess calls, pip installs or unsafe deserialization in a search for urlopen, requests, subprocess and pip_install. The deletions I found are limited to a tempfile.mkdtemp folder (DynamicPETEditor.py:2087-2097). The CSV companion overwrite is minor. I did not read every file, so I rate safety ok.
- gpt on re-check: **rating blocking**: The verified companion-file data-loss path in DICOMGatedDynamicPET/DynamicPETModeling.py:384-397 and 1882-1893 meets the blocking safety criterion; notably `with open(tacPath, "w", encoding="utf-8", newline="") as stream:` truncates without a separate confirmation. I also inspected the temporary DICOM export cleanup in DynamicPETEditor.py:2087-2097, which removes a newly created temporary directory, and searched the source for network, subprocess, unsafe deserialization, and file deletion APIs. This was not an exhaustive audit, and exact revision resolution and runtime testing were unavailable.
- gemini on re-check: **rating ok**: Checked across the repository for network calls, subprocesses, eval/exec/pickle, and file deletions (`DICOMGatedDynamicPET/DynamicPETEditor.py:2087-2097` only removes its own `tempfile.mkdtemp` folder; `DICOMGatedDynamicPET/DynamicPETModeling.py:384-399, 1882-1895` writes user-initiated CSV exports). There is no malicious behavior, telemetry, unsafe deserialization, or blocking safety defect.

### D3. Rating of soundness
rating dispute; category soundness; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (concern, ok)**
Ratings: claude unknown, gemini ok, gpt concern
- claude on re-check: **real: yes, minor**: The code is guarded (_guard on export, line 1893) and reports errors to the user. The only issue I verified is the unprompted companion-file overwrite (DynamicPETModeling.py:395-397). That is minor, so I rate soundness minor.
- gpt on re-check: **rating concern**: DICOMGatedDynamicPET/DynamicPETModeling.py:231-255 initializes curves with NaNs and, if progress returns false, `break`s but returns those partial curves; lines 269-276 wrap them in an Analysis. The UI's cancellation callback returns `not dialog.wasCanceled` (1635-1640), but lines 1645-1646 cache the resulting analysis, so canceling can leave incomplete data treated as complete rather than discard it. Fit-all also returns partial results on cancellation (342-344). There are positive features: map work has progress and cancellation (1911-1928), cleanup removes observers (2009-2012), and Testing/test_kinetics.py:1-4 describes independent simulated-curve tests. These were inspected, not run.
- gemini on re-check: **rating ok**: Checked `DICOMGatedDynamicPET/DICOMGatedDynamicPET.py:1-100`, `DICOMGatedDynamicPET/DynamicPETModeling.py:1-120, 360-430, 1870-1920`, `DICOMGatedDynamicPET/DynamicPETMotionCorrection.py:1-100`, `DICOMGatedDynamicPET/DynamicPETRegistration.py:1-100`, and `DICOMGatedDynamicPET/DynamicPETEditor.py:2070-2120`. The modules follow Slicer ScriptedLoadableModule conventions, separate logic from widgets, use progress dialogs and temporary/helper nodes with `try...finally` cleanup, and include unit tests.


## Findings from some reviewers

### Fit all excludes a segment even when the input is a plasma file
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DICOMGatedDynamicPET/DynamicPETModeling.py:324`](https://github.com/4burakfe/SlicerPET4D/blob/7e1112e5eda734cfa1c3e975a3e77c5416b1df12/DICOMGatedDynamicPET/DynamicPETModeling.py#L324): The GUI always selects a reference segment, including for plasma-file models; this unconditional exclusion skips that segment in Fit all. With one target segment and a plasma curve, preview is allowed but Fit all produces no segment result.
  ```
      def fitSegments(self, analysis, modelKey, referenceId=None, options=None, plasma=None, segmentIds=None,
                      progress=None):
          """{segment ID: result} of every segment (but the reference) or of segmentIds; a segment that cannot be
          fitted gets {"error": text}."""
          inputFunction, reference, blood = self.inputs(analysis, modelKey, referenceId, plasma)
          ids = [s for s in (segmentIds or analysis.segments) if s != referenceId]
  ```
  Suggestion: Allow an optional whole-blood segment for plasma-file models and include the selected target in batch fitting when it is not actually being used as a reference input.

### Missing target-frame values are treated as zero in SUVR
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DICOMGatedDynamicPET/DICOMGatedDynamicPETLib/kinetics.py:865`](https://github.com/4burakfe/SlicerPET4D/blob/7e1112e5eda734cfa1c3e975a3e77c5416b1df12/DICOMGatedDynamicPET/DICOMGatedDynamicPETLib/kinetics.py#L865): When a target segment has no voxels on some frame grids, segmentCurves records NaN for those frames, but this sum ignores the missing numerator while retaining its duration in the denominator. If the reference is present and the target exists in at least one frame, SUVR can be reported too low without a missing-data warning.
  ```
      target = float(np.nansum(w * tissue) / w.sum())
      ref = float(np.nansum(w * reference.frameMeans()) / w.sum())
      suvr = _ratio(target, ref)
  ```
  Suggestion: Reject incomplete curves or compute both target and reference on a common set of finite frames, with an explicit warning.

### Prepending module directory to sys.path at module import
info; environment; raised by gemini
- **gemini** (info, high confidence, quote verified) [`DICOMGatedDynamicPET/DICOMGatedDynamicPET.py:55`](https://github.com/4burakfe/SlicerPET4D/blob/7e1112e5eda734cfa1c3e975a3e77c5416b1df12/DICOMGatedDynamicPET/DICOMGatedDynamicPET.py#L55): Each scripted module (`DICOMGatedDynamicPET.py`, `DynamicPETEditor.py`, `DynamicPETModeling.py`, `DynamicPETMotionCorrection.py`, `DynamicPETRegistration.py`, `GatedDynamicPETSettings.py`) inserts its module directory at the front of `sys.path` if not already present. Slicer already adds scripted module directories to `sys.path` or supports importing helper packages placed alongside the module script, and the modules/packages here use distinct names (`DICOMGatedDynamicPETLib`, `DynamicPET*`), so the risk of name collisions with standard or bundled libraries is very low.
  ```
  _MODULE_DIR = os.path.dirname(os.path.abspath(globals().get("__file__", "") or "."))
  if globals().get("__file__") and _MODULE_DIR not in sys.path:
      sys.path.insert(0, _MODULE_DIR)
  ```
  Suggestion: Rely on Slicer's standard module path handling or append rather than prepend to `sys.path` if needed for standalone testing.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read the CMake files, the modeling module, the settings module and several helper libraries in full, and I searched all of the source. I found no network access, subprocess calls, pip installs, eval/exec, pickle, or text aimed at reviewers. The only deletion is a `shutil.rmtree` of the extension's own temporary export folder. The extension makes no environment changes beyond inserting its own module directory on sys.path. It uses only Slicer-bundled numpy, scipy, SimpleITK, pydicom and BRAINSFit. The LICENSE is MIT. The catalog entry is valid and uses `scm_revision` "main", a moving branch. CMake lists all the Python files the modules import. Minor points: large committed PNGs, the moving branch, and the absence of a clinical-use disclaimer. I did not read every file in full.
Not checked: 
<parameter name="items">Full line-by-line reading of DICOMGatedDynamicPET.py, DynamicPETEditor.py, DynamicPETMotionCorrection.py, DynamicPETRegistration.py, petseries.py, kinetics.py and sitkreg.py; I checked them only through regex searches.

### Gemini 4 Argon (`google/gemini-4-argon`): no concerns
PET4D is a well-structured, self-contained 3D Slicer extension for loading, reviewing, motion-correcting, registering, and kinetically modeling gated and dynamic PET series. It relies solely on Slicer's bundled Python/C++ libraries (numpy, scipy, SimpleITK, pydicom, BRAINSFit), performs no external network requests or package installations, is licensed under MIT, and has a valid CMake build configuration and catalog entry. 🟢 Recommend merge.
Not checked: Runtime execution of tests and interactive GUI layouts inside a running 3D Slicer instance.

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The modeling CSV export can silently overwrite an existing companion file, so it needs an overwrite check. Non-blocking modeling issues can also produce incorrect or incomplete results. CMake lists the scripts flagged by the automated scan. The source snapshot identifies the reviewed commit, but the moving catalog revision, remote access and copied third-party terms could not be independently verified. 🔴 Do not merge yet: fix the unintended file overwrite and complete revision and licensing verification.
Not checked: Cannot access GitHub or independently resolve main to the supplied commit 7e1112e5eda734cfa1c3e975a3e77c5416b1df12; exact snapshot identity and future branch contents are not verified.; Cannot run Slicer, build the extension, execute tests, or inspect CI results.; Could not independently verify the source license and required attribution for color tables copied from Tarvos, or verify the EasyReg source license beyond the local declaration.; No prior index revision, submission checklist, or PR diff was available for comparison.; Full numerical validation of PET quantification and registration and exhaustive review of all large source files were not performed.
Questions for the author: Can you provide the applicable license and attribution for the Tarvos color tables, and confirm it permits their redistribution here?


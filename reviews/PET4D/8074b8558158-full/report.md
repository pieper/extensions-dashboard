# AI review: PET4D

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/4burakfe/SlicerPET4D.git at commit `8074b8558158b7a4e9ba7f4d2adf4a589b7fa92b`
- Context: pull request 2449 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-17T21:23:05Z; cost $0.86

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

- **claude**: PET4D adds DICOM plugins that load gated, dynamic and static PET series as sequences in SUV or Bq/ml. It also adds modules for frame review/editing, motion correction, PET-to-CT/MR registration (BRAINSFit and SimpleITK) and kinetic modelling (1TC, 2TC, Patlak, Logan, SRTM, SUVR), for nuclear-medicine researchers.
- **gemini**: PET4D provides a DICOM plugin for loading ECG-gated, dynamic, and static PET series into 3D Slicer as volume sequences with SUV (bw/lbm/bsa) or Bq/ml scaling, decay correction, and frame timing metadata. It also provides interactive modules for frame-by-frame review/editing, motion correction, PET-to-CT/MR registration, and compartmental/graphical kinetic modeling (1TC, 2TC, Patlak, Logan, SRTM, SUVR) for nuclear medicine researchers.
- **gpt**: PET4D loads static, gated, and dynamic PET DICOM series into 3D Slicer with activity, SUV, and timing metadata. It provides researchers with frame review and editing, motion correction, registration, and kinetic modeling tools.

## Disagreements (start here)

### D1. CSV export silently overwrites the companion TAC file
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DICOMGatedDynamicPET/DynamicPETModeling.py:400`](https://github.com/4burakfe/SlicerPET4D/blob/8074b8558158b7a4e9ba7f4d2adf4a589b7fa92b/DICOMGatedDynamicPET/DynamicPETModeling.py#L400): The save dialog selects only the results CSV. Even if that file does not yet exist, exporting also opens the derived _TACs.csv in write mode without checking whether it exists, silently truncating an unrelated existing file in the chosen directory.
  ```
              tacPath = os.path.splitext(path)[0] + "_TACs.csv"
              with open(tacPath, "w", encoding="utf-8", newline="") as stream:
                  stream.write(kin.tacCsv(analysis.frames, curves, analysis.units))
  ```
  Suggestion: Check both output paths before writing and explicitly confirm each overwrite, or let the user select a new companion path; avoid writing either file if the user declines.
- claude on re-check: **real: yes, minor**: DynamicPETModeling.py:400-402 opens the derived <name>_TACs.csv with 'w' without checking whether it exists. The save dialog (1897-1898) only confirms the main CSV. This is real, but it only affects a file the extension names itself, next to a path the user chose, and the status label lists both files (1905). That is a small UX gap, not a concrete path to harm, so it is not blocking.
- gpt on re-check: **real: yes, blocking**: DICOMGatedDynamicPET/DynamicPETModeling.py:1895-1903 asks only for the results path and calls exportCsv with its default tacs=True. Lines 400-401 say `tacPath = os.path.splitext(path)[0] + "_TACs.csv"` and `with open(tacPath, "w", encoding="utf-8", newline="") as stream:`. A distinct pre-existing companion file is truncated without an existence check or confirmation, even when the chosen results path is new. The tooltip at 1154-1155 discloses a companion export, but not an overwrite. Confirm both destinations before writing.
- gemini on re-check: **real: yes, minor**: In DICOMGatedDynamicPET/DynamicPETModeling.py lines 389-404 and 1892-1906, `onExport()` asks the user for a single CSV save path via `QFileDialog.getSaveFileName` and passes it to `exportCsv()`, which writes both `path` and `tacPath = os.path.splitext(path)[0] + "_TACs.csv"` with `open(tacPath, "w", ...)` without checking if `<stem>_TACs.csv` already exists. While this behavior is real, it is a minor UX/soundness detail (writing a companion `<stem>_TACs.csv` next to a user-chosen export file) rather than a blocking safety vulnerability.

### D2. Fit all can erase an unrelated scene table with the same name
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DICOMGatedDynamicPET/DynamicPETModeling.py:1882`](https://github.com/4burakfe/SlicerPET4D/blob/8074b8558158b7a4e9ba7f4d2adf4a589b7fa92b/DICOMGatedDynamicPET/DynamicPETModeling.py#L1882): Any existing table with this name is treated as this module's results table, even if it belongs to another dataset or was created by the user. resultsTable calls table.Initialize() at line 362, clearing its prior contents without confirmation when Fit all is pressed; the results-table option is enabled by default.
  ```
          if self.tableCheck.checked:
              name = f"{analysis.sequence.GetName()} {key} results"
              existing = slicer.mrmlScene.GetFirstNodeByName(name)
              table = existing if existing is not None and existing.IsA("vtkMRMLTableNode") else None
              self.logic.resultsTable(analysis, results, key, name, table)
  ```
  Suggestion: Reuse only a table explicitly associated with the current sequence and module, otherwise create a uniquely named table; confirm before replacing unrelated data.
- claude on re-check: **real: yes, minor**: Lines 1882-1886 reuse any vtkMRMLTableNode with the name '<sequence> <key> results', and resultsTable line 362 calls table.Initialize(). That clears the node's contents. The name is module-specific, the node is a scene object (not a file) and is regenerated on each fit, and the option is user-visible. Collision with an unrelated table is unlikely, so this is a minor overwrite-without-confirmation bug, not a safety issue.
- gpt on re-check: **real: yes, blocking**: DICOMGatedDynamicPET/DynamicPETModeling.py:1151-1153 defaults the scene-table option on. Lines 1883-1886 use `existing = slicer.mrmlScene.GetFirstNodeByName(name)` and select any first matching table without checking provenance. Lines 361-362 then execute `table = tableNode.GetTable()` and `table.Initialize()`, destroying its previous contents. A same-named unrelated unsaved table can therefore be erased on Fit all; reuse only a verified owned table or create a unique one. If the first matching node is not a table, the code creates a new one instead.
- gemini on re-check: **real: yes, minor**: In DICOMGatedDynamicPET/DynamicPETModeling.py lines 1882-1886 and 356-387, when `self.tableCheck.checked` is True, `onFitAll()` looks up `slicer.mrmlScene.GetFirstNodeByName(f"{analysis.sequence.GetName()} {key} results")` without checking its `KM_PREFIX` attributes (`DynamicPET.Modeling.Sequence` / `DynamicPET.Modeling.Model`) and passes it to `resultsTable()`, which calls `table.Initialize()` at line 362. This is real, and checking the node attribute or matching the sequence ID before reusing the table node is a good soundness improvement, but overwriting an in-memory MRML table node specifically named `<sequence name> <model> results` when re-running kinetic fitting is minor and not a blocking safety issue.

### D3. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (ok, blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **rating ok**: A search for pip_install, subprocess, network, eval, exec, pickle and socket found nothing. The only deletions are shutil.rmtree on mkdtemp folders under the Slicer temporary path (DynamicPETEditor.py:2147-2157, plus atexit cleanup). File writes go to user-chosen CSV paths. I found no data exfiltration and no concrete path to harm. The D1 and D2 overwrites are minor behaviors, not safety blockers.
- gpt on re-check: **rating blocking**: Blocking because the verified D1 file truncation and D2 scene-table data loss have concrete paths to unintended destruction. In DICOMGatedDynamicPET/DynamicPETModeling.py:400-401, `with open(tacPath, "w", encoding="utf-8", newline="") as stream:` writes the unchecked companion; lines 1883-1886 and 361-362 show same-name table reuse and initialization. I also searched source for network, execution, deserialization and deletion APIs and inspected temporary DICOM export cleanup (DynamicPETEditor.py:2147-2157); this was not an exhaustive audit. The supplied commit identifier was not independently resolved, and no code was executed.
- gemini on re-check: **rating ok**: Inspected DICOMGatedDynamicPET/*.py and DICOMGatedDynamicPET/DICOMGatedDynamicPETLib/*.py. There are no network requests, telemetry, subprocess calls, dynamic code execution, unsafe deserialization, or hidden side effects. File writes occur only in temporary directories or user-selected export paths. The two issues raised as blocking safety findings (D1 and D2) are minor soundness/UX details.

### D4. Rating of soundness
rating dispute; category soundness; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (minor, concern, ok)**
Ratings: claude unknown, gemini ok, gpt concern
- claude on re-check: **rating minor**: I only inspected part of this large code base. The silent overwrite of the _TACs.csv companion file (399-402) and the reuse and clearing of a same-named table (1882-1886 with 362) are minor soundness issues. Errors are guarded (_guard) and reported to the user, and fit failures are recorded per segment. I saw no concern-level defects.
- gpt on re-check: **rating concern**: DICOMGatedDynamicPET/DynamicPETModeling.py:335-349 returns accumulated partial results after cancellation: `if progress is not None and progress(i + 1, len(ids), analysis.name(segmentId)) is False:` followed by `break` and `return results`. Lines 1872-1886 treat this as a completed fit, report the count fitted and can overwrite the scene results table with partial results without identifying cancellation. This can mislead users and discard prior results; it is an ordinary correctness concern separate from the safety issue. The inspected implementation does provide a progress dialog and reports per-segment errors (lines 343-346 and 1852-1860). No runtime or scientific validation was possible.
- gemini on re-check: **rating ok**: Inspected the module and library implementations across DICOMGatedDynamicPET/ (including DynamicPETModeling.py, DynamicPETEditor.py, DynamicPETMotionCorrection.py, DynamicPETRegistration.py, DICOMGatedDynamicPET.py) and Testing/. The extension follows 3D Slicer conventions well (`ScriptedLoadableModule` classes, `VTKObservationMixin`, progress dialogs, error handling, and unit tests). Minor UX edge cases like D1 and D2 do not rise to a concern rating.


## Findings from some reviewers

### Module directory is prepended to the shared Python import path
minor; environment; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DICOMGatedDynamicPET/DynamicPETModeling.py:45`](https://github.com/4burakfe/SlicerPET4D/blob/8074b8558158b7a4e9ba7f4d2adf4a589b7fa92b/DICOMGatedDynamicPET/DynamicPETModeling.py#L45): At module import this changes import resolution for the entire Slicer process, potentially shadowing other modules with files in this directory. Other PET4D module scripts use the same pattern.
  ```
  _MODULE_DIR = os.path.dirname(os.path.abspath(globals().get("__file__", "") or "."))
  if globals().get("__file__") and _MODULE_DIR not in sys.path:
      sys.path.insert(0, _MODULE_DIR)
  ```
  Suggestion: Use the module loading and package paths provided by Slicer where possible rather than prepending a directory globally.

### Registration uses a synchronous CLI call
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified, other lines) [`DICOMGatedDynamicPET/DynamicPETRegistration.py:245`](https://github.com/4burakfe/SlicerPET4D/blob/8074b8558158b7a4e9ba7f4d2adf4a589b7fa92b/DICOMGatedDynamicPET/DynamicPETRegistration.py#L245): During a long BRAINSFit invocation, this synchronous call can leave the Slicer interface unresponsive until the CLI returns, limiting progress feedback and cancellation during that invocation.
  ```
      @staticmethod
      def _runCli(module, parameters):
          cliNode = slicer.cli.runSync(module, None, parameters, update_display=False)
  ```
  Suggestion: Use an asynchronous CLI with status observers and cancellation where feasible.

### Catalog entry PET4D.json committed in extension source repository
info; packaging; raised by gemini; **quote not found in source**
- **gemini** (info, high confidence, quote quote not found) [`PET4D.json:1`](https://github.com/4burakfe/SlicerPET4D/blob/8074b8558158b7a4e9ba7f4d2adf4a589b7fa92b/PET4D.json#L1): The catalog entry file `PET4D.json` belongs in the Slicer Extensions Index repository rather than inside the extension's own source repository. It is harmless, but unnecessary in the source repository.
  ```
  PET4D.json  (365 bytes)
  ```
  Suggestion: Optionally remove `PET4D.json` from the extension source repository, as the catalog entry is maintained in `Slicer/ExtensionsIndex`.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read the catalog entry, both CMake files, the LICENSE and the modelling, settings, plot and settings-library code. I also ran searches over the whole source. I found no network access, subprocess calls, pip installs, eval/exec, pickle or downloads. File writes go only to user-chosen CSV paths, temporary DICOM export folders that are cleaned up, and the DICOM database after an explicit export. The license is MIT. EXTENSION_DEPENDS "NA" matches an empty build_dependencies list, and the Python files that are not listed in the plugin's script list are installed by their own module macros. Remaining points are minor: the revision is the moving branch "main", the plugin confidence of 1.05 outranks other loaders, and the 1.5 MB module icon is large. I did not read every file.

### Gemini 4 Argon (`google/gemini-4-argon`): no concerns
PET4D is a well-engineered, self-contained 3D Slicer extension for loading, reviewing, motion-correcting, registering, and kinetically modeling gated and dynamic PET series. It relies solely on Slicer-bundled Python packages (`numpy`, `scipy`, `SimpleITK`, `pydicom`) and built-in CLI modules (`BRAINSFit`, `BRAINSResample`), has no network activity or unsafe operations, is released under the MIT license, and has valid CMake packaging and thorough tests.

🟢 Recommend merge
Not checked: Runtime execution of the modules and tests inside a live 3D Slicer environment

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The source includes documentation, synthetic tests, and an MIT license; CMake lists the modules that the scan suggested were missing. Two export/result paths can silently destroy existing user data and should be fixed. The exact revision selected by the moving catalog branch and the licensing of copied color tables could not be independently verified. 🔴 Do not merge yet: fix the unintended overwrites and verify the selected revision and copied-material permissions.
Not checked: The catalog entry uses main; network access was unavailable, so the branch could not be resolved to the stated commit 8074b8558158b7a4e9ba7f4d2adf4a589b7fa92b or checked for accessibility.; The upstream Tarvos color table license and attribution requirements, and the upstream EasyReg source license, could not be independently verified.; No extension build, Slicer session, test execution, external dependencies, CI results, or real-patient-data validation could be inspected.; The source is large; targeted searches and selected execution paths were inspected, not every line.
Questions for the author: Can you provide the Tarvos color-table source and its distribution terms and required attribution?


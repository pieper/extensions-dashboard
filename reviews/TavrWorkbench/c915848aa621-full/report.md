# AI review: TavrWorkbench

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/pcdslab/TavrWorkbench.git at commit `c915848aa62164d373166e7c2fd9984f5f8c826e`
- Context: pull request 2402 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-13T17:23:56Z; cost $0.97

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | concern | concern |
| packaging | unknown | blocking | concern |
| license | unknown | minor | minor |
| soundness | unknown | ok | concern |
| utility | unknown | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: TavrWorkbench is a Slicer module for clinicians and researchers who review TAVR CT segmentations and measurements. It lets them rate masks, correct contours and hinge points, regenerate annulus measurements, and build and export a parametric valve STL.
- **gemini**: TavrWorkbench is a 3D Slicer extension for clinicians and researchers to review and edit automated TAVR (transcatheter aortic valve replacement) CT segmentations, anatomical contours, hinge points, and height measurements across a batch of cases. It also includes an annular-plane recomputation pipeline and a parametric TAVR valve mesh generator that exports placed valve models to STL.
- **gpt**: TavrWorkbench helps reviewers inspect, rate, and correct TAVR CT segmentations and anatomical measurements case by case. It also regenerates annular measurements and produces a parametric valve model for export.

## Disagreements (start here)

### D1. Case IDs can escape the output folder or collide
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (2 of 2)**
- **gpt** (blocking, high confidence, quote verified) [`TavrWorkbench/TavrWorkbenchLib/storage.py:39`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/TavrWorkbench/TavrWorkbenchLib/storage.py#L39): A manifest case_id of '..' remains '..'; case_dir joins it to the selected output root, so saving a review or mask writes into its parent and can overwrite existing review.json or segmentation.seg.nrrd. Distinct IDs such as 'a/b' and 'ab' also map to the same folder, so one case can overwrite another case's corrections while their status entries remain distinct.
  ```
  def safe_name(name):
      safe = "".join(c for c in str(name) if c.isalnum() or c in ("_", "-", ".")).strip()
      return safe or "unknown_case"
  ```
  Suggestion: Reject '.' and '..', enforce resolved-path containment, and use a collision-resistant mapping or reject duplicate normalized case IDs before loading.
- gpt on re-check: **real: yes, blocking**: TavrWorkbench/TavrWorkbenchLib/storage.py:39-41: `safe = "".join(c for c in str(name) if c.isalnum() or c in ("_", "-", ".")).strip()`; lines 83-95: `return self.path(safe_name(cid))`. The input case ID is preserved by cases.py:19-20 and not validated by read_data_map at lines 88-98. Thus '..' selects the output root's parent, and a/b and ab collide. storage.py:268-271 writes the review there; TavrWorkbench.py:798-801 also saves a mask there. Existing files or another case's corrections can be overwritten.
- gemini on re-check: **real: yes, minor**: In TavrWorkbench/TavrWorkbenchLib/storage.py:39-41, safe_name(name) strips non-[A-Za-z0-9_-.] characters rather than rejecting traversal tokens or normalizing separators, so safe_name('..') returns '..' and safe_name('a/b') == safe_name('ab') == 'ab'. Furthermore, storage.py:106 uses self.path(str(cid)) directly without safe_name. However, in normal use case_ids come from a user-selected local data_map.json, and OutputStore only writes fixed filenames (review.json, segmentation.seg.nrrd, etc.), so this is a minor path sanitization bug rather than a blocking exploit.

### D2. Dataset packaging can delete files outside the case directory
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (2 of 2)**
- **gpt** (blocking, high confidence, quote verified) [`TavrWorkbench/tools/package_dataset.py:121`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/TavrWorkbench/tools/package_dataset.py#L121): safe_name permits the case ID '..', and package constructs case_rel as cases/<ID>. For such a manifest, cleanup walks cases/.., i.e. the whole selected output directory, and removes files not in the new entry, including unrelated data. Even normal IDs cause untracked files in an existing case folder to be deleted without confirmation.
  ```
  def remove_stale_files(out_dir, case_rel, entry):
      """Delete files in this case's folder that the new map no longer references (left by an earlier
      run, e.g. image.nii.gz / label.seg.nrrd from before the case-id naming). Returns how many."""
      case_dir = os.path.join(out_dir, *case_rel.split("/"))
      keep = {os.path.normcase(os.path.join(out_dir, *p.split("/"))) for p in referenced_paths(entry)}
  ```
  Suggestion: Reject dot components, verify resolved paths remain beneath a dedicated case directory, and remove only files recorded as generated by a previous run, with explicit confirmation or a non-destructive default.
- gpt on re-check: **real: yes, blocking**: TavrWorkbench/tools/package_dataset.py:97-98: `return "".join(c for c in str(name) if c.isalnum() or c in "_-.") or "case"`; lines 144-152 derive `case_rel = f"cases/{safe_name(cid)}"` after requiring an existing image. Lines 124-131 walk that path and call `os.remove(full)` for every file not in the new entry. For '..', if the intermediate cases directory exists, the walk reaches the output root and recursively removes other files and case data. Ordinary case folders also have all unreferenced files removed, not just files tracked from a previous run.
- gemini on re-check: **real: yes, minor**: In TavrWorkbench/tools/package_dataset.py:97-98, safe_name('..') returns '..', and lines 121-135 (remove_stale_files) walk os.path.join(out_dir, 'cases', '..') (i.e. out_dir) and call os.remove(full) on any file not in keep. However, package_dataset.py is a standalone CLI helper script in tools/ (not imported or executed by the Slicer module) and requires a malformed case_id='..' in the user's input JSON to traverse out of cases/<id>, so it is a minor bug rather than a blocking safety issue.

### D3. TavrWorkbenchLib Python files are missing from MODULE_PYTHON_SCRIPTS in CMakeLists.txt
partial; category packaging; raised by gemini, gpt; outcome after cross-examination: **real, blocking (2 of 2)**
- **gemini** (blocking, high confidence, quote verified) [`TavrWorkbench/CMakeLists.txt:5`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/TavrWorkbench/CMakeLists.txt#L5): `TavrWorkbench/TavrWorkbench.py` imports 11 modules from the `TavrWorkbenchLib/` package (`annular_plane.py`, `annulus_pipeline.py`, `cases.py`, `constants.py`, `geometry.py`, `measurement_editor.py`, `rating_table.py`, `segmentation_editor.py`, `storage.py`, `valve_generator.py`, `valve_panel.py`, and `__init__.py`), but `TavrWorkbench/CMakeLists.txt` only lists `${MODULE_NAME}.py` in `MODULE_PYTHON_SCRIPTS`. When built and packaged by the Slicer Extension build system, none of `TavrWorkbenchLib/*.py` will be installed, causing `ModuleNotFoundError: No module named 'TavrWorkbenchLib'` when Slicer attempts to load `TavrWorkbench`.
  ```
  set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    )
  ```
  Suggestion: Add all `TavrWorkbenchLib/*.py` files (`TavrWorkbenchLib/__init__.py`, `TavrWorkbenchLib/annular_plane.py`, `TavrWorkbenchLib/annulus_pipeline.py`, `TavrWorkbenchLib/cases.py`, `TavrWorkbenchLib/constants.py`, `TavrWorkbenchLib/geometry.py`, `TavrWorkbenchLib/measurement_editor.py`, `TavrWorkbenchLib/rating_table.py`, `TavrWorkbenchLib/segmentation_editor.py`, `TavrWorkbenchLib/storage.py`, `TavrWorkbenchLib/valve_generator.py`, `TavrWorkbenchLib/valve_panel.py`) to `MODULE_PYTHON_SCRIPTS` in `TavrWorkbench/CMakeLists.txt`.
- **gpt** (major, high confidence, quote verified) [`TavrWorkbench/CMakeLists.txt:5`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/TavrWorkbench/CMakeLists.txt#L5): TavrWorkbench.py imports TavrWorkbenchLib.cases and other helpers at module import, but no helper files are listed for installation in this CMake file. A catalog-built package therefore lacks the package and cannot import the module, even though running from the source tree can work. This is a non-blocking extension packaging defect under the index admission policy.
  ```
  set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    )
  
  set(MODULE_PYTHON_RESOURCES
    Resources/Icons/${MODULE_NAME}.png
  ```
  Suggestion: Install all TavrWorkbenchLib Python files with their package directory preserved, and test loading the installed package in a clean Slicer.
- gpt on re-check: **real: yes, blocking**: TavrWorkbench/CMakeLists.txt:5-7 lists only `  ${MODULE_NAME}.py`, and lines 16-20 pass just the listed scripts and resources to the Slicer macro. Root CMakeLists.txt:20-22 only adds that module directory; neither file installs the helper package separately. TavrWorkbench/TavrWorkbench.py:30 imports `from TavrWorkbenchLib.cases import (case_id_of, has_contours, has_measurements, is_file, is_image_path,`. The built package therefore lacks required imports and the module cannot load. Broken loading is blocking under the severity rubric; this is distinct from the index policy's separate admission recommendation.
- gemini on re-check: **real: yes, blocking**: TavrWorkbench/TavrWorkbench.py:30-44 imports modules from TavrWorkbenchLib at module import time, while TavrWorkbench/CMakeLists.txt:5-7 only lists ${MODULE_NAME}.py in MODULE_PYTHON_SCRIPTS. Because slicerMacroBuildScriptedModule only installs files listed in SCRIPTS and RESOURCES, the packaged extension will fail to load with ModuleNotFoundError: No module named 'TavrWorkbenchLib'. Under the review rubric, broken loading of the packaged extension is blocking.

### D4. macOS installer can delete an existing Slicer installation after a failed start
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (2 of 2)**
- **gpt** (blocking, high confidence, quote verified) [`install/install_mac.sh:224`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/install/install_mac.sh#L224): The installer may reuse an existing same-version Slicer application, not necessarily one it installed. If macOS terminates that process during configuration, the recovery path can recursively delete that application without asking, including any user modifications stored in it; a process termination does not prove the application is disposable.
  ```
          local broken="$SLICER_APP"
          rm -f "$MARKER"
          install_slicer fresh
          if [ "$SLICER_APP" = "$broken" ]; then
              # The standard location holds the broken copy itself: replace it with a fresh download
              rm -rf "$broken" 2>/dev/null || true
  ```
  Suggestion: Never automatically remove an existing Slicer application; install a separate copy or request explicit confirmation after identifying its ownership and backing it up.
- gpt on re-check: **real: yes, blocking**: install/install_mac.sh:144-149 reuses an existing matching-version application, and lines 182-213 return 2 for a signal-terminated process with no result, not just a proven corrupt installation. Lines 224-231 contain `            rm -rf "$broken" 2>/dev/null || true` when the fresh lookup reuses the same path. This can delete a pre-existing Slicer application and its user modifications without consent after an unrelated termination.
- gemini on re-check: **real: yes, minor**: In install/install_mac.sh:148-150, if /Applications/Slicer.app already exists and matches the latest release version, the script sets SLICER_APP to it even if the user installed it independently. In configure_slicer (lines 220-231), if Slicer exits with status >= 128 before writing the result file (rc == 2), line 229 executes rm -rf "$broken" on that /Applications/Slicer.app and replaces it with a fresh download. While install/install_mac.sh is a standalone curl|bash helper script rather than part of the Slicer Extension Manager build, deleting an existing /Applications/Slicer.app without confirmation is a minor issue worth fixing.

### D5. Global VTK warning display disabled at module import time
partial; category environment; raised by gemini, gpt; outcome after cross-examination: **real, major (2 of 2)**
- **gemini** (major, high confidence, quote verified) [`TavrWorkbench/TavrWorkbench.py:46`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/TavrWorkbench/TavrWorkbench.py#L46): At module import time (when Slicer starts up and discovers scripted modules), `TavrWorkbench.py` disables VTK warning display globally across the entire Slicer process. This affects all users and all other modules even if the user never opens `TavrWorkbench`.
  ```
  # Suppress VTK warnings globally to prevent console flooding and UI freezing
  vtk.vtkObject.GlobalWarningDisplayOff()
  ```
  Suggestion: Remove `vtk.vtkObject.GlobalWarningDisplayOff()` at import time, or scope warning suppression locally around specific noisy operations and restore the previous `GlobalWarningDisplay` state in a `finally:` block.
- **gpt** (major, high confidence, quote verified) [`TavrWorkbench/TavrWorkbench.py:46`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/TavrWorkbench/TavrWorkbench.py#L46): Once the module imports, VTK warnings from Slicer and other extensions are suppressed globally, including for users who never open TavrWorkbench. This hides diagnostic information unrelated to this module.
  ```
  # Suppress VTK warnings globally to prevent console flooding and UI freezing
  vtk.vtkObject.GlobalWarningDisplayOff()
  ```
  Suggestion: Remove the global toggle or narrowly handle the specific warnings in the operation that causes them.
- gpt on re-check: **real: yes, major**: TavrWorkbench/TavrWorkbench.py:46-47 has `vtk.vtkObject.GlobalWarningDisplayOff()` at top level, outside any module class or user action. When the module successfully imports, this switches off VTK warnings process-wide, hiding diagnostics from Slicer and other modules; the effect is contingent on the helper imports at lines 30-44 succeeding.
- gemini on re-check: **real: yes, major**: TavrWorkbench/TavrWorkbench.py:47 executes vtk.vtkObject.GlobalWarningDisplayOff() at module top level. When Slicer starts up and imports scripted modules during discovery, this globally disables VTK warning display across the entire Slicer session for all modules, even if the user never opens TavrWorkbench.

### D6. Navigating away discards unsaved mask edits without warning
single; category soundness; raised by gpt; outcome after cross-examination: **real, minor (2 of 2)**
- **gpt** (major, high confidence, quote verified) [`TavrWorkbench/TavrWorkbench.py:513`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/TavrWorkbench/TavrWorkbench.py#L513): The leave check covers hinge and measurement edits but not segmentation edits. When a reviewer paints a mask and navigates without clicking Save Mask, loading the next case removes the current segmentation node, losing the changes without a prompt.
  ```
      def _confirmLeaveCase(self):
          """Ask about unapplied hinge moves / unsaved contour edits. Returns False if the user cancels."""
          if self._case_loaded and self.meas.hinges_moved():
              if not slicer.util.confirmOkCancelDisplay(
                      "The hinge points were moved but not applied (Annular Plane tab). Discard these moves?"):
                  return False
  ```
  Suggestion: Track segmentation modifications and prompt to save, discard, or cancel navigation.
- gpt on re-check: **real: yes, major**: TavrWorkbench/TavrWorkbench.py:513-520 only checks `self.meas.hinges_moved()` and `self.meas.is_dirty()` before returning true; loadCase at lines 530-540 then loads the next case. Lines 553-562 remove nodes returned by `self.seg.release()`, including the segmentation node (segmentation_editor.py:99-111). saveCase at TavrWorkbench.py:715-760 does not save the mask; saveMask at lines 786-801 is separate. Navigating or using Save & Next without saving the mask can silently discard potentially extensive edits. This is non-blocking soundness feedback under the admission policy.
- gemini on re-check: **real: yes, minor**: TavrWorkbench/TavrWorkbench.py:513-528 (_confirmLeaveCase) checks self.meas.hinges_moved() and self.meas.is_dirty(), and prompts to save contour/height edits via saveCase, which does not save the segmentation mask (saved separately via saveMask at line 786). Navigating to another case calls _loadCaseData -> _clearCaseNodes (lines 553-566), which removes the segmentation node from the MRML scene without warning if the user edited segments in the embedded Segment Editor without clicking Save Mask.

### D7. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, minor)**
Ratings: claude unknown, gemini ok, gpt blocking
- gpt on re-check: **rating blocking**: Inspected storage and case parsing, dataset packaging, and the macOS installer. Concrete data-loss paths establish a blocking safety rating: storage.py:86-87 says `return self.path(safe_name(cid))`, package_dataset.py:127-131 removes unreferenced walked files, and install/install_mac.sh:227-230 may recursively delete a reused Slicer app. The exact source revision and runtime behavior were not independently verified; no code was executed.
- gemini on re-check: **rating minor**: Checked TavrWorkbench/TavrWorkbench.py, TavrWorkbench/TavrWorkbenchLib/*.py, TavrWorkbench/tools/package_dataset.py, and install/*. There is no malicious behavior, telemetry, or unsafe deserialization; the path sanitization issues in storage.py:39-41 and tools/package_dataset.py:97-98,121-135 and the recovery rm -rf in standalone install/install_mac.sh:229 are real but minor issues.

### D8. Rating of soundness
rating dispute; category soundness; raised by claude, gemini, gpt; outcome after cross-examination: **settled: minor (concern, minor)**
Ratings: claude unknown, gemini ok, gpt concern
- gpt on re-check: **rating concern**: Inspected case navigation, saving, and segmentation controller. TavrWorkbench/TavrWorkbench.py:519-520 says `        if not (self._case_loaded and self.meas.is_dirty()):` followed by `            return True`; the subsequent case load removes the segmentation without checking mask edits, and normal Save & Next does not invoke the separate saveMask method (lines 715-801). This can silently lose user work. Assessment is based on source inspection, not a Slicer runtime test.
- gemini on re-check: **rating minor**: Checked TavrWorkbench/TavrWorkbench.py and TavrWorkbench/TavrWorkbenchLib/*.py. The module structure, UI, and cleanup are generally well-written, with minor soundness issues such as unsaved Segment Editor mask edits not being checked in _confirmLeaveCase (TavrWorkbench.py:513-528) and five stale .patch files left in the repository root.


## Findings from some reviewers

### A failed image load is still marked as a loaded case
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`TavrWorkbench/TavrWorkbench.py:538`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/TavrWorkbench/TavrWorkbench.py#L538): _loadCaseData returns False when the image cannot be loaded, but this caller ignores the result and sets _case_loaded to True. The interface can then show the failed case as loaded and permit review actions despite the missing volume.
  ```
              self._cacheReview()      # keep in memory so Prev/Next doesn't lose ratings
          self.current_index = idx
          self._loadCaseData()
          self._case_loaded = True
          self._restoreReview(idx)
  ```
  Suggestion: Check the return value and leave the case unloaded, with review actions disabled, on failure.

### Documentation describes workflows absent from the current module
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`README.md:27`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/README.md#L27): The inspected module sets up a JSON map selector and calls read_data_map; it does not implement the documented directory input. The README also describes a three-option rating scheme while the current interface uses Approve and Flag, which can mislead new reviewers.
  ```
  The Input panel offers two ways to load a dataset. Choose one using the Directory or JSON Manifest option.
  
  ### Directory Mode
  
  Select a folder that contains your volumes in .nii, .nii.gz or .nrrd format. The module finds the cases in one of three ways.
  
  ```
  Suggestion: Update the tutorial and output descriptions to match the current UI, and provide a representative sample manifest and clinical-use limitations.

### Placeholder SampleData entries registered at startup
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`TavrWorkbench/TavrWorkbench.py:86`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/TavrWorkbench/TavrWorkbench.py#L86): `registerSampleData()` registers two template placeholder sample datasets (`TavrWorkbench1` and `TavrWorkbench2`) pointing to generic Slicer testing data with missing icons (`TavrWorkbench1.png`, `TavrWorkbench2.png`).
  ```
      # TODO: replace these placeholder sample data entries with real sample datasets for TavrWorkbench,
      # or remove this function (and the startupCompleted connection above) entirely.
      SampleData.SampleDataLogic.registerCustomSampleDataSource(
          category="TavrWorkbench",
          sampleName="TavrWorkbench1",
  ```
  Suggestion: Either remove `registerSampleData()` and its `startupCompleted()` connection, or provide real sample data for `TavrWorkbench`.

### Extension uses CC BY-NC-ND 4.0 license (NonCommercial, NoDerivatives)
info; license; raised by gemini
- **gemini** (info, high confidence, quote verified) [`LICENSE.md:1`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/LICENSE.md#L1): The repository is licensed under CC BY-NC-ND 4.0 (`LICENSE.md` and `LICENSE.txt`), which permits reproduction and sharing of the unmodified material for non-commercial purposes only and prohibits sharing adapted material. While this permits verbatim distribution by the Extensions Index, users should be aware of the non-commercial and no-derivatives restrictions, and a standard open-source software license (such as BSD, MIT, or Apache 2.0) is generally recommended for code repositories.
  ```
  Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International Public License
  ```
  Suggestion: Consider whether an open-source software license (or at least noting the non-commercial restriction in `README.md`) is appropriate for your intended users.

### Leftover development .patch files committed to repository root
info; packaging; raised by gemini; **quote not found in source**
- **gemini** (info, medium confidence, quote quote not found) [`CMakeLists.txt:1`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/CMakeLists.txt#L1): Five development `.patch` files (`annular_plane.patch`, `crosshair_overlap.patch`, `height_editing.patch`, `valve_tab.patch`, `views_fix.patch`) totaling ~185 KB are committed to the repository root. While they do not break the build, they appear to be leftover development artifacts.
  ```
  annular_plane.patch  (83184 bytes)
  crosshair_overlap.patch  (11735 bytes)
  height_editing.patch  (25690 bytes)
  valve_tab.patch  (53682 bytes)
  views_fix.patch  (11375 bytes)
  ```
  Suggestion: Remove the `.patch` files from the root of the repository.

### License limits redistribution and commercial use
info; license; raised by gpt
- **gpt** (info, high confidence, quote verified) [`LICENSE.md:70`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/LICENSE.md#L70): The license permits noncommercial sharing of the unadapted material, but users cannot rely on it for commercial use or to distribute adaptations. This is a material restriction for prospective users, not by itself evidence that an unmodified catalog package cannot be distributed.
  ```
              the Licensed Rights in the Licensed Material to:
               A. reproduce and Share the Licensed Material, in whole or in part,
                  for NonCommercial purposes only; and
               B. produce and reproduce, but not Share, Adapted Material for
                  NonCommercial purposes only.
  ```
  Suggestion: Make the restrictions prominent in extension metadata and documentation, and retain required attribution in distributed packages.

### Module category set to Examples, placeholder help URL, and outdated README
info; utility; raised by gemini
- **gemini** (info, high confidence, quote verified) [`TavrWorkbench/TavrWorkbench.py:57`](https://github.com/pcdslab/TavrWorkbench/blob/c915848aa62164d373166e7c2fd9984f5f8c826e/TavrWorkbench/TavrWorkbench.py#L57): In `TavrWorkbench.py`, `self.parent.categories` is set to `"Examples"` (whereas `CMakeLists.txt` and the catalog entry use `"Segmentation"`), and `self.parent.helpText` still contains the template placeholder URL `https://github.com/organization/projectname#TavrWorkbench`. Additionally, `README.md` describes an older UI (e.g., "Directory Mode", "Centerline Slicing", and "The module installs pandas, numpy and SimpleITK automatically") that does not match the current implementation.
  ```
          self.parent.title = _("TavrWorkbench")
          self.parent.categories = [translate("qSlicerAbstractCoreModule", "Examples")]
          self.parent.dependencies = ["Segmentations", "SegmentStatistics", "Markups"]
          self.parent.contributors = ["Mohammed Khubaib (Saeed Lab: Florida International University)"]
          self.parent.helpText = _("""
          A 3D Slicer extension for fast, structured review of TAVR CT segmentations and measurements.
  ```
  Suggestion: Set `self.parent.categories = ["Segmentation"]`, update the documentation link in `helpText` to `https://github.com/pcdslab/TavrWorkbench`, and update `README.md` to reflect the current 4-tab workflow.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
The code looks benign. It has no network calls, no pip installs and no unsafe deserialization. The module cannot load from a packaged build because CMake installs only TavrWorkbench.py and not the TavrWorkbenchLib package it imports. That is blocking. The license is CC BY-NC-ND 4.0, whose non-commercial and no-derivatives terms make permission to redistribute the extension and its builds unclear. The entry tracks the moving branch "main". Smaller issues: leftover template sample-data registration, a global VTK warning suppression, and an out-of-band installer using `irm | iex`. Recommendation: 🔴 Do not merge yet.
Not checked: 
<parameter name="0">measurement_editor.py, segmentation_editor.py, valve_generator.py and the rest of annulus_pipeline.py (only the first 60 lines) were not read in full

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
🔴 Do not merge yet: `TavrWorkbench/CMakeLists.txt` only lists `TavrWorkbench.py` in `MODULE_PYTHON_SCRIPTS` and omits the 12 Python files under `TavrWorkbenchLib/`, causing the packaged extension to fail to load (`ModuleNotFoundError: No module named 'TavrWorkbenchLib'`). Additionally, `TavrWorkbench/TavrWorkbench.py` calls `vtk.vtkObject.GlobalWarningDisplayOff()` at import time, which globally silences VTK warnings for the entire Slicer process. Once `TavrWorkbenchLib/*.py` are added to `TavrWorkbench/CMakeLists.txt` (and ideally the global VTK warning suppression at import time is removed), the extension will be ready to merge.
Not checked: Screenshots/main_panel.png (2 MB binary image not inspected); Runtime execution in 3D Slicer
Questions for the author: Could you add the `TavrWorkbenchLib/*.py` files to `MODULE_PYTHON_SCRIPTS` in `TavrWorkbench/CMakeLists.txt` so that CMake installs the helper package when building the extension?; Could you remove the module-level `vtk.vtkObject.GlobalWarningDisplayOff()` call in `TavrWorkbench/TavrWorkbench.py` so it does not silence VTK warnings globally across Slicer at startup?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The source has concrete data-loss paths: a crafted case ID can escape the output folder, the dataset packager can recursively delete unrelated files, and the macOS installer may delete an existing Slicer installation after a startup failure. The catalog build also omits the Python helper package required to load the module. 🔴 Do not merge yet: fix the data-loss paths and verify the selected catalog revision and packaged build.
Not checked: Could not run Slicer, CMake, tests, or reproduce behavior dynamically; conclusions are based on static inspection.; Could not independently fetch the source repository, resolve the catalog's moving main branch, or verify that the supplied checkout is exactly commit c915848aa62164d373166e7c2fd9984f5f8c826e.; Could not inspect PR checklist, CI results, prior index entry, or extension maintenance history.; Did not independently verify licensing or provenance of the original batch scripts mentioned in annulus_pipeline.py or the externally hosted placeholder sample data.; Did not exhaustively review every line of the measurement and annulus computation or validate clinical measurements.
Questions for the author: Can you add installed-package load coverage and verify that the catalog-selected revision includes the fixes?; Can you clarify clinical validation and intended clinical versus research use, including the provenance of the original measurement scripts?


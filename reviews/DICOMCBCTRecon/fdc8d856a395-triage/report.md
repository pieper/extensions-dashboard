# AI review: DICOMCBCTRecon

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/4burakfe/SlicerDICOMCBCTRecon.git at commit `fdc8d856a39562bd282e1d204896297b070ec05f`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:30:29Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | minor | ok | minor |
| packaging | ok | ok | ok |
| license | ok | ok | ok |
| soundness | minor | ok | minor |
| utility | minor | ok | minor |
| **overall** | minor issues | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: A hidden Slicer DICOM plugin that recognises rotational C-arm X-ray runs (multi-frame XA/XRF) in the DICOM browser and reconstructs them into a 3D volume with FDK and/or SART in PyTorch, with an interactive preview window, optional 3D-DSA subtraction of a matching mask sweep, and optional use of GE's private 3D calibration. It targets researchers and clinicians who want cone-beam CT from C-arm spins without leaving Slicer.
- **flash-lite**: DICOMCBCTRecon is a 3D Slicer scripted module and DICOM plugin that enables cone-beam CT reconstruction (FDK and SART algorithms) of rotational C-arm X-ray acquisitions (XA/XRF multi-frame DICOM) using PyTorch.
- **haiku**: Adds a hidden DICOM plugin and reconstruction window to 3D Slicer that turns rotational C-arm XA/XRF runs (multi-frame DICOM) into cone-beam CT volumes using FDK and SART, with PyTorch from Slicer's PyTorch extension. It is for researchers and clinicians working with C-arm 3D/DynaCT-style data.

## Findings from some reviewers

### Cancelling the reconstruction window returns None from the DICOM plugin load()
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTRecon.py:259`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTRecon.py#L259): When the user presses Cancel, or when ensureDependencies() fails, the DICOM plugin's load() returns None. Slicer's DICOM browser treats a None return as a failed load and typically reports an error to the user, so a deliberate cancellation is presented as a load failure. The dependency-missing path already shows its own message, so the extra browser error is redundant and confusing.
  ```
          image, info = dialog.run()
          if image is None:
              logging.info("Cone-beam reconstruction cancelled by user.")
              return None
  ```
  Suggestion: Return a sentinel the browser accepts, or suppress the browser's error for the deliberate-cancel path.

### Good documentation and synthetic tests, but no clinical-use disclaimer
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`README.md:3`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/README.md#L3): The README documents the workflow, the DICOM tags used for geometry, the GE private calibration, the reconstruction methods with literature references, the vendor-orientation troubleshooting steps and how to run the tests, and the module ships a synthetic phantom plus a self test. What is missing is any statement that the output is not validated for clinical use: the module produces HU-like volumes from vendor data and offers no accuracy claim or disclaimer, which matters for a tier-1 tool that will be used on patient studies.
  ```
  Reconstructs rotational C-arm X-ray runs ("spins", e.g. GE Innova 3D / Siemens DynaCT / Philips XperCT
  exports stored as one multi-frame XA or XRF DICOM object) into a 3D volume, straight from Slicer's
  DICOM browser.
  ```
  Suggestion: Add a short research-use / not-for-clinical-decisions disclaimer and state what validation exists (synthetic phantom only).
- **haiku** (minor, medium confidence, quote verified) [`README.md:8`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/README.md#L8): The module produces Hounsfield-like values from C-arm rotational data, which are only approximate. The README states the DISP caveat and the calibration caveat, but nowhere says that the output is for research and not for diagnosis. Users could take the values as clinically calibrated.
  ```
  Author: Burak Demir, MD, FEBNM
  ```
  Suggestion: Add a short research-use-only statement to the README and the module help text, noting that HU values are approximate and depend on the water value chosen.

### Manual I0 of 0 is silently ignored and replaced by the percentile estimate
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTReconLib/reconstruction.py:85`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTReconLib/reconstruction.py#L85): A user who selects "Fixed value" and enters 0 (or a value that evaluates falsy) silently falls through to the 99.9th-percentile estimate instead of using the entered value, so the log line "I0 = ..." reports a number the user did not choose. The spin box minimum is 1.0 so 0 is not reachable through the UI, which keeps the practical impact small.
  ```
      if mode == I0_MANUAL and manualValue:
          return float(manualValue)
  ```
  Suggestion: Test `manualValue is not None` instead of truthiness.

### Module import inserts its own directory at the front of sys.path
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTRecon.py:42`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTRecon.py#L42): Importing the module mutates the shared interpreter's sys.path for the whole Slicer session, inserting the module directory at position 0. Any file in that directory would then shadow a stdlib or site-packages module of the same name for every other extension. The directory currently holds only DICOMCBCTRecon.py and DICOMCBCTReconLib/, so the practical risk is low, and Slicer already puts scripted-module directories on sys.path, making this largely redundant.
  ```
  _MODULE_DIR = os.path.dirname(os.path.abspath(globals().get("__file__", "") or "."))
  if globals().get("__file__") and _MODULE_DIR not in sys.path:
      sys.path.insert(0, _MODULE_DIR)
  ```
  Suggestion: Drop the sys.path manipulation and rely on Slicer's scripted-module path handling, or append instead of insert at position 0.
- **haiku** (minor, medium confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTRecon.py:43`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTRecon.py#L43): On import the module inserts its own folder at index 0 of sys.path. This is a global side effect in the shared Slicer Python process and affects every later import, including for users who never open the module. The folder contains only this extension's files, so the risk is low, but the insert is not needed when the extension is loaded through Slicer's module paths.
  ```
  if globals().get("__file__") and _MODULE_DIR not in sys.path:
      sys.path.insert(0, _MODULE_DIR)
  ```
  Suggestion: Append rather than prepend, or rely on Slicer's module loader, which already adds the module folder when the module is loaded through the CMake build.

### Module-level loadable caches are never cleared and are keyed by a name string
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTRecon.py:46`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTRecon.py#L46): Both caches are module-level dicts that are written in examineFiles and never cleared, so they grow for the lifetime of the Slicer session and keep geometry dicts (per-frame numpy arrays) alive for every run ever examined. The sweep lookup is keyed by (filePath, loadable.name), and the name is built from series description plus run label, so two files with the same description and instance number would collide and the wrong sweep could be reconstructed. The comment shows the author knows Qt-wrapped loadables lose attributes, which is why the side table exists.
  ```
  # (file, sweep) -> other sweeps of the study that follow the same trajectory, filled in by examine()
  _OTHER_RUNS_FOR_SWEEP = {}
  # (file, loadable name) -> sweep index (Qt-wrapped loadables can lose Python attributes)
  _SWEEP_FOR_LOADABLE = {}
  ```
  Suggestion: Clear both dicts at the start of each examine() pass, or key the sweep on the loadable object identity / a per-examine token instead of a name string.

### Reconstruction runs on the GUI thread and re-enters the Qt event loop
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTReconLib/dialog.py:543`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTReconLib/dialog.py#L543): FDK and SART run on the GUI thread and pump the Qt event loop from the progress and log callbacks. The modal dialog plus the BusyDialogGuard and the `if self.busy: return` guard in onApply limit re-entrancy, but any other queued event (scene changes, other module callbacks, timers) is still dispatched while a multi-minute reconstruction holds the interpreter, and a second Reconstruct click is only prevented by the disabled button. This is a common Slicer pattern but is the weakest point for responsiveness and re-entrancy.
  ```
      self.logText.appendPlainText(message)
      slicer.app.processEvents()
  ```
  Suggestion: Consider running the reconstruction in a worker thread (or at least a slicer.util.ProgressDialog with a queued abort flag) so the event loop is not re-entered from inside the computation.

### Subtraction-run search parses the header of every file in the study during examine
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTRecon.py:180`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTRecon.py#L180): For every candidate sweep, examineFiles calls _matchingRuns, which enumerates every file of every series in the study and, for each one that passes the cheap modality/numberOfFrames check, parses its header with pydicom to look for a matching trajectory. On a study with many series (or many single-frame XA objects) this makes the DICOM browser's examine step read a large number of headers synchronously, which can stall the browser. Results are memoised in the `summaries` dict within one examineFiles call, which limits but does not remove the cost.
  ```
              for seriesUID in db.seriesForStudy(studyUID):
                  files += [f for f in db.filesForSeries(seriesUID) if f != filePath]
  ```
  Suggestion: Restrict the scan to series whose modality is XA/XRF/RF and whose NumberOfFrames is large, using the DICOM database before reading any header.

### Testing/Python unit tests are not registered with CTest
minor; packaging; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`DICOMCBCTRecon/CMakeLists.txt:30`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/CMakeLists.txt#L30): Only the in-module self test (DICOMCBCTReconTest) is registered with CTest. The 300-line unittest suite in Testing/Python/test_cbct_reconstruction.py, which covers FDK accuracy, Parker weights, the GE calibration fit and SART, is never run by the extension build, so regressions in the reconstruction maths would not be caught by CI.
  ```
  if(BUILD_TESTING)
    # Self test inside Slicer (synthetic phantom)
    slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)
  endif()
  ```
  Suggestion: Add a second slicer_add_python_unittest (or a plain add_test) for Testing/Python/test_cbct_reconstruction.py so the numeric tests run in the extension build.

### CMake installs every imported Python file; entry and CMake dependencies agree
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`DICOMCBCTRecon/CMakeLists.txt:5`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/CMakeLists.txt#L5): Every Python file the module imports is listed in MODULE_PYTHON_SCRIPTS and all of them exist in the tree (verified against the file listing), plus the icon in MODULE_PYTHON_RESOURCES. The catalog entry's build_dependencies ["PyTorch"] matches `set(EXTENSION_DEPENDS PyTorch)`, build_subdirectory "." matches the root CMakeLists.txt, and scm_revision "main" is a branch reference the index supports. The only uninstalled Python file is Testing/Python/test_cbct_reconstruction.py, which the module never imports.
  ```
  set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    ${MODULE_NAME}Lib/__init__.py
    ${MODULE_NAME}Lib/xadata.py
    ${MODULE_NAME}Lib/geometry.py
    ${MODULE_NAME}Lib/gecalib.py
  ```
  Suggestion: None needed.

### Catalog category (DICOM) differs from EXTENSION_CATEGORY (Reconstruction)
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`CMakeLists.txt:8`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/CMakeLists.txt#L8): The catalog entry declares `"category": "DICOM"` while the extension's own CMakeLists.txt declares EXTENSION_CATEGORY "Reconstruction". This is descriptive metadata only and does not affect building or loading, but the two sources disagree about where the extension belongs in the module list.
  ```
  set(EXTENSION_CATEGORY "Reconstruction")
  ```
  Suggestion: Make the catalog category and EXTENSION_CATEGORY agree (DICOM seems the better fit given the DICOM-browser workflow).

### No network, subprocess, eval/exec, pickle or torch.load anywhere in the extension
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTRecon.py:30`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTRecon.py#L30): I searched the whole tree for network, process and deserialization primitives (requests, urllib, urlopen, socket, subprocess, os.system, eval, exec, pickle, torch.load, pip_install, download). The only hits are the GitHub URLs in CMakeLists.txt/README.md and the dialog's own `requestStop` method. DICOM input is read with pydicom (`pydicom.dcmread`) and SimpleITK, both of which parse data rather than execute it. No telemetry, no upload of images or identifiers, no credentials, no obfuscated code, and no text addressed to AI reviewers.
  ```
  import logging
  import os
  import sys
  import traceback
  ```
  Suggestion: None needed.

### PyTorch installed only through PyTorchUtils, with user confirmation, never at import
info; environment; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`DICOMCBCTRecon/DICOMCBCTRecon.py:359`](https://github.com/4burakfe/SlicerDICOMCBCTRecon/blob/fdc8d856a39562bd282e1d204896297b070ec05f/DICOMCBCTRecon/DICOMCBCTRecon.py#L359): PyTorch is obtained only through Slicer's PyTorch extension: `import PyTorchUtils` then `PyTorchUtils.PyTorchUtilsLogic().installTorch(askConfirmation=False)` after an explicit user confirmation, and the catalog entry lists PyTorch in build_dependencies while CMakeLists.txt sets `EXTENSION_DEPENDS PyTorch`. There is no pip_install, no torch pin, no index URL, and no numpy/scipy/SimpleITK/pydicom pinning anywhere in the tree. Installation happens only when a user loads a run, never at import or startup.
  ```
      if not slicer.util.confirmOkCancelDisplay(
              "Cone-beam reconstruction needs PyTorch, which is not installed yet.\n\n"
              "Install it now with the PyTorch extension? It selects the CPU or CUDA build for "
              "this computer and can take several minutes."):
          return False
  ```
  Suggestion: None needed.

### catalog scm_revision is a branch name (main), not a fixed commit
info; packaging; raised by haiku; **quote not found in source**
- **haiku** (info, high confidence, quote quote not found) no file cited: The catalog entry pins scm_revision to "main", so the built code can change without a catalog update. The reviewed source is commit fdc8d856a39562bd282e1d204896297b070ec05f per the request, but the index will build whatever main points to. Policy accepts branch references, so this is informational only.
  ```
  "scm_revision": "main"
  ```
  Suggestion: Pin scm_revision to the reviewed commit hash in future updates so that approvals cover the exact code.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): minor issues
DICOMCBCTRecon is a well-structured, MIT-licensed DICOM plugin that reconstructs C-arm rotational XA/XRF runs with FDK/SART in PyTorch. I found no network access, telemetry, subprocess, eval/exec, pickle or torch.load, no package pinning, and PyTorch is installed only through PyTorchUtils after explicit confirmation; the catalog entry matches the CMake dependencies and every imported Python file is installed. Remaining issues are non-blocking: a sys.path insert at import, GUI-thread reconstruction with processEvents, never-cleared module-level caches keyed by loadable name, a full-study header scan during examine, and no clinical-use disclaimer. 🟢 Recommend merge.
Not checked: The exact source revision: the catalog entry pins scm_revision "main" (a branch), so the code I read is the tip of main at review time, not a fixed commit; the commit fdc8d856a39562bd282e1d204896297b070ec05f named in the request could not be resolved with the available tools.; The tail of reconstruction.py (toOutputUnits and the last lines after line 633) and the tail of geometry.py (matrixFromVectors after line 252) were truncated by the reader; I did not verify those function bodies.; The last ~90 lines of Testing/Python/test_cbct_reconstruction.py (after line 227) were truncated.; Whether the extension actually builds and loads in Slicer, and whether the CTest self test passes: no build or Slicer installation was available.; Whether the PyTorch extension is available for every platform the index builds for, and whether the reconstruction runs correctly on real vendor data (no GE/Siemens/Philips sample run was available).; The binary files screenshot.jpg and Resources/Icons/DICOMCBCTRecon.png were not inspected beyond their sizes.

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
DICOMCBCTRecon is a well-structured 3D Slicer extension providing cone-beam CT reconstruction (FDK, SART, 3D DSA subtraction) for rotational X-ray angiography (XA/XRF) runs loaded through the DICOM browser. It adheres to all Slicer conventions, utilizes PyTorch correctly via PyTorchUtils, includes robust error handling and self-tests, and features an MIT license. 🟢 Recommend merge
Not checked: DICOMCBCTReconLib/reconstruction.py (PyTorch tensor operations, cone-beam backprojection/forward projection and filtering math); DICOMCBCTReconLib/geometry.py and gecalib.py (projection geometry matrices and calibration)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
I read the catalog entry, CMake files, main module, dialog, xadata, display, README and LICENSE, and searched all files for network, install, pickle, eval and subprocess calls. I found none. Torch is obtained only through the PyTorch extension, after user confirmation. The MIT license is present. CMake installs all eight Lib Python files. The points that remain are a sys.path insert at import, scm_revision pinned to a branch, and the absence of a research-use disclaimer. None block admission. Coverage is partial: gecalib.py, geometry.py, phantom.py, most of reconstruction.py and the test file were not read.
Not checked: gecalib.py, geometry.py, phantom.py and roughly two thirds of reconstruction.py were not read in full. Only the imports, torchDevice, fovMask and the FDK return path were inspected.; The test file DICOMCBCTRecon/Testing/Python/test_cbct_reconstruction.py was not read.; The live scm_url and scm_revision were not resolved. I did not confirm that commit fdc8d856 exists or matches the file contents shown.; No CI or build reports were available, so loading in Slicer, the CMake build and the in-Slicer self test were not verified.; The screenshot and icon binaries were not inspected.; Behaviour of PyTorchUtils.installTorch and the Slicer DICOM plugin API was not checked against upstream Slicer sources.


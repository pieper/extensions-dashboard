# AI review: NeuroStrip

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/dyollb/SlicerNeuroStrip at commit `1576f50b2883dede76ac284782caf166b6b3760c`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T17:36:23Z; cost $0.02

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | ok |
| environment | concern | ok | minor |
| packaging | blocking | ok | blocking |
| license | minor | ok | ok |
| soundness | concern | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: NeuroStrip is a 3D Slicer scripted module that runs CNN-based skull stripping (brain masking) on MRI volumes using the external `neurostrip` Python library, producing a brain mask labelmap and optionally a masked brain volume.
- **flash-lite**: NeuroStrip is a 3D Slicer scripted loadable module that provides CNN-based skull stripping (brain masking) from MRI volumes using the NeuroStrip library.
- **haiku**: NeuroStrip is a Slicer scripted module that runs CNN-based skull stripping (brain masking) on MRI volumes by calling the external neurostrip Python package. It is intended for Slicer users in the Segmentation category who want brain masks and optionally masked brain volumes.

## Disagreements (start here)

### D1. Missing NeuroStrip/CMakeLists.txt: extension cannot be configured or installed
partial; category packaging; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`CMakeLists.txt:22`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/CMakeLists.txt#L22): The top-level CMakeLists.txt adds the NeuroStrip subdirectory, but the repository has no NeuroStrip/CMakeLists.txt (directory listing shows only NeuroStrip.py, Resources/Icons/NeuroStrip.png, Resources/Icons/NeuroStrip1.png, Resources/UI/NeuroStrip.ui). CMake configuration of the catalog entry therefore fails, and even if it did not, nothing would install NeuroStrip.py, the .ui file or the icons, so the module would not load from the Extension Manager build.
  ```
  add_subdirectory(NeuroStrip)
  ```
  Suggestion: Add NeuroStrip/CMakeLists.txt using slicerMacroBuildScriptedModule(NAME NeuroStrip) with the standard Resources install rules (UI, Icons) and verify the extension builds from the catalog entry.
- **haiku** (blocking, high confidence, quote verified) [`CMakeLists.txt:22`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/CMakeLists.txt#L22): The catalog entry uses build_subdirectory '.', so the build runs the root CMakeLists.txt. Line 22 calls add_subdirectory(NeuroStrip), and CMake fails if that folder has no CMakeLists.txt. The NeuroStrip/ folder lists only NeuroStrip.py and Resources/, and reading NeuroStrip/CMakeLists.txt returned 'No such file'. The extension therefore cannot be configured, built, or packaged, and the module is not installed. Other Slicer extensions normally put a CMakeLists.txt in the module folder that calls slicer_add_python_scripted_module-style install rules (or the equivalent for this extension) to install NeuroStrip.py and Resources.
  ```
  add_subdirectory(NeuroStrip)
  ```
  Suggestion: Add NeuroStrip/CMakeLists.txt that installs NeuroStrip.py and the Resources/ folder (UI, Icons) into the extension's lib/Slicer-X/qt-scripted-modules directories, following the standard ScriptedLoadableModule template, then confirm the extension builds in the Slicer extension CI.

### D2. Direction matrix copy is wrong: list passed to GetIJKToRASDirections and identity hardcoded
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`NeuroStrip/NeuroStrip.py:339`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/NeuroStrip/NeuroStrip.py#L339): vtkMRMLVolumeNode.GetIJKToRASDirections expects a vtkMatrix4x4 (or a wrapped C array), not a Python list, so this call is likely to raise a TypeError after the (expensive) prediction has already run, making Apply fail with 'Failed to compute results.' Even if it did not raise, the direction is overwritten with identity rather than the input volume's orientation, so results for oblique or non-axially-aligned MRI would be misoriented in the scene. The same pattern is repeated at lines 357-359 for the masked volume.
  ```
  outputMask.SetAndObserveImageData(tempMaskNode.GetImageData())
                      outputMask.SetOrigin(tempMaskNode.GetOrigin())
                      outputMask.SetSpacing(tempMaskNode.GetSpacing())
                      directionMatrix = np.eye(3, 3).tolist()
                      tempMaskNode.GetIJKToRASDirections(directionMatrix)
  ```
  Suggestion: Use `outputMask.SetIJKToRASMatrix(tempMaskNode.GetIJKToRASMatrix())` (or copy the input volume's IJKToRAS matrix) instead of building an identity list, and add a test with a non-identity direction.

### D3. Unpinned pip install of neurostrip[cpu] into Slicer's shared Python environment
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`NeuroStrip/NeuroStrip.py:31`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/NeuroStrip/NeuroStrip.py#L31): The module installs a third-party package with no version constraint into the Slicer Python environment shared by all extensions. The transitive dependency set of `neurostrip[cpu]` (onnxruntime, and possibly torch or pinned numpy) could not be inspected from this repository, so it cannot be confirmed that it does not pull PyTorch from PyPI, does not pin/downgrade numpy or other Slicer-bundled packages, or does not bundle its own Qt/VTK. Any such dependency would affect users who never open this module, and an unpinned install means the code that runs changes silently over time.
  ```
  def installPythonDependencies() -> None:
      msg = "Extra python packages (neurostrip and onnxruntime) are required."
      msg += "\nClick OK to install them for NeuroStrip."
      if not slicer.util.confirmOkCancelDisplay(msg):
          logging.info('Installation of neurostrip aborted by user')
          return
  ```
  Suggestion: Pin a reviewed version range, verify the dependency tree of neurostrip[cpu] (no torch, no pins of Slicer-bundled packages, headless-only Qt/VTK), and document the reviewed dependency set; consider shipping the model via a Slicer data/extension mechanism instead of a pip package.
- **haiku** (minor, medium confidence, quote verified) [`NeuroStrip/NeuroStrip.py:37`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/NeuroStrip/NeuroStrip.py#L37): On first enter of the module, the code installs neurostrip[cpu] into Slicer's shared Python environment, which can bring in onnxruntime and other packages that may conflict with Slicer-bundled ones. The install is gated by a confirm dialog, which is good. However, if the user cancels, _dependenciesInstalled stays False, so the prompt reappears on every module enter. The dependency tree was not verified.
  ```
  slicer.util.pip_install("neurostrip[cpu]")
  ```
  Suggestion: Remember the user's decline for the session, state the approximate download size in the prompt, and check that the neurostrip dependency set does not pin or replace packages Slicer bundles.

### D4. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor

### D5. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku blocking

### D6. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### Brittle test assertion on exact intensity maximum
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`NeuroStrip/NeuroStrip.py:411`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/NeuroStrip/NeuroStrip.py#L411): The test asserts an exact maximum intensity of 605, which depends on the model version and preprocessing; any model update or minor numerical difference will fail the test even when the module works. It also requires the pip dependency to be installed, so the test cannot run in a clean build environment.
  ```
  outputScalarRange = outputMaskedVolume.GetImageData().GetScalarRange()
          self.assertEqual(outputScalarRange[0], 0)
          self.assertEqual(outputScalarRange[1], 605)  # Maximum value in mask
  ```
  Suggestion: Assert structural properties (non-empty mask, mask values in {0,1}, masked volume zero outside the mask) instead of exact intensity values.

### CNN inference runs synchronously on the GUI thread without progress reporting
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`NeuroStrip/NeuroStrip.py:263`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/NeuroStrip/NeuroStrip.py#L263): The whole prediction (potentially minutes on CPU) runs inside the button handler with only a wait cursor; Slicer's UI is frozen and the user gets no progress or cancel option, which looks like a hang for large volumes. Errors are at least surfaced via tryWithErrorDisplay, so this is a usability/robustness issue rather than a safety one.
  ```
  with slicer.util.tryWithErrorDisplay(
              _("Failed to compute results."), waitCursor=True
          ):
              # Compute output
              self.logic.process(
  ```
  Suggestion: Run the prediction in a background thread/CLI node with progress reporting, or at minimum show a modal progress dialog and process events.

### Inference runs synchronously on the GUI thread with no progress feedback
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`NeuroStrip/NeuroStrip.py:323`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/NeuroStrip/NeuroStrip.py#L323): process() calls neurostrip.predict in the main thread, so the Slicer UI freezes for the whole CNN run on a full MRI volume. The README acknowledges that processing takes time. A user may think Slicer has hung, and the window may be marked unresponsive.
  ```
  neurostrip.predict(
                        image_path=input_path,
  ```
  Suggestion: Show a progress dialog or run inference in a worker thread, with an explicit device choice (the CPU is hardcoded at line 327).

### Install prompt repeats on every module entry if the user declines
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`NeuroStrip/NeuroStrip.py:182`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/NeuroStrip/NeuroStrip.py#L182): If the user cancels the installation dialog, `_dependenciesInstalled` stays False and the confirmation dialog reappears every time the module is entered; conversely, after a successful install the flag is not re-checked, so a failed install is only detected on the next Apply. Minor UX issue.
  ```
  # Make sure dependencies are installed
          if not self._dependenciesInstalled:
              self._dependenciesInstalled = checkPythonDependencies()
              if not self._dependenciesInstalled:
                  installPythonDependencies()
  ```
  Suggestion: Remember the user's decline for the session and re-check availability before running the algorithm.

### No clinical-use disclaimer or model provenance/validation information
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.md:1`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/README.md#L1): The README describes features and usage but gives no information about the training data, model version, reported accuracy, or a research-use-only disclaimer, which users of an AI-based segmentation tool need in order to judge whether results are trustworthy.
  ```
  # NeuroStrip 3D Slicer Extension
  
  This extension provides CNN-based skull stripping (brain masking) from MRI using the [NeuroStrip library](https://github.com/dyollb/neurostrip) directly within 3D Slicer.
  ```
  Suggestion: Document model provenance, validation results and add a research-use-only disclaimer.

### No clinical-use disclaimer or model validation information
info; utility; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`NeuroStrip/NeuroStrip.py:56`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/NeuroStrip/NeuroStrip.py#L56): The module produces brain masks used for medical image analysis, but the help text and README contain no statement that the output is unvalidated for clinical use and no information on the model's training or validation. The README points to external docs only.
  ```
  It can generate brain masks and apply them to create masked brain images.
  ```
  Suggestion: Add a research-use disclaimer and a short note on model provenance and validation to the help text and README.

### Screenshot URL points to the sample-data thumbnail rather than a screenshot
info; packaging; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`CMakeLists.txt:12`](https://github.com/dyollb/SlicerNeuroStrip/blob/1576f50b2883dede76ac284782caf166b6b3760c/CMakeLists.txt#L12): NeuroStrip1.png is registered as the Sample Data thumbnail (NeuroStrip.py:90) and is not the Screenshot01.png committed at the repository root, so the catalog screenshot will show the thumbnail image. Cosmetic only.
  ```
  set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/dyollb/SlicerNeuroStrip/main/NeuroStrip/Resources/Icons/NeuroStrip1.png")
  ```
  Suggestion: Point EXTENSION_SCREENSHOTURLS at Screenshot01.png.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The module code itself is small and does not transmit data: it exports the input volume to a temporary directory, calls `neurostrip.predict` locally, and loads results back. However the extension cannot be built as submitted: `CMakeLists.txt:22` does `add_subdirectory(NeuroStrip)` but no `NeuroStrip/CMakeLists.txt` exists in the repository, so CMake configuration fails and no Python/UI/icon files are installed. There are also environment concerns (unpinned `pip_install("neurostrip[cpu]")` into Slicer's shared Python, contents of that package unverifiable) and a likely runtime bug in the direction-matrix copy. License (MIT) is fine for the extension itself; the bundled/downloaded library and model weights could not be verified.
Not checked: The `neurostrip` PyPI package (https://github.com/dyollb/neurostrip) and its pyproject.toml could not be fetched: its dependency tree (whether it pulls torch, pins numpy/onnxruntime, or bundles Qt/VTK), its license, and the provenance/license of the model weights it downloads are unverified.; No network access, so the catalog entry's scm_revision 'main' could not be resolved to the stated commit 1576f50b2883dede76ac284782caf166b6b3760c, and the sample-data URL/checksum at NeuroStrip.py:92-96 could not be verified.; The extension was not built or run; the missing NeuroStrip/CMakeLists.txt finding is based on the repository file listing, not on an actual CMake configure attempt.; Binary files (Screenshot01.png, NeuroStrip.png, NeuroStrip1.png) were not inspected for embedded content.
Questions for the author: Where is NeuroStrip/CMakeLists.txt? The top-level CMakeLists.txt adds that subdirectory but the file is not in the repository.; What are the exact dependencies of `neurostrip[cpu]` (does it install torch, and does it pin numpy/onnxruntime)? Which version is intended to be reviewed?; What license and training-data provenance apply to the model weights downloaded by the neurostrip package?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
NeuroStrip is a well-structured 3D Slicer extension providing CNN-based skull stripping using the NeuroStrip library. All files, packaging configuration, licensing, and code implementation adhere to Slicer community standards and guidelines. 🟢 Recommend merge
Not checked: Exact runtime execution of the pip package install and model inference in 3D Slicer environment.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The root CMakeLists.txt calls add_subdirectory(NeuroStrip), but the NeuroStrip/ folder has no CMakeLists.txt (confirmed by list_files and a direct read, which returned "No such file"). CMake configure will therefore fail, so the extension cannot build from the catalog entry. The Python module itself is reasonable: it asks before pip-installing neurostrip[cpu], uses temporary directories, and downloads sample data with a SHA256 check. The packaging defect must be fixed before admission.
Not checked: The neurostrip PyPI package and its transitive dependencies (for example whether torch or other large or conflicting packages are pulled in) were not inspected.; The upstream source at commit 1576f50 was not fetched; the catalog entry uses scm_revision 'main', so I could not confirm the revision.; The NeuroStrip.ui file (5303 bytes) was not read, so widget and parameter wiring was not verified.; The sample data file on GitHub SlicerTestingData and its license were not checked.; The MIT license of the neurostrip library referenced in the README was not verified.; No CI build results were available, so the build and load were not verified.


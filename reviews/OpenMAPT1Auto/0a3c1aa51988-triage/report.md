# AI review: OpenMAPT1Auto

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/niyaziacer/SlicerOpenMAPT1Auto.git at commit `0a3c1aa519880a4c8f3d6110810b88829f9c615b`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T10:03:47Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | unknown |
| environment | blocking | ok | unknown |
| packaging | concern | ok | unknown |
| license | minor | ok | unknown |
| soundness | concern | ok | unknown |
| utility | minor | ok | unknown |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer scripted module that runs the OpenMAP-T1 deep-learning pipeline on a T1-weighted brain MRI to parcellate 280 anatomical regions, then loads the labelmap/segmentation into Slicer and exports per-region volumes to CSV/Excel. It targets neuroimaging researchers; the model weights (~1.5 GB) are downloaded separately from Google Drive under a non-commercial JHU license.
- **flash-lite**: OpenMAPT1Auto is a 3D Slicer extension that automates brain MRI parcellation into 280 anatomical regions using the OpenMAP-T1 deep learning model.
- **haiku**: A 3D Slicer scripted module that runs the OpenMAP-T1 deep-learning pipeline to parcellate a T1 brain MRI into 280 regions, producing a labelmap, volume tables, and a 3D segmentation. It is aimed at neuroimaging researchers who accept a non-commercial license.

## Disagreements (start here)

### D1. PyTorch and other packages pip-installed at module import (Slicer startup) without consent
partial; category environment; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:11`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L11): `install_requirements()` is executed unconditionally at import time (line 28). Slicer imports every scripted module at startup to register it, so on first launch after installing the extension, every user gets `slicer.util.pip_install` runs for torch, torchvision, numpy, pandas, nibabel, gdown, openpyxl and tqdm — even users who never open the module. This installs PyTorch outside the Slicer PyTorch extension (no PyTorchUtils in EXTENSION_DEPENDS/build_dependencies), and `pip_install("numpy")` can upgrade/downgrade the numpy that Slicer bundles, breaking Slicer and other extensions. It also blocks Slicer startup for minutes on a slow network.
  ```
      required = [
          "torch",
          "torchvision", 
          "numpy",
  ```
  Suggestion: Remove the import-time install entirely. Declare PyTorchUtils in EXTENSION_DEPENDS/build_dependencies and use `PyTorchUtils.PyTorchUtilsLogic().installTorch()`, and install the remaining pure-Python packages only after an explicit user action with a confirmation dialog (or list them in the extension metadata).
- **haiku** (major, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:11`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L11): install_requirements() runs at module import time, before any user action. It pip-installs torch and torchvision (and numpy, pandas, nibabel, gdown, openpyxl, tqdm) into Slicer's shared Python environment whenever a package is missing. This affects every Slicer user at startup, not just those who open the module, and PyTorch is not installed through the PyTorch extension (PyTorchUtils), which the index policy requires. Package installation at import without confirmation is also listed as a request-for-changes item.
  ```
  required = [
          "torch",
          "torchvision", 
          "numpy",
  ```
  Suggestion: Remove install_requirements() from import time. Declare PyTorch via the PyTorchUtils build dependency and use its PyTorchUtils.installTorch helper behind an explicit user prompt. Do not pip-install torch directly, and do not pin or upgrade numpy/scipy/SimpleITK/pandas, which Slicer bundles.

### D2. Conflicting license terms: MIT stated, but non-commercial restriction applies to the extension itself
single; category license; raised by haiku
- **haiku** (major, high confidence, quote verified) [`CMakeLists.txt:9`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/CMakeLists.txt#L9): LICENSE.txt and README say the extension code is MIT, which allows commercial use. The CMake description and the in-app dialog say the extension is 'NON-COMMERCIAL USE ONLY', and the UI says 'Commercial use requires separate license'. Users and the index cannot tell which terms govern the distributed extension. Distribution under the Slicer catalog needs an unambiguous statement of terms.
  ```
  set(EXTENSION_DESCRIPTION "Automated brain MRI parcellation into 280 anatomical regions using OpenMAP-T1 deep learning model. NON-COMMERCIAL USE ONLY.")
  ```
  Suggestion: State one consistent license position: separate MIT terms for the wrapper code and non-commercial JHU terms for the model weights downloaded at runtime, with the same wording in CMake, the UI, and README. Confirm the author has the right to offer MIT terms for code that depends on the non-commercial model.

### D3. Generic top-level package name `utils` inserted at sys.path[0]
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:43`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L43): The inserted directory contains a top-level package literally named `utils`. Because it is placed at position 0 of the shared Slicer Python `sys.path`, any other module or extension that does `import utils` (a very common name) will silently get this package instead of its own, causing hard-to-diagnose failures in unrelated code. This is a process-wide side effect that persists for the whole Slicer session.
  ```
  lib_path = os.path.join(module_dir, "OpenMAPT1AutoParcellationLib")
  if lib_path not in sys.path:
      sys.path.insert(0, lib_path)
  ```
  Suggestion: Rename the package to something unique (e.g. `OpenMAPT1AutoLib`) and import it as `from OpenMAPT1AutoLib.utils...`, or load the modules via importlib from an explicit path without modifying sys.path.
- **haiku** (minor, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:44`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L44): The module inserts its lib folder at sys.path[0] and imports the generic top-level name 'utils'. This can shadow or be shadowed by other Python packages named 'utils'. os.chdir to the module folder changes the process-wide working directory for the whole Slicer session.
  ```
  if lib_path not in sys.path:
      sys.path.insert(0, lib_path)
  ```
  Suggestion: Rename the package to a unique name (e.g. openmap_t1_utils) and import it under that name. Do not chdir; pass absolute paths.

### D4. Installed layout does not match the code's sys.path assumption for OpenMAPT1AutoParcellationLib
severity dispute; category packaging; raised by deepseek, flash-lite
- **deepseek** (major, medium confidence, quote verified) [`OpenMAPT1AutoParcellation/CMakeLists.txt:20`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/CMakeLists.txt#L20): The module file is installed to the qt-scripted-modules directory, but the library goes to the qt-scripted-modules *lib* directory. The code then inserts `os.path.join(os.path.dirname(__file__), "OpenMAPT1AutoParcellationLib")` into sys.path (OpenMAPT1AutoParcellation.py:43) — a path that does not exist in an installed extension — and imports `from utils.cropping import ...`. In the installed tree the package is `.../qt-scripted-modules/OpenMAPT1AutoParcellationLib/utils`, so `import utils` cannot resolve; `utils_import_error` is set and `runPipeline` raises `RuntimeError("utils import failed: ...")` (line 296). The module UI loads but the pipeline cannot run from a catalog build.
  ```
  install(
    DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/OpenMAPT1AutoParcellationLib
    DESTINATION ${Slicer_INSTALL_QTSCRIPTEDMODULES_LIB_DIR}
  )
  ```
  Suggestion: Install the library so that the imported package name matches (e.g. install `OpenMAPT1AutoParcellationLib/utils` as `utils` into the lib dir that Slicer already puts on PYTHONPATH), or import via a unique package name resolved from the lib directory, and verify with an installed (not build-tree) test.
- **flash-lite** (info, high confidence, quote verified) [`OpenMAPT1AutoParcellation/CMakeLists.txt:20`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/CMakeLists.txt#L20): CMakeLists.txt correctly installs the module script and the supporting OpenMAPT1AutoParcellationLib directory into Slicer's target directories so that the module loads and functions correctly when built and packaged.
  ```
  install(
    DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/OpenMAPT1AutoParcellationLib
    DESTINATION ${Slicer_INSTALL_QTSCRIPTEDMODULES_LIB_DIR}
  )
  ```
  Suggestion: None

### D5. Long pipeline runs on the GUI thread with no progress or cancel
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:172`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L172): `onRunClicked` -> `runPipeline` -> `_runPipelineSteps` executes N4 correction, seven model loads and hundreds of 2D forward passes directly in the button slot. The README itself states 15-45 minutes on CPU. The only event processing is inside `logMessage`, so the UI is frozen between log lines, the progress bar is never used for the run, and there is no way to cancel; users will likely force-quit Slicer mid-run. Errors are only written to the log widget, not shown as a message box.
  ```
      def logMessage(self, text):
          self.log.append(text)
          slicer.app.processEvents()
  ```
  Suggestion: Run the pipeline in a `slicer.util.ProgressDialog`/`qSlicerCLIProgressBar`-style worker (e.g. `qt.QTimer`-driven or `slicer.util.runInBackground`-style thread) with progress reporting and a cancel flag, and report failures with `slicer.util.errorDisplay`.
- **haiku** (minor, medium confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:179`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L179): MODEL_FOLDER is created under self.moduleDir (the installed extension folder). The author's own UI text notes that the extension folder is replaced on update, so ~1.5 GB of models can be lost on each extension update, and the user must re-download them.
  ```
  model_folder = os.path.join(self.moduleDir, "MODEL_FOLDER")
          if os.path.exists(model_folder) and os.listdir(model_folder):
  ```
  Suggestion: Store downloaded models in a user-writable location, such as the Slicer application data folder, outside the extension install folder.

### D6. Unverified 1.5 GB archive from a personal Google Drive extracted with extractall into the extension directory
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:216`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L216): The model payload is fetched from a single Google Drive file ID owned by the author (line 72), with no checksum, signature or version pin, and then `z.extractall(self.moduleDir)` (line 224) writes every archive member into the extension's install directory without validating member paths (zip-slip) or contents. A replaced or compromised Drive file would silently overwrite files inside the extension directory, and the extracted `.pth` files are then loaded by `torch.load` (mitigated by `weights_only=True`, but the archive can contain arbitrary other files). Users cannot verify that the weights are the upstream OpenMAP-T1 release.
  ```
              temp_zip = os.path.join(self.moduleDir, "models_temp.zip")
              url = "https://drive.google.com/uc?id=" + self.GDRIVE_FILE_ID
  ```
  Suggestion: Download from the official OpenMAP-T1 release location, verify a published SHA-256 of the archive before extraction, extract into a dedicated user-writable model directory (not the extension install dir), and validate each member path stays inside that directory.
- **haiku** (minor, medium confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:223`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L223): The model archive downloaded from a Google Drive ID is extracted with extractall into the module folder without checking member paths. A malicious or tampered archive could write outside the intended folder (zip-slip). The download is not checksum-verified, so a changed Drive file would be trusted.
  ```
  with zipfile.ZipFile(temp_zip, 'r') as z:
                    z.extractall(self.moduleDir)
  ```
  Suggestion: Validate each member path resolves inside the target folder before extraction, and verify a published SHA-256 of the archive before extracting.

### D7. labeled.txt installed to the lib directory but read from the module directory
single; category packaging; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`OpenMAPT1AutoParcellation/CMakeLists.txt:20`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/CMakeLists.txt#L20): `loadLabels()` reads `os.path.join(self.moduleDir, "labeled.txt")` (OpenMAPT1AutoParcellation.py:257), where moduleDir is the directory of the module .py (qt-scripted-modules). CMake installs labeled.txt into the separate lib directory, so in an installed extension the file is not found: the log shows "labeled.txt not found", the CSV `LabelName` column is empty and no segments are renamed. The `OPTIONAL` keyword also hides a missing file at build time.
  ```
  install(
    FILES ${CMAKE_CURRENT_SOURCE_DIR}/labeled.txt
    DESTINATION ${Slicer_INSTALL_QTSCRIPTEDMODULES_LIB_DIR}
    OPTIONAL
  ```
  Suggestion: Install labeled.txt next to the module file (or into the same lib directory the code actually searches) and drop `OPTIONAL` so a missing file fails the build.

### D8. os.chdir changes the working directory of the whole Slicer process
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:298`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L298): The working directory is changed to the extension directory and never restored. Every other module and library in the same Slicer process that resolves relative paths (including Slicer's own file dialogs' last-directory behaviour and other extensions) is affected for the rest of the session. It is also the reason the bundled `make_csv.py` can use relative paths like `"level/Level5.txt"`.
  ```
          os.chdir(self.moduleDir)
  ```
  Suggestion: Remove the `os.chdir`; pass absolute paths to the pipeline functions (they already accept `work_folder`/`output_dir`).

### D9. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku unknown

### D10. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku unknown

### D11. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku unknown

### D12. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku unknown


## Findings from some reviewers

### Internal metadata references branch `master` while the index selects `main`
minor; packaging; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`OpenMAPT1Auto.json:26`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1Auto.json#L26): The catalog entry pins `scm_revision: "main"`, but the extension's own metadata, README links and CMake icon/screenshot URLs all use `master`. If the default branch is `main`, the raw.githubusercontent `master` URLs for the icon and screenshots 404, and the metadata is misleading. The root `OpenMAPT1Auto.json` is also not a file the Slicer extension build consumes.
  ```
    "repository": {
      "type": "git",
      "url": "https://github.com/niyaziacer/SlicerOpenMAPT1Auto",
      "branch": "master"
  ```
  Suggestion: Align all branch references with the branch actually used by the index, and remove or relocate the non-standard root JSON if it is not used by the build.

### Long CPU-bound pipeline runs on the GUI thread
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified, other lines) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:312`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L312): runPipeline() runs all inference synchronously in the Qt GUI thread. The README says CPU runs take 15-45 minutes. The UI freezes apart from processEvents calls in logMessage, and there is no cancel button.
  ```
  work_folder = tempfile.mkdtemp(prefix="OpenMAPT1_")
          try:
              self._runPipelineSteps(volumeNode, output_folder, work_folder)
  ```
  Suggestion: Run inference in a worker thread or as a separate process, and show progress with a cancel option.

### Model folder deleted recursively without confirmation
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified, other lines) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:179`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L179): Pressing "Re-download Models" deletes the whole MODEL_FOLDER recursively. The README instructs users to place manually downloaded models there (README.md:44), so a user who manually populated that folder loses it without any confirmation prompt. The path is fixed inside the extension directory, so the blast radius is limited, but the deletion is still unannounced.
  ```
          model_folder = os.path.join(self.moduleDir, "MODEL_FOLDER")
          if os.path.exists(model_folder):
              shutil.rmtree(model_folder)
  ```
  Suggestion: Ask for confirmation before deleting, and move models to a user-chosen data directory instead of the extension install directory (which is replaced on extension update).
- **haiku** (minor, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:204`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L204): downloadModels() calls shutil.rmtree on MODEL_FOLDER before downloading. If the download fails (common, given the 1.5 GB size), the user loses working models and must download them again.
  ```
  if os.path.exists(model_folder):
              shutil.rmtree(model_folder)
  ```
  Suggestion: Download and extract to a temporary folder, then swap it in only on success.

### No tests, no sample data, no research-use disclaimer, weak model provenance
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`OpenMAPT1AutoParcellation/CMakeLists.txt:12`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/CMakeLists.txt#L12): Only the generic load test is built; there is no test of the pipeline, no sample T1 volume, and no tutorial beyond the README steps. For a deep-learning tool producing anatomical measurements there is no statement of validation/accuracy, no model version or checksum, and no explicit research-use-only / not-for-clinical-diagnosis disclaimer (only the non-commercial note).
  ```
  slicerMacroBuildScriptedModule(
    NAME ${MODULE_NAME}
    SCRIPTS ${MODULE_PYTHON_SCRIPTS}
    RESOURCES ${MODULE_PYTHON_RESOURCES}
    WITH_GENERIC_TESTS
  )
  ```
  Suggestion: Add a small sample dataset and a smoke test, document the model version/checksum and any published validation, and add an explicit research-use-only disclaimer in the module UI and README.

### Redistribution of JHU-licensed weights via a personal Google Drive is undocumented; license links inconsistent
minor; license; raised by deepseek, flash-lite
- **deepseek** (minor, medium confidence, quote verified) [`LICENSE.txt:39`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/LICENSE.txt#L39): The extension code is MIT (fine), and the non-commercial model terms are disclosed in the UI, README and metadata. However the weights are re-hosted on the author's own Google Drive (OpenMAPT1AutoParcellation.py:72) rather than linked from the upstream release, and nothing states that the JHU license permits this redistribution. The license link in the module dialog points to `OishiLab/OpenMAP-T1` (line 195) while LICENSE.txt and the metadata point to `TaikiNishimaki/OpenMAP-T1`, so users cannot be sure which terms apply.
  ```
  **Original Repository:** https://github.com/TaikiNishimaki/OpenMAP-T1
  
  **License:** JHU Research Software License Agreement
  ```
  Suggestion: State explicitly whether the JHU license permits re-hosting the weights, or download from the upstream official location; make the license URL consistent across LICENSE.txt, README, metadata and the dialog.
- **flash-lite** (info, high confidence, quote partly verified) [`LICENSE.txt:33`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/LICENSE.txt#L33): The extension clearly separates its own MIT license for the Slicer integration code from the non-commercial JHU Research Software License governing the underlying OpenMAP-T1 deep learning models and weights. Users are duly informed that model weights are not bundled and must be downloaded separately under the JHU non-commercial license.
  ```
  ## 2. OpenMAP-T1 Model and Core Algorithm (JHU License)
    **License:** JHU Research Software License Agreement
  ```
  Suggestion: None

### Version specifier passed to importlib.import_module, so gdown is reinstalled every startup
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:22`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L22): `required` contains `"gdown>=4.6.0"` (line 17). `importlib.import_module("gdown>=4.6.0")` can never succeed because that is not a module name, so the ImportError branch runs `pip_install("gdown>=4.6.0")` on every Slicer start, adding network traffic and startup delay even when gdown is already installed. `torchvision` and `tqdm` are installed but never imported anywhere in the extension.
  ```
      for package in required:
          try:
              importlib.import_module(package)
          except ImportError:
              slicer.util.pip_install(package)
  ```
  Suggestion: Separate module names from requirement specifiers (dict of name -> spec), and drop unused packages.

### `pip_install("gdown --upgrade")` passes a flag inside a single requirement string
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:207`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L207): `slicer.util.pip_install` forwards its arguments to pip; `"gdown --upgrade"` is a single argument and is not a valid requirement specifier, so pip will error out (caught by the broad except and only logged). Even if it worked, it would silently upgrade a package in Slicer's environment during a download action.
  ```
              slicer.util.pip_install("gdown --upgrade")
              import importlib
              import gdown
              importlib.reload(gdown)
  ```
  Suggestion: Use `slicer.util.pip_install("gdown")` (or `pip_install("--upgrade", "gdown")` if an upgrade is really needed) and only after user confirmation.
- **haiku** (minor, medium confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py:207`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellation.py#L207): Clicking Download runs pip install --upgrade gdown in Slicer's shared Python environment, changing a package that other extensions may use, with no separate consent beyond the license dialog.
  ```
  slicer.util.pip_install("gdown --upgrade")
              import importlib
              import gdown
  ```
  Suggestion: Install gdown only if missing and in a pinned range, or fetch the model via Slicer's own download utilities or a plain HTTP request with a checksum.

### pickle.load of a committed binary blob (split_map.pkl)
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellationLib/utils/postprocessing.py:7`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellationLib/utils/postprocessing.py#L7): The lookup table is deserialized with `pickle`, which can execute arbitrary code. The file is committed in the repository (7 KB binary) and cannot be audited by reading it, so any future replacement of that file — or a tampered build — becomes code execution inside Slicer. The data is a simple key→value mapping that needs no pickle.
  ```
      split_map_path = os.path.join(os.path.dirname(__file__), "split_map.pkl")
      with open(split_map_path, "rb") as tf:
          dictionary = pickle.load(tf)
  ```
  Suggestion: Store the mapping as JSON or .npz and load it with `json.load`/`numpy.load`, or at minimum document and hash-pin the pickle.
- **haiku** (minor, medium confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellationLib/utils/postprocessing.py:9`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellationLib/utils/postprocessing.py#L9): The postprocessing step unpickles split_map.pkl. The file is bundled and not user-supplied, so the risk is limited, but pickle execution is unsafe if the file is ever replaced or tampered with.
  ```
  dictionary = pickle.load(tf)
  ```
  Suggestion: Convert the mapping to JSON or NPZ, or keep pickle but document it as trusted only.

### Catalog has no build dependency on PyTorch; EXTENSION_DEPENDS is NA
info; packaging; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`CMakeLists.txt:12`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/CMakeLists.txt#L12): The catalog entry has no build_dependencies and CMake sets EXTENSION_DEPENDS to NA, although the module needs torch and torchvision. The index cannot ensure the PyTorch extension is present.
  ```
  set(EXTENSION_DEPENDS "NA")
  ```
  Suggestion: Set EXTENSION_DEPENDS to PyTorchUtils and add it to build_dependencies in the catalog entry.

### PyTorch model loading uses weights_only=True
info; soundness; raised by flash-lite
- **flash-lite** (info, high confidence, quote verified) [`OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellationLib/utils/load_model.py:29`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/OpenMAPT1AutoParcellation/OpenMAPT1AutoParcellationLib/utils/load_model.py#L29): The extension loads PyTorch state dicts with weights_only=True and uses safetensors/pickle appropriately for its local assets, but torch.load of model weights downloaded from external sources (Google Drive) relies on the security guarantees of PyTorch weights_only=True. Furthermore, the pickle module is used to load split_map.pkl from the local extension directory. While local assets are controlled, ensure weights_only=True is consistently adhered to for any future weights loading.
  ```
      cnet.load_state_dict(torch.load(os.path.join(opt.m, "CNet/CNet.pth"), weights_only=True))
  ```
  Suggestion: Keep weights_only=True when loading model checkpoints.

### Unreferenced large images committed
info; utility; raised by haiku
- **haiku** (info, low confidence, quote no quote) [`images/img1.png:1`](https://github.com/niyaziacer/SlicerOpenMAPT1Auto/blob/0a3c1aa519880a4c8f3d6110810b88829f9c615b/images/img1.png#L1): images/img1.png (about 814 KB) is in the repository and not referenced by CMake or README. Screenshots are referenced via URL, so they are not blocking, but they add repository weight.
  Suggestion: Remove unused images or move them to an external hosting location.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The wrapper code is small and contains no telemetry, no data upload, and no obfuscation; the model download is user-initiated behind a license dialog. However, the module installs PyTorch (and numpy/pandas/etc.) with `slicer.util.pip_install` at import time, i.e. at Slicer startup for every user, which is a blocking environment violation. Additional major issues: the installed layout does not match the code's `sys.path`/`labeled.txt` assumptions (pipeline likely cannot run from the catalog build), `os.chdir` on the whole Slicer process, a long GUI-thread pipeline with no progress/cancel, and an unverified binary payload extracted with `extractall` from a personal Google Drive. License for the code is MIT and the non-commercial model terms are disclosed. 🔴 Do not merge yet.
Not checked: Binary content of Screenshots/Screenshot2.png and images/img2.png (not readable in this environment); Binary content of OpenMAPT1AutoParcellationLib/utils/split_map.pkl — the pickle payload cannot be audited by reading, so its safety is unverified; Contents of the Google Drive model archive (file ID 1YEE65X5Cx8LHK-C070TbZARHp1C08KxA) — not downloadable here; whether it contains only the expected .pth weights is unknown; The actual JHU Research Software License text and whether it permits re-hosting the weights on a personal Google Drive; Whether the repository's default branch is `main` or `master`, and whether the raw.githubusercontent `master` URLs for icon/screenshots resolve; CI/build results for this revision and whether the extension actually builds and loads on the Slicer build farm; Runtime behaviour in a real Slicer session (the packaging findings about the installed layout are inferred from CMake install destinations and the code's path assumptions, not executed)
Questions for the author: Why is PyTorch installed with `slicer.util.pip_install` at module import instead of through the Slicer PyTorch extension (PyTorchUtils in EXTENSION_DEPENDS)?; Can you confirm that the JHU Research Software License permits you to re-host the OpenMAP-T1 weights on your personal Google Drive, and can you publish a checksum for the archive?; Have you tested the extension as installed from a build (not from the source tree)? The code looks for `OpenMAPT1AutoParcellationLib` and `labeled.txt` next to the module file, but CMake installs both into the qt-scripted-modules lib directory.; Is the default branch `main` or `master`? The index entry uses `main` while your metadata and raw URLs use `master`.; Can the pipeline be moved off the GUI thread with progress and cancel, given the documented 15-45 minute CPU runtime?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
OpenMAPT1Auto is a well-structured 3D Slicer extension that integrates the OpenMAP-T1 deep learning pipeline for automated brain parcellation into 280 anatomical regions. The code correctly follows Slicer conventions, uses proper CMake installation rules, securely loads PyTorch weights with weights_only=True, and clearly documents its MIT/JHU dual licensing terms and non-commercial model constraints. 🟢 Recommend merge.
Not checked: Runtime execution of the deep learning pipeline on real MRI data (requires GPU/CPU hardware and downloaded 1.5GB model weights).

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The module is a plausible research tool, and I found no malicious or concealed behavior. Model weights are loaded with weights_only=True and no data leaves the machine except the Google Drive model download. However, the module pip-installs torch, torchvision and other packages at import time (Slicer startup), which violates the PyTorch-extension rule. It also has a license conflict: the extension is labelled MIT, but its own UI and CMake description say non-commercial only. Smaller issues include zip extraction without path checks, a global chdir, and models stored inside the extension install folder. Overall: needs fixes.
Not checked: The Google Drive model archive (ID 1YEE65X5Cx8LHK-C070TbZARHp1C08KxA): its contents, hashes, and license terms were not inspected.; The upstream OpenMAP-T1 repository and its JHU license text were not fetched.; The entry's scm_revision is 'main', a moving branch; I did not resolve a commit.; The catalog JSON for the index entry (build_dependencies) was not in the provided files.; No runtime testing, build, or Slicer load was performed; I could not run the extension.; Binary screenshots and icons were not visually inspected.; The extension's test coverage beyond WITH_GENERIC_TESTS was not inspected because no test files exist in the listing.
Questions for the author: Will you remove the import-time pip installation and depend on PyTorchUtils instead?; Which license governs the extension code: MIT (LICENSE.txt) or non-commercial only (CMakeLists.txt, UI)? Please make them consistent.; Can the model archive be published with a SHA-256 hash that the module verifies?; Can the models be stored outside the extension install folder so updates do not delete them?


# AI review: PySERA

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/radiuma-com/SlicerPySERA at commit `cff96861e0541080592bc2be99cba02d8d72f837`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T10:09:39Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | concern |
| environment | concern | ok | concern |
| packaging | concern | minor | minor |
| license | minor | ok | concern |
| soundness | concern | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: SlicerPySERA is a 3D Slicer scripted module that wraps the external PySERA radiomics library, letting researchers configure handcrafted or deep radiomics parameters in a GUI and run single-case or folder-batch feature extraction, writing timestamped CSVs. It targets radiomics researchers who want a Slicer-native front end instead of scripting PySERA directly.
- **flash-lite**: PySERA is a 3D Slicer extension that integrates the PySERA radiomics feature extraction library (supporting both handcrafted radiomics and deep features) into Slicer with a graphical user interface and CLI module.
- **haiku**: PySERA is a Slicer scripted module (plus an unbuilt CLI wrapper) that drives the PySERA radiomics library from a Qt UI, running single-case or batch handcrafted/deep feature extraction and writing CSV output. It is aimed at radiomics researchers who want a GUI workflow inside 3D Slicer.

## Disagreements (start here)

### D1. Deep-feature mode implies PyTorch-class dependencies installed via pip, not via the PyTorch extension
single; category environment; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`README.md:231`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/README.md#L231): The UI offers resnet50/vgg16/densenet121 (PySera.py:1289) and the README tells users to preinstall 'deep learning dependencies used by PySERA'. If pysera declares torch/torchvision as requirements, `pip_install('pysera')` will pull PyTorch from PyPI into Slicer's environment, which the review policy forbids (PyTorch must come through the PyTorch extension / PyTorchUtils). I could not read pysera's metadata, so this is unverified but plausible and needs an author answer before admission.
  ```
  deep learning dependencies used by PySERA (if you enable deep features)
  ```
  Suggestion: Confirm pysera's declared dependencies. If it requires torch, install it through PyTorchUtils, add PyTorch to build_dependencies/EXTENSION_DEPENDS, and gate deep mode behind that.

### D2. Feature extraction runs on the GUI thread with no progress reporting
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`PySERA/PySera.py:1437`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/PySera.py#L1437): onCompute calls the whole PySERA pipeline synchronously after a single processEvents(); for batch folders or deep features this freezes Slicer for minutes to hours with no progress bar and no cancel. README:568 confirms 'Slicer may temporarily appear unresponsive'. Additionally _wait_for_readable_file (PySera.py:464-476) sleeps up to 40 s inside a QTimer callback, blocking the event loop again.
  ```
  output_csv, result = self.logic.run_single_case(image_path, mask_path, params)
  ```
  Suggestion: Run the extraction in a CLI node or a worker thread with slicer.util.progress / a progress dialog, and poll the CSV asynchronously without time.sleep on the GUI thread.
- **haiku** (minor, high confidence, quote verified, other lines) [`PySERA/PySera.py:111`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/PySera.py#L111): onCompute calls the PySERA process_batch directly on the Qt main thread. The output-CSV poller also uses time.sleep. Slicer becomes unresponsive for large batch jobs, and the user gets no cancel option. The README acknowledges the freeze but does not fix it.
  ```
  try:
                  t0 = time.time()
                  if is_single:
                      output_csv, result = self.logic.run_single_case(image_path, mask_path, params)
  ```
  Suggestion: Run the extraction in a worker thread or subprocess with progress reporting and a cancel button.

### D3. Non-commercial phantom data committed in an MIT-licensed extension repo without notice
partial; category license; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`Data/ct_radiomics_phantom/README.md:12`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/Data/ct_radiomics_phantom/README.md#L12): The repository ships 61 DICOM files and a NIfTI phantom under CC BY-NC 3.0. Redistribution is permitted with attribution, but the non-commercial restriction applies to users, and the top-level README (which lists Data/ct_radiomics_phantom in the repository structure) never mentions it. Users in commercial settings could unknowingly use NC-licensed data.
  ```
  The phantom is licensed under the Creative Commons Attribution-NonCommercial 3.0 Unported Licence.
  ```
  Suggestion: State the CC BY-NC 3.0 terms and attribution for the phantom in the top-level README, or move the data to a separately downloaded resource.
- **haiku** (major, high confidence, quote verified) [`Data/ct_radiomics_phantom/README.md:11`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/Data/ct_radiomics_phantom/README.md#L11): The repository ships the IBSI CT phantom (DICOM and NIfTI) under CC BY-NC 3.0, which prohibits commercial use. The extension's README and LICENSE declare only MIT, and the README does not mention the NC restriction. Users who fetch the source may redistribute or use the data in ways the NC license forbids.
  ```
  ## License
  The phantom is licensed under the Creative Commons Attribution-NonCommercial 3.0 Unported Licence.
  ```
  Suggestion: State the data license in the top-level README, or remove the phantom from the repo and link to its source (CancerData) instead. Confirm that the data is not required by the module.

### D4. Unpinned pip install of 'pysera' into Slicer's shared Python without user confirmation
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`PySERA/PySera.py:209`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/PySera.py#L209): On the first Run, _ensure_package_available installs the PyPI package 'pysera' into Slicer's Python environment with no confirmation dialog, no version pin and no hash. This affects the shared interpreter used by all modules and persists after the extension is uninstalled; a future or compromised PyPI release is installed automatically. The same pattern is in PySeraCLIModule.py:32. The README (line 223) documents the auto-install but the user is never asked at runtime.
  ```
  slicer.util.pip_install(package_name)
  ```
  Suggestion: Ask the user for explicit confirmation before installing, pin a known-good version (or install from a reviewed wheel/URL), and document the exact package and version in the README.
- **haiku** (major, high confidence, quote verified) [`PySERA/PySera.py:208`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/PySera.py#L208): On first use, the module installs 'pysera' from PyPI with no version pin and no user prompt. Pysera's transitive dependencies (and any deep-learning stack for deep mode) are then installed into the shared Slicer environment, which affects other extensions. The README claims network access only happens for pip, but the install is not gated behind an explicit opt-in.
  ```
  logger.info(f"Installing '{package_name}' via slicer.util.pip_install ...")
              slicer.util.pip_install(package_name)
  ```
  Suggestion: Pin a tested pysera version, confirm with the user before installing (for example with slicer.util.confirmOkCancelDisplay), and document which transitive packages are installed. Deep mode should go through the PyTorch extension rather than pip.

### D5. parameters.yaml / parameters.json are not installed, so an installed extension loses all configuration
single; category packaging; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`PySERA/CMakeLists.txt:10`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/CMakeLists.txt#L10): PySera.py:123-124 resolves YAML_PATH/JSON_PATH next to the module file and load_parameters() (PySera.py:145-174) is executed at import. MODULE_PYTHON_RESOURCES installs only the icon, so in a catalog-installed extension neither parameter file exists: CFG_FILE, RDEF and CLI_MAP all become {} and _build_cli_kwargs (PySera.py:265-293) returns essentially only extraction_mode/categories/dimensions. Every advanced setting the user picks in the GUI (BinSize, DataType, interpolation, resegmentation, IVH, num_workers, ...) is silently dropped and PySERA runs with its own defaults, producing results that do not match the displayed parameters.
  ```
  Resources/Icons/SlicerPySERA_png_icon.png
  ```
  Suggestion: Add parameters.yaml and parameters.json to MODULE_PYTHON_RESOURCES in PySERA/CMakeLists.txt (and to the CLI module's resources), and show a visible error instead of silently falling back to empty defaults.

### D6. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D7. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D8. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D9. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### CLI wrapper passes 'report' twice and forwards non-parameter YAML keys as kwargs
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`PySERA/PySeraCLI/PySeraCLIModule.py:130`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/PySeraCLI/PySeraCLIModule.py#L130): _load_default_params() returns the whole parameters.yaml, which contains a 'report' entry (PySERA/parameters.yaml:202-206) plus the top-level 'radiomics' and 'radiomics_meta' blocks. main() therefore builds params containing 'report' and passes it together with report=True, and also passes radiomics/radiomics_meta as unexpected keywords, so pysera.process_batch raises TypeError. Currently masked because the CLI module is not built.
  ```
  report=True,
  ```
  Suggestion: Only forward keys from the radiomics_meta block, and drop 'report' from params (or stop passing report=True explicitly).

### Committed compiled bytecode and IDE files that cannot be verified
minor; safety; raised by deepseek
- **deepseek** (minor, high confidence, quote no quote) [`PySERA/__pycache__/PySera.cpython-312.pyc:1`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/__pycache__/PySera.cpython-312.pyc#L1): An 83 KB .pyc plus .idea/ project files are committed. The bytecode is a binary blob whose content cannot be compared with PySera.py by inspection, and it is not installed by CMake, so it serves no purpose in the repository. It is not evidence of malice, but it is unverifiable content in a distributed source tree.
  Suggestion: Remove __pycache__/ and .idea/ from the repository and add them to .gitignore.

### Default output location falls back to ~/Desktop/output_result or the process working directory
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`PySERA/PySera.py:312`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/PySera.py#L312): If no output folder is set, _make_output_csv creates ~/Desktop/output_result; the UI default is the relative path './output_result' (PySera.py:888), which resolves against Slicer's working directory. Files are then written to locations the user did not choose, which is contrary to the Slicer convention of writing to a user-selected or temporary folder.
  ```
  os.path.expanduser("~"), "Desktop", "output_result"
  ```
  Suggestion: Default to a user-selected folder or slicer.app.temporaryPath, and refuse to run when the output folder is empty.

### Large binary assets committed to the source repository
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote no quote) [`PySERA/Resources/Screenshots/0_screenshot_title_with_categories.png:1`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/Resources/Screenshots/0_screenshot_title_with_categories.png#L1): Eight screenshots of ~1.3-1.6 MB each (~11 MB total), a 3 MB NIfTI phantom and 61 DICOM files are committed. Only one icon is installed by CMake, so the rest is repository weight that slows clones and extension builds without being needed at runtime.
  Suggestion: Downscale the screenshots and host the phantom as a downloadable sample-data resource instead of committing it.

### Missing extension dependencies declaration
minor; packaging; raised by flash-lite
- **flash-lite** (minor, high confidence, quote verified) [`CMakeLists.txt:12`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/CMakeLists.txt#L12): The PySERA extension installs 'pysera' (and potentially other deep learning packages or requirements) via pip at runtime, but declares NO extension dependencies (EXTENSION_DEPENDS "NA"). In particular, if deep features or models (such as ResNet/VGG/DenseNet) are used, PyTorch or other required packages might be pulled in without ensuring PyTorchUtils is declared as a build/extension dependency or handling PyTorch installation properly per Slicer guidelines.
  ```
  set(EXTENSION_DEPENDS "NA")  # Specified as a list or "NA" if no dependencies
  ```
  Suggestion: Declare appropriate extension dependencies (such as PyTorchUtils if deep learning features require PyTorch) and ensure dependencies are correctly configured.

### No parameter node and no Slicer scene integration
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`PySERA/PySera.py:867`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/PySera.py#L867): Inputs are file paths on disk rather than MRML volume/segmentation node selectors, and no parameter node is used, so the module state is not saved with the scene and users must export images and masks to NIfTI before running. This is a usability deviation from Slicer conventions rather than a defect.
  ```
  self.imagePathEdit = ctk.ctkPathLineEdit()
  ```
  Suggestion: Offer node selectors (with an option to save to a temporary NIfTI) and store settings in a parameter node.

### Parameter-file load errors are silently swallowed
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`PySERA/PySera.py:139`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/PySera.py#L139): If parameters.yaml is malformed or PyYAML is missing, the loader returns an empty dict with no logged reason. The module then silently runs with defaults or fails later with a confusing message.
  ```
          with open(path, "r", encoding="utf-8") as f:
              return yaml.safe_load(f) or {}
      except Exception:
          return {}
  ```
  Suggestion: Log the exception (logger.error) with the path before falling back.

### PySeraCLI module is never built or installed
minor; packaging; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`PySERA/CMakeLists.txt:14`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/CMakeLists.txt#L14): PySERA/CMakeLists.txt only builds the PySera scripted module; there is no add_subdirectory(PySeraCLI), so PySeraCLI/CMakeLists.txt, PySeraCLI.xml and PySeraCLIModule.py are dead code that never reaches users, while the README (lines 394-397) documents the CLI wrapper configuration files as part of the extension.
  ```
  slicerMacroBuildScriptedModule(
  ```
  Suggestion: Either add add_subdirectory(PySeraCLI) and verify the CLI module works, or remove the CLI directory and its README references.
- **haiku** (minor, high confidence, quote verified) [`PySERA/CMakeLists.txt:1`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/CMakeLists.txt#L1): The root CMakeLists adds only the PySERA subdirectory, and PySERA/CMakeLists.txt does not call add_subdirectory(PySeraCLI). The CLI module, its XML, and its parameter files are therefore not part of the packaged extension, despite being described in the README's repository layout.
  ```
  #-----------------------------------------------------------------------------
  set(MODULE_NAME PySera)
  ```
  Suggestion: Either add the CLI subdirectory to the build or remove the PySeraCLI directory from the repo to avoid confusion.

### MIT copyright holder line looks like a course identifier
info; license; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`LICENSE:3`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/LICENSE#L3): The MIT text permits distribution, but the copyright holder 'CPSC210-2025S' appears to be a course code rather than the authors or their institution, which weakens the provenance of the license grant. This is not a distribution blocker but should be clarified.
  ```
  Copyright (c) 2025  CPSC210-2025S
  ```
  Suggestion: Replace the holder with the actual authors or institution.

### README privacy claim depends on pip-installed code that was not reviewed
info; safety; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`README.md:577`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/README.md#L577): The data-privacy section says no data is uploaded and network access happens only for pip. The pysera library, which processes the images, was not inspected, so this claim is unverified.
  ```
  - **No data is uploaded** by the extension itself.
  - Any network access typically occurs only if Slicer installs Python packages via pip.
  ```
  Suggestion: Verify the pysera package has no telemetry, and state the pinned version tested.

### Test is only an instantiation check; no sample-data regression test
info; utility; raised by haiku
- **haiku** (info, high confidence, quote verified) [`PySERA/PySera.py:1482`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/PySera.py#L1482): PySeraTest.runTest only asserts that PySERALogic() can be constructed. It does not exercise extraction on the bundled phantom, so regressions in the pysera integration would not be caught.
  ```
      def runTest(self):
          self.delayDisplay("Running PySera tests...")
          try:
              logic = PySERALogic()
  ```
  Suggestion: Add a test that runs a small extraction on the phantom and checks the output CSV.

### Test only instantiates the logic class
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified, other lines) [`PySERA/PySera.py:519`](https://github.com/radiuma-com/SlicerPySERA/blob/cff96861e0541080592bc2be99cba02d8d72f837/PySERA/PySera.py#L519): PySeraTest.runTest only constructs PySERALogic and asserts it is not None; no extraction is exercised, so the generic tests built by WITH_GENERIC_TESTS cannot catch the missing parameter files or a broken pysera install.
  ```
  logic = PySERALogic()
  ```
  Suggestion: Add a test that runs extraction on the bundled phantom (or a synthetic volume) and asserts a non-empty CSV.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Reviewed the catalog entry, CMake files, PySera.py, the CLI wrapper, parameter files, README and licenses at commit cff9686. No malicious behavior, telemetry, data upload, eval/exec or unsafe deserialization found; the extension only writes CSVs to a user-chosen folder. Main problems are environmental and packaging: `pysera` is pip-installed into Slicer's shared Python without any user confirmation and without a version pin (deep mode implies torch-class dependencies), and `parameters.yaml`/`parameters.json` are not listed in MODULE_PYTHON_RESOURCES, so an installed extension silently loses its whole parameter/CLI mapping. Also: PySeraCLI is never built, heavy work runs on the GUI thread, and a CC BY-NC phantom is bundled without a non-commercial note in the README. 🔴 Do not merge yet: fix the unconfirmed pip install and the missing parameter resources first.
Not checked: The external PyPI package 'pysera' (its metadata, declared dependencies, whether it pulls torch, and its license) could not be inspected; no network access was available.; The upstream PySERA library repository (github.com/radiuma-com/PySERA) and its license terms were not inspected.; The committed binary PySERA/__pycache__/PySera.cpython-312.pyc could not be decompiled or compared with PySera.py.; The 61 DICOM files and the 3 MB NIfTI phantom under Data/ct_radiomics_phantom were not opened; only their license/README were read.; PySERA/PySeraCLI/pysera_cli_lib/parameters.yaml and parameters.json were not read (same byte sizes as the PySERA copies, so the duplicate-'report' finding assumes identical content).; No build or runtime test was performed; the claim that parameters.yaml is not installed follows from reading PySERA/CMakeLists.txt, not from an actual install.; The catalog entry's scm_revision 'main' was not resolved to a specific commit; the review covers the snapshot provided (cff96861e0541080592bc2be99cba02d8d72f837).
Questions for the author: What are the declared dependencies of the PyPI package 'pysera'? Does it require torch/torchvision, and if so, why is PyTorch not installed through the PyTorch extension (PyTorchUtils)?; Is the PyPI package 'pysera' published by the same team as github.com/radiuma-com/PySERA, and which version should the extension pin?; Why are parameters.yaml and parameters.json missing from MODULE_PYTHON_RESOURCES in PySERA/CMakeLists.txt, given that PySera.py loads them at import?; Is PySeraCLI intended to be shipped? It is not added via add_subdirectory in PySERA/CMakeLists.txt.; Can the CC BY-NC 3.0 phantom in Data/ct_radiomics_phantom be documented in the top-level README, or moved to a separately downloaded sample dataset?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
PySERA is a well-structured 3D Slicer extension integrating the PySERA radiomics and deep feature extraction library. Its code follows Slicer conventions, defers package installation to runtime user actions, and provides a clear graphical user interface and CLI. Minor packaging consideration noted regarding extension dependencies.
Not checked: Complete execution of runtime feature extraction with live pysera package installation.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The module code I read is a plain UI wrapper with no network calls, no telemetry and no obfuscation. The main concerns are: it pip-installs an unpinned 'pysera' at run time into Slicer's shared Python without a confirmation step and without declaring the dependency footprint (deep mode may pull heavy packages); the repository commits a non-commercial (CC BY-NC) phantom dataset alongside an MIT-licensed extension; and the PySeraCLI wrapper is not built by CMake. I could not inspect the pysera package itself or the phantom NIfTI binary.
Not checked: The pysera PyPI package (its code, dependencies, network behaviour and license) was not accessible.; The bundled binary Data/ct_radiomics_phantom/nifti/phantom.nii.gz was not read (listed only as a large file).; The scm_revision 'main' was not resolved to a commit; no build or Slicer load was run.; parameters.json and parameters.yaml contents were not read beyond the loader code.; Screenshots and icons (binary) were not inspected.


# AI review: RadioembolizationDosimetry

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/4burakfe/SlicerRadioembolizationDosimetry at commit `848591b55545bd62aa27c2001be71c59a76944e3`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T02:31:22Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | minor |
| environment | concern | ok | concern |
| packaging | minor | ok | minor |
| license | minor | ok | ok |
| soundness | minor | ok | minor |
| utility | ok | ok | ok |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: Taranis is a radioembolization (Y-90 TARE/SIRT) dosimetry suite for nuclear-medicine physicians: a hub module drives a 7-step case workflow (data roles, registration, segmentation, CBCT territory planning, lung shunt fraction, patient-relative/absolute voxel dosimetry, report) with supporting modules (easy_reg, LSFcalc, CBCTPlanning, two dosimetry modules) and optional AI segmentation models.
- **flash-lite**: RadioembolizationDosimetry (Taranis) is a comprehensive 3D Slicer extension and suite of integrated modules for voxel-based dosimetry in Y-90 radioembolization of liver tumors, supporting patient-relative and absolute calibration methods, AI segmentation, registration, and CBCT planning workflows.
- **haiku**: Taranis is a suite of Slicer scripted modules for voxel-based Y-90 radioembolization dosimetry, lung shunt fraction, CBCT territory planning, and AI-assisted liver/lung segmentation. It is aimed at researchers and clinical physicists working with SPECT/PET/CT in Slicer.

## Disagreements (start here)

### D1. Global monkey-patch of Slicer's SegmentEditorEffects class at startup
single; category environment; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`Taranis/TaranisLib/segtools.py:85`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/Taranis/TaranisLib/segtools.py#L85): TaranisLib/__init__.py:29-33 calls guardAutoCompleteEffect() from startupCompleted (Taranis.py:136), so the class method of Slicer's AbstractScriptedSegmentEditorAutoCompleteEffect is replaced for every Slicer user, including those who never open Taranis. Any change in Slicer's effect implementation or in other extensions that also patch this method can silently break Fill between slices / Grow from seeds, and the patch is never removed on shutdown.
  ```
      def onSegmentationModified(self, caller, event):
          if getattr(self, "selectedSegmentIds", None) is None:
              return   # not initialised yet: nothing to update
          return original(self, caller, event)
  
      onSegmentationModified._taranisGuard = True
  ```
  Suggestion: Do not patch Slicer classes at startup. Report the upstream bug instead, or apply the guard only while a Taranis widget is active and restore the original method on cleanup.

### D2. scikit-image installed into Slicer's Python with full dependency resolution
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`CBCTPlanning/CBCTPlanning.py:816`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/CBCTPlanning/CBCTPlanning.py#L816): Unlike the MONAI/einops installs, this call has no --no-deps, so pip resolves scikit-image's requirements (numpy, scipy, networkx, imageio, tifffile, pillow, lazy_loader) and may upgrade or downgrade numpy/scipy that Slicer bundles, breaking Slicer or other extensions for the user. The user consents to installing scikit-image, not to changing numpy/scipy.
  ```
      if not slicer.util.confirmOkCancelDisplay(
              "The centerlines need the Python package scikit-image (3D thinning), which is not installed.\n\n"
              "Install it now (download from the Python package index)?", windowTitle="CBCT planning"):
          return False
      slicer.app.setOverrideCursor(qt.Qt.WaitCursor)
      try:
  ```
  Suggestion: Install with --no-deps after checking that the dependencies are already present, or ship the thinning step without scikit-image; at minimum warn explicitly that bundled numpy/scipy may be changed.
- **haiku** (major, medium confidence, quote verified) [`CBCTPlanning/CBCTPlanning.py:822`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/CBCTPlanning/CBCTPlanning.py#L822): The user is asked to confirm, but the install is a plain pip_install with no --no-deps, so scikit-image's declared requirements (numpy/scipy/etc.) can be upgraded or changed in Slicer's shared environment and affect other extensions. The MONAI path already avoids this with --no-deps. Requirements are not pinned, so a downgrade of a bundled package is possible through transitive dependencies.
  ```
  slicer.util.pip_install("scikit-image")
  ```
  Suggestion: Install with --no-deps after checking that numpy/scipy/imageio/etc. are already present, or pin a compatible version range and document the change in the confirmation dialog.

### D3. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Large binary images committed to the repository
minor; packaging; raised by haiku; **quote not found in source**
- **haiku** (minor, high confidence, quote quote not found) [`RadioembolizationDosimetryAbsolute/Resources/banner.png:1`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/RadioembolizationDosimetryAbsolute/Resources/banner.png#L1): banner.png (about 1.7 MB) is duplicated in four module Resources folders, and several multi-megabyte screenshots and JPEGs are in the repository root. These bloat the clone and are not needed at runtime beyond the icon and banner.
  ```
  RadioembolizationDosimetryAbsolute/Resources/banner.png  (1736880 bytes, binary)
  ```
  Suggestion: Keep one shared copy of the banner and move the large screenshots to a release asset or external URL, which EXTENSION_SCREENSHOTURLS already references.

### Licence of the downloaded AI model weights is not stated
minor; license; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`Taranis/TaranisLib/ai.py:27`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/Taranis/TaranisLib/ai.py#L27): The extension is MIT, but the SwinUNETR weights it downloads come from a different repository (SlicerAether) and no licence or terms for those weights are given in the code or (as far as I read) the README. Users and redistributors cannot tell whether the weights may be used clinically or commercially.
  ```
  # Release that holds the model files (upload the .pth and .txt files as release assets with these names)
  MODEL_RELEASE_URL = "https://github.com/4burakfe/SlicerAether/releases/download/Trained_Models/"
  ```
  Suggestion: State the licence/provenance of the model weights (training data, terms) in the README and next to the download.

### Same torch.load pattern in the LSF calculator
minor; safety; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`LSFcalc/LSFcalc.py:1710`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/LSFcalc/LSFcalc.py#L1710): LSFcalc loads the same weights the same way, so the same risk applies to the LSF module's model folders.
  ```
  model.load_state_dict(torch.load(modelPath, map_location=device))
  ```
  Suggestion: Use weights_only=True and share the verified loader between the two modules.

### Taranis test suite is not registered with CTest
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Taranis/CMakeLists.txt:50`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/Taranis/CMakeLists.txt#L50): Taranis/Testing/Python contains 9 test files (e.g. test_rules.py) but Taranis/CMakeLists.txt never does add_subdirectory(Testing), so those tests are neither built nor run by the extension's CI, unlike the other modules which have a Testing/CMakeLists.txt.
  ```
  if(BUILD_TESTING)
    # Register the unittest subclass in the main script as a ctest.
    # Note that the test will also be available at runtime.
    slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)
  endif()
  ```
  Suggestion: Add add_subdirectory(Testing) under BUILD_TESTING and register the test files, or remove the unused directory.

### Tests for submodules are not registered with CTest
minor; utility; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`LSFcalc/Testing/Python/CMakeLists.txt:2`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/LSFcalc/Testing/Python/CMakeLists.txt#L2): The per-module Testing/Python CMakeLists for LSFcalc, easy_reg, and the dosimetry modules only contain commented-out slicer_add_python_unittest calls. Only the hub has unit tests wired into the build, so regressions in those modules would not be caught by CI.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Register the existing module tests, or remove the empty test directories.

### Unbounded module-level DICOM header cache
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote partly verified) [`Taranis/TaranisLib/case.py:224`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/Taranis/TaranisLib/case.py#L224): The cache is keyed by node ID and instance UIDs and is never cleared, so loading many series in a long session keeps growing it (and keeps stale entries for deleted nodes). Small leak, but it also means a volume whose DICOM header changed is never re-read.
  ```
  _dicomCache = {}
  ...
      key = (volumeNode.GetID(), volumeNode.GetAttribute("DICOM.instanceUIDs") or "")
      if key in _dicomCache:
          return _dicomCache[key]
  ```
  Suggestion: Clear the cache on scene close or cap its size.

### sys.path.append with a generic path at import time in three modules
minor; environment; raised by haiku
- **haiku** (minor, low confidence, quote verified) [`CBCTPlanning/CBCTPlanning.py:31`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/CBCTPlanning/CBCTPlanning.py#L31): When TaranisLib cannot be imported, these modules append a Taranis folder to sys.path. This is a global side effect at import in Slicer's process and may pick up an unrelated TaranisLib package. It is only reached in the fallback branch.
  ```
  sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Taranis"))
  ```
  Suggestion: Rely on the extension's CMake install, which already installs TaranisLib next to each module, or remove the fallback for release builds.

### torch.load of downloaded model weights without weights_only
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`Taranis/TaranisLib/ai.py:436`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/Taranis/TaranisLib/ai.py#L436): The .pth files come from a GitHub release and are unpickled by torch.load. In ai.py the download is SHA256-pinned (ai.py:172-174), which mitigates tampering, but the same pattern appears in LSFcalc/LSFcalc.py:1710 whose download path I could not verify, and on PyTorch < 2.6 the default is weights_only=False, so a replaced release asset would execute code. A user-supplied models folder (SETTING_MODELS_FOLDER) is also searched, so arbitrary local .pth files are loaded.
  ```
          model = buildModel(descriptor, device)
          model.load_state_dict(torch.load(modelPath, map_location=device))
  ```
  Suggestion: Pass weights_only=True to torch.load (state_dicts load fine) and verify the SHA256 in the LSFcalc download path as well.
- **haiku** (minor, medium confidence, quote verified) [`Taranis/TaranisLib/ai.py:437`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/Taranis/TaranisLib/ai.py#L437): Weights are loaded with torch.load(modelPath) from any file found in user-selected or module folders. The download path verifies SHA256, but files already on disk, or files placed in the custom AI models folder, are trusted without a checksum. On PyTorch versions where weights_only defaults to False, a malicious .pth can execute code on load. Exposure is limited to users who place untrusted files in those folders.
  ```
  model.load_state_dict(torch.load(modelPath, map_location=device))
  ```
  Suggestion: Pass weights_only=True to torch.load (state_dict only), and verify the SHA256 of local files when they match a known model name.

### ~10 MB of screenshots and banners committed to the repository
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`CMakeLists.txt:11`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/CMakeLists.txt#L11): Four screenshots (~1.5 MB each), taranis_logo.png (620 KB) and four copies of banner.png (1.7 MB each) are committed, so every extension build and checkout downloads ~10 MB of images that are only used for documentation and the module panel. The automated scan also reported much larger PNG/JFIF files (7-11 MB) that I could not read.
  ```
  set(EXTENSION_ICONURL "https://raw.githubusercontent.com/4burakfe/SlicerRadioembolizationDosimetry/refs/heads/main/taranis_logo.png")
  set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/4burakfe/SlicerRadioembolizationDosimetry/refs/heads/main/ss_relative.jpg https://raw.githubusercontent.com/4burakfe/SlicerRadioembolizationDosimetry/refs/heads/main/ss_absolut.jpg https://raw.githubusercontent.com/4burakfe/SlicerRadioembolizationDosimetry/refs/heads/main/ss_segment.jpg https://raw.githubusercontent.com/4burakfe/SlicerRadioembolizationDosimetry/refs/heads/main/ss_lsf.jpg"
  ```
  Suggestion: Downscale the screenshots and banners (a few hundred KB is enough) or host them outside the build tree.

### Licence of downloaded model weights not stated in what was reviewed
info; license; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`README.md:533`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/README.md#L533): The app downloads model weights from the SlicerAether release, but the licence of those weights is not stated in this repository. The extension's MIT licence covers only the code. TotalSegmentator-based liver-lesion tasks are non-commercial only, and the README and UI state this.
  ```
  Taranis is released under the **MIT License**.
  ```
  Suggestion: State the licence of the downloaded model weights (SlicerAether release) and the TotalSegmentator terms in the README.

### Optional runtime dependencies (PyTorch, TotalSegmentator) not declared in EXTENSION_DEPENDS
info; environment; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`CMakeLists.txt:13`](https://github.com/4burakfe/SlicerRadioembolizationDosimetry/blob/848591b55545bd62aa27c2001be71c59a76944e3/CMakeLists.txt#L13): AI segmentation needs the PyTorch extension (PyTorchUtils) and liver-on-MRI segmentation needs TotalSegmentator; both are optional and handled with clear messages, so this is not a defect, but declaring them would let the Extensions Manager install them.
  ```
  set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies
  ```
  Suggestion: Consider listing PyTorch and TotalSegmentator in EXTENSION_DEPENDS if they are meant to be installed with the extension.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Large, well-documented research suite (MIT, explicit "not a medical device" disclaimer, sample data, unit tests). No data exfiltration, telemetry or credential access found; model downloads are SHA256-pinned and PyTorch is delegated to PyTorchUtils. Two environment problems should be fixed: the extension monkey-patches Slicer's SegmentEditorEffects class at startupCompleted for every user, and CBCTPlanning installs scikit-image with full dependency resolution into Slicer's Python (risk of upgrading bundled numpy/scipy). Packaging is otherwise complete (all Python files installed), though the 9 Taranis test files are not registered in CMake and ~10 MB of screenshots/banners are committed. Model-weight licensing is not stated.
Not checked: LSFcalc/LSFcalc.py download path and whether it verifies SHA256 before torch.load (line 1710); Taranis/TaranisLib/dicomexport.py: whether shutil.rmtree(work) only removes a temporary directory it created; Whether long AI inference / CBCT planning runs off the GUI thread (only processEvents pumping seen in CBCTPlanning._progress); Correctness of the dosimetry math (dosimetry.py, dosekernel.py, vascular.py, cbct.py) - not read; README.md content in detail (66 KB) and the sample-data hosting for RadioembolizationDosimetry1/2; The large binary files reported by the scan (SlicerRadioembolizationDosimetry.png 7 MB, SlicerRadioembolizationDosimetrynoisy.png 11 MB, art.jfif 3 MB, banner.png 8 MB) - not readable and not in the file listing; Actual build/CI results and whether the extension loads in a Slicer build; Licence/terms of the SlicerAether model release assets; easy_reg/EasyRegLib/sitkreg.py and RadioembolizationDosimetryAbsolute/Relative module code beyond the CMakeLists
Questions for the author: Why does Taranis patch Slicer's AbstractScriptedSegmentEditorAutoCompleteEffect at startup instead of reporting the upstream bug or guarding only while its own widget is active?; Can the scikit-image install use --no-deps (or be avoided) so that Slicer's bundled numpy/scipy are never changed?; What licence and training-data provenance apply to the SwinUNETR model weights downloaded from the SlicerAether release?; Does the LSFcalc model download verify the SHA256 checksums before torch.load, as TaranisLib/ai.py does?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
RadioembolizationDosimetry (Taranis) is an exceptionally well-structured and comprehensive 3D Slicer extension for Y-90 radioembolization dosimetry. The codebase adheres strictly to Slicer conventions, uses safe patterns for AI inference and optional package installation with user consent, verifies downloaded model weights using checksums, and includes extensive automated unit tests. All packaging, licensing, safety, and environment criteria are fully satisfied. 🟢 Recommend merge
Not checked: Running full GUI workflows and test execution inside 3D Slicer

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
No malicious or concealed behaviour found in the files read. Model downloads are SHA256-checked and user-confirmed, and MONAI is installed with --no-deps after confirmation. Main concerns: the CBCT module installs scikit-image with its dependencies into Slicer's shared Python without --no-deps, and model weights are loaded with torch.load. Licence is MIT. Coverage is partial: I read about a quarter of the ~20k lines and did not read Taranis.py, dosimetry.py or the other large modules in full.
Not checked: Taranis/Taranis.py, Taranis/TaranisLib/dosimetry.py, cbct.py, vascular.py, controller.py, segtools.py, workflow.py, and most other large modules were not read in full; findings there are unverified.; LSFcalc/LSFcalc.py, RadioembolizationDosimetry* and easy_reg.py were only sampled through search hits.; The scm_revision is 'main' (a moving branch); the reviewed source snapshot is not pinned to a commit.; No CI results or test runs were available; the test suite was not executed.; Licence terms of the SlicerAether model weights and the SampleImages data were not checked.; Large binary files (screenshots, banner) were listed but not inspected.
Questions for the author: Why is scikit-image installed without --no-deps, and have you checked that its dependencies do not change numpy or scipy in Slicer?; Can torch.load be called with weights_only=True for both the Taranis and LSF model loaders?; What is the licence of the SlicerAether model weights, and are they cleared for redistribution through your download?; Can you pin scm_revision to a tagged commit instead of 'main'?


# AI review: MuscleMap

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/MuscleMap/SlicerMuscleMap at commit `b578f909ab47f6033acfedc3ea6a900dde71f596`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T10:21:00Z; cost $0.05

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | concern |
| environment | concern | ok | concern |
| packaging | minor | ok | ok |
| license | ok | ok | ok |
| soundness | minor | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer module (MuscleMap) that runs the external MuscleMap deep-learning models to segment whole-body and regional muscles from CT/MRI volumes, showing results as a segmentation and exporting labelmap/CSV/color table. It targets researchers and clinicians doing quantitative muscle analysis.
- **flash-lite**: MuscleMap is a 3D Slicer extension that provides automated whole-body and regional muscle segmentation models using MONAI and PyTorch.
- **haiku**: A 3D Slicer extension that runs the MuscleMap muscle segmentation tool (whole-body and regional models) on a selected volume, installing MuscleMap and its Python dependencies into Slicer's Python and downloading model weights from Zenodo. It is aimed at researchers working with CT/MRI muscle images.

## Disagreements (start here)

### D1. Generic top-level 'scripts' package is used and installed into Slicer's site-packages
partial; category environment; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:511`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L511): The logic discovers the installed package with importlib.util.find_spec('scripts') and runs it as 'python -m scripts.mm_segment'. 'scripts' is a generic top-level name: any other installed distribution (or leftover directory) providing a 'scripts' package with an mm_util.py would be treated as MuscleMap, its ZENODO_MODELS table read (ast.literal_eval) and its code executed from this module. The check `os.path.isfile(os.path.join(d, 'mm_util.py'))` is weak protection against such a collision.
  ```
      def _musclemap_package_dirs(self):
          """Directories of the installed MuscleMap package ('scripts'), without importing it."""
          spec = importlib.util.find_spec("scripts")
  ```
  Suggestion: Have the upstream package expose a unique top-level name (e.g. 'musclemap') and/or verify the located package with importlib.metadata.distribution('musclemap') before executing it.
- **haiku** (major, medium confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:513`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L513): The module locates and runs a package named 'scripts' (find_spec('scripts') and 'python -m scripts.mm_segment'). 'scripts' is a very generic top-level module name that other packages may also install, so the module may pick up or shadow a different package. The package is installed into Slicer's shared environment, where it is importable by any code in Slicer. This pollutes the shared namespace for users who never open the module.
  ```
  spec = importlib.util.find_spec("scripts")
  ```
  Suggestion: Rely on the upstream package's real importable name, or verify that the found 'scripts' package is MuscleMap (for example by checking mm_util.py content or a version marker) before using it. Document the side effect of installing a top-level 'scripts' package.

### D2. Installer pip-installs MuscleMap from an unpinned git branch into Slicer's shared Python
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:792`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L792): Clicking 'Install MuscleMap dependencies' runs pip against the head of MuscleMap's default branch with --force-reinstall. The code that ends up in Slicer's site-packages is therefore not the code pinned to this review (b578f90...), and it is imported/executed by Slicer's interpreter on every run. A force-push, a compromised upstream repo/account, or a plain upstream commit changes what users execute inside their Slicer process without any new extension review or version bump. It also requires git on the user's machine, otherwise pip fails with a confusing error.
  ```
              slicer.util.pip_install([
                  "--no-deps", "--upgrade", "--force-reinstall",
                  "git+https://github.com/MuscleMap/MuscleMap.git",
              ])
  ```
  Suggestion: Install a pinned source (release tag or commit hash, e.g. 'git+https://github.com/MuscleMap/MuscleMap.git@​v1.0.0') or a PyPI release with a version specifier, and update that pin through the extension release process.
- **haiku** (major, high confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:792`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L792): On the user clicking 'Install MuscleMap dependencies', the module runs pip install from the mutable git default branch of an external repository. Whatever commit is on main at install time executes inside Slicer's Python, with no revision pin or hash check. A compromised or unreviewed upstream commit would therefore reach users without any change in this extension. The extension's own version (__version__ = '1.0.0') does not identify the installed MuscleMap code.
  ```
  slicer.util.pip_install([
      "--no-deps", "--upgrade", "--force-reinstall",
      "git+https://github.com/MuscleMap/MuscleMap.git",
  ])
  ```
  Suggestion: Pin the install to a tagged release or commit SHA (for example git+https://github.com/MuscleMap/MuscleMap.git@<tag-or-sha>), and document the pinned version alongside __version__.

### D3. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D4. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Blocking GUI-thread pip installation
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:373`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L373): onInstallClicked calls ensureDependencies synchronously, which runs multiple slicer.util.pip_install calls (possibly large downloads such as scipy and scikit-learn) on the Qt main thread. The UI can freeze for minutes, and no progress updates are shown beyond the static dialog.
  ```
  self.logic.ensureDependencies()
              self.updateModelComboBoxes()
  ```
  Suggestion: Run pip installs off the GUI thread or with explicit progress, and keep the progress dialog responsive.

### Input volume copy left in temp dir on failure and export silently overwrites sidecar files
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:1088`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L1088): On failure, runSegmentation keeps tempDir (containing the patient input volume) on disk and does not clean it up. Export writes _labels.csv and .ctbl next to the chosen path without a confirmation prompt, so existing files with those names are overwritten silently.
  ```
  csvPath = base + "_labels.csv"
          labelsJson = segmentationNode.GetAttribute(self.LABELS_ATTRIBUTE)
  ```
  Suggestion: Ask before overwriting existing sidecar files, and clean up or warn about the temp dir containing patient data after failures.

### Model weights are downloaded from Zenodo at runtime without any integrity verification
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, low confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:602`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L602): On first use the module (via the external mm_segment) downloads .pth weights from Zenodo and caches them under site-packages. Nothing in this repository verifies a hash or signature of the downloaded file, and PyTorch checkpoints are historically unpickled, so whatever the Zenodo record currently serves is executed/loaded inside the user's process. The download is announced in the progress dialog, so it is not concealed, but there is no integrity pinning.
  ```
          model_info = self._read_zenodo_models().get(region)
          if not model_info:
              raise RuntimeError(f"No cached model json and no Zenodo record known for region '{region}'.")
  ```
  Suggestion: Record expected SHA-256 checksums for each published model version and verify them before use, and prefer torch.load(..., weights_only=True) in the upstream loader.
- **haiku** (minor, medium confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:612`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L612): Models (.pth weights and json) are fetched from Zenodo by the upstream mm_segment tool, and the json fallback is fetched directly by this module (lines 601-615). No checksum or pinned record hash is checked here. Loading a tampered .pth file with torch.load could execute code, and this extension has no visibility into that step.
  ```
  for f in self._fetch_json(url).get("files", []):
              if f.get("key") == jsonFilename:
                  return self._fetch_json(f["links"]["self"])
  ```
  Suggestion: Verify Zenodo file checksums (the Zenodo API exposes them) before use, and confirm upstream loads weights with weights_only=True or equivalent. Document the trust model for model downloads.

### No automated tests and no clinical-use disclaimer
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`WholeBodyMuscleSegmentation/Testing/Python/CMakeLists.txt:2`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/Testing/Python/CMakeLists.txt#L2): The only test hook is commented out (Testing/Python/CMakeLists.txt line 2), so nothing verifies segmentation or export. The help text and README do not state that output is research-only and not for clinical decisions.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add at least a smoke test (label-table parsing and export), and add a research-use disclaimer to the module help text.

### Python unit test is declared but does not exist
minor; packaging; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`WholeBodyMuscleSegmentation/CMakeLists.txt:21`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/CMakeLists.txt#L21): The module CMakeLists calls slicer_add_python_unittest on the module script, and Testing/Python/CMakeLists.txt has the corresponding line commented out. No test class (e.g. WholeBodyMuscleSegmentationTest) exists in WholeBodyMuscleSegmentation.py, so the generated test cannot instantiate the test class and the extension's test suite will report a failure on the build dashboard even though nothing is actually tested.
  ```
  if(BUILD_TESTING)
    slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)
    add_subdirectory(Testing)
  endif()
  ```
  Suggestion: Either add a minimal WholeBodyMuscleSegmentationTest (e.g. instantiate the widget logic / check getAvailableModels parsing) or drop the slicer_add_python_unittest call.

### UI logo file is not installed by CMake
minor; packaging; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:113`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L113): The widget loads its logo from the module source directory ('MuscleMap.png' next to the .py), but MODULE_PYTHON_RESOURCES only installs Resources/Icons/MuscleMap.png and Resources/UI/....ui. In an installed extension build the plain MuscleMap.png is not copied next to WholeBodyMuscleSegmentation.py, so qt.QPixmap(logoPath) yields a null pixmap and the module shows a blank logo area.
  ```
          logoLabel = qt.QLabel()
          logoPath = os.path.join(os.path.dirname(__file__), "MuscleMap.png")
          pixmap = qt.QPixmap(logoPath)
  ```
  Suggestion: Use Resources/Icons/MuscleMap.png (which is installed) for the logo, or add the file to MODULE_PYTHON_RESOURCES.

### Unpinned install of packages Slicer bundles (scipy, scikit-learn, pandas) with a constraints file that only pins numpy and torch
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:780`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L780): The constraints file protects numpy and torch only; scipy, scikit-learn and pandas are requested with no version bound. Slicer ships its own scipy/scikit-learn, and pip will leave them alone only as long as the installed versions satisfy the requirements pulled in transitively (e.g. by monai or scikit-learn). If a newer upstream requirement exceeds Slicer's version, pip upgrades those bundled packages in place, which is exactly the ABI-fragility the authors' own comment warns about for numpy/scipy. The environment is shared with every other Slicer extension.
  ```
          segmentation_packages = [
              "monai",
              "nibabel",
              "scikit-learn",
              "scipy",
  ```
  Suggestion: Add scipy, scikit-learn, pandas and other Slicer-bundled packages to the same constraints file (pinned to the installed versions), or use the SlicerWizard/PyTorch-extension-style helpers that only install what is missing.

### Bundled .ui file is the unused Slicer template with unrelated widgets
info; soundness; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`WholeBodyMuscleSegmentation/Resources/UI/WholeBodyMuscleSegmentation.ui:59`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/Resources/UI/WholeBodyMuscleSegmentation.ui#L59): Resources/UI/WholeBodyMuscleSegmentation.ui still contains the template widgets (inputSelector, imageThresholdSliderWidget, applyButton, invertedOutputSelector) for a thresholding algorithm; the module never calls slicer.util.loadUI and builds its entire UI in setup(). Dead, misleading UI definition shipped with the module.
  ```
           <widget class="ctkSliderWidget" name="imageThresholdSliderWidget">
  ```
  Suggestion: Remove the unused .ui (and its CMake resource entry) or move the real widget tree into it.

### Input image left in the system temp directory when segmentation fails
info; soundness; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py:944`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/WholeBodyMuscleSegmentation.py#L944): On failure the temp working directory is intentionally kept and its path shown to the user, leaving a copy of the patient volume (input.nii.gz) in the OS temp folder. This is deliberate for debugging and disclosed, but on shared workstations it leaves identifiable medical data outside the user's chosen location.
  ```
              # keep tempDir for debugging
  ```
  Suggestion: Mention in the error message that the folder can be deleted, and offer a button/setting to remove it.

### Large PNG committed three times
info; utility; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`WholeBodyMuscleSegmentation/CMakeLists.txt:9`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/WholeBodyMuscleSegmentation/CMakeLists.txt#L9): The same ~570 KB image is committed at MuscleMap.png, WholeBodyMuscleSegmentation/MuscleMap.png and WholeBodyMuscleSegmentation/Resources/Icons/MuscleMap.png (the first two report the identical size 570294 bytes). Only the Resources/Icons copy is actually installed. Not harmful, just redundant binary weight in the repository.
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/Icons/MuscleMap.png
  ```
  Suggestion: Keep one copy under Resources/Icons and reference it from both the module widget and the extension metadata.

### No research-use/clinical disclaimer and no bundled sample data
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.MD:18`](https://github.com/MuscleMap/SlicerMuscleMap/blob/b578f909ab47f6033acfedc3ea6a900dde71f596/README.MD#L18): README.MD links external OSF datasets for testing and the module text asks for citations, but neither README nor the module states that output is for research use and not for clinical diagnosis, and there is no validation/performance information in the repository for the Zenodo models. This matters for an AI-based segmentation tool at tier 1.
  ```
  ### Usage
  ```
  Suggestion: Add a short 'Research use only - not a medical device' note and a pointer to the validation publications for each model region.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The module is an honest pip/progress-dialog wrapper around an external `mm_segment` package and Zenodo-hosted models; it avoids installing torch itself, pins numpy/torch via a constraints file, runs the subprocess without a shell, writes to a temp dir, and uses MIT licensing. Main issues are environment-level: the user-triggered installer does an unpinned `pip install --force-reinstall git+https://github.com/MuscleMap/MuscleMap.git` into Slicer's shared Python (so the code that runs later is not what was reviewed at this commit), plus unpinned installs of Slicer-bundled scipy/scikit-learn/pandas, a generic top-level package name `scripts`, an unpackaged logo resource, and a declared but nonexistent test. No telemetry, no data exfiltration, no prompt-injection text found.
Not checked: The external MuscleMap package (github.com/MuscleMap/MuscleMap, installed at runtime from an unpinned branch) and its mm_segment/mm_util implementation, including how model checkpoints are loaded (torch.load usage), what mm_segment imports, and how it downloads from Zenodo.; The Zenodo records themselves: model file hashes, licensing of the model weights, and training-data provenance.; The licensing terms of the MuscleMap pip package and of its dependencies (MONAI, nibabel, scikit-learn, psutil).; Whether the git branch 'main' currently resolves to the stated commit b578f909ab47f6033acfedc3ea6a900dde71f596 (network access not available); I reviewed the file contents supplied for that commit.; Runtime behavior: I could not run Slicer, the module, pip, or the extension build, so the missing-logo and missing-test-class conclusions are from reading CMake/module code rather than observing a build.; Whether Slicer's build dashboard currently reports test failures for this extension.
Questions for the author: Can the MuscleMap package be installed from a pinned release tag or commit instead of the head of the default branch, ideally with a published version and hash?; Can scipy, scikit-learn and pandas be added to the pip constraints file alongside numpy and torch so Slicer's bundled versions can never be upgraded?; Does the upstream package plan to expose a uniquely named top-level module instead of 'scripts', so the extension cannot pick up an unrelated 'scripts' package?; What license covers the Zenodo-hosted model weights, and are their checksums published so they can be verified after download?; Is a WholeBodyMuscleSegmentationTest intended, given that CMake currently declares one? The bundled .ui file appears to be the unused template - can it be removed?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
MuscleMap is a well-implemented 3D Slicer extension for automated muscle segmentation. The code follows Slicer conventions cleanly, utilizes robust asynchronous process execution with cancellation support, protects critical core packages (numpy and torch) during pip installation, and includes appropriate licensing and documentation. 🟢 Recommend merge
Not checked: Remote GitHub repository execution or downloads performed by pipeline / tests on build servers.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
No malicious or concealed behavior found in the inspected module. The main concerns are supply-chain and environment hygiene: the MuscleMap package is pip-installed unpinned from the git main branch, a generic top-level "scripts" package is installed into Slicer's site-packages, and model weights are fetched from Zenodo with no checksum verification visible in this repo. Packaging, PyTorch dependency handling, and MIT licensing look correct. The review is limited to the extension repo; MuscleMap upstream code, model weights, and model licensing were not inspected.
Not checked: Upstream MuscleMap source (github.com/MuscleMap/MuscleMap), including mm_segment.py, mm_util.py, and any torch.load calls.; Zenodo model records, their checksums, and their license terms.; The .ui file (Resources/UI/WholeBodyMuscleSegmentation.ui) contents and the icon, beyond existence.; The exact commit at scm_revision 'main' was not resolved; the review relies on the provided source reference.; CI or build results for the extension were not available.; Runtime behavior under Slicer was not run.


# AI review: SimVascular

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/SimVascular/SlicerSimVascular at commit `4a52c4bbaa9a500f0012c8488331e9546a1abc74`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:46:18Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | minor | concern |
| environment | blocking | concern | concern |
| packaging | minor | ok | unknown |
| license | unknown | ok | ok |
| soundness | minor | ok | minor |
| utility | ok | ok | ok |
| **overall** | needs fixes | minor issues | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A bundle of seven Slicer modules from the SimVascular/Marsden lab for vascular modelling: surface face painting and face-aware remeshing, mesh-complete preparation, SDF-based virtual stent deployment, SeqSeg/nnU-Net vessel segmentation, and setup/run of 0D (svZeroDSolver) and 3D (svMultiPhysics) simulations. It targets researchers doing cardiovascular simulation work in 3D Slicer.
- **flash-lite**: The SimVascular extension provides comprehensive 3D Slicer scripted modules for vascular modeling, mesh preparation, surface remeshing, model painting, stent deployment (SDFStent), 0D reduced-order modeling, multi-physics case setup, and AI-assisted vessel segmentation (SeqSeg).
- **haiku**: SimVascular is a bundle of seven scripted 3D Slicer modules (SDFStent, PaintModel, FaceAwareRemesh, SimVascularMeshPrep, SeqSeg, SimVascularROM, SimVascularMultiPhysics) for vascular modeling, meshing, and 0D/3D simulation setup, aimed at researchers using Slicer. It is a multi-module extension whose modules install packages from PyPI at runtime and download pretrained weights and test data.

## Disagreements (start here)

### D1. SeqSeg downgrades Slicer's bundled NumPy to <2
partial; category environment; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`SeqSeg/seqseg.py:2839`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SeqSeg/seqseg.py#L2839): Pressing Run SeqSeg replaces the NumPy that Slicer bundles with a 1.x build, and a pip constraint file (`numpy<2`, line 2512) is then applied to every subsequent install. Any other extension or Slicer component built against NumPy 2 breaks in that installation, including for users who never open SeqSeg. The policy lists downgrading or exactly pinning packages Slicer bundles (numpy named explicitly) as blocking.
  ```
  numpy_version_str = importlib.metadata.version("numpy")
          restart_for_numpy = pkg_version.parse(numpy_version_str) >= pkg_version.parse("2.0.0")
          if restart_for_numpy:
              logging.info(_("Downgrading NumPy from {current} to <2 for PyTorch 2.2.2 compatibility...").format(current=numpy_version_str))
              self._pipInstall("numpy<2")
  ```
  Suggestion: Do not change NumPy. Use a torch build compatible with Slicer's NumPy (through PyTorchUtils), or run the segmentation in a separate process/environment.
- **haiku** (major, high confidence, quote partly verified) [`SeqSeg/seqseg.py:2835`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SeqSeg/seqseg.py#L2835): Slicer's own numpy is downgraded and torch 2.2.2 is installed into Slicer's Python for all users, including those who never open SeqSeg. The index policy requires PyTorch to go through the PyTorchUtils extension and forbids downgrading bundled packages. Other extensions can break after the downgrade.
  ```
  # torch 2.2.2 is built against NumPy 1.x; NumPy 2.x fails import with _ARRAY_API not found.
  ...self._pipInstall("numpy<2")
  ```

### D2. SeqSeg installs PyTorch itself via light-the-torch with an exact pin
severity dispute; category environment; raised by deepseek, flash-lite, haiku
- **deepseek** (blocking, high confidence, quote partly verified) [`SeqSeg/seqseg.py:2618`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SeqSeg/seqseg.py#L2618): When the PyTorch extension is not installed, `_installTorchWithoutExtension` pip-installs light-the-torch from a GitHub main-branch zip and then runs `light_the_torch install torch==2.2.2 torchvision==0.17.2 numpy<2` into Slicer's shared Python (requiredTorchVersion = "2.2.2" at line 2827). The index policy names direct use of light-the-torch and exact torch pins as blocking, because the wheel is chosen outside PyTorchUtils and can mismatch the Slicer build; it also affects every other extension in that Slicer installation.
  ```
  slicer.util.pip_install("https://github.com/Slicer/light-the-torch/archive/main.zip")
  ...
              f"torch=={requiredTorchVersion}",
              f"torchvision=={requiredTorchVisionVersion}",
              "numpy<2",
  ```
  Suggestion: Declare PyTorch (and NNUNet) in `build_dependencies`/`EXTENSION_DEPENDS` and install torch only through `PyTorchUtils`; if the extension is absent, tell the user to install it from the Extensions Manager instead of falling back to light-the-torch.
- **flash-lite** (major, high confidence, quote quote not found) [`SeqSeg/seqseg.py:2615`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SeqSeg/seqseg.py#L2615): SeqSeg downloads and installs arbitrary code from a GitHub zip archive (light-the-torch) at runtime without cryptographic verification or pinning, and installs PyTorch/nnUNet outside Slicer's PyTorch extension (PyTorchUtils), which risks modifying Slicer's core Python environment and breaking compatibility or reproducibility.
  ```
  SeqSeg/seqseg.py:2618: slicer.util.pip_install("https://github.com/Slicer/light-the-torch/archive/main.zip")
  ```
  Suggestion: Use PyTorchUtils for PyTorch installation and avoid downloading unpinned zip archives from GitHub at runtime.
- **haiku** (minor, medium confidence, quote verified) [`SeqSeg/seqseg.py:2618`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SeqSeg/seqseg.py#L2618): An unpinned branch archive is installed into Slicer's Python to choose a torch wheel. It is a mutable reference, so the code that runs can change without notice.
  ```
  slicer.util.pip_install("https://github.com/Slicer/light-the-torch/archive/main.zip")
  ```

### D3. SeqSeg pip-installs nnunetv2, which pulls torch from PyPI
single; category environment; raised by deepseek
- **deepseek** (blocking, high confidence, quote verified) [`SeqSeg/seqseg.py:2696`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SeqSeg/seqseg.py#L2696): The policy explicitly names `nnunetv2` as a package that must not be pip-installed because it pulls torch from PyPI, and requires the NNUNet extension's install logic instead. Here the module installs nnunetv2 recursively with a hand-maintained skip list (lines 2637-2656) and additionally installs imagecodecs and acvl-utils pins (lines 2719, 2735) into Slicer's Python. The user is asked once via confirmOkCancelDisplay (line 2929), but the resulting environment is still modified outside the supported installers.
  ```
  def _installNnunetWithoutExtension(self, nnunetRequirement):
          """Install nnunetv2 without the NNUNet extension."""
          packagesToSkip = self._nnunetPackagesToSkip()
          if sys.platform == "darwin":
              self._installImagecodecsForDarwin()
  
  ```
  Suggestion: Depend on the NNUNet extension (declare it in `build_dependencies`/`EXTENSION_DEPENDS`) and use `SlicerNNUNetLib.InstallLogic`; remove the pip fallback path.

### D4. SDFStent pip-installs svmorph into Slicer's Python without asking
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`SDFStent/SDFStent.py:422`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SDFStent/SDFStent.py#L422): The first click on Update silently installs `svmorph` and all of its declared dependencies into Slicer's shared Python, with no confirmation dialog and no skip list, so pip may replace packages Slicer bundles. Docs/SDFStent.md:22 tells users this may take minutes to download packages, but nothing asks them first. This affects every extension in that Slicer installation.
  ```
  self._appendLog(_("svmorph is not installed. Installing svmorph..."))
          self._setStatus(_("Installing svmorph..."))
          try:
              slicer.util.pip_install("svmorph")
          except Exception as exc:
              raise RuntimeError(_("Failed to install required dependency 'svmorph'.")) from exc
  ```
  Suggestion: Ask for confirmation before installing (as SimVascularROM does with `confirmOkCancelDisplay`), install with `--no-deps` plus an explicit skip list for Slicer-provided packages, and state the package and size in the dialog.
- **haiku** (major, medium confidence, quote partly verified) [`SDFStent/SDFStent.py:422`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SDFStent/SDFStent.py#L422): Packages are installed into the shared Slicer environment on first run without a separate confirmation dialog. Its transitive dependencies are not controlled, so NumPy/SimpleITK pins may be affected. The intended dependency set is not visible in the sampled code.
  ```
  self._appendLog(_("svmorph is not installed. Installing svmorph..."))
  ...
   slicer.util.pip_install("svmorph")
  ```


## Findings from some reviewers

### Module unit tests are commented out of the CMake test registration
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SeqSeg/Testing/Python/CMakeLists.txt:2`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SeqSeg/Testing/Python/CMakeLists.txt#L2): The same commented-out line appears in SDFStent, PaintModel, FaceAwareRemesh and SeqSeg Testing/Python/CMakeLists.txt, so the in-module `ScriptedLoadableModuleTest` classes (e.g. PaintModel/PaintModel.py:1070-1133) are never run by ctest. The package-level pytest suites exist (FaceAwareRemesh/tests, SimVascularMeshPrep/Testing/Python) but are not wired into the build either, so a regression in these modules would not be caught by the extension build.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Register the existing module tests with `slicer_add_python_unittest`, or add a ctest that runs the package pytest suites.

### PaintModel runs region growing on the GUI thread and edits the user's polydata in place
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`PaintModel/PaintModel.py:250`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/PaintModel/PaintModel.py#L250): `createFaceGroups` builds per-cell normals, an edge map and a merge loop over all cells (lines 905-975) synchronously on the GUI thread with only a wait cursor and no progress or cancel, so a large surface freezes Slicer. The module also adds `ModelFaceID` and `_PaintModelSelectionDisplay` arrays directly to the user's model node polydata, so the in-memory model is modified without an undo snapshot for the selection overlay (only `onClearFaceGroups` calls `SaveStateForUndo`, line 278).
  ```
  qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
      try:
        groupCount = self.logic.createFaceGroups(
          modelNode, float(self.faceGroupAngleSlider.value), int(self.faceGroupSizeSpinBox.value))
  ```
  Suggestion: Run the grouping in a `qt.QTimer`/worker with progress and cancellation, and take an undo snapshot before the first modification of the model.

### SDFStent mutates sys.path with a generic module directory
minor; environment; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`SDFStent/SDFStent.py:1079`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SDFStent/SDFStent.py#L1079): Inserting the module directory at position 0 can shadow other top-level packages imported later in the session. The effect is global to the process.
  ```
  import sys
  moduleDir = os.path.dirname(__file__)
  if moduleDir not in sys.path:
      sys.path.insert(0, moduleDir)
  ```

### SimVascularROM installs svromutils/svzerod into Slicer's Python at first use
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote partly verified) [`SimVascularROM/SimVascularROM.py:253`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SimVascularROM/SimVascularROM.py#L253): The ROM panel installs `svromutils` with `--no-deps` and skips vmtk/vtk/numpy/scipy (ROM_PACKAGE_SKIPPED_DEPENDENCIES, line 173), and `svzerod` whole, after a confirmation dialog. This is the careful pattern the policy asks for, but `svzerod` is installed with its own dependencies (numpy unpinned, pandas) into Slicer's environment, so a future release could still change Slicer's NumPy. Worth documenting the residual risk or pinning the solver install.
  ```
  elif slicer.util.confirmOkCancelDisplay(
  ...
                  slicer.util.pip_install(("--no-deps " if skipPackages else "") + requirement)
  ```
  Suggestion: Consider installing svzerod with `--no-deps` plus an explicit skip list for numpy/pandas, or verify after install that Slicer's numpy version is unchanged.

### Weights archive downloaded and extracted without path checks
minor; safety; raised by haiku
- **haiku** (minor, medium confidence, quote partly verified) [`SeqSeg/seqseg.py:2304`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SeqSeg/seqseg.py#L2304): The archive comes from Zenodo over HTTPS after a user confirm, with no checksum verification and no member path validation before extractall. A malicious archive could write outside the target folder. The risk is limited by the trusted hosts, but integrity is not checked.
  ```
  urllib.request.urlretrieve(profile["url"], zip_file, show_progress)
  ...
  with zipfile.ZipFile(zip_file, "r") as zip_ref:
      zip_ref.extractall(extract_target)
  ```

### Model weights and solver binaries are downloaded at run time; provenance is documented but not validated
info; utility; raised by deepseek
- **deepseek** (info, medium confidence, quote partly verified) [`SeqSeg/seqseg.py:495`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SeqSeg/seqseg.py#L495): SeqSeg downloads nnU-Net weights from Zenodo (with a confirmation dialog) and SDFStent downloads sample data from GitHub releases. The Docs describe the models, but there is no checksum verification of the downloaded archives and no statement of the weights' licence or validation, which matters for a clinical-adjacent segmentation tool.
  ```
  "url": "https://zenodo.org/records/15020477/files/nnUNet_results.zip?download=1",
              "zip_filename": "nnUNet_results.zip",
              "extracted_dir_name": "nnUNet_results",
              "progress_label": "Downloading Aorta weights (CT/MR) (236.3 MB)...",
  ```
  Suggestion: Record a SHA256 for each archive and verify it after download, and state the weights' licence and validation data in Docs/SeqSeg.md.

### Revision is 'main' and was not resolved
info; packaging; raised by haiku; **quote not found in source**
- **haiku** (info, high confidence, quote file not found) [`SimVascular:1`](https://github.com/SimVascular/SlicerSimVascular/blob/4a52c4bbaa9a500f0012c8488331e9546a1abc74/SimVascular#L1): A branch reference is not a security finding by itself, but the reviewed commit could not be confirmed. The 4a52c4bb commit in the review header was not resolved against the entry.
  ```
  "scm_revision": "main",
  ```


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Well-documented, thoughtfully written extension, but the SeqSeg module installs PyTorch itself (light-the-torch, exact `torch==2.2.2` pin), installs `nnunetv2` from PyPI, and downgrades Slicer's bundled NumPy to <2 — all explicitly disallowed by the index policy, and none of it declared in `build_dependencies`/`EXTENSION_DEPENDS`. SDFStent also pip-installs `svmorph` into Slicer's Python with no confirmation. No data exfiltration, telemetry, or reviewer-manipulating text found; downloads are from GitHub/Zenodo/PyPI and model weights require confirmation. Packaging is largely correct; most module tests are commented out of CMake. License texts were not read, so distribution permission is unverified.
Not checked: The licence texts themselves (LICENSE.txt, SeqSeg/LICENSE.txt, FaceAwareRemesh/NOTICE.txt, THIRD_PARTY_NOTICES.txt) were not read, so distribution permission is unverified.; The licence and validation of the Zenodo nnU-Net weight archives and the GitHub-release sample data were not verified.; SeqSeg/seqseg.py is 4112 lines; I read the installer paths (lines 2390-3010) and searched the rest, but did not read the segmentation/process-launch code in full.; SDFStent/SDFStent.py (1715 lines) and SimVascularMeshPrep/SimVascularMeshPrep.py, SimVascularMultiPhysics/SimVascularMultiPhysics.py, SimVascularROM/SimVascularROM.py were only searched, not read end to end; the external-Python subprocess paths in SDFStent (lines 1317-1450) were seen only as search; FaceAwareRemesh/svremesh/remesh.py (92 KB) and dynamic_mesh.py were not read; the geometry3Sharp port was not compared against the original.; AGENTS.md in the extension repository was not read in full; search hits show developer guidance for the extension's own contributors, and I saw no text aimed at index reviewers.; The catalog entry's `scm_revision` is the branch `main`; I could not resolve the commit 4a52c4bbaa9a500f0012c8488331e9546a1abc74 or confirm that the files shown correspond to it.; No build or test run was possible, so I could not confirm that every imported module file is installed by CMake (e.g. cross-module imports of `svmeshcomplete` and `svromsetup` between the ROM, MultiPhysics and MeshPrep modules).
Questions for the author: Can SeqSeg be changed to require the PyTorch and NNUNet extensions (declared in `build_dependencies` and `EXTENSION_DEPENDS`) instead of installing torch via light-the-torch and nnunetv2 from PyPI, and to stop downgrading Slicer's NumPy?; Can SDFStent ask for confirmation before pip-installing `svmorph`, and install it with `--no-deps` plus a skip list for packages Slicer provides?; What licence covers the nnU-Net weight archives downloaded from Zenodo, and are checksums recorded for them?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): minor issues
The SimVascular extension for 3D Slicer contains robust, well-documented modules for vascular modeling, mesh preparation, remeshing, 0D ROM, multi-physics setup, and vessel segmentation. Packaging, CMake configuration, and licensing are in order. A major concern is SeqSeg's runtime downloading and installation of unpinned external packages and PyTorch components outside of PyTorchUtils. Overall, the extension is high quality with minor environment/safety considerations. 🟢 Recommend merge.
Not checked: Extensive runtime execution of complex simulation workflows and UI event handlers across all modules (SimVascularROM, SimVascularMultiPhysics, SimVascularMeshPrep, SDFStent, PaintModel, FaceAwareRemesh, SeqSeg).
Questions for the author: Are the large binary documentation images intended to be checked into the source repository?

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
I reviewed a partial sample: the catalog entry, top-level CMake/LICENSE/THIRD_PARTY_NOTICES, and grep-level hits for pip installs, downloads, and sys.path edits in SDFStent.py, SeqSeg/seqseg.py, SimVascularROM.py, and svromsetup/testing_data.py. I did not read the full modules or the Docs. The main concerns are that SeqSeg installs torch 2.2.2 and downgrades NumPy into Slicer's shared Python, and that SDFStent pip-installs svmorph without a PyTorch-extension path. Both are environment issues the index policy asks me to flag. The licence picture is mixed (BSD at top level, Apache-2.0 for SeqSeg, Boost for remesh ports) and looks clear. I could not verify the pinned revision, so this is not a full approval.
Not checked: Full contents of SDFStent.py, seqseg.py, SimVascularROM.py, SimVascularMeshPrep, SimVascularMultiPhysics, FaceAwareRemesh modules, and the svromsetup/svmpsetup/svmeshcomplete packages (only grep-level hits and a few excerpts were read).; Whether every imported Python file is listed in CMake, and whether EXTENSION_DEPENDS matches the catalog build_dependencies.; Whether revision 'main' or commit 4a52c4bb exists and matches what was reviewed.; Docs/*.png and Docs/*.jpg binaries (large-file hint) and SimVascular.png.; Testing folders and any CI results.; Copyright-SimVascular.txt referenced by the root LICENSE was not present in the file list.; Network endpoints actually used at runtime (testing data URLs in svromsetup/testing_data.py beyond its header).
Questions for the author: Can SeqSeg rely on the PyTorchUtils extension and NNUNet extension exclusively rather than pip-installing torch and downgrading numpy into Slicer?; Should SDFStent's svmorph install ask for confirmation before pip installing, and what are its full transitive dependencies?; Can the light-the-torch install be pinned to a release or commit instead of main.zip?; Can the weights archive be checked against a SHA-256 and its members validated before extraction?


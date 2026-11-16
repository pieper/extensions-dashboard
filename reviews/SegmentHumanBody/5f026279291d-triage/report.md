# AI review: SegmentHumanBody

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/mazurowski-lab/SlicerSegmentHumanBody at commit `5f026279291d2980a01274a0d0aaa6c1a4d68960`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T02:38:58Z; cost $0.10

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | concern | concern |
| environment | blocking | blocking | concern |
| packaging | concern | ok | concern |
| license | concern | ok | concern |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **deepseek**: SegmentHumanBody is a 3D Slicer scripted module that wraps Mazurowski Lab's SegmentAnyBone / SAM-family deep-learning models to segment bones and other structures in MRI/CT volumes, with 2D/3D label assignment and an interactive SAM prompt-point workflow.
- **flash-lite**: SegmentHumanBody provides deep learning-based segmentation tools for medical data within 3D Slicer, integrating models developed by the Mazurowski Lab such as SegmentAnyBone, SAM, and nnUNet-based tools.
- **haiku**: SegmentHumanBody is a 3D Slicer scripted module that wraps several Mazurowski Lab deep-learning segmentation models (SegmentAnyBone/SAM-based bone segmentation, SegmentAnyMuscle, a breast VNet, a CT nnU-Net body-composition pipeline, and an SAM2 annotation tool) for MRI/CT segmentation. It is intended for researchers using Slicer's Segmentation workflow and depends on the PyTorch extension.

## Disagreements (start here)

### D1. Bundling GUI libraries via opencv-python
partial; category environment; raised by deepseek, flash-lite
- **deepseek** (major, high confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:371`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L371): opencv-python ships its own Qt libraries; installing it into Slicer's environment can cause Qt symbol clashes and crashes in Slicer itself and in other extensions. The policy explicitly requires opencv-python-headless instead.
  ```
  slicer.util.pip_install("opencv-python")
  ```
  Suggestion: Install opencv-python-headless, or avoid OpenCV entirely (the only use seen is cv2.cvtColor/COLOR_GRAY2RGB at line 842).
- **flash-lite** (blocking, high confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:371`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L371): Installing `opencv-python` instead of `opencv-python-headless` bundles GUI libraries (Qt) which conflicts with 3D Slicer's bundled Qt libraries and can cause crashes or windowing issues.
  ```
  slicer.util.pip_install("opencv-python")
  ```
  Suggestion: Use opencv-python-headless instead of opencv-python.

### D2. Unsafe PyTorch/nnunetv2 installation via pip
partial; category environment; raised by flash-lite, haiku
- **flash-lite** (blocking, high confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:172`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L172): Installing `nnunetv2` directly via pip inside Slicer can pull PyPI dependencies including PyTorch, which violates Slicer policy requiring PyTorch to be managed exclusively via PyTorchUtils.
  ```
  slicer.util.pip_install("nnunetv2")
  ```
  Suggestion: Remove direct pip installations of packages that pull PyTorch or manage dependencies through PyTorchUtils.
- **haiku** (major, high confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:167`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L167): nnunetv2 pulls torch from PyPI as a dependency, which violates the policy requirement that PyTorch be installed only through the PyTorch extension. opencv-python (line 371) bundles its own Qt, which the policy flags explicitly; opencv-python-headless is the expected package. Other packages (pandas, blosc2, totalsegmentator, hydra-core, tensorboard) can downgrade or conflict with packages Slicer bundles. The installs are confirmation-gated but still change the shared environment for all Slicer users.
  ```
  import nnunetv2
   except ModuleNotFoundError:
   if slicer.util.confirmOkCancelDisplay(
   "nnunetv2 package is missing. Click OK to install it now!"
   ):
   slicer.util.pip_install("nnunetv2")
  ```
  Suggestion: Use the NNUNet extension's install logic for nnunetv2 with torch pins handled by PyTorchUtils, use opencv-python-headless, and check each package against Slicer's bundled versions before installing.

### D3. nnunetv2 and totalsegmentator are pip-installed and pull torch from PyPI
single; category environment; raised by deepseek
- **deepseek** (blocking, high confidence, quote verified, other lines) [`SegmentHumanBody/SegmentHumanBody.py:103`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L103): The module imports nnunetv2 and totalsegmentator and installs them with slicer.util.pip_install when missing. Both packages declare torch as a dependency, so pip resolves torch from PyPI into Slicer's shared environment, bypassing the PyTorch extension/PyTorchUtils that the catalog entry declares as a build dependency. This can replace or shadow the Slicer-managed torch and break other extensions for users who never open this module.
  ```
          try:
              import nnunetv2
  ```
  Suggestion: Remove nnunetv2/totalsegmentator from the runtime install path, or install them with --no-deps and obtain torch only through PyTorchUtils as the policy requires.

### D4. Blocking input() prompts in a GUI application
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`SegmentHumanBody/models/sam/build_sam.py:182`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/models/sam/build_sam.py#L182): build_sam.py asks for confirmation on stdin and then calls urllib.request.urlretrieve. Inside Slicer there is no usable stdin, so this either hangs the GUI thread or raises EOFError; the download also has no progress reporting or checksum.
  ```
          cmd = input("Download sam_vit_b_01ec64.pth from facebook AI? [y]/n: ")
  ```
  Suggestion: Replace with slicer.util.confirmOkCancelDisplay and a background download with progress, or ship the checkpoint via the extension's download mechanism.

### D5. CMake installs only part of the model tree the module reads
single; category packaging; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`SegmentHumanBody/CMakeLists.txt:9`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/CMakeLists.txt#L9): The resource list covers models/sam/* and models/bone_sam.pth only. The module resolves models/segment_any_muscle, models/ct_segmentation and models/sam2_annotation_tool through resourcePath("UI") + "/../../models/..." (e.g. SegmentHumanBody.py:760-761), and those directories are never installed, so the muscle, CT and SAM2 features fail in an installed build. models/utils.py and models/efficientnet.py are also not installed despite being imported by models/efficientnet.py.
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/Icons/${MODULE_NAME}.png
    Resources/UI/${MODULE_NAME}.ui
    models/cfg.py
  ```
  Suggestion: Add every directory/file the module imports or opens to MODULE_PYTHON_RESOURCES (or install the models tree wholesale), and verify from a packaged build.

### D6. Hardcoded developer path in os.system call
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:1197`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L1197): The muscle/fat prediction path points at the author's own Windows home directory, so it fails for every other user and on macOS/Linux. It also shells out to whatever 'python' is on PATH rather than Slicer's interpreter, and the return code is ignored so the failure is silent.
  ```
  os.system("python C:/Users/zafry/SlicerSegmentHumanBody/SegmentHumanBody/models/ct_segmentation/predict_muscle_fat.py")
  ```
  Suggestion: Resolve the script with self.resourcePath()/moduleDir and run it with slicer.util.launchConsoleProcess or in-process, checking the exit status and reporting errors to the user.
- **haiku** (major, high confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:1197`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L1197): The CT Segmentation path shells out to the system 'python' on a hardcoded path from the author's Windows account. On any other machine the script does not run, and the next line loads a result file that does not exist. On a machine where that path happens to exist, it runs whatever Python is first on PATH outside Slicer's interpreter. This is a broken path and a shell call that bypasses Slicer's environment.
  ```
  os.system("python C:/Users/zafry/SlicerSegmentHumanBody/SegmentHumanBody/models/ct_segmentation/predict_muscle_fat.py")
  ```
  Suggestion: Call the script in-process via the module path, use the Slicer Python executable (sys.executable) with an argument list via subprocess, and drop the hardcoded user path.

### D7. Large binaries committed to the repository
partial; category packaging; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`SegmentHumanBody/CMakeLists.txt:30`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/CMakeLists.txt#L30): bone_sam.pth (46 MB), segment_any_muscle/segmentanymuscle.pth (56 MB) and an 18 MB Miniconda3-latest-MacOSX-arm64.sh installer are committed. This bloats every clone and the extension package, and the Miniconda installer is a redistributable binary that should not ship inside a Slicer extension.
  ```
    models/bone_sam.pth
  ```
  Suggestion: Download weights on demand with checksum verification and remove the Miniconda installer from the repository.
- **haiku** (major, high confidence, quote verified) [`SegmentHumanBody/CMakeLists.txt:30`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/CMakeLists.txt#L30): models/bone_sam.pth (46 MB) is listed as a module resource and committed to git. The tree also contains a 18 MB Miniconda-latest-MacOSX-arm64.sh installer under models/sam2_annotation_tool and a segment_any_muscle .pth of 56 MB. Big binaries inflate every clone and the extension package, and the installer is an unneeded executable. The policy says large binaries should be downloaded on demand. Unverified: I could not read these binaries, so I did not check their contents or hashes.
  ```
      models/bone_sam.pth
      )
  ```
  Suggestion: Remove the installer and fetch model weights on demand with checksums, as the module already does for other models.

### D8. Model and code downloads from Google Drive and GitHub at widget init without integrity checks
single; category safety; raised by haiku
- **haiku** (major, high confidence, quote partly verified) [`SegmentHumanBody/SegmentHumanBody.py:306`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L306): On first open the module clones the repo over the network and downloads several checkpoints (breast VNet, CT nnU-Net, SLM-SAM2) from Google Drive with no hash or signature check. The checkpoints are loaded with torch.load and pickle in-process. A tampered or swapped Drive file would run in the user's Slicer. Each download is behind a confirm dialog, which limits the exposure. Consider pinning revisions and checking SHA-256 for every artifact.
  ```
  git.Repo.clone_from("https://github.com/mazurowski-lab/SlicerSegmentHumanBody", copyFolder)
   url = 'https://drive.google.com/uc?id=1IQu_8hYnvAR1_GSKpzkf5l7mqlcQpq3j'
   gdown.download(url, output, quiet=False)
  ```
  Suggestion: Pin the clone to a commit SHA, verify checksums for each downloaded weight, and prefer safetensors or weights_only=True loading.

### D9. Model weights downloaded without integrity verification and loaded with torch.load
single; category safety; raised by deepseek
- **deepseek** (major, high confidence, quote verified, other lines) [`SegmentHumanBody/SegmentHumanBody.py:318`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L318): Weights are fetched from Google Drive with no checksum or signature check, then deserialized in models/sam/build_sam.py:215 with torch.load(f) without weights_only=True. A substituted or tampered .pth file executes arbitrary Python in the Slicer process with the user's privileges. The same pattern appears in models/utils.py:377 via model_zoo.load_url over plain http.
  ```
  gdown.download(url, output, quiet=False)
  ```
  Suggestion: Pin a SHA-256 for each checkpoint and verify after download, and load with torch.load(..., weights_only=True) or map_location plus a safe state-dict loader.

### D10. Multiple packages installed into the shared environment at runtime
single; category environment; raised by deepseek
- **deepseek** (major, high confidence, quote verified, other lines) [`SegmentHumanBody/SegmentHumanBody.py:103`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L103): timm, einops, gdown, blosc2, pandas and pywintypes are all imported and pip-installed on demand into Slicer's shared Python. Each install mutates the environment for every extension and can pin or upgrade numpy/scipy/pillow as transitive dependencies. pywintypes is also not a valid PyPI distribution name (pywin32 provides it), so that install path is broken.
  ```
          try:
              import timm
  ```
  Suggestion: Bundle what is needed in the extension's own wheel/venv, or document and gate each install behind an explicit confirmation dialog; fix the pywintypes import to pywin32.

### D11. Non-commercial license and missing third-party license texts
single; category license; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`CMakeLists.txt:10`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/CMakeLists.txt#L10): CC BY-NC 4.0 permits redistribution but forbids commercial use, so users and clinical deployments must be told. The bundled Meta SAM/SAM2 sources are Apache-2.0 (headers say 'licensed under the license found in the LICENSE file in the root directory of this source tree') but no Apache-2.0 text is included, and the license of the bundled .pth weights and the Miniconda installer is not stated.
  ```
  set(EXTENSION_DESCRIPTION "SegmentHumanBody aims to asist its users in segmenting MRI medical data on 3D Slicer by integrating varios deep learning models developed by Mazurowski Lab. SegmentHumanBody has CC BY-NC 4.0 license which does not allow commercial use.")
  ```
  Suggestion: Add the Apache-2.0 text for the bundled SAM/SAM2 code, state the license of each model checkpoint, and surface the non-commercial restriction in the README and module UI.

### D12. Runtime installation of remote source archive
single; category safety; raised by flash-lite
- **flash-lite** (major, high confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:353`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L353): Downloading and installing arbitrary code archives from GitHub via pip at runtime without user consent verification or integrity checks poses security and stability risks.
  ```
  slicer.util.pip_install("https://github.com/facebookresearch/segment-anything/archive/6fdee8f2727f4506cfbbe553e23b895e27956588.zip")
  ```
  Suggestion: Declare external dependencies properly in CMake and packaging rather than installing via zip URL at runtime.

### D13. createFeatures deletes every file in a folder without checking its contents
single; category safety; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:834`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L834): The code unconditionally removes all files matching * in featuresFolder. If that folder is ever configured to a user directory (or the default resolves outside a temp dir), user data is destroyed without confirmation. I could not verify where featuresFolder is set, so the blast radius is unconfirmed.
  ```
          oldFeatureFiles = glob.glob(self.featuresFolder + "/*")
          for filename in oldFeatureFiles:
              os.remove(filename)
  ```
  Suggestion: Use a dedicated temporary directory created with tempfile.mkdtemp(), or restrict deletion to files matching the expected *_features.pkl pattern.

### D14. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D15. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D16. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Global git config changed on widget init
minor; environment; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:294`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L294): The module changes the user's global git configuration, outside the extension's own scope, as a side effect of opening the module.
  ```
  os.system("git config --global core.longpaths true")
  ```
  Suggestion: Remove the global git config change, or pass the setting per repository.

### Global sys.path mutation in a model module
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SegmentHumanBody/models/vae.py:2`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/models/vae.py#L2): Importing this module appends a directory to the process-wide sys.path, which can shadow Slicer's own modules for the whole session. It is a side effect at import time rather than a local import.
  ```
  sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  ```
  Suggestion: Use relative imports or importlib with an explicit path instead of mutating sys.path.

### Malformed icon URL in module CMakeLists
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SegmentHumanBody/CMakeLists.txt:36`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/CMakeLists.txt#L36): The URL omits the branch segment (/main/), so it resolves to a non-existent path. The root CMakeLists.txt:11 has the correct URL; the duplicate in the module file is wrong.
  ```
  set(EXTENSION_ICONURL "https://raw.githubusercontent.com/mazurowski-lab/SlicerSegmentHumanBody/SegmentHumanBody/Resources/Icons/SegmentHumanBody.png")
  ```
  Suggestion: Remove the duplicate EXTENSION_* variables from the module CMakeLists or fix the URL to include /main/.

### Model imports may fail: SAM_LST uses undefined names
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`SegmentHumanBody/models/sam_LST.py:1`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/models/sam_LST.py#L1): The file imports 'sam' as a top-level module and uses 'os' without importing it, so it cannot load inside the extension. It is not in the CMake list, so it is dead code, but it shows that not all bundled modules were tested. Also, the module-level 'args = cfg.parse_args()' at SegmentHumanBody.py:24 runs argparse on import.
  ```
  from sam import sam_model_registry
  import torch
  import torch.nn as nn
  from torchvision.models.resnet import resnet18
  ```
  Suggestion: Remove unused model files, or fix the imports and add tests.

### Model-specific subprocess call uses a hardcoded Windows path and os.system
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`SegmentHumanBody/models/ct_segmentation/predict_muscle_fat.py:28`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/models/ct_segmentation/predict_muscle_fat.py#L28): The command is built by string interpolation and run through the shell. Paths containing spaces or shell metacharacters break or inject commands. The input path comes from the user's volume filename, so this is a command injection path on the user's own machine. Severity is minor because the user already controls the input.
  ```
  command = (f"TotalSegmentator -i {input_path} -o {output_path} "
                  f"--roi_subset vertebrae_T12 vertebrae_L3 vertebrae_L4")
        print(f"Running command: {command}")
        os.system(command)
  ```
  Suggestion: Use subprocess.run with an argument list and no shell.

### No automated tests
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`SegmentHumanBody/Testing/Python/CMakeLists.txt:2`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/Testing/Python/CMakeLists.txt#L2): The only test registration is commented out. SegmentHumanBody/CMakeLists.txt:52 registers a unittest against SegmentHumanBody.py, but no test class was visible in the module, so there is effectively no coverage of the segmentation or label-assignment logic.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a real module test with a small sample volume and enable it in Testing/Python/CMakeLists.txt.
- **haiku** (minor, high confidence, quote verified) [`SegmentHumanBody/Testing/Python/CMakeLists.txt:2`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/Testing/Python/CMakeLists.txt#L2): The only test registration is commented out, so there is no automated check that the module loads or that the models run. This is non-blocking, but it makes the install-and-download behavior above hard to validate.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a minimal load test that does not download weights, and a smoke test on sample data.

### No sample data, validation, or clinical-use disclaimer
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:26`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/README.md#L26): The README gives a usable workflow and screenshots, but there is no sample dataset, no accuracy/validation information for the bundled models, and no statement that output is not for clinical use. The README also confirms the first-run install blocks the GUI for several minutes.
  ```
  - Load an image to be segmented.
  - Choose **Modules > Segmentation > SegmentHumanBody** module in the module selector. The first time the module is started, it will ask permission to install pytorch. Give permission and wait several minutes for the installation to complete. The application will not be responsive during the installation.
  ```
  Suggestion: Add a small sample volume, cite validation results for SegmentAnyBone, and add a research-use-only disclaimer.

### Non-commercial license restricts use of extension and weights
minor; license; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`LICENSE.md:1`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/LICENSE.md#L1): CC BY-NC 4.0 permits distribution but prohibits commercial use. The extension description and the module's warningDisplay state this, so users are informed. Bundled third-party model weights (SAM, SegmentAnyMuscle, SLM-SAM2, nnU-Net) may carry their own terms that I did not verify. The grant itself is not missing and does not prohibit distribution.
  ```
  # Attribution-NonCommercial 4.0 International
  ```
  Suggestion: Confirm that the upstream model licenses allow redistribution under CC BY-NC, and list them in the README.

### pickle used for feature caches
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:1096`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L1096): Features are written with pickle.dump (line 846) and read back with pickle.load. The files are self-generated, so risk is low, but any file placed in that folder by another process would be deserialized as arbitrary Python.
  ```
  self.sam.features = pickle.load(f)
  ```
  Suggestion: Use np.save/np.load or torch.save with weights_only=True for the feature cache.
- **haiku** (minor, medium confidence, quote verified) [`SegmentHumanBody/SegmentHumanBody.py:1095`](https://github.com/mazurowski-lab/SlicerSegmentHumanBody/blob/5f026279291d2980a01274a0d0aaa6c1a4d68960/SegmentHumanBody/SegmentHumanBody.py#L1095): Feature files are written by the module itself (line 846) into the module resource folder, so exploitation needs write access to that folder. The unpickle is still unsafe in principle if the folder is shared or the files are copied from elsewhere. Note the same pattern at line 1461.
  ```
  with open(self.featuresFolder + "/slice_" + str(currentSliceIndex) + "_features.pkl" , 'rb') as f:
                        self.sam.features = pickle.load(f)
  ```
  Suggestion: Store features as .npy or safetensors and load with allow_pickle=False.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The module is a large, research-grade SAM wrapper. Safety-wise there is no telemetry or exfiltration, but it downloads model weights from Google Drive without integrity checks and loads them with torch.load (no weights_only), and it deletes every file in a features folder. Environment impact is the main problem: nnunetv2, totalsegmentator, timm, blosc2, gdown and opencv-python are pip-installed at runtime; nnunetv2/totalsegmentator pull torch from PyPI and opencv-python bundles its own Qt. Packaging is also weak: CMake installs only models/sam plus bone_sam.pth while the code reads models/segment_any_muscle, models/ct_segmentation and models/sam2_annotation_tool, and ~120 MB of binaries (including a Miniconda installer) are committed. License is CC BY-NC 4.0 (non-commercial) with bundled Meta SAM code whose license text is absent.
Not checked: The exact source revision: the catalog entry uses scm_revision "main" (a moving branch), so the code reviewed is the tip at review time, not a pinned commit.; SegmentHumanBody.py lines 200-460 and 460-760 in full detail (only search hits and excerpts were read), so the confirmation dialogs around each pip_install call were not verified line by line.; Where self.featuresFolder and self.slicesFolder are set, so the blast radius of the os.remove loop is unconfirmed.; models/sam2_annotation_tool/demo/backend/server/app.py: whether this HTTP server is ever started by the module and whether it binds a port.; models/ct_segmentation/predict_muscle_fat.py and models/segment_any_muscle/main.py: their download and file-writing behavior.; The binary .pth checkpoints and the Miniconda installer could not be inspected for content or embedded code.; Whether torch itself is installed via PyTorchUtils or via pip_install; the README says the module asks permission to install pytorch, but the install call was not read.; The license terms of the bundled model weights and of the Miniconda installer.
Questions for the author: Is torch installed through PyTorchUtils (the PyTorch extension) or via slicer.util.pip_install? Please point to the code path.; Why are nnunetv2 and totalsegmentator installed at runtime when both pull torch from PyPI?; Where do self.featuresFolder and self.slicesFolder point, and is the os.remove loop guaranteed to stay inside a temporary directory?; Are the downloaded .pth checkpoints verified against a published checksum before torch.load?; What are the license terms of bone_sam.pth and segmentanymuscle.pth, and why is an 18 MB Miniconda installer committed to the repository?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): needs fixes
The SegmentHumanBody extension offers advanced deep learning segmentation models for medical imaging in 3D Slicer. However, it violates core 3D Slicer environment guidelines by installing packages like `nnunetv2` (which can pull PyTorch from PyPI) and `opencv-python` (which bundles conflicting Qt binaries instead of using `opencv-python-headless`) at runtime. These issues must be fixed before the extension can be accepted into the catalog.
Not checked: Complete functionality testing within a live 3D Slicer runtime environment; Detailed inspection of all model weight files and subdirectories under sam2_annotation_tool and ct_segmentation

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The module's widget constructor, which runs on first open, installs a long list of pip packages (including nnunetv2, opencv-python, totalsegmentator, and a segment-anything zip from GitHub) after confirmation dialogs, clones the GitHub repo with git, and downloads several model checkpoints from Google Drive with gdown. It also uses pickle.load on feature files, runs os.system with a hardcoded developer path (C:/Users/zafry/...), and ships a 46 MB .pth and an 18 MB Miniconda installer in the tree. The CC BY-NC license forbids commercial use but is clearly stated. Overall: needs fixes before listing. I could not inspect the large binaries, the full module, or the CMake/Slicer build.
Not checked: The full SegmentHumanBody.py (lines 400-690, 715-1085, 1101-1185, 1205-1548) was not read, so the segmentation logic and any other network or file behavior there are unverified.; Binary files (bone_sam.pth, segmentanymuscle.pth, the Miniconda installer, checkpoints) were not inspected for contents, provenance, or hashes.; The sam2_annotation_tool, segment_any_muscle, and ct_segmentation subtrees were only searched by pattern, not read in full. The subprocess and torch.load call sites in those trees were not traced.; The live GitHub revision 'main' was not resolved, and the CMake build, Slicer loading, and the Google Drive file contents were not verified.; No commands were run and no network access was used, so the install and download behavior was assessed from source only.
Questions for the author: Why does the module clone the GitHub repo and copy subfolders at runtime instead of packaging them through CMake?; Can nnunetv2 and opencv-python be installed through the NNUNet extension and opencv-python-headless instead, to avoid PyTorch and Qt conflicts?; Is the CT Segmentation path (SegmentHumanBody.py:1197) meant to run the script in-process? The hardcoded C:/Users/zafry path must be removed.; Should models/sam2_annotation_tool/Miniconda3-latest-MacOSX-arm64.sh and the large .pth binaries be removed from the repo and fetched on demand with checksums?; Do the upstream model licenses (SAM, SegmentAnyBone, SLM-SAM2, nnU-Net, SegmentAnyMuscle) permit redistribution under CC BY-NC 4.0?


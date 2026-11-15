# AI review: DBSCoalignment

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/IVarha/SlicerDBSCoalignment.git at commit `d1d9b946b46f05f6f40fd53305c84ac9e0e7c240`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T17:26:17Z; cost $0.07

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | blocking | concern | concern |
| environment | blocking | blocking | blocking |
| packaging | blocking | ok | concern |
| license | minor | ok | minor |
| soundness | concern | minor | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **deepseek**: DBSCoalignment bundles six Slicer modules for deep brain stimulation (DBS) work: STN segmentation from T1/T2 MRI, atlas mapping, MER/electrode shift prediction integrated with Lead-OR, label conversion and text-to-markup helpers. It targets DBS clinicians and researchers using Slicer with SlicerElastix and SlicerNetstim.
- **flash-lite**: DBSCoalignment is a 3D Slicer extension providing modules for DBS pre-processing, STN segmentation, atlas mapping, shift prediction, and label conversion.
- **haiku**: A 3D Slicer extension for DBS (deep brain stimulation) planning: it segments the subthalamic nucleus (STN) from T1/T2 MRI using pretrained networks, maps atlas meshes, and estimates brain shift and electrode trajectories from intraoperative MER/Lead-OR data. It is intended for neurosurgery research groups using Slicer, Netstim/Lead-OR and Elastix.

## Disagreements (start here)

### D1. CMake installs resource files that do not exist in the repository
single; category packaging; raised by deepseek
- **deepseek** (blocking, medium confidence, quote verified) [`DBS_STN/CMakeLists.txt:16`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/DBS_STN/CMakeLists.txt#L16): Directory listing of DBS_STN/Resources/nets shows only 3.obj, cent_detect_hist.pkl, detect_mask.pkl, mer_pca_mesh.pkl, shape_hist.pkl, shape_pcas.pkl, stn_shape_mask.pkl and transformer_classifier_test.pt; net_transformer.pt is absent (read_file returned 'No such file'). Likewise STNSegmenter/CMakeLists.txt:18,23 list Resources/MNI/MNI152_T1_1mm_brain.nii.gz and Resources/nets/cent_pred.pt, which are also absent. CMake install of missing files fails the extension build/package step.
  ```
  set(MODULE_PYTHON_RESOURCES
      Resources/Icons/${MODULE_NAME}.png
      Resources/UI/${MODULE_NAME}.ui
      Resources/nets/net_transformer.pt
  ```
  Suggestion: Either commit the referenced weights/templates or remove them from MODULE_PYTHON_RESOURCES and rely on the existing download path (STNSegmenter.py:730).

### D2. Wheel downloaded from a Box.com shared link and installed without integrity check
partial; category safety; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`STNSegmenter/STNSegmenter.py:35`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L35): On Linux/Python 3.12 the module fetches a binary wheel from an anonymous file-sharing link and pip-installs it into Slicer's Python (line 44). The link is not a package index, has no checksum or signature verification, and the content can be replaced by whoever controls the Box share, giving arbitrary code execution in the user's Slicer session. It also runs at import time (see the try/except at lines 55-62).
  ```
  download_url = "https://app.box.com/shared/static/mu1gy26t80oopbtv3mndl5yveb6s4431.whl"
          whl_filename = "antspyx-0.6.2-cp312-cp312-linux_x86_64.whl"
          whl_path = Path(tempfile.gettempdir()) / whl_filename
  ```
  Suggestion: Install antspyx from PyPI (or a pinned, hash-verified release asset) and only after explicit user confirmation; never install binaries from file-sharing links.
- **haiku** (major, high confidence, quote verified) [`STNSegmenter/STNSegmenter.py:35`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L35): On a specific Linux/Python combination, _install_antspyx() fetches a wheel from app.box.com with no checksum, then installs it. Anyone who can replace the Box file controls code that runs in the user's Slicer Python. The URL is also a personal share link that can change.
  ```
  download_url = "https://app.box.com/shared/static/mu1gy26t80oopbtv3mndl5yveb6s4431.whl"
          whl_filename = "antspyx-0.6.2-cp312-cp312-linux_x86_64.whl"
          whl_path = Path(tempfile.gettempdir()) / whl_filename
  
          logging.info("Downloading antspyx wheel from %s", download_url)
          urllib.request.urlretrieve(download_url, str(whl_path))
  ```
  Suggestion: Install antspyx from PyPI with a pinned version, or verify a SHA256 of the wheel before installing. Do not depend on a personal file-share link.

### D3. Code installed directly from a git branch at import time
single; category safety; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`STNSegmenter/STNSegmenter.py:60`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L60): pip installs the current tip of an unpinned third-party branch into Slicer's environment; whatever is committed there later executes inside Slicer. The same call is repeated in _install_segm_runtime_dependencies (line 189). No revision pin, no user confirmation.
  ```
  slicer.util.pip_install('git+https://github.com/ANTsX/ANTsTorch.git')
      import antstorch
  ```
  Suggestion: Depend on a released, version-pinned package (or a pinned commit) and install it only on explicit user action.

### D4. EXTENSION_DEPENDS does not match the catalog entry's build_dependencies
partial; category packaging; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`CMakeLists.txt:12`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/CMakeLists.txt#L12): The catalog entry declares "build_dependencies": [], so the index will not fetch SlicerElastix/SlicerNetstim before building, while AtlasMapping.py:1027 imports Elastix at runtime and DBS_STN integrates with Netstim. The two declarations must agree for the entry to be mechanically usable.
  ```
  set(EXTENSION_DEPENDS "SlicerElastix;SlicerNetstim") # AtlasMapping uses Elastix, DBS workflow integrates with Netstim/Lead-OR
  ```
  Suggestion: Add SlicerElastix and SlicerNetstim to build_dependencies in the catalog entry (or drop them from EXTENSION_DEPENDS if truly optional).
- **haiku** (major, high confidence, quote verified) [`CMakeLists.txt:12`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/CMakeLists.txt#L12): CMakeLists.txt declares EXTENSION_DEPENDS of SlicerElastix and SlicerNetstim, but the catalog entry lists no build_dependencies. The index build may not see the dependencies, and the policy requires them to match.
  ```
  set(EXTENSION_DEPENDS "SlicerElastix;SlicerNetstim") # AtlasMapping uses Elastix, DBS workflow integrates with Netstim/Lead-OR
  ```
  Suggestion: Align the catalog entry's build_dependencies with EXTENSION_DEPENDS (and add SlicerPyTorch once the torch install is moved to PyTorchUtils).

### D5. Loop over an integer raises TypeError
partial; category soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`DBS_STN/Lib/mer_support.py:347`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/DBS_STN/Lib/mer_support.py#L347): shape[0] is an int, so this raises TypeError whenever the function is called; the function also mixes numpy and torch operands. It is dead/broken code in the shift-prediction path.
  ```
  for i in points_to_compute.shape[0]:
  ```
  Suggestion: Use range(points_to_compute.shape[0]) and convert operands consistently.
- **haiku** (major, high confidence, quote verified) [`DBS_STN/Lib/mer_support.py:347`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/DBS_STN/Lib/mer_support.py#L347): compute_distances_to_mesh iterates over points_to_compute.shape[0], which is an int. The first call raises TypeError, so the function cannot run. It is a visible correctness bug.
  ```
  for i in points_to_compute.shape[0]:
  ```
  Suggestion: Use range(points_to_compute.shape[0]) or remove the function if it is unused.

### D6. Model weights downloaded without integrity check and loaded with torch.load
single; category safety; raised by haiku
- **haiku** (major, high confidence, quote verified) [`STNSegmenter/STNSegmenter.py:160`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L160): shp_pred.pt is downloaded from a GitHub release with no checksum, then passed to torch.load, which unpickles arbitrary code. Anyone able to replace the release asset, or a man-in-the-middle, can execute code on the user's machine. A corrupt download also triggers a re-download and a second load. The first load also runs with no weights_only restriction.
  ```
  if not file_path.exists() or _looks_like_git_lfs_pointer(file_path):
          _download_weights()
  
      try:
          return torch.load(str(file_path), map_location=torch.device('cpu'))
  ```
  Suggestion: Verify a pinned SHA256 for each downloaded or bundled .pt file before loading. Load with torch.load(..., weights_only=True) or use safetensors. Document the source of the weights.

### D7. Multiple packages installed at import without asking the user
single; category environment; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`STNSegmenter/STNSegmenter.py:19`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L19): dbs-pure-lib, antspyx, intensity-normalization, scikit-learn and pandas are all installed silently at import (STNSegmenter.py:22,52,75,122,186-189; DBSShiftPrediction.py:9,37,46; segm_lib/visualisiation.py:51). These installs modify the shared Slicer Python for all users and can pull transitive dependencies that conflict with Slicer's bundled numpy/scipy.
  ```
  try:
      from dbs_image_utils.mask import SubcorticalMask
  except ImportError:
      slicer.util.pip_install('dbs-pure-lib')
      from dbs_image_utils.mask import SubcorticalMask
  ```
  Suggestion: Move dependency installation behind an explicit user prompt (slicer.util.pip_install after confirmation) or declare them as extension dependencies.

### D8. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku concern


## Findings all reviewers agree on

### Automatic package installation at import time
blocking; environment; raised by deepseek, flash-lite, haiku
- **deepseek** (major, medium confidence, quote verified, other lines) [`STNSegmenter/STNSegmenter.py:19`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L19): Weights are auto-downloaded from GitHub releases (line 730) and then unpickled with torch.load; on torch versions before 2.6 this can execute arbitrary code from the file. The same pattern is at lines 178 and DBSShiftPrediction.py:1761. Files are also loaded from the module resource directory, which is writable by the user.
  ```
  try:
          return torch.load(str(file_path), map_location=torch.device('cpu'))
  ```
  Suggestion: Pass weights_only=True (or load a safetensors file) and verify a published SHA256 of the downloaded weights.
- **flash-lite** (blocking, high confidence, quote verified) [`STNSegmenter/STNSegmenter.py:22`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L22): Multiple modules automatically run `slicer.util.pip_install(...)` at import time (top-level module loading / when modules are accessed), installing third-party packages without user consent. Slicer extensions must not perform automatic package installations at import time or startup.
  ```
  slicer.util.pip_install('dbs-pure-lib')
  ```
  Suggestion: Remove automatic pip installation of external packages at module import time.
- **haiku** (major, high confidence, quote verified, other lines) [`STNSegmenter/STNSegmenter.py:19`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L19): STNSegmenter.py installs packages when the module is loaded (dbs-pure-lib, antspyx, a git+https ANTsTorch install, intensity-normalization). Each install runs without a version pin or user confirmation, and the ANTsTorch install follows a moving default branch. Module import can therefore change the shared Python environment.
  ```
  try:
      import ants
      import antstorch
  except ImportError:
      _install_antspyx()
      slicer.util.pip_install('git+https://github.com/ANTsX/ANTsTorch.git')
  ```
  Suggestion: Move installs behind an explicit user action in the widget, pin versions, and avoid installing from a VCS URL. Install only on first use of the feature, not at import.

### PyTorch installed with pip at module import instead of via PyTorchUtils
blocking; environment; raised by deepseek, flash-lite, haiku
- **deepseek** (blocking, high confidence, quote verified, other lines) [`STNSegmenter/STNSegmenter.py:19`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L19): Scripted modules are imported when Slicer loads the extension, so this runs for every user who installs DBSCoalignment, even if they never open STNSegmenter. It pulls a PyPI torch build (CPU/CUDA mismatch, large download, no user confirmation) into Slicer's shared Python and can break other extensions; the same pattern is at DBSShiftPrediction.py:17-25 and STNSegmenter.py:1745-1750 (torchio).
  ```
  try:
      import torch
  except ImportError:
      slicer.util.pip_install('torch')
      import torch
  ```
  Suggestion: Remove the import-time installs and use the Slicer PyTorch extension's PyTorchUtils (add PyTorch to build_dependencies and EXTENSION_DEPENDS), prompting the user before any download.
- **flash-lite** (blocking, high confidence, quote verified) [`STNSegmenter/STNSegmenter.py:70`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L70): The extension installs PyTorch directly via `slicer.util.pip_install('torch')` inside module files (`STNSegmenter/STNSegmenter.py` and `DBS_STN/DBSShiftPrediction.py`) rather than declaring `PyTorchUtils` in `EXTENSION_DEPENDS` and using it correctly according to Slicer guidelines. This can disrupt Slicer's shared Python environment and cause package version conflicts.
  ```
  slicer.util.pip_install('torch')
  ```
  Suggestion: Remove direct `pip_install('torch')` calls and declare PyTorchUtils as an extension dependency in CMakeLists.txt and the catalog entry.
- **haiku** (blocking, high confidence, quote verified, other lines) [`DBS_STN/DBSShiftPrediction.py:6`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/DBS_STN/DBSShiftPrediction.py#L6): Torch is installed with slicer.util.pip_install('torch') at import time and in logic construction. This bypasses SlicerPyTorch and can change or conflict with the Python environment that Slicer and other extensions use, including for users who never open the module. The policy requires torch to come through PyTorchUtils.
  ```
  try:
      import torch
      from torch import nn
      from torch.nn import functional as F
  except ImportError:
      slicer.util.pip_install('torch')
  ```
  Suggestion: Add SlicerPyTorch to EXTENSION_DEPENDS and build_dependencies, and use the PyTorchUtils install logic instead of pip_install('torch'). Remove the same call from STNSegmenter/STNSegmenter.py line 70 and line 189.


## Findings from some reviewers

### Bundled model weights and MNI template have no documented license or provenance
minor; license; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`LICENSE.txt:1`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/LICENSE.txt#L1): The extension code is MIT, but the repository ships trained networks (transformer_classifier_test.pt, shape_pcas.pkl, mer_pca_mesh.pkl, 3.obj) and MNI152-derived templates whose origin, training data and redistribution terms are not stated; MNI templates carry their own attribution terms. Users cannot tell what they may redistribute.
  ```
  MIT License
  
  Copyright (c) 2025 Czech Technical University in Prague, Faculty of Electrical Engineering, Department of Computer Science and Engineering
  ```
  Suggestion: Add a NOTICE/Resources README stating the source, license and training data of each bundled model and template.
- **haiku** (minor, medium confidence, quote verified) [`LICENSE.txt:1`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/LICENSE.txt#L1): The repository license covers the code only. The pretrained .pt/.pkl networks and the MNI152 template are bundled and downloaded without stated terms or attribution. Distribution is probably permitted, but the terms are not documented.
  ```
  MIT License
  
  Copyright (c) 2025 Czech Technical University in Prague
  ```
  Suggestion: Document the source and license of the model weights and the MNI template, and include attribution where required.

### Module metadata and help text are still template placeholders
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`STNSegmenter/STNSegmenter.py:240`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L240): Contributors, help text and acknowledgement are the Slicer template defaults ('This is an example of scripted loadable module bundled in an extension'), so users get no in-application guidance for a neurosurgical workflow; the same applies to AtlasMapping.py:238-248, LabelConversion.py:49 and TextToMarkups.py:61.
  ```
  self.parent.contributors = [
              "John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
  ```
  Suggestion: Fill in real contributors, help text and acknowledgements, and add a research-use disclaimer.

### Module test calls process() with the wrong signature
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`AtlasMapping/AtlasMapping.py:1178`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/AtlasMapping/AtlasMapping.py#L1178): AtlasMappingLogic.process is defined as process(self, inputMesh, inputBaseTransform) (line 866-868), so the bundled test raises TypeError immediately; the test also treats a model node as a volume (inputMesh.GetImageData()). The test therefore cannot validate anything.
  ```
  logic.process(inputMesh, outputVolume, threshold, True)
  ```
  Suggestion: Rewrite the test against the real signature and a real input mesh/transform, or remove it.
- **haiku** (minor, high confidence, quote verified) [`AtlasMapping/AtlasMapping.py:1178`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/AtlasMapping/AtlasMapping.py#L1178): The AtlasMapping test calls logic.process with four arguments and checks volume scalar ranges, but process() takes (inputMesh, inputBaseTransform) and returns a transform. The test would fail if enabled, and it is not part of the build test list.
  ```
  logic.process(inputMesh, outputVolume, threshold, True)
  ```
  Suggestion: Rewrite the test for the current process() API, or remove the stale test code.

### No clinical or research-use disclaimer and no tests
minor; utility; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`README.md:1`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/README.md#L1): The software supports surgical electrode placement, but the README and CMake metadata contain no statement that results are research-only and not for clinical decisions. Test suites are commented out (e.g., DBS_STN/Testing/Python/CMakeLists.txt), so there is no regression coverage.
  ```
  Project: SlicerDBSCoalignment
  
  This project focuses on improving the precision of electrode placement in Deep Brain Stimulation (DBS) surgery
  ```
  Suggestion: Add a research-use disclaimer, document model provenance and validation for the networks, and enable at least a smoke test.

### Resource directories present in the repo are not installed by CMake
minor; packaging; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`DBS_STN/CMakeLists.txt:6`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/DBS_STN/CMakeLists.txt#L6): DBS_STN/Resources/MNI/MNI152_T1_1mm_subbr_mask.nii.gz, Resources/elastix/*.txt, Resources/Smk_utils/*.smk and Resources/py/bet.py exist in the repository but are not listed in MODULE_PYTHON_RESOURCES, so they will not be present in an installed extension. Whether the runtime code needs them was not verified.
  ```
  set(MODULE_PYTHON_SCRIPTS
      ${MODULE_NAME}.py
  ```
  Suggestion: Add the resources actually used at runtime to MODULE_PYTHON_RESOURCES, or delete the unused ones.

### Shell-like command built by string formatting and shlex.split
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote partly verified) [`STNSegmenter/segm_lib/slicer_preprocessing.py:28`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/segm_lib/slicer_preprocessing.py#L28): register_t2_to_t1 and _run_cli_wm_segmentation build commands by f-string and shlex.split. Paths with spaces or quotes break, and an embedded quote can alter the Python command passed to 'python -c'. Inputs are user-selected paths, so this is a robustness issue more than a remote attack, but it is still fragile.
  ```
  cmd += f"t1_image = ants.image_read(\"{t1}\");"
      ...
      subprocess.check_output(cmd,env={})
  ```
  Suggestion: Pass arguments as a list without a shell, and call the Python APIs directly rather than building python -c strings.

### Temporary working directories are intentionally never cleaned up
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AtlasMapping/AtlasMapping.py:1113`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/AtlasMapping/AtlasMapping.py#L1113): Every AtlasMapping run leaves a TemporaryDirectory (line 882) with NIfTI volumes, distance maps and elastix logs on disk; the object is garbage collected without cleanup, so repeated use accumulates hundreds of MB in the user's temp folder.
  ```
  # Keep temporary output available for troubleshooting.
              # Set cleanup() here once diagnostics are no longer needed.
              pass
  ```
  Suggestion: Call working_dir_obj.cleanup() in the finally block, optionally keeping the log text in the error message only.

### WM segmentation uses Python `or` on numpy arrays
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`STNSegmenter/segm_lib/slicer_preprocessing.py:53`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/segm_lib/slicer_preprocessing.py#L53): `si == 3` is an array, so `or` raises 'truth value of an array with more than one element is ambiguous' and the WM mask step fails. The same bug is in DBS_STN/Lib/slicer_preprocessing.py:33. Additionally `subprocess.check_output(cmd, env={})` at line 38 runs the child with an empty environment, which will typically fail.
  ```
  si = res['segmentation_image']
      wm = (si == 3) or (si == 4) or (si == 5)
  ```
  Suggestion: Use np.isin(si, (3, 4, 5)) and pass a proper environment to the subprocess.

### nibabel installed on demand inside a helper function
minor; environment; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AtlasMapping/AtlasMapping.py:86`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/AtlasMapping/AtlasMapping.py#L86): A silent pip install into Slicer's shared environment triggered by a helper call, without user confirmation; nibabel is also installed at import in STNSegmenter.py:187.
  ```
  try:
          import nibabel as nib
  except ImportError:
          slicer.util.pip_install("nibabel")
          import nibabel as nib
  ```
  Suggestion: Declare nibabel as a dependency and install it once, with user confirmation.

### pickle.load of bundled .pkl resources
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`STNSegmenter/STNSegmenter.py:104`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/STNSegmenter.py#L104): Model/histogram pickles are deserialized with pickle (also DBSShiftPrediction.py:1038). The files ship with the extension so the risk is limited, but pickle can execute code if a resource file is replaced, and the provenance of these pickles is undocumented.
  ```
  def _read_pickle(filename):
      f = open(filename, 'rb')
      res = pickle.load(f)
  ```
  Suggestion: Prefer a non-executable format (npz/json) or document and checksum the pickle files.
- **haiku** (minor, medium confidence, quote verified) [`DBS_STN/DBSShiftPrediction.py:1036`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/DBS_STN/DBSShiftPrediction.py#L1036): Several .pkl files are read with pickle.load (DBS_STN/DBSShiftPrediction.py line 1036-1040 and STNSegmenter line 104-108). The files ship inside the extension, so the risk is limited to tampering with the package or the user's copy. The same code path is still unsafe in principle.
  ```
  def _read_pickle(filename):
      f = open(filename, 'rb')
      res = pickle.load(f)
  ```
  Suggestion: Convert the bundled pickles to a non-executable format (JSON/NPZ) or document their provenance and hashes.

### No automated tests are registered
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`STNSegmenter/Testing/Python/CMakeLists.txt:2`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/STNSegmenter/Testing/Python/CMakeLists.txt#L2): All five Testing/Python/CMakeLists.txt files have the test registration commented out, so the extension's CI provides no functional coverage; combined with the broken AtlasMapping test this means nothing is verified automatically.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Register at least a smoke test per module.

### Personal local path committed in AGENTS.md
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`AGENTS.md:7`](https://github.com/IVarha/SlicerDBSCoalignment/blob/d1d9b946b46f05f6f40fd53305c84ac9e0e7c240/AGENTS.md#L7): A developer's Windows user path is committed in the repository. It is not a credential and contains no instructions to reviewers, but it is environment-specific clutter that should not ship.
  ```
  # SLICER INSTALLATION PATH
  C:\Users\varhai\AppData\Local\slicer.org\3D Slicer 5.10.0
  ```
  Suggestion: Remove the machine-specific path from AGENTS.md.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The extension is a substantial DBS research toolkit with an MIT license and a usable README, but it fails the environment and packaging admission requirements. Several modules install packages into Slicer's shared Python at import time — including `pip_install('torch')` (not via PyTorchUtils), `git+https://github.com/ANTsX/ANTsTorch.git`, and an `antspyx` wheel downloaded from an unverified Box.com shared link with no checksum — so users who never open the modules are affected. The CMake files also list resource files that are absent from the inspected checkout, and `EXTENSION_DEPENDS` does not match the catalog entry's empty `build_dependencies`. Soundness has ordinary bugs (broken test, numpy `or` misuse).
Not checked: The catalog entry pins scm_revision 'master'; I inspected the checkout provided to me, not a resolved commit hash, so I cannot confirm it equals d1d9b946b46f05f6f40fd53305c84ac9e0e7c240.; The automated scan hint lists large files (MNI152_T1_1mm_brain.nii.gz, cent_pred.pt, shp_pred.pt, net_transformer.pt) that my directory listings and read_file calls show as absent from this checkout; the discrepancy may mean the hint was produced from a different revision. The packaging finding is b; I could not read the binary model weights (.pt/.pkl), the MNI templates, the .ui files, the elastix parameter files or the .smk files, so their content, provenance and license are unverified.; I did not read the full bodies of DBSShiftPrediction.py (2407 lines), STNSegmenter.py (1191 lines), LabelConversion.py, TextToMarkups.py or segm_lib/visualisiation.py; findings there are based on the sections and searches I did inspect.; I could not verify whether the extension actually builds or loads in Slicer, whether the referenced GitHub release assets (shp_pred.pt, left_share.mrb) exist, or whether the Box.com wheel link is live.; I did not audit the third-party packages installed at runtime (dbs-pure-lib, antspyx, ANTsTorch, intensity-normalization) for their own licenses or transitive dependency pins.
Questions for the author: Why are torch, antspyx, ANTsTorch, dbs-pure-lib and intensity-normalization installed at module import rather than through the Slicer PyTorch extension and an explicit user prompt?; Can the antspyx wheel be served from PyPI or a hash-verified release asset instead of an anonymous Box.com shared link?; Do Resources/nets/net_transformer.pt, Resources/nets/cent_pred.pt and Resources/MNI/MNI152_T1_1mm_brain.nii.gz exist at the catalogued revision? They are listed in CMakeLists.txt but absent from the checkout I inspected.; Should the catalog entry's build_dependencies list SlicerElastix and SlicerNetstim to match EXTENSION_DEPENDS?; What are the license and training-data provenance of the bundled .pt/.pkl model weights and the MNI152 templates?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): needs fixes
The DBSCoalignment extension implements several useful scripted modules for deep brain stimulation (DBS) analysis and coalignment. However, it violates core Slicer extension policies by installing PyTorch directly via pip (`slicer.util.pip_install('torch')`) instead of utilizing `PyTorchUtils`, and by executing multiple automatic `pip_install` commands at module import time. These issues must be resolved before the extension can be accepted into the extensions catalog.
Not checked: Full execution of trained deep learning models and external CLI tools (elastix/transformix) in a running Slicer instance.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
Reviewed the catalog entry, CMake files, README, and the main Python modules' install/download/deserialization paths. The entry is mechanically simple, but the code installs torch and other packages via pip at import time, runs unpinned GitHub and third-party-host wheel installs, downloads model weights without checksums and loads them with torch.load, and declares runtime dependencies in EXTENSION_DEPENDS that the catalog does not list. Several soundness bugs are visible (a broken test call and a non-iterable loop). No malicious behavior was seen. Needs fixes before admission.
Not checked: Binary files (.pt, .pkl, .nii.gz, .mrb) were not readable, so their contents, checksums and sizes were not verified.; The exact revision 'master' was not resolved; the source at commit d1d9b946 was not fetched, and no CI build or Slicer run was performed.; Whether every file listed in CMake (e.g., nets/mer_pca_mesh.pkl, transformer_classifier_test.pt) exists in the repository was not checked.; STNSegmenter/STNSegmenter.py beyond lines 1-230 and 690-740, and most of DBSShiftPrediction.py, were not read in full; no full dataflow or network-transmission audit was done.; Upstream dependencies (dbs-pure-lib, antstorch, brainextractor, intensity_normalization) were not inspected.


# AI review: PETDenoise

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/4burakfe/SlicerPETDenoise at commit `40a63cbfba7875615de0f75e3fd936a4b1ba95b6`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:35:12Z; cost $0.05

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | ok |
| environment | minor | ok | minor |
| packaging | minor | ok | minor |
| license | ok | ok | minor |
| soundness | minor | ok | minor |
| utility | ok | ok | minor |
| **overall** | minor issues | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: SlicerPETDenoise provides two Slicer modules for PET/CT research: "Belenos - PET Denoise" runs UNET/SwinUNETR denoising models (downloaded from the author's GitHub releases) on PET volumes, and "Belenos - Volume Comparator" computes MSE/MAE/SSIM/PSNR/edge-loss between two volumes. It targets nuclear-medicine researchers, not clinical use.
- **flash-lite**: SlicerPETDenoise provides two 3D Slicer modules for research use in nuclear medicine: PETDenoise (AI-based PET denoising using UNET, SwinUNETR, and SwinUNETR+GCFN with MONAI and PyTorch) and VolumeComparator (numerical comparison and loss metrics for volumes).
- **haiku**: Belenos PET Denoise and Volume Comparator, two scripted Slicer modules under the Nuclear Medicine category. They run PyTorch/MONAI denoising networks (UNET/SwinUNETR) on PET volumes and compute image-similarity metrics between two volumes, for research use.

## Findings from some reviewers

### Compiled Python cache committed to the repository
minor; packaging; raised by deepseek, haiku; **quote not found in source**
- **deepseek** (minor, high confidence, quote no quote) [`PETDenoise/__pycache__/PETDenoise.cpython-313.pyc:1`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/__pycache__/PETDenoise.cpython-313.pyc#L1): A 93 KB CPython 3.13 bytecode file is committed. It is not installed by CMake so it does not affect users at runtime, but it is a stale binary artifact that can drift from the source and should not be in the source repository.
  Suggestion: Remove PETDenoise/__pycache__ and add __pycache__/ and *.pyc to .gitignore.
- **haiku** (minor, high confidence, quote quote not found) [`PETDenoise/__pycache__/PETDenoise.cpython-313.pyc:1`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/__pycache__/PETDenoise.cpython-313.pyc#L1): PETDenoise/__pycache__/PETDenoise.cpython-313.pyc (93 KB) is a build artifact from a developer machine. It is not needed for the extension, may not match the source, and should not be in the source tree.
  ```
  PETDenoise/__pycache__/PETDenoise.cpython-313.pyc  (93384 bytes, binary)
  ```
  Suggestion: Remove __pycache__ from the repository and add it to .gitignore.

### Denoising and metric computation run on the GUI thread
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`PETDenoise/PETDenoise.py:440`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/PETDenoise.py#L440): The whole sliding-window inference (PETDenoise.py lines 1184-1266) and the metric computation (VolumeComparator.py lines 406-464) run in the button-click slot; progress is only shown by pumping the Qt event loop with processEvents. During a long run the UI stays re-entrant, so scene changes or module switches can occur mid-inference, and the application appears frozen between log messages.
  ```
  def log(self, text):
          self.outputTextBox.append(text)
          slicer.app.processEvents()  # show progress while the run is going
  ```
  Suggestion: Move the heavy work to a slicer.util.ProgressDialog / CLI-style worker thread (or a qSlicerCLI-like background task) and keep processEvents out of the compute path.

### Model download silently overwrites a same-named file of different size
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`PETDenoise/PETDenoise.py:993`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/PETDenoise.py#L993): isCompleteModelFile returns False for an existing file of a different size, so the download path is taken and os.replace() overwrites the file in the user's model folder. A user-supplied model with the same name, or a partially edited file, is replaced without confirmation. The data loss is limited to model files, but it is unannounced.
  ```
  os.replace(partPath, destination)
  ```
  Suggestion: Ask for confirmation before replacing an existing file, or download into a separate folder and report the conflict.

### Model folder path is written into the extension installation directory
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`PETDenoise/PETDenoise.py:648`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/PETDenoise.py#L648): saveModelFolderPath writes model_config.ini next to the module file. In an installed extension that directory is typically read-only (and shared by all users), so the write fails and is only logged at info level; the setting is still kept in QSettings, so functionality is preserved, but writing into the program installation is not a user-chosen location.
  ```
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_config.ini")
  ```
  Suggestion: Keep the folder only in QSettings, or write the compatibility ini into the user settings/cache directory instead of the module directory.

### Module icon and banner PNGs are not installed by CMake
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`PETDenoise/CMakeLists.txt:9`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/CMakeLists.txt#L9): PETDenoise.py lines 282-284 and 376-381 (and VolumeComparator.py lines 32-34, 82-87) load Resources/logo.png and Resources/banner.png, but only Icons/*.png and UI/*.ui are listed as module resources, so those files are not installed with the extension. The os.path.exists guards mean no crash, but users of the installed extension get no module icon and no banner, and the 9 MB banner files are dead weight in the repository.
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/Icons/${MODULE_NAME}.png
    Resources/UI/${MODULE_NAME}.ui
    )
  ```
  Suggestion: Add Resources/logo.png (and, if wanted, Resources/banner.png) to MODULE_PYTHON_RESOURCES in both module CMakeLists.txt files, or drop the unused images.

### Registered ctest has no unittest class to run
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`PETDenoise/CMakeLists.txt:27`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/CMakeLists.txt#L27): Both module CMakeLists.txt register a Python unittest on the module script, but a search for unittest classes in PETDenoise.py and VolumeComparator.py found none, and Testing/Python/CMakeLists.txt only contains a commented-out line. The generated test therefore exercises nothing, so the extension ships without any automated verification of the denoising or metric code.
  ```
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)
  ```
  Suggestion: Add a real test class (e.g. exercising parseSidecar/parseSequence/validateParameters and the metric formulas on synthetic arrays) or remove the test registration.

### Release asset names from GitHub are used as file paths without sanitization
minor; safety; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified, other lines) [`PETDenoise/PETDenoise.py:817`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/PETDenoise.py#L817): Asset names come from the GitHub release JSON (parseReleaseAssets, lines 207-221) and are joined directly onto the model folder, both for the .pth (line 1021) and the sidecar (line 1036). An asset named e.g. '../../x.pth' would make the download write outside the chosen model folder. The repository is author-controlled, so the practical risk is low, but the path is not validated.
  ```
  name = entry["name"]
          destination = os.path.join(folder, name)
  ```
  Suggestion: Reject asset names containing path separators or '..' (e.g. require os.path.basename(name) == name) before using them as file names.

### Terms for the downloadable pretrained model weights are not stated
minor; license; raised by deepseek, haiku
- **deepseek** (info, medium confidence, quote verified) [`LICENSE:5`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/LICENSE#L5): The MIT text covers the extension source; the .pth weights downloaded from the repository's GitHub releases are not explicitly covered by a stated license, and the README does not say under which terms the models may be used or redistributed. This is a clarity gap rather than a prohibition.
  ```
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "SlicerPETDenoise"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  ```
  Suggestion: State in the README (and ideally in the release notes) that the published model weights are released under the same MIT terms or another named license.
- **haiku** (minor, medium confidence, quote verified) [`LICENSE:1`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/LICENSE#L1): The module downloads .pth weights from the GitHub release 'Models' and 'SuperRes_Models'. The repository MIT license covers the code only. Users and redistributors have no stated terms for the weights, so the permission to distribute or use them for any purpose is unclear.
  ```
  MIT License
  
  Copyright (c) 2025 Burak Demir
  ```
  Suggestion: State the license or terms for the published models in the release notes or README.

### Two 9 MB banner images committed
minor; packaging; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`README.md:10`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/README.md#L10): The scan reports PETDenoise/Resources/banner.png and VolumeComparator/Resources/banner.png at ~9 MB each (not readable here). Large binaries in the source repository slow clones and the extension build, and they are not even installed (see the resource finding).
  ```
  ![Screenshot](PETDenoise/Resources/banner.png)
  ```
  Suggestion: Downscale the banners to a few hundred KB, or reference the images from the README only.

### Unpinned monai install and exact einops pin in Slicer's shared environment
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`PETDenoise/PETDenoise.py:608`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/PETDenoise.py#L608): After user confirmation, `slicer.util.pip_install("monai")` (also VolumeComparator.py line 309) resolves monai's dependencies inside Slicer's Python, which can upgrade Slicer-bundled numpy, while `einops==0.6.1` is an exact pin that can conflict with other extensions needing a newer einops. Installation is at least user-confirmed and not at import, so this is not a blocking environment change.
  ```
  for moduleName, requirement in (("monai", "monai"), ("einops", EINOPS_REQUIREMENT)):
  ```
  Suggestion: Pin a tested monai version (e.g. monai==1.3.x) and relax the einops pin to a minimum version, and mention the tested versions in the README.
- **haiku** (minor, medium confidence, quote verified) [`PETDenoise/PETDenoise.py:25`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/PETDenoise.py#L25): When the user accepts the install prompt, the module runs pip install einops==0.6.1 into Slicer's shared environment. This can downgrade einops for other extensions or conflict with newer packages that need a later version. The prompt does not mention the version downgrade.
  ```
  EINOPS_REQUIREMENT = "einops==0.6.1"
  ```
  Suggestion: Use a lower-bound requirement (for example einops>=0.6.1) or document the pin and its reason in the prompt; avoid exact pins in shared environments.

### scm_revision points to a moving branch ('main')
minor; packaging; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`PETDenoise.json:8`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise.json#L8): The catalog entry pins no commit, so the index builds whatever is on main at build time. The reviewed source (commit 40a63cbf...) can change without any review. This is not a security defect, but it weakens reproducibility and the basis of this review.
  ```
  "scm_revision": "main",
  ```
  Suggestion: Pin scm_revision to the reviewed commit SHA, or accept that updates need a new review.

### torch.load fallback without weights_only for old PyTorch
minor; safety; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`PETDenoise/PETDenoise.py:1136`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/PETDenoise.py#L1136): On a PyTorch older than 1.13 the code silently falls back to a full pickle load of a user-supplied .pth file, which can execute arbitrary code. The PyTorch extension normally provides a recent build, so this path is unlikely, but it removes the protection exactly where a user-chosen model file is loaded.
  ```
  # weights_only: a .pth file cannot run arbitrary code when it is loaded
              state = torch.load(modelPath, map_location=device, weights_only=True)
          except TypeError:  # PyTorch < 1.13
              state = torch.load(modelPath, map_location=device)
  ```
  Suggestion: Drop the fallback and report that a newer PyTorch (from PyTorch Utils) is required, or keep weights_only and fail with a clear message on TypeError.

### Automatic GitHub API request when the download section is opened
info; safety; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`PETDenoise/PETDenoise.py:755`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/PETDenoise.py#L755): Expanding the 'Download Published Models' section contacts api.github.com (at most once per day) without a separate confirmation. Only the request itself (IP address, User-Agent '3DSlicer-PETDenoise') leaves the machine; no image data, identifiers or telemetry are sent, so this is informational.
  ```
  def onDownloadSectionCollapsed(self, collapsed):
          """Opening the section: check GitHub for new published models (at most once a day)."""
          if not collapsed:
              self.updatePublishedModelCatalog(force=False)
  ```
  Suggestion: Optionally mention in the README/tooltip that opening the section queries GitHub for the model list.
- **haiku** (info, high confidence, quote verified) [`PETDenoise/PETDenoise.py:757`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/PETDenoise.py#L757): Opening 'Download Published Models' sends an HTTP request to api.github.com (at most once a day) with a fixed User-Agent. No user data is sent, and the request is not a telemetry channel, but it is network access the user does not explicitly start.
  ```
  if not collapsed:
              self.updatePublishedModelCatalog(force=False)
  ```
  Suggestion: Mention the GitHub check in the documentation, or make it manual-only.

### Committed model_config.ini contains the author's local path
info; soundness; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`PETDenoise/model_config.ini:1`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/model_config.ini#L1): The committed ini holds a developer machine path. It is harmless to users (loadModelFolderPath only uses it if the directory exists) but it is a leftover development artifact and reveals the author's local layout.
  ```
  [ModelFolder]
  path = H:/SuperResPY/APPS/Models
  ```
  Suggestion: Remove model_config.ini from the repository and add it to .gitignore.

### No automated tests are active
info; utility; raised by haiku
- **haiku** (info, high confidence, quote verified) [`PETDenoise/Testing/Python/CMakeLists.txt:2`](https://github.com/4burakfe/SlicerPETDenoise/blob/40a63cbfba7875615de0f75e3fd936a4b1ba95b6/PETDenoise/Testing/Python/CMakeLists.txt#L2): The module Testing/Python CMake files only contain a commented-out test line, so the generic tests and the unit test are not registered. Changes to the parsing, metric, and sliding-window logic are not covered by automated checks.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add unit tests for parseSidecar, parseSequence, and mergePublishedModelCatalog, which are pure functions.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): minor issues
No malicious or concealed behavior found: no telemetry, no image upload, network use limited to GitHub release/API downloads with user-initiated buttons, size/SHA-256 verification, and `weights_only=True` model loading. MIT license present; catalog entry is consistent (EXTENSION_DEPENDS "PyTorch" matches build_dependencies). Remaining issues are non-blocking: logo/banner PNGs are not installed by CMake (icon/banner silently missing), a committed `__pycache__` .pyc and two 9 MB banners, no real unit tests despite registered ctests, unsanitized release asset names used as file paths, unpinned `pip_install("monai")`, and long inference on the GUI thread. Recommend merge with follow-ups.
Not checked: The exact source revision 40a63cbfba7875615de0f75e3fd936a4b1ba95b6 could not be verified; I reviewed the file snapshot provided for this repository, and the catalog entry points at the moving branch 'main'.; PETDenoise/Resources/banner.png and VolumeComparator/Resources/banner.png (~9 MB each) are binary and were not readable, so their content is unverified.; The GitHub release assets (model .pth weights, their SHA-256 digests and .txt sidecars) and the model weights' license were not accessible, so model provenance beyond the built-in checksums in PUBLISHED_MODELS could not be confirmed.; Whether `pip_install("monai")` resolves cleanly against the numpy/torch versions bundled with current Slicer releases was not tested.; CI/build results for the extension (catalog build, ctest) were not available.; The .ui files were only partially read (first 60 lines of PETDenoise/Resources/UI/PETDenoise.ui); they appear unused because both widgets are built in code.
Questions for the author: Under which license are the published .pth model weights released, and may they be redistributed?; Which monai and einops versions were the models and metrics validated with, and can those be pinned?; Would you add a real unittest class (parameter parsing, metric formulas) so the registered ctest actually tests something?; Can the logo/banner PNGs be added to MODULE_PYTHON_RESOURCES (or removed) and the committed __pycache__ .pyc dropped?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
🟢 Recommend merge. The extension is well-structured, follows Slicer conventions, handles dependencies cleanly via PyTorchUtils with user consent prompts for MONAI/einops, implements secure downloading and checksum validation for pretrained models, and uses safe deserialization practices.
Not checked: Pretrained model weights downloaded at runtime from GitHub releases (inspected code structure and hash checks).

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
I read the catalog entry, CMake files, both module scripts and the LICENSE. I found no malicious or concealed behaviour and no unsafe deserialization: model weights are loaded with weights_only=True, sidecar values are parsed with literal_eval, and downloads are checked by size and SHA-256. Remaining issues are minor: a floating scm_revision of "main", a committed __pycache__ .pyc, a einops pin, a model-folder overwrite path, and unstated model-weight licensing. Nothing is blocking. I could not run anything or inspect the pinned revision or the 9 MB banner files.
Not checked: The pinned revision is not verified: scm_revision is 'main', so I reviewed the code as provided in the review bundle, not a fixed commit.; PETDenoise/Resources/banner.png and VolumeComparator/Resources/banner.png (9 MB each) were not readable; the directory listing does not show them, and the code tolerates their absence.; The .ui files and icon PNGs were not read; they could hide widget wiring issues.; No code was executed. The behaviour of the GitHub release assets, their checksums, and the model weights was not inspected.; The PyTorch and MONAI version interactions (including the swinExtra img_size logic) were not validated against a running Slicer.; Whether Slicer's shared environment already has einops and whether the pin conflicts with other extensions could not be checked.


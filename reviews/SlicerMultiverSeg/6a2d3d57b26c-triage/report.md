# AI review: SlicerMultiverSeg

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/dalcalab/SlicerMultiverSeg at commit `6a2d3d57b26c0107274ae4926c0d8aa44afc8260`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T22:09:21Z; cost $0.03

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | concern |
| environment | concern | ok | concern |
| packaging | minor | ok | ok |
| license | concern | ok | unknown |
| soundness | concern | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: SlicerMultiverSeg adds a "MultiverSeg" Segment Editor effect that runs the MultiverSeg/ScribblePrompt in-context segmentation models on 2D slices or a slice range of a loaded volume, guided by user-drawn positive/negative scribbles and a small set of user-curated example slices ("tasks"). It targets researchers who want to segment new biomedical datasets from a few examples.
- **flash-lite**: SlicerMultiverSeg is a 3D Slicer extension that provides a Segment Editor effect utilizing the MultiverSeg model for rapid interactive biomedical image segmentation.
- **haiku**: Adds a MultiverSeg segmentation effect to Slicer's Segment Editor, letting users create task contexts from labeled 2D slices and run 2D or 3D predictions with the MultiverSeg and ScribblePrompt models. It is aimed at researchers doing interactive biomedical segmentation in Slicer.

## Disagreements (start here)

### D1. Model checkpoints downloaded from Dropbox without integrity verification, then unpickled
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py:11`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py#L11): The two .pt files are pickle-based checkpoints fetched from personal Dropbox shared links and then loaded by the multiverseg/scribbleprompt code (SegmentationLogic.py:97-101 points the model weights at these paths). Nothing verifies size or hash after download, so a replaced/expired link, a compromised Dropbox account, or a tampered file results in arbitrary code execution via torch.load in the user's Slicer. The download is at least user-confirmed (74MB / 16MB prompts).
  ```
      MULTIVERSEG_FILE_NAME = "MultiverSeg_v0_nf256_res128.pt"
      MULTIVERSEG_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/5sup9s5l9xkp28wbwkm9g/MultiverSeg_v0_nf256_res128.pt?rlkey=tquwxhezdgl2v8a2akvco5jim&st=1gnbqplc&dl=1"
  
      SCRIBBLEPROMPT_FILE_NAME = "ScribblePrompt_unet_v1_nf192_res128.pt"
      SCRIBBLEPROMPT_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/pnw88n05irnv5z1snlklr/ScribblePrompt_unet_v1_nf192_res128.pt?rlkey=dr8xvkf0wj2r082h1zzpcmz5o&dl=1"
  ```
  Suggestion: Host the weights at a stable, project-controlled URL and verify a pinned SHA-256 of each file before use; fail loudly on mismatch.
- **haiku** (major, medium confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py:12`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py#L12): The weights are downloaded from Dropbox share links with no SHA256 or other verification. The downloaded files are then loaded by the MultiverSeg and ScribblePrompt libraries, which normally use torch.load (pickle-based). A tampered or swapped file on the remote host, or a cached file in SampleData's cache, would run arbitrary code in the user's Slicer process when the model is initialized.
  ```
  MULTIVERSEG_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/5sup9s5l9xkp28wbwkm9g/MultiverSeg_v0_nf256_res128.pt
  ```
  Suggestion: Verify a pinned checksum after download and before copying into the checkpoint directory. Host the weights on a stable, versioned location. Load with weights_only=True where supported. Note in the docs that the weights are pickled.

### D2. No license information for the downloaded model weights or the pip-installed package
single; category license; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`README.md:84`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/README.md#L84): The extension itself is Apache-2.0 (LICENSE.txt), but the two checkpoints it downloads (MultiverSeg_v0, ScribblePrompt_unet_v1) and the `multiverseg` package it installs from git are third-party material whose terms are not stated anywhere in the repository. I could not access those sources, so I cannot confirm that redistribution/use of the weights is permitted; this is unverified rather than proven incompatible.
  ```
  - [MultiverSeg official implementation](https://github.com/halleewong/MultiverSeg)
  - [MultiverSeg Project Page](https://multiverseg.csail.mit.edu/)
  - [MultiverSeg Paper](https://arxiv.org/abs/2412.15058)
  ```
  Suggestion: State the license of each downloaded checkpoint and of the multiverseg package in the README, and confirm the weights may be redistributed/downloaded by users.

### D3. PyTorch extension used at runtime but not declared in EXTENSION_DEPENDS / build_dependencies
single; category environment; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`CMakeLists.txt:12`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/CMakeLists.txt#L12): InstallLogic.py:118 imports PyTorchUtils and InstallLogic.py:130-139 installs the PyTorch extension from the extension server on demand, but the catalog entry declares `"build_dependencies": []` and CMake declares `EXTENSION_DEPENDS "NA"`. The index therefore does not know the extension needs PyTorch, and users get a runtime prompt plus a required Slicer restart instead of having the dependency resolved at install time.
  ```
  set(EXTENSION_DEPENDS "NA")
  ```
  Suggestion: Add `PyTorch` to `EXTENSION_DEPENDS` in CMakeLists.txt and to `build_dependencies` in the catalog entry, keeping the runtime check as a fallback.

### D4. Task contexts and model checkpoints are stored inside the extension installation directory
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py:16`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py#L16): By default user-created tasks (PNG images and masks of the user's data) are written to `<extension>/MultiverSeg/Context` and the 90MB of checkpoints to `<extension>/MultiverSeg/Resources/Checkpoints` (InstallLogic.py:10). On macOS (/Applications) and Windows (Program Files) or a system-wide Linux install these paths are not writable, so task creation and model download fail; on any install the data is silently lost when the extension is updated or reinstalled. The user's own image data is also stored outside any user-chosen folder.
  ```
          self.contextRootPath = pathlib.Path(__file__).parent.joinpath("../Context").resolve()
  ```
  Suggestion: Default to a per-user writable location (e.g. `slicer.util.getUserResourceDirectory()` or `qt.QStandardPaths`), keeping the extension directory read-only.
- **haiku** (minor, medium confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py:154`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py#L154): The default context root is resolved relative to the module file, so user-created tasks and examples are written inside the extension install tree. Uninstalling or upgrading the extension can silently destroy them. Separately, deleteCurrentTask passes activeContext (which may be None) to joinpath and calls rmtree without a check.
  ```
  def deleteCurrentTask(self):
          import shutil
          shutil.rmtree(self.contextRootPath.joinpath(self.activeContext))
  ```
  Suggestion: Store context data in a user-data location (such as the Slicer application data directory). Add an assert or guard for activeContext being None before calling rmtree.

### D5. Unpinned third-party git repository pip-installed into Slicer's Python environment
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py:159`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py#L159): On first Initialize the user is asked to confirm, then pip installs the current HEAD of a third-party GitHub repository into Slicer's shared Python environment. There is no commit pin, so any future commit (or compromise of that account) executes arbitrary code in every user's Slicer at install time, and the package's own declared requirements can pull torch from PyPI or upgrade/downgrade numpy/scipy/torchvision that Slicer bundles. I could not inspect that repository's setup.py, so the exact dependency impact is unverified.
  ```
      def installMultiverSeg(cls):
          slicer.util.pip_install("git+https://github.com/halleewong/MultiverSeg.git")
  ```
  Suggestion: Pin an exact commit (`git+https://github.com/halleewong/MultiverSeg.git@<sha>`) and install with `--no-deps`, installing only the specific dependencies that are known to be safe (torch/torchvision via PyTorchUtils).
- **haiku** (major, high confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py:160`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py#L160): installMultiverSeg pip-installs whatever HEAD of a third-party GitHub repo is current at install time. There is no commit pin or hash, so the code run in users' Slicer environments can change without review. The package's own dependencies are not shown, and if they pull torch or other bundled packages from PyPI, they would bypass the PyTorch extension and could change Slicer's shared environment for all users.
  ```
  slicer.util.pip_install("git+https://github.com/halleewong/MultiverSeg.git")
  ```
  Suggestion: Pin to a specific release or commit (and ideally a hash) and document the transitive dependencies. Confirm that the package does not install torch or other Slicer-bundled packages, or constrain them.

### D6. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D7. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D8. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku unknown

### D9. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### 3D prediction runs on the GUI thread and leaves the slice view moved
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/SegmentationLogic.py:293`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/SegmentationLogic.py#L293): `predict3d` is connected directly to a button click (SegmentEditorEffect.py:165) and loops over every slice in the range on the main thread, calling `slicer.app.processEvents()`; for a large volume this keeps the UI busy for a long time. It also permanently changes the slice offset of the user's view and never restores it, and there is no try/except around `predict`/`predict3d`, so exceptions such as the `ValueError` raised by `computeSliceAxis` for oblique views (SegmentationLogic.py:359) only appear in the Python console.
  ```
              sliceLogic.SetSliceOffset(sliceOffset)
  ```
  Suggestion: Wrap the prediction entry points in try/except with `slicer.util.errorDisplay`, restore the original slice offset afterwards, and consider a CLI/worker thread for the 3D loop.

### Adding a context example changes the user's segment display visibility
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/SegmentEditorEffect.py:321`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/SegmentEditorEffect.py#L321): `addImageDialog` hides all segments and shows only the selected one, then at line 378 restores `SetAllSegmentsVisibility(True)` — i.e. it does not restore the user's previous per-segment visibility, and if the dialog is closed abnormally the segmentation stays mostly hidden. This silently alters the user's scene display state.
  ```
              displayNode.SetAllSegmentsVisibility(False)
              displayNode.SetSegmentVisibility(segmentID, True)
  ```
  Suggestion: Save and restore the per-segment visibility states instead of forcing all-visible.

### Catalog entry tracks a moving branch rather than a reviewed revision
minor; packaging; raised by haiku; **quote not found in source**
- **haiku** (minor, high confidence, quote file not found) [`SlicerMultiverSeg.json:1`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/SlicerMultiverSeg.json#L1): scm_revision is "main", so the index will build whatever is at the branch tip. The source reviewed here is at commit 6a2d3d5, and later changes are not covered by this review.
  ```
  "scm_revision": "main",
  ```
  Suggestion: Pin scm_revision to a reviewed commit or release tag, and update it when the code changes.

### Dependency install failures are reported as success
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified, other lines) [`MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py:124`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py#L124): installMultiverSegIfNeeded returns True after calling installMultiverSeg without checking that the import now works. A failed pip install then surfaces later as an obscure ImportError from initModel, not as a clear message.
  ```
  if ret:
                  cls.installMultiverSeg()
                  return True
  ```
  Suggestion: After the install, try the import again and return False with a visible error if it fails.

### Division by zero when normalising a constant slice or volume
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/SegmentationLogic.py:395`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/SegmentationLogic.py#L395): The same pattern appears in `preprocessVolume` (lines 422-424). For a uniform slice (e.g. air-only slice, or a constant-valued volume) `torch.max(result)` is 0 after the subtraction, producing NaN/Inf inputs and a meaningless prediction instead of a clear message.
  ```
          if not isSegmentation:
              result -= torch.min(result)
              result /= torch.max(result)
  ```
  Suggestion: Guard with `if torch.max(result) > 0:` or clamp the denominator.

### Failed or cancelled checkpoint download is silent and leaves the progress dialog open
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py:69`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py#L69): If the download does not reach 100% (network error, server error), no file is copied, no exception is raised and the progress window is never closed; `downloadCheckpointsIfNeeded` then returns False and `initModel` (SegmentationLogic.py:88-90) returns False, so `onInit` simply returns and the user sees nothing. `slicer.progressWindow` is also set as an attribute on the global `slicer` module, which is a process-wide side effect.
  ```
          fileDest = sampleDataLogic.downloadFileIntoCache(modelURI, modelName)
  
          if sampleDataLogic.downloadPercent and sampleDataLogic.downloadPercent == 100:
              shutil.copyfile(fileDest, modelPath)
              slicer.progressWindow.close()
  ```
  Suggestion: Raise/report an error when the download does not complete, always close the progress dialog in a finally block, and keep the progress window as an instance attribute.
- **haiku** (minor, high confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py:71`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/InstallLogic.py#L71): _downloadModel copies the file only if downloadPercent == 100, but the caller returns True regardless. If the download stops short, initModel continues and fails when MultiverSeg loads a missing or partial weights file.
  ```
  if sampleDataLogic.downloadPercent and sampleDataLogic.downloadPercent == 100:
              shutil.copyfile(fileDest, modelPath)
  ```
  Suggestion: Raise or return False when the copy does not happen, and check that modelPath exists before reporting success.

### No research-use or clinical-use disclaimer
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:3`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/README.md#L3): This is an AI segmentation tool applied to medical images, but neither the README nor the module help text (SegmentEditorMultiverSeg.py:27-31) states that output is not validated for clinical use. Users could reasonably treat the predictions as diagnostic-quality segmentations.
  ```
  MultiverSeg is a model that enables users to rapidly segment new biomedical imaging datasets. This extension add a
  segmentation effect that uses MultiverSeg.
  ```
  Suggestion: Add a short research-use-only / not-for-clinical-use notice to the README and the effect help text.

### Observer connected to the Segment Editor widget is never disconnected; assertion in the callback
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/SegmentEditorEffect.py:66`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/SegmentEditorEffect.py#L66): `sourceVolumeNodeChanged` caches the shared Segment Editor widget and connects a callback to it, but nothing disconnects it when the effect is destroyed or the module is reloaded, so stale effect instances keep receiving signals. The callback also starts with `assert segmentID == sen.GetSelectedSegmentID()`, which raises AssertionError if the signal arrives in a different order.
  ```
          self.sew.connect("currentSegmentIDChanged(QString)", self.tryToPreselectTask)
  ```
  Suggestion: Disconnect in a cleanup/`__del__`-style hook or use a weak connection, and replace the assertion with an early return.

### Runtime pip install of `packaging` without confirmation
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py:27`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py#L27): If `packaging` is missing, it is installed into Slicer's shared environment silently from inside a model-loading helper, with no user confirmation. `packaging` is bundled with current Slicer, so this is mostly dead code, but it is an unannounced environment mutation on a code path that runs during prediction.
  ```
      try:
          from packaging.version import Version
      except ModuleNotFoundError:
          print("Installing packaging")
          slicer.util.pip_install("packaging")
  ```
  Suggestion: Remove the fallback and rely on the bundled `packaging`, or compare versions without it.
- **haiku** (minor, medium confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py:29`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py#L29): loadImage silently runs pip install when packaging is missing. This is a small installation into the shared environment that the user did not confirm, and it can happen during prediction rather than at setup.
  ```
  except ModuleNotFoundError:
              print("Installing packaging")
              slicer.util.pip_install("packaging")
  ```
  Suggestion: Remove the dependency (for example with a simple version comparison) or install it during the confirmed setup step.

### User-supplied task names are used directly as directory names
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py:160`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py#L160): `createTask` and `renameTask` take the raw text from `qt.QInputDialog().getText` (SegmentEditorEffect.py:467, 488) and join it to the context root without validation. A name containing `../` or an absolute path creates or moves directories outside the chosen root, and `deleteCurrentTask` (line 156) then `shutil.rmtree`s whatever `activeContext` names. This requires deliberate user input, so it is a robustness issue rather than an attack path.
  ```
          destDir = self.contextRootPath.joinpath(name)
  
          if destDir.is_dir():
              return False
  
          destDir.mkdir(parents=True)
  ```
  Suggestion: Reject names containing path separators or `..`, and verify the resolved path stays under `contextRootPath`.

### CI test workflow is non-gating
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified, other file) [`.github/workflows/windows-testing.yml:14`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/.github/workflows/windows-testing.yml#L14): The workflow runs the unit tests on three platforms, but `continue-on-error: true` means a failing test never fails the run, so regressions (including broken model loading) can go unnoticed. This is a maintenance observation, not an admission blocker.
  ```
    Running-Tests:
      timeout-minutes: 30
      continue-on-error: true
  ```
  Suggestion: Drop `continue-on-error` once the suite is stable, or split the torch-dependent tests into a separate non-gating job.

### Segmentation logic has no automated test
info; utility; raised by haiku
- **haiku** (info, high confidence, quote verified) [`MultiverSeg/Testing/Python/CMakeLists.txt:4`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/Testing/Python/CMakeLists.txt#L4): The only test that would exercise SegmentationLogic is commented out because it needs PyTorch. Inference, the slice-axis mapping, and the 3D loop are therefore untested in CI.
  ```
  # slicer_add_python_unittest(SCRIPT SegmentationLogicTestCase.py) # This need pytorch to run
  ```
  Suggestion: Add a PyTorch-gated test that skips when PyTorch is absent, or add a fake-model unit test for the slice-handling logic.

### Zip import of task archives is not vulnerable to path traversal
info; safety; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py:147`](https://github.com/dalcalab/SlicerMultiverSeg/blob/6a2d3d57b26c0107274ae4926c0d8aa44afc8260/MultiverSeg/SegmentEditorMultiverSegLib/ContextLogic.py#L147): I checked the only archive-extraction path: it uses `shutil.unpack_archive` with the zip format, whose `ZipFile.extractall` strips absolute paths and `..` components, and the destination is a fresh directory that must not already exist. No traversal or overwrite of existing user files was identified here; a zip bomb remains theoretically possible but requires the user to import a hostile archive.
  ```
          dest = self.contextRootPath.joinpath(file.stem)
  
          if dest.is_dir(): raise IsADirectoryError(f"Task {file.stem} already exist.")
  
          shutil.unpack_archive(file, dest, "zip")
  ```
  Suggestion: Optional: cap the number and total size of extracted entries.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Well-structured Segment Editor effect with tests, CI and documentation, and no telemetry or import-time installs. Three concrete concerns keep it from merging as-is: (1) it pip-installs an unpinned third-party git repository (`git+https://github.com/halleewong/MultiverSeg.git`) into Slicer's Python environment at runtime, so any future commit to that repo runs arbitrary code in every user's Slicer and its declared dependencies can pull/downgrade packages Slicer bundles; (2) two pickle model checkpoints are downloaded from Dropbox shared links with no hash verification and then loaded by third-party code; (3) the PyTorch extension is used via PyTorchUtils but is not declared in `EXTENSION_DEPENDS`/`build_dependencies`. License of the downloaded weights and of the pip-installed package is not documented and could not be verified. 🔴 Do not merge yet.
Not checked: The multiverseg package installed from https://github.com/halleewong/MultiverSeg (its setup.py dependencies, license, and any torch.load call sites) — no network access.; The contents and license of the two Dropbox-hosted checkpoints (MultiverSeg_v0_nf256_res128.pt, ScribblePrompt_unet_v1_nf192_res128.pt).; The scribbleprompt package imported at SegmentationLogic.py:81 — its origin and license are not visible in this repository.; Whether the catalog entry's `scm_revision: "main"` currently resolves to the reviewed commit 6a2d3d57b26c0107274ae4926c0d8aa44afc8260, and whether the Extensions Index schema v1.0.1 validation passes.; Actual build/load of the extension in Slicer and the CI results of the windows-testing workflow.; Binary resources (icons, screenshots, test .nrrd/.png/.zip data) were not inspected beyond their sizes.
Questions for the author: Can the multiverseg dependency be pinned to a specific commit and installed with --no-deps, with torch/torchvision coming only from PyTorchUtils?; Can the model checkpoints be hosted at a stable project URL with published SHA-256 hashes verified after download?; Why is the PyTorch extension not declared in EXTENSION_DEPENDS / build_dependencies even though PyTorchUtils is required at runtime?; What are the licenses of the MultiverSeg and ScribblePrompt checkpoints and of the multiverseg package?; Would you consider storing tasks and checkpoints in a per-user writable directory instead of the extension installation folder?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
SlicerMultiverSeg is a cleanly implemented 3D Slicer segment editor effect extension integrating the MultiverSeg in-context segmentation model. It adheres to Slicer conventions by deferring heavy imports, utilizing PyTorchUtils for PyTorch installation, prompting users before downloading model checkpoints, and properly cleaning up states. All packaging, licensing, and safety checks pass without issue. 🟢 Recommend merge
Not checked: Binary files and model checkpoint weights hosted externally on Dropbox.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The module code is readable, has no telemetry or obvious malicious behavior, and all Python files listed in MultiverSeg/CMakeLists.txt exist. The main concerns are environment and supply-chain: the MultiverSeg package is pip-installed unpinned from a third-party GitHub HEAD into Slicer's shared Python environment, and model checkpoints are fetched from Dropbox with no checksum and loaded as PyTorch files. The catalog entry tracks the moving "main" branch. Several soundness issues (install success not verified, incomplete downloads reported as success) and unverified model-weight licensing need fixing. I could not inspect the upstream packages, the weights, or CI results.
Not checked: Upstream MultiverSeg and ScribblePrompt package contents, their pip dependencies, and whether they pull torch or other packages from PyPI.; The downloaded checkpoint files: no hash check was possible, and their contents were not inspected.; Licenses of the model weights and upstream packages (only the extension's Apache-2.0 LICENSE.txt was read).; Whether the MultiverSeg/ScribblePrompt loaders use torch.load with weights_only.; CI results (only windows-testing.yml was listed, not read), and whether the Slicer extension builds on all platforms.; Binary screenshots and icons (not inspected).


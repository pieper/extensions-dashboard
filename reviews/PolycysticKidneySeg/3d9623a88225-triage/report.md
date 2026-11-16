# AI review: PolycysticKidneySeg

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/conze/SlicerPolycysticKidneySeg at commit `3d9623a88225d8fcebe92922b09dcbe6bf91951e`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T02:42:30Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | ok |
| environment | concern | ok | concern |
| packaging | ok | ok | minor |
| license | minor | ok | concern |
| soundness | concern | ok | concern |
| utility | minor | ok | concern |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer module that runs the PKDIA Swin-UNet model to segment left and right polycystic kidneys from T2 MRI or CT volumes, for researchers and clinicians working with autosomal-dominant polycystic kidney disease imaging.
- **flash-lite**: PolycysticKidneySeg is a 3D Slicer extension that provides automated deep learning-based segmentation of polycystic kidneys (left and right kidneys) in T2-weighted MRI and CT imaging modalities using a Swin Transformer UNet architecture.
- **haiku**: Provides a Slicer module that runs the PKDIA transformer-based network to segment polycystic kidneys (left and right) from T2 MRI or CT volumes, with weights downloaded from the author's GitHub releases. It is aimed at researchers and clinicians working with ADPKD imaging in 3D Slicer.

## Disagreements (start here)

### D1. Log helper passes a method object instead of the scrollbar maximum, breaking log output and Apply/Install
single; category soundness; raised by haiku
- **haiku** (major, medium confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/Widget.py:122`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/Widget.py#L122): moveTextEditToEnd uses `.maximum` without calling it. onProgressInfo calls this helper on every message, and onApply and onInstall call onProgressInfo before any inference. In PythonQt the `maximum` attribute is a callable, so setValue receives a non-integer and raises. The user would see the Apply or Install action fail before segmentation starts. I could not run this, so confidence is medium.
  ```
  textEdit.verticalScrollBar().setValue(textEdit.verticalScrollBar().maximum)
  ```
  Suggestion: Use `textEdit.verticalScrollBar().maximum()` (call the method), and verify on a Slicer build that Apply reaches inference.

### D2. Multi-minute inference runs on the GUI thread without progress or cancel
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified, other lines) [`PolycysticKidneySeg/SlicerPKDIALib/Widget.py:82`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/Widget.py#L82): onApply calls applySegmentation synchronously from the button slot; the slice loop in PKDIA.py:53-85 never calls processEvents, so Slicer's UI is frozen for the whole run (README says "several minutes"). Users cannot cancel, and the window may be reported as unresponsive. Additionally only RuntimeError is caught (line 156), so an OSError from nibabel or a torch error propagates and leaves all buttons disabled because _setButtonsEnabled(True) at line 158 is never reached.
  ```
              try:
                  with tempfile.TemporaryDirectory() as tempDirPath:
                      inputFileName = "volume.nii.gz"
                      inputFilePath = Path(tempDirPath) / inputFileName
                      slicer.util.saveNode(inputVolume, str(inputFilePath))
  ```
  Suggestion: Run the inference in a worker thread (slicer.util.createProgressDialog / qSlicerCoreApplication or a QThread with progress callbacks), and use try/finally to re-enable the UI for any exception.
- **haiku** (major, medium confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/Widget.py:75`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/Widget.py#L75): The extension downloads PKDIAv1/v2 weights from GitHub releases and provides no license for them. Its acknowledgements say the models were trained on Genkyst cohort data, which may carry its own data-use terms. Users and redistributors cannot tell what they may do with the weights.
  ```
  ModalityEnum.T2: "https://github.com/conze/SlicerPolycysticKidneySeg/releases/download/v.1.1.0/PKDIAv1-weights.pth"
  ```
  Suggestion: Add a license or terms-of-use statement for the weights (and any data restrictions) in the repository and release notes.

### D3. Unconfirmed pip installs of Slicer-bundled packages (numpy, scikit-image)
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified, other lines) [`PolycysticKidneySeg/SlicerPKDIALib/InstallLogic.py:31`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/InstallLogic.py#L31): `pip_install("numpy")` installs a Slicer-bundled package directly, and `pip_install("scikit-image")` resolves numpy/scipy/pillow requirements that pip may upgrade in place. Slicer's own modules and other extensions are compiled against the bundled numpy/scipy, so an upgrade can break them for the whole installation. No confirmation dialog is shown for these installs (doAskConfirmation is only used for PyTorch), and pip_install swallows CalledProcessError and still returns True (lines 169-177), so a failed install is reported as success.
  ```
      try:
          import numpy  # noqa
      except ImportError:
          self.pip_install("numpy")
      try:
          import skimage  # noqa
  ```
  Suggestion: Do not install numpy at all (Slicer always ships it); install scikit-image/nibabel with version constraints compatible with Slicer's bundled numpy/scipy, ask the user for confirmation before modifying the environment, and propagate pip failures so the UI reports them.
- **haiku** (minor, medium confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/InstallLogic.py:67`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/InstallLogic.py#L67): numpy, scikit-image, nibabel and timm are installed with plain pip install (no constraints), and this happens on a button press or during the self-test. Installing scikit-image can pull or upgrade numpy/scipy that Slicer and other extensions depend on. Users are not asked to confirm these installs, unlike PyTorch.
  ```
  self.pip_install("scikit-image")
          try:
              import nibabel  # noqa
  ```
  Suggestion: Ask for confirmation before installing packages, pin compatible versions, or use constraints that protect Slicer's bundled numpy and scipy.

### D4. pip_install("timm") pulls torchvision from PyPI outside PyTorchUtils
single; category environment; raised by deepseek
- **deepseek** (major, high confidence, quote verified, other lines) [`PolycysticKidneySeg/SlicerPKDIALib/InstallLogic.py:31`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/InstallLogic.py#L31): timm declares torchvision (and torch) as hard requirements. When the user presses "Install dependencies", `slicer.util.pip_install("timm")` resolves torchvision from PyPI, which is not the build installed by the PyTorch extension/PyTorchUtils. A CPU-only or CUDA-mismatched torchvision can break the torch install that PyTorchUtils just set up, affecting every other extension using PyTorch in the same Slicer installation. The policy explicitly requires PyTorch-family packages to come through PyTorchUtils.
  ```
      try:
          import timm  # noqa
      except ImportError:
          self.pip_install("timm")
  ```
  Suggestion: Install timm with `--no-deps` after ensuring torch/torchvision are provided by PyTorchUtils (e.g. `torchLogic.installTorch(...)` plus a torchvision install through PyTorchUtils), or vendor the small amount of timm functionality used (create_model for swinv2_cr_tiny_ns_224) so no extra dependency is needed.

### D5. pretrained=True triggers a silent HuggingFace download during every Apply
severity dispute; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/pkdia/PKDIA.py:24`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/pkdia/PKDIA.py#L24): timm.create_model(..., pretrained=True) downloads ImageNet encoder weights from the HuggingFace hub the first time (and re-checks the hub on later runs). This happens inside the segmentation call, with no user opt-in and no mention in the README, and it makes Apply fail on offline/air-gapped machines even though the local PKDIA checkpoint is loaded immediately afterwards at line 40 and overwrites those weights. It also adds an unannounced third-party network destination to the module's behaviour.
  ```
      net = swinv2Unet.SwinV2TwoDecoder(
          model_name="swinv2_cr_tiny_ns_224",
          pretrained=True,
  ```
  Suggestion: Pass pretrained=False (the state dict is loaded right after) or, if the pretrained encoder is genuinely needed, download it explicitly through the existing "Download weights" flow with a checksum and document it.
- **haiku** (info, low confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/pkdia/PKDIA.py:26`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/pkdia/PKDIA.py#L26): applyPKDIA builds the network with pretrained=True, so timm may download encoder weights on first use. This is an undisclosed network access, though the trained weights are then loaded over them. It is not clearly documented to users.
  ```
  pretrained=True,
          img_size=(img_size, img_size),
  ```
  Suggestion: Use pretrained=False because the trained state dict is loaded anyway, which avoids an extra download.

### D6. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D7. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D8. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D9. Rating of utility
rating dispute; category utility; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings from some reviewers

### Integration test imports submodules as classes and will fail
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`PolycysticKidneySeg/Testing/IntegrationTestCase.py:6`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/Testing/IntegrationTestCase.py#L6): SlicerPKDIALib/__init__.py is empty, so `from SlicerPKDIALib import InstallLogic, SegmentationLogic, Widget` yields module objects. Calling `InstallLogic()` or `SegmentationLogic()` then raises TypeError. The test therefore cannot validate the pipeline, and the only test is also marked slow.
  ```
  from SlicerPKDIALib import InstallLogic, SegmentationLogic, Widget
  ```
  Suggestion: Import the classes from their modules, e.g. `from SlicerPKDIALib.InstallLogic import InstallLogic`, and check the test runs in CI.

### Model weights downloaded without integrity verification
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/Widget.py:82`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/Widget.py#L82): The .pth checkpoints are fetched from GitHub releases and loaded with torch.load (PKDIA.py:40). weights_only=True limits pickle-based code execution, but a corrupted or substituted download is still loaded without any SHA256 check, unlike the sample data in PolycysticKidneySeg.py:57/68 which do declare checksums. A truncated download also produces a confusing load error rather than a clear message.
  ```
              try:
                  weightPath.parent.mkdir(parents=True, exist_ok=True)
                  urllib.request.urlretrieve(weightURL, weightPath)
              except (urllib.error.HTTPError, urllib.error.URLError):
  ```
  Suggestion: Add SHA256 checksums for PKDIAv1-weights.pth and PKDIAv2-weights.pth and verify after download, as already done for the sample volumes.
- **haiku** (minor, medium confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/Widget.py:83`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/Widget.py#L83): urlretrieve writes directly to the final weights path. A failed or interrupted download can leave a truncated .pth file. areWeightsFound only checks existence, so later torch.load fails with a confusing error. The downloads also have no SHA256 check, unlike the sample data.
  ```
  weightPath.parent.mkdir(parents=True, exist_ok=True)
                  urllib.request.urlretrieve(weightURL, weightPath)
              except (urllib.error.HTTPError, urllib.error.URLError):
  ```
  Suggestion: Download to a temporary file, verify a SHA256 checksum, then rename. Remove partial files on failure.

### No clinical-use disclaimer or validation statement for a medical segmentation tool
minor; utility; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`PolycysticKidneySeg/PolycysticKidneySeg.py:30`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/PolycysticKidneySeg.py#L30): The module produces kidney segmentations used for ADPKD assessment, yet the help text and README have no statement that results are not for clinical decisions, and no validation or intended-use limits are given beyond a citation.
  ```
  This extension allows the use of PKDIA neural networks in 3DSlicer.<br><br>
  ```
  Suggestion: Add a research-use-only disclaimer and the validation scope to the help text and README.

### No stated license or terms for the downloaded model weights; no clinical disclaimer
minor; license; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`README.md:35`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/README.md#L35): The repository LICENSE is Apache-2.0 for the code, but the PKDIAv1/v2 checkpoints distributed via GitHub releases and the Genkyst cohort data behind them have no explicit license or usage terms, and neither README.md nor the module helpText states that the output is for research use and not for clinical decision making. Users cannot tell what they may do with the weights.
  ```
  Models were developed and trained by Pierre-Henri Conze (IMT Atlantique) using imaging data from the Genkyst cohort.
  ```
  Suggestion: State the license/terms of the model weights explicitly (e.g. in README and next to the release assets) and add a research-use-only disclaimer to README and helpText.

### Segmentation geometry may not match the input volume orientation
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/Widget.py:153`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/Widget.py#L153): The pipeline reorients the volume with nibabel.as_closest_canonical (exam_genkyst_prod.py:23) and writes predictions in that canonical space, while the segmentation node is then given the original volume's geometry. If the loaded volume is not already in closest-canonical orientation, the resulting segments can be displayed misaligned with the image. SetReferenceImageGeometryParameterFromVolumeNode only sets the reference-geometry parameter, not the segment geometry.
  ```
                      segmentationNode = self.logic.applySegmentation(str(inputFilePath), tempDirPath, modality)
                      segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(inputVolume)
  ```
  Suggestion: Either skip as_closest_canonical and work in the volume's own orientation, or resample the prediction back to the input volume geometry before creating the segmentation node.
- **haiku** (minor, high confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/Widget.py:156`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/Widget.py#L156): onApply disables the buttons, then catches only RuntimeError. A nibabel, timm or shape error inside applySegmentation propagates and the buttons are never re-enabled, so the user must restart the module. Errors are not reported in the log either.
  ```
  except RuntimeError as e:
                  self._reportError(f"Inference ended in error:\n{e}")
          self._setButtonsEnabled(True)
  ```
  Suggestion: Use try/finally to re-enable buttons and report any Exception to the user.

### Validation errors overwrite each other; only the last is shown
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/Widget.py:136`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/Widget.py#L136): Each failed check replaces errorMessage, so a user with no volume selected and missing weights only sees the weights message and may not understand why Apply does nothing useful. Also areWeightsFound() (SegmentationLogic.py:19-23) requires both T2 and CT checkpoints, so a user who only downloaded one modality is blocked from using it.
  ```
          if inputVolume is None:
              errorMessage = "Invalid input volume"
          if modality not in ModalityEnum:
              errorMessage = "Invalid modality"
  ```
  Suggestion: Collect all failures into a list and display them together; check only the weights file for the selected modality.

### Weights are written inside the extension installation directory
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`PolycysticKidneySeg/SlicerPKDIALib/SegmentationLogic.py:10`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/SlicerPKDIALib/SegmentationLogic.py#L10): Downloaded checkpoints land in <extension>/weights, i.e. inside the Slicer installation tree. On read-only or system-wide installs the mkdir/urlretrieve fails, and the files are not removed on uninstall. Slicer convention is to store such data in the user's settings/temporary directory.
  ```
          fileDir = Path(__file__).parent
          self.weightsDir = fileDir.parent / "weights"
  ```
  Suggestion: Store weights under slicer.util.settingsValue / a user-writable cache directory (e.g. slicer.mrmlScene temp dir or QStandardPaths AppDataLocation).

### Integration test uses MRHead and an undeclared test-runner extension
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`PolycysticKidneySeg/Testing/IntegrationTestCase.py:26`](https://github.com/conze/SlicerPolycysticKidneySeg/blob/3d9623a88225d8fcebe92922b09dcbe6bf91951e/PolycysticKidneySeg/Testing/IntegrationTestCase.py#L26): The only integration test feeds a head MR into a kidney model, so it can only assert that two segments were created, not that the pipeline is correct; it is also marked slow and excluded by the module's own `-m not slow` filter. PolycysticKidneySeg.py:93-100 additionally requires the SlicerPythonTestRunner extension, which is not declared anywhere.
  ```
          SampleData.SampleDataLogic().downloadMRHead()
          widget.ui.modalityComboBox.setCurrentIndex(0)  # T2
  
          widget.ui.applyButton.click()
  ```
  Suggestion: Use the registered T2/CT sample data in the test and declare SlicerPythonTestRunner as a test dependency in the documentation.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The extension is a straightforward ScriptedLoadableModule wrapper around a SwinV2-UNet; I found no data exfiltration, secrets, obfuscation, or reviewer-directed text, and the catalog entry, CMake file lists and Apache-2.0 LICENSE are consistent. The main problems are environmental and behavioural: `pip_install("timm")` will pull torchvision from PyPI outside PyTorchUtils, `pip_install("numpy")`/`scikit-image` can touch Slicer-bundled packages without confirmation, and inference calls `timm.create_model(..., pretrained=True)`, silently downloading ImageNet weights at Apply time (and failing offline) even though the checkpoint is loaded immediately afterwards. Weights are downloaded without checksum verification, and multi-minute inference runs on the GUI thread.
Not checked: Could not verify the actual content of the downloaded checkpoints PKDIAv1-weights.pth / PKDIAv2-weights.pth (binary, hosted on GitHub releases) or their license terms.; Could not verify the timm model 'swinv2_cr_tiny_ns_224' pretrained weight source/license or confirm the exact dependency resolution pip performs for timm in Slicer's Python.; Could not run the extension, its tests, or the CMake build; packaging was assessed by comparing CMakeLists file lists against the repository tree only.; Could not confirm the catalog entry's scm_revision 'main' resolves to the stated commit 3d9623a88225d8fcebe92922b09dcbe6bf91951e (no network access).; Did not inspect the binary PNG resources (icons, screenshots) beyond their presence and size.
Questions for the author: Why is pretrained=True used in PKDIA.applyPKDIA when the PKDIA checkpoint is loaded immediately afterwards? Can it be set to False to avoid the HuggingFace download?; How is torchvision provided? timm requires it, and pip installing timm outside PyTorchUtils can install a torchvision build that does not match the PyTorch extension's torch.; What are the license/usage terms for the PKDIAv1/v2 weights and the Genkyst training data, and can SHA256 checksums be published for the weight downloads?; Can inference be moved off the GUI thread with a progress bar and cancel button?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The PolycysticKidneySeg extension is well-structured, follows 3D Slicer conventions, properly packages its Python scripts and resources via CMake, integrates with PyTorch and PyTorchUtils safely (including weights_only=True for model weight loading), and includes good documentation, tests, and sample data. 🟢 Recommend merge.
Not checked: Exact execution test in 3D Slicer runtime environment (static analysis only)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The extension is a reasonably structured ScriptedLoadableModule with no obvious malicious behavior. torch.load uses weights_only=True, sample-data checksums are present, the PyTorch dependency is declared and installed through the PyTorch extension, and the code is Apache-2.0. However, the widget has a defect in the scroll-to-end helper (Widget.py line 122) that is called on every log message, so Apply and Install likely fail before inference. The integration test imports modules where it expects classes. Model-weight licensing is undocumented, and there is no clinical-use disclaimer. I recommend fixes before the extension is offered to users.
Not checked: Whether the source at commit 3d9623a88225d8fcebe92922b09dcbe6bf91951e matches the catalog (scm_revision is 'main', a moving branch).; Whether the listed icon and UI resources exist (only directory listings were shown).; Runtime behavior: no Slicer run, no CI logs, no model download or inference.; Contents of the pkdia network and utility modules beyond the files shown, and the released weights files themselves.; Whether the PythonQt maximum attribute behavior in Widget.py line 122 raises in practice.
Questions for the author: What is the license or terms of use for PKDIAv1-weights.pth and PKDIAv2-weights.pth, and does Genkyst data impose restrictions?; Has Apply been verified end-to-end on a Slicer build since Widget.py line 122 was written?; Should weight downloads be checksum-verified as the sample data is?


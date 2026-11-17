# AI review: BreastUltrasoundAnalysis

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis.git at commit `8ef5c700d3f635d686ce1e820d88cce009baf3b1`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-17T12:42:51Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | blocking | minor | blocking |
| environment | blocking | concern | blocking |
| packaging | ok | ok | minor |
| license | concern | ok | concern |
| soundness | concern | ok | concern |
| utility | minor | ok | concern |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer scripted module (BUS_Diagnosis) that segments breast-ultrasound nodules and predicts benign/malignant class with a bundled ConvFormer multi-task network, aimed at physicians reviewing DICOM ultrasound series.
- **flash-lite**: The BreastUltrasoundAnalysis extension provides a 3D Slicer scripted module for automated segmentation and benign/malignant classification of breast ultrasound nodules using a multi-task transformer (Conformer) architecture.
- **haiku**: A Slicer scripted module (BUS_Diagnosis) for breast ultrasound lesion segmentation and benign/malignant prediction using a PyTorch multi-task transformer, for physicians as a decision aid. It depends on the PyTorch extension and downloads a model weight file and a sample volume from third-party file hosts.

## Disagreements (start here)

### D1. Model weights downloaded with TLS verification disabled and loaded via torch.load without integrity check
severity dispute; category safety; raised by deepseek, flash-lite, haiku
- **deepseek** (major, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:738`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L738): downloadShowProgress() is used both for the model weights (line 768) and the sample volume (line 458) with verify=False, so a man-in-the-middle can substitute the payload. Combined with the torch.load path this makes the code-execution risk practical; for the sample data it silently replaces the intended sample file with whatever the attacker sends.
  ```
      response = requests.get(url, stream=True, verify=False, headers=headers)
  ```
  Suggestion: Use verify=True (the default) and pin the payload with a checksum.
- **flash-lite** (minor, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:738`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L738): The download logic disables SSL certificate verification (`verify=False`) when downloading model weights and sample data via `requests.get`. This exposes users to man-in-the-middle (MitM) attacks where an attacker could intercept or tamper with the downloaded deep learning model weights or sample data.
  ```
      response = requests.get(url, stream=True, verify=False, headers=headers)
  ```
  Suggestion: Remove `verify=False` or implement checksum verification (e.g., SHA256) for downloaded models and datasets.
- **haiku** (blocking, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:738`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L738): setupNet downloads net_weight_base.pth from a third-party Zoho host through downloadShowProgress, which calls requests.get with verify=False, so any network attacker can substitute the file. The file is then passed to torch.load, which unpickles by default in older PyTorch versions, giving arbitrary code execution as the user. No checksum or signature is verified, even though the commented-out sample-data code shows the author knows about checksums. The sample download uses the same unverified path.
  ```
  response = requests.get(url, stream=True, verify=False, headers=headers)
  ```
  Suggestion: Enable certificate verification, pin a SHA-256 checksum of the weight file and verify it before loading, and use torch.load(..., weights_only=True) or a safetensors format. Host the weights on a stable HTTPS source tied to a release.

### D2. Model weights fetched without integrity check are loaded with torch.load (unsafe deserialization of a remote file)
partial; category safety; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:772`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L772): On first use the module downloads net_weight_base.pth from files.zohopublic.com.cn into the extension's Resources folder (lines 762-768) and immediately unpickles it with torch.load (line 772), without weights_only, checksum or signature. Because the same download disables TLS verification (line 738), anyone able to intercept or compromise that host can deliver an arbitrary pickle that executes with the user's privileges the moment they click 'AI Automatically Segment and Diagnose'.
  ```
        self.model_seg.load_state_dict(torch.load(self.weight_path_seg, map_location=torch.device(self.device)))
  ```
  Suggestion: Host the weights with the extension (GitHub release) and verify a SHA-256 checksum, load with torch.load(..., weights_only=True) where available, and use certificate verification (remove verify=False).
- **haiku** (major, medium confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:772`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L772): The downloaded checkpoint is deserialized with torch.load. Because the file comes from an unverified source (see above), this is unsafe deserialization. Even with a good checksum, weights_only=True should be used.
  ```
  self.model_seg.load_state_dict(torch.load(self.weight_path_seg, map_location=torch.device(self.device)))
  ```
  Suggestion: Use torch.load(path, map_location=..., weights_only=True) after checksum verification.

### D3. Heavy inference runs on the GUI thread with a modal dialog but no event processing
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:939`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L939): In 'Segment All' mode the module loops over every slice, running the full ConvFormer on each, synchronously in the button handler; progressDiag.setValue() is never followed by processEvents, so the window does not repaint and Slicer appears frozen for the 'several minutes' the UI warns about. The model is also constructed eagerly in BUS_DiagnosisLogic.__init__ (line 700), slowing the first module open.
  ```
            result_img_temp[:, :, i] = np.squeeze(self.AIAssistedSegment(input_img[:, :, i])[0], axis=2)
  ```
  Suggestion: Run the loop in a slicer.util.ProgressDialog/CLI-style worker (or at least call qt.QApplication.processEvents() per slice) and build/load the network lazily in setupNet().

### D4. No license or provenance terms for the downloaded weights and sample data
partial; category license; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`README.md:57`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/README.md#L57): The Apache-2.0 LICENSE covers the repository code only. The net_weight_base.pth and BenignSample.nrrd payloads are distributed exclusively through third-party file-hosting links (also Zoho/Google Drive), with no license statement, no redistribution permission, and no information on how the sample ultrasound data was obtained or de-identified. The extension cannot be said to have clear distribution permission for the material it fetches.
  ```
  - [NetWeight (Zoho WorkDrive)](https://workdrive.zoho.com.cn/file/jy075dd560e5a2fe7475b8a02ebc889aca769)
  ```
  Suggestion: Attach an explicit license/permission statement for the weights and sample data (ideally host them as GitHub release assets under the same terms) and document the sample data's provenance and de-identification.
- **haiku** (minor, medium confidence, quote verified) [`README.md:56`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/README.md#L56): The repository license is Apache-2.0 for code, but the trained weight file and the sample NRRD are only referenced from Google Drive and Zoho links. No terms for those artifacts are given, so users cannot tell whether they may use or redistribute them, especially in a clinical-research setting.
  ```
  - [NetWeight (Google Drive)](https://drive.google.com/file/d/1lfYU8dPFIRQ4uWio_YlbG-31i35uttwA/view?usp=sharing)
  ```
  Suggestion: State the license for the weights and sample data in the README, or add a LICENSE/NOTICE for those artifacts.

### D5. PyTorchUtils result ignored and failures swallowed
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:34`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L34): Even when PyTorchUtils successfully installs a matching torch, the code then runs pip_install of the newest PyPI torch anyway (line 37); the return value of installTorch is discarded and the bare 'except: pass' (line 35) hides failures. Users get either a silently upgraded/duplicated torch or an obscure import error, with no explanation of what was installed.
  ```
        torch = torchLogic.installTorch(askConfirmation=True)
  ```
  Suggestion: Check the value returned by installTorch (and torchLogic.ensureTorch / version list), and report failure to the user instead of continuing into pip_install.
- **haiku** (major, high confidence, quote verified, other lines) [`BUS_Diagnosis/BUS_Diagnosis.py:37`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L37): onInstallPytorchButton installs torch, torchvision and torchaudio directly from PyPI, with no CUDA selection and no use of PyTorchUtils. This bypasses the extension's logic and can break the shared environment for other extensions.
  ```
  slicer.util.pip_install('torch torchvision torchaudio')
        import torch
  ```
  Suggestion: Route the button through PyTorchUtils.PyTorchUtilsLogic().installTorch(askConfirmation=True).

### D6. Sample-data download over unverified TLS with no checksum
single; category safety; raised by haiku
- **haiku** (major, medium confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:453`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L453): The sample NRRD is fetched from a third-party URL with verify=False and no checksum, then loaded into the scene. A MITM could substitute crafted image data. The file is then parsed by Slicer's loader, so the impact is limited, but the download is still unauthenticated.
  ```
  url = "https://files.zohopublic.com.cn/public/workdrive-public/download/jy075c6237954580e4ccf98fca3fd55bacf66?x-cli-msg=%7B%22isFileOwner%22%3Afalse%2C%22version%22%3A%221.0%22%7D"
  ```
  Suggestion: Verify TLS and check a SHA-256 digest of the sample file before loading it.

### D7. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite minor, haiku blocking

### D8. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D9. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D10. Rating of utility
rating dispute; category utility; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings all reviewers agree on

### PyTorch installed with pip_install at module import, bypassing the PyTorch extension
blocking; environment; raised by deepseek, flash-lite, haiku
- **deepseek** (blocking, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:37`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L37): The module-level try/except ends in an unconditional pip_install of torch/torchvision/torchaudio, so importing the script (which happens when Slicer scans the qt-scripted-modules folder at startup, before the module is ever opened) installs PyPI torch into Slicer's shared Python, together with its own numpy/pillow pins. This affects users who never open the module and can break Slicer and other extensions; README.md:33 confirms the intent ('This module will install them automatically when you restart 3D Slicer for the first time'). The catalog declares PyTorch in build_dependencies/EXTENSION_DEPENDS, which is the supported route.
  ```
      slicer.util.pip_install('torch torchvision torchaudio')
  ```
  Suggestion: Remove the pip_install fallback (and the duplicate one in onInstallPytorchButton, line 446); require torch via PyTorchUtils.installTorch/ensureTorch with a version list and let the PyTorch extension provide it, showing a clear error if unavailable.
- **flash-lite** (major, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:37`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L37): The extension attempts to pip-install `torch torchvision torchaudio` directly via `slicer.util.pip_install` at module import time (and again on demand). Per Extensions Index review policy, PyTorch must not be installed via `pip_install` from PyPI, but rather through the Slicer PyTorch extension (`PyTorchUtils`, listed in `build_dependencies` and `EXTENSION_DEPENDS`). Installing PyTorch directly from PyPI can break Slicer's environment, CUDA compatibility, or bundle integrity.
  ```
      slicer.util.pip_install('torch torchvision torchaudio')
  ```
  Suggestion: Remove the top-level `pip_install('torch torchvision torchaudio')` block from `BUS_Diagnosis.py`, rely on `PyTorchUtils` in `build_dependencies` / `EXTENSION_DEPENDS`, and prompt or guide users appropriately through `PyTorchUtilsLogic().installTorch()` without unpinned pip installs from PyPI.
- **haiku** (blocking, high confidence, quote verified, other lines) [`BUS_Diagnosis/BUS_Diagnosis.py:37`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L37): At module import (the except branch), the code calls slicer.util.pip_install('torch torchvision torchaudio') after a failed PyTorchUtils attempt. This runs during Slicer startup for every user who has the module loaded, and installs unpinned PyPI torch into Slicer's shared Python environment. AGENTS.md requires requesting changes for this. The README (line 33) describes the automatic install as expected behavior.
  ```
      slicer.util.pip_install('torch torchvision torchaudio')
  ```
  Suggestion: Remove the direct pip install. Rely on PyTorchUtils (listed in build_dependencies) and its user-confirmed installTorch, and do not install at import time. If the try-import fails, show a message asking the user to install PyTorch through the PyTorch extension.


## Findings from some reviewers

### Download error handling is broken; retry settings are ineffective
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:741`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L741): The content-length read is outside the try block, so a missing header raises KeyError that escapes the 'except: QMessageBox ... Download failed' path and surfaces as a generic 'Failed to compute results' (or nothing). requests.DEFAULT_RETRIES does not exist in requests and the created session 's' is unused, so the intended retry behaviour never happens; verify=False is also applied here.
  ```
      content_size = int(response.headers['content-length'])
  ```
  Suggestion: Move all network/file operations into the try block, drop or implement retries properly, and report the exception text to the user.
- **haiku** (minor, medium confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:741`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L741): content_size is read from response.headers['content-length'] outside the try block, so a missing header raises an unhandled KeyError and the user sees no message. Non-200 responses fall through silently and the 'success' path still runs when showsuccess is set.
  ```
  content_size = int(response.headers['content-length'])
  ```
  Suggestion: Move the request inside the try, check response.status_code and raise_for_status, and handle a missing content-length.

### Model weights are written into the Slicer installation tree
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:763`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L763): The downloaded weight file is stored in the extension's own installed Resources directory. On system-wide or read-only Slicer installations this fails (and the failure is reported only as 'Download failed'), and it modifies installed program files rather than user or temporary data.
  ```
        path = os.path.join(os.path.dirname(__file__), 'Resources')
  ```
  Suggestion: Download to the Slicer user settings/cache directory (e.g. under slicer.app.userSettingsPath()) or a temporary folder.

### No functional tests; test scaffold is empty
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`BUS_Diagnosis/Testing/Python/CMakeLists.txt:2`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/Testing/Python/CMakeLists.txt#L2): The only test method body is a stub, and the CTest registration is commented out. Logic such as fromCurrentOffsettoCurrentSlice, the classifier output mapping, and the save routines is untested, so regressions would not be caught.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a small unit test that exercises the logic with a dummy or synthetic model and enable the CTest registration.

### No model provenance, training data description or validation metrics
minor; utility; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`README.md:27`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/README.md#L27): The README cites the JBHI paper but the module itself gives no information about training data, intended population, reported sensitivity/specificity, or whether the shipped weights correspond to the published model. Clinicians cannot judge when the benign/malignant output is trustworthy.
  ```
  **Caution! The AI prediction results are not absolutely accurate, and are only for physicians' reference in diagnosis.**
  ```
  Suggestion: State the weights' version/date, the training cohort, and published performance, and repeat the caution inside the module help text.

### Result-folder name built by string surgery on the last character
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified, other lines) [`BUS_Diagnosis/BUS_Diagnosis.py:543`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L543): The 'next free folder' logic assumes the last character is a single digit of the counter; after '_9' the next candidate becomes '_11' and the pattern only works by accident, and the while loop can spin on names it cannot parse. It also silently creates new folders instead of asking, which can scatter patient results across the chosen directory.
  ```
            savePath = savePath[:-1] + f"{int(savePath[-1]) + 1}"
  ```
  Suggestion: Use an integer counter (e.g. itertools.count or an int variable) with os.path.exists on the formatted name.

### Test class contains no assertions
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`BUS_Diagnosis/BUS_Diagnosis.py:30`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L30): BUS_DiagnosisTest.test_BUS_Diagnosis1 only contains 'pass', so the registered ctest (BUS_Diagnosis/CMakeLists.txt:28) can never catch a regression such as a renamed UI widget or a broken torch API, even though the module depends on fast-moving third-party packages.
  ```
      pass
  ```
  Suggestion: Add at least a smoke test that instantiates the logic, checks parameter-node defaults, and (if a small test volume is shipped) runs process() on it.

### Unpinned branch reference in catalog entry
minor; soundness; raised by haiku; **quote not found in source**
- **haiku** (minor, high confidence, quote quote not found) [`BUS_Diagnosis/BUS_Diagnosis.py:1`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L1): scm_revision is 'master', a moving branch. The code the index builds may change without review, so the approved source is not fixed.
  ```
  "scm_revision": "master",
  ```
  Suggestion: Pin scm_revision to a reviewed commit SHA or a release tag.

### Use of eval in the Conformer forward pass
minor; soundness; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:1250`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L1250): The evaluated string is built only from an integer loop counter over self.add_module names, so there is no injection path from user input; flagged only as a style/robustness note (getattr would be equivalent and safer).
  ```
              x, x_t = eval('self.conv_trans_' + str(i))(x, x_t)
  ```
  Suggestion: Replace with getattr(self, 'conv_trans_' + str(i))(x, x_t).
- **haiku** (minor, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:1250`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L1250): eval builds attribute names from a constant prefix and integer. Current inputs are safe, but it is an unnecessary eval and hides the module graph from tooling.
  ```
  x, x_t = eval('self.conv_trans_' + str(i))(x, x_t)
  ```
  Suggestion: Use getattr(self, 'conv_trans_' + str(i))(x, x_t).

### Patient identifiers written to a plain-text file in a user-chosen folder
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`BUS_Diagnosis/BUS_Diagnosis.py:550`](https://github.com/ZhyBrian/SlicerBreastUltrasoundAnalysis/blob/8ef5c700d3f635d686ce1e820d88cce009baf3b1/BUS_Diagnosis/BUS_Diagnosis.py#L550): Saving results writes name, ID, birth date and sex into Classification_Result.txt next to the images. This is user-initiated and to a user-chosen directory, so it is expected behaviour, but the identifiers are unencrypted and the patient name is also used as part of the folder name; worth a note in the documentation.
  ```
        f.write(f"Patient Name       :  {patientName}\n")
  ```
  Suggestion: Document that saved results contain PHI, and consider offering a de-identified option.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The module is well documented (tutorial, video, screenshots, citation, caution note) and its CMake/catalog wiring looks consistent, but it has two blocking problems: it pip-installs `torch torchvision torchaudio` at module import (i.e. at Slicer startup for every user of the extension, bypassing PyTorchUtils and ignoring its result), and it downloads the model weights with TLS verification disabled and no checksum, then feeds that file to `torch.load` (pickle) — a concrete remote-code-execution path via MITM or a compromised host. Secondary issues: GUI-thread inference, broken download error handling, empty test stub, and no stated license/terms for the downloaded weights and sample data. Recommendation: 🔴 Do not merge yet.
Not checked: Could not build the extension or load it in Slicer; CMake wiring was assessed by reading CMakeLists.txt files only.; Could not resolve scm_url/scm_revision: the catalog pins the branch 'master', so the reviewed code is the snapshot described as commit 8ef5c700d3f635d686ce1e820d88cce009baf3b1; I could not verify that commit or the current tip of master.; Could not download or inspect net_weight_base.pth or BenignSample.nrrd (hosted on Zoho WorkDrive / Google Drive); their contents, license, and the exact payload served today are unknown.; Could not review the referenced JBHI paper's licensing or the module's clinical validation data.; Did not inspect binary files (PNG screenshots, .ui beyond widget-name greps) in detail.
Questions for the author: Can the torch pip_install at import (line 37) and in onInstallPytorchButton (line 446) be removed so that torch is provided only through PyTorchUtils / the PyTorch extension, with a clear user-facing error when it is missing?; Can the model weights be hosted as a GitHub release asset with a published SHA-256 checksum and loaded with torch.load(..., weights_only=True), and can verify=False (line 738) be removed?; Under what license and with what provenance/de-identification are net_weight_base.pth and BenignSample.nrrd distributed?; Which published performance figures correspond to the shipped weights, and can they be stated in the module help text?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): needs fixes
The `BreastUltrasoundAnalysis` extension is well-documented and implements a deep learning-based breast ultrasound analysis module for 3D Slicer. However, it violates Slicer extension review policy regarding PyTorch installation by invoking `slicer.util.pip_install('torch torchvision torchaudio')` at import time rather than correctly relying on `PyTorchUtils` (though `PyTorch` is correctly listed in `build_dependencies`, the Python code forces a raw PyPI pip install). Additionally, SSL verification is disabled during model weight and sample data downloads. Therefore, the PR needs fixes before merging.
Not checked: Runtime execution and live Slicer UI interaction (assessed via static source analysis of the repository files).

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The module is plausibly benign in intent (Apache-2.0, clear research-use caveat), but it fails the admission bar on safety and environment. It disables TLS verification for downloads, loads an unverified downloaded pickle-based checkpoint with torch.load, and pip-installs PyTorch from PyPI at import and from a button rather than through the PyTorch extension. The entry also tracks a branch rather than a pinned revision, and the test suite is empty. I did not run anything; findings come from reading the supplied files only.
Not checked: Did not resolve the catalog scm_url or check that the revision 'master' exists; no network access was used.; Did not confirm the Resources/UI/BUS_Diagnosis.ui and Icons files exist in the repository (only the file listing was supplied).; Did not run the module, the PyTorch install path, or any download; behavior is inferred from source only.; Did not check the remote weight or sample files' contents, checksum, or the current availability of the Zoho and Google Drive links.; Did not check the upstream source for newer commits or CI results.


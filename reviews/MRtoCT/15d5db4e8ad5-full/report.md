# AI review: MRtoCT

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/kgiraldo09/SlicerMRtoCT.git at commit `15d5db4e8ad533a82015c0178e4cd8d78600fdf7`
- Context: pull request 2445 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-13T17:00:35Z; cost $0.42

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | ok | ok | blocking |
| environment | ok | ok | ok |
| packaging | minor | ok | unknown |
| license | minor | ok | ok |
| soundness | concern | concern | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: Slicer extension that generates a synthetic CT (in HU) from a brain MR volume. It uses a SAdaNGF 3D generator run with PyTorch sliding-window inference. It targets radiotherapy researchers.
- **gemini**: MRtoCT is a 3D Slicer scripted module for radiotherapy researchers that generates a synthetic CT volume (in Hounsfield units) from a brain MR volume using a 3D ResNet generator (SAdaNGF).
- **gpt**: MRtoCT generates a synthetic CT volume from a brain MR using a deep-learning model. It is intended for non-commercial radiotherapy research, not clinical treatment planning.

## Disagreements (start here)

### D1. Selecting the input as output destroys the in-scene MR data
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`MRtoCT/MRtoCT.py:289`](https://github.com/kgiraldo09/SlicerMRtoCT/blob/15d5db4e8ad533a82015c0178e4cd8d78600fdf7/MRtoCT/MRtoCT.py#L289): Both selectors accept scalar volume nodes and there is no check that the output differs from the input. If a user inadvertently selects the MR as the output, a successful generation replaces its voxel data with synthetic CT; subsequently saving that node can lose the original MR data.
  ```
          # same voxel grid and position as the input MR
          ijkToRas = vtk.vtkMatrix4x4()
          inputVolume.GetIJKToRASMatrix(ijkToRas)
          outputVolume.SetIJKToRASMatrix(ijkToRas)
          slicer.util.updateVolumeFromArray(outputVolume, sct)
          outputVolume.SetAndObserveTransformNodeID(inputVolume.GetTransformNodeID())
  ```
  Suggestion: Reject identical input and output nodes, or require a clear explicit overwrite confirmation; consider protecting other existing output volumes as well.
- claude on re-check: **real: yes, minor**: MRtoCT/MRtoCT.py:289-294 and onApply 146-150 have no check that outputVolume differs from inputVolume, so choosing the MR as output overwrites its voxels in the scene. It needs a deliberate user selection, and it only changes the in-memory node. The original file on disk is not touched unless the user saves over it. Slicer modules commonly allow in-place output. This is an ordinary usability/soundness issue and not a concrete path to harm, so it is minor and not a safety blocker. A guard or warning would be a sensible fix.
- gpt on re-check: **real: yes, blocking**: MRtoCT/MRtoCT.py:74-75 and 85-86 give both selectors the same node type: "self.inputSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']" and "self.outputSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']". Lines 135-158 pass the selected nodes to process without checking that they differ. At lines 291-294 the result is written in place: "slicer.util.updateVolumeFromArray(outputVolume, sct)". If the same node is selected, successful inference replaces the in-scene MR voxels; saving that node over the source could make the loss persistent. The source file is not automatically overwritten by this call. This path requires usable custom or local weights at this revision: lines 226-228 reject the configured default download URL. Reject identical nodes in both the UI and logic.
- gemini on re-check: **real: yes, minor**: In MRtoCT/MRtoCT.py lines 85-96 and 146-159, outputSelector has `noneEnabled = True` and `noneDisplay = '(Create new volume)'` by default, creating a new volume if left at None. However, if a user manually selects the same volume node in both `inputSelector` and `outputSelector`, neither `onApply()` (lines 135-163) nor `process()` (lines 265-302) checks `if inputVolume == outputVolume:`. At line 293, `slicer.util.updateVolumeFromArray(outputVolume, sct)` overwrites the in-memory MRML node's voxel array. Under the review rubric ("Do not label ordinary bugs as safety issues merely because the extension processes medical images" and "Ordinary bugs are minor or concern, not safety"), allowing an in-scene output selector to target the input node (a standard Slicer pattern unless guarded, with `(Create new volume)` as the default and without modifying files on disk unless the user later explicitly saves) is a minor soundness/usability oversight, not a blocking safety issue.

### D2. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (ok, blocking, ok)**
Ratings: claude ok, gemini ok, gpt blocking
- claude on re-check: **rating ok**: I read MRtoCT.py 135-300 and found the following. The weights download is a single GitHub release URL, and it is checked against a pinned SHA256 (lines 33-34, 250). The weights are loaded with torch.load(..., weights_only=True) (mr_to_sct.py:109). There is a license acceptance prompt before the download. PyTorch comes through PyTorchUtils. Nothing is sent from the user's machine, and I found no eval, exec, subprocess or pickle use. The input/output overwrite case (D1) is a minor soundness issue, so safety is ok.
- gpt on re-check: **rating blocking**: Safety is blocking because of D1's concrete path to unintended destruction of in-scene MR data and possible persistent loss on save. MRtoCT/MRtoCT.py:146-150 retrieves the output without an identity check, and line 293 writes it: "slicer.util.updateVolumeFromArray(outputVolume, sct)". I also inspected model loading (MRtoCT/MRtoCTLib/mr_to_sct.py:103-114, including "state = torch.load(str(weights), map_location='cpu', weights_only=True)"), the dependency and weight download paths (MRtoCT/MRtoCT.py:183-253), and the CLI file-writing path (MRtoCT/MRtoCTLib/mr_to_sct.py:226-279). The code does not itself save the replaced scene node to its original file. Exact checkout revision, Slicer runtime behavior, and external payloads were not independently verified.
- gemini on re-check: **rating ok**: Checked MRtoCT/MRtoCT.py (lines 1-346) and MRtoCT/MRtoCTLib/mr_to_sct.py (lines 1-289). There is no malicious behavior, telemetry, or unauthorized data transmission. Model weights are loaded safely with `torch.load(..., weights_only=True)` (MRtoCT/MRtoCTLib/mr_to_sct.py:109) and verified with SHA-256 on download (MRtoCT/MRtoCT.py:250-252) after explicit user confirmation of the license and download prompt (MRtoCT/MRtoCT.py:38-45, 140, 174-181). D1 is a minor UI/soundness check omission on in-memory MRML nodes rather than a safety vulnerability. Therefore, the safety rating is `ok`.


## Findings all reviewers agree on

### Default weights download always fails because of a leftover placeholder guard
major; soundness; raised by claude, gemini, gpt
- **claude** (major, high confidence, quote verified) [`MRtoCT/MRtoCT.py:227`](https://github.com/kgiraldo09/SlicerMRtoCT/blob/15d5db4e8ad533a82015c0178e4cd8d78600fdf7/MRtoCT/MRtoCT.py#L227): downloadWeights raises 'WEIGHTS_URL is not set' whenever the URL contains 'kgiraldo09'. The real URL is on github.com/kgiraldo09/…, so the check always fires. A user who installs from the catalog and does not supply custom weights or a local file gets an error every time. The advertised workflow therefore does not work. It also means the download and checksum path was never exercised.
  ```
          if 'kgiraldo09' in WEIGHTS_URL:
              raise RuntimeError('WEIGHTS_URL is not set in MRtoCT.py (see README, step 3).')
  ```
  Suggestion: Remove the placeholder check, or compare against an explicit empty or placeholder constant. Confirm that the release asset exists and matches WEIGHTS_SHA256.
- **gemini** (major, high confidence, quote verified) [`MRtoCT/MRtoCT.py:227`](https://github.com/kgiraldo09/SlicerMRtoCT/blob/15d5db4e8ad533a82015c0178e4cd8d78600fdf7/MRtoCT/MRtoCT.py#L227): In `MRtoCTLogic.downloadWeights`, the check `if 'kgiraldo09' in WEIGHTS_URL:` always evaluates to `True` because `WEIGHTS_URL` is `'https://github.com/kgiraldo09/SlicerMRtoCT/releases/download/v1.0/best_net_G_A.pth'`. As a result, any user running the module for the first time without providing custom weights or manually placing `best_net_G_A.pth` in the module directory will get a `RuntimeError` and the model weights will never be downloaded.
  ```
          if 'kgiraldo09' in WEIGHTS_URL:
              raise RuntimeError('WEIGHTS_URL is not set in MRtoCT.py (see README, step 3).')
  ```
  Suggestion: Remove this placeholder check, or check for an actual placeholder string (such as `'YOUR_USERNAME'` or `not WEIGHTS_URL`).
- **gpt** (minor, high confidence, quote verified) [`MRtoCT/MRtoCT.py:226`](https://github.com/kgiraldo09/SlicerMRtoCT/blob/15d5db4e8ad533a82015c0178e4cd8d78600fdf7/MRtoCT/MRtoCT.py#L226): The configured URL at line 33 contains kgiraldo09, so every fresh installation without custom or cached weights raises this error before attempting the documented download. The included test bypasses this path using custom weights.
  ```
      def downloadWeights(self, target):
          if 'kgiraldo09' in WEIGHTS_URL:
              raise RuntimeError('WEIGHTS_URL is not set in MRtoCT.py (see README, step 3).')
  ```
  Suggestion: Replace the placeholder check with a valid configuration check and add a test for the default model resolution and download path.


## Findings from some reviewers

### Catalog entry tracks the moving branch 'main'; weights asset unverified
minor; packaging; raised by claude
- **claude** (minor, medium confidence, quote no quote) no file cited: The scm_revision is a branch, so what users get can change after review. The weights are loaded from a separate GitHub release, and I could not verify that asset is published. Without it, the module cannot run for catalog users.
  Suggestion: Pin the catalog entry to a commit or tag, and make sure the v1.0 release asset is public.

### Non-commercial license and leftover template text
minor; license; raised by claude, gemini
- **claude** (minor, medium confidence, quote verified) [`LICENSE.txt:13`](https://github.com/kgiraldo09/SlicerMRtoCT/blob/15d5db4e8ad533a82015c0178e4cd8d78600fdf7/LICENSE.txt#L13): CC BY-NC 4.0 allows distribution but excludes commercial use, including by clinics or companies. The LICENSE.txt header still carries an unedited instruction line. Creative Commons recommends against using its licenses for software.
  ```
  (Paste the full legal code below: https://creativecommons.org/licenses/by-nc/4.0/legalcode.txt)
  ```
  Suggestion: Remove the template line. Consider a software license for the code, and clearly document the weights' terms and training data provenance.
- **gemini** (info, high confidence, quote verified) [`LICENSE.txt:4`](https://github.com/kgiraldo09/SlicerMRtoCT/blob/15d5db4e8ad533a82015c0178e4cd8d78600fdf7/LICENSE.txt#L4): Both the extension code and the model weights are licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0). This permits non-commercial distribution via the Slicer Extensions Index, and the module clearly prompts users to accept the non-commercial and research-only terms before first use (`MRtoCT/MRtoCT.py` lines 38-45, 174-181). Users in commercial settings should be aware of this restriction.
  ```
  This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International
  License (CC BY-NC 4.0). Full license text: https://creativecommons.org/licenses/by-nc/4.0/legalcode
  ```
  Suggestion: No action required; the non-commercial and research-only terms are already clearly disclosed in `CMakeLists.txt`, `README.md`, `LICENSE.txt`, and an in-app confirmation dialog.

### Output can overwrite the input volume; inference runs on the GUI thread
minor; soundness; raised by claude, gpt
- **claude** (minor, medium confidence, quote verified) [`MRtoCT/MRtoCT.py:146`](https://github.com/kgiraldo09/SlicerMRtoCT/blob/15d5db4e8ad533a82015c0178e4cd8d78600fdf7/MRtoCT/MRtoCT.py#L146): outputSelector accepts any scalar volume, including the input MR. updateVolumeFromArray would then replace the MR with the sCT. Inference with 0.8 overlap on 128^3 windows blocks the UI, and progress is only a 'Running...' label. The download via urlretrieve has no timeout.
  ```
          outputVolume = self.outputSelector.currentNode()
          if outputVolume is None:
  ```
  Suggestion: Reject output == input. Consider progress reporting or a background thread, and add a network timeout.
- **gpt** (minor, high confidence, quote verified) [`MRtoCT/MRtoCT.py:152`](https://github.com/kgiraldo09/SlicerMRtoCT/blob/15d5db4e8ad533a82015c0178e4cd8d78600fdf7/MRtoCT/MRtoCT.py#L152): The button handler calls processing synchronously, and the sliding-window inference loop does not process events or report progress. Large volumes or CPU inference can leave Slicer unresponsive for a prolonged period.
  ```
          self.statusLabel.text = 'Running...'
          slicer.app.processEvents()
          try:
              with slicer.util.tryWithErrorDisplay('Synthetic CT generation failed.', waitCursor=True):
                  device, seconds = self.logic.process(
                      inputVolume, outputVolume, customWeights, useGPU=self.gpuCheckBox.checked,
  ```
  Suggestion: Run the computation off the GUI thread and provide progress and cancellation while keeping MRML updates on the main thread.

### Limited validation evidence for the model
info; utility; raised by claude, gpt
- **claude** (info, medium confidence, quote verified) [`README.md:38`](https://github.com/kgiraldo09/SlicerMRtoCT/blob/15d5db4e8ad533a82015c0178e4cd8d78600fdf7/README.md#L38): The citation is 'Paper in preparation'. Dataset and validation metrics are not documented. The research-only disclaimer is present and clear, which mitigates clinical risk.
  ```
  Paper in preparation
  ```
  Suggestion: Document the training data, performance, and limits (brain MR only, sequence and contrast assumptions).
- **gpt** (info, high confidence, quote verified) [`README.md:36`](https://github.com/kgiraldo09/SlicerMRtoCT/blob/15d5db4e8ad533a82015c0178e4cd8d78600fdf7/README.md#L36): The README identifies the model but does not describe its training data or report validation results, making it difficult for researchers to assess its suitability for their data. It appropriately warns that the result is not clinically validated.
  ```
  ## Citation
  
  Paper in preparation
  ```
  Suggestion: Document training-data provenance, intended input population and available quantitative validation when they can be shared.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I read all the source in the repository at the listed commit. I found no malicious behavior, telemetry, or unsafe deserialization. The weights download is gated by license acceptance, is SHA-256 checked, and loads with weights_only=True. PyTorch comes through the PyTorch extension, and the CMake and catalog dependencies match. The main defect is functional: downloadWeights refuses to run because the real URL contains "kgiraldo09", so the default model can never be fetched. The license is CC BY-NC 4.0, which permits distribution but restricts commercial use. Validation evidence for the model is thin (paper in preparation). I could not check that the release asset exists. Recommendation: 🔴 Do not merge yet, pending the download fix and confirmation that the weights asset is published.
Not checked: Whether the release asset v1.0/best_net_G_A.pth exists and matches the SHA-256; Actual runtime behavior in Slicer, since nothing could be run; The contents of the icon file under MRtoCT/Resources/Icons (the folder holds 1 file, presumably MRtoCT.png); The model's training data and licensing, and its quality; Whether the catalog JSON passes the index CI checks

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
MRtoCT is a clean, well-structured extension for brain MR-to-synthetic-CT translation using a pure-PyTorch 3D ResNet generator. It follows Slicer best practices: it uses `PyTorchUtils` for PyTorch, avoids heavy imports at startup, verifies downloaded weights with SHA-256, loads weights safely with `weights_only=True`, and clearly discloses its CC BY-NC 4.0 and research-only terms. One major non-blocking bug should be fixed by the author: `MRtoCTLogic.downloadWeights` (`MRtoCT/MRtoCT.py:227-228`) still checks `if 'kgiraldo09' in WEIGHTS_URL:`, which matches the configured `WEIGHTS_URL` and raises a `RuntimeError` whenever automatic weight download is triggered. Under the Extensions Index admission policy (safety, license, and catalog entry requirements all met), 🟢 Recommend merge.
Not checked: Availability and SHA-256 checksum of the remote model weights asset at https://github.com/kgiraldo09/SlicerMRtoCT/releases/download/v1.0/best_net_G_A.pth (no network access in review environment).
Questions for the author: Could you remove the leftover `if 'kgiraldo09' in WEIGHTS_URL:` check in `MRtoCT/MRtoCT.py` (lines 227-228) so that the first-run download of `best_net_G_A.pth` from your GitHub release works?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The module can overwrite its input MR in place without warning if the same volume is selected as output. Its default model download also always fails because a placeholder check matches the configured URL; that functionality issue is non-blocking under the index policy. Licensing permits non-commercial distribution. 🔴 Do not merge yet: prevent unintended input-volume destruction. Review is also incomplete because the source revision and model asset could not be independently verified.
Not checked: Could not independently access the repository to verify that the supplied files correspond to commit 15d5db4e8ad533a82015c0178e4cd8d78600fdf7 or that the catalog's main branch resolves to it.; Could not fetch or inspect the external model asset, verify its availability or SHA-256, or independently assess its provenance.; Could not run Slicer, build the extension, execute tests, or inspect CI results.; Could not inspect the submission checklist or prior review baseline.


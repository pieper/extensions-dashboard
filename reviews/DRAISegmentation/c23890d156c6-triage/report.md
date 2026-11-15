# AI review: DRAISegmentation

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/DeepReasoningAI/SlicerDRAISegmentation.git at commit `c23890d156c643b1afa48a3e0854ae9b0e377a09`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:48:38Z; cost $0.02

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | blocking | ok | concern |
| environment | ok | ok | ok |
| packaging | ok | ok | ok |
| license | minor | ok | ok |
| soundness | concern | ok | concern |
| utility | concern | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer module that sends a loaded CT/CTA volume to the vendor's cloud service (DRAI) for AI segmentation of spine/pelvis or aorta-iliac-femoral arteries, then downloads the label map, imports it as a segmentation and builds closed surface models. Intended for clinicians/engineers doing spine, pelvic and vascular segmentation and 3D modeling.
- **flash-lite**: DRAISegmentation is a 3D Slicer extension that provides AI-powered segmentation and 3D surface modeling for Spine/Pelvis CT and Aorta-Iliac-Femoral CTA by uploading volumes to the Deep Reasoning AI cloud server.
- **haiku**: A 3D Slicer scripted module that uploads a selected CT/CTA volume to a remote DRAI server for AI segmentation, then loads the returned label map as a segmentation with a closed-surface 3D model. It is for clinicians and researchers who want cloud-based spine/pelvis and aorta-iliac-femoral segmentation.

## Disagreements (start here)

### D1. Patient CT volumes uploaded over unencrypted HTTP to a hard-coded IP address
partial; category safety; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:33`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L33): submitJob (lines 441-461) and downloadResult (lines 481-495) POST/GET against this URL, so the exported NIfTI of the patient's CT and the returned segmentation cross the public internet in cleartext. Anyone on the network path (clinic Wi-Fi, ISP, hosting provider) can read or modify the images and the returned mask. The module's own help text (line 59) and README.md:60-62 tell users data is 'securely processed', which is not true of plain HTTP, so consent is not fully informed. There is also no TLS certificate to authenticate the server, so a spoofed endpoint could return arbitrary label maps that a clinician would then use.
  ```
  DEFAULT_SERVER_URL = "http://209.20.158.219:8000"
  ```
  Suggestion: Serve the API over HTTPS with a real hostname and a valid certificate, make that the default, and reject non-HTTPS URLs in setServerUrl (or warn explicitly). Update the privacy text to state the actual transport and destination.
- **haiku** (major, high confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:33`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L33): The default server is plain HTTP on a raw IP, so the full medical image and the X-Device-ID header travel unencrypted and can be read or altered by anyone on the network path. This conflicts with the description claiming data is 'securely processed'. A user following the documented workflow sends PHI over an unauthenticated channel, and the server identity is never verified. The server should be served over HTTPS with a stable hostname, and the default should not be a bare IP.
  ```
  DEFAULT_SERVER_URL = "http://209.20.158.219:8000"
  ```

### D2. Blocking network I/O on the GUI thread freezes Slicer during upload, download and polling
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified, other lines) [`DRAISegmentation/DRAISegmentation.py:409`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L409): _onRunClicked calls submitJob directly on the GUI thread with timeout=300; a large CT upload can block the whole application for minutes with no progress and no way to cancel (the Cancel button cannot be clicked while the event loop is blocked). _pollStatus (line 294) likewise performs a 15 s-timeout GET every 5 s on the GUI thread, and downloadResult blocks for up to 300 s.
  ```
          if HAS_REQUESTS:
              with open(niftiPath, "rb") as f:
                  resp = requests.post(
                      url,
                      files={"file": (os.path.basename(niftiPath), f, "application/gzip")},
                      data={"model": model},
  ```
  Suggestion: Move upload/download to a worker thread (e.g. ctk.QLabel or a QThread/QRunnable) and report progress via signals; keep only the timer-driven status check on the GUI thread with a short timeout.

### D3. Exported patient volumes and downloaded results are left in temp folders indefinitely
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:431`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L431): exportVolume and downloadResult (line 483, 'tempfile.mkdtemp(prefix="drai_result_")') create directories that are never removed, so a copy of the patient's CT and the segmentation stay on disk after the session, on shared or multi-user machines too. This contradicts the 'No data is retained' statement shown to users (lines 172-173) and leaves PHI-derived files behind.
  ```
          tmpDir = tempfile.mkdtemp(prefix="drai_")
          filename = "volume.nii.gz"
          filepath = os.path.join(tmpDir, filename)
  ```
  Suggestion: Use a TemporaryDirectory owned by the widget/logic and delete it after the result is loaded (and on cancel/cleanup), or write into slicer.app.temporaryPath with explicit cleanup.
- **haiku** (minor, high confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:431`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L431): Each run writes the input CT to a new mkdtemp directory and writes the result to another, and neither is removed afterwards. Medical images are left in the user's temp folder, which conflicts with the 'no data retained' messaging. Users on shared machines may expose PHI. The code should delete these directories after upload and after loading, for example with shutil.rmtree in a finally block.
  ```
  tmpDir = tempfile.mkdtemp(prefix="drai_")
          filename = "volume.nii.gz"
          filepath = os.path.join(tmpDir, filename)
  ```

### D4. No terms of service or privacy policy for the cloud service that receives patient data
single; category license; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`README.md:58`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/README.md#L58): The extension's core function is a remote service, but the repository contains only the BSD-3 code license; there is no link to service terms, a privacy policy, a data-processing agreement, or any statement of who operates 209.20.158.219 and under which jurisdiction data is handled. Users (and their institutions) have no documented basis for the retention/deletion claims made in the UI, and no way to verify them.
  ```
  ## Data Privacy
  
  - Your CT volume is uploaded to the DRAI server **only** for the duration of the segmentation
  - All uploaded images are **deleted from the server immediately** after segmentation is complete
  ```
  Suggestion: Publish and link service terms and a privacy policy covering upload, retention, deletion, subprocessors and jurisdiction, and reference them from the consent dialog and README.

### D5. Persistent device identifier sent to the vendor server automatically on module open, without consent
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:400`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L400): DRAISegmentationWidget.setup() calls self.logic.ensureDeviceRegistered() (line 90) as soon as the module panel is opened, which POSTs a UUID persisted in QSettings (getDeviceId, lines 379-386) to /api/v1/register. This happens before, and independently of, the consent dialog at line 226, so merely opening the module contacts a third-party server and transmits a stable per-installation identifier. The consent dialog and privacy notice never mention this registration.
  ```
      def ensureDeviceRegistered(self):
          key = f"{SETTINGS_KEY_PREFIX}/DeviceRegistered"
          if self._settings.value(key, "false") == "true":
              return
  ```
  Suggestion: Do not contact the server until the user has consented; fold registration into the first consented job submission, or ask explicitly. Disclose the device identifier in the privacy notice.
- **haiku** (major, high confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:89`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L89): setup() calls ensureDeviceRegistered(), which POSTs a generated UUID to the remote server as soon as the module GUI is created. The consent dialog only appears when the user clicks Run. This sends an identifier off the machine without opt-in, and the UUID persists in QSettings and is sent on every later request as X-Device-ID. The registration should happen only after consent or be clearly disclosed in the privacy notice.
  ```
  self.logic = DRAISegmentationLogic()
          self.logic.ensureDeviceRegistered()
  ```

### D6. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku concern

### D7. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D8. Rating of utility
rating dispute; category utility; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### Cancel only stops polling; server job and job state are not cleaned up
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:257`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L257): The remote job keeps running and its result is never fetched or deleted, so the server retains a job (and, per the vendor's claim, the uploaded volume until it finishes) after the user believes they cancelled. The timeout path in _pollStatus (lines 300-306) likewise leaves _currentJobId set.
  ```
      def _onCancelClicked(self, _checked):
          self._stopPolling()
          self._currentJobId = None
          self._setUIIdle()
          self.statusLabel.text = "Cancelled by user."
  ```
  Suggestion: Send a cancel/delete request to the API on cancel and on timeout, and clear _currentJobId in all terminal paths.
- **haiku** (minor, medium confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:257`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L257): _onCancelClicked only stops local polling. The job keeps running on the server and the user is told 'Cancelled by user.' with no server-side cancel call. Separately, the 'deleted immediately' and 'no data is retained' statements in the consent text and in the description cannot be checked from this code. The client should either send a cancel request or word the message accurately, and the privacy statements should be backed by a published retention policy.
  ```
  def _onCancelClicked(self, _checked):
          self._stopPolling()
          self._currentJobId = None
  ```

### Job ID is interpolated into the request URL without escaping
minor; soundness; raised by haiku
- **haiku** (minor, low confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:465`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L465): The job_id returned by the server is inserted directly into the URL path. A malformed or hostile server response could inject path segments or query characters. The impact is limited because the server is the only source, but the value should be validated or URL-encoded.
  ```
  def getJobStatus(self, jobId: str):
          url = f"{self.getServerUrl()}/api/v1/jobs/{jobId}/status"
  ```

### No clinical-use disclaimer, regulatory status or model validation information
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:5`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/README.md#L5): The module produces anatomical labels and 3D models that a clinician may act on, but neither README nor the module help text states that output is for research/visualization only, nor gives any accuracy/validation data, training data description, or regulatory clearance status. Users cannot judge whether the output is fit for clinical decisions.
  ```
  ## Description
  
  DRAI Segmentation and 3D Modeling provides automatic, deep-learning-based segmentation of anatomical structures from CT and CTA scans and creates 3D surface models from the results.
  ```
  Suggestion: Add a clear intended-use statement (e.g. research use only unless cleared), a pointer to validation results, and a note that results must be reviewed by a qualified clinician.

### Reference geometry set after label map import may misalign the segmentation
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:505`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L505): The usual Slicer pattern is to set the reference image geometry before importing the label map so the imported segments are placed in the reference frame. Setting it afterwards can leave the segmentation in the label map's own geometry while the node claims the volume's geometry, producing a mask that does not overlay the CT. Also, loadLabelVolume's return value is not checked, so a failed load passes None into ImportLabelmapToSegmentationNode.
  ```
          slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(
              labelmapNode, segmentationNode
          )
  
          slicer.mrmlScene.RemoveNode(labelmapNode)
  
  ```
  Suggestion: Set the reference geometry on the segmentation node before importing, and raise a user-visible error if loadLabelVolume returns None.

### Test only checks that a device ID exists; no functional test or sample data
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DRAISegmentation/DRAISegmentation.py:678`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/DRAISegmentation/DRAISegmentation.py#L678): The generic test exercises none of the module's real logic (volume export, multipart encoding, error parsing, segmentation import), so regressions in those paths would go unnoticed; there is also no sample volume for users to try the module without their own patient data.
  ```
      def test_ModuleLoads(self):
          self.delayDisplay("Starting module load test")
          logic = DRAISegmentationLogic()
          self.assertIsNotNone(logic.getDeviceId())
          self.assertTrue(len(logic.getDeviceId()) > 0)
  ```
  Suggestion: Add offline unit tests for exportVolume, _postMultipart body construction and _extractApiErrorMessage, and ship a small public sample CT for a tutorial.

### Description and privacy text overstate security and the test is trivial
info; utility; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`CMakeLists.txt:12`](https://github.com/DeepReasoningAI/SlicerDRAISegmentation/blob/c23890d156c643b1afa48a3e0854ae9b0e377a09/CMakeLists.txt#L12): The CMake description says 'All data is securely processed', but the transport is plain HTTP. The only test checks that a device ID is non-empty. The README and Screenshots are reasonable, but there is no sample data, no accuracy or validation information for the models, and no clinical-use disclaimer.
  ```
  All data is securely processed and deleted immediately after inference.
  ```


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Small, readable scripted module with a clear consent dialog and no code downloads, no pip installs and no import-time side effects. However, patient CT volumes are uploaded over plain HTTP to a hard-coded bare IP address with no TLS, no published privacy policy or service terms, while the UI and README claim data is "securely processed" — a concrete path to interception of medical images. A persistent device UUID is also sent to that server automatically when the module is opened, without consent, and exported volumes/results are left indefinitely in temp folders. Packaging and the BSD-3 license are fine. Needs fixes before distribution.
Not checked: The remote service at 209.20.158.219:8000 was not contacted, so its actual behaviour (retention, deletion, authentication, whether it logs images) could not be verified — the 'deleted immediately / no data retained' claims are unverified vendor statements.; The exact source revision: the catalog entry pins scm_revision 'main' (a moving branch), so the reviewed code is the snapshot provided, not a fixed commit.; Whether the NIfTI written by slicer.util.saveNode embeds patient identifiers from DICOM metadata (e.g. in the NIfTI descrip field) — not verified.; Model weights and training data are server-side and were not available for inspection; no validation or provenance evidence exists in the repository.; No build or runtime test was performed (no execution environment).
Questions for the author: Why is the API served over plain HTTP at a bare IP address rather than HTTPS on a named host, and is there a plan to change this before release?; What exactly does /api/v1/register do with the device UUID, and why is it called when the module panel is opened rather than after the user consents?; Where are the service terms and privacy policy that back the 'deleted immediately, no data is retained' statement, and which jurisdiction processes the data?; Are uploaded NIfTI files free of DICOM patient identifiers, and is any of the upload retained for logging or model improvement?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
DRAISegmentation is a well-structured Slicer extension providing cloud-based AI segmentation for medical imaging. It features explicit user consent prior to data transmission, robust error handling, proper CMake packaging, and a clear BSD 3-Clause license. 🟢 Recommend merge
Not checked: External repository commit execution (not runnable without Slicer/network)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The code is a single, readable ScriptedLoadableModule with a BSD-3 license, a per-upload consent dialog, and no environment changes or package installs. The main concerns are about data handling: patient volumes are sent over plain HTTP to a bare IP address, a persistent device UUID is registered with the server at module setup before any consent, and exported volumes and downloaded results are left in temp directories that are never deleted. The "deleted immediately" claim cannot be verified from the client. I could not inspect the server or the catalog's CI results. Overall: needs fixes before users are directed to this for clinical data.
Not checked: The remote server (209.20.158.219) was not accessible, so the actual retention behavior, TLS support, and server-side handling of uploaded data were not verified.; The source at the catalog revision 'main' was taken from the supplied files; the exact commit was not resolved or pinned.; Model provenance, validation data, and weight licensing were not available in the repository.; No Slicer build or runtime test was possible, and no CI results were provided.; The icon image and screenshot contents were not visually inspected.


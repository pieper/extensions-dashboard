# AI review: ABLTemporalBoneSegmentation

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation at commit `227bc565ddec65509bac6dcbbddd6c02e718eaeb`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-17T03:16:13Z; cost $0.78

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | concern | blocking |
| environment | unknown | blocking | blocking |
| packaging | unknown | concern | unknown |
| license | unknown | ok | unknown |
| soundness | unknown | concern | concern |
| utility | unknown | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: Slicer extension for CT temporal bone scans. It guides fiducial and Elastix rigid registration against an atlas, ROI cropping, and deep-learning segmentation (via the ABLInfer package, run in local Docker or on a remote server). It also exports results for CardinalSim and includes a batch registration module.
- **gemini**: ABLTemporalBoneSegmentation provides 3D Slicer modules for preprocessing, atlas-based fiducial and rigid registration, and deep-learning segmentation of CT temporal bone scans, along with batch intra-sample registration. It is intended for otolaryngology researchers and clinicians working with temporal bone CT imagery and CardinalSim surgical simulation exports.
- **gpt**: This extension prepares and segments temporal-bone CT scans using landmark and rigid registration followed by local Docker or remote inference. It also provides batch registration and export tools for researchers working with temporal-bone images.

## Disagreements (start here)

### D1. Cancelling export can delete or overwrite files in the current directory
severity dispute; category safety; raised by gemini, gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gemini** (minor, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1038`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L1038): If the user cancels the `QFileDialog.getExistingDirectory` dialog, `target` is an empty string `""`. `export_for_cardinalsim` then calls `os.path.abspath("")`, which resolves to the current working directory, and proceeds to write files and `shutil.rmtree(os.path.join(directory, volume.GetName() + "_dicom"))` in the current working directory instead of aborting.
  ```
          target = qt.QFileDialog.getExistingDirectory(None, "Choose an output directory *MUST BE EMPTY*")
          ABLTemporalBoneSegmentationModuleLogic.export_for_cardinalsim(self.movingSelector.currentNode(), self.exportSelector.currentNode(), target)
  ```
  Suggestion: Check `if not target: return` before calling `export_for_cardinalsim`.
- **gpt** (blocking, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1038`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L1038): Cancelling the directory dialog returns an empty path, but the export proceeds. Lines 1390–1396 turn it into the process working directory and recursively remove an existing volume-named DICOM folder; lines 1449–1453 can overwrite label files there. The empty-directory warning does not protect a user who cancels.
  ```
          target = qt.QFileDialog.getExistingDirectory(None, "Choose an output directory *MUST BE EMPTY*")
          ABLTemporalBoneSegmentationModuleLogic.export_for_cardinalsim(self.movingSelector.currentNode(), self.exportSelector.currentNode(), target)
  ```
  Suggestion: Return immediately on cancellation, validate that the selected directory is empty, and refuse to remove or overwrite existing files without explicit confirmation.
- claude on re-check: **real: yes, major**: Lines 1038-1039 pass the dialog result to export_for_cardinalsim without checking for an empty string. A cancelled dialog returns "". Line 1390 `os.path.abspath("")` then gives the working directory. Lines 1394-1395 rmtree `<volume>_dicom` there if it exists, and lines 1449-1453 overwrite `<volume>_<name>-label.nrrd` files there. The damage is limited to paths named after the volume, so I rate it major, not blocking. Even a deliberately chosen directory has its `<volume>_dicom` subfolder deleted.
- gpt on re-check: **rating blocking**: ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1038-1039 passes the dialog result without a cancellation check: 'target = qt.QFileDialog.getExistingDirectory(None, "Choose an output directory *MUST BE EMPTY*")'. Lines 1390-1395 then execute 'directory = os.path.abspath(directory)' and 'shutil.rmtree(dicom_dir)' when the volume-named directory exists. Cancellation thus targets the current working directory and can delete an existing folder; lines 1449-1453 can overwrite matching output files. This is a concrete unintended data-loss path.
- gemini on re-check: **real: yes, major**: Checked ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1038-1039 and 1390-1396, 1449-1453. If the user cancels QFileDialog.getExistingDirectory, target is "", os.path.abspath("") resolves to the current working directory, shutil.rmtree removes {volume.GetName()}_dicom if present, and segment .nrrd files are written into the current working directory. However, because it only deletes a folder literally named "<volume_name>_dicom" and writes "<volume_name>_<segment>-label.nrrd" rather than wiping the directory itself, the risk of destructive data loss is limited, making it a major issue rather than blocking.

### D2. Remote inference disables certificate verification
partial; category safety; raised by gemini, gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:932`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L932): When using remote inference, TLS certificate verification is unconditionally disabled (`s.verify = False`), and the user's password is saved in plaintext in Slicer's `QSettings` (`ablinfer_server_password`), while `self.inferServerPassword` is also a plain `qt.QLineEdit()` without `Password` echo mode. Disabling TLS verification exposes credentials and medical image payloads to man-in-the-middle interception, and storing passwords in plaintext settings exposes them on disk.
  ```
              ## Setup the session
              s = requests.Session()
              s.verify = False
              if username:
                  s.auth = (username, password)
                  settings.setValue("ablinfer_server_username", username) 
  ```
  Suggestion: Enable TLS verification by default (or provide an explicit opt-in checkbox for self-signed certificates), set `self.inferServerPassword.setEchoMode(qt.QLineEdit.Password)`, and avoid persisting plaintext passwords in `QSettings`.
- **gpt** (blocking, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:932`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L932): When users run remote inference over HTTPS, an on-path attacker can impersonate the configured server, intercept credentials and scan data, and alter responses. The UI also gives an HTTP URL as an example, permitting unencrypted use.
  ```
              ## Setup the session
              s = requests.Session()
              s.verify = False
              if username:
                  s.auth = (username, password)
  ```
  Suggestion: Require HTTPS and certificate verification, allow a user-provided CA for private servers, and reject insecure endpoints.
- claude on re-check: **real: yes, major**: Line 934 sets `s.verify = False` unconditionally, and line 935 sends the basic-auth credentials over that session. This allows man-in-the-middle interception of credentials and scan data, and there is no user option to turn verification on. It affects only the optional remote-inference path, so I rate it major.
- gpt on re-check: **rating blocking**: ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:932-941 sets 's.verify = False', adds credentials with 's.auth = (username, password)', and passes that session to the remote dispatcher. Lines 959-963 supply the selected volume for inference; lines 354-355 also give an HTTP example. A network attacker can impersonate an HTTPS server or intercept HTTP traffic and expose credentials and medical data. The external ablinfer implementation was not available to inspect, so the exact wire payload was not independently verified.
- gemini on re-check: **real: yes, major**: Checked ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:355, 932-938. In click_infer_apply, s = requests.Session(); s.verify = False unconditionally disables TLS certificate verification when communicating with the remote inference server, and line 355 gives an http:// URL example. Disabling TLS verification exposes medical image data and user credentials to MitM interception. Because remote server mode is an optional user-configured feature (local Docker is default), this is a major safety concern (or blocking under strict TLS verification standards, rated major here as user-configured server).

### D3. Unconditional pip_install("ablinfer") executed at module import / Slicer startup
partial; category environment; raised by gemini, gpt; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (blocking, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:23`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L23): When Slicer starts up and imports scripted modules, `ABLTemporalBoneSegmentationModule.py` runs `slicer.util.pip_install("ablinfer")` at top-level module import time without user confirmation. This modifies Slicer's shared Python environment and triggers network downloads during Slicer startup even for users who never open the module.
  ```
  try:
      import ablinfer
  except ModuleNotFoundError:
      slicer.util.pip_install("ablinfer")
  ```
  Suggestion: Defer importing and installing `ablinfer` (and `docker`) until the user enters the module or clicks 'Run Inference', and prompt the user for confirmation before running `slicer.util.pip_install("ablinfer")`.
- **gpt** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:23`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L23): When ablinfer is absent, importing the module downloads and installs an unpinned package and dependencies into Slicer's shared Python environment without asking. This can affect other extensions or users who did not request inference.
  ```
  try:
      import ablinfer
  except ModuleNotFoundError:
      slicer.util.pip_install("ablinfer")
  ```
  Suggestion: Install dependencies only after explicit user confirmation, and inspect their requirements for compatibility with Slicer's bundled packages.
- claude on re-check: **real: yes, blocking**: Lines 23-26 run `slicer.util.pip_install("ablinfer")` at module import, unpinned and without confirmation. This is the install-at-import behavior the policy says to request changes for. Line 28 and following lines also import ablinfer submodules and `docker` at top level, so a failed install breaks module loading.
- gpt on re-check: **rating concern**: ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:23-26 runs 'import ablinfer' and, on 'except ModuleNotFoundError:', calls 'slicer.util.pip_install("ablinfer")' at module top level, with no confirmation or version pin. When the import fails during scripted-module discovery, this can change the shared environment even for users who never open the module. It is conditional on the import failing, not literally unconditional. The package's external dependency metadata was not inspected.
- gemini on re-check: **real: yes, blocking**: Checked ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:23-26. At top-level module import (which runs during Slicer startup/module discovery), the module catches ModuleNotFoundError for ablinfer and immediately executes slicer.util.pip_install("ablinfer") without user confirmation. Per the review policy, package installation at module import or Slicer startup without user confirmation is a blocking environment issue.

### D4. Export assigns fixed anatomy names by label number rather than segment identity
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1418`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L1418): The UI permits selection of any segmentation, and the exporter converts its segments in their current order before assigning these fixed names to label values. A reordered or different segmentation can therefore be exported under incorrect anatomical filenames without warning.
  ```
          if labels is None:
              labels = {
                  1: "Sigmoid Sinus",
                  2: "Facial Nerve",
                  3: "Bony Inner Ear",
                  4: "Malleus",
  ```
  Suggestion: Map labels using verified segment names or IDs, reject unexpected or missing structures, and test reordered segments.
- claude on re-check: **real: yes, minor**: Lines 1408-1429 export all segments in their current order and assign fixed names to label values 1-9. Nothing checks segment names. A reordered or different segmentation would get wrong filenames. The export is designed for this module's own output, so I rate it minor.
- gpt on re-check: **rating concern**: ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:400-401 permits a segmentation node selection: 'self.exportSelector.nodeTypes = ["vtkMRMLSegmentationNode"]'. Lines 1412-1416 export segment IDs in their current order, while lines 1418-1429 assign fixed anatomical names to numeric values and lines 1434-1453 save by those names. A different or reordered segmentation can therefore be mislabeled. This is a serious ordinary correctness issue, not a blocking admission safety finding.
- gemini on re-check: **real: yes, major**: Checked ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:400-408 and 1408-1453. exportSelector allows selecting any vtkMRMLSegmentationNode, and export_for_cardinalsim exports all segments in index order to a labelmap and then maps integer label values 1..9 to hardcoded temporal bone structure names regardless of the actual segment names or IDs.

### D5. Fragile build-time unpinned download of ABLTempSeg.json in SuperBuild INSTALL_COMMAND
single; category packaging; raised by gemini; outcome after cross-examination: **still disputed**
- **gemini** (major, high confidence, quote verified) [`SuperBuild.cmake:38`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/SuperBuild.cmake#L38): During the SuperBuild `INSTALL_COMMAND`, CMake downloads `ABLTempSeg.json` from the `master` branch of an external repository (`Auditory-Biophysics-Lab/temporal-bone-segmentation`) and overwrites the placeholder file in the source tree. Because `INSTALL_COMMAND` runs after the inner project's configure/build/install steps (and replaces the default install command), the inner build may package the placeholder file (`you shouldn't see this, this file should be retrieved during build`) before `_download_model` runs, causing `json.load(f)` in `click_infer_apply` to fail with a `JSONDecodeError`. Furthermore, commits to `.idea/` IDE configuration files are tracked in the repository.
  ```
  ## Pull the latest model JSON file on build
  set(_download_model COMMAND ${CMAKE_COMMAND}
    -E env
    ${PYTHON_EXECUTABLE} -c "import urllib.request $<SEMICOLON> urllib.request.urlretrieve('https://raw.githubusercontent.com/Auditory-Biophysics-Lab/temporal-bone-segmentation/master/ABLTempSeg.json', '${CMAKE_CURRENT_SOURCE_DIR}/ABLTemporalBoneSegmentationModule/Resources/Models/ABLTempSeg.json')"
    )
  ```
  Suggestion: Commit a valid `ABLTempSeg.json` directly in the repository (or fetch it before configuring the inner build, pinned to a specific commit/release with a SHA256 checksum).
- claude on re-check: **real: unsure, minor**: SuperBuild.cmake lines 38-42 do download the JSON from the `master` branch at build time, unpinned and writing into the source tree. That is fragile and unreproducible. The claimed ordering failure is speculative. The outer INSTALL_COMMAND is not the inner project's install, which runs at packaging time and uses the source file. I did not verify the build order, so I rate this minor.
- gpt on re-check: **rating unknown**: SuperBuild.cmake:38-48 downloads the moving-branch JSON during the external project's install step: 'INSTALL_COMMAND ${CMAKE_COMMAND} -E echo_append ""' followed by '${_download_model}'. ABLTemporalBoneSegmentationModule/Resources/Models/ABLTempSeg.json:1 contains 'you shouldn't see this, this file should be retrieved during build', and ABLTemporalBoneSegmentationModule/CMakeLists.txt:20,24-27 lists it as a scripted-module resource. A build-tree copy could be stale, but the available files do not establish when the Slicer macro copies resources or when CPack installs them relative to the download; therefore a broken packaged artifact is not verified. No build was run.
- gemini on re-check: **real: yes, major**: Checked SuperBuild.cmake:38-49, ABLTemporalBoneSegmentationModule/CMakeLists.txt:20-29, and ABLTemporalBoneSegmentationModule/Resources/Models/ABLTempSeg.json:1. In SuperBuild.cmake, _download_model is attached to INSTALL_COMMAND of the inner ExternalProject, which runs after the inner project's build step where slicerMacroBuildScriptedModule copies Resources/Models/ABLTempSeg.json into the build tree, and also fetches an unpinned file from master during build.

### D6. Insecure-request warnings are disabled process-wide
partial; category environment; raised by gemini, gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gemini** (minor, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:37`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L37): Calling `urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)` at the top level of the module globally silences TLS certificate verification warnings across the entire Slicer Python process at startup, affecting all other modules and extensions.
  ```
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  ```
  Suggestion: Avoid globally disabling `InsecureRequestWarning` at module import time; scope warning suppression locally if unverified HTTPS requests are explicitly requested by the user.
- **gpt** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:37`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L37): Importing the module suppresses urllib3 warnings for the whole Slicer process, hiding insecure HTTPS use by this and other extensions.
  ```
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  ```
  Suggestion: Remove the global suppression and use verified connections.
- claude on re-check: **real: yes, minor**: Line 37 calls `urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)` at import. This silences that warning process-wide for all extensions and is a global side effect. It is narrow in scope, but it hides the insecure TLS use at line 934.
- gpt on re-check: **rating concern**: ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:37 runs 'urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)' at import, installing a process-wide warning filter for that warning category. This can hide warnings about unverified HTTPS in this module and other code using the same urllib3 warning class. It does not itself disable certificate verification in other sessions.
- gemini on re-check: **real: yes, minor**: Checked ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:37. At top-level import time, urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) is called, which globally suppresses InsecureRequestWarning across the entire Slicer Python process for all modules. This is a real global side effect at import time, though minor in severity compared to pip_install at import.

### D7. Remote credentials are displayed and persisted in application settings
single; category safety; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:935`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L935): Remote server passwords are stored as ordinary Slicer settings and are restored into a normal QLineEdit at lines 357–364, exposing them to anyone who can read the settings or see the screen.
  ```
              if username:
                  s.auth = (username, password)
                  settings.setValue("ablinfer_server_username", username) 
                  settings.setValue("ablinfer_server_password", password)
  ```
  Suggestion: Mask the password field and avoid persisting credentials, or use an operating-system credential store with explicit consent.
- claude on re-check: **real: yes, minor**: Lines 936-938 save the username and password to QSettings in plaintext. Line 363 restores the password into a plain `qt.QLineEdit()` created at line 357, and a search found no EchoMode setting. The password is therefore shown on screen and stored unencrypted, but the save only happens when the user fills in a username and runs remote inference. This is a credential-hygiene weakness, not exfiltration.
- gpt on re-check: **rating concern**: ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:935-938 stores the password with 'settings.setValue("ablinfer_server_password", password)' when a username is entered. Lines 357-364 create an ordinary QLineEdit and restore the setting: 'self.inferServerPassword.text = settings.value("ablinfer_server_password") or ""'. No password echo mode is configured in the inspected source, exposing it on screen and as an ordinary application setting; exact on-disk permissions depend on the platform.
- gemini on re-check: **real: yes, major**: Checked ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:357-364 and 935-938. self.inferServerPassword is a standard qt.QLineEdit() without Password echo mode, displaying the password in cleartext in the UI, and settings.setValue("ablinfer_server_password", password) persists it in cleartext in Slicer's QSettings file.

### D8. Use of removed Slicer 4 AnnotationROI and legacy MarkupsFiducial APIs
single; category soundness; raised by gemini; outcome after cross-examination: **still disputed**
- **gemini** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:824`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L824): `vtkMRMLAnnotationROINode` was deprecated and removed in Slicer 5 in favor of `vtkMRMLMarkupsROINode`, and `Fiducial_L.fcsv` / `Fiducial_R.fcsv` use legacy markups format along with removed `vtkMRMLMarkupsFiducialNode` APIs (`GetNumberOfFiducials`, `GetNthFiducialLabel`, `GetNthFiducialPosition`). In Slicer 5, Step 1 (Fiducial Registration) and Step 3 (ROI cropping) will fail with attribute/class errors.
  ```
          self.roiNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLAnnotationROINode')
  ```
  Suggestion: Migrate from `vtkMRMLAnnotationROINode` to `vtkMRMLMarkupsROINode` and update `vtkMRMLMarkupsFiducialNode` calls to the Slicer 5 control point API (`GetNumberOfControlPoints`, `GetNthControlPointLabel`, `GetNthControlPointPosition`).
- claude on re-check: **real: unsure, minor**: Line 824 does use `vtkMRMLAnnotationROINode`, which newer Slicer versions no longer provide. Crop Volume expects a Markups ROI, so this likely breaks cropping on current Slicer. I did not verify the target Slicer version. The claim about the fiducial APIs is wrong, because `GetNumberOfFiducials`, `GetNthFiducialLabel` and `GetNthFiducialPosition` (lines 746-768, 1181-1271) still exist on vtkMRMLMarkupsFiducialNode in Slicer 5. The legacy `.fcsv` format is also still readable. This is an ordinary compatibility bug limited to the ROI crop step.
- gpt on re-check: **rating unknown**: ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:824 does request 'vtkMRMLAnnotationROINode', and lines 745-747 and 765-768 use legacy fiducial methods. ABLTemporalBoneSegmentationModule/Resources/Atlases/Fiducial_L.fcsv:1 says '# Markups fiducial file version = 4.10'. These establish use of old APIs and data format, but not that the node class or compatibility methods are absent in the target Slicer 5 build, nor that the old file format cannot load. Slicer source/runtime was unavailable, so the claimed failures cannot be verified.
- gemini on re-check: **real: yes, major**: Checked ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:753-768, 824, 1181-1183, 1266-1276, and Resources/Atlases/Fiducial_L.fcsv:1-8. Line 824 calls slicer.mrmlScene.AddNewNodeByClass('vtkMRMLAnnotationROINode'), which was removed in Slicer 5 (replaced by vtkMRMLMarkupsROINode), causing Step 3 cropping to fail in Slicer 5. Lines 753-768, 1181-1183, 1266-1276 also use removed Slicer 4 MarkupsFiducial methods (GetNumberOfFiducials, GetNthFiducialLabel, GetNthFiducialPosition, AddFiducialFromArray, SetNthFiducialVisibility).


## Findings from some reviewers

### ElastixLogic instantiated at class definition (import) time
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`IntraSampleRegistration/IntraSampleRegistration.py:99`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/IntraSampleRegistration/IntraSampleRegistration.py#L99): Both `IntraSampleRegistrationWidget` (line 100) and `ABLTemporalBoneSegmentationModuleWidget` (line 151) instantiate `Elastix.ElastixLogic()` in the class body rather than inside `__init__` or `setup()`. This executes `ElastixLogic()` at module import time during Slicer startup, slowing startup and risking initialization order issues if `Elastix` is not yet loaded.
  ```
      # Registration logic nodes
      elastixLogic = Elastix.ElastixLogic()
      brainsCliLogic = None
  ```
  Suggestion: Instantiate `Elastix.ElastixLogic()` inside `__init__` or lazily when registration is run rather than at class definition time.

### Remote model retrieval error handler references an unimported name
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1366`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L1366): The module does not import logging, so a failed remote model lookup raises NameError instead of logging the failure and continuing with the local model as intended.
  ```
          if get_model and isinstance(dispatch, DispatchRemote): ## Try to retrieve the model from the remote server
              try:
                  model = dispatch.get_model(model["id"])
              except Exception as e:
                  logging.warning("Encountered an error retrieving model from remote: " + str(e))
  ```
  Suggestion: Import logging and test the remote lookup failure path.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
The extension is BSD-3 licensed, the catalog entry's build dependencies match CMake, and the atlas download is checksummed. Three problems stand out. First, the module runs pip_install("ablinfer") at import time, unpinned and without asking. Second, the build downloads Resources/Models/ABLTempSeg.json from a mutable master branch into the source tree, and the committed file is only a placeholder. Third, the remote-inference path disables TLS verification, stores the password in plain text in the settings, and uploads volumes with no explicit data-transfer notice. There are also soundness bugs, such as an unimported logging module and Elastix instantiated at class-definition time. I could not inspect ablinfer itself.

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
ABLTemporalBoneSegmentation provides a comprehensive workflow for registering and segmenting temporal bone CT scans and exporting results to CardinalSim, licensed under BSD-3-Clause.

🔴 Do not merge yet: `ABLTemporalBoneSegmentationModule.py` runs `slicer.util.pip_install("ablinfer")` unconditionally at top-level module import (Slicer startup) without user confirmation, which violates the Slicer Extensions Index environment policy. Additionally, non-blocking but important issues should be addressed: remote inference disables TLS verification (`s.verify = False`) and stores passwords in plaintext in `QSettings`, `SuperBuild.cmake` fetches `ABLTempSeg.json` in `INSTALL_COMMAND` over an invalid placeholder file, and Slicer 4 legacy APIs (`vtkMRMLAnnotationROINode`, `GetNumberOfFiducials`) are used.
Not checked: External PyPI package `ablinfer` source code and its transitive dependencies (not in repository); External repository `Auditory-Biophysics-Lab/temporal-bone-segmentation` release assets (`Atlas_L.mha`, `Atlas_R.mha`), remote `ABLTempSeg.json`, and Docker container image contents/licenses
Questions for the author: What are the dependencies of the `ablinfer` PyPI package, and can its installation be moved from module import time to an explicit user-confirmed action when running inference?; What license applies to the downloaded atlas volumes (`Atlas_L.mha`, `Atlas_R.mha`) and the deep learning model/container referenced by `ABLTempSeg.json`?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The reviewed source has concrete safety issues: remote inference disables TLS verification, and cancelling an export can write to or delete files in the current directory. It also installs a Python package at import without consent. External inference code, model configuration and asset licenses were not available for inspection, and the catalog’s moving revision was not independently resolved. 🔴 Do not merge yet: fix the security and data-loss issues and complete the external-payload and revision review.
Not checked: The supplied source is identified by the user as commit 227bc565ddec65509bac6dcbbddd6c02e718eaeb; no independent Git resolution or verification that catalog branch master selects it was available.; The build fetches a mutable model JSON from another repository (SuperBuild.cmake:38–48); the actual generated configuration, its image or weights, integrity, and distribution terms could not be inspected.; The ablinfer package, its dependency tree and remote/local dispatch implementation, the atlas release assets and their license terms were not available to inspect.; No Slicer execution, build, tests, network access, CI results, or comparison with a previously reviewed source revision were available.


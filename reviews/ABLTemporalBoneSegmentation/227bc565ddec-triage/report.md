# AI review: ABLTemporalBoneSegmentation

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation at commit `227bc565ddec65509bac6dcbbddd6c02e718eaeb`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T10:32:38Z; cost $0.05

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | concern |
| environment | blocking | ok | concern |
| packaging | concern | ok | minor |
| license | minor | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer extension for segmenting temporal-bone structures in CT: it resamples and rigidly registers a user's scan to a left/right atlas (fiducial + Elastix), crops an ROI, then runs a deep-learning model either in a local Docker container or on a remote ABLInfer server, and exports results for CardinalSim. It also ships a second module for batch intra-sample registration.
- **flash-lite**: The ABLTemporalBoneSegmentation extension provides deep-learning segmentation and pre-processing tools for temporal bone CT scans, including fiducial registration, rigid registration, resampling, and inference dispatch (local Docker or remote server).
- **haiku**: Provides a Slicer module for temporal bone CT preprocessing (resampling, fiducial and Elastix rigid registration, ROI cropping), remote or Docker-based deep-learning segmentation via ABLInfer, rendering, and CardinalSim export, plus a batch registration module. It is for ABL/Western University researchers and clinical-research users working with temporal bone CT.

## Disagreements (start here)

### D1. `ablinfer` is pip-installed at module import, unpinned, without user consent
severity dispute; category environment; raised by deepseek, flash-lite, haiku
- **deepseek** (blocking, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:23`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L23): Slicer imports every installed module's script at startup to discover its classes, so this installs a package from PyPI into Slicer's shared Python on first start after installation, for every user, with no prompt, no version pin and no record. It also drags in `docker`/`requests` (imported at lines 18, 33) and can silently upgrade or conflict with packages Slicer bundles. Offline machines fail here and then the module cannot load at all because lines 28-33 import from the package unconditionally.
  ```
  try:
      import ablinfer
  except ModuleNotFoundError:
      slicer.util.pip_install("ablinfer")
  ```
  Suggestion: Remove the import-time pip_install; use the Slicer extension build system (install into the extension's own site-packages via CMake/SuperBuild, as the commented block in SuperBuild.cmake:32-36 suggests) or a user-confirmed, version-pinned install button per the ScriptedLoadableModule dependency-install convention.
- **flash-lite** (minor, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:23`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L23): The module automatically attempts to pip install 'ablinfer' upon import if not present. While not PyTorch or a restricted bundle, automatic package installation on module import is discouraged in Slicer extensions because it modifies the shared environment without explicit user confirmation during module usage or setup.
  ```
  try:
      import ablinfer
  except ModuleNotFoundError:
      slicer.util.pip_install("ablinfer")
  ```
  Suggestion: Move package installation or check into user-triggered initialization or setup rather than at module import time.
- **haiku** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:23`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L23): At import of the module (and transitively of IntraSampleRegistration.py, which imports the module), if 'ablinfer' is missing the code runs pip install with no user confirmation. This changes the shared Slicer Python environment for users who never open this module, and ablinfer's own dependencies (possibly including docker/requests versions) are pulled in unchecked.
  ```
  try:
      import ablinfer
  except ModuleNotFoundError:
      slicer.util.pip_install("ablinfer")
  ```
  Suggestion: Move the import into the inference code path, ask for user confirmation before pip install, and declare the requirement in a way the user can see.

### D2. Committed model descriptor is a placeholder; no unit tests are registered
single; category packaging; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/Resources/Models/ABLTempSeg.json:1`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/Resources/Models/ABLTempSeg.json#L1): The file installed by CMake (CMakeLists.txt:20) is not valid JSON, so any build that does not run the SuperBuild download (offline build, download failure, or a user running from a checkout) produces a module whose inference step fails with 'Unable to load inference model'. Additionally both Testing/Python/CMakeLists.txt files keep the unittest registration commented out, and ABLTemporalBoneSegmentationModule.py defines no test class at all.
  ```
  you shouldn't see this, this file should be retrieved during build
  ```
  Suggestion: Commit a valid, versioned model descriptor and add at least a smoke test (module loads, atlas/mask files load) for both modules.

### D3. Local variable 'docker' shadows the docker module in the error handler
single; category soundness; raised by haiku
- **haiku** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:949`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L949): In click_infer_apply, 'docker' is assigned as a string in the local branch and is unbound in the remote branch. The except block then evaluates docker.errors.ImageNotFound, which raises AttributeError or UnboundLocalError and hides the real inference error.
  ```
  docker = self.inferDockerHost.text.strip()
              is_docker = True
  ```
  Suggestion: Rename the local variable (e.g. docker_host) so the module name is not shadowed.

### D4. Model descriptor is downloaded from a mutable branch at build time, without checksum, overwriting a tracked source file
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`SuperBuild.cmake:38`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/SuperBuild.cmake#L38): The build step runs urllib.request.urlretrieve against `.../temporal-bone-segmentation/master/ABLTempSeg.json` and writes the result over `${CMAKE_CURRENT_SOURCE_DIR}/ABLTemporalBoneSegmentationModule/Resources/Models/ABLTempSeg.json`. That JSON determines which container image / remote model id is executed on the user's machine, so the content that runs is whatever is on someone else's `master` at build time — not what was reviewed here — and no checksum is checked (unlike the atlas download, which does use SHA256, line 1200-1203). It also writes into the source checkout, which dirties the tree and fails on read-only sources.
  ```
  ## Pull the latest model JSON file on build
  set(_download_model COMMAND ${CMAKE_COMMAND}
  ```
  Suggestion: Commit a real model descriptor and pin it, or download with a versioned URL plus SHA256 verification at runtime into the user's cache directory, not into the source tree.
- **haiku** (minor, high confidence, quote partly verified) [`SuperBuild.cmake:39`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/SuperBuild.cmake#L39): SuperBuild.cmake fetches ABLTempSeg.json from the master branch of another repository with no checksum and writes it into the source tree. The model configuration used by the module can change without any review of this extension, and the build depends on network access.
  ```
  set(_download_model COMMAND ${CMAKE_COMMAND}
    -E env
    ${PYTHON_EXECUTABLE} -c "import urllib.request $<SEMICOLON> urllib.request.urlretrieve('https://raw.githubusercontent.com/Auditory-Biophysics-Lab/temporal-bone-segmentation/master/ABLTempSeg.json', ...
  ```
  Suggestion: Pin to a release tag or commit with a SHA256 check, or commit the file.

### D5. TLS certificate verification disabled for remote inference, and server password stored in plain text
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:933`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L933): When the user chooses 'Run on a remote server?', the session sends the user's CT data (and Basic-Auth credentials, line 936) over a connection whose certificate is never validated, so any network attacker can intercept both. The password is additionally persisted in clear text in the Slicer settings file (`settings.setValue("ablinfer_server_password", password)`, line 938) and re-loaded into the UI at startup (line 363). Line 37 suppresses the urllib3 warning that would otherwise tell the user.
  ```
              s = requests.Session()
              s.verify = False
              if username:
                  s.auth = (username, password)
  ```
  Suggestion: Drop `s.verify = False` (offer an explicit, warned-about opt-in if self-signed certs must be supported), do not persist the password (or store it via a keychain), and remove the global `disable_warnings` call.
- **haiku** (major, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:933`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L933): For remote inference, requests.Session is created with verify=False and HTTP basic credentials are attached. An attacker on the network path can impersonate the server, capture the username and password, and receive the uploaded patient CT volume. InsecureRequestWarning is also silenced globally.
  ```
  s = requests.Session()
              s.verify = False
              if username:
                  s.auth = (username, password)
  ```
  Suggestion: Keep verification enabled by default, use a CA bundle or an explicit opt-in for self-signed servers, and document it.

### D6. logging used without importing the logging module
partial; category soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1370`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L1370): `logging` is never imported in this file. When fetching the model from a remote server fails, the except handler raises NameError instead of degrading gracefully to the locally configured model, and the user sees a confusing traceback.
  ```
                  logging.warning("Encountered an error retrieving model from remote: " + str(e))
  ```
  Suggestion: Add `import logging` (or use `slicer.util.errorDisplay`/print as elsewhere in the file).
- **haiku** (major, high confidence, quote verified, other lines) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:637`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L637): run_inference calls logging.warning when the remote model retrieval fails, but the module never imports logging. The fallback path raises NameError instead of continuing with the local model, so remote inference fails with an unrelated error.
  ```
  except Exception as e:
                  logging.warning("Encountered an error retrieving model from remote: " + str(e))
  ```
  Suggestion: Add 'import logging' at the top or use print/slicer logging.

### D7. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D8. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku concern

### D9. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor

### D10. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Declared module dependencies are empty although Elastix is required at import
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:82`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L82): The module imports `Elastix` at line 16 and `IntraSampleRegistration.py` imports it at line 4; if SlicerElastix is missing, the module fails to load entirely instead of Slicer warning the user. Same for IntraSampleRegistration.py:87.
  ```
          self.parent.dependencies = []
  ```
  Suggestion: Set `self.parent.dependencies = ["Elastix"]` (and in the second module) so Slicer reports the missing dependency.

### Elastix logic and mutable UI state created/held at class level
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified, other file) [`IntraSampleRegistration/IntraSampleRegistration.py:96`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/IntraSampleRegistration/IntraSampleRegistration.py#L96): In IntraSampleRegistration.py these lists and `elastixLogic = Elastix.ElastixLogic()` (line 100) are class attributes, and ABLTemporalBoneSegmentationModule.py:151 instantiates `Elastix.ElastixLogic()` at class definition time (i.e. at import). State therefore leaks between widget instances/reloads and an Elastix logic object is constructed even if the user never opens the module.
  ```
      registrationSteps = []
      volumePairs = []
  ```
  Suggestion: Initialise these in `__init__`/`setup` as instance attributes.

### Export recursively deletes an existing subfolder of the user-chosen directory
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1394`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L1394): `export_for_cardinalsim` is called with a directory picked via QFileDialog (line 1038) and unconditionally `shutil.rmtree`s `<directory>/<volumeName>_dicom` if it exists, with no confirmation. If the user selects a non-empty folder (the dialog text asks for an empty one but nothing enforces it) and a folder of that name is already there, its contents are destroyed irreversibly. The name is derived from a user-editable volume name.
  ```
          if os.path.exists(dicom_dir):
              shutil.rmtree(dicom_dir)
          os.makedirs(dicom_dir, exist_ok=True)
  ```
  Suggestion: Refuse to write into a non-empty directory, or ask for confirmation before removing anything, and use a temporary folder plus explicit copy.
- **haiku** (minor, medium confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1393`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L1393): export_for_cardinalsim calls shutil.rmtree on any existing '<volume>_dicom' folder in the chosen directory. The dialog text asks for an empty folder, but nothing enforces it, so prior exports or user data with that name are silently erased.
  ```
  dicom_dir = os.path.join(directory, volume.GetName() + "_dicom")
          if os.path.exists(dicom_dir):
              shutil.rmtree(dicom_dir)
  ```
  Suggestion: Ask for confirmation or refuse to overwrite a non-empty directory.

### Export writes to current working directory if the folder dialog is cancelled
minor; safety; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1038`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L1038): getExistingDirectory returns an empty string on cancel. The code passes it on without checking, and export_for_cardinalsim calls os.path.abspath('') (the process CWD), so DICOM and label files are written to an arbitrary location the user never chose.
  ```
  target = qt.QFileDialog.getExistingDirectory(None, "Choose an output directory *MUST BE EMPTY*")
          ABLTemporalBoneSegmentationModuleLogic.export_for_cardinalsim(self.movingSelector.currentNode(), self.exportSelector.currentNode(), target)
  ```
  Suggestion: Return early if target is empty.

### Global warning suppression at import
minor; environment; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:37`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L37): Executed when Slicer imports the module at startup, this silences insecure-request warnings for all of Slicer's Python, hiding the `verify = False` issue from the user and from other code.
  ```
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  ```
  Suggestion: Remove it; if truly needed, scope suppression to the single request.

### No functional tests and no clinical-use disclaimer
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`IntraSampleRegistration/IntraSampleRegistration.py:441`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/IntraSampleRegistration/IntraSampleRegistration.py#L441): Test directories contain only commented-out ctest lines and IntraSampleRegistrationTest.runTest is an empty placeholder. Users get no automated coverage of the registration or export logic and no statement that output is not for clinical diagnosis.
  ```
  class IntraSampleRegistrationTest(ScriptedLoadableModuleTest):
      def setUp(self):
          slicer.mrmlScene.Clear(0)
  ```
  Suggestion: Add a sample-data test and a research-use disclaimer.

### No research/clinical-use disclaimer or model validation information
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:6`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/README.md#L6): The module produces anatomical segmentations of temporal bone structures used downstream (e.g. CardinalSim), but the README gives no statement that it is for research use, no accuracy/validation figures, and no model provenance beyond a link; the Docker image version actually run depends on the remote model descriptor.
  ```
  This 3D Slicer module handles spacing resampling, fiducial registration, rigid registration, and inference of the major structures of CT temporal bone scans.
  ```
  Suggestion: Add a research-use disclaimer and cite the network's validation study and image version.

### Option deletes every fiducial node in the scene without confirmation
minor; safety; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1175`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L1175): Called from `finalize_input` (line 606) whenever the 'Clear All Markups When Loading New Input Volume' checkbox is ticked. It removes all fiducial markups in the scene, including ones the user created for other purposes, with no confirmation and no undo prompt.
  ```
      def clear_all_markups_from_scene():
          for n in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode"): slicer.mrmlScene.RemoveNode(n)
  ```
  Suggestion: Only remove markups created by this module (track their node IDs), or ask for confirmation.

### Server password stored in plaintext application settings
minor; safety; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:937`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L937): The password typed into the remote server field is written to Slicer's persistent settings on every run. Any local user or process that can read the settings file obtains the credential in cleartext.
  ```
  settings.setValue("ablinfer_server_username", username) 
                    settings.setValue("ablinfer_server_password", password)
  ```
  Suggestion: Do not persist passwords; store them in the OS keyring or only keep them for the session.

### scm_revision points to a moving branch
minor; packaging; raised by haiku; **quote not found in source**
- **haiku** (minor, medium confidence, quote quote not found) [`ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py:1`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/ABLTemporalBoneSegmentationModule/ABLTemporalBoneSegmentationModule.py#L1): The catalog entry uses scm_revision 'master', so the indexed build can change without a catalog update. The reviewed commit is 227bc565ddec65509bac6dcbbddd6c02e718eaeb, which the entry does not pin.
  ```
  "scm_revision": "master"
  ```
  Suggestion: Pin scm_revision to a specific commit or release tag.

### IDE project files are committed despite being git-ignored
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified, other file) [`.gitignore:1`](https://github.com/Auditory-Biophysics-Lab/Slicer-ABLTemporalBoneSegmentation/blob/227bc565ddec65509bac6dcbbddd6c02e718eaeb/.gitignore#L1): .idea/ is listed in .gitignore yet 9 .idea files (including a 26 KB .idea/workspace.xml that typically records local paths and usernames) are in the repository; .gitignore also carries leftovers from an unrelated project (SkullThicknessMapping lines 127-130). Harmless but noise.
  ```
  # Idea
  .idea/
  ```
  Suggestion: Remove the committed .idea files and the unrelated ignore entries.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Useful, documented otolaryngology workflow (README tutorial, screenshots, BSD-3 license, catalog entry consistent). Two blockers-class problems: `ablinfer` is pip-installed at module import with no user consent or pin (affects the shared Slicer Python environment for every user at startup), and the build fetches the model descriptor JSON from a mutable `master` branch, without checksum, overwriting a tracked source file, so the reviewed content is not what ships. Also: TLS verification is disabled (`s.verify = False`) and server passwords are stored in plain text in Slicer settings. Tests are disabled/absent and there are minor code bugs. 🔴 Do not merge yet.
Not checked: The `ablinfer` PyPI package (licence, dependencies, what it sends to Docker/remote servers) and the `temporal-bone-segmentation` repository (model JSON content, Docker image, atlas files, licence) were not accessible from this environment.; `.idea/workspace.xml`, `.idea/inspectionProfiles/Project_Default.xml`, `Parameters_Rigid_Sumit.txt` and the binary Resources (atlas .mha download, masks, icons, Images/*.png) were not read; the .mha atlas is downloaded at runtime and its content was not inspected.; Runtime behaviour (Docker image pull/exec, remote inference payloads, whether the model descriptor references a specific image tag) could not be executed or verified.; The exact commit 227bc565ddec65509bac6dcbbddd6c02e718eaeb was not resolvable here; all citations are from the file contents supplied for review.
Questions for the author: Why is `ablinfer` installed with `pip_install` at import rather than shipped by the extension build, and which version of it is expected?; Is `s.verify = False` required for your server deployment, and can it be replaced by a proper certificate or an explicit opt-in with a warning?; What does the downloaded `ABLTempSeg.json` contain (container image tag / remote model id), and can it be pinned with a checksum instead of pulled from `master` at build time?; What are the licences of the atlas volumes, the trained model and the Docker image distributed from the `temporal-bone-segmentation` repository?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
🟢 Recommend merge. The ABLTemporalBoneSegmentation extension is a well-structured otolaryngology extension with valid metadata, BSD 3-Clause licensing, clean CMake build setup, and robust Slicer scripted module implementations. A minor finding notes automatic package installation of 'ablinfer' on import, but overall there are no blocking security, packaging, or soundness concerns.
Not checked: Execution of remote inference or Docker dispatch logic against external servers.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
No evidence of malicious code, but several concrete defects. The module pip-installs a package at import time, globally disables urllib3 TLS warnings, and disables certificate verification (verify=False) while sending a username and password to the server. It also references an undefined `logging` module and shadows the `docker` module with a local variable, so error handling in inference can crash. Export can write into the current working directory when the folder dialog is cancelled. The catalog pins `master` and fetches the model JSON unpinned at build time. No tests exist. Overall: needs fixes.
Not checked: Remote ABLInfer server and Docker image behavior, data handling, and retention were not inspected.; Licensing of the downloaded atlas (Auditory-Biophysics-Lab/temporal-bone-segmentation releases) and the model JSON was not checked.; The ablinfer PyPI package source and its dependencies were not inspected.; The scm_revision 227bc56 was not resolved; only the files given in the prompt were reviewed.; IntraSampleRegistration.py beyond the shown lines and the Resources/Parameters text files were not read.; .idea/workspace.xml was not read.; No Slicer runtime test or build was performed.


# AI review: FlywheelCaseIterator

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://gitlab.com/flywheel-io/scientific-solutions/app/Slicerflywheelcaseiterator.git at commit `e23ba0dff8db72a3283e38000c4d1130442aa31f`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-20T03:07:15Z; cost $0.07

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | concern |
| environment | blocking | ok | concern |
| packaging | minor | ok | minor |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A Flywheel-specific fork of SlicerCaseIterator that lets a user iterate over NIfTI cases listed in a Flywheel CSV export, segment them in Slicer, and upload the resulting masks back to the Flywheel instance. It targets research imaging teams that store their data in Flywheel.
- **flash-lite**: FlywheelCaseIterator is a 3D Slicer extension that allows users to iterate through NIfTI images from Flywheel, create and update segmentations, and upload mask outputs back to Flywheel.
- **haiku**: FlywheelCaseIterator is a scripted Slicer module, adapted from SlicerCaseIterator, that iterates over NIfTI cases listed in a CSV exported from a Flywheel instance. It lets clinicians or researchers load images, edit segmentations in Slicer, and upload masks back to Flywheel.

## Disagreements (start here)

### D1. pip install and dependency check run at module import (Slicer startup)
partial; category environment; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIterator.py` line 41: Scripted module files are imported when Slicer registers modules, so every user who installs this extension triggers a PyPI install of fw-pyqt-management (and whatever check_requirements pulls in, e.g. the flywheel SDK) at startup, without being asked. This modifies Slicer's shared Python environment for users who never open the module, can downgrade/pin packages Slicer bundles, and makes module loading fail entirely when the machine is offline or PyPI is unreachable.
  ```
  if not importlib.util.find_spec("fw_pyqt_management"):
      slicer.util.pip_install("fw-pyqt-management")
  
  from fw_pyqt_management.utils import check_developer_mode, check_requirements
  
  check_requirements(REQUIRED_MODULES)
  ```
  Suggestion: Move the dependency handling into the module widget's setup()/first use, ask the user for confirmation before installing, and declare the dependencies in the extension metadata instead of installing at import.
- **haiku** (major, high confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIterator.py` line 41: On import, the module runs slicer.util.pip_install("fw-pyqt-management") whenever the package is missing, then check_requirements(REQUIRED_MODULES) runs. Scripted modules are parsed at Slicer startup, so every user who installs the extension gets a package install, without being asked, at startup, whether or not they ever open the module. The install also pulls the package's own transitive dependencies into Slicer's shared Python environment. This is the kind of startup install the index policy asks to be removed or gated behind explicit confirmation.
  ```
  if not importlib.util.find_spec("fw_pyqt_management"):
      slicer.util.pip_install("fw-pyqt-management")
      
  from fw_pyqt_management.utils import check_developer_mode, check_requirements
  ```
  Suggestion: Move the import and install into setup() (widget creation), ask the user to confirm the install, and keep pip installs out of module import. Also pin the version consistently with required_modules.json.

### D2. Case cleanup deletes every volume and segmentation node in the scene
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 917: closeCase() runs on every case change and in its finally block removes all vtkMRMLScalarVolumeNode and vtkMRMLSegmentationNode instances in the scene, not just the nodes belonging to the current case. Any volume or segmentation the user loaded independently (e.g. a reference atlas, or work in progress in another module) is silently destroyed when advancing to the next case.
  ```
  deque(
                  map(
                      slicer.mrmlScene.RemoveNode,
                      slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode"),
                  )
              )
  ```
  Suggestion: Remove only the node IDs recorded in the case data (as the try block already does) and drop the scene-wide sweep.
- **haiku** (major, high confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 924: The finally block of closeCase removes all vtkMRMLScalarVolumeNode and vtkMRMLSegmentationNode instances in the scene, not only the case's own nodes. A user who loaded an unrelated volume, or who is comparing a segmentation outside the batch, loses it on the next Next/Previous action or on Reset. Because closeCase runs in cleanup paths, this can happen even after an error elsewhere in the case.
  ```
  # clean up any dangling volume nodes
              deque(
                  map(
                      slicer.mrmlScene.RemoveNode,
                      slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode"),
  ```
  Suggestion: Remove only nodes tracked in the case data (InputImage_ID, InputMask_ID, and the additional IDs). If an orphan sweep is needed, restrict it to nodes this extension created and tagged.

### D3. Connecting to Flywheel clears the whole MRML scene without confirmation
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 377: Pressing 'Connect Flywheel' discards every node in the current scene, including the user's own loaded volumes, segmentations and any unsaved work, with no prompt and no undo. A user who has been annotating in another module and then connects to Flywheel loses that work.
  ```
  # Clear out any other instance's data from Slicer before proceeding.
  slicer.mrmlScene.Clear(0)
  self.batchTableSelector.setCurrentNodeID("")
  ```
  Suggestion: Ask for confirmation (or only remove nodes the extension itself created, e.g. via the singleton parameter node) before clearing the scene.
- **haiku** (major, high confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 377: on_connect_api_pushed calls slicer.mrmlScene.Clear(0) before loading the batch table. Any unsaved volumes, segmentations, or other scene content the user has open are discarded. The user is not warned, and the clear happens right after an API key is entered, which is an easy action to take by accident. This is unintended data loss from user work, not a crash.
  ```
  # Clear out any other instance's data from Slicer before proceeding.
  slicer.mrmlScene.Clear(0)
  ```
  Suggestion: Ask for confirmation before clearing, or clear only nodes this extension created (for example by tracking node IDs or using the parameter node). Do not clear the entire scene.

### D4. Undeclared pinned dependency fw-pyqt-management 0.0.4 with upgrade disabled
single; category environment; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) `FlywheelCaseIterator/Resources/required_modules.json` line 2: The extension hard-pins a third-party package and disables upgrades, and its transitive requirements (flywheel SDK and anything else fw-pyqt-management declares) are installed into Slicer's Python without review or declaration. If those requirements pin or downgrade packages Slicer bundles (numpy, requests, etc.), other extensions break for all users of the installation.
  ```
  "fw_pyqt_management": {
      "package": "fw-pyqt-management",
      "version": "0.0.4",
      "upgrade": false
    }
  ```
  Suggestion: Declare the dependency in the catalog entry/CMake and let the user install it, or at minimum document the full transitive requirement set and avoid exact pins of shared packages.

### D5. eval() of a string read from the MRML scene
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 954: The CaseData parameter is read from a vtkMRMLScriptedModuleNode that lives in the MRML scene. A scene (.mrml/.mrb) received from a colleague or downloaded from a data repository can contain a node named 'FlywheelCaseIterator' whose CaseData parameter holds arbitrary Python; when the user starts or advances a batch, getCaseData() executes it with Slicer's privileges. closeCase() already uses the safe ast.literal_eval for the same value (line 910), so the eval is unnecessary.
  ```
  caseData = eval(self.parameterNode.GetParameter("CaseData"))
  ```
  Suggestion: Use ast.literal_eval here as well, or store the case data as individual node-ID parameters instead of a serialized dict.
- **haiku** (minor, medium confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 954: getCaseData calls eval() on the CaseData parameter string. The value is produced by SetParameter from a Python dict of Slicer node IDs, so the practical risk is low. eval is still unnecessary, and the same class uses ast.literal_eval at line 910. Any writer of that parameter, including a loaded scene file, could execute code during getCaseData.
  ```
  caseData = eval(self.parameterNode.GetParameter("CaseData"))
  ```
  Suggestion: Use ast.literal_eval as closeCase does, or store the case data as JSON with json.loads.

### D6. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D7. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku concern

### D8. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### API key read from other tools' config and persisted in plaintext
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 350: The module silently falls back to the API key stored by the Flywheel CLI in ~/.config/flywheel/user.json (lines 312-317) and then writes the key in plaintext into ~/.config/flywheel/fw_connect.json. Credentials are therefore harvested from another tool's config and stored unencrypted on disk; the docs mention the saving but not the CLI fallback.
  ```
  if api_key:
              fw_client = flywheel.Client(api_key)
              self.config["api_key"] = api_key
  ```
  Suggestion: Only use a key the user explicitly entered, and store it with restrictive file permissions or in Slicer's settings rather than a plaintext JSON file.
- **haiku** (minor, medium confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 351: The API key entered in the GUI is written to the shared config at ~/.config/flywheel/fw_connect.json, and a key from the Flywheel CLI (~/.config/flywheel/user.json) is read and reused. The documentation says the key is saved for future use, but no secure storage or permission restriction is applied. Anyone who can read the user's home directory can use the key to access the Flywheel instance.
  ```
  fw_client = flywheel.Client(api_key)
              self.config["api_key"] = api_key
  ```
  Suggestion: Use the OS keychain, or at least restrict the config file permissions. Document the plaintext storage clearly for users on shared machines.

### Bare except blocks silently skip failing cases
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) `FlywheelCaseIterator/FlywheelCaseIterator.py` line 306: start(), nextCase() and previousCase() (lines 585-588, 606-611, 633) catch every exception, including KeyboardInterrupt/SystemExit, and just advance the index. A case that fails to load (network error, permission problem, bad file) is skipped with no user-visible message, so a reader can silently miss cases and believe the batch was complete.
  ```
  try:
              self._loadCase()
          except:
              self.nextCase()
  ```
  Suggestion: Catch Exception, log the failing case index, and surface a warning to the user (slicer.util.warningDisplay) when cases are skipped.

### Default cache directory is a fixed path under /tmp
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) `FlywheelCaseIterator/Resources/config_defaults.json` line 3: Downloaded patient images are cached in /tmp/flywheel_cache, a world-writable, predictable location on Linux/macOS. Another local user can pre-create that directory or symlinks inside it, and cached medical images are left behind after the session with default permissions.
  ```
  "CachePath": "/tmp",
    "CacheDirName": "flywheel_cache"
  ```
  Suggestion: Default to a per-user directory (e.g. under the user's home or Slicer's temporary directory created with tempfile.mkdtemp) and create it with user-only permissions.
- **haiku** (minor, medium confidence, quote verified) `FlywheelCaseIterator/Resources/config_defaults.json` line 3: Images downloaded from Flywheel are cached under CachePath/CacheDirName, which defaults to /tmp/flywheel_cache. On shared Linux or macOS machines /tmp is often readable by other local users, and nothing in the module clears the cache after the batch ends. TODO.md line 48 lists a cache-clearing option as unchecked. The exposure is of medical data at rest, and it depends on the Flywheel data's sensitivity.
  ```
  "CachePath": "/tmp",
    "CacheDirName": "flywheel_cache"
  ```
  Suggestion: Default the cache to a per-user, non-world-readable directory (for example the Slicer user cache or a tempfile.mkdtemp with 0700 permissions). Provide a cache clear action and clean up on batch end.

### Flywheel SDK dependency is undeclared and unpinned
minor; packaging; raised by haiku
- **haiku** (minor, medium confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 34: CsvFWTableIterator.py imports the flywheel SDK at module level, but required_modules.json declares only fw-pyqt-management 0.0.4. The project's own TODO.md (lines 57-59) notes that the required SDK version is not specified. Installs can therefore break on SDK API changes, and the dependency is not visible to the extension manager.
  ```
  import flywheel
  import qt
  import slicer
  ```
  Suggestion: Declare the flywheel SDK and its version in required_modules.json, or in the install logic, and keep it consistent with the fw-pyqt-management pin.

### KeyError when an additional-image entry is empty
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 773: In the else branch the code logs `image_data["name"]` even when image_data is falsy (None/{}), which raises TypeError/KeyError and aborts loading of the whole case instead of skipping the bad entry.
  ```
  if image_data and (
                        image_file := self._download_from_container(
                            image_data["parent"], image_data["name"]
                        )
                    ):
  ```
  Suggestion: Guard the log message with `if image_data:` and use .get('name').

### No automated tests are registered
minor; packaging; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) `FlywheelCaseIterator/Testing/Python/CMakeLists.txt` line 2: The only test registration is commented out, and FlywheelCaseIterator.py contains no unittest subclass for the slicer_add_python_unittest call in FlywheelCaseIterator/CMakeLists.txt line 32. Nothing verifies that the module loads or that the CSV parsing works, so regressions reach users unnoticed.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a minimal module test (module loads, iterator factory returns the CSV widget) and enable it in CMake.
- **haiku** (minor, high confidence, quote verified) `FlywheelCaseIterator/Testing/Python/CMakeLists.txt` line 2: The only test registration is commented out, so the extension ships without automated tests. Behavior of the batch iteration, mask save, and the scene-clear and node-removal paths is unverified in CI.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add at least unit tests for the iterator logic (case index navigation, node cleanup scope) that run without a Flywheel instance.

### README module structure no longer matches the repository
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) `README.md` line 133: The documented fw_case_management package is not in the repository and not installed by FlywheelCaseIterator/CMakeLists.txt; the code now imports fw_pyqt_management from PyPI. Users and reviewers following the README will look for code that does not exist, and the actual runtime dependency is undocumented.
  ```
  ├── fw_case_management
  │   ├── config.py
  │   ├── fw_container_items.py
  ```
  Suggestion: Update the module-structure section and document the fw-pyqt-management dependency.

### Reload path uses the removed `imp` module
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/IteratorFactory.py` line 86: The imp module was deprecated in Python 3.4 and removed in Python 3.12, which newer Slicer versions ship. onReload() of the module widget will therefore raise ImportError on those Slicer builds.
  ```
  import imp
  
          f, filename, description = imp.find_module(packageName)
  ```
  Suggestion: Use importlib (importlib.reload / importlib.util.find_spec) instead of imp.

### User-controlled names are used directly in output filenames
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 1475: The reader name and the mask node name are concatenated into the output filename without sanitizing path separators. A reader name or segment name containing '/' or '..' can place the file outside the intended folder. The exposure is limited because the user typed the value, but it is an unvalidated path construction.
  ```
  if reader is not None:
                            nodename += "_" + reader
                        file_name = nodename + ".nii.gz"
  ```
  Suggestion: Sanitize reader and node names (for example, restrict to alphanumerics and a few safe characters) before forming paths, and confirm the resolved path stays inside the output directory.

### getCaseData returns a list where a tuple is documented
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 969: Callers unpack the result as a 4-tuple (e.g. `im, ma, add_im, add_ma = self.getCaseData()`), and the error path returns a list; more importantly the exception is swallowed without logging, so a corrupted CaseData parameter silently looks like an empty case.
  ```
  except Exception:
              return [None, None, [], []]
  ```
  Suggestion: Return a tuple and log the exception.

### load_success may be unbound in _loadMaskNode
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) `FlywheelCaseIterator/FlywheelCaseIteratorLib/CsvFWTableIterator.py` line 1128: load_success is only assigned inside `if ma_node:`; if loadLabelVolume returns None the code falls through to `if not load_success:` at line 1169 and raises UnboundLocalError instead of returning None, which then propagates as a case-load failure.
  ```
  ma_node = slicer.util.loadLabelVolume(ma_path)
              if ma_node:
  ```
  Suggestion: Initialise load_success = False before the branch and return None when the label volume could not be loaded.

### Installation docs point at a Google Drive folder for packages
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) `docs/installation_and_usage.md` line 53: Users are directed to download extension packages from an unversioned Google Drive folder rather than the Slicer extension manager, which makes provenance of the binaries unclear and bypasses the catalog build.
  ```
  1. Download the latest version of the extension package from the
  [Releases](https://drive.google.com/drive/folders/13MZ5DUShqhP9nc0hGGihKcKEBLiOBqTk?usp=sharing)
  page.
  ```
  Suggestion: Point users at the Extension Manager once the extension is published and remove the Drive instructions.

### No clinical-use disclaimer for a tool that writes annotations back to a data system
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) `README.md` line 154: The disclaimer only covers maintenance responsibility; it does not state that the tool is for research use and not for clinical diagnosis, although it is used to produce and upload segmentations.
  ```
  ## Disclaimer
  
  This Slicer Extension is adapted from Slicer Case Iterator and is maintained by
  Flywheel.
  ```
  Suggestion: Add a research-use-only statement to the README and module acknowledgement.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The module does what it advertises, but it installs Python packages at module import (blocking environment issue) and has several concrete data-loss / code-execution paths: `eval()` of a string read from the MRML scene, `slicer.mrmlScene.Clear(0)` on "Connect Flywheel", and a cleanup routine that removes every scalar-volume and segmentation node in the scene. API keys are read from and written to plaintext config files. Packaging is mostly correct (all Python files and resources are installed, EXTENSION_DEPENDS matches), license is BSD-3. Tests are absent and docs are partly stale. Needs fixes before being offered to users.
Not checked: The implementation of fw_pyqt_management (check_requirements, check_developer_mode, Config, FileItem._add_to_cache, ContainerParentModel) is not in this repository and could not be inspected; it is pip-installed at import, so its behavior (including whether it pins/downgrades Slicer-bundled packages; Licenses of the pip-installed packages fw-pyqt-management and the flywheel SDK were not verified.; The exact source revision e23ba0dff8db72a3283e38000c4d1130442aa31f was not resolved against the GitLab repository; the review is based on the file contents provided for that commit.; No build, load, or runtime test was performed; the module's behavior on Windows (symlink/developer-mode requirement) and on Slicer versions shipping Python 3.12 was not verified.; The remaining lines of CsvFWTableIterator.py beyond line 1554 (if any) and the .gitlab-ci.yml / .pre-commit-config.yaml contents were not read.
Questions for the author: What exactly does fw_pyqt_management.check_requirements() install, and can the install be moved out of module import into an explicit, user-confirmed step?; Why does connecting to Flywheel need slicer.mrmlScene.Clear(0), and can it be limited to nodes created by this extension?; Can the eval() in getCaseData() be replaced with ast.literal_eval, as closeCase() already does?; Why does closeCase() remove every scalar-volume and segmentation node in the scene rather than only the case's own node IDs?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
FlywheelCaseIterator is a clean, well-structured 3D Slicer extension adapted from SlicerCaseIterator to facilitate case iteration and segmentation workflows with Flywheel. It adheres to Slicer standards, uses the 3-Clause BSD license, packages all required python modules correctly via CMake, and handles optional dependencies gracefully. All review criteria are met successfully.
Not checked: Full execution of CsvFWTableIterator.py (60kb) which interacts with Flywheel SDK and instances, as network interaction and live Flywheel setup are not available in this static review environment.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The catalog entry is well formed: the s4ext and CMake metadata agree, the listed Python files exist, the BSD-3 license permits distribution, and the source revision is "main". The code has real concerns. Module load runs an unconditional pip install of fw-pyqt-management. Connecting clears the whole MRML scene without a prompt. Closing a case deletes every volume and segmentation node in the scene, not just the case's own nodes. The API key is stored in plaintext, and downloaded patient images are cached under /tmp. I did not verify the pinned commit or run anything. The middle of CsvFWTableIterator.py was not read.
Not checked: Commit e23ba0dff8db72a3283e38000c4d1130442aa31f and the scm_revision 'main' were not resolved or fetched; the source reviewed is only the content provided in the prompt plus the files I read.; CsvFWTableIterator.py lines 121-295, 400-515, 600-895, 990-1270, 1330-1410, and 1510-1530 were not read.; The fw_pyqt_management package (Config, FileItem._add_to_cache, check_requirements, check_developer_mode) was not available; its cache, config permissions, and install behavior are unverified.; The Flywheel Connect config and any other network calls, including the destinations of data sent to the Flywheel instance, were not traced beyond the SDK calls.; No CI results, build logs, or Slicer runtime tests were available, and nothing was executed.; The PNG icon and screenshot binaries were not inspected for content.
Questions for the author: Why is fw-pyqt-management installed at module import rather than in setup() after user action? Would you accept a confirmation prompt?; Is clearing the entire MRML scene on connect intended? Can it be limited to nodes this extension created?; Should closeCase remove only the nodes listed in the case data rather than every volume and segmentation in the scene?; Where is the cache directory cleaned up, and what permissions apply to /tmp/flywheel_cache on multi-user systems?; Which flywheel SDK version is required, and why is it not declared in required_modules.json?


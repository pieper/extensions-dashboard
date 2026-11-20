# AI review: ConnectToSupervisely

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely at commit `5280d7a007948ac0486b57edaf55aefdb6479c6a`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-20T02:52:13Z; cost $0.07

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | minor |
| environment | concern | ok | concern |
| packaging | minor | ok | ok |
| license | ok | ok | ok |
| soundness | concern | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: ConnectToSupervisely connects 3D Slicer to the Supervisely cloud annotation platform so annotators and reviewers can download Labeling Job volumes, edit 3D segmentations and tags in Slicer, and upload results and review statuses back to the server.
- **flash-lite**: The ConnectToSupervisely extension enables 3D Slicer users to seamlessly access, annotate, and review volumetric labeling jobs hosted on the Supervisely computer vision platform.
- **haiku**: A 3D Slicer scripted-module extension (two modules, Labeling Jobs Annotating and Reviewing) that lets users download volumes and masks from, and upload annotations to, a Supervisely server. It is for Supervisely users who run labeling jobs and want to annotate or review volumetric data in Slicer.

## Disagreements (start here)

### D1. Missing-requirement install is not --no-deps and can upgrade or downgrade Slicer-bundled packages
single; category environment; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`ConnectToSupervisely/moduleLib/utils.py:167`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/utils.py#L167): get_missing_requirements() only filters on top-level names that are absent, but pip then resolves each requirement's own dependencies, which can replace numpy, requests or other packages Slicer bundles. The dialog text claims "Packages already installed in 3D Slicer are not changed" (utils.py:200), which is not guaranteed for transitive dependencies. The backup/restore mechanism (utils.py:55-109) mitigates but does not prevent the breakage.
  ```
  slicer.util.pip_install(" ".join(shlex.quote(r) for r in missing))
  ```
  Suggestion: Install with --no-deps and verify each requirement against the installed version, or install into an isolated environment; correct the dialog wording.

### D2. Module setup pip-installs Supervisely and its requirements into Slicer's shared Python with no way to decline
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified, other lines) [`ConnectToSupervisely/moduleLib/utils.py:163`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/utils.py#L163): import_supervisely() is called from setup() of both widgets (labelingJobsAnnotating.py:79, labelingJobsReviewing.py:80), so simply opening the module runs pip_install into Slicer's shared Python. The preceding SuperviselyDialog is type="info" with only an OK button, so the user cannot cancel; the only escape is closing Slicer. This changes the interpreter for every other extension in that Slicer installation.
  ```
  slicer.util.pip_install(f"--no-deps supervisely=={SUPERVISELY_VERSION}")
  ```
  Suggestion: Use a confirm dialog with a real Cancel path and only install after explicit consent; keep the install in a documented, user-initiated step.
- **haiku** (minor, medium confidence, quote verified) [`ConnectToSupervisely/moduleLib/utils.py:162`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/utils.py#L162): On first open, import_supervisely shows an informational dialog and calls install_supervisely, which runs pip install --no-deps for an exact SDK pin plus any missing transitive requirements, then forces slicer.util.restart(). The user is not asked to confirm, and this affects the whole Slicer process, not just this module. Any transitive dependency that is pulled in can change other extensions' environment. The change is recorded and a restore button is offered, which partly mitigates the risk. The dependency set of supervisely 6.74.48 was not inspected, so whether it pulls packages that bundle Qt or VTK is unknown.
  ```
  if get_installed_version("supervisely") != SUPERVISELY_VERSION:
              slicer.util.pip_install(f"--no-deps supervisely=={SUPERVISELY_VERSION}")
              importlib.invalidate_caches()
          missing = get_missing_requirements()
          if missing:
              slicer.util.pip_install(" ".join(shlex.quote(r) for r in missing))
  ```
  Suggestion: Ask for explicit confirmation before downloading and installing (the current dialog is informational only). Document the packages that will be added to Slicer's environment. Check that the transitive set does not include Qt/VTK bundles or packages Slicer pins, such as numpy or requests, and state this in the README.

### D3. Network downloads and uploads run synchronously on the GUI thread
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified, other lines) [`ConnectToSupervisely/moduleLib/baseLogic.py:247`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/baseLogic.py#L247): downloadData() calls VolumeProject.download() and uploadAnnObjectChangesToServer() performs per-segment uploads and per-object removals directly inside the button handler under waitCursor. For large volume projects the Slicer UI freezes for the whole transfer and the progress bar cannot repaint reliably; the same applies to _filterVolumeJobs(), which issues one project.get_info_by_id() call per project on the GUI thread.
  ```
  self._dowloadProject()
  ```
  Suggestion: Move the transfer into a slicer.util.createProgressDialog-driven worker thread or a CLI, and update the UI from the main thread.

### D4. Slicer is restarted automatically after the install, without an explicit save prompt in the extension's flow
single; category environment; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`ConnectToSupervisely/moduleLib/utils.py:202`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/utils.py#L202): After installing, the code calls slicer.util.restart() (utils.py:208) and also on the failure path (utils.py:217). A user who opens the module with an unsaved scene loses in-memory work; the extension gives no save prompt and no cancel option.
  ```
  3D Slicer will be restarted after installation.
  ```
  Suggestion: Ask the user to save and confirm the restart, or defer the restart until the user chooses it.

### D5. clear() wipes the entire MRML scene, including data the extension did not load
single; category safety; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`ConnectToSupervisely/moduleLib/utils.py:247`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/utils.py#L247): clear() is called on team change, job change, logout, job finish and submit (labelingJobsAnnotating.py:176,198,301; labelingJobsReviewing.py:179,201,299). It removes every node in the scene, so any volume, segmentation or unsaved annotation the user loaded independently is destroyed without a dedicated confirmation. The save prompt only appears when self.logic.volume is set and only covers the extension's own annotations.
  ```
  slicer.mrmlScene.Clear()
  ```
  Suggestion: Remove only the nodes the extension created (track their IDs) and confirm before clearing anything else.

### D6. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor

### D7. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D8. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### Catalog entry pins a moving branch rather than a commit
minor; packaging; raised by deepseek, haiku; **quote not found in source**
- **deepseek** (minor, high confidence, quote quote not found) [`ConnectToSupervisely.s4ext:1`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely.s4ext#L1): The catalog entry uses scm_revision "master", so the code users install is whatever the branch points at, not the commit 5280d7a this review examined. Branch references are allowed, but the reviewed revision is not what the index will build.
  ```
  scm_revision
  ```
  Suggestion: Pin scm_revision to a tagged release or commit for reproducible builds.
- **haiku** (info, high confidence, quote quote not found) no file cited: scm_revision is 'master', so the index build will fetch whatever commit is at the branch tip at build time. The reviewed commit 5280d7a is not the revision the index will build. This is a reproducibility concern, not a defect, and it is acceptable under the index policy for branch references.
  ```
  "scm_revision": "master",
  ```
  Suggestion: Consider pinning scm_revision to the reviewed commit 5280d7a007948ac0486b57edaf55aefdb6479c6a so the reviewed code is what gets built, and bump it on each update.

### Global logger level and Data Probe visibility are toggled process-wide
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`ConnectToSupervisely/labelingJobsAnnotating.py:138`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/labelingJobsAnnotating.py#L138): enter() raises the root logger to CRITICAL and hides the Data Probe for the whole Slicer session while the module is open. The logger level is restored immediately, but the Data Probe change is global and only undone in exit(); if the module crashes or is reloaded, other modules keep the modified state.
  ```
  logger.setLevel(logging.CRITICAL)
  ```
  Suggestion: Use a module-scoped logger instead of the root logger and restore the Data Probe in cleanup() as well as exit().
- **haiku** (minor, medium confidence, quote verified) [`ConnectToSupervisely/labelingJobsAnnotating.py:136`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/labelingJobsAnnotating.py#L136): enter() sets the root logger to CRITICAL around a dotenv call and restores it afterwards. If dotenv.get_key raises, the root logger stays at CRITICAL for the whole Slicer session, silencing logs for other extensions. The exposure is small, but it is a global side effect.
  ```
  logger = logging.getLogger()
              original_level = logger.getEffectiveLevel()
              logger.setLevel(logging.CRITICAL)
              activeModule = dotenv.get_key(ENV_FILE_PATH, "ACTIVE_SLY_MODULE")
              logger.setLevel(original_level)
  ```
  Suggestion: Use try/finally around the dotenv call, or drop the global level change since dotenv.get_key does not need it.

### Local project data is deleted recursively without a path sanity check
minor; safety; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified, other lines) [`ConnectToSupervisely/moduleLib/baseLogic.py:239`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/baseLogic.py#L239): removeLocalData() recursively deletes self.savePath, which is built as os.path.join(self.workingDir, f"{self.activeJob.project_id}") (baseLogic.py:227) where workingDir comes from the user-editable working-directory button. If a user points the working directory at an existing folder, the extension deletes <workingDir>/<project_id> on logout/finish. The path is extension-derived, so risk is limited, but there is no guard that the directory belongs to the extension.
  ```
  remove_dir(self.savePath)
  ```
  Suggestion: Write a marker file into the download directory and refuse to delete a directory that lacks it.

### Login credentials and token are stored in plaintext in the home directory
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`ConnectToSupervisely/moduleLib/baseLogic.py:157`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/baseLogic.py#L157): With "Remember login" checked, Api.from_credentials(..., env_file=ENV_FILE_PATH) writes the server address and credentials/token to ~/supervisely_slicer.env (baseLogic.py:47) with default file permissions. On a shared workstation another local user can read the token. The behaviour is opt-in and documented in README.md:139, but the file is not permission-restricted.
  ```
  self.api = Api.from_credentials(
  ```
  Suggestion: Create the env file with 0600 permissions and mention the plaintext storage in the UI next to the checkbox.
- **haiku** (minor, medium confidence, quote verified) [`ConnectToSupervisely/moduleLib/baseLogic.py:157`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/baseLogic.py#L157): With rememberLogin checked, Api.from_credentials is called with override=True and env_file pointing to ~/supervisely_slicer.env. The file then holds the account token in plaintext, and any local user or process with read access to the home directory can use it. The behaviour is opt-in and disclosed in the README, so this is a minor hardening issue rather than a concealed-data problem.
  ```
  self.api = Api.from_credentials(
              server_address=self.ui.serverAddress.text,
              login=self.ui.login.text,
              password=self.ui.password.text,
              override=self.ui.rememberLogin.isChecked(),
              env_file=ENV_FILE_PATH,
  ```
  Suggestion: Store the token with OS keychain or restricted file permissions (chmod 600) where possible. Keep the opt-in wording explicit in the UI, noting that the token is saved in plaintext.

### No automated tests or sample data
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`README.md:19`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/README.md#L19): The repository contains no test module and no sample Labeling Job data; every code path requires a live Supervisely account and server, so regressions in the download/upload logic cannot be caught automatically.
  ```
  A 3D Slicer extension designed to organize and manage the work of labeling teams on the
  ```
  Suggestion: Add a ScriptedLoadableModuleTest with mocked API responses and a small sample volume project.

### SuperviselyDialog.__bool__ reads an attribute that is never set for delay/comment dialogs
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`ConnectToSupervisely/moduleLib/ui.py:176`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/ui.py#L176): self.decision is only assigned in on_ok_clicked/on_cancel_clicked, which are not connected for type "delay" or "comment". Any truth-value test of such a dialog raises AttributeError; the code currently avoids it only by not testing those instances.
  ```
  def __bool__(self):
  ```
  Suggestion: Set self.decision = False in __init__ before the type branches.

### changeVolumeStatus can raise UnboundLocalError when the volume name is not in the job entities
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ConnectToSupervisely/moduleLib/baseLogic.py:378`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/baseLogic.py#L378): volumeId is only assigned inside the loop when entity["name"] == self.volume.name. If the refreshed job no longer contains that entity (for example after a sync or a server-side change), volumeId is unbound and the accept/reject action fails with an obscure error instead of a clear message.
  ```
  self.api.labeling_job.set_entity_review_status(self.activeJob.id, volumeId, status)
  ```
  Suggestion: Initialise volumeId to None and raise a descriptive error when no matching entity is found.

### python-dotenv is imported defensively but used unconditionally
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`ConnectToSupervisely/moduleLib/baseLogic.py:29`](https://github.com/supervisely-ecosystem/SlicerConnectToSupervisely/blob/5280d7a007948ac0486b57edaf55aefdb6479c6a/ConnectToSupervisely/moduleLib/baseLogic.py#L29): The import is wrapped in try/except ModuleNotFoundError, but BaseLogic.__init__ immediately calls dotenv.get_key(ENV_FILE_PATH, "WORKING_DIR") (baseLogic.py:78). If python-dotenv is not installed and is not a dependency of the installed Supervisely release, the module fails to load with NameError instead of the intended blocked-widget message.
  ```
  import dotenv  # isort:skip
  ```
  Suggestion: Declare python-dotenv in requirements.txt and handle its absence explicitly in import_supervisely().

### No automated tests and no sample data in the repository
info; utility; raised by haiku
- **haiku** (info, high confidence, quote no quote) no file cited: The file list contains no test directory or sample data. Behaviour that touches a live server (login, download, upload, tag and figure sync) cannot be checked by a reviewer or regression-tested. This is a maturity point and is non-blocking under the index policy.
  Suggestion: Add unit tests for the pure helpers in utils.py (requirement parsing, backup/restore) and document a test Supervisely instance or mock for the logic layer.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
A functional, well-documented Slicer↔Supervisely client (MIT, tier 1) with no telemetry, no obfuscation and no AI-directed text. The main problems are environmental and destructive: opening the module pip-installs the Supervisely SDK and its missing requirements into Slicer's shared Python behind an OK-only dialog (no opt-out) and then restarts Slicer, and the module's clear() calls slicer.mrmlScene.Clear(), wiping the user's whole scene including data the extension did not load. Also GUI-thread network work, plaintext credentials in ~/.supervisely_slicer.env, and an undeclared python-dotenv import. Needs fixes before offering to users.
Not checked: The Supervisely SDK source and its license terms (only the extension's own MIT LICENSE was read).; Whether python-dotenv is a transitive dependency of supervisely 6.74.48.; The contents of .github/workflows/build_installation_files.yml, FOR_DEVELOPERS.md, setup.cfg, .vscode/*, the .ui files and the binary images.; Whether Slicer's slicer.util.restart() prompts the user to save the scene before restarting.; Actual build/CI results for this revision and whether the extension loads on the supported Slicer versions.; The exact commit 5280d7a versus the master branch the catalog entry points at.
Questions for the author: Is python-dotenv guaranteed to be installed by the Supervisely SDK, or should it be added to requirements.txt?; Would you accept replacing the OK-only install dialog with a confirm/cancel dialog and installing requirements with --no-deps?; Can clear() be changed to remove only the nodes the extension created instead of calling slicer.mrmlScene.Clear()?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
ConnectToSupervisely is a well-structured 3D Slicer extension that integrates with the Supervisely annotation platform. Review of its source code, build configuration, dependency management, and safety aspects revealed no blocking issues or concerns. The MIT License provides clear distribution permission, and CMake packaging is correctly configured. 🟢 Recommend merge
Not checked: Executing the extension inside 3D Slicer and exercising full integration against a live Supervisely server.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
The code is a plausible, MIT-licensed Slicer scripted module with CMake files that list every imported Python file and an EXTENSION_DEPENDS value that matches the catalog entry. The main concern is that opening the module installs the pinned supervisely SDK and its missing transitive dependencies into Slicer's shared Python environment after only an informational dialog, followed by a forced restart. Credentials can be stored in plaintext in a home-directory .env file when the user ticks "remember login". The catalog entry tracks the floating "master" branch. I did not run anything, and I did not inspect segmentation logic beyond the first 120 lines.
Not checked: Full segmentation.py (only lines 1-120 read) and the rest of ui.py-driven logic beyond what was shown.; README.md and FOR_DEVELOPERS.md were not read, so the documented consent and privacy text was only confirmed through a grep match at README.md:139.; The transitive dependency tree of supervisely==6.74.48 (whether it pulls in opencv-python, PyQt, or pins numpy/requests) was not verified.; The source commit 5280d7a was not fetched; all inspection relied on the snapshot in the catalog file listing.; The .github/workflows/build_installation_files.yml was only grep-matched, not read in full.; No CI/build results, Slicer version compatibility, or runtime behaviour were verified; nothing was executed.


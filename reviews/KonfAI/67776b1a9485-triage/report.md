# AI review: KonfAI

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/vboussot/SlicerKonfAI at commit `67776b1a948593e52745d21ae718b86bc20cce13`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T10:23:29Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | concern |
| environment | concern | ok | concern |
| packaging | minor | ok | ok |
| license | ok | ok | ok |
| soundness | minor | ok | minor |
| utility | ok | ok | ok |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: KonfAI is a Slicer module that downloads KonfAI "Apps" (segmentation, synthetic CT, registration models) from Hugging Face or local folders, runs inference/evaluation/uncertainty on scene volumes through an external `konfai-apps` CLI, and can offload the computation to a user-configured remote GPU server. It targets clinical-research users who want deep-learning pipelines in Slicer without writing Python.
- **flash-lite**: KonfAI is a 3D Slicer extension that lets users run KonfAI deep learning applications (segmentation, synthetic CT, registration) from Hugging Face or local folders on volumes in the Slicer scene, providing evaluation, uncertainty estimation, and local or remote execution.
- **haiku**: KonfAI is a 3D Slicer scripted module that runs KonfAI Apps (segmentation, synthetic CT, registration) from Hugging Face or local folders on Slicer volumes, with evaluation, uncertainty, and optional local or remote GPU execution. It is for medical-imaging researchers who want to run deep-learning workflows inside Slicer.

## Disagreements (start here)

### D1. Runtime pip installs into Slicer's shared Python environment
single; category environment; raised by haiku
- **haiku** (major, medium confidence, quote partly verified) [`KonfAI/KonfAILib/logic/dependencies.py:103`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/logic/dependencies.py#L103): On first use of the module, konfai-apps and its dependencies are pip-installed into Slicer's Python environment, pinned to the newest PyPI release. The install-or-upgrade is prompted, which is good. Lines 153-155 also run a '--force-reinstall --no-deps' of konfai-apps followed by an unpinned pip install of numpy, tensorboard and others. These can change packages Slicer relies on or other extensions use. They are not visible to users who never open the module, but they are installed once they open it.
  ```
  if installed is None:
          ...
          slicer.util.pip_install(f"{package}=={latest}")
  ```
  Suggestion: Pin the dependency set to versions compatible with the Slicer release, avoid unpinned installs of packages Slicer bundles (numpy), and document the installed packages in the tutorial.

### D2. `keyring` is pip-installed into Slicer's Python silently, with no user confirmation
single; category environment; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`KonfAI/KonfAILib/logic/servers.py:58`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/logic/servers.py#L58): Any time a RemoteServer object is constructed (module entry when stored remote servers exist in QSettings, or when a run/check is triggered), an ImportError triggers `slicer.util.pip_install("keyring")` with no prompt. This mutates the shared Slicer environment for the user without consent, and the same pattern is repeated in both server dialogs. If the install fails or pulls a different version than expected, it affects every Slicer session, not just this module.
  ```
      try:
          import keyring
      except ImportError:
          slicer.util.pip_install("keyring")
      import keyring  # noqa: F811
  ```
  Suggestion: Bundle keyring as a declared dependency (or ask the user first via the existing ask_user_to_install_dependency helper) and disable the remote-token feature with an explanatory message when keyring is unavailable.

### D3. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D4. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Catalog entry tracks a moving branch, not a fixed revision
minor; packaging; raised by haiku; **quote not found in source**
- **haiku** (minor, high confidence, quote file not found) [`KonfAI.json:1`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI.json#L1): The entry pins 'main', so the built extension changes with every commit. The review covers the source as of the commit named in the review request, not a fixed commit.
  ```
  "scm_revision": "main",
  ```
  Suggestion: Pin scm_revision to a specific commit or tag after review.

### Hugging Face repo id / app name interpolated into a generated `-c` script
minor; safety; raised by deepseek
- **deepseek** (minor, low confidence, quote verified) [`KonfAI/KonfAILib/widgets/panels/selection.py:444`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/widgets/panels/selection.py#L444): The refresh/download action builds a Python source string with textwrap.dedent f-string interpolation of `app._repo_id` and `app._app_name` and executes it with `sys.executable -c`. `selected_files` is inserted with !r (safe), but the repo id and app name are inserted verbatim inside double quotes, so a quote character in either value would break out of the literal and inject code into the executed script. The values come from app objects the user selected, so this is a robustness/defense-in-depth issue rather than an established external attack path.
  ```
                      for filename in selected_files:
                          LocalAppRepositoryFromHF.download(
                              "{app._repo_id}",
                              "{app._app_name}" + "/" + filename,
                              True,
                          )
  ```
  Suggestion: Insert these values with `{app._repo_id!r}` / `{app._app_name!r}`, or run the download in-process / from a real script file with arguments instead of -c.

### Icons referenced by the code are not installed by the module CMakeLists
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`KonfAI/CMakeLists.txt:40`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/CMakeLists.txt#L40): `core_widget.py` loads `Icons/studio.png` and `helpers.app_task_icon` loads `Icons/task_segmentation.png` / `task_registration.png` / `task_synthesis.png` / `task_app.png`, but MODULE_PYTHON_RESOURCES only lists download.png, folder.png, gear.png, KonfAI.png and refresh.png. In a package built by the extension factory those files are absent, so the Studio button and the app-selector glyphs render as empty icons for end users, even though they exist in the source tree (10 files under Resources/Icons).
  ```
    Resources/Icons/download.png
    Resources/Icons/folder.png
    Resources/Icons/gear.png
    Resources/Icons/${MODULE_NAME}.png
    Resources/Icons/refresh.png
  ```
  Suggestion: Add Resources/Icons/studio.png and Resources/Icons/task_*.png to MODULE_PYTHON_RESOURCES (or list all icons in Resources/Icons).

### Network work on the GUI thread
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`KonfAI/KonfAILib/widgets/core_widget.py:581`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/widgets/core_widget.py#L581): populate_apps() lists Hugging Face repositories and builds app objects on the GUI thread (using processEvents feedback), `_update_ram`/`_update_vram` issue an HTTP GET to the remote server every 3 s while the module is visible, and `get_latest_pypi_version` blocks up to 5 s on module entry. With a slow or unreachable server the module panel freezes during those calls.
  ```
      def _update_resources(self) -> None:
          self._update_ram()
          self._update_vram()
  
      def _update_ram(self) -> None:
          """
  ```
  Suggestion: Move the remote polling and repository listing to a worker thread or a QProcess/QtNetwork request and update the widgets from the main thread.

### Recursive delete of a folder path taken from the app object
minor; safety; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`KonfAI/KonfAILib/widgets/panels/selection.py:375`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/widgets/panels/selection.py#L375): When the user ticks 'Also delete the folder from disk' and confirms the warning dialog, `shutil.rmtree(app.get_name())` deletes whatever path the local app repository reports. The path is not validated against the app repository root and may be relative, so it resolves against Slicer's current working directory. The action is explicitly double-confirmed by the user, which limits the risk.
  ```
          if chk.isChecked():
              if isinstance(app, LocalAppRepositoryFromDirectory):
                  try:
                      shutil.rmtree(app.get_name())
  ```
  Suggestion: Resolve the app directory from the repository object and refuse to delete unless it is inside the known KonfAI app repository/cache root.

### Remote server bearer token is passed on the child-process command line
minor; safety; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`KonfAI/KonfAILib/logic/servers.py:84`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/logic/servers.py#L84): cli_args() appends `--token <token>` to the konfai-apps argv. On shared multi-user machines any local user can read the full command line of the child process (e.g. via ps), exposing the remote GPU server credentials the extension stores encrypted in the keyring. The token is only sent to a server the user configured, so the exposure is local and modest.
  ```
          args = ["--host", self.host, "--port", str(self.port)]
          if self.token:
              args += ["--token", self.token]
  ```
  Suggestion: Pass the token through an environment variable or a 0600 temporary config/credential file rather than argv.

### Repair path pip-installs unpinned packages that Slicer bundles (numpy, requests)
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`KonfAI/KonfAILib/logic/dependencies.py:153`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/logic/dependencies.py#L153): On the 'reinstall KonfAI-apps' branch the extension installs `tqdm numpy ruamel.yaml psutil tensorboard lxml h5py nvidia-ml-py requests huggingface_hub` unpinned in one pip call. If any package is missing (e.g. on a Slicer build where a dependency was not satisfied) pip resolves and installs the latest release, including its transitive requirements, which can upgrade numpy/requests under Slicer's feet. This runs only after user consent, which limits the impact.
  ```
              slicer.util.pip_install(f"--upgrade --force-reinstall --no-deps konfai-apps=={latest}")
              slicer.util.pip_install(
                  "tqdm numpy ruamel.yaml psutil tensorboard lxml h5py nvidia-ml-py requests huggingface_hub"
              )
  ```
  Suggestion: Let konfai-apps' own metadata declare these dependencies (install it without --no-deps), or constrain them so Slicer-bundled packages such as numpy and requests are never upgraded.

### Run failures are swallowed with a bare print
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`KonfAI/KonfAILib/widgets/app_template.py:108`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/widgets/app_template.py#L108): In on_run_button, any exception raised while preparing or starting the run is only `print(e)`ed and the running flag is reset; the user sees the log/progress stop but no error message. For instance a missing `konfai` module or a broken app manifest leaves the user with a silently cancelled operation.
  ```
              try:
                  function(remote_server, device)
              except Exception as e:
                  # Log the exception for debugging and reset running state
                  print(e)
                  self.set_running(False)
  ```
  Suggestion: Also report the exception in the log panel and via slicer.util.errorDisplay (with details/traceback).

### `eval()` applied to a string read back from the parameter node
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`KonfAI/KonfAILib/widgets/app_template.py:198`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/widgets/app_template.py#L198): get_remote_server splits the `RemoteServer` parameter on '|' and evaluates the fourth field to a bool. Today only the module writes that parameter, so this is not an injection path from outside, but a saved scene file can carry arbitrary parameter strings, and a crafted .mrs scene would execute code when the module runs a job with a remote server set.
  ```
          if self._parameter_node is not None and self._parameter_node.GetParameter("RemoteServer") != "None|True":
              name, host, port, ok = self._parameter_node.GetParameter("RemoteServer").split("|")
              return RemoteServer(name, host, port) if host != "None" else None, eval(ok)
  ```
  Suggestion: Replace `eval(ok)` with `ok == "True"`.
- **haiku** (minor, medium confidence, quote verified) [`KonfAI/KonfAILib/widgets/app_template.py:199`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/widgets/app_template.py#L199): eval() runs on the 'ok' field of a string stored in the parameter node. The value is written by the extension itself (a bool string), so the practical risk is low. Still, a parameter node could be edited or loaded from a scene file, so eval() on it is an unnecessary code-execution surface. Replacing it with a literal comparison such as ok == 'True' removes the risk.
  ```
  name, host, port, ok = self._parameter_node.GetParameter("RemoteServer").split("|")
              return RemoteServer(name, host, port) if host != "None" else None, eval(ok)
  ```
  Suggestion: Replace eval(ok) with ok == "True" (or ast.literal_eval), and parse the field explicitly.

### keyring and konfai-studio installed on demand
minor; environment; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`KonfAI/KonfAILib/widgets/core_widget.py:279`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/widgets/core_widget.py#L279): The Studio install is only after a user click (confirmed by a dialog), so it is consent-based. keyring is installed on first remote-server use in servers.py line 61. Both are pip installs of unpinned packages into the shared Python environment.
  ```
  with slicer_wait_popup("KonfAI Studio", "Installing konfai-studio..."):
                      slicer.util.pip_install("konfai-studio")
  ```
  Suggestion: Pin the versions, and state the packages in the documentation.

### Module import deletes KonfAILib entries from sys.modules
info; environment; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`KonfAI/KonfAI.py:36`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAI.py#L36): KonfAI.py purges every `KonfAILib*` entry from sys.modules at import time to support Slicer's Reload. That is a global interpreter side effect: sister extensions (ImpactSynth, ImpactReg) holding references to old KonfAILib classes keep stale identities, as the author's own comment acknowledges. It does not affect modules that do not import KonfAI.
  ```
  for _cached_module in [name for name in sys.modules if name == "KonfAILib" or name.startswith("KonfAILib.")]:
      del sys.modules[_cached_module]
  ```
  Suggestion: Only purge on an explicit Reload path (e.g. when the module is re-executed as a reload, detectable via the wasSetupOnce property used below), or document the constraint in README.

### One-click install and detached launch of a local web app that can drive an LLM CLI
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`KonfAI/KonfAILib/widgets/core_widget.py:205`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/KonfAILib/widgets/core_widget.py#L205): The Studio button can pip-install `konfai-studio` after a confirmation dialog, launch it detached on 127.0.0.1:8730, and the launcher deliberately appends `~/.local/bin` to PATH because that is where the `claude` CLI ('Studio's default brain') lives. The server is loopback-only and the user consents, but users should understand that this third-party tool is started outside Slicer's process and keeps running after Slicer closes.
  ```
          inside_slicer = executable.startswith(slicer.app.slicerHome)
          env = dict(os.environ) if inside_slicer else dict(slicer.util.startupEnvironment())
          user_bin = os.path.expanduser("~/.local/bin")
          path = env.get("PATH", "")
          if user_bin not in path.split(os.pathsep):
              env["PATH"] = f"{path}{os.pathsep}{user_bin}" if path else user_bin
  ```
  Suggestion: Keep the consent dialog, and document in README that Studio is a separate, persistent local web app.

### Single API-contract test; no functional tests
info; utility; raised by haiku
- **haiku** (info, medium confidence, quote partly verified) [`KonfAI/CMakeLists.txt:60`](https://github.com/vboussot/SlicerKonfAI/blob/67776b1a948593e52745d21ae718b86bc20cce13/KonfAI/CMakeLists.txt#L60): The only automated test checks that public symbols exist. Inference, evaluation and remote-server behavior have no tests in the repo. This is a non-blocking maturity note.
  ```
  slicer_add_python_unittest(
    SCRIPT KonfAIApiContractTest.py
  ```
  Suggestion: Add a small smoke test on bundled or public sample data.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Reviewed all Python sources, CMake files and the packaging layout of SlicerKonfAI. No malicious, obfuscated or exfiltrating behavior found: network use is limited to Hugging Face/PyPI lookups, a user-configured remote server, and a loopback Studio server the user is asked about. The main problem is the shared Python environment: the extension pip-installs `keyring` silently (no prompt) from `RemoteServer.__init__`/dialogs, and the KonfAI repair path pip-installs unpinned `numpy`, `requests`, `h5py`, `lxml`, etc. into Slicer's Python. Secondary issues: two icon sets referenced by code are not installed by CMake, remote tokens are passed on the child-process command line, and one `eval()` on a parameter-node string. License (Apache-2.0) and catalog entry are fine.
Not checked: Whether `konfai-apps` / `konfai` on PyPI (installed at runtime by install_konfai) pull `torch` or other Slicer-bundled packages as transitive requirements — the package metadata could not be fetched during this review.; License terms of the Hugging Face app repositories and model weights downloaded at runtime (VBoussot/ImpactSynth, MRSegmentator-KonfAI, TotalSegmentator-KonfAI, ImpactSeg, DentalSegmentator-KonfAI) and of `konfai-studio`.; Behaviour of the external `konfai-apps` CLI itself (network destinations, what it uploads to a remote server, model handling), which is not part of this repository.; Contents of README.md and TUTORIAL.md beyond their existence and size; not read in full within this review.; Binary resources (KonfAI.png, screenshots, mp4 videos) and the .ui files, which were not parsed.; Whether the pinned commit 67776b1a corresponds to the current `main` tip (the catalog entry tracks the branch).
Questions for the author: Does `konfai-apps` (or `konfai`) declare `torch` as a dependency on PyPI? If so, `pip_install(f"konfai-apps=={latest}")` can install PyTorch outside the Slicer PyTorch extension — how is that avoided?; Why is `keyring` installed at RemoteServer construction time instead of being declared/confirmed up front?; Could Resources/Icons/studio.png and Resources/Icons/task_*.png be added to MODULE_PYTHON_RESOURCES, given the code loads them?; What license do the Hugging Face apps/weights distributed under VBoussot/* carry, and is redistribution/clinical-research use documented in README?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The KonfAI extension is well-structured, follows Slicer conventions for scripted modules and dependencies (such as instructing users to install PyTorch via SlicerPyTorch), includes clear Apache 2.0 licensing, and provides a mechanically usable catalog entry. 🟢 Recommend merge
Not checked: Exhaustive inspection of all UI files and widgets (core_widget.py, app_template.py, etc.) beyond what was read.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
Reviewed the catalog entry and roughly 20 source files of the KonfAI extension (Apache-2.0). I found no malicious or concealed behavior in what I read. The main concerns are environment-level: on-demand pip installs of konfai-apps, konfai-studio and keyring with pins to latest PyPI, and an eval() of a stored string in app_template.py. The entry uses branch "main" rather than a fixed revision, and the Testing directory has only one API-contract test. Several files (core_widget, selection, inference panel, app_template) were only partially read, and the three large MP4 files were not inspected.
Not checked: Full bodies of core_widget.py, app_template.py, panels/inference.py, panels/selection.py and dialogs/remote_server.py beyond the excerpts read.; The three large MP4 screenshots and the binary PNG/JPG assets (not readable with the available tools).; The upstream konfai and konfai-apps packages and the Hugging Face app repositories that are downloaded and executed at runtime (model weights and any code they contain).; Whether the pinned scm_revision exists; I did not resolve the repository or the 'main' commit.; Clinical-use disclaimer and model provenance for the Hugging Face apps.; CI results and build of the extension in Slicer; none were available in the review input.; The KonfAIApiContractTest.py contents (only its size and registration were visible).
Questions for the author: Can you pin scm_revision to a tagged or commit-hash release instead of 'main'?; Can you replace eval(ok) in app_template.py with an explicit string comparison?; Which konfai-apps and konfai versions are tested with Slicer 5.10+, and can the installer use pinned versions?; Is there a clinical-use disclaimer, and what is the license and provenance of the Hugging Face model apps?


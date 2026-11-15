# AI review: ImpactReg

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/vboussot/SlicerImpactReg at commit `0103b37caabcb4431f7cc4570156b5b627dd4249`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T10:11:45Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | minor |
| environment | concern | ok | concern |
| packaging | ok | ok | minor |
| license | minor | ok | minor |
| soundness | minor | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer front-end (GUI wrapper around the `impact-reg-konfai` CLI) for multimodal deformable image registration driven by the IMPACT deep-feature similarity metric through KonfAI, running elastix / ConvexAdam / FireANTs presets, optionally ensembling them, and evaluating the result on images, segmentations or landmarks or estimating uncertainty from the ensemble spread. Aimed at researchers and clinical users registering MRI/CT/CBCT of the same patient inside Slicer.
- **flash-lite**: ImpactReg is a 3D Slicer extension for multimodal medical image registration driven by the IMPACT metric across multiple registration engines (elastix, ConvexAdam, FireANTs), powered by KonfAI.
- **haiku**: ImpactReg is a 3D Slicer scripted module that runs multimodal image registration (IMPACT metric via elastix, ConvexAdam and FireANTs presets) by driving the impact-reg-konfai command-line tool through the KonfAI extension. It is aimed at medical imaging researchers who register MRI, CT and CBCT volumes and evaluate the result with images, segmentations, landmarks or ensemble uncertainty.

## Disagreements (start here)

### D1. PyTorch is a hard requirement but is not declared; torch may be pulled from PyPI instead of PyTorchUtils
single; category environment; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`CMakeLists.txt:13`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/CMakeLists.txt#L13): The extension only declares KonfAI (`set(EXTENSION_DEPENDS "KonfAI")`, build_dependencies ["KonfAI"]), while README.md:140-141 tells users to install the SlicerPyTorch extension and states that `impact-reg-konfai` is then pip-installed into Slicer's Python on first open. If `impact-reg-konfai` declares torch in its requirements (its whole purpose is running torch-based presets), pip will pull a PyPI torch build on Impact Reg's first open — exactly the pattern the review policy asks to prevent (torch must come through PyTorchUtils/SlicerPyTorch, declared in build_dependencies and EXTENSION_DEPENDS). I could not read impact-reg-konfai's requirements.txt, so this is flagged as a probable rather than proven path to a duplicated/CUDA-mismatched torch in Slicer's environment.
  ```
  set(EXTENSION_DEPENDS "KonfAI")
  ```
  Suggestion: Add PyTorch to EXTENSION_DEPENDS/build_dependencies, and make `impact-reg-konfai` install torch only through PyTorchUtils (or declare torch as an already-satisfied dependency). Point to the exact requirements file in a follow-up message so it can be verified.

### D2. pip-installs impact-reg-konfai (with pinned konfai/konfai-apps) into Slicer's shared Python on every module open
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`ImpactReg/ImpactReg.py:482`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/ImpactReg/ImpactReg.py#L482): ImpactRegWidget.enter() runs the KonfAI extension's shared `install_package` for a package fetched from PyPI. The author's own comment above the call says that package 'pins and pulls the matching konfai / konfai-apps': if the pin is older than the installed KonfAI extension package, opening Impact Reg can silently downgrade the package another extension depends on, affecting every user of that extension, not only Impact Reg users. The install/prompt behavior lives in the KonfAI extension, which is not in this repository, so whether the user is asked and whether the pin can downgrade KonfAI could not be verified here.
  ```
  install_package("impact-reg-konfai", "IMPACT-Reg")
  ```
  Suggestion: State the exact `impact-reg-konfai` version range and confirm on the KonfAI/pip side that its requirements are `>=` (never `==`) for konfai/konfai-apps, that the install is user-confirmed and version-checked, and that a failed install surfaces to the user. If the dependency cannot be relaxed, install it in a dedicated venv instead of Slicer's interpreter, or ship it through the extension build.
- **haiku** (major, medium confidence, quote verified) [`ImpactReg/ImpactReg.py:482`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/ImpactReg/ImpactReg.py#L482): enter() calls install_package("impact-reg-konfai", ...) each time the module is opened. Per README.md line 141 and the module's own comment, this pins the matching konfai and konfai-apps versions in Slicer's shared environment. That can change or downgrade packages other extensions use, and I could not confirm from the repository that the user is asked before this happens. The package is needed only for this module, so it is not a safety issue, but the shared-environment side effect needs an explicit, confirmed install.
  ```
  install_package("impact-reg-konfai", "IMPACT-Reg")
  ```
  Suggestion: Ask for confirmation before installing, and report which konfai/konfai-apps versions will be pinned. Document the environment change in the README. Verify the behaviour of KonfAI's install_package.

### D3. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Catalog pins a moving branch and a 9 MB video is committed to the source repo
minor; packaging; raised by haiku; **quote not found in source**
- **haiku** (minor, high confidence, quote file not found) [`catalog entry`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/catalog entry): scm_revision is "main", so the exact reviewed source can change without a catalog update. The 9 MB tutorial video referenced in the text-scan hints is committed to the repository and is not needed at runtime.
  ```
  "scm_revision": "main",
  ```
  Suggestion: Pin scm_revision to a tagged commit for the release, and consider hosting the video externally (the README already links to it).

### Fallback evaluation path can pass None as a CLI argument and crash the run
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ImpactReg/ImpactReg.py:304`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/ImpactReg/ImpactReg.py#L304): When no evaluation tab is active, `_export_node` can return None (nothing selected in the reference or moving selectors), yet the code unconditionally appends the value to the argument list, so `impact-reg-konfai eval -f None -m None` is constructed or the process launcher raises. The user gets a traceback instead of the 'select a reference image' message; also a failed `slicer.util.saveNode` is ignored and a non-existent filename is forwarded.
  ```
  fixed_file = self._export_node(self.ui.referenceVolumeSelector.currentNode(), "FixedImage")
  ```
  Suggestion: Check for None (and the boolean return of `saveNode`) and report a clear message with `set_running(False)`, as the registration panel does for missing inputs.

### No automated test despite the CMake test entry
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`ImpactReg/Testing/Python/CMakeLists.txt:2`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/ImpactReg/Testing/Python/CMakeLists.txt#L2): `slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)` registers ImpactReg.py as a CTest, but the module file contains no `ScriptedLoadableModuleTest` subclass (only module/widget classes), and the extra Python test is commented out. The registered test can therefore report nothing or fail as 'no test found', and no regression coverage exists for the argument construction that is the heart of the module. The video/tutorial manual workflow is the only validation.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a ModuleTest class that at least instantiates the widget and, with small synthetic volumes, checks the generated `register`/`eval` argument lists.
- **haiku** (minor, high confidence, quote verified) [`ImpactReg/Testing/Python/CMakeLists.txt:2`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/ImpactReg/Testing/Python/CMakeLists.txt#L2): ImpactReg/CMakeLists.txt registers ImpactReg.py as a Python unittest under BUILD_TESTING. The file has no unittest class, and the only test file is commented out, so CTest runs no meaningful test. This makes the module's logic (argument construction, output loading) unverified by automated tests.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a test that checks the CLI argument construction and the output-loading path with a small fixture, or remove the misleading BUILD_TESTING registration.

### Output file names derive from downloaded app-manifest keys and are joined to the temp folder without sanitization
minor; safety; raised by deepseek
- **deepseek** (minor, low confidence, quote verified) [`ImpactReg/ImpactReg.py:321`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/ImpactReg/ImpactReg.py#L321): The evaluation export uses the manifest key as a filename base: `file_name = self._export_node(selector.currentNode(), key)` and then `self._work_dir / f"{base}.mha"`. Keys come from the preset `app.json` fetched from Hugging Face rather than from this repository, so a manifest containing `../` segments would make `slicer.util.saveNode`/`_write_volume` write outside the temporary folder. Impact is bounded by the fixed `.mha`/`.fcsv` suffixes and requires a compromised or malicious upstream manifest, hence low confidence and minor severity.
  ```
  file_name = self._export_node(selector.currentNode(), key)
  ```
  Suggestion: Whitelist/escape the manifest keys (e.g. take os.path.basename and allow only [A-Za-z0-9_-]) before using them as file names.

### Presets, model weights and a GPU-specific binary are downloaded and executed on first use without per-item confirmation or visible verification
minor; safety; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`ImpactReg/ImpactReg.py:92`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/ImpactReg/ImpactReg.py#L92): The first run of a preset triggers downloads that are executed locally: the preset apps from Hugging Face (`VBoussot/ImpactReg`, whose python/yaml configs drive the run), the TorchScript feature models, `pip install fireants`, and the elastix-IMPACT binary built for the installed CUDA (README.md:103, README.md:141). This is the advertised function and is documented, but nothing in this repository shows hash/signature verification of these payloads; that logic, if any, is in impact-reg-konfai and could not be inspected. A compromised upstream hub repo would therefore run code inside the user's registrations.
  ```
  "Registration presets are distributed as KonfAI Apps (downloaded automatically from Hugging Face),"
  ```
  Suggestion: Surface a confirmation before the first download of each preset/binary and state (in the UI or README) whether downloads are integrity-checked and from which exact repository/revision.

### Registration end callback loads Moved.mha without checking that the file exists
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ImpactReg/ImpactReg.py:224`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/ImpactReg/ImpactReg.py#L224): Only `Transform.h5` is checked before continuing; `Moved.mha` is read and pushed with no existence test, and per-preset fields are globbed with `sorted((case_dir / "Ensemble").glob("*.h5"))`, which silently yields an empty sequence if `--keep-fields` produced nothing. A partial CLI run therefore raises inside the completion callback (leaving the panel without a message) or leaves an empty DVF sequence behind while the log still reports success.
  ```
  moved_node = sitkUtils.PushVolumeToSlicer(
  ```
  Suggestion: Verify the presence of `Moved.mha` (and warn when `Ensemble/` is empty although uncertainty was ticked) and report the problem through `_update_logs(..., False)`.

### Remote-server access token is passed on the command line (visible in the process list)
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`ImpactReg/ImpactReg.py:206`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/ImpactReg/ImpactReg.py#L206): When a remote server is selected, the login token is appended as a plain CLI argument to the `impact-reg-konfai` process: any local user able to list processes (`ps`) on the same machine can read the credential, and it may also end up in log files or shell history. The same block also chooses the host that receives the fixed/moving images, so the destination is worth documenting explicitly for users.
  ```
  args += ["--token", remote_server.token]
  ```
  Suggestion: Pass the token through an environment variable or a stdin/temporary file with restrictive permissions instead of argv, and document in the UI that images are uploaded to the chosen host.
- **haiku** (minor, medium confidence, quote verified) [`ImpactReg/ImpactReg.py:204`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/ImpactReg/ImpactReg.py#L204): When a remote server is selected, the token is appended to the CLI argument list. Command-line arguments are visible to other local users through process listings and may be logged. The data path itself (images sent to a user-chosen server) is opt-in through the server selection.
  ```
  args += ["--host", remote_server.host, "--port", str(remote_server.port)]
              if remote_server.token:
                  args += ["--token", remote_server.token]
  ```
  Suggestion: Pass the token through an environment variable or a file with restricted permissions rather than on the command line.

### Terms of downloaded presets and model weights are not stated in the repository
minor; license; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`README.md:103`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/README.md#L103): The module downloads presets, feature models (TotalSegmentator, MIND, anatomix), elastix-IMPACT binaries and fireants at run time. README.md line 103 refers to a NOTICE for FireANTs, but no such file or summary of the terms for the models is in the repository. The redistribution and commercial-use terms for these downloads cannot be checked from the repository alone.
  ```
  FireANTs is distributed under its own license, shipped in each preset's `NOTICE`.
  ```
  Suggestion: Add a short section listing the license of each downloaded model, binary and preset, with links.

### 9 MB tutorial video committed to the repository
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.md:37`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/README.md#L37): The repository carries `Screenshots/SlicerImpactReg-tutorial.mp4` (9 MB) in git history; it is not needed for building or running the module and only bloats the checkout and the archive the index fetches. Non-blocking packaging observation.
  ```
  <!-- Drop Screenshots/SlicerImpactReg-tutorial.mp4 into the README editor on GitHub and paste the user-attachments URL it gives here: GitHub then embeds a player. -->
  ```
  Suggestion: Host the video on a release asset or external page and link to it, rather than committing it.

### No research-only / clinical-use disclaimer
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.md:134`](https://github.com/vboussot/SlicerImpactReg/blob/0103b37caabcb4431f7cc4570156b5b627dd4249/README.md#L134): The module is positioned for radiotherapy-style CT/CBCT and MR/CT registration and the README reports Dice/TRE improvements on one case, but nothing states that results are research outputs that must be verified before clinical use (README.md:134 only says 'One case: validate the presets on your own data before drawing conclusions from this table'). Users may otherwise treat the automatic transform as clinically validated.
  ```
  One case: validate the presets on your own data before drawing conclusions from this table.
  ```
  Suggestion: Add an explicit disclaimer (README and module help/acknowledgment text) that the module is not a certified medical device and that registration results must be checked by a qualified user.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Well-documented thin GUI over `impact-reg-konfai` plus the KonfAI extension; no malicious, obfuscated or data-exfiltrating code was found in the reviewed module, and the module code is Apache-2.0. Two environment questions are the main open issues: on every module open the widget pip-installs `impact-reg-konfai`, which (per the author's own comment) pins/pulls `konfai`/`konfai-apps`, and PyTorch is not declared as a dependency even though it is required — the catalog entry and CMake list only KonfAI, so torch may come from PyPI instead of PyTorchUtils. Ordinary bugs (None passed as a CLI filename, unchecked output file) are minor. 🔴 Do not merge yet: Review incomplete — confirm `impact-reg-konfai`'s dependency resolution (torch via PyTorchUtils, no konfai downgrade).
Not checked: KonfAI extension source (install_package, KonfAICoreWidget/process.run, RemoteServer host/port/token handling, temporary `_work_dir` creation and cleanup, IPython/main-thread behaviour of the completion callbacks) - not part of this repository; impact-reg-konfai PyPI package contents and requirements (torch/konfai pins, download/integrity verification, `--host/--port/--token` transport security) - no access to PyPI; Hugging Face preset apps (VBoussot/ImpactReg) and feature models (VBoussot/impact-torchscript-models): their code, revisions, hashes and licenses; Licenses of fireants, itk-impact and the elastix-IMPACT binary mentioned in the README; Build/CTest results: not built or run; no CI reports available in this environment; Binary/asset files (ImpactReg.png, Screenshots/*.jpg, Screenshots/SlicerImpactReg-tutorial.mp4) not read; Verification that the reviewed commit 0103b37caabcb4431f7cc4570156b5b627dd4249 is what the catalog's `scm_revision: "main"` currently resolves to
Questions for the author: What are the exact requirements of `impact-reg-konfai` (especially torch, konfai, konfai-apps) and are they declared with `>=` ranges so an existing PyTorch-extension / KonfAI install is never replaced or downgraded?; Does the shared `install_package` in the KonfAI extension ask the user before installing, and does it reuse an already-installed compatible version instead of reinstalling on every module open?; Are the Hugging Face preset apps, the TorchScript feature models, the elastix-IMPACT binary and `fireants` integrity-checked (hash/signature) and pinned to a revision?; Under which licenses are the presets/model weights and the downloaded elastix-IMPACT and fireants binaries distributed, and can those licenses be added to the repository (e.g. a NOTICE file)?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
ImpactReg is a clean, well-structured 3D Slicer extension for multimodal image registration using the IMPACT similarity metric across multiple backends (elastix, ConvexAdam, FireANTs) via KonfAI. All files conform to Slicer extension standards, dependencies are correctly declared, and safety, licensing, and environment requirements are fully met.
Not checked: Binary assets and video files; External behavior of KonfAI framework and impact-reg-konfai package on PyPI

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
The module code I could read (ImpactReg/ImpactReg.py, CMake files, README, TUTORIAL) is a thin UI layer over KonfAI: it writes inputs to a temp folder, runs the CLI via a process manager, and loads outputs. I found no obfuscation, no telemetry, and no unsafe deserialization. The main concerns are the runtime pip installation into Slicer's Python on module entry (which pins konfai/konfai-apps), the unverified licensing of downloaded presets and feature models, and the absence of working tests. The KonfAI dependency, the downloaded payloads and the video were not inspected.
Not checked: KonfAI extension source, including install_package() and whether it asks for consent before pip installs.; The impact-reg-konfai PyPI package and its pinned dependencies.; Hugging Face presets (VBoussot/ImpactReg), the feature models, the elastix-IMPACT binary and the fireants package, including their licenses and the integrity of the downloads.; The source at scm_revision main; I reviewed only the files shown in the prompt, not the exact commit.; Screenshots/SlicerImpactReg-tutorial.mp4 and the binary images; ImpactReg/Resources/Icons contents.; Whether the module runs in Slicer; no build or run was possible.


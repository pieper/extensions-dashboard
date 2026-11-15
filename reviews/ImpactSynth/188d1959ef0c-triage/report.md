# AI review: ImpactSynth

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/vboussot/SlicerImpactSynth at commit `188d1959ef0c6782fcebc9a533b0ccb9964410bf`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T10:22:05Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | unknown |
| environment | minor | ok | concern |
| packaging | minor | ok | ok |
| license | ok | ok | ok |
| soundness | minor | ok | minor |
| utility | ok | ok | ok |
| **overall** | minor issues | no concerns | incomplete |

## What each reviewer says the extension does

- **deepseek**: ImpactSynth (IMPACT-Synth) is a thin 3D Slicer front end for the TotalSynth synthetic-CT models: it registers KetFusion-free KonfAI app templates so users can run MRI/CBCT-to-CT synthesis, evaluate an sCT against a reference CT, estimate uncertainty, and run segmentation models on the sCT. Its target users are radiotherapy / medical-imaging researchers working with MR-only or CBCT-based workflows.
- **flash-lite**: ImpactSynth is a 3D Slicer extension for generating whole-body synthetic CT images from MRI or CBCT scans using pretrained TotalSynth models, evaluation tools, and segmentation pipelines powered by the KonfAI framework.
- **haiku**: ImpactSynth is a thin Slicer scripted module (ImpactSynth/ImpactSynth.py) that registers KonfAI-based app tabs for synthetic CT generation from MRI/CBCT and for segmentation of the sCT. It is aimed at radiotherapy and imaging researchers who want to run TotalSynth models inside 3D Slicer.

## Disagreements (start here)

### D1. Python package installation into Slicer's environment is triggered by the module, per the docs
partial; category environment; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`README.md:134`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/README.md#L134): Opening the module modifies Slicer's shared Python environment; TUTORIAL.md:12-14 repeats this. The actual install code lives in the KonfAI extension, which is not in this repository, so I could not verify whether the user is asked before installing, whether pinned versions of Slicer-bundled packages (numpy, scipy, SimpleITK) are downgraded, or whether PyTorch is pulled via pip rather than the SlicerPyTorch extension. The README does correctly state that PyTorch comes from SlicerPyTorch.
  ```
  2. Restart Slicer and open **Impact Synth** (category **Image Synthesis**). On the first opening, `konfai-apps` is installed into Slicer's Python.
  ```
  Suggestion: State in the module help/UI that a Python package will be installed into Slicer on first use, and confirm in the KonfAI review that the install is confirmed by the user and does not pin Slicer-bundled packages.
- **haiku** (major, medium confidence, quote verified) [`README.md:134`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/README.md#L134): README.md line 134 says 'On the first opening, konfai-apps is installed into Slicer's Python', and TUTORIAL.md line 12-13 repeats this. Installing a large dependency set (with its own transitive requirements) into the shared Slicer Python on first module use can change versions of packages Slicer and other extensions rely on. The module code here does not show whether it asks the user for confirmation or pins versions; that logic is in the KonfAI dependency and was not reviewed.
  ```
  2. Restart Slicer and open **Impact Synth** (category **Image Synthesis**). On the first opening, `konfai-apps` is installed into Slicer's Python.
  ```
  Suggestion: Document exactly which packages and versions are installed, confirm with the user before a large download, and confirm no Slicer-bundled packages (numpy, SimpleITK, torch, vtk, opencv) are downgraded or pulled in with bundled Qt/VTK. Provide the KonfAI install-logic source for review.

### D2. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings from some reviewers

### Catalog pins the branch 'main' rather than a reviewed commit
minor; packaging; raised by haiku; **quote not found in source**
- **haiku** (minor, high confidence, quote quote not found) no file cited: The catalog entry uses scm_revision 'main', so the code built by the index can change without review. This is a reproducibility concern, not a defect; the reviewed source is commit 188d1959 per the review request.
  ```
  "scm_revision": "main",
  ```
  Suggestion: Pin scm_revision to a reviewed commit SHA for stable builds, or accept the branch and rely on later re-review of updates.

### KonfAI imported at top level, so the dependency is loaded for every Slicer startup
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`ImpactSynth/ImpactSynth.py:17`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/ImpactSynth/ImpactSynth.py#L17): Slicer imports scripted-module Python files when it scans the extension module paths at startup, so this top-level import executes for every user of that Slicer installation, including users who never open Impact Synth. Whatever KonfAI pulls in at import time (its widgets, and potentially torch/other heavy dependencies) then affects startup time and memory for everyone. The same file re-imports KonfAI inside setup() (line 100), which suggests the author was aware heavy imports belong in setup() but the top-level import was left in place.
  ```
  import slicer
  from KonfAI import KonfAIAppTemplateWidget, KonfAICoreWidget, _is_reload_setup
  from qt import QWidget
  ```
  Suggestion: Move the KonfAI imports into ImpactSynthWidget.setup() (and store the classes on the instance) or into a try/except that reports a clear message, so that importing the module file has no third-party side effects.
- **haiku** (minor, medium confidence, quote verified) [`ImpactSynth/ImpactSynth.py:18`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/ImpactSynth/ImpactSynth.py#L18): ImpactSynth.py imports `_is_reload_setup` (underscore-prefixed, so private) from KonfAI at line 18, which can break silently on KonfAI changes. The only test registration is commented out in ImpactSynth/Testing/Python/CMakeLists.txt, so there are no automated tests for the module's setup logic.
  ```
  from KonfAI import KonfAIAppTemplateWidget, KonfAICoreWidget, _is_reload_setup
  ```
  Suggestion: Use a public API from KonfAI or document the coupling, and enable a basic test that checks module load and the API-version gate.

### Module fails to load entirely if KonfAI renames its private helper `_is_reload_setup`
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`ImpactSynth/ImpactSynth.py:18`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/ImpactSynth/ImpactSynth.py#L18): The module depends on an underscore-prefixed private symbol of KonfAI in a top-level import. A refactor of KonfAI's internals produces an ImportError while Slicer imports this file, so the module disappears from the module selector with only a console traceback instead of a readable diagnostic, even though the public API version check at lines 102-109 would otherwise have handled incompatibilities gracefully.
  ```
  from KonfAI import KonfAIAppTemplateWidget, KonfAICoreWidget, _is_reload_setup
  ```
  Suggestion: Import `_is_reload_setup` defensively (e.g. getattr on the KonfAI module inside setup(), defaulting to a no-op or reporting the incompatibility through the existing API-version message).

### No automated tests: the module test file is commented out and the module defines no test class
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ImpactSynth/Testing/Python/CMakeLists.txt:2`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/ImpactSynth/Testing/Python/CMakeLists.txt#L2): ImpactSynth/CMakeLists.txt:26 registers `slicer_add_python_unittest(SCRIPT ImpactSynth.py)`, but ImpactSynth.py contains no test class, and the dedicated test CMake entry is commented out. Consequently nothing exercises the widget construction, the KonfAI API-version guard, or the app registration in CI, so a broken dependency or a wrong app identifier would only be discovered by a user opening the module.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a minimal module test (instantiate the widget / check the app identifiers resolve) and enable it in ImpactSynth/Testing/Python/CMakeLists.txt.

### PEP 604 annotation `QWidget | None` requires Python >= 3.10 at import time
minor; soundness; raised by deepseek
- **deepseek** (minor, low confidence, quote verified) [`ImpactSynth/ImpactSynth.py:85`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/ImpactSynth/ImpactSynth.py#L85): Without `from __future__ import annotations` this annotation is evaluated when the class body is executed, i.e. while Slicer imports the module file; on a Slicer built with Python 3.9 this raises TypeError and the module never loads. The README requires Slicer >= 5.10, so the practical risk depends on which Python that Slicer bundles - I could not verify it here. The pre-commit config (`--py310-plus`) confirms 3.10 is the intended minimum.
  ```
  def __init__(self, parent: QWidget | None = None) -> None:
  ```
  Suggestion: Either add `from __future__ import annotations` or use `typing.Optional[QWidget]` to keep the module importable on older Python builds, and state the minimum Slicer/Python version in the README.

### PyTorch required by the README but not declared as an extension dependency
minor; packaging; raised by deepseek
- **deepseek** (minor, low confidence, quote verified) [`CMakeLists.txt:13`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/CMakeLists.txt#L13): README.md:133 instructs users to install the PyTorch extension manually and KonfAI inference needs torch, but neither the catalog entry ('build_dependencies': ['KonfAI']) nor EXTENSION_DEPENDS mentions PyTorch. A user who installs only ImpactSynth and misses step 1 gets an inference failure instead of having the dependency pulled in by the Extensions Manager (unless the separate KonfAI entry already declares PyTorch).
  ```
  set(EXTENSION_DEPENDS "KonfAI")
  ```
  Suggestion: Add PyTorch (and keep it consistent with the catalog entry's build_dependencies) if the KonfAI entry does not already declare it, or document explicitly that PyTorch is an indirect dependency satisfied by KonfAI.

### Catalog entry follows a moving branch
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`CMakeLists.txt:7`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/CMakeLists.txt#L7): The catalog entry uses "scm_revision": "main"; branch references are supported, but an approval then covers only the commit reviewed (188d1959... as given in the review request), not future code on main. Combined with the fact that the effective behaviour lives in KonfAI (downloaded apps and weights), users should be aware that the installed extension may change without a new index review.
  ```
  set(EXTENSION_HOMEPAGE "https://github.com/vboussot/SlicerImpactSynth")
  ```
  Suggestion: Consider pinning a tag per release if reproducible builds are desired.

### Large binary media committed to the repository
info; packaging; raised by haiku
- **haiku** (info, low confidence, quote verified) [`README.md:40`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/README.md#L40): The repo carries a 5 MB tutorial video and several large PNG/JPG images (ImpactSynth.png is duplicated at root and in Resources/Icons). These add to clone size but do not break loading.
  ```
  **[Watch the walkthrough](Screenshots/SlicerImpactSynth-tutorial.mp4)** (2 min, with captions)
  ```
  Suggestion: Host the video externally (the README already uses a user-attachments URL) and avoid duplicate binaries.

### Licence of downloaded model weights and pip package not stated in this repository
info; license; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`README.md:58`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/README.md#L58): The extension code is Apache-2.0, but the pretrained TotalSynth apps are downloaded from huggingface.co/VBoussot/ImpactSynth and the CLI is distributed as `impact_synth_konfai` (README.md:151); neither licence is mentioned in the README, and I could not inspect the Hugging Face model card. This does not block the index (no weights are bundled), but users lack a statement of terms for the downloaded artefacts.
  ```
  TotalSynth covers the brain, head and neck, thorax, abdomen and pelvis
  ```
  Suggestion: Add a short licence/inference-terms note for the TotalSynth weights and the pip package in the README.

### Module icon is a 700 KB PNG duplicated at the repository root
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`ImpactSynth/CMakeLists.txt:9`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/ImpactSynth/CMakeLists.txt#L9): ImpactSynth/Resources/Icons/ImpactSynth.png and the root ImpactSynth.png are both 723764 bytes; the icon is installed and loaded at module listing time, so a smaller PNG would reduce package size and module-browser memory slightly. This is cosmetic, not a defect.
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/Icons/${MODULE_NAME}.png
    )
  ```
  Suggestion: Downscale the icon to the usual 128x128/256x256 size.

### Patient images can be sent to a user-specified remote inference server
info; safety; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`README.md:75`](https://github.com/vboussot/SlicerImpactSynth/blob/188d1959ef0c6782fcebc9a533b0ccb9964410bf/README.md#L75): README.md line 76 and TUTORIAL.md line 64-66 describe a remote konfai-apps-server that performs inference. Input medical images would be transmitted to that host. This is a user-chosen, explicit setting, not hidden telemetry, but the docs should say that patient data leaves the workstation, and whether transfer is encrypted or authenticated is not visible here.
  ```
  - **Local GPU, CPU or remote server**
    The batch size is measured on the card (8 GB of VRAM is enough). A `konfai-apps-server` on a GPU workstation does the computation instead
  ```
  Suggestion: Add a clear warning that images are sent to the remote host, that the connection is unencrypted unless configured otherwise, and recommend only trusted servers.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): minor issues
The extension repository is a small, readable wrapper: one scripted module (~150 lines) that delegates all logic to the KonfAI extension's widgets and registers four TotalSynth apps by name plus three segmentation apps. Code is Apache-2.0 with a matching LICENSE, the catalog entry's build_dependencies match EXTENSION_DEPENDS ("KonfAI"), every Python file is installed by CMake, and there is no data upload, telemetry, download-and-exec or credential handling in this repository. Non-blocking issues: a top-level `from KonfAI import ...` (including a private helper) runs at Slicer startup and makes the whole module unloadable if KonfAI's private API changes; PyTorch is only mentioned in the README, not declared as a dependency; no real tests; heavy behaviour (installing konfai-apps, Hugging Face weight download, remote-server inference) lives in the KonfAI/SlicerKonfAI extensions which I could not inspect. 🟢 Recommend merge: no blocking safety, licence or catalog issues found in the inspected source.
Not checked: KonfAI and SlicerKonfAI extension source (https://github.com/vboussot/SlicerKonfAI, https://github.com/fideus-labs/KonfAI): the `konfai-apps` pip install on first use, torch usage/pinning, Hugging Face weight download logic, the optional `konfai-apps-server` remote inference (whether images are sent; Hugging Face model card and licence for VBoussot/ImpactSynth and the pip package impact_synth_konfai.; No build or CI result was available; the extension's configure/build on the supported platforms was not verified.; Which Python version the targeted 3D Slicer (>= 5.10) bundles, needed to judge the `QWidget | None` annotation risk.; The tutorial video Screenshots/SlicerImpactSynth-tutorial.mp4 (5 MB) was not readable, so its content was not reviewed; the README links were not checked for reachability.; Binary images (ImpactSynth.png, Screenshots/*.jpg) were not inspected for embedded metadata or steganographic content.
Questions for the author: Does the KonfAI extension ask the user before pip-installing `konfai-apps` into Slicer's Python, and does that install pin or downgrade any package Slicer bundles (numpy, scipy, SimpleITK, pydicom, requests)?; Does the KonfAI catalog entry declare the PyTorch extension as a dependency, so that installing ImpactSynth pulls PyTorch automatically?; What licence applies to the TotalSynth weights on huggingface.co/VBoussot/ImpactSynth and to `impact_synth_konfai`?; Which Slicer version and Python version does the extension officially support, given the `QWidget | None` annotation and the README's 'Slicer >= 5.10' requirement?; When the optional remote server (`konfai-apps-server`) is used, what exactly is transmitted and does the UI tell the user that the image leaves the machine?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
ImpactSynth is a well-structured, thoroughly documented 3D Slicer extension built on top of the KonfAI deep learning framework. It provides synthetic CT generation from MRI and CBCT scans, evaluation against reference CTs, uncertainty estimation, and segmentation. The code follows Slicer conventions cleanly, properly checks for API version compatibility with KonfAI, and carries an Apache 2.0 license. 🟢 Recommend merge
Not checked: Downloaded model weights and external execution of underlying KonfAI framework (handled by dependency extension KonfAI)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): incomplete
The repository itself is small: a CMake wrapper, a ~150-line ScriptedLoadableModule that builds two KonfAI app widgets, Apache-2.0 license, and docs. The real behaviour (installing konfai-apps into Slicer's Python, downloading Hugging Face weights, running subprocesses, optional remote-server transfer of images) lives in the KonfAI/SlicerKonfAI dependency, which was not in the review scope. The entry is mechanically plausible (build_dependencies matches EXTENSION_DEPENDS, license present). Safety and environment cannot be closed without reviewing the dependency's install and network code, so the review is incomplete.
Not checked: KonfAI and SlicerKonfAI source (the actual install logic, subprocess calls, Hugging Face download code, remote-server transport, and KONFAI_SLICER_API_VERSION definition) was not available in the review scope.; Scm source at commit 188d1959 was not fetched; only the files shown in the prompt were inspected, and no repo file listing beyond the module folder was checked for hidden files.; Hugging Face model licenses and terms for VBoussot/ImpactSynth, TotalSegmentator, MRSegmentator and ImpactSeg were not verified.; No CI build, Slicer load test, or runtime check was run; the .mp4 video and JPG/PNG screenshots were not viewed.; The ArXiv/paper claims (performance, challenge ranks) were not verified.


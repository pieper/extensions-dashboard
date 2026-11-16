# AI review: CADSWholeBodyCTSeg

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg at commit `d06eaf8b2c5b3800227d38266ffbc24f8024a5ed`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-16T02:29:15Z; cost $0.46

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | unknown |
| environment | unknown | blocking | blocking |
| packaging | unknown | ok | unknown |
| license | unknown | ok | minor |
| soundness | unknown | minor | concern |
| utility | unknown | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: Slicer module that runs the CADS nnU-Net models to segment 167 anatomical structures in whole-body CT. It installs the CADS Python package and its dependencies on first use, runs inference in a subprocess, and imports the results as segmentations with SNOMED terminology.
- **gemini**: CADSWholeBodyCTSeg provides automated segmentation of 167 anatomical structures across 9 task groups in head-to-knee CT volumes for researchers and clinicians using the nnU-Net-based CADS framework. It wraps the external CADS Python package with a 3D Slicer GUI and maps output segments to standard SNOMED-CT terminologies.
- **gpt**: CADSWholeBodyCTSeg segments anatomical structures in whole-body CT images using the CADS model. It provides Slicer users with task and target selection, terminology mapping, and segmentation output.

## Disagreements (start here)

### D1. Exact pin of `numpy==1.26.4` overwrites Slicer's bundled NumPy
partial; category environment; raised by gemini, gpt; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (blocking, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:995`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L995): `setupPythonRequirements` forcefully installs exact pinned versions `numpy==1.26.4` and `scikit-image==0.22.0` into Slicer's shared Python environment. `numpy` is bundled with 3D Slicer; replacing or downgrading Slicer's bundled `numpy` (especially in newer Slicer releases that use Python 3.12+ or NumPy 2.x, or while `numpy` C-extensions are already loaded in memory) can corrupt Slicer's Python environment and break Slicer core modules or other installed extensions.
  ```
          base_packages = [
              "numpy==1.26.4",
              "scikit-image==0.22.0",
          ]
          for package in base_packages:
              self.log(f'Installing {package}...')
  ```
  Suggestion: Do not install or pin `numpy` (rely on Slicer's bundled `numpy` and add `'numpy'` to `packagesToSkip`), and avoid hard-pinning `scikit-image==0.22.0` unless strictly necessary (or use a minimum version constraint like `scikit-image>=0.22.0` only if not already satisfied).
- **gpt** (blocking, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:993`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L993): The Apply handler invokes this setup before segmentation. On a Slicer installation with a different NumPy version, pip may replace the shared bundled package, breaking Slicer or other extensions, including in later sessions. The installation happens even before checking whether PyTorch is available.
  ```
          # Step 1) Install base dependencies first
          # To avoid repeated uninstall/install of packages, we specify exact versions of some packages
          base_packages = [
              "numpy==1.26.4",
              "scikit-image==0.22.0",
  ```
  Suggestion: Do not pin or replace Slicer-bundled NumPy; use compatible dependencies or isolate the inference environment from Slicer's Python.
- claude on re-check: **real: yes, blocking**: CADSWholeBodyCTSeg.py:995-1001 runs slicer.util.pip_install('numpy==1.26.4') and 'scikit-image==0.22.0' unconditionally in setupPythonRequirements, which Apply calls (line 387). There is no check of the installed version. numpy is bundled with Slicer. The pin therefore downgrades or replaces it on any Slicer build that ships a different version, for example NumPy 2.x. The policy explicitly lists exact pins of Slicer-bundled packages as a request-changes item. It runs on Apply, not at import. On a Slicer that already ships 1.26.4 it is a no-op.
- gpt on re-check: **real: yes, major**: CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:993-1001 contains `"numpy==1.26.4",` and `slicer.util.pip_install(package)`, before the PyTorch check at lines 1016-1024. Apply calls setup at lines 385-388. On an installation with another NumPy version, pip may replace the shared package; it need not replace an already matching installation. This is a serious shared-environment compatibility risk and the security policy requests a fix for exact pins of bundled packages, but actual breakage on a particular Slicer version was not demonstrated, so I rate the finding major rather than blocking.
- gemini on re-check: **real: yes, blocking**: In `CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:995-1001`, `setupPythonRequirements` explicitly runs `slicer.util.pip_install("numpy==1.26.4")` (and `scikit-image==0.22.0`) on every first run of the session. Under the review rubric and AGENTS.md policy ("Request changes for: ... Downgrading or exactly pinning packages that Slicer bundles (such as numpy, scipy, SimpleITK, pydicom, requests, vtk)"), replacing Slicer's bundled `numpy` with an exact pin can break Slicer's core environment and other extensions.

### D2. First Apply installs dependencies without asking for confirmation
single; category environment; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified, other lines) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:90`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L90): Clicking Apply immediately starts package installation and shared-environment changes, including the CADS archive and its dependencies when absent. There is no confirmation before this installation path; a status message after starting is not consent to downloads or changes.
  ```
          try:
              slicer.app.setOverrideCursor(qt.Qt.WaitCursor)
              self.logic.setupPythonRequirements()
              slicer.app.restoreOverrideCursor()
  ```
  Suggestion: Before modifying the environment, explain the packages and download size and obtain explicit confirmation; allow cancellation without changes.
- claude on re-check: **real: yes, major**: onApplyButton (lines 385-388) sets a wait cursor and calls setupPythonRequirements() directly. That function pip-installs numpy, scikit-image and acvl_utils (lines 995-1014). It also downloads CADS from GitHub and installs its dependencies and TPTBox (lines 1053-1087). The only confirmation prompt is for updating an already-installed CADS (lines 1046-1049). A first install gets no consent dialog. The install is user-triggered by Apply, not at import or startup, so I rate it major rather than blocking.
- gpt on re-check: **real: yes, major**: CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:362-388 calls `self.logic.setupPythonRequirements()` directly when Apply is clicked. Lines 993-1001 run `slicer.util.pip_install(package)`; lines 1051-1064 install CADS when absent without an initial-install confirmation. The confirmation at lines 1043-1049 is limited to updating an existing CADS package from a different URL, and the one at 399-403 concerns a restart after an error. Apply is described as `Start segmentation` at lines 217-221, not as consent to change shared packages. CADS installation is conditional on reaching it, including passing the earlier PyTorch check.
- gemini on re-check: **real: yes, minor**: In `CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:385-388`, `onApplyButton` directly calls `self.logic.setupPythonRequirements()` without prompting the user for confirmation before downloading and installing multiple Python packages into Slicer's environment (note that confirmation is only asked on lines 1046-1048 when upgrading an already-installed CADS package from a different URL, not on initial installation). While installing on `Apply` is much better than installing at module import/startup, installing large dependency trees without user confirmation is a minor/moderate issue.

### D3. Selective dependency installer does not prevent transitive overwrites of Slicer-bundled packages or `numpy`/`scipy`
single; category environment; raised by gemini; outcome after cross-examination: **real, major (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:871`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L871): `pipInstallSelectiveFromURL` strips `packagesToSkip` (`SimpleITK`, `torch`, `requests`, `nnunetv2`, etc.) from CADS's top-level `METADATA`, but then installs each remaining requirement (and `TPTBox==...` at line 1087) via normal `slicer.util.pip_install(...)` without `--no-deps` and without excluding `numpy`, `scipy`, `vtk`, or `SimpleITK`. Transitive dependencies (such as `TPTBox` or `monai`/`nibabel`/`scipy`) can still pull or downgrade `torch`, `SimpleITK`, `numpy`, or `scipy` from PyPI into Slicer's shared environment.
  ```
                  # Install remaining dependencies
                  requirements = importlib.metadata.requires(packageToInstall) or []
                  for requirement in requirements:
                      # Skip dev dependencies
                      if '; extra == "dev"' in requirement:
                          continue
  ```
  Suggestion: Include `'numpy'` and `'scipy'` in `packagesToSkip` and pass constraints or check installed packages before calling `pip_install` so transitive dependencies of `CADS` and `TPTBox` cannot overwrite Slicer's bundled packages (`SimpleITK`, `numpy`, `scipy`, `requests`) or PyTorch.
- claude on re-check: **real: yes, major**: pipInstallSelectiveFromURL (lines 871-892) skips only the names in packagesToSkip. It calls slicer.util.pip_install(requirement) on each remaining requirement, with no --no-deps and no exclusion of numpy, scipy or vtk. Line 1087 installs TPTBox==version the same way. TPTBox's own dependencies are not filtered, so a transitive pull or downgrade of bundled packages is possible. I did not verify what TPTBox actually requires. The skip list does cover torch, SimpleITK, requests and nnunetv2 at the top level only.
- gpt on re-check: **real: yes, major**: The lack of transitive protection is real: CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:871-892 filters direct requirements with `skipThisPackage = any(requirement.startswith(pkg) for pkg in packagesToSkip)` but then calls `slicer.util.pip_install(requirement)` without `--no-deps`. Lines 1028-1035 list packages skipped only at that level; lines 1085-1087 independently run `slicer.util.pip_install(f"TPTBox=={required_version}")` with dependency resolution enabled. Thus transitive requirements are not constrained by the skip list and can change shared packages. The actual external CADS/TPTBox dependency metadata and a particular resulting downgrade were not available to verify, so the named downstream replacements remain conditional risks, not demonstrated outcomes.
- gemini on re-check: **real: yes, major**: In `CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:872-892` and `1086-1087`, `pipInstallSelectiveFromURL` filters `packagesToSkip` (`SimpleITK`, `torch`, `requests`, `acvl-utils`, `nnunetv2`, `TPTBox`) from CADS's top-level metadata, then installs each remaining requirement (and later `TPTBox=={required_version}`) via `slicer.util.pip_install(...)` with full dependency resolution. Because `packagesToSkip` neither blocks `numpy`/`scipy`/`vtk` at the top level nor constrains transitive dependencies (for example `TPTBox` and other packages depend on `SimpleITK`, `torch`, `numpy`, `scipy`, etc., or pinned versions in CADS's `METADATA`), `pip` can still overwrite or downgrade Slicer-bundled packages or pull `torch`/`SimpleITK` if version specifiers conflict.


## Findings from some reviewers

### All-target mode stays disabled after first-use installation
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:319`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L319): On a fresh installation, opening the module before CADS is installed disables the all-targets radio button. The successful updateTargetsList path never re-enables it, and Apply does not refresh the list after installing CADS, so users cannot select that mode in the current widget session.
  ```
          except ImportError:
              self.ui.allTargetsRadio.setEnabled(False)
              self.ui.targetsList.setEnabled(True)
              # CADSWholeBodyCTSeg package not installed (when open this extension for the very 1st time)
              self.ui.targetsList.addItem("CADSWholeBodyCTSeg package needs to be installed first.")
              self.ui.targetsList.addItem("You can either:")
  ```
  Suggestion: Refresh the list after successful setup and explicitly re-enable allTargetsRadio when the package becomes available.

### Inference output blocks the GUI thread while awaiting lines
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:1139`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L1139): Apply calls this synchronous reader after launching CADS. While inference emits no output, readline blocks the UI event loop, potentially making Slicer unresponsive for the lengthy inference interval.
  ```
          while True:
              try:
                  line = proc.stdout.readline()
                  if not line:
                      break
                  if returnOutput:
  ```
  Suggestion: Use asynchronous process notifications or a worker thread and provide responsive progress and cancellation.

### Segmentation test does not verify segmentation output
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:1623`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L1623): The test substitutes echo for inference and does not assert the returned result or any segments. A run returning an empty list because no output file exists can be reported as passing, so it does not detect a broken inference/import pipeline.
  ```
                  task="551",
                  subset=None,
                  cpu=True,
                  cadsCommand=["echo", "test"]
              )
              
  ```
  Suggestion: Add a deterministic test with representative generated labelmaps and assertions, and an integration test for real inference where practical.

### Self-test `CADSWholeBodyCTSegTest` has mismatched expectations and will fail
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:1539`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L1539): In `setDefaultParameters` (line 1131), `TargetMode` is initialized to `"all"`, whereas `test_Logic` asserts that the default value of `TargetMode` is `"subset"` (and the `.ui` file has `subsetTargetsRadio` checked by default). In addition, `test_ErrorHandling` (lines 1712-1729) expects `logic.process` to raise a `ValueError` for an invalid subset, which `logic.process` does not implement. As a result, the self-test fails.
  ```
              # test input arg setting
              defaultParameters = {
                  "CPU": "false",
                  "UseStandardSegmentNames": "true",
                  "Task": "551",  # by default
                  "TargetMode": "subset"
  ```
  Suggestion: Align the default `TargetMode` between `setDefaultParameters`, `CADSWholeBodyCTSeg.ui`, and `CADSWholeBodyCTSegTest`, and update `test_ErrorHandling` to match the actual behavior of `logic.process`.

### `UnboundLocalError` on `segmentationNodes` when `logic.process()` fails
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:411`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L411): In `onApplyButton`, `self.ui.statusLabel.appendPlainText(f"\nProcessing finished. Created {len(segmentationNodes)} segmentation nodes.")` is outside the `with slicer.util.tryWithErrorDisplay(...)` block. Because `tryWithErrorDisplay` catches exceptions and suppresses them after showing an error dialog, if `self.logic.process(...)` raises an exception, `segmentationNodes` is unbound and line 432 raises an unhandled `UnboundLocalError`.
  ```
          with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):
              # Create initial segmentation node if needed
              if not self.ui.outputSegmentationSelector.currentNode():
                  self.ui.outputSegmentationSelector.addNode()
  
              self.logic.useStandardSegmentNames = self.ui.useStandardSegmentNamesCheckBox.checked
  ```
  Suggestion: Indent the `self.ui.statusLabel.appendPlainText(...)` call so it is inside the `with slicer.util.tryWithErrorDisplay(...):` block.

### Downloaded model weights are under non-commercial license (CC BY-NC-SA 4.0)
info; license; raised by gemini, gpt
- **gemini** (info, high confidence, quote verified) [`LICENSE_MODEL:3`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/LICENSE_MODEL#L3): The extension code is licensed under Apache 2.0 (`LICENSE`), which permits distribution. However, the pretrained model weights downloaded at runtime are licensed under CC BY-NC-SA 4.0 (`LICENSE_MODEL` and `README.md`), restricting model usage to non-commercial/research purposes. Users in clinical or commercial settings should be aware of this restriction.
  ```
  The model weights released in the Releases section of this repository are licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0).
  ```
  Suggestion: Consider noting the CC BY-NC-SA 4.0 non-commercial model license in the module's `helpText` or `acknowledgementText` inside Slicer so users see it without having to visit the GitHub repository.
- **gpt** (info, high confidence, quote verified) [`LICENSE_MODEL:3`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/LICENSE_MODEL#L3): The stated license permits redistribution under conditions but limits commercial use; the README also calls the weights research-only while describing clinical workflows. Users should be made aware of these restrictions before downloading or using the model.
  ```
  The model weights released in the Releases section of this repository are licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0).
  
  This licensing reflects the inclusion of training data with non-commercial restrictions.
  ```
  Suggestion: Surface the model terms and intended-use limitations in the module before model download or inference.

### Large screenshot PNG files (~3.7 MB total) committed to repository root
info; packaging; raised by gemini; **quote not found in source**
- **gemini** (info, medium confidence, quote quote not found) [`CMakeLists.txt:12`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CMakeLists.txt#L12): Two large PNG screenshots (~1.85 MB and ~1.83 MB, ~3.7 MB total) are committed directly to the root of the source repository. While not installed by CMake, storing multi-megabyte screenshots in the main git history bloats repository clones.
  ```
  Screenshot_01.png  (1847577 bytes, binary)
  Screenshot_02.png  (1828461 bytes, binary)
  ```
  Suggestion: Consider compressing the screenshots or hosting them in a separate documentation branch/release asset.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I read the full module source, both CMakeLists files, the licenses and the README. I found no malicious behaviour, telemetry or credential access. The CMake files, the catalog entry and the CADS source download (a commit-pinned GitHub zip) all look consistent. The main concern is the environment. On Apply, the module pip-installs exact pins (numpy==1.26.4, scikit-image==0.22.0) into Slicer's shared Python, with no confirmation and no downgrade check. It also installs the CADS requirements, which I could not see, with no hash verification. The model weights are CC BY-NC-SA, non-commercial only, and the UI does not tell users that. The tests would fail in CI.
Not checked: 
<parameter name="x">CADS package source at commit 457638bac28e8618a66e9d4c56d5ade824acc87c (setup.py, requirements, entry points, model weight download code and its integrity checks)

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
`CADSWholeBodyCTSeg` is a well-structured 3D Slicer wrapper for the CADS whole-body CT segmentation model (167 structures across 9 tasks) with SNOMED-CT terminology support, Apache-2.0 code licensing (CC BY-NC-SA 4.0 for model weights), and matching `PyTorch`/`NNUNet` extension dependencies. However, `setupPythonRequirements()` in `CADSWholeBodyCTSeg.py` explicitly runs `slicer.util.pip_install("numpy==1.26.4")`, which pins and replaces Slicer's bundled `numpy` in the shared Python environment and can break Slicer and other extensions. Additionally, `numpy` and `scipy` are not in `packagesToSkip` when installing `CADS` and `TPTBox` dependencies.

🔴 Do not merge yet: `setupPythonRequirements` pins `numpy==1.26.4`, overwriting Slicer's bundled `numpy`.
Not checked: Contents of the external Python package archive downloaded at runtime: https://github.com/murong-xu/CADS/archive/457638bac28e8618a66e9d4c56d5ade824acc87c.zip (including its setup.py, dependencies, and model weight download URLs)
Questions for the author: Can `numpy==1.26.4` be removed from `base_packages` (and `numpy` added to `packagesToSkip`) so that Slicer's bundled NumPy is never overwritten?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The wrapper, build files, UI, documentation, and supplied licenses were inspected. Applying the module can replace Slicer's bundled NumPy with an exact older version and install dependencies without prior confirmation. The external CADS implementation and model download path were not available for safety review, and the catalog branch and supplied commit could not be independently resolved. 🔴 Do not merge yet: fix the shared-environment changes and complete the external payload and revision review.
Not checked: No network or execution tools were available to resolve main or independently verify the supplied commit d06eaf8b2c5b3800227d38266ffbc24f8024a5ed, repository accessibility, catalog schema validity, CI, or an actual Slicer build and run.; The externally downloaded CADS archive at 457638bac28e8618a66e9d4c56d5ade824acc87c, its transitive package requirements, inference code, network behavior, model acquisition and actual model license were not accessible for inspection.; Previous catalog entry, submission checklist and prior reviewed source baseline were not provided.
Questions for the author: Can you provide the pinned CADS source and exact model download code and license for independent safety and distribution review?


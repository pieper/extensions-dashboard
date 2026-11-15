# AI review: CADSWholeBodyCTSeg

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg at commit `d06eaf8b2c5b3800227d38266ffbc24f8024a5ed`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T17:29:21Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | concern |
| environment | blocking | ok | concern |
| packaging | ok | ok | ok |
| license | minor | ok | concern |
| soundness | concern | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer module that runs the CADS nnU-Net model to fully automatically segment 167 anatomical structures in whole-body CT, for researchers and clinicians doing CT anatomy segmentation. It installs the CADS Python package and model weights on demand and imports results as Slicer segmentation nodes with SNOMED terminology.
- **flash-lite**: CADSWholeBodyCTSeg is a 3D Slicer extension providing automated whole-body anatomical segmentation of 167 structures in CT scans, powered by the CADS framework and PyTorch/nnUNet.
- **haiku**: A 3D Slicer scripted module that runs the CADS whole-body CT segmentation model (167 anatomical structures) on a selected volume through the CADS Python package, which it installs into Slicer's Python environment. It is for Slicer users doing segmentation research, and it depends on the PyTorch and NNUNet extensions.

## Disagreements (start here)

### D1. Exact numpy pin installed into Slicer's shared Python environment
partial; category environment; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:995`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L995): numpy is bundled with Slicer. Installing an exact pin on the first Apply silently replaces the numpy that Slicer and every other installed extension use, for the rest of that Slicer installation. If the Slicer version ships a different numpy (e.g. numpy 2.x in newer previews), other extensions that were built against it can break even though the user never intended to change them. The index policy lists exact pinning/downgrading of bundled packages such as numpy as a request-changes item.
  ```
          base_packages = [
              "numpy==1.26.4",
              "scikit-image==0.22.0",
          ]
          for package in base_packages:
              self.log(f'Installing {package}...')
  ```
  Suggestion: Do not pin numpy; only install it if missing, or use a minimum-version requirement, and let the CADS package resolve against Slicer's numpy. Same for scikit-image if it is not strictly required at a fixed version.
- **haiku** (major, medium confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:995`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L995): setupPythonRequirements installs numpy==1.26.4 and scikit-image==0.22.0 unconditionally each time the user clicks Apply (until the class-level flag is set). If the Slicer build bundles a different numpy, this downgrades a package Slicer and other extensions depend on, affecting users who never open this module. The cached _requirements_checked flag only limits repeats within a session.
  ```
  base_packages = [
              "numpy==1.26.4",
              "scikit-image==0.22.0",
          ]
  ```
  Suggestion: Do not pin packages Slicer bundles; only install a version when the installed one is incompatible, and check the installed version first. Document the dependency on a specific numpy if it is truly required.

### D2. Downgrades dynamic_network_architectures shared with the NNUNet extension
single; category environment; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:1110`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L1110): dynamic_network_architectures is a dependency of nnunetv2, which the NNUNet extension installs and other nnU-Net based extensions rely on. Forcing 0.2.0 whenever the installed version is 0.4 (or anything else that raises PackageNotFoundError) can break the NNUNet extension and other nnU-Net modules for the same user, in the same shared environment.
  ```
              if version.parse(installed_version) == version.parse("0.4"):
                  raise importlib.metadata.PackageNotFoundError
          except importlib.metadata.PackageNotFoundError:
              self.log(f'dynamic_network_architectures package version is incompatible or not installed. Installing working version...')
              slicer.util.pip_install("dynamic_network_architectures==0.2.0")
  ```
  Suggestion: Report the incompatibility to the user and let them resolve it via the NNUNet extension, or coordinate the required version with the NNUNet extension instead of silently downgrading.

### D3. Installer edits the METADATA of installed packages and installs dependencies by hand, bypassing pip resolution
single; category environment; raised by haiku
- **haiku** (major, medium confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:846`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L846): pipInstallSelectiveFromURL installs CADS with --no-deps, rewrites its METADATA file in place to remove requirements, and then installs the remaining requirements one by one. Pip's dependency resolver is bypassed, so conflicts are not checked and the installed metadata no longer matches the real requirements. This can leave the environment inconsistent for other extensions.
  ```
  with open(metadataPath.locate(), "r+", encoding="latin1") as file:
                      for line in file:
                          skipThisPackage = False
                          requirementPrefix = 'Requires-Dist: '
  ```
  Suggestion: Install with pip's normal resolver, using constraints that exclude the packages Slicer provides, instead of editing installed metadata. If editing is unavoidable, document it and verify with pip check.

### D4. Multiple packages are pip-installed into the shared environment, including exact pins, without a confirmation for the initial install
single; category environment; raised by haiku
- **haiku** (major, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:1054`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L1054): On the first Apply, the module downloads and installs the CADS package from a GitHub zip and its dependencies, with several-minute installs, with no user confirmation. It also installs exact versions of acvl_utils, TPTBox and dynamic_network_architectures. These changes persist in the shared Slicer environment and can conflict with other extensions. Only the update path asks the user (line 1046).
  ```
  self.log(f'CADS Python package is required. Installing it from {self.cadsPythonPackageDownloadUrl}... (it may take several minutes)')
  
              if upgrade:
                  # CADS version information is usually not updated with each git revision, therefore we must uninstall it to force the upgrade
                  slicer.util.pip_uninstall("CADS")
  ```
  Suggestion: Ask for explicit user confirmation before the large first-time install and before exact-version installs, and mention the packages to be installed in the UI. Avoid installing into the shared environment without consent.

### D5. UnboundLocalError after a failed processing run
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified, other lines) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:359`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L359): segmentationNodes is assigned only inside the 'with slicer.util.tryWithErrorDisplay(...)' block. tryWithErrorDisplay catches the exception and returns, so execution continues to line 431 where segmentationNodes is undefined, raising UnboundLocalError. The user sees the real error plus a second, confusing traceback instead of a clean failure message.
  ```
          self.ui.statusLabel.appendPlainText(
              f"\nProcessing finished. Created {len(segmentationNodes)} segmentation nodes."
          )
  ```
  Suggestion: Initialize segmentationNodes = [] before the with-block, or return from onApplyButton inside the error path.

### D6. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D7. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku concern

### D8. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D9. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### Bundled tests assert behavior the code does not implement
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:1722`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L1722): No code path raises these messages (grep finds them only in the test), and test_Logic expects TargetMode default 'subset' while setDefaultParameters sets 'all' (lines 1130-1131, 1544). test_SegmentationProcessing passes cadsCommand=["echo","test"] and asserts nothing, so it passes trivially. The test suite therefore does not validate the pipeline and will likely fail in CI.
  ```
                  expected_messages = [
                      "Invalid organs in subset",
                      "Cannot validate subset for task"
                  ]
  ```
  Suggestion: Align the tests with the actual implementation and add at least one assertion on produced segments (or mark heavy tests as manual).

### Downloaded zip is extracted without member validation and then pip-installed
minor; safety; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:772`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L772): The module downloads a zip from GitHub and runs pip install on the extracted setup.py, i.e. it executes third-party code. The URL is pinned to a commit hash in the author's own repository (line 503), which limits the risk, but zip_ref.extractall(temp_dir) (line 784) does not validate member paths, so a tampered archive could write outside the temp folder. No hash/signature check is performed on the download.
  ```
                  if installURL.startswith(('http://', 'https://')):
                      self.log(f'Downloading package from {installURL}...')
                      urllib.request.urlretrieve(installURL, zip_path)
                      source_url = installURL
  ```
  Suggestion: Validate archive members before extraction (reject absolute paths and '..'), and optionally verify a pinned SHA-256 of the downloaded zip.

### Exact pin of acvl_utils==0.2 in shared environment
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:1013`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L1013): acvl_utils is also used by nnunetv2; pinning it to 0.2 for all users of the shared Slicer Python can conflict with the version the NNUNet extension expects. The comment acknowledges this is a temporary upstream workaround.
  ```
          if needToInstallAcvlUtils:
              slicer.util.pip_install("acvl_utils==0.2")
  ```
  Suggestion: Prefer a version range, or document/coordinate the pin with the NNUNet extension and remove it once upstream is fixed.

### Installed package METADATA is rewritten in place to strip requirements
minor; safety; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:867`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L867): The extension edits the dist-info METADATA of the just-installed CADS package to remove Requires-Dist lines, and writes a custom direct_url.json. This leaves the environment with metadata that no longer matches the package, which can confuse pip (dependency resolution, 'pip check', later upgrades) and other tools. It is not malicious, but it is a fragile modification of the shared Python environment.
  ```
                      file.seek(0)
                      file.write(filteredMetadata)
                      file.truncate()
  ```
  Suggestion: Install with --no-deps and install the needed dependencies explicitly instead of mutating installed metadata.

### Long-running install and inference block the GUI thread without progress
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:386`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L386): pip installs (potentially several GB with model weights) and the CADS subprocess (logProcessOutput loops until the process ends, line 1139-1153) run on the GUI thread; the only relief is slicer.app.processEvents() inside addLog. Slicer appears frozen for many minutes with no progress bar or cancel option, and the ~727 MB per-task weight download happens without an explicit size confirmation.
  ```
              slicer.app.setOverrideCursor(qt.Qt.WaitCursor)
              self.logic.setupPythonRequirements()
              slicer.app.restoreOverrideCursor()
  ```
  Suggestion: Run installation and inference in a CLI node / worker thread with progress reporting and a cancel button, and confirm the download size with the user before fetching weights.

### Long-running segmentation blocks the GUI thread while reading process output
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:1139`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L1139): logProcessOutput reads the child process stdout in a blocking loop on the GUI thread. The UI only gets processEvents in addLog. The app may appear frozen for minutes during CPU inference, and cancellation is not possible.
  ```
  while True:
                  try:
                      line = proc.stdout.readline()
                      if not line:
                          break
  ```
  Suggestion: Run the process asynchronously (QProcess or a thread), or pump events regularly, and offer cancellation.

### No clinical-use disclaimer
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`README.md:8`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/README.md#L8): The README advertises clinical workflows but nowhere states that the segmentation is a research tool and must not be used for diagnosis or treatment decisions without validation. For an AI segmentation tool this disclaimer matters to users.
  ```
  👉 This repository focuses only on the plugin for [CADS-model](https://github.com/murong-xu/CADS), providing an easy-to-use interface for clinical and research workflows.
  ```
  Suggestion: Add an explicit 'not for clinical use / research only' statement to the README and module help text.
- **haiku** (minor, medium confidence, quote verified) [`README.md:8`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/README.md#L8): The README describes the tool for 'clinical and research workflows', but there is no statement that output is not validated for diagnostic or treatment use. Users could rely on automated organ segmentations without review.
  ```
  👉 This repository focuses only on the plugin for [CADS-model](https://github.com/murong-xu/CADS), providing an easy-to-use interface for clinical and research workflows.
  ```
  Suggestion: Add a research-use-only disclaimer and a note that results need human review, both in the README and in the module help text.

### Non-commercial model license disclosed only in README, with a broken link
minor; license; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`README.md:111`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/README.md#L111): The weights the extension downloads are CC BY-NC-SA 4.0 (LICENSE_MODEL:3), i.e. non-commercial and share-alike. That permits distribution, but users must know they may not use the output commercially; the README link points to MODEL_LICENSE while the file is named LICENSE_MODEL, and the in-module acknowledgementText (CADSWholeBodyCTSeg.py:24-30) does not mention the restriction at all.
  ```
  - **Model weights** released in the [Releases](https://github.com/murong-xu/CADS/releases) section are licensed under [CC BY-NC-SA 4.0](MODEL_LICENSE) for research-only purposes.
  ```
  Suggestion: Fix the link to LICENSE_MODEL and state the non-commercial/research-only restriction in the module acknowledgementText and help text.
- **haiku** (minor, high confidence, quote verified) [`README.md:111`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/README.md#L111): The README links the model license to 'MODEL_LICENSE', which is not in the repository; the file is LICENSE_MODEL. The model weights are CC BY-NC-SA 4.0 (non-commercial, research), and the extension downloads them at runtime. Users may not notice the restriction from inside Slicer.
  ```
  - **Model weights** released in the [Releases](https://github.com/murong-xu/CADS/releases) section are licensed under [CC BY-NC-SA 4.0](MODEL_LICENSE) for research-only purposes.
  ```
  Suggestion: Fix the link to LICENSE_MODEL and state the non-commercial restriction in the module helpText or the Slicer documentation.

### Pattern-based result lookup can pick the wrong file
minor; soundness; raised by haiku
- **haiku** (minor, low confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:1419`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L1419): readSegmentation locates results with glob('*{task}*.nii.gz') and uses the first match. Task IDs such as '551' can match unrelated filenames in the output folder, and the code logs a warning but continues with an arbitrary file. The range check at line 1412 can never trigger for label values, since it tests the minimum key.
  ```
  pattern = os.path.join(outputSegmentationFolder, f'*{task}*.nii.gz')
          matching_files = glob.glob(pattern)
  ```
  Suggestion: Use the exact expected output filename from CADS, and fail instead of silently choosing one of several matches.

### Target list construction can KeyError on structures missing from the CSV mapping
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:289`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L289): Structure names come from the CADS package's label maps, while cadsLabelTerminology is built from the bundled CSV. If the installed CADS version adds or renames a structure, the lookup raises KeyError, which is caught by the generic handler at line 329 and silently disables the target list, leaving the user unable to select targets.
  ```
                  availableTargets_snomed = [
                      self.logic.getSegmentLabelColor(self.logic.cadsLabelTerminology[i]['terminologyStr'])[0] 
                      for i in all_targets
                  ]
  ```
  Suggestion: Use .get() with a fallback to the raw structure name and log which structures lack terminology.

### Terminology file loaded into global terminology logic at Slicer startup
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:31`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L31): Every Slicer start with the extension installed loads the CADS terminology into the shared terminology logic, even for users who never open the module. This is a global side effect (extra startup work and an extra terminology context visible in other modules' terminology selectors).
  ```
          slicer.app.connect("startupCompleted()",
                             self.configureDefaultTerminology)
  ```
  Suggestion: Load the terminology lazily on first module entry (enter()) or when the logic is first used.

### Unit tests that exercise processing are disabled and rely on network sample data
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`CADSWholeBodyCTSeg/Testing/Python/CMakeLists.txt:2`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/Testing/Python/CMakeLists.txt#L2): The only real test registration is commented out in Testing/Python/CMakeLists.txt. The unittest class depends on SampleData.downloadSample('CTChest') and on the CADS model, so CI does not verify the processing path.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Enable a lightweight test that does not download large data, and mock the CADS call for CI.

### Large screenshots committed to the repository
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`CMakeLists.txt:12`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CMakeLists.txt#L12): Screenshot_01.png and Screenshot_02.png are ~1.8 MB each and are committed rather than fetched on demand; this is not a functional problem but bloats the extension package.
  ```
  set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/murong-xu/SlicerCADSWholeBodyCTSeg/main/Screenshot_01.png")
  ```
  Suggestion: Downscale the screenshots or host them outside the packaged source.

### Module declares no dependencies although it requires PyTorch and NNUNet
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py:18`](https://github.com/murong-xu/SlicerCADSWholeBodyCTSeg/blob/d06eaf8b2c5b3800227d38266ffbc24f8024a5ed/CADSWholeBodyCTSeg/CADSWholeBodyCTSeg.py#L18): The extension-level EXTENSION_DEPENDS is correct, but the module itself reports no dependencies, so Slicer's module dependency checks cannot warn the user when PyTorch/NNUNet are missing.
  ```
          self.parent.dependencies = []
  ```
  Suggestion: Set self.parent.dependencies = ["PyTorch", "NNUNet"].


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Well-documented, Apache-2.0 extension with a clean CMake layout and no telemetry or data exfiltration. However it installs an exact numpy pin (numpy==1.26.4) and downgrades dynamic_network_architectures/acvl_utils in Slicer's shared Python, which the index policy explicitly asks to change, and it rewrites installed package metadata. There are also real code bugs (UnboundLocalError after a failed run, tests asserting messages that do not exist) and the model weights are CC BY-NC-SA (non-commercial), which is disclosed only in the README. Needs fixes before merge.
Not checked: The upstream CADS package downloaded at runtime (https://github.com/murong-xu/CADS/archive/457638bac28e8618a66e9d4c56d5ade824acc87c.zip) was not inspected; its setup.py, dependencies and model-weight download logic are outside this repository.; The model weights themselves (CC BY-NC-SA 4.0, ~727 MB per task) and the CADS-dataset on HuggingFace were not inspected.; Whether numpy==1.26.4 conflicts with the numpy bundled in the targeted Slicer versions (5.10.0 / 5.11.0) could not be verified without a Slicer installation.; The full content of Resources/SegmentationCategoryTypeModifier-CADS.term.json (107 KB) and cads_snomed_mapping.csv (168 lines) was only spot-checked, not fully reviewed.; No CI/build results were available, so a successful build on all platforms is unverified; the catalog entry uses scm_revision "main" and I reviewed the snapshot at d06eaf8b2c5b3800227d38266ffbc24f8024a5ed.; The extension was not executed, so runtime behavior of the pip-install and inference paths is inferred from code reading only.
Questions for the author: Can the numpy==1.26.4 and scikit-image==0.22.0 exact pins be relaxed so Slicer's bundled numpy is not replaced?; Can the dynamic_network_architectures==0.2.0 downgrade be avoided or coordinated with the NNUNet extension, since it is shared with nnunetv2?; Can the ~727 MB per-task model weight download be confirmed with the user (size and license) before it starts?; Would you add the CC BY-NC-SA 4.0 non-commercial restriction and a not-for-clinical-use statement to the module help/acknowledgement text?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The CADSWholeBodyCTSeg extension is well-structured, follows Slicer scripted module conventions, properly declares PyTorch and NNUNet build dependencies, handles Python dependencies safely without breaking Slicer bundled libraries or PyTorch installations, and includes thorough testing and documentation. 🟢 Recommend merge
Not checked: External CADS python package repository source code at GitHub archive URL (though code uses standard packaging and pip install selective approach).

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
No malicious or data-exfiltration behavior seen in the module; patient data stays in a temp folder and the CADS package is pinned to a commit hash. The main concerns are environmental: on every Apply the module pins numpy and scikit-image and installs CADS and its dependencies into the shared Slicer Python environment, with rewriting of installed package metadata and no confirmation for the initial large install. Licensing is clear for the code (Apache-2.0) but the model weights are non-commercial. I could not inspect the CADS package, the UI file, or the model weights, and I did not run anything.
Not checked: The CADS Python package (github.com/murong-xu/CADS at the pinned commit) was not inspected: its entry point CADSSlicer, its model download logic, and any network access during inference.; Model weights downloaded from the CADS GitHub release were not inspected for integrity or format (no pickle check).; The UI file Resources/UI/CADSWholeBodyCTSeg.ui and icon were not read; only their presence in the file list was confirmed.; The scm_revision is 'main' rather than a fixed commit, so the exact reviewed revision is unknown; I reviewed the content shown in the catalog listing only.; No CI results, Slicer build, or runtime behavior were available; I did not run anything.; Whether numpy 1.26.4 or scikit-image 0.22.0 conflicts with the Slicer version bundled packages was not verified.


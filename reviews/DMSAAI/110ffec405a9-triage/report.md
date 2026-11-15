# AI review: DMSAAI

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/4burakfe/SlicerDMSAAI.git at commit `110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:21:33Z; cost $0.05

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | minor |
| environment | minor | ok | ok |
| packaging | ok | ok | ok |
| license | minor | ok | concern |
| soundness | minor | ok | minor |
| utility | minor | ok | ok |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: DMSAAI is a 3D Slicer extension (plus a hidden DICOM plugin) that segments kidneys on planar Tc-99m DMSA nuclear-medicine images with MONAI/PyTorch networks, computes split renal function and shows AI-based kidney evaluation, for nuclear-medicine physicians and researchers.
- **flash-lite**: DMSAAI is a 3D Slicer extension for AI-powered renal cortical scintigraphy analysis (Tc-99m DMSA studies), providing automated kidney segmentation, split renal function quantification, and AI-assisted classification from planar nuclear medicine DICOM images.
- **haiku**: DMSAAI is a Slicer scripted extension for research analysis of planar Tc-99m DMSA renal scintigraphy: it loads planar NM DICOM views, segments kidneys with SwinUNETR/SegResNet/DynUNet networks, computes split renal function, and runs DenseNet-based cortical evaluation. It is intended for nuclear medicine researchers and clinicians working with Slicer, with PyTorch supplied by the PyTorch extension.

## Disagreements (start here)

### D1. Downloaded weights are loaded with an unguarded torch.load fallback (possible pickle code execution)
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`DMSAAI/DMSAAILib/networks.py:96`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAILib/networks.py#L96): The common path is safe, but if unpickling with weights_only=True raises TypeError (torch older than 1.13, and any TypeError raised inside the unpickler), the same file is re-loaded as a full pickle through the second call. The files come from a network download (see next finding), so a modified .pth could run arbitrary Python in the Slicer process on such setups.
  ```
      try:
          state = torch.load(path, map_location=device, weights_only=True)
      except TypeError:  # torch < 1.13
          state = torch.load(path, map_location=device)
  ```
  Suggestion: Remove the fallback and report a clear error asking the user to install PyTorch through the PyTorch extension, or at minimum only fall back after verifying the file against a pinned SHA-256.
- **haiku** (minor, medium confidence, quote verified) [`DMSAAI/DMSAAILib/networks.py:96`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAILib/networks.py#L96): _load wraps torch.load(weights_only=True) in a bare except TypeError and then calls torch.load without weights_only, which unpickles arbitrary objects. The intent is only for torch<1.13, but any TypeError raised inside the safe path would silently fall back to the unsafe load.
  ```
  try:
          state = torch.load(path, map_location=device, weights_only=True)
      except TypeError:  # torch < 1.13
          state = torch.load(path, map_location=device)
  ```
  Suggestion: Check torch.__version__ (or inspect the signature) before choosing the call, and do not fall back to the unrestricted pickle load for any other exception.

### D2. License of the downloaded model weights is not stated
single; category license; raised by haiku
- **haiku** (major, medium confidence, quote verified) [`LICENSE.txt:1`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/LICENSE.txt#L1): The extension's MIT license covers only the wrapper code. The ~140 MB weights are fetched from a different repository (4burakfe/DMSAAI) and the files reviewed do not state their terms. Users and redistributors cannot tell whether the weights may be used or redistributed, including for commercial use.
  ```
  MIT License
  
  Copyright (c) 2026 Burak Demir
  ```
  Suggestion: Confirm and state the license of the weights (in the DMSAAI repo or README), and note any non-commercial terms, since the extension downloads them on demand.

### D3. Model weights downloaded from a moving branch without integrity check
single; category safety; raised by deepseek
- **deepseek** (major, high confidence, quote verified, other lines) [`DMSAAI/DMSAAILib/networks.py:11`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAILib/networks.py#L11): download_weights() fetches each .pth from `raw.githubusercontent.com/4burakfe/DMSAAI/main/` (line 11, urlretrieve at line 192) with no expected hash and no pinned commit/tag. Whatever the `main` branch contains at download time is deserialized by torch (see previous finding), so content changes upstream silently propagate to users' machines; it also makes results non-reproducible between users.
  ```
  WEIGHTS_BASE_URL = "https://raw.githubusercontent.com/4burakfe/DMSAAI/main/"
  ```
  Suggestion: Pin the download URLs to a specific commit (or release asset) and verify a published SHA-256 per file before use; state the hash list in the README so the provenance is auditable.

### D4. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor

### D5. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings from some reviewers

### DICOM plugin switches module and replaces the layout without asking
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`DMSAAI/DICOMDmsaaiPlugin.py:144`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DICOMDmsaaiPlugin.py#L144): Loading any DMSA series in the DICOM module silently takes the user out of the DICOM module, and DMSAAILogic.showLayout() then replaces the current layout with the fixed 2x3 layout (DMSAAI.py:1052-1062). The opt-out key `DMSAAI/SwitchToModuleAfterDICOMLoad` is documented in the README but has no UI in the module, so a user must edit QSettings by hand.
  ```
      if not nodes or slicer.app.testingEnabled():
          return
      if str(qt.QSettings().value(SETTINGS_SWITCH_MODULE, "true")).lower() not in ("true", "1"):
          return
      if not hasattr(slicer.modules, "dmsaai"):
          return
  ```
  Suggestion: Default the switch to off or expose a checkbox in the module's Advanced section; if the switch is kept, do not force the layout change on module entry.

### Downloaded model weights are not integrity-checked
minor; safety; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`DMSAAI/DMSAAILib/networks.py:192`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAILib/networks.py#L192): download_weights fetches each .pth file from raw.githubusercontent.com with urllib.request.urlretrieve and no checksum or signature check, then loads it with torch.load. A compromised upstream repo or a network MITM would deliver arbitrary weights. The weights_only=True load limits code execution from pickle, but tampered weights could still change clinical outputs silently. Download is gated by user confirmation.
  ```
  urllib.request.urlretrieve(WEIGHTS_BASE_URL + name, tmp)
          os.replace(tmp, target)
  ```
  Suggestion: Pin SHA-256 hashes for each weight file and verify before os.replace; state the source commit of the weights in the docs.

### Inference runs on the GUI thread and log() pumps the event loop
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`DMSAAI/DMSAAI.py:411`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAI.py#L411): segment()/classify() call the networks synchronously from the button handler (no thread, no progress bar), so Slicer is frozen during CPU inference of up to 7 networks and looks hung. Additionally log() calls `slicer.app.processEvents()` for every message (DMSAAI.py:319-323), which re-enters the event loop from within a slot and can let the user click buttons while preprocessed state is half-updated.
  ```
      def onSegment(self):
          with slicer.util.tryWithErrorDisplay("Segmentation failed.", waitCursor=True):
              if not self.logic.ensureRequirements(askConfirmation=True):
                  return
  ```
  Suggestion: Run the analysis in a slicer.util.ProgressDialog worker (or disable/enable the buttons around a guarded event-process) and drop processEvents from log().

### Module test does not reset the scene before the third test
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DMSAAI/DMSAAI.py:1136`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAI.py#L1136): test_AnalysisSettings runs on the scene left over from the quantification test, and it writes to the user's real Qt settings (settings.save_analysis_settings), restoring only the values it captured. If the test is interrupted between save and restore, the user's saved preferences are replaced by the test's values.
  ```
      def runTest(self):
          self.setUp()
          self.test_PlanarGeometry()
          self.setUp()
          self.test_QuantificationOnSyntheticImage()
          self.test_AnalysisSettings()
  ```
  Suggestion: Call setUp() before every test and back up/restore the full QSettings group (or use a temporary settings scope).

### No model provenance, validation or bundled sample data for an AI diagnostic-adjacent tool
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:35`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/README.md#L35): The README explains installation and usage but gives no training cohort, validation metrics, failure modes or reference publication for the segmentation and classification networks, and the tests require an external DMSAAI checkout (Testing/test_pipeline.py:28-29) instead of shipping a small anonymised sample study. Users cannot judge the reliability of the printed findings such as "Probable Abnormal Cortical Uptake".
  ```
  3. The model weights (about 140 MB) are downloaded from the DMSAAI repository on first use into Slicer's cache
     folder, after you confirm the download. You can point *Advanced → Model weights* at an existing DMSAAI folder
     instead.
  ```
  Suggestion: Add a short model-provenance section (training data, reported accuracy, limitations) and ship or cite a small de-identified sample study.

### No stated terms for the downloaded model weights and bundled colour maps
minor; license; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`DMSAAI/DMSAAILib/networks.py:11`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAILib/networks.py#L11): The extension code is MIT, but about 140 MB of .pth weights are fetched at runtime from the author's DMSAAI repository and seven colour-map CSVs are bundled (DMSAAI/Resources/ColorMaps) whose origin is undocumented. I could not verify that the upstream repository grants permission to redistribute these artefacts, so distribution permission for the bundled/downloaded material is unconfirmed.
  ```
  WEIGHTS_BASE_URL = "https://raw.githubusercontent.com/4burakfe/DMSAAI/main/"
  ```
  Suggestion: State the license of the weights and of the colour maps in the README (and confirm the upstream DMSAAI repository carries a compatible license).

### README button name does not match the UI
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`README.md:61`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/README.md#L61): The README says to click 'Clinical Evaluation', but the widget button is labeled 'AI-powered Evaluation'. Users following the docs will not find the button.
  ```
  5. Click **Clinical Evaluation** for the cortical abnormality, normal kidney, afunctional kidney and horseshoe
     kidney models.
  ```
  Suggestion: Use the actual label 'AI-powered Evaluation' in the README.

### Screenshot URL points to a different repository name
minor; packaging; raised by deepseek, haiku
- **deepseek** (info, low confidence, quote verified) [`CMakeLists.txt:11`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/CMakeLists.txt#L11): The icon is served from the extension repository while the screenshot is served from the separate stand-alone app repository on a moving `main` branch; a change or deletion there breaks the catalog listing silently. I could not fetch the URLs to confirm they resolve.
  ```
  set(EXTENSION_ICONURL "https://raw.githubusercontent.com/4burakfe/SlicerDMSAAI/main/DMSAAI.png")
  set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/4burakfe/DMSAAI/main/scr.jpg")
  ```
  Suggestion: Serve both from the extension repository (scr.jpg is already committed there) and, if possible, pin to a commit or release asset.
- **haiku** (minor, medium confidence, quote verified) [`CMakeLists.txt:11`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/CMakeLists.txt#L11): The screenshot URL uses the repo name DMSAAI while the source repo is SlicerDMSAAI; the icon URL uses SlicerDMSAAI. If scr.jpg is not present in the DMSAAI repo, the Extensions Manager screenshot will be broken. scr.jpg is also committed in this repo.
  ```
  set(EXTENSION_ICONURL "https://raw.githubusercontent.com/4burakfe/SlicerDMSAAI/main/DMSAAI.png")
  set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/4burakfe/DMSAAI/main/scr.jpg")
  ```
  Suggestion: Point EXTENSION_SCREENSHOTURLS at the SlicerDMSAAI repo (main/scr.jpg), which contains the file.

### monai/einops installed into Slicer's Python unpinned and with dependency resolution enabled
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`DMSAAI/DMSAAI.py:675`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAI.py#L675): `monai>=1.3` (REQUIREMENTS, DMSAAI.py:589-592) is an open-ended range, and pip_install resolves its transitive requirements into Slicer's shared environment, so a future MONAI release can pull different dependency versions (and its model API could change so the published weights no longer load). This affects all extensions sharing that Python once any user runs the install.
  ```
          for requirement in missing:
              self.log(f"Installing {requirement}...")
              slicer.util.pip_install(requirement)
          importlib.invalidate_caches()
  ```
  Suggestion: Use an upper bound (e.g. `monai>=1.3,<1.6`), consider `pip_install(..., no_deps=True)` where feasible, and record the tested MONAI version in the README.

### Dependency installation can bypass the confirmation dialog
info; environment; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`DMSAAI/DMSAAI.py:543`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAI.py#L543): The Advanced button installs packages without a second confirmation. This is an explicit user click on a button whose tooltip states it installs MONAI and einops, so it is informed consent in practice, but it is one click away from modifying Slicer's environment with no size/version information shown.
  ```
      def onInstallDependencies(self):
          with slicer.util.tryWithErrorDisplay("Failed to install Python dependencies.", waitCursor=True):
              if self.logic.ensureRequirements(askConfirmation=False):
  ```
  Suggestion: Show the exact requirements (and their resolved versions) in the confirmation dialog even for the button.

### Model is reloaded from disk on every call
info; soundness; raised by haiku
- **haiku** (info, high confidence, quote verified, other lines) [`DMSAAI/DMSAAILib/networks.py:143`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAILib/networks.py#L143): segment() and classify() rebuild the network and reload weights from disk on each click, including one DenseNet per kidney side and per class (up to 7 loads per evaluation). This is slow on CPU and adds memory churn, but it is not a correctness defect.
  ```
  for side in ("left", "right"):
          findings = []
          for typeName, files in CLASSIFIER_FILES.items():
              p = _positive_probability(_load(_build_classifier(), os.path.join(weightsDir, files[side]), device),
  ```
  Suggestion: Cache loaded models keyed by path and device, and run long inference off the GUI thread with progress.

### Patient name and ID are stored as node attributes and shown in the UI (local only)
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`DMSAAI/DMSAAILib/volumes.py:83`](https://github.com/4burakfe/SlicerDMSAAI/blob/110ffec405a958b8cbcbbf0c5bb3c11b63f5c0c0/DMSAAI/DMSAAILib/volumes.py#L83): Identifying DICOM fields are copied into MRML node attributes and displayed (DMSAAI.py:770-783), so they persist in any saved .mrb scene/volumes created from these nodes. Nothing leaves the machine, but users saving scenes should know the identity is embedded.
  ```
      if ds is not None:
          attributes[ATTR_PATIENT_ID] = str(getattr(ds, "PatientID", ""))
          attributes[ATTR_PATIENT_NAME] = str(getattr(ds, "PatientName", ""))
          attributes[ATTR_STUDY_DATE] = str(getattr(ds, "StudyDate", ""))
  ```
  Suggestion: Mention in the README that patient identifiers are stored in node attributes and end up in saved scenes, or make the attributes optional.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Well-structured port: heavy imports are lazy, PyTorch is left to the PyTorch extension (EXTENSION_DEPENDS/build_dependencies match), all Python files are installed by CMake, and there is no telemetry or image upload; weights/MONAI are only fetched after a confirmation dialog. Two safety hardenings are needed: downloaded weights come from an unpinned `.../main/` URL with no checksum, and `_load` falls back to `torch.load` without `weights_only=True` on older torch, so a tampered file could execute code. Remaining issues are minor (unpinned `monai>=1.3`, GUI-thread inference, forced module/layout switching, weights/colour-map license unverified).
Not checked: Could not access the network: the upstream weight repository 4burakfe/DMSAAI (weight licence, current content, SHA-256 of the .pth files) and the icon/screenshot URLs were not fetched.; No build was run: I did not verify that the extension configures/builds against the current Slicer superbuild or that any CI exists for this repository.; Binary resources (DMSAAI.png, icons, banners, scr.jpg) and 7 colour-map CSV files beyond the first lines were not inspected for content or provenance.; No Slicer runtime was available, so DICOM plugin registration, layout switching and segmentation/classification behaviour were assessed by reading code only.; The stand-alone tests in Testing/test_pipeline.py were not executed (they need an external DMSAAI checkout).
Questions for the author: What license applies to the .pth model weights in 4burakfe/DMSAAI, and are users allowed to redistribute them?; Why is the `torch.load(..., weights_only=True)` TypeError fallback kept? Which supported torch versions would hit it, given PyTorch is installed through the PyTorch extension?; Could the weight downloads be pinned to a commit (or release asset) with published SHA-256 hashes?; Where do the custom colour maps (Hel, TruGold, Valhalla, Jotun, Vanaheim, HotIron, DICOM-Custom) come from and under what terms are they redistributed?; Is there any published validation (cohort, sensitivity/specificity) for the segmentation and classification networks that could be linked from the README?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
DMSAAI is a well-structured and implemented 3D Slicer extension for automated renal cortical scintigraphy analysis. It adheres to Slicer module conventions, correctly implements deferred dependency installation and PyTorch integration, provides clear research-use disclaimers, and includes robust unit tests. All files and licensing are in order. 🟢 Recommend merge
Not checked: Execution of extension in a running 3D Slicer instance (relies on automated tests and code inspection)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
Reviewed the catalog entry, CMake files, the main module, DICOM plugin, networks, settings, volumes, dicomviews and processing modules, plus README and a test file header. No malicious or concealed behavior found. PyTorch is not installed by the extension; MONAI/einops are pip-installed only after user confirmation. Weights are downloaded only after confirmation and loaded with torch.load(weights_only=True). Main gaps: no checksum verification of downloaded weights, unverified license for the weights, a screenshot URL pointing at a different repository name, and a few documentation mismatches. None block admission in my view, but the weight-licensing and integrity points should be confirmed.
Not checked: Did not read the bundled ColorMap CSV files or the banner/icon images beyond their listing.; Did not verify that the root icon DMSAAI.png and screenshot scr.jpg exist in the source repository at the pinned revision; scr.jpg exists locally, the icon is inferred from the scan hint.; scm_revision is 'main' (a moving branch); the exact commit reviewed is unknown and I did not resolve it.; Did not check the license or contents of the external DMSAAI weights repository, nor the weight files themselves.; Did not run the module, the tests, or any pip/pre-commit checks; no CI report was available.; Clinical validity of the networks and thresholds is not assessable from the code.


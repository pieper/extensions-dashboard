# AI review: SEEGContactDetector

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector at commit `739933484efeb08cf1b72d2507bf3b4795e3ac6b`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T10:12:59Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | ok |
| environment | concern | ok | concern |
| packaging | minor | ok | ok |
| license | ok | ok | ok |
| soundness | concern | ok | minor |
| utility | ok | ok | minor |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: Automatically localizes SEEG electrode contacts from post-implantation CT (bolts, trajectories, Gaussian-mixture electrode segmentation, polynomial curve fitting) and outputs an editable fiducial list, for epilepsy clinicians/researchers using 3D Slicer.
- **flash-lite**: SEEGContactDetector is a 3D Slicer extension for automatic localization of stereoelectroencephalography (SEEG) electrode contact centers from post-implantation CT data, supporting optional MRI-based brain masking, manual correction tools, and interactive visualization.
- **haiku**: SEEG Contact Detector is a 3D Slicer scripted extension that automatically localizes SEEG electrode contacts in post-implantation CT, using HDBrainExtraction for brain masking and optional T1-to-CT registration. It is intended for clinical and research teams working on presurgical epilepsy evaluation, and it depends on the HDBrainExtraction extension.

## Disagreements (start here)

### D1. Default-on auto-save writes fixed filenames into the CT's folder, overwriting earlier results
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`SEEGContactDetector/SEEGContactDetector.py:902`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/SEEGContactDetector/SEEGContactDetector.py#L902): autoSave defaults to True (line 136) and the save path defaults to os.path.dirname of the CT file (lines 588-589, 666-667, 753-754). Every run silently writes CT_brain_mask_autosave.seg.nrrd, transform_T1_to_CT_autosave.h5, contacts_autosave.mrk.json and bolt_fiducials_autosave.mrk.json (also lines 867-870, 1098-1100) into the user's data folder. Processing a second patient whose CT sits in the same folder (common for a study/protocol directory) destroys the first patient's saved contact localizations without any prompt, and the names also collide with the sample-data files downloaded as SEEGContactDetector_*.
  ```
          # save updated fiducials
          if save and path:
              slicer.util.saveNode(fiducial_node, os.path.join(path, "contacts_autosave.mrk.json"))
  ```
  Suggestion: Turn auto-save off by default or ask before overwriting, and include the CT/patient node name or a timestamp in the autosave filenames; keep an explicit 'Save result' action that asks for a destination.
- **haiku** (minor, medium confidence, quote verified, other lines) [`SEEGContactDetector/SEEGContactDetector.py:867`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/SEEGContactDetector/SEEGContactDetector.py#L867): With the default autoSave=True, the module writes to fixed filenames in the directory of the input CT. Each run overwrites the earlier autosave files and the user's bolt fiducial file, with no confirmation. A user who edited contacts manually and then reruns can lose those edits.
  ```
          if save and path:
              slicer.util.saveNode(boltFiducials, os.path.join(path, "bolt_fiducials_autosave.mrk.json"))
              slicer.util.saveNode(markupsNode, os.path.join(path, "contacts_autosave.mrk.json"))
  ```
  Suggestion: Use timestamped or run-specific filenames, or confirm before overwriting. Do not write over the user's original fiducial file without asking.

### D2. Registered unittest runs the full HD-BET/pytorch pipeline although the comment says testing is disabled
single; category packaging; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`SEEGContactDetector/SEEGContactDetector.py:1499`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/SEEGContactDetector/SEEGContactDetector.py#L1499): The module registers this test as a ctest (SEEGContactDetector/CMakeLists.txt:30). As written it downloads sample CT/T1/fcsv from GitHub and calls register_and_brain_mask, which invokes HDBrainExtraction and therefore downloads/installs PyTorch wheel plus model weights (line 860-861). On offline or resource-limited build machines this either fails or takes very long, so the extension's own test will be red or time out; the in-code comment contradicts the code.
  ```
          # Logic testing is disabled by default to not overload automatic build machines (pytorch is a huge package).
          # Set testLogic to True to enable testing.
          testLogic = True
  ```
  Suggestion: Set testLogic = False as the comment intends (or gate it behind an environment variable), and add a lightweight test that exercises only label parsing / load_electrodes / select_contact_points without network or pytorch.

### D3. pip installs of scipy / scikit-learn / scikit-image into Slicer's shared Python environment
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`SEEGContactDetector/SEEGContactDetector.py:920`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/SEEGContactDetector/SEEGContactDetector.py#L920): On first use the module installs scipy, scikit-learn and scikit-image with pip into Slicer's own site-packages (also lines 1112-1123, 1211-1216, 1266-1271). scikit-learn and scikit-image declare numpy/scipy dependencies, so pip can replace Slicer-bundled numpy/scipy with PyPI versions in the user's installation; that breakage is inherited by every other module and extension in that Slicer, including users who never open this module. The prompt only says a package is required, not that Slicer's environment is modified.
  ```
          try:
              import scipy
          except ModuleNotFoundError:
              if slicer.util.confirmOkCancelDisplay("This module requires 'scipy' Python package. Click OK to install it now."):
                  slicer.util.pip_install("scipy")
                  import scipy
  ```
  Suggestion: Ship the dependencies via the extension's CMake/pip requirements mechanism or the SlicerPython wheel-based approach used by other extensions; if runtime installation stays, state that it modifies the shared environment, install with --no-deps plus explicit user choice of versions, and never touch numpy/scipy that Slicer bundles.
- **haiku** (minor, medium confidence, quote verified, other lines) [`SEEGContactDetector/SEEGContactDetector.py:929`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/SEEGContactDetector/SEEGContactDetector.py#L929): On user confirmation, the module installs scikit-learn, scipy and scikit-image into Slicer's shared Python environment without version constraints. Their dependency resolution can upgrade or replace numpy or scipy that Slicer and other extensions rely on. This affects all users of the Slicer install, not just those who use this module.
  ```
              if slicer.util.confirmOkCancelDisplay("This module requires 'scikit-learn' Python package. Click OK to install it now."):
                  slicer.util.pip_install("scikit-learn")
                  from sklearn.mixture import GaussianMixture
  ```
  Suggestion: Install with constraints that keep the bundled numpy/scipy versions, or check the installed versions first and warn the user. Document the side effects of the install.

### D4. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D5. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### Long computation runs on the GUI thread with processEvents instead of a background thread
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`SEEGContactDetector/SEEGContactDetector.py:369`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/SEEGContactDetector/SEEGContactDetector.py#L369): The whole detection chain (bolt segmentation, PCA, GMM over all metal voxels, curve fitting with a correlation loop per offset) executes in the GUI thread guarded only by slicer.app.processEvents() calls (e.g. lines 958, 1030, 1134). The progress dialog has its cancel button removed and shows hard-coded percentages, so the UI appears frozen for the multi-minute runs the README advertises and the user cannot abort.
  ```
      def onRunClicked(self):
          progressbar = slicer.util.createProgressDialog(windowTitle="Detecting contacts")
          progressbar.setCancelButton(None)
  ```
  Suggestion: Move the pipeline into the logic class as a cli/CLI-node or use a QThread/slicer.util.createProgressDialog with real progress and cancellation support, as other Slicer extensions do.
- **haiku** (minor, medium confidence, quote verified) [`SEEGContactDetector/SEEGContactDetector.py:370`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/SEEGContactDetector/SEEGContactDetector.py#L370): onRunClicked creates a progress dialog and updates its text and value, but it never calls close(). The dialog can stay open after the run finishes, and it has no cancel button. If a sub-step raises (for example the ValueError in bolt_segmentation), the dialog stays open.
  ```
          progressbar = slicer.util.createProgressDialog(windowTitle="Detecting contacts")
          progressbar.setCancelButton(None)
  ```
  Suggestion: Close the dialog in a finally block, and report errors to the user.

### No research-use disclaimer or validation metrics for a clinical localization task
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`README.md:20`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/README.md#L20): The module produces electrode contact coordinates used to interpret invasive recordings, and the README/docs claim high accuracy, but no accuracy numbers, no statement of validation cohort, and no 'not for primary clinical decision making / research use' disclaimer appear anywhere (searched for clinical/disclaimer/not intended terms).
  ```
  - Automatic localization of SEEG contact centers from post-implantation CT
  - Robust detection of thousands of contacts within minutes
  ```
  Suggestion: Add a short 'Intended use / limitations' section citing the reported accuracy from the Janca et al. paper on the tested data and stating that automatic results must be reviewed by a clinician.
- **haiku** (minor, high confidence, quote verified) [`README.md:3`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/README.md#L3): The module is meant to localize electrodes for presurgical planning, and the docs describe it as supporting clinical review. The help text, the README and the docs do not say that the output is research-only or must be verified by a clinician. Users may rely on automated positions without review.
  ```
  **SEEG Contact Detector** is a 3D Slicer extension for automatic and highly accurate localization of intracerebral electrode contacts from post-implantation CT imaging.
  ```
  Suggestion: Add a clear statement that the software is not a medical device, that the output needs expert verification, and that the accuracy claims come from a cited validation.

### Scene NodeAdded observer silently overrides user-selected inputs by name matching
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`SEEGContactDetector/SEEGContactDetector.py:671`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/SEEGContactDetector/SEEGContactDetector.py#L671): Any volume whose name contains 'ct' or 't1' (and any markup list containing 'fiducials') is assigned to the module's inputs as soon as it is added to the scene, replacing the node the user explicitly selected. Loading e.g. 'T1_postcontrast' or 'func_t1_map' after choosing the preoperative T1 changes the input without notification and can silently change registration/masking results.
  ```
      def onNodeAdded(self, caller, event,  node):
          # Every time a new node is added to the scene check if it's input node
          if "ct" in node.GetName().lower() and isinstance(node, SEEGContactDetectorParameterNode.__annotations__['inputCT']):
  ```
  Suggestion: Use name heuristics only to prefill empty selections (as initializeParameterNode does) and never overwrite a non-empty user choice without asking.

### Catalog points to the moving branch 'main' rather than a fixed revision
info; soundness; raised by haiku; **quote not found in source**
- **haiku** (info, high confidence, quote quote not found) no file cited: The catalog entry sets scm_revision to 'main'. The reviewed code can therefore change without any change to the index, and I could not confirm that commit 739933484efeb08cf1b72d2507bf3b4795e3ac6b is the one in the catalog. This is informational, not a defect.
  ```
  "scm_revision": "main"
  ```
  Suggestion: Pin scm_revision to a reviewed commit or release tag, as the index usually recommends.

### Large PNG/GIF screenshots committed to the source repository
info; packaging; raised by deepseek
- **deepseek** (info, medium confidence, quote no quote) [`Screenshot01.png:1`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/Screenshot01.png#L1): About 6-7 MB of screenshots and animated GIFs (Screenshot01.png 627 KB, Screenshot02.png 674 KB, docs/images/microsteps.gif 814 KB, etc.) are committed; not blocking, but the extension package and clone size grow unnecessarily when images could be optimised or hosted in a release.
  Suggestion: Downscale or convert the documentation GIFs, or host the largest media in a release as the module comment itself recommends for data.

### License/terms of the distributed sample data are not stated
info; license; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`docs/sample_data.md:3`](https://github.com/EpiReC-ISARG/SlicerSEEGContactDetector/blob/739933484efeb08cf1b72d2507bf3b4795e3ac6b/docs/sample_data.md#L3): The module downloads a CT, a T1 and bolt fiducials from the project's GitHub releases (SEEGContactDetector.py:85-113, with SHA256 checksums, which is good), but no terms or provenance statement for the patient data accompany them. TODO.md says 'Sample data (defaced)', which suggests de-identification, yet redistribution permission is not documented.
  ```
  We provide sample data used in this documentation and in the video tutorial, which can be downloaded directly from 3D Slicer.
  ```
  Suggestion: Add one sentence in docs/sample_data.md about the de-identification and the terms under which the sample data may be redistributed and used.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Coherent, well-documented scripted module (Apache-2.0, sample data with SHA256 checksums, docs and tutorial). Main issues are environment-related: it pip-installs scipy/scikit-learn/scikit-image into Slicer's shared Python on first use (scikit-learn and scikit-image pull their own numpy/scipy, which can replace Slicer-bundled versions), which users of other extensions also inherit. It also writes fixed-name autosave files into the CT folder by default, and the registered unittest runs the full HD-BET/pytorch pipeline although its comment says logic testing is disabled. No telemetry, no uploads of user data. Fixes needed before merge: pip-install handling and the heavy default test.
Not checked: Whether HDBrainExtraction's setupPythonRequirements() prompts the user before downloading PyTorch/HD-BET weights (external repository not available in this review); The exact scm_revision commit content beyond the provided snapshot; the entry uses scm_revision 'main' so a moving branch was reviewed as of the snapshot; Licensing of HD-BET model weights downloaded by HDBrainExtraction; Behaviour of the .ui file's remaining widgets (lines 445-948) and the four icon files beyond existence; Actual runtime behaviour of the algorithms and whether the CI build/test currently passes (no execution or CI reports available)

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
SEEGContactDetector is a robust and well-crafted 3D Slicer extension for automated localization of SEEG electrode contacts from post-implantation CT and preoperative MRI scans. Code structure adheres to Slicer conventions, with proper parameter node usage, UI management, cleanup, and Apache 2.0 licensing. All dependencies are correctly declared and optional Python packages are installed via standard Slicer prompts. 🟢 Recommend merge.
Not checked: External HDBrainExtraction extension source code (though standard dependency integration via HDBrainExtractionTool is used correctly)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
I reviewed the catalog entry, the CMake files, the full main module (SEEGContactDetector.py, about 1,545 lines), the LICENSE, and the README and installation docs. I found no malicious or concealed behavior, no telemetry, and no unsafe deserialization. Sample downloads are pinned by SHA256. Package installs happen only after an OK dialog, but they are unpinned and could change shared numpy/scipy. Minor gaps: no clinical-use disclaimer, and autosave can overwrite files next to the CT. The source revision is the moving branch "main", and I did not run anything.
Not checked: The source repository was not fetched. Only the files supplied in the review package were read, so the exact commit 739933484efeb08cf1b72d2507bf3b4795e3ac6b and the main branch tip were not verified.; The UI file (Resources/UI/SEEGContactDetector.ui), icons and Testing content were listed but not read, so resource presence and the Qt widget names were not checked.; The HDBrainExtraction dependency and its model weights were not inspected.; The sample-data URLs and SHA256 checksums were not downloaded or recomputed. The claim that the sample data is defaced was not verified.; The docs/*.md files (usage, advanced, module_overview, sample_data, index, acknowledgements) were searched but not read in full.; No code was executed, and no CI results were available.
Questions for the author: Can the Python dependencies (scikit-learn, scipy, scikit-image) be pinned or constrained so that Slicer's bundled numpy and scipy are not changed?; Should autosave write to run-specific filenames, or ask before overwriting the user's bolt fiducial file?; Will you add a clinical-use disclaimer and state the validation evidence for the accuracy claims?; Can scm_revision be pinned to a reviewed commit or release tag rather than 'main'?


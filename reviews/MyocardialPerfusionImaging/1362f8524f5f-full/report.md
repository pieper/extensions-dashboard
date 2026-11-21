# AI review: MyocardialPerfusionImaging

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/4burakfe/SlicerMyocardialPerfusionImaging.git at commit `1362f8524f5fb6be045df440c5c2dce4db77467e`
- Context: pull request 2449 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-21T01:00:01Z; cost $1.11

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | minor | minor |
| packaging | unknown | concern | blocking |
| license | unknown | ok | ok |
| soundness | unknown | ok | concern |
| utility | unknown | ok | ok |
| **overall** | needs fixes | minor issues | needs fixes |

## What each reviewer says the extension does

- **claude**: Tarvos is a Slicer workflow for myocardial perfusion SPECT/PET. It covers study roles, reorientation to cardiac axes, LV wall detection, stress/rest slices and polar maps, gated QC and review (thickening, motion, EF), and DICOM export of screens and scenes. It targets nuclear medicine users.
- **gemini**: Tarvos (MyocardialPerfusionImaging) is a 3D Slicer extension for nuclear medicine clinicians and researchers to process and review myocardial perfusion SPECT and PET studies. It provides a guided six-step workflow covering study role assignment, cardiac axis reorientation (SA, HLA, VLA), automatic left ventricular wall segmentation, static stress/rest perfusion review with polar maps and TID, gated quality control, and cine gated review with wall thickening, motion, regional EF, and LV volume curves.
- **gpt**: Tarvos provides a 3D Slicer workflow for reviewing myocardial perfusion SPECT and PET studies, including cardiac reorientation, wall detection, polar maps, and gated functional measurements. It is intended for researchers working with reconstructed cardiac imaging data.

## Disagreements (start here)

### D1. CMake references a resource with the wrong filename case
partial; category packaging; raised by gemini, gpt; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`MyocardialPerfusionImaging/CMakeLists.txt:25`](https://github.com/4burakfe/SlicerMyocardialPerfusionImaging/blob/1362f8524f5fb6be045df440c5c2dce4db77467e/MyocardialPerfusionImaging/CMakeLists.txt#L25): `MyocardialPerfusionImaging/CMakeLists.txt` lists `Resources/Images/banner.jpg` (lowercase `b`) in `MODULE_PYTHON_RESOURCES`, and `MyocardialPerfusionImaging/MyocardialPerfusionImaging.py` line 50 looks up `Resources/Images/banner.jpg`. However, the file committed in the repository is `MyocardialPerfusionImaging/Resources/Images/Banner.jpg` (uppercase `B`). On case-sensitive filesystems (such as Linux, where Slicer extensions are built and packaged on the Linux factory), CMake's `slicerMacroBuildScriptedModule` will fail to find `Resources/Images/banner.jpg` during configuration/installation, breaking the Linux build.
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/Icons/${MODULE_NAME}.png
    Resources/Images/banner.jpg
    Resources/Images/logo.png
    )
  ```
  Suggestion: Rename `MyocardialPerfusionImaging/Resources/Images/Banner.jpg` to `MyocardialPerfusionImaging/Resources/Images/banner.jpg` (or update both `MyocardialPerfusionImaging/CMakeLists.txt` and `MyocardialPerfusionImaging/MyocardialPerfusionImaging.py` to match the exact filename case).
- **gpt** (blocking, high confidence, quote verified) [`MyocardialPerfusionImaging/CMakeLists.txt:25`](https://github.com/4burakfe/SlicerMyocardialPerfusionImaging/blob/1362f8524f5fb6be045df440c5c2dce4db77467e/MyocardialPerfusionImaging/CMakeLists.txt#L25): The available repository listing contains Resources/Images/Banner.jpg, not banner.jpg. On case-sensitive filesystems the build macro cannot find the listed banner resource, preventing the extension from building or packaging; the hub also looks for the lowercase name.
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/Icons/${MODULE_NAME}.png
    Resources/Images/banner.jpg
    Resources/Images/logo.png
  ```
  Suggestion: Rename the file to banner.jpg or consistently change both the CMake entry and runtime path to the actual filename; verify a Linux build.
- claude on re-check: **real: yes, blocking**: CMakeLists.txt:25-29 lists Resources/Images/banner.jpg and Resources/Images/logo.png. The directory listing shows only Resources/Images/Banner.jpg (capital B), and no logo.png at all. On case-sensitive Linux build machines both resources are missing, so the scripted-module build/install step will fail. MyocardialPerfusionImaging.py:50 also uses the lowercase name. The issue is larger than the case mismatch: logo.png is absent too.
- gpt on re-check: **real: yes, blocking**: MyocardialPerfusionImaging/CMakeLists.txt:25-34 lists 'Resources/Images/banner.jpg' as a resource supplied to the build macro, but the repository listing shows only 'Resources/Images/Banner.jpg'. On case-sensitive systems the specified input is absent, breaking the scripted-module build/package; CMake also lists missing 'Resources/Images/logo.png'. MyocardialPerfusionImaging/MyocardialPerfusionImaging.py:49-50 likewise references the lowercase banner. I could not run the build or inspect the Slicer macro implementation.
- gemini on re-check: **real: yes, blocking**: `MyocardialPerfusionImaging/CMakeLists.txt:25-29` lists `Resources/Images/banner.jpg` (lowercase `b`) and `Resources/Images/logo.png` in `MODULE_PYTHON_RESOURCES`, and `MyocardialPerfusionImaging/MyocardialPerfusionImaging.py:50` looks up `Resources/Images/banner.jpg`. In the repository, `MyocardialPerfusionImaging/Resources/Images/` contains `Banner.jpg` (uppercase `B`) and does not contain `logo.png` at all. On case-sensitive filesystems (Linux build factory) and for the missing `logo.png` on all platforms, `slicerMacroBuildScriptedModule` (`ctkMacroCompilePythonScript`) will fail to copy/install the missing resources.

### D2. DICOM scene export can file unrelated patient data under one patient
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (2 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/dicomexport.py:389`](https://github.com/4burakfe/SlicerMyocardialPerfusionImaging/blob/1362f8524f5fb6be045df440c5c2dce4db77467e/MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/dicomexport.py#L389): The exporter packs the entire Slicer scene but selects one reference patient's DICOM identity. The mixed-patient scan in case.py explicitly excludes studies assigned role None, whereas those nodes remain in the scene. If an unrelated patient's study is present or excluded, exporting the scene and sending it from the DICOM browser can disclose that patient's images and identifiers inside a bundle filed under the selected patient, without a specific warning about the excluded data.
  ```
  def exportScene(folder):
      """The whole scene as a Slicer Data Bundle DICOM file in folder. Returns ([path], reference node or None, added
      to the database)."""
      import DICOMLib
      slicer = _slicer()
      tags, fileName, reference = exportTags()
  ```
  Suggestion: Export a patient-scoped scene or inspect all scene contents, including excluded and unidentifiable nodes, and block or obtain explicit informed confirmation before writing a mixed-patient DICOM bundle.
- claude on re-check: **real: unsure, minor**: dicomexport.py:389-409 exports the whole scene as a Slicer Data Bundle under the reference study's tags. That is the user's own loaded scene, saved only after the user clicks Save > Scene as DICOM. The report dialog (_report, ~445-455) says which patient and study it was filed under. Mixing in another patient's data would require the user to have loaded it, and nothing is sent out automatically. This is a possible data-labelling pitfall, not a concrete path to harm, so it is not blocking safety.
- gpt on re-check: **real: yes, blocking**: MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/dicomexport.py:389-406 calls 'exportTags()' and 'DICOMLib.DICOMExportScene(fileName, work)' to export the entire scene under a single reference; lines 56-61 describe the whole scene as a private-tag bundle filed under the MPI patient's study. case.py:159-168 excludes role None from the patient scan, and case.py:243-245 advises setting another patient's volumes to None. Those volumes remain in the scene; if the user subsequently sends the bundle via the DICOM browser, unrelated patient data may be disclosed under the wrong identity. The tooltip says whole scene, but does not specifically warn that excluded patients remain included. The Slicer DICOM exporter implementation and an actual export were not available to inspect.
- gemini on re-check: **real: yes, minor**: `MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/dicomexport.py:389-409` uses `DICOMLib.DICOMExportScene` to export the entire Slicer scene (`slicer.mrmlScene`) as a Slicer Data Bundle (`sdbFile`) tagged with the reference patient's DICOM attributes (`exportTags()`). Meanwhile, `MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/case.py:166-168` skips studies with `study.role == studiesLib.EXCLUDED_ROLE` (`None`), and `case.py:244-245` instructs the user to "set the volumes of another patient to None in Data roles", leaving those nodes in the scene where `exportScene` (as well as `saveSceneBundle`) will include them in the exported scene bundle. Note that `dicomexport.py:56-59` explicitly documents in the UI tooltip that "Save scene as DICOM Packs the whole Slicer scene", which is how Slicer's built-in `DICOMExportScene` works, though the advice in `case.py:244-245` to exclude another patient's volume by setting its role to `None` rather than removing it from the scene is a minor usability/design caveat rather than a blocking security issue.

### D3. Second-monitor screenshot can overwrite an existing file without confirmation
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/dicomexport.py:545`](https://github.com/4burakfe/SlicerMyocardialPerfusionImaging/blob/1362f8524f5fb6be045df440c5c2dce4db77467e/MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/dicomexport.py#L545): The save dialog only selects and checks the first path. When a second monitor window is captured, the automatically constructed _2.png path can already exist, and saving it overwrites that unrelated prior screenshot without an overwrite confirmation.
  ```
          root = path[:-4]
          paths = []
          for number, (_, image) in enumerate(grabs, start=1):
              target = path if number == 1 else f"{root}_{number}.png"
              if not image.save(target, "PNG"):
                  raise ExportError(f"Could not write {target}.")
  ```
  Suggestion: Check every generated output path before writing and ask before replacing any existing file, or use collision-free filenames.
- claude on re-check: **real: yes, minor**: dicomexport.py:545-550 writes {root}_2.png without checking whether it exists. The Qt save dialog only confirms overwrite of the first path. The overwritten file is a user-chosen screenshot name with a numeric suffix, so this is an ordinary minor bug, not a safety blocker.
- gpt on re-check: **real: yes, blocking**: MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/dicomexport.py:531-550 asks for one path, then uses 'target = path if number == 1 else f"{root}_{number}.png"' and 'image.save(target, "PNG")' without checking whether the derived paths already exist. With a second monitor capture an existing _2.png can be overwritten without confirmation, a concrete path to unintended user-file destruction. Lines 326-337 confirm additional visible monitor windows are included; the exact Qt runtime behavior was not tested.
- gemini on re-check: **real: yes, minor**: In `MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/dicomexport.py:534-551`, `saveScreenshot()` prompts for `path` via `QFileDialog.getSaveFileName` (defaulting to a timestamped name `Tarvos_{caseLabel()}_{stamp()}.png`) and then writes any additional Monitor 2 window capture to `f"{root}_{number}.png"` (`dicomexport.py:548-549`) without a second overwrite prompt. Because the default filename includes a second-granularity timestamp (`%Y%m%d_%H%M%S`, `dicomexport.py:166`), an overwrite would only happen if a user manually chose an existing base name where `{root}_2.png` already existed. This is a minor UX detail, not a blocking safety issue.

### D4. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **real: yes, info**: I read dicomexport.py (exports, file dialogs, temp files). Files are written only to user-chosen folders or temporary folders, and the data stays local. There is no network use and no pip install. I found no concrete safety path. The D2 and D3 findings are minor. I did not audit every file, such as myocardium.py, in full. Rating: ok.
- gpt on re-check: **rating blocking**: The safety rating is blocking: dicomexport.py:389-406 exports the whole scene under one patient's DICOM identity while case.py:159-168 excludes role None from the mixed-patient check, enabling unintended disclosure on subsequent sending; dicomexport.py:541-550 also writes derived screenshot filenames without overwrite checks. I reviewed these flows and searched the repository for download, subprocess, unsafe deserialization, and deletion APIs; this was not an exhaustive audit of all code or external dependencies.
- gemini on re-check: **rating ok**: Checked `CMakeLists.txt`, `MyocardialPerfusionImaging/CMakeLists.txt`, `MyocardialPerfusionImaging/MyocardialPerfusionImaging.py`, and `MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/` modules (`dicomexport.py`, `case.py`, etc.). There is no malicious behavior, telemetry, silent network transmission, arbitrary code execution, or environment modification. DICOM and file exports are explicitly user-triggered to local user-chosen folders and local Slicer DICOM database (`dicomexport.py:427-556`).

### D5. Rating of soundness
rating dispute; category soundness; raised by claude, gemini, gpt; outcome after cross-examination: **settled: minor (concern, minor)**
Ratings: claude unknown, gemini ok, gpt concern
- claude on re-check: **real: yes, minor**: Export code reports errors through message boxes (dicomexport.py:458-475) and uses temp folders with cleanup. Minor issues are the silent overwrite of the _N.png files (D3) and the scene export being filed under a single reference patient (D2). The missing resource files are a packaging problem (D1). Rating: minor.
- gpt on re-check: **rating concern**: MyocardialPerfusionImaging/MPIGatedQC.py:723-743 invokes 'self.gatedStudy(slot, rebuild)' synchronously under a wait cursor, and lines 231-258 show per-frame segmentation and reslicing; long sequences can block the UI with no progress during this work. There are positive conventions too: MyocardialPerfusionImaging.py:302-306 removes its listeners and observers, and MPIGatedQC.py contains synthetic numerical tests (e.g. lines 980-1007). This is a non-blocking soundness assessment based on inspected paths, not runtime or algorithm validation.
- gemini on re-check: **rating minor**: Checked `MyocardialPerfusionImaging/CMakeLists.txt`, `MyocardialPerfusionImaging/MyocardialPerfusionImaging.py`, `MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/case.py`, and `MyocardialPerfusionImaging/MyocardialPerfusionImagingLib/dicomexport.py`. The codebase is well-structured, uses lazy imports, handles errors cleanly, and follows Slicer conventions, with only minor issues (such as the resource path mismatch in `MyocardialPerfusionImaging.py:50` / `CMakeLists.txt:27-28` and the minor behaviors in D2/D3).


## Findings from some reviewers

### Gated segmentation runs synchronously without per-frame progress
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`MyocardialPerfusionImaging/MPIGatedQC.py:243`](https://github.com/4burakfe/SlicerMyocardialPerfusionImaging/blob/1362f8524f5fb6be045df440c5c2dce4db77467e/MyocardialPerfusionImaging/MPIGatedQC.py#L243): The UI's show() calls gatedStudy().build() synchronously, fitting and reslicing each frame before returning to the event loop. For large gated sequences the interface can appear frozen, with no per-frame progress or cancellation.
  ```
          for label, node in gates:
              array = slicer.util.arrayFromVolume(node).astype(np.float32)
              matrix = worldToIjk(node, self.study)
              spacing = node.GetSpacing()
              try:
                  # on the gate masked like the static volume the wall was detected on (liver and gut out)
  ```
  Suggestion: Move computation off the GUI thread where safe, or provide responsive per-frame progress and cancellation.

### Module directory is inserted into the shared Python import path
minor; environment; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`MyocardialPerfusionImaging/MyocardialPerfusionImaging.py:34`](https://github.com/4burakfe/SlicerMyocardialPerfusionImaging/blob/1362f8524f5fb6be045df440c5c2dce4db77467e/MyocardialPerfusionImaging/MyocardialPerfusionImaging.py#L34): Loading the extension changes import precedence for the whole Slicer process, including other extensions, and can cause name collisions if another module uses the same top-level names.
  ```
  _MODULE_DIR = os.path.dirname(os.path.abspath(globals().get("__file__", "") or "."))
  if globals().get("__file__") and _MODULE_DIR not in sys.path:
      sys.path.insert(0, _MODULE_DIR)
  ```
  Suggestion: Use Slicer's normal module paths and uniquely named packages without prepending to sys.path, where possible.

### Regional EF tooltip misstates the default reference
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`MyocardialPerfusionImaging/MPIGated.py:630`](https://github.com/4burakfe/SlicerMyocardialPerfusionImaging/blob/1362f8524f5fb6be045df440c5c2dce4db77467e/MyocardialPerfusionImaging/MPIGated.py#L630): DEFAULT_EF_REFERENCE is actually 'fixed', and the combo selects that constant. A user relying on the tooltip may believe whole-heart motion is removed when the selected fixed reference instead incorporates that motion into regional EF.
  ```
              "rings into wedges from the long axis out to the endocardium, between the valve plane and the LV "
              "center (so a basal wedge also shrinks as the valve plane descends), and on the apex into cones from "
              "the LV center. Floating (default): every frame's own LV center and epicardial apex, since with a "
              "fixed center a heart that moves as a whole makes the wedges on one side grow and on the other shrink "
              "(a 4 mm shift changes them by tens of %). Fixed: the static fit's LV center and axis. Myocardium mass "
  ```
  Suggestion: Align the displayed default, the constant, and the documented interpretation.

### Toolbar and MRML scene observers are installed globally at Slicer startup
minor; environment; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`MyocardialPerfusionImaging/MyocardialPerfusionImaging.py:78`](https://github.com/4burakfe/SlicerMyocardialPerfusionImaging/blob/1362f8524f5fb6be045df440c5c2dce4db77467e/MyocardialPerfusionImaging/MyocardialPerfusionImaging.py#L78): Every module in this extension (`MyocardialPerfusionImaging.py` and the step modules) connects `_installToolbar` to `startupCompleted()`, which instantiates `WorkflowToolbar` (`MyocardialPerfusionImagingLib/toolbar.py` lines 278-324) at Slicer startup for all users, even if the user never opens the Myocardial Perfusion Imaging module. While the toolbar hides itself when another module is active, `WorkflowToolbar.__init__` also attaches persistent `EndCloseEvent` and `EndImportEvent` observers to `slicer.mrmlScene` that call `resetToStart()`. `resetToStart()` creates/modifies a singleton `vtkMRMLScriptedModuleNode` (`MPISession`) in the scene on every scene import or close across the entire Slicer session. Creating toolbar widgets and scene observers should be deferred until the user actually enters the module.
  ```
          if not slicer.app.commandOptions().noMainWindow:
              slicer.app.connect("startupCompleted()", _installToolbar)
  ```
  Suggestion: Install the workflow toolbar and register scene observers lazily when `MyocardialPerfusionImagingWidget.enter()` (or `setup()`) is first called rather than on Slicer's `startupCompleted()` signal.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I read the CMake files, MPIGated.py, widgets.py, the module class of MyocardialPerfusionImaging.py, and parts of toolbar.py and dicomexport.py. A search of the whole module folder found no pip installs, subprocess calls, network access, pickle, eval or exec. The MIT license is present and the dependencies match between the catalog entry and EXTENSION_DEPENDS. The main problem is packaging. The CMake resource list names `Resources/Images/banner.jpg`, but the committed file is `Banner.jpg`. On case-sensitive build machines (Linux, probably macOS) this can break the build or the banner. The logo.png listed in the hints was not visible in the file listing, which showed only Banner.jpg. I did not read most of the remaining large modules. No clinical-use disclaimer was checked.
Not checked: Most of the code of MPIProcessing, MPIMyocardium, MPIReview, MPIGatedQC, MPIDataRoles and Lib/myocardium, display and parameters was not read line by line; I relied on a regex search for dangerous calls.; Whether Resources/Images/logo.png and Branding/Tarvos_logo.png exist (large files not readable).; Whether the build succeeds in practice, and the DICOMSpectRecon and PET4D dependencies.; Clinical-use disclaimer in the README and module help.; Whether the revision `main` resolves to commit 1362f85.
Questions for the author: Is the resource file `banner.jpg` or `Banner.jpg`, and is `Resources/Images/logo.png` committed? Does the build pass on Linux?; Do you plan to pin scm_revision to a commit or tag?

### Gemini 4 Argon (`google/gemini-4-argon`): minor issues
Tarvos (`MyocardialPerfusionImaging`) is a well-written, self-contained 3D Slicer extension for myocardial perfusion SPECT and PET analysis under the MIT license. It has no security concerns, no external pip dependencies, and good documentation with a clear non-clinical disclaimer. One packaging issue should be fixed: `MyocardialPerfusionImaging/CMakeLists.txt` and `MyocardialPerfusionImaging.py` reference `Resources/Images/banner.jpg` (lowercase), whereas the file in the repository is `Resources/Images/Banner.jpg` (uppercase), which will cause CMake build failures on case-sensitive Linux filesystems. Additionally, deferring toolbar creation from Slicer startup (`startupCompleted()`) to module entry is recommended.

🟢 Recommend merge (admission requirements met; fixing the `Banner.jpg` case mismatch is strongly recommended so Linux factory builds succeed).
Not checked: Binary image contents of Branding/Tarvos_logo.png and MyocardialPerfusionImaging/Resources/Images/logo.png (2 MB each); Runtime execution in 3D Slicer with sample SPECT/PET datasets
Questions for the author: Could you rename `MyocardialPerfusionImaging/Resources/Images/Banner.jpg` to `banner.jpg` so that CMake configuration succeeds on case-sensitive Linux filesystems?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The source contains a build-breaking resource filename mismatch on case-sensitive systems and two export paths that can unintentionally disclose or overwrite data. The documented workflow, research-use notice, MIT license, and synthetic tests are useful, but the build and tests could not be run. The catalog's moving branch, external dependencies, and exact source revision could not be independently verified. 🔴 Do not merge yet: fix the resource path and export safety issues, and verify the selected revision and dependencies.
Not checked: No commands, builds, Slicer runtime tests, or automated CI results were available.; The supplied commit 1362f8524f5fb6be045df440c5c2dce4db77467e and catalog branch main could not be independently resolved or compared; the exact revision of the provided file snapshot is unverified.; The DICOMSpectRecon and PET4D source, transitive dependencies, and distribution terms were not accessible for inspection.; Binary images, real patient datasets, clinical validation, prior review baseline, and submission checklist were not inspected.


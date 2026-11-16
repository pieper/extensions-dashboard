# AI review: ClassAnnotation

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/lorenaromeo/SlicerClassAnnotation.git at commit `f2db4d2b6b2a626a7318aa50359fb01cb2538a1d`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-16T10:13:31Z; cost $0.81

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | ok | minor |
| packaging | unknown | minor | minor |
| license | unknown | ok | ok |
| soundness | unknown | minor | concern |
| utility | unknown | ok | minor |
| **overall** | minor issues | minor issues | needs fixes |

## What each reviewer says the extension does

- **claude**: ClassAnnotation is a scripted Slicer module for manually assigning class labels (single or multi-label) to cases in flat or hierarchical image datasets. It writes results to CSV and copies the cases into per-class output folders. It is aimed at clinicians and researchers building annotated datasets.
- **gemini**: ClassAnnotation is a 3D Slicer scripted module that helps clinicians and researchers manually annotate medical image datasets (NRRD, NIfTI, DICOM, MHA, and 2D images) with single-label or multi-label class assignments. It supports flat and hierarchical dataset folders, saves annotations and SHA-256 volume hashes to CSV/JSON files, organizes copies of patient files into class subfolders, and offers random and manual review modes.
- **gpt**: ClassAnnotation lets Slicer users browse medical image datasets and assign case-level class labels. It saves annotations in CSV files and organizes copied cases by class, with manual and random review modes.

## Disagreements (start here)

### D1. Feature name `..` can delete the entire output directory
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified, other lines) [`ClassAnnotation/ClassAnnotation.py:2888`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/ClassAnnotation.py#L2888): Feature names are editable and generation calls migrateRenamedFeaturesBeforeGenerate, which invokes this function for the new name. Renaming a feature to `..` makes featureDir resolve to the parent output directory; rmtree can recursively remove its CSVs, class folders, and any unrelated user files there, even if the final directory removal fails.
  ```
          outDir = self._baseOutputDir(datasetPath, outputPath)
          base = os.path.join(outDir, "multi_label")
          featureDir = os.path.join(base, feature_name.replace(" ", "_").replace("/", "_"))
  
          if os.path.isdir(featureDir):
              shutil.rmtree(featureDir, ignore_errors=True)
  ```
  Suggestion: Reject dot components and path separators, resolve and verify containment under a dedicated managed directory, and avoid recursively deleting paths based on user-provided names.
- claude on re-check: **real: yes, minor**: ClassAnnotation.py:3618-3623 builds featureDir from the user-typed feature name with only ' ' and '/' replaced, and then calls rmtree. A name of '..' resolves to the output folder (_baseOutputDir, 2800-2803). The rename path (1125-1191) passes the typed name through. So the code really can delete the module's output dir, including its CSVs. It needs the user to deliberately type '..' as a feature name. The target is the module's own 'output' folder, not arbitrary user data. On Windows a backslash name could go further. It is a missing-sanitization bug, not a concrete path to harm, so not blocking.
- gpt on re-check: **real: yes, blocking**: ClassAnnotation/ClassAnnotation.py:253-254 calls migration on generation; lines 1140-1145 map edited names, and lines 1180-1190 rebuild using the new name. Lines 3618-3623 say `featureDir = os.path.join(base, feature_name.replace(" ", "_").replace("/", "_"))` and `shutil.rmtree(featureDir, ignore_errors=True)`. For a renamed feature `..`, with multi_label still present, the path reaches the output directory and recursively deletes its contents, including unrelated files. The final removal of the `..` path may fail, but its contents may already be gone.
- gemini on re-check: **real: yes, minor**: In ClassAnnotation/ClassAnnotation.py:1180-1191 (migrateRenamedFeaturesBeforeGenerate) and 3618-3623 (rebuildMultiFeatureFolders), feature_name is only sanitized with `.replace(" ", "_").replace("/", "_")`. If a feature is named or renamed to `..`, `featureDir = os.path.join(base, "..")` points to `outDir`, and `shutil.rmtree(featureDir, ignore_errors=True)` deletes the contents of `outDir` (CSVs, JSONs, and folders inside `output/`). While real, this requires a user to type `..` as a feature name in the UI table and primarily affects the extension's own `output/` subdirectory, so it is a minor input-sanitization issue rather than a blocking safety vulnerability.

### D2. Routine classification clears unrelated unsaved Slicer scene nodes
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified, other lines) [`ClassAnnotation/ClassAnnotation.py:446`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/ClassAnnotation.py#L446): After assigning a single-label class, the module clears the entire MRML scene, not just its own loaded patient nodes. Users who added or edited unrelated unsaved nodes after the initial dataset-load confirmation lose that work without a new warning; similar clears occur during mode changes and review.
  ```
          self.updateTable()
          self.populatePatientDropdown()
  
          self.updateButtonStates()
  
          slicer.mrmlScene.Clear(0)
  ```
  Suggestion: Remove only nodes created by this module, or explicitly confirm and save before any whole-scene clear.
- claude on re-check: **real: yes, minor**: mrmlScene.Clear(0) is called at many places (e.g. 452, 2394). It clears the whole scene after each classification. The module's workflow loads each patient into the scene. At dataset load (1632-1645) the user confirms that 'Loading a new dataset will clear the scene'. Clearing the scene is the intended design of an annotation module, and the user is warned once. It is a UX and soundness concern, not a safety one. The code sends no data anywhere.
- gpt on re-check: **real: yes, blocking**: ClassAnnotation/ClassAnnotation.py:2361-2397 performs classification and then `slicer.mrmlScene.Clear(0)` before loading the next case, without asking again. The separate dataset-load confirmation at lines 1632-1645 says `Loading a new dataset will clear the scene. Do you want to continue?` but does not protect unrelated unsaved nodes added later. Those nodes can be lost during normal classification.
- gemini on re-check: **real: yes, minor**: In ClassAnnotation/ClassAnnotation.py:2394 (and lines 452, 778, 952, 986, 1652, 1885, 2039, 2061, 2133, 2172, 2217, 2729), the module calls `slicer.mrmlScene.Clear(0)` before loading the next patient or switching modes, rather than removing only the nodes it loaded. This is a real Slicer usability/soundness issue if the user has other unsaved nodes in the scene, though in a dedicated batch-annotation workflow clearing the scene between patients is an understandable design shortcut (minor severity, not a blocking safety issue).

### D3. Saving can delete pre-existing unrelated class-named folders
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`ClassAnnotation/ClassAnnotation.py:3718`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/ClassAnnotation.py#L3718): Every single-label save invokes this cleanup on the selected base's existing output folder. An unrelated directory such as output/class123_backup that is not an active class matches the regex and is silently removed recursively, without checking ownership or asking the user.
  ```
              looks_like_class = bool(re.match(r"^class\d+.*$", d, re.IGNORECASE)) or (d in set(self._safe_folder(v) for v in (classIdToName or {}).values() if v))
              if not looks_like_class:
                  continue
  
              if d not in allowed:
                  shutil.rmtree(full, ignore_errors=True)
  ```
  Suggestion: Use a dedicated newly created managed output directory or an explicit ownership manifest; never recursively delete unverified existing folders.
- claude on re-check: **real: yes, minor**: cleanupSingleClassFolders (3694-3725) only scans the module's own '<dataset>/output' folder. It rmtree's any directory matching ^class\d+.* that is not an active class folder (3718-3723). A user-created folder like class123_backup in that output folder would be removed. This is real, but the scope is narrow: only the module-owned output folder, with names that mimic its own class folders. It is a minor data-loss edge case, not blocking.
- gpt on re-check: **real: yes, blocking**: ClassAnnotation/ClassAnnotation.py:2994-2996 calls cleanup following single-label saving. Lines 3700-3709 return only if there are no allowed active class folders; lines 3718-3723 use `looks_like_class = bool(re.match(r"^class\d+.*$", d, re.IGNORECASE)) or (d in set(self._safe_folder(v) for v in (classIdToName or {}).values() if v))` and `shutil.rmtree(full, ignore_errors=True)`. Thus, when at least one active class exists, a pre-existing unrelated `output/class123_backup` not in the allowed set can be silently recursively removed.
- gemini on re-check: **real: yes, minor**: In ClassAnnotation/ClassAnnotation.py:3696-3723 (`cleanupSingleClassFolders`, called from `saveSingleCSV` at line 2996), `outDir` is `os.path.join(base, "output")` (from `_baseOutputDir` at lines 2800-2803). Inside that `output` subdirectory, any directory matching `^class\d+.*$` (case-insensitive) or a current class name that is not in the currently active `allowed` set is deleted with `shutil.rmtree(full, ignore_errors=True)`. Since this occurs inside the extension's `output` folder to clean up stale class folders when all cases of a class are reclassified, it is intentional state synchronization, though the broad regex `^class\d+.*$` could remove a user-created backup folder named `class1_backup` placed inside `output/`. This is a minor issue, not blocking.

### D4. Flat dataset file matching mixes patients with shared ID prefixes
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`ClassAnnotation/ClassAnnotationLib/ClassAnnotationUtils.py:42`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/ClassAnnotationLib/ClassAnnotationUtils.py#L42): For flat cases named patient1.nrrd and patient10.nrrd, the original-file lookup for patient1 includes both. The save and hash paths use this lookup, so patient10's image is copied into patient1's class folder and duplicate detection hashes the wrong group; users can distribute or interpret a mislabeled case.
  ```
                  else:
                      if baseName.startswith(patientID):
                          originalFiles.append(os.path.join(root, file))
  ```
  Suggestion: Match the exact extracted patient ID consistently with getPatientFilesForReview, and test IDs that share prefixes.
- claude on re-check: **real: yes, major**: ClassAnnotationUtils.py:42-44 uses baseName.startswith(patientID) for flat datasets. patient1 therefore also matches patient10.nrrd. findOriginalFile is used when copying files into class folders (ClassAnnotation.py:3653-3662) and for hashing. The result is mis-copied files and wrong duplicate hashes in flat datasets with shared ID prefixes. This is a real correctness bug that affects output integrity.
- gpt on re-check: **real: yes, major**: ClassAnnotation/ClassAnnotationLib/ClassAnnotationUtils.py:42-44 uses `if baseName.startswith(patientID):` then `originalFiles.append(os.path.join(root, file))`; with flat patient1.nrrd and patient10.nrrd and a dataset path not containing `output`, patient1 matches both. Patient IDs are separately derived at ClassAnnotation/ClassAnnotation.py:3521-3531, whereas lines 3268-3275 copy every matched file to patient1's class folder and lines 2987-2988 hash the matched group. This can mislabel exported images and distort duplicate detection; it is an ordinary correctness issue, not an admission blocker by itself.
- gemini on re-check: **real: yes, major**: In ClassAnnotation/ClassAnnotationLib/ClassAnnotationUtils.py:42-44 (`findOriginalFile`), flat dataset matching uses `if baseName.startswith(patientID):`, whereas `extract_patient_id_from_name` (lines 110-126, used by `getAllPatientIDs` at ClassAnnotation.py:3530) splits on `[-_]`. Consequently, in a flat dataset with `patient1_CT.nrrd` (`patientID="patient1"`) and `patient10_CT.nrrd` (`patientID="patient10"`), `findOriginalFile(datasetPath, "patient1", False)` matches both files because `"patient10_CT".startswith("patient1")` is True. This causes `saveSingleCSV` (line 2987) and `rebuildMultiFeatureFolders` (line 3653) to hash and copy `patient10`'s files into `patient1`'s folder. This is a major soundness bug for flat datasets.

### D5. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, minor)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **real: yes, minor**: A grep over ClassAnnotation found no network, subprocess, pip install, eval/exec, or pickle use. The only exec hits are Qt dialog.exec() calls at 669 and 1261. The code has no telemetry, downloads or concealed behavior. The only safety-adjacent issues are unsanitized rmtree paths limited to the module's output folder (D1, D3). These are ordinary bugs without a concrete path to harm. My rating is minor, not blocking. I did not read every line of the 3850-line file.
- gpt on re-check: **rating blocking**: The inspected source has concrete data-loss paths: ClassAnnotation/ClassAnnotation.py:3620-3623 includes `shutil.rmtree(featureDir, ignore_errors=True)` on the feature-name-derived path; lines 3718-3723 remove unrelated class-like folders; and line 2394 calls `slicer.mrmlScene.Clear(0)` during classification. These warrant a blocking safety rating. I inspected the relevant module, utilities, build files and repository-wide security-pattern search; I could not run Slicer, resolve the exact commit independently, or inspect external dependencies.
- gemini on re-check: **rating minor**: Checked ClassAnnotation/ClassAnnotation.py (lines 430-470, 750-800, 1125-1195, 2361-2400, 2790-3000, 3500-3750) and ClassAnnotation/ClassAnnotationLib/ClassAnnotationUtils.py (lines 1-126). There is no malicious behavior, network transmission, or unsafe code execution. The file deletion behaviors in D1 (`rebuildMultiFeatureFolders` lacking `..` sanitization) and D3 (`cleanupSingleClassFolders` regex in `output/`), as well as `slicer.mrmlScene.Clear(0)` in D2, are real but minor edge cases within the extension's workflow and `output/` directory rather than blocking safety vulnerabilities.


## Findings from some reviewers

### Datasets under paths containing `output` are excluded from file lookup
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`ClassAnnotation/ClassAnnotationLib/ClassAnnotationUtils.py:31`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/ClassAnnotationLib/ClassAnnotationUtils.py#L31): If a user selects a dataset under a parent such as /data/output-study, every walked root contains `output`, so no originals are found for copying or hashing even though the images can be displayed and labeled.
  ```
          for root, _, files in os.walk(datasetPath):
              if "output" in root:
                  continue
  ```
  Suggestion: Prune only the actual output directory by comparing normalized paths, rather than matching a substring in the full path.

### Duplicate dataset initialization in `onLoadDatasetClicked` after calling `loadDataset`
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote partly verified) [`ClassAnnotation/ClassAnnotation.py:1500`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/ClassAnnotation.py#L1500): In `onLoadDatasetClicked`, `self.loadDataset()` is called at line 1680 (which loads the CSV state, generates class buttons, and loads the first patient into the scene), and then lines 1693-1822 immediately repeat most of the dataset initialization (`reloadStateFromCSVs()`, `clearClassificationArea()`, `generateClassButtons()`/`generateMultiLabelClassButtons()`, etc.). In multi-label mode, `generateMultiLabelClassButtons()` clears the MRML scene and reloads the first patient a second time.
  ```
          self.loadDataset() 
  ...
          self.isFlat = self.logic.isFlatDataset(self.datasetPath)
          self.isHierarchical = self.logic.isHierarchicalDataset(self.datasetPath)
  ```
  Suggestion: Consolidate the dataset loading logic into `loadDataset()` and remove the duplicated initialization block in `onLoadDatasetClicked()`.

### Import modifies the shared Python module search path
minor; environment; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`ClassAnnotation/ClassAnnotation.py:15`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/ClassAnnotation.py#L15): Loading the extension prepends its library directory to Slicer's process-wide import path, making its generic helper module names available before other packages for all extensions, including users who never open this module.
  ```
  MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
  LIB_DIR = os.path.join(MODULE_DIR, "ClassAnnotationLib")
  
  
  
  if LIB_DIR not in sys.path:
  ```
  Suggestion: Use the ClassAnnotationLib package imports without modifying sys.path.

### Missing icon resource `Resources/Icons/pensil.png` in CMakeLists.txt
minor; packaging; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`ClassAnnotation/CMakeLists.txt:11`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/CMakeLists.txt#L11): In `ClassAnnotation/ClassAnnotation.py` (line 420), the multi-label UI loads `self.resourcePath("Icons/pensil.png")` for the label-renaming button (`pencil.setIcon(qt.QIcon(self.resourcePath("Icons/pensil.png")))`). However, `Resources/Icons/pensil.png` is not listed in `MODULE_PYTHON_RESOURCES` in `ClassAnnotation/CMakeLists.txt`, so it will not be copied into the installed package and the rename button will appear without an icon in packaged installations.
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/Icons/${MODULE_NAME}.png
    Resources/UI/${MODULE_NAME}.ui
    )
  ```
  Suggestion: Add `Resources/Icons/pensil.png` (and `ClassAnnotationLib/__init__.py` in `MODULE_PYTHON_SCRIPTS`) to `ClassAnnotation/CMakeLists.txt`.

### Registered Python test has no test implementation
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`ClassAnnotation/CMakeLists.txt:27`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/CMakeLists.txt#L27): The main script has no ClassAnnotationTest class or test methods, and the additional test registration is commented out. The configured test cannot exercise the annotation or file management workflows.
  ```
    # Register the unittest subclass in the main script as a ctest.
    # Note that the test will also be available at runtime.
    slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)
  ```
  Suggestion: Add a Slicer test class and regression tests for safe output handling and patient matching.

### Rename icon is not included in packaged resources
minor; packaging; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`ClassAnnotation/ClassAnnotation.py:418`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/ClassAnnotation.py#L418): The source contains this icon, but ClassAnnotation/CMakeLists.txt lists only ClassAnnotation.png and the UI file as resources. The installed extension can therefore show an empty rename button.
  ```
              # --- Pencil button (fixed right column) ---
              pencil = qt.QToolButton()
              pencil.setIcon(qt.QIcon(self.resourcePath("Icons/pensil.png")))
  ```
  Suggestion: Add Resources/Icons/pensil.png to MODULE_PYTHON_RESOURCES.

### `onClassCountChanged` reads unused `self.classificationData` instead of `self.singleClassification`
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`ClassAnnotation/ClassAnnotation.py:1378`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/ClassAnnotation.py#L1378): `onClassCountChanged` checks `self.classificationData.values()` to prevent reducing the number of classes below an already assigned class index, whereas single-label classifications are actually stored in `self.singleClassification` (`self.classificationData` remains empty). As a result, `existingClasses` is always empty and the guard never triggers when lowering the spinbox value.
  ```
      def onClassCountChanged(self):
          """Check if the number of classes is lower than the highest existing class and generate a warning."""
          
          minRequiredClasses = 2  
  
          existingClasses = [c for c in self.classificationData.values() if c is not None]
  ```
  Suggestion: Inspect `self.singleClassification.values()` (filtering out `"DUPLICATE"` and non-integers, as done in `onLoadDatasetClicked` at lines 1726-1729) instead of `self.classificationData.values()`.

### `blinkTimer` is not stopped in a widget `cleanup()` method
info; soundness; raised by gemini
- **gemini** (info, medium confidence, quote verified) [`ClassAnnotation/ClassAnnotation.py:74`](https://github.com/lorenaromeo/SlicerClassAnnotation/blob/f2db4d2b6b2a626a7318aa50359fb01cb2538a1d/ClassAnnotation/ClassAnnotation.py#L74): `ClassAnnotationWidget` starts `self.blinkTimer` (every 300 ms) whenever a patient is loaded in the table, and does not implement `cleanup()` to stop the timer when the module widget is destroyed or reloaded. Stopping the timer in `cleanup()` avoids timer callbacks firing on deleted Qt items.
  ```
          self.blinkTimer = qt.QTimer() 
          self.blinkTimer.timeout.connect(self.toggleBlink)
  ```
  Suggestion: Implement `def cleanup(self):` on `ClassAnnotationWidget` and call `self.blinkTimer.stop()`.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read the catalog entry, both CMake files, the helper libraries, the README and LICENSE, and grepped the 3850-line ClassAnnotation.py. I did not read that file in full. I found no network access, no package installation, no subprocess, eval or exec, and no telemetry. File operations are local: CSV writes, copying images into an output folder, and deleting class or patient folders under that folder. The licence is MIT, and the CMake lists every Python file and resource the module loads. The issues are non-blocking. findOriginalFile skips any path containing "output". Class names are only partly sanitised before being used in rmtree paths. Hash errors are swallowed silently. There are no real tests. The catalog entry tracks the moving "main" branch.

### Gemini 4 Argon (`google/gemini-4-argon`): minor issues
ClassAnnotation is a clean, self-contained scripted module for manual single-label and multi-label classification of medical imaging datasets. It has no external dependencies, performs no network requests, and is licensed under the MIT License. All file writes and directory cleanups are scoped to the `output/` folder inside the user-chosen dataset or output directory. Only minor non-blocking issues were found: `Resources/Icons/pensil.png` is missing from `ClassAnnotation/CMakeLists.txt`, `onClassCountChanged` checks an unused dictionary (`self.classificationData`), and `onLoadDatasetClicked` duplicates work already performed by `loadDataset()`. 🟢 Recommend merge.
Not checked: External Google Drive video tutorial linked in README.md was not fetched or inspected.; Runtime execution of the UI in 3D Slicer was not performed (static code review only).
Questions for the author: Did you intend to include `Resources/Icons/pensil.png` in `ClassAnnotation/CMakeLists.txt` so the multi-label rename button icon is installed in packaged builds?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
Several operations can destroy unrelated user data: renaming a feature to `..` can recursively delete the output directory, cleanup deletes matching pre-existing folders, and routine actions clear the whole Slicer scene. Flat datasets can also be grouped and copied under the wrong patient. These are concrete safety issues that require fixes. 🔴 Do not merge yet: fix the destructive file and scene operations before admission.
Not checked: Could not run Slicer, configure or build the extension, or execute the tests; only static file inspection was available.; Could not independently resolve the catalog's moving main reference to the supplied commit or compare against a previous revision.; The complete 3,850-line module was searched and relevant sections inspected, but not every line was read; the linked video tutorial and external resources were not accessed.; No catalog submission checklist or CI results were available.


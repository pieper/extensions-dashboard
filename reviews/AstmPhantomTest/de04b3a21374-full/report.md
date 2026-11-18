# AI review: AstmPhantomTest

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/Atracsys/SlicerAstmPhantomTest.git at commit `de04b3a2137407f38eff5f468a1331975a364b5e`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-18T03:18:58Z; cost $1.07

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | ok | concern |
| packaging | unknown | ok | minor |
| license | unknown | ok | ok |
| soundness | unknown | minor | concern |
| utility | unknown | ok | minor |
| **overall** | minor issues | minor issues | needs fixes |

## What each reviewer says the extension does

- **claude**: Slicer scripted module that guides an operator through the ASTM F2554 tracking-system accuracy tests. It uses a phantom and pointer, with transforms streamed over OpenIGTLink from a Plus server. It records measurements and writes JSON and HTML reports for tracker users such as Atracsys customers.
- **gemini**: AstmPhantomTest is a 3D Slicer module that guides operators through performing spatial tracking system accuracy and precision evaluations according to the ASTM F2554-22 standard using a calibrated divot phantom and tracked pointer connected via OpenIGTLink (PLUS Toolkit). It provides 3D visual guidance for working-volume placement, single-point, rotation, and multi-point distance tests, and generates HTML and JSON statistical reports.
- **gpt**: AstmPhantomTest guides operators through ASTM F2554 tracking-system accuracy and precision tests using a tracked phantom and pointer. It consumes OpenIGTLink transforms and produces measurement data and an HTML report.

## Disagreements (start here)

### D1. Existing scene nodes are deleted by name without checking ownership
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTestClasses/Phantom.py:28`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTestClasses/Phantom.py#L28): Opening the module initializes Phantom and removes the first existing node named phantCalibTransfo, even if it belongs to the user's current scene. Unsaved transform data can be lost. Similar name-based deletion occurs for model and connector nodes.
  ```
      # Detects if a transfo node with the same name is already present
      prevTransfoNode = slicer.mrmlScene.GetFirstNodeByName('phantCalibTransfo')
      # if so, remove it
      if prevTransfoNode:
        slicer.mrmlScene.RemoveNode(prevTransfoNode)
      # Create the transfo node
  ```
  Suggestion: Keep references to nodes created by this module and remove only those it owns; let Slicer assign unique names when existing nodes conflict.
- claude on re-check: **real: yes, minor**: Phantom.py:29-34 removes the first node named 'phantCalibTransfo' and Phantom.py:61-63 removes 'PhantomModel'. Pointer.py:79, WorkingVolume.py:120,180 and AstmPhantomTest.py:262-264 do the same for other nodes. The names are specific to this module, so it is unlikely to hit unrelated user data. It would only remove a stale node from an earlier run of this module, or a user node that happens to share the name. This is an ordinary robustness issue, not a concrete path to harm, so not blocking.
- gpt on re-check: **real: yes, blocking**: AstmPhantomTest/AstmPhantomTest.py:124-137,152 and 914-918 show that choosing the output folder initializes Phantom; AstmPhantomTest/AstmPhantomTestClasses/Phantom.py:28-34 says exactly: "    prevTransfoNode = slicer.mrmlScene.GetFirstNodeByName('phantCalibTransfo')" and "      slicer.mrmlScene.RemoveNode(prevTransfoNode)". No ownership check is made. A same-named unsaved node in the user's scene can be removed; this is a concrete data-loss path. Similar name-based removal occurs for models and PointerConnector (Pointer.py:76-79; AstmPhantomTest.py:261-264).
- gemini on re-check: **real: yes, minor**: Checked AstmPhantomTest/AstmPhantomTestClasses/Phantom.py:28-34 and 60-63, Pointer.py:76-79, WorkingVolume.py:118-120 and 178-180, and AstmPhantomTest/AstmPhantomTest.py:262-264. The module removes existing MRML nodes with specific internal names ('phantCalibTransfo', 'PhantomModel', 'PointerModel', 'SimpPhantomModel', 'TrackerModel', 'PointerConnector') before recreating them. While deleting by name instead of keeping node references is poor Slicer practice, these are specific module-internal node names in a dedicated phantom testing workflow, not a blocking safety issue.

### D2. Acquisition checks pointer status but not phantom-relative transform status
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified, other lines) [`AstmPhantomTest/AstmPhantomTestClasses/Pointer.py:183`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTestClasses/Pointer.py#L183): After the initial connection check, a pointer-to-phantom update is accepted based only on PointerToTracker status. If the phantom is missing while the pointer remains tracked, an invalid or stale relative transform can enter the acquisition queue and affect measured points; the red status display does not itself halt acquisition. This is non-blocking correctness feedback.
  ```
    @vtk.calldata_type(vtk.VTK_STRING)
    def onPtrRefTransformModified(self, caller, event=None, calldata=None):
      if self.ptrTransfoNode.GetAttribute("TransformStatus") == "OK":
        # update current matrix
        self.ptrRefMat = slicer.util.arrayFromTransformMatrix(self.ptrRefTransfoNode)
  ```
  Suggestion: Require valid status for the phantom and relative transforms as well, and abort or pause an active acquisition on tracking loss.
- claude on re-check: **real: yes, minor**: Pointer.py:205 checks self.ptrTransfoNode's TransformStatus inside onPtrRefTransformModified. It does not check ptrRefTransfoNode, which is the transform actually read on line 207. The status of the phantom-relative transform is therefore not validated there. I did not trace the handling of a missing phantom elsewhere, so the actual impact on acquisition is unconfirmed. It is a correctness weakness, not a safety issue.
- gpt on re-check: **real: yes, major**: Pointer.py:203-212 says "    if self.ptrTransfoNode.GetAttribute(\"TransformStatus\") == \"OK\":" and "      self.pq.push(self.pos())"; lines 237-256 then accumulate and emit samples without checking relative or phantom status. AstmPhantomTest.py:771-794 checks all three only for initial startup, subsequently showing status through the border. If relative-transform events continue while the phantom is missing, stale or invalid data can affect an accuracy measurement; exact behavior depends on the tracker stream. This is non-blocking correctness feedback.
- gemini on re-check: **real: yes, major**: Checked AstmPhantomTest/AstmPhantomTestClasses/Pointer.py:203-207 and AstmPhantomTest/AstmPhantomTest.py:734-794. In onPtrRefTransformModified, it checks `if self.ptrTransfoNode.GetAttribute("TransformStatus") == "OK":` instead of checking `self.ptrRefTransfoNode.GetAttribute("TransformStatus") == "OK"` (or both). If PointerToPhantom is MISSING while PointerToTracker is OK, stale/invalid relative transforms can be processed.

### D3. Session log captures unrelated Slicer logs and remains attached
partial; category safety; raised by gemini, gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gemini** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:121`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L121): When the module widget is initialized (`setup`), it immediately blocks on a modal `QFileDialog.exec()`, resizes and maximizes the Slicer main window (lines 73-75), attaches a `FileHandler` to the root Python logger (`logging.getLogger().addHandler(fh)`) without removing it on cleanup, and starts an OpenIGTLink client connector on the default localhost port (`self.cnode.Start()`). Furthermore, if the user cancels the file dialog (`self.saveDialog.exec()` returns 0), `self.logic`, UI signal connections, and the OpenIGTLink connector are never initialized, leaving the module UI in a broken/unresponsive state for the rest of the Slicer session.
  ```
      self.saveDialog = qt.QFileDialog()
      self.saveDialog.setFileMode(qt.QFileDialog().DirectoryOnly)
  
      if self.saveDialog.exec():
        # Path where the ouput files (including the log) will be saved
        savePath = self.saveDialog.selectedFiles()[0]
  ```
  Suggestion: Avoid blocking modal dialogs, root logger mutations, and main window resizing inside `setup()`. Provide a directory selector widget (e.g., `ctkDirectoryButton`) in the module UI to choose the output folder and start the session explicitly.
- **gpt** (major, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:127`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L127): The handler is attached to the process-wide root logger and is not retained or removed in cleanup. INFO-and-higher records from other modules that propagate to the root can therefore be written to the selected session folder even after the user leaves this module, potentially exposing other session information in a shared report directory.
  ```
        # The log file doesn't overwrite itself and is named after the date,
        # so any use of this module on a same day will be logged in the same file
        fh = logging.FileHandler(savePath + "/AstmPhantomTest_log_" + datetime.now().strftime("%Y.%m.%d") + ".log")
        fh.setLevel(logging.INFO)
        logging.getLogger().addHandler(fh)
        logging.info(f"Save path set to {savePath}")
  ```
  Suggestion: Use a module-specific logger and remove and close its handler when the session or widget ends; describe the contents of the output log.
- claude on re-check: **real: yes, minor**: AstmPhantomTest.py:121-131 shows a modal QFileDialog.exec() in setup(). It then adds a FileHandler to the root logger (line 131) and never removes it. Everything else from line 134 onward, including logic creation and UI connections, sits inside `if self.saveDialog.exec():`. If the user cancels, the module is left half-initialized. The log goes to a folder the user chose and the level is INFO, so this is not a safety problem. It is a soundness and side-effect issue. Setup() also maximizes the main window (lines 73-75).
- gpt on re-check: **real: yes, major**: AstmPhantomTest.py:124-132 attaches a file handler to the root logger: "      fh.setLevel(logging.INFO)" and "      logging.getLogger().addHandler(fh)". The handler is local, while cleanup at 796-800 only calls "    self.removeObservers()" and exit at 807-810 has no teardown. Thus other propagating log records can persist in the selected directory after switching modules, potentially disclosing sensitive information if shared. The dialog cancellation also skips logic and signal initialization (124-136,162-169). The code starts a connector at 261-270, but its actual default mode/address was not verified; no assumption of a localhost client is needed for this finding.
- gemini on re-check: **real: yes, minor**: Checked AstmPhantomTest/AstmPhantomTest.py:73-75, 121-132, 267-270, and 796-800. In setup(), the widget resizes/maximizes the main window, opens a modal QFileDialog, adds a FileHandler to the root logger (`logging.getLogger().addHandler(fh)`) that is never removed in cleanup(), starts an OpenIGTLink connector, and leaves `self.logic` uninitialized if the dialog is canceled. Writing root logger messages to the user-selected local save directory is a soundness/cleanup flaw, not a blocking safety issue.

### D4. Similarity calibration scales the reference distances used in accuracy results
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTestClasses/Phantom.py:193`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTestClasses/Phantom.py#L193): Similarity registration permits scale as well as rigid alignment. The resulting transform is applied to all CMM ground-truth points, and the scaled points are subsequently used for multi-point distance comparisons; a tracker scale error can therefore be partly absorbed into the reference and underreported. This is non-blocking correctness feedback.
  ```
      ldmkTransfo = vtk.vtkLandmarkTransform()
      ldmkTransfo.SetSourceLandmarks(ptsFrom)
      ldmkTransfo.SetTargetLandmarks(ptsTo)
      ldmkTransfo.SetModeToSimilarity()
      ldmkTransfo.Update()
      transfoMat = ldmkTransfo.GetMatrix()
  ```
  Suggestion: Use rigid registration for the physical phantom reference, or justify and validate scaling separately and compare distances against the original CMM geometry.
- claude on re-check: **real: yes, minor**: Phantom.py:196 uses SetModeToSimilarity(), which allows scaling. Lines 201-205 apply the fitted transform to all ground-truth points. Scale error in the tracker can therefore be partly absorbed into the reference. This may be a deliberate design choice, and I could not verify the ASTM method's intent. It is a methodological point, not a defect that blocks anything.
- gpt on re-check: **real: yes, major**: Phantom.py:190-205 fits CMM points to acquired points with "    ldmkTransfo.SetModeToSimilarity()" and then "      self.calGtPts[k] = np.array([p1[0], p1[1], p1[2]])". AstmPhantomTest.py:1249-1265 passes these points to the distance measurement, which computes "      gtDist = Dist(self.gtPts[kp[0]], self.gtPts[kp[1]])" and "      errors.append(abs(gtDist - ptrDist))" (Measurements.py:218-224). A fitted scale can therefore absorb a tracker scale error and reduce reported distance errors. This is non-blocking correctness feedback.
- gemini on re-check: **real: yes, major**: Checked AstmPhantomTest/AstmPhantomTestClasses/Phantom.py:185-206, AstmPhantomTest/AstmPhantomTest.py:1250-1279, and AstmPhantomTest/AstmPhantomTestClasses/Measurements.py:218-225. `Phantom.calibrate()` uses `ldmkTransfo.SetModeToSimilarity()` (allowing isotropic scaling) and transforms `self.gtPts` into `self.calGtPts`. `self.calGtPts` is then passed to `distMeasurement.fullReset` / `setGtPts` and used in `updateDistStats` to compute ground-truth pairwise distances `gtDist = Dist(self.gtPts[kp[0]], self.gtPts[kp[1]])`, scaling the ground-truth reference distances instead of using rigid registration or unscaled CMM coordinates `Phantom.gtPts`.

### D5. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **real: yes**: My search found no pip_install, subprocess, os.system, urllib or requests, and no pickle, eval or exec. ast.literal_eval is used only on module-generated strings. The only network use is an OpenIGTLink client connector (AstmPhantomTest.py:267-270), which is part of the tracker workflow and sends no data out. Name-based node removal and the root-logger file handler are ordinary robustness issues, not harm paths. I did not audit the license or the other files in full.
- gpt on re-check: **rating blocking**: Safety rating: blocking because the scene-node deletion in Phantom.py:28-32 ("      slicer.mrmlScene.RemoveNode(prevTransfoNode)") can destroy unrelated unsaved scene data; it occurs after output-folder selection and initialization (AstmPhantomTest.py:124-152,914-918). Root-logger persistence at AstmPhantomTest.py:129-131 and 796-800 adds a privacy concern. I inspected the source file list, imports, build scripts and searched for network, execution and file operations; actual connector defaults, external dependencies, runtime behavior and independent commit verification were not available.
- gemini on re-check: **rating ok**: Checked all Python files in AstmPhantomTest/ and AstmPhantomTest/AstmPhantomTestClasses/. There is no malicious behavior, unauthorized network transmission (only local OpenIGTLink connector on default localhost), command injection, or user file destruction. Note: `ast.literal_eval` is used only on internal VTK event calldata strings, and the salted SHA-256 hash in AstmPhantomTest.py:640-645 only unlocks UI developer shortcut buttons (`hackCollapsibleButton`).

### D6. Rating of environment
rating dispute; category environment; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (concern, ok)**
Ratings: claude unknown, gemini ok, gpt concern
- claude on re-check: **real: yes, minor**: I found no package installation. There are some global side effects when the module widget opens: it resizes and maximizes the main window (AstmPhantomTest.py:73-75), registers a custom layout, hides the box and axis labels on all view nodes (lines 105-108), and adds a root-logger FileHandler (line 131). These only happen when the user opens the module, not at Slicer startup or import. They are minor.
- gpt on re-check: **rating concern**: Environment rating: concern. On module setup, AstmPhantomTest.py:129-131 uses "      logging.getLogger().addHandler(fh)" and cleanup at 796-800 only has "    self.removeObservers()", so process-wide logging continues to be redirected into the chosen folder after leaving. Setup also changes the shared main window and layout (73-75,98-108). I inspected imports, CMake and searched for pip installation, sys.path and environment changes; none were found in the available source. These effects are triggered on opening the module, not merely installing it; runtime and external dependency behavior were not checked.
- gemini on re-check: **rating ok**: Checked AstmPhantomTest/AstmPhantomTest.py:1-15 and AstmPhantomTest/AstmPhantomTestClasses/*.py. Nothing is installed via pip, no global environment variables or package pins are modified at import/startup. Window resizing, layout switching, and root logger handler attachment happen only in `AstmPhantomTestWidget.setup()` when the user opens the module, not at module import or Slicer startup.


## Findings from some reviewers

### Typo `msgBoxsgBox` raises NameError when point acquisition collects no samples
minor; soundness; raised by gemini, gpt
- **gemini** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTestClasses/Pointer.py:279`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTestClasses/Pointer.py#L279): In `Pointer.staticTimerCallback`, when no samples were collected during the point-acquisition timer duration, the code instantiates `msgBox` but then references `msgBoxsgBox` on the next three lines, raising a `NameError` instead of displaying the warning dialog to the user.
  ```
            if np.size(self.coordAccumulator,0) == 0:
              msgBox = qt.QMessageBox()
              msgBox.setText("No sample taken during timer duration for point acquisition. Restart module and try again with increased duration.")
              msgBoxsgBox.setIcon(qt.QMessageBox().Warning)
              msgBoxsgBox.setStandardButtons(qt.QMessageBox().Ok)
              msgBoxsgBox.exec()
  ```
  Suggestion: Replace `msgBoxsgBox` with `msgBox` on lines 282-284.
- **gpt** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTestClasses/Pointer.py:279`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTestClasses/Pointer.py#L279): If a timed acquisition receives no samples, the misspelled variable raises NameError instead of displaying the recovery instructions. This is non-blocking correctness feedback.
  ```
          if np.size(self.coordAccumulator,0) == 0:
            msgBox = qt.QMessageBox()
            msgBox.setText("No sample taken during timer duration for point acquisition. Restart module and try again with increased duration.")
            msgBoxsgBox.setIcon(qt.QMessageBox().Warning)
            msgBoxsgBox.setStandardButtons(qt.QMessageBox().Ok)
            msgBoxsgBox.exec()
  ```
  Suggestion: Use msgBox consistently and reset the acquisition state so the operator can retry.

### Uninstalled working volume preset and large committed STL/GIF assets
info; packaging; raised by gemini
- **gemini** (info, high confidence, quote verified) [`AstmPhantomTest/CMakeLists.txt:9`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/CMakeLists.txt#L9): The repository commits two large binary STL meshes (`phantom2018_RAS.stl` at 10 MB and `phantom2022_RAS.stl` at 13 MB) and three large animated GIFs in `readme_img/` (6-8 MB each), and `AstmPhantomTest/CMakeLists.txt` omits `Resources/wv/PolarisVegaExt_ftk500Locs.txt` from `RESOURCES_FILES` so that working-volume preset is not installed in packaged builds.
  ```
  set(RESOURCES_FILES
    Resources/gt/phantom.txt
    Resources/models/ftk250_RAS.stl
    Resources/models/ftk500_RAS.stl
    Resources/models/phantom2018_RAS.stl
    Resources/models/phantom2022_RAS.stl
  ```
  Suggestion: Add `Resources/wv/PolarisVegaExt_ftk500Locs.txt` to `RESOURCES_FILES` in `AstmPhantomTest/CMakeLists.txt` if it is intended to be selectable in packaged builds, and consider simplifying or decimating the visual phantom STL meshes.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read the module, helper classes, CMake files, license and sample resources. I found no malicious behavior, network exfiltration, package installation or unsafe deserialization. Data is written only to a user-chosen folder. The CMake files install what the module imports, and the dependencies match. The license is the Slicer BSD-style license. Findings are non-blocking: a hidden password-gated developer mode that can fake calibration, target hits and skipped tests in a tool meant to produce standards-compliance data; a NameError bug in an error path; a modal folder dialog at module setup that leaves the module half-initialised if cancelled; and global side effects on the main window and root logger. The source is on the `master` branch, so I could not verify an exact revision. Recommend merge, with the suggestions as non-blocking.
Not checked: 
<parameter name="0">The 10–13 MB STL models, GIFs, WAV files and the .ui file were not read.
Questions for the author: 
<parameter name="0">Is the hashed dev operator ID intended to remain in the released extension? If so, will use of the shortcuts be recorded in the report?

### Gemini 4 Argon (`google/gemini-4-argon`): minor issues
AstmPhantomTest is a well-documented IGT extension for evaluating tracking system accuracy and precision under the ASTM F2554-22 standard using OpenIGTLink/PLUS. The extension is safe, self-contained, and permissively licensed under the 3D Slicer license, with matching CMake and catalog dependencies (`SlicerOpenIGTLink`). A couple of non-blocking soundness issues were identified: a `msgBoxsgBox` variable name typo in `Pointer.py` when zero samples are acquired, and modal file dialog / main-window resizing / root logger handler side effects inside `AstmPhantomTestWidget.setup()`. 🟢 Recommend merge.
Not checked: Binary contents of AstmPhantomTest/Resources/models/phantom2018_RAS.stl (10 MB) and AstmPhantomTest/Resources/models/phantom2022_RAS.stl (13 MB); Runtime hardware testing with a live Plus Server / OpenIGTLink tracker stream
Questions for the author: Should `Resources/wv/PolarisVegaExt_ftk500Locs.txt` be listed in `AstmPhantomTest/CMakeLists.txt` under `RESOURCES_FILES` so it is installed with the package?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
Opening the module can remove pre-existing, potentially unsaved scene nodes solely because their names match its own. Its process-wide log handler also captures unrelated application logs beyond the session. Non-blocking correctness concerns include accepting measurements when the phantom transform is invalid and scaling the reference geometry during calibration. The supplied catalog points to a moving branch; its resolution and an actual build were not independently verified. 🔴 Do not merge yet: fix the unintended scene-node deletion and address the cross-module logging exposure.
Not checked: No code was executed; Slicer runtime behavior, build and automated tests were not verified.; The supplied commit identifier and the current resolution and accessibility of the catalog's master branch could not be independently verified with the available tools.; The two large phantom STL files and other binary assets were not inspected; their independent provenance and any third-party licensing were not verified.; OpenIGTLink and Plus Toolkit implementation and network security were not inspected.; No previous catalog entry, prior reviewed commit, PR checklist or CI results were available for comparison.


# AI review: DeformView

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/elisedl1/SlicerDeformView.git at commit `7ca647fe4d6550c5fa07939d3e10f7da8431dd17`
- Context: pull request 2371 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-21T01:01:49Z; cost $0.69

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | ok | ok | blocking |
| environment | ok | ok | minor |
| packaging | minor | ok | unknown |
| license | ok | ok | ok |
| soundness | minor | minor | concern |
| utility | ok | ok | minor |
| **overall** | minor issues | minor issues | needs fixes |

## What each reviewer says the extension does

- **claude**: DeformView is a scripted Slicer module that turns a transform node into dense displacement-magnitude and Jacobian (volume change) volumes. It adds interactive overlays, a hover readout and an incremental-transform slider. It is aimed at registration researchers and image-guided surgery work.
- **gemini**: DeformView is a 3D Slicer scripted module for researchers and clinicians that provides dense, quantitative voxel-wise visualization of non-linear registration deformation fields. Given a moving image, fixed image, and transformation, it computes and overlays displacement magnitude (mm) and Jacobian determinant (% volumetric change) maps with interactive cursor readout and incremental transform scaling.
- **gpt**: DeformView generates displacement-magnitude and local-volume-change maps from registration transforms in 3D Slicer. It is intended for researchers and other users interpreting non-linear deformation and registration results.

## Disagreements (start here)

### D1. Opening the module removes any scene node named JacobianMap
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DeformView/DeformView.py:235`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L235): During widget setup, removeAllNamedNode is called on a generic name. Its implementation at lines 688–707 removes every matching node without checking its class or ownership, so an unrelated unsaved image, segmentation, or other scene node named JacobianMap is deleted simply by opening DeformView.
  ```
          self.enableVTKErrorTracking()
  
          self.cleanupDuplicateColorNodes("JacobianMap")
          self.removeAllNamedNode("JacobianMap")
  
          self.resetBuiltInColorNodes()
  ```
  Suggestion: Manage only color nodes created by this extension, using a unique ownership attribute or stored node reference; never remove arbitrary same-named scene nodes.
- claude on re-check: **real: yes, minor**: DeformView.py:237-238 calls removeAllNamedNode('JacobianMap'); lines 683-707 collect all nodes by name (any class) and RemoveNode them. Real, but the name is the extension's own color-map name, so a collision requires a user node deliberately named JacobianMap. Not a concrete blocking harm; a minor soundness issue.
- gpt on re-check: **real: yes, blocking**: DeformView/DeformView.py:121-123 says setup is called on first opening; lines 237-238 call `self.cleanupDuplicateColorNodes("JacobianMap")` and `self.removeAllNamedNode("JacobianMap")`. Lines 688 and 700-707 use `allNodes = slicer.mrmlScene.GetNodesByName(nodeName)`, append every result, then `slicer.mrmlScene.RemoveNode(node)` without a class or ownership check. An unrelated unsaved node with that exact name can be lost merely by opening the module.
- gemini on re-check: **real: yes, minor**: In DeformView/DeformView.py:238, `self.removeAllNamedNode("JacobianMap")` is called during widget setup. In lines 683-707, `removeAllNamedNode` retrieves `slicer.mrmlScene.GetNodesByName(nodeName)` and removes every matching node from the scene regardless of node class (`vtkMRMLColorTableNode` vs other nodes). However, because it only affects nodes literally named "JacobianMap" (the exact name used by this module's custom color node at line 715), the practical risk of accidental user data loss is low; it is a minor soundness/cleanup bug rather than a blocking safety vulnerability.

### D2. Recomputing maps can overwrite a previous result volume
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DeformView/DeformView.py:2191`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L2191): After a new computation, onLoadDisplacementVolume selects the first matching scene volume rather than the newly created one. Lines 2233–2253 then copy the newly computed array into that selected volume: if an older result has the same voxel count, its data is silently overwritten; if counts differ, the assignment can fail. This also applies to Jacobian maps when loaded.
  ```
          # Find the volume by suffix
          scene = slicer.mrmlScene
          for i in range(scene.GetNumberOfNodesByClass("vtkMRMLScalarVolumeNode")):
              node = scene.GetNthNodeByClass(i, "vtkMRMLScalarVolumeNode")
              if node.GetName() and suffix in node.GetName():
                  selectedVolume = node
  ```
  Suggestion: Keep explicit references to the newly computed output nodes and only restore arrays to their corresponding nodes after checking geometry; never select writable outputs by name substring.
- claude on re-check: **real: yes, minor**: Lines 2191-2197 break on the first scalar volume whose name contains the suffix, which is the oldest if results exist. Lines 2233-2255 write the stored full array into it with numpy_scalars[:] = ..., so a same-size older result is overwritten or a size mismatch raises. Real ordinary bug affecting only derived output volumes (names are built at 3246/3353), not a safety issue.
- gpt on re-check: **real: yes, blocking**: DeformView/DeformView.py:2073-2094 creates new maps and saves copies of their arrays; lines 2143-2145 call `self.onLoadDisplacementVolume(flag=0)`. Lines 2193-2197 select the first scalar node whose name contains the suffix, and lines 2233-2239 assign `numpy_scalars[:] = self._fullDisplacementArray`. Thus an older or unrelated suffix-matching volume can be silently overwritten, including one with different geometry but equal scalar count; incompatible array sizes can instead fail. Lines 2245-2251 do the analogous Jacobian assignment when loaded. This is unintended destruction of existing scene data, not merely an incorrect display.
- gemini on re-check: **real: yes, minor**: In DeformView/DeformView.py:2084-2145, computing maps creates new volumes via `AddNewNodeByClass`, stores their voxel arrays in `self._fullDisplacementArray` and `self._fullJacobianArray` (lines 2090-2095), and then calls `self.onLoadDisplacementVolume(flag=0)` (line 2145). In `onLoadDisplacementVolume` (lines 2192-2197), it loops over `vtkMRMLScalarVolumeNode` in the scene and picks the first node matching `_displacementMagnitude` or `_jacobianMagnitude` by substring, then copies `self._fullDisplacementArray` or `self._fullJacobianArray` into `selectedVolume` (lines 2233-2255). If an earlier computed result volume exists in the scene, it matches first and gets overwritten (or raises a broadcast ValueError if dimensions differ). This is a real logic bug affecting the module's own generated output volumes, making it a minor/major soundness issue rather than a blocking safety issue.

### D3. Increment slider changes the user's shared input transform
single; category soundness; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`DeformView/DeformView.py:1262`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L1262): Changing the slider alters the selected transform itself rather than a display-only copy. Other scene nodes using this transform are also changed, and saving the scene while it is at an intermediate setting may preserve an unintended registration; selecting 0% actually applies 0.0001 rather than zero.
  ```
          # Apply the scale to the transform (updates spatial positions)
          bsplineTransform.SetDisplacementScale(scale)
          transformNode.Modified()
  ```
  Suggestion: Apply scaling to an extension-owned transform or resampled display copy, preserving the user's original transform and its prior scale.
- claude on re-check: **real: yes, minor**: Lines 1262-1264 call SetDisplacementScale on the parameter node's transform in place, and 0 maps to 0.0001 (1219-1220). Load at 2223-2230 resets to 1.0. This is the tool's intended interactive behavior, though it mutates the user's transform node. Soundness minor.
- gpt on re-check: **real: yes, major**: DeformView/DeformView.py:370 connects `self.ui.incrementalSlider.valueChanged.connect(self.onIncrementalChanged)`; lines 1217-1224 read the selected parameter-node transform and substitute `scale = 0.0001` for zero. Lines 1262-1264 call `bsplineTransform.SetDisplacementScale(scale)` and `transformNode.Modified()` on that shared node. Other nodes using the supported transform change too, and an intermediate state can be saved. Severity is major for unintended effects on shared registration state, not a blanket clinical-harm claim.
- gemini on re-check: **real: yes, minor**: In DeformView/DeformView.py:1218-1264, `onIncrementalSliderChanged` sets `scale = 0.0001` when `scale == 0`, gets `transformNode = self._parameterNode.transformNode` and `bsplineTransform = transformNode.GetTransformFromParent()`, and directly calls `bsplineTransform.SetDisplacementScale(scale)` and `transformNode.Modified()`. This mutates the selected transform node in place in the scene.

### D4. Replaces global VTK output window singleton when module UI is opened
single; category soundness; raised by gemini; outcome after cross-examination: **real, major (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`DeformView/DeformView.py:454`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L454): When `DeformViewWidget.setup()` runs, `enableVTKErrorTracking()` replaces Slicer's global `vtkOutputWindow` singleton with a default `vtkFileOutputWindow()`. This redirects all subsequent VTK warnings and errors across the entire Slicer session away from Slicer's error log into a local file in the current working directory.
  ```
          # Add observer to VTK output window
          errorObserver = vtk.vtkFileOutputWindow()
          vtk.vtkOutputWindow.SetInstance(errorObserver)
  ```
  Suggestion: Remove `enableVTKErrorTracking()` or do not replace the global `vtk.vtkOutputWindow` instance.
- claude on re-check: **real: yes, major**: Lines 455-456 create a vtkFileOutputWindow and call vtkOutputWindow.SetInstance, called from setup() at line 235. This replaces the global output window, so VTK messages go to a log file (default vtkMessageLog.log) instead of Slicer's error log for the whole session. The errorCallback returned is never used. It is a global side effect, but not harmful to data.
- gpt on re-check: **real: yes, major**: DeformView/DeformView.py:235 calls `self.enableVTKErrorTracking()` during setup; lines 454-456 create `errorObserver = vtk.vtkFileOutputWindow()` and call `vtk.vtkOutputWindow.SetInstance(errorObserver)`. This replaces a process-global VTK output instance and risks interfering with other modules' diagnostics; the callback is not attached here. The repository code alone does not establish the default filename, that every message reaches a local file, or exactly how Slicer's error log behaves in the targeted VTK build.
- gemini on re-check: **real: yes, major**: In DeformView/DeformView.py:235, `setup()` calls `self.enableVTKErrorTracking()`. At lines 454-456, `enableVTKErrorTracking()` creates `errorObserver = vtk.vtkFileOutputWindow()` and calls `vtk.vtkOutputWindow.SetInstance(errorObserver)`, replacing Slicer's global VTK output window singleton for the entire process.

### D5. Temporary transform files remain on disk when saving or reading fails
severity dispute; category safety; raised by claude, gpt; outcome after cross-examination: **real, info (3 of 3)**
- **claude** (info, medium confidence, quote verified) [`DeformView/DeformView.py:3219`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L3219): The temp .h5 file is removed only on the success path. If saveNode or ReadTransform raises, the file stays in the temp folder.
  ```
  slicer.util.saveNode(transformNode, tmpPath)
  
          # Read into SimpleITK
          itkTx = sitk.ReadTransform(tmpPath)
  
          # Clean up
  ```
  Suggestion: Wrap the calls in try/finally, or use a TemporaryDirectory.
- **gpt** (major, high confidence, quote verified) [`DeformView/DeformView.py:3215`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L3215): Removal at line 3225 is reached only after a successful read. A save or read error leaves the potentially patient-related registration transform in the system temporary directory indefinitely; the Jacobian and incremental paths have the same pattern.
  ```
          # Write computed transform to temporary .h5 file
          with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp:
              tmpPath = tmp.name
  
          slicer.util.saveNode(transformNode, tmpPath)
  
  ```
  Suggestion: Use a finally block or a temporary directory context to remove every temporary transform on success and failure, and check saveNode's return value.
- claude on re-check: **real: yes, info**: Lines 3216-3225, 3311-3320 and 3471-3478 create a NamedTemporaryFile(delete=False) and remove it only after a successful read (no try/finally). Leftover files occur only on error, and the file lives in the OS temp dir, so the impact is small.
- gpt on re-check: **real: yes, minor**: DeformView/DeformView.py:3215-3225 creates a `NamedTemporaryFile(suffix=".h5", delete=False)`, calls `slicer.util.saveNode(transformNode, tmpPath)` and `sitk.ReadTransform(tmpPath)`, and only then calls `os.remove(tmpPath)`, without a finally block. The same pattern appears at lines 3311-3320 and 3471-3478. A failed save/read can leave an empty, partial or complete patient-related transform in the system temp directory until externally cleaned; actual identifiers, permissions and indefinite persistence are not established. Use finally cleanup.
- gemini on re-check: **real: yes, info**: In DeformView/DeformView.py:3216-3225 (and similarly in `computeJacobianVolume` and incremental sequence creation), `tempfile.NamedTemporaryFile(suffix=".h5", delete=False)` is used and `os.remove(tmpPath)` is called without a `try...finally` block. If `saveNode` or `sitk.ReadTransform` raises an exception, the `.h5` file remains in the user's local system temp directory. Leaving a temp file in the local OS temp folder on exception is a minor cleanup issue, not a major safety risk.

### D6. cleanup() removes all observers from the shared vtkMRMLCrosshairNode
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`DeformView/DeformView.py:1934`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L1934): In `DeformViewWidget.cleanup()`, calling `crosshairNode.RemoveAllObservers()` removes all observers on the shared crosshair node, not just the observer added by `DeformView` (which is already removed via `self.crosshairObserverTag` immediately above). This can break other Slicer modules or built-in components (such as DataProbe) that observe crosshair movements.
  ```
          crosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
          if crosshairNode:
              crosshairNode.RemoveAllObservers()
  ```
  Suggestion: Remove the `crosshairNode.RemoveAllObservers()` call and rely solely on `self.crosshairNode.RemoveObserver(self.crosshairObserverTag)`.
- **gpt** (minor, high confidence, quote verified) [`DeformView/DeformView.py:1934`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L1934): The crosshair is shared by Slicer and other modules. Removing all its observers on cleanup can disable unrelated crosshair-dependent behavior, including during module reload.
  ```
          crosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
          if crosshairNode:
              crosshairNode.RemoveAllObservers()
              # print("Removed all crosshair observers")
  ```
  Suggestion: Remove only observer tags registered by DeformView.
- claude on re-check: **real: yes, minor**: Lines 1934-1936 call RemoveAllObservers() on the first vtkMRMLCrosshairNode in cleanup, after the module's own observer was removed at 1929-1932. This can drop other observers on a shared node. Real, but it only happens on cleanup or reload and is a soundness issue.
- gpt on re-check: **real: yes, minor**: DeformView/DeformView.py:1916-1918 identifies widget cleanup; lines 1929-1932 remove the module's own tagged observer. Lines 1934-1936 then get the shared node and call `crosshairNode.RemoveAllObservers()`, including observers owned by other components. This can disrupt their crosshair-dependent behavior on widget destruction or reload; a particular component failure is not demonstrated. Remove only owned observer tags.
- gemini on re-check: **real: yes, major**: In DeformView/DeformView.py:1929-1936, `cleanup()` already removes `self.crosshairObserverTag` from `self.crosshairNode`, and then fetches the shared `vtkMRMLCrosshairNode` and calls `crosshairNode.RemoveAllObservers()`, stripping observers registered by Slicer core (e.g. DataProbe) or other modules.

### D7. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude ok, gemini ok, gpt blocking
- claude on re-check: **real: no, info**: I found no network access, downloads, exec/eval or data exfiltration in the examined code. The issues are ordinary bugs: node removal by name, temp-file cleanup, and global VTK output window and crosshair observer handling. None gives a concrete path to serious harm, so safety is ok or at most minor. The blocking rating is overstated. I did not audit every file.
- gpt on re-check: **rating blocking**: Safety is blocking based on verified unintended scene data loss and corruption, not on a demonstrated data exfiltration. DeformView/DeformView.py:237-238 calls `self.removeAllNamedNode("JacobianMap")`; lines 688-707 remove every exact-name match regardless of ownership. Lines 2193-2197 and 2233-2239 also select an existing suffix-matching scalar volume and overwrite its array. I inspected these paths and searched for network, execution and file-deletion APIs; I could not run Slicer or independently verify the exact source revision or external payloads.
- gemini on re-check: **rating ok**: Inspected DeformView/DeformView.py around all reported items. There is no malicious behavior, network communication, unsafe deserialization, or arbitrary user file destruction. The issues raised under safety by gpt (D1 removing nodes named 'JacobianMap', D2 overwriting previously computed `_displacementMagnitude` volumes in the scene, D5 leaving a `.h5` file in temp on error) are ordinary module correctness/cleanup bugs without a concrete path to serious harm.


## Findings from some reviewers

### Increment slider supports fewer transforms than the documented workflow suggests
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DeformView/DeformView.py:1238`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L1238): The module accepts general transform nodes, but the GUI disables incremental scaling when the underlying transform lacks this method. The README describes the slider without this restriction, and the analytic incremental test exercises a separate logic method rather than this UI path.
  ```
          # Check if it has SetDisplacementScale method
          if not hasattr(bsplineTransform, 'SetDisplacementScale'):
              transformType = bsplineTransform.GetClassName()
              
              slicer.util.warningDisplay(
                  f"Incremental Scaling Not Supported\n\n"
  ```
  Suggestion: Document the restriction or implement the slider for the other accepted transform types; add a GUI-path test.

### Orphaned display node created in scene on every volume load
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DeformView/DeformView.py:2274`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L2274): Each call to `onLoadDisplacementVolume` creates a new display node in the MRML scene via `AddNewNodeByClass`, then immediately overwrites the `internalDisplayNode` variable with `persistentDisplayNode`, leaving an orphaned, unused display node in the scene every time a volume is loaded.
  ```
          persistentDisplayNode = selectedVolume.GetDisplayNode()
  
          internalDisplayNode = slicer.mrmlScene.AddNewNodeByClass(persistentDisplayNode.GetClassName())
  
          #internalDisplayNode.Copy(persistentDisplayNode)
          internalDisplayNode = persistentDisplayNode
  ```
  Suggestion: Remove the unused `slicer.mrmlScene.AddNewNodeByClass(persistentDisplayNode.GetClassName())` call.

### Repository size exceeds 100 MB guideline
minor; packaging; raised by claude
- **claude** (minor, low confidence, quote no quote) no file cited: The automated scan reports 233 MB. The visible binary files total about 10 MB, so the bulk is probably git history or large images. This slows cloning for the index build.
  Suggestion: Check for large files in the history. Move the figures to releases or shrink them.

### Reset Window/Level button handler expects a volume node instead of a clicked(bool) signal argument
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DeformView/DeformView.py:301`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L301): `resetWindowLevelButton`'s `clicked(bool)` signal passes a boolean (`False`) as the first argument to `onResetWindowLevel(self, volumeNode)`. When `self.defaultWindow` and `self.defaultLevel` are set, `onResetWindowLevel` calls `volumeNode.GetDisplayNode()` on `False`, raising `AttributeError: 'bool' object has no attribute 'GetDisplayNode'`. Note also that `self.defaultWindow` and `self.defaultLevel` are never assigned (only `self.defaultWindow_DisplacementMag` / `self.defaultWindow_Jacobian` are assigned), so clicking the button currently re-runs `initializeWindowLevelControls` instead of resetting as intended.
  ```
          self.ui.resetWindowLevelButton.connect('clicked(bool)', self.onResetWindowLevel)
  ```
  Suggestion: Change `onResetWindowLevel` to accept `checked=False` and retrieve `volumeNode = self.ui.loadedTransformVolume.currentNode()`, and check `self.defaultWindow_DisplacementMag` rather than `self.defaultWindow`.

### Typo in windowLevelFlagUpdate assigns defaultLevel_Jacobian to window
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DeformView/DeformView.py:2763`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/DeformView.py#L2763): In `windowLevelFlagUpdate`, when `flag == 1` (Jacobian), `window` is assigned `self.defaultLevel_Jacobian` instead of `self.defaultWindow_Jacobian`.
  ```
          elif flag == 1: #Jacobian
              window = self.defaultLevel_Jacobian
              level = self.defaultLevel_Jacobian
  ```
  Suggestion: Use `window = self.defaultWindow_Jacobian`.

### Unused generated PyQt5 UI file and dev script shipped in module folder
minor; packaging; raised by claude, gemini
- **claude** (minor, high confidence, quote verified) [`DeformView/Resources/UI/DeformView_ui.py:11`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/Resources/UI/DeformView_ui.py#L11): Resources/UI/DeformView_ui.py imports PyQt5. It is not installed by CMake and is not imported by the module, so it is harmless in the built extension. It is stale pyuic output (with an absolute path to the author's machine) and would fail if anyone imported it in Slicer.
  ```
  from PyQt5 import QtCore, QtGui, QtWidgets
  ```
  Suggestion: Delete the file from the repository.
- **gemini** (info, high confidence, quote verified) [`DeformView/Resources/UI/DeformView_ui.py:11`](https://github.com/elisedl1/SlicerDeformView/blob/7ca647fe4d6550c5fa07939d3e10f7da8431dd17/DeformView/Resources/UI/DeformView_ui.py#L11): `DeformView/Resources/UI/DeformView_ui.py` is an unused `pyuic5`-generated file importing `PyQt5` and `DeformView/DeformView_shift_check.py` is a standalone console helper script. Neither is installed by CMake or imported by the module, and the repository git history may also contain large historical blobs (automated check noted 233 MB repo size, though the working tree is ~7.5 MB). Cleaning up unused generated files and any large historical git objects is recommended.
  ```
  from PyQt5 import QtCore, QtGui, QtWidgets
  ```
  Suggestion: Remove the unused `DeformView/Resources/UI/DeformView_ui.py` file and prune any large unreferenced objects from git history if applicable.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I found no safety or environment problems. Searching DeformView.py for pip installs, subprocess, network calls, eval/exec and pickle returned nothing. The module uses only Slicer-bundled packages (numpy, SimpleITK, vtk, qt), and temporary .h5 files are written and removed. The MIT license is present. The catalog entry is valid, has no build dependencies, and points to the 'main' branch, which is allowed. CMake installs DeformView.py, DeformViewTesting.py and the resources the module needs. Remaining points are non-blocking: the scan reports a repository size of 233 MB, a stray PyQt5-generated UI file is shipped but not installed or used, and DeformView.py is a very large single file. Documentation and analytic self-tests are good. I did not read all 3,700 lines of DeformView.py. Recommend merge.
Not checked: Most of DeformView.py (about 3,700 lines) was only searched by pattern, not read in full; Whether the repository size is caused by git history; Actual build and load of the extension in Slicer; Whether the 'main' branch tip differs from the commit 7ca647fe that I was given

### Gemini 4 Argon (`google/gemini-4-argon`): minor issues
DeformView is a well-documented and thoroughly validated scripted extension for computing and visualizing dense displacement magnitude (mm) and Jacobian determinant (%) maps from deformation fields in 3D Slicer. It meets all three admission requirements: it is safe (no network calls, telemetry, or unsafe execution), clearly licensed under the MIT License, and has a valid catalog entry and CMake configuration. A few non-blocking soundness issues in `DeformViewWidget` should be addressed in future updates, notably avoiding replacing the global `vtk.vtkOutputWindow` singleton during widget setup and avoiding `crosshairNode.RemoveAllObservers()` in `cleanup()`.

🟢 Recommend merge
Not checked: Git commit history size (automated hint noted 233 MB repository size, whereas the checked-out files total ~7.5 MB); Binary image files exampleImages/main_UI.png and paper/figures/UI_overview.png
Questions for the author: Why is the git repository ~233 MB when the working tree files total ~7.5 MB? Were large sample volumes committed and later deleted in git history?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The extension has useful documentation and analytic tests, but opening it can remove unrelated scene nodes, and recomputing maps can overwrite earlier results. Both are concrete data-loss risks. Temporary transform files can also remain after errors. 🔴 Do not merge yet: fix the scene-data loss and complete revision verification.
Not checked: Could not run Slicer, build the extension, or execute the analytic or UI tests.; Could not independently access the remote repository, resolve main to the supplied commit 7ca647fe4d6550c5fa07939d3e10f7da8431dd17, inspect a prior revision, or check CI results.; Could not verify the reported 233 MB repository size or inspect unavailable binary images and repository history.; The large main module was searched and relevant sections read, but not every line was independently audited; external dependencies and payloads were not fetched. The PyQt5 import is in an uninstalled generated UI file, while the installed module loads the .ui resource directly.


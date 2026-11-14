# AI review: DeformView

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/elisedl1/SlicerDeformView.git at commit `8260b331c57d7d692957482e80bcbb19b86f3eb9`
- Context: pull request 2371 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-14T17:28:31Z; cost $1.02

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | concern | concern |
| packaging | unknown | ok | unknown |
| license | unknown | ok | ok |
| soundness | unknown | minor | concern |
| utility | unknown | ok | minor |
| **overall** | minor issues | minor issues | needs fixes |

## What each reviewer says the extension does

- **claude**: DeformView is a Slicer scripted module that turns a transform node (linear, grid, B-spline, thin-plate spline or composite) into dense displacement-magnitude and Jacobian volume-change volumes, shown as overlays with a hover readout and an incremental-application slider. It is aimed at registration researchers and image-guided surgery users.
- **gemini**: DeformView is a scripted 3D Slicer module for researchers and clinicians to quantitatively visualize and analyze non-linear registration deformation fields. It computes and displays dense voxel-wise displacement magnitude (mm) and Jacobian determinant (% volume change) maps as interactive color overlays with real-time cursor hover readouts and incremental transformation scaling.
- **gpt**: DeformView visualizes displacement magnitudes and local volume changes from registration transforms as voxel-wise overlays. It is intended for researchers and other Slicer users examining non-linear registration and tissue deformation.

## Disagreements (start here)

### D1. Compute and incremental slider mutate shared input scene nodes
single; category safety; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DeformView/DeformView.py:2065`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L2065): Compute discards the fixed/background volume's existing parent transform before calculations and later assigns the selected transform to it (line 2102), without restoring the prior relationship even if calculation fails. The slider also changes the shared input transform itself at lines 1262–1264, affecting any other nodes using it and potentially changing subsequently saved registration results.
  ```
              hoverWasEnabled = self.ui.enableHoverDisplayCheckbox.isChecked()
              
              #  NEW: Reset background volume to have no transform
              if self._parameterNode.backgroundVolume:
                  self._parameterNode.backgroundVolume.SetAndObserveTransformNodeID(None)
  ```
  Suggestion: Operate on module-owned copies or derived nodes, preserve the original parent transform, and avoid mutating the user-selected transform.
- claude on re-check: **real: yes, minor**: DeformView.py:2068-2069 clears the fixed volume's parent transform, and line 2102 assigns the selected transform to it. Line 1263 changes the transform's displacement scale, and 2110 resets it to 1. These are the module's intended visualization actions on the user-selected nodes. There is no data loss or exfiltration. Not a safety issue. At most it is a soundness or usability point, because the previous parent transform isn't restored.
- gpt on re-check: **real: yes, blocking**: DeformView/DeformView.py:2067-2069 says `self._parameterNode.backgroundVolume.SetAndObserveTransformNodeID(None)` before the computations at 2073-2085; 2098-2105 assigns the selected transform instead of restoring the original, including on success. If computation fails in between, the original link is already lost. Lines 1222-1224 and 1262-1264 say `bsplineTransform.SetDisplacementScale(scale)` and `transformNode.Modified()`: for supported transforms the slider edits the shared input, not a copy. This can change other scene objects and saved registration state without adequate disclosure; use copies and preserve/restore input relationships.
- gemini on re-check: **real: yes, major**: In DeformView/DeformView.py lines 2068-2070, onApplyButton calls `self._parameterNode.backgroundVolume.SetAndObserveTransformNodeID(None)` and later at line 2102 calls `self._parameterNode.backgroundVolume.SetAndObserveTransformNodeID(transformNode.GetID())`. Furthermore, at lines 1263-1264, `bsplineTransform.SetDisplacementScale(scale)` and `transformNode.Modified()` directly mutate the shared input transform node in the MRML scene. Under the rubric and AGENTS.md, mutating scene nodes selected by the user in a visualization module is a soundness/correctness issue (major), not a blocking malicious/safety vulnerability.

### D2. Opening the module deletes any scene node named JacobianMap
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DeformView/DeformView.py:235`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L235): During widget setup, removeAllNamedNode collects and removes every node with this name without checking its class, origin or ownership (lines 683–707). A user's existing volume, transform, markup or color node named JacobianMap is removed merely by opening the module, potentially losing unsaved scene data and references.
  ```
          self.enableVTKErrorTracking()
  
          self.cleanupDuplicateColorNodes("JacobianMap")
          self.removeAllNamedNode("JacobianMap")
  ```
  Suggestion: Keep references to extension-owned color nodes and remove only those created by this module; do not delete arbitrary nodes by name.
- claude on re-check: **real: yes, minor**: Line 238 calls removeAllNamedNode('JacobianMap'). Lines 683-707 remove every node with that name regardless of class. This is real, but the name is specific to this module's own colour node. A collision with a user node is unlikely, so it is a minor robustness bug and not a blocking safety issue.
- gpt on re-check: **real: yes, blocking**: DeformView/DeformView.py:121-122 identifies setup as first module opening, and 237-238 calls `self.removeAllNamedNode("JacobianMap")`. Lines 688 and 700-707 get all nodes by name and call `slicer.mrmlScene.RemoveNode(node)` on each without ownership or class filtering. An unrelated unsaved node with this exact name is removed just by opening the module, with possible loss of data and references; only remove nodes owned by the module.
- gemini on re-check: **real: yes, minor**: In DeformView/DeformView.py lines 237-238, `setup()` calls `self.cleanupDuplicateColorNodes("JacobianMap")` followed immediately by `self.removeAllNamedNode("JacobianMap")`. In `removeAllNamedNode` (lines 683-707), `slicer.mrmlScene.GetNodesByName(nodeName)` finds all nodes in the scene with that name regardless of node class and removes all of them (`slicer.mrmlScene.RemoveNode(node)`). Because "JacobianMap" is a specific internal name for its color table node (`createJacobianColorNode` at line 724), this is an ordinary bug in duplicate-color-node cleanup rather than a blocking safety issue.

### D3. Recomputing can overwrite an earlier or unrelated scene volume
single; category safety; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DeformView/DeformView.py:2191`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L2191): Compute creates a new map and calls this loader, which instead picks the first scene volume whose name contains the suffix. Lines 2233–2253 then copy the latest computed arrays into that selected volume. Recomputing after changing inputs can silently overwrite the old map or an unrelated matching user volume; different array sizes can instead raise an error.
  ```
          # Find the volume by suffix
          scene = slicer.mrmlScene
          for i in range(scene.GetNumberOfNodesByClass("vtkMRMLScalarVolumeNode")):
              node = scene.GetNthNodeByClass(i, "vtkMRMLScalarVolumeNode")
              if node.GetName() and suffix in node.GetName():
                  selectedVolume = node
  ```
  Suggestion: Load maps by the actual newly created node references or explicit user selection and never copy cached arrays into an independently selected node.
- claude on re-check: **real: yes, minor**: Lines 2191-2197 take the first scalar volume whose name contains the suffix. The module creates its outputs at lines 3246 and 3353 as referenceVolume name + suffix. After a recompute, the loader can pick an older output, and lines 2233-2253 then copy the new arrays into it. A size mismatch would raise an error, which tryWithErrorDisplay reports. This is a soundness bug, and it mostly affects module-generated volumes. It is not a safety issue.
- gpt on re-check: **real: yes, blocking**: DeformView/DeformView.py:3246-3255 creates a new output, but onApplyButton calls `self.onLoadDisplacementVolume(flag=0)` at 2143-2145. At 2193-2197 the loader takes the first scalar volume for which `suffix in node.GetName()`, and at 2233-2239 writes `numpy_scalars[:] = self._fullDisplacementArray` into it. Thus an earlier output or unrelated matching volume with compatible array size is silently modified, and incompatible arrays may raise; Jacobian follows the same pattern at 2245-2251. Use the actual output node rather than a name search to avoid destroying unsaved voxel data.
- gemini on re-check: **real: yes, major**: In DeformView/DeformView.py lines 3246-3250, `computeDisplacementMagnitude` always creates a new volume with `AddNewNodeByClass` ending in `_displacementMagnitude`. However, `onLoadDisplacementVolume` (lines 2191-2197) iterates over `vtkMRMLScalarVolumeNode` in the scene and picks the first one whose name contains `_displacementMagnitude` (or `_jacobianMagnitude`), and lines 2233-2255 overwrite that first matching volume's scalar array in-place (`numpy_scalars[:] = self._fullDisplacementArray`) with the newly computed array. If the user recomputes on a second volume, it overwrites the earlier volume's scalars (or raises a shape mismatch error). This is a major soundness bug, not a safety vulnerability.

### D4. Fixed image is transformed despite the UI describing it as stationary
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`DeformView/DeformView.py:779`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L779): The apply handler instead attaches the selected transform to backgroundVolume at line 2102 and displays it as the background. Thus the fixed image is moved even though the UI says it does not warp, potentially producing misleading overlays and interpretation.
  ```
          inputLayout.addRow("Moving Image:", self.ui.referenceVolume)
          inputLayout.addRow("Fixed Image:", self.ui.backgroundVolume)
          inputLayout.addRow("Transformation:", self.ui.transformNode)
          self.ui.referenceVolume.setToolTip(
              "The volume that is warped by the deformation field to match the fixed image."
          )
  ```
  Suggestion: Keep the fixed image in its original coordinate system and explicitly define and test the mapping grid and transform direction in an end-to-end GUI test.
- claude on re-check: **real: yes, minor**: The tooltip at lines 785-787 says the fixed image 'Does not warp'. Line 2102 attaches the transform to backgroundVolume. This is a real inconsistency between the UI text and the behavior. It may be intended for visualization, so it is a documentation or soundness issue and not a safety one.
- gpt on re-check: **real: yes, major**: DeformView/DeformView.py:779-786 labels `self.ui.backgroundVolume` Fixed Image and says `Does not warp.` Yet 2098-2105 executes `self._parameterNode.backgroundVolume.SetAndObserveTransformNodeID(transformNode.GetID())`, and 2136-2141 shows that volume as background. For nonidentity transforms the fixed image is moved, contrary to the UI, and overlays can be misleading. This is a serious correctness issue, separate from D1's destructive scene mutation; ordinary soundness feedback is non-blocking for admission.
- gemini on re-check: **real: yes, major**: In DeformView/DeformView.py lines 779-787, `referenceVolume` is labeled "Moving Image:" ("The volume that is warped by the deformation field to match the fixed image") and `backgroundVolume` is labeled "Fixed Image:" ("The reference volume that the moving image is registered to. Does not warp."). Yet in `onApplyButton` at line 2102, the transform is applied to `self._parameterNode.backgroundVolume.SetAndObserveTransformNodeID(transformNode.GetID())`, warping the Fixed Image in the slice views.

### D5. Hover sampling ignores the displayed volume's parent transform
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`DeformView/DeformView.py:1644`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L1644): The cursor RAS position is in world coordinates, but the volume's local RAS-to-IJK matrix does not invert its parent transform. The apply handler assigns a transform to the displacement map at line 2105, so with a non-identity parent the hover value can come from the wrong voxel or be reported out of bounds.
  ```
          # convert RAS to IJK
          rasToIjk = vtk.vtkMatrix4x4()
          displacementVolume.GetRASToIJKMatrix(rasToIjk)
          ijk = [0.0, 0.0, 0.0, 1.0]
          ras_hom = list(ras) + [1.0]
          rasToIjk.MultiplyPoint(ras_hom, ijk)
  ```
  Suggestion: Transform the cursor world position into the volume's local coordinates before applying RAS-to-IJK, or keep the output in world coordinates; test a translated and non-linear parent transform.
- claude on re-check: **real: yes, minor**: Lines 1644-1650 use the volume's local RAS-to-IJK matrix with a world-coordinate cursor position. Line 2105 assigns a parent transform to the displacement volume. The hover location is therefore offset by the local transform. The label can be slightly wrong, which is a soundness bug of limited impact.
- gpt on re-check: **real: yes, major**: DeformView/DeformView.py:1627-1628 gets cursor RAS, while 1644-1649 uses `displacementVolume.GetRASToIJKMatrix(rasToIjk)` and directly multiplies the cursor position without converting world RAS into volume-local RAS. Lines 1652-1658 then bounds-check and sample the resulting index. The computed displacement volume is assigned the selected transform at 2104-2105, so nonidentity parent transforms can cause wrong hover values or blank labels. This is a serious non-blocking correctness issue.
- gemini on re-check: **real: yes, major**: In DeformView/DeformView.py lines 1644-1650, hover sampling converts the crosshair world RAS coordinates to IJK using only `displacementVolume.GetRASToIJKMatrix(rasToIjk)`, without accounting for the parent transform that `onApplyButton` attaches to `displacementVolume` at line 2105 (`displacementVolume.SetAndObserveTransformNodeID(transformNode.GetID())`). When the parent transform is non-identity, world RAS does not match the volume's local RAS coordinates.

### D6. Module setup replaces Slicer's global vtkOutputWindow singleton
partial; category environment; raised by gemini, gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`DeformView/DeformView.py:454`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L454): When DeformViewWidget.setup() runs, enableVTKErrorTracking() replaces VTK's global singleton vtkOutputWindow with a new unconfigured vtkFileOutputWindow instance. This breaks Slicer's application-wide VTK error and warning logging for the rest of the session across all modules, and causes VTK to write a default output file in the current working directory. Note also that errorCallback defined in that method is never attached as an observer.
  ```
          # Add observer to VTK output window
          errorObserver = vtk.vtkFileOutputWindow()
          vtk.vtkOutputWindow.SetInstance(errorObserver)
  ```
  Suggestion: Remove enableVTKErrorTracking() and the call to vtk.vtkOutputWindow.SetInstance(), or use standard Slicer logging without replacing the global VTK output window singleton.
- **gpt** (major, high confidence, quote verified) [`DeformView/DeformView.py:454`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L454): Opening the module installs a process-wide file output window, replacing Slicer's existing VTK output handler for other modules; cleanup does not restore it. VTK diagnostics can be redirected away from the normal application handler for the remainder of the session.
  ```
          # Add observer to VTK output window
          errorObserver = vtk.vtkFileOutputWindow()
          vtk.vtkOutputWindow.SetInstance(errorObserver)
  ```
  Suggestion: Do not replace the global singleton; use scoped observers or preserve and restore the original output window.
- claude on re-check: **real: yes, major**: Lines 455-456 create a vtkFileOutputWindow and call vtkOutputWindow.SetInstance on it. Line 235 calls this from setup(). The errorCallback returned at line 459 is never attached. This replaces the process-wide VTK output handler and is never restored. It happens when the module widget is opened, not at import. It is a real global side effect that can redirect VTK diagnostics for the rest of the session. It is a should-fix environment issue and not a safety block.
- gpt on re-check: **real: yes, major**: DeformView/DeformView.py:235 calls tracking from setup; 442-459 defines `errorCallback` but creates `errorObserver = vtk.vtkFileOutputWindow()` and calls `vtk.vtkOutputWindow.SetInstance(errorObserver)` without attaching the callback. Cleanup at 1916-1941 and exit at 1965-1971 do not restore the previous output window. The process-wide replacement can redirect diagnostics from Slicer's usual handler for the rest of the session. A specific default output filename or write was not independently verified.
- gemini on re-check: **real: yes, major**: In DeformView/DeformView.py lines 235 and 442-456, `setup()` calls `self.enableVTKErrorTracking()`, which executes `errorObserver = vtk.vtkFileOutputWindow()` and `vtk.vtkOutputWindow.SetInstance(errorObserver)`. This replaces Slicer's process-wide VTK output window singleton for the entire session when the module is opened.

### D7. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **real: no, info**: I found no network access, pip installs, subprocess calls, downloads, unsafe deserialization or credentials in the code. The only exec( hit is in DeformView_shift_check.py:5, which looks like a stand-alone helper script. The items raised are ordinary bugs and side effects, with no concrete path to harm. My rating for safety is ok.
- gpt on re-check: **rating blocking**: Safety is blocking because DeformView/DeformView.py:237-238 calls `self.removeAllNamedNode("JacobianMap")`, whose implementation removes every name match at 688-707, risking loss of unrelated unsaved data. Independent destructive paths are the input transform changes at 2067-2069 and 2098-2105, and the array overwrite at 2193-2197 and 2233-2239. I inspected those paths, setup, cleanup, relevant calculation and output code, and searched the available repository for downloads, process execution, and removal APIs; this is not a complete execution or dependency audit. The supplied snapshot is identified as 8260b331c57d, but its revision and remote catalog source could not be independently verified with these tools. 🔴 Do not merge yet: fix unintended scene-data deletion and overwriting.
- gemini on re-check: **rating ok**: Checked DeformView/DeformView.py for safety issues. Temp file handling in `computeDisplacementMagnitude` / `computeJacobianMagnitude` uses `tempfile.NamedTemporaryFile(suffix=".h5", delete=False)` and removes it (lines 3216-3225). There are no network calls, unsafe deserialization, command execution, or malicious behaviors. The issues flagged by gpt under safety (D1, D2, D3) are ordinary MRML scene state management / correctness bugs, which AGENTS.md explicitly notes should not be labeled as blocking safety issues.


## Findings from some reviewers

### Incremental slider is restricted to B-spline transforms
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DeformView/DeformView.py:1238`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L1238): Grid, linear and other transforms can be used for maps but cannot use this advertised increment feature. README.md lines 76–79 describes the slider without this restriction, while the independent incremental logic tested in DeformViewTesting.py is not called by this slider.
  ```
          # Check if it has SetDisplacementScale method
          if not hasattr(bsplineTransform, 'SetDisplacementScale'):
              transformType = bsplineTransform.GetClassName()
              
              slicer.util.warningDisplay(
                  f"Incremental Scaling Not Supported\n\n"
  ```
  Suggestion: Document the restriction or implement and test GUI incremental visualization for the other supported transform types.

### Module setup resets and renames built-in Slicer color table nodes
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DeformView/DeformView.py:593`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L593): When DeformViewWidget.setup() runs, resetBuiltInColorNodes() removes and re-adds all default Slicer color nodes, and create_colour_node() renames built-in Slicer color table nodes (e.g. renaming 'vtkMRMLColorTableNodeFileColdToHotRainbow.txt' from 'ColdToHotRainbow' to 'Hot-To-Cold Rainbow'). Any code or user workflow relying on standard built-in color node names may be affected.
  ```
          existing_node = slicer.mrmlScene.GetNodeByID(f'{node_ID}')
          if existing_node:
              existing_node.SetName(name_str)
              # CRITICAL FIX: Set the attribute even on existing nodes
              existing_node.SetAttribute("MyColourMaps", "1")
  ```
  Suggestion: Avoid removing/re-adding default color nodes or renaming Slicer's built-in color nodes in-place; if custom display names are desired, either clone the color nodes or use their standard names.

### Orphan display node leaked into MRML scene on each volume load
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DeformView/DeformView.py:2274`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L2274): Every time onLoadDisplacementVolume is called, AddNewNodeByClass creates an orphan display node in the MRML scene that is immediately overwritten by internalDisplayNode = persistentDisplayNode and never used or removed.
  ```
          persistentDisplayNode = selectedVolume.GetDisplayNode()
  
          internalDisplayNode = slicer.mrmlScene.AddNewNodeByClass(persistentDisplayNode.GetClassName())
  
          #internalDisplayNode.Copy(persistentDisplayNode)
          internalDisplayNode = persistentDisplayNode
  ```
  Suggestion: Remove the unused slicer.mrmlScene.AddNewNodeByClass(persistentDisplayNode.GetClassName()) call and the redundant AddAndObserveDisplayNodeID call.

### Reset Window/Level button handler has mismatched signature and uninitialized state attributes
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DeformView/DeformView.py:300`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L300): The QPushButton clicked(bool) signal passes a boolean (the checked state, False) as the first argument to onResetWindowLevel(self, volumeNode). When self.defaultWindow and self.defaultLevel are set, onResetWindowLevel calls volumeNode.GetDisplayNode() on the bool argument, raising AttributeError: 'bool' object has no attribute 'GetDisplayNode'. Furthermore, self.defaultWindow and self.defaultLevel are initialized to None in setup() and never updated (initializeWindowLevelControls sets self.defaultWindow_DisplacementMag and self.defaultWindow_Jacobian instead), so clicking the button currently only re-runs initializeWindowLevelControls and returns early.
  ```
          # Connect reset button
          self.ui.resetWindowLevelButton.connect('clicked(bool)', self.onResetWindowLevel)
  ```
  Suggestion: Accept clicked: bool = False in onResetWindowLevel, retrieve selectedVolume = self.ui.loadedTransformVolume.currentNode() inside the method, and check self.defaultWindow_DisplacementMag / self.defaultWindow_Jacobian instead of self.defaultWindow.

### Typo in windowLevelFlagUpdate assigns defaultLevel_Jacobian to window
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DeformView/DeformView.py:2763`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L2763): In windowLevelFlagUpdate, when flag == 1 (Jacobian), window is assigned self.defaultLevel_Jacobian instead of self.defaultWindow_Jacobian. Additionally, in initializeWindowLevelControls (lines 2625-2628), level_jacobian and window_jacobian are hardcoded to 1.0 instead of centering at 0.0 with a symmetric window (2.0 * maxAbsValue, which is commented out).
  ```
          elif flag == 1: #Jacobian
              window = self.defaultLevel_Jacobian
              level = self.defaultLevel_Jacobian
  ```
  Suggestion: Use self.defaultWindow_Jacobian for window, and verify whether defaultLevel_Jacobian should be 0.0 and defaultWindow_Jacobian should be 2.0 * maxAbsValue.

### cleanup() removes all observers from shared vtkMRMLCrosshairNode singleton
minor; soundness; raised by gemini, gpt
- **gemini** (minor, high confidence, quote verified) [`DeformView/DeformView.py:1934`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L1934): In cleanup(), calling crosshairNode.RemoveAllObservers() removes all observers on the shared singleton crosshair node, not just the observer added by DeformView (which was already removed on lines 1929-1932). This can break other modules or Slicer components observing the crosshair node.
  ```
          crosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
          if crosshairNode:
              crosshairNode.RemoveAllObservers()
  ```
  Suggestion: Remove the crosshairNode.RemoveAllObservers() call and rely only on removing self.crosshairObserverTag.
- **gpt** (minor, high confidence, quote verified) [`DeformView/DeformView.py:1934`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView/DeformView.py#L1934): When this widget is cleaned up, all observers on the shared crosshair node are removed, including callbacks owned by Slicer or other extensions. Those features may stop reacting to cursor updates after a module reload or cleanup.
  ```
          crosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
          if crosshairNode:
              crosshairNode.RemoveAllObservers()
  ```
  Suggestion: Remove only observer tags registered by DeformView.

### Repository git history contains ~233 MB of data and unused pyuic5-generated file
info; packaging; raised by gemini
- **gemini** (info, medium confidence, quote verified) [`DeformView.json:6`](https://github.com/elisedl1/SlicerDeformView/blob/8260b331c57d7d692957482e80bcbb19b86f3eb9/DeformView.json#L6): The automated repository scan notes that the git repository size is ~233 MB (exceeding the 100 MB guideline), although the working tree at commit 8260b331c57d7d692957482e80bcbb19b86f3eb9 is only ~9.7 MB, indicating large files were committed in earlier git history. Also, DeformView/Resources/UI/DeformView_ui.py (which imports PyQt5) and DeformView/DeformView_shift_check.py are unused files in the repository that are not installed by CMake.
  ```
    "scm_revision": "main",
    "scm_url": "https://github.com/elisedl1/SlicerDeformView.git",
  ```
  Suggestion: Consider cleaning large historical blobs from git history if practical, and removing the unused DeformView/Resources/UI/DeformView_ui.py file.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I found no malicious or concealed behavior. In DeformView.py I searched for pip installs, subprocess, network access, eval/exec and pickle and found none. The only file I/O is a temporary .h5 transform written and removed, plus a user-selected tag file read. The MIT license is present. The CMake installs every module the code imports, and the catalog entry is valid, with a branch revision and no dependencies. The main concern is global side effects when the module widget is first opened. It replaces VTK's global output window and resets Slicer's default color nodes. It also deletes every scene node named "JacobianMap". The 233 MB repository size flagged by the scan is above the 100 MB limit, and I could not verify it. Minor leftovers include stale placeholder text and unused files.
Not checked: Most of DeformView.py (about 3,700 lines) was only searched for risky patterns, not read line by line.; I did not run the self-tests or load the module in Slicer.; I could not verify the repository size or what causes it.; I did not verify that the main branch tip equals commit 8260b33.; I did not read the .ui file, the paper bibliography, or the workflow draft-pdf.yml.

### Gemini 4 Argon (`google/gemini-4-argon`): minor issues
DeformView is a well-documented and thoroughly validated scripted module for visualizing non-linear deformation fields (voxel-wise displacement magnitude and Jacobian determinant maps). It meets all three admission requirements: it is safe with no network or file-system risks, is distributed under the MIT License, and has a valid, buildable CMake and catalog configuration (note that `DeformView_ui.py` which imports `PyQt5` is an unused file neither imported nor installed). One notable non-blocking issue in `DeformViewWidget.setup()` should be fixed soon: `enableVTKErrorTracking()` replaces Slicer's global `vtkOutputWindow` singleton with a bare `vtkFileOutputWindow`. Several minor UI/cleanup bugs are also noted.

🟢 Recommend merge
Not checked: Could not inspect exampleImages/main_UI.png (2 MB) and paper/figures/UI_overview.png (4 MB) contents directly, though they are documentation/screenshot PNG images not packaged into the extension binary.; Could not execute the build or run tests in a live 3D Slicer instance.
Questions for the author: In DeformView.py line 456, enableVTKErrorTracking() replaces Slicer's global vtkOutputWindow with a bare vtkFileOutputWindow; can this debugging leftover be removed so Slicer's error log continues working?; In initializeWindowLevelControls (lines 2625-2628) and windowLevelFlagUpdate (line 2764), Jacobian default window and level are both set to 1.0 instead of level 0.0 and symmetric window 2*maxAbsValue; was that intentional?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The source contains concrete scene-data destruction and modification risks: opening the module removes any node named JacobianMap, and recomputing can overwrite an earlier map with unrelated values. The module also modifies input transforms and replaces VTK’s global output window. The catalog uses a moving branch; its remote resolution and repository-size hint could not be verified. 🔴 Do not merge yet: prevent unintended scene data loss and modification, and verify the selected source and catalog build.
Not checked: No execution, Slicer build, GUI interaction, automated tests or CI results were available.; The remote repository, current main branch resolution and exact relationship to supplied commit 8260b331c57d7d692957482e80bcbb19b86f3eb9 could not be independently verified.; Repository history and the reported 233 MB size could not be measured; binary images were not inspected.; The entire 3,725-line module was not read line by line; targeted searches and relevant execution paths were inspected.; Submission checklist and index-side validation results were not provided.
Questions for the author: Can you provide the catalog CI/build results and verify the repository-size limit and the commit currently selected by main?


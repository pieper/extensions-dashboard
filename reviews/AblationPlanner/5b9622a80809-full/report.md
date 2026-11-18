# AI review: AblationPlanner

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/naterex23/SlicerAblationPlanner at commit `5b9622a808096cb2d1a7b14410c8b50b1b6f29a3`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-18T03:11:34Z; cost $0.51

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | ok | ok |
| packaging | unknown | ok | unknown |
| license | unknown | ok | ok |
| soundness | unknown | concern | concern |
| utility | unknown | ok | minor |
| **overall** | minor issues | minor issues | needs fixes |

## What each reviewer says the extension does

- **claude**: Slicer scripted module for planning ablation probe placement. Users place fiducial pairs to position copies of a vendor ablation-zone segmentation, then compute signed margin distances to a tumor segmentation using ModelToModelDistance. It is aimed at interventional radiology research.
- **gemini**: AblationPlanner is a 3D Slicer extension for planning and evaluating thermal or cryoablation procedures for tumors (such as kidney, liver, and lung lesions). It enables users to place virtual ablation probe profiles using fiducial endpoints, align pre-procedural tumor segmentations to intra-operative scans via fiducial registration, and compute tumor ablation margins using ModelToModelDistance.
- **gpt**: AblationPlanner lets Slicer users position theoretical ablation profiles around segmented tumors and estimate surface margins. It also supports landmark-based tumor alignment for research workflows.

## Disagreements (start here)

### D1. Generating probe lines deletes all line markups in the scene
single; category safety; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:298`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L298): Pressing Place Markup Line removes every line markup, including pre-existing measurements and annotations belonging to the user or other modules. The endpoint drag handler also calls onLineButton, so routine probe adjustment can silently destroy unsaved scene data without confirmation.
  ```
      lineNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
  
      if lineNodes is not None:
        for lineNode in lineNodes:
          slicer.mrmlScene.RemoveNode(lineNode)
  ```
  Suggestion: Track only lines created by this module using node references or a dedicated attribute, and update or remove only those lines.
- claude on re-check: **real: yes, major**: AblationPlanner.py:298-302 removes every vtkMRMLMarkupsLineNode in the scene with no confirmation or filtering. Line 462 calls onLineButton again after endpoint drags. Only in-memory scene nodes are removed, not files, and the user can recreate the lines. This is a real data-loss bug that should be fixed. I don't consider it a blocking safety issue, because it isn't malicious or exfiltrating.
- gpt on re-check: **real: yes, blocking**: AblationPlanner/AblationPlanner.py:298-302 obtains all scene line nodes and unconditionally removes them: `lineNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")` and `slicer.mrmlScene.RemoveNode(lineNode)`. The button is connected at line 159, and the endpoint interaction handler calls `self.onLineButton()` at line 462. Unrelated, unsaved line measurements can be lost without confirmation, even if subsequent line creation fails.
- gemini on re-check: **real: yes, major**: In AblationPlanner/AblationPlanner.py lines 298-302, onLineButton() fetches all vtkMRMLMarkupsLineNode instances from slicer.mrmlScene and removes them without filtering for nodes created by the module. Also, onMarkupEndInteraction() (line 462) calls self.onLineButton(). However, this is an ordinary MRML scene-node management bug (deleting MRML line markup nodes in the active Slicer scene rather than user filesystem files), so under the rubric and policy ("Do not label ordinary bugs as safety issues merely because the extension processes medical images"), it is a major soundness issue rather than a blocking safety vulnerability.

### D2. Applying margin colors overwrites signed distance data and revert is incomplete
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified, other lines) [`AblationPlanner/AblationPlanner.py:595`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L595): The color button replaces the model's Signed distance values with bin numbers rather than creating a separate display scalar. Revert iterates only to len(originalColorArray)-1, while the snapshot itself omits the final value, so at least one modified value is never restored; the original values are also kept only in widget memory. Subsequent use or saving of the model can therefore retain incorrect distance data.
  ```
          for j in range(0,len(args)):
              if (colorval < args[j]):
                  thresholded = True
                  VTKFieldDataArray.SetValue(i,j)
                  break
          if (not thresholded):
  ```
  Suggestion: Keep Signed unchanged, create a separate color-bin array, and test the full apply/revert and scene-reload workflow.
- claude on re-check: **real: yes, minor**: AblationPlanner.py:611-621 overwrites the 'Signed' array in place with bin indices. The snapshot (353-357) and the loops at 591/611/633 all stop at size-1, and the revert loop at 633 runs to len-1 over a list that is already one entry short. So the last two values are never restored. The snapshot is only in widget memory. It affects a derived margin model, not the user's source data, so I rate it minor.
- gpt on re-check: **real: yes, major**: AblationPlanner/AblationPlanner.py:367-376 calls `self.logic.changeColorsByMargin_(outputMarginModel,-10,-5,-2)` and later restores from `self.originalColorArray`. Lines 603-621 overwrite the `Signed` array with bin values, including `VTKFieldDataArray.SetValue(i,j)`. The snapshot at lines 351-359 and the recoloring loop at line 611 both omit the final element, but the restore at line 633 uses `range(0, len(originalColorArray)-1)`, omitting one additional element. Thus, for an array of at least two elements, the penultimate value remains binned after revert. This corrupts calculated distance data in the output model, not merely its appearance.
- gemini on re-check: **real: yes, major**: In AblationPlanner/AblationPlanner.py lines 604-621, changeColorsByMargin_() mutates the "Signed" array of the model's field data in-place with bin indices (0..num_regions). In onMarginButton() (lines 350-359), originalColorArray only records range(0, VTKFieldDataArray.GetSize()-1) in self.originalColorArray, and regenerateOriginalModelColors() (lines 633-636) only iterates over range(0, len(originalColorArray)-1). This is a real soundness defect, though it only affects the generated outputMarginModel and is minor/major in severity (major is reasonable since the distance array and table column on the output model are corrupted).

### D3. Parallel probe endpoints yield a singular rotation
single; category soundness; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:747`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L747): When a probe's endpoints are aligned or anti-aligned with the reference direction [0,0,-1], the cross product is zero and the rotation formula divides by zero. Probe placement can then fail or propagate non-finite transform values for an otherwise valid axis-aligned input.
  ```
      v = np.cross(a, b)
      c = np.dot(a, b)
      s = np.linalg.norm(v)
      kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
      rotationMatrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
      return rotationMatrix
  ```
  Suggestion: Handle parallel and antiparallel vectors explicitly, reject coincident endpoints, and test these cases.
- claude on re-check: **real: yes, minor**: AblationPlanner.py:747-751 divides by s**2 with no check for s==0. The reference direction is [0,0,-1] (line 435). A probe whose endpoints are exactly parallel or anti-parallel to it gives s=0, so the matrix becomes NaN or inf. This is a real edge-case bug, but it needs exactly axis-aligned input.
- gpt on re-check: **real: yes, major**: AblationPlanner/AblationPlanner.py:435 uses the reference endpoints `[0,0,0], [0,0,-1]`; lines 502-506 pass the normalized target vector into the rotation calculation. At lines 747-751, `v = np.cross(a, b)`, `s = np.linalg.norm(v)`, and `rotationMatrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))` give division by zero for parallel or antiparallel vectors. Lines 715-733 then use the resulting matrix in a transform and harden it. Axis-aligned placements can fail or yield non-finite geometry; actual runtime behavior was not tested.
- gemini on re-check: **real: yes, minor**: In AblationPlanner/AblationPlanner.py lines 740-752, rotationMatrixFromVectors(vec1, vec2) computes s = np.linalg.norm(v) where v = np.cross(a, b), and divides by (s ** 2) on line 751 without checking for s == 0 (when the probe vector is parallel or anti-parallel to [0, 0, -1]). This produces NaN/Inf in the rotation matrix for vertical probes.

### D4. Use of removed Slicer 4 Markups fiducial API methods
single; category soundness; raised by gemini; outcome after cross-examination: **still disputed**
- **gemini** (major, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:307`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L307): `vtkMRMLMarkupsNode.GetNthFiducialLabel()` was deprecated in Slicer 4 and removed in Slicer 5 (replaced by `GetNthControlPointLabel()`). Similarly, `GetNumberOfFiducials()` and `GetNthFiducialPosition()` used in `onProbeButton` (lines 413-428) are removed in Slicer 5. Calling `onLineButton` or `onProbeButton` in Slicer 5 will raise an `AttributeError`.
  ```
      for i in range(0,numNodePoints,2):
          fiducialLabel = endPointsMarkupsNode.GetNthFiducialLabel(i)        
          ras1 = vtk.vtkVector3d(0,0,0)
  ```
  Suggestion: Replace `GetNthFiducialLabel`, `GetNumberOfFiducials`, and `GetNthFiducialPosition` with `GetNthControlPointLabel`, `GetNumberOfControlPoints`, and `GetNthControlPointPosition`.
- claude on re-check: **real: no, info**: The EndPoints selector is restricted to vtkMRMLMarkupsFiducialNode (Resources/UI/AblationPlanner.ui:89). From memory, Slicer 5 still provides GetNumberOfFiducials, GetNthFiducialPosition and GetNthFiducialLabel on vtkMRMLMarkupsFiducialNode as legacy methods. I could not check the Slicer source, so this is not verified. The label at AblationPlanner.py:308 is unused anyway. The claim that these methods were removed and raise AttributeError is likely wrong.
- gpt on re-check: **real: unsure**: AblationPlanner/AblationPlanner.py:307-308 calls `fiducialLabel = endPointsMarkupsNode.GetNthFiducialLabel(i)`, and lines 413 and 427-428 call `GetNumberOfFiducials()` and `GetNthFiducialPosition(i, xyz[i])`. These legacy calls are verified, but the available repository does not establish whether the targeted Slicer 5 version retains compatibility wrappers. Slicer API source and runtime were unavailable, so removal and the asserted AttributeError could not be verified.
- gemini on re-check: **real: yes, major**: In AblationPlanner/AblationPlanner.py line 308 (endPointsMarkupsNode.GetNthFiducialLabel(i)) and lines 413, 416, 418, 419, 422, 427, 428 (GetNumberOfFiducials() and GetNthFiducialPosition()), the code calls legacy Slicer 4 Markups fiducial methods that were removed in Slicer 5 in favor of ControlPoint methods (which are already used on lines 305, 310, 313). Calling onLineButton or onProbeButton in Slicer 5 raises an AttributeError.

### D5. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **real: yes, minor**: I read AblationPlanner.py around lines 285-440 and 585-780. I also searched the repo for pip_install, urlopen, requests and subprocess and found nothing. I saw no network access, no code downloads, no eval or exec, and no data leaving the machine. The only safety-adjacent issue is D1, the deletion of all line markups in the scene. That is a data-loss bug, not a malicious or exfiltration issue. I rate safety minor, because that deletion could silently destroy user annotations. I did not read every file in the repo, such as CMake files and the lines after 780, so that part is unchecked.
- gpt on re-check: **rating blocking**: AblationPlanner/AblationPlanner.py:298-302 contains `lineNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")` followed by `slicer.mrmlScene.RemoveNode(lineNode)` for each node, without ownership filtering or confirmation. This is a concrete path to unintended loss of unrelated unsaved user annotations, making safety blocking. I inspected the full Python module, CMake files, extension metadata, and README; external ModelToModelDistance and the sample-data payload were not inspected, and the supplied commit identity could not be independently resolved.
- gemini on re-check: **rating ok**: Inspecting AblationPlanner/AblationPlanner.py and the repository build files shows no malicious or concealed behavior, no network transmission (other than the standard SlicerTestingData sample data URL in registerSampleData on line 65), no command injection, unsafe deserialization, or filesystem destruction. D1 is an ordinary MRML scene node management bug rather than a safety issue.


## Findings from some reviewers

### Fragile assumption that child SubjectHierarchy item ID is folderItemID + 1
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:793`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L793): `convertSegmentToModel` assumes that the exported model's subject hierarchy item ID is `modelNode + 1`. Subject hierarchy item IDs are not guaranteed to be sequential integers (`modelNode + 1`), which can cause `shNode.GetItemDataNode(modelNode + 1)` to return `None` and raise an `AttributeError` on `folder.GetDisplayNode()`.
  ```
  def convertSegmentToModel(segmentNode, folderName="Folder"):
  
      shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
      modelNode = shNode.CreateFolderItem(shNode.GetSceneItemID(), folderName)
      slicer.modules.segmentations.logic().ExportVisibleSegmentsToModels(segmentNode,modelNode)
      folder = shNode.GetItemDataNode(modelNode +1)
  ```
  Suggestion: Use `vtkIdList` with `shNode.GetItemChildren(modelNode, childIds)` to retrieve the exported child item ID reliably.

### Off-by-one segment index in convertSegmentsToSegment union loop
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:689`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L689): The loop iterates up to `GetNumberOfSegments() + 1`, so on the last iteration `i == GetNumberOfSegments()`, which is out of bounds for 0-indexed `GetNthSegmentID(i)` (returning an empty/None segment ID). Additionally, `convertSegmentsToSegment` instantiates a GUI widget (`slicer.qMRMLSegmentEditorWidget()`) inside the Logic class and leaks `vtkMRMLSegmentEditorNode` in the scene.
  ```
      for i in range(1, segmentationNode.GetSegmentation().GetNumberOfSegments()+1):  #TWO ADDITIONAL PROBES
          segmentEditorWidget.setActiveEffectByName("Logical operators")
          effect = segmentEditorWidget.activeEffect()
          effect.self().scriptedEffect.setParameter("Operation","UNION")
          effect.self().scriptedEffect.setParameter("ModifierSegmentID",segmentationNode.GetSegmentation().GetNthSegmentID(i))
  ```
  Suggestion: Iterate over `range(1, segmentationNode.GetSegmentation().GetNumberOfSegments())` and remove the temporary `segmentEditorNode` from `slicer.mrmlScene` when finished.

### Parameter node observer is attached to old parameter node instead of new one
minor; soundness; raised by gemini, gpt
- **gemini** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:220`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L220): In `setParameterNode`, `self.addObserver(self._parameterNode, ...)` is called before `self._parameterNode = inputParameterNode` is assigned. This re-observes the old parameter node instead of observing the newly set `inputParameterNode`, and when `self._parameterNode` starts as `None`, the new parameter node is never observed at all.
  ```
      if self._parameterNode is not None:
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
      if self._parameterNode is not None:
        self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
  
      self._parameterNode = inputParameterNode
  ```
  Suggestion: Assign `self._parameterNode = inputParameterNode` before checking `if self._parameterNode is not None:` to add the observer.
- **gpt** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:220`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L220): The observer is re-added to the old node before the new one is assigned, so the initially selected parameter node is not observed. Separately, updateGUIFromParameterNode reads the role NativeFiducialsƒ whereas selections are stored under NativeFiducials, preventing that selection from being restored correctly.
  ```
      if self._parameterNode is not None:
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
      if self._parameterNode is not None:
        self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
  
      self._parameterNode = inputParameterNode
  ```
  Suggestion: Observe inputParameterNode after assignment and use the same reference role for saving and restoring.

### Registered test does not exercise the planner
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:854`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L854): The test reports success without loading data, placing probes, or checking computed margins, so it will not detect regressions in the main workflow.
  ```
      self.delayDisplay("Starting the test")
      
      # Get/create input data
  
     
      self.delayDisplay('Loaded test data set')
  ```
  Suggestion: Add automated tests with known probe geometry, expected margins, and invalid input cases.

### Typo in parameter node reference role "NativeFiducialsƒ" resets selector
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:249`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L249): In `updateGUIFromParameterNode`, the node reference role has a stray `ƒ` character (`"NativeFiducialsƒ"`), whereas `self.nodeSelectors` (line 122) and `onTumorButton` (line 277) use `"NativeFiducials"`. Whenever `updateGUIFromParameterNode` runs, `nativeFiducialsSelector` will be reset to `None`.
  ```
      wasBlocked = self.ui.nativeFiducialsSelector.blockSignals(True)
      self.ui.nativeFiducialsSelector.setCurrentNode(self._parameterNode.GetNodeReference("NativeFiducialsƒ"))
      self.ui.nativeFiducialsSelector.blockSignals(wasBlocked)
  ```
  Suggestion: Change `"NativeFiducialsƒ"` to `"NativeFiducials"`.

### Unmodified boilerplate SampleData registration and 10 MB test STL in repository
info; packaging; raised by gemini
- **gemini** (info, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:57`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L57): `registerSampleData()` registers boilerplate sample data pointing to `AblationPlanner1.png` (which does not exist in `AblationPlanner/Resources/Icons`) and the default Slicer MRHead testing volume checksum. Meanwhile, actual test data (`AblationPlanner/Testing/solid_LT6015.stl` (10 MB), `tumor.seg.nrrd`, `Endpoints.mrk.json`) is committed directly to the git repository, and `AblationPlannerTest` is an empty stub.
  ```
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
      # Category and sample name displayed in Sample Data module
      category='AblationPlanner',
      sampleName='AblationPlanner1',
      # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
      # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
  ```
  Suggestion: Either remove the unused template `registerSampleData` function or update it to load the actual ablation planning sample data from a release asset rather than committing a 10 MB STL file in `Testing/`.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read the full module Python file, the CMake files, the catalog entry, the README and the license. I found no network access beyond the standard Slicer sample-data registration. I found no package installs, no subprocess or eval use, and no data exfiltration. The license is the Slicer BSD-style license, and the README carries a research-only disclaimer. The catalog entry is usable, and its build dependency matches EXTENSION_DEPENDS. The problems are ordinary quality ones. The module deletes every Markups Line node in the scene, makes a global 3D-view change at setup, has a few latent bugs, uses a branch reference as the revision, and has weak tests and sample data. None of these block admission. 🟢 Recommend merge.
Not checked: 
<parameter name="x">AblationPlanner.ui contents (only grepped for URLs and commands)

### Gemini 4 Argon (`google/gemini-4-argon`): minor issues
AblationPlanner is a clean, self-contained scripted extension for planning tumor ablation probe placements and evaluating ablation margins using `ModelToModelDistance` and `FiducialRegistration`. It has no safety, environment, or licensing issues, and its CMake packaging and dependency declarations (`ModelToModelDistance`) are properly configured. However, the code contains several soundness issues—most notably calls to legacy Slicer 4 Markups API methods (`GetNumberOfFiducials`, `GetNthFiducialPosition`, `GetNthFiducialLabel`) removed in Slicer 5, a typo in `"NativeFiducialsƒ"` when updating the GUI from the parameter node, and fragile SubjectHierarchy ID arithmetic (`modelNode + 1`). These bugs are non-blocking for catalog admission Policy requirements. 🟢 Recommend merge
Not checked: AblationPlanner/Testing/solid_LT6015.stl (10 MB binary/large file not inspected)
Questions for the author: Have you tested the module on Slicer 5, where legacy Markups methods like `GetNumberOfFiducials()`, `GetNthFiducialPosition()`, and `GetNthFiducialLabel()` were removed in favor of the `ControlPoint` equivalents?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The module can delete unrelated line markups from the user's scene without confirmation, including when a probe endpoint is dragged. Several non-blocking correctness issues also affect probe orientation, stored selections, and margin colors. The inspected source has a research-only disclaimer and permissive license terms, but the catalog's moving branch and repository accessibility could not be independently verified. 🔴 Do not merge yet: fix the unintended deletion and verify the catalog source and revision.
Not checked: Could not independently access the remote repository, verify that the supplied snapshot is commit 5b9622a808096cb2d1a7b14410c8b50b1b6f29a3, or resolve the catalog's moving main branch.; Could not build or run the extension, Slicer, or its tests; no CI results were available.; The hinted 10 MB STL and binary sample data were not inspectable; external sample download, ModelToModelDistance source, and the separately linked profile library were not reviewed.; No previous catalog entry, PR checklist, or earlier reviewed source baseline was provided.


# AI review: AblationPlanner

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/naterex23/SlicerAblationPlanner at commit `5b9622a808096cb2d1a7b14410c8b50b1b6f29a3`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-17T03:25:06Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | ok |
| environment | ok | ok | ok |
| packaging | ok | ok | minor |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: AblationPlanner is a 3D Slicer scripted module for planning CT-guided tumor ablation: the user places fiducial pairs to position virtual vendor ablation profiles (ellipsoid segmentations), combines them, and computes signed tumor-to-ablation-zone margins via the ModelToModelDistance CLI, displayed as a colored surface model plus a distance table. It also supports intra-procedural re-alignment of a pre-procedure tumor segmentation to a new scan by fiducial registration.
- **flash-lite**: AblationPlanner is a 3D Slicer extension that enables users to place virtual ablation profiles (probes) and evaluate theoretical ablation margins relative to segmented tumors.
- **haiku**: AblationPlanner is a scripted 3D Slicer module for planning thermal ablation. It places virtual probe ablation zones from fiducial pairs, fuses them, and computes signed margins against a segmented tumor using ModelToModelDistance. It is intended for research use, as the README disclaimer states.

## Disagreements (start here)

### D1. Margin color button overwrites the computed signed-distance array in place
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified, other lines) [`AblationPlanner/AblationPlanner.py:591`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L591): changeColorsByMargin_ replaces the 'Signed' distance values on the output model with region indices 0..num_regions, so the distance data that the margin evaluation produced is destroyed on the model. 'Revert Color' (regenerateOriginalModelColors, lines 628-636) only restores len(originalColorArray)-1 values and depends on widget state (self.originalColorArray) that is lost when the scene is reloaded or the module is reopened, leaving a model whose 'Signed' scalars are region indices rather than distances. For a tool whose purpose is reading margins, a model that silently shows wrong distance values is misleading.
  ```
      for i in range(0,VTKFieldDataArray.GetSize()-1):
          colorval = VTKFieldDataArray.GetValue(i)
  
          thresholded = False
          for j in range(0,len(args)):
              if (colorval < args[j]):
  ```
  Suggestion: Write the region index into a separate array (e.g. 'MarginRegion') and switch the active scalar, leaving 'Signed' untouched; or store the original array as a node attribute so it survives scene reload.
- **haiku** (minor, high confidence, quote partly verified) [`AblationPlanner/AblationPlanner.py:591`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L591): The loops iterate range(0, GetSize()-1), so the final point value is never read or recoloured. This silently drops one vertex from signedVals, the statistics, and the colouring, and can change the reported minimum margin in edge cases.
  ```
  for i in range(0,VTKFieldDataArray.GetSize()-1):
            signedVals.append(VTKFieldDataArray.GetValue(i)) #value
  ```
  Suggestion: Use range(0, GetSize()) in all these loops (lines 353, 548, 591, 611, 633).

### D2. onLineButton deletes every markup line node in the scene, including user-created ones
single; category safety; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:298`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L298): The handler removes all vtkMRMLMarkupsLineNode objects in the scene, not just the lines this module created. A user who has measurement or trajectory lines in the same scene loses them without confirmation, and Slicer has no undo for node removal. The removal also happens while iterating the live collection returned by GetNodesByClass, which mutates the scene during iteration. This runs on every 'Place Markup Line' click and again from onMarkupEndInteraction (line 462) after each fiducial drag, so the loss can repeat silently.
  ```
      lineNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
  
      if lineNodes is not None:
        for lineNode in lineNodes:
          slicer.mrmlScene.RemoveNode(lineNode)
  ```
  Suggestion: Track the IDs of the line nodes the module creates (as is already done for probe nodes) and remove only those; iterate over a copied list of IDs.

### D3. setParameterNode never observes the new parameter node
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:220`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L220): Both guards test the old self._parameterNode instead of inputParameterNode, so the observer is removed from and re-added to the previous node and the incoming parameter node is never observed. After a scene close/reopen or a parameter-node switch, GUI updates from the parameter node stop working, and the module's saved selections are not reflected in the selectors.
  ```
      if self._parameterNode is not None:
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
      if self._parameterNode is not None:
        self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
  ```
  Suggestion: Change the second guard to `if inputParameterNode is not None:` and add the observer to inputParameterNode.

### D4. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku ok

### D5. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings all reviewers agree on

### Native fiducial selector restored from a misspelled node reference
major; soundness; raised by deepseek, flash-lite, haiku
- **deepseek** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:249`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L249): The role name contains a stray non-ASCII character, so GetNodeReference always returns None and the 'Native Fiducials' selector is cleared whenever the GUI is refreshed from the parameter node, even though updateParameterNodeFromGUI stores it under "NativeFiducials" (line 273). The user's selection is silently lost, which then feeds a None landmark node into the registration in onTumorButton.
  ```
      wasBlocked = self.ui.nativeFiducialsSelector.blockSignals(True)
      self.ui.nativeFiducialsSelector.setCurrentNode(self._parameterNode.GetNodeReference("NativeFiducialsƒ"))
  ```
  Suggestion: Use the exact string "NativeFiducials".
- **flash-lite** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:250`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L250): Line 250 in AblationPlanner/AblationPlanner.py queries reference key "NativeFiducialsƒ" (with a trailing unicode character 'ƒ') instead of "NativeFiducials". This mismatch will prevent the GUI from correctly restoring the native fiducials node reference from the parameter node when updating GUI from parameter node.
  ```
  self.ui.nativeFiducialsSelector.setCurrentNode(self._parameterNode.GetNodeReference("NativeFiducialsƒ"))
  ```
  Suggestion: Change "NativeFiducialsƒ" to "NativeFiducials".
- **haiku** (major, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:250`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L250): updateGUIFromParameterNode looks up "NativeFiducialsƒ" (with a stray non-ASCII character), but updateParameterNodeFromGUI stores the key "NativeFiducials". On scene reload or GUI refresh the native fiducial selector will show nothing, and onTumorButton (which reads "NativeFiducials") may then register against the wrong or no fiducials.
  ```
  self.ui.nativeFiducialsSelector.setCurrentNode(self._parameterNode.GetNodeReference("NativeFiducialsƒ"))
  ```
  Suggestion: Use the plain key "NativeFiducials" to match setup and updateParameterNodeFromGUI.


## Findings from some reviewers

### Automated test asserts nothing; committed test data is unused
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`AblationPlanner/AblationPlanner.py:854`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L854): test_AblationPlanner1 only shows delay dialogs and always reports 'Test passed', so the ctest registered by slicer_add_python_unittest (AblationPlanner/CMakeLists.txt:27) can never detect a regression. The committed files AblationPlanner/Testing/tumor.seg.nrrd and Endpoints.mrk.json are not loaded by any code, and Testing/Python/CMakeLists.txt contains only a commented-out line.
  ```
      self.delayDisplay("Starting the test")
      
      # Get/create input data
  
     
      self.delayDisplay('Loaded test data set')
  ```
  Suggestion: Load the committed tumor segmentation and endpoints, run the probe placement and margin logic, and assert on the resulting model/table contents.

### Division by zero for coincident or parallel fiducial vectors
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:746`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L746): When the two probe direction vectors are parallel or antiparallel (a plausible user placement, e.g. two probes along the same needle track), s is 0 and the expression divides by zero, producing NaNs that are then written into the transform matrix. Similarly updateProbePosition (lines 498-504) divides by fiducialDistance1/2, which is zero if the tip and entry fiducials coincide. The resulting transform is silently invalid rather than reported.
  ```
      a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
      v = np.cross(a, b)
      c = np.dot(a, b)
      s = np.linalg.norm(v)
      kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
      rotationMatrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
  ```
  Suggestion: Handle the parallel/antiparallel and zero-length cases explicitly and report an error to the user instead of building a NaN transform.

### Endpoint positions are appended in a loop and then overwritten
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote partly verified) [`AblationPlanner/AblationPlanner.py:429`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L429): Inside the loop, self.endPoints_positions is appended with xyz each iteration, then immediately reassigned to xyz. The append is dead code and misleads readers. Also, self.probeNodeIDs is indexed with endPoints_positions[i*2], which will raise IndexError if the fiducial count is odd or no probes were created.
  ```
  self.endPoints_positions.append(xyz) #.GetNthFiducialPosition(0, [1,1,1])
            self.endPoints_positions = xyz
  ```
  Suggestion: Remove the append and guard the index loop against odd counts and missing probe IDs; report the error to the user instead of printing.

### Fiducial registration runs without validating inputs or CLI status
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:277`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L277): None of the three nodes is checked before being passed to the FiducialRegistration CLI, and the returned CLI node status is ignored. If a selector is empty or the two fiducial sets have different point counts, the registration fails silently and the tumor is still attached to a transform node (line 291), so the user may believe the tumor was moved when it was not.
  ```
         nativeFiducials = self._parameterNode.GetNodeReference("NativeFiducials")
         tableFiducials = self._parameterNode.GetNodeReference("NewFiducials")
         tumorNode = self._parameterNode.GetNodeReference("InputTumor")
  ```
  Suggestion: Validate that both fiducial nodes exist and have equal, >=3 point counts, check the CLI status, and report failures with slicer.util.errorDisplay.

### Handlers use attributes that only exist after 'Place Probes' was pressed
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:382`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L382): self.formerMarkupID and self.observerID are only assigned at the end of onProbeButton (lines 446-447). Pressing 'Finalize / Combine Probes' first, or after a scene reload, raises AttributeError; if the markup node was deleted, GetNodeByID returns None and RemoveObserver fails. The same pattern appears in onProbeButton at lines 439-444. Neither handler has error handling, so the user sees a Python traceback instead of guidance.
  ```
      thisScene = probeNode.GetScene()
      markupReference = thisScene.GetNodeByID(self.formerMarkupID)
      markupReference.RemoveObserver(self.observerID)
  ```
  Suggestion: Initialise formerMarkupID/observerID to None in setup() and guard the observer removal; report a clear message when probes have not been placed yet.
- **haiku** (minor, medium confidence, quote verified) [`AblationPlanner/AblationPlanner.py:382`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L382): Probe placement and duplication call time.sleep and processEvents on the GUI thread, and the README notes runs of 2-5 minutes. onTranslateButton dereferences self.formerMarkupID and self.observerID, which are only set after onProbeButton, so pressing Translate first raises AttributeError.
  ```
  thisScene = probeNode.GetScene()
        markupReference = thisScene.GetNodeByID(self.formerMarkupID)
        markupReference.RemoveObserver(self.observerID)
  ```
  Suggestion: Guard these attributes with hasattr checks, show progress, and move long work off the GUI thread where possible.

### Long-running CLI executed synchronously on the GUI thread without progress
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`AblationPlanner/AblationPlanner.py:283`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L283): README.md:28 states the margin evaluation takes 2-5 minutes. runSync blocks the GUI for that whole time with no progress bar and no cancel, so Slicer appears frozen during the module's central operation. The CLI status is also never checked, so a failed run leaves an empty output model and the failure surfaces only as a generic exception in onMarginButton.
  ```
      parameters = {}
      parameters["vtkFile1"] = modelNode2
      parameters["vtkFile2"] = modelNode1
      parameters['distanceType'] = "signed_closest_point"
      parameters["vtkOutput"] = vtkOutput
  
  ```
  Suggestion: Use slicer.cli.run with a completion callback (or run the work in a background thread with progress), and check cliNode.GetStatusString() before reading the output arrays.

### Module forces a white 3D background on the user's views
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:101`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L101): Opening the module changes the background color of the first two 3D views, a persistent view setting saved with the scene, without asking the user. It is a side effect on shared application state unrelated to the module's function.
  ```
        threeDViewNode1 = slicer.app.layoutManager().threeDWidget(0).threeDController()
        threeDViewNode1.setWhiteBackground()
  ```
  Suggestion: Remove this, or make it an explicit user option.
- **haiku** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:103`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L103): Errors when configuring the 3D views are caught and assigned to an unused variable, so failures are silently dropped. This is minor, but it hides real problems from users and developers.
  ```
  except Exception as e:
           this_exception = e
          #print("Didn't find 3D View Open")
  ```
  Suggestion: Log the exception with logging.debug or narrow the try block.

### Off-by-one loop over segments in convertSegmentsToSegment
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`AblationPlanner/AblationPlanner.py:689`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L689): GetNthSegmentID is 0-based, so the last iteration passes an out-of-range index and returns None, which is then set as ModifierSegmentID. Depending on the effect implementation this either unions nothing or errors, and the segment count also changes as segments are merged, so the loop bound is stale. The subsequent removal loop (lines 706-708) always removes index 1, which is fragile.
  ```
      for i in range(1, segmentationNode.GetSegmentation().GetNumberOfSegments()+1):  #TWO ADDITIONAL PROBES
          segmentEditorWidget.setActiveEffectByName("Logical operators")
          effect = segmentEditorWidget.activeEffect()
          effect.self().scriptedEffect.setParameter("Operation","UNION")
          effect.self().scriptedEffect.setParameter("ModifierSegmentID",segmentationNode.GetSegmentation().GetNthSegmentID(i))
  ```
  Suggestion: Iterate over a snapshot of segment IDs (excluding the target segment) and remove segments by their captured IDs.

### Probe and tumor display nodes are swapped when setting opacity
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:537`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L537): The variable names are inverted relative to the nodes they come from, so the opacity intended for the tumor is applied to the probe segmentation and vice versa. This is cosmetic but makes the documented output appearance (README step 6) unreliable and confuses later maintenance.
  ```
      tumorDisplayNode = probeNode.GetDisplayNode()
      #tumorDisplayNode.SetVisibility(False) # Hide all points
      tumorDisplayNode.SetOpacity(0.2)
      probeDisplayNode = tumorNode.GetDisplayNode()
  ```
  Suggestion: Assign tumorDisplayNode = tumorNode.GetDisplayNode() and probeDisplayNode = probeNode.GetDisplayNode().

### Registered sample data points to a generic test blob and a missing thumbnail
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`AblationPlanner/AblationPlanner.py:57`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L57): The template registration was left in place: the URI is a SlicerTestingData SHA256 blob (not ablation data), and thumbnailFileName points to Resources/Icons/AblationPlanner1.png, which does not exist (the only icon in that folder is AblationPlanner.png). Users opening Sample Data > AblationPlanner get an unrelated volume and a broken thumbnail, which is worse than offering no sample data.
  ```
      SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='AblationPlanner',
        sampleName='AblationPlanner1',
  ```
  Suggestion: Either register real ablation sample data (tumor segmentation plus an ablation profile) with a matching thumbnail, or remove registerSampleData and the startupCompleted connection.
- **haiku** (minor, medium confidence, quote verified) [`AblationPlanner/AblationPlanner.py:63`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L63): registerSampleData points thumbnailFileName at Resources/Icons/AblationPlanner1.png, but the Icons folder contains only AblationPlanner.png. The sample entry will show no thumbnail.
  ```
  thumbnailFileName=os.path.join(iconsPath, 'AblationPlanner1.png'),
  ```
  Suggestion: Add the thumbnail to Resources/Icons or fix the path.

### Test is a placeholder and not registered
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`AblationPlanner/Testing/Python/CMakeLists.txt:2`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/Testing/Python/CMakeLists.txt#L2): The only ScriptedLoadableModuleTest does no assertions (it only calls delayDisplay), and the Testing/Python CMake registration is commented out. Regressions in the margin and probe logic (for example, the off-by-one and fiducial-key issues above) would not be caught by CI.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a test using the included Testing/tumor.seg.nrrd and Endpoints.mrk.json that asserts margin outputs, and enable it in CMake.

### onProbeButton dereferences the endpoints markup node without a None check
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`AblationPlanner/AblationPlanner.py:304`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/AblationPlanner.py#L304): Only probeNode is validated; endPointsMarkupsNode is used at line 413 (GetNumberOfFiducials) and line 428. If the user presses 'Place Probes' without selecting an endpoints markup node, the module raises AttributeError in the GUI thread rather than telling the user what is missing.
  ```
           endPointsMarkupsNode = self._parameterNode.GetNodeReference("EndPoints")
           probeNode = self._parameterNode.GetNodeReference("InputSurface")
           if probeNode is None:
            print("Please enter a valid probe segmentation!")
            return
  ```
  Suggestion: Add the same None check for endPointsMarkupsNode and return with a user-visible message.

### Large binary assets committed; scanner-reported 10 MB STL not present at this revision
info; packaging; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`AblationPlanner/Testing/CMakeLists.txt:1`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/Testing/CMakeLists.txt#L1): The automated scan flagged AblationPlanner/Testing/solid_LT6015.stl (10 MB), but a full listing of the tree at this revision shows no such file; the largest committed binaries are the icon (139 KB) and roughly 2.8 MB of screenshots. The screenshots are documentation assets, not build inputs, so this is informational only.
  ```
  add_subdirectory(Python)
  ```
  Suggestion: No action required for the STL; consider moving screenshots to the README's hosted images if repository size matters.

### Large binary test asset noted by the automated scan
info; packaging; raised by haiku
- **haiku** (info, low confidence, quote no quote) [`AblationPlanner/Testing/solid_LT6015.stl`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/Testing/solid_LT6015.stl): The scan reports AblationPlanner/Testing/solid_LT6015.stl (10 MB) in the source repo, though it is not in the listed file tree I received. Large binaries should be fetched on demand, not committed. I could not read it to confirm.
  Suggestion: Confirm whether the STL is tracked; if so, move it to a release or SampleData download.

### Legacy .s4ext screenshot URLs use a different case than the committed files
info; packaging; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`AblationPlanner.s4ext:41`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner.s4ext#L41): The committed files are minimum_required_inputs.PNG / minimum_required_placement.PNG (upper-case extension), so these URLs 404 on GitHub raw. The index uses the JSON entry and CMakeLists.txt:12 (which references existing files), so this only affects the legacy .s4ext metadata.
  ```
  screenshoturls https://github.com/naterex23/SlicerAblationPlanner/raw/main/Screenshots/minimum_required_inputs.png https://github.com/naterex23/SlicerAblationPlanner/raw/main/Screenshots/minimum_required_placement.png
  ```
  Suggestion: Fix the case or drop the stale .s4ext file.

### UI file still carries the ExtractCenterline template class name
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`AblationPlanner/Resources/UI/AblationPlanner.ui:3`](https://github.com/naterex23/SlicerAblationPlanner/blob/5b9622a808096cb2d1a7b14410c8b50b1b6f29a3/AblationPlanner/Resources/UI/AblationPlanner.ui#L3): The top-level widget and the parameterNodeSelector baseName (line 38) are leftovers from the ExtractCenterline template. Loading works because childWidgetVariables looks up child names, but the parameter node combo box will suggest the name 'ExtractCenterline' to users.
  ```
   <class>ExtractCenterline</class>
   <widget class="qMRMLWidget" name="ExtractCenterline">
  ```
  Suggestion: Rename the top-level widget and baseName to AblationPlanner.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
No malicious behavior found: no network transmission of user data, no pip installs, no eval/exec/pickle, no obfuscated code, no reviewer-directed text. The Slicer BSD-style license permits distribution and the README carries a research-only disclaimer. The catalog entry is mechanically usable (ModelToModelDistance matches EXTENSION_DEPENDS, CMake installs the .py/.ui/icon). The main problems are ordinary correctness bugs in the module: a button that deletes every markup line node in the scene (including user-created ones), a broken parameter-node observer, in-place overwriting of the computed signed-distance array, and several unguarded None/zero-division paths. Non-blocking, but should be fixed.
Not checked: Could not execute the module or run its ctest in a Slicer installation, so runtime behavior (deprecated markups API such as GetNthFiducialPosition/GetNumberOfFiducials, vtkSegmentationCorePython import, and the Logical operators effect calls) was assessed by reading only.; Could not verify the exact upstream commit 5b9622a808096cb2d1a7b14410c8b50b1b6f29a3 against GitHub; the catalog entry pins scm_revision "main", so the reviewed content is the snapshot provided, not a fixed commit.; Did not inspect the ModelToModelDistance dependency extension's source or license.; Did not inspect the linked ablation-profile repository (https://github.com/naterex23/SlicerAblationPlannerProfiles) referenced in README.md:19.; Could not read the binary assets (icon PNG, screenshots, tumor.seg.nrrd) to check for embedded metadata or patient identifiers.; Could not verify whether the SlicerTestingData SHA256 blob used by registerSampleData actually resolves, or whether the missing AblationPlanner1.png thumbnail breaks the Sample Data entry at runtime.
Questions for the author: Should 'Place Markup Line' really delete every vtkMRMLMarkupsLineNode in the scene, or only the lines this module created?; Is the 'Signed' distance array intended to be overwritten by 'Apply Margin Color', and how should a user recover the original distances after reloading the scene?; Do you plan to add a real automated test using the committed Testing/tumor.seg.nrrd and Endpoints.mrk.json, and real sample data instead of the SlicerTestingData placeholder?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
AblationPlanner is a well-structured 3D Slicer scripted module designed for planning and evaluating ablation procedures. The repository includes clear documentation, screenshots, and correct CMake/s4ext packaging. Inspection of the source code reveals no safety or security issues, proper use of Slicer modules and CLI tools, and a clear research disclaimer. A minor typo in a parameter node reference key was noted and reported.

🟢 Recommend merge
Not checked: Full runtime test execution in a 3D Slicer environment with sample data and ModelToModelDistance extension installed.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
I found no malicious, network, or shared-environment behavior in the inspected files. There are no pip installs, no network calls except a checksummed SampleData registration (which only registers and does not download at startup), and no unsafe deserialization. The main issues are soundness: a wrong node-reference name in the GUI refresh, an off-by-one loop that drops the last array element, a missing sample thumbnail, and an empty test that is not registered. Admission requirements look met (dependency matches, license permits distribution, revision is "main"). Overall: minor issues. I did not run anything and did not read the 10 MB STL or the .ui file.
Not checked: The 10 MB STL in Testing (reported by the scan but not in the file listing) and the .ui file were not read.; The exact source revision was not resolved; I reviewed the repository snapshot provided, and 'main' is a moving branch reference.; No code was run; Slicer runtime behavior, the ModelToModelDistance dependency, and the SampleData download were not verified.; The external SampleData URL (SlicerTestingData) was not fetched; only the SHA256 string in the source was checked.; CI or build results were not available.


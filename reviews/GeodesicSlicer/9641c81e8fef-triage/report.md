# AI review: GeodesicSlicer

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/FredericBr/SlicerGeodesic at commit `9641c81e8fef5183594f53f40bffad01b1a0a0b8`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-20T03:10:03Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | ok |
| environment | ok | ok | ok |
| packaging | minor | ok | minor |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: GeodesicSlicer is a Slicer module for brain-stimulation targeting: it builds a scalp mesh from a head volume, computes geodesic (surface) distances with VTK Dijkstra, draws a 10-20 EEG electrode layout, projects a stimulation site onto the scalp, and computes rTMS motor-threshold correction factors. It is aimed at researchers doing MRI-guided TMS/EEG work.
- **flash-lite**: GeodesicSlicer is a 3D Slicer scripted module extension that calculates geodesic paths on 3D anatomical meshes, draws the EEG 10-20 electrode positioning system, projects scalp stimulation sites, and corrects rTMS resting motor thresholds.
- **haiku**: GeodesicSlicer is a scripted Slicer module for neuronavigation-free brain stimulation targeting. It computes geodesic paths on a scalp mesh, places EEG 10-20 fiducials, projects a stimulation site to the scalp, and estimates an adjusted rTMS motor threshold. It is aimed at TMS/NIBS researchers.

## Disagreements (start here)

### D1. Hard-coded MRML node IDs ('vtkMRMLSegmentationNode1', 'vtkMRMLModelNode4') break the mesh workflow in non-empty scenes
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:640`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L640): The code assumes the segmentation it just created is named vtkMRMLSegmentationNode1 and that the model it just loaded is vtkMRMLModelNode4. In any scene that already contains segmentation or model nodes (a normal working session, or a reloaded scene) these IDs belong to other nodes: the wrong node is hidden, and getNode('vtkMRMLModelNode4') either returns an unrelated node (wrong colour applied) or raises 'node not found', aborting the workflow after the STL has already been written. Same pattern at lines 759-767.
  ```
        SegNode_View = slicer.util.getNode('vtkMRMLSegmentationNode1')
        SegNode_View.SetDisplayVisibility(0)
  
        slicer.util.loadModel(name2)
  
        #Add skin color
  ```
  Suggestion: Keep the node objects returned by AddNewNodeByClass/loadModel in local variables and use them directly instead of looking nodes up by generated ID.
- **haiku** (major, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:640`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L640): mesh() and mesh2() look up nodes by fixed IDs. If the user's scene already contains a segmentation or model with those IDs (for example after a previous run or with other data loaded), slicer.util.getNode returns the wrong node. The code then hides that node (SetDisplayVisibility(0)) and recolours it. If the ID is absent, the call raises an exception after the STL has already been written.
  ```
  SegNode_View = slicer.util.getNode('vtkMRMLSegmentationNode1')
  SegNode_View.SetDisplayVisibility(0)
  
  slicer.util.loadModel(name2)
  
  #Add skin color
  ```
  Suggestion: Keep references to the nodes that were created (the segmentationNode object and the node returned by loadModel), and use those instead of looking up fixed IDs. Apply the same fix in mesh2 (lines 759-764).

### D2. Mesh output is written next to the input volume file, silently overwriting any existing '<volume>.stl'
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:626`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L626): Clicking 'Create a quick mesh'/'Create a mesh' derives the output path from the input volume's storage filename and writes an STL into the user's own data directory without asking. If a file with that name already exists it is overwritten without confirmation; if the volume has no storage node (e.g. a volume created in the scene or loaded from DICOM) GetStorageNode() returns None and the call raises AttributeError, and if the filename is empty the STL is written as '.stl' in the process working directory. Same pattern at lines 742-750 in mesh2().
  ```
        volumeNode2 = slicer.util.getNode(nom)
        filename2 = volumeNode2.GetStorageNode().GetFileName()
        nom=filename2+'.stl'
        logging.info('Model is writing')
        writer.SetFileName(nom)
  ```
  Suggestion: Write to a temporary directory or ask the user for an output path (e.g. qt.QFileDialog / slicer.util.getNewFileName), and guard against a missing storage node or empty filename.
- **haiku** (minor, medium confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:626`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L626): The output path is derived from the volume's storage file name plus '.stl'. The file is overwritten silently if it exists. If the volume was never saved, GetStorageNode() returns None and the call crashes after the segmentation work is done.
  ```
  volumeNode2 = slicer.util.getNode(nom)
  filename2 = volumeNode2.GetStorageNode().GetFileName()
  nom=filename2+'.stl'
  ```
  Suggestion: Write to a user-chosen or temporary location, or at least check that the storage node exists and warn before overwriting. Keep the mesh in the scene where possible.

### D3. Unbounded convergence loop in EEG() can freeze Slicer
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:1036`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L1036): The Cz search iterates until the sagittal and coronal midpoints map to the same mesh vertex. There is no iteration cap, no progress update and no cancel check inside the loop, and each iteration runs several full Dijkstra passes on the whole scalp mesh. On a mesh where the two estimates never coincide (coarse or asymmetric mesh, misplaced landmarks) the loop runs forever on the GUI thread and the user must kill Slicer.
  ```
        while closestPointIdCz_tmp_cor !=closestPointIdCz_tmp_sag:
  ```
  Suggestion: Add a maximum iteration count (and/or a distance tolerance) and report failure to the user; update the progress dialog and check progressBar.wasCanceled() inside the loop.
- **haiku** (minor, medium confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:1034`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L1034): The Cz search loop repeats until the closest-vertex index from the sagittal pass equals the one from the coronal pass. Nothing caps the iterations, and the loop runs on the GUI thread. If the two estimates oscillate between vertices, Slicer freezes with no way out.
  ```
  closestPointIdCz_tmp_sag=0 #to determine Cz
  
      while closestPointIdCz_tmp_cor !=closestPointIdCz_tmp_sag:
  ```
  Suggestion: Add a maximum iteration count with a user-facing error, and run the computation with progress feedback so the GUI stays responsive.

### D4. onApplyCorrect replaces the slider widget attribute with an int, causing AttributeError on later UI updates
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:473`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L473): self.MTunadjusted is the ctkSliderWidget created in setup(); after 'Correct the motor threshold' is clicked it becomes a plain int. Any later call that touches the widget (e.g. onM1SiteOff at line 453 'self.MTunadjusted.enabled = False', or onM1SiteOn line 463) raises AttributeError: 'int' object has no attribute 'enabled', leaving the rTMS correction panel in a broken state. self.skip is also only assigned in onTubeUpdated, so the value depends on whether the slider ever emitted valueChanged.
  ```
      def onApplyCorrect(self):
        logic = GeodesicSlicerLogic()
        self.MTunadjusted = self.skip
  ```
  Suggestion: Read the value with self.MTunadjusted.value and pass it to the logic; never rebind the widget attribute.

### D5. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Catalog pins the moving branch 'master' instead of a commit
minor; packaging; raised by haiku; **quote not found in source**
- **haiku** (minor, high confidence, quote file not found) [`GeodesicSlicer.json:1`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer.json#L1): scm_revision is a branch name, so the revision built by the index can change without a catalog update. The reviewed source is commit 9641c81, which the index does not record.
  ```
  "scm_revision": "master",
  ```
  Suggestion: Pin scm_revision to a full commit hash, such as 9641c81e8fef5183594f53f40bffad01b1a0a0b8, that has been reviewed.

### Dead or unused code paths in the widget
minor; soundness; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:408`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L408): onSelect is never connected and refers to self.outputSelector, which is never created; if it were ever wired up it would raise AttributeError. Harmless today but misleading.
  ```
      def onSelect(self):
        self.applyButton.enabled = self.inputTargetModelSelector.currentNode() and self.outputSelector.currentNode()
  ```
  Suggestion: Remove the method or implement it against the real selectors.
- **haiku** (minor, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:408`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L408): onSelect refers to self.outputSelector, which is never created, so it would fail if called. Both 'Find the shortest path' and 'Make 10-20' reuse self.applyButton and self.inputTargetModelSelector. The reused names are harmless only because connections are made before reassignment. This is confusing and fragile.
  ```
  def onSelect(self):
        self.applyButton.enabled = self.inputTargetModelSelector.currentNode() and self.outputSelector.currentNode()
  ```
  Suggestion: Remove onSelect and give each widget a unique name.

### Electrode selection depends on fiducial order via fixed slice indices
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:1771`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L1771): ProjectedPoint assumes the first four fiducials are the landmarks and the last three are the stimulation point and T3P3. A user who adds or reorders fiducials gets a wrong nearest-electrode list with no warning.
  ```
  EEG_electrodes_real=EEG_electrodes[4:-3] #remove nasion,inion,tragus left & right, stim_point & T3P3
  EEG_electrodes_names_real=EEG_electrodes_names[4:-3]
  ```
  Suggestion: Select electrodes by their label names rather than by slice position, and validate the fiducial count and labels before use.

### Fewer than two fiducials raises IndexError despite the 'Add at least two fiducials' check
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:814`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L814): The guard at line 791 only checks that a markups node is selected, not how many fiducials it holds; line 831 then evaluates list[1], so with 0 or 1 fiducials the user gets a Python IndexError traceback instead of the intended error dialog. Same pattern in draw() (lines 913-930).
  ```
        numFids = fiducialInput.currentNode().GetNumberOfFiducials()
  
        list=[]
        for i in range(numFids):
            ras = [0,0,0]
            fiducialInput.currentNode().GetNthFiducialPosition(i,ras)
  ```
  Suggestion: Check numFids >= 2 and show the error dialog before indexing the list.
- **haiku** (minor, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:791`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L791): run_djikstra and draw check only that a fiducial node exists. They then index list[1] (lines 830-831, 929-930), so a node with a single point raises an unhandled IndexError with no user message.
  ```
  if not fiducialInput.currentNode():
          error_text='Add at least two fiducials'
  ```
  Suggestion: Check GetNumberOfFiducials() >= 2 (and == 4 for EEG, which already exists) and show the error text the message promises.

### GetStorageNode() may be None for scene-created or DICOM-loaded models
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:804`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L804): run_djikstra(), draw() and EEG() (lines 806, 905, 997) look the model up by name and dereference GetStorageNode() unconditionally. A model without a storage node (created in the scene, or loaded from a scene file) yields AttributeError, and a duplicate node name can select the wrong node. The retrieved filename is only used for logging in run_djikstra/EEG, so the crash is avoidable.
  ```
        nom = inputModel.GetName()
        volumeNode = slicer.util.getNode(nom)
        filename = volumeNode.GetStorageNode().GetFileName()
  ```
  Suggestion: Use the model node passed in directly and guard the storage-node lookup (or drop it where it is only logged).

### Long computations run on the GUI thread; mesh2() blocks it with time.sleep
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified, other lines) [`GeodesicSlicer/GeodesicSlicer.py:593`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L593): mesh()/mesh2()/EEG()/ProjectedPoint()/CorrectedPoint() run thresholding, morphological closing and many Dijkstra passes synchronously in the button callback; mesh2() additionally sleeps 5 s twice and 3 s once (lines 707, 716, 740), during which the UI is frozen and the progress dialog cannot be cancelled. Only a few code paths call slicer.app.processEvents().
  ```
        progressBar.value = 10
        time.sleep(5)
  ```
  Suggestion: Move the heavy work to a CLI module or a worker thread (slicer.util.ProgressDialog with wasCanceled checks) and remove the artificial sleeps.
- **haiku** (minor, high confidence, quote verified, other lines) [`GeodesicSlicer/GeodesicSlicer.py:593`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L593): mesh2 calls time.sleep for 5, 5, and 3 seconds in the GUI thread, so the application freezes during those pauses. The sleeps are not needed for the computation.
  ```
        progressBar.value = 10
        time.sleep(5)
  ```
  Suggestion: Remove the sleeps. Use processEvents or a progress dialog if needed.

### No parameter node; logic state is stored on throw-away logic instances
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:486`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L486): Every callback constructs a new GeodesicSlicerLogic() (e.g. lines 426-443), so setStimulationPoint()/setM1Site() write to objects that are immediately discarded; the values are never read anywhere, so the radio-button state has no effect on the computation. Nothing is stored in a parameter node, so module state is not saved with the scene and cannot be scripted, contrary to Slicer conventions. The base-class __init__ is also not called.
  ```
      def __init__(self):
        self.StimulationPoint = 0
        self.M1Site = 0
        self.MTunadjusted = 100
  ```
  Suggestion: Use a vtkMRMLScriptedModuleNode parameter node (or a single widget-owned logic instance) and read the state from there.

### No working test suite
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`GeodesicSlicer/Testing/Python/CMakeLists.txt:2`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/Testing/Python/CMakeLists.txt#L2): The module's unit-test registration is commented out, and no test class is defined in the module file. Changes to geodesic or threshold calculations cannot be checked automatically.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a small test using the bundled template, or a synthetic mesh, to check path length and fiducial placement.

### README points to files/folders that do not exist at this revision
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`README.md:13`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/README.md#L13): The repository contains LICENSE/LICENCE (not License.txt) and no Example_template directory at commit 9641c81, so the advertised sample data and license pointer are dead links; users have no sample data to try the module with.
  ```
  - See License.txt for information on using and contributing.
  
  ### Template
  In Example_template folder
  ```
  Suggestion: Fix the file names in README and either commit the example template or link to where it can be downloaded.
- **haiku** (info, medium confidence, quote verified) [`README.md:8`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/README.md#L8): The README and help text point to a 4.10 wiki page. The module prints debug output (print(nom), print ('length= ' ...)) during processing, which clutters the Python console.
  ```
  - For documentation, tutorials, and more information about the extension, please see: https://www.slicer.org/wiki/Documentation/4.10/Modules/GeodesicSlicer
  ```
  Suggestion: Point to current documentation and replace print calls with logging.

### Skin segmentation uses hard-coded CT Hounsfield thresholds
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:589`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L589): The threshold 100..5000 HU only makes sense for CT. With an MRI volume (the module's own example template is a .nii) the segment is empty or wrong, and the subsequent surface extraction/Dijkstra steps silently produce meaningless paths rather than an error. Same values at lines 702-703.
  ```
        effect.setParameter("MinimumThreshold","100") #adjusting according to your data
        effect.setParameter("MaximumThreshold","5000") #adjusting according to your data
  ```
  Suggestion: Expose the threshold range in the UI (or auto-detect CT vs MR) and warn when the resulting segment is empty.

### Unit test is registered but the module contains no test class
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`GeodesicSlicer/CMakeLists.txt:22`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/CMakeLists.txt#L22): slicer_add_python_unittest is pointed at GeodesicSlicer.py, but the file defines no unittest.TestCase subclass (only 'import unittest' at line 57), so the registered ctest exercises nothing; GeodesicSlicer/Testing/Python/CMakeLists.txt is entirely commented out. Users therefore get no automated verification of the geodesic/10-20 computations.
  ```
  if(BUILD_TESTING)
  
    # Register the unittest subclass in the main script as a ctest.
    # Note that the test will also be available at runtime.
    slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)
  ```
  Suggestion: Add a real test class (e.g. GeodesicSlicerTest) using the bundled template data, or remove the test registration.

### draw() reloads the model file for every fiducial pair and rewires the model's polydata connection
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:955`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L955): Each loop iteration loads another copy of the STL into the scene and points the model node's polydata connection at a Dijkstra filter output, which is not a supported way to display a path; the scene accumulates duplicate models and the drawn path is not stored as a proper model/markup node. The computed path points are discarded.
  ```
            model2 = slicer.util.loadModel(filename)
            model2.GetDisplayNode().SetColor(1,0,0)
            dijkstra2 = vtk.vtkDijkstraGraphGeodesicPath()
            dijkstra2.SetInputConnection(model2.GetPolyDataConnection())
            model2.SetPolyDataConnection(dijkstra2.GetOutputPort())
  ```
  Suggestion: Compute the path once from the already-loaded model and add the resulting polyline as a vtkMRMLModelNode (or markups curve).

### Duplicate license files and unfilled template text in source headers
info; license; raised by haiku
- **haiku** (info, high confidence, quote verified) [`GeodesicSlicer/GeodesicSlicer.py:11`](https://github.com/FredericBr/SlicerGeodesic/blob/9641c81e8fef5183594f53f40bffad01b1a0a0b8/GeodesicSlicer/GeodesicSlicer.py#L11): LICENCE and LICENSE are both present, with different sizes (22364 and 21778 bytes). The module header still has placeholders such as '[rappeler les caractéristiques techniques de votre logiciel]'. These do not block distribution but should be cleaned up.
  ```
  # Ce logiciel est un programme informatique servant à [rappeler les caractéristiques techniques de votre logiciel].
  ```
  Suggestion: Keep one license file and replace the placeholder descriptions in the headers.

### Text-scan hint about 25 MB / 70 MB template files is not reproducible at this revision
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote no quote) no file cited: A recursive listing of the repository at commit 9641c81 shows only CMakeLists.txt, README.md, LICENCE, LICENSE, .gitignore, two PNGs and the module sources - there is no Example_template/Template.nii or Template.stl. The large-file hint therefore does not apply to this revision (the README reference to the folder is still stale, see the utility finding).
  Suggestion: No action needed for repository size.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Admission requirements are met: no network access, no package installation, no obfuscation or reviewer-directed text; CeCILL 2.1 (FR+EN) permits distribution; the catalog entry is consistent with the CMake (EXTENSION_DEPENDS "NA" vs empty build_dependencies) and the module file/icon are installed. The code is a research tool with a clear disclaimer, but it has several ordinary robustness bugs: it writes an STL next to the input volume, relies on hard-coded node IDs ('vtkMRMLModelNode4'), overwrites a Qt widget attribute with an int, and has an unbounded convergence loop. None of these is a blocking admission issue; they are non-blocking quality fixes. 🟢 Recommend merge.
Not checked: Could not verify the source revision 9641c81e8fef5183594f53f40bffad01b1a0a0b8 against GitHub (no network access); all statements are about the files as provided in this checkout.; Did not run the module or any build/test; behaviour of the VTK Dijkstra/parametric-spline computations and the numerical correctness of the 10-20 electrode placement and MT correction formulas were not validated.; Did not inspect the binary PNG assets (GeodesicSlicer.png, Resources/Icons/GeodesicSlicer.png) beyond their presence and size.; Did not verify whether the registered ctest actually fails or silently passes without a test class (inferred from the absence of a TestCase subclass).; Did not check the Slicer wiki documentation page linked from the module help text.
Questions for the author: Where should the generated STL go? Writing '<inputVolume>.stl' next to the user's data can overwrite an existing file - would you accept a user-chosen or temporary output path?; Is the hard-coded lookup of 'vtkMRMLSegmentationNode1'/'vtkMRMLModelNode4' known to fail when the scene already contains segmentation or model nodes?; Can the Cz convergence loop in EEG() be bounded so that a non-converging mesh reports an error instead of hanging Slicer?; The README mentions an Example_template folder and License.txt that are not in the repository - were they removed intentionally?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
GeodesicSlicer is a well-structured 3D Slicer extension for computing geodesic paths, generating the 10-20 EEG system on scalp models, projecting stimulation targets, and adjusting rTMS motor thresholds. Source code inspection reveals clean Slicer scripted module conventions, valid build configuration, proper CeCILL licensing, and no security or environment concerns. 🟢 Recommend merge
Not checked: Example_template/Template.nii (25 MB binary file not available in source repo checkout or index entry); Example_template/Template.stl (70 MB binary file not available in source repo checkout or index entry)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
I read the catalog entry, the module CMake files, and the full GeodesicSlicer.py (1962 lines). I found no network access, no package installation, no dynamic code execution, and no data transmission, so the safety picture is clean. The main issues are soundness: mesh functions depend on hard-coded scene node IDs (vtkMRMLSegmentationNode1, vtkMRMLModelNode4), the EEG Cz search loop has no iteration cap, and the module has no working tests. The catalog uses an unpinned "master" branch. I could not inspect the Example_template binaries or the exact source at the stated commit.
Not checked: Example_template/Template.nii and Template.stl (about 95 MB combined) were not readable; their content and license status were not verified.; The exact source at commit 9641c81 was not fetched. The review is based on the files supplied in the submission bundle.; The full text of LICENSE and LICENCE was not read; I only confirmed that CeCILL is named in the README and module.; No Slicer runtime was used. I did not run the module, the mesh pipeline, or any tests, so the behaviour of the hard-coded node IDs and the Cz loop is inferred from the code.; The screenshot URL and the external documentation links were not accessed.; No CI results were available to me.
Questions for the author: Can the mesh and EEG workflows run in a scene that already contains segmentation or model nodes? Why are fixed node IDs used instead of node references?; Is the Cz fixed-point loop guaranteed to converge? Has it been tested on meshes where the two estimates might oscillate?; Will you pin scm_revision to a commit hash rather than 'master'?; Are the large Example_template files (Template.nii, Template.stl) intended to remain in the source repository, and do they need a separate license statement?


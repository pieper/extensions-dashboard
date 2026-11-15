# AI review: ScapularMorphology

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/liukuan5625/SlicerScapularMorphology at commit `28fe666318286c72303515ba32902b51cf1864a5`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T10:07:03Z; cost $0.05

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | concern |
| environment | concern | ok | concern |
| packaging | blocking | ok | blocking |
| license | minor | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | concern |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer scripted module that takes scapula and humerus masks from a shoulder CT and runs two deep-learning models (2D U-Net for glenoid segmentation, 3D SegResNet for landmarks) to output a glenoid segmentation, five scapular landmarks and optional landmark heatmaps, for orthopaedic shoulder-morphology research.
- **flash-lite**: ScapularMorphology is a 3D Slicer scripted loadable module extension that performs deep-learning-based scapular morphology assessment, including glenoid segmentation and key anatomical landmark localization from CT scans.
- **haiku**: A 3D Slicer scripted module that segments the glenoid and locates five scapular landmarks from segmented scapula and humerus inputs, using deep-learning models run in a separate Slicer Python subprocess. It is aimed at researchers doing shoulder CT morphology analysis, and it requires the PyTorch extension.

## Disagreements (start here)

### D1. Inference script is never installed, so the module cannot run after installation
partial; category packaging; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`ScapularMorphology/CMakeLists.txt:5`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/CMakeLists.txt#L5): Only ScapularMorphology.py is installed by slicerMacroBuildScriptedModule. The logic launches `os.path.join(self.path, 'Scripts', "scapularmorphology_inference.py")` (ScapularMorphology.py:461), which does not exist in an installed extension, so every Apply fails with a CalledProcessError from logProcessOutput and no result is produced. The same missing directory is also the download target for the weights.
  ```
  set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    )
  ```
  Suggestion: Add `Scripts/scapularmorphology_inference.py` to MODULE_PYTHON_SCRIPTS (or install the Scripts folder explicitly) and verify the installed tree contains it.
- **haiku** (blocking, high confidence, quote verified) [`ScapularMorphology/CMakeLists.txt:5`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/CMakeLists.txt#L5): ScapularMorphology/CMakeLists.txt lists only ${MODULE_NAME}.py and the icon and UI resources. The module runs Scripts/scapularmorphology_inference.py via a subprocess, so every Apply in an installed build fails with a missing-file error. The downloaded weights are also written into the Scripts directory inside the install tree, which may be read-only in a system-wide Slicer install.
  ```
  set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    )
  ```
  Suggestion: Add Scripts/scapularmorphology_inference.py to the installed files (for example through an extra install(FILES ...) call or by placing it in a location the module can find after installation). Store downloaded weights in a user-writable location such as the Slicer cache or a user-chosen folder.

### D2. GUI update crashes when only the humerus mask is selected
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:242`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L242): The condition is true when only the humerus selector is filled, but the body dereferences scapulaVolume, which is then None, raising AttributeError inside the parameter-node observer each time the user picks a humerus node. The GUI then stops updating.
  ```
  if humerusVolume or scapulaVolume:
              self.ui.outputSegmentationSelector.baseName = _("{volume_name} segmentation").format(
                  volume_name=scapulaVolume.GetName())
  ```
  Suggestion: Use `if scapulaVolume:` (or fall back to the humerus name) before calling GetName().
- **haiku** (minor, high confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:242`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L242): The output name is built from scapulaVolume.GetName() whenever either input is set. If only the humerus input is selected, scapulaVolume is None and the widget raises AttributeError.
  ```
  if humerusVolume or scapulaVolume:
              self.ui.outputSegmentationSelector.baseName = _("{volume_name} segmentation").format(
                  volume_name=scapulaVolume.GetName())
  ```
  Suggestion: Use whichever input is set, or fall back to a fixed name when scapulaVolume is None.

### D3. Module setup assumes a 'Red' slice view exists
single; category soundness; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:120`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L120): initializeISrange() is called from setup() (line 110). In layouts without a Red slice view (e.g. a 3D-only layout) sliceWidget('Red') returns None, so setup() raises AttributeError and the module panel fails to open for that user.
  ```
  redCompositeNode = slicer.app.layoutManager().sliceWidget('Red').sliceLogic().GetSliceCompositeNode()
          volumeID = redCompositeNode.GetBackgroundVolumeID()
  ```
  Suggestion: Guard for a missing slice widget (or use the first slice view / the parameter node's volume) and fall back to a disabled range widget.

### D4. Unpinned pip installs can pull torch/torchvision from PyPI and upgrade Slicer-bundled packages
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:353`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L353): `monai[fire,pyyaml,nibabel,pynrrd,psutil,tensorboard,skimage,itk,tqdm]>=1.3` (line 350) installs pip `itk`, tensorboard and scikit-image into Slicer's shared environment, and `segmentation_models_pytorch` is unpinned and depends on torch/torchvision, so pip may install or upgrade torch from PyPI instead of using the PyTorch extension's build, and may upgrade numpy/scipy/protobuf that Slicer bundles. This affects every user of that Slicer installation, and it happens without any confirmation dialog.
  ```
  slicer.util.pip_install(monaiInstallString)
          modelInstallString = "segmentation_models_pytorch"
          slicer.util.pip_install(modelInstallString)
  ```
  Suggestion: Install only what is needed, pinned to versions compatible with Slicer's bundled packages, avoid the `itk`/`tensorboard` extras, ensure torch/torchvision come from PyTorchUtils, and ask the user before installing.
- **haiku** (major, medium confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:353`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L353): MONAI with several extras and segmentation_models_pytorch are installed with no version constraints and no confirmation prompt. Their transitive dependencies can upgrade or downgrade packages Slicer and other extensions rely on, and the installs run at the first Apply.
  ```
  slicer.util.pip_install(monaiInstallString)
          modelInstallString = "segmentation_models_pytorch"
          slicer.util.pip_install(modelInstallString)
  ```
  Suggestion: Ask for confirmation before installing. Pin or constrain versions so Slicer-bundled packages (numpy, scipy, SimpleITK, etc.) are not changed, and confirm that segmentation_models_pytorch does not pull torch from PyPI. Check the installed MONAI and smp versions against the ones the models were trained with.

### D5. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D6. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D7. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku blocking

### D8. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D9. Rating of utility
rating dispute; category utility; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings all reviewers agree on

### Downloaded model weights are deserialized with weights_only=False and no checksum
major; safety; raised by deepseek, flash-lite, haiku
- **deepseek** (major, high confidence, quote verified) [`ScapularMorphology/Scripts/scapularmorphology_inference.py:110`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/Scripts/scapularmorphology_inference.py#L110): downloadModel() fetches model_2d.pt/model_3d.pt with `checksum=None` (ScapularMorphology.py:381-382) and the inference script (also line 175) unpickles them with weights_only=False. If the release asset or the download is tampered with, arbitrary Python code runs with the user's privileges in the PythonSlicer subprocess. There is no integrity check anywhere in the chain.
  ```
  model_dict = torch.load(weight_pth, weights_only=False, map_location=torch.device(args.device))["state_dict"]
  ```
  Suggestion: Pin expected SHA256 checksums for both weight files and pass them to downloadFile, and load with `weights_only=True` (or load a state_dict-only checkpoint) so no pickle code can execute.
- **flash-lite** (minor, high confidence, quote verified) [`ScapularMorphology/Scripts/scapularmorphology_inference.py:110`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/Scripts/scapularmorphology_inference.py#L110): Using `torch.load` with `weights_only=False` on downloaded model weight files (`model_2d.pt`, `model_3d.pt` from GitHub releases) can execute arbitrary pickle payloads if model checkpoint files were ever compromised or maliciously replaced. While downloaded from the project repository release, best security practice in Slicer extensions is to use `weights_only=True` (available in modern PyTorch versions) or rely on safe state dictionary loading mechanisms.
  ```
  model_dict = torch.load(weight_pth, weights_only=False, map_location=torch.device(args.device))["state_dict"]
  ```
  Suggestion: Set `weights_only=True` in `torch.load` if compatible, or ensure state dict loading avoids arbitrary object deserialization.
- **haiku** (major, high confidence, quote verified) [`ScapularMorphology/Scripts/scapularmorphology_inference.py:110`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/Scripts/scapularmorphology_inference.py#L110): The module downloads model_2d.pt and model_3d.pt from GitHub release URLs with checksum=None and then calls torch.load(weights_only=False). Any tampered or replaced release asset, or a compromised account, gives arbitrary code execution in the user's Slicer process. The download also happens during processing without an explicit confirmation step.
  ```
  model_dict = torch.load(weight_pth, weights_only=False, map_location=torch.device(args.device))["state_dict"]
  ```
  Suggestion: Pin SHA-256 checksums for the weight files and pass them to downloadFile. Load with weights_only=True, or convert the weights to safetensors. Ask the user before downloading.


## Findings from some reviewers

### Bundled test uses a removed Slicer API and downloads data into the install directory
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:616`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L616): `returnNode` was removed from slicer.util load functions in current Slicer, so the registered unittest (slicer_add_python_unittest in ScapularMorphology/CMakeLists.txt:27) raises TypeError. The test also downloads sample data into the extension's Scripts folder and runs full GPU/CPU inference, so it cannot serve as a CI smoke test.
  ```
  [success, rawVolume] = slicer.util.loadVolume(samplerawPath, returnNode=True)
          [success, scapulaVolume] = slicer.util.loadSegmentation(samplescaPath, returnNode=True)
          [success, humerusVolume] = slicer.util.loadSegmentation(samplehumPath, returnNode=True)
  ```
  Suggestion: Use the current load API, keep test data in a temporary directory, and make the test skip gracefully when network or models are unavailable.

### Heat/CPU defaults use 'True' but the GUI compares against 'true'
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:390`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L390): updateGUIFromParameterNode compares `GetParameter("Heat") == "true"` (lines 221-222) while the default is "True", so on a fresh scene the checkboxes do not reflect the stored state and the saved settings are not restored consistently.
  ```
  if not parameterNode.GetParameter("Heat"):
              parameterNode.SetParameter("Heat", "True")
          if not parameterNode.GetParameter("CPU"):
              parameterNode.SetParameter("CPU", "True")
  ```
  Suggestion: Use one canonical value (e.g. "true"/"false") everywhere.

### Inference script has fragile error handling and index casts
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`ScapularMorphology/Scripts/scapularmorphology_inference.py:84`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/Scripts/scapularmorphology_inference.py#L84): An empty slice range (e.g. scapula and humerus masks never within 25 mm, or an IS range outside the volume) aborts with a bare AssertionError instead of a user-readable message. Related: `np.int8(np.round(gc_idx))` (line 154) overflows for indices above 127 in the 512-wide crop, and `affine = ori_aff_mat` followed by in-place modification (lines 89-90) mutates the original affine metadata.
  ```
  if len(gle_idx) == 0:
          assert 1 == 0
  ```
  Suggestion: Raise a descriptive error, use int32/int64 for indices, and copy the affine before modifying it.

### Input node types are inconsistent between the .ui file, the code and the parameter node defaults
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified, other lines) [`ScapularMorphology/Resources/UI/ScapularMorphology.ui:41`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/Resources/UI/ScapularMorphology.ui#L41): The .ui declares vtkMRMLScalarVolumeNode for both inputs and the output, the code overrides them to vtkMRMLSegmentationNode (ScapularMorphology.py:103-105), and initializeParameterNode() auto-selects the first vtkMRMLScalarVolumeNode into 'ScapulaVolume'/'HumerusVolume' (lines 176-183), which the segmentation-only selectors cannot display. The masks are then written with a vtkMRMLSegmentationStorageNode to a .nrrd file (lines 488-491) and read back by MONAI LoadImage, which is unlikely to yield the single binary mask the pipeline expects.
  ```
  <string>vtkMRMLScalarVolumeNode</string>
  ```
  Suggestion: Make the .ui, the code and the parameter-node defaults agree on segmentation nodes, and verify the written file is a binary labelmap the inference script can consume.

### Landmark index cast to int8 overflows for indices above 127
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`ScapularMorphology/Scripts/scapularmorphology_inference.py:154`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/Scripts/scapularmorphology_inference.py#L154): np.int8 wraps values outside -128 to 127. CT slice and voxel indices routinely exceed 127, so the glenoid index wraps to a wrong value and is passed on to cal_landmarks. The landmark index list is not written to the output in the current code, so the visible effect is limited, but the cast is wrong.
  ```
  gc_idx = tuple(np.int8(np.round(gc_idx)))
  ```
  Suggestion: Use np.int32 or plain integers, and apply the same fix to the landmark index cast on line 194.

### License and provenance of the downloaded model weights are not stated
minor; license; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`README.md:16`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/README.md#L16): The extension code is MIT, but nothing in the repository states the terms under which model_2d.pt and model_3d.pt (and the linked training repository) may be redistributed or used, and the 2D model also initializes with `encoder_weights="imagenet"` (scapularmorphology_inference.py:103), which downloads third-party pretrained weights at runtime. Users and the index cannot tell whether the weights are research-only.
  ```
  The module internally downloads pretrained model weights to intialize models.
  ```
  Suggestion: State the weights' license/provenance in the README (and in the release notes), and note any non-commercial or research-only restriction.

### Long-running work blocks the GUI thread with no progress reporting
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:516`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L516): process() runs pip installs (line 436), the weight download (line 437) and the blocking readline loop of logProcessOutput on the GUI thread, so Slicer freezes for the whole run (minutes on first use, when pip installs and downloads happen) with only a wait cursor and no progress or cancel.
  ```
  proc = slicer.util.launchConsoleProcess(scapularMorphologyCommand + options)
          self.logProcessOutput(proc)
  ```
  Suggestion: Run the pipeline in a CLI node or a worker thread with progress reporting, and separate dependency installation from the inference step.

### Model weights are downloaded into the installed extension directory without confirmation
minor; environment; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:368`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L368): Weights are written inside the extension installation folder, which may be read-only for system-wide installs and is deleted on extension update, forcing a re-download. The download starts automatically on the first Apply with no size/consent prompt.
  ```
  current_file_path = os.path.abspath(__file__)
          current_dir = os.path.dirname(current_file_path)
          destination_folder = os.path.join(current_dir, 'Scripts')
          model2dPath = os.path.join(destination_folder, 'model_2d.pt')
          model3dPath = os.path.join(destination_folder, 'model_3d.pt')
  ```
  Suggestion: Store weights in the Slicer user settings/cache directory and ask the user before downloading.

### Module help text is unedited template text
minor; utility; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:40`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L40): Users see template text instead of a description of the workflow, and the README gives no accuracy/validation figures or statement that the output is for research use only, which matters for a landmark/segmentation AI tool used in orthopaedic planning.
  ```
  self.parent.helpText = _("""
  This is an example of scripted loadable module bundled in an extension.
  See more information in <a href="https://github.com/liukuan5625/SlicerScapularMorphology">module documentation</a>.
  """)
  ```
  Suggestion: Replace the placeholder help text with the real workflow description and add a short research-use disclaimer plus validation summary.
- **haiku** (minor, high confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:41`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L41): The help text still describes the module as an example, which misleads users about what the module does and where to find documentation.
  ```
  This is an example of scripted loadable module bundled in an extension.
  See more information in <a href="https://github.com/liukuan5625/SlicerScapularMorphology">module documentation</a>.
  ```
  Suggestion: Replace it with a description of the glenoid and landmark pipeline and a link to the README tutorial.

### Scalar volumes are written with the segmentation storage node
minor; soundness; raised by haiku
- **haiku** (minor, low confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:488`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L488): processVolume creates vtkMRMLSegmentationStorageNode and uses it to write the scapula and humerus inputs, which are typed as scalar volumes. The inputs are actually segmentation nodes from the widget. The writer and the reader (MONAI LoadImage on NRRD) are not aligned, so the input array may not match what the model expects. I could not run this to confirm.
  ```
  scavolumeStorageNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationStorageNode")
          scavolumeStorageNode.SetFileName(scaInputFile)
          scavolumeStorageNode.UseCompressionOff()
          scavolumeStorageNode.WriteData(scapulaVolume)
  ```
  Suggestion: Confirm the exact NRRD layout the model expects. Write a labelmap or a scalar volume explicitly, and fix the type hints so they match what the GUI passes.

### Selected output segmentation node is ignored; a new node is created on every run
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:526`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L526): The `outputSegmentation` argument passed through process()/processVolume() is never used, so the node the user chose in the Outputs selector stays empty while a new 'ScapularGlenoid' node is added each click. The storage node created here is also never UnRegister()ed, leaking a node per run.
  ```
  def readSegmentation(self, output2DSegmentationFile):
          segNode2D = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", "ScapularGlenoid")
          scavolumeStorageNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationStorageNode")
          scavolumeStorageNode.SetFileName(output2DSegmentationFile)
          scavolumeStorageNode.ReadData(segNode2D)
  ```
  Suggestion: Write the result into the user-selected segmentation node (or remove the selector) and UnRegister the temporary storage node.

### Test does not assert anything and downloads data from the network
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`ScapularMorphology/ScapularMorphology.py:629`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/ScapularMorphology/ScapularMorphology.py#L629): test_ScapularMorphology downloads sample data and runs logic.process, but it never checks the output. The ctest registration is commented out, so CI does not exercise the module. This gives no protection against regressions.
  ```
  logic.process(scapulaVolume, humerusVolume, outputSegmentation,
                              False, False, False, False)
  ```
  Suggestion: Assert the segmentation and landmark outputs (for example segment count and fiducial count). Register the test in CTest. Keep the test data in a fixed, checksummed location.

### Catalog scm_revision is a moving branch
info; soundness; raised by haiku; **quote not found in source**
- **haiku** (info, high confidence, quote quote not found) no file cited: The catalog entry uses scm_revision "main", so the built code can change without a catalog update. The reviewed commit is 28fe666318286c72303515ba32902b51cf1864a5.
  ```
  "scm_revision": "main",
  ```
  Suggestion: Pin scm_revision to a reviewed commit or release tag.

### No license stated for the downloaded model weights and sample data
info; license; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`LICENSE:1`](https://github.com/liukuan5625/SlicerScapularMorphology/blob/28fe666318286c72303515ba32902b51cf1864a5/LICENSE#L1): The MIT license covers the code. The weights and sample files are downloaded from the author's GitHub releases, and their terms are not stated in the repository. Redistribution by others is therefore uncertain.
  ```
  MIT License
  
  Copyright (c) 2025 liukuan5625
  ```
  Suggestion: State the terms for the model weights and sample data in the README.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The extension is a thin GUI wrapper around a bundled inference script and two model weights downloaded from the author's GitHub release. The code license is MIT and the catalog entry is consistent (EXTENSION_DEPENDS PyTorch matches build_dependencies), but the extension cannot work as packaged: `Scripts/scapularmorphology_inference.py` is not listed in `MODULE_PYTHON_SCRIPTS`, so it is never installed and the subprocess launch fails. Safety/environment concerns: weights are downloaded with `checksum=None` and loaded with `torch.load(..., weights_only=False)`, and unpinned `pip_install` of `monai[...]` and `segmentation_models_pytorch` can pull torch/torchvision from PyPI and upgrade Slicer-bundled numpy/scipy. Several GUI crashes are also present. Recommendation: 🔴 Do not merge yet.
Not checked: Could not access the GitHub release assets (model_2d.pt, model_3d.pt, sample_*.nii.gz) to verify their existence, size, license or checksums.; Could not inspect the linked training repository https://github.com/liukuan5625/ScapularMorphology (license, model provenance, validation).; Could not run Slicer or the module, so runtime behaviour (segmentation storage node writing a segmentation to .nrrd, MONAI LoadImage reading it, subprocess launch) is inferred from code reading only.; Could not verify whether slicerMacroBuildScriptedModule installs subdirectories of the module folder; the packaging finding is based on the explicit SCRIPTS/RESOURCES lists in ScapularMorphology/CMakeLists.txt.; Could not check CI/build results for this extension or the resolved commit 28fe666318286c72303515ba32902b51cf1864a5 (catalog entry uses scm_revision "main").; Did not inspect the binary PNG files (ScapularMorphology.png, Screenshot01.png) beyond their size.
Questions for the author: How is ScapularMorphology/Scripts/scapularmorphology_inference.py installed? It is not in MODULE_PYTHON_SCRIPTS, so the module cannot find it after installation.; Can you publish SHA256 checksums for model_2d.pt/model_3d.pt and load them with weights_only=True?; Which license applies to the pretrained weights and to the linked training repository?; Why are monai extras `itk` and `tensorboard` installed into Slicer's shared Python environment, and can the install be pinned and confirmed with the user?; Should the input selectors accept segmentation nodes or scalar labelmap volumes? The .ui, the code and the parameter-node defaults currently disagree.

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
ScapularMorphology is a well-structured 3D Slicer extension providing deep-learning-based glenoid segmentation and scapular landmark localization. It integrates properly with PyTorchUtils, installs necessary python dependencies on demand, provides clear documentation, tutorial steps, and sample data references, and includes an MIT license. The catalog entry is correct and `🟢 Recommend merge` is warranted.
Not checked: Execution of full inference workflow inside 3D Slicer runtime (requires GPU/CUDA and sample datasets).

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The extension's main functionality cannot work as packaged: the inference script it launches (Scripts/scapularmorphology_inference.py) is not installed by CMake. The module also downloads pickled model weights from GitHub with no checksum and loads them with weights_only=False, and it installs MONAI and segmentation_models_pytorch into Slicer's shared Python environment without confirmation or pins. Test coverage is effectively absent, and there are several ordinary bugs. The MIT license is fine. I did not run anything, and I did not inspect the model weights or the upstream repository beyond the files listed.
Not checked: I did not run the extension, its installation, or any tests, and I did not execute any code.; I did not inspect the model weights, the sample data, or the upstream training repository (liukuan5625/ScapularMorphology).; I did not verify that scm_revision 28fe6663... exists or matches the files listed; I relied on the provided file contents.; I did not check the .ui file, the icon, or the screenshot files beyond their listing.; I did not check CI results, because none were provided.; I did not verify whether the Slicer extension packaging step installs non-listed Python files, which I assumed based on the CMake macro usage.
Questions for the author: Is Scripts/scapularmorphology_inference.py meant to be installed? If so, which CMake change installs it?; Can you publish SHA-256 checksums for model_2d.pt, model_3d.pt, and the sample files, and state their license?; Why does the module install unpinned MONAI and segmentation_models_pytorch without confirmation, and which versions were used to train the models?; Does the input written in processVolume match what the model was trained on (scalar volume or segmentation NRRD)?


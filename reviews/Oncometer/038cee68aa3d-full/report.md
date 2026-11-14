# AI review: Oncometer

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/Oncometer/SlicerOncometer at commit `038cee68aa3d2c7d823f192cd346bad4969a4c3c`
- Context: pull request 2395 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-14T17:23:23Z; cost $1.01

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | blocking | blocking |
| packaging | unknown | ok | unknown |
| license | unknown | ok | unknown |
| soundness | unknown | concern | concern |
| utility | unknown | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: Oncometer is a PET/CT oncology workflow extension with four modules: lesion segmentation (LION/lionz), organ segmentation (MOOSE/moosez or custom nnU-Net), lesion radiomics, and organ-level SUV quantification. It is for clinical researchers using 3D Slicer.
- **gemini**: Oncometer is a 3D Slicer extension for PET/CT oncology workflows providing automated lesion and organ segmentation (via ENHANCE-PET LION, MOOSE, or custom nnU-Net v2 models) and subsequent radiomics and organ-level SUV quantification. It is designed for clinical researchers and imaging scientists analyzing PET/CT scans.
- **gpt**: Oncometer supports PET/CT oncology workflows with lesion and organ segmentation and radiomics or organ-level quantification. It is intended for 3D Slicer users analyzing segmented PET/CT data.

## Disagreements (start here)

### D1. Selected existing segmentations are erased without warning
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`SegmentLesionsModule/SegmentLesionsModule.py:732`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/SegmentLesionsModule/SegmentLesionsModule.py#L732): The output selector explicitly allows an existing segmentation, but successful prediction deletes every existing segment before importing the result, without a replacement confirmation. Unsaved manual or other patient segmentations can be lost; the organ module has the same behavior at SegmentOrgansModule/SegmentOrgansModule.py:773-778. Import failure can also leave the selected node empty.
  ```
          segmentation = outputSegmentation.GetSegmentation()
          while segmentation.GetNumberOfSegments() > 0:
              segmentation.RemoveSegment(segmentation.GetNthSegmentID(0))
  
          outputSegmentation.CreateDefaultDisplayNodes()
          slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelMapNode, outputSegmentation)
  ```
  Suggestion: Create a new output by default, or clearly confirm destructive replacement and import into a temporary node before replacing existing contents.
- claude on re-check: **real: yes, minor**: SegmentLesionsModule.py:732-737 and SegmentOrgansModule.py:773-778 remove all segments from the user-selected output node with no confirmation (search found no askOkCancel/confirm). However, this is the node the user explicitly picked as output, so overwriting it is the expected behavior of a 'run into this node' workflow. It is a UX issue, not a concrete path to harm, so it isn't a blocking safety issue.
- gpt on re-check: **real: yes, blocking**: SegmentLesionsModule/Resources/UI/SegmentLesionsModule.ui:451-453 says "Select an existing segmentation node or create a new one." The apply handler uses that current node without a replacement prompt (SegmentLesionsModule/SegmentLesionsModule.py:458-483). At lines 732-737 it executes "while segmentation.GetNumberOfSegments() > 0:" and "segmentation.RemoveSegment(segmentation.GetNthSegmentID(0))" before import. SegmentOrgansModule/SegmentOrgansModule.py:773-778 does the same. Unsaved segments can be lost, including if import fails. Create a new output or confirm and replace transactionally.
- gemini on re-check: **real: yes, minor**: Verified in SegmentLesionsModule/SegmentLesionsModule.py:732-737 and SegmentOrgansModule/SegmentOrgansModule.py:773-778: _loadLabelMapAsSegmentation removes all existing segments from the selected outputSegmentation node without prompting. Overwriting the user-selected output node is standard for Slicer output selectors, not a blocking safety issue.

### D2. Unprompted pip_install("lionz") pulls PyTorch and nnUNetv2 directly from PyPI without PyTorchUtils
partial; category environment; raised by gemini, gpt; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (blocking, high confidence, quote verified) [`SegmentLesionsModule/SegmentLesionsModule.py:47`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/SegmentLesionsModule/SegmentLesionsModule.py#L47): Installing `lionz` directly via `pip_install` pulls in `nnunetv2`, `torch`, and other scientific Python dependencies directly from PyPI without using `PyTorchUtils` or prompting the user for confirmation. This can corrupt Slicer's shared Python environment by replacing Slicer-bundled packages or existing PyTorch installations.
  ```
  def _ensureLionInstalled() -> None:
      if importlib.util.find_spec("lionz") is None:
          slicer.util.pip_install("lionz")
  ```
  Suggestion: Add `PyTorch` to `EXTENSION_DEPENDS` and `build_dependencies`, use `PyTorchUtils` to manage PyTorch installation, avoid overwriting Slicer's bundled packages when installing `lionz`/`nnunetv2`, and ask the user for confirmation before installing large dependencies.
- **gpt** (blocking, high confidence, quote verified) [`SegmentLesionsModule/SegmentLesionsModule.py:47`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/SegmentLesionsModule/SegmentLesionsModule.py#L47): Running the default lesion model invokes this installer at line 766; the default organ workflow likewise installs moosez at SegmentOrgansModule/SegmentOrgansModule.py:29-31 and 895. Neither path asks permission before modifying Slicer's shared Python environment or explains download size and dependencies. The installed packages and dependency trees were not available, so whether they install torch, downgrade bundled packages, or download additional code or weights remains unverified.
  ```
  def _ensureLionInstalled() -> None:
      if importlib.util.find_spec("lionz") is None:
          slicer.util.pip_install("lionz")
  ```
  Suggestion: Ask for explicit confirmation and audit the resolved dependencies; install PyTorch through the PyTorch extension and use Slicer-compatible nnUNet installation logic where applicable.
- claude on re-check: **real: yes, blocking**: SegmentLesionsModule.py:47-49 calls slicer.util.pip_install('lionz') from _ensureLionInstalled(), which line 766 calls inside inference. There is no confirmation dialog. CMakeLists.txt:12 has EXTENSION_DEPENDS only on SlicerRadiomics, so PyTorchUtils is not used. README line 104 says it installs automatically. I could not inspect lionz's own requirements, but it is an nnU-Net-based tool that I expect to pull torch/nnunetv2 from PyPI. The index policy asks for changes when torch is installed outside PyTorchUtils and when large downloads happen without confirmation. The install happens on first use, not at import, which softens it somewhat.
- gpt on re-check: **real: yes, major**: The unprompted installation is verified: SegmentLesionsModule/SegmentLesionsModule.py:47-49 says "if importlib.util.find_spec(\"lionz\") is None:" followed by "slicer.util.pip_install(\"lionz\")"; lines 758-766 call it during built-in inference. The apply path at 447-483 has no install confirmation. The direct installation modifies Slicer's shared environment, but the repository does not establish the actual resolved PyPI dependency tree, PyTorch installation, downgrades, or download size. Those stronger claims remain unverified; the verified behavior warrants a major environment finding rather than asserting concrete environment breakage.
- gemini on re-check: **real: yes, blocking**: Verified in SegmentLesionsModule/SegmentLesionsModule.py:47-49 and 766: _ensureLionInstalled() runs slicer.util.pip_install('lionz') without user confirmation and without PyTorchUtils/NNUNet extension dependency handling (CMakeLists.txt:12 only depends on SlicerRadiomics). lionz depends on nnunetv2 and torch from PyPI, which violates the Extensions Index policy against installing PyTorch/nnunetv2 directly via pip and installing large packages without user confirmation.

### D3. Unprompted pip_install("moosez") pulls PyTorch and nnUNetv2 directly from PyPI without PyTorchUtils
single; category environment; raised by gemini; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (blocking, high confidence, quote verified) [`SegmentOrgansModule/SegmentOrgansModule.py:29`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/SegmentOrgansModule/SegmentOrgansModule.py#L29): Installing `moosez` directly via `pip_install` pulls in `nnunetv2`, `torch`, `torchvision`, and transitive dependencies (such as `SimpleITK`, `scipy`, `numpy`, `requests`, and potentially `opencv-python`) directly from PyPI without going through the Slicer PyTorch extension (`PyTorchUtils`) or the `NNUNet` extension's controlled install logic. This installs CPU/mismatched PyTorch wheels from PyPI, can overwrite or downgrade Slicer's bundled core packages, and runs a multi-gigabyte installation without user confirmation.
  ```
  def _ensureMooseInstalled() -> None:
      if importlib.util.find_spec("moosez") is None:
          slicer.util.pip_install("moosez")
  ```
  Suggestion: Depend on `PyTorch` (and/or `SlicerNNUNet`) in `CMakeLists.txt` (`EXTENSION_DEPENDS`) and the catalog entry (`build_dependencies`), ensure PyTorch is installed via `PyTorchUtils` before installing `moosez` (or install `nnunetv2`/`moosez` with `--no-deps` or constraints matching Slicer's bundled packages), and prompt the user with `slicer.util.confirmOkCancelDisplay` before downloading and installing large packages.
- claude on re-check: **real: yes, blocking**: SegmentOrgansModule.py:29-31 runs pip_install('moosez') with no confirmation, and line 895 triggers it during inference. PyTorchUtils is not used (CMakeLists.txt:12). I could not inspect moosez's own requirements, but it is an nnU-Net-based tool that I expect to pull torch/nnunetv2. The policy concern is the same as D2.
- gpt on re-check: **real: yes, major**: SegmentOrgansModule/SegmentOrgansModule.py:29-31 says "if importlib.util.find_spec(\"moosez\") is None:" followed by "slicer.util.pip_install(\"moosez\")"; lines 886-895 invoke it for built-in inference without a confirmation in the apply path at 445-504. This changes the shared environment without an install prompt. The actual PyPI dependency metadata, resolved wheels, download sizes and any downgrades were not available, so direct PyTorch/nnUNet installation and the specific downstream damage are not verified.
- gemini on re-check: **real: yes, blocking**: Verified in SegmentOrgansModule/SegmentOrgansModule.py:29-31 and 895: _ensureMooseInstalled() calls slicer.util.pip_install('moosez') without user confirmation and without PyTorchUtils/NNUNet extension dependency management. moosez pulls in nnunetv2 and torch directly from PyPI, which violates the Extensions Index policy on PyTorch/nnunetv2 installation and unprompted large downloads.

### D4. Dmax measures voxel-to-voxel diameter instead of lesion-centroid distance
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`RadiomicsModule/RadiomicsModule.py:723`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/RadiomicsModule/RadiomicsModule.py#L723): The module's help defines Dmax as the maximum distance between tumor centroids, but the implementation takes the convex hull of every tumor voxel and computes the farthest pair of hull points. A single extended lesion therefore receives a nonzero Dmax and multi-lesion distances include lesion size rather than just separation.
  ```
          arr = sitk.GetArrayFromImage(composantes_connexes) > 0
          coords = np.argwhere(arr)
          if coords.size == 0:
              return 0.0
          # Convex hull in index space, then transform hull vertices to physical points
          try:
  ```
  Suggestion: Calculate physical centroids per connected component and their maximum pairwise distance; test single and multiple lesions.
- claude on re-check: **real: yes, minor**: RadiomicsModule.py:723-748 computes the maximum pairwise distance between convex-hull voxel points of the whole mask. The help text at line 326 says 'maximum distance between tumor centroids'. The implementation therefore does not match its documentation: a single lesion gets a nonzero Dmax, and lesion extent is included. Voxel-based Dmax is a known definition, so this is mostly a documentation mismatch.
- gpt on re-check: **real: yes, major**: RadiomicsModule/RadiomicsModule.py:326 defines "Dmax : maximum distance between tumor centroids (mm)". Lines 723-730 select all foreground voxels, "coords = np.argwhere(arr)", and take "hull = ConvexHull(coords)"; lines 742-748 use "distances = pdist(physical, metric='euclidean')" and return its maximum. This measures the extreme voxel separation, not centroid separation, including for one extended lesion.
- gemini on re-check: **real: yes, major**: Verified in RadiomicsModule/RadiomicsModule.py:326 and 723-748: help text defines Dmax as 'maximum distance between tumor centroids (mm)', whereas _calculate_Dmax computes the convex hull of all tumor voxels (sitk.GetArrayFromImage(composantes_connexes) > 0) and returns the maximum pairwise Euclidean distance between hull vertices.

### D5. Global SUVmax, SUVmean, and TLG calculations only include the first connected component (label == 1)
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gemini** (major, medium confidence, quote verified) [`RadiomicsModule/RadiomicsModule.py:663`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/RadiomicsModule/RadiomicsModule.py#L663): In `RadiomicsModuleLogic.process`, `composantes_connexes = sitk.ConnectedComponent(binaryMask)` assigns distinct integer labels `1, 2, ..., N` to each connected lesion component. However, `_calculate_SUV_max`, `_calculate_SUV_mean`, and `_calculate_TLG` only select voxels where `composantes_connexes == 1`, ignoring all other lesions (`> 1`) when computing global SUVmean, SUVmax, and TLG.
  ```
          scan_array = sitk.GetArrayFromImage(scan)
          # temp extractors expect lesion label == 1
          mask_array = sitk.GetArrayFromImage(composantes_connexes) == 1
          vals = scan_array[mask_array]
  ```
  Suggestion: Use `sitk.GetArrayFromImage(composantes_connexes) > 0` (or pass `binaryMask`) when computing global `SUVmax`, `SUVmean`, and `TLG` across all segmented lesions.
- **gpt** (major, high confidence, quote verified) [`RadiomicsModule/RadiomicsModule.py:671`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/RadiomicsModule/RadiomicsModule.py#L671): The process creates a distinct connected-component label for each lesion, but global SUVmean and SUVmax select only label 1. TLG also uses only label 1's mean and volume, so a multi-lesion patient's reported global values omit other lesions and may miss the maximum uptake.
  ```
      def _calculate_SUV_mean(self, scan, composantes_connexes):
          scan_array = sitk.GetArrayFromImage(scan)
          mask_array = sitk.GetArrayFromImage(composantes_connexes) == 1
          vals = scan_array[mask_array]
          if vals.size == 0:
              return 0.0
  ```
  Suggestion: Compute global SUV statistics and TLG on the union of all nonzero lesion labels and add multi-lesion tests with different voxel values.
- claude on re-check: **real: yes, major**: RadiomicsModule.py:662-677 select only 'composantes_connexes == 1' for SUVmax and SUVmean. _calculate_TLG (687-694) uses the mean from that and volume[1], which is label 1 only. process() (lines 965-992) labels every lesion with a separate id. Global SUVmax, SUVmean and TLG therefore ignore every lesion except the first component on multi-lesion patients. This gives silently wrong clinical values.
- gpt on re-check: **real: yes, major**: RadiomicsModule/RadiomicsModule.py:963-965 computes "composantes_connexes = sitk.ConnectedComponent(binaryMask)"; global metric dispatch is at 981-992. Lines 662-673 use "mask_array = sitk.GetArrayFromImage(composantes_connexes) == 1" for both SUV statistics. Lines 687-694 multiply that mean by "volume[1]" for TLG. Other disconnected lesions are omitted from all three reported global metrics.
- gemini on re-check: **real: yes, major**: Verified in RadiomicsModule/RadiomicsModule.py:662-677 and 687-695: _calculate_SUV_max and _calculate_SUV_mean filter by `sitk.GetArrayFromImage(composantes_connexes) == 1`, and _calculate_TLG multiplies _calculate_SUV_mean by `volume[1]`, ignoring all connected components with label > 1.

### D6. Organ segmentations without numeric names silently report zero uptake
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`OrganomicsModule/OrganomicsModule.py:532`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/OrganomicsModule/OrganomicsModule.py#L532): Organomics accepts a segmentation node but maps organs solely by digits in segment names. A segmentation with ordinary names such as 'Liver' is treated as missing and the logic emits SUVmean and SUVmax of zero for those organs, presenting plausible measurements rather than warning that mapping failed. Numbers unrelated to labels may also select the wrong organ.
  ```
          for i in range(segmentIds.GetNumberOfValues()):
              segId = segmentIds.GetValue(i)
              segment = segmentation.GetSegment(segId)
              segmentName = segment.GetName() or ""
              match = re.search(r"(\d+)", segmentName)
              if match:
  ```
  Suggestion: Use explicit, validated organ-to-segment mapping or recognized anatomical names, and report missing or ambiguous organs rather than substituting zeros.
- claude on re-check: **real: yes, minor**: OrganomicsModule.py:531-538 maps segments to labels only by the first digits in the segment name. Lines 550-560 report zeros for unmapped organs without any warning. This matches the finding. The mapping is designed for segmentations produced by the companion SegmentOrgans module, so it is a robustness gap rather than a major defect. Digits unrelated to the label could also select the wrong organ.
- gpt on re-check: **real: yes, major**: OrganomicsModule/OrganomicsModule.py:535-538 maps segments only via "match = re.search(r\"(\\d+)\", segmentName)" and "labelToSegmentId[int(match.group(1))] = segId". Lines 550-560 assign "SUV_mean": 0.0 and "SUV_max": 0.0 when no label maps. Thus a name such as Liver produces zero rather than a warning; unrelated digits can map to the wrong organ.
- gemini on re-check: **real: yes, major**: Verified in OrganomicsModule/OrganomicsModule.py:531-560: segment mapping extracts the first integer via `re.search(r'(\d+)', segmentName)` and maps it to LABEL_MAP (1..9). Any organ segment without the expected numeric label in its name is not matched and silently receives 0.0 for SUV_mean, SUV_max, SUV_min, n_voxels, and volume_mm3.

### D7. Radiomics metrics install packages without asking
single; category environment; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`RadiomicsModule/RadiomicsModule.py:23`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/RadiomicsModule/RadiomicsModule.py#L23): Selecting TMTS or TVSR calls this helper for scikit-image, and Dmax calls it for scipy if absent. These operations modify the shared environment without a confirmation dialog; pip may also change dependencies used by other modules.
  ```
  def _ensurePythonPackage(packageName: str, moduleName: str) -> None:
      if importlib.util.find_spec(moduleName) is not None:
          return
  
      try:
          slicer.util.pip_install(packageName)
  ```
  Suggestion: Check for dependencies before processing, explain the changes and ask for confirmation, while preserving Slicer-bundled packages.
- claude on re-check: **real: yes, minor**: RadiomicsModule.py:23-28 _ensurePythonPackage calls pip_install, used at lines 698 (scikit-image) and 714 (scipy) without confirmation. scipy ships with Slicer, so find_spec succeeds and that call does nothing in practice. Only scikit-image may be installed, on first use of TMTS/TVSR. This is a small package, installed on explicit user action and documented in the README.
- gpt on re-check: **real: yes, major**: RadiomicsModule/RadiomicsModule.py:23-28 checks for a module and calls "slicer.util.pip_install(packageName)" with no confirmation. Lines 696-698 call it for scikit-image and 713-714 for scipy; lines 1017-1031 also invoke TMTS when calculating TVSR. This can change Slicer's shared environment during metric calculation. The exact packages pip resolves or changes were not inspected.
- gemini on re-check: **real: yes, major**: Verified in RadiomicsModule/RadiomicsModule.py:23-38, 698, and 714: _ensurePythonPackage calls slicer.util.pip_install(packageName) without user confirmation when computing TMTS ('scikit-image') or Dmax ('scipy').

### D8. TVSR mixes cubic centimeters with square millimeters
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`RadiomicsModule/RadiomicsModule.py:632`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/RadiomicsModule/RadiomicsModule.py#L632): Despite the comment, _calculate_TMTV returns mm³ divided by 1000, i.e. cm³, while _calculate_TMTS returns surface in mm². The global TVSR result is thus 1000 times smaller than the documented millimeter value.
  ```
      def calculate_TVSR(self, TMTV, TMTS):
          if TMTS <= 0.0:
              return float('nan') # division par 0
          
          # mm^3 / mm^2 = mm
          return TMTV / TMTS
  ```
  Suggestion: Convert volume or surface to consistent units before division and test with a known-volume phantom.
- claude on re-check: **real: yes, minor**: RadiomicsModule.py:679-685 returns TMTV in cm3 (mm3/1000). _calculate_TMTS (696-711) returns mm2 from marching cubes with spacing in mm. calculate_TVSR (632-637) divides them and its comment says 'mm^3 / mm^2 = mm'. The global TVSR is therefore 1000 times too small relative to the documented mm. The help text at line 332 also says TMTS is cm2. This is a units bug in one derived metric.
- gpt on re-check: **real: yes, major**: RadiomicsModule/RadiomicsModule.py:679-685 returns "total_mm3 / 1000.0" (cm³). Lines 706-710 calculate marching-cubes surface using physical spacing in mm, so it is mm². Lines 632-637 nevertheless state "# mm^3 / mm^2 = mm" and return "TMTV / TMTS"; the global call is at 1021-1031. This is 1000 times too small when expressed in the documented mm unit at line 330.
- gemini on re-check: **real: yes, major**: Verified in RadiomicsModule/RadiomicsModule.py:632-637, 679-685, and 696-711: _calculate_TMTV divides total_mm3 by 1000.0 (returning cm^3), while _calculate_TMTS returns mesh surface area in mm^2 (moreover help text at line 332 claims TMTS is cm^2), and calculate_TVSR returns TMTV / TMTS with comment '# mm^3 / mm^2 = mm', making global TVSR off by a factor of 1000 compared to _calculate_TVSR_local (lines 639-647).

### D9. Windows inference uses a selector on subprocess pipes
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`SegmentLesionsModule/SegmentLesionsModule.py:635`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/SegmentLesionsModule/SegmentLesionsModule.py#L635): On Windows Python's selector implementation supports sockets, not subprocess pipe handles, so registration fails when a prediction is launched. The organ module uses the same approach at lines 662-669; its process is started before registration and is not terminated on this failure. The provided inference smoke tests stub out the subprocess and do not exercise this path.
  ```
          stdout_lines: list[str] = []
          stderr_lines: list[str] = []
          selector = selectors.DefaultSelector()
          try:
              if process.stdout is not None:
                  selector.register(process.stdout, selectors.EVENT_READ)
  ```
  Suggestion: Use a cross-platform subprocess reader such as worker threads or Qt's QProcess, and terminate and reap the child on errors.
- claude on re-check: **real: yes, major**: SegmentLesionsModule.py:637-658 uses selectors.DefaultSelector() on subprocess pipes and calls selector.select(). On Windows, DefaultSelector is based on select.select, which only supports sockets. The select() call would raise OSError, not caught, in a loop at line 658. SegmentOrgansModule.py:664-669 does the same. This likely breaks inference on Windows, and the subprocess is not terminated on failure. The finding says registration fails; the failure is more precisely at select(), but the impact is the same.
- gpt on re-check: **real: yes, major**: SegmentLesionsModule/SegmentLesionsModule.py:625-642 creates subprocess pipes and registers them with "selector = selectors.DefaultSelector()" and "selector.register(process.stdout, selectors.EVENT_READ)"; line 658 selects on them. On Windows the default selector handles sockets, not subprocess pipes, so this fails when selection is attempted (not necessarily at registration). SegmentOrgansModule/SegmentOrgansModule.py:650-669, 686 and 708-712 uses the same pattern and only closes the selector in finally, without terminating the child. The smoke tests substitute fake inference at SegmentLesionsModule/SegmentLesionsModule.py:949-956 and SegmentOrgansModule/SegmentOrgansModule.py:1108-1115. This is a static platform assessment, not a Windows test.
- gemini on re-check: **real: yes, major**: Verified in SegmentLesionsModule/SegmentLesionsModule.py:637-642 and SegmentOrgansModule/SegmentOrgansModule.py:664-669: _runSubprocess registers process.stdout and process.stderr pipes with selectors.DefaultSelector(), which raises OSError on Windows because select() on Windows only supports sockets, not pipes, leaving the spawned process running on failure.

### D10. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **real: yes, minor**: I found no malicious or concealed behavior, no telemetry, no servers, and no eval or pickle use in the lines I read. Subprocess commands are built as lists (SegmentLesionsModule.py:614-618) and temp dirs are used. The safety-adjacent issues are the unconfirmed pip installs (D2/D3), which belong under the environment criterion, and the output-node overwrite (D1), which is not a path to harm. I did not read every file in full, so I rate this minor rather than ok.
- gpt on re-check: **rating blocking**: The safety concern is concrete: SegmentLesionsModule/Resources/UI/SegmentLesionsModule.ui:451-453 explicitly permits an existing output, and SegmentLesionsModule/SegmentLesionsModule.py:732-734 executes "while segmentation.GetNumberOfSegments() > 0:" then "segmentation.RemoveSegment(segmentation.GetNthSegmentID(0))" without replacement confirmation in the apply path (447-483); SegmentOrgansModule/SegmentOrgansModule.py:773-778 repeats this. Unsaved user data can be destroyed. I inspected these paths and searched the repository for network, execution, and destructive APIs; external lionz/moosez packages and models, exact resolved revision, and runtime behavior were not independently verified.
- gemini on re-check: **rating ok**: Checked SegmentLesionsModule/SegmentLesionsModule.py, SegmentOrgansModule/SegmentOrgansModule.py, RadiomicsModule/RadiomicsModule.py, OrganomicsModule/OrganomicsModule.py, and CMakeLists.txt: there is no malicious behavior, unauthorized telemetry, or command injection. The pip_install issues belong under the environment criterion, and overwriting the selected output segmentation node (D1) is normal Slicer UI behavior rather than a safety defect.


## Findings from some reviewers

### Axis order mismatch between voxel coordinates and spacing in _calculate_medPCD
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`RadiomicsModule/RadiomicsModule.py:510`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/RadiomicsModule/RadiomicsModule.py#L510): In `RadiomicsModuleLogic._calculate_medPCD`, `center_idx_zyx` and `boundary_indices` are reversed (`[::-1]`, converting zyx to xyz) and then multiplied by `spacing_zyx` (which was already reversed from `GetSpacing()` to zyx at line 504). Consequently, the x-index is multiplied by the z-spacing and the z-index is multiplied by the x-spacing, producing inaccurate physical distances on anisotropic volumes.
  ```
              # centroid in index (zyx) space
              indices = np.argwhere(mask_arr)
              center_idx_zyx = np.mean(indices, axis=0)
              center_mm = center_idx_zyx[::-1].astype(float) * spacing_zyx
  ```
  Suggestion: Either keep indices in `zyx` order when multiplying by `spacing_zyx`, or use `spacing_xyz = np.array(composantes_connexes.GetSpacing(), dtype=float)` with `indices[:, ::-1]`.

### volume_mm3 in OrganomicsModuleLogic equals voxel count instead of physical volume in mm3
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified, other lines) [`OrganomicsModule/OrganomicsModule.py:552`](https://github.com/Oncometer/SlicerOncometer/blob/038cee68aa3d2c7d823f192cd346bad4969a4c3c/OrganomicsModule/OrganomicsModule.py#L552): In `OrganomicsModuleLogic.process`, `volume_mm3` is set to `float(np.sum(mask))`, which is the raw voxel count rather than the physical volume multiplied by the voxel spacing (`np.prod(petVolume.GetSpacing())`).
  ```
                  results[label] = {
                      "name": self.LABEL_MAP[label]["name"],
                      "SUV_mean": float(np.mean(values)),
                      "SUV_max": float(np.max(values)),
                      "SUV_min": float(np.min(values)),
                      "n_voxels": int(np.sum(mask)),
  ```
  Suggestion: Multiply the voxel count `np.sum(mask)` by `float(np.prod(petVolume.GetSpacing()))` to compute the volume in cubic millimeters.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
The code has no sign of malicious behaviour, hidden telemetry or obfuscation. The main problem is environment handling. The segmentation modules call slicer.util.pip_install("lionz") and pip_install("moosez") with no confirmation. These packages bring in torch, nnunetv2 and numerous pinned dependencies from PyPI, which bypasses the PyTorchUtils and NNUNet extensions, and neither is declared in build_dependencies or EXTENSION_DEPENDS. The Radiomics module also installs scipy and scikit-image silently. The packages that moosez and lionz download at runtime (model weights) are undocumented. Minor items: scm_revision is "main", there are no real tests, and clinical disclaimers are missing. The license (MIT) is fine. Recommendation: 🔴 Do not merge yet, until the install logic is fixed.
Not checked: Whether the main branch matches the commit shown

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
Oncometer is a well-structured PET/CT oncology extension with four modules for lesion/organ segmentation and radiomics/organomics extraction, licensed under MIT. However, it has a blocking environment issue under the Extensions Index policy: `SegmentLesionsModule` and `SegmentOrgansModule` run `slicer.util.pip_install("lionz")` and `slicer.util.pip_install("moosez")` directly without user confirmation and without using the Slicer `PyTorch` extension (`PyTorchUtils`), which pulls `torch`, `nnunetv2`, and transitive dependencies directly from PyPI into Slicer's shared Python environment. Additionally, there are a few non-blocking calculation bugs in `RadiomicsModule` (SUVmean/SUVmax/TLG only consider connected component `== 1`, and `_calculate_medPCD` mixes xyz indices with zyx spacing). 🔴 Do not merge yet.
Not checked: Exact transitive pip dependency trees of lionz and moosez at runtime (no network/pip execution in review environment).; UI layout rendering in Slicer 5.10.
Questions for the author: Can `PyTorch` (and optionally `NNUNet`) be added to `EXTENSION_DEPENDS` and `build_dependencies` so PyTorch is installed through `PyTorchUtils` prior to installing `lionz` and `moosez`?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The extension silently replaces selected output segmentations and installs segmentation packages into Slicer's shared environment without confirmation. Several radiomics calculations also produce incorrect global results, and Windows subprocess handling appears incompatible with pipe selection. The extension source was supplied for commit 038cee68aa3d2c7d823f192cd346bad4969a4c3c, but the catalog's moving branch and external inference packages and models could not be independently verified. 🔴 Do not merge yet: address destructive output replacement and unconfirmed dependency installation; review the external inference payloads and model terms.
Not checked: Independent resolution of the catalog's main branch to the supplied commit, previous PR baseline, catalog validation, and CI results.; Execution, builds, runtime tests, and platform verification in 3D Slicer were not possible with the available tools.; Source, dependency metadata, download destinations, data handling, model integrity, and model-weight licenses of the externally installed lionz and moosez packages were not available.; Custom nnUNet checkpoints and their provenance, loading behavior, and license terms depend on user-provided models and were not inspected.; Clinical validation or suitability for clinical decision-making was not verified.
Questions for the author: Can you provide the exact lionz and moosez distributions, their dependency trees, model download locations and weight licenses, and their handling of input images?; Can the inference output always be created in a new node, or can replacement of a nonempty output be explicitly confirmed?


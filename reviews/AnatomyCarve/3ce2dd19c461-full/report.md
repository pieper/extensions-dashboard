# AI review: AnatomyCarve

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/andrey-titov/SlicerAnatomyCarve.git at commit `3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-16T02:25:50Z; cost $0.61

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | ok | ok | blocking |
| environment | concern | blocking | concern |
| packaging | concern | ok | unknown |
| license | ok | ok | ok |
| soundness | concern | concern | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: AnatomyCarve is a Rendering module that lets users clip a CT volume rendering with movable spheres. Each sphere hides segments the user chooses, using OpenGL compute shaders that write into a vector volume's GPU texture. A bundled C++ helper module, VolumeTextureIDHelper, reads the OpenGL texture handle out of VTK's internal volume mapper.
- **gemini**: AnatomyCarve is a 3D Slicer rendering extension for researchers and clinicians to interactively clip selected anatomical segments using sphere markups and OpenGL compute shaders. It enables textbook-style cutaway 3D volume visualizations where chosen segments are carved away inside user-placed spheres while preserving inner structures.
- **gpt**: AnatomyCarve lets Slicer users interactively carve selected anatomical segments from a volume-rendered medical image. It is intended for generating customized anatomical visualizations using clipping spheres.

## Disagreements (start here)

### D1. Uniform upload requests more data than the sphere array contains
single; category safety; raised by gpt; outcome after cross-examination: **real, major (2 of 2)**
- **gpt** (blocking, medium confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:328`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py#L328): The array has four floats per actual control point, but the native OpenGL call is told to read 32 vec4s. Rendering starts with one point, so absent wrapper-side padding this asks the driver to read beyond the NumPy allocation, potentially crashing Slicer or uploading unrelated process memory to the GPU. The call is made on every render.
  ```
          sphereDetails = np.array(sphereDetailsArray, dtype=np.float32)
          
          self.context.mask.updateSelectedRowFromSegmentation()
          
          #self.context.mask.texture.readRow2d(0)
  
  ```
  Suggestion: Upload only the actual number of vectors, or explicitly allocate and zero-pad a contiguous 32-by-4 array; enforce the 32-sphere limit and test with one and many spheres.
- gpt on re-check: **real: yes, major**: AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:321-328 builds one four-float entry per control point: "sphereDetailsArray.append(spherePosRadius)" and "sphereDetails = np.array(sphereDetailsArray, dtype=np.float32)". Line 337 nevertheless calls "glUniform4fv(glGetUniformLocation(shader.program, "sphereDetails"), 32, sphereDetails)"; lines 93-100 and 181 start with an initial point, and CarveVoxelsAA.comp:3,10 declares 32 vec4s. The size/count mismatch is real and presents a serious potential native out-of-bounds read on each tick, but the installed PyOpenGL wrapper and an actual native read or crash were not inspected or tested. Pad to 32 entries or pass the actual count; I would not claim a verified crash or information exposure.
- gemini on re-check: **real: yes, major**: In AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:321-337, sphereDetailsArray is populated with one [x, y, z, r] entry per control point in clippingSpheresNode (starting with 1 point in addInitialClippingSphere at line 181), converted to a NumPy array of shape (N, 4), and passed to glUniform4fv(..., 32, sphereDetails). Passing count=32 tells OpenGL to read 32 vec4s (128 floats) from the pointer, reading past the N*4 float buffer when N < 32. However, per the rubric and AGENTS.md ("Do not label ordinary bugs as safety issues merely because the extension processes medical images"), this is an ordinary buffer-size correctness bug (passing 32 instead of len(sphereDetailsArray)), not malicious behavior or a security/data-destruction vulnerability, and in the shader CarveVoxelsAA.comp:129,140 only indices < sphereCount are read.

### D2. C++ helper uses VTK-internal API and undeclared Volume Rendering dependency
single; category packaging; raised by claude; outcome after cross-examination: **still disputed**
- **claude** (major, medium confidence, quote verified) [`VolumeTextureIDHelper/Logic/vtkSlicerVolumeTextureIDHelperLogic.cxx:79`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/VolumeTextureIDHelper/Logic/vtkSlicerVolumeTextureIDHelperLogic.cxx#L79): The helper includes vtkSlicerVolumeRenderingLogic.h and the private VTK headers vtkVolumeInputHelper.h and vtkVolumeTexture.h. It accesses mapper->AssembledInputs, which may not be public or exported. Its CMake does not add Volume Rendering include directories or link the Volume Rendering logic, and the extension declares no dependencies. The build may therefore fail on the factory build machines. I could not verify this by building.
  ```
  auto it = mapper->AssembledInputs.find(portIndex);
  ```
  Suggestion: Confirm that the extension builds on all three platforms against the target Slicer. Add the Volume Rendering include directories and libraries to the helper's CMake. Document the dependency on the VTK version. Consider a public-API alternative.
- gpt on re-check: **real: unsure**: The dependency and fragile-API observations are real: VolumeTextureIDHelper/Logic/vtkSlicerVolumeTextureIDHelperLogic.h:43 includes "#include <vtkSlicerVolumeRenderingLogic.h>"; the .cxx:69-70 includes "#include <vtkVolumeInputHelper.h>" and "#include <vtkVolumeTexture.h>", and line 79 uses "auto it = mapper->AssembledInputs.find(portIndex);". Logic/CMakeLists.txt:7-8 has an empty include list and lines 15-17 list only "${ITK_LIBRARIES}". However, whether Slicer supplies these includes and libraries transitively, whether this particular VTK exposes the symbols, and whether a factory build fails are unverified. Volume Rendering is a Slicer built-in, so EXTENSION_DEPENDS "NA" alone does not establish a missing extension dependency. Investigate with the targeted Slicer/VTK build before asserting a build defect.
- gemini on re-check: **real: yes, major**: VolumeTextureIDHelper/Logic/vtkSlicerVolumeTextureIDHelperLogic.h:43 includes <vtkSlicerVolumeRenderingLogic.h>, and VolumeTextureIDHelper/Logic/vtkSlicerVolumeTextureIDHelperLogic.cxx:47-48,69-70 includes <vtkMRMLVolumeRenderingDisplayNode.h>, <vtkMRMLVolumeRenderingDisplayableManager.h>, <vtkVolumeInputHelper.h>, and <vtkVolumeTexture.h>, and line 79 accesses mapper->AssembledInputs. Meanwhile VolumeTextureIDHelper/Logic/CMakeLists.txt:7-17 only links ${ITK_LIBRARIES} with empty INCLUDE_DIRECTORIES and does not include or link Slicer's VolumeRendering module targets/directories.

### D3. RenderWindow StartEvent observer is never removed on scene close or module cleanup
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, major (2 of 2)**
- **gemini** (major, high confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:228`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py#L228): When `startRender` is called, an observer for `vtkCommand.StartEvent` is added to the 3D view's `vtkRenderWindow`, but `observerTag` is stored only in a local variable and is never removed when the scene closes, when the module is exited/cleaned up, or if rendering is restarted. If the scene is closed afterwards, `applyCarveVoxelsComputeShaderTick` will continue to fire on every render of the 3D view and attempt to access deleted/stale MRML nodes and textures.
  ```
      def applyCarveVoxelsComputeShader(self):
          
  
          renderWindow = slicer.app.layoutManager().threeDWidget(self.context.getViewIndex()).threeDView().renderWindow()
          
          observerTag = renderWindow.AddObserver(vtk.vtkCommand.StartEvent, self.applyCarveVoxelsComputeShaderTick)
  ```
  Suggestion: Store `observerTag` and the observed `renderWindow` on `self`, and provide a cleanup method (called on scene close and widget cleanup) that removes the observer from `renderWindow` and releases OpenGL textures.
- **gpt** (minor, high confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:228`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py#L228): The observer tag is only stored in a local variable and the widget cleanup removes different observers. After a scene is closed or the module is reloaded, the render window can continue calling the old logic with stale scene nodes and textures, generating errors and retaining GPU resources.
  ```
      def applyCarveVoxelsComputeShader(self):
          
  
          renderWindow = slicer.app.layoutManager().threeDWidget(self.context.getViewIndex()).threeDView().renderWindow()
          
          observerTag = renderWindow.AddObserver(vtk.vtkCommand.StartEvent, self.applyCarveVoxelsComputeShaderTick)
  ```
  Suggestion: Store the render window and observer tag, remove the callback on scene close and cleanup, and release owned OpenGL resources.
- gpt on re-check: **real: yes, major**: AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:231-233 creates "observerTag = renderWindow.AddObserver(vtk.vtkCommand.StartEvent, self.applyCarveVoxelsComputeShaderTick)" as a local variable. AnatomyCarve/AnatomyCarve.py:305-314 removes the widget's own and markup observers, while lines 330-339 reset the parameter node without removing the render-window observer. The callback at Logic.py:308-325 continues using the old context and markup node. After scene closure or module reload, it may continue executing with stale objects and produce errors; repeated starts via the logic API can add callbacks. The normal UI disables the render button after start (AnatomyCarve.py:412-419), so routine restart through that button should not be assumed. Exact errors and resource retention were not runtime-tested.
- gemini on re-check: **real: yes, major**: In AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:228-233, applyCarveVoxelsComputeShader adds a vtkCommand.StartEvent observer on the 3D view's vtkRenderWindow and stores observerTag only in a local variable. Neither AnatomyCarveWidget.cleanup (AnatomyCarve/AnatomyCarve.py:305-315) nor onSceneStartClose (lines 330-333) removes this observer, and clicking Render again adds duplicate observers.

### D4. Segmentation is used in the volume grid without geometry alignment
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (2 of 2)**
- **gpt** (major, high confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/Context.py:211`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/Context.py#L211): The label map is generated in the segmentation's saved reference geometry and uploaded without resampling to the selected intensity volume. FillColorVolume.comp then indexes both grids with the same coordinates, so differing origins, extents, spacing, directions or transforms can produce displaced or missing anatomy and incorrect clipping.
  ```
          # 2. Generate it.  Use EXTENT_REFERENCE_GEOMETRY or another extent mode.
          #    EXTENT_REFERENCE_GEOMETRY will use the segmentation’s saved reference image geometry.
          success = self.segmentation.GenerateMergedLabelmapForAllSegments(mergedLabelmap, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)
  ```
  Suggestion: Resample the segmentation into the selected intensity volume's geometry, including transforms, or reject mismatched inputs with a clear message. Add tests with different extents and geometry.
- gpt on re-check: **real: yes, major**: Context.py:211-213 calls "self.segmentation.GenerateMergedLabelmapForAllSegments(mergedLabelmap, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)" without passing the chosen intensity volume, and lines 218-226 upload the resulting scalars without applying geometry. Context.py:93-120 derives the output geometry from the intensity volume. FillColorVolume.comp:22-31 derives "coord" from the output and does "uint label = imageLoad(labelMap, coord).x;". Thus differently aligned segmentation and volume grids are treated as if their voxel indices match, potentially miscoloring or misclipping anatomy; this is a core visualization correctness issue, not by itself evidence of clinical harm.
- gemini on re-check: **real: yes, major**: In AnatomyCarve/AnatomyCarveLogic/Context.py:213, createLabelVolume calls self.segmentation.GenerateMergedLabelmapForAllSegments(mergedLabelmap, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY) without passing the selected intensityVolume's geometry or resampling to match it (the code that set reference geometry from intensityVolume is commented out at lines 188-190). Both FillColorVolume.comp (lines 22-38) and CarveVoxelsAA.comp (lines 109-170) index labelMap, colorVolume, intensityVolume, and outputVolume with the same integer voxel coord.

### D5. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (concern, ok)**
Ratings: claude ok, gemini ok, gpt blocking
- gpt on re-check: **rating concern**: The safety concern is the unpadded sphere upload: AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:328,337 contains "sphereDetails = np.array(sphereDetailsArray, dtype=np.float32)" and "glUniform4fv(glGetUniformLocation(shader.program, "sphereDetails"), 32, sphereDetails)". It merits investigation and correction as a possible native over-read, not an unconditional assertion of a demonstrated crash: PyOpenGL's wrapper and GPU driver were not available to inspect or test. I also inspected the CMake files, Python module and shader logic, and searched for network, subprocess, deserialization, and deletion calls; AnatomyCarve.py:22-25 additionally installs PyOpenGL at import when missing, an environment concern. Exact revision, external packages, and runtime behavior were not independently verified.
- gemini on re-check: **rating ok**: Inspected all Python, C++, CMake, and GLSL files. There is no malicious behavior, telemetry, network communication, unsafe deserialization, or command execution. Note that AnatomyCarve/AnatomyCarve.py:22-25 calls slicer.util.pip_install('PyOpenGL') at top-level import if OpenGL is missing, which belongs under the environment criterion; the glUniform4fv count mismatch in AnatomyCarveLogic.py:337 is an ordinary coding bug (soundness) rather than a blocking safety issue under AGENTS.md.

### D6. Rating of packaging
rating dispute; category packaging; raised by claude, gemini, gpt; outcome after cross-examination: **settled: concern (concern)**
Ratings: claude concern, gemini ok, gpt unknown
- gpt on re-check: **rating unknown**: AnatomyCarve/CMakeLists.txt:5-12 lists the main Python module and all five logic files plus __init__.py; lines 15-22 list the shader and UI resources. Root CMakeLists.txt:12 says "set(EXTENSION_DEPENDS "NA")" and lines 21-22 add both modules. The helper includes potentially non-public VTK headers and a Volume Rendering header without explicitly listing their include paths (VolumeTextureIDHelper/Logic/CMakeLists.txt:7-17), but a build failure is not established. No catalog entry, independent revision resolution, Slicer build environment, or build results were available; packaging admission cannot be fully assessed.
- gemini on re-check: **rating concern**: In VolumeTextureIDHelper/Logic/vtkSlicerVolumeTextureIDHelperLogic.h:43 and .cxx:47-48,69-70,79, the C++ module includes VolumeRendering headers (vtkSlicerVolumeRenderingLogic.h, vtkMRMLVolumeRenderingDisplayNode.h) and VTK internal headers (vtkVolumeInputHelper.h, vtkVolumeTexture.h) and accesses mapper->AssembledInputs, while VolumeTextureIDHelper/Logic/CMakeLists.txt:7-17 does not add VolumeRendering include directories or link libraries. In addition, repo root and data/ contain committed binary/data files (VolumeTextureIDHelper/VolumeTextureIDHelper.zip, data/Panoramix-cropped.seg.nrrd).


## Findings all reviewers agree on

### Unconditional pip_install('PyOpenGL') at module import / Slicer startup
blocking; environment; raised by claude, gemini, gpt
- **claude** (major, high confidence, quote verified) [`AnatomyCarve/AnatomyCarve.py:22`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarve.py#L22): When 'OpenGL' cannot be imported, the module file calls slicer.util.pip_install at import. Slicer imports scripted modules at startup, so this changes the shared Python environment and downloads from the network for anyone who installed the extension. It happens without confirmation, and a failure will leave later wildcard imports broken.
  ```
  try:
      from OpenGL.GL import *
  except ImportError:
      slicer.util.pip_install('PyOpenGL')
  ```
  Suggestion: Defer the OpenGL import to the widget or logic. Ask the user before installing PyOpenGL, ideally from a button in the module UI. Show an error if installation fails.
- **gemini** (blocking, high confidence, quote verified) [`AnatomyCarve/AnatomyCarve.py:22`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarve.py#L22): In AnatomyCarve/AnatomyCarve.py, `slicer.util.pip_install('PyOpenGL')` is called at the top level of the module file when `OpenGL.GL` cannot be imported. In 3D Slicer, scripted module files are imported during Slicer startup to discover modules. Installing Python packages at module import/startup modifies Slicer's shared Python environment and blocks startup with network/pip activity even for users who never open the AnatomyCarve module. Furthermore, if `pip_install` runs, `from OpenGL.GL import *` is not re-executed afterward, so the subsequent imports (`from AnatomyCarveLogic import *`) will still work only if they import `OpenGL.GL` themselves, while `glGetError()` in `AnatomyCarve.py` remains undefined until restart.
  ```
  try:
      from OpenGL.GL import *
  except ImportError:
      slicer.util.pip_install('PyOpenGL')
  ```
  Suggestion: Do not call `slicer.util.pip_install` at module import time. Instead, defer the `OpenGL` import and `PyOpenGL` installation (with user confirmation or inside `setup()` / `onRenderButton()`) until the user actually enters or uses the module.
- **gpt** (major, high confidence, quote verified) [`AnatomyCarve/AnatomyCarve.py:22`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarve.py#L22): If PyOpenGL is absent, importing the module automatically contacts the package index and changes the shared Slicer Python environment, including for users who never open AnatomyCarve. A network or pip failure can also prevent module loading. The OpenGL names are not imported again into this module after the installation.
  ```
  try:
      from OpenGL.GL import *
  except ImportError:
      slicer.util.pip_install('PyOpenGL')
  ```
  Suggestion: Move dependency installation to an explicit user-confirmed setup flow and import the package after successful installation; do not install at startup.


## Findings from some reviewers

### Automated test does not exercise carving
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`AnatomyCarve/AnatomyCarve.py:483`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarve.py#L483): The test downloads a segmentation and constructs the logic but never renders a volume or asserts clipping results. Regressions in the central visualization workflow can therefore pass the registered test.
  ```
          # outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
          # threshold = 100
  
          # Test the module logic
  
          logic = AnatomyCarveLogic()
  ```
  Suggestion: Add automated checks for rendering, sphere limits, segmentation geometry and cleanup, with an appropriate OpenGL-capable test environment.

### GL shaders compiled in logic constructor without a current GL context
minor; soundness; raised by claude
- **claude** (minor, medium confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:49`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py#L49): AnatomyCarveLogic.__init__ calls glCreateShader and glCompileShader via ComputeShader before any 3D view's context is made current. That happens when the widget is created. The calls may fail or act on the wrong context. Later GL work runs from a render StartEvent observer that is never removed, and errors there are only cleared with glGetError.
  ```
  self.shaderFillColorVolume = ComputeShader("FillColorVolume.comp")
          self.shaderCarveVoxels = ComputeShader("CarveVoxelsAA.comp")
  ```
  Suggestion: Create shaders lazily in startRender after calling renderWindow.MakeCurrent(). Remove the StartEvent observer on cleanup. Check the GL version and report a clear error if OpenGL 4.3 is not available.

### Leftover template/binary artifacts and placeholder metadata
minor; packaging; raised by claude
- **claude** (minor, high confidence, quote verified) [`VolumeTextureIDHelper/qSlicerVolumeTextureIDHelperModule.cxx:71`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/VolumeTextureIDHelper/qSlicerVolumeTextureIDHelperModule.cxx#L71): A VolumeTextureIDHelper.zip is committed, and the helper's module metadata still holds placeholder help, contributor and funding text (John Doe, NIH grant NXNN...). The C++ module also carries an unused FooBar widget. The module's category is 'Examples', and it is hidden.
  ```
  moduleContributors << QString("John Doe (AnyWare Corp.)");
  ```
  Suggestion: Remove the zip and the unused FooBar widget. Fill in real module metadata.

### Committed zip archive and binary assets in source repository
info; packaging; raised by gemini; **quote not found in source**
- **gemini** (info, high confidence, quote quote not found) [`CMakeLists.txt:10`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/CMakeLists.txt#L10): The repository commits sample data (`data/Panoramix-cropped.seg.nrrd`, ~934 KB), two large screenshots in `docs/` (~1.5 MB and ~2 MB), a duplicate top-level icon (`SlicerAnatomyCarve.png`, ~413 KB), and a leftover archive (`VolumeTextureIDHelper/VolumeTextureIDHelper.zip`, ~2 KB). While none of these break the build, keeping large binary assets and leftover zip archives out of the main source tree (or storing sample datasets in GitHub releases) keeps the repository lightweight.
  ```
  SlicerAnatomyCarve.png  (412956 bytes, binary)
  ```
  Suggestion: Remove `VolumeTextureIDHelper/VolumeTextureIDHelper.zip` and consider hosting sample data and documentation images in releases or a separate branch/assets location.

### Platform limitation and the tracking branch
info; utility; raised by claude
- **claude** (info, medium confidence, quote verified) [`AnatomyCarve/Testing/Python/CMakeLists.txt:2`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/Testing/Python/CMakeLists.txt#L2): The extension only works on Windows and Linux with OpenGL 4.3, but the catalog entry does not restrict platforms. The entry's scm_revision is 'main' rather than a fixed commit. Tests are stubbed out and AnatomyCarveTest only downloads sample data. The module is also not a clinical tool, and there is no disclaimer.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a real test, and consider pinning a commit.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I read the catalog entry, the CMake files, all Python modules and the C++ helper. I found no malicious behaviour, network calls other than the sample-data download (which has a checksum), or data exfiltration. The main concerns are:
- PyOpenGL is pip-installed at module import time, without asking the user, so it runs at Slicer startup for anyone who has the extension.
- The C++ helper depends on VTK-internal members and headers and has no declared dependency on the Volume Rendering module. It may not compile, and I could not verify that.
- Shaders are compiled on the GUI thread with no known-current GL context.
- There is a leftover template zip, and the C++ metadata is placeholder text.
- Platform and OpenGL 4.3 limits are documented only in the README and description, not enforced.
The Apache-2.0 license is present.
Not checked: Shader files (.comp) and the .ui file were not read.; I did not build the C++ module or run Slicer, so I could not confirm compile success or runtime behaviour.; Binary files (PNG, zip, the seg.nrrd sample) were not inspected.; I did not check the VolumeTextureIDHelper UI and qrc resource files.
Questions for the author: Does the VolumeTextureIDHelper module compile on Windows, Linux and macOS factory builds against the current Slicer VTK (which headers expose AssembledInputs)?; Can PyOpenGL installation be moved out of import time and made opt-in?; What happens when the module is opened on a system without OpenGL 4.3, or on macOS?

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
AnatomyCarve provides interactive segment-aware spherical clipping for 3D volume rendering using OpenGL 4.3 compute shaders and a C++ helper module (`VolumeTextureIDHelper`) that retrieves VTK's internal OpenGL texture handle. The codebase is clean, well-documented, and licensed under Apache-2.0 with no malicious or data-exfiltration behavior. However, `AnatomyCarve/AnatomyCarve.py` runs `slicer.util.pip_install('PyOpenGL')` at top-level module import time (which runs at Slicer startup). Per the Slicer Extensions Index review policy, package installation at module import or Slicer startup is a blocking environment issue. Additionally, the `vtkRenderWindow` `StartEvent` observer is never disconnected on scene close or module cleanup.

🔴 Do not merge yet: move `pip_install('PyOpenGL')` out of module import/startup.
Not checked: Binary contents of VolumeTextureIDHelper/VolumeTextureIDHelper.zip and image files; Runtime execution of OpenGL 4.3 compute shaders and VTK internal mapper texture handle extraction across platforms
Questions for the author: Can the `PyOpenGL` installation and `OpenGL.GL` imports be moved from top-level module import into `AnatomyCarveWidget.setup()` or `onRenderButton()` so packages are not installed during Slicer startup?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The supplied source installs PyOpenGL at module import without consent and passes an undersized sphere array to an OpenGL uniform upload, risking a native out-of-bounds read. Rendering also assumes segmentation and intensity voxels share geometry, and its render observer is not removed. Source and build were inspected statically, but the catalog branch could not be independently resolved or built. 🔴 Do not merge yet: fix the startup installation and unsafe uniform upload, and verify the catalog revision and build.
Not checked: No Slicer instance, GPU, build, automated tests or CI reports were available; the review is static.; The supplied source is identified as commit 3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b, but the catalog's moving main branch and repository accessibility could not be independently resolved.; PyOpenGL's wrapper implementation and actual driver behavior were not available to verify whether it pads or rejects the undersized uniform array.; The binary ZIP, image contents, third-party package distribution terms, and independent provenance and permissions for the sample segmentation were not inspected.
Questions for the author: What is the provenance and redistribution permission for the cropped Panoramix segmentation and what is contained in VolumeTextureIDHelper.zip?


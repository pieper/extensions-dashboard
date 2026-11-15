# AI review: AnatomyCarve

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/andrey-titov/SlicerAnatomyCarve.git at commit `3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T17:41:27Z; cost $0.05

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | concern |
| environment | concern | ok | concern |
| packaging | minor | ok | concern |
| license | concern | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: AnatomyCarve is a 3D Slicer rendering module that lets a user place invisible "clipping spheres" in a 3D view so that selected segments of a segmentation are carved away interactively, producing textbook-style anatomical renderings. It targets users creating anatomical illustrations from CT/segmentation data, with a bundled C++ helper module exposing the volume-rendering OpenGL texture ID.
- **flash-lite**: AnatomyCarve is a 3D Slicer extension that enables interactive GPU-accelerated volumetric carving and visualization of medical images using custom compute shaders and segmentation masks.
- **haiku**: AnatomyCarve is a Slicer scripted module (with a small C++ helper module, VolumeTextureIDHelper) for interactive GPU-based clipping of 3D volumes by segment, using OpenGL compute shaders and clipping spheres, aimed at researchers producing anatomy-textbook-style renderings. It targets Windows and Linux with OpenGL 4.3 or newer.

## Disagreements (start here)

### D1. Bundled sample dataset has no provenance or licence statement
single; category license; raised by deepseek
- **deepseek** (major, medium confidence, quote partly verified) [`AnatomyCarve/AnatomyCarve.py:90`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarve.py#L90): The extension ships data/Panoramix-cropped.seg.nrrd (934 KB, derived from the Panoramix CTA case, an IRCAD 3D-IRCADb-style dataset) and downloads it from the project's own repository, but neither LICENSE.txt nor README.md states the origin or the terms under which this data may be redistributed. Apache-2.0 covers the code only. Users and the index therefore cannot verify that the extension may redistribute this third-party dataset; such datasets are frequently limited to research use and require acknowledgement.
  ```
          sampleName="CTA abdomen (Panoramix) segmentation",
  ...
          uris="https://raw.githubusercontent.com/andrey-titov/SlicerAnatomyCarve/main/data/Panoramix-cropped.seg.nrrd",
  ```
  Suggestion: Add a data/README or LICENSE-DATA note stating the dataset origin, its licence/terms of use, required citation, and any non-commercial/research-only restriction, and confirm redistribution is permitted.

### D2. No bound check on sphere count versus MAX_SPHERES=32
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote partly verified) [`AnatomyCarve/AnatomyCarveLogic/Mask.py:21`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/Mask.py#L21): The user can place arbitrarily many control points with the markups widget. Each one calls addSphere(), which writes row sphereCount-1 into a 2D texture allocated with exactly MAX_SPHERES rows (line 59) and, from index 33 on, writes outside the texture (GL error, undefined results, possible driver hang). The compute shader also declares sphereDetails[MAX_SPHERES] and reads mask column i for i < sphereCount, so with more than 32 spheres the shader reads the mask out of bounds while the uniform upload above under/over-runs its array. Nothing validates the count or warns the user.
  ```
      MAX_SPHERES = 32    
  ...
              self.texture.updateRow2d(self.sphereCount - 1, rowMask)
  ```
  Suggestion: Clamp the number of clipping spheres (disable the place-control-point action at 32, or size the texture/uniform from the actual count) and validate sphereCount before dispatch.
- **haiku** (major, medium confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/Mask.py:21`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/Mask.py#L21): Mask has a fixed capacity of 32 spheres (texture width/rows), but addSphere() does not check it. A user adding a 33rd clipping sphere writes beyond the texture (updateRow2d with yoffset >= height), which GL rejects. Since errors are cleared with glGetError() at the event handlers, this fails silently, and sphereDetails is still sent with a fixed count of 32. The clipping result becomes incorrect with no message to the user.
  ```
  MAX_SPHERES = 32    
  NEW_POINT_MASK_BASED_ON_SELECTED_ROW = True
  ```
  Suggestion: Check sphereCount against MAX_SPHERES in addSphere/addLastClippingSphere and report a clear error to the user (or refuse to add the point). Do not clear GL errors silently in event handlers.

### D3. PyOpenGL is pip-installed at module import, i.e. at Slicer startup, without asking the user
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`AnatomyCarve/AnatomyCarve.py:22`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarve.py#L22): Slicer imports every scripted-module file at startup to register modules, so this runs for all users who have the extension installed, even if they never open AnatomyCarve. It silently installs a third-party package from PyPI into Slicer's shared Python environment (changing an environment shared with other extensions, and downloading and executing code without informed opt-in). Conversely, on a machine without network access pip_install raises and the whole extension fails to load at startup, so the module does not even appear in the module selector. PyOpenGL is also not declared anywhere in CMake, so the dependency is resolved at runtime only.
  ```
  try:
      from OpenGL.GL import *
  except ImportError:
      slicer.util.pip_install('PyOpenGL')
  ```
  Suggestion: Move the OpenGL import into the logic/widget, and if PyOpenGL is really required, ask the user before installing (e.g. a ctkMessageBox confirmation or the Slicer 'install dependencies' pattern with progress), or state it as a documented prerequisite / add it to the extension's dependency documentation.
- **haiku** (major, high confidence, quote verified) [`AnatomyCarve/AnatomyCarve.py:22`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarve.py#L22): If importing OpenGL fails, the module file runs pip install into Slicer's shared Python environment during import, without confirmation and without a version pin. This affects every Slicer session in which the module file is loaded, not only sessions where the user opens AnatomyCarve, and it changes shared environment state.
  ```
  try:
      from OpenGL.GL import *
  except ImportError:
      slicer.util.pip_install('PyOpenGL')
  ```
  Suggestion: Declare PyOpenGL as an explicit dependency with user confirmation at first use (e.g. inside the widget setup or on Render click), and do not install at import time. Pin a version if practical, and check whether Slicer already provides it.

### D4. RenderWindow StartEvent observer is never removed and stays active after the module is closed
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:228`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py#L228): The returned observer tag is stored in a local variable and discarded, and AnatomyCarveWidget.cleanup() (AnatomyCarve.py:305-314) only removes the parameter-node and markups observers. The observer therefore keeps firing on every frame after the user leaves the module or closes the scene, holding the logic/context and their GPU objects alive; applyCarveVoxelsComputeShaderTick then indexes self.sphereRadiuses with IDs from a possibly cleared scene (KeyError) or uses deleted nodes, raising exceptions from inside a render callback where they are not shown to the user. Clicking Render again after a scene change also adds a second observer.
  ```
      def applyCarveVoxelsComputeShader(self):
  
  
          renderWindow = slicer.app.layoutManager().threeDWidget(self.context.getViewIndex()).threeDView().renderWindow()
          
          observerTag = renderWindow.AddObserver(vtk.vtkCommand.StartEvent, self.applyCarveVoxelsComputeShaderTick)
  ```
  Suggestion: Store the tag on the logic, remove it in a cleanup/stop method called from the widget's cleanup() and from exit(), and guard the tick callback with observers/heap checks.
- **haiku** (minor, medium confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:233`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py#L233): applyCarveVoxelsComputeShader registers a StartEvent observer on the 3D render window and discards the returned tag. Every Render click adds another observer that runs the compute shader on each frame, and cleanup() does not remove it. This leads to repeated GPU work and stale callbacks after the module is closed or the scene changes.
  ```
  observerTag = renderWindow.AddObserver(vtk.vtkCommand.StartEvent, self.applyCarveVoxelsComputeShaderTick)
  ```
  Suggestion: Store the observer tag and remove it when the context is torn down; guard against adding a second observer.

### D5. Shipped C++ helper module is an unmodified template with placeholder metadata
severity dispute; category packaging; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote partly verified) [`VolumeTextureIDHelper/qSlicerVolumeTextureIDHelperModule.cxx:64`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/VolumeTextureIDHelper/qSlicerVolumeTextureIDHelperModule.cxx#L64): The hidden helper module still advertises the 'Examples' category, a 'John Doe (AnyWare Corp.)' contributor and a dummy NIH grant, and ships an unused FooBar widget. This does not affect safety but makes the extension's provenance metadata misleading if the helper module is ever surfaced.
  ```
    return "This work was partially funded by NIH grant NXNNXXNNNNNN-NNXN";
  ...
    moduleContributors << QString("John Doe (AnyWare Corp.)");
  ```
  Suggestion: Replace placeholders with the real contributors/acknowledgement or remove the unused widget and template text.
- **haiku** (major, high confidence, quote partly verified) [`VolumeTextureIDHelper/qSlicerVolumeTextureIDHelperModule.cxx:64`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/VolumeTextureIDHelper/qSlicerVolumeTextureIDHelperModule.cxx#L64): VolumeTextureIDHelper is built as a loadable module (CMakeLists.txt line 22) but its metadata is template boilerplate: a fictitious contributor and a placeholder NIH acknowledgement, under a category named 'Examples'. Its widget is still the 'FooBar' sample. This misrepresents authorship and funding to users who install the extension, and it adds an unneeded compiled module to every Slicer install.
  ```
  This work was partially funded by NIH grant NXNNXXNNNNNN-NNXN
  moduleContributors << QString("John Doe (AnyWare Corp.)");
  return QStringList() << "Examples";
  ```
  Suggestion: Replace the placeholder contributor, acknowledgement and category with real values, or remove the FooBar widget and the unused template parts. Mark the module as hidden only if it is intended as an internal helper, and document that.

### D6. glUniform4fv called with hard-coded count 32 on a variable-length array: out-of-bounds host memory read
single; category safety; raised by deepseek
- **deepseek** (major, high confidence, quote partly verified) [`AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:328`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py#L328): sphereDetailsArray has one row per control point, so with a single clipping sphere the numpy buffer holds 4 floats, while glUniform4fv is asked to read 32*4 floats (512 bytes) from it. PyOpenGL passes the buffer pointer, so the driver reads memory beyond the array: garbage sphere positions at best, a segfault in the render callback (called on the GUI thread from the render window StartEvent) at worst. The engine adds exactly one control point at start (addInitialClippingSphere), so the very first render already takes this path.
  ```
          sphereDetails = np.array(sphereDetailsArray, dtype=np.float32)
  
          glUseProgram(shader.program)
          glUniform4fv(glGetUniformLocation(shader.program, "sphereDetails"), 32, sphereDetails)
  ```
  Suggestion: Pass the real element count (sphereDetails.shape[0]) or pad the array to exactly 32 rows filled with zeros before the call.

### D7. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D8. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D9. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D10. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku ok

### D11. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Compute shaders are compiled in AnatomyCarveLogic.__init__, so opening the module requires a current GL context
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:48`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py#L48): The logic object is created in AnatomyCarveWidget.setup(), i.e. the first time the user opens the module, and it immediately calls glCreateShader/glCompileShader. With no current OpenGL context (and certainly on macOS, where the OpenGL 4.3 compute shaders are unavailable) this raises from ComputeShader.createComputeShader and the module widget fails to appear with a raw driver error, instead of a readable 'OpenGL 4.3 required' message as the README's Windows/Linux prerequisite implies.
  ```
          ScriptedLoadableModuleLogic.__init__(self)
          self.shaderFillColorVolume = ComputeShader("FillColorVolume.comp")
          self.shaderCarveVoxels = ComputeShader("CarveVoxelsAA.comp")
  ```
  Suggestion: Defer shader creation to the Render action inside tryWithErrorDisplay, and check the GL version up front to give a clear message.

### Divide-by-zero normalisation and max() over possibly empty segment lists
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/Texture.py:57`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/Texture.py#L57): A constant-intensity volume (min == max, e.g. a mask-like or empty volume a user picks by accident) yields an all-NaN texture, so the render appears blank/black with no error shown. Similarly Mask.createTexture (Mask.py:55-58) and Context.createLabelToColorMap (Context.py:56-59) call max(...) over the segmentation's segment IDs, which raises ValueError for a segmentation with no segments; the widget auto-selects the first segmentation node in the scene, which can be empty.
  ```
          data = slicer.util.arrayFromVolume(scalarVolumeNode).astype(DEFAULT_TYPE)
          data = data.reshape(data.shape[::-1])
          min = data.min()
          max = data.max()
          data = (data - min) / (max - min)
  ```
  Suggestion: Guard max == min (skip normalisation) and validate that the segmentation has at least one segment, reporting a clear message to the user.

### Registered test asserts nothing
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AnatomyCarve/AnatomyCarve.py:468`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarve.py#L468): This unittest is registered as a ctest (AnatomyCarve/CMakeLists.txt:38) but only downloads the sample data and prints 'Test passed'; no assertion covers the logic, the OpenGL path or the sample-data checksum, so CI cannot detect regressions and the test may pass even when the module is unusable.
  ```
          self.delayDisplay("Starting the test")
  
          # Get/create input data
  
          import SampleData
  
  ```
  Suggestion: Add at least assertions on the sample download, texture/mask bookkeeping (add/remove sphere, radius update) using headless-safe helpers, and clean up node creation.

### Test case asserts nothing and Python test registration is disabled
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`AnatomyCarve/AnatomyCarve.py:490`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarve.py#L490): AnatomyCarveTest.test_AnatomyCarve1 only downloads sample data and calls AnatomyCarveLogic(); all assertions are commented out. The Testing/Python CMake registration is commented out, so the test does not check any behavior.
  ```
  # # Test algorithm with non-inverted threshold
  # logic.process(inputVolume, outputVolume, threshold, True)
  ```
  Suggestion: Add real tests (for example mask-row behavior, sphere add/remove, and sample-data load), and enable the registration in Testing/Python/CMakeLists.txt.

### Unconditional rewrite of slice background and creation of new output/VR nodes on every Render
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote partly verified) [`AnatomyCarve/AnatomyCarveLogic/Context.py:112`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/Context.py#L112): Starting a render silently replaces the slice views' background layer chosen by the user and adds an 'AnatomyCarve Output' vector volume plus a volume-rendering display node to the scene. If the user starts the module again (new scene, or after a failed start that left nodes behind), duplicates accumulate and the user's slice layout is overwritten without a way to undo from the module. Nothing is deleted permanently, but the scene is modified without consent.
  ```
          outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLVectorVolumeNode", "AnatomyCarve Output")
  ...
          slicer.util.setSliceViewerLayers(background=outputVolume)
  ...
          displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(outputVolume)
  ```
  Suggestion: Reuse an existing output node if present, ask or warn before replacing the slice background, and remove the temporary nodes when rendering stops.
- **haiku** (minor, medium confidence, quote partly verified) [`AnatomyCarve/AnatomyCarveLogic/Context.py:112`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/Context.py#L112): Context.createVectorVolume creates a new volume node, replaces the slice background with setSliceViewerLayers and enables volume rendering, all as side effects of the Render button. Users who did not expect this may lose their slice layout, and each click creates another node. No cleanup is performed on exit.
  ```
  outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLVectorVolumeNode", "AnatomyCarve Output")
  slicer.util.setSliceViewerLayers(background=outputVolume)
  ```
  Suggestion: Document the side effects in the UI, and offer to remove the output node. Guard against repeated rendering.

### Unused committed binary archive VolumeTextureIDHelper.zip
minor; packaging; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote no quote) [`VolumeTextureIDHelper/VolumeTextureIDHelper.zip`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/VolumeTextureIDHelper/VolumeTextureIDHelper.zip): A 2 KB zip archive is committed in the repository but referenced by no CMakeLists or source file (searched for the name across the tree). Its contents could not be inspected with the available tools, so an unreviewed binary blob ships in the extension source; it also looks like an accidental export artifact.
  Suggestion: Delete the archive unless it is required for a build step, and state its purpose if it is.
- **haiku** (minor, medium confidence, quote no quote) [`VolumeTextureIDHelper/VolumeTextureIDHelper.zip:1`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/VolumeTextureIDHelper/VolumeTextureIDHelper.zip#L1): VolumeTextureIDHelper/VolumeTextureIDHelper.zip (2111 bytes) is a binary in the source tree that CMake does not reference. Its content could not be inspected here, so reviewers cannot confirm it is harmless or that it is not a stray artifact. Binaries in source repos are a review and provenance concern.
  Suggestion: Remove the zip if it is not needed, or document what it contains and why it is committed.

### Whole-volume float32 RGBA copy made synchronously on the GUI thread
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/Context.py:99`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/Context.py#L99): For the bundled 441x321x215 sample this allocates roughly 0.5 GB of host RAM in several temporaries while the wait cursor blocks the GUI; a typical 512x512x500 CT needs several GB twice over, which on a 8-16 GB laptop triggers swapping or MemoryError after the user clicked Render. The same full-volume work is repeated per StartEvent in the shaders, but the Python-side copies happen once without progress reporting.
  ```
          arrayR = np.zeros(dims, dtype=np.float32)
          arrayG = np.ones(dims, dtype=np.float32)
          arrayB = np.ones(dims, dtype=np.float32)        
          arrayA = slicer.util.arrayFromVolume(self.intensityVolume).astype(np.float32) #np.ones(dims, dtype=np.uint8)
  
          arrayRGBA = np.stack((arrayR, arrayG, arrayB, arrayA), axis=-1)
  ```
  Suggestion: Build the RGBA array in one allocation (or reuse the existing VectorVolumeNode's array) and run the setup off the GUI thread or with a progress dialog.

### Helper module relies on VTK internal GPU handles
info; soundness; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`AnatomyCarve/AnatomyCarveLogic/Context.py:182`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/Context.py#L182): GetTextureIdForVolume returns raw GL texture handles from VTK internals (vtkVolumeInputHelper, vtkVolumeTexture) and the Python code writes into them through glTexParameter/glBindTexture. This depends on specific VTK/Slicer internals and can break on a Slicer upgrade. The -1 return path is not handled by the Python caller.
  ```
  self.outputVolumeTex3d.textureId = slicer.modules.volumetextureidhelper.logic().GetTextureIdForVolume(self.outputVolume, viewIndex)
  ```
  Suggestion: Check for -1 and raise a clear error, and pin the tested Slicer version in the README.

### No concealed behaviour found in the reviewed source
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote no quote) [`AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py:210`](https://github.com/andrey-titov/SlicerAnatomyCarve/blob/3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b/AnatomyCarve/AnatomyCarveLogic/AnatomyCarveLogic.py#L210): Reported for completeness: I searched the whole tree for network/socket/requests, subprocess, eval/exec, pickle/torch.load, and found no telemetry, outbound data transmission, credential handling, archive extraction or obfuscated code. The only network accesses are the SampleData download of the project's own NRRD (with SHA256 checksum) and the PyPI install noted above. Several heavily commented-out debug blocks remain but contain no instructions to reviewers or AI tools.
  Suggestion: No action required beyond the environment/packaging items above.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Sound core idea with a working tutorial and Apache-2.0 license, but not ready as submitted. A pip install of PyOpenGL runs at scripted-module import, i.e. at Slicer startup for every user who installs the extension, without any confirmation. The GPU data path has an unbounded clipping-sphere list fed to a fixed-size uniform array and a 32-row mask texture, a concrete out-of-bounds/crash path. A render-window observer is never removed, and the sample dataset's third-party provenance/licence is undocumented. Fixes are small but should land before the extension is offered to users.
Not checked: Could not read or unzip VolumeTextureIDHelper/VolumeTextureIDHelper.zip (binary, tool cannot extract archives).; Could not view the committed screenshots (docs/Screenshot 2025-06-26 153232.png, SlicerAnatomyCarve.png, Icons/*.png) or the remaining ~17 590 lines of data/Panoramix-cropped.seg.nrrd; the NRRD header was inspected only.; Did not build the extension or run Slicer, so whether vtkSlicerVolumeTextureIDHelperLogic.cxx compiles against the current Slicer/VTK (it uses vtkVolumeInputHelper.h, vtkVolumeTexture.h and mapper->AssembledInputs) and whether the 3D-view GL context is current when ComputeShader objects are created; Could not verify the licence terms of the Panoramix / CTA-abdomen dataset externally (no network access); the finding is based on the absence of any provenance or licence statement in the repository.; Did not verify the upstream repository at the exact revision 3ce2dd19c461184cf17456bdbbd84a30c6ad8f7b beyond the files provided for this review (scm_revision is 'main', a moving branch), nor that all referenced files exist at that revision.; Did not review CI/build results or previous review history for this extension.
Questions for the author: What are the origin, licence and citation terms of data/Panoramix-cropped.seg.nrrd, and do they permit redistribution inside the extension (or should the sample be removed and only referenced)?; Can the PyOpenGL dependency be avoided or installed only after an explicit user prompt, instead of at scripted-module import?; Is the number of clipping spheres intentionally limited to 32, and where is that limit enforced in the UI?; Was VolumeTextureIDHelper.zip meant to be committed?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns

Not checked: Building and running the extension inside a full 3D Slicer runtime with active GPU compute shader support (Windows/Linux)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
No malicious behavior found in the files read. The main concerns are packaging and soundness: a C++ helper module that is still the unmodified template (placeholder contributor "John Doe", NIH placeholder acknowledgement, "FooBar" widget), a PyOpenGL pip install at module import without user consent, an unexplained committed binary zip, and no bound check on the 32-sphere limit. Tests are empty. Admission-level issues (license, catalog entry) look acceptable. I did not inspect the shaders, the .ui file, the zip contents, or the full C++ logic file, so coverage is partial.
Not checked: Contents of VolumeTextureIDHelper/VolumeTextureIDHelper.zip (binary, not readable here).; The four GLSL shaders under AnatomyCarve/Resources/Shaders and the AnatomyCarve.ui file.; VolumeTextureIDHelper/Logic/vtkSlicerVolumeTextureIDHelperLogic.cxx beyond line 120 and the Widgets .cxx were only partly read.; docs/ screenshot and SlicerAnatomyCarve.png binary assets (not read; the scan hint notes a 2 MB screenshot).; Whether the sample data checksum and the raw.githubusercontent.com URL resolve; the scm_revision 'main' was not resolved to a commit, and no build, CI, or Slicer run was performed.; Whether PyOpenGL is already shipped by the targeted Slicer version, and the Slicer-version compatibility of the VTK internals used by the helper.


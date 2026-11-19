# AI review: BigImage

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/gaoyi/SlicerBigImage.git at commit `15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-19T02:55:55Z; cost $1.00

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | unknown |
| environment | unknown | blocking | blocking |
| packaging | unknown | ok | unknown |
| license | unknown | ok | unknown |
| soundness | unknown | concern | concern |
| utility | unknown | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: BigImage is a 3D Slicer extension for viewing very large whole-slide microscopy images (using tiffslide) and for H&E stain decomposition and nucleus segmentation (C++ CLIs). It also has a hidden Zarr reader/writer module. It is aimed at computational pathology users.
- **gemini**: BigImage is a 3D Slicer extension for pathologists and researchers to view multi-gigabyte whole-slide microscopy images (WSI) at multiple resolutions and perform histopathology image analysis. It provides whole-slide patch viewing via TiffSlide, stain color deconvolution (e.g., H&E separation), nucleus segmentation via level-set and mean-shift clustering, and experimental Zarr volume I/O.
- **gpt**: BigImage helps microscopy and computational histopathology users view whole-slide images larger than memory. It also provides stain decomposition, nucleus segmentation, and experimental Zarr image I/O.

## Disagreements (start here)

### D1. Unconditional pip_install("tiffslide") at module import / Slicer startup
partial; category environment; raised by gemini, gpt; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (blocking, high confidence, quote verified) [`BigImageViewer/BigImageViewer.py:17`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/BigImageViewer/BigImageViewer.py#L17): `BigImageViewer.py` calls `slicer.util.pip_install("tiffslide")` at module import time. Slicer imports all scripted loadable modules during application startup to discover and register them, so installing this extension causes `pip install tiffslide` (and its dependency tree, including `tifffile`, `imagecodecs`, and `zarr`) to run unconditionally on Slicer startup without user confirmation, even for users who never open the BigImageViewer module. This also contradicts `README.md` line 29, which states packages are installed on first use.
  ```
  try:
      from tiffslide import TiffSlide
  except ImportError:
      slicer.util.pip_install("tiffslide")
      from tiffslide import TiffSlide
  ```
  Suggestion: Move the `tiffslide` import and `pip_install("tiffslide")` out of the module top level and into `BigImageViewerLogic.installPreRequisites()` (or a lazy helper called when the user actually loads a slide), with user confirmation or a status message before installing.
- **gpt** (blocking, high confidence, quote verified) [`BigImageViewer/BigImageViewer.py:17`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/BigImageViewer/BigImageViewer.py#L17): When Slicer imports the scripted module and tiffslide is absent, it downloads and installs tiffslide and its dependencies into Slicer's shared Python environment without a prompt, including for users who never open the viewer. This can change packages used by Slicer or other extensions and can cause startup failure when installation fails.
  ```
  try:
      from tiffslide import TiffSlide
  except ImportError:
      slicer.util.pip_install("tiffslide")
      from tiffslide import TiffSlide
  ```
  Suggestion: Move dependency checks and installation to an explicitly invoked workflow, explain the dependencies and request confirmation before installing; handle refusal and installation errors.
- claude on re-check: **real: yes, blocking**: BigImageViewer/BigImageViewer.py:17-21 is at module top level: `try: from tiffslide import TiffSlide / except ImportError: slicer.util.pip_install("tiffslide")`. Slicer imports scripted modules at startup, so tiffslide and its dependencies are pip-installed without confirmation for users who never open the module. The review policy lists package installation at import or startup as a change-request item.
- gpt on re-check: **real: yes, blocking**: BigImageViewer/BigImageViewer.py:17-21 executes `from tiffslide import TiffSlide` and, on `ImportError`, `slicer.util.pip_install("tiffslide")` at module import without prompting. The installation is conditional on import failure, not unconditional on every startup; it can nevertheless affect users who never open the viewer. README.md:29 says packages are installed 'automatically on first use'. Startup-time package installation is an admission-policy concern. The exact resolved dependency tree was not inspected.
- gemini on re-check: **real: yes, blocking**: In BigImageViewer/BigImageViewer.py lines 17-21, `slicer.util.pip_install("tiffslide")` is executed at the top-level module scope when `from tiffslide import TiffSlide` raises `ImportError`. Because Slicer imports scripted loadable modules on startup, this installs packages into Slicer's shared Python environment at startup even if the user never opens the module, which violates the AGENTS.md requirement against package installation at module import or Slicer startup.

### D2. Additional packages are installed without user confirmation
single; category environment; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`NgffImageIO/NgffImageIO.py:53`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/NgffImageIO/NgffImageIO.py#L53): Volume conversion and Zarr writing call this helper and can install zarr, dask, and xarray into the shared environment without asking; the viewer similarly installs scikit-image when loading a slide. Pip may also change shared dependencies, affecting other modules.
  ```
      @staticmethod
      def installRequiredPythonPackages():
          try:
              import zarr
          except ImportError:
              slicer.util.pip_install('zarr')
  ```
  Suggestion: Offer a user-confirmed dependency setup with compatible requirements and a clear cancellation path, rather than silently invoking pip during conversion or loading.
- claude on re-check: **real: yes, minor**: NgffImageIO.py:53-66 installs zarr, dask and xarray via pip_install, called from xarrayFromVolume (l.81) and volumeFromXarray (l.126). BigImageViewer.py:1196-1199 installs scikit-image in installPreRequisites. These installs happen only when the user runs a conversion, writes Zarr or loads a slide, not at startup. There is no confirmation prompt. The packages are moderate in size and are not Slicer-bundled pins, so this is minor.
- gpt on re-check: **real: yes, major**: NgffImageIO/NgffImageIO.py:53-66 contains `slicer.util.pip_install('zarr')`, `slicer.util.pip_install('dask')`, and `slicer.util.pip_install('xarray')` on import failures without a confirmation dialog. Lines 81 and 126 call the helper from conversions, and lines 262-263 call conversion from the writer. BigImageViewer/BigImageViewer.py:1196-1199 similarly installs `scikit-image`, with the slide-loading path calling the helper at lines 904-917. Actual installed versions, sizes, and resulting dependency changes were not verified.
- gemini on re-check: **real: yes, minor**: In NgffImageIO/NgffImageIO.py lines 53-66, `installRequiredPythonPackages()` runs `slicer.util.pip_install` for `zarr`, `dask`, and `xarray` without user confirmation when called during volume conversion/writing. Similarly, BigImageViewer/BigImageViewer.py lines 1196-1199 installs `scikit-image` in `installPreRequisites()` when loading a slide. Since these happen on first use rather than at startup and are pure/standard scientific Python packages, this is a minor environment issue.

### D3. NgffImageIOFileReader.load() does not install required packages before importing xarray and zarr
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`NgffImageIO/NgffImageIO.py:209`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/NgffImageIO/NgffImageIO.py#L209): `NgffImageIOFileReader.load()` imports `xarray` and `zarr` directly without calling `NgffImageIOLogic.installRequiredPythonPackages()` first (whereas `NgffImageIOFileWriter.write()` calls `xarrayFromVolume()`, which calls `installRequiredPythonPackages()`). If a user loads a `.zarr` file via Slicer's standard Add Data dialog before ever exporting one, `import xarray` or `import zarr` will raise `ModuleNotFoundError` and the file load will fail.
  ```
        # Read zarr image file
        import xarray as xr
        import zarr
        ds = xr.open_zarr(zarr.ZipStore(filePath))
  ```
  Suggestion: Call `NgffImageIOLogic.installRequiredPythonPackages()` at the beginning of `NgffImageIOFileReader.load()` before importing `xarray` and `zarr`.
- **gpt** (minor, high confidence, quote verified) [`NgffImageIO/NgffImageIO.py:209`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/NgffImageIO/NgffImageIO.py#L209): On a fresh environment without xarray or zarr, loading fails at the imports before volumeFromXarray can reach the dependency helper. Therefore the advertised Zarr reader cannot bootstrap its own dependencies on first load.
  ```
              # Read zarr image file
              import xarray as xr
              import zarr
              ds = xr.open_zarr(zarr.ZipStore(filePath))
  
              # Convert to volume
  ```
  Suggestion: Check dependencies through the same user-consented setup before importing them and add a fresh-install reader test.
- claude on re-check: **real: yes, minor**: NgffImageIO.py:210-212 does `import xarray as xr; import zarr` inside load() before volumeFromXarray (l.215) calls installRequiredPythonPackages. On a fresh environment the load fails with ImportError. The exception is caught and logged at l.218-222, and load returns False. The reader cannot bootstrap its own dependencies. This is an ordinary bug in a secondary module.
- gpt on re-check: **real: yes, minor**: NgffImageIO/NgffImageIO.py:209-215 performs `import xarray as xr` and `import zarr` before calling `NgffImageIOLogic.volumeFromXarray(ds.image)`, whose dependency helper is at line 126. If either import fails, lines 218-222 log the exception and return False. This is a recoverable first-load functionality bug, not an admission-blocking safety issue.
- gemini on re-check: **real: yes, major**: In NgffImageIO/NgffImageIO.py lines 209-215, `NgffImageIOFileReader.load()` executes `import xarray as xr` and `import zarr` before calling `NgffImageIOLogic.volumeFromXarray(ds.image)` (which calls `installRequiredPythonPackages()`). If `xarray` or `zarr` is not yet installed, loading a `.zarr` file fails with `ModuleNotFoundError`.

### D4. Red slice view interactor observers are never removed and remain active across all Slicer modules
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`BigImageViewer/BigImageViewer.py:165`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/BigImageViewer/BigImageViewer.py#L165): In `BigImageViewerWidget.__init__`, five VTK observers are added directly to the Red slice view interactor via `interactor.AddObserver(...)` instead of `self.addObserver(...)`, and their observer tags are never stored or removed on `exit()` or `cleanup()`. Additionally, `__init__` immediately forces `lm.setLayout(6)` (Red slice only). Once the user opens `BigImageViewer` once, scrolling the mouse wheel or left-clicking and releasing in the Red slice view continues to trigger `BigImageViewer` callbacks (`onLeftButtonReleased`, `onMouseWheelForwardEvent`, etc.) even after switching to other Slicer modules.
  ```
      interactor = redView.interactorStyle().GetInteractor()
      interactor.AddObserver(vtk.vtkCommand.RightButtonPressEvent, self.onRightButtonPressed)
  
      interactor.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.onLeftButtonPressed)
      interactor.AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent, self.onLeftButtonReleased)
  
  ```
  Suggestion: Use `self.addObserver(...)` (from `VTKObservationMixin`) or store and remove the observer tags when leaving the module (`exit()`) and in `cleanup()`, and only change layout or attach Red view interactor observers when the module is active (`enter()`).
- **gpt** (minor, high confidence, quote verified) [`BigImageViewer/BigImageViewer.py:165`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/BigImageViewer/BigImageViewer.py#L165): These raw VTK observers are not tracked by VTKObservationMixin, while exit only removes the parameter-node observer and cleanup calls the mixin's removeObservers. After switching modules, red-view mouse events can still move viewer sliders and trigger slide loading; reloading the module can accumulate callbacks.
  ```
      interactor = redView.interactorStyle().GetInteractor()
      interactor.AddObserver(vtk.vtkCommand.RightButtonPressEvent, self.onRightButtonPressed)
  
      interactor.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.onLeftButtonPressed)
      interactor.AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent, self.onLeftButtonReleased)
  
  ```
  Suggestion: Track observer tags or use the observation mixin, remove view observers on exit and cleanup, and restore them on re-entry.
- claude on re-check: **real: yes, minor**: BigImageViewer.py:165-172 adds raw interactor.AddObserver callbacks in the widget __init__. Their tags are not stored. exit() (l.1032-1037) removes only the parameter-node observer, and cleanup() (l.540-544) calls self.removeObservers(), which does not cover these callbacks. onLeftButtonReleased (l.204-217) changes the slider values with no guard on whether the module is active or a slide is loaded. Red-view interaction is therefore affected after leaving the module. This is a real soundness defect but does not cause harm, so it is minor.
- gpt on re-check: **real: yes, major**: BigImageViewer/BigImageViewer.py:165-172 adds interactor observers directly, e.g. `interactor.AddObserver(vtk.vtkCommand.MouseWheelForwardEvent, self.onMouseWheelForwardEvent, 1.0)`, without saving tags. Cleanup only calls `self.removeObservers()` (lines 540-544), while exit removes the parameter-node observer (lines 1032-1037). While the observed interactor remains alive, callbacks can still run after switching modules: lines 216-217 and 223-233 change viewer controls and fit the Red view, with controls connected to patch loading at lines 404-407. This can interfere with other work, though persistence across interactor/layout replacement was not tested.
- gemini on re-check: **real: yes, major**: In BigImageViewer/BigImageViewer.py lines 165-172, `BigImageViewerWidget.__init__` adds five observers directly on `redView.interactorStyle().GetInteractor()` using `interactor.AddObserver(...)` instead of `self.addObserver(...)`, and lines 120-121 set layout to Red view only (`lm.setLayout(6)`). `cleanup()` (line 544) only calls `self.removeObservers()` from `VTKObservationMixin`, so the interactor observers are never removed and remain active when switching to other modules.

### D5. Slide loading changes CUDA visibility for the entire Slicer process
partial; category environment; raised by gemini, gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gemini** (minor, high confidence, quote verified) [`BigImageViewer/BigImageViewer.py:1214`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/BigImageViewer/BigImageViewer.py#L1214): Calling `installPreRequisites()` (which happens whenever a WSI is loaded) mutates the process-wide environment variable `CUDA_VISIBLE_DEVICES` to `"0"`, affecting any other Slicer modules or extensions running in the same Slicer process. Moreover, `BigImageViewer` does not actually use CUDA in its active code.
  ```
      os.environ["CUDA_VISIBLE_DEVICES"] = "0"
  ```
  Suggestion: Remove `os.environ["CUDA_VISIBLE_DEVICES"] = "0"` from `installPreRequisites()`.
- **gpt** (major, high confidence, quote verified) [`BigImageViewer/BigImageViewer.py:1212`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/BigImageViewer/BigImageViewer.py#L1212): Loading a slide calls installPreRequisites, which overwrites the user's CUDA visibility setting. Other GPU libraries initialized later in the same process, or child processes, may see a different GPU selection or lose access to their intended devices.
  ```
      #     slicer.util.pip_install("keras")
  
      os.environ["CUDA_VISIBLE_DEVICES"] = "0"
  ```
  Suggestion: Do not change CUDA_VISIBLE_DEVICES globally; configure any GPU-specific work locally and only if needed.
- claude on re-check: **real: yes, minor**: BigImageViewer.py:1214 `os.environ["CUDA_VISIBLE_DEVICES"] = "0"` runs in installPreRequisites, which is called on slide load (l.871, 913, 980). It overrides the user's process-wide GPU selection. Nothing in the extension uses CUDA, because the tensorflow and keras lines are commented out. It only takes effect when a slide is loaded, so the impact is limited and minor.
- gpt on re-check: **real: yes, major**: BigImageViewer/BigImageViewer.py:1214 sets `os.environ["CUDA_VISIBLE_DEVICES"] = "0"`; slide loading calls `self.logic.installPreRequisites()` at lines 904-917. This overwrites any existing selection process-wide, potentially affecting later GPU initialization and child processes, though already initialized GPU runtimes need not change. Installation or import failures earlier in the helper can prevent the assignment.
- gemini on re-check: **real: yes, minor**: In BigImageViewer/BigImageViewer.py line 1214, `BigImageViewerLogic.installPreRequisites()` sets `os.environ["CUDA_VISIBLE_DEVICES"] = "0"`, mutating the process-wide environment variable whenever a slide is loaded.

### D6. Undefined variable `key` in NgffImageIOLogic.xarrayFromVolume raises NameError when volume has attributes
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`NgffImageIO/NgffImageIO.py:115`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/NgffImageIO/NgffImageIO.py#L115): In `NgffImageIOLogic.xarrayFromVolume()`, the loop variable is `attributeName`, but the dictionary assignment uses an undefined variable `key` (`attrs[key] = ...`). Whenever a `volumeNode` has any MRML attributes (`volumeNode.GetAttributeNames()` is non-empty), `xarrayFromVolume` (and thus `NgffImageIOFileWriter.write`) will fail with `NameError: name 'key' is not defined`.
  ```
          attrs = {"xyzToPhysicalTransform": np.flip(xyzToLpsMatrix)}
          for attributeName in volumeNode.GetAttributeNames():
              attrs[key] = volumeNode.GetAttribute(attributeName)
          data_array = xr.DataArray(array_view, dims=dims, coords=coords, attrs=attrs)
  ```
  Suggestion: Replace `attrs[key] = volumeNode.GetAttribute(attributeName)` with `attrs[attributeName] = volumeNode.GetAttribute(attributeName)`.
- **gpt** (minor, high confidence, quote verified) [`NgffImageIO/NgffImageIO.py:115`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/NgffImageIO/NgffImageIO.py#L115): For any volume with at least one MRML attribute, key is undefined and conversion raises NameError. The Zarr writer catches the exception and fails to save the volume.
  ```
          attrs = {"xyzToPhysicalTransform": np.flip(xyzToLpsMatrix)}
          for attributeName in volumeNode.GetAttributeNames():
              attrs[key] = volumeNode.GetAttribute(attributeName)
          data_array = xr.DataArray(array_view, dims=dims, coords=coords, attrs=attrs)
  ```
  Suggestion: Use attributeName as the dictionary key and test saving volumes with attributes.
- claude on re-check: **real: yes, minor**: NgffImageIO.py:116-117 loops with `for attributeName in ...` but assigns `attrs[key] = ...`. `key` is undefined in xarrayFromVolume, so a NameError is raised whenever the volume has any MRML attribute. The writer then fails for that volume. This is a real bug in the secondary Zarr export feature. It is not a safety issue, and volumes without attributes still work, so it is minor.
- gpt on re-check: **real: yes, minor**: NgffImageIO/NgffImageIO.py:115-118 has `for attributeName in volumeNode.GetAttributeNames():` followed by `attrs[key] = volumeNode.GetAttribute(attributeName)`, with no local or module-level definition of `key` in this path. For a node with attributes this raises NameError; the writer invokes the conversion at lines 262-263 and catches the exception and returns False at lines 271-275. This is a conditional, reported save failure rather than an admission-blocking defect.
- gemini on re-check: **real: yes, major**: In NgffImageIO/NgffImageIO.py lines 116-117, the loop `for attributeName in volumeNode.GetAttributeNames():` assigns `attrs[key] = volumeNode.GetAttribute(attributeName)`, referencing an undefined variable `key` and raising `NameError` whenever a volume node has any MRML attributes.


## Findings from some reviewers

### CLI modules call abort() / raise(SIGABRT) on error, which can crash Slicer if run as shared libraries
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`NucleusSegmentation/include/utilitiesIO.hxx:34`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/NucleusSegmentation/include/utilitiesIO.hxx#L34): `NucleusSegmentation` is built via `SEMMacroBuildCLI` (which builds both a shared-library CLI module and an executable). Throughout `NucleusSegmentation` (`utilitiesIO.hxx`, `SFLSSegmentor2D.hxx`, `BinaryMaskAnalysisFilter.cxx`, `HAndEImageAnalysisFilter.cxx`, `HematoxylinImageSegmentationFilter.cxx`) and `ColorDecomposition.cxx` (line 69), error handling calls `raise(SIGABRT)` or `abort()`. If the CLI is executed in-process as a shared library (or if an invalid/corrupt image or parameter is encountered), calling `abort()` / `raise(SIGABRT)` terminates the entire Slicer application instead of returning `EXIT_FAILURE`.
  ```
        catch ( itk::ExceptionObject &err)
          {
            std::cerr<< "ExceptionObject caught !" << std::endl;
            std::cerr<< err << std::endl;
            raise(SIGABRT);
          }
  ```
  Suggestion: Throw an exception (`itkGenericExceptionMacro` or `std::runtime_error`) and catch it in `main()` (the CLI entry point) to return `EXIT_FAILURE` cleanly instead of calling `abort()` or `raise(SIGABRT)`.

### Nucleus segmentation receives inverted zoom-dependent pixel size
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`BigImageViewer/BigImageViewer.py:1006`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/BigImageViewer/BigImageViewer.py#L1006): At reduced magnification this passes a smaller microns-per-pixel value, although the displayed patch covers more physical area per pixel. The viewer itself computes spacing using the reciprocal ratio at lines 719–720, and the nucleus pipeline uses mpp for physical size filtering, so segmentation can change incorrectly with zoom.
  ```
      parameters['outputHImage'] = volumeNode.GetID()
      parameters['outputImageName'] = nucleusLabelImageNode.GetID()
      parameters['mpp'] = self.MPP/self.objectiveMagnificationMax*float(self.ui.ObjectiveMagnificationSlicerWidget.value)
      slicer.cli.run( slicer.modules.nucleussegmentation, None, parameters, wait_for_completion=True )
  ```
  Suggestion: Derive mpp from the patch's actual physical spacing and test segmentation at several magnifications, including whole-slide view.

### Self-tests in BigImageViewer, ColorDecomposition, and NucleusSegmentation are left over from template and fail
minor; soundness; raised by gemini, gpt
- **gemini** (minor, high confidence, quote verified, other lines) [`BigImageViewer/BigImageViewer.py:57`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/BigImageViewer/BigImageViewer.py#L57): In `BigImageViewerTest.test_BigImageViewer1`, `registerSampleData()` is commented out, so `'BigImageViewer1'` is never registered with `SampleData`. Running the self-test will fail when trying to download `'BigImageViewer1'`, and `BigImageViewerLogic.process()` only runs the template `thresholdscalarvolume` CLI rather than testing any `BigImageViewer` functionality. Furthermore, the C++ tests in `ColorDecomposition/Testing/Cxx/CMakeLists.txt` and `NucleusSegmentation/Testing/Cxx/CMakeLists.txt` pass `--sigma 2.5` (from the template CLI) which neither CLI accepts.
  ```
      import SampleData
      #registerSampleData()
      inputVolume = SampleData.downloadSample('BigImageViewer1')
  ```
  Suggestion: Update the Python and C++ tests to pass valid arguments and sample data for the actual modules.
- **gpt** (minor, high confidence, quote verified) [`BigImageViewer/BigImageViewer.py:1472`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/BigImageViewer/BigImageViewer.py#L1472): The sample registration is commented out, so the test cannot normally retrieve BigImageViewer1. The remainder exercises template thresholding instead of loading and navigating a whole-slide image, leaving the primary viewer workflow without useful regression coverage.
  ```
      # Get/create input data
  
      import SampleData
      #registerSampleData()
      inputVolume = SampleData.downloadSample('BigImageViewer1')
  ```
  Suggestion: Register a suitable small test slide or provide a local fixture and exercise loading, pan, zoom, and cleanup.

### Whole-slide preview can read an entire unpyramided image into memory
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified, other lines) [`BigImageViewer/BigImageViewer.py:312`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/BigImageViewer/BigImageViewer.py#L312): The initial whole-slide preview reads the entire selected pyramid level before resizing. For a very large image without a sufficiently small pyramid level, this can allocate gigabytes and freeze or exhaust memory despite the module's stated purpose of viewing images too large to load.
  ```
      level = self.BigRGBAImageLevelToLoad
      downsample = float(self.level_downsamples[level])
      levelWidth = int(self.WSISizesXAtAllLevels[level])
      levelHeight = int(self.WSISizesYAtAllLevels[level])
      q = self.getRegionFromFileAsRGBNumpyArray(self.BigRGBAImagePathname, level, 0, 0, levelWidth, levelHeight)
  ```
  Suggestion: Use a bounded thumbnail or tiled, incrementally downsampled preview and test on single-level large images.

### 12 MB screenshot committed to repository
info; packaging; raised by gemini; **quote not found in source**
- **gemini** (info, high confidence, quote quote not found) [`CMakeLists.txt:12`](https://github.com/gaoyi/SlicerBigImage/blob/15af77d3d348e9a3dce63131ca1a1ce9ddfcaea6/CMakeLists.txt#L12): The repository commits a 12 MB screenshot (`Screenshots/1.png`) directly in the git tree, which bloats repository clones.
  ```
  - [info] Large files not available to read: Screenshots/1.png (12 MB)
  ```
  Suggestion: Compress the screenshot or host large screenshots outside the main source tree (e.g. in a separate documentation branch or release asset).


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
The source has no signs of malicious behavior, network transmission, or unsafe execution. The main problem is environmental. BigImageViewer.py runs `pip_install("tiffslide")` at module top level, so a package install can happen when Slicer loads the module, without user consent. Other issues are lower severity. NgffImageIO has bugs (undefined `key` in the attribute loop, and `canLoadFile` always returns True). BigImageViewer has dead or broken code paths (`numpy.float`, an undefined Keras model, and CLI parameters that are not in the XML). The widget makes global changes in its constructor and never removes its interactor observers. The catalog entry uses `scm_revision: main`, a moving branch, so I could not review a pinned commit. The license is the Slicer BSD-style license, which is acceptable.
Not checked: Compilation of the C++ CLI modules, and whether they build on all platforms; Contents of the unread C++ headers and sources: SFLS*, Meanshift*, BinaryMaskAnalysisFilter.cxx, lib/ColorDecomposition.cxx, and the test .cxx files; The BigImageViewer.ui file and the binary resources; Screenshots/1.png (12 MB) and the test data files; Whether the NgffImageIO reader and writer are actually registered with Slicer at load time; The commit pointed to by 'main' versus the stated commit 15af77d

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
BigImage provides whole-slide microscopy viewing (`BigImageViewer`), histopathology stain deconvolution (`ColorDecomposition`), H&E nucleus segmentation (`NucleusSegmentation`), and experimental Zarr image I/O (`NgffImageIO`). It is licensed under the 3D Slicer license and has no safety or malicious-code concerns. However, `BigImageViewer/BigImageViewer.py` calls `slicer.util.pip_install("tiffslide")` at module import time (lines 17-21), which executes during Slicer startup for all users without confirmation. This is a blocking environment issue under the Slicer Extensions Index review policy. Several non-blocking soundness bugs in `NgffImageIO.py` and `BigImageViewer.py` should also be addressed.

🔴 Do not merge yet: `BigImageViewer/BigImageViewer.py` installs `tiffslide` via `pip_install` at module import / Slicer startup.
Not checked: Binary test data files under ColorDecomposition/Data and NucleusSegmentation/Data; Screenshots/1.png (12 MB binary image not available in text viewer)
Questions for the author: Can `slicer.util.pip_install("tiffslide")` in `BigImageViewer/BigImageViewer.py` be moved from the top-level module import into `BigImageViewerLogic.installPreRequisites()` so packages are not installed during Slicer startup?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The viewer installs a Python package during module import, changing Slicer's shared environment without consent even for users who never open it. Other unprompted installations and process-wide CUDA changes also need attention. Static inspection found several non-blocking correctness issues in image I/O, segmentation scale, and viewer lifecycle. Distribution permission for adapted third-party code and the catalog's live source revision could not be independently verified. 🔴 Do not merge yet: remove startup installation; review remains incomplete pending those licensing and revision checks.
Not checked: Could not independently access the live catalog repository, resolve main to the supplied commit, or compare an earlier catalog entry and review baseline.; Could not build or run the extension, Slicer tests, package installation, or automated CI checks.; Could not inspect the external ImageJ plugin's applicable license and provenance, or the terms and payloads of dynamically installed Python dependencies; confirm distribution permission for the adapted implementation.; The large screenshot binary and example-slide contents were not inspected.
Questions for the author: What are the applicable distribution terms for the ImageJ color-deconvolution code identified as the source of the adapted implementation, and where are its required notices included?


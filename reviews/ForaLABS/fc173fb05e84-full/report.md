# AI review: ForaLABS

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/HarlleyHauradou/SlicerForaLABS.git at commit `fc173fb05e84c5aa9c5a973d3bc19b1061e64c42`
- Context: pull request 2318 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-15T02:09:57Z; cost $0.57

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | ok | ok | blocking |
| environment | minor | ok | minor |
| packaging | blocking | blocking | blocking |
| license | ok | ok | ok |
| soundness | concern | concern | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: ForaLABS provides two Slicer scripted modules for micro-CT of foraminifera. Measures computes surface area, volume, S/V, genus-based pore count and ray-cast wall thickness from a segment mesh and exports a PDF report. ImportTXM reads Zeiss .txm files and saves them as NRRD.
- **gemini**: ForaLABS provides 3D Slicer modules for researchers analyzing micro-CT scans of foraminifera and other porous structures. It includes an importer for ZEISS TXM reconstructed volume files (`ImportTXM`) and a morphometric analysis module (`Measures`) that cleans surface meshes, computes pore counts via topological genus, surface area, volume, and ray-cast wall thickness, and exports PDF reports.
- **gpt**: ForaLABS provides micro-CT tools for researchers analyzing foraminifera and other porous specimens. It imports Zeiss TXM volumes and computes mesh-based pore, geometry, and thickness measurements.

## Disagreements (start here)

### D1. PDF export replaces an existing report without warning
severity dispute; category safety; raised by claude, gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **claude** (minor, medium confidence, quote verified) [`ForaLABS/Measures.py:583`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/Measures.py#L583): export_results always writes MAR_ForaLABS.pdf in the chosen folder and overwrites any existing file without asking. Missing selections use assert, which gives poor user feedback. Segment and volume names are inserted into HTML unescaped.
  ```
  pdfPath = os.path.join(outDir, "MAR_ForaLABS.pdf")
  ```
  Suggestion: Use a save dialog or confirm before overwriting. Replace asserts with user messages and html.escape the names.
- **gpt** (blocking, high confidence, quote verified) [`ForaLABS/Measures.py:581`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/Measures.py#L581): The UI asks only for a directory, then uses the same fixed PDF filename every time. Exporting another specimen to that directory can overwrite a previous report without an overwrite confirmation; the user is not choosing the existing file itself.
  ```
          if not os.path.isdir(outDir):
              os.makedirs(outDir, exist_ok=True)
          pdfPath = os.path.join(outDir, "MAR_ForaLABS.pdf")
          self._save_html_to_pdf(html, pdfPath)
  ```
  Suggestion: Use a save-file dialog with overwrite confirmation or generate unique report filenames.
- claude on re-check: **real: yes, minor**: Measures.py:583 uses a fixed filename "MAR_ForaLABS.pdf" in the user-chosen folder, with no overwrite check. The file is a derived report in a folder the user picked, so there is no concrete path to harm. This is minor usability, not safety-blocking.
- gpt on re-check: **real: yes, blocking**: ForaLABS/Measures.py:221-226 selects only a directory: `outDir = qt.QFileDialog.getExistingDirectory(None, "Choose output folder")`. Lines 581-584 then use `pdfPath = os.path.join(outDir, "MAR_ForaLABS.pdf")` and `self._save_html_to_pdf(html, pdfPath)` with no existence check. Lines 557-559 and 571-575 direct QPrinter to that path and print. Re-export into the same folder can destroy a previous report without confirmation; this concrete unintended data loss is blocking under the safety policy. The checked-in CMake packaging is broken (ForaLABS/CMakeLists.txt:2-7), so normal catalog reachability is conditional on repair; the source can also be manually loaded. No runtime test was possible.
- gemini on re-check: **real: yes, minor**: In ForaLABS/Measures.py lines 578-586, `export_results(self, outDir, include=None)` constructs `pdfPath = os.path.join(outDir, "MAR_ForaLABS.pdf")` and calls `self._save_html_to_pdf(html, pdfPath)` without checking if the file already exists or prompting the user. Also at lines 183-184, 222, 248-249, 269-270, 299-300 `assert` is used for input validation, and in `render_metrics_html` (lines 480-510) volume/segment names are interpolated into HTML for QTextDocument. However, writing a fixed report name `MAR_ForaLABS.pdf` into a user-selected export folder when the user clicks "Export Report (PDF)" is an ordinary usability/soundness issue, not a blocking safety vulnerability.

### D2. TXM conversion silently overwrites an existing NRRD
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`ForaLABS/ImportTXM.py:639`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/ImportTXM.py#L639): The destination is constructed from the input basename and output directory at lines 631–633; when no directory is selected it defaults to the TXM directory. Importing a TXM when a same-named NRRD already exists writes over that file without checking or asking, potentially destroying unrelated or earlier image data. This path is reachable when the source module is loaded manually or packaging is repaired.
  ```
          writer = sitk.ImageFileWriter()
          writer.SetFileName(nrrdPath)
          writer.UseCompressionOn()
          writer.Execute(img)
  ```
  Suggestion: Let users choose the output filename and explicitly confirm replacement, or generate a noncolliding filename and use an atomic write.
- claude on re-check: **real: yes, minor**: ImportTXM.py:631-642 writes <safeBase>.nrrd into outDir with no existence check. outDir is user-selected and defaults to the TXM's folder (lines 200-202). The filename is sanitized, so there is no path traversal. The file is a derived conversion of the user's own input, so overwriting is a minor usability issue, not blocking.
- gpt on re-check: **real: yes, blocking**: ForaLABS/ImportTXM.py:200-202 defaults the output directory to the input directory: `outDir = os.path.dirname(txmPath)`. Lines 631-633 derive `nrrdPath = os.path.join(outDir, f"{safeBase}.nrrd")`, and lines 639-642 call `writer.SetFileName(nrrdPath)` and `writer.Execute(img)` without an overwrite check; the action calls it at line 231. An existing, potentially unrelated NRRD can be destroyed without selecting that file or consenting to replacement. This is blocking data loss. Normal packaged reachability is conditional on fixing the missing module scripts in ForaLABS/CMakeLists.txt:2-7; manual loading is another path. No runtime test was possible.
- gemini on re-check: **real: yes, minor**: In ForaLABS/ImportTXM.py lines 193-203 and 626-646, `onImport` defaults `outDir` to `os.path.dirname(txmPath)` if no output directory is specified, and `saveAndLoadNRRD` writes `nrrdPath = os.path.join(outDir, f"{safeBase}.nrrd")` via `sitk.ImageFileWriter().Execute(img)` without checking whether `<safeBase>.nrrd` already exists. While real, converting `<name>.txm` to `<name>.nrrd` in the chosen or source folder on user-initiated import is expected converter behavior / minor UX concern (lack of overwrite confirmation), not a blocking safety issue.

### D3. Thickness export reuses an image for different selected inputs
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`ForaLABS/Measures.py:883`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/Measures.py#L883): The cached image is reused without checking the selected segment, segmentation, voxel size, or cleaning parameters. After changing inputs or recomputing with thickness unchecked, users can export or view the previous specimen's map as if it belonged to the current selection. This is non-blocking correctness feedback.
  ```
      def export_thickness_nrrd(self, segNode, wallSegmentId, outPath, voxel_mm=0.003, minDiamPct=10.0, removeUnref=True):
          try:
              # if we already have it, save directly
              if self.last_thick_img is not None:
                  sitk.WriteImage(self.last_thick_img, outPath)
                  return True, outPath
  ```
  Suggestion: Invalidate the cache on input or parameter changes, or key it to all relevant inputs and their modification times.
- claude on re-check: **real: yes, minor**: Measures.py:886-888 writes the cached last_thick_img without checking that the segment, segmentation or parameters match. Line 393 and line 874 set the cache from different runs. A stale map can be exported or shown (line 903) after the inputs change. This is a real soundness bug, but it is ordinary and non-blocking, and the severity is closer to minor than major.
- gpt on re-check: **real: yes, major**: ForaLABS/Measures.py:883-888 checks only `if self.last_thick_img is not None:` and then calls `sitk.WriteImage(self.last_thick_img, outPath)`, without comparing the current inputs or settings. Lines 298-315 and 900-913 similarly reuse the cache for slice display. Lines 344 and 386-393 show the cached image is updated only when thickness is computed, so computing a different selection with thickness unchecked retains the previous image. A user may unknowingly export or view the wrong specimen's map; this is major but non-blocking correctness feedback, not a demonstrated safety harm.
- gemini on re-check: **real: yes, major**: In ForaLABS/Measures.py lines 883-888 (`export_thickness_nrrd`) and lines 900-912 (`show_thickness_in_slices`), `self.last_thick_img` is checked (`if self.last_thick_img is not None:`) and reused directly without verifying whether `segNode`, `wallSegmentId`, `voxel_mm`, `minDiamPct`, or `removeUnref` changed since `self.last_thick_img` was cached, and `compute_metrics` (lines 387-393) does not clear `self.last_thick_img` when `need_thickness` is False. This can cause stale thickness maps from a previous specimen or parameter set to be exported or displayed.

### D4. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (ok, blocking, ok)**
Ratings: claude ok, gemini ok, gpt blocking
- claude on re-check: **rating ok**: I searched for pip_install, subprocess, eval, exec, pickle, network calls and deletion calls. The only hit is slicer.util.pip_install("olefile") in ImportTXM.py:363-367, inside ensurePackages, a small package installed on demand. I found no network transmission, no code download or execution, and no deletion. The overwrite cases (D1, D2) write derived files to user-chosen folders and are not safety blockers.
- gpt on re-check: **rating blocking**: The blocking rating is supported by the two independent unintended-overwrite paths. ForaLABS/Measures.py:221-226 chooses a folder and lines 583-584 use `pdfPath = os.path.join(outDir, "MAR_ForaLABS.pdf")` and `self._save_html_to_pdf(html, pdfPath)` without confirmation. ForaLABS/ImportTXM.py:631-642 constructs a same-basename NRRD and calls `writer.Execute(img)` without checking for an existing file; lines 200-202 default to the source folder. Both can destroy existing user data when their source modules are used. The checked-in CMake references a missing ForaLABS.py instead of installing these scripts (ForaLABS/CMakeLists.txt:2-7), so their catalog reachability depends on packaging repair or manual loading. Inspected both module actions, write paths, packaging and repository-wide searches for network, execution and file operations; did not run code, verify the stated commit hash, inspect external dependency payloads, or perform an exhaustive safety audit.
- gemini on re-check: **rating ok**: Checked ForaLABS/Measures.py and ForaLABS/ImportTXM.py. There is no malicious behavior, unauthorized network transmission, command injection, or unsafe deserialization. The two file-overwrite findings (D1: writing `MAR_ForaLABS.pdf` in the user-chosen export folder; D2: writing `<txm_basename>.nrrd` when converting a `.txm` file) are ordinary UX/soundness behaviors triggered by explicit user export/import actions, not blocking safety defects.


## Findings all reviewers agree on

### CMake installs nonexistent ForaLABS.py and omits the real module scripts
blocking; packaging; raised by claude, gemini, gpt
- **claude** (blocking, medium confidence, quote verified) [`ForaLABS/CMakeLists.txt:5`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/CMakeLists.txt#L5): The ForaLABS/ directory has no ForaLABS.py. The actual modules, Measures.py and ImportTXM.py, are not listed in the CMake script list. slicerMacroBuildScriptedModule will fail or produce an extension with no loadable modules. The README's installation route (additional module paths) does not apply to catalog users.
  ```
  set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    )
  ```
  Suggestion: Call slicerMacroBuildScriptedModule once per module (Measures and ImportTXM) with its own NAME and SCRIPTS. Remove the ForaLABS.py references, including the slicer_add_python_unittest call. Put each module's resources in its own call.
- **gemini** (blocking, high confidence, quote verified) [`ForaLABS/CMakeLists.txt:2`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/CMakeLists.txt#L2): `ForaLABS/CMakeLists.txt` sets `MODULE_NAME` to `ForaLABS` and lists `${MODULE_NAME}.py` (`ForaLABS.py`) in `MODULE_PYTHON_SCRIPTS` and `slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)`. However, `ForaLABS.py` does not exist in the repository; the actual scripted modules are `ImportTXM.py` and `Measures.py`, neither of which is installed by CMake. As a result, configuring/building the extension via CMake will fail to find `ForaLABS.py` and neither `ImportTXM` nor `Measures` will be packaged into the extension.
  ```
  set(MODULE_NAME ForaLABS)
  
  #-----------------------------------------------------------------------------
  set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    )
  ```
  Suggestion: Either split `ImportTXM` and `Measures` into their own module subdirectories with their own `CMakeLists.txt`, or update `ForaLABS/CMakeLists.txt` to build and install `ImportTXM.py` and `Measures.py` (and reference an existing script in `slicer_add_python_unittest`), removing the nonexistent `ForaLABS.py`.
- **gpt** (blocking, high confidence, quote verified) [`ForaLABS/CMakeLists.txt:2`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/CMakeLists.txt#L2): The repository listing has no ForaLABS/ForaLABS.py; it has Measures.py and ImportTXM.py instead. The scripted-module macro therefore refers to a nonexistent script, and neither actual module is registered for packaging, so the extension cannot be built and delivered as intended.
  ```
  set(MODULE_NAME ForaLABS)
  
  #-----------------------------------------------------------------------------
  set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    )
  ```
  Suggestion: Configure separate scripted modules for Measures and ImportTXM, with the correct scripts, resources, and tests, then build and install the extension.

### Thickness map volume and mesh colormap are filled with a single constant mean value
major; soundness; raised by claude, gemini, gpt
- **claude** (minor, medium confidence, quote verified) [`ForaLABS/Measures.py:831`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/Measures.py#L831): The thickness volume is the mean value written into every voxel of the mask, so it is not a spatial map. The README describes a Maurer/medial-distance method, which the code does not use. export_thickness_nrrd writes the cached last_thick_img whenever it exists, even if the segment or voxel size has changed. The same applies to show_thickness_in_slices. Mesh vertices are colored from this constant volume.
  ```
  thick_vol = np.zeros_like(mask_arr, dtype=np.float32)
              thick_vol[mask_arr > 0] = stats["mean_mm"]
  ```
  Suggestion: Store per-vertex thickness and rasterize it, or describe the output accurately. Invalidate the cache when inputs change, and update the README.
- **gemini** (major, high confidence, quote verified) [`ForaLABS/Measures.py:826`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/Measures.py#L826): In `_thickness_map_medial_from_poly`, after computing per-vertex ray-cast thickness values, `thick_vol` is filled uniformly with the single scalar `stats["mean_mm"]` at all non-zero mask voxels. Consequently, the exported thickness NRRD volume, the slice view overlay, and the 3D mesh colormap produced by `_paint_poly_with_thickness` (which samples `thick_img` at vertex coordinates) all contain a constant value (or 0 where rounding misses the mask) rather than a spatial thickness map.
  ```
          # Cria imagem de espessura para visualização (opcional)
          # Voxeliza e preenche com valor médio
          try:
              mask, spacing, origin, shape = self._voxelize_poly_solid(poly, voxel_mm=float(voxel_mm))
              mask_arr = sitk.GetArrayFromImage(mask)
              thick_vol = np.zeros_like(mask_arr, dtype=np.float32)
  ```
  Suggestion: Store the per-vertex ray-cast distances directly as a point scalar array on the `vtkPolyData` for 3D mesh coloring, and interpolate or splat local thickness values into the voxel grid if a volumetric thickness map is needed.
- **gpt** (major, high confidence, quote verified, other lines) [`ForaLABS/Measures.py:45`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/Measures.py#L45): All occupied voxels receive the same global mean; the mesh coloring samples this image. The advertised map and exported NRRD therefore do not encode spatially varying thickness, which can mislead researchers interpreting local variation. This is non-blocking correctness feedback under the index policy.
  ```
          try:
              mask, spacing, origin, shape = self._voxelize_poly_solid(poly, voxel_mm=float(voxel_mm))
              mask_arr = sitk.GetArrayFromImage(mask)
              thick_vol = np.zeros_like(mask_arr, dtype=np.float32)
              thick_vol[mask_arr > 0] = stats["mean_mm"]
  ```
  Suggestion: Compute spatially assigned local thickness values, validate them against known geometries, and align the documentation with the implemented method.


## Findings from some reviewers

### Tests do not exercise the advertised calculations or import
minor; utility; raised by claude, gpt
- **claude** (info, medium confidence, quote verified) [`ForaLABS/Measures.py:1048`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/Measures.py#L1048): MeasuresTest is a placeholder and the Testing/Python CMake is commented out. The pore count is a genus-based proxy that depends on mesh quality. No validation is provided.
  ```
  class MeasuresTest(ScriptedLoadableModuleTest):
      def runTest(self):
          self.setUp(); self.test_All()
      def test_All(self):
          self.delayDisplay("Measures mesh-only test placeholder…"); self.delayDisplay("OK")
  ```
  Suggestion: Add a synthetic torus or shell test and sample data, and document the limits of the pore-count proxy.
- **gpt** (minor, high confidence, quote verified) [`ForaLABS/Measures.py:1048`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/Measures.py#L1048): The Measures test only displays messages; the TXM test similarly skips when its sample path is empty. Consequently neither analytic correctness nor TXM conversion is checked by these tests. This is non-blocking feedback.
  ```
  class MeasuresTest(ScriptedLoadableModuleTest):
      def runTest(self):
          self.setUp(); self.test_All()
      def test_All(self):
          self.delayDisplay("Measures mesh-only test placeholder…"); self.delayDisplay("OK")
  ```
  Suggestion: Add small synthetic meshes with known measures and a redistributable TXM fixture for conversion and metadata tests.

### pip_install of olefile without user confirmation
minor; environment; raised by claude, gpt
- **claude** (minor, medium confidence, quote verified) [`ForaLABS/ImportTXM.py:365`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/ImportTXM.py#L365): Clicking Import silently installs olefile into Slicer's shared Python. The package is small, but the user is not asked first. The test also calls ensurePackages.
  ```
              import olefile  # noqa: F401
          except Exception:
              slicer.util.pip_install("olefile")
  ```
  Suggestion: Ask for confirmation with a dialog before installing, and document the dependency.
- **gpt** (minor, high confidence, quote verified) [`ForaLABS/ImportTXM.py:363`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/ImportTXM.py#L363): On the first TXM import, if olefile cannot be imported, pip modifies Slicer's shared Python environment without a confirmation dialog. This is triggered by an explicit import action rather than startup; the UI only posts a status message.
  ```
      def ensurePackages(self):
          try:
              import olefile  # noqa: F401
          except Exception:
              slicer.util.pip_install("olefile")
  ```
  Suggestion: Ask before installing and handle a declined or failed installation explicitly.

### OLE file handle is not closed if reading an image stream raises an exception
info; soundness; raised by gemini
- **gemini** (info, high confidence, quote verified) [`ForaLABS/ImportTXM.py:215`](https://github.com/HarlleyHauradou/SlicerForaLABS/blob/fc173fb05e84c5aa9c5a973d3bc19b1061e64c42/ForaLABS/ImportTXM.py#L215): `readTXM` reads the entire `.txm` OLE image stack into memory (`vol = np.empty((int(n_imgs), int(height), int(width)), dtype=np_dtype)`) without closing `ole` if an exception occurs during slice reading (lines 488-493). Using a `with olefile.OleFileIO(txmPath) as ole:` context manager would ensure the file handle is always closed on error.
  ```
              self._msg(f"Reading TXM (OLE): {txmPath}", 15)
              arr, meta = self.logic.readTXM(txmPath)
              if arr is None:
                  raise RuntimeError("Failed to read the .txm file")
  ```
  Suggestion: Use `with olefile.OleFileIO(txmPath) as ole:` in `readTXM` so the OLE file is guaranteed to close even if a stream is missing or corrupted.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
The extension's CMake build is broken. ForaLABS/CMakeLists.txt names the module ForaLABS and installs ForaLABS.py, which does not exist. The real modules, Measures.py and ImportTXM.py, are never installed or registered. The extension would fail at configure time or ship no working modules. Other points:
- ImportTXM runs pip_install("olefile") without asking.
- The thickness "map" is a constant mean value, which the README does not make clear.
- A stale cached thickness image can be exported.
- The license is Apache-2.0, which is fine.
- The catalog entry uses scm_revision "main", which is acceptable, and the build_dependencies match EXTENSION_DEPENDS ("NA").
- I found no data exfiltration or malicious behavior.
Recommendation: 🔴 Do not merge yet, because of the packaging defect.
Not checked: Contents of the .ui and HTML resource files, which I did not read; Whether the main branch head matches commit fc173fb; Runtime behavior inside Slicer; Binary icon and screenshot contents

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
ForaLABS is a well-documented extension for importing Zeiss `.txm` micro-CT volumes and computing morphometric measurements (surface area, volume, genus-based pore count, and wall thickness) on segmented foraminifera shells. It has no safety or environment concerns and is licensed under Apache-2.0.

However, there is a blocking packaging defect in `ForaLABS/CMakeLists.txt`: it lists a nonexistent `ForaLABS.py` script in `MODULE_PYTHON_SCRIPTS` and `slicer_add_python_unittest`, while omitting the actual module scripts (`ImportTXM.py` and `Measures.py`). Additionally, in `Measures.py`, the volumetric thickness map is filled with the single constant mean value rather than local thickness measurements.

🔴 Do not merge yet: fix `ForaLABS/CMakeLists.txt` so that `ImportTXM.py` and `Measures.py` are installed and `ForaLABS.py` is removed.
Not checked: Runtime execution of the modules inside 3D Slicer with sample .txm files or segmentation data.
Questions for the author: In `Measures._thickness_map_medial_from_poly`, was `thick_vol[mask_arr > 0] = stats["mean_mm"]` intended as a temporary placeholder before implementing spatial per-vertex/per-voxel thickness mapping?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The examined source has a broken module build and two output paths that can silently overwrite existing user files. The thickness map and cache also have non-blocking correctness issues. The catalog selects the moving main branch; the supplied commit was not independently resolved. 🔴 Do not merge yet: fix packaging and unintended overwrites, and verify the selected revision.
Not checked: No code was executed; Slicer builds, loading, UI behavior, output writes, and tests were not run.; The supplied commit fc173fb05e84c5aa9c5a973d3bc19b1061e64c42 and the catalog's main branch were not independently resolved against the remote repository; the exact checked-out revision is not independently verified.; The Extensions Index PR checklist, CI results, previous entry or reviewed baseline were not available.; The olefile package and its transitive metadata and distribution license were not inspected; network access and package installation were unavailable.; Binary icon and screenshot contents were not examined.


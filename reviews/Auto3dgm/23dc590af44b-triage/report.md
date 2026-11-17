# AI review: Auto3dgm

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/ToothAndClaw/SlicerAuto3dgm at commit `23dc590af44bdb2cafb460cdc1728cf5b43cce9d`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-17T03:32:54Z; cost $0.08

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | concern |
| environment | concern | ok | minor |
| packaging | concern | ok | minor |
| license | concern | ok | concern |
| soundness | concern | ok | concern |
| utility | minor | ok | concern |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: Auto3dgm brings the Auto3dgm automated 3D geometric-morphometrics pipeline (farthest-point subsampling, pairwise Procrustes/assignment alignment, globalized alignment) into 3D Slicer for comparative analysis of collections of 3D surface meshes, plus a small web-based mesh viewer CLI module. It targets researchers in evolutionary biology/morphometrics rather than clinicians.
- **flash-lite**: Auto3dgm allows for comparative analysis of 3D digital models representing biological surfaces using fully automated landmark placement and alignment within 3D Slicer.
- **haiku**: Auto3dgm is a 3D Slicer scripted module that wraps the Auto3dgm automated 3D geometric morphometrics pipeline (subsampling, pairwise and globalized alignment, landmark and mesh export) and includes a small web mesh viewer as a CLI module. It is for morphometrics researchers who want to align and compare batches of biological surface meshes inside Slicer.

## Disagreements (start here)

### D1. Committed prebuilt binary extension module for CPython 3.6 Windows, unused by the code
single; category packaging; raised by deepseek
- **deepseek** (major, high confidence, quote no quote) [`Auto3dgm/auto3dgm_nazar/lap_windows/_lapjv.cp36-win_amd64.pyd`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/lap_windows/_lapjv.cp36-win_amd64.pyd): A 99 KB compiled .pyd for CPython 3.6 win_amd64 is committed to the repository and installed with the extension (Auto3dgm/CMakeLists.txt installs the whole auto3dgm_nazar directory). Current Slicer releases use Python 3.9+, so the binary cannot load, and a search shows nothing in the extension imports lap_windows (only its own __init__.py/lapmod.py/tests reference it). Committed binaries of unverified provenance that are not needed should not ship; the upstream 'lap' package is the normal source.
  Suggestion: Delete lap_windows (or exclude it from the install rule) and, if the solver is needed, depend on the upstream package installed on demand.

### D2. Long-running alignment runs synchronously on the GUI thread with no progress or error reporting
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:281`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L281): runAll performs farthest-point subsampling plus an all-pairs Procrustes/assignment alignment (Correspondence computes n*n pairs, since has_pair at correspondence.py:128-135 always returns False) and mosek solves, all on the Qt main thread. Slicer freezes with no progress bar or cancel for the whole run, and failures surface only as tracebacks in the Python console rather than a dialog. The same applies to the individual step buttons.
  ```
      def allStepsButtonOnLoad(self):
        self.Auto3dgmData.phase1SampledPoints = self.phase1PointNumber.value
        self.Auto3dgmData.phase2SampledPoints = self.phase2PointNumber.value
        Auto3dgmLogic.runAll(self.Auto3dgmData, self.reflectionCheckBox.checked)
        Auto3dgmLogic.exportData(self.Auto3dgmData, self.outputFolder, phases = [1, 2])
  ```
  Suggestion: Run the pipeline in a CLI module or a worker thread with slicer.util.progress / a progress dialog, and wrap failures in a user-visible error dialog.

### D3. No license terms for the Slicer module code itself
single; category license; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`Readme.md:1`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Readme.md#L1): The only license file in the repository is Auto3dgm/auto3dgm_nazar/LICENSE (MIT, 'Copyright (c) 2018 Julie Winchester et al.'), which covers the vendored auto3dgm_nazar package. There is no LICENSE at the repository root and the Readme states no terms, so distribution permission for the Slicer-specific code (Auto3dgm/Auto3dgm.py, meshviewer/) is not stated. The bundled three.js/jquery/OpenCTM assets do carry their own notices.
  ```
  # Welcome to Slicer Auto3dgm!
  
  For details please see our web page:
  
  https://toothandclaw.github.io/
  ```
  Suggestion: Add a root LICENSE (or explicit terms in the Readme) covering the Slicer module code, and keep the vendored MIT notice.

### D4. Unpinned pip_install('mosek') into Slicer's shared Python when the module widget is constructed
severity dispute; category environment; raised by deepseek, flash-lite, haiku
- **deepseek** (major, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:72`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L72): The install happens in Auto3dgmWidget.__init__, i.e. as soon as the module is opened, and installs an unpinned package into Slicer's shared Python environment, affecting every other extension in that Slicer installation. There is a confirmation dialog, which is why this is not blocking, but the dialog text also tells users to drop a license file into the installed extension's lib folder (wiped on extension update, and often not writable). The dependency is also proprietary (see license finding).
  ```
        try:
          import mosek
        except ModuleNotFoundError as e:
          if slicer.util.confirmOkCancelDisplay("Auto3dgm requires 'mosek' python package. Click OK to download it now. It may take a few minues. Please also download an academic mosek license from https://www.mosek.com/products/academic-licenses/ and save the license file in the lib folder. More details about installing a mosek license can be found on https://toothandclaw.github.io/installations/"):
            slicer.util.pip_install('mosek')
            import mosek
  ```
  Suggestion: Pin a tested version, install only after an explicit user action (a dedicated button), and document the license path in a user-writable location instead of the install tree.
- **flash-lite** (info, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:72`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L72): The extension requires the commercial optimization package MOSEK and an external license file to perform core correspondence analysis, which may limit out-of-the-box usability for community users without academic licenses.
  ```
      try:
        import mosek
      except ModuleNotFoundError as e:
        if slicer.util.confirmOkCancelDisplay("Auto3dgm requires 'mosek' python package. Click OK to download it now. It may take a few minues. Please also download an academic mosek license from https://www.mosek.com/products/academic-licenses/ and save the license file in the lib folder. More details about installing a mosek license can be found on https://toothandclaw.github.io/installations/"):
            slicer.util.pip_install('mosek')
            import mosek
  ```
  Suggestion: Ensure users are well-informed about the MOSEK dependency and licensing requirements in the documentation.
- **haiku** (minor, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:72`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L72): If the user cancels the confirmation dialog, the widget constructor does nothing, and the module loads. Later, Correspondence imports mosek at the analysis step, which raises an unhandled ModuleNotFoundError in the GUI. The error is not reported to the user as a clear message.
  ```
      try:
          import mosek
        except ModuleNotFoundError as e:
          if slicer.util.confirmOkCancelDisplay("Auto3dgm requires 'mosek' python package. Click OK to download it now.
  ```
  Suggestion: Show an explicit error or disable the Run buttons when mosek is unavailable, and check the import before running an analysis step.

### D5. Visualize buttons clear the user's MRML scene without confirmation
single; category safety; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:845`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L845): Clicking 'View Phase 1 alignment' or 'View Phase 2 alignment' (Auto3dgm.py:386-401) calls viewAlignedMeshWithinSlicer, which unconditionally clears the whole MRML scene. Any unsaved work in the user's current scene (loaded volumes, segmentations, markups, other module state) is discarded with no prompt and no undo. Fix: ask for confirmation, or load into a new scene / separate view without clearing.
  ```
      def viewAlignedMeshWithinSlicer(viewMeshFolder, viewLmkFolder):
          slicer.mrmlScene.Clear(0)
  ```
  Suggestion: Prompt with slicer.util.confirmOkCancelDisplay before clearing, or avoid clearing and only remove the nodes this module created.

### D6. meshviewer starts an unauthenticated HTTP server on all interfaces with unsanitized path handling
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`meshviewer/web_view_mesh/viewer.py:20`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/meshviewer/web_view_mesh/viewer.py#L20): serve_viewer() binds to ("", 8000), i.e. every network interface, and the overridden translate_path bypasses SimpleHTTPRequestHandler's '..' sanitization by plain string concatenation. Any host on the same network can therefore request e.g. /../../../../home/<user>/... and read any file the Slicer user can read, and the /mesh prefix serves the user's chosen mesh directory (their research/medical surface data) with no authentication. Reachable when a user launches the installed 'meshviewer' CLI module (meshviewer/meshviewer.py -> web_view_mesh.viewer.serve_viewer); the Auto3dgm module's own server button is commented out, which limits but does not remove the exposure. Fix: bind to 127.0.0.1 and normalize/validate the resolved path against the allowed roots.
  ```
    def translate_path(self, path):
      if self.ext_prefix and self.path.startswith(self.ext_prefix):
        return self.ext_dir_path + path[len(self.ext_prefix):]
      else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        return base_path + path
  ```
  Suggestion: Bind to ('127.0.0.1', port) and resolve paths with os.path.realpath + a commonpath check against the allowed directories before serving.
- **haiku** (major, medium confidence, quote verified) [`meshviewer/web_view_mesh/viewer.py:20`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/meshviewer/web_view_mesh/viewer.py#L20): serve_viewer starts an HTTP server on ('', 8000), so it listens on every network interface, not just localhost. WebViewMeshRequestHandler.translate_path concatenates the raw request path without normalizing it or rejecting '..'. A raw HTTP request such as GET /mesh/../../../../etc/passwd (or a path outside the web root when the path does not start with /mesh) resolves to a file outside the mesh directory and is served. Any host on the local network can therefore read files the user can read while the viewer runs. The server is reachable through the installed meshviewer CLI executable; the GUI's serveWebViewer call is currently commented out.
  ```
  def translate_path(self, path):
    if self.ext_prefix and self.path.startswith(self.ext_prefix):
      return self.ext_dir_path + path[len(self.ext_prefix):]
    else:
      base_path = os.path.dirname(os.path.abspath(__file__))
      return base_path + path
  ```
  Suggestion: Bind to 127.0.0.1, normalize with os.path.normpath/realpath and verify the result stays under the intended root (return 404 otherwise), or use SimpleHTTPRequestHandler's own translate_path logic. Document the server's exposure.

### D7. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D8. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor

### D9. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor

### D10. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D11. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D12. Rating of utility
rating dispute; category utility; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings from some reviewers

### Committed __pycache__ .pyc files and a 16 MB test fixture are installed/carried
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote no quote) [`meshviewer/web_view_mesh/__pycache__/viewer.cpython-36.pyc`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/meshviewer/web_view_mesh/__pycache__/viewer.cpython-36.pyc): meshviewer/CMakeLists.txt copies the whole web_view_mesh directory into the install tree, so stale CPython-3.6 .pyc files ship to users; .gitignore only covers the root pattern. Auto3dgm/auto3dgm_nazar/tests/fixtures/test.ply (16 MB) and two 2 MB PNG textures are also committed rather than downloaded on demand.
  Suggestion: Remove __pycache__ from the repository and exclude it from the install rule; move large fixtures to a download or a smaller sample.

### Core alignment step requires the proprietary mosek solver under a separate academic license
minor; license; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`Auto3dgm/auto3dgm_nazar/analysis/correspondence.py:453`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/analysis/correspondence.py#L453): The sparse assignment branch calls Mosek Fusion, which is commercial software; the module tells users to obtain an academic license (Auto3dgm.py:75). Academic mosek licenses are typically non-commercial, so users must be told the extension's core computation is not usable without a third-party license and is restricted to non-commercial use. Auto3dgm/auto3dgm_nazar/lib/Save_mosek_license_here is an empty placeholder, so no license is bundled (which is correct).
  ```
                  ### specify mosek license
                  file_path = os.path.dirname(os.path.abspath(__file__))
                  lic_path = os.path.join(file_path, '../lib/mosek.lic')
  ```
  Suggestion: State the mosek dependency and its non-commercial academic restriction prominently in the module help and Readme.

### Identity comparison against a string literal in subsample method dispatch
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Auto3dgm/auto3dgm_nazar/mesh/subsample.py:112`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/mesh/subsample.py#L112): `func is 'FPS'` relies on string interning; with a non-interned method string the function returns None and Job validation raises 'Unexpected value ... for type func'. The module currently passes method=None so it works by accident, but any caller supplying 'FPS' explicitly can break.
  ```
      def generate_func(self, func='FPS'):
          #print(func)
          if func is 'FPS' or func is None:
              #print("entered")
              return self.far_point_subsample
  ```
  Suggestion: Use == for string comparison.

### Module help text is the unmodified Slicer template and the registered test is empty
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:30`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L30): Users opening the module see help text describing volume thresholding, which has nothing to do with the morphometrics workflow, and the acknowledgement credits the Slicer template authors. The ctest registered in Auto3dgm/CMakeLists.txt:32 runs Auto3dgmTest.test_Auto3dgm1, which is `pass` (Auto3dgm.py:928-929), so CI gives no signal about the pipeline.
  ```
      self.parent.helpText = """
  This is an example of scripted loadable module bundled in an extension.
  It performs a simple thresholding on the input volume and optionally captures a screenshot.
  """
  ```
  Suggestion: Write real help text (inputs, parameters, outputs, mosek requirement, citation) and add at least a smoke test on the bundled fixtures.

### No meaningful tests and minimal documentation
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:928`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L928): Auto3dgmTest.test_Auto3dgm1 is an empty pass, and the Testing/Python CMake registration is commented out. The module README is one line and the module help text still describes the template thresholding example. A user cannot verify the pipeline or learn the workflow from the extension.
  ```
      def test_Auto3dgm1(self):
        pass
  ```
  Suggestion: Add a real test with the sample fixtures and a documented tutorial; update parent.helpText to describe Auto3dgm rather than the template.

### No top-level license for the extension's Slicer glue code and meshviewer
minor; license; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`meshviewer/meshviewer.xml:8`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/meshviewer/meshviewer.xml#L8): The MIT license only covers the auto3dgm_nazar subpackage. The Auto3dgm module (Auto3dgm.py) and meshviewer have no license file or header, and the meshviewer.xml license element is empty. Distribution permission for the extension as a whole is therefore not explicit, although the core code is MIT.
  ```
  <license/>
  ```
  Suggestion: Add a top-level LICENSE covering the Slicer module and meshviewer code, and fill in the meshviewer.xml license and contributor fields.

### OFF parser ignores its argument and opens a hardcoded file
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Auto3dgm/auto3dgm_nazar/mesh/meshfactory.py:86`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/mesh/meshfactory.py#L86): Any .off mesh in the user's input folder is read from 'hammas.off' in the current working directory instead of the requested file, so .off inputs either fail with FileNotFoundError or silently analyse the wrong mesh. .off is in the accepted extension list (meshfactory.py:28), so this is reachable from the normal Load Data path.
  ```
      def off_parser(file_path):
          file=open("hammas.off","r")
  ```
  Suggestion: Use open(file_path, 'r').

### Output folder handling assumes a folder was chosen
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:216`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L216): self.outputFolder starts as None and is only set by the folder dialog; the Run buttons are enabled by the input folder alone, so pressing Run without choosing an output folder raises TypeError on None + str instead of telling the user what is missing. Paths are also built by string concatenation rather than os.path.join.
  ```
      def prepareOutputFolder(self):
        if (not os.path.exists(self.outputFolder+"/lowres/")):
          os.mkdir(self.outputFolder+"/lowres/")
  ```
  Suggestion: Validate that an output folder is set and show a message; use os.path.join.

### Process-wide MOSEKLM_LICENSE_FILE environment variable set at import of correspondence.py
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`Auto3dgm/auto3dgm_nazar/analysis/correspondence.py:18`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/analysis/correspondence.py#L18): Importing this module mutates the Slicer process environment for all code that runs afterwards (including other extensions that might use mosek). It is imported lazily from Auto3dgmLogic.correspondence, so it does not fire at Slicer startup, but the side effect is global and silent.
  ```
  file_path = os.path.dirname(os.path.abspath(__file__))
  os.environ.setdefault('MOSEKLM_LICENSE_FILE', os.path.join(file_path, '../lib/mosek.lic'))
  ```
  Suggestion: Pass the license path explicitly to M.putlicensepath() (already done at line 468) and drop the environment mutation.
- **haiku** (minor, medium confidence, quote verified) [`Auto3dgm/auto3dgm_nazar/analysis/correspondence.py:19`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/analysis/correspondence.py#L19): correspondence.py sets MOSEKLM_LICENSE_FILE in os.environ at import time for the whole Slicer process, which is a global side effect. exportRotations modifies the stored globalized rotation arrays in place (rot[2][0] = -1 * rot[2][0]), so calling the export twice changes results.
  ```
  os.environ.setdefault('MOSEKLM_LICENSE_FILE', os.path.join(file_path, '../lib/mosek.lic'))
  ```
  Suggestion: Pass the license path to the Mosek model only, avoid global env changes, and copy the rotation array before flipping its signs.

### Test fixtures, a Windows-only binary and a 16 MB file are installed with the extension
minor; packaging; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`Auto3dgm/CMakeLists.txt:21`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/CMakeLists.txt#L21): CMake installs the whole auto3dgm_nazar directory, which contains tests/fixtures/test.ply (16 MB), a Windows-only compiled module lap_windows/_lapjv.cp36-win_amd64.pyd (not built by the CMake build and not loadable on Linux/macOS), and lap_windows/tests that import a 'lap' module that is not packaged. This bloats the package and ships an unused, platform-specific binary. The lap_windows package is not imported by the module code I read.
  ```
  install(DIRECTORY "auto3dgm_nazar"
    DESTINATION "${Slicer_INSTALL_QTSCRIPTEDMODULES_BIN_DIR}"
  ```
  Suggestion: Install only the Python sources needed at runtime (or exclude tests/ and lap_windows/ with PATTERN filters) and move large fixtures out of the installed tree.

### Transform export writes the wrong translation component
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:583`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L583): The third translation value is m[1,3] instead of m[2,3], so .tfm files written by saveTFM contain a wrong z translation. saveTFM is currently only reachable from dead/commented code paths, hence minor, but the exported transform would be silently incorrect if re-enabled.
  ```
      file.write(str(-1 * m[0,3]) + " " + str(-1 * m[1,3]) + " " + str(m[1,3]) + "\n")
  ```
  Suggestion: Write str(m[2,3]) as the third component.

### requirements.txt lists bare 'vtk', which would shadow Slicer's bundled VTK
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`Auto3dgm/auto3dgm_nazar/requirements.txt:1`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/requirements.txt#L1): Nothing in the build or code reads this file, so it is not executed automatically; but a user or packager following it would pip-install a second VTK into Slicer's environment, which is a known way to break Slicer and other extensions. numpy is likewise bundled by Slicer.
  ```
  numpy
  vtk
  ```
  Suggestion: Remove the file or replace it with a comment stating that numpy/VTK come from Slicer.
- **haiku** (minor, low confidence, quote verified) [`Auto3dgm/auto3dgm_nazar/requirements.txt:1`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/requirements.txt#L1): The pip package vtk bundles its own VTK, which conflicts with Slicer's VTK if a user installs the requirements into Slicer's Python environment. The file is not installed automatically by the code I read, so the risk depends on users following it manually.
  ```
  numpy
  vtk
  ```
  Suggestion: Remove vtk and numpy from requirements.txt (Slicer provides both) or document that it should not be installed into Slicer's Python.

### Debug and dead-code leftovers in the shipped package
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:8`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L8): pdb is imported at module import, and Auto3dgm/auto3dgm_nazar/analysis/mini-auto3dgm_barakshan.py executes matplotlib plotting code at import (it is not importable due to the dashes in its name, so it is dead weight). meshviewer/web_view_mesh/examples/http_server_two_dirs.py hardcodes '/Users/jmw110/data/bunny'. None of these affect users directly but they add noise to the installed package.
  ```
  import pdb
  ```
  Suggestion: Remove debug imports, the scratch script, and the example file from the installed tree.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Research-grade morphometrics extension with a working-looking pipeline, but several issues should be fixed before it is offered to users: an unauthenticated HTTP server bound to all interfaces with unsanitized path handling (meshviewer), a button that clears the user's MRML scene without confirmation, an unpinned `pip_install('mosek')` into Slicer's shared Python environment at module open, a committed prebuilt Windows CPython-3.6 binary, and no license covering the Slicer module code itself (only the vendored auto3dgm_nazar subdirectory is MIT). Documentation is the unmodified Slicer template text and the module test is empty. No malicious or reviewer-manipulating content was found.
Not checked: Could not verify the catalog revision: the entry pins scm_revision 'master' (a moving branch), so the exact source commit reviewed is unknown; I inspected the snapshot provided in this review.; Could not read binary files: Auto3dgm/auto3dgm_nazar/lap_windows/_lapjv.cp36-win_amd64.pyd (provenance and contents unverified), the committed .pyc files, the PNG icons/screenshots, and the 16 MB tests/fixtures/test.ply.; Did not audit the ~189 vendored three.js/jquery JavaScript files under meshviewer/web_view_mesh/js beyond confirming that index.html loads them locally (the CDN script tags are commented out) and that license notices exist for OpenCTM/js-lzma.; Did not verify the mosek Fusion API usage or run the pipeline, so I cannot confirm the alignment results are numerically correct.; Did not check whether the extension builds on any platform (no CI evidence available to me).; Did not inspect the remaining test scripts under Auto3dgm/auto3dgm_nazar/tests/ or the sample fixture meshes.
Questions for the author: Is the meshviewer CLI module intended for end users? If so, can it bind to 127.0.0.1 and sanitize request paths, or be removed from the install?; Can the 'View Phase 1/2 alignment' buttons avoid clearing the user's MRML scene (or at least ask first)?; Can the mosek install be moved behind an explicit button with a pinned version, and can the license file location be a user-writable folder?; Which license covers Auto3dgm/Auto3dgm.py and meshviewer/? A root LICENSE would resolve the distribution-permission question.; Is the committed _lapjv.cp36-win_amd64.pyd still needed? It cannot load in current Slicer (Python 3.9+) and nothing imports lap_windows.

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
Auto3dgm is a 3D Slicer extension for automated 3D geometric morphometric analysis and alignment of surfaces. Inspection of the source code, CMake configuration, and catalog entry reveals clean packaging, proper adherence to Slicer scripted module conventions, and explicit user confirmation for third-party package installation (`mosek`). No safety or packaging issues were identified. 🟢 Recommend merge
Not checked: Detailed algorithms in auto3dgm_nazar/analysis/correspondence.py; Test fixtures and execution of heavy numerical routines

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
No malicious or concealed behavior found in the files read. The main concerns are the meshviewer HTTP server: it binds to all interfaces and its translate_path override does not normalize the request path, allowing traversal outside the mesh folder. Other issues: an uncommitted license at the extension level, a committed Windows-only binary and a 16 MB fixture inside the installed package, a placeholder test with no real coverage, and a requirements.txt that lists pip vtk. Core auto3dgm_nazar code is MIT-licensed. The catalog entry is well formed, and the scm_revision is a branch name rather than a pinned commit.
Not checked: Did not resolve scm_url or verify the master branch revision; reviewed only the files in the catalog listing.; Did not inspect analysis/mini-auto3dgm_barakshan.py, most of correspondence.py (lines 61-440), the remaining tests, the meshviewer JS libraries beyond the license headers, the pre-compiled .pyd, or the PNG and ply binaries.; Did not run the module, the CMake build, or the meshviewer server; the traversal finding is from reading code only.; Did not verify the mosek pip package or its license terms; the MOSEK academic license is a user-obtained requirement.
Questions for the author: Is the meshviewer CLI intended to be runnable by users? If so, should it bind to localhost and reject path traversal?; Which license applies to the Auto3dgm Slicer module and meshviewer code? Please add a top-level LICENSE.; Can the scm_revision be pinned to a specific commit instead of 'master'?; Why is a Windows-only compiled lap_windows module and a 16 MB fixture included in the installed extension?


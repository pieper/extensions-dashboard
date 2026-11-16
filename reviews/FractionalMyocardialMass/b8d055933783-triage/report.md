# AI review: FractionalMyocardialMass

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/dmolony3/SlicerFractionalMyocardialMass.git at commit `b8d055933783c33f5c6e239b3790b38eeb8b2517`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T10:26:22Z; cost $0.07

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | concern |
| environment | ok | ok | ok |
| packaging | minor | ok | concern |
| license | minor | ok | minor |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A Slicer scripted module that computes fractional myocardial mass (FMM) and myocardial mass at risk (MMAR) by assigning a tetrahedral left-ventricle myocardium mesh to coronary artery centerline segments with a Voronoi/point-interpolation scheme. It targets researchers and clinicians doing coronary physiology analysis who already have centerline trees (e.g. from SlicerVMTK) and a volumetric mesh (e.g. from SegmentMesher).
- **flash-lite**: The FractionalMyocardialMass extension computes the fractional myocardial mass and myocardial mass at risk (MMAR) for an input myocardial volume mesh using coronary centerlines and the Voronoi algorithm in 3D Slicer.
- **haiku**: Computes fractional myocardial mass (Voronoi split of an LV tetrahedral mesh between LCA/RCA centerline trees) and myocardial mass at risk for a stenosis point, for cardiac imaging researchers using 3D Slicer. It is a ScriptedLoadableModule with a Qt UI, logic class, and sample-data registration pointing to the author's GitHub releases.

## Disagreements (start here)

### D1. Apply button always fails: segmentMesh returns None but is unpacked
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`FMM/FMM.py:324`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L324): FMMLogic.segmentMesh (FMM/FMM.py:505-586) has no return statement; it mutates outputModel/outputTable in place. Unpacking its None result raises TypeError, which tryWithErrorDisplay turns into a 'Failed to compute results.' dialog, and the following line 327 then raises NameError on the undefined outputMesh. Every GUI run therefore ends in an error and no display setup (colouring, MMAR table, layout) ever happens.
  ```
              outputTable, outputMesh = self.logic.segmentMesh(self.ui.inputModelSelector.currentNode(), self.ui.inputLCAMarkupSelector.currentNode(),
  ```
  Suggestion: Call segmentMesh without unpacking (or make it return the nodes) and move the display code inside the try block.

### D2. Declared SlicerVMTK dependency contradicts EXTENSION_DEPENDS "NA"
partial; category packaging; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`FMM/FMM.py:24`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L24): CMakeLists.txt:16 sets EXTENSION_DEPENDS "NA" and the catalog entry has build_dependencies [], so SlicerVMTK is not installed with this extension, yet the module declares it as a dependency and README.md:51-54 states both SegmentMesher and SlicerVMTK are 'automatically installed'. The module test also imports ExtractCenterline (FMM/FMM.py:614), which only exists with SlicerVMTK, so the test fails on a clean install.
  ```
          self.parent.dependencies = ["SlicerVMTK"]
  ```
  Suggestion: Either add SlicerVMTK to EXTENSION_DEPENDS/build_dependencies and the catalog entry, or drop the runtime dependency declaration and correct the README.
- **haiku** (minor, high confidence, quote verified) [`FMM/FMM.py:29`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L29): The acknowledgement attributes the file to Kitware, PerkLab and Isomics developers and an NIH grant, which is template text and does not describe this extension's authors or funding. The TODO comment also remains.
  ```
  # TODO: replace with organization, grant and thanks
          self.parent.acknowledgementText = """
  This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
  ```
  Suggestion: Replace with the actual acknowledgements for this extension.

### D3. Runtime dependencies are declared inconsistently
single; category packaging; raised by haiku
- **haiku** (major, high confidence, quote verified) [`CMakeLists.txt:16`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/CMakeLists.txt#L16): The module declares SlicerVMTK as a dependency and the README says SegmentMesher and SlicerVMTK are installed automatically. The catalog entry has empty build_dependencies and CMakeLists.txt sets EXTENSION_DEPENDS to "NA". Users may therefore get an extension whose test and documented workflow need ExtractCenterline (from SlicerVMTK) but which does not install or declare it. The test imports ExtractCenterline at line 614, so the test fails without it.
  ```
  set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies
  ```
  Suggestion: Set EXTENSION_DEPENDS to "SlicerVMTK" (and SegmentMesher if it is truly required) and mirror this in the catalog build_dependencies, or remove the claim from the README and the parent.dependencies line if the dependency is optional.

### D4. Sample-data downloader executes an arbitrary setup.py from a user-chosen folder
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`FMM/FMM.py:51`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L51): downloadSampleDataInFolder is registered as the customDownloader for the RCA and LCA sample data (FMM/FMM.py:83, 102). When a user loads that sample data (or runs the module test, FMM/FMM.py:618), a folder chooser opens and any file named setup.py in the chosen folder is imported and executed with full Slicer privileges. A user who picks a shared/network folder, a download folder, or a colleague's data folder runs whatever code is there, with no warning and no relation to the module's advertised function. Nothing in the repository ships such a setup.py, so this is dead code that only creates an execution path.
  ```
        filepath=destFolderPath+"/setup.py"
        if (os.path.exists(filepath)):
          spec = importlib.util.spec_from_file_location("setup",filepath)
          setup = importlib.util.module_from_spec(spec)
          spec.loader.exec_module(setup)
  ```
  Suggestion: Delete the setup.py import/exec block entirely; if post-download setup is genuinely needed, ship it inside the extension and call it directly instead of executing a file from a user-writable directory.
- **haiku** (major, high confidence, quote verified) [`FMM/FMM.py:51`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L51): downloadSampleDataInFolder lets the user pick a destination folder, downloads sample files into it, then if '<folder>/setup.py' exists it loads that file with importlib and calls exec_module and setup.setup(). The extension never downloads a setup.py, so any pre-existing setup.py in the chosen folder (for example from another project) runs with the user's privileges when a sample is downloaded. This is arbitrary code execution with no prompt or opt-in. Concrete case: user selects a folder containing an unrelated Python project's setup.py while fetching RCA or LCA sample data.
  ```
  filepath=destFolderPath+"/setup.py"
    if (os.path.exists(filepath)):
      spec = importlib.util.spec_from_file_location("setup",filepath)
      setup = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(setup)
  ```
  Suggestion: Remove the setup.py execution entirely. If a post-download hook is really needed, ship it inside the extension and never execute files from user-selected folders.

### D5. qt and importlib are used but never imported
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`FMM/FMM.py:38`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L38): The module imports only logging, os, vtk and slicer (FMM/FMM.py:1-8); `qt` (lines 40, 42) and `importlib` (line 53) are never imported. Any call to downloadSampleDataInFolder raises NameError, so the RCA/LCA sample data and the module test cannot work as written.
  ```
        savedDirectory = slicer.app.userSettings().value(
              "SampleData/Last%sDownloadDirectory" % category,
              qt.QStandardPaths.writableLocation(qt.QStandardPaths.DocumentsLocation))
  ```
  Suggestion: Add `import qt` and `import importlib` at the top of the module (or remove the code that needs them).

### D6. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D7. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D8. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### At-risk points decided by point index rather than position along the vessel
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`FMM/FMM.py:454`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L454): addMMARArray marks a point as at-risk when its index in the concatenated polydata is >= the index of the closest point to the stenosis marker. Point order in the appended LCA/RCA polydata is an implementation detail of markupToPolyData, so the split between 'proximal' and 'distal' depends on insertion order rather than on arc length along the curve; results can silently be wrong for trees whose points are not ordered root-to-leaf.
  ```
              if currentGroupId in childIds:
                  if currentGroupId == groupId:
                      if i >= pointId:
  ```
  Suggestion: Compute the arc-length position of each point along its curve and compare with the arc-length position of the MMAR point.

### Heavy computation on the GUI thread without progress reporting
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`FMM/FMM.py:320`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L320): The Voronoi point interpolation (FMM/FMM.py:469-486) and the per-cell Python loop in computeVolume (FMM/FMM.py:494-501) run synchronously in the Apply slot with only a wait cursor and a single status message. For the tetrahedral meshes the README recommends, Slicer will appear frozen with no progress or cancel option.
  ```
              slicer.util.showStatusMessage("Segmenting myocardium...")
              slicer.app.processEvents()  # force update
  ```
  Suggestion: Run the computation in a CLI or a worker thread with progress reporting, or at least report progress per cell block.

### LICENSE is an unfilled MIT template
minor; license; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`LICENSE:1`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/LICENSE#L1): The MIT grant text is present, so distribution is permitted, but the copyright line still contains the template placeholders, so no licensor is identified and the notice cannot be reproduced as required by the license itself. The sample data published in the GitHub release has no stated license either.
  ```
  MIT License
  
  Copyright (c) [year] [fullname]
  ```
  Suggestion: Fill in the year and copyright holder (e.g. David Molony) and state the license of the sample data assets.
- **haiku** (minor, high confidence, quote verified) [`LICENSE:3`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/LICENSE#L3): The MIT text is present and grants distribution rights, but the copyright holder and year are still placeholders. This does not block distribution but leaves attribution undefined.
  ```
  Copyright (c) [year] [fullname]
  ```
  Suggestion: Fill in the year and copyright holder.

### MMAR table looked up by hardcoded node name and recreated on every run
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`FMM/FMM.py:336`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L336): segmentMesh creates a new table node literally named 'MMAR' on each run (FMM/FMM.py:584), and the widget then fetches it by name. After a second run there are several 'MMAR' nodes and getNode may return the wrong (stale) one or raise if the user renamed it; the scene also accumulates duplicate tables.
  ```
                  MMARNode = slicer.util.getNode('MMAR')
  ```
  Suggestion: Return the MMAR table node from segmentMesh (or store it in the parameter node) instead of looking it up by name, and reuse an existing node.

### MMAR volumes truncated to integers
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`FMM/FMM.py:581`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L581): The MMAR table uses vtkIntArray for volumes in mm^3, so the fractional part of the computed volume is silently discarded. The table value for 'Myocardial volume at risk' and 'Total volume' is therefore inaccurate by up to 1 mm^3 per entry.
  ```
  volCol1 = vtk.vtkIntArray()
              volCol1.InsertNextTuple([volMMAR[1] + volMMAR[0], ])
              volCol1.InsertNextTuple([volMMAR[1], ])
  ```
  Suggestion: Use vtk.vtkDoubleArray, consistent with the per-segment volume column.

### README claims dependencies are installed automatically; no clinical disclaimer
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:51`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/README.md#L51): EXTENSION_DEPENDS is "NA" (CMakeLists.txt:16), so SegmentMesher and SlicerVMTK are not installed with the extension; users following the README will not find the tools it tells them to use. The README also gives no statement that the computed FMM/MMAR values are research output and not validated for clinical decision making, which matters for a cardiac risk metric.
  ```
  The following extensions are automatically installed with SlicerFractionalMyocardialMass. Although SlicerFractionalMyocardialMass does not directly rely on these extensions, they provide a the capability for generating the required input data.
  ```
  Suggestion: Correct the dependency statement and add a short research-use disclaimer.

### Sample data downloaded without integrity checks
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`FMM/FMM.py:80`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L80): The RCA/LCA markup sources pass checksums=None and the surface/volume sources omit checksums altogether (FMM/FMM.py:85-127), so the .vtp/.stl/.vtu/.mrk.json payloads pulled from the GitHub release are loaded into the scene without verification. Combined with the setup.py execution above, a tampered release asset would be consumed silently.
  ```
          checksums=None,
  ```
  Suggestion: Provide checksums for every registered sample data source.
- **haiku** (minor, medium confidence, quote verified) [`FMM/FMM.py:80`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L80): All registered sample sources use checksums=None, so downloaded meshes and centerlines are not verified. A compromised or changed release asset would be loaded silently.
  ```
  checksums=None,
            loadFiles=True,
            loadFileType='MarkupsFile',
  ```
  Suggestion: Provide SHA256 checksums for each release asset.

### Sample data is never registered at startup
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`FMM/FMM.py:58`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L58): registerSampleData is only called from the test (FMM/FMM.py:616); there is no `slicer.util.infoDisplay`/`startupCompleted` connection anywhere in the file, so the RCA/LCA/myocardium sample data never appears in the Sample Data module for normal users, contrary to the README's tutorial intent.
  ```
  def registerSampleData():
  ```
  Suggestion: Connect registerSampleData to slicer.app.startupCompleted as in the module template.

### Stale compiled bytecode committed to the repository
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote no quote) [`FMM/__pycache__/FMM.cpython-39.pyc`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/__pycache__/FMM.cpython-39.pyc): FMM/__pycache__/FMM.cpython-39.pyc (15 KB, Python 3.9 bytecode) is checked in. It is not installed by CMake (FMM/CMakeLists.txt:5-12 lists only FMM.py and the resources), so it is dead weight that can drift from the source and confuse anyone reading the repository.
  Suggestion: Remove the __pycache__ directory and add it to .gitignore.

### Unguarded display-node access on the input model
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`FMM/FMM.py:333`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L333): If the selected input model has no display node (e.g. a node created by a script or a CLI output), GetDisplayNode() returns None and this raises AttributeError, aborting the display setup after the mesh has already been computed.
  ```
              inputModelNode.GetDisplayNode().SetVisibility(0)
  ```
  Suggestion: Create default display nodes for the input model first, or guard with a None check.

### importlib and qt used without import
minor; soundness; raised by haiku
- **haiku** (minor, low confidence, quote verified) [`FMM/FMM.py:1`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/FMM.py#L1): The sample-data helper uses importlib.util at line 53 but the module imports only logging, os and vtk at the top (lines 1-8). It works only if Slicer injects importlib into the module namespace via the star import, which is not guaranteed. The same applies to qt at line 40.
  ```
  import logging
  import os
  
  import vtk
  ```
  Suggestion: Add explicit 'import importlib.util' and 'import qt' (or use slicer.qt) at module top.

### Test is not registered in the Testing/Python CMakeLists
info; utility; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`FMM/Testing/Python/CMakeLists.txt:2`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/Testing/Python/CMakeLists.txt#L2): The only test is the FMMTest class registered via slicer_add_python_unittest in FMM/CMakeLists.txt:27; the Testing/Python directory is empty apart from a commented-out line. The test itself downloads sample data and needs SlicerVMTK, so it will not pass in a minimal build environment.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Either remove the empty Testing directory or add a self-contained test that does not depend on downloaded data.
- **haiku** (info, medium confidence, quote verified) [`FMM/Testing/Python/CMakeLists.txt:2`](https://github.com/dmolony3/SlicerFractionalMyocardialMass/blob/b8d055933783c33f5c6e239b3790b38eeb8b2517/FMM/Testing/Python/CMakeLists.txt#L2): The module computes mass-at-risk values used in cardiac analysis but has no research-use disclaimer. The only test downloads network data and is intended to run in CI, and the Testing/Python CMake registration is commented out.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a research-use-only disclaimer to the README and module help, and document how the network-dependent test is run.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Small, readable module with no network servers, no pip installs and no environment tampering, but it has a concrete unsafe code path: the sample-data downloader executes a `setup.py` found in a user-chosen folder. The GUI "Apply" path is also broken (segmentMesh returns None but is unpacked into two variables), `qt`/`importlib` are never imported, and the declared SlicerVMTK dependency contradicts `EXTENSION_DEPENDS "NA"`. The LICENSE is an unfilled MIT template. Recommend 🔴 Do not merge yet until the arbitrary-code-execution path and the broken Apply path are fixed.
Not checked: Contents of FMM/__pycache__/FMM.cpython-39.pyc (binary, not readable as text) - could not confirm it matches FMM.py; Contents and license of the sample data assets in the GitHub release (RCA/LCA markups, surfaces, myocardium mesh); Whether scm_revision "main" currently resolves to the stated commit b8d0559 (reviewed the files provided for that commit); CI/build results for this extension on the Slicer factory; Media/Manual_centerline.gif (5 MB, not readable)
Questions for the author: Why does downloadSampleDataInFolder execute a setup.py from the folder the user selects? Can that block be removed?; Is SlicerVMTK a real runtime dependency (then EXTENSION_DEPENDS should list it) or only needed for the test?; Should segmentMesh return the output nodes, given the widget unpacks two values from it?; Will you fill in the copyright holder in LICENSE and state the license of the sample data?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The FractionalMyocardialMass extension is well-structured, implements clear cardiac quantification tools using Slicer and VTK APIs, contains a valid MIT license, and presents no safety, environment, or packaging concerns. 🟢 Recommend merge
Not checked: Building the extension binary packages or running automated tests in a live Slicer runtime instance.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
I reviewed the catalog entry, CMake files, the full FMM/FMM.py module, README and LICENSE as provided. I found no network calls, telemetry, or obfuscation. The main concern is a sample-data helper that executes any setup.py found in a user-chosen folder. Packaging also declares SlicerVMTK as a module dependency and the README says SegmentMesher and SlicerVMTK are installed automatically, but neither is declared in EXTENSION_DEPENDS or build_dependencies. LICENSE is an unfilled MIT template. Overall the entry needs fixes before it is offered to users. I did not run anything and did not fetch the source repository or the sample-data release files.
Not checked: Source repository at https://github.com/dmolony3/SlicerFractionalMyocardialMass.git and revision b8d05593 were not fetched; only the files shown in the prompt were read.; Sample-data release assets (RCA, LCA, surfaces, volumes) on GitHub were not downloaded or checksummed.; The module icon Resources/Icons/FMM.png and UI file Resources/UI/FMM.ui were listed but not inspected.; Media/Manual_centerline.gif (5 MB, referenced in README) was not available; committed large binaries could not be assessed.; The committed FMM/__pycache__/FMM.cpython-39.pyc was not inspected; it should not be in a source tree.; Whether the code runs on a current Slicer build, and whether SlicerVMTK's ExtractCenterline API still matches, was not tested.


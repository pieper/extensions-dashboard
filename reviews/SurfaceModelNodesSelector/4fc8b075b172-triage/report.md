# AI review: SurfaceModelNodesSelector

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector.git at commit `4fc8b075b172918f01ceddeed9d48613fd5c59d0`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:23:24Z; cost $0.02

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | blocking | ok | blocking |
| environment | minor | ok | concern |
| packaging | minor | minor | concern |
| license | ok | ok | ok |
| soundness | concern | concern | blocking |
| utility | minor | ok | concern |
| **overall** | needs fixes | needs fixes | do not accept |

## What each reviewer says the extension does

- **deepseek**: A Slicer scripted module that scans a user-chosen folder for .ply surface models, loads each model, and writes a fiducial markup file (.mrk.json) with one control point per mesh vertex, for researchers who need per-vertex point sets from surface models. It is aimed at batch processing of model folders rather than interactive picking.
- **flash-lite**: SurfaceModelNodesSelector is a 3D Slicer scripted module that processes a directory of .ply surface models, places fiducial points at every vertex of each model, and saves the resulting markup points as JSON files alongside a CSV index of the models.
- **haiku**: A scripted Slicer module that, given a folder, loads each .ply surface model, creates a fiducial markups node with one point per mesh vertex, and saves each as .mrk.json plus a models_ids.csv index into that folder. It is intended for researchers working with surface meshes.

## Disagreements (start here)

### D1. Apply wipes the entire MRML scene without confirmation
partial; category safety; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:384`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L384): process() is invoked from the Apply button (line 280) and calls slicer.mrmlScene.Clear(0) once per .ply file. Any nodes the user has loaded — models, volumes, segmentations, markups, unsaved work — are deleted from the scene with no warning, no undo, and no prompt. A user who loads their own data, then points the module at a folder and clicks Apply, loses that session's work. This is a concrete path to unintended data destruction.
  ```
              slicer.util.saveNode(markupsNode, os.path.join(dataDirectoryPath, modelFileName+".mrk.json"))
              slicer.mrmlScene.Clear(0)
  ```
  Suggestion: Do not clear the scene. Remove each temporary model/markup node individually (slicer.mrmlScene.RemoveNode) after saving, or process the mesh without adding nodes to the scene at all; if a scene reset is ever needed, ask the user first.
- **haiku** (blocking, high confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:385`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L385): Inside the per-file loop, after each markups node is saved, slicer.mrmlScene.Clear(0) is called. This removes every node in the user's current Slicer session (volumes, segmentations, unsaved work, other modules' data), not just the nodes this module created. A user who clicks Apply on a folder with several .ply files loses their open scene on the first iteration, with no warning.
  ```
  slicer.mrmlScene.Clear(0)
  ```
  Suggestion: Remove the Clear call. Remove the created markups and model nodes explicitly (slicer.mrmlScene.RemoveNode) after saving, and only those nodes.

### D2. Silently overwrites files in the user's input folder
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:355`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L355): Outputs are written into the same directory the user selected as input: models_ids.csv (line 356) and <modelname>.mrk.json (line 384). If files with those names already exist there (e.g. from a previous run or a user's own annotations), they are overwritten without any prompt or backup. The README does document that outputs go to the same directory, but there is no overwrite check.
  ```
          filepath = dataDirectoryPath+'/models_ids.csv'
          df.to_csv(filepath, index=True)
  ```
  Suggestion: Write to a user-selected output directory or a temporary folder, and prompt before overwriting existing files.
- **haiku** (major, medium confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:355`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L355): process() writes models_ids.csv and <name>.mrk.json into the folder the user selects. Existing files with the same names are overwritten silently. Folder listing also picks up every *.ply file, so unrelated models in that folder are processed.
  ```
  filepath = dataDirectoryPath+'/models_ids.csv'
          df.to_csv(filepath, index=True)
  ```
  Suggestion: Warn before overwriting, use os.path.join, and document the outputs in the module help.

### D3. pandas is imported but never declared or installed
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:351`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L351): pandas is not part of Slicer's bundled Python and the extension neither declares it (build_dependencies is empty, EXTENSION_DEPENDS is "NA") nor installs it. On a stock Slicer install, clicking Apply raises ModuleNotFoundError, which tryWithErrorDisplay shows as "Failed to compute results." The DataFrame is only used to iterate a list of filenames, so the dependency is avoidable.
  ```
          import pandas as pd
          
          #dataframe to store all the ply files name along with index
          df = pd.DataFrame(modelFiles, columns =['FileNames'])
  ```
  Suggestion: Drop pandas and iterate the file list directly (e.g. `for modelFileName in modelFiles:`), or declare and install the dependency with explicit user consent.
- **haiku** (minor, medium confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:351`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L351): process() imports pandas to build a two-column index. pandas is not declared in EXTENSION_DEPENDS or as a package requirement, so the module fails at run time on Slicer builds without it. The logic is simple enough to use the standard library.
  ```
  import pandas as pd
  ```
  Suggestion: Use the csv module, or declare and install pandas explicitly through a user-confirmed step.

### D4. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku blocking

### D5. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D6. Rating of utility
rating dispute; category utility; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings all reviewers agree on

### Bundled module test calls process() with an obsolete signature and will fail
major; soundness; raised by deepseek, flash-lite, haiku
- **deepseek** (major, high confidence, quote verified, other lines) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:127`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L127): process() now takes (dataDirectoryPath, showResult=True) and treats the first argument as a folder path, but the test passes four arguments (a volume node, an output volume, a threshold, a bool). The test registered by `slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)` in SurfaceModelNodesSelector/CMakeLists.txt:27 therefore raises TypeError, so the extension's own test suite fails and gives no coverage of the actual .ply workflow.
  ```
          logic = SurfaceModelNodesSelectorLogic()
  
          # Test algorithm with non-inverted threshold
          logic.process(inputVolume, outputVolume, threshold, True)
  ```
  Suggestion: Rewrite the test to create a temporary folder with a small .ply model, call process(folder), and assert the resulting .mrk.json exists with the expected number of control points.
- **flash-lite** (major, high confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:447`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L447): The unit test SurfaceModelNodesSelectorTest is a copy-paste template from the Slicer scripted module template (testing volume thresholding), whereas the actual extension processes surface models and directories of .ply files to generate markup fiducial JSON files. Running the test fails because logic.process expects a directory path and processes surface models rather than scalar volume nodes and thresholds.
  ```
          # Test algorithm with non-inverted threshold
          logic.process(inputVolume, outputVolume, threshold, True)
          outputScalarRange = outputVolume.GetImageData().GetScalarRange()
          self.assertEqual(outputScalarRange[0], inputScalarRange[0])
          self.assertEqual(outputScalarRange[1], threshold)
  ```
  Suggestion: Update SurfaceModelNodesSelectorTest to correctly test the module logic (e.g., testing with a sample model or mock directory) or remove the broken test.
- **haiku** (major, high confidence, quote verified, other lines) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:127`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L127): The test calls logic.process with volume arguments (inputVolume, outputVolume, threshold, True), but process() takes a directory path. It also asserts on image scalar ranges that have nothing to do with surface models. The Python test registration is commented out, so the test does not run in CTest.
  ```
  logic = SurfaceModelNodesSelectorLogic()
  
            # Test algorithm with non-inverted threshold
            logic.process(inputVolume, outputVolume, threshold, True)
  ```
  Suggestion: Rewrite the test for the .ply-to-markups workflow with a small .ply fixture, and re-enable slicer_add_python_unittest.

### Compiled bytecode and a developer scratch script are committed
minor; packaging; raised by deepseek, flash-lite, haiku; **quote not found in source**
- **deepseek** (minor, high confidence, quote no quote) [`SurfaceModelNodesSelector/__pycache__/SurfaceModelNodesSelector.cpython-39.pyc:1`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/__pycache__/SurfaceModelNodesSelector.cpython-39.pyc#L1): Two .pyc files (cpython-36 and cpython-39) are committed under SurfaceModelNodesSelector/__pycache__/, and surfaceModel.py at the repository root contains a hardcoded developer path (`/media/useradmin/Disk2/Slicer-5.3.0-...`). Neither is installed by CMake, so they do not break loading, but stale bytecode is a maintenance and review hazard and the scratch script exposes local paths.
  Suggestion: Remove __pycache__ from the repository and add a .gitignore; move or delete surfaceModel.py.
- **flash-lite** (info, medium confidence, quote file not found) [`SurfaceModelNodesSelector/__pycache__/:1`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/__pycache__/#L1): Compiled Python bytecode (.pyc files under __pycache__) are checked into the source repository. While not blocking extension loading, generated build artifacts or cache files should not be kept in source control.
  ```
  SurfaceModelNodesSelector/__pycache__/SurfaceModelNodesSelector.cpython-36.pyc
  SurfaceModelNodesSelector/__pycache__/SurfaceModelNodesSelector.cpython-39.pyc
  ```
  Suggestion: Remove __pycache__ directory and compiled .pyc files from the repository and add them to .gitignore.
- **haiku** (minor, high confidence, quote quote not found) [`SurfaceModelNodesSelector/__pycache__/SurfaceModelNodesSelector.cpython-39.pyc:1`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/__pycache__/SurfaceModelNodesSelector.cpython-39.pyc#L1): Python 3.6 and 3.9 .pyc files are committed inside the source tree. These are generated artifacts, are interpreter-specific, and can go stale relative to the .py source.
  ```
  SurfaceModelNodesSelector/__pycache__/SurfaceModelNodesSelector.cpython-39.pyc  (12987 bytes, binary)
  ```
  Suggestion: Remove the __pycache__ directories and add a .gitignore entry.


## Findings from some reviewers

### Documentation is minimal and helpText still contains template placeholders
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:27`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L27): The in-Slicer help link points to the template URL github.com/organization/projectname, so users get a dead link; README.md has no tutorial, no sample .ply data, and no note on limitations. There is also no disclaimer about research use, which matters for a tool that generates point sets from anatomical models.
  ```
          self.parent.helpText = """
  This module is used to select the indeces/nodes of the any 3D surface model <a href="https://github.com/organization/projectname#SurfaceModelNodesSelector">module documentation</a>.
  """
  ```
  Suggestion: Point helpText at the real README, add a short step-by-step usage section with a sample model, and state the intended (research) use.
- **haiku** (minor, high confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:28`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L28): The module help text links to 'https://github.com/organization/projectname' and the contributor list is a placeholder. The repository README is the only real documentation.
  ```
  This module is used to select the indeces/nodes of the any 3D surface model <a href="https://github.com/organization/projectname#SurfaceModelNodesSelector">module documentation</a>.
  ```
  Suggestion: Point the help link to the real README and update the help text.

### Hardcoded personal filesystem path in a committed script
minor; safety; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`surfaceModel.py:1`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/surfaceModel.py#L1): surfaceModel.py at the repository root runs a hardcoded path from the author's machine (/media/useradmin/Disk2/...). It is not installed by CMake, so it does not affect users directly, but it reveals a local environment and would fail for others.
  ```
  s = slicer.modules.surfacemodelnodesselector.widgetRepresentation().self().logic.process("/media/useradmin/Disk2/Slicer-5.3.0-2023-01-21-linux-amd64/25_manually_picking_points/25_manually_picking_points/")
  ```
  Suggestion: Replace with a command-line argument or move to an examples folder with a placeholder path.

### Long batch runs on the GUI thread with no progress reporting
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:375`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L375): Every vertex of every model is added as an individual control point inside the Apply callback (only a wait cursor from tryWithErrorDisplay, line 276). For meshes with tens of thousands of vertices and multiple files, Slicer's UI freezes for a long time with no progress bar and no way to cancel, which users will read as a hang.
  ```
              for i in range(nPoints):
                  p = points.GetPoint(i)
                  markupsNode.AddControlPoint(p[0],p[1],p[2])
                  markupsNode.SetNthControlPointLocked(i, True)
  ```
  Suggestion: Report progress with slicer.util.ProgressDialog / qSlicerApplication.processEvents, or run the batch in a CLI/worker thread; consider building the point list in bulk instead of one AddControlPoint call per vertex.

### Model load failures are not checked and abort the whole batch
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:365`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L365): loadModel returns None on failure (corrupt or unsupported .ply). The next line dereferences modelNode.GetMesh() (line 372), raising AttributeError that aborts the entire loop, so one bad file prevents all remaining models from being processed and the already-created markup node is left in the scene.
  ```
              modelNode = slicer.util.loadModel(dataDirectoryPath+ "/" + modelFileName)
              size = len(modelFileName)
              modelFileName = modelFileName[:size - 4]
              print(modelFileName)
              markupsNode.SetName(modelFileName)
  ```
  Suggestion: Check `if not modelNode: logging.warning(...); continue` and report which files were skipped.

### Sample data registration points at missing thumbnails and irrelevant data
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:63`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L63): Resources/Icons contains only SurfaceModelNodesSelector.png; SurfaceModelNodesSelector1.png and SurfaceModelNodesSelector2.png do not exist, so the Sample Data entries show broken thumbnails. The registered samples are .nrrd scalar volumes, which cannot be used with a module that only reads .ply models, so they do not help users try the module. registerSampleData is also connected to startupCompleted (line 36), adding these entries for every Slicer user at startup.
  ```
          thumbnailFileName=os.path.join(iconsPath, 'SurfaceModelNodesSelector1.png'),
  ```
  Suggestion: Register a small .ply model (or remove the sample-data block entirely) and provide the referenced thumbnails.

### Description claims per-triangle vertex selection but code emits one point per mesh vertex
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`SurfaceModelNodesSelector/SurfaceModelNodesSelector.py:372`](https://github.com/saimasafdar2021/Slicer_SurfaceModelNodesSelector/blob/4fc8b075b172918f01ceddeed9d48613fd5c59d0/SurfaceModelNodesSelector/SurfaceModelNodesSelector.py#L372): The README and CMake EXTENSION_DESCRIPTION say the module "selects the nodes/vertices of each triangle", but the implementation simply iterates all mesh points once; shared vertices are not enumerated per triangle. Users expecting per-triangle vertex lists will get different output than advertised.
  ```
              meshModel = modelNode.GetMesh()
              points = meshModel.GetPoints()
              nPoints = points.GetNumberOfPoints()
  ```
  Suggestion: Either implement per-triangle vertex enumeration or reword the description to "one fiducial per mesh vertex".


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The extension is small and has no network, install, or obfuscation behavior, and it ships an Apache-2.0 LICENSE. However, its core loop calls `slicer.mrmlScene.Clear(0)` after each model, wiping the user's entire scene (all loaded nodes and unsaved work) with no confirmation — a concrete data-destruction path. It also silently writes `models_ids.csv` and `<model>.mrk.json` into the user's input folder, imports `pandas` without declaring or installing it (Apply fails on stock Slicer), and its bundled test calls `process()` with a signature that no longer exists. Needs fixes before being offered to users.
Not checked: Could not resolve or fetch the remote repository at commit 4fc8b075b172918f01ceddeed9d48613fd5c59d0; the review is based on the file contents provided for that revision only.; Could not verify whether pandas is present in the targeted Slicer version's bundled Python (finding rated medium confidence).; Could not run the module, its tests, or the extension build; the test failure is inferred from the signature mismatch between process() and the test call.; Could not verify that the SlicerTestingData sample-data URLs and checksums resolve.; Could not inspect the binary files (SurfaceModelNodesSelector.png, sModel.png, Resources/Icons/SurfaceModelNodesSelector.png, the two .pyc files) for embedded content.; Could not check repository history, maintenance activity, or whether the catalog entry's scm_revision "main" currently points at the reviewed commit.
Questions for the author: Why does process() call slicer.mrmlScene.Clear(0) after each model? Users lose all loaded data and unsaved work when they press Apply — can this be replaced by removing only the temporary nodes?; Is pandas guaranteed to be available in the Slicer versions you target? If not, can the DataFrame be replaced with a plain list iteration?; Should outputs be written into the input folder, and what should happen when models_ids.csv or <model>.mrk.json already exist there?; The bundled test calls logic.process(inputVolume, outputVolume, threshold, True), which no longer matches the signature — was the test updated for the folder-based workflow?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): needs fixes
SurfaceModelNodesSelector is a well-structured 3D Slicer extension with a clear purpose, proper licensing (Apache 2.0), and safe file operations. However, the automated unit test in `SurfaceModelNodesSelectorTest` is unedited template code from the Slicer scripted module wizard (testing image volume thresholding rather than surface model point extraction), which results in a test failure. Consequently, the extension needs fixes for its unit tests before acceptance.
Not checked: Qt .ui file layout widgets and connections beyond main structure inspection.
Questions for the author: Can you update the unit test to properly exercise the surface model processing logic instead of the template volume thresholding test?

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): do not accept
The extension's logic calls slicer.mrmlScene.Clear(0) inside the per-file loop, which wipes the user's entire open scene (including unsaved work) every iteration. Its test is broken (calls logic.process with an incompatible signature) and is not registered with CTest. It also writes files into the user-selected folder without confirmation, has committed __pycache__ binaries, and a hardcoded personal path script. Not ready for distribution in its current form.
Not checked: The .ui file and icon contents were not read beyond existence in the file listing.; The source repository at the 'main' branch was not fetched; the commit 4fc8b075... was not verified against the catalog's scm_revision.; No Slicer runtime was available, so the scene-clear and file-overwrite behavior was verified by reading code only.; The sample-data thumbnails referenced in registerSampleData (SurfaceModelNodesSelector1.png, SurfaceModelNodesSelector2.png) were not confirmed to exist in Resources/Icons.; The catalog build_dependencies is empty while the module needs no PyTorch; no unusual dependency was seen.


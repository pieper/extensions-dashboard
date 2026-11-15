# AI review: EVARSim

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/rwic/SlicerEVARSim at commit `0568d174ab552f3ff41e42d380e2cfaf80a35e8e`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T17:38:04Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | ok | ok | ok |
| packaging | concern | ok | minor |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | minor issues | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: EVARSim is a 3D Slicer scripted module for simulating endovascular stent grafts (EVAR): it builds tube/stent geometry along a markup centerline curve or along polylines extracted from a VTK model, with per-stent radius, length, position, resolution and smoothing controls. It targets clinicians and researchers doing procedural planning/simulation, not diagnosis.
- **flash-lite**: EVARSim is a 3D Slicer extension that enables simulation and visualization of endovascular devices (stents) along vessel centerline curves for Endovascular Aneurysm Repair (EVAR) procedures.
- **haiku**: EVARSim is a scripted 3D Slicer module (Modeling category, tier 1) that generates cylindrical endovascular device models (tubes with rigid caps) along a centerline curve or a VTK polyline model, for EVAR simulation teaching and research. It is intended for researchers and educators who want to visualize stent placement along vessel centerlines.

## Disagreements (start here)

### D1. Registered unit test calls logic.process() with the wrong signature and will fail
partial; category packaging; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`EVARSim/EVARSim.py:1567`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L1567): process() is defined as process(self, centerlineCurve, inputModel, outputModel, radius, length, position, numberOfTubes, resolution, showResult=True) (lines 1403-1412), so this call passes only 5 of 8 required positional arguments and raises TypeError. EVARSim/CMakeLists.txt line 27 registers this class as a ctest (slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)), so the extension's test step fails and the core geometry code is effectively untested.
  ```
  logic.process(centerlineCurve, outputModel, radius, length, resolution)
  ```
  Suggestion: Update the test to the current signature, e.g. logic.process(centerlineCurve, None, outputModel, radius, length, 0.0, 1, resolution), and add a second case using a polyline model input.
- **haiku** (major, high confidence, quote verified) [`EVARSim/EVARSim.py:1567`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L1567): test_EVARSim1 calls logic.process with 5 positional arguments, but process requires at least 8 (centerlineCurve, inputModel, outputModel, radius, length, position, numberOfTubes, resolution). The call raises TypeError. The test is registered via slicer_add_python_unittest(SCRIPT EVARSim.py) in EVARSim/CMakeLists.txt, so ctest for the extension fails. It also never checks branch or multi-tube behavior.
  ```
  logic.process(centerlineCurve, outputModel, radius, length, resolution)
  ```
  Suggestion: Update the test to the current signature, e.g. logic.process(centerlineCurve, None, outputModel, 2.0, 10.0, 0.5, 1, 16), and add assertions for the input-model path and multi-tube output.

### D2. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor

### D3. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Additional tubes are placed along tube 1's reduced segment, not the full centerline
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`EVARSim/EVARSim.py:1483`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L1483): reducedPoints is the 4-point spline of the already positioned segment for tube 1 (lines 1475-1479). _createAdditionalTubes then distributes positions 0.2-0.8 along that short segment (line 1130), so tubes 2..N are stacked inside tube 1's span instead of being spread along the vessel; with the default length of 10 mm and a long centerline the extra stents overlap almost completely.
  ```
  self._createAdditionalTubes(reducedPoints, radius, length, numberOfTubes, resolution)
  ```
  Suggestion: Pass the full (smoothed) curvePoints to _createAdditionalTubes and let each tube position itself along the whole centerline.

### Branch selection ignored in the process() path
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`EVARSim/EVARSim.py:1451`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L1451): The widget applies the selected branch through _extractBranchCenterline, but process() always takes the first line cell of an input model. A headless caller of process() therefore gets a different branch from the GUI for the same input.
  ```
  # Get the first line segment (or could be modified to use branch selection)
                    lines = polyData.GetLines()
  ```
  Suggestion: Pass the branch index into process() and reuse _extractBranchCenterline so both paths match.

### Division by zero on duplicate centerline points
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`EVARSim/EVARSim.py:806`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L806): segmentLengths[i] is zero when two consecutive curve points coincide (common in imported polylines), producing inf/nan points; the same risk exists in _addRigidEndCaps (line 904, 909) and _createCircularCap (line 935) where a zero-length direction vector is normalized. In process() this surfaces as a confusing error or an empty/garbage model rather than a clear message.
  ```
  t = (startDistance - segmentStart) / segmentLengths[i]
  ```
  Suggestion: Skip zero-length segments and guard the normalizations with a length check.

### Errors swallowed with print() instead of being reported to the user
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`EVARSim/EVARSim.py:438`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L438): _updateSelectedTube, _analyzeBranches, _createBranchLabels, _removeBranchLabels, _extractBranchCenterline, _smoothCenterline, _reduceCenterlinePoints and _applySplineSmoothing all catch Exception and only print to stdout. In a GUI session the user sees nothing when, for example, branch extraction fails, and the module appears to do nothing; the same pattern also hides real bugs from the test suite.
  ```
  print(f"Error updating selected tube: {e}")
  ```
  Suggestion: Report failures via slicer.util.errorDisplay or logging.warning, and let unexpected exceptions propagate to the tryWithErrorDisplay wrapper in onApplyButton.
- **haiku** (minor, high confidence, quote verified) [`EVARSim/EVARSim.py:437`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L437): Several broad except blocks print the exception and continue, so a failing tube update or branch analysis leaves the GUI silently stale. Users see no error dialog or status message.
  ```
          except Exception as e:
              print(f"Error updating selected tube: {e}")
  ```
  Suggestion: Report failures via slicer.util.errorDisplay or logging.error and keep the GUI state consistent.

### No clinical-use or simulation-only disclaimer
minor; utility; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`EVARSim/EVARSim.py:37`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L37): The module simulates endovascular stent placement for EVAR, a clinical procedure. The help text and README do not state that output is not validated for clinical decisions or planning. Users could misread the simulation as clinically accurate.
  ```
  This module allows users to place endovascular devices along centerline curves for EVAR (Endovascular Aneurysm Repair) simulation.
  ```
  Suggestion: Add an explicit research-only / not-for-clinical-use disclaimer to helpText and README.

### No validation or clinical-use disclaimer for a device-sizing simulation tool
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`README.md:157`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/README.md#L157): The module produces stent geometry from centerlines that users may interpret as sizing information, yet there is no statement that results are not validated for clinical decision making, no accuracy/validation data, and the license pointer names a file that does not exist (the file is LICENSE).
  ```
  See License.txt. This extension is developed for medical research and educational purposes.
  ```
  Suggestion: Add an explicit research-only / not-for-clinical-use disclaimer, state the intended accuracy and validation status, and fix the license filename reference.
- **haiku** (minor, high confidence, quote verified) [`README.md:157`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/README.md#L157): The README says the license is in License.txt, but the repository only has LICENSE (Apache-2.0). Users may be unable to find the terms. Low impact; the LICENSE file itself is present and permissive.
  ```
  See License.txt. This extension is developed for medical research and educational purposes.
  ```
  Suggestion: Change the reference to LICENSE (Apache-2.0).

### README instructions and parameter ranges disagree with the module
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:30`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/README.md#L30): The module registers itself under the 'Modeling' category (EVARSim.py line 33) and the UI allows radius 0.1-50, length 0.1-200 and resolution 6-64, while the README says 'Examples', radius 0.1-10.0, length 1.0-200 and resolution 4-32. Users following the README will look in the wrong category and expect different limits.
  ```
  Find "EVARSim" in the module dropdown under the "Examples" category
  ```
  Suggestion: Update the README to match the implemented category and slider ranges.

### Sample data CL_model.vtk is committed but not installed by CMake
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`EVARSim/CMakeLists.txt:11`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/CMakeLists.txt#L11): MODULE_PYTHON_RESOURCES lists only the icon and the .ui file, so EVARSim/CL_model.vtk (290 KB) is not copied into the installed extension. README line 122 states 'The extension includes `CL_model.vtk` - a sample branched centerline file of the aorta and the aortic bifurcation.', which is false for users who install from the extension manager; they have no sample data to try the module with.
  ```
    Resources/UI/${MODULE_NAME}.ui
  ```
  Suggestion: Either install the file (add it to MODULE_PYTHON_RESOURCES / a data directory) or register it as Sample Data, or remove the claim from the README.

### Scene nodes are deleted by name, which can remove user-created nodes
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`EVARSim/EVARSim.py:1180`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L1180): _clearExistingTubes removes any node named EVARSim_Tube_2..EVARSim_Tube_10 and _removeBranchLabels removes any node whose name starts with 'EVARSim_BranchLabel_' (line 592). If a user renamed their own model or fiducial to such a name, pressing Apply or changing the input model deletes it without confirmation.
  ```
  slicer.mrmlScene.RemoveNode(existingNode)
  ```
  Suggestion: Track the created nodes in the parameter node or a member list and remove only those instances.

### Selecting an input model silently adds fiducial nodes to the scene
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`EVARSim/EVARSim.py:563`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L563): _onInputModelChanged calls _analyzeBranches, which calls _createBranchLabels and inserts one markup fiducial per detected line segment into the user's scene. Merely choosing an input model therefore modifies the scene (and the saved .mrrl if the user saves), which is unexpected and can pollute a clinical scene.
  ```
  fiducialNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
  ```
  Suggestion: Make branch labels opt-in via a checkbox, or use a single non-persistent display node / 3D text actor instead of MRML nodes.

### Smoothing-factor slider has no effect on Apply
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`EVARSim/EVARSim.py:1470`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L1470): The GUI exposes a smoothingFactor slider (UI lines 331-350, parameter node line 86) and the live preview uses it, but onApplyButton() (lines 602-611) never passes it to process(), which hardcodes 0.3. A user who sets smoothing to 0 or 1 and presses Apply silently gets 0.3, so the applied result differs from the preview.
  ```
  smoothingFactor = 0.3  # Default smoothing factor for the process method
  ```
  Suggestion: Add a smoothingFactor argument to process() and pass self.ui.smoothingFactorSliderWidget.value from onApplyButton().

### Stale compiled bytecode committed to the repository
minor; packaging; raised by deepseek, haiku; **quote not found in source**
- **deepseek** (minor, high confidence, quote no quote) [`EVARSim/__pycache__/EVARSim.cpython-39.pyc`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/__pycache__/EVARSim.cpython-39.pyc): A 36 KB Python 3.9 bytecode cache of the module is checked in and .gitignore only lists '.DS_Store' and '.git'. It is not installed by CMake so it does not shadow the source, but it is a stale binary artifact that can drift from EVARSim.py and confuses review of what actually runs.
  Suggestion: Remove EVARSim/__pycache__ from the repository and add '__pycache__/' and '*.pyc' to .gitignore.
- **haiku** (minor, medium confidence, quote quote not found) [`EVARSim/__pycache__/EVARSim.cpython-39.pyc:1`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/__pycache__/EVARSim.cpython-39.pyc#L1): EVARSim/__pycache__/EVARSim.cpython-39.pyc (36 KB) is a generated artifact that is committed, and .gitignore does not exclude it. The 290 KB CL_model.vtk sample is also committed. The bytecode may be stale against the source and adds clutter to the extension source.
  ```
  EVARSim/__pycache__/EVARSim.cpython-39.pyc  (36536 bytes, binary)
  ```
  Suggestion: Remove __pycache__ from the repository, add it to .gitignore, and keep sample data only if it is needed by the documented workflow.

### Unused and dead code paths referencing wrong signatures
minor; soundness; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`EVARSim/EVARSim.py:980`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L980): _createMultipleTubes (line 980) and _createSeparateTubes (line 1055) are never called, and numpy is imported but unused in _extractCenterlineFromModel (line 641). This makes the actual behaviour harder to follow for reviewers and future maintainers.
  ```
  def _createMultipleTubes(self, curvePoints: vtk.vtkPoints, radius: float, length: float,
  ```
  Suggestion: Remove the unused methods and imports, or wire them up if they are intended features.
- **haiku** (minor, low confidence, quote verified) [`EVARSim/EVARSim.py:980`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L980): _createMultipleTubes, _createSeparateTubes, and _createAdditionalTubes are not called from the current flow or have mismatched parameters. The dead code increases maintenance risk and hides the test mismatch.
  ```
  def _createMultipleTubes(self, curvePoints: vtk.vtkPoints, radius: float, length: float,
  ```
  Suggestion: Remove dead helpers or consolidate tube creation into one code path.

### process() assumes a 3D view exists when showResult is True
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`EVARSim/EVARSim.py:1508`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L1508): If the user has a layout without a 3D view (e.g. only slice views), threeDWidget(0) returns None and threeDView.resetFocalPoint() raises AttributeError after the model was already created, so the operation reports failure even though it succeeded.
  ```
  threeDWidget = layoutManager.threeDWidget(0)
  ```
  Suggestion: Check threeDWidget for None before calling resetFocalPoint().

### Full geometry rebuild on every slider tick runs on the GUI thread
info; soundness; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`EVARSim/EVARSim.py:142`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L142): Each slider movement triggers _updateSelectedTube, which re-extracts/smooths the centerline and rebuilds the tube synchronously in the GUI thread; with a large input model (the O(points x 20 slices) scan in _findCenterAtLevel) the UI will freeze while dragging.
  ```
  self.ui.cylinderRadiusSliderWidget.connect("valueChanged(double)", self._onParameterChanged)
  ```
  Suggestion: Debounce the preview (e.g. QTimer) or move the computation to a background thread with progress reporting.

### Integer-valued parameters typed as float in the parameter node
info; soundness; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`EVARSim/EVARSim.py:84`](https://github.com/rwic/SlicerEVARSim/blob/0568d174ab552f3ff41e42d380e2cfaf80a35e8e/EVARSim/EVARSim.py#L84): numberOfTubes and cylinderResolution are counts but are declared as float and converted with int() at every use site (lines 269, 609-610), which is fragile if a non-integral value ever reaches them.
  ```
  numberOfTubes: Annotated[float, WithinRange(1.0, 10.0)] = 1.0
  ```
  Suggestion: Use Annotated[int, WithinRange(1, 10)] and Annotated[int, WithinRange(6, 64)].


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): minor issues
No network access, downloads, subprocesses, eval/exec, pickle or file writes: the module only manipulates MRML nodes, so the security and environment requirements are met (numpy is imported lazily and ships with Slicer; no pip installs, no sys.path or logging changes). Apache-2.0 LICENSE is present and the catalog entry (category Modeling, build_subdirectory ".", EXTENSION_DEPENDS "NA" vs empty build_dependencies) is consistent. Main defects are quality issues: the registered in-module unittest calls logic.process() with the wrong signature and will fail, the sample CL_model.vtk is not installed by CMake although the README says it is included, a stale __pycache__ .pyc is committed, and the smoothing slider is ignored by process(). 🟢 Recommend merge per index policy; the listed items are non-blocking fixes.
Not checked: Could not verify that the catalog scm_revision 'main' resolves to the stated commit 0568d174ab552f3ff41e42d380e2cfaf80a35e8e (no network access); the review covers the file contents provided for that revision.; Could not inspect the binary files EVARSim/CL_model.vtk, EVARSim.png, EVARSim/Resources/Icons/1.jpeg and EVARSim/__pycache__/EVARSim.cpython-39.pyc; the .vtk sample was not parsed for embedded scripts or unexpected content.; Could not run the module, the registered unittest, or the extension build, so the reported test failure is derived from reading the call site and the process() signature, not from an executed test run.; Could not check CI/build results for this extension on the Slicer extension factory or the repository's issue tracker/maintenance activity.
Questions for the author: Was the in-module test (EVARSim.py line 1567) ever run after the process() signature changed? It currently raises TypeError.; Should CL_model.vtk be installed with the extension or registered as Sample Data so users can try the module?; Is the smoothing-factor slider intended to affect the applied result, or only the live preview?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
EVARSim is a well-structured 3D Slicer extension for simulating endovascular aneurysm repair (EVAR) device placement along centerlines. Code inspection reveals proper use of Slicer scripted module conventions, parameter nodes, observer cleanup, and VTK filters without introducing safety risks or environmental side effects. The extension includes proper CMake configuration, an Apache 2.0 license, and documentation. 🟢 Recommend merge
Not checked: Execution and runtime behavior inside 3D Slicer application

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
No malicious behavior, network access, package installation, or environment changes were found in EVARSim.py. The main defects are soundness/testing: the bundled unit test calls logic.process with the wrong arguments and would fail with a TypeError, and the README points to a nonexistent License.txt. Documentation lacks any clinical-use or simulation-only disclaimer. Apache-2.0 LICENSE is present. Catalog entry is structurally usable (scm_revision is a branch, "main"). Overall: minor fixes needed before wider distribution.
Not checked: The UI file EVARSim/Resources/UI/EVARSim.ui was not read; widget names used in the code were only checked by search.; Source repository at scm_url was not fetched; scm_revision is the branch 'main', so the exact reviewed commit is unknown beyond the commit in the request header.; No Slicer runtime was available, so the module was not loaded, the test was not run, and the GUI behavior was not exercised.; CL_model.vtk and the icon/screenshot binaries were not inspected for content.; Build from the catalog entry was not performed.


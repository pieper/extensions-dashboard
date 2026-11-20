# AI review: FiducialsToModelDistance

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance at commit `9ba774a39460fac85da215c5cfbbb19881094d6b`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-20T03:06:28Z; cost $0.02

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | ok | ok | ok |
| packaging | ok | ok | minor |
| license | blocking | blocking | blocking |
| soundness | concern | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer scripted module that computes distances between a set of fiducial (markup) points and either a surface model or a second fiducial set, writing per-point distances and summary error metrics (mean, RMS, max/min, Hausdorff) into table nodes. It targets researchers quantifying registration or model-fitting accuracy.
- **flash-lite**: FiducialsToModelDistance is a 3D Slicer scripted module extension that computes distances between a set of fiducial points and either a model surface or another set of fiducial points, outputting summary metrics and detailed distance tables.
- **haiku**: A 3D Slicer scripted module that computes distances from fiducial points to a model surface or to another fiducial set, and writes summary metrics and per-point distances to table nodes. It is intended for researchers doing registration or error analysis.

## Disagreements (start here)

### D1. Missing license file
single; category license; raised by flash-lite
- **flash-lite** (blocking, high confidence, quote no quote) no file cited: No license file (such as LICENSE, LICENSE.txt, or COPYING) is present in the repository or referenced in metadata, meaning clear distribution permission is missing.
  Suggestion: Add an open source license file (e.g., MIT, Apache-2.0, or BSD) to the repository.

### D2. No license file, headers or terms anywhere in the repository
partial; category license; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`README.md:1`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/README.md#L1): A repository-wide search for 'licen[cs]e|copyright|BSD|Apache|MIT' returned no matches: there is no LICENSE/COPYING file, no license header in FiducialsToModelDistance/FiducialsToModelDistance.py, and README.md states no terms. Without explicit permission, the Extensions Index cannot redistribute the extension in the binary package, so the 'clear distribution permission' admission requirement is unmet.
  ```
  # Fiducials to model distance
  
  This is an extension for 3D Slicer that computes distance between two point sets or a point set and a surface mesh.
  ```
  Suggestion: Add a LICENSE file (any OSI-approved license is acceptable, e.g. the Slicer BSD-3-Clause style) and reference it from README.md and the module's acknowledgementText.
- **haiku** (blocking, high confidence, quote verified) [`README.md:3`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/README.md#L3): The repository has no LICENSE/COPYING file, and a text search for 'license' or 'copyright' across the repository returns nothing. README.md and the module header give no terms, so the extension and its contributors' code have no stated distribution permission. The index policy requires clear distribution terms before the extension can be offered to users.
  ```
  This is an extension for 3D Slicer that computes distance between two point sets or a point set and a surface mesh.
  ```
  Suggestion: Add a LICENSE file (any OSI-approved or equivalent license) at the repository root and state the license in README.md.

### D3. Hausdorff distance is computed with min() instead of max()
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`FiducialsToModelDistance/FiducialsToModelDistance.py:267`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/FiducialsToModelDistance/FiducialsToModelDistance.py#L267): The symmetric Hausdorff distance is the maximum over both directions of the per-point minimum distances, but the code takes the minimum of the two minima. For the module's own test data (moving points 1.25-2.3 mm from the fixed set) the reported value is 1.25 mm instead of 2.3 mm, and the test at line 362 asserts the wrong value, so the bug is locked in. Users comparing registration accuracy would systematically under-report the worst-case error.
  ```
            # Hausdorff Distance is the max of the minimum distances
            inversePointDistances, inverseLabels = self.pointDistancesLabelsFromPoints(inputReference, inputPoints)
            metricLabels.append("Hausdorff Distance")
            metricValues.append(max(abs(pointDistances).min(), abs(inversePointDistances).min()))
  ```
  Suggestion: Use max(abs(pointDistances).max(), abs(inversePointDistances).max()) and update the expected value in the test to 2.3.
- **haiku** (minor, medium confidence, quote partly verified) [`FiducialsToModelDistance/FiducialsToModelDistance.py:267`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/FiducialsToModelDistance/FiducialsToModelDistance.py#L267): For fiducial-to-fiducial comparisons, the code takes max(min distance of A to B, min distance of B to A) (line 270). The symmetric Hausdorff distance is the max over points of the nearest-neighbour distance, so this min-based value can understate it. Users reporting it as Hausdorff could be misled.
  ```
  # Hausdorff Distance is the max of the minimum distances
   metricValues.append(max(abs(pointDistances).min(), abs(inversePointDistances).min()))
  ```
  Suggestion: Use the max of per-point nearest distances in each direction, or rename the metric and document the definition.

### D4. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### Catalog tracks moving branch 'master' instead of a pinned commit
minor; packaging; raised by haiku; **quote not found in source**
- **haiku** (minor, high confidence, quote quote not found) no file cited: scm_revision is 'master', so the built extension is whatever master points to at build time. The reviewed commit 9ba774a39460fac85da215c5cfbbb19881094d6b is not what the index will build, and later changes would bypass review.
  ```
  "scm_revision": "master",
  ```
  Suggestion: Pin scm_revision to a reviewed commit hash (or a release tag) in the catalog entry.

### Long computation runs on the GUI thread without progress or cancellation
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`FiducialsToModelDistance/FiducialsToModelDistance.py:135`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/FiducialsToModelDistance/FiducialsToModelDistance.py#L135): compute() is called directly from the button slot; the nested loops in pointDistancesLabelsFromPoints (lines 177-191) are O(n*m) and the surface path builds a vtkImplicitPolyDataDistance over the full mesh. With large fiducial sets or dense models Slicer freezes with no progress bar and no way to cancel, which looks like a crash to the user.
  ```
      def onApplyButton(self):
        logic = FiducialsToModelDistanceLogic()
        try:
          logic.compute(self._parameterNode.GetNodeReference("InputPoints"), self._parameterNode.GetNodeReference("InputReference"),
  ```
  Suggestion: Use slicer.util.ProgressDialog / a CLI-style progress callback, or run the computation in a worker thread with progress and cancellation.

### Metrics table is not cleared, so stale columns persist between runs
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`FiducialsToModelDistance/FiducialsToModelDistance.py:252`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/FiducialsToModelDistance/FiducialsToModelDistance.py#L252): The distances table is cleared with RemoveAllColumns() (line 247) but the metrics table is only passed to slicer.util.updateTableFromArray, which adds/overwrites the named columns without removing others. If a user first computes fiducial-to-model metrics (Mean Absolute Distance, Maximum Absolute Distance, ...) and then fiducial-to-fiducial metrics into the same table, the absolute-distance columns remain and the table mixes results from two different runs.
  ```
        if outputMetricsTable:
          import numpy as np
          metricValues = []
          metricLabels = []
  ```
  Suggestion: Call outputMetricsTable.RemoveAllColumns() (or reset the table) before writing the new metrics.

### Missing input validation for the input points node
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`FiducialsToModelDistance/FiducialsToModelDistance.py:228`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/FiducialsToModelDistance/FiducialsToModelDistance.py#L228): compute() dereferences inputReference and inputPoints without None checks; the GUI selectors have noneEnabled=false so the normal path is safe, but the logic class is public API and the test calls it directly. A None input produces an AttributeError that is only caught by the generic handler in onApplyButton, giving a confusing message.
  ```
      def compute(self, inputPoints, inputReference, outputMetricsTable, outputDistancesTable):
  
        if inputReference.IsA("vtkMRMLMarkupsFiducialNode"):
  ```
  Suggestion: Validate that inputPoints and inputReference are not None and raise a clear ValueError.

### No usage documentation, sample data or clinical disclaimer
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:8`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/README.md#L8): README.md only describes the purpose and shows two screenshots; there is no step-by-step tutorial, no sample scene, and no statement about intended (research) use. Users must guess the workflow, and there is no warning that the metrics are not validated for clinical decision making.
  ```
  This module was primarily designed to compute distances from a low density point cloud of fiducial points to the surface of a model.
  ```
  Suggestion: Add a short usage section (select input points, reference, output tables, press Apply) and a research-use disclaimer.

### Signed minimum distance reported without documentation
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`FiducialsToModelDistance/FiducialsToModelDistance.py:263`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/FiducialsToModelDistance/FiducialsToModelDistance.py#L263): 'Minimum Distance' is computed from signed values (line 264) while 'Maximum Absolute Distance' is used for the surface case, so users get a negative minimum that is not explained in the UI or README. This is confusing for clinical error reporting.
  ```
  metricLabels.append("Minimum Distance")
   metricValues.append(pointDistances.min())
  ```
  Suggestion: Document the sign convention in the help text, or report absolute values consistently.

### Surface distance uses the raw polydata without checking for a non-closed mesh
minor; soundness; raised by deepseek
- **deepseek** (minor, low confidence, quote verified) [`FiducialsToModelDistance/FiducialsToModelDistance.py:200`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/FiducialsToModelDistance/FiducialsToModelDistance.py#L200): vtkImplicitPolyDataDistance returns signed distances whose sign depends on surface orientation, so for open or inconsistently oriented meshes the 'Mean Distance'/'Minimum Distance' values can be misleading while the absolute variants are fine. This is a documented-behaviour caveat rather than a crash, but the module presents signed values without any note.
  ```
        # Transform model polydata to world coordinate system
        if inputModel.GetParentTransformNode():
  ```
  Suggestion: Document that signed distances depend on mesh orientation and that absolute metrics should be used for open surfaces.

### Test coverage and disclaimer are limited
minor; utility; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`FiducialsToModelDistance/Testing/Python/CMakeLists.txt:2`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/FiducialsToModelDistance/Testing/Python/CMakeLists.txt#L2): The Testing/Python directory contains only a commented-out registration, but the module's own unittest is still registered by slicer_add_python_unittest in FiducialsToModelDistance/CMakeLists.txt line 27, so the test does run. The empty directory is harmless clutter.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Remove the unused Testing/Python directory or add a real test file.
- **haiku** (minor, medium confidence, quote verified) [`FiducialsToModelDistance/Testing/Python/CMakeLists.txt:2`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/FiducialsToModelDistance/Testing/Python/CMakeLists.txt#L2): The only test is a single ScriptedLoadableModuleTest case. The separate Testing/Python test file is commented out, and the test depends on a node named 'Model' existing (line 310). The README has no clinical-use disclaimer for a tool that computes surgical or registration error metrics.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Enable or remove the commented test, add a clinical-use disclaimer, and document sign and definition conventions for the metrics.

### Catalog entry pins a moving branch and the source revision could not be verified
info; packaging; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`CMakeLists.txt:13`](https://github.com/ReynoldsJ20/SlicerFiducialsToModelDistance/blob/9ba774a39460fac85da215c5cfbbb19881094d6b/CMakeLists.txt#L13): The catalog entry uses scm_revision 'master' and EXTENSION_DEPENDS 'NA' with empty build_dependencies, which is consistent with the source (no dependencies are used). I could not resolve the commit 9ba774a39460fac85da215c5cfbbb19881094d6b or the branch tip from this environment, so the exact reviewed revision is unverified; the code shown is what was reviewed.
  ```
  set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any
  ```
  Suggestion: No action required for the dependency settings; consider whether a fixed revision is preferable for reproducibility.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Small, self-contained scripted module with no network access, no downloads, no pip installs and no global side effects; it only uses Slicer's own VTK/numpy and writes results into user-selected table nodes. Packaging is conventional and complete (all imported Python files and resources are installed by CMake), and the catalog entry is consistent with the source. The main gap is licensing: no LICENSE file, no license headers, and no terms in the README, so distribution permission is not established. Remaining issues are ordinary correctness bugs (Hausdorff metric, stale metric columns, no progress/threading) and thin documentation.
Not checked: Could not resolve the git revision 9ba774a39460fac85da215c5cfbbb19881094d6b or the current master tip; the review covers the file contents provided in the submission.; Binary files (FiducialsToModelDistance.png, Screenshots/*.PNG) were not inspected beyond their sizes.; No build or test run was possible, so the CMake configuration and the module's unittest were not executed.; Repository metadata such as commit history, maintenance activity, issues and CI status was not accessible.
Questions for the author: Which license applies to this extension, and can a LICENSE file be added to the repository?; Is the 'Hausdorff Distance' metric intended to be the symmetric maximum (max of the two directed maxima)? The current code and test use the minimum.; Should the metrics table be cleared between runs so that fiducial-to-model and fiducial-to-fiducial results are not mixed in one table?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): needs fixes

Not checked: Execution of tests inside 3D Slicer runtime environment
Questions for the author: Please add a license file to the repository to grant clear distribution and use permissions.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The Python module is small and local-only: no network access, no package installs, no subprocess or eval, and it uses the standard ScriptedLoadableModule structure with observer cleanup. The main admission blocker is that the repository contains no license file or license text, so distribution permission is not established. The catalog also tracks the moving branch "master" rather than a pinned commit. Soundness issues are minor: a Hausdorff-style metric and a signed "Minimum Distance" are not clearly defined, and tests are thin.
Not checked: The .ui file and icon under Resources/ were not read; only their existence in the listing was confirmed.; The source at the pinned commit 9ba774a39460fac85da215c5cfbbb19881094d6b was not fetched; the review is of the content supplied in the prompt.; No build, install or run of the module in Slicer was performed.; The .gitignore, screenshots and the remote repository's license file (if any outside this checkout) were not inspected beyond the listing.


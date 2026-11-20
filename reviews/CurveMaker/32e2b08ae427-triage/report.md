# AI review: CurveMaker

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/tokjun/CurveMaker at commit `32e2b08ae427074f0d4c98261d53857c9962382f`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-20T02:54:59Z; cost $0.03

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | ok | ok | ok |
| packaging | minor | ok | minor |
| license | blocking | blocking | concern |
| soundness | concern | ok | concern |
| utility | minor | ok | concern |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **deepseek**: CurveMaker is a Slicer scripted module that turns a list of fiducial/markup points into a 3D curve (optionally a closed ring, optionally a cardinal spline) rendered as a tube model, and reports curve length, point-to-curve distances and per-point curvature. It targets researchers who need a quick spline/tube through landmarks, e.g. for trajectory or catheter-path visualization.
- **flash-lite**: CurveMaker is a 3D Slicer scripted module that generates a 3D curve model and tube from a list of fiducial points, with support for interpolation, length measurement, point-to-curve distance calculations, and curvature analysis.
- **haiku**: CurveMaker is a scripted 3D Slicer module that builds a tube-shaped 3D curve model through the fiducials of a Markups node, with optional cardinal-spline interpolation, ring mode, curvature coloring, and point-to-curve distance readouts. It is intended for Slicer users who need to visualize or measure fiducial-based curves, such as needle or catheter paths.

## Disagreements (start here)

### D1. Missing License File
single; category license; raised by flash-lite
- **flash-lite** (blocking, high confidence, quote no quote) no file cited: The repository does not contain a license file or licensing terms specifying how the extension may be used or distributed. Under the review policy, missing distribution permission is a blocking admission requirement.
  Suggestion: Add a LICENSE file (e.g., MIT, Apache 2.0, or similar) to the repository to grant clear distribution and usage permissions.

### D2. No license file or license terms anywhere in the repository
partial; category license; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`README.md:1`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/README.md#L1): The repository listing contains only CMakeLists.txt, CurveMaker.png, README.md, CurveMaker/CMakeLists.txt, CurveMaker/CurveMaker.py, the icon and the Testing CMakeLists files; a case-insensitive search for 'license|copyright|BSD|MIT|apache' over all text files returned no matches. Without any license or copyright grant, users and the extension index have no permission to redistribute the module, so the distribution-permission admission requirement is unmet.
  ```
  CurveMaker
  ==========
  
  3D Slicer scripted module to generage a curve from a list of fiducials.
  ```
  Suggestion: Add a LICENSE file (any OSI-approved or otherwise permissive license is acceptable) and a short copyright/license statement in README.md and/or the header of CurveMaker.py.
- **haiku** (major, medium confidence, quote verified) [`README.md:1`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/README.md#L1): Nothing in the provided tree grants terms for redistributing CurveMaker. The file list contains CMakeLists.txt, README.md, CurveMaker.py, and an icon, but no LICENSE. Without explicit terms, the Index cannot confirm that distribution is permitted. The author should add a license file, or the reviewer should confirm one exists at the pinned revision.
  ```
  CurveMaker
  ==========
  
  3D Slicer scripted module to generage a curve from a list of fiducials.
  ```
  Suggestion: Add a LICENSE file (for example BSD or MIT) at the repository root and reference it in the README and the module metadata.

### D3. distanceToPoint() returns a scalar that the caller unpacks as a tuple
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified, other lines) [`CurveMaker/CurveMaker.py:952`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L952): updateTargetFiducialsTable() does '(err, evec) = self.logic.distanceToPoint(pos, extrapolate)' (line 613). Before any curve has been generated CurvePoly is None, so distanceToPoint returns a float and the unpacking raises TypeError, breaking the Distance table as soon as a target markups node is selected before pressing 'Generate Curve'.
  ```
  if self.CurvePoly == None:
        return numpy.Inf
  ```
  Suggestion: Return a tuple such as (float('inf'), numpy.zeros(3)) in the early-return branch, or handle the None-curve case in the caller.
- **haiku** (major, high confidence, quote verified, other lines) [`CurveMaker/CurveMaker.py:952`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L952): When no curve has been generated, distanceToPoint returns numpy.Inf. updateTargetFiducialsTable unpacks the result into (err, evec), so it raises TypeError. This happens when the user selects a target fiducial list while the source curve is absent, for example after the Source selector is set to None. The GUI callback fails with an unhandled exception.
  ```
        if self.CurvePoly == None:
          return numpy.Inf
  ```
  Suggestion: Return a tuple, for example `return (numpy.Inf, numpy.array([0.0, 0.0, 0.0]))`, and fix the caller's unpacking accordingly.

### D4. setup() assumes a 3D view exists and crashes in layouts without one
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`CurveMaker/CurveMaker.py:368`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L368): When the module is opened while the current layout has no 3D view (for example 'Red slice only' or a custom slice-only layout), layoutManager.threeDWidget(0) returns None, so .threeDView() raises AttributeError during setup() and the module panel fails to build. The scalar bar is also bound to whichever 3D view happened to be first, and is never re-bound or detached.
  ```
  layout = slicer.app.layoutManager()
      view = layout.threeDWidget(0).threeDView()
      renderer = layout.activeThreeDRenderer()
      self.scalarBarWidget.SetInteractor(renderer.GetRenderWindow().GetInteractor())
  ```
  Suggestion: Guard the 3D-view lookup (skip scalar-bar setup when no 3D view is available) and attach the scalar bar lazily when curvature display is enabled, or use the view's own renderer via a layout observer.

### D5. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D6. Rating of utility
rating dispute; category utility; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings from some reviewers

### Division by zero for coincident control points in curvature and spline code
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`CurveMaker/CurveMaker.py:905`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L905): computeCurvatures divides by ds, the distance between consecutive points, without checking for zero. Two identical adjacent fiducials give a NaN or ZeroDivisionError during curvature updates. This is an ordinary robustness bug.
  ```
        for i in range(1,n-1):
          p = numpy.array(points.GetPoint(pts.GetId(i+1)))
          ds = numpy.linalg.norm(p-pp)
          T  = (p-pp) / ds
  ```
  Suggestion: Skip or merge duplicate points before computing tangents, and guard the division.

### Icon file present but not installed through CMake resources
minor; packaging; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`CurveMaker/CMakeLists.txt:9`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CMakeLists.txt#L9): CurveMaker/Resources/Icons/CurveMaker.png exists, but MODULE_PYTHON_RESOURCES is empty, so the icon is not installed with the module. The module's icon depends on the external URL in the root CMakeLists instead.
  ```
  set(MODULE_PYTHON_RESOURCES
    )
  ```
  Suggestion: Add Resources/Icons/CurveMaker.png to RESOURCES, or delete the unused file.

### Minimum curvature is always reported as 0 or below
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified, other lines) [`CurveMaker/CurveMaker.py:914`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L914): minKappa is initialized to 0.0 and kappa is a norm, so it is never negative. Its update is therefore never triggered, so the 'Minimum' readout in the GUI always shows 0. The max branch is also an elif, so a value that lowers the minimum cannot also raise the maximum. Users relying on the min/max readouts get wrong values.
  ```
          if kappa < minKappa:
            minKappa = kappa
          elif kappa > maxKappa:
            maxKappa = kappa
  ```
  Suggestion: Initialize minKappa and maxKappa from the first kappa value (or to +/-inf), and use two independent `if` statements.

### No documentation, tutorial, sample data or tests; overlaps MarkupsToModel
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:1`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/README.md#L1): The only documentation is a two-line README (with a typo); there is no tutorial, no sample markups, no screenshots in the repository and no working test. The core function (fit a curve through markups and render it as a tube) is already provided by the MarkupsToModel extension, so users have no guidance on when to prefer this module.
  ```
  CurveMaker
  ==========
  
  3D Slicer scripted module to generage a curve from a list of fiducials.
  ```
  Suggestion: Add a README with usage steps and a sample .mrk.json, and state the difference from MarkupsToModel.

### No functional tests; test module commented out
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`CurveMaker/Testing/Python/CMakeLists.txt:2`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/Testing/Python/CMakeLists.txt#L2): The only test wiring is a commented-out line in Testing/Python/CMakeLists.txt, and the in-script unittest is not exercised by CMake. Regressions such as the distanceToPoint and curvature bugs above would not be caught by CI.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a unit test that exercises the logic class (nodeToPoly, distanceToPoint, computeCurvatures) without the GUI, and register it with slicer_add_python_unittest.

### Registered unittest does not exist in the module script
minor; packaging; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CurveMaker/CMakeLists.txt:23`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CMakeLists.txt#L23): CurveMaker.py imports unittest (line 2) but defines no unittest.TestCase subclass, and CurveMaker/Testing/Python/CMakeLists.txt has its test commented out. The generated ctest therefore has nothing to run and will fail or silently pass, so the extension has no automated coverage.
  ```
  # Register the unittest subclass in the main script as a ctest.
    # Note that the test will also be available at runtime.
    slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)
  ```
  Suggestion: Add a CurveMakerTest(unittest.TestCase) class exercising nodeToPoly/calculateLineLength/distanceToPoint, or remove the registration.

### Tag used before assignment in target-fiducials handler
minor; soundness; raised by haiku
- **haiku** (minor, low confidence, quote verified) [`CurveMaker/CurveMaker.py:572`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L572): onTargetFiducialsSelected reads self.tag, which is only assigned in setup when a target node is chosen. This works only because targetFiducialsNode is None initially. It is fragile: self.tag is never initialized in setup, so any change to that guard can raise AttributeError.
  ```
        if self.targetFiducialsNode and self.tag:
          self.targetFiducialsNode.RemoveObserver(self.tag)
  ```
  Suggestion: Initialize self.tag = None in setup() alongside targetFiducialsNode.

### Unbound nnvec when two consecutive curve points coincide
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CurveMaker/CurveMaker.py:1059`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L1059): If a segment has zero length (duplicate control points, or a spline that produces repeated samples), nnvec is never assigned and numpy.inner(op, nnvec) raises UnboundLocalError, aborting the distance table update. computeCurvatures() has the analogous division by ds without a zero check (lines 906-909).
  ```
  norm = numpy.linalg.norm(nvec)
        if norm != 0:
          nnvec = nvec / norm
  
        # Calculate the distance between the point and the segment
        mag2 = 0.0
  ```
  Suggestion: Skip zero-length segments (continue) or initialise nnvec to a zero vector and guard the divisions.

### cleanup() does nothing, leaving observers and the scalar bar attached
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`CurveMaker/CurveMaker.py:386`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L386): Observers are added to the source markups node, the destination model node and its display node (lines 407, 426, 429, 578) but never removed when the module widget is closed or the scene is closed. The observers keep references to the widget's Python methods, so later node modifications can call into a half-destroyed widget, and the vtkScalarBarWidget stays registered with the 3D view interactor.
  ```
  def cleanup(self):
      pass
  ```
  Suggestion: Remove all observer tags and disable the scalar bar widget in cleanup(), and reset the stored node references.
- **haiku** (minor, medium confidence, quote verified) [`CurveMaker/CurveMaker.py:386`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L386): cleanup() is an empty pass, so PointModifiedEvent and ModifiedEvent observers registered on the Markups/Model nodes persist when the module is closed or reloaded. Separately, onSourceSelected does not reset tagSourceNode or self.logic.SourceNode when the selector is cleared, so a later callback can act on a removed node. This can cause duplicate or stale updates.
  ```
      def cleanup(self):
        pass
  
      def onEnableAutoUpdate(self, state):
  ```
  Suggestion: Implement cleanup() to call RemoveObserver for all stored tags, and reset the tags and node references when the selection is cleared.

### cmake_minimum_required(VERSION 2.8.9) is rejected by CMake 4
minor; packaging; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`CMakeLists.txt:1`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CMakeLists.txt#L1): CMake 4.x removed compatibility with cmake_minimum_required values below 3.5 and errors out, so the extension cannot be configured on a modern build machine unless the Slicer superbuild injects CMAKE_POLICY_VERSION_MINIMUM.
  ```
  cmake_minimum_required(VERSION 2.8.9)
  ```
  Suggestion: Raise the minimum to a version supported by current Slicer builds (e.g. 3.16 or higher).
- **haiku** (minor, medium confidence, quote verified) [`CMakeLists.txt:6`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CMakeLists.txt#L6): scm_revision is 'master', a moving branch, so the reviewed code can change without a catalog update. The README is three lines, with no usage instructions, sample data, or tutorial, and it points to an outdated wiki URL in CMakeLists.txt. This limits how well users can adopt the module.
  ```
  set(EXTENSION_HOMEPAGE "https://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/CurveMaker")
  ```
  Suggestion: Pin scm_revision to a tagged commit, and add usage documentation and a link to a working homepage.

### numpy.Inf removed in NumPy 2 breaks distance computation
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CurveMaker/CurveMaker.py:1048`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L1048): numpy.Inf was deprecated in NumPy 1.20 and removed in NumPy 2.0; on a Slicer build shipping NumPy 2 the Distance table raises AttributeError. The same alias is used at line 1035.
  ```
  minMag2 = numpy.Inf
  ```
  Suggestion: Use float('inf') or numpy.inf.

### Legacy Slicer-4 idioms and unused imports
info; soundness; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`CurveMaker/CurveMaker.py:1`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L1): os, math and unittest are unused; 'from __main__ import ...' is the pre-Slicer-5 pattern (slicer.util / slicer.qSlicerWidget imports are preferred), and self.tag is never initialised in setup() (line 43 is commented out) although onTargetFiducialsSelected reads it at line 572. None of this changes behavior today but makes the module fragile.
  ```
  import os
  import unittest
  from __main__ import vtk, qt, ctk, slicer
  import math
  import numpy
  ```
  Suggestion: Drop unused imports, initialise self.tag = None in setup(), and modernise the imports.
- **haiku** (info, medium confidence, quote verified) [`CurveMaker/CurveMaker.py:1`](https://github.com/tokjun/CurveMaker/blob/32e2b08ae427074f0d4c98261d53857c9962382f/CurveMaker/CurveMaker.py#L1): The module uses `from __main__ import vtk, qt, ctk, slicer` and the PythonQt-style connect() calls, along with unused imports os and unittest. Compatibility with the current Slicer release was not verified. These are non-blocking, but they should be modernized.
  ```
  import os
  import unittest
  from __main__ import vtk, qt, ctk, slicer
  ```
  Suggestion: Verify the module loads and runs on the current Slicer release, then replace the __main__ imports with explicit imports.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
No malicious or network behavior: the module only uses Slicer/VTK/numpy, installs nothing and transmits nothing, so safety and environment are fine. However the repository contains no license file or license headers anywhere (README.md is four lines, no terms), which blocks distribution permission. Soundness has real defects: setup() assumes a 3D view exists, distanceToPoint() returns a bare numpy.Inf that the caller unpacks as a tuple, observers are never removed in cleanup(), and numpy.Inf no longer exists in NumPy 2. Documentation is a two-line README with no tutorial, sample data or tests, and functionality overlaps the MarkupsToModel extension.
Not checked: Whether the catalog revision 'master' currently resolves to the reviewed commit 32e2b08ae427074f0d4c98261d53857c9962382f (no network access; the entry uses a moving branch reference, which is allowed but means an approval covers only the reviewed source).; Whether slicerMacroBuildScriptedModule installs CurveMaker/Resources/Icons/CurveMaker.png even though MODULE_PYTHON_RESOURCES is empty (CurveMaker/CMakeLists.txt:9-10); if it does not, the module will show a generic icon.; Whether the extension actually builds and loads on current Slicer versions (no build or Slicer runtime available).; Whether the referenced wiki homepage/screenshot URLs in CMakeLists.txt:6,10,11 still exist.; Git history, maintenance activity and issue tracker of https://github.com/tokjun/CurveMaker.
Questions for the author: Which license governs CurveMaker, and can a LICENSE file be added so the extension may be redistributed?; Was the module tested on a current Slicer 5.x build, in particular in a layout without a 3D view and with NumPy 2?; Is the module still maintained, given that MarkupsToModel already provides curve fitting and tube rendering from markups?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): needs fixes
CurveMaker is a well-structured 3D Slicer scripted module for generating 3D curves and tubes from markups/fiducials, calculating lengths, point-to-curve distances, and curvature. The code conforms to Slicer standards and has no safety or environmental issues. However, the repository lacks a license file, which is a blocking requirement for clear distribution permission under the Extensions Index policy.
Not checked: Remote repository contents beyond the inspected files (though catalog entry points to https://github.com/tokjun/CurveMaker at master)
Questions for the author: Does the repository have a license granting permission for distribution in the Slicer Extensions Index?

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The module is small, local-only, and does no network access, package installation, or unsafe deserialization, so I found no safety concern. The main problems are on the admission side: no LICENSE file appears in the reviewed snapshot, so distribution permission is unverified. There are also soundness bugs: distanceToPoint returns a bare value where callers unpack a tuple, and the minimum-curvature computation is wrong. The entry pins to branch "master", has no tests, and has minimal documentation. Overall: needs fixes.
Not checked: The source repository at tokjun/CurveMaker was not fetched. The 'master' ref was not resolved, and the commit 32e2b08 is unverified against the snapshot provided.; Whether a LICENSE file exists at the upstream repository root (the snapshot may be incomplete).; The icon binary (CurveMaker.png) and its contents were not inspected.; The module was not loaded or run in Slicer; GUI behavior and the reported bugs are from static reading only.; No CI or build logs were available.


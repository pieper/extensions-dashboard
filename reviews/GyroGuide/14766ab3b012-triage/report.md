# AI review: GyroGuide

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/lpfang/GyroGuide.git at commit `14766ab3b012c28f5ef0657395256e15b9304073`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-20T03:11:45Z; cost $0.03

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | concern |
| environment | ok | ok | ok |
| packaging | minor | ok | minor |
| license | blocking | ok | blocking |
| soundness | concern | ok | concern |
| utility | concern | ok | concern |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: GyroGuide is a Slicer scripted module for image-guided puncture (e.g. neurosurgical) planning: it takes five registration fiducial markers plus a target and an entry point, computes puncture depth and the angles between the trajectory and three reference planes, draws the planes/path in the 3D view, and optionally sends the resulting transform to an external device over OpenIGTLink. Its users are clinicians preparing a trajectory.
- **flash-lite**: GyroGuide is a 3D Slicer extension that calculates puncture trajectory angles and depth relative to reference planes using fiducial markers, and transmits navigation data via OpenIGTLink.
- **haiku**: GyroGuide is a scripted Slicer module (IGT category) that computes puncture-path depth and angles relative to three reference planes from Markups fiducials, and can send a transform to an external OpenIGTLink device. It is intended for surgical navigation research use by the authors' group and Slicer users.

## Disagreements (start here)

### D1. No license file or license terms in the repository
single; category license; raised by haiku
- **haiku** (blocking, high confidence, quote verified) [`CMakeLists.txt:3`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/CMakeLists.txt#L3): The repository file listing (root and GyroGuide/) has no LICENSE/COPYING file and no license header in the module. Without explicit terms, users and the Extensions Index have no permission to redistribute the extension. Under the index policy, missing distribution terms block approval.
  ```
  project(GyroGuide)
  
  #-----------------------------------------------------------------------------
  set(EXTENSION_HOMEPAGE "https://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/GyroGuide")
  ```
  Suggestion: Add a LICENSE file (any permissive or equivalent open license) at the repository root and a license header in GyroGuide.py.

### D2. No license terms anywhere in the repository
single; category license; raised by deepseek
- **deepseek** (blocking, high confidence, quote verified) [`README.md:4`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/README.md#L4): A repository-wide search for license/copyright/GPL/BSD/MIT/Apache found no LICENSE/COPYING file and no license or copyright header in CMakeLists.txt, GyroGuide/CMakeLists.txt, GyroGuide.py or README.md. Without terms, the Extensions Index (and downstream packagers/mirrors) has no permission to redistribute the extension, and users have no statement of permitted use.
  ```
  An python extension of 3D Slicer which helps surgeons determine the puncture trajectory.
  ```
  Suggestion: Add a LICENSE file (any OSI/permissive license the authors choose) and a matching header or README statement; confirm the authors own the code and the bundled icon.

### D3. Python 2 xrange used in the default Markups calculation path (NameError on Slicer 5)
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`GyroGuide/GyroGuide.py:575`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L575): All three point-collection branches use `xrange` (lines 549, 577, 601), which does not exist in Python 3, so pressing Calculate on any fiducial node raises NameError and no result is produced in Slicer 5. The module also uses the pre-`ScriptedLoadableModule` template and Slicer 3/4 node classes (`vtkMRMLFiducialListNode`, `vtkMRMLAnnotationHierarchyNode`) and deprecated accessors, so it cannot deliver what the catalog description advertises.
  ```
  self.p = numpy.zeros((n,3))
  
                  for j in xrange(n):
  ```
  Suggestion: Port to the current module template (`ScriptedLoadableModule`/`ScriptedLoadableModuleWidget`), replace `xrange` with `range`, and use vtkMRMLMarkupsNode APIs (GetNumberOfControlPoints/GetNthControlPointPosition); test in the targeted Slicer version.
- **haiku** (blocking, high confidence, quote verified) [`GyroGuide/GyroGuide.py:577`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L577): Slicer 5 runs Python 3, where xrange is undefined. When the Markers/Target/Entry nodes are vtkMRMLMarkupsFiducialNode (the normal case, see the nodeTypes filter), the code reaches the loop using xrange and raises NameError. The Calculate button therefore fails before any result is shown.
  ```
                    for j in xrange(n):
  
                        coord = [0.0, 0.0, 0.0]
  
                        self.fids[i].GetNthFiducialPosition(j, coord)
  ```
  Suggestion: Replace xrange with range (also at lines 549 and 601) and test the Calculate path in Slicer 5.

### D4. Angles computed in degrees are fed to numpy trig functions as radians
single; category soundness; raised by haiku
- **haiku** (major, high confidence, quote verified) [`GyroGuide/GyroGuide.py:467`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L467): angleRed/Green/Blue are stored in degrees (arcsin * 180/pi). The transmission code then passes them to numpy.sin/numpy.cos, which expect radians. The rotation matrix sent to the OpenIGTLink device is therefore wrong, which could misdirect a navigation device during a procedure.
  ```
          theta = self.result.angleRed
  
          omega = self.result.angleGreen
  
          phi = self.result.angleBlue
  ```
  Suggestion: Convert the angles to radians (numpy.radians) before building the matrix, and add a unit test comparing the transform to the displayed angles.

### D5. Calculate deletes unrelated scene model nodes by name prefix
single; category safety; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`GyroGuide/GyroGuide.py:717`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L717): Every model node in the scene whose name starts with 'Plane', 'Puncture', 'Project' or 'Line' is removed when the user presses Calculate - not just nodes created by this module (all its lines are even just named 'Line'). A user's own imported/model-maker output (e.g. 'Plane-anatomy', 'Line-of-approach') is silently destroyed in the scene, and the loss is unrecoverable if the scene was not saved; the same pattern removes any transform named 'Result-Data' (line 451-453). Because this happens without confirmation and in a planning workflow, it is a concrete path to losing patient-derived data.
  ```
  if modelName[i][0:5] == 'Plane' or modelName[i][0:8] == 'Puncture' or modelName[i][0:7] == 'Project' or modelName[i][0:4] == 'Line':
  
  
  
                  scene.RemoveNode(model[i])
  ```
  Suggestion: Track the node IDs the module creates and delete only those (or store them under a dedicated subject hierarchy folder), instead of matching name prefixes; prompt before removing nodes the module did not create.

### D6. Clinical guidance output with no disclaimer; blocking GUI sleeps
partial; category safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`GyroGuide/GyroGuide.py:503`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L503): The OpenIGTLink send runs in the button-click slot and freezes Slicer's event loop for two seconds per press, with no progress feedback; the fixed delays are also a fragile substitute for waiting for an actual message handshake.
  ```
  time.sleep(1)
  
          matrix.DeepCopy((e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12,0,0,0,1))
  
          time.sleep(1)
  
  ```
  Suggestion: Push the transform through the connector node without sleep, or run the send asynchronously (e.g. qt.QTimer / cli node) with progress and a status message.
- **haiku** (major, medium confidence, quote verified) [`GyroGuide/GyroGuide.py:503`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L503): The module reports puncture depth and angles and transmits them to a navigation device, but has no statement that it is research-only or not validated. The Send handler blocks the GUI thread with time.sleep(1) twice, so Slicer can freeze while sending, and a wrong transform could be used for navigation.
  ```
          time.sleep(1)
  
          matrix.DeepCopy((e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12,0,0,0,1))
  
          time.sleep(1)
  ```
  Suggestion: Add a clinical-use disclaimer in helpText and the README, remove the sleeps (or use a Qt timer), and check the transform before sending.

### D7. Surgical trajectory tool ships without documentation, validation or clinical disclaimer
single; category utility; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`README.md:1`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/README.md#L1): The module computes puncture angle/depth for neurosurgical puncture and drives an external navigation probe, yet the repository provides only a one-sentence README, no tutorial or sample data, no accuracy/validation evidence, and no statement that it is not approved for clinical use. At tier 3 (community supported), users have no way to judge correctness or suitability for patient care.
  ```
  GyroGuide
  =========
  
  An python extension of 3D Slicer which helps surgeons determine the puncture trajectory.
  ```
  Suggestion: Add usage documentation with sample data, describe how the angles are defined and validated, and include an explicit research/not-for-clinical-use disclaimer until validation is published.

### D8. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D9. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku blocking

### D10. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D11. Rating of utility
rating dispute; category utility; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### CMake registers a unittest on a script that contains no tests; real test target is commented out
minor; packaging; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`GyroGuide/CMakeLists.txt:21`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/CMakeLists.txt#L21): GyroGuide.py defines no unittest.TestCase subclass, so the registered ctest has nothing to run, and GyroGuide/Testing/Python/CMakeLists.txt only contains a commented-out line, leaving the extension without any automated test at tier 3.
  ```
  if(BUILD_TESTING)
  
      # Register the unittest subclass in the main script as a ctest.
  
      # Note that the test will also be available at runtime.
  
  ```
  Suggestion: Add a real ScriptedLoadableModuleTest (or the standard ModuleTest.py) and register it, so the extension has a passing smoke test.

### Calculator returns early but callers assume results exist; 5-marker assumption unchecked
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`GyroGuide/GyroGuide.py:611`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L611): If any selected node has zero points the constructor `return`s (lines 545, 569, 595) leaving `self.position` short, so the following indexing raises IndexError/AttributeError; likewise markers nodes with fewer than five points make `self.position[0][3] - self.position[0][4]` (line 617) fail. The UI enables Calculate for any node with a valid type, so these exceptions reach the user as raw tracebacks.
  ```
  vector1 = self.position[0][0] - self.position[0][1] #a vector in the plane red
  
          vector2 = self.position[0][0] - self.position[0][2] #a vector in the plane red
  ```
  Suggestion: Validate point counts (>=5 markers, >=1 target, >=1 entry, distinct points, non-zero-length vectors) and report a clear message via slicer.util.errorDisplay instead of continuing.
- **haiku** (minor, high confidence, quote verified) [`GyroGuide/GyroGuide.py:611`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L611): The calculation indexes fiducials 0 through 4 of the marker list, and target/entry index 0. A list with fewer than five markers raises IndexError inside the Calculate handler, and no message explains the requirement.
  ```
          vector1 = self.position[0][0] - self.position[0][1] #a vector in the plane red
  
          vector2 = self.position[0][0] - self.position[0][2] #a vector in the plane red
  ```
  Suggestion: Validate the number of markers (5) and target/entry points (1 each) and show a message box.

### Connector-node lookup creates duplicate connector nodes
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`GyroGuide/GyroGuide.py:405`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L405): The else branch is inside the loop, so for every connector node not named 'Send-Data' a new node is created and added; with N existing connectors the scene accumulates extra 'Send-Data' nodes and only the last one is used. Also, `vtkMRMLIGTLConnectorNode` is used without checking that the OpenIGTLink extension is installed.
  ```
  if slicer.mrmlScene.GetNthNodeByClass(i, 'vtkMRMLIGTLConnectorNode').GetName() == 'Send-Data':
  
                      connectorNode = slicer.mrmlScene.GetNthNodeByClass(i, 'vtkMRMLIGTLConnectorNode')
  
                  else:
  
  ```
  Suggestion: Look the node up once outside the loop (e.g. via GetFirstNodeByName) and create it only if absent; guard for a missing vtkMRMLIGTLConnectorNode class.
- **haiku** (minor, medium confidence, quote verified) [`GyroGuide/GyroGuide.py:405`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L405): The connector loop creates a new vtkMRMLIGTLConnectorNode for every existing connector that is not named 'Send-Data', so repeated Send clicks add nodes to the scene. Result transform nodes are also re-created each time.
  ```
                    if slicer.mrmlScene.GetNthNodeByClass(i, 'vtkMRMLIGTLConnectorNode').GetName() == 'Send-Data':
  
                        connectorNode = slicer.mrmlScene.GetNthNodeByClass(i, 'vtkMRMLIGTLConnectorNode')
  
                    else:
  
  ```
  Suggestion: Look up or create a single connector node once, and reuse or update the existing transform node.

### Legacy module structure and unpinned source revision
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`GyroGuide/GyroGuide.py:1`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L1): The module uses plain classes with 'from __main__ import' rather than ScriptedLoadableModule, which is fragile on current Slicer. The catalog pins scm_revision to the branch 'master', so the built code can change without a catalog update.
  ```
  from __main__ import vtk, qt, ctk, slicer
  ```
  Suggestion: Port to ScriptedLoadableModule and pin scm_revision to a specific commit hash.

### No active tests and minimal documentation
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`GyroGuide/Testing/Python/CMakeLists.txt:2`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/Testing/Python/CMakeLists.txt#L2): WITH_GENERIC_TESTS is set, but the module has no test class and the Testing registration is commented out. The README is one sentence, and no sample data or tutorial is included, so maintainers and users cannot verify the geometry.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a unit test with synthetic fiducials and expected angles and depth, and expand the README with usage and a disclaimer.

### OpenIGTLink connection failure is silently ignored
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`GyroGuide/GyroGuide.py:427`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/GyroGuide.py#L427): The result of Start() is never checked and no error is shown, so if the device is unreachable the transform is registered and then the connector is stopped without the user knowing nothing was delivered; a non-numeric port raises an uncaught ValueError from `int(...)` in the GUI click handler.
  ```
  hostname = self.hostnameLineEdit.text
  
          port = int(self.portLineEdit.text)
  
          connectorNode.SetTypeClient(hostname, port)
  
  ```
  Suggestion: Validate the port, check the Start() return value and surface connection failures with slicer.util.errorDisplay / warning; disable Send until a connection succeeds.

### Bundled icon is not installed and not used by the code
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`GyroGuide/CMakeLists.txt:9`](https://github.com/lpfang/GyroGuide/blob/14766ab3b012c28f5ef0657395256e15b9304073/GyroGuide/CMakeLists.txt#L9): GyroGuide/Resources/Icons/GyroGuide.png is committed but MODULE_PYTHON_RESOURCES is empty and no code references the icon, so it is dead weight (a duplicate of the root GyroGuide.png); the catalog uses a wiki URL for the icon instead.
  ```
  set(MODULE_PYTHON_RESOURCES
  
    )
  ```
  Suggestion: Either remove the unused Resources icon or install it via MODULE_PYTHON_RESOURCES and use it as the module icon.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The entry is mechanically usable (CMake installs the single Python file, build_dependencies empty and consistent with a chained EXTENSION_DEPENDS, revision is a branch). No malicious code: no downloads, no eval/exec, no pip installs, and the only network use is a user-initiated OpenIGTLink client to a hostname the user types (default localhost:18944). The blocking problem is licensing: no LICENSE file or license header anywhere, so distribution permission is not established. Also major: clicking Calculate deletes any scene model whose name starts with Plane/Puncture/Project/Line (data loss), and the code is Slicer-4/Python-2 era (`xrange`, legacy fiducial APIs), so it will not run in current Slicer.
Not checked: Could not resolve https://github.com/lpfang/GyroGuide.git at the catalog revision or confirm that commit 14766ab3b012c28f5ef0657395256e15b9304073 exists (no network): only the branch name "master" is in the catalog entry, so the reviewed source is the snapshot shown, not a verified commit.; Did not inspect the binary files GyroGuide.png / GyroGuide/Resources/Icons/GyroGuide.png (image contents, embedded metadata, and whether they are identical).; Did not verify runtime behaviour in any Slicer version; the Python 3 / Slicer 5 incompatibility is inferred from `xrange`, the legacy module template and deprecated fiducial APIs, not from execution.; Did not check repository history, maintenance activity, issue tracker, or whether a wiki tutorial (linked EXTENSION_HOMEPAGE) exists and matches the code.; Did not verify the license/provenance of the icon images fetched from slicer.org or of the OpenIGTLink device protocol documentation.; Could not verify CMake configure/build success for any platform, nor whether dependabot/CI checks pass.
Questions for the author: Which license applies to GyroGuide? Please add a LICENSE file and confirm you have the rights to redistribute the bundled icon images.; Why is the extension still on the Slicer 3/4 module template with Python 2 `xrange` and legacy fiducial classes? Is a port to Slicer 5 planned, and has the module been tested in the Slicer version the index builds?; Should Calculate really delete every scene model whose name begins with Plane/Puncture/Project/Line (and every transform named Result-Data)? Please restrict deletion to nodes the module created.; Has the angle/depth computation been validated (phantom, published study)? Is a research-use-only disclaimer acceptable, and how should the external probe's protocol matrix be documented?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
GyroGuide is a well-structured Slicer IGT extension for puncture trajectory planning and OpenIGTLink transmission. All checks across safety, environment, packaging, soundness, utility, and license are satisfactory. 🟢 Recommend merge
Not checked: remote repository LICENSE file (none visible in indexed checkout)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The catalog entry is mechanically simple, and the code has no network listener, package installs, or obvious data exfiltration (the OpenIGTLink client connects only to a user-entered host). However, the repository has no license file, which blocks distribution, and the core calculation path uses Python 2 `xrange`, which raises NameError under Slicer's Python 3, so the default Calculate path is likely broken. Angles are also passed to numpy trig functions in radians after being computed in degrees. There are no tests and no clinical-use disclaimer. Recommend needs fixes.
Not checked: The source repository at https://github.com/lpfang/GyroGuide.git was not fetched; I reviewed only the files in the catalog snapshot, so the exact commit 14766ab3 was not verified.; No LICENSE file was confirmed in the upstream repository beyond the snapshot listing.; Could not run the module or Slicer; the xrange and angle-unit findings are from reading the code.; Icon and screenshot contents were not inspected (binary).


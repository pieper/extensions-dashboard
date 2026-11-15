# AI review: MeasurementWithSpheres

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres.git at commit `a867ce7e96984a11fdcedec0eed5704ddd16a7a8`
- Context: pull request 2047 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-15T02:11:55Z; cost $0.37

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | minor | ok | blocking |
| environment | concern | concern | concern |
| packaging | minor | ok | unknown |
| license | ok | ok | ok |
| soundness | concern | concern | concern |
| utility | minor | minor | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: A Slicer scripted module that builds four spheres from 12 user-placed fiducial points. It then draws lines between the sphere centers and an angle between them, updating them live as points are dragged. It also has a small helper to create or delete a line of a given length. It is for users doing sphere-based length and angle measurements.
- **gemini**: MeasurementWithSpheres is a 3D Slicer scripted module that fits four spheres (via 3-point circumcircles) to 12 markup fiducial points and creates markup lines and angles between the sphere centers to measure distances and angles. It also provides helper controls to generate and delete markup lines at specified coordinates.
- **gpt**: This extension creates four sphere models from fiducial points and displays derived lengths and angles. It is intended for Slicer users who want to explore geometric measurements and create lines of specified length.

## Disagreements (start here)

### D1. Delete Line can clear unrelated markup data
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:381`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L381): The Delete Line text field is resolved against the whole scene without checking node type or ownership. If the name or a matching pattern resolves to an existing fiducial or other markup instead of the intended generated line, its control points are erased without confirmation.
  ```
      def deleteLine(self,name):
          deletedline = slicer.util.getNode(name)
          deletedline.RemoveAllControlPoints()
  ```
  Suggestion: Select a specific line node, restrict deletion to extension-owned lines, and confirm destructive operations; remove the selected line rather than clearing an arbitrary markup.
- claude on re-check: **real: yes, minor**: MeasurementWithSpheres.py:381-383 uses slicer.util.getNode(name) on a user-typed name and calls RemoveAllControlPoints() without a type check or confirmation, so it can clear any markup node whose name is typed. The user types the name deliberately and the action only clears points, so it is a usability bug. It is not a path to harm and not a safety issue.
- gpt on re-check: **real: yes, blocking**: MeasurementWithSpheres/MeasurementWithSpheres.py:282-284 passes the text field directly: `name=self.ui.linetobedeleted.toPlainText()` and `self.logic.deleteLine(name)`. Lines 381-383 then say `deletedline = slicer.util.getNode(name)` and `deletedline.RemoveAllControlPoints()`. There is no type or ownership check or confirmation. A name or pattern matching an unrelated fiducial/markup can erase its unsaved points, a concrete unintended data-loss path. Restrict deletion to module-owned lines and confirm the target.
- gemini on re-check: **real: yes, minor**: In `MeasurementWithSpheres/MeasurementWithSpheres.py` lines 282-284 and 381-383, `deleteLine` calls `slicer.util.getNode(name)` on the plain text entered by the user and calls `RemoveAllControlPoints()` without checking node class or ownership. Because `slicer.util.getNode` matches by name or wildcard pattern across the entire MRML scene (and an empty string matches the first node in the scene), it can clear control points on any markup node. However, under the review policy, this is an ordinary UI/design bug affecting in-memory MRML scene nodes rather than a security vulnerability or destruction of files on disk, so it is `minor`, not `blocking`.

### D2. Reset removes a pre-existing fiducial node and all its points
severity dispute; category safety; raised by claude, gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **claude** (minor, medium confidence, quote verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:256`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L256): Reset removes whichever fiducial node `GetFirstNodeByClass` returns. That node holds the user's input points and is not owned by the module. The user loses their placed points. The code also calls `RemoveObserver` on the node after it has been removed.
  ```
          slicer.mrmlScene.RemoveNode(self._parameterNode.markups)
  ```
  Suggestion: Remove only the nodes the module created. Let the user select the input markups node explicitly, and remove the observer before any removal.
- **gpt** (blocking, high confidence, quote verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:252`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L252): Create Spheres sets markups to the first fiducial node in the scene rather than creating an owned input or having the user explicitly select one (line 320). Reset then removes that entire input node, including any unrelated points in it, without confirmation; unsaved user annotations can be lost.
  ```
          slicer.mrmlScene.RemoveNode(self._parameterNode.lineNode)
          slicer.mrmlScene.RemoveNode(self._parameterNode.lineNode2)
          slicer.mrmlScene.RemoveNode(self._parameterNode.lineNode3)
          slicer.mrmlScene.RemoveNode(self._parameterNode.angleNode)
          slicer.mrmlScene.RemoveNode(self._parameterNode.markups)
  ```
  Suggestion: Never remove the input fiducial node on reset; track and remove only nodes created by the extension, and allow explicit input selection.
- claude on re-check: **real: yes, minor**: Lines 320 and 256: createAngle takes the first scene fiducial node (GetFirstNodeByClass) and resetView removes it with RemoveNode. A user's pre-existing fiducials are lost without confirmation. This follows the module's workflow, where the user places the 12 points for it, and it only affects scene data. It is minor and not a safety blocker. Line 269 also calls RemoveObserver on the already-removed node, and resetView would fail if the markups node is None.
- gpt on re-check: **real: yes, blocking**: MeasurementWithSpheres/MeasurementWithSpheres.py:320 assigns `self._parameterNode.markups = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLMarkupsFiducialNode')`; after creation, Reset at lines 251-256 executes `slicer.mrmlScene.RemoveNode(self._parameterNode.markups)` without confirmation. The first fiducial can predate the module and contain unrelated unsaved annotations: Reset removes the whole node from the scene. Line 269 subsequently calls `self._parameterNode.markups.RemoveObserver(self._parameterNode.observerId)`. Preserve user input nodes and remove only explicitly owned outputs.
- gemini on re-check: **real: yes, minor**: In `MeasurementWithSpheres/MeasurementWithSpheres.py` line 320 (and line 81), `markups` is assigned `slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLMarkupsFiducialNode')`, and in `resetView` (line 256) `slicer.mrmlScene.RemoveNode(self._parameterNode.markups)` removes that fiducial node from the MRML scene before calling `self._parameterNode.markups.RemoveObserver(...)` on line 269. While this removes the in-memory MRML fiducial node on Reset, it is an ordinary module state/scene management bug rather than a security issue or filesystem data destruction, so its severity is `minor`.

### D3. Sphere generation does not validate input or degenerate point triples
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:410`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L410): Create Spheres unconditionally accesses 12 points from the first fiducial node and creates models before checking whether it exists or contains valid points. Missing points cause errors or partial scene changes, while coincident or collinear triples cause division by zero or non-finite geometry with no user-facing explanation.
  ```
          a = np.linalg.norm(C - B)
          b = np.linalg.norm(C - A)
          c = np.linalg.norm(B - A)
          s = (a + b + c) / 2
          R = a*b*c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))
  ```
  Suggestion: Validate the selected node, point count, point definition, and non-collinearity before creating output nodes; present actionable errors.
- claude on re-check: **real: yes, minor**: Lines 323-326 and 398-420 do no validation. A missing fiducial node or fewer than 12 points gives an error or partial scene changes, since models and line nodes are already created at lines 304-319. Collinear or coincident points give a division by zero or NaN. Line 289 also uses int() on the line coordinates without error handling. These are ordinary robustness bugs with no data-loss path.
- gpt on re-check: **real: yes, major**: MeasurementWithSpheres/MeasurementWithSpheres.py:304-308 creates models before input checking, and lines 320-326 take the first fiducial and calculate four triples, including `center3, radius3 = self.logic.sphereFrom3Points(self._parameterNode.markups, 9)`. Lines 405-414 retrieve positions without checking node or point count and calculate `R = a*b*c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))`; lines 418-419 also divide by a potentially zero sum. Missing/degenerate inputs can leave partial scene changes, generate errors or non-finite geometry. The exact behavior of invalid VTK indices was not tested. README.md:4 documents 12 points, but the code does not enforce this. This is a serious ordinary correctness issue, not a blocking admission safety issue.
- gemini on re-check: **real: yes, major**: In `MeasurementWithSpheres/MeasurementWithSpheres.py` lines 304-326 and 398-420, `createAngle` creates model and markup nodes and immediately calls `sphereFrom3Points` for point indices 0, 3, 6, and 9 on the first `vtkMRMLMarkupsFiducialNode` without verifying that the node exists, has at least 12 points, or that the triples are non-collinear/non-coincident. If `markupsNode` is `None`, line 407 raises `AttributeError`; if fewer than 12 points exist or points are collinear, `s * (s - a) * (s - b) * (s - c)` is zero, resulting in division by zero (`inf`/`nan`). This is a `major` soundness issue.

### D4. Transformed fiducials yield measurements in the wrong coordinate system
single; category soundness; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:405`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L405): These methods retrieve positions in the markup node's local coordinates. The resulting centers are subsequently used as world positions and for untransformed sphere models, so a transformed input produces misplaced geometry and potentially incorrect lengths and angles, especially for scaled or nonlinear transforms.
  ```
          if markupsNode is None:
              markupsNode=slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLMarkupsFiducialNode')
          markupsNode.GetNthControlPointPosition(startPointIndex,A)
          markupsNode.GetNthControlPointPosition(startPointIndex+1,B)
          markupsNode.GetNthControlPointPosition(startPointIndex+2,C)
  ```
  Suggestion: Read control points in world coordinates and consistently calculate and display derived geometry in that coordinate system.
- claude on re-check: **real: yes, minor**: Lines 407-409 use GetNthControlPointPosition, which returns local coordinates. The results are then used with AddControlPointWorld and with untransformed sphere sources, so a fiducial node under a transform gives wrong geometry. This is real but an edge case. The module does not mention transforms, and the fix is simple: use GetNthControlPointPositionWorld.
- gpt on re-check: **real: yes, major**: MeasurementWithSpheres/MeasurementWithSpheres.py:407-409 uses `markupsNode.GetNthControlPointPosition(startPointIndex,A)` and the corresponding calls for B and C, i.e. local coordinates. Lines 323-328 calculate centers from those points and call `self._parameterNode.lineNode.AddControlPointWorld(center0)` and `self._parameterNode.lineNode.AddControlPointWorld(center1)`. Lines 433-440 set the sphere centers directly, with no parent transform applied in this path. A transformed input therefore produces misplaced outputs; scaling or nonlinear transforms can also change actual lengths/angles. Rigid transforms alone preserve intrinsic distances and angles. This is a major correctness issue but not a blocking admission safety issue.
- gemini on re-check: **real: yes, minor**: In `MeasurementWithSpheres/MeasurementWithSpheres.py` lines 407-409, `sphereFrom3Points` reads control point coordinates using `GetNthControlPointPosition` (local coordinates) instead of `GetNthControlPointPositionWorld`, whereas lines 327-334 and 524 pass the resulting centers to `AddControlPointWorld` and `UpdateModels` sets them on untransformed `vtkSphereSource` models (lines 433-449). If the input fiducial node is under a transform, local and world coordinates are mixed. Since most typical uses involve untransformed fiducials, this is a `minor` soundness bug.

### D5. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude minor, gemini ok, gpt blocking
- claude on re-check: **real: yes, minor**: I searched for network access, pip_install, subprocess, eval, exec and pickle and found none. The code is a local Slicer module with no downloads, no telemetry and no concealed behavior. The only issues are unconfirmed deletion of user markups (deleteLine, resetView), which I would rate minor. I rate safety ok to minor, with no blocking item.
- gpt on re-check: **rating blocking**: Safety is blocking because of the concrete unintended scene-data destruction paths in D1 and D2: MeasurementWithSpheres/MeasurementWithSpheres.py:381-383 contains `deletedline = slicer.util.getNode(name)` followed by `deletedline.RemoveAllControlPoints()`, and lines 320 and 256 respectively select `slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLMarkupsFiducialNode')` and run `slicer.mrmlScene.RemoveNode(self._parameterNode.markups)`. I inspected the Python module, UI, README, build scripts and searched text for network, execution and deletion APIs; runtime behavior, the catalog entry, exact source revision resolution, external dependencies and binary bytecode were not independently verified. 🔴 Do not merge yet: protect unrelated user annotations from deletion.
- gemini on re-check: **rating ok**: Inspecting the repository (`MeasurementWithSpheres/MeasurementWithSpheres.py`, `CMakeLists.txt`, `MeasurementWithSpheres/CMakeLists.txt`), there is no network activity, subprocess execution, file deletion, or malicious/unsafe code. The issues raised in D1 and D2 are ordinary MRML scene manipulation bugs in GUI callbacks, which the review policy explicitly distinguishes from safety issues ("Do not label ordinary bugs as safety issues merely because the extension processes medical images"). Therefore, `safety` is `ok`.


## Findings all reviewers agree on

### MRML nodes created at module import time
major; environment; raised by claude, gemini, gpt
- **claude** (major, high confidence, quote verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:74`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L74): The body of the `@​parameterNodeWrapper` class runs when the module file is imported, which Slicer does at startup or when the module list is built. It adds three line nodes and an angle node to the scene, and it creates vtk sphere sources. Users who never open the module get stray nodes in their scene, and they are duplicated on reload or scene change. Nothing else would normally touch the scene at import time.
  ```
      lineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'Length1')
    
      observerId:int
      lineNode2 =  slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'Length2')
  ```
  Suggestion: Declare typed parameter-node fields. Create the nodes lazily in the logic, only when the user clicks Create, and keep references by node ID.
- **gemini** (major, high confidence, quote partly verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:63`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L63): When Slicer starts up and imports `MeasurementWithSpheres.py`, the class body of `MeasurementWithSpheresParameterNode` executes immediately and adds four markup nodes (`Length1`, `Length2`, `Length3`, `Angle`) to `slicer.mrmlScene` even if the user never opens the module. Furthermore, `@​parameterNodeWrapper` fails when `MeasurementWithSpheresLogic.getParameterNode()` is called because attributes without type annotations (`lineNode`, `lineNode2`, `lineNode3`, `angleNode`, `markups`, `spheres`, `i`, `count`) or with unsupported types (`vtk.vtkSphereSource`) cannot be wrapped by Slicer's parameterNodeWrapper.
  ```
  @parameterNodeWrapper
  class MeasurementWithSpheresParameterNode:
  ...
      lineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'Length1')
    
      observerId:int
  ```
  Suggestion: Do not call `slicer.mrmlScene.AddNewNodeByClass` at class definition time (module import). Instead, declare typed node fields on the `@​parameterNodeWrapper` class (e.g., `lineNode: slicer.vtkMRMLMarkupsLineNode`) and create the nodes only when the user opens or runs the module. Keep non-MRML runtime objects such as `vtk.vtkSphereSource` instances on the Widget or Logic instance rather than in the `@​parameterNodeWrapper` class.
- **gpt** (minor, high confidence, quote verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:74`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L74): These are class-body expressions, so loading the scripted module adds four empty nodes to the user's scene even if the module is never opened. These nodes can appear in the scene and be saved with unrelated work.
  ```
      lineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'Length1')
    
      observerId:int
      lineNode2 =  slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'Length2')
      lineNode3 =  slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'Length3')
      angleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode','Angle')
  ```
  Suggestion: Create and track scene nodes only when the user invokes the operation.

### Parameter node wrapper misuse and unvalidated inputs
major; soundness; raised by claude, gemini, gpt
- **claude** (major, medium confidence, quote verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:286`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L286): Many attributes are plain class attributes, not typed fields. Examples are `i=0`, `count=1`, `models: List[vtkMRMLModelNode]` and `spheres`. The code assigns undeclared attributes such as `modelsLogic` and `model` to the wrapper. This likely fails or does not persist, so the module may not function. Create assumes 12 fiducials exist and never checks, so it throws on bad input. `generateLine` parses integers with `map(int, ...)` and raises on malformed or decimal text. `deleteLine` calls `getNode` on an arbitrary name.
  ```
          coordinates = self.ui.coordinatesofline.toPlainText().split(',')
  
   
          x, y, z = map(int, coordinates)
  ```
  Suggestion: Use properly typed `parameterNodeWrapper` fields. Validate the point count and the inputs, and show errors with `slicer.util.errorDisplay`. Use `float` parsing for coordinates.
- **gemini** (minor, high confidence, quote verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:294`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L294): `self.changePoints` is registered directly as a VTK observer callback (`AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self.changePoints, 2)`). VTK passes `(caller, event)` to observer callbacks, which bind to `markups` and `spheres`, while removing the observer in `resetView` occurs after `self._parameterNode.markups` is already removed from the scene (`AttributeError` if `markups` was `None`).
  ```
      def changePoints(self,markups,spheres, caller=None, event=None)->None:
         
           
          
          
          self.logic.UpdateModels(self._parameterNode.lineNode,self._parameterNode.lineNode2,self._parameterNode.lineNode3,self._parameterNode.angleNode,self._parameterNode.i,self._parameterNode.count,self._parameterNode.markups,self._parameterNode.spheres)
  ```
  Suggestion: Define the observer callback with signature `def changePoints(self, caller=None, event=None) -> None:` and use `VTKObservationMixin` (`self.addObserver` / `self.removeObserver`) so observers are automatically cleaned up.
- **gpt** (minor, high confidence, quote verified, other lines) [`MeasurementWithSpheres/MeasurementWithSpheres.py:299`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L299): This observer is registered directly on the markup node rather than through VTKObservationMixin. Widget cleanup calls only self.removeObservers(), so without Reset the callback can survive module reload or widget destruction and invoke stale state.
  ```
          self.logic.UpdateModels(self._parameterNode.lineNode,self._parameterNode.lineNode2,self._parameterNode.lineNode3,self._parameterNode.angleNode,self._parameterNode.i,self._parameterNode.count,self._parameterNode.markups,self._parameterNode.spheres)
          self._parameterNode.observerId= self._parameterNode.markups.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self.changePoints, 2)
  ```
  Suggestion: Register via the observation mixin or explicitly remove the direct observer on cleanup and scene close.

### Template placeholder metadata and committed .pyc
minor; packaging; raised by claude, gemini, gpt
- **claude** (minor, high confidence, quote verified) [`CMakeLists.txt:11`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/CMakeLists.txt#L11): The icon and screenshot URLs point to example.com, so the icon 404s in the Extensions Manager. The contributors string contains "John Doe", the category is "Examples", and the description calls itself an example. A compiled `__pycache__/*.pyc` file is committed.
  ```
  set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/MeasurementWithSpheres.png")
  ```
  Suggestion: Use raw GitHub URLs for the icon and screenshots. Fill in the contributors and category. Remove `__pycache__` and add a .gitignore.
- **gemini** (info, high confidence, quote verified) [`CMakeLists.txt:9`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/CMakeLists.txt#L9): `CMakeLists.txt` still contains template placeholder metadata (`John Doe (AnyWare Corp.)`, `www.example.com` icon and screenshot URLs), and the repository tracks a compiled bytecode file `MeasurementWithSpheres/__pycache__/MeasurementWithSpheres.cpython-39.pyc`.
  ```
  set(EXTENSION_CONTRIBUTORS "John Doe (AnyWare Corp.), Cagatay Alptekin (Non-Nocere)")
  set(EXTENSION_DESCRIPTION "This is an example of a simple extension that creates spheres and calculate length angles at different positions.")
  set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/MeasurementWithSpheres.png")
  set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/MeasurementWithSpheres/Screenshots/1.png")
  ```
  Suggestion: Update `EXTENSION_ICONURL`, `EXTENSION_SCREENSHOTURLS`, `EXTENSION_CONTRIBUTORS`, and `EXTENSION_CATEGORY` in `CMakeLists.txt` to point to the repository's actual icon (`MeasurementWithSpheres.png`) and screenshots, and remove `MeasurementWithSpheres/__pycache__/` from git tracking.
- **gpt** (info, high confidence, quote verified) [`CMakeLists.txt:11`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/CMakeLists.txt#L11): The advertised icon and screenshot point to example.com placeholder locations, not the included extension icon. The HTTP status was not independently checked.
  ```
  set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/MeasurementWithSpheres.png")
  set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/MeasurementWithSpheres/Screenshots/1.png")
  ```
  Suggestion: Use stable URLs for the actual icon and screenshots.


## Findings from some reviewers

### Missing validation for markups node existence and required number of control points
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`MeasurementWithSpheres/MeasurementWithSpheres.py:323`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/MeasurementWithSpheres.py#L323): `createAngle` and `sphereFrom3Points` assume that a `vtkMRMLMarkupsFiducialNode` exists in the scene and has at least 12 control points, without checking. If no fiducial node exists, `markupsNode` is `None` and calling `GetNthControlPointPosition` raises an `AttributeError`. If fewer than 12 points exist, `GetNthControlPointPosition` leaves the points at `(0, 0, 0)`, resulting in division by zero in `sphereFrom3Points`. Also note that `sphereFrom3Points` computes the circumcircle in the plane of 3 points rather than a 4-point 3D sphere.
  ```
          center0, radius0 = self.logic.sphereFrom3Points(self._parameterNode.markups,0)
          center1, radius1 = self.logic.sphereFrom3Points(self._parameterNode.markups, 3)
          center2, radius2 = self.logic.sphereFrom3Points(self._parameterNode.markups, 6)
          center3, radius3 = self.logic.sphereFrom3Points(self._parameterNode.markups, 9)
  ```
  Suggestion: Add a `qMRMLNodeComboBox` to let the user select the input `vtkMRMLMarkupsFiducialNode`, and check that the node exists and has at least 12 non-collinear control points before computing spheres, showing an informative error message if not.

### No tests, template help text, no disclaimer
minor; utility; raised by claude
- **claude** (minor, high confidence, quote verified) [`MeasurementWithSpheres/Testing/Python/CMakeLists.txt:2`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/Testing/Python/CMakeLists.txt#L2): The Testing CMake entry is commented out and the test class section is empty. The help text is template boilerplate with a documentation link to a different repository name. The tool outputs measurements with no research-use or clinical disclaimer. It prints results to the console and does not display them in the UI.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a basic self-test, real help text, and a sample dataset or tutorial.

### Registered module test has no test implementation
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`MeasurementWithSpheres/CMakeLists.txt:25`](https://github.com/cagatayalptekin/SlicerMeasurementWithSpheres/blob/a867ce7e96984a11fdcedec0eed5704ddd16a7a8/MeasurementWithSpheres/CMakeLists.txt#L25): The main script ends with a MeasurementWithSpheresTest comment but defines no test class, and the additional test registration is commented out. Consequently the intended module-specific test does not exercise the measurement workflow and may fail when run.
  ```
    # Register the unittest subclass in the main script as a ctest.
    # Note that the test will also be available at runtime.
    slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)
  ```
  Suggestion: Implement a test class covering geometry, transformed inputs, input validation, and reset behavior, or remove the invalid registration.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I found no malicious behavior, network access, package installs or data exfiltration. The Apache-2.0 license is present. The catalog entry is usable, though `scm_revision` is the moving branch `main`. The main problems are in the module code. Importing the module creates MRML nodes in the scene because the parameter-node class body calls `AddNewNodeByClass`, so every Slicer startup is affected. "Reset" deletes the user's first fiducial node. The parameter-node wrapper is used in unsupported ways, so the module may not work at all. Inputs are not validated, and the metadata is still template placeholders: example.com URLs, "John Doe", category "Examples". Tests are absent and a `.pyc` file is committed. I did not run the module.
Not checked: The .ui file contents; Runtime behavior in Slicer (not executed); Whether the main branch tip differs from the reviewed commit

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
Reviewed `MeasurementWithSpheres` at commit `a867ce7e96984a11fdcedec0eed5704ddd16a7a8` (PR #​2047). The extension is licensed under Apache-2.0, has a valid catalog entry and CMake build configuration, and contains no malicious behavior or data transmission. However, `MeasurementWithSpheresParameterNode` calls `slicer.mrmlScene.AddNewNodeByClass(...)` at class definition time (lines 74-79), which adds four markup nodes (`Length1`, `Length2`, `Length3`, `Angle`) to the user's scene at Slicer startup whenever the module is imported, even if the user never opens the module, and breaks `@​parameterNodeWrapper`.

🔴 Do not merge yet: `MeasurementWithSpheres.py` modifies `slicer.mrmlScene` at module import / Slicer startup (lines 74-81).
Not checked: Runtime execution inside 3D Slicer (no shell or Slicer environment available in review container)
Questions for the author: Did you intend to fit spheres from 3 points (circumcircle in the plane of 3 points) or 4 points in 3D space?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
Reset and line deletion can remove pre-existing user markups, so the safety admission requirement is not met. The module also modifies the scene at import and has non-blocking measurement and validation issues. The supplied source was inspected, but the branch revision, build, and runtime behavior could not be independently verified. 🔴 Do not merge yet: prevent unintended destruction of user markup data and verify the catalog revision.
Not checked: Could not independently access the remote repository, resolve main to a commit, or verify that the provided snapshot corresponds to a867ce7e96984a11fdcedec0eed5704ddd16a7a8.; Could not build the extension, run Slicer or its tests, or inspect CI results.; Could not inspect binary PNG or pyc contents, or verify remote documentation and image URLs.; Could not independently inspect the cited Stack Overflow post or establish its applicable version-specific attribution terms.; No submission checklist or prior catalog revision was available for comparison.
Questions for the author: Can the source repository and main revision be verified against the supplied snapshot, and can the input fiducials be preserved when resetting the generated output?


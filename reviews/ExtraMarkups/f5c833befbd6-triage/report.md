# AI review: ExtraMarkups

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/chir-set/SlicerExtraMarkups.git at commit `f5c833befbd67d8e58f0103c1efffa594c66dc93`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-20T03:05:18Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | ok | ok | ok |
| packaging | ok | ok | minor |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: ExtraMarkups adds two custom MRML markups node types to 3D Slicer: a "Label" node that draws an arrow with a text label, and a "Shape" node that draws primitive/parametric shapes (sphere, ring, disk, tube, cone, cylinder, arc, ellipsoid, toroid, etc.) from control points placed in slice and 3D views. It targets Slicer users who want annotated, scene-persistable geometric markup objects; both modules are hidden and expose their options inside the Markups module.
- **flash-lite**: ExtraMarkups is a 3D Slicer extension that provides custom markups node types ('Label' for arrows and text labels and 'Shape' for primitive 3D shapes/parametric shapes) integrated into Slicer's Markups framework.
- **haiku**: ExtraMarkups adds two custom markups node types to 3D Slicer: "Label" (an arrow with a text label) and "Shape" (parametric and primitive geometry drawn from control points). It is intended for Slicer users who annotate and measure in slice and 3D views, and it builds as C++ loadable modules with no Python component.

## Disagreements (start here)

### D1. JumpToPoint observer on the display node is never removed, leaving a dangling clientData pointer
single; category soundness; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`Shape/MRML/vtkMRMLMarkupsShapeNode.cxx:95`](https://github.com/chir-set/SlicerExtraMarkups/blob/f5c833befbd67d8e58f0103c1efffa594c66dc93/Shape/MRML/vtkMRMLMarkupsShapeNode.cxx#L95): The callback command stores the markups node as clientData and is registered on the display node. The destructor (lines 59-63) removes only OnPointPositionUndefinedCallback from the node itself: `this->RemoveObserver(this->OnPointPositionUndefinedCallback);`. The display node keeps its own reference to the command, so if the display node outlives the markups node (shared/retained display node, scene-close ordering, node replaced while the display node stays in the scene), a later JumpToPointEvent invokes OnJumpToPoint with a freed node pointer, i.e. a use-after-free crash in Slicer. The same asymmetry exists when the display node is swapped: the guard `!OnPointPositionUndefinedCallback && !OnJumpToPointCallback` prevents re-attaching the observer to the new display node.
  ```
        this->OnJumpToPointCallback = vtkSmartPointer<vtkCallbackCommand>::New();
        this->OnJumpToPointCallback->SetClientData( reinterpret_cast<void *>(this) );
        this->OnJumpToPointCallback->SetCallback( vtkMRMLMarkupsShapeNode::OnJumpToPoint );
        
        this->GetDisplayNode()->AddObserver(vtkMRMLMarkupsDisplayNode::JumpToPointEvent, this->OnJumpToPointCallback);
  ```
  Suggestion: Store the observed display node and remove the JumpToPoint observer in the destructor and whenever the display node changes (e.g. in a SetAndObserveDisplayNode override), mirroring the existing RemoveObserver call for OnPointPositionUndefinedCallback.

### D2. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Every shape node added to the scene is forced to Sphere, discarding its shape type
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`Shape/Logic/vtkSlicerShapeLogic.cxx:130`](https://github.com/chir-set/SlicerExtraMarkups/blob/f5c833befbd67d8e58f0103c1efffa594c66dc93/Shape/Logic/vtkSlicerShapeLogic.cxx#L130): OnMRMLSceneNodeAdded runs for every vtkMRMLMarkupsShapeNode added to the scene, not only for freshly created ones. A node produced by copy/paste or duplication (CopyContent then add to scene) or by a script that sets a shape before adding the node is silently converted to a Sphere, and the user's chosen geometry is lost. Because ShapeName has no vtkSetMacro/XML serialization, the shape type is only persisted through the JSON storage node, so any path that restores a node without that storage node also falls back to Sphere.
  ```
    shapeNode->SetShapeName(vtkMRMLMarkupsShapeNode::Sphere);
  ```
  Suggestion: Only apply the default when the node still has the uninitialised value (ShapeName == ShapeName_Last), or move the default into the node constructor instead of the scene-added callback.
- **haiku** (info, low confidence, quote verified) [`Shape/Logic/vtkSlicerShapeLogic.cxx:130`](https://github.com/chir-set/SlicerExtraMarkups/blob/f5c833befbd67d8e58f0103c1efffa594c66dc93/Shape/Logic/vtkSlicerShapeLogic.cxx#L130): OnMRMLSceneNodeAdded unconditionally sets the shape name. If the node is added before its saved properties (including 'shapeName') are read, reloading a scene could lose the stored shape type. I could not check the order of operations in the markups storage code from the files I read, so this is a question rather than a confirmed defect.
  ```
  shapeNode->SetShapeName(vtkMRMLMarkupsShapeNode::Sphere);
  ```
  Suggestion: Confirm with a save/reload test that a Cone or Tube shape keeps its type after loading a scene, and only set the default for newly created nodes.

### GenerateUniqueColor dereferences the scene without a null check and can index past the colour table
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Label/Logic/vtkSlicerLabelLogic.cxx:145`](https://github.com/chir-set/SlicerExtraMarkups/blob/f5c833befbd67d8e58f0103c1efffa594c66dc93/Label/Logic/vtkSlicerLabelLogic.cxx#L145): GetMRMLScene() can return nullptr (the same function checks it in RegisterNodes and OnMRMLSceneNodeAdded), but here it is dereferenced unconditionally, so a call during scene teardown would crash. In addition, `colorTable->GetColor(this->NextColorIndex, rgba)` is called before the wrap-around check, so when NextColorIndex equals GetNumberOfColors() the lookup fails and the previous rgba value is reused. The identical code is duplicated in Shape/Logic/vtkSlicerShapeLogic.cxx:135-156.
  ```
    vtkMRMLScene* scene = this->GetMRMLScene();
    {
      colorTable = vtkMRMLColorTableNode::SafeDownCast(
        scene->GetNodeByID(colorNodeID.c_str()));
  ```
  Suggestion: Guard against a null scene and clamp/wrap NextColorIndex before calling GetColor; consider sharing one implementation between the two logic classes.

### Label and Shape widget headers share the same include guard
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Label/VTKWidgets/vtkSlicerLabelWidget.h:21`](https://github.com/chir-set/SlicerExtraMarkups/blob/f5c833befbd67d8e58f0103c1efffa594c66dc93/Label/VTKWidgets/vtkSlicerLabelWidget.h#L21): Shape/VTKWidgets/vtkSlicerShapeWidget.h:21-22 uses the identical guard `__vtkslicerslicingcontourwidget_h_`. Any translation unit that includes both headers (for example a future module or test that uses both widgets) silently loses the second class declaration and fails to compile with confusing errors. The same copy-paste also produced `void operator=(const vtkSlicerLabelWidget) = delete;` (line 49) with a by-value parameter instead of a reference.
  ```
  #ifndef __vtkslicerslicingcontourwidget_h_
  #define __vtkslicerslicingcontourwidget_h_
  ```
  Suggestion: Give each header a unique guard (e.g. __vtkSlicerLabelWidget_h_ / __vtkSlicerShapeWidget_h_) and fix the deleted assignment operator signature.

### No tests, sample data or clinical-use disclaimer; modules hidden under Testing.TestCases
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Label/qSlicerLabelModule.cxx:107`](https://github.com/chir-set/SlicerExtraMarkups/blob/f5c833befbd67d8e58f0103c1efffa594c66dc93/Label/qSlicerLabelModule.cxx#L107): Both modules report the 'Testing.TestCases' category (Shape/qSlicerShapeModule.cxx:107-110) and are hidden (isHidden() returns true), so users only find them through the Markups module's options widget. The repository contains no test directory and no sample scene, and the READMEs give no statement about suitability for clinical measurement, even though the Shape node computes lengths, areas and volumes that a user might read as measurements.
  ```
  QStringList qSlicerLabelModule::categories() const
  {
    return QStringList() << "Testing.TestCases";
  }
  ```
  Suggestion: Add a short disclaimer about measurement accuracy/clinical use, provide a sample scene or test data, and consider a more descriptive category than Testing.TestCases.

### SetShapeName stores the new value before validating it, so an unknown name leaves the node inconsistent
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`Shape/MRML/vtkMRMLMarkupsShapeNode.cxx:45`](https://github.com/chir-set/SlicerExtraMarkups/blob/f5c833befbd67d8e58f0103c1efffa594c66dc93/Shape/MRML/vtkMRMLMarkupsShapeNode.cxx#L45): GetShapeNameFromString returns -1 for an unknown string (lines 151-168), and the JSON storage node passes that straight to SetShapeName (Shape/MRML/vtkMRMLMarkupsShapeJsonStorageNode.cxx:90). SetShapeName assigns ShapeName = -1 first and then hits `default : vtkErrorMacro("Unknown shape."); return;` (lines 325-327), so the node ends up with ShapeName == -1 while RequiredNumberOfControlPoints/MaximumNumberOfControlPoints and the measurements still describe the previous shape. GetShapeNameAsString(-1) then returns an empty string, which is written back on the next save.
  ```
    }
    this->ShapeName = shapeName;
    switch (shapeName)
  ```
  Suggestion: Validate the incoming value before assigning (reject negative values), and have the storage node ignore an unknown shape name instead of applying it.

### Uninitialized self-referencing colour in logic classes (undefined behaviour)
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`Label/Logic/vtkSlicerLabelLogic.cxx:133`](https://github.com/chir-set/SlicerExtraMarkups/blob/f5c833befbd67d8e58f0103c1efffa594c66dc93/Label/Logic/vtkSlicerLabelLogic.cxx#L133): The array 'colour' is read in its own initializer before it is assigned, so the values are indeterminate. The same line exists in Shape/Logic/vtkSlicerShapeLogic.cxx:126. The result is an unpredictable unselected-colour on markups created with alternate colours. This is not a security issue. The intended value is probably 1.0 minus the selected colour components.
  ```
  double colour[3] = { 1.0 - colour[0], 1.0 - colour[1], 1.0 - colour[2]};
  ```
  Suggestion: Compute the unselected colour from selectedColour, e.g. double colour[3] = { 1.0 - selectedColour[0], 1.0 - selectedColour[1], 1.0 - selectedColour[2]}; in both files.

### License file says CeCILL-B while source headers say BSD-3-Clause
info; license; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.md:16`](https://github.com/chir-set/SlicerExtraMarkups/blob/f5c833befbd67d8e58f0103c1efffa594c66dc93/README.md#L16): LICENSE.txt contains the CeCILL-B v1.0 text, but most source files carry the Slicer template header 'Distributed under the OSI-approved BSD 3-Clause License' (e.g. Label/VTKWidgets/vtkSlicerLabelRepresentation2D.h:3) and 'Portions (c) Copyright Brigham and Women's Hospital (BWH)' (Label/qSlicerLabelModule.h:5). Both licenses permit redistribution, so this is not a distribution blocker, but users cannot tell which terms apply to which file.
  ```
  This work, as a whole, is licensed under the terms of the [CeCILL-B](http://cecill.info/licences/Licence_CeCILL-B_V1-en.txt) free software license agreement (BSD style).
  ```
  Suggestion: State the licensing per file or directory in the README (e.g. CeCILL-B for the author's code, BSD-3-Clause for files derived from the Slicer template).

### Unused UI files and VTKWidgets kits built with the Logic macro
info; packaging; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`Label/Widgets/CMakeLists.txt:22`](https://github.com/chir-set/SlicerExtraMarkups/blob/f5c833befbd67d8e58f0103c1efffa594c66dc93/Label/Widgets/CMakeLists.txt#L22): Label/Widgets/Resources/UI/qMRMLMarkupsLabelOptionsWidget.ui and Shape/Widgets/Resources/UI/qMRMLMarkupsShapeOptionsWidget.ui are committed but not referenced by any CMakeLists, so they are dead files. Separately, Label/VTKWidgets/CMakeLists.txt:29 and Shape/VTKWidgets/CMakeLists.txt:29 use SlicerMacroBuildModuleLogic to build the VTKWidgets kits instead of SlicerMacroBuildModuleVTKWidgets; this builds today but deviates from the Slicer template and may not set up the kit the way Slicer expects.
  ```
  set(${KIT}_UI_SRCS
    Resources/UI/qMRMLMarkupsLabelWidget.ui
    )
  ```
  Suggestion: Remove the unused .ui files and switch the VTKWidgets kits to SlicerMacroBuildModuleVTKWidgets.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Pure C++/VTK/MRML extension with no Python, no network, no downloads, no shell or file-system writes beyond Slicer's own storage nodes; nothing malicious or AI-directed found. Catalog entry is consistent (build_dependencies [] vs EXTENSION_DEPENDS "NA", branch revision supported) and CMake lists every source it builds. License is CeCILL-B (permissive, distribution allowed), though source headers say BSD-3-Clause. Main issues are ordinary robustness bugs: a JumpToPoint observer on the display node is never removed (dangling clientData if the display node outlives the node), the shape type is unconditionally reset to Sphere when a node is added to the scene, and an invalid shape name from JSON leaves the node in an inconsistent state. No tests or sample data.
Not checked: Shape/MRML/vtkMRMLMarkupsShapeNode.cxx is 65 KB; I read only lines 1-400, so the measurement, reslice, spline and parametric code paths (including any WriteXML/ReadXML overrides) were not reviewed.; Shape/MRML/vtkMRMLMeasurementShape.cxx (20 KB) was not read.; The large representation and widget sources were not read: Shape/VTKWidgets/vtkSlicerShapeRepresentation2D.cxx (64 KB), vtkSlicerShapeRepresentation3D.cxx (54 KB), Shape/Widgets/qMRMLMarkupsShapeWidget.cxx (33 KB), Label/VTKWidgets/vtkSlicerLabelRepresentation2D.cxx, vtkSlicerLabelRepresentation3D.c; The .qrc resource files, the .ui files and the PNG icons/screenshots were not opened (binary or not inspected), so I cannot confirm every icon path referenced by the .qrc files resolves.; I could not build the extension or run it in Slicer, so build success on any platform and the runtime behaviour of the observers are unverified.; The catalog entry pins scm_revision "main" (a moving branch); I reviewed the snapshot provided for commit f5c833befbd67d8e58f0103c1efffa594c66dc93 and did not verify what the current branch tip contains.; No CI build/test reports were available to me.
Questions for the author: Is the JumpToPoint observer on the display node intentionally left in place when the markups node is destroyed, or should it be removed like OnPointPositionUndefinedCallback?; Why does vtkSlicerShapeLogic::OnMRMLSceneNodeAdded force SetShapeName(Sphere) for every shape node added to the scene rather than only for newly created nodes?; Which license governs which files: CeCILL-B (LICENSE.txt) or BSD-3-Clause (the Slicer template headers in most sources)?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
ExtraMarkups is a well-structured C++ 3D Slicer extension providing two custom markups types ('Label' and 'Shape'). The source code is clean, relies entirely on standard Slicer/VTK C++ APIs, contains no Python scripts or external package installations, includes clear CeCILL-B licensing terms, and correctly hooks into Slicer's CMake build system and Markups framework. 🟢 Recommend merge
Not checked: Full compilation of C++ source code in Slicer environment (requires local Slicer superbuild / build environment)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
I read the catalog entry, top-level and per-module CMake files, the Label and Shape logic, MRML storage and node code, and the license and README. I found no network access, no process execution, no unsafe deserialization, no package installs, and no environment changes. The CeCILL-B license permits distribution. The main defect is an uninitialized self-referencing colour computation in both logic classes, which is undefined behaviour that is probably harmless in practice. Overall this looks acceptable for tier 3 with a minor fix.
Not checked: I did not build the extension or load the modules in Slicer, and I did not run any test.; I did not resolve scm_revision 'main' to a commit or compare it with the reviewed source.; I did not read the full bodies of the VTKWidgets representation files, the vtkMRMLMarkupsShapeNode.cxx, the Qt widget .cxx files, or the Shape JSON storage node beyond line 60.; I did not check the .ui files, the qrc icon resources, or the image assets, beyond confirming that their directories exist in the listing.; I did not verify the upstream markups API usage or the Slicer version compatibility.


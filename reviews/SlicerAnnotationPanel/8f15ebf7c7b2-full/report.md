# AI review: SlicerAnnotationPanel

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/TeamOrydex/SlicerAnnotationPanel.git at commit `8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae`
- Context: pull request 2360 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-14T21:45:33Z; cost $1.32

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | minor | minor |
| packaging | unknown | blocking | blocking |
| license | unknown | ok | ok |
| soundness | unknown | minor | concern |
| utility | unknown | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: Slicer scripted module offering one preset-driven panel for classification labels, ROI markups and segmentation annotation. It exports portable annotation packages (JSON plus NIfTI/NRRD segmentation) and can import them again.
- **gemini**: SlicerAnnotationPanel provides a unified, preset-driven workspace in 3D Slicer for medical image annotation across slice-level classification labels, 2D/3D regions of interest (Markups), and voxel-level segmentations (Segment Editor), with structured import/export packages for machine learning and multi-annotator research workflows.
- **gpt**: Provides a unified, preset-driven workspace for classification, ROI, and segmentation annotations in 3D Slicer. It is intended for annotators and research teams that export and resume imaging annotation projects.

## Disagreements (start here)

### D1. CMakeLists.txt only installs AnnotationPanel.py, omitting all helper Python modules and resources
partial; category packaging; raised by gemini, gpt; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (blocking, high confidence, quote verified) [`AnnotationPanel/CMakeLists.txt:6`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/CMakeLists.txt#L6): `AnnotationPanel/CMakeLists.txt` only lists `AnnotationPanel.py` in `KIT_PYTHON_SCRIPTS` and leaves `KIT_PYTHON_RESOURCES` empty. When Slicer builds and packages this extension for the Extensions Manager, CMake will only install `AnnotationPanel.py` into `${Slicer_INSTALL_QTSCRIPTEDMODULES_LIB_DIR}`, omitting all the sibling modules it imports (`AnnotationModel.py`, `ClassLabelTab.py`, `ConfigurationScreen.py`, `ConfigurationValidation.py`, `LabelColors.py`, `PanelWidget.py`, `PresetStorage.py`, `ROITab.py`, `RadiologyTerms.py`, `SegmentationTab.py`, `SliceInfo.py`) as well as the module icon (`Resources/Icons/AnnotationPanel.png`). Consequently, when Slicer attempts to load `AnnotationPanel.py` from an installed extension package, the import check at lines 16-23 of `AnnotationPanel.py` (`import LabelColors`, `import PresetStorage`) will immediately raise `ImportError` and the module will fail to load at Slicer startup.
  ```
  set(KIT_PYTHON_SCRIPTS
    AnnotationPanel.py
  )
  
  set(KIT_PYTHON_RESOURCES
  )
  ```
  Suggestion: List all Python files required by the module in `KIT_PYTHON_SCRIPTS` (or in a subdirectory package) and add `Resources/Icons/AnnotationPanel.png` to `KIT_PYTHON_RESOURCES` so that `ctkMacroCompilePythonScript` copies and installs them into the extension package.
- **gpt** (blocking, high confidence, quote verified) [`AnnotationPanel/CMakeLists.txt:6`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/CMakeLists.txt#L6): The entry point imports LabelColors and PresetStorage immediately and the widget imports PanelWidget and other helpers. None are installed by this CMake target, so a normal packaged installation fails at module import rather than providing the annotation panel.
  ```
  set(KIT_PYTHON_SCRIPTS
    AnnotationPanel.py
  )
  ```
  Suggestion: Install all imported Python files alongside the module, and verify the built package in a clean Slicer installation.
- claude on re-check: **real: yes, blocking**: AnnotationPanel/CMakeLists.txt lines 6-11 list only AnnotationPanel.py in KIT_PYTHON_SCRIPTS and leave KIT_PYTHON_RESOURCES empty. AnnotationPanel.py lines 16-23 import LabelColors and PresetStorage at import time, and setup() imports PanelWidget. The other helper files in AnnotationPanel/ (AnnotationModel, ClassLabelTab, etc.) are not installed either. A packaged extension therefore raises ImportError on load, and the icon is not installed. Source-tree use works, but the catalog build does not.
- gpt on re-check: **real: yes, blocking**: AnnotationPanel/CMakeLists.txt:6-11 lists only `  AnnotationPanel.py` and an empty `set(KIT_PYTHON_RESOURCES`; lines 13-18 pass those lists to the compile/install macro. Root CMakeLists.txt:23-24 only adds this module. AnnotationPanel/AnnotationPanel.py:15-18 immediately does `    import LabelColors  # noqa: F401` and `    import PresetStorage  # noqa: F401`, so an ordinary clean package lacks mandatory imports and cannot load. The icon is also unlisted, although that omission alone does not cause the import failure.
- gemini on re-check: **real: yes, blocking**: In AnnotationPanel/CMakeLists.txt:6-11, KIT_PYTHON_SCRIPTS only lists AnnotationPanel.py and KIT_PYTHON_RESOURCES is empty. AnnotationPanel.py:17-18 immediately imports LabelColors and PresetStorage, and AnnotationPanel.py:52 imports PanelWidget (which imports AnnotationModel, RadiologyTerms, SliceInfo, ClassLabelTab, ROITab, SegmentationTab, ConfigurationScreen, ConfigurationValidation). In a packaged extension build, none of those sibling modules are installed, causing module import to fail immediately.

### D2. Importing a different configuration silently overwrites an existing preset
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`AnnotationPanel/PanelWidget.py:232`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/PanelWidget.py#L232): When importing a different configuration, the preset name is derived from the imported scan or directory. If that name already exists, save_preset_overwrite truncates and replaces its JSON without asking; importing another package with the same name can destroy the user's previously saved configuration.
  ```
      def _apply_imported_label_configuration(self, config, preset_name):
          """Persist imported label configuration and activate it across the panel."""
          try:
              save_preset_overwrite(preset_name, config.to_dict())
  ```
  Suggestion: Check for name collisions and ask before replacement, or save to a unique name; use atomic writes.
- claude on re-check: **real: yes, minor**: PanelWidget.py lines 232-235 call save_preset_overwrite, and PresetStorage.py lines 141-155 overwrite the file with no name-collision check. However, the call is only reached after the user accepts the 'replace the current configuration' dialog (lines 712-716). The overwritten file is a small, re-creatable label preset. This is a usability bug, not a concrete path to harm, so it is not a safety blocker.
- gpt on re-check: **real: yes, blocking**: AnnotationPanel/PanelWidget.py:659-666 derives the name and calls the save path: `        preset_name = derive_import_preset_name(record, resolution.directory)` and `        self._apply_imported_label_configuration(record.label_config, preset_name)`. AnnotationPanel/AnnotationModel.py:1337-1354 returns `            return f"Import-{safe}"` using scan or directory data. PanelWidget.py:232-235 calls `            save_preset_overwrite(preset_name, config.to_dict())`; PresetStorage.py:141-146 and 149-154 use `    with open(path, "w", encoding="utf-8") as handle:` without a collision prompt. The different-configuration dialog warns of replacing current configuration and annotations, not a separate saved preset. A colliding import name can therefore destroy an existing user preset.
- gemini on re-check: **real: yes, minor**: In AnnotationPanel/PanelWidget.py:232-235 and 663-664, _apply_import_with_new_configuration derives a preset name via derive_import_preset_name(record, resolution.directory) (which produces 'Import-<scan_or_dir_name>', AnnotationModel.py:1337-1356) and calls save_preset_overwrite(preset_name, config.to_dict()). This overwrites any existing preset with the same derived 'Import-<name>' without checking for a collision, though the user already confirmed replacing the configuration in _prompt_import_configuration_choice (PanelWidget.py:615-634) and the name is prefixed with 'Import-'. This is an ordinary UX/soundness issue rather than a blocking safety vulnerability.

### D3. Matching-configuration import clears the current session without confirmation
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`AnnotationPanel/PanelWidget.py:548`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/PanelWidget.py#L548): The matching-configuration import path calls set_record with its default clear_existing=True, without the replacement prompt used for differing configurations. Existing ROI and segmentation scene nodes and classification annotations are removed, including unsaved work; a subsequent segmentation load can also fail after this destruction.
  ```
      def set_record(self, record, *, clear_existing=True):
          volume = self._active_volume_node
          if clear_existing:
              self._class_label_tab.set_class_label_annotations([])
              self._roi_tab.clear_and_unbind()
              self._segmentation_tab.clear_and_unbind()
  ```
  Suggestion: Explicitly confirm replacement whenever existing annotations are present, and load and validate the incoming project before deleting the old session.
- claude on re-check: **real: yes, minor**: When the configuration matches, import_annotations (lines 718-719) calls _apply_import_with_current_configuration, which calls set_record(record) with the default clear_existing=True (lines 548-553). It clears the existing annotations without a prompt. The user explicitly started an import and the label configuration is identical, so replacing the session is expected behavior. At most this is a missing confirmation, which is minor UX and not a safety issue.
- gpt on re-check: **real: yes, blocking**: PanelWidget.py:712-718 calls `        self._apply_import_with_current_configuration(record, resolution)` without the differing-configuration prompt; lines 672-675 then call `        self.set_record(record)`. The default in lines 548-553 invokes `            self._roi_tab.clear_and_unbind()` and `            self._segmentation_tab.clear_and_unbind()`. ROITab.py:1544-1549 removes registered scene nodes via `                        slicer.mrmlScene.RemoveNode(node)`; SegmentationTab.py:331-337 removes its segmentation node. PanelWidget.py:579-590 shows the new segmentation load can fail after removal. Unsaved existing work can be lost without an explicit replacement warning.
- gemini on re-check: **real: yes, minor**: In AnnotationPanel/PanelWidget.py:712-719, when label_configs_differ is False, import_annotations calls _apply_import_with_current_configuration (lines 672-678), which calls self.set_record(record) with the default clear_existing=True (lines 548-553) without prompting whether to discard existing in-memory annotations if self._has_any_annotations() is True. Furthermore, if record.segmentation fails to load at line 580, the previous annotations have already been cleared. While real, this occurs when the user explicitly initiates 'Import Annotations' and selects an import file/folder; missing an 'unsaved changes' confirmation dialog on explicit file load is a soundness/UX bug (minor/major), not a blocking safety issue.

### D4. Anatomical slice indices assume voxel axes match anatomical axes
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`AnnotationPanel/SliceInfo.py:271`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/SliceInfo.py#L271): IJK axes depend on the volume's orientation, not on anatomical plane names. For permuted or oblique acquisitions this can export a different voxel axis as the slice index; additionally, index zero falls through to a different calculation in capture_slice_info_for_view.
  ```
      normalized = slice_view_to_plane(plane)
      if normalized == "Axial":
          return int(voxel_index_ijk[2])
      if normalized == "Coronal":
          return int(voxel_index_ijk[1])
      if normalized == "Sagittal":
  ```
  Suggestion: Derive the relevant axis and index from the volume and slice geometry, and explicitly handle zero and oblique views in tests.
- claude on re-check: **real: yes, minor**: SliceInfo.py lines 267-278 map Axial, Coronal and Sagittal to IJK axes 2, 1 and 0. This is only correct for volumes whose voxel axes are aligned with the anatomical axes. In capture_slice_info_for_view, `if anatomical_index:` (line 367) treats index 0 as false and falls back to the offset-based index. This is a real soundness limitation for oblique or permuted volumes, but it only affects exported metadata. I rate it minor.
- gpt on re-check: **real: yes, major**: SliceInfo.py:267-277 fixes anatomical planes to IJK components, including `        return int(voxel_index_ijk[2])` for axial, without using the volume orientation; permuted or oblique volumes therefore need not have the assumed normal axis. Lines 364-373 use `        if anatomical_index:` so a valid zero instead takes the GetSliceIndexFromOffset fallback. This can give incorrect exported slice metadata; the full IJK and geometric context are also retained (lines 329-362), so the finding does not establish destruction of voxel data.
- gemini on re-check: **real: yes, major**: In AnnotationPanel/SliceInfo.py:267-278, anatomical_slice_index_from_ijk hardcodes Axial -> voxel_index_ijk[2], Coronal -> voxel_index_ijk[1], and Sagittal -> voxel_index_ijk[0]. Because IJK axes depend on the volume's IJKToRAS orientation matrix rather than fixed anatomical planes, non-LPS/RAS-aligned or sagittal/coronal/oblique acquisitions will pick the wrong voxel axis. Additionally, in SliceInfo.py:364-370, 'if anatomical_index:' treats slice index 0 as falsy and falls through to the offset fallback.

### D5. Slice-view event filters all reference the final loop callback
single; category soundness; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`AnnotationPanel/SliceInfo.py:72`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/SliceInfo.py#L72): The eventFilter method closes over the loop-local name _remember_view rather than binding the current callback. After the loop completes, filters can all use the last view's callback, so mouse or wheel events in another view may record the wrong active slice and thus the wrong ROI context.
  ```
              def _remember_view(view_name=name):
                  global _last_active_slice_view
                  _last_active_slice_view = view_name
  
              class _SliceViewTracker(qt.QObject):
                  def eventFilter(self, obj, event):
  ```
  Suggestion: Bind the view name or callback separately to each tracker instance and test interactions in all slice views.
- claude on re-check: **real: yes, minor**: In SliceInfo.py lines 72-80 the eventFilter of the class defined inside the loop calls `_remember_view()`. That name is a free variable of the enclosing function, resolved late, so every tracker calls the last loop iteration's callback. The default-argument binding only protects the callback's own view_name. The bug is real. Its impact is limited because lines 49-70 add per-view slice-modified and interactor observers that bind view_name correctly, so most of the time the active view is still tracked.
- gpt on re-check: **real: yes, minor**: SliceInfo.py:72-79 defines `_remember_view` inside the loop and `                        _remember_view()` inside eventFilter without binding that callback per iteration. Python's shared closure cell therefore points all such filters to the last callback after the loop. ROITab.py:1417-1423 uses `        slice_info = capture_slice_info(self._volume_node)` on ROI finalization, and SliceInfo.py:392-407 obtains the active view from this tracking state. Other slice-node and interactor callbacks at SliceInfo.py:49-70 bind `view_name=name` correctly and can update it too, so actual impact depends on event ordering; incorrect context metadata is plausible, not proven for every interaction.
- gemini on re-check: **real: yes, major**: In AnnotationPanel/SliceInfo.py:41-84, inside the 'for name in layout_manager.sliceViewNames():' loop, _SliceViewTracker.eventFilter (lines 76-80) calls _remember_view() without arguments, looking up the function name _remember_view in the enclosing install_slice_tracking scope. After the loop finishes, _remember_view is bound to the function created in the last loop iteration (where default argument view_name=name is the final slice view). Consequently, mouse press or wheel events intercepted by the Qt eventFilter on any slice view will record the last loop iteration's view name.

### D6. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **real: no, info**: I searched AnnotationPanel/ for urllib, requests, socket, subprocess, os.system, eval, exec, pickle, pip_install, rmtree, zipfile and tarfile and found no matches. I found no network access, downloads, code execution, package installation or obfuscation. File writes go to the presets folder (PresetStorage.py) and to user-chosen export folders. The preset name is sanitized by sanitize_preset_filename. The only issues are ordinary data-handling and UX bugs, so I rate safety ok.
- gpt on re-check: **rating blocking**: Concrete unintended user-data loss is present: PanelWidget.py:712-718 imports matching configurations without a replacement prompt and lines 548-553 call `            self._roi_tab.clear_and_unbind()` and `            self._segmentation_tab.clear_and_unbind()`; ROITab.py:1544-1549 and SegmentationTab.py:331-337 remove scene nodes. Separately PanelWidget.py:232-235 calls `            save_preset_overwrite(preset_name, config.to_dict())`, and PresetStorage.py:149-154 writes with `    with open(path, "w", encoding="utf-8") as handle:`, potentially replacing a saved preset without warning. I also searched AnnotationPanel source for network, subprocess and unsafe-deserialization patterns; no matches were returned. This is not a full audit, and I could not verify the supplied commit against a remote or run Slicer.
- gemini on re-check: **rating ok**: Checked all Python files in AnnotationPanel/ (AnnotationPanel.py, PanelWidget.py, AnnotationModel.py, PresetStorage.py, ConfigurationScreen.py, ClassLabelTab.py, ROITab.py, SegmentationTab.py, SliceInfo.py, LabelColors.py, RadiologyTerms.py, ConfigurationValidation.py). There is no network communication, telemetry, subprocess execution, dynamic code execution, or unsafe deserialization. File writes are restricted to user-selected export directories and the extension's preset JSON directory using sanitized filenames (PresetStorage.py:75-87). The issues raised in D2 and D3 are ordinary UX/state-management behaviors during user-initiated imports, not safety vulnerabilities.


## Findings from some reviewers

### Export includes patient identifiers without a clear privacy warning
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`AnnotationPanel/AnnotationModel.py:1039`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/AnnotationModel.py#L1039): Patient ID and DICOM identifiers are automatically captured and written into the user-selected export. Users sharing annotation packages may not realize they contain identifiers: the README mentions series metadata and UIDs but does not explicitly mention patient ID. No automatic network transmission was found.
  ```
              "modality": self.modality,
              "patient_id": self.patient_id,
              "study_description": self.study_description,
              "series_description": self.series_description,
              "study_instance_uid": self.study_instance_uid,
  ```
  Suggestion: Warn in the export dialog and documentation, and offer a de-identified export option.

### Generic helper module names placed on sys.path at Slicer startup
minor; environment; raised by gemini, gpt
- **gemini** (minor, high confidence, quote verified) [`AnnotationPanel/AnnotationPanel.py:11`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/AnnotationPanel.py#L11): At module import time (which happens during Slicer startup for all scripted loadable modules), `AnnotationPanel.py` inserts its directory at the front of `sys.path` and imports top-level modules with generic names (`LabelColors`, `PresetStorage`, and later `PanelWidget`, `AnnotationModel`, `SliceInfo`, `ROITab`, `SegmentationTab`, `ClassLabelTab`, `ConfigurationScreen`). While Slicer normally adds scripted module directories or packages, placing 11 generic top-level module names in `sys.path[0]` at startup risks name collisions with other Slicer extensions in the shared Python environment.
  ```
  MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
  if MODULE_DIR not in sys.path:
      sys.path.insert(0, MODULE_DIR)
  
  # Fail fast with a clear import error if extension files are incomplete.
  try:
  ```
  Suggestion: Move the helper modules into a dedicated Python package directory (e.g., `AnnotationPanelLib/`) and install them via `KIT_PYTHON_SCRIPTS`, importing them as `from AnnotationPanelLib import ...`.
- **gpt** (minor, high confidence, quote verified) [`AnnotationPanel/AnnotationPanel.py:11`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/AnnotationPanel.py#L11): If the directory is not already present, importing the module inserts it at the front of the shared interpreter search path. Generic helper names such as PanelWidget and SliceInfo may then collide with other extensions' imports or already-loaded modules.
  ```
  MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
  if MODULE_DIR not in sys.path:
      sys.path.insert(0, MODULE_DIR)
  ```
  Suggestion: Package helpers under a uniquely named Python package and use qualified imports without prepending a generic module directory.

### Global slice-tracking observers and event filters are not removed in cleanup()
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`AnnotationPanel/PanelWidget.py:742`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/PanelWidget.py#L742): `install_slice_tracking()` in `SliceInfo.py` attaches VTK observers and Qt event filters to Slicer's Red/Green/Yellow slice nodes, interactors, and slice views, storing them in the module-level `_slice_observers` list. Although `SliceInfo.py` defines `remove_slice_tracking()`, `AnnotationPanelRootWidget.cleanup()` never calls `remove_slice_tracking()`, leaving those observers and event filters active after the widget is cleaned up.
  ```
      def cleanup(self):
          """Clean up observers when the panel is destroyed."""
          self._remove_scene_observers()
          self._roi_tab.cleanup()
          self._segmentation_tab.cleanup()
  ```
  Suggestion: Call `remove_slice_tracking()` inside `AnnotationPanelRootWidget.cleanup()`.

### Module category in AnnotationPanel.py ("Annotation") differs from README and catalog ("Quantification")
info; packaging; raised by gemini
- **gemini** (info, high confidence, quote verified) [`AnnotationPanel/AnnotationPanel.py:29`](https://github.com/TeamOrydex/SlicerAnnotationPanel/blob/8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae/AnnotationPanel/AnnotationPanel.py#L29): The catalog entry and `CMakeLists.txt` specify the category `"Quantification"`, and `README.md` (line 124) instructs users that "The module will appear under the **Quantification** category." However, `AnnotationPanel.py` sets `self.parent.categories = ["Annotation"]`, so users looking under Quantification in Slicer's module selector will not find it there.
  ```
      def __init__(self, parent):
          ScriptedLoadableModule.__init__(self, parent)
          self.parent.title = "Annotation Panel"
          self.parent.categories = ["Annotation"]
  ```
  Suggestion: Align `self.parent.categories` in `AnnotationPanel.py` with the documented category (or update the README).


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I found no malicious behavior, network access, package installation or unsafe deserialization in the files I read. I did not read all of AnnotationModel.py, SegmentationTab.py or ConfigurationScreen.py. The blocking problem is packaging. AnnotationPanel/CMakeLists.txt installs only AnnotationPanel.py, but the module imports about ten sibling Python files. In a catalog-built package those files would be missing and the module would fail to load. Minor items are generic top-level module names added to sys.path, writing presets into the module install directory, an unset icon resource, and the catalog entry tracking the moving "production" branch.
Not checked: Full contents of AnnotationModel.py, SegmentationTab.py, ConfigurationScreen.py and ClassLabelTab.py; Existence of the 'production' branch/revision on GitHub; Runtime behavior in Slicer; Binary icon and screenshot contents

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
🔴 Do not merge yet: SlicerAnnotationPanel is a well-documented, safe, Apache-2.0-licensed extension for unified classification, ROI, and segmentation annotation with no external dependencies or unsafe behavior. However, there is a blocking packaging defect in `AnnotationPanel/CMakeLists.txt`: `KIT_PYTHON_SCRIPTS` only lists `AnnotationPanel.py` and omits all 11 sibling Python modules (`PanelWidget.py`, `AnnotationModel.py`, `LabelColors.py`, `PresetStorage.py`, `ROITab.py`, `SegmentationTab.py`, `ClassLabelTab.py`, `ConfigurationScreen.py`, `ConfigurationValidation.py`, `RadiologyTerms.py`, `SliceInfo.py`) and `Resources/Icons/AnnotationPanel.png`. In a CMake-built extension package, none of those files will be installed and `AnnotationPanel.py` will immediately raise `ImportError` at startup.
Not checked: Runtime execution in 3D Slicer (static source review only).
Questions for the author: Did you test installing the built extension package via CMake/CPack, where only files listed in `AnnotationPanel/CMakeLists.txt` (`KIT_PYTHON_SCRIPTS` and `KIT_PYTHON_RESOURCES`) are copied into the installation directory?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The build installs only the entry-point script, so the packaged module cannot import its required helpers. Import can also silently overwrite a saved preset or discard an existing annotation session. Several spatial-metadata issues warrant non-blocking follow-up. 🔴 Do not merge yet: fix the missing packaged files and unintended data loss; the production branch revision also needs verification.
Not checked: Could not run Slicer, build the extension, or execute the test suite; findings are based on static inspection.; Could not access the remote repository or resolve the production branch to independently verify that it matches the supplied commit 8f15ebf7c7b23f7b4f7120f190bec89cbdd73bae.; No prior catalog entry, PR checklist, CI reports, or trusted previous source revision was available for comparison.; External dependencies and binary image assets were not independently audited for provenance or licensing.
Questions for the author: Can the catalog production branch be verified to resolve to the supplied source commit, and can a clean packaged-install smoke test be provided?


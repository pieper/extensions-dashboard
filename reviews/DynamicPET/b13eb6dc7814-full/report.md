# AI review: DynamicPET

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/DanieleDallOlio/SlicerDynamicPET.git at commit `b13eb6dc78149d147166a071512bab885e98d949`
- Context: pull request 2436 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-13T17:10:06Z; cost $0.70

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | minor | concern |
| packaging | unknown | ok | unknown |
| license | unknown | ok | unknown |
| soundness | unknown | minor | unknown |
| utility | unknown | ok | minor |
| **overall** | needs fixes | minor issues | needs fixes |

## What each reviewer says the extension does

- **claude**: DynamicPET is a C++ loadable module bundle for dynamic PET analysis in 3D Slicer. It extracts time-activity curves from segmentations, fits kinetic models (Patlak, Logan, compartment models) per ROI or per voxel, and creates parametric images. It also bundles a dynamic PET DICOM importer and a dynamic RTSTRUCT importer.
- **gemini**: DynamicPET is a 3D Slicer extension for importing, visualizing, and quantitatively analyzing dynamic positron emission tomography (PET) acquisitions. It provides PET DICOM and dynamic RT Structure Set import/export, regional time-activity curve (TAC) extraction, kinetic modeling (Patlak, Logan, RE, 1TCM, 2TCM, Liver DBIF), and voxel-wise parametric map generation for researchers.
- **gpt**: DynamicPET helps researchers import and analyze dynamic PET data in 3D Slicer. It extracts time-activity curves, fits kinetic models, produces parametric images, and supports temporal RT structures.

## Disagreements (start here)

### D1. Excel exports replace existing workbooks without confirmation
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (2 of 2)**
- **gpt** (blocking, high confidence, quote verified) [`DynamicPET/qSlicerDynamicPETModuleWidget.cxx:9297`](https://github.com/DanieleDallOlio/SlicerDynamicPET/blob/b13eb6dc78149d147166a071512bab885e98d949/DynamicPET/qSlicerDynamicPETModuleWidget.cxx#L9297): The TAC save handler passes the chosen directory and default patient-based filename directly to this writer without checking for an existing file (lines 25647–25652 and 25749–25752). A repeated save or same-name patient can therefore destroy a previous workbook without warning; the other Excel save helpers should also be checked.
  ```
      pd, dependency_error = DPE_prepare_excel_dependencies("export")
      if pd is None:
          return {"ok": False, "error": dependency_error}
  
      with pd.ExcelWriter(filepath, engine="xlsxwriter") as writer:
          for sheet, data in sheet_data_dict.items():
  ```
  Suggestion: Confirm existing-file replacement, use unique study-aware names, and write safely via a temporary file.
- gpt on re-check: **real: yes, blocking**: DynamicPET/qSlicerDynamicPETModuleWidget.cxx:23833-23838 sets the default from the patient name: `d->fileexcel->setText(name + QStringLiteral("_TAC.xlsx"));`. Lines 25647-25652 construct the path from directory and filename, and 25749-25752 pass it directly to the writer. Line 9301 is `    with pd.ExcelWriter(filepath, engine="xlsxwriter") as writer:`: the default write mode replaces an existing workbook, with no overwrite check in the handler. Repeated saves or different studies sharing a patient name can destroy prior results. The other four handlers at 25763-25840 and writers at 9704, 9742, 9799, and 9839 follow the same pattern. Require confirmation or a unique filename and safe replacement.
- gemini on re-check: **real: yes, minor**: Checked DynamicPET/qSlicerDynamicPETModuleWidget.cxx lines 9291-9313, 9688-9715, 9717-9745, and 25647-25849. The Excel save button handlers construct `fullPath = QDir(path).filePath(filename)` from the UI directory selector and filename text box (which defaults to a patient-based filename) and call `pd.ExcelWriter(filepath, engine="xlsxwriter")`, which overwrites an existing file at that path without a confirmation dialog. However, writing directly to the user-specified directory and filename when the user clicks the Save button is a standard UI/UX omission (lack of an overwrite prompt), not a blocking safety issue.

### D2. Parametric-map export silently deletes existing files
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (2 of 2)**
- **gpt** (blocking, high confidence, quote verified) [`DynamicPET/qSlicerDynamicPETModuleWidget.cxx:10713`](https://github.com/DanieleDallOlio/SlicerDynamicPET/blob/b13eb6dc78149d147166a071512bab885e98d949/DynamicPET/qSlicerDynamicPETModuleWidget.cxx#L10713): When DICOM output is selected, the caller constructs deterministic filenames from the patient name, model and field (lines 22185–22205). Repeating an export into the same directory, including for a different study of the same patient, silently deletes the previous map; if writing fails after removal, the previous file is already lost.
  ```
          output_path = os.path.abspath(str(output_path))
          os.makedirs(os.path.dirname(output_path), exist_ok=True)
          if os.path.isfile(output_path):
              os.remove(output_path)
  
          pm.save_as(output_path, enforce_file_format=True)
  ```
  Suggestion: Detect collisions before export, ask for explicit replacement or generate unique filenames, and write to a temporary file before an atomic replacement.
- gpt on re-check: **real: yes, blocking**: DynamicPET/qSlicerDynamicPETModuleWidget.cxx:22185-22205 constructs the deterministic patient/method/model/field filename using `"%1_PMAP_%2_%3_%4.dcm"`; lines 22227-22235 pass it to the Python exporter without an existence confirmation. Lines 10715-10718 say `        if os.path.isfile(output_path):` / `            os.remove(output_path)` / `        pm.save_as(output_path, enforce_file_format=True)`. A repeated export or a different study with the same patient name can silently destroy a previous map, even if the following write fails. Prompt for replacement and use safe transactional writes.
- gemini on re-check: **real: yes, minor**: Checked DynamicPET/qSlicerDynamicPETModuleWidget.cxx lines 10713-10718 and 22185-22205. When exporting a DICOM Parametric Map to the user-chosen `outputDirectory`, `outputPath` is constructed deterministically as `%1_PMAP_%2_%3_%4.dcm` (patient name, method, model, field), and `DPE_export_parametric_map` removes `output_path` if `os.path.isfile(output_path)` before calling `pm.save_as(output_path, enforce_file_format=True)`. Overwriting an earlier export with the same deterministic name in the same output directory without prompting (or before writing a temp file) is an ordinary usability/robustness concern rather than a blocking safety vulnerability.

### D3. Parametric-map export installs highdicom without consent
single; category environment; raised by gpt; outcome after cross-examination: **real, minor (2 of 2)**
- **gpt** (major, high confidence, quote verified) [`DynamicPET/qSlicerDynamicPETModuleWidget.cxx:9242`](https://github.com/DanieleDallOlio/SlicerDynamicPET/blob/b13eb6dc78149d147166a071512bab885e98d949/DynamicPET/qSlicerDynamicPETModuleWidget.cxx#L9242): On parametric-map export, DPE_export_parametric_map calls this function; if highdicom is absent it downloads and installs a package into Slicer's shared Python environment without asking, even though the user selected an export rather than a package installation.
  ```
          import highdicom as hd
      except ModuleNotFoundError as exc:
          if exc.name != "highdicom":
              raise RuntimeError(
                  "The installed highdicom package could not be imported because "
                  f"Python module '{exc.name}' is unavailable. SlicerDynamicPET "
  ```
  Suggestion: Explain the dependency and request confirmation before installing it, as the Excel dependency helper does; handle missing dependencies without altering existing bundled packages.
- gpt on re-check: **real: yes, major**: DynamicPET/qSlicerDynamicPETModuleWidget.cxx:9918-9919 calls `        hd = DPE_get_highdicom()` when exporting a parametric map. If the top-level package is absent, lines 9242-9254 execute `            slicer.util.pip_install("--no-deps highdicom")` without asking. This changes Slicer's shared Python environment during export; `--no-deps` limits dependency changes but does not provide consent. Ask before installation or use an appropriate dependency mechanism.
- gemini on re-check: **real: yes, minor**: Checked DynamicPET/qSlicerDynamicPETModuleWidget.cxx lines 9233-9260. Unlike `DPE_prepare_excel_dependencies` (lines 9200-9213), which prompts the user with `slicer.util.confirmYesNoDisplay` before calling `slicer.util.pip_install`, `DPE_get_highdicom()` immediately calls `slicer.util.pip_install("--no-deps highdicom")` when `import highdicom` raises `ModuleNotFoundError`. Because this only happens on user-initiated DICOM Parametric Map export (not at startup/import) and uses `--no-deps` for a small pure-Python package so existing packages cannot be upgraded or downgraded, the impact on Slicer's environment is minor, though prompting for confirmation like the Excel helper does would be better.

### D4. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- gpt on re-check: **rating blocking**: Blocking is warranted by two verified unintended-data-loss paths: DynamicPET/qSlicerDynamicPETModuleWidget.cxx:9301 uses `    with pd.ExcelWriter(filepath, engine="xlsxwriter") as writer:` for the patient-named export without an overwrite check, and 10715-10718 deletes a pre-existing deterministic DICOM map before writing it. These can destroy earlier user files, not merely produce incorrect calculations. I inspected the main export paths and searched the available DynamicPET source for downloads, execution, removal and network-related APIs; this is not a complete safety audit. The submodule sources listed in .gitmodules:1-9 and the exact checkout revision could not be independently verified with the available tools.
- gemini on re-check: **rating ok**: Checked the safety findings raised in D1 and D2 (DynamicPET/qSlicerDynamicPETModuleWidget.cxx lines 9291-9313, 10713-10718, 22185-22205, 25647-25849). There is no malicious behavior, unauthorized data transmission, unsafe deserialization, or arbitrary file destruction; overwriting previously exported files in a user-selected export folder when the user clicks Save/Export is a minor UX/soundness issue, so safety is `ok`.


## Findings from some reviewers

### Empty KIT_TEST_SRCS in DynamicPET/Testing/Cxx/CMakeLists.txt
minor; packaging; raised by gemini, gpt
- **gemini** (minor, high confidence, quote verified) [`DynamicPET/Testing/Cxx/CMakeLists.txt:4`](https://github.com/DanieleDallOlio/SlicerDynamicPET/blob/b13eb6dc78149d147166a071512bab885e98d949/DynamicPET/Testing/Cxx/CMakeLists.txt#L4): In `DynamicPET/Testing/Cxx/CMakeLists.txt`, `KIT_TEST_SRCS` is empty (the test source is commented out), which is then passed to `slicerMacroConfigureModuleCxxTestDriver`. Depending on the CMake/Slicer version, configuring a Cxx test driver with no test sources may fail or produce an empty test executable when `BUILD_TESTING` is enabled.
  ```
  set(KIT_TEST_SRCS
    #qSlicer${MODULE_NAME}ModuleTest.cxx
    )
  ```
  Suggestion: Either add a basic module test source file or guard `add_subdirectory(Testing)` / `slicerMacroConfigureModuleCxxTestDriver` until C++ tests are enabled.
- **gpt** (minor, high confidence, quote verified) [`DynamicPET/Testing/Cxx/CMakeLists.txt:4`](https://github.com/DanieleDallOlio/SlicerDynamicPET/blob/b13eb6dc78149d147166a071512bab885e98d949/DynamicPET/Testing/Cxx/CMakeLists.txt#L4): The visible test driver has no enabled module test source, so this checkout does not provide automated regression coverage for the main PET workflow through this test configuration.
  ```
  set(KIT_TEST_SRCS
    #qSlicer${MODULE_NAME}ModuleTest.cxx
    )
  ```
  Suggestion: Add reproducible tests for representative PET timing, fitting, and export workflows.

### Placeholder metadata and "Examples" category in qSlicerDynamicPETModule.cxx
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DynamicPET/qSlicerDynamicPETModule.cxx:58`](https://github.com/DanieleDallOlio/SlicerDynamicPET/blob/b13eb6dc78149d147166a071512bab885e98d949/DynamicPET/qSlicerDynamicPETModule.cxx#L58): `qSlicerDynamicPETModule.cxx` still has the cookiecutter template strings for `helpText()`, `acknowledgementText()` ("NIH grant NXNNXXNNNNNN-NNXN"), `contributors()` ("John Doe (AnyWare Corp.)"), and `categories()` ("Examples", whereas `CMakeLists.txt` and the catalog entry use "Quantification"). Users will look for the module under "Quantification" in Slicer's module selector, not "Examples".
  ```
  QString qSlicerDynamicPETModule::helpText() const
  {
    return "This is a loadable module that can be bundled in an extension";
  }
  ```
  Suggestion: Update `categories()` to return `"Quantification"` (matching the catalog entry and top-level `CMakeLists.txt`), and replace the placeholder help text, acknowledgements, and contributor name (`John Doe`) in `qSlicerDynamicPETModule.cxx`.

### Unprompted pip install of highdicom during Parametric Map export
minor; environment; raised by gemini
- **gemini** (minor, high confidence, quote verified, other lines) [`DynamicPET/qSlicerDynamicPETModuleWidget.cxx:9182`](https://github.com/DanieleDallOlio/SlicerDynamicPET/blob/b13eb6dc78149d147166a071512bab885e98d949/DynamicPET/qSlicerDynamicPETModuleWidget.cxx#L9182): When a user exports a DICOM Parametric Map (`DPE_export_parametric_map`), `DPE_get_highdicom()` runs `slicer.util.pip_install("--no-deps highdicom")` without asking the user for confirmation first (unlike `DPE_prepare_excel_dependencies`, which prompts via `slicer.util.confirmYesNoDisplay`). Additionally, because `--no-deps` is used, if any of `highdicom`'s non-bundled dependencies (such as `pyjpegls` or newer `pillow`/`numpy` requirements depending on the PyPI release) are absent, importing or using `highdicom` may fail at runtime.
  ```
          try:
              slicer.util.pip_install("--no-deps highdicom")
              importlib.invalidate_caches()
              import highdicom as hd
  ```
  Suggestion: Prompt the user with `slicer.util.confirmYesNoDisplay` before installing `highdicom` into Slicer's shared Python environment, just as `DPE_prepare_excel_dependencies` does for `pandas`/`openpyxl`/`xlsxwriter`.

### Extension uses three Git submodules (KMAP-CPP, dPETImporter, dRTImporter)
info; packaging; raised by gemini
- **gemini** (info, high confidence, quote verified) [`CMakeLists.txt:139`](https://github.com/DanieleDallOlio/SlicerDynamicPET/blob/b13eb6dc78149d147166a071512bab885e98d949/CMakeLists.txt#L139): The extension relies on three Git submodules (`KMAP-CPP`, `dPETImporter`, `dRTImporter` declared in `.gitmodules` and added via `add_subdirectory` in `CMakeLists.txt`). While Slicer's extension build system initializes submodules recursively during builds, the contents of those three external repositories are not present in this repository checkout and could not be directly inspected here.
  ```
  add_subdirectory(KMAP-CPP)
  ```
  Suggestion: Verify that the pinned submodule commits in `KMAP-CPP`, `dPETImporter`, and `dRTImporter` exist on GitHub and carry compatible license files.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I reviewed the top-level CMake files, the module, watcher and worker sources, the logic header, and the README. I searched the two very large .cxx files with targeted greps instead of reading them in full. I found no malicious behaviour, network access or data exfiltration. Excel dependencies are installed only after a confirmation prompt. highdicom is pip-installed without any prompt when a Parametric Map export is first used. The module still carries template placeholder metadata ("John Doe", category "Examples", an NIH grant placeholder). Most of the code lives in three git submodules that I could not inspect, and the scm_revision "5.12" could not be resolved. The MIT license is present. The verdict is minor issues, but the review is incomplete for the submodule code.
Not checked: 
<parameter name="1">

### Gemini 4 Argon (`google/gemini-4-argon`): minor issues
DynamicPET provides a rich C++ loadable module and Python bridges for dynamic PET DICOM and temporal RTSTRUCT handling, time-activity curve extraction, compartmental and graphical kinetic modeling, and voxel-wise parametric imaging. In the inspected main repository (`b13eb6dc`), there are no blocking safety, licensing, or catalog entry defects. Non-blocking suggestions include updating the cookiecutter placeholder metadata and `"Examples"` category in `qSlicerDynamicPETModule.cxx`, prompting the user before installing `highdicom`, and guarding the empty test source list in `DynamicPET/Testing/Cxx/CMakeLists.txt`. Note that the three Git submodules (`KMAP-CPP`, `dPETImporter`, `dRTImporter`) are external repositories not expanded in this checkout and could not be directly inspected. 🟢 Recommend merge (subject to submodule availability).
Not checked: Source code and license files inside the three Git submodules (dPETImporter, dRTImporter, KMAP-CPP), which are external repositories not expanded in the workspace checkout.; Whether branch `5.12` (referenced in `scm_revision` of the catalog entry) resolves to commit `b13eb6dc78149d147166a071512bab885e98d949` on GitHub.
Questions for the author: Could you update `qSlicerDynamicPETModule::categories()` from `"Examples"` to `"Quantification"` and replace the template `John Doe` contributor and help text in `DynamicPET/qSlicerDynamicPETModule.cxx`?; Could you add a user confirmation prompt (`slicer.util.confirmYesNoDisplay`) before `slicer.util.pip_install("--no-deps highdicom")` in `DPE_get_highdicom()`, matching how Excel dependencies are handled?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The main code silently replaces existing DICOM parametric maps and Excel workbooks on repeat exports, creating a concrete risk of data loss. Parametric-map export also installs highdicom without asking. The three required submodules, their licenses and the catalog branch resolution were unavailable for inspection. 🔴 Do not merge yet: prevent unconfirmed overwrites and complete the source, dependency, license and revision review.
Not checked: The catalog branch 5.12 could not be resolved to the stated b13eb6dc78149d147166a071512bab885e98d949 commit; source repository accessibility and exact revision are unverified.; The KMAP-CPP, dPETImporter and dRTImporter submodule contents, gitlink revisions, build rules, installation behavior and license files were unavailable. The README reports an additional on-demand highdicom installation in the importer; its consent and dependency behavior could not be inspected.; No Slicer build, CI results, runtime tests, dependency metadata, numerical validation, or network access were available.; The large widget and numerical C++ files were searched and sampled rather than reviewed line by line; no complete security audit is claimed.
Questions for the author: Can you provide the resolved 5.12 commit and a checkout with all three submodules at their recorded revisions, including their license files and build configuration?


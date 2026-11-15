# AI review: RadReirradiation

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/LuisParedesOcampo/SlicerRadReirradiation at commit `397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:45:31Z; cost $0.03

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | concern |
| environment | minor | ok | minor |
| packaging | minor | ok | concern |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: RadReirradiation is a SlicerRT-dependent scripted module for medical physicists that registers two CT/dose courses, computes voxel-wise BED/EQD2 summation with per-structure alpha/beta and recovery, and reports DVH metrics, a PDF report and an exported EQD2 RTDOSE for TPS import.
- **flash-lite**: RadReirradiation is a 3D Slicer scripted module for radiotherapy re-irradiation analysis, voxel-based EQD2/BED biological dose calculation, sequential boost integration, and DVH metrics generation.
- **haiku**: RadReirradiation is a Slicer scripted module for radiotherapy re-irradiation analysis: it registers previous and current CT scans, resamples and sums LQ-model EQD2/BED doses voxel by voxel, computes DVH and DMax/DMean metrics, and exports a PDF report and a derived RTDOSE/RTPLAN for TPS import. It is aimed at medical physicists and radiation oncologists, and depends on SlicerRT for DICOM-RT loading.

## Disagreements (start here)

### D1. Derived RTDOSE/RTPLAN intended to bypass TPS dose locks
single; category safety; raised by haiku
- **haiku** (major, high confidence, quote verified) [`README.md:266`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/README.md#L266): The README says the export feature 'bypasses standard TPS dose-lock restrictions' and produces a 'shadow' RTPLAN and RTDOSE for import into commercial TPS (Eclipse, Monaco). The code (RadReirradiation.py:2305-2358) builds a plan from the original RTPLAN with the dose references removed and a new SOP UID, then writes it. A research-only tool's derived dose could be imported into a clinical TPS and mistaken for an approved plan. The code sets ApprovalStatus to UNAPPROVED, which is a partial mitigation, but the README's claim is an explicit bypass of a safety control.
  ```
  This ensures seamless import compatibility and bypasses standard TPS dose-lock restrictions.
  ```
  Suggestion: Remove the 'bypasses dose-lock' wording. Add an on-screen warning before export that the file is research-only and not for treatment. Keep the UNAPPROVED status and add a visible marker in the DICOM (e.g., SeriesDescription or a text note) identifying it as a derived research dose.

### D2. Exported EQD2 RTDOSE keeps the template's spatial geometry and a fabricated shadow RTPLAN
single; category soundness; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`RadReirradiation.py:2182`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/RadReirradiation.py#L2182): The export clones the original RTDOSE and only replaces NumberOfFrames/Rows/Columns, GridFrameOffsetVector, DoseGridScaling and PixelData (lines 2179-2210). ImagePositionPatient, PixelSpacing, ImageOrientationPatient and FrameOfReferenceUID are never taken from the EQD2 volume, which after registration was resampled to the *current* CT geometry (lines 2876-2894). The written file therefore carries the previous course's origin/spacing/frame of reference with the new voxel data, so a TPS importing it can place the accumulated EQD2 dose at the wrong location. In addition the code copies the original RTPLAN, strips ReferencedDoseSequence, assigns new SOP UIDs and sets DoseSummationType = "PLAN" (lines 2305-2343) although the dose is a two-course sum, so the receiving TPS sees a plan whose dose does not correspond to its beams. Non-blocking per index policy (ordinary correctness), but it should be fixed before the export is advertised as TPS-ready.
  ```
          frames, rows, cols = eqd2_array.shape
          ds.NumberOfFrames = frames
          ds.Rows = rows
          ds.Columns = cols
  ```
  Suggestion: Set ImagePositionPatient, PixelSpacing, ImageOrientationPatient and FrameOfReferenceUID from the EQD2 volume node (and BitsStored/HighBit), use DoseSummationType MULTI_PLAN/FRACTION for a summed dose, and warn the user that the shadow plan is a placeholder.

### D3. SlicerRT dependency set with a non-standard CMake variable
severity dispute; category packaging; raised by deepseek, flash-lite, haiku
- **deepseek** (minor, medium confidence, quote verified) [`CMakeLists.txt:11`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/CMakeLists.txt#L11): The catalog entry contains only $schema, build_subdirectory, category, scm_revision, scm_url and tier, with no build_dependencies, while CMakeLists declares SlicerRT and the module sets self.parent.dependencies = [] (RadReirradiation.py line 19). The index therefore has no declared dependency to build/order SlicerRT, and Slicer will not warn users who open the module without SlicerRT installed even though DICOM-RT loading depends on it.
  ```
  set(EXTENSION_DEPENDENCIES SlicerRT)
  ```
  Suggestion: Add "build_dependencies": ["SlicerRT"] to the catalog entry and set self.parent.dependencies = ["SlicerRT"] in the module class.
- **flash-lite** (info, high confidence, quote quote not found) [`CMakeLists.txt:11`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/CMakeLists.txt#L11): CMake lists SlicerRT as the extension dependency, which matches the README requirements. All necessary scripts are bundled and registered via slicerMacroBuildScriptedModule.
  ```
  11  set(EXTENSION_DEPENDENCIES SlicerRT)
  ```
- **haiku** (major, medium confidence, quote verified) [`CMakeLists.txt:11`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/CMakeLists.txt#L11): The Slicer extension build reads EXTENSION_DEPENDS to declare required extensions. The CMakeLists sets EXTENSION_DEPENDENCIES, so SlicerRT is not recorded as a dependency. The module's parent.dependencies is also empty. Users who install from the catalog may get an extension that fails to load DICOM-RT features without SlicerRT, and the index may not install SlicerRT first. The README requires SlicerRT, so the declared dependency should match.
  ```
  set(EXTENSION_DEPENDENCIES SlicerRT)
  ```
  Suggestion: Use set(EXTENSION_DEPENDS SlicerRT). Also set parent.dependencies in the module to include SlicerRT, if the module imports it or needs its nodes.

### D4. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek ok, flash-lite ok, haiku concern

### D5. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D6. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings all reviewers agree on

### pip_install("pydicom") without user confirmation can override Slicer's bundled pydicom
minor; environment; raised by deepseek, flash-lite, haiku
- **deepseek** (minor, high confidence, quote verified) [`RadReirradiation.py:2078`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/RadReirradiation.py#L2078): pydicom ships with Slicer; if the import ever fails (broken install, conflicting module on the path) this silently installs the latest PyPI pydicom into Slicer's shared Python, which is exactly the bundled-package replacement the index policy asks to avoid and can break SlicerRT and other extensions for users who never open this module. It is not at import time and is unlikely to trigger, hence minor.
  ```
          except ImportError:
              slicer.util.pip_install("pydicom")
              import pydicom
              from pydicom.uid import generate_uid
  ```
  Suggestion: Remove the pip fallback and report a clear error asking the user to reinstall Slicer/SlicerRT, or gate any install behind an explicit user confirmation dialog.
- **flash-lite** (minor, high confidence, quote quote not found) [`RadReirradiation.py:2078`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/RadReirradiation.py#L2078): The module installs `pydicom` on demand via `slicer.util.pip_install("pydicom")` when exporting DICOM. While pydicom is generally safe and common in medical imaging, installing packages at runtime rather than declaring them in extension dependencies can cause environment side-effects or fail if offline. However, there is no malicious intent.
  ```
  2079          slicer.util.pip_install("pydicom")
  ```
- **haiku** (minor, high confidence, quote verified) [`RadReirradiation.py:2079`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/RadReirradiation.py#L2079): If pydicom cannot be imported, the export handler installs it into Slicer's Python environment with no prompt. This is a side effect on the shared environment, triggered by a button, and it can fail silently or pull an unpinned version that conflicts with the bundled one. slicer.util.pip_install normally shows a progress dialog, but the user has not agreed to the install.
  ```
  slicer.util.pip_install("pydicom")
  ```
  Suggestion: Ask the user for confirmation before installing, or rely on the pydicom that Slicer bundles and show a clear error if it is missing. Do not install unpinned packages at runtime.


## Findings from some reviewers

### Broad exception handling and a no-op test
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`RadReirradiation.py:3206`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/RadReirradiation.py#L3206): The export and PDF handlers catch all exceptions and show only the message string (RadReirradiation.py:2371-2374), and some reads use bare except (RadReirradiation.py:2279-2280). Failures may be hard to diagnose. The only test, RadReirradiationTest.runTest, is 'pass' (RadReirradiation.py:3206-3207), so there is no automated coverage of the EQD2 math or the DICOM export.
  ```
  def runTest(self):
          pass
  ```
  Suggestion: Add unit tests for the LQ/EQD2 formula and for DICOM export on small synthetic data. Narrow the exception handling and log details.

### Exceptions silently swallowed in DICOM lookup and fraction extraction
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`RadReirradiation.py:1157`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/RadReirradiation.py#L1157): attemptSilentFractionExtraction discards every error, and the DICOM search loops use bare `except: pass` (lines 2152-2153, 2235-2236, 2279-2280). If the fraction count cannot be recovered the spinbox keeps its default (25, line 120) and the EQD2 calculation silently uses a wrong fractionation, which is a dosimetric error the user is never told about.
  ```
          except Exception as e:
                  pass  # Silencio absoluto ante errores
  ```
  Suggestion: Log the exception and tell the user that the fraction count could not be read from the RTPLAN so it must be entered manually.

### Export copies files into the chosen folder with second-resolution names, risking overwrite
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`RadReirradiation.py:2298`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/RadReirradiation.py#L2298): The RTSTRUCT is copied under a fixed name and the RTPLAN/RTDOSE names use only HHMMSS (lines 2330, 2356), so two exports into the same folder within the same second, or a re-export, silently overwrite earlier files without asking. The user-chosen folder is respected, so this is limited to files the user pointed at.
  ```
              rtstruct_filename = f"RTSTRUCT_original_{os.path.basename(rtstruct_path)}"
              rtstruct_dest = os.path.join(output_dir, rtstruct_filename)
              shutil.copy2(rtstruct_path, rtstruct_dest)
  ```
  Suggestion: Include the date in the filenames and check for existing files before writing, or ask the user to confirm overwriting.

### Registration and resampling run synchronously on the GUI thread
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`RadReirradiation.py:2859`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/RadReirradiation.py#L2859): BRAINSFit (and BRAINSResample at line 2892) are run with slicer.cli.runSync inside the widget's button handler, with only a busy progress dialog and processEvents (lines 2806-2814). The README itself warns this can take several minutes (README line 206), during which Slicer is unresponsive and the user cannot cancel; a crash or forced quit loses the session state.
  ```
                  brainsFit = slicer.modules.brainsfit
                  cliNode = slicer.cli.runSync(brainsFit, None, parameters)
  
                  if cliNode.GetStatus() & cliNode.ErrorsMask:
                      raise ValueError("The image registration engine (BRAINSFit) failed.")
  ```
  Suggestion: Use slicer.cli.run with a status observer (or a CLI node plus progress bar) so the GUI stays responsive and the operation can be cancelled.

### Clinical-use disclaimer present and appropriate
info; utility; raised by haiku
- **haiku** (info, high confidence, quote verified) [`README.md:272`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/README.md#L272): The README states that the software is for research and educational purposes only and has not been cleared by any regulator, and it asks for independent verification. This is good practice for a dosimetry tool.
  ```
  **This software is for research and educational purposes only and has not been cleared for clinical use by any regulatory body (FDA, CE, etc.).**
  ```
  Suggestion: Repeat the disclaimer in the module's helpText so it is visible inside Slicer.

### No automated tests and premature availability claim in README
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.md:48`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/README.md#L48): The repository has no test suite for the radiobiology math (EQD2/BED, overlap priority, DVH metrics), which is the part most in need of regression checks for a clinical tool; the README also states the extension is already in the Extensions Manager before this submission is accepted. The research-only disclaimer (README lines 271-273) is present and appropriate.
  ```
  RadReirradiation is officially available in the 
  3D Slicer Extensions Manager.
  ```
  Suggestion: Add a small self-test (e.g., ScriptedLoadableModuleTest) covering EQD2/BED for known single- and two-course cases, and adjust the installation wording until the extension is published.

### Resources/UI/RadReirradiation.ui is not installed by CMake
info; packaging; raised by deepseek, flash-lite
- **deepseek** (info, low confidence, quote verified) [`CMakeLists.txt:16`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/CMakeLists.txt#L16): Only the icon is listed as a resource; the .ui file is not installed. The widget builds its interface programmatically in setup() (RadReirradiation.py lines 46-140), so the .ui file appears unused — but if any code path loaded it, the module would fail after installation. I did not find a loadUI call in the parts I read.
  ```
  slicerMacroBuildScriptedModule(
    NAME RadReirradiation
    SCRIPTS
      RadReirradiation.py
    RESOURCES
      Resources/Icons/RadReirradiation.png
  ```
  Suggestion: Either delete the unused .ui file or add it to RESOURCES if it is loaded at runtime.
- **flash-lite** (info, high confidence, quote quote not found) [`CMakeLists.txt:8`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/CMakeLists.txt#L8): The extension is well-documented with a comprehensive README, tutorials, clinical workflow steps, and standard research/educational use disclaimers.
  ```
  8  set(EXTENSION_DESCRIPTION "A clinical tool for Reirradiation analysis, EQD2 dose calculation, and integrated DVH metrics.")
  ```

### Valid MIT License present
info; license; raised by flash-lite; **quote not found in source**
- **flash-lite** (info, high confidence, quote quote not found) [`LICENSE:1`](https://github.com/LuisParedesOcampo/SlicerRadReirradiation/blob/397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee/LICENSE#L1): The repository includes a standard MIT License file with proper copyright attribution, permitting distribution.
  ```
  1  MIT License
  ```


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
No malicious or concealed behavior found: no network calls, telemetry, eval/exec, or downloads; the only pip call is a fallback `pip_install("pydicom")` inside the export handler. MIT license permits distribution; the catalog entry is usable (branch `main`, `build_subdirectory: "."`), though it lacks `build_dependencies` while CMakeLists declares `EXTENSION_DEPENDENCIES SlicerRT`. Main non-blocking concern: the DICOM export rewrites pixel data and frame count but never updates ImagePositionPatient/PixelSpacing/FrameOfReferenceUID, and fabricates a "shadow" RTPLAN, so the exported EQD2 dose can be spatially wrong in the receiving TPS. Also: synchronous BRAINSFit on the GUI thread and several silently swallowed exceptions. Per index policy the three admission requirements are met; recommend merge with follow-up fixes.
Not checked: The catalog entry pins scm_revision "main" while the review prompt names commit 397dba9fe4f00a7d5b2dfb7e4bf7d71a2871a0ee; I could not resolve the repository or verify that commit exists, so the exact reviewed revision is unknown.; I read roughly 600 of the 3207 lines of RadReirradiation.py (module/widget setup, export, PDF, registration logic); the DICOM auto-match, EQD2/BED math, DVH and metrics sections were not read line by line.; Whether Resources/UI/RadReirradiation.ui is loaded anywhere at runtime (no loadUI call seen in the inspected ranges).; Build/CI results for this extension and whether SlicerRT is present in the build environment.; Contents of the two PNG binaries (icon and screenshot).; Runtime behaviour of the BRAINSFit/BRAINSResample calls and of the generated DICOM files in a real TPS.
Questions for the author: Does the exported EQD2 RTDOSE set ImagePositionPatient/PixelSpacing/FrameOfReferenceUID from the resampled EQD2 volume, or does it intentionally inherit them from the template RTDOSE?; Why is pydicom installed with pip when Slicer already bundles it?; Should the catalog entry declare build_dependencies: ["SlicerRT"] and the module set parent.dependencies accordingly?; Is Resources/UI/RadReirradiation.ui used at all, or can it be removed?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
RadReirradiation is a robustly documented 3D Slicer extension for radiotherapy re-irradiation analysis and biological dose summation. It meets all packaging, licensing, and safety requirements. 🟢 Recommend merge
Not checked: Full mathematical verification of voxel-based radiobiology EQD2/BED calculations and DVH metric accuracy against clinical gold standards.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
I read the CMake file, license, README and the export/PDF sections of the single 3207-line module, plus targeted searches. I found no network calls, telemetry, obfuscation, or unsafe deserialization in the parts I searched. Concerns: a runtime pip install of pydicom on the export click without confirmation, a dependency variable (EXTENSION_DEPENDENCIES) that is not the standard EXTENSION_DEPENDS name, a README claim that the derived dose "bypasses standard TPS dose-lock restrictions", and an empty test. The MIT license is fine. Most of the registration and dose-engine code was not reviewed in detail.
Not checked: Most of RadReirradiation.py (about 3,000 lines), including the registration, BRAINSFit calls, LQ/EQD2 engine, DVH and metrics logic, and the PDF HTML template.; The UI file Resources/UI/RadReirradiation.ui, and whether the module loads it.; The actual source revision 397dba9 (the catalog uses scm_revision 'main'), so the reviewed code may differ from the tip.; No build or Slicer load was performed. CI reports were not available.; Whether pydicom is bundled with the Slicer version targeted, which determines whether the runtime install is ever reached.; The YouTube tutorial and the external streamlit web app, which were not accessed.
Questions for the author: Why does the module use EXTENSION_DEPENDENCIES rather than EXTENSION_DEPENDS in CMakeLists.txt, and should SlicerRT be added to parent.dependencies?; Can the pydicom install be removed, or made to ask the user first?; Please reword the 'bypasses standard TPS dose-lock restrictions' claim and describe the derived files as research-only in the export dialog.; Please add real tests (even a synthetic LQ/EQD2 check) and state the Slicer version that was tested.


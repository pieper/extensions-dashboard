# AI review: Breast_DCEMRI_FTV

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV at commit `271ece80ce3db9cc79596ee5436dd5d44ed1a50c`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-20T02:41:05Z; cost $1.02

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | blocking | blocking |
| environment | unknown | blocking | concern |
| packaging | unknown | minor | unknown |
| license | unknown | ok | ok |
| soundness | unknown | concern | concern |
| utility | unknown | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: Two scripted modules for computing breast DCE-MRI functional tumor volume (FTV). Module 1 identifies the DCE series and early/late phases from a DICOM exam folder. Module 2 lets the user set an ROI and omit regions, shows SER-colorized segmentation and writes a PDF report. Aimed at UCSF/I-SPY/ACRIN-style research workflows.
- **gemini**: Breast_DCEMRI_FTV is a two-module 3D Slicer extension developed by the UCSF Breast Imaging Research Group for breast cancer researchers to compute functional tumor volume (FTV) from dynamic contrast-enhanced MRI (DCE-MRI) exams. It loads pre-contrast, early post-contrast, and late post-contrast series, allows ROI and omit-region definition, overlays Signal Enhancement Ratio (SER) color maps, and generates summary PDF/DICOM/text reports.
- **gpt**: This extension loads breast DCE-MRI exams, selects contrast phases, and computes functional tumor volume within a user-defined region. It is intended for breast imaging researchers and produces segmentation overlays and reports.

## Disagreements (start here)

### D1. Mixed compressed series deletes original files without checking compression
single; category safety; raised by gpt; outcome after cross-examination: **real, blocking (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/gzip_gunzip_pyfuncs.py:165`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/gzip_gunzip_pyfuncs.py#L165): During phase selection for a mixed compressed/uncompressed DCE folder, this deletes each original uncompressed file even if 7-Zip fails, for example because of an invalid executable or a path containing spaces. The input exam can therefore lose its only copy of DICOM images or other files.
  ```
              for f_i in files:
                  if('.gz' not in f_i):
                      fullfile = os.path.join(dcegzipped_paths[0],f_i)
                      gzcmd = gzcmd_base + fullfile + '.gz' + ' ' + fullfile
                      os.system(gzcmd) #create a gzipped copy of the file
                      os.remove(fullfile) #delete the original, non-gzipped copy of the file
  ```
  Suggestion: Never modify source exams; decompress or copy into a private temporary directory, and verify subprocess success before using outputs.
- claude on re-check: **real: yes, major**: DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/gzip_gunzip_pyfuncs.py:163-170 runs os.system(7z a ...) with an unquoted path and a hard-coded C:\Program Files\7-Zip path. It then calls os.remove(fullfile) without checking the return code or that the .gz exists. If 7z is missing (non-Windows) or the path has spaces, the original is deleted. This only happens in the mixed gz/non-gz case, but it is real data loss on the user's exam files. Because it needs 7z to fail and the folder to be mixed, I rate it major rather than blocking.
- gpt on re-check: **real: yes, blocking**: DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/gzip_gunzip_pyfuncs.py:145-170 selects the mixed/unrecognized-file branch and executes `os.system(gzcmd) #create a gzipped copy of the file` followed immediately by `os.remove(fullfile) #delete the original, non-gzipped copy of the file`, without checking the result. chooseEarly_LateByManufacturer.py:70-76 calls this for a gunzipped exam. If the destination exists and compression fails, original files can be lost. Note extractGZ first checks a different, apparently mistyped 7-Zip directory (gzip_gunzip_pyfuncs.py:30-33), which can impede the usual route; the destructive path remains reachable when its prerequisites are satisfied.
- gemini on re-check: **real: yes, blocking**: In both `DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/gzip_gunzip_pyfuncs.py` (lines 163-170) and `DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py` (lines 163-170), `gunzipAllFilesDCE` enters the mixed branch whenever a DCE series directory contains any file that does not match `.gz`, `.dcm`, `.DCM`, or `isdigit()` (e.g. `.DS_Store` or `Thumbs.db`), or contains both `.gz` and uncompressed files. It then runs `os.system(gzcmd)` with unquoted paths and hard-coded `C:\Program Files\7-Zip\7z` and immediately calls `os.remove(fullfile)` without checking the return code or verifying that `fullfile + '.gz'` was created. If 7-Zip is not installed, on non-Windows platforms, or if the path contains spaces, this permanently deletes the user's original DICOM files.

### D2. Report filename is interpolated into a shell command
single; category safety; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:788`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py#L788): The JPEG and DICOM paths are derived from the path chosen in the report save dialog. Shell metacharacters in a chosen or externally supplied path can execute arbitrary commands, and spaces also break normal paths. The gzip helpers similarly concatenate exam paths into shell commands.
  ```
      #save as dicom too
      command = "img2dcm" + " " + savenamejpeg + " " + savenamedcm #use img2dcm to create dicom report from jpeg
      os.system(command)
  ```
  Suggestion: Invoke the executable with subprocess and an argument list without a shell, and handle failures explicitly.
- claude on re-check: **real: yes, minor**: DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:789-790 builds the img2dcm command by string concatenation and runs it with os.system. The path comes from the user's own save dialog (lines 434-438), so there is no outside attacker, only self-inflicted injection or breakage with spaces. It is poor practice (subprocess with an argument list would fix it) but not a concrete path to harm.
- gpt on re-check: **real: yes, blocking**: DCE_TumorMapProcess/DCE_TumorMapProcess.py:2575-2583 passes the save-dialog result to createPDFreport. DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:433-435 derives the JPEG and DICOM paths, and lines 789-790 execute `command = "img2dcm" + " " + savenamejpeg + " " + savenamedcm` and `os.system(command)`. An attacker-controlled selected path containing shell syntax can execute commands; ordinary spaces can break the conversion. It requires a suitable path reaching report generation, not merely opening the module.
- gemini on re-check: **real: yes, major**: In `DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:788-790`, `command = "img2dcm" + " " + savenamejpeg + " " + savenamedcm` and `os.system(command)` passes unquoted file paths derived from `qt.QFileDialog.getSaveFileName` (and defaulting to `exampath/SlicerReports/...`) to the system shell. Similarly, `gzip_gunzip_pyfuncs.py` (lines 79-86, 98-99, 154-155, 168-169, 174-175) concatenates unquoted paths into `os.system()`. While the paths come from user-selected local folders/dialogs rather than untrusted remote input (making arbitrary command injection mainly a self-inflicted or crafted-folder-name risk, and breaking paths with spaces), passing unquoted paths to `os.system` instead of `subprocess.run([..., path])` or Python's built-in `gzip` module is a real defect.

### D3. Report generation deletes any existing gunzipped directory
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py:108`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py#L108): Module 2 calls this unconditionally after generating a report, including for uncompressed exams. Any pre-existing directory named gunzipped under the selected exam, including user-owned data never created by this extension, is recursively deleted without confirmation.
  ```
  def deleteGunzipped(exampath):
      #Edit 7/16/2020: If there is a gunzipped folder inside the exampath, delete it
      gunzip_path = os.path.join(exampath,"gunzipped")
  
      if(os.path.isdir(gunzip_path) == 1):
          shutil.rmtree(gunzip_path)
  ```
  Suggestion: Use a uniquely created temporary directory and only delete directories owned by the current run; never recursively delete a pre-existing exam folder.
- claude on re-check: **real: yes, minor**: gzip_gunzip_pyfuncs.py:108-113 does rmtree on exampath/gunzipped if that directory exists. That name is the extension's own temporary directory, created at lines 126-127. Deleting a user's pre-existing folder of the same name is unlikely, and the call at DCE_TumorMapProcess.py:2586 is cleanup. A minor risk.
- gpt on re-check: **real: yes, blocking**: DCE_TumorMapProcess/DCE_TumorMapProcess.py:2583-2586 calls `gzip_gunzip_pyfuncs.deleteGunzipped(exampath)` after the report function returns, independently of gzipped status. DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py:110-113 sets `gunzip_path = os.path.join(exampath,"gunzipped")` and calls `shutil.rmtree(gunzip_path)` whenever it is a directory. A pre-existing user-owned directory at that location can be deleted recursively without a provenance check or confirmation.
- gemini on re-check: **real: yes, minor**: In `DCE_TumorMapProcess/DCE_TumorMapProcess.py:2586`, `gzip_gunzip_pyfuncs.deleteGunzipped(exampath)` is called unconditionally after report generation (regardless of whether `gzipped == 1`), and `deleteGunzipped` in `DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py:108-115` calls `shutil.rmtree(os.path.join(exampath, "gunzipped"))`. Note that in `DCE_IDandPhaseSelect`, `extractGZ` (line 30) checks `os.path.isdir(r'C:\Program Fileszz\7-Zip')` (a typo with `zz`), so `extractGZ` never creates `"gunzipped"` itself, while `deleteGunzipped` still deletes `exampath/gunzipped` if present. Since `"gunzipped"` is the extension's specific working folder name inside `exampath`, accidental collision with unrelated user data is unlikely, making this a minor issue rather than blocking.

### D4. Report sidecars overwrite existing files without confirmation
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:641`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py#L641): The report dialog asks for a PDF path, but the code derives a same-stem .txt path and opens it in truncating mode without checking whether it already exists. It also writes a same-stem JPEG; choosing a new PDF name can silently destroy unrelated existing sidecar files.
  ```
      txt_file = open(savenametxt, "w+")
  
      txt_file.write( "I-SPY ID: " + idstr + "\r\n")
      txt_file.write( "Date: " + studydate[4:6]+"/"+studydate[6:]+"/"+studydate[0:4]+" "+studytime[0:2]+":"+studytime[2:4]+":"+studytime[4:] + "\r\n")
  ```
  Suggestion: Check all output paths before writing and ask for explicit overwrite confirmation, or create a new output directory.
- claude on re-check: **real: yes, minor**: ftv_plots.py:434-438 derives the .jpeg, .dcm and .txt names from the PDF name chosen in the dialog, and line 641 opens the .txt in 'w+' mode. There is no existence check on the sidecar files. The user picks the stem and the sidecars are report outputs, so overwriting is possible but unlikely. A minor issue.
- gpt on re-check: **real: yes, blocking**: DCE_TumorMapProcess/DCE_TumorMapProcess.py:2575-2583 prompts for a PDF and passes the path to the report. DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:433-438 derives same-stem names, and line 641 executes `txt_file = open(savenametxt, "w+")`, truncating an existing text file without checking it. Line 785 similarly saves the JPEG. Confirming the PDF path does not confirm overwriting unrelated sidecars; this is a concrete data-loss path.
- gemini on re-check: **real: yes, minor**: In `DCE_TumorMapProcess/DCE_TumorMapProcess.py:2566-2578`, the user selects a `.pdf` save path (defaulting to `exampath/SlicerReports/<site>_<id>_<visit>.pdf`), and `DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:434-438, 641, 785-790` derives `.jpeg`, `.dcm`, and `.txt` paths by replacing the last 3 characters (`savenamepdf[:-3] + ...`) and writes them without checking if the sidecar files already exist. Because the user explicitly chose the base report path in a save dialog (by default in a dedicated `SlicerReports` subdirectory), writing companion report files with the same stem is expected behavior for this report generator, though using `os.path.splitext` and documenting/confirming sidecar overwrites would be cleaner.

### D5. Top-level pip installation at module import time and non-headless OpenCV dependency
single; category environment; raised by gemini; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (blocking, high confidence, quote verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:58`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L58): Both `DCE_IDandPhaseSelect.py` (lines 54-58) and `DCE_TumorMapProcess.py` (lines 83-89) execute `_pipEnsure` / `slicer.util.pip_install` at module top-level import time (when 3D Slicer starts up and discovers scripted modules, even if the user never opens the module) without user confirmation. Furthermore, `DCE_TumorMapProcess.py` line 84 calls `_importOptional('cv2', 'cv2')` (there is no valid PyPI package named `cv2`, and `pyproject.toml` lists `opencv-python` instead of `opencv-python-headless`, which bundles duplicate Qt libraries that conflict with Slicer's Qt).
  ```
  def _importOptional(package, moduleName=None):
    moduleName = moduleName or package
    try:
      return __import__(moduleName)
    except ImportError:
      _pipEnsure(package)
  ```
  Suggestion: Move optional package imports and `pip_install` calls inside the widget `setup()` or logic `run()` methods after prompting the user for confirmation, and install `opencv-python-headless` rather than `cv2` or `opencv-python`.
- claude on re-check: **real: yes, major**: DCE_IDandPhaseSelect.py:54-58 and DCE_TumorMapProcess.py:83-89 run at module level and call pip_install via _pipEnsure whenever an import fails. The install happens at Slicer startup or module discovery, with no confirmation. _importOptional('cv2','cv2') passes 'cv2' to pip, which is the wrong distribution name (opencv-python). pyproject.toml:8 lists opencv-python, not the headless variant. This only triggers when the packages are missing, and it is the install-at-import pattern the policy asks to change. It is not malicious, so major rather than blocking.
- gpt on re-check: **real: yes, blocking**: DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py:42-58 and DCE_TumorMapProcess/DCE_TumorMapProcess.py:46-64,83-89 contain top-level import-time dependency installation on failed imports; the fallback calls `slicer.util.pip_install(package)` without a local prompt. TumorMapProcess.py:84 calls `cv2 = _importOptional('cv2', 'cv2')`, using the import name rather than the OpenCV distribution, so a missing cv2 can prevent loading. pyproject.toml:6-9 declares `"opencv-python",` rather than the headless distribution. I did not verify that this project metadata is actually installed by the Slicer build, nor the internal consent behavior of slicer.packaging.pip_ensure; the direct pip fallback is demonstrable.
- gemini on re-check: **real: yes, blocking**: In `DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py:54-58` and `DCE_TumorMapProcess/DCE_TumorMapProcess.py:58-64, 83-89`, missing dependencies trigger `_pipEnsure` -> `slicer.util.pip_install(...)` at module top-level import time (during Slicer startup/module discovery, before the user ever opens the module and without confirmation). Furthermore, `DCE_TumorMapProcess.py:84` calls `_importOptional('cv2', 'cv2')`, attempting to `pip install cv2` (which does not exist on PyPI as a valid distribution name for OpenCV), and `pyproject.toml:8` specifies `opencv-python` instead of `opencv-python-headless`, which bundles duplicate Qt libraries that conflict with Slicer's Qt environment. Under the Slicer Extensions Index review policy, installing packages at module import/Slicer startup and specifying `opencv-python` instead of `opencv-python-headless` are blocking environment issues.

### D6. Unquoted os.system calls and unconditional deletion of original user DICOM files in gunzipAllFilesDCE
single; category safety; raised by gemini; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (blocking, high confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py:163`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py#L163): In `gzip_gunzip_pyfuncs.py` (present in both modules), `extractGZ` and `gunzipAllFilesDCE` construct shell commands by concatenating unescaped file paths and executing them with `os.system(...)`. If paths or filenames contain spaces or shell metacharacters, `os.system` will fail or execute unintended commands. In addition, lines 165-170 run `os.system(gzcmd)` and then unconditionally call `os.remove(fullfile)` on the user's original uncompressed DICOM files without checking whether `7z` succeeded, which permanently deletes user exam data if `7z` is missing or fails.
  ```
              gzcmd_base = r'"C:\Program Files\7-Zip\7z" a -tgzip '
              #Edit 2/4/2021: if file is not gzipped, gzip it and delete the original copy
              for f_i in files:
                  if('.gz' not in f_i):
                      fullfile = os.path.join(dcegzipped_paths[0],f_i)
                      gzcmd = gzcmd_base + fullfile + '.gz' + ' ' + fullfile
  ```
  Suggestion: Use Python's built-in `gzip` and `shutil` standard library modules to decompress `.gz` files directly into a temporary directory instead of invoking external `7z` via `os.system`, and never delete original files in the user's source exam directory.
- claude on re-check: **real: yes, major**: The 7z calls are unquoted os.system calls and the deletion is unchecked (gzip_gunzip_pyfuncs.py:153-175). It duplicates D1, with the same major-severity data-loss path in the mixed-series case. The command-injection part is limited because the paths are the user's own exam paths.
- gpt on re-check: **real: yes, blocking**: DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py:74-80 and 163-170 concatenate paths into shell commands; lines 169-170 run `os.system(gzcmd) #create a gzipped copy of the file` then `os.remove(fullfile) #delete the original, non-gzipped copy of the file` regardless of exit status. The corresponding plugin1 copy at the same lines is actually called by DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/chooseEarly_LateByManufacturer.py:70-76. This duplicates D1's original-file loss and adds shell injection; entry into that branch requires a prepared destination and the mixed or unrecognized-file case. The extractGZ prerequisite at plugin1/gzip_gunzip_pyfuncs.py:30-33 may impede the ordinary path.
- gemini on re-check: **real: yes, blocking**: In both `DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/gzip_gunzip_pyfuncs.py:163-175` and `DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py:163-175`, `gunzipAllFilesDCE` builds shell commands by string concatenation without quoting file paths and runs them via `os.system(gzcmd)`, then unconditionally deletes the user's original uncompressed file via `os.remove(fullfile)` on line 170 without checking if `7z` succeeded or if `fullfile + '.gz'` exists. If `C:\Program Files\7-Zip\7z` is missing, if running on macOS/Linux, or if `fullfile` contains spaces, `os.system(gzcmd)` fails and `os.remove(fullfile)` permanently destroys the user's original exam files.

### D7. Dependencies are installed on module import and cv2 uses the wrong distribution name
single; category environment; raised by gpt; outcome after cross-examination: **real, blocking (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:83`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L83): The helper calls pip when an import fails, so module discovery can change the shared environment before the user opens the extension. In particular cv2 is an import name, not the OpenCV distribution name, so a missing cv2 can cause module loading to fail; pyproject.toml instead declares opencv-python, which bundles Qt rather than the headless variant.
  ```
  nib = _importOptional('nibabel')
  cv2 = _importOptional('cv2', 'cv2')
  nrrd = _importOptional('pynrrd', 'nrrd')
  yattag = _importOptional('yattag')
  matplotlib = _importOptional('matplotlib')
  import matplotlib.pyplot as plt
  ```
  Suggestion: Move dependency setup to a user-confirmed module action; use an appropriate Slicer-compatible headless OpenCV distribution and check requirements before proceeding.
- claude on re-check: **real: yes, major**: DCE_TumorMapProcess.py:83-89 calls _importOptional at import time. 'cv2' is passed as the pip package name, which is wrong (opencv-python is the distribution), so the pip install fails and the module fails to load. pyproject.toml:8 lists opencv-python (non-headless), which bundles its own Qt libraries. The pip installs happen at module discovery without consent. This is a real environment concern; I rate it major.
- gpt on re-check: **real: yes, blocking**: DCE_TumorMapProcess/DCE_TumorMapProcess.py:58-64 calls `_pipEnsure(package)` on ImportError, and lines 83-89 perform those imports at module scope, including `cv2 = _importOptional('cv2', 'cv2')`. The direct fallback at lines 52-56 calls pip without an explicit confirmation. A missing cv2 can cause module loading to fail because cv2 is the import name, not the OpenCV distribution. pyproject.toml:8 declares `"opencv-python",`; I did not establish that this metadata is installed during normal extension operation. This duplicates D5.
- gemini on re-check: **real: yes, blocking**: This is the same underlying issue as D5: `DCE_TumorMapProcess/DCE_TumorMapProcess.py:83-89` (and `DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py:54-58`) runs `pip_install` at top-level module import time during Slicer startup, uses `'cv2'` as the pip package name in `_importOptional('cv2', 'cv2')` (causing installation and module loading to fail when `cv2` is not already installed), and declares `opencv-python` (which bundles conflicting Qt libraries) instead of `opencv-python-headless` in `pyproject.toml:8`. Under the review policy, package installation at module import/startup and `opencv-python` (non-headless) / broken module loading are blocking issues.


## Findings from some reviewers

### Blocking file dialog and unguarded state assumptions in Widget setup()
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py:294`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py#L294): `DCE_IDandPhaseSelectWidget.setup()` immediately opens a modal `QFileDialog.getExistingDirectory` when the widget is initialized and proceeds to index paths and read files assuming a valid directory was chosen. Similarly, `DCE_TumorMapProcessWidget.setup()` immediately calls `slicer.util.getNode("path node")` (line 240) and loads `current_exam_workspace.pickle` (line 269) inside `setup()`, which raises an unhandled exception if Module 2 is opened before Module 1 has been run.
  ```
      #Edit 2/11/2021: Moving exampath selection here
      self.exampath = qt.QFileDialog.getExistingDirectory(0,("Select folder for DCE-MRI exam"))
  ```
  Suggestion: Trigger directory selection via a UI button or `ctkPathLineEdit` rather than a blocking dialog inside `setup()`, and guard against missing `"path node"` or workspace state when `DCE_TumorMapProcessWidget.setup()` runs.

### Case-sensitive filename mismatch for ser_colorbar.PNG
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:932`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L932): The repository and `DCE_TumorMapProcess/CMakeLists.txt` (line 23) install `ser_colorbar.PNG` with an uppercase extension, whereas `DCE_TumorMapProcess.py` looks for `ser_colorbar.png` in lowercase. On case-sensitive filesystems (such as Linux), loading the pixmap fails.
  ```
      pathtoscript,scriptname = os.path.split(os.path.realpath(__file__))
      colorbar_path = os.path.join(pathtoscript,'ser_colorbar.png')
  ```
  Suggestion: Match the exact filename casing (`ser_colorbar.PNG`) or rename the file to lowercase in both the repository and `CMakeLists.txt`.

### Persistent modification of global DataProbe slice view annotation settings
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:230`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L230): When opening `DCE_TumorMapProcess`, `setup()` writes to `qt.QSettings()` to persistently disable Slicer's DataProbe slice view annotations across all future Slicer sessions, affecting the user's global Slicer configuration even after closing the module.
  ```
      # Disable slice annotations immediately
      slicer.modules.DataProbeInstance.infoWidget.sliceAnnotations.sliceViewAnnotationsEnabled=False
      slicer.modules.DataProbeInstance.infoWidget.sliceAnnotations.updateSliceViewFromGUI()
      # Disable slice annotations persistently (after Slicer restarts)
      settings = qt.QSettings()
      settings.setValue('DataProbe/sliceViewAnnotations.enabled', 0)
  ```
  Suggestion: Avoid modifying persistent global `QSettings` for `DataProbe/sliceViewAnnotations.enabled`, or restore the user's previous setting in `cleanup()`.

### ROI coordinates outside image bounds are not clipped
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_map_gen.py:89`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_map_gen.py#L89): When the ROI crosses an image boundary, negative NumPy slice bounds wrap from the far edge and may produce an empty or incorrect mask; excessive positive limits are also used later by explicit colorization loops. FTV computation can fail or omit portions of the selected lesion.
  ```
        zs = int( round( float(center[2]) - float(radius[2]) ) )
        zf = int( round( float(center[2]) + float(radius[2]) ) )
  
        #because it's a numpy array, it must have dimension order z,y,x in order to match orientations with input image
        #4/27/21: Add the +1 to each dimension to compensate for
        #Python array indexing rules
  ```
  Suggestion: Clip all ROI and omit bounds to image dimensions and reject empty intersections before calculating thresholds or coloring voxels.

### Registered module test calls an undefined test method
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:2619`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L2619): The registered module test calls test_roiAndOmitsTest1, but the defined test shown immediately below has a different name. Consequently the self-test cannot exercise the workflow as intended.
  ```
    def runTest(self):
      """Run as few or as many tests as needed here.
      """
      self.setUp()
      self.test_roiAndOmitsTest1()
  
  ```
  Suggestion: Replace the template test with working automated tests for phase selection, ROI boundaries, and report generation.

### Workspace is stored in a shared fixed file next to installed code
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py:143`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py#L143): An installation directory may be read-only, preventing module 1 from completing. Concurrent sessions also overwrite the same file, while module 2 unpickles it, potentially associating one session's exam metadata with another session's images.
  ```
    #Save workspace for original exam selected by user
    if(orig == 1):
      #7/9/2021: Make this path part independent of computer & directory
      #code is stored in.
      extension_path = os.path.join( os.path.dirname( __file__ ), '..' )
      wkspc_savepath = os.path.join(extension_path,'current_exam_workspace.pickle')
  ```
  Suggestion: Keep the state in the MRML scene or a uniquely scoped, access-controlled temporary location, and avoid pickle for cross-session data.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I read the CMake files, the Module 2 main file, the first third of the Module 1 main file and the gzip helper. I found no sign of malicious behaviour, network exfiltration or text aimed at reviewers. The main concerns are environment related. Both modules pip-install packages at import time with no confirmation. These include opencv-python (non-headless, the catalog's Qt/VTK concern), scikit-image and matplotlib. Module 1 also imports distutils, which is gone in Python 3.12. The code uses hardcoded Windows 7-Zip paths with os.system. It also writes a pickle into the extension install directory and rmtree's a folder in the user's exam directory. The catalog entry tracks the moving `master` branch, and there are no automated tests. License is the Slicer BSD-style text plus a copyright notice.
Not checked: 
<parameter name="__placeholder__">

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
Breast_DCEMRI_FTV provides a well-documented workflow for computing functional tumor volume (FTV) from breast DCE-MRI exams. However, there are two blocking issues that should be resolved:
1. Both modules run `pip_install` at top-level module import time (during Slicer startup) without user confirmation, and request `cv2` / `opencv-python` instead of `opencv-python-headless`.
2. `gzip_gunzip_pyfuncs.py` runs unquoted `os.system` commands calling `C:\Program Files\7-Zip\7z` and unconditionally deletes original user DICOM files (`os.remove(fullfile)`) without checking if `7z` succeeded.

🔴 Do not merge yet: please move package installation out of top-level imports (and use `opencv-python-headless`), and replace the `os.system` / `os.remove` logic in `gzip_gunzip_pyfuncs.py` with safe standard-library `gzip` handling.
Not checked: StepByStepInstructionsForSlicerFTV_12_14_2022_FINAL_Rdcd.pdf (13 MB binary PDF file not inspected)
Questions for the author: Could you replace the external `7z` `os.system` calls in `gzip_gunzip_pyfuncs.py` with Python's built-in `gzip` module so that decompression works cross-platform without risking deletion of original exam files?; Could you move the runtime `pip_install` / `_pipEnsure` calls out of top-level module import into module execution (with user consent) and replace `cv2` / `opencv-python` with `opencv-python-headless`?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The examined source has blocking data-loss and command-injection paths, as well as unsolicited dependency installation at import. The FTV calculation and workspace handling also have non-blocking robustness problems. The README identifies the Slicer license, and CMake lists the plugin files, but the catalog’s moving revision and the supplied commit could not be independently resolved. 🔴 Do not merge yet: fix the data-loss and injection paths and validate the selected revision.
Not checked: No code was executed; Slicer loading, packaging, and platform behavior were not tested.; Network access was unavailable: the repository URL, master branch target, claimed commit 271ece80ce3db9cc79596ee5436dd5d44ed1a50c, and any prior review baseline were not independently verified.; The large linked tutorial PDF and binary image assets were not inspected; third-party asset provenance was not established.; The full image processing algorithm and every manufacturer-specific path were not exhaustively audited; external packages and their transitive licenses were not inspected.; No submission checklist or CI results were provided.


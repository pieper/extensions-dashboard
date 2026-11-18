# AI review: Breast_DCEMRI_FTV

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV at commit `271ece80ce3db9cc79596ee5436dd5d44ed1a50c`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-18T03:20:02Z; cost $0.11

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | concern |
| environment | blocking | minor | concern |
| packaging | minor | ok | minor |
| license | ok | ok | minor |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A two-module 3D Slicer extension for the UCSF Breast Imaging Research Group that loads the pre-, early- and late-contrast phases of a bilateral axial breast DCE-MRI exam and computes functional tumor volume (FTV) from a user-drawn ROI, with an SER-colourised report. It targets breast-MRI researchers and I-SPY-style trial sites.
- **flash-lite**: Provides two 3D Slicer modules to compute Functional Tumor Volume (FTV) from breast DCE-MRI exams.
- **haiku**: Two Slicer scripted modules (FTV Segmentation category) that load pre, early and late post-contrast breast DCE-MRI phases and compute functional tumor volume (FTV) with SER/PE maps, an ROI/omit-region editor, and a PDF/DICOM report. Intended for research users of bilateral axial breast MR exams.

## Disagreements (start here)

### D1. pip installs executed at module import (Slicer startup)
partial; category environment; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:83`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L83): Slicer imports every installed scripted module file at startup to register it, so these module-level calls run pip_ensure/pip_install for nibabel, opencv, pynrrd, yattag, matplotlib and scikit-image for every user who has the extension installed, even if they never open the module, and without asking. DCE_IDandPhaseSelect.py lines 54-58 does the same for nibabel. This mutates Slicer's shared Python environment silently and can break other extensions.
  ```
  nib = _importOptional('nibabel')
  cv2 = _importOptional('cv2', 'cv2')
  nrrd = _importOptional('pynrrd', 'nrrd')
  yattag = _importOptional('yattag')
  matplotlib = _importOptional('matplotlib')
  ```
  Suggestion: Move the imports inside the functions that need them and ask the user for confirmation before installing anything; declare the dependencies in the extension metadata instead.
- **haiku** (major, high confidence, quote verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:83`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L83): These run whenever the module file is loaded, so a missing package triggers slicer.util.pip_install without user confirmation, even for users who never open the module. For cv2 the pip target is 'cv2' (the import name), not the OpenCV distribution; the pip package named cv2 is not the OpenCV project. pyproject.toml asks for 'opencv-python', which bundles its own Qt and conflicts with Slicer's Qt, rather than 'opencv-python-headless'. The same pattern appears in DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py lines 54-57 for nibabel.
  ```
  nib = _importOptional('nibabel')
  cv2 = _importOptional('cv2', 'cv2')
  nrrd = _importOptional('pynrrd', 'nrrd')
  yattag = _importOptional('yattag')
  ```
  Suggestion: Move imports into the functions that need them and ask the user before installing. Use the PyPI name opencv-python-headless (import name cv2). Declare the extra dependencies in the extension, not in pyproject.toml, and avoid installing at startup.

### D2. Module 2 cannot be opened unless module 1 was run first
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:240`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L240): setup() immediately looks up the 'path node' created by module 1 and then unpickles the workspace file (lines 267-270). If the user opens module 2 first, or after restarting Slicer, slicer.util.getNode raises and the module widget fails to build, leaving a broken panel with no explanation.
  ```
  exampath_node = slicer.util.getNode("path node")
  #2. Read exampath from current node in pathSelector
  self.exampath = exampath_node.GetParameter("exampath")
  ```
  Suggestion: Check for the node/file and show a clear message ('run Module 1 first') instead of raising.

### D3. Original DICOMs deleted from the user's exam folder without verification
single; category safety; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py:168`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py#L168): In the mixed gzipped/non-gzipped branch, each original DICOM in the user's exam directory is gzipped with a hardcoded 7-Zip path and then unconditionally deleted. If 7-Zip is missing or the command fails (the path is hardcoded to 'C:\Program Files\7-Zip\7z', and line 30 even contains the typo 'C:\Program Fileszz\7-Zip'), the original image is removed with no copy left - permanent loss of source medical images. I found no call site for gunzipAllFilesDCE in the files I read, so this may currently be dead code, but it is shipped and reachable.
  ```
  gzcmd = gzcmd_base + fullfile + '.gz' + ' ' + fullfile
  os.system(gzcmd) #create a gzipped copy of the file
  os.remove(fullfile) #delete the original, non-gzipped copy of the file
  ```
  Suggestion: Never delete source DICOMs; write decompressed copies to a separate output folder and verify success before any removal, or remove this function.

### D4. Persistent global change to Slicer's DataProbe settings
single; category environment; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:231`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L231): Opening module 2 permanently disables the DataProbe slice annotations in the user's Slicer settings. This survives restarts and affects every other module and workflow, including for users who only tried this extension once.
  ```
  slicer.modules.DataProbeInstance.infoWidget.sliceAnnotations.sliceViewAnnotationsEnabled=False
  slicer.modules.DataProbeInstance.infoWidget.sliceAnnotations.updateSliceViewFromGUI()
  # Disable slice annotations persistently (after Slicer restarts)
  settings = qt.QSettings()
  settings.setValue('DataProbe/sliceViewAnnotations.enabled', 0)
  ```
  Suggestion: Do not write global QSettings; if the annotations must be hidden, restore the previous value in cleanup().

### D5. Shell commands built from user-controlled folder names and run with os.system
single; category safety; raised by deepseek
- **deepseek** (major, high confidence, quote partly verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py:74`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py#L74): extractGZ() is called from module 1 (DCE_IDandPhaseSelect.py lines 655 and 766) on the exam folder the user selected. Folder and file names from that directory are concatenated into a command string without quoting and passed to os.system, so a DICOM folder or file named with a shell metacharacter (e.g. '1 & calc', '"; ...') executes arbitrary commands with the user's privileges. This is reachable with any downloaded or shared DICOM dataset whose folder names are not sanitised. The same pattern is repeated at lines 153-175.
  ```
  cmd_base = r'"C:\Program Files\7-Zip\7z" x '
  cmd1_7z = cmd_base + str(os.path.join(curr_path,file1)) + ' -o' + new_path   #command for file 1 uncompressed
  os.system(cmd1_7z) #execute above command
  ```
  Suggestion: Use subprocess.run with an argument list (no shell), or better, decompress with Python's gzip module instead of shelling out to 7-Zip.

### D6. Windows-only 7-Zip shell commands built from unquoted paths; return codes ignored
single; category soundness; raised by haiku
- **haiku** (major, medium confidence, quote partly verified) [`DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/gzip_gunzip_pyfuncs.py:74`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/gzip_gunzip_pyfuncs.py#L74): The 7-Zip path is hard-coded, so on machines without 7-Zip at that location (and on macOS, which the README says works) gunzip silently fails and the module loads no images. Exam and output paths are concatenated without quotes, so folder names with spaces or shell metacharacters break or inject commands. The same pattern is in DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py lines 74-80 and 153-175. gzip_gunzip_pyfuncs.py line 30 also has a 'C:\Program Fileszz\7-Zip' path that looks like a typo.
  ```
  cmd_base = r'"C:\Program Files\7-Zip\7z" x '
   cmd1_7z = cmd_base + str(os.path.join(curr_path,file1)) + ' -o' + new_path   #command for file 1 uncompressed
   os.system(cmd1_7z) #execute above command
  ```
  Suggestion: Use Python's gzip module (no external tool) to decompress the DICOM files. If 7-Zip must stay, use subprocess with an argument list, check the exit code, and show a clear error when 7-Zip is missing.

### D7. opencv-python (non-headless) declared as a dependency
partial; category environment; raised by deepseek, flash-lite
- **deepseek** (major, high confidence, quote verified) [`pyproject.toml:6`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/pyproject.toml#L6): opencv-python bundles its own Qt libraries, which conflicts with the Qt that Slicer ships and can crash or destabilise the application for all modules. The extension only uses cv2.imread/cvtColor (ftv_plots.py lines 46-48), which opencv-python-headless provides.
  ```
  dependencies = [
      "nibabel",
      "opencv-python",
  ```
  Suggestion: Use opencv-python-headless, or avoid cv2 entirely (matplotlib.image / PIL are already available).
- **flash-lite** (minor, high confidence, quote quote not found) [`pyproject.toml:7`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/pyproject.toml#L7): opencv-python bundles its own GUI/Qt libraries which can conflict with Slicer's bundled Qt libraries. Extensions should use opencv-python-headless instead.
  ```
  pyproject.toml
  8:     "opencv-python",
  ```
  Suggestion: Change opencv-python to opencv-python-headless in pyproject.toml.

### D8. os.system with user-chosen report filename (img2dcm)
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:789`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py#L789): savenamejpeg derives from the path the user picked in qt.QFileDialog.getSaveFileName (DCE_TumorMapProcess.py line 2576). A save name containing shell metacharacters is executed as a shell command. In addition img2dcm is not bundled with Slicer or the extension, so on typical installs this silently produces no DICOM report and the user gets no error.
  ```
  command = "img2dcm" + " " + savenamejpeg + " " + savenamedcm #use img2dcm to create dicom report from jpeg
  os.system(command)
  ```
  Suggestion: Use subprocess.run([...]) with a list, check the return code, and report failure to the user (or drop the DICOM export).
- **haiku** (major, medium confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:789`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py#L789): savenamejpeg derives from the path the user types in the Qt save dialog (DCE_TumorMapProcess.py 2576-2583). The string is passed to the shell unquoted. A filename with spaces breaks the command, and shell metacharacters such as & or | in the filename run extra commands. The return value is also ignored, so a failed DICOM conversion goes unreported.
  ```
  command = "img2dcm" + " " + savenamejpeg + " " + savenamedcm #use img2dcm to create dicom report from jpeg
  os.system(command)
  ```
  Suggestion: Call the converter with subprocess.run([...], check=True) using an argument list, or do the DICOM conversion in Python (for example pydicom/pydicom-based writer). Report failures to the user.

### D9. progressBar used outside the branch that creates it
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py:138`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py#L138): progressBar is only created when at least one DCE folder was identified, but it is dereferenced unconditionally a few lines later (line 153, 'progressBar.value = 25'). When automatic DCE identification finds nothing, the user gets a NameError traceback instead of an actionable error message, and the progress dialog is never closed on the success path either.
  ```
  if(len(dce_folders) > 0):
    progbarttl = "Visit: " + nodevisstr
    progressBar = slicer.util.createProgressDialog(windowTitle = progbarttl)
  ```
  Suggestion: Create the dialog unconditionally (or guard every use) and close it in a finally block; report 'no DCE series found' to the user.

### D10. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D11. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite minor, haiku concern

### D12. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Deletes any 'gunzipped' folder inside the user-selected exam folder
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py:110`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py#L110): After a report is written, deleteGunzipped removes exampath/gunzipped recursively. If the exam folder already contains a user-owned folder named 'gunzipped' with data, that data is deleted. The extension only creates this folder itself when the DICOMs are gzipped, so the risk is limited to unusual folder layouts.
  ```
  gunzip_path = os.path.join(exampath,"gunzipped")
  
      if(os.path.isdir(gunzip_path) == 1):
          shutil.rmtree(gunzip_path)
  ```

### Extension metadata URLs point to a different repository than scm_url
minor; packaging; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`CMakeLists.txt:7`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/CMakeLists.txt#L7): The catalog entry points at https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV, while homepage, icon and screenshot URLs point at rnadkarni2/SlicerBreast_DCEMRI_FTV. If the old repository is deleted or diverges, the Extension Manager shows broken icons/screenshots and users are sent to the wrong project.
  ```
  set(EXTENSION_HOMEPAGE "https://github.com/rnadkarni2/SlicerBreast_DCEMRI_FTV")
  ```
  Suggestion: Point EXTENSION_HOMEPAGE/ICONURL/SCREENSHOTURLS at the radiology-research repository.
- **haiku** (minor, high confidence, quote verified) [`CMakeLists.txt:7`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/CMakeLists.txt#L7): The catalog entry's scm_url is radiology-research/SlicerBreast_DCEMRI_FTV, but the extension metadata, icon and screenshot URLs use rnadkarni2. Users may land on a different repository, and the index shows a mismatched homepage. The catalog entry is usable as written; this is a metadata issue.
  ```
  set(EXTENSION_HOMEPAGE "https://github.com/rnadkarni2/SlicerBreast_DCEMRI_FTV")
  ```

### File dialog opened during widget setup and blocking sleep on the GUI thread
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py:295`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py#L295): A modal folder dialog is opened as soon as the module widget is constructed, so merely selecting the module in the module list pops a dialog and the rest of setup() runs against whatever the user picked (or an empty string). Combined with time.sleep(1) at line 239 and the long DICOM loading done on the GUI thread with processEvents, the UI is unresponsive during processing.
  ```
  self.exampath = qt.QFileDialog.getExistingDirectory(0,("Select folder for DCE-MRI exam"))
  ```
  Suggestion: Move folder selection to a button, and run the loading in a CLI logic call with a proper progress dialog.

### Module test code is disabled and the in-module test downloads external data
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`DCE_IDandPhaseSelect/Testing/Python/CMakeLists.txt:2`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_IDandPhaseSelect/Testing/Python/CMakeLists.txt#L2): The CTest registration for the module tests is commented out. The unittest class in DCE_IDandPhaseSelect.py (lines 822-866) only downloads 'FA.nrrd' from slicer.kitware.com and asserts nothing. There are no tests of the DICOM-parsing or FTV computation logic, so regressions are not caught.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```

### Module test downloads sample data and does not test the module
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py:857`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py#L857): The only test is the Slicer template test: it downloads an unrelated FA volume over plain HTTP and asserts nothing about the extension, so it cannot catch regressions in the DCE loading or FTV logic. The Testing/Python/CMakeLists.txt files have their unittest lines commented out.
  ```
  SampleData.downloadFromURL(
    nodeNames='FA',
    fileNames='FA.nrrd',
    uris='http://slicer.kitware.com/midas3/download?items=5767')
  ```
  Suggestion: Add a test that exercises the logic with a small anonymised DICOM series or synthetic volume.

### Runtime pip dependencies are not declared where the build can see them
minor; packaging; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`pyproject.toml:2`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/pyproject.toml#L2): The Slicer extension build does not consume pyproject.toml, and the catalog entry has build_dependencies []. The real dependencies (nibabel, opencv, pynrrd, yattag, scikit-image, matplotlib) are therefore satisfied by silent pip installs at import time rather than by declared requirements, so the packaged extension has no reproducible dependency set.
  ```
  name = "slicer-ext-breast-dcemri-ftv"
  ```
  Suggestion: Declare the dependencies in the extension metadata / documentation and install them with explicit user consent.

### Template help text and no sample data
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py:261`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_IDandPhaseSelect/DCE_IDandPhaseSelect.py#L261): Both modules still show the Slicer template help text and acknowledgement, so the in-application documentation does not describe what the module does; there is also no sample dataset, so a new user cannot try the workflow without their own DICOM exam.
  ```
  self.parent.helpText = """
  This is an example of scripted loadable module bundled in an extension.
  """  # TODO: update with short description of the module
  ```
  Suggestion: Replace the template helpText with the README description and link the step-by-step PDF.

### distutils imported (removed in Python 3.12)
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py:26`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/gzip_gunzip_pyfuncs.py#L26): distutils was removed from the standard library in Python 3.12, which recent Slicer versions use. On such builds importing this plugin module raises ImportError, and because DCE_TumorMapProcess.py imports it at module level (line 101) the whole module fails to load.
  ```
  from distutils.dir_util import copy_tree
  ```
  Suggestion: Use shutil.copytree(dirs_exist_ok=True) instead.
- **haiku** (minor, medium confidence, quote verified) [`DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/gzip_gunzip_pyfuncs.py:25`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_IDandPhaseSelect/Breast_DCEMRI_FTV_plugins1/gzip_gunzip_pyfuncs.py#L25): distutils was removed in Python 3.12. The import fails at module load if the Slicer build moves to that version, which breaks Module 1 entirely. The same import is in the DCE_TumorMapProcess copy.
  ```
  import shutil
  from distutils.dir_util import copy_tree
  ```

### matplotlib backend switched globally during report generation
minor; environment; raised by haiku
- **haiku** (minor, high confidence, quote verified, other lines) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:30`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py#L30): matplotlib.use() changes the process-wide backend. After one report is created, any other Slicer extension or Python console code that uses pyplot with the Qt backend gets the non-interactive Agg backend for the rest of the session.
  ```
  import slicer
       import matplotlib
       matplotlib.use('Agg')
  ```

### pickle.load of a file at a fixed path in the extension install directory
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:268`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L268): Module 1 writes this pickle (DCE_IDandPhaseSelect.py lines 147-150) into the extension installation directory and module 2 unpickles it. Anyone able to write that file gets code execution in Slicer, and on a normal install the extension directory is read-only, so module 1 fails for non-admin users. It also stores patient-identifying exam metadata in the install tree.
  ```
  wkspc_savepath = os.path.join(extension_path,'current_exam_workspace.pickle')
  with open(wkspc_savepath,'rb') as f:
    self.tempres, self.all_folders_info, self.dce_folders, self.dce_ind, self.fsort, self.studydate, self.nslice, self.earlyPostContrastNum, self.latePostContrastNum, self.earlydiffmm, self.earlydiffss, self.latediffmm, self.latediffss = pickle.load(f)
  ```
  Suggestion: Store the workspace in a vtkMRMLScriptedModuleNode parameter node or in the user's temp/settings directory, and use JSON instead of pickle.
- **haiku** (minor, medium confidence, quote partly verified) [`DCE_TumorMapProcess/DCE_TumorMapProcess.py:268`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/DCE_TumorMapProcess.py#L268): The pickle is written by Module 1 into the extension's installation directory (DCE_IDandPhaseSelect.py lines 147-150). Unpickling is arbitrary code execution if the file is replaced by a malicious one. The risk is low (it needs local write access), but the pattern is unsafe and the install directory is often not user-owned.
  ```
  wkspc_savepath = os.path.join(extension_path,'current_exam_workspace.pickle')
       with open(wkspc_savepath,'rb') as f:
         self.tempres, self.all_folders_info, ... = pickle.load(f)
  ```

### Clinical-use disclaimer only appears on the generated report
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py:767`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/DCE_TumorMapProcess/Breast_DCEMRI_FTV_plugins2/ftv_plots.py#L767): The generated report is marked 'NOT FOR DIAGNOSIS', which is good, but the README and module help do not state that the FTV values are research-only and not validated for clinical decision making.
  ```
  txtplot = plt.text(0.1,0.7,'NOT FOR DIAGNOSIS', fontsize = 14)
  ```
  Suggestion: Add a short research-use-only statement to the README and module helpText.

### Large binaries committed to the source repository
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.md:73`](https://github.com/radiology-research/SlicerBreast_DCEMRI_FTV/blob/271ece80ce3db9cc79596ee5436dd5d44ed1a50c/README.md#L73): A 13 MB PDF plus ~2 MB of screenshots are committed. This bloats every clone and the extension package; documentation of this size is normally hosted externally and linked.
  ```
  For complete, step-by-step user instructions on how to use this extension, please read the document <br>
  **[UserInstructionsFor_Breast_DCEMRI_FTV.pdf](StepByStepInstructionsForSlicerFTV_12_14_2022_FINAL_Rdcd.pdf)**, which has been included in this repository.
  ```
  Suggestion: Host the PDF externally (or in a release asset) and link it from the README.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The extension does what it claims (DCE phase selection + FTV segmentation + PDF report) and ships a Slicer BSD license, but it has serious environment and safety problems: six pip packages (including non-headless opencv-python) are installed at module import, i.e. at Slicer startup for users who never open the module; shell commands are built by string concatenation from user-controlled folder/file names and run with os.system; one code path deletes original DICOMs from the user's exam folder; and module 2 cannot be opened unless module 1 was run first. Packaging is mostly consistent (all imported plugin files are installed by CMake). Needs fixes before being offered to users.
Not checked: Most of DCE_TumorMapProcess.py beyond line 730 (the remaining ~1900 lines, including the segmentation/report button handlers) was not read.; Plugin modules not read: Get_header_info_all_manufacturer.py, chooseEarly_LateByManufacturer.py/.new.py, Exam_Ident_and_timing.py/.new.py, timing_info_class_all_manufacturer.py, compute_lps_to_rcs.py (both copies), multivolume_folder_sort.py (both), read_DCE_images_to_numpy.py (both), create2DimgAll; Whether gunzipAllFilesDCE (the function containing the os.remove of original DICOMs) has any call site - I found none in the files I read, so it may be dead code.; The 13 MB StepByStepInstructionsForSlicerFTV_12_14_2022_FINAL_Rdcd.pdf could not be read.; The catalog entry uses scm_revision 'master'; I could not verify that commit 271ece80ce3db9cc79596ee5436dd5d44ed1a50c exists or that the branch tip matches what I reviewed.; No build or CI results were available, so I could not confirm the extension builds or that the modules load in a real Slicer.; Whether the pip packages installed at import (nibabel, opencv, pynrrd, yattag, matplotlib, scikit-image) pull in versions that downgrade or pin packages Slicer bundles (e.g. numpy) was not verified.
Questions for the author: Why are nibabel, opencv, pynrrd, yattag, matplotlib and scikit-image installed with pip at module import instead of being declared as dependencies and installed with user consent?; Can the 7-Zip shell calls be replaced with Python's gzip module (or subprocess without a shell), and can the hardcoded 'C:\Program Files\7-Zip\7z' path be removed?; Is gunzipAllFilesDCE still used? It deletes original DICOMs from the user's exam folder after a gzip command that may fail.; Can the module-1 workspace be stored in a parameter node or the user's temp directory instead of a pickle inside the extension install directory?; Can module 2 show a clear message instead of raising when module 1 has not been run yet?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The Breast_DCEMRI_FTV extension provides two well-structured 3D Slicer scripted modules for computing breast functional tumor volume (FTV) from DCE-MRI exams. Code quality, safety, packaging, and licensing meet standard requirements, with only a minor recommendation to use opencv-python-headless rather than opencv-python to avoid potential Qt conflicts in Slicer.
Not checked: Full execution of DCE-MRI pipeline on clinical data

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
I read the catalog entry, CMake files, license/README, the module entry points and several plugin files, but not every file. No network exfiltration or obfuscation was found. The main concerns are shared-environment side effects: pip installs at module import (including a package named 'cv2' that is not the OpenCV distribution), a global matplotlib backend switch, and shell commands built from unquoted user-selected paths. The license is Slicer's BSD-style agreement with a research-only note, and the catalog has no build dependencies. I recommend fixes before listing.
Not checked: The 13 MB user guide PDF (StepByStepInstructionsForSlicerFTV_12_14_2022_FINAL_Rdcd.pdf) and the screenshots were not read.; Most plugin files (for example Exam_Ident_and_timing.py, chooseEarly_LateByManufacturer.py, read_DCE_images_to_numpy.py, ftv_map_gen_p2.py, the DCE_TumorMapProcess.py body beyond the imports and the report section) were not read in full, so I did not check every import against the CMake install list; I did not resolve the scm_revision 'master' to a commit, did not check the upstream repository, and did not verify whether the PyPI package 'cv2' exists or what it contains.; Nothing was executed; the Slicer version targeted and the build/CI results are unknown.; The rest of license.txt was read in full, but whether the UCSF copyright notice conflicts with the Slicer agreement was not assessed legally.
Questions for the author: Why does _importOptional('cv2', 'cv2') install 'cv2' rather than opencv-python-headless? Which package was intended?; Can the module installs be moved to an explicit user-confirmed action rather than module load?; Can the 7-Zip calls be replaced with Python gzip, and can subprocess argument lists be used for img2dcm?; Please confirm the canonical repository (rnadkarni2 vs radiology-research) and whether the catalog should pin a commit rather than 'master'.; Is matplotlib.use('Agg') needed globally, or can it be scoped to the report function?


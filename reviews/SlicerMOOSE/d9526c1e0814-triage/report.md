# AI review: SlicerMOOSE

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/mprires/SlicerMOOSE at commit `d9526c1e0814bad1eb49349a73684544f690d078`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T02:37:10Z; cost $0.03

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | concern |
| environment | blocking | ok | concern |
| packaging | ok | ok | ok |
| license | ok | ok | ok |
| soundness | minor | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: SlicerMOOSE wraps the MOOSE/moosez multi-organ CT segmentation tool (nnU-Net based) in a Slicer module so researchers can produce multi-label organ segmentations of whole-body CT/PET-CT volumes from within Slicer.
- **flash-lite**: SlicerMOOSE is a 3D Slicer extension that integrates the MOOSE 3.0 multi-organ segmentation tool (based on PyTorch and nnU-Net) into Slicer, providing automated multi-organ CT and PET/CT segmentation models.
- **haiku**: A Slicer scripted module that runs the MOOSE multi-organ CT segmentation tool (via the `moosez` pip package) on a selected volume and loads the result as a segmentation. It is aimed at researchers in the Segmentation category who want to run MOOSE models inside Slicer.

## Disagreements (start here)

### D1. Hard torch==2.2.2 and numpy<2 pins on macOS downgrade Slicer-bundled packages
partial; category environment; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`MOOSE/MOOSE.py:101`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L101): On macOS the module pip-installs an exact torch pin and forces numpy<2 into Slicer's Python. numpy is a package Slicer bundles; pinning/downgrading it can break Slicer core and other extensions for users who never open MOOSE. The policy explicitly lists exact torch pins and pins of Slicer-bundled packages (numpy) as blocking environment changes.
  ```
              slicer.util.pip_install('torch==2.2.2 "numpy<2"')
  ```
  Suggestion: Install torch through PyTorchUtils (which handles platform-appropriate versions) and avoid constraining numpy; if a numpy constraint is truly required, document it and coordinate with the PyTorch extension rather than pinning in this module.
- **haiku** (major, high confidence, quote verified) [`MOOSE/MOOSE.py:101`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L101): The macOS branch installs torch==2.2.2 together with "numpy<2" (line 101). An exact torch pin plus a NumPy downgrade is the kind of change the policy prohibits. Slicer's bundled NumPy is replaced for all Slicer users, and the same constraint is added to the moosez install (line 67). Other extensions relying on NumPy 2.x may break.
  ```
  slicer.util.pip_install('torch==2.2.2 "numpy<2"')
  ```
  Suggestion: Route torch through the PyTorch extension with a version range, and find a way to run moosez without downgrading Slicer's NumPy (for example an isolated environment or a subprocess with its own site-packages), or document and gate the change behind explicit user consent.

### D2. PyTorch installed with pip_install("torch") on Linux instead of PyTorchUtils
partial; category environment; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote verified) [`MOOSE/MOOSE.py:92`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L92): On Linux the module installs torch directly from PyPI into Slicer's shared Python environment, bypassing the PyTorch extension. This is exactly the pattern the review policy forbids: it can install a torch build incompatible with Slicer's CUDA/VTK stack, and it affects every user of that Slicer installation, not just users of MOOSE. The Windows branch (lines 73-90) already does it correctly via PyTorchUtils.installTorch, so the same approach should be used on Linux.
  ```
          elif sys.platform.startswith("linux"):
              slicer.util.pip_install("torch")
  ```
  Suggestion: Use PyTorchUtils.PyTorchUtilsLogic().installTorch(askConfirmation=True, torchVersionRequirement=...) on all platforms, and list PyTorch in build_dependencies/EXTENSION_DEPENDS (already done).
- **haiku** (blocking, high confidence, quote verified) [`MOOSE/MOOSE.py:92`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L92): On Linux, install_pytorch calls slicer.util.pip_install("torch") (line 93). This pulls torch from PyPI into Slicer's shared Python environment without using PyTorchUtils, which the index policy requires. It can replace or conflict with a torch build the user already has, and it affects other extensions even for users who never open this module. The README (line 11) also says the PyTorch extension is not required on Linux, which contradicts the catalog's build_dependencies.
  ```
  elif sys.platform.startswith("linux"):
      slicer.util.pip_install("torch")
  ```
  Suggestion: Use the PyTorch extension on all platforms (PyTorchUtilsLogic.installTorch with a version requirement), as the Windows branch already does, and update README lines 10-11 to match.

### D3. moosez pip-installed into Slicer's Python pulls torch from PyPI and can upgrade numpy
severity dispute; category environment; raised by deepseek, haiku
- **deepseek** (blocking, high confidence, quote partly verified) [`MOOSE/MOOSE.py:62`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L62): moosez depends on torch (and on numpy/scipy and other scientific packages). Installing it with pip_install resolves those dependencies from PyPI inside Slicer's environment, so on Linux/Windows it can install or upgrade torch and numpy independently of the PyTorch extension, and on macOS the numpy<2 constraint is applied to a Slicer-bundled package. The policy names this exact case (packages that pull torch from PyPI, e.g. nnunetv2) as requiring the dedicated extension's install logic instead.
  ```
              requirements = "moosez>=3.1.1"
              if sys.platform.startswith("darwin"):
                  requirements += ' "numpy<2"'
              slicer.util.pip_install(requirements)
  ```
  Suggestion: Install torch first via PyTorchUtils and then install moosez with `--no-deps` for torch (or use a dependency set that does not resolve torch/numpy), verifying the remaining dependencies do not upgrade Slicer-bundled packages; alternatively coordinate with the MOOSE/NNUNet extension install logic.
- **haiku** (minor, medium confidence, quote verified) [`MOOSE/MOOSE.py:62`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L62): install_moosez calls pip_install(requirements) (line 68), which pulls moosez and its large dependency tree into Slicer's Python without a confirmation step. The button click is an explicit action, so this is not a hidden install, but the policy asks for confirmation before large downloads.
  ```
  requirements = "moosez>=3.1.1"
              if sys.platform.startswith("darwin"):
  ```
  Suggestion: Ask for confirmation before installing, and list the packages and approximate download size.

### D4. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D5. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku concern


## Findings from some reviewers

### Error path in forward_process_status passes stdout object as CalledProcessError output
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`MOOSE/MOOSE.py:381`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L381): On a non-zero return code, the code raises CalledProcessError with output=proc.stdout, which is the stream object, not captured output, and stderr=proc.stderr is not set by launchConsoleProcess. The user sees a confusing message rather than the moosez error text, which makes failures harder to diagnose.
  ```
  raise CalledProcessError(retcode, proc.args, output=proc.stdout, stderr=proc.stderr)
  ```
  Suggestion: Pass the collected output (returnOutput=True) and report it to the user.

### Long segmentation runs on the GUI thread without progress or cancel
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`MOOSE/MOOSE.py:312`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L312): The readline loop in forward_process_status calls slicer.app.processEvents() via the status callback, so the UI is not fully frozen, but the whole run (up to ~40 minutes on CPU per README) executes inside the button slot with no progress bar, no cancel button and no way to abort; the module widget is disabled for the duration.
  ```
          result = slicer.util.launchConsoleProcess(cmd)
          self.forward_process_status(result)
  ```
  Suggestion: Run the subprocess in a worker thread (e.g. slicer.util.Process or a QThread) with a progress dialog and a cancel action.

### No active automated tests; the only test is commented out
minor; utility; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`MOOSE/Testing/Python/CMakeLists.txt:2`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/Testing/Python/CMakeLists.txt#L2): The Testing/Python directory registers no test; the only test is the unittest subclass in MOOSE.py registered by MOOSE/CMakeLists.txt line 27. Not a defect, but the empty subdirectory is dead weight and the integration test requires network access and a full dependency install, so it will not run in a normal build environment.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Either remove the empty Testing/Python directory or add a lightweight test that does not require downloading models.
- **haiku** (minor, high confidence, quote verified) [`MOOSE/Testing/Python/CMakeLists.txt:2`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/Testing/Python/CMakeLists.txt#L2): MOOSE/Testing/Python/CMakeLists.txt has its only test line commented out, and the in-module test (MOOSEIntegration) downloads a sample CT from an external S3 bucket and installs dependencies. Regressions in the install or segmentation path would not be caught by CI.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Enable a test that checks the module loads and the pure-Python logic (label mapping, JSON parsing), and keep the heavy segmentation test opt-in.

### No research-use disclaimer or model validation/provenance information
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`README.md:15`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/README.md#L15): The extension produces organ segmentations intended for research, but the README and module helpText contain no statement that output is not for clinical use and no information on how/where the models were trained or validated beyond a citation. Users may otherwise treat the output as clinically validated.
  ```
  4. Select a volume (which has to be a CT image) and a model and click on `Run Segmentation` and wait for the process to finish.
  ```
  Suggestion: Add a short research-use-only notice and a pointer to the model training/validation description in the upstream MOOSE repository.
- **haiku** (info, medium confidence, quote verified) [`README.md:10`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/README.md#L10): README lines 10-11 say the PyTorch extension is needed only on Windows, while the catalog and CMake list PyTorch as a dependency. The README also does not say the output is research-only and not for clinical decisions.
  ```
  * For Windows users: Please make sure that the PyTorch extension is also installed. 
      * For Linux/Unix users: The PyTorch extension is not required, as native `torch` works in most cases.
  ```
  Suggestion: Align the README with the dependency declaration and add a research-use disclaimer.

### PythonSlicer path may be None, producing an unusable command
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`MOOSE/MOOSE.py:275`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L275): If PythonSlicer is not on PATH (e.g. unusual launch environment), self.python_slicer is None and launchConsoleProcess receives None as argv[0], failing with an obscure error instead of a clear message. Similarly the moosez console script path is assumed rather than checked for existence.
  ```
          self.moosez = os.path.join(sysconfig.get_path('scripts'), self.format_executable_name("moosez"))
          self.python_slicer = shutil.which("PythonSlicer")
  ```
  Suggestion: Fall back to slicer.util.launchConsoleProcess with sys.executable or raise a clear InstallError when PythonSlicer/moosez are not found.
- **haiku** (minor, medium confidence, quote verified) [`MOOSE/MOOSE.py:276`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L276): self.python_slicer = shutil.which("PythonSlicer") (line 276) can be None, so cmd begins with None and launchConsoleProcess fails with an unclear error. get_default_download_folder (line 463) uses os.getenv('USERPROFILE') without a fallback, and that returns None on unusual Windows setups.
  ```
  self.python_slicer = shutil.which("PythonSlicer")
  ```
  Suggestion: Use slicer.app.applicationDirPath or sys.executable, and check for None before running a process.

### Segment renaming can raise KeyError and abort after the segmentation was loaded
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`MOOSE/MOOSE.py:192`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L192): If the moosez JSON's organ_indices does not contain every label index present in the NIfTI (or the segment ID is not of the form Segment_<int>), the loop raises KeyError/ValueError after the segmentation node has already been added to the scene, so the user sees 'Segmentation failed.' even though a segmentation exists, and the temp folder is not cleaned up.
  ```
                      segmentID_numeric = int(segmentID.replace("Segment_", ""))
                      segment = segmentation.GetSegment(segmentID)
                      newName = label_indices[segmentID_numeric]
  ```
  Suggestion: Use label_indices.get(segmentID_numeric) and skip/keep the default name when missing; guard the int() conversion.

### Temporary working folder leaks when segmentation fails
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`MOOSE/MOOSE.py:197`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L197): moose_folder is created with slicer.util.tempDirectory() and only removed on the success path at line 197. Any exception (missing segmentation, KeyError while renaming segments, subprocess failure) leaves the copied CT volume and moosez outputs on disk; repeated failures accumulate patient image copies in the temp directory.
  ```
                  shutil.rmtree(moose_folder)
  ```
  Suggestion: Move the cleanup into a finally block (or use a try/finally around prepare_data/run_segmentation).

### Test downloads into the user's Downloads folder and deletes that path
minor; safety; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`MOOSE/MOOSE.py:445`](https://github.com/mprires/SlicerMOOSE/blob/d9526c1e0814bad1eb49349a73684544f690d078/MOOSE/MOOSE.py#L445): The integration test writes sample_CT.nii.gz into the user's ~/Downloads (or %USERPROFILE%\Downloads) and later calls os.remove(sampleVolume_path) (line 439). If a user already has a file with that name there, it is silently overwritten and then deleted. The download is also not integrity-checked.
  ```
          download_directory = self.get_default_download_folder()
          URL = "https://enhance-pet.s3.eu-central-1.amazonaws.com/slicer_sample_data/sample_CT.nii.gz"
          download_file_name = os.path.basename(URL)
          download_file_path = os.path.join(download_directory, download_file_name)
  ```
  Suggestion: Download into slicer.util.tempDirectory() (or a TemporaryDirectory) instead of the user's Downloads folder, and delete only that temporary copy.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The module is a thin, readable wrapper around the `moosez` CLI: it writes the selected volume to a temp folder, runs moosez in a subprocess, loads the resulting NIfTI segmentation and renames segments from the generated JSON. No telemetry, no data upload, no obfuscation, and licensing (Apache-2.0 code, CC BY 4.0 models) permits distribution. The blocking problem is environment handling: PyTorch is installed with `pip_install("torch")` on Linux and a hard `torch==2.2.2 "numpy<2"` pin on macOS instead of through PyTorchUtils, and `moosez>=3.1.1` is pip-installed into Slicer's Python, pulling torch from PyPI and able to upgrade Slicer-bundled numpy. Otherwise only minor robustness issues.
Not checked: The `moosez` package itself (its license, its model download URLs, and whether it transmits any data) was not inspected; only the wrapper code in this repository was reviewed.; Whether moosez's first-run model download asks the user for confirmation before downloading large model files.; The exact source revision: the catalog entry uses scm_revision "main"; the reviewed content corresponds to commit d9526c1e0814bad1eb49349a73684544f690d078 as stated in the task, but I could not resolve the repository remotely.; Binary assets (SlicerMOOSE.png, Images/*.gif, Images/*.png) were not opened; only their presence and size were noted.; No build or runtime test was performed; CMake/CTest behaviour and the actual moosez CLI output layout were not verified.
Questions for the author: Why is torch installed with pip_install on Linux and with an exact 2.2.2 pin plus numpy<2 on macOS, rather than through PyTorchUtils on all platforms?; Does moosez pull torch from PyPI as a dependency, and can it be installed without touching Slicer's bundled numpy/scipy?; Does moosez download model weights on first run, and does it ask the user before downloading them?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
SlicerMOOSE is a well-implemented 3D Slicer extension that integrates MOOSE 3.0 deep learning segmentation models. It correctly handles platform-specific PyTorch requirements, dependencies, and temporary data management. All catalog entries, CMake configuration files, and Python logic follow Slicer best practices.🟢 Recommend merge
Not checked: Binary files Images/MOOSE.gif, Images/moose.png, Images/Enhance.gif, Images/SlicerMOOSE_Screenshot1.png, SlicerMOOSE.png

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The module is small and readable, and its UI, CMake install list and icon path are consistent. The main problems are environment-related: on Linux it runs a bare `pip_install("torch")` instead of using the PyTorch extension, and on macOS it pins torch 2.2.2 and downgrades NumPy below 2, which affects Slicer's shared Python environment. Installs run on a button click with no size confirmation. Test coverage is effectively absent. I did not inspect the moosez package or the model download source, so the model-weight provenance and network behaviour of the segmentation run are unverified.
Not checked: The moosez package (PyPI) and its code, including what it downloads at run time and from where, were not inspected.; Model weight source, integrity checks and licence of the MOOSE models (only the CC BY 4.0 MODEL_LICENSE.txt text was read).; Upstream MOOSE and nnU-Net licence terms.; The GitHub source at the 'main' revision was not fetched, so the revision reviewed is unknown beyond the catalog text.; Binary images (SlicerMOOSE.png, MOOSE.gif, Enhance.gif) were not viewed. Their size is noted but they do not appear to be needed by the build.; Whether CI builds on any platform; no CI report was provided.


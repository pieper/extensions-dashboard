# AI review: SynthSeg

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/niyaziacer/SlicerSynthSeg.git at commit `09790b8b7b40fb2396312a055927eb9828a583b3`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:14:35Z; cost $0.08

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | ok |
| environment | concern | minor | concern |
| packaging | ok | ok | ok |
| license | concern | ok | concern |
| soundness | minor | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A Slicer module that runs SynthSeg (Billot et al.) brain-MRI segmentation on a loaded volume, producing a segmentation node plus a regional volume table, using either Slicer's own Python (TensorFlow installed on first use) or a user-supplied Python/conda environment. It targets neuroimaging researchers who want contrast-agnostic whole-brain segmentation without a conda setup.
- **flash-lite**: SynthSeg 3D Slicer extension for contrast- and resolution-agnostic brain MRI segmentation and volume estimation using Benjamin Billot's SynthSeg algorithms.
- **haiku**: SlicerSynthSeg is a 3D Slicer scripted module that runs the bundled SynthSeg brain-MRI segmentation (Billot et al.) and returns a labelled segmentation plus volume table. It is for researchers who want contrast-agnostic brain segmentation without a separate conda environment.

## Disagreements (start here)

### D1. Child process stdout/stderr pipes are never drained while polling; long runs can stall
partial; category soundness; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:922`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L922): The poll loop at lines 928-938 only calls proc.poll() and processEvents(); communicate() is called after the process exits. SynthSeg prints progress and TensorFlow warnings to stdout/stderr; once the OS pipe buffer (typically 64 KB) fills, the child blocks on write and never exits, so the run hangs until SYNTHSEG_TIMEOUT_SECONDS (1800 s) kills it and the user sees a misleading 'machine too slow' error.
  ```
              proc = subprocess.Popen(
                  cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                  text=True, env=env,
              )
  ```
  Suggestion: Redirect output to a temporary file, or read the pipes in a thread/with select while polling, and include the captured output in the error message.
- **haiku** (major, medium confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:922`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L922): subprocess.Popen is started with stdout=PIPE and stderr=PIPE. The loop only calls poll(), processEvents() and sleep(). If the SynthSeg/TensorFlow child writes more than the OS pipe buffer (about 64 KB) before exiting, it blocks on write. The poll loop then never sees an exit and the run is killed after 30 minutes with a misleading 'may be stuck' error. TensorFlow warnings make this plausible.
  ```
  proc = subprocess.Popen(
      cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
      text=True, env=env,
  )
  ```
  Suggestion: Redirect output to a temporary log file instead of PIPE, or read both pipes in background threads, or use communicate() after a non-blocking wait. Keep the timeout.

### D2. Redistribution of SynthSeg model weights rests on an unverifiable, future-dated e-mail claim
partial; category license; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:80`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L80): The extension downloads synthseg_1.0.h5 / synthseg_2.0.h5 / synthseg_parc_2.0.h5 from the author's GitHub release (MODEL_RELEASE_URL, line 83) and tells users in the UI that the models 'are redistributed with their permission' (lines 296, 424, 484). The only evidence in the repository is this comment, whose date (23 Oct 2026) is in the future, and there is no license or terms file covering the weights. If the upstream model terms do not permit redistribution, users are being given a false assurance about the models they download.
  ```
  # Automatic model download. The SynthSeg authors (B. Billot, J.E. Iglesias) allowed this extension to
  # redistribute the models (e-mail, 23 Oct 2026). Sources are tried in order and every file must match
  # its SHA-256 before it is used, so a partial download or a Google Drive warning page is never accepted.
  ```
  Suggestion: Add a documented permission statement (or the upstream model license) to the repository, e.g. a MODELS_LICENSE file referenced from README, and correct the date; if permission cannot be documented, download only from the official SynthSeg/FreeSurfer location instead of redistributing.
- **haiku** (major, high confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:80`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L80): The extension downloads and redistributes SynthSeg .h5 weights from the maintainer's GitHub release and a Google Drive mirror. The only evidence of permission is a claim in code and README that the authors allowed it by e-mail on '23 Oct 2026'. No license file or written grant accompanies the weights, and the upstream SynthSeg Apache-2.0 license covers source code, not necessarily the trained models. Reviewers and users cannot verify the terms, so distribution rights for the weights are unclear.
  ```
  # Automatic model download. The SynthSeg authors (B. Billot, J.E. Iglesias) allowed this extension to
  # redistribute the models (e-mail, 23 Oct 2026). Sources are tried in order and every file must match
  ```
  Suggestion: Add the written permission (or a license file for the models) to the repository, for example in a models/ LICENSE or NOTICE, and cite it in README. Check the date, which is unusual. Confirm the upstream model terms explicitly.

### D3. h5py is pip-installed into Slicer's shared Python without asking the user
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:552`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L552): When the user clicks 'Import models from folder', _validateDownloadedModel (line 575) calls _ensurePackageInstalled("h5py"), which runs slicer.util.pip_install with no confirmation dialog and no version constraint. This modifies the Python environment shared by Slicer and every other extension, for a step the user did not associate with installing packages; pip may also resolve/upgrade dependencies of h5py (numpy) in that environment. The TensorFlow install, by contrast, is gated by an explicit confirmOkCancelDisplay (lines 405-411).
  ```
      def _ensurePackageInstalled(self, moduleName):
          """Import moduleName in Slicer's own Python, installing it via
          slicer.util.pip_install if it isn't available yet."""
          try:
              return __import__(moduleName)
          except ImportError:
  ```
  Suggestion: Ask for confirmation before installing (or use slicer.util.pip_install with a numpy constraint file as installSlicerTensorFlow does), or avoid h5py by validating the file size only / using a bundled reader.
- **haiku** (minor, medium confidence, quote verified, other lines) [`SlicerSynthSeg/SlicerSynthSeg.py:146`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L146): _ensurePackageInstalled calls slicer.util.pip_install when h5py is missing. It is reached from the Import models path without the confirmation dialog used for TensorFlow. This changes Slicer's shared environment silently and may replace a version other extensions rely on. The README already notes h5py was downgraded in testing.
  ```
  try:
      return __import__(moduleName)
  except ImportError:
      slicer.util.pip_install(moduleName)
  ```
  Suggestion: Ask the user before installing, or validate the HDF5 file with a package already in Slicer. Avoid unpinned installs of shared packages.

### D4. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D5. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings from some reviewers

### Bare except silently discards a corrupt configuration file
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSegLib/synthseg_config.py:32`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSegLib/synthseg_config.py#L32): Any error reading config.json (corrupt JSON, permission problem) is swallowed and the module silently falls back to defaults, so a user whose saved custom-Python configuration is unreadable sees the module behave as if never configured, with no diagnostic. The bare except also hides KeyboardInterrupt/SystemExit.
  ```
              try:
                  with open(self.config_file, 'r') as f:
                      return json.load(f)
              except:
                  pass
  ```
  Suggestion: Catch (OSError, ValueError) and log a warning naming the file and the error.

### Custom Python validation only checks that the path exists
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSegLib/synthseg_config.py:77`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSegLib/synthseg_config.py#L77): Any existing file passes validation, so a user who selects a non-executable or a Python without TensorFlow/nibabel gets 'Configuration saved successfully' and only discovers the problem when segmentation fails with a subprocess exit code. The dialog text (lines 477-478) promises a Python 'that has TensorFlow, Keras and nibabel'.
  ```
      def validate_python_env(self, python_path):
          """Validate Python environment - only check if executable exists"""
          python_path = Path(python_path)
          if not python_path.exists():
              return False, "Python executable not found"
  ```
  Suggestion: Run the chosen interpreter once with a short import check (e.g. `-c "import tensorflow, nibabel"`) and report the result in the dialog.

### Models are downloaded into the extension installation directory
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:735`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L735): With no saved configuration, synthseg_path defaults to bundledSynthSegPath() (lines 718-721), i.e. the installed extension tree under Slicer's qt-scripted-modules directory. downloadModelsWithProgress then mkdirs and writes ~150 MB of .h5 files there. If the extension is installed in a read-only or administrator-owned location (common for system-wide Slicer installs), the download fails with a permission error, and in all cases user data is written into an installation directory that extension updates may replace.
  ```
          models_dir = Path(self.getConfiguration()['synthseg_path']) / "models"
          return models_dir, [m for m in SYNTHSEG_MODES[mode][2] if not (models_dir / m).exists()]
  ```
  Suggestion: Store models in a user-writable location (e.g. under slicer.app.userSettingsPath() or a per-user cache dir) and point SynthSeg at it, or copy the bundled source to a user directory on first use.

### Module self-test asserts nothing
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:993`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L993): WITH_GENERIC_TESTS is enabled in SlicerSynthSeg/CMakeLists.txt:22, so this test runs in the extension build/CI, but it only displays two messages and always passes. It gives no signal about configuration loading, label-name parsing, colour-table construction or the CSV annotation step, all of which are testable without TensorFlow.
  ```
      def test_SlicerSynthSeg1(self):
          self.delayDisplay("Starting the test")
          self.delayDisplay('Test passed')
  ```
  Suggestion: Add assertions for the pure-Python helpers (getConfiguration defaults, _labelNames, _buildColorTableNode, _annotateVolumeCsv) and mark the segmentation run as skipped when models/TensorFlow are absent.
- **haiku** (minor, high confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:993`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L993): The scripted test prints 'Test passed' without checking any output, so the ScriptedLoadableModule test gives no coverage of segmentation or configuration logic.
  ```
  def test_SlicerSynthSeg1(self):
      self.delayDisplay("Starting the test")
      self.delayDisplay('Test passed')
  ```
  Suggestion: Add a small test with a bundled sample volume, or with a mock subprocess, that checks the config and the label-name table. Add a clinical-use / research-only disclaimer to the README.

### Segmentation runs on the GUI thread with no progress reporting
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:927`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L927): process() is called directly from onApplyButton (line 438) and spins on processEvents() for up to 30 minutes. The UI stays partially responsive but the user gets no progress or elapsed-time feedback and cannot cancel, which for a CPU-only SynthSeg run of several minutes looks like a freeze.
  ```
              pollStart = time.time()
              while proc.poll() is None:
                  if time.time() - pollStart > SYNTHSEG_TIMEOUT_SECONDS:
  ```
  Suggestion: Run the subprocess from a slicer.util.ProgressDialog / CLI-style worker with a cancel button, or at least show elapsed time and allow cancellation.

### Shared-package downgrade acknowledged in README
minor; environment; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`README.md:42`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/README.md#L42): The README states TensorFlow installation changed h5py from 3.16.0 to 3.14.0 in the authors' environment. Installing TensorFlow into Slicer's Python can therefore break other extensions that depend on Slicer's shared packages. The numpy constraint in code does not protect h5py or other shared packages.
  ```
  > Note: installing TensorFlow can change versions of packages it shares with other extensions
  > (in our test, h5py 3.16.0 became 3.14.0; TotalSegmentator and OpenMAP-T1 kept working).
  ```
  Suggestion: Extend the pip constraints file to every package already installed in Slicer (not just numpy), or pin them to their current versions, so no existing package is downgraded.

### TensorFlow is exactly pinned into Slicer's shared Python
minor; environment; raised by deepseek, flash-lite
- **deepseek** (minor, medium confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:58`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L58): installSlicerTensorFlow (lines 204-220) installs these exact pins into Slicer's own Python after user confirmation. numpy is protected by a constraints file, but TensorFlow's other transitive dependencies (protobuf, ml_dtypes, h5py, ...) are not, so other extensions that need different versions can break for users who accept the install. The pinned version also has to exist on PyPI for the Slicer Python version in use; if it does not, the install fails with a pip error rather than a clear message.
  ```
  SLICER_TF_REQUIREMENTS = ["tensorflow==2.21.*", "tf-keras==2.21.*"]
  ```
  Suggestion: Constrain the full dependency set (or install into a separate venv/launcher), and verify the pinned version exists for the Slicer Python versions you support.
- **flash-lite** (minor, high confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:58`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L58): The extension installs TensorFlow and tf-keras directly into Slicer's Python environment via pip_install upon user prompt. While it uses constraints to preserve the numpy version, installing heavyweight packages like TensorFlow directly into Slicer's shared Python environment can potentially interfere with other extensions or Slicer's internal libraries. However, it respects user consent and does not install at import or startup.
  ```
  SLICER_TF_REQUIREMENTS = ["tensorflow==2.21.*", "tf-keras==2.21.*"]
  ```
  Suggestion: Ensure robust testing across different Slicer releases to prevent dependency conflicts with TensorFlow.

### Bundled upstream code contains os.system and pickle.load, not reachable from the Slicer UI path
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`SynthSeg/ext/lab2im/utils.py:303`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SynthSeg/ext/lab2im/utils.py#L303): The vendored SynthSeg/lab2im tree includes unsafe-deserialisation helpers and os.system calls (e.g. SynthSeg/ext/lab2im/edit_volumes.py lines 1516, 1546, 1574, 1596, 1736, 1776, 1790, 1844, 1888, 1896, 1902, 1917, 2254) used for FreeSurfer registration. The Slicer module only invokes scripts/commands/SynthSeg_predict.py, so these are not reachable from the module UI; they are noted so future changes that expose training/registration paths get re-reviewed.
  ```
  def read_pickle(filepath):
      """ read a python object with a pickle"""
      with open(filepath, 'rb') as file:
          unpickler = pickle.Unpickler(file)
          return unpickler.load()
  ```
  Suggestion: Keep the Slicer entry point limited to SynthSeg_predict.py, or prune the unused training/registration modules from the packaged tree.

### Model search globs WSL network shares on Windows
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`SlicerSynthSeg/SlicerSynthSeg.py:264`](https://github.com/niyaziacer/SlicerSynthSeg/blob/09790b8b7b40fb2396312a055927eb9828a583b3/SlicerSynthSeg/SlicerSynthSeg.py#L264): findModelFolders enumerates \\wsl.localhost\<distro>\home\<user>\freesurfer\models when the user opens 'Import models from folder'. This only lists paths and copies .h5 files the user then confirms, but it does touch other users' home directories over a network share, which may be slow or trigger access auditing on managed machines.
  ```
      if os.name == "nt":
          for root in (r"\\wsl.localhost", r"\\wsl$"):
              try:
                  found += [Path(p) for p in glob.glob(root + r"\*\home\*\freesurfer\models")]
  ```
  Suggestion: Only probe $FREESURFER_HOME by default and let the user browse to a WSL path explicitly.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
No malicious or concealed behaviour found: all image processing is local, the only network use is model/TensorFlow download with explicit dialogs and SHA-256 verification, and the subprocess call uses an argument list (no shell). Main problems are environment and provenance: h5py is pip-installed into Slicer's shared Python silently, TensorFlow is pinned exactly into Slicer's Python, and redistribution of the SynthSeg model weights rests on a code comment citing an e-mail dated in the future (23 Oct 2026) with no terms file for the models. Soundness issues are ordinary (pipe-buffer stall risk, stub test, models written into the extension install dir).
Not checked: The exact source revision: the catalog entry pins scm_revision "main", so the reviewed code is the snapshot provided, not a fixed commit (the prompt mentions 09790b8b7b40fb2396312a055927eb9828a583b3, which I could not resolve myself).; The SHA-256 values in MODEL_SHA256 and the actual content of the GitHub release / Google Drive model files could not be verified; I could not confirm that the published weights match the upstream SynthSeg models.; Whether tensorflow==2.21.* and tf-keras==2.21.* exist on PyPI for Slicer's Python versions (the code comment also cites numpy 2.4.6, which I could not confirm exists).; The upstream license/terms for the SynthSeg model weights (BBillot/SynthSeg) and the claimed e-mail permission from the SynthSeg authors.; SlicerSynthSeg/Resources/UI/SlicerSynthSeg.ui and Resources/Icons/SlicerSynthSeg.png contents (only their existence in the file listing), so widget names used at SlicerSynthSeg.py:328-344 (configureButton, testConfigButton, applyButton, inputVolumeSelector, parametersCollapsibleButton, volumeTableVi; README.md, USER_GUIDE.md and SynthSeg/README.md were not read in full, so documentation quality, clinical-use disclaimers and model validation statements were not assessed in detail.; No build, install or runtime test was performed; the CMake install layout and the SlicerSynthSegLib/SynthSeg import path were reasoned from the files only.
Questions for the author: Can you add written evidence (or the upstream license) permitting redistribution of synthseg_1.0.h5, synthseg_2.0.h5 and synthseg_parc_2.0.h5, and correct the e-mail date in the comment at SlicerSynthSeg.py:80-82?; Why is h5py pip-installed into Slicer's Python without a confirmation dialog, and can that be replaced by a size check or a constrained install?; Are tensorflow==2.21.* and tf-keras==2.21.* available for the Slicer Python versions you support, and have you checked that installing them does not break other extensions that share Slicer's Python?; Should the downloaded models live in a user-writable directory instead of the extension installation tree?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
SynthSeg is a well-structured 3D Slicer extension providing brain MRI segmentation and volume estimation via Benjamin Billot's SynthSeg algorithm. It installs TensorFlow and model weights on demand with user confirmation, respects existing numpy constraints, and properly manages temporary files and progress dialogs. The catalog entry and packaging are correct, and distribution terms are clear under the Apache 2.0 license. 🟢 Recommend merge
Not checked: Execution of model training or runtime inference in Slicer environment

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The module code is readable and has no obvious malicious behaviour. Network access happens only after user confirmation, model files are checked by SHA-256, and no data leaves the machine. Two issues need fixing before admission. First, the bundled .h5 model weights are redistributed under an e-mail permission that is not in the repository, so the distribution terms are unclear. Second, the SynthSeg subprocess pipes are not drained while polling, which can stall long runs. Other points are minor. I did not run anything; the review is from static reading.
Not checked: Did not read the bulk of the upstream SynthSeg Python sources (predict.py beyond the portion shown, lab2im/neuron modules, SynthSeg_predict.py) for behaviour beyond their imports.; Did not verify the GitHub release assets (models-v1) or their SHA-256 values against the released files; did not fetch the Google Drive mirror.; Did not verify the e-mail permission or the model upstream license terms.; Did not build or load the extension in Slicer; CMake install layout was inferred from the CMake files.; Did not check the .ui file, icons, or the .gitignore contents.; Did not verify the exact commit 09790b8b7b40fb2396312a055927eb9828a583b3 or that the catalog revision 'main' matches what was reviewed.
Questions for the author: Where is the written permission from the SynthSeg authors for redistributing the .h5 weights, and can it be placed in the repository? What is the date '23 Oct 2026' referring to?; Does the upstream SynthSeg model license allow redistribution, or only use?; Have you tested a segmentation on a T1 volume larger than the pipe buffer limit, with TensorFlow warnings on stderr, to rule out the pipe stall?; Which other installed Slicer packages besides numpy and h5py can change during the TensorFlow install?


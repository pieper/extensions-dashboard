# AI review: SPINEPS

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/BerDom-Ing/SlicerSPINEPS.git at commit `5f2d78ca91f413f2b9a10023b7c940d7d7019c05`
- Context: pull request 2392 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-14T17:25:44Z; cost $0.57

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | unknown |
| environment | unknown | blocking | blocking |
| packaging | unknown | ok | unknown |
| license | unknown | ok | unknown |
| soundness | unknown | minor | concern |
| utility | unknown | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: Slicer module that wraps the SPINEPS spine segmentation pipeline (MRI T2w/T1w/Vibe and CT). One button pip-installs SPINEPS and its dependencies, including PyTorch, into Slicer's Python. It then runs inference in a child process and loads the vertebra and semantic masks as segmentations.
- **gemini**: SlicerSPINEPS integrates the SPINEPS whole-spine segmentation pipeline into 3D Slicer to segment MRI (T2w, T1w, Vibe) and CT spine volumes into anatomical per-vertebra instance masks and semantic subregion masks. It provides both a graphical module for clinicians and researchers and a reusable Python library interface for other Slicer modules.
- **gpt**: SPINEPS integrates an upstream AI pipeline into 3D Slicer to segment vertebrae and spinal subregions from MRI and CT volumes. It is intended for researchers and other Slicer users who need whole-spine segmentation.

## Disagreements (start here)

### D1. PyTorch installed directly via light-the-torch instead of the Slicer PyTorch extension
partial; category environment; raised by gemini, gpt; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (blocking, high confidence, quote verified) [`SlicerSPINEPS/SlicerSPINEPSLib/InstallLogic.py:498`](https://github.com/BerDom-Ing/SlicerSPINEPS/blob/5f2d78ca91f413f2b9a10023b7c940d7d7019c05/SlicerSPINEPS/SlicerSPINEPSLib/InstallLogic.py#L498): The Slicer Extensions Index review policy explicitly requires PyTorch to be installed through the Slicer PyTorch extension (`PyTorchUtils`, listed in `build_dependencies` and `EXTENSION_DEPENDS`) rather than via direct use of `light-the-torch`. Additionally, the catalog entry has `"build_dependencies": []` and `CMakeLists.txt` has `set(EXTENSION_DEPENDS "NA")`. While the author's design rationale (avoiding an extra extension install, Slicer restart, and importing `torch` into the main Slicer process on Windows) and the care taken to reuse existing PyTorch installations and pin core packages (`SimpleITK`, `numpy`, `scipy`, `torch`, `nnunetv2`) are well-reasoned, bypassing the `PyTorch` extension directly conflicts with the Extensions Index policy for managing Slicer's shared Python environment.
  ```
          if not self.isPackageInstalled("light-the-torch"):
              self._log("Installing light-the-torch (selects the right PyTorch build)...")
              self.pip_install(LIGHT_THE_TORCH_REQUIREMENT)
  
          backend = "CUDA" if self.isCudaGpuAvailable() else "CPU"
          self._log(
  ```
  Suggestion: Declare `PyTorch` (and optionally `NNUNet` if sharing its install logic) in `EXTENSION_DEPENDS` in `CMakeLists.txt` and `build_dependencies` in `SPINEPS.json`, and use `PyTorchUtils` to manage PyTorch installation in accordance with Slicer Extensions Index policy.
- **gpt** (blocking, high confidence, quote verified) [`SlicerSPINEPS/SlicerSPINEPSLib/InstallLogic.py:498`](https://github.com/BerDom-Ing/SlicerSPINEPS/blob/5f2d78ca91f413f2b9a10023b7c940d7d7019c05/SlicerSPINEPS/SlicerSPINEPSLib/InstallLogic.py#L498): On a fresh Slicer installation, accepting the dependency prompt invokes light-the-torch directly to install torch and torchvision into Slicer's shared Python environment. This bypasses the required PyTorch extension and can produce a build or version incompatible with other extensions.
  ```
          if not self.isPackageInstalled("light-the-torch"):
              self._log("Installing light-the-torch (selects the right PyTorch build)...")
              self.pip_install(LIGHT_THE_TORCH_REQUIREMENT)
  ```
  Suggestion: Declare PyTorch in both EXTENSION_DEPENDS and catalog build_dependencies, and install or reuse torch through PyTorchUtils; prevent transitive dependencies from independently installing torch.
- claude on re-check: **real: yes, blocking**: InstallLogic.py:498-507 pip-installs light-the-torch and then runs `slicer.util._executePythonModule("light_the_torch", ["install", *TORCH_PACKAGES])`. This is the direct light-the-torch use that the policy lists as a reason to request changes. CMakeLists.txt:19 has `set(EXTENSION_DEPENDS "NA")` and README.md:70-77 explains why PyTorchUtils is not used. The code mitigates the risk: ensureTorchAvailable (441-485) reuses any existing torch, the user is asked first (422-423, 634+), and a constraints file pins protected packages (542+). The path is still real and conflicts with the policy, so I rate it as the policy requires.
- gpt on re-check: **real: yes, blocking**: InstallLogic.py:415-425 calls ensureTorchAvailable after the install confirmation; lines 471-477 call _installTorch only if no torch is present. Lines 498-507 state `self.pip_install(LIGHT_THE_TORCH_REQUIREMENT)` and `slicer.util._executePythonModule("light_the_torch", ["install", *TORCH_PACKAGES])`; lines 105-107 define `TORCH_PACKAGES = ["torch", "torchvision"]`. CMakeLists.txt:13-19 explicitly states `set(EXTENSION_DEPENDS "NA")`. The existing torch is reused (InstallLogic.py:457-469), and the user is asked before installation, but direct light-the-torch installation violates the policy's explicit PyTorch extension requirement. The catalog entry was not available here, so its dependency list was not independently verified.
- gemini on re-check: **real: yes, blocking**: Checked `SlicerSPINEPS/SlicerSPINEPSLib/InstallLogic.py` lines 487-509 and `CMakeLists.txt` lines 13-19. In `InstallLogic._installTorch`, when PyTorch is not already installed, the code installs `light-the-torch>=0.8` via `self.pip_install(LIGHT_THE_TORCH_REQUIREMENT)` and runs `slicer.util._executePythonModule("light_the_torch", ["install", *TORCH_PACKAGES])`. `CMakeLists.txt` line 19 sets `set(EXTENSION_DEPENDS "NA")`. Under the Slicer Extensions Index review policy (Security review of extensions, item 3), requests for changes are explicitly required for "PyTorch installed other than through the Slicer PyTorch extension (`PyTorchUtils`, listed in `build_dependencies` and `EXTENSION_DEPENDS`). This includes `pip_install("torch")`, direct use of light-the-torch, PyTorch index URLs, exact torch pins, and packages that pull torch from PyPI as a dependency".

### D2. A first run can download several large models without confirmation
single; category environment; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`SlicerSPINEPS/SlicerSPINEPS.py:173`](https://github.com/BerDom-Ing/SlicerSPINEPS/blob/5f2d78ca91f413f2b9a10023b7c940d7d7019c05/SlicerSPINEPS/SlicerSPINEPS.py#L173): The widget warns when the model folder is empty, but running inference initiates downloads without a confirmation. Once any model directory exists it only lists directories, so selecting a different model may silently trigger further downloads of hundreds of MB per model.
  ```
          if not models:
              return (
                  f"Model weights: none yet. The first segmentation downloads them "
                  f"(a few hundred MB per model) into {folder} and needs an internet "
                  "connection. To work offline, copy that folder from a machine that "
                  "already has them."
  ```
  Suggestion: Check whether the selected model and its companion weights are available, and ask for confirmation before any substantial missing-weight download.
- claude on re-check: **real: yes, minor**: SlicerSPINEPS.py:173-180 shows the widget tells the user before they run anything that the first segmentation downloads weights of a few hundred MB each, and onApplyClicked (239-256) starts inference with no further prompt. A search of the module found no confirmation dialog for the weights download. The downloads are done by the SPINEPS package at inference time, not by this extension's installer. They are documented in the UI and Parameter.py:84. The package-install confirmation rule does not clearly cover this. The remaining gap is that the label only counts existing model folders, so picking another model can download again without warning. That makes it a minor usability issue, not a major or safety one.
- gpt on re-check: **real: yes, major**: SlicerSPINEPS.py:173-180 says `f"Model weights: none yet. The first segmentation downloads them "` and `f"(a few hundred MB per model) into {folder} and needs an internet "`, but once any directory exists it only returns `f"Model weights ({len(models)}) in {folder}: {', '.join(models)}"`. The selected model is passed directly to a run without a download confirmation (lines 239-256); Parameter.py:157-162 passes semantic, instance, and labeling model names, and SegmentationLogic.py:228-240 starts the external process. Parameter.py:33-42 identifies different CT companion models. Thus the first run is warned about but not separately confirmed, and subsequent selections may download missing models without the initial warning. The external SPINEPS downloader and exact transfer sizes were not available for independent verification.
- gemini on re-check: **real: yes, minor**: Checked `SlicerSPINEPS/SlicerSPINEPS.py` lines 160-180 and 239-256. `describeWeightsState` inspects `folder.iterdir()` for existing subdirectories (`models = sorted(p.name for p in folder.iterdir() if p.is_dir())`) and displays a label in the UI explaining that the first segmentation downloads weights ("a few hundred MB per model"), or lists existing folders if any exist. `onApplyClicked` starts the segmentation process directly when the user clicks "Run segmentation" without a separate modal confirmation dialog before downloading missing model weights. However, because the user explicitly clicks "Run segmentation" in an AI segmentation module whose UI label (`self.weightsLabel`) already states ahead of time that the first run downloads model weights into the target folder, this is a minor UX/informational issue rather than a major environment defect (model weights are stored in a dedicated models folder, not modifying Slicer's shared Python environment).


## Findings from some reviewers

### Registered test uses obsolete command-line flags
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`SlicerSPINEPS/SlicerSPINEPS.py:394`](https://github.com/BerDom-Ing/SlicerSPINEPS/blob/5f2d78ca91f413f2b9a10023b7c940d7d7019c05/SlicerSPINEPS/SlicerSPINEPS.py#L394): Parameter.asArgList emits --cpu, not -cpu, so this registered test fails deterministically. Its later CT assertions also expect old -model_instance and -model_labeling spellings rather than the current double-dash forms.
  ```
          self.assertIn("sample", args)
          self.assertIn("--model-semantic", args)
          self.assertEqual(args[args.index("--model-semantic") + 1], "t2w")
          self.assertIn("-cpu", args)
          self.assertEqual(parameter.inputFileName(), "sub-spineps_acq-sag_T2w.nii.gz")
  ```
  Suggestion: Update the assertions to match the current flags and run the registered Slicer test.

### Result files are accepted before checking inference exit status
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`SlicerSPINEPS/SlicerSPINEPSLib/SegmentationLogic.py:121`](https://github.com/BerDom-Ing/SlicerSPINEPS/blob/5f2d78ca91f413f2b9a10023b7c940d7d7019c05/SlicerSPINEPS/SlicerSPINEPSLib/SegmentationLogic.py#L121): The process emits its finished signal for nonzero exits and cancellation as well as success. If a matching final file was written before failure or cancellation, this method returns it without consulting the exit code and the widget can load an incomplete or failed-run result.
  ```
      def _findOutputFile(self, pattern: str, description: str) -> Path:
          # SPINEPS places results in a "derivatives_seg" folder whose exact location
          # depends on how it resolves the BIDS path, so search the whole temp tree.
          matches = sorted(Path(self._tmpDir.path()).rglob(pattern))
          matches = [m for m in matches if not self._isIntermediateResult(m)]
          if matches:
  ```
  Suggestion: Only signal successful completion and load outputs after confirming normal exit with code zero; report cancellation and failed runs separately.

### Unit test `test_ParameterArgList` checks outdated CLI flag names and will fail
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`SlicerSPINEPS/SlicerSPINEPS.py:409`](https://github.com/BerDom-Ing/SlicerSPINEPS/blob/5f2d78ca91f413f2b9a10023b7c940d7d7019c05/SlicerSPINEPS/SlicerSPINEPS.py#L409): `Parameter.asArgList` was updated for SPINEPS >= 2.1.1 to emit double-dash hyphenated flags (`--model-semantic`, `--model-instance`, `--model-labeling`, `--cpu`), and line 395 of `test_ParameterArgList` was updated to check `--model-semantic`. However, lines 397, 413, and 414 of `test_ParameterArgList` still check for the old single-dash flags (`-cpu`, `-model_instance`, `-model_labeling`), which causes `SlicerSPINEPSTest.test_ParameterArgList` to fail with a `ValueError` when the self-test runs.
  ```
          # The CT semantic model has its own instance and labeling models. SPINEPS' own
          # "sample" command does not pair them (only "dataset" resolves "auto"), and it
          # accepts a mismatch silently, so selecting "ct" must switch all three.
          ctArgs = Parameter(semanticModel="ct").asArgList(Path("/tmp/x.nii.gz"))
          self.assertEqual(ctArgs[ctArgs.index("-model_instance") + 1], "ct_instance")
          self.assertEqual(ctArgs[ctArgs.index("-model_labeling") + 1], "ct_labeling")
  ```
  Suggestion: Update `test_ParameterArgList` in `SlicerSPINEPS/SlicerSPINEPS.py` to assert `"--cpu"`, `"--model-instance"`, and `"--model-labeling"` instead of `"-cpu"`, `"-model_instance"`, and `"-model_labeling"`.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
Reviewed all of the Python code, both CMakeLists files, the README and the LICENSE at the submitted revision. I found no malicious behavior or hidden data transmission. Installation only happens on a button click after a confirmation dialog, and inference runs out of process. The license is Apache-2.0. The blocking problem is the environment policy: the extension installs PyTorch itself with light-the-torch instead of through the PyTorchUtils extension. It does so by design and has no PyTorchUtils entry in `build_dependencies` or `EXTENSION_DEPENDS`. It also installs nnunetv2 and other packages into Slicer's shared environment. Smaller issues: the catalog entry uses `main` as the revision, the install call blocks the GUI thread, a failed install is reported only in the log, and model weights are downloaded without a prompt. Do not merge yet. Switch PyTorch installation to PyTorchUtils and add it to the dependency declarations.

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
SlicerSPINEPS is a well-engineered and thoroughly documented extension for whole-spine MRI and CT segmentation using SPINEPS, running inference out-of-process and carefully pinning Slicer's bundled packages (`SimpleITK`, `numpy`, `scipy`) during dependency installation. No safety or licensing issues were found. However, under the Slicer Extensions Index review policy, installing PyTorch directly via `light-the-torch` without declaring and using the Slicer `PyTorch` extension (`PyTorchUtils` in `EXTENSION_DEPENDS` and `build_dependencies`) is a blocking environment issue. Additionally, there is a minor non-blocking mismatch in `test_ParameterArgList` where assertions check for outdated single-dash CLI flags.

🔴 Do not merge yet: PyTorch must be installed via the Slicer `PyTorch` extension (`PyTorchUtils` and `build_dependencies` / `EXTENSION_DEPENDS`) rather than directly invoking `light-the-torch`.
Not checked: Runtime execution in 3D Slicer and live PyPI package resolution/download behavior.; External SPINEPS GitHub release payloads (model weights downloaded at first inference run).
Questions for the author: Would you be able to switch PyTorch management to use the standard `PyTorch` Slicer extension (`PyTorchUtils` and `EXTENSION_DEPENDS` / `build_dependencies`), or coordinate with Slicer core maintainers if out-of-process installation should be upstreamed to `PyTorchUtils`?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The installer directly installs PyTorch using light-the-torch rather than the required PyTorch extension, affecting Slicer's shared environment. The registered tests also contain obsolete argument expectations, and failed inference can still yield loaded output. The extension code is Apache-2.0, but upstream weights and runtime dependencies could not be inspected; the source revision and catalog access could not be independently verified. 🔴 Do not merge yet: replace the direct PyTorch installation, and complete review of the upstream payloads, weight distribution terms, and catalog revision.
Not checked: No shell, Slicer runtime, build, automated test execution, or CI results were available.; The source checkout could not be independently resolved to commit 5f2d78ca91f413f2b9a10023b7c940d7d7019c05 or compared with catalog main; source content was provided in the review input.; Upstream SPINEPS, its transitive PyPI packages, model download endpoints and artifacts, and model weight distribution permissions could not be inspected.; No previous catalog entry or submission checklist was available for comparison.
Questions for the author: Can you provide the upstream license or explicit distribution permission covering all model weights downloaded by SPINEPS?; Can the installer be revised to use the Slicer PyTorch extension and prompt before downloading missing model weights?


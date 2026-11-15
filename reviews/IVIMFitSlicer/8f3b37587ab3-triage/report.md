# AI review: IVIMFitSlicer

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/Atakanisik/SlicerIVIMFit.git at commit `8f3b37587ab39b41b30a37e197a91c567f866981`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T10:16:35Z; cost $0.05

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | concern |
| environment | concern | ok | concern |
| packaging | minor | ok | ok |
| license | minor | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: IVIMFitSlicer is a 3D Slicer module for Intravoxel Incoherent Motion (IVIM) analysis of diffusion-weighted MRI: it fits mono-, bi- and tri-exponential (and optional Bayesian) models to ROI-averaged signals, generates voxel-wise parameter maps, and plots the fitted curve. It targets researchers analysing DWI/IVIM datasets in Slicer.
- **flash-lite**: IVIMFitSlicer is a 3D Slicer extension that provides advanced Intravoxel Incoherent Motion (IVIM) diffusion-weighted MRI analysis, supporting voxel-wise parametric mapping and ROI-based statistical modeling across mono-exponential, bi-exponential, tri-exponential, and Bayesian fitting algorithms.
- **haiku**: IVIMFitSlicer is a Slicer scripted module for intravoxel incoherent motion (IVIM) diffusion MRI analysis. It fits mono-, bi- and tri-exponential and Bayesian models to ROI-averaged signals and optionally to voxel-wise maps, using the external ivimfit package, for researchers working with DWI data.

## Disagreements (start here)

### D1. Heavy voxel-wise fitting runs on the GUI thread and errors are silently swallowed
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified, other lines) [`IVIMFitSlicer/IVIMFitSlicer.py:406`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L406): run_fitting is called from the button handler on the main thread; only processEvents between chunks keeps the UI alive, so Slicer appears frozen for minutes on real volumes. Any per-voxel fit failure is discarded by 'except: pass', leaving zeros in the parameter maps with no indication to the user that the fit failed.
  ```
              except: pass
          return start_idx, res
          
      with ThreadPoolExecutor(max_workers=4) as ex:
  ```
  Suggestion: Run the computation in a CLI or a worker thread (slicer.util.ProgressDialog / qt.QTimer pattern), count failures and report them to the user, and avoid bare excepts.
- **haiku** (minor, high confidence, quote partly verified) [`IVIMFitSlicer/IVIMFitSlicer.py:924`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L924): Every per-voxel fit failure is discarded with a bare except, so maps silently contain zeros where fitting failed, and the user gets no report. Bare excepts also catch KeyboardInterrupt.
  ```
  try:
   if method in ["segmented", "bayesian"]: 
   ...
   except: pass
  ```
  Suggestion: Catch Exception, count failed voxels, and report the count in the status message or log.

### D2. Version check compares version strings lexicographically
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:530`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L530): String comparison makes e.g. '0.1.10' or '0.1.7.10' compare as older than '0.1.7.2', so every run re-triggers pip_install and importlib.reload, repeatedly touching the shared environment and slowing each analysis. Also the except clause 'except (ImportError, Exception)' catches everything, so genuine import errors are indistinguishable from an outdated version.
  ```
          if importlib.metadata.version("ivimfit") < "0.1.7.2":
              raise ImportError("Outdated version")
  ```
  Suggestion: Use packaging.version.parse(...) for the comparison and catch only ImportError/PackageNotFoundError.
- **haiku** (minor, high confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:530`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L530): importlib.metadata.version returns a string and is compared lexicographically with '0.1.7.2'. Versions such as '0.1.10' or '0.10.0' compare incorrectly, so the update check can skip a needed upgrade or trigger unnecessary reinstalls each run.
  ```
  if importlib.metadata.version("ivimfit") < "0.1.7.2":
  ```
  Suggestion: Compare parsed versions, for example with packaging.version.Version, and handle the ImportError path separately from the version check.

### D3. pip requirement string embeds the --upgrade option
single; category soundness; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:534`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L534): slicer.util.pip_install treats a string argument as a single requirement, so 'ivimfit>=0.1.7.2 --upgrade' is passed to pip as one requirement specifier and pip rejects it as an invalid requirement; the install then fails and the subsequent 'import ivimfit' raises, so the module cannot run on a machine without ivimfit pre-installed. (Slicer's util.py was not available to me, so this is inferred from the documented API.)
  ```
          slicer.util.pip_install("ivimfit>=0.1.7.2 --upgrade")
  ```
  Suggestion: Pass the requirement and the option separately, e.g. pip_install("ivimfit>=0.1.7.2", extraOptions=["--upgrade"]) or pip_install(["ivimfit>=0.1.7.2"]).

### D4. pip_install of ivimfit and pymc into Slicer's shared Python without user confirmation
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote partly verified) [`IVIMFitSlicer/IVIMFitSlicer.py:534`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L534): Clicking 'Run Analysis' silently installs/upgrades packages into the Slicer Python environment shared by all modules. 'pymc' is a large download whose dependency chain (numpy, scipy, pandas, pytensor) can upgrade or downgrade packages Slicer bundles, which can break Slicer and other extensions for users who never open this module. The policy requires user confirmation for such installs and forbids changing Slicer-bundled packages.
  ```
          slicer.util.pip_install("ivimfit>=0.1.7.2 --upgrade")
  ...
              slicer.util.pip_install("pymc")
  ```
  Suggestion: Ask the user with slicer.util.confirmOkCancelDisplay before installing, install into an isolated location or document a manual install, and constrain dependencies so numpy/scipy are not modified (e.g. install with --no-deps for the risky transitive packages, or use a dedicated extension dependency).
- **haiku** (major, high confidence, quote partly verified) [`IVIMFitSlicer/IVIMFitSlicer.py:530`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L530): When the user clicks Run, the module calls pip_install for ivimfit (with --upgrade) and for pymc if missing. These change the shared Slicer Python environment for every extension and can pull in large dependencies, including numpy/scipy changes, with no explicit confirmation. The request to upgrade is not version-pinned against Slicer's bundled packages.
  ```
  if importlib.metadata.version("ivimfit") < "0.1.7.2":
   raise ImportError("Outdated version")
  ...
  slicer.util.pip_install("ivimfit>=0.1.7.2 --upgrade")
  ```
  Suggestion: Ask the user for confirmation before installing, show the packages and their sizes, avoid --upgrade on shared packages, and check that the bundled numpy/scipy versions are not downgraded. Document these installs in the README.

### D5. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D6. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D7. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Caller's b-value list is mutated in place
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:567`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L567): process() inserts into the list passed by the widget (and by the test suite), so repeated runs with the same list object accumulate b=0 entries and can produce a frame-count mismatch on the second run.
  ```
      if B != len(b_values):
          if B == len(b_values) + 1: b_values.insert(0, 0.0)
  ```
  Suggestion: Work on a copy: b_values = list(b_values).

### Creates a 'libs' directory inside the Slicer Python installation at runtime
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:544`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L544): The module writes into the Slicer installation directory (sys.exec_prefix) as a side effect of running an analysis. On a system-wide install this either fails silently (bare except) or modifies the installation, and it is a global side effect unrelated to the advertised function.
  ```
          libs_path = os.path.join(sys.exec_prefix, "libs")
          if not os.path.exists(libs_path):
              try:
                  os.makedirs(libs_path)
  ```
  Suggestion: Do not create directories inside the Slicer installation; document the manual setup step instead (as the README already does) and report a clear error if the environment is unsuitable.
- **haiku** (minor, medium confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:544`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L544): The PyTensor workaround creates sys.exec_prefix/libs inside the Slicer installation. This writes into the application directory, which may be read-only or belong to another user, and it is a global side effect for all Slicer Python code.
  ```
  libs_path = os.path.join(sys.exec_prefix, "libs")
   if not os.path.exists(libs_path):
   try:
   os.makedirs(libs_path)
  ```
  Suggestion: Avoid writing to the Slicer install directory. Use a per-user cache directory or configure PyTensor flags through environment variables scoped to the Bayesian call.

### Each run adds new table/chart/series nodes with fixed names
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:453`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L453): Repeated analyses accumulate 'IVIM_ROI_Data', 'IVIM_Chart', 'Raw Data' and 'Fit Data' nodes in the scene, cluttering the Data module and confusing which chart is current.
  ```
      tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "IVIM_ROI_Data")
  ```
  Suggestion: Reuse existing nodes by name or remove the previous ones before creating new ones.

### No clinical/research-use disclaimer in the module UI
minor; utility; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:25`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L25): The module produces quantitative diffusion parameters that could be mistaken for validated clinical measurements; the disclaimer exists only as an acknowledgement string and in the README, not in the module panel or results area.
  ```
      parent.acknowledgementText = "This work is an academic research tool."
  ```
  Suggestion: Add a visible 'research use only, not for clinical decision making' note in the module widget and README.

### README instructs users to run Slicer as Administrator and modify the Slicer installation
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`README.md:83`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/README.md#L83): Following the documented Bayesian setup, users copy Python headers/libs into the Slicer installation and run Slicer with elevated privileges, which weakens the security posture of the whole application and is not needed for the extension's advertised function.
  ```
  4. **Restart 3D Slicer as Administrative Mode:**
  ```
  Suggestion: Remove the Administrator recommendation and describe a non-privileged, per-user setup (or drop the C++ acceleration instructions in favour of a supported PyMC/PyTensor configuration).
- **haiku** (minor, medium confidence, quote verified) [`README.md:83`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/README.md#L83): The Bayesian setup guide asks users to copy headers and libraries into Slicer's directory and then to restart Slicer in administrative mode. Running a scientific application with elevated privileges widens the impact of any bug or malicious code and is not needed for the described compilation step.
  ```
  4. **Restart 3D Slicer as Administrative Mode:**
   Run the Bayesian  mode.
  ```
  Suggestion: Remove the administrator requirement. Describe a per-user approach, for example setting PyTensor compiler flags through a user config.

### ROI fit exceptions are printed to console instead of shown to the user
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified, other lines) [`IVIMFitSlicer/IVIMFitSlicer.py:313`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L313): If the ROI fit fails (e.g. bad bounds, missing ivimfit.bayesian), the exception is only printed and the function returns empty params, so the results panel shows 0.000000 values and the plot shows a flat curve without any error message.
  ```
      except Exception as e:
          print(f"\n🚨 HATA YAKALANDI ({method}): {e}")
  ```
  Suggestion: Re-raise or surface the error via slicer.util.errorDisplay and skip displaying results when fitting failed.
- **haiku** (minor, high confidence, quote verified, other lines) [`IVIMFitSlicer/IVIMFitSlicer.py:313`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L313): If the ROI fit raises, the error is only printed to the console and the code continues with a zero fit curve and an R^2 of 0 or NaN. The user sees results and plots that look valid.
  ```
  except Exception as e:
   print(f"\n🚨 HATA YAKALANDI ({method}): {e}")
   import traceback
   traceback.print_exc()
  ```
  Suggestion: Surface the error with slicer.util.errorDisplay or a status message and stop before plotting.

### Registered python unittest has no test class; real test suite is not registered
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`IVIMFitSlicer/CMakeLists.txt:25`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/CMakeLists.txt#L25): IVIMFitSlicer.py contains no unittest.TestCase subclass (only an unused 'import unittest'), so the generated ctest runs zero tests and gives false assurance. The actual round-trip suite in Testing/Python is not installed or registered (Testing/Python/CMakeLists.txt line 2 is commented out), so CI never exercises it.
  ```
    # Register the unittest subclass in the main script as a ctest.
    # Note that the test will also be available at runtime.
    slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)
  ```
  Suggestion: Add a proper ScriptedLoadableModuleTest class in the module script, or register Testing/Python/test_IVIMFitSlicer_roundtrip.py with slicer_add_python_unittest and install it.

### Sample dataset provenance and licence not stated
minor; license; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:962`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L962): The Sample Data entry downloads a converted clinical liver DWI series from the author's GitHub release. Neither the repository nor the README states the licence, de-identification status or consent basis for redistributing this data, so permission to distribute it is unclear even though the code itself is MIT.
  ```
      uris='https://github.com/Atakanisik/SlicerIVIMFit/releases/download/v1.0.0-data/21.MR.ep2d_diff_b50_400_800_cor_p2.IVIMkurtozis.karaciger._TRACEW_DFC.-.10.frames.MultiVolume.by.AcquisitionTime.nrrd',
  ```
  Suggestion: Document the origin, de-identification and licence/consent of the sample dataset (or replace it with the synthetic phantom), and state the licence of the 'ivimfit' dependency.

### Unreachable duplicate code after return in extract_pixel_data_safe
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:775`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L775): Lines 781-804 can never execute; the dead copy makes the function's actual behaviour (no temporary reference node for MultiVolume in the second block) hard to reason about and suggests an incomplete refactor.
  ```
      return arr, ref
      
      # 2. MultiVolume ise Labelmap modülü için geçici bir 3D referans oluştur
  ```
  Suggestion: Delete the unreachable block.
- **haiku** (minor, high confidence, quote verified) [`IVIMFitSlicer/IVIMFitSlicer.py:775`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/IVIMFitSlicer.py#L775): extract_pixel_data_safe has a second block of code after an unconditional return, which is never executed. The Temp_Scalar_Ref node is created for multivolumes and only removed on the success path in process(), so it can leak when an exception occurs.
  ```
  return arr, ref
   
   # 2. MultiVolume ise Labelmap modülü için geçici bir 3D referans oluştur
   if node.IsA("vtkMRMLMultiVolumeNode") or node.IsA("vtkMRMLSequenceNode"):
  ```
  Suggestion: Delete the dead block and clean up temporary nodes in a finally clause.

### Catalog entry tracks a moving branch
info; soundness; raised by haiku; **quote not found in source**
- **haiku** (info, high confidence, quote file not found) [`IVIMFitSlicer.json:1`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer.json#L1): scm_revision is 'main', so the code that users install can change without a catalog update. This does not indicate a defect, but the reviewed commit is not pinned.
  ```
  "scm_revision": "main",
  ```
  Suggestion: Pin scm_revision to a reviewed commit or tag, or accept branch tracking as a deliberate choice.

### Self-test not registered with CTest and sample data is external
info; utility; raised by haiku
- **haiku** (info, high confidence, quote verified) [`IVIMFitSlicer/Testing/Python/CMakeLists.txt:2`](https://github.com/Atakanisik/SlicerIVIMFit/blob/8f3b37587ab39b41b30a37e197a91c567f866981/IVIMFitSlicer/Testing/Python/CMakeLists.txt#L2): The round-trip test is described in the README but must be run manually from the Slicer Python console. The commented-out CTest registration in Testing/Python/CMakeLists.txt means the test never runs in CI.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Register the round-trip test with slicer_add_python_unittest, or document why it cannot run in CI.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
A well-documented IVIM fitting module (MIT licensed, sample data with checksum, phantom scripts, self-tests). No data exfiltration, no eval/exec, no bundled binaries. Main problems are environment-related: it runs `slicer.util.pip_install` for `ivimfit` and `pymc` into Slicer's shared Python without any user confirmation, `pymc`'s dependency chain can upgrade Slicer-bundled numpy/scipy, and it creates a `libs` folder inside Slicer's Python installation. Soundness issues: string-based version comparison, a likely malformed pip requirement string, heavy fitting on the GUI thread, and bare `except: pass` that silently yields zero maps. Sample-data provenance/licence is unstated. Recommend fixes before merge.
Not checked: The 'ivimfit' and 'pymc' packages themselves (source, licence, dependency pins) were not inspected; only the extension's use of them.; Slicer's slicer/util.py implementation of pip_install was not available, so the exact failure mode of the '--upgrade' argument is inferred.; The sample-data NRRD at the GitHub release URL and its checksum were not downloaded or verified.; The exact source revision 8f3b37587ab39b41b30a37e197a91c567f866981 could not be resolved against the repository; the catalog entry pins scm_revision 'main', so the reviewed content is the snapshot provided.; No build or runtime execution was possible; CMake configuration and module loading were assessed by reading only.
Questions for the author: Can the ivimfit/PyMC installation be made opt-in with an explicit confirmation dialog, and can it avoid upgrading numpy/scipy that Slicer bundles?; Is 'ivimfit>=0.1.7.2 --upgrade' intended as a single pip requirement string, or should --upgrade be passed as a separate option?; What is the provenance, de-identification status and licence of the sample DWI dataset hosted in the v1.0.0-data release?; Why does the module create a 'libs' folder inside the Slicer Python installation at runtime instead of relying on the documented manual setup?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
IVIMFitSlicer is a well-structured, robust, and fully documented 3D Slicer extension for IVIM diffusion MRI analysis. It includes multi-model fitting algorithms, hybrid parametric mapping, DICOM b-value extraction, sample data registration, and a comprehensive self-test suite. All checks across safety, environment, packaging, license, soundness, and utility are fully satisfied. 🟢 Recommend merge.
Not checked: Execution of unit tests against a running 3D Slicer instance (automated testing framework verified code structure and self-test suite).; Full Bayesian MCMC sampling performance under PyMC in Slicer's embedded Python environment.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
The module is a standard ScriptedLoadableModule with no network calls, no eval/exec/pickle, and a MIT license. Main concerns are runtime pip installs of ivimfit and pymc from the Run button (with a lexicographic version check that is wrong), a Windows workaround that writes into Slicer's install directory and suggests running Slicer as administrator, and many swallowed exceptions. The package is mechanically valid (CMake, EXTENSION_DEPENDS NA, build_dependencies empty), but the entry tracks a moving "main" branch. I did not inspect ivimfit or the sample-data release. Overall: minor issues to fix before listing.
Not checked: The ivimfit, pymc, and PyTensor packages and their licenses, and whether the pip installs succeed.; The sample-data release at the GitHub URL (SHA256 checksum given at line 964 was not verified), and the contents of the phantom generator scripts.; The UI file Resources/UI/IVIMFitSlicer.ui and the Icons PNG (not read).; The full test file beyond line 60, and any CI results.; The exact source revision: the reviewer did not resolve 'main' to a commit.; Whether the catalog entry JSON file exists at the root of the index (only the entry in the prompt was reviewed).


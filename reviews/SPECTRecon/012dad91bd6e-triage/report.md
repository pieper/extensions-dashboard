# AI review: SPECTRecon

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/PyTomography/SlicerSPECTRecon.git at commit `012dad91bd6e78eac23509a1dc0aec3a08749bc3`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T02:32:53Z; cost $0.08

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | minor |
| environment | concern | ok | concern |
| packaging | concern | ok | concern |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | ok | ok | ok |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: SlicerSPECTRecon is a 3D Slicer module that reconstructs SPECT projection data (OSEM/BSREM/OSMAPOSL with attenuation, PSF and scatter modelling) using the PyTomography library on the GPU, and converts SIMIND Monte Carlo output to DICOM. It targets nuclear-medicine researchers working with clinical or simulated SPECT/CT data.
- **flash-lite**: SPECTRecon is a 3D Slicer extension that provides GPU-accelerated SPECT image reconstruction using PyTomography and supports data conversion from SIMIND.
- **haiku**: SPECTRecon is a 3D Slicer scripted extension that provides GPU-accelerated SPECT reconstruction (via the PyTomography library) for projection data loaded from DICOM, plus a SIMIND-to-DICOM converter. It is aimed at academic researchers and nuclear-medicine physicists.

## Disagreements (start here)

### D1. Bundled PSF model files are not installed by CMake, so Advanced PSF fails in the installed extension
single; category packaging; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`SPECTRecon/CMakeLists.txt:21`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/CMakeLists.txt#L21): MODULE_PYTHON_RESOURCES lists only the icon, the .ui and three JSON files. The 14 files in SPECTRecon/Resources/Data/PSF_models/*.pt are never installed, yet AdvancedPSF.get_psf_operator builds a path under Resources/Data/PSF_models and calls torch.load on it (AdvancedPSF.py:26-35). In an extension-manager installation, checking 'Advanced PSF' therefore raises FileNotFoundError instead of reconstructing.
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/Icons/${MODULE_NAME}.png
    Resources/UI/${MODULE_NAME}.ui
    Resources/algorithmTestSettings.json
  ```
  Suggestion: Add the PSF model files (e.g. Resources/Data/PSF_models/*.pt) to MODULE_PYTHON_RESOURCES, or download them on demand with user consent.

### D2. Catalog entry build_dependencies is empty while the extension declares EXTENSION_DEPENDS "PyTorch"
partial; category packaging; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`CMakeLists.txt:13`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/CMakeLists.txt#L13): The extension imports PyTorchUtils and raises InstallError if the PyTorch extension is absent (SPECTRecon.py:22-25), and the catalog entry supplied for review has "build_dependencies": []. The index therefore does not declare the PyTorch extension as a dependency of this entry, so the packaged dependency metadata and the index metadata disagree and the extension manager cannot be relied on to install PyTorch first; users who install only SPECTRecon hit the InstallError path.
  ```
  set(EXTENSION_DEPENDS "PyTorch") # Specified as a list or "NA" if no dependencies
  ```
  Suggestion: Set "build_dependencies": ["PyTorch"] in the catalog entry (or remove EXTENSION_DEPENDS if it is genuinely not needed) so both declarations agree.
- **haiku** (major, high confidence, quote verified) [`CMakeLists.txt:13`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/CMakeLists.txt#L13): The module requires the PyTorch extension (SPECTRecon.py lines 22-25 import PyTorchUtils and raise if missing), and CMakeLists declares it as EXTENSION_DEPENDS. The catalog entry declares an empty build_dependencies, so the index will not build or install PyTorch as a dependency. Users may load the module without PyTorch and then hit an error on first open.
  ```
  set(EXTENSION_DEPENDS "PyTorch") # Specified as a list or "NA" if no dependencies
  ```
  Suggestion: Set build_dependencies in the catalog entry to ["PyTorch"] to match EXTENSION_DEPENDS.

### D3. Exactly pinned pip packages installed on module open, plus a silent multi-GB PyTorch download
single; category environment; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`SPECTRecon/SPECTRecon.py:29`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/SPECTRecon.py#L29): ensure_packages_installed() is called from setup() (SPECTRecon.py:152), i.e. as soon as the user opens the module, and runs slicer.util.pip_install for dill==0.3.9, torchquad==0.4.1, pytomography==3.3.2, spectpsftoolbox==0.1.0 and beautifulsoup4==4.13.3 with no confirmation dialog and no cancel button. PyTorch is installed through PyTorchUtils (correct path) but with askConfirmation=False, so a multi-gigabyte download starts without consent. The exact pins and pytomography's transitive requirements (numpy/scipy/pydicom are Slicer-bundled) can change the shared Slicer Python environment for every user of that Slicer installation.
  ```
      if not torchLogic.torchInstalled():
          torch = torchLogic.installTorch(askConfirmation=False, torchVersionRequirement = f">={minimumTorchVersion}", torchvisionVersionRequirement=f">={minimumTorchvisionVersion}")
      installed_packages = {f'{pkg.key}=={pkg.version}'for pkg in pkg_resources.working_set}
      required_packages = {
          "dill==0.3.9",
  ```
  Suggestion: Ask the user before installing (or at least before the torch download), avoid exact pins where possible, and verify/constrain pytomography's transitive requirements so Slicer-bundled numpy/scipy/pydicom are not upgraded or downgraded.

### D4. Pinned pip packages installed into Slicer's Python environment without confirmation
single; category environment; raised by haiku
- **haiku** (major, high confidence, quote verified) [`SPECTRecon/SPECTRecon.py:40`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/SPECTRecon.py#L40): On first opening the module, setup() calls ensure_packages_installed(), which pip-installs pytomography==3.3.2, torchquad, spectpsftoolbox, dill and beautifulsoup4 into the shared Slicer Python. No user confirmation is requested and the packages are not isolated. Transitive requirements can change packages Slicer relies on or other extensions use. The rubric treats installs without user confirmation as a concern.
  ```
  missing_all = required_packages - installed_packages
      num_packages = len(missing_all)
      logging.info('ensure_packages_installed called')
      for i, missing in enumerate(missing_all):
          slicer.util.pip_install(missing)
  ```
  Suggestion: Ask the user for confirmation before installing, show the package list and approximate size, and check resolved dependencies (numpy, scipy, pydicom, torch) against Slicer's bundled versions. Use the PyTorch extension's install logic for torch and avoid pulling torch from PyPI through pytomography.

### D5. Registered test script name does not match the actual file (simind_To_dicom.py vs simind_to_dicom.py)
partial; category packaging; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`SPECTRecon/Logic/CMakeLists.txt:2`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/Logic/CMakeLists.txt#L2): The repository contains SPECTRecon/Testing/Python/simind_to_dicom.py (lower-case 'to'), which is also what SPECTRecon.py:118 imports. On case-sensitive filesystems the registered ctest points at a non-existent path, so the SIMIND converter test can never run and the extension's CI test coverage silently disappears.
  ```
  slicer_add_python_unittest(SCRIPT ./../Testing/Python/simind_To_dicom.py SLICER_ARGS --no-main-window)
  ```
  Suggestion: Change the path to ./../Testing/Python/simind_to_dicom.py.
- **haiku** (minor, medium confidence, quote verified) [`SPECTRecon/Logic/CMakeLists.txt:2`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/Logic/CMakeLists.txt#L2): The CMake test entry names simind_To_dicom.py, but the file is Testing/Python/simind_to_dicom.py. The test registration fails on case-sensitive filesystems when BUILD_TESTING is on.
  ```
  slicer_add_python_unittest(SCRIPT ./../Testing/Python/simind_To_dicom.py SLICER_ARGS --no-main-window)
  ```
  Suggestion: Correct the filename to simind_to_dicom.py.

### D6. store_recons path uses volume_node before assignment, so 'store iterations' and uncertainty estimation always fail
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`SPECTRecon/Logic/SPECTReconLogic.py:171`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/Logic/SPECTReconLogic.py#L171): volume_node is only created on line 174, after it is dereferenced on line 173. Whenever the user ticks 'store iterations' (SPECTRecon.py:563 store_recons=self.ui.storeItersCheckBox.checked), reconstruct() raises UnboundLocalError after the whole reconstruction has already run, so the result is lost and the progress dialog is never closed. compute_uncertainty() depends on self.stored_recon_iters, so the uncertainty feature can never work either.
  ```
          if store_recons:  # Store information for accessing later
              
              self.stored_recon_iters[volume_node.GetID()] = [recon_algorithm_all_beds, callbacks]
          volume_node = self.create_volume_node_from_recon(reconstructed_image_multibed, files_NM, test_mode)
          progressDialog.close()
  ```
  Suggestion: Create the volume node first, then store self.stored_recon_iters[volume_node.GetID()] = [recon_algorithm_all_beds, callbacks].
- **haiku** (major, high confidence, quote verified) [`SPECTRecon/Logic/SPECTReconLogic.py:171`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/Logic/SPECTReconLogic.py#L171): When the 'store intermediate iterations' option is checked, reconstruct() reads volume_node before it is assigned, since volume_node is only created later by create_volume_node_from_recon. Any reconstruction with store_recons=True therefore fails at the end, after the full computation has run, and the result is lost.
  ```
  if store_recons:  # Store information for accessing later
  
               self.stored_recon_iters[volume_node.GetID()] = [recon_algorithm_all_beds, callbacks]
          volume_node = self.create_volume_node_from_recon(reconstructed_image_multibed, files_NM, test_mode)
  ```
  Suggestion: Move the storage after create_volume_node_from_recon and key it on the returned node's ID. Add a test covering store_recons=True.

### D7. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D8. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D9. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Broad bare except hides real errors when building the attenuation map
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`SPECTRecon/Logic/SPECTReconLogic.py:50`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/Logic/SPECTReconLogic.py#L50): Any failure in the CT-based attenuation map (wrong series selected, missing geometry, out-of-memory) is swallowed and retried as a SIMIND attenuation map, which then fails with a confusing secondary error or silently produces a wrong mu-map. Errors are not reported to the user.
  ```
              try: # typical DICOM CT
                  attenuation_map = dicom.get_attenuation_map_from_CT_slices(files_CT, file_NM, index_peak, HU2mu_technique='from_cortical_bone_fit')
              except: # if saved by SIMIND
                  attenuation_map = dicom.get_attenuation_map_from_file(files_CT[0])
  ```
  Suggestion: Catch the specific exception raised for non-CT input and report other failures with slicer.util.errorDisplay.

### Deprecated pkg_resources import at module load
minor; environment; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`SPECTRecon/SPECTRecon.py:1`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/SPECTRecon.py#L1): pkg_resources is imported at module top level and is deprecated, and newer setuptools releases may remove it. That would break the module at import time on newer Slicer Python builds.
  ```
  import slicer
  import importlib
  import pkg_resources
  ```
  Suggestion: Use importlib.metadata to list installed packages, or import pkg_resources lazily with a fallback.

### License copyright line still contains template brackets
minor; license; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`LICENSE.txt:3`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/LICENSE.txt#L3): The copyright line uses bracketed placeholders, which is a cosmetic defect in the license file. The grant itself is intact.
  ```
  Copyright (c) [2024] [Obed Dzikunu]
  ```
  Suggestion: Replace with the full copyright holder name and year.

### QComboBox currentText compared without calling it, so UI show/hide logic never matches
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SPECTRecon/SPECTRecon.py:334`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/SPECTRecon.py#L334): currentText is a bound method, so these comparisons are always False; the scatter window selectors and the Prior group box are never shown/hidden as intended (lines 334-343). Users selecting 'Energy Window' scatter correction may not see the window selectors, and the prior group box visibility does not follow the algorithm choice.
  ```
          if self.ui.spect_scatter_combobox.currentText=='Energy Window':
              self.ui.upperwindowLabel.setVisible(True)
              self.ui.lowerwindowLabel.setVisible(True)
              self.ui.spect_upperwindow_combobox.setVisible(True)
  ```
  Suggestion: Call currentText() (or use currentTextChanged signals) in hideShowItems().

### Reconstruction runs on the GUI thread with a non-cancellable progress dialog
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`SPECTRecon/SPECTRecon.py:16`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/SPECTRecon.py#L16): onReconstructButton calls self.logic.reconstruct synchronously; the only event processing is slicer.app.processEvents() inside the callbacks (Callbacks.py:12, 25). A multi-bed, multi-iteration GPU reconstruction therefore freezes the Slicer UI with no way to cancel, and any exception leaves the modal progress dialog open (see the store_recons bug above).
  ```
          progress = slicer.util.createProgressDialog()
          progress.labelText = "Reconstructing..."
          progress.value = 0
          progress.setCancelButton(None)
  ```
  Suggestion: Run the reconstruction in a CLI/worker thread (or at least keep a cancel button and close the dialog in a finally block).

### Scatter toggle checked as a widget object instead of its .checked state
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`SPECTRecon/SPECTRecon.py:513`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/SPECTRecon.py#L513): self.ui.scatter_toggle is a QCheckBox object, which is always truthy, so 'not self.ui.scatter_toggle' is always False and the scatter windows are never cleared when the user unchecks scatter correction. The same pattern appears on line 519 for the single-photopeak branch. Users who disable scatter correction can still get scatter estimates applied, silently changing quantification.
  ```
              if not self.ui.scatter_toggle: # enforce none if not checked
                  upperwindow_idx = lowerwindow_idx = [None] * num_peaks
  ```
  Suggestion: Use self.ui.scatter_toggle.checked in both places.
- **haiku** (minor, medium confidence, quote verified) [`SPECTRecon/SPECTRecon.py:513`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/SPECTRecon.py#L513): The guard tests the widget object rather than its checked state. The widget is always truthy, so the 'enforce none' branch never runs. In multi-photopeak mode, scatter windows are kept even when scatter correction is unchecked.
  ```
  if not self.ui.scatter_toggle: # enforce none if not checked
                   upperwindow_idx = lowerwindow_idx = [None] * num_peaks
  ```
  Suggestion: Use self.ui.scatter_toggle.checked.

### Temporary DICOM directories are created but never removed
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SPECTRecon/Logic/VolumeUtils.py:7`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/Logic/VolumeUtils.py#L7): create_volume_node_from_recon (SPECTReconLogic.py:216-221) creates a temp directory per reconstruction and never deletes it; removeNode() exists but is never called. Every reconstruction leaves DICOM copies of the reconstructed patient image in the system temp folder indefinitely, which is a privacy/hygiene issue on shared workstations.
  ```
  def createTempDir():
      return tempfile.mkdtemp()
  ```
  Suggestion: Delete the temporary directory (shutil.rmtree) after the volume is loaded, e.g. in a finally block.

### Temporary DICOM folders with patient data are never removed
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`SPECTRecon/Logic/SPECTReconLogic.py:216`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/Logic/SPECTReconLogic.py#L216): Reconstructed DICOM slices are written to a fresh temp directory and loaded into the database, but the directory is never deleted. Patient-identifying DICOM files remain in the system temp location after use. removeNode with its dir-cleanup option exists but is unused.
  ```
  temp_dir = createTempDir()
          for i, dataset in enumerate(recon_ds):
              temp_file_path = os.path.join(temp_dir, f"temp_{i}.dcm")
              dataset.save_as(temp_file_path)
  ```
  Suggestion: Remove the temp directory after the DICOM import completes (try/finally with shutil.rmtree), or write directly to the Slicer DICOM database path.

### Test code hard-codes CUDA device
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`SPECTRecon/Testing/Python/reconstruction.py:191`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/Testing/Python/reconstruction.py#L191): The tests move reference tensors to "cuda" unconditionally, so they fail on CPU-only machines and on any non-CUDA GPU, even though pytomography.device is used elsewhere. This makes the registered ctests unreliable across the build farm.
  ```
          mse_upper = torch.sum((attenuation_map_upper.to("cuda")-attenuation_map1)**2)/2
  ```
  Suggestion: Use pytomography.device (or the device of the computed tensor) instead of the literal "cuda".

### torch.load without weights_only on bundled and downloaded .pt files
minor; safety; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`SPECTRecon/Logic/AdvancedPSF.py:29`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/Logic/AdvancedPSF.py#L29): torch.load with the default pickle-based loader executes arbitrary code embedded in the file. The bundled PSF parameter files are trusted repository content, but the same pattern is used in the tests on archives downloaded from Zenodo (reconstruction.py:187-188, 259-260, 267-268), so a compromised or substituted download would execute code in the user's Slicer process. No evidence of malicious content was found in the committed .pt files (they are small, ~1.6-3 KB parameter tensors).
  ```
      gauss_amplitude_params = torch.load(path+'gauss_amplitude.pt')
      gauss_sigma_params = torch.load(path+'gauss_sigma.pt')
  ```
  Suggestion: Pass weights_only=True (or map_location plus weights_only) when loading these parameter tensors, and verify checksums of downloaded test data.

### Documentation links point to a different repository name than the catalog entry
info; utility; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`README.md:3`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/README.md#L3): The catalog entry points to https://github.com/PyTomography/SlicerSPECTRecon.git while README/User_Manual/CONTRIBUTING link to PyTomography/Slicer and PyTomography/slicer_spect_recon. Users following the manual may clone a different repository than the one the extension manager builds, which is confusing but not a functional defect.
  ```
  This is the official repository for the `Slicer` extension `SlicerSPECTRecon`. **For details on how to use, see the [user manual](https://github.com/PyTomography/Slicer/blob/main/User_Manual.md) and the [associated youtube video tutorial](https://www.youtube.com/watch?v=DzV1soWTzEA)**
  ```
  Suggestion: Update the documentation links to the canonical repository URL.

### Provenance and license of bundled PSF model weights not documented
info; utility; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`SPECTRecon/Logic/AdvancedPSF.py:9`](https://github.com/PyTomography/SlicerSPECTRecon/blob/012dad91bd6e78eac23509a1dc0aec3a08749bc3/SPECTRecon/Logic/AdvancedPSF.py#L9): The extension ships 14 .pt parameter files for two collimator models but neither README nor the manual states how they were generated, on what data, or under which license. For an AI/parameter-fitting component used in quantitative imaging this is a documentation gap rather than a distribution blocker, since the extension itself is MIT.
  ```
  psf_operator_dict = {
      'GI-HEGP @ 440 keV': 'params_440keV_GIHEGP_256shift_sparse_DW_pyrex66_1DR',
      'SY-HE @ 440 keV': 'params_440keV_SYHE_256shift_sparse_DW_pyrex66_1DR'
  }
  ```
  Suggestion: Document the origin, fitting data and license of the PSF parameter files in the README or User_Manual.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Well-documented research extension (manual, tutorial, Zenodo sample data, JOSS paper, tests, explicit non-clinical disclaimer) with MIT licensing and no telemetry or data exfiltration. However the catalog entry declares no build_dependencies while the CMakeLists requires the PyTorch extension, the bundled PSF model files under Resources/Data are not installed by CMake (Advanced PSF breaks in the installed extension), a test registration points at a non-existent file name, and the module pip-installs several exactly pinned packages plus a silent multi-GB PyTorch download when the module is opened. There are also concrete code bugs (store-iterations path raises UnboundLocalError, scatter toggle ignored). Do not merge yet: fix the dependency declaration and the missing resource install first; the remaining items are non-blocking suggestions.
Not checked: Could not verify the exact source revision: the catalog entry uses scm_revision "main" (a moving branch), so the reviewed content is the snapshot provided, not a pinned commit.; Could not inspect the transitive requirements of pytomography==3.3.2, torchquad==0.4.1 and spectpsftoolbox==0.1.0 (no network access), so whether they upgrade/downgrade Slicer-bundled numpy/scipy/pydicom is unverified.; Could not inspect the binary contents of the 14 bundled .pt PSF parameter files or the PNG images; only their sizes were listed.; Could not inspect SPECTRecon/Resources/UI/SPECTRecon.ui (82 KB) in detail, so widget names referenced in SPECTRecon.py were not cross-checked against the .ui file.; Could not run the extension, its tests, or any build; no CI results were available.; Could not verify the Zenodo sample/test data (records 14172228, 14190900) or the Google Drive sample links in Resources/sample_data.txt.; Could not verify the license terms of the PyTomography library and its external collimator/PSF data referenced by the extension.
Questions for the author: Should the catalog entry declare "build_dependencies": ["PyTorch"] to match EXTENSION_DEPENDS in CMakeLists.txt?; Are the PSF model files in Resources/Data/PSF_models intended to be installed with the extension, and if so can they be added to MODULE_PYTHON_RESOURCES?; Can the pip installs be made user-confirmed and the exact pins relaxed, and has pytomography's effect on Slicer-bundled numpy/scipy/pydicom been checked?; What is the provenance and license of the bundled PSF parameter files?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
SPECTRecon is a well-implemented 3D Slicer extension for GPU-accelerated SPECT image reconstruction using PyTomography. It properly depends on PyTorch via PyTorchUtils, includes an MIT license, provides thorough documentation and user guides, and follows Slicer development best practices. Recommend merge.
Not checked: External test dataset files on Zenodo / Google Drive

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
No malicious or concealed behavior found in the files read; the medical-use disclaimer is present and the MIT license is included. The main problems are admission and quality issues: the catalog entry has build_dependencies [] while CMakeLists sets EXTENSION_DEPENDS "PyTorch", the module pip-installs pinned packages into Slicer's Python environment on first open without confirmation, and the store_recons path in SPECTReconLogic.py references volume_node before it is assigned. These need fixes before the extension is offered to users. I could not run anything or fetch the source revision, so the review rests on the provided files.
Not checked: The source at scm_revision 'main' was not fetched, so the revision reviewed is unknown; only the provided files were read.; PSF model .pt files (torch.load) were not inspected for content; they are read with torch.load on bundled files.; Remaining files such as SPECTRecon.ui, the icon, and the rest of reconstruction.py test logic were not read in full.; The PyTorchUtils, pytomography and spectpsftoolbox behavior and licenses were not verified against upstream packages.; No build, install, or test was run, and no CI reports were available.; Licensing terms of the bundled PSF model data and the zenodo test datasets were not verified.


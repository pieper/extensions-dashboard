# AI review: DICOMSpectRecon

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/4burakfe/SlicerDICOMSpectRecon.git at commit `d9d1864c61f23c0830359c31f39f297da2400b22`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:27:02Z; cost $0.05

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | concern | ok | minor |
| packaging | ok | ok | ok |
| license | ok | ok | ok |
| soundness | minor | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: A Slicer extension for nuclear-medicine users that turns raw SPECT projection series from the DICOM browser into reconstructed volumes (OSEM/BSREM/FBP via PyTomography, with CT attenuation, energy-window scatter, resolution recovery, gating, motion correction) plus optional Bq/ml and SUV quantification from a camera calibration library.
- **flash-lite**: DICOMSpectRecon provides DICOM SPECT reconstruction and quantification in 3D Slicer using PyTomography and PyTorch, supporting OSEM, BSREM, and FBP reconstructions with CT attenuation and scatter correction, multi-bed stitching, and camera calibration.
- **haiku**: A 3D Slicer extension that reconstructs NM SPECT projection series from the DICOM browser using PyTomography (OSEM, BSREM, FBP, with CT attenuation, scatter and resolution recovery), plus a SPECT Calibration module for Bq/ml and SUV and a SPECT Collimators library module. It is aimed at nuclear medicine researchers and physicists.

## Disagreements (start here)

### D1. PyTomography installed with --upgrade while only torch is constrained
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`DICOMSpectRecon/DICOMSpectRecon.py:664`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/DICOMSpectRecon/DICOMSpectRecon.py#L664): The constraint file pins only torch. `pip install --upgrade pytomography>=4.0,<5` will also upgrade any dependency that does not satisfy PyTomography's requirements, which for PyTomography 4 includes numpy, scipy and pydicom - packages Slicer bundles and links against. A user who accepts the install prompt can therefore end up with a numpy/scipy that breaks Slicer's own modules and other extensions, for the rest of that Slicer installation. The user is told only that 'Your PyTorch installation will not be changed'.
  ```
      torchVersion = metadata.version("torch")
      with tempfile.TemporaryDirectory() as tempDir:
          constraints = os.path.join(tempDir, "keep-torch.txt")
          with open(constraints, "w") as f:
              f.write(f"torch=={torchVersion}\n")
          # List form: the constraints path is passed as one argument even if it contains spaces
  ```
  Suggestion: Add the Slicer-bundled packages to the same constraints file (e.g. numpy, scipy, pydicom, SimpleITK, vtk, requests at their installed versions) or install with `--no-deps` plus an explicit, reviewed dependency list, and state in the confirmation dialog that other packages may be installed.
- **haiku** (minor, low confidence, quote verified) [`DICOMSpectRecon/DICOMSpectRecon.py:668`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/DICOMSpectRecon/DICOMSpectRecon.py#L668): The install is user-confirmed and torch is held at its installed build, which is good. But the constraint file only mentions torch, so PyTomography's own requirements could upgrade or downgrade packages Slicer bundles (numpy, SimpleITK, pydicom, scipy), affecting Slicer for users who never open this module. I could not verify PyTomography's dependency list from the repo.
  ```
  f.write(f"torch=={torchVersion}\n")
  # List form: the constraints path is passed as one argument even if it contains spaces
  slicer.util.pip_install(["--upgrade", PYTOMOGRAPHY_REQUIREMENT, "--constraint", constraints])
  ```
  Suggestion: Also constrain numpy, SimpleITK, pydicom and scipy to their currently installed versions in the same constraints file, or document the expected impact and test a clean Slicer install with PyTomography 4.

### D2. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### Drift check failures are silently ignored
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`DICOMSpectRecon/SPECTCalibration.py:75`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/DICOMSpectRecon/SPECTCalibration.py#L75): If the calibration library cannot be read, the user gets no drift comparison and no indication that the check was skipped, which matters for a quantitative calibration workflow where a large drift is the main warning sign.
  ```
                      try:
                          drift = quant.driftMessage(record, quant.loadLibrary(quant.calibrationLibraryPath()))
                          if drift:
                              messages.append(drift)
                      except Exception:
                          pass
  ```
  Suggestion: Log the exception and append an info message such as 'drift check skipped: library unreadable'.

### Fixed temporary filename in collimator library save can collide and leave a partial file
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`DICOMSpectRecon/DICOMSpectReconLib/collimators.py:196`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/DICOMSpectRecon/DICOMSpectReconLib/collimators.py#L196): saveLibrary writes to path + '.tmp' and then os.replace()s it. Two Slicer instances saving at once would write to the same temp file and could interleave, and an exception during json.dump leaves the .tmp file behind. The library is a shared user file, so a corrupted or lost edit is possible. The calibration library in quantification.py already uses mkstemp, so this is inconsistent.
  ```
  tmp = path + ".tmp"
      with open(tmp, "w", encoding="utf-8") as f:
          json.dump({"version": LIBRARY_VERSION, "collimators": clean}, f, indent=2)
      os.replace(tmp, path)
  ```
  Suggestion: Use tempfile.mkstemp in the same folder, as quantification._writeLibrary does, and remove the temp file on failure.

### Module-level caches keyed by file path are never cleared
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`DICOMSpectRecon/DICOMSpectRecon.py:68`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/DICOMSpectRecon/DICOMSpectRecon.py#L68): These dictionaries accumulate one entry per examined NM file for the lifetime of the Slicer session and are only partially cleared in addMultiBedLoadables (lines 225-226). In a long session with many studies they grow without bound, and stale CT/bed pairings from an earlier examine can be reused by load() (lines 376-379) if the browser serves cached loadables.
  ```
  # NM projection file -> (CT file list, how it was matched), filled in during examine()
  _CT_FOR_NM_FILE = {}
  # Multi-bed: header facts of NM files (nmdata.bedInfo), the beds found for each NM file, the single-bed
  # files that are already part of a multi-bed loadable of the same selection, and the groups loaded
  _BED_INFO = {}
  _BEDS_FOR_NM_FILE = {}
  ```
  Suggestion: Clear the caches at the start of examine() or key them on the study/series UID and drop entries for series no longer in the database.

### No automated tests and no clinical/research-use disclaimer
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:91`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/README.md#L91): The README documents the workflow well, but the only tests are manual scripts under Testing/PyTomography4 (run_recon.py, compare.py, check_beds.py) and there is no statement that the reconstructions and Bq/ml/SUV values are for research use and not validated for clinical decisions - relevant for a quantitative nuclear-medicine tool.
  ```
  1. Import the study into the DICOM database and select the NM SPECT series.
  2. Load opens the reconstruction window: projections in cine, reconstruction and CT fusion previews,
     and the settings (OSEM, BSREM or FBP, attenuation, scatter, filter, scaling, quantification).
  3. Press **Reconstruct**, check the preview, then **Load into Slicer**.
  ```
  Suggestion: Add a short 'not for clinical use / research only' note and, if feasible, a small headless test that runs the pure-numpy parts (quantification, collimators, FBP windows) in CI.

### No clinical or research-use disclaimer for quantitative and diagnostic-style output
minor; utility; raised by haiku
- **haiku** (minor, medium confidence, quote verified, other lines) [`README.md:82`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/README.md#L82): The README describes Bq/ml and SUV quantification, dosimetry traceability and clinical-style workflows (e.g. 'the usual clinical choice'), but contains no statement that outputs are unvalidated for clinical decisions or that the user must verify calibration. Users may trust the numbers without checking. This is a documentation gap, not a code defect.
  ```
  - **Quantification (optional)**: with a calibration factor (cps/MBq) made in the **SPECT Calibration**
    module, the static image is converted to Bq/ml and optionally to SUV:
  ```
  Suggestion: Add a 'Research use only / not validated for clinical decisions' disclaimer and a short validation note (phantom checks, versioning) to the README and the module helpText.

### Reconstruction and preview work runs on the GUI thread
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`DICOMSpectRecon/DICOMSpectReconLib/dialog.py:2089`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/DICOMSpectRecon/DICOMSpectReconLib/dialog.py#L2089): The OSEM/BSREM/FBP loop is driven from the dialog with slicer.app.processEvents() to keep the UI responsive, so a long reconstruction blocks the event loop between callbacks and can make Slicer appear hung; the abort callback (reconstruction.py:149-157) mitigates this but the work is not moved off the GUI thread.
  ```
      def log(self, message):
          logging.info(message)
          self.logBox.appendPlainText(message)
          self.logBox.verticalScrollBar().setValue(self.logBox.verticalScrollBar().maximum)
          slicer.app.processEvents()
  ```
  Suggestion: Run the reconstruction in a worker thread (or a CLI) and report progress through signals, as other Slicer reconstruction extensions do.

### Silent exception swallowing when attaching the CT volume to subject hierarchy
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified, other lines) [`DICOMSpectRecon/DICOMSpectRecon.py:118`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/DICOMSpectRecon/DICOMSpectRecon.py#L118): If the subject-hierarchy check or insertion fails, the error is dropped with a bare except and pass. The CT then loads without DICOM metadata, and the user gets no message, which makes the later fusion or calibration steps hard to debug.
  ```
                            except Exception:
                                pass
                            return node
  ```
  Suggestion: Log the traceback with logging.warning, as the surrounding code does elsewhere in this file.

### sys.path mutated at module import in three modules
minor; environment; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DICOMSpectRecon/DICOMSpectRecon.py:60`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/DICOMSpectRecon/DICOMSpectRecon.py#L60): The hidden module is imported when Slicer starts, so this prepends the module folder to sys.path for the whole process (same pattern in SPECTCalibration.py:28-30 and SPECTCollimators.py:23-25). Any file in that folder whose name shadows a stdlib or Slicer module would then win the import; today the folder only holds the extension's own files, so the practical risk is low.
  ```
  _MODULE_DIR = os.path.dirname(os.path.abspath(globals().get("__file__", "") or "."))
  if globals().get("__file__") and _MODULE_DIR not in sys.path:
      sys.path.insert(0, _MODULE_DIR)
  ```
  Suggestion: Append instead of insert, or rely on the extension build's normal package layout and drop the sys.path change.

### Loadable confidence deliberately set above 1.0 to outrank other DICOM plugins
info; soundness; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`DICOMSpectRecon/DICOMSpectRecon.py:355`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/DICOMSpectRecon/DICOMSpectRecon.py#L355): The value is documented and only applied to files whose ImageType contains TOMO/GATED TOMO, so it does not hijack other modalities; it does mean the reconstruction loadable always wins over any other plugin offering the same NM series, which users should be aware of.
  ```
              # Above 1.0: the DICOM browser keeps only the highest confidence loadables of each series
              # (DICOMUtils.selectHighestConfidenceLoadables, grouped by the series of their first file).
              # With two NM series selected, MultiVolumeImporter lumps them into one multi-series
              # loadable of confidence 1.0, which would otherwise deselect the reconstruction of one of
              # them; the scalar volume plugin offers less than that.
              loadable.confidence = 1.05
  ```
  Suggestion: None required; consider mentioning in the README that the reconstruction loadable is preselected for TOMO series.

### Package installation is gated by an explicit confirmation dialog
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`DICOMSpectRecon/DICOMSpectRecon.py:591`](https://github.com/4burakfe/SlicerDICOMSpectRecon/blob/d9d1864c61f23c0830359c31f39f297da2400b22/DICOMSpectRecon/DICOMSpectRecon.py#L591): Nothing is installed at import or startup: PyTorch comes only from PyTorchUtils (lines 623-655) and PyTomography only after this prompt, which is the behaviour the review policy asks for. The prompt text is however incomplete about side effects (see the environment finding).
  ```
              if not slicer.util.confirmOkCancelDisplay(
                      "PyTomography is required for SPECT reconstruction but is not installed.\n\n"
                      "Install it now? Your PyTorch installation will not be changed."):
                  return False
              with slicer.util.WaitCursor():
                  _installPytomographyKeepingTorch()
  ```
  Suggestion: Keep the confirmation; extend its wording to mention that PyTomography's own dependencies may be installed or upgraded.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Well-structured, documented extension: MIT license, CMake installs every Python file, EXTENSION_DEPENDS matches the PyTorch build dependency, PyTorch is installed only through PyTorchUtils, and I found no data transmission, unsafe deserialization or obfuscation. The main issue is environment hygiene: PyTomography is installed with `pip install --upgrade` while only torch is constrained, so Slicer-bundled numpy/scipy/pydicom can be replaced. Secondary: `sys.path.insert` at import, reconstruction on the GUI thread, unbounded module-level caches, a few swallowed exceptions, no automated tests and no clinical-use disclaimer. Large parts of the library (nmdata, motion, most of dialog.py) were not read.
Not checked: DICOMSpectRecon/DICOMSpectReconLib/nmdata.py (49 KB) was not read - DICOM header parsing, energy windows, gating and CT matching logic are unreviewed.; DICOMSpectRecon/DICOMSpectReconLib/motion.py and motiondialog.py were not read - motion detection and the shift dialog are unreviewed.; Most of DICOMSpectRecon/DICOMSpectReconLib/dialog.py (2921 lines) was not read; only the CT selection, collimator and motion-correction sections were inspected.; reconstruction.py lines 200-998, quantification.py lines 300-522 and collimators.py lines 1-90/230-292 were not read.; Testing/PyTomography4/*.py scripts were not read.; PyTomography's license and the redistribution terms of the SIMIND collimator database shipped with it could not be verified from this repository.; The catalog entry's scm_revision is the branch `main`; I could not verify that commit d9d1864 is the current tip or that the extension builds on any platform (no build or CI evidence available).
Questions for the author: Can the PyTomography install be constrained to the numpy/scipy/pydicom versions Slicer bundles (or installed with --no-deps), so accepting the prompt cannot replace Slicer's own packages?; Would you add a short research-use-only disclaimer to the README, given the Bq/ml and SUV outputs?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The DICOMSpectRecon extension is well-structured, implements nuclear medicine SPECT reconstruction and quantification workflows using PyTomography and PyTorch correctly, respects Slicer environment conventions (leveraging PyTorchUtils and pip constraints for PyTorch), and includes clear licensing. 🟢 Recommend merge
Not checked: External repository code in DICOMSpectReconLib files (dialog.py, reconstruction.py, nmdata.py, motion.py, motiondialog.py, quantification.py, collimators.py) beyond structural and dependency checks; Exact behavior of PyTomography reconstruction execution in runtime environment

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
I read the extension entry, CMakeLists, the main module, the calibration and collimator modules, most of the reconstruction helpers, the README and LICENSE. I found no malicious or concealed behaviour, no telemetry or network transmission, and no eval/pickle/unsafe deserialization. PyTorch is obtained only through the PyTorch extension, and PyTomography is installed on user confirmation with torch pinned by a constraint. The main gaps are soft: no clinical or research-use disclaimer, a few swallowed exceptions, a fixed temp filename in one save path, and the possibility that the pip install of PyTomography changes Slicer-bundled packages that I could not verify. Overall: minor issues.
Not checked: Did not read dialog.py (about 155 KB), motion.py, motiondialog.py, nmdata.py, most of quantification.py, or the rest of reconstruction.py and collimators.py, so the internal logic, the DICOM parsing and the GUI-thread handling are not reviewed.; Did not check the upstream PyTomography license or its dependency list, so the environment impact of pip install is unverified.; Did not resolve the scm_revision 'main' to a commit, and did not inspect the Testing/PyTomography4 scripts in detail.; Did not run anything. No CI results were available to me, so no build or load evidence is available.; Did not check the icon resources or screenshots in the repo.
Questions for the author: Does PyTomography 4's dependency set change any numpy, SimpleITK, pydicom or scipy version that Slicer bundles? If so, should those be constrained too?; Please add a research-use or clinical validation disclaimer to the README and helpText.; Is the calibration library written from more than one workstation? If so, is the mkstemp approach also used for the collimator library?


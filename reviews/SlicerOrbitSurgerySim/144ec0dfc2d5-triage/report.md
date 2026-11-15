# AI review: SlicerOrbitSurgerySim

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/chz31/SlicerOrbitSurgerySim at commit `144ec0dfc2d52484d6a59ee1404d2a0933a08c08`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T17:30:20Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | blocking | minor | concern |
| environment | concern | minor | concern |
| packaging | minor | ok | minor |
| license | minor | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | minor issues | needs fixes |

## What each reviewer says the extension does

- **deepseek**: SlicerOrbitSurgerySim is a 3D Slicer extension for orbital fracture repair planning: PlateRegistration registers preformed orbital plates to fractured/reconstructed orbits and computes plate-fit metrics, while MirrorOrbitRecon reconstructs a fractured orbit by mirroring the contralateral side. It targets oral/maxillofacial surgeons and researchers doing virtual plate selection and comparison.
- **flash-lite**: SlicerOrbitSurgerySim is a 3D Slicer extension providing modules for interactive orbital plate registration, fit evaluation, and contralateral orbit mirroring.
- **haiku**: A 3D Slicer extension for registering preformed orbital fracture plates to orbit models and computing plate-fit metrics (PlateRegistration), plus a mirror-based orbit reconstruction tool (MirrorOrbitRecon) that depends on SlicerMorph. It is aimed at maxillofacial researchers and clinicians doing virtual planning.

## Disagreements (start here)

### D1. Registered unit test cannot pass (wrong sample name, nonexistent logic.process)
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified, other lines) [`MirrorOrbitRecon/MirrorOrbitRecon.py:57`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/MirrorOrbitRecon/MirrorOrbitRecon.py#L57): registerSampleData registers the sample as "orbitMirrorReconSampleData", not "MirrorOrbitRecon1", and MirrorOrbitReconLogic has no `process` method (line 745 calls logic.process(inputVolume, outputVolume, threshold, True)). MirrorOrbitRecon/CMakeLists.txt:27 registers this class as a ctest, so the extension's own test always fails, giving no regression signal.
  ```
          registerSampleData()
          inputVolume = SampleData.downloadSample("MirrorOrbitRecon1")
          self.delayDisplay("Loaded test data set")
  ```
  Suggestion: Replace the template test with a real test of the mirror/registration logic, or remove the test registration until one exists.

### D2. Sample data downloaded from a moving branch with no checksum
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`PlateRegistration/PlateRegistration.py:87`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/PlateRegistration.py#L87): The data users load into the scene (and, per the previous finding, code that is executed) comes from `refs/heads/main` with `checksums=None`, so the content can change silently after review and there is no integrity check on download. Combined with the setup.py execution this removes any guarantee about what runs on the user's machine.
  ```
          uris="https://github.com/chz31/orbitSurgeySim_sampleData/raw/refs/heads/main/plateRegistrationSampleData.zip",
          loadFiles=False,
          fileNames="PlateRegistrationSampleData.zip",
          loadFileType='ZipFile',
          checksums=None,
  ```
  Suggestion: Reference a fixed commit/tag and supply the SHA256 checksum in `checksums`.
- **haiku** (minor, high confidence, quote verified) [`PlateRegistration/PlateRegistration.py:87`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/PlateRegistration.py#L87): Both registerSampleData functions set checksums=None and point to refs/heads/main URLs. The content can change without notice, so the sample data the user gets is not reproducible or verified, and it feeds the setup.py execution above.
  ```
  uris="https://github.com/chz31/orbitSurgeySim_sampleData/raw/refs/heads/main/plateRegistrationSampleData.zip",
          loadFiles=False,
          fileNames="PlateRegistrationSampleData.zip",
          loadFileType='ZipFile',
          checksums=None,
  ```
  Suggestion: Pin the download to a release tag or commit and publish a SHA-256 checksum that Slicer's downloadFile can verify.

### D3. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite minor, haiku concern

### D4. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings all reviewers agree on

### Sample-data downloader executes a setup.py downloaded from a GitHub branch without checksum
blocking; safety; raised by deepseek, flash-lite, haiku
- **deepseek** (blocking, high confidence, quote verified) [`MirrorOrbitRecon/MirrorOrbitRecon.py:100`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/MirrorOrbitRecon/MirrorOrbitRecon.py#L100): When the user clicks the sample-data entry, downloadSampleDataInFolder downloads a ZIP from https://github.com/chz31/orbitSurgeySim_sampleData/raw/refs/heads/main/... with `checksums=None` (line 79) and then imports and runs any `setup.py` found in the chosen folder. Whoever controls that repository (or a compromised account / MITM without checksum verification) can execute arbitrary Python inside the user's Slicer process with the user's privileges. The same code exists in PlateRegistration/PlateRegistration.py:112-117. It currently fails only because `importlib` is not imported in either file, which is a one-line fix away from being live.
  ```
        filepath=destFolderPath+"/setup.py"
        if (os.path.exists(filepath)):
          spec = importlib.util.spec_from_file_location("setup",filepath)
          setup = importlib.util.module_from_spec(spec)
          spec.loader.exec_module(setup)
          setup.setup()
  ```
  Suggestion: Remove the setup.py execution entirely. If post-download setup is needed, implement it in the extension's own code, and pin the sample data to a fixed commit with a published SHA256 checksum passed to downloadFile.
- **flash-lite** (major, high confidence, quote verified) [`MirrorOrbitRecon/MirrorOrbitRecon.py:100`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/MirrorOrbitRecon/MirrorOrbitRecon.py#L100): The sample data downloader automatically executes arbitrary python code (`setup.py`) found inside downloaded sample data zips from remote repositories, which represents a potential arbitrary code execution risk if untrusted sample data archives are loaded.
  ```
      filepath=destFolderPath+"/setup.py"
      if (os.path.exists(filepath)):
        spec = importlib.util.spec_from_file_location("setup",filepath)
        setup = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(setup)
        setup.setup()
  ```
  Suggestion: Avoid executing arbitrary Python scripts found within downloaded sample data zips, or perform strict validation.
- **haiku** (major, high confidence, quote verified) [`PlateRegistration/PlateRegistration.py:112`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/PlateRegistration.py#L112): After the user picks a folder, downloadSampleDataInFolder downloads the sample zip with checksum None and then, if setup.py exists in the destination folder, loads it with spec.loader.exec_module and calls setup.setup(). The zip comes from a moving branch (refs/heads/main) of a third-party GitHub repo with no integrity check, so anyone who controls that repo or the branch gets arbitrary code execution in the user's Slicer process. The same pattern appears in MirrorOrbitRecon. This is a download-and-run path that the extension's advertised function (plate registration) does not need.
  ```
  filepath=destFolderPath+"/setup.py"
    if (os.path.exists(filepath)):
      spec = importlib.util.spec_from_file_location("setup",filepath)
      setup = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(setup)
  ```
  Suggestion: Remove the setup.py execution entirely, or require a pinned checksum for the sample archive and explicit user confirmation before running any code from it. Do the same in MirrorOrbitRecon/MirrorOrbitRecon.py lines 100-105.

### pandas and matplotlib installed into Slicer's Python without asking the user
major; environment; raised by deepseek, flash-lite, haiku
- **deepseek** (major, high confidence, quote verified) [`PlateRegistration/PlateRegistration.py:210`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/PlateRegistration.py#L210): Simply opening the PlateRegistration module modifies Slicer's shared Python environment with unpinned pip installs, without a consent prompt. Unpinned installs can upgrade shared packages (e.g. numpy) that Slicer and other extensions rely on, affecting users who never use this module. The tutorial even tells users 'Required Python packages will be installed automatically' (Tutorials/00_Quick_Tutorial.md:84-86).
  ```
          if needInstall:
              progressDialog = slicer.util.createProgressDialog(
                  windowTitle="Installing...",
                  labelText="Installing Python dependencies. This may take a minute...",
                  maximum=0,
              )
  ```
  Suggestion: Ask the user for confirmation before installing, pin compatible versions, and prefer declaring the dependency so the extension build/Extension Manager handles it.
- **flash-lite** (minor, medium confidence, quote verified, other lines) [`PlateRegistration/PlateRegistration.py:204`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/PlateRegistration.py#L204): Packages (`pandas`, `matplotlib`) are installed via `pip_install` at runtime upon opening the module widget, rather than being declared purely in metadata or pre-bundled.
  ```
              try:
                  slicer.util.pip_install(["pandas"])
                  slicer.util.pip_install(["matplotlib"])
              except:
  ```
  Suggestion: Declare required dependencies in extension metadata or handle package installation gracefully.
- **haiku** (minor, medium confidence, quote verified) [`PlateRegistration/PlateRegistration.py:203`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/PlateRegistration.py#L203): When the PlateRegistration widget is first created and pandas or matplotlib cannot be imported, it installs them with pip without asking the user. This happens in the user's shared Slicer environment, and the installs are unpinned. Matplotlib is also installed again on demand inside plotScalarHistogram. The effect is limited to Slicer installs where the packages are missing, but the user is not informed before modifying the environment.
  ```
  needInstall = False
          try:
              import pandas
              import matplotlib
          except ModuleNotFoundError:
              needInstall = True
  ```
  Suggestion: Ask for user confirmation before pip_install, state the packages and their size, and avoid unpinned installs in the shared environment. Check whether these packages are already bundled with the Slicer version targeted (5.10).


## Findings from some reviewers

### Bare except blocks silently swallow failures
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`PlateRegistration/PlateRegistration.py:204`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/PlateRegistration.py#L204): This pattern (also MirrorOrbitRecon.py:392-399, 480-487, 520-527, 545-548) hides real errors such as a missing display node or an unset parameter, so the module can silently do nothing when the user clicks a button instead of reporting the problem. Example: onResetPushButton calls `self.halfModelRigidNode.GetDisplayNode.SetVisibility(False)` (missing parentheses, line 546) and the resulting AttributeError is swallowed.
  ```
          try:
              self._parameterNode.fractureOrbitModel.GetDisplayNode().SetVisibility(False)
          except:
              pass
  ```
  Suggestion: Catch specific exceptions and report unexpected ones to the user (slicer.util.errorDisplay) or log them.

### Half-model affine registration uses the full-skull point sets
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified, other lines) [`MirrorOrbitRecon/MirrorOrbitRecon.py:221`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/MirrorOrbitRecon/MirrorOrbitRecon.py#L221): onRigidMirroredHalfButton stores the half-model point sets in self.sourcePointsHalf/self.targetPointsHalf (line 466), but onAffineMirroredHalfButton passes the full-skull self.sourcePoints/self.targetPoints. The affine transform applied to the half model is therefore computed from the wrong point clouds, producing a silently wrong registration result that the user may then use for fit metrics.
  ```
          logic = MirrorOrbitReconLogic()
          transformation, translation = logic.CPDAffineTransform(self.halfModelaffineNode, self.sourcePoints, self.targetPoints)
  ```
  Suggestion: Use self.sourcePointsHalf and self.targetPointsHalf here.

### Long registrations run on the GUI thread without progress or cancellation
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`MirrorOrbitRecon/MirrorOrbitRecon.py:344`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/MirrorOrbitRecon/MirrorOrbitRecon.py#L344): FPFH/RANSAC/ICP registration and the CPD affine step (line 372) run synchronously in the button slot with no progress dialog or cancellation, so Slicer appears frozen for the duration on large skull meshes. The same applies to the heatmap/projection batch operations in PlateRegistration.
  ```
          #Perfrom itk rigid registration
          logic = MirrorOrbitReconLogic()
          self.sourcePoints, self.targetPoints, scalingTransformNode, ICPTransformNode = logic.ITKRegistration(self.mirroredSkullRigidNode,
  ```
  Suggestion: Run the heavy work in a CLI or a worker thread with progress reporting, or at minimum show a progress dialog with processEvents.

### Module help text and category are still template placeholders
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`PlateRegistration/PlateRegistration.py:44`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/PlateRegistration.py#L44): Both modules are listed under the "Examples" category and their help text still says 'This is an example of scripted loadable module bundled in an extension. See more information in <a href="https://github.com/organization/projectname#PlateRegistration">module documentation</a>.' (lines 51-54; MirrorOrbitRecon.py:38-48 identical). Users looking for a planning tool will not find it, and the in-app help points to a nonexistent URL.
  ```
          self.parent.categories = [translate("qSlicerAbstractCoreModule", "Examples")]
  ```
  Suggestion: Set a real category (e.g. Planning) and write help text linking to the tutorials in this repository.

### No research-use / clinical disclaimer for a surgical planning tool
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:4`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/README.md#L4): The README markets the tool for 'clinical decision support' and plate ranking for surgery, but contains no statement that it is not cleared for clinical use and that results must be verified by a clinician. Users may treat computed fit metrics as validated surgical guidance.
  ```
  **SlicerOrbitSurgerySim** is a 3D Slicer extension for **interactive registration, evaluation, and comparison of preformed orbital plates** used in the repair of orbital fractures.
  ```
  Suggestion: Add an explicit research-use-only / not-for-clinical-use disclaimer and describe the validation status of the fit metrics.

### Sample data license and provenance not stated
minor; license; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`Tutorials/00_Quick_Tutorial.md:39`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/Tutorials/00_Quick_Tutorial.md#L39): The extension downloads a ZIP from a separate repository (chz31/orbitSurgeySim_sampleData) containing segmentations derived from a third-party dataset, but neither the extension repository nor the README states the license of that data or of the derived segmentations. Distribution permission for the bundled/downloaded material is therefore unclear.
  ```
  This tutorial uses open-source segmentations derived from the **CBCTDental Surgery** dataset from Slicer's Sample Data module.
  ```
  Suggestion: State the license of the sample data (and of the source dataset) in the README and in the sample-data repository.

### Template placeholder metadata left in shipped modules
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`PlateRegistration/PlateRegistration.py:53`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/PlateRegistration.py#L53): The help text links to a placeholder URL and the acknowledgement says 'Will update soon'. Users reading the module's help in Slicer will see a dead link and incomplete attribution. This does not affect how the extension runs.
  ```
  See more information in <a href="https://github.com/organization/projectname#PlateRegistration">module documentation</a>.
  """)
          # TODO: replace with organization, grant and thanks
          self.parent.acknowledgementText = _("""
  Will update soon
  ```
  Suggestion: Point helpText to the README or tutorials and write the acknowledgement text (the README already contains the grant and acknowledgements).

### Undefined names and missing imports cause runtime failures
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`MirrorOrbitRecon/MirrorOrbitRecon.py:599`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/MirrorOrbitRecon/MirrorOrbitRecon.py#L599): `mirrorOrbitReconParameterNode` is never defined (the class is MirrorOrbitReconParameterNode), so any call to getParameterNode raises NameError. Likewise `importlib` is used at lines 102-104 and PlateRegistration.py:114-116 but never imported, and `itk` is used at line 216 outside the try/except that guards its import, so a missing dependency produces a NameError instead of a user-facing message.
  ```
      def getParameterNode(self):
          return mirrorOrbitReconParameterNode(super().getParameterNode())
  ```
  Suggestion: Fix the class name reference, import importlib, and move the itk usage inside the guarded block with a clear error dialog.

### importlib used without import in MirrorOrbitRecon sample-data setup
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`MirrorOrbitRecon/MirrorOrbitRecon.py:100`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/MirrorOrbitRecon/MirrorOrbitRecon.py#L100): downloadSampleDataInFolder uses importlib.util, but MirrorOrbitRecon.py does not import importlib (its imports are logging, os, typing, vtk, numpy, copy, math, qt, slicer, and the ScriptedLoadableModule wildcard). This raises NameError in the setup.py path unless a wildcard import happens to provide it. The same missing import exists in PlateRegistration.py.
  ```
  filepath=destFolderPath+"/setup.py"
        if (os.path.exists(filepath)):
          spec = importlib.util.spec_from_file_location("setup",filepath)
  ```
  Suggestion: Remove the setup.py mechanism (see the safety finding) or add an explicit import importlib.util.

### matplotlib re-installed from inside plotting functions
minor; environment; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`PlateRegistration/PlateRegistration.py:2745`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/PlateRegistration.py#L2745): pip_install("matplotlib") is called again at lines 2745 and 2911 whenever a plot is produced, so a network install can be triggered mid-workflow (and can fail or hang) long after the module was set up. This is redundant with the setup-time install and adds another uncontrolled environment change.
  ```
          slicer.util.pip_install("matplotlib")
  ```
  Suggestion: Install once, with user consent, or require the package to be present and report a clear error if it is missing.

### Reused SlicerMorph code acknowledged but no license notice
info; license; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`MirrorOrbitRecon/MirrorOrbitRecon.py:51`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/MirrorOrbitRecon/MirrorOrbitRecon.py#L51): The registration logic is described as reused from SlicerMorph (BSD-2-Clause). Acknowledgement is present, but the BSD-2-Clause copyright notice and conditions are not reproduced anywhere in the repository, which the license requires for redistributed source.
  ```
  In addition to Slicer base functions, the module reused itk functions for rigid registration from the ALPACA and FastModelAlign Modules of SlicerMorph extension (https://slicermorph.github.io/).
  ```
  Suggestion: Add the SlicerMorph BSD-2-Clause notice to LICENSE.txt or a THIRD_PARTY file.

### Stray tutorial stub files in the repository
info; packaging; raised by haiku
- **haiku** (info, medium confidence, quote no quote) [`Tutorials/02_Edit_existing_plate_registration:1`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/Tutorials/02_Edit_existing_plate_registration#L1): Files named '02_Edit_existing_plate_registration' and 'Generate_Plate_Fit_Metrics' (about 100 bytes each) and duplicate images in Tutorials/ look like leftovers. They clutter the repo and may confuse readers.
  Suggestion: Remove the stubs or turn them into proper tutorial pages.

### Test scaffolding is commented out
info; utility; raised by haiku
- **haiku** (info, high confidence, quote verified) [`PlateRegistration/Testing/Python/CMakeLists.txt:2`](https://github.com/chz31/SlicerOrbitSurgerySim/blob/144ec0dfc2d52484d6a59ee1404d2a0933a08c08/PlateRegistration/Testing/Python/CMakeLists.txt#L2): The per-module Testing/Python CMake entries are commented out, and the test classes are templates. There is no automated regression coverage for registration or metrics. This is non-blocking for the admission review.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a small test that loads the sample data and checks the registration outputs.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The extension is well documented (README, quick tutorial, videos, sample data) and its CMake/EXTENSION_DEPENDS setup is consistent with the catalog entry, with an MIT license. However, both modules' sample-data downloader downloads a ZIP from a moving GitHub branch with no checksum and then executes a `setup.py` from it inside the Slicer process — download-and-execute of remote code, which is blocking. Both modules also run `slicer.util.pip_install` for pandas/matplotlib without asking the user, and the code has numerous swallowed exceptions, a broken registered unit test, and template help text. Recommend fixes before offering to users.
Not checked: The sample-data repository chz31/orbitSurgeySim_sampleData (contents, setup.py, license) could not be fetched, so what the downloaded ZIP contains and whether it includes an executable setup.py is unverified.; PlateRegistration.py was only partially read (lines 1-470, 890-1030, 1690-1900 plus a symbol/pattern search); the heatmap, projection, comparison and plotting code (lines ~1940-3336) was not reviewed line by line, including the os.remove calls at lines 2778 and 2958.; The .ui files, icons and the two extension screenshots were not inspected (binary/large XML).; No build or test run was performed; the claim that the registered MirrorOrbitRecon ctest fails is based on reading the test code, not on executing it.; The cited JOMS 2026 DOI and the YouTube tutorials were not verified.; Whether SlicerMorph's ALPACA module installs itk/itk-fpfh/cpdalp at import (which this extension relies on) was not inspected.
Questions for the author: Why does the sample-data downloader execute a setup.py from the downloaded folder, and can that step be removed or replaced with code shipped in the extension?; Can the sample data be pinned to a fixed commit with SHA256 checksums instead of refs/heads/main with checksums=None?; Can pandas/matplotlib installation be gated behind an explicit user confirmation prompt (or declared as a build dependency) instead of running automatically when the module is opened?; What is the license of the sample data and of the CBCTDental Surgery-derived segmentations, and where is it documented?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): minor issues
SlicerOrbitSurgerySim is a well-documented 3D Slicer extension for orbital fracture repair planning and plate registration. It provides two scripted modules (`PlateRegistration` and `MirrorOrbitRecon`), comprehensive Markdown tutorials, and sample data integration. Minor issues include runtime `pip_install` of `pandas` and `matplotlib`, and execution of `setup.py` scripts from downloaded sample data archives. Overall, the extension is well-structured and ready with minor improvements recommended.
Not checked: Full test suite execution in a live 3D Slicer environment; Complete visual inspection of all 3300+ lines of PlateRegistration.py
Questions for the author: Are there plans to bundle pandas and matplotlib or declare them as formal extension build dependencies instead of runtime pip installation?

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
Reviewed the catalog entry, CMake files, README/tutorials, LICENSE, and the sample-data, dependency-install, and file-write code in both Python modules. The main concern is that the sample-data custom downloader executes a setup.py from an unverified downloaded zip (checksums=None), in both modules. Runtime pip installs of pandas/matplotlib happen on widget setup without a confirmation prompt. Several placeholder texts remain. The MIT license and the SlicerMorph dependency declaration are consistent. I did not read most of the 3300-line PlateRegistration.py, so the review is partial.
Not checked: Most of PlateRegistration/PlateRegistration.py (about 3,300 lines) was not read in full. I searched it for dangerous patterns (exec, eval, pickle, subprocess, network calls, and file writes) and read the setup, sample-data, and plotting sections, but not the registration, file I/O, or metrics logic; Upstream SlicerMorph ALPACA/cpdalp behavior and the MirrorOrbitRecon logic were not inspected beyond the calls shown.; The .ui files, icons, and the Testing contents were not read.; The remote source repo at revision 144ec0d was not fetched. I could not verify that the commit matches the catalog's 'main' reference, and I could not confirm the sample-data zip's contents or license.; The build and the Slicer load were not run. Import-time behavior and the SlicerMorph dependency were inferred from code.


# AI review: MorphoWeave

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/agporto/SlicerMorphoWeave.git at commit `6fd9e448fb3441b71f7fed2bec9434a9b2190d24`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:23:52Z; cost $0.09

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | ok |
| environment | minor | ok | minor |
| packaging | minor | ok | minor |
| license | ok | ok | ok |
| soundness | minor | ok | concern |
| utility | ok | ok | ok |
| **overall** | minor issues | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: MorphoWeave is a 3D Slicer extension for digital-morphology workflows: it builds mean anatomical atlases and dense correspondences from meshes plus sparse landmarks (Atlas Builder), fits and explores PCA statistical shape models (Model Library), transfers template landmarks to new specimens with rigid + SSM-guided deformable registration (Landmark Transfer), and segments homologous surface regions (Surface Segmentation). Its users are morphometricians and anatomy researchers working on surface models, not clinicians.
- **flash-lite**: MorphoWeave is a 3D Slicer extension providing workflows for constructing 3D anatomical atlases, statistical shape models, and transferring landmarks via rigid and shape-model-guided deformable registration.
- **haiku**: MorphoWeave is a set of 3D Slicer scripted modules for building anatomical atlases and statistical shape models, transferring landmarks to new surface models, and correspondence-guided surface segmentation. It is aimed at morphometrics researchers and is listed as a Tier 1 Registration extension.

## Disagreements (start here)

### D1. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings from some reviewers

### Long pipelines run on the GUI thread with processEvents pumping and no re-entrancy guard
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified, other lines) [`MorphoWeaveAtlasBuilder/MorphoWeaveAtlasBuilder.py:256`](https://github.com/agporto/SlicerMorphoWeave/blob/6fd9e448fb3441b71f7fed2bec9434a9b2190d24/MorphoWeaveAtlasBuilder/MorphoWeaveAtlasBuilder.py#L256): Atlas Builder alignment/export and Model Library ingest (MorphoWeaveModelLibrary.py:589) run synchronously on the GUI thread and call processEvents to keep the UI alive. Because the Run button is not disabled during the run (self.runBtn is only enabled/disabled by _reeval, line 308), a second click during a pumped event loop can start a second pipeline that writes into the same output/library folders, and there is no cancel path for long runs. This is a usability/robustness issue, not a data-safety one, since outputs go to timestamped folders.
  ```
          now = time.monotonic()
          if done == total or (now - last_ui_pump >= 0.10):
            qt.QApplication.processEvents()
            last_ui_pump = now
  ```
  Suggestion: Disable the Run/Ingest buttons for the duration of the pipeline (or move the work to a slicer.util.ProgressDialog / CLI-style worker) and add a cancellation check between specimens.

### Model Library ingest does not validate the database name (path traversal / writes outside library root)
minor; safety; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`MorphoWeaveModelLibrary/MorphoWeaveModelLibrary.py:573`](https://github.com/agporto/SlicerMorphoWeave/blob/6fd9e448fb3441b71f7fed2bec9434a9b2190d24/MorphoWeaveModelLibrary/MorphoWeaveModelLibrary.py#L573): The name typed in 'New Database Name' is joined to the library root without any check, so a name such as '../atlas' or 'a/b' makes ingestSSMDatabase create directories and copy files outside the configured library folder. The same unvalidated path is later passed to removeSSMDatabase, which calls shutil.rmtree(dbPath) (line 199) after a single confirmation dialog, so a mis-typed or crafted name can delete a directory the user did not intend. Atlas Builder already implements the correct guard (isSafeLibraryName, MorphoWeaveAtlasBuilder.py:536-545) but Model Library does not reuse it.
  ```
      dbName = self.ssmNameEditor.text or Path(self.ssmTemplateModelSelector.currentPath).stem
      dbRootPath = self.databasePathSelector.currentPath
      db_path = os.path.join(dbRootPath, dbName)
  
      if os.path.exists(db_path):
  ```
  Suggestion: Reuse MorphoWeaveAtlasBuilderLogic.isSafeLibraryName (or an equivalent check) in onIngestButton and in Atlas Builder's _saveSsmToLibrary path, and refuse names containing separators, '..' or reserved characters before creating or deleting anything.

### README and EXTENSION_ICONURL reference logo.png and Docs/Media/morphoweave.gif that are not in the file listing
minor; packaging; raised by deepseek
- **deepseek** (minor, low confidence, quote verified) [`CMakeLists.txt:10`](https://github.com/agporto/SlicerMorphoWeave/blob/6fd9e448fb3441b71f7fed2bec9434a9b2190d24/CMakeLists.txt#L10): The repository listing at this revision contains Docs/Images/nsf-logo.png and tutorial/images/*.png but no root logo.png and no Docs/Media directory, while README.md:2 uses <img src="logo.png"> and README.md:22 uses Docs/Media/morphoweave.gif. If those files are genuinely absent, the catalog icon URL 404s and the README renders broken images. The automated scan reported these two files as present but unreadable, so this may be a tooling limitation rather than a defect; it should be confirmed against the commit.
  ```
  set(EXTENSION_ICONURL "https://raw.githubusercontent.com/agporto/SlicerMorphoWeave/main/logo.png")
  set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/agporto/SlicerMorphoWeave/main/tutorial/images/20.png")
  ```
  Suggestion: Confirm logo.png and Docs/Media/morphoweave.gif exist at the reviewed commit (or add them / point EXTENSION_ICONURL at an existing file such as Docs/Images/nsf-logo.png).

### pip_uninstall of tiny3d/tiny3d-rs modifies Slicer's shared Python environment
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`MorphoWeaveLandmarkTransfer/MorphoWeaveLandmarkTransfer.py:211`](https://github.com/agporto/SlicerMorphoWeave/blob/6fd9e448fb3441b71f7fed2bec9434a9b2190d24/MorphoWeaveLandmarkTransfer/MorphoWeaveLandmarkTransfer.py#L211): Installing tiny3d-rs/rustcpd is user-confirmed and acceptable, but the code also uninstalls the legacy 'tiny3d' distribution from Slicer's shared environment. Any other installed extension that imports tiny3d (for example a SlicerMorph-style point-cloud workflow) stops working after this action, for a user who only wanted to run MorphoWeave. The confirmation dialog at lines 203-206 mentions the removal, which limits the surprise, but the impact on other extensions is not stated.
  ```
        if legacy_tiny3d_installed:
          slicer.packaging.pip_uninstall(["tiny3d", "tiny3d-rs"])
  
        slicer.packaging.pip_ensure(
          requirements,
          prompt_install=not legacy_tiny3d_installed,
  ```
  Suggestion: State in the confirmation dialog that other extensions using tiny3d will stop working, and prefer installing tiny3d-rs without removing tiny3d when the two can coexist, or document the conflict in the module help text.
- **haiku** (minor, high confidence, quote verified) [`MorphoWeaveLandmarkTransfer/MorphoWeaveLandmarkTransfer.py:211`](https://github.com/agporto/SlicerMorphoWeave/blob/6fd9e448fb3441b71f7fed2bec9434a9b2190d24/MorphoWeaveLandmarkTransfer/MorphoWeaveLandmarkTransfer.py#L211): In _ensure_dependencies, when a legacy tiny3d is detected the code calls slicer.packaging.pip_uninstall(['tiny3d','tiny3d-rs']) and then pip_ensure. This modifies Slicer's shared Python environment and can affect other extensions that import tiny3d. It is gated by a confirmation dialog and occurs only when the user opens the module's workflow, so it is a minor concern rather than a defect.
  ```
  if legacy_tiny3d_installed:
            slicer.packaging.pip_uninstall(["tiny3d", "tiny3d-rs"])
  
          slicer.packaging.pip_ensure(
  ```
  Suggestion: Keep the confirmation. Consider documenting in the tutorial which other extensions use tiny3d so users are not surprised.

### rustcpd calls lack local error handling
minor; soundness; raised by haiku
- **haiku** (minor, low confidence, quote verified) [`MorphoWeaveLandmarkTransfer/MorphoWeaveLandmarkTransfer.py:1569`](https://github.com/agporto/SlicerMorphoWeave/blob/6fd9e448fb3441b71f7fed2bec9434a9b2190d24/MorphoWeaveLandmarkTransfer/MorphoWeaveLandmarkTransfer.py#L1569): runDeformable calls rustcpd.register_atlas and register_deformable without try/except around the native calls. A failure surfaces only through the caller. Error reporting therefore depends on higher-level handling that was not fully traced.
  ```
  pca = rustcpd.register_atlas(
              np.asarray(tgt_n),             # scaled target
              np.asarray(src_n),             # source is the SSM base
  ```
  Suggestion: Confirm that batch and single-run callers surface exceptions to the user with a clear message.

### Several megabytes of images committed to the repository
info; packaging; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`README.md:22`](https://github.com/agporto/SlicerMorphoWeave/blob/6fd9e448fb3441b71f7fed2bec9434a9b2190d24/README.md#L22): The tutorial images total roughly 5 MB and the animated GIF is reported at about 4 MB. This is acceptable for documentation but is on the heavy side for a source repository; it does not affect the built extension.
  ```
    <img src="Docs/Media/morphoweave.gif" alt="MorphoWeave statistical shape space animation" width="720">
  ```
  Suggestion: Consider hosting the animation externally or compressing it.

### Submission doc tells the author what to state in the index PR; no reviewer-directed instructions found
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`Docs/ExtensionCatalogSubmission.md:41`](https://github.com/agporto/SlicerMorphoWeave/blob/6fd9e448fb3441b71f7fed2bec9434a9b2190d24/Docs/ExtensionCatalogSubmission.md#L41): This is author-facing publication guidance, not an attempt to instruct AI reviewers to skip checks, so it is not a manipulation finding. I independently confirmed the claim: the only URLs in the code are documentation/help links, and no network, telemetry or upload code exists in the files I read.
  ```
  State that:
  
  - The repository follows the recommended `Slicer+ExtensionName` naming convention while the extension remains displayed as MorphoWeave in Slicer.
  - The extension operates locally and does not upload user data.
  ```
  Suggestion: None required.

### Unclosed file handles and first-markup assumption when reading markup files
info; soundness; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`MorphoWeaveModelLibrary/MorphoWeaveModelLibrary.py:105`](https://github.com/agporto/SlicerMorphoWeave/blob/6fd9e448fb3441b71f7fed2bec9434a9b2190d24/MorphoWeaveModelLibrary/MorphoWeaveModelLibrary.py#L105): json.load(open(...)) leaves the file handle to garbage collection, and only the first entry of the 'markups' array is read, so a .mrk.json containing several markup nodes silently yields the wrong point set. Neither is a safety issue; both are ordinary robustness nits.
  ```
      def _read_json(self, path):
        data=json.load(open(path,'r'))
        m=(data.get('markups') or [{}])[0]
  ```
  Suggestion: Use a with-block and either validate that exactly one markup node is present or merge all fiducial nodes.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): minor issues
No network transmission, no torch, no unsafe deserialization (np.load with allow_pickle=False), and runtime pip installs go through slicer.packaging.pip_ensure with explicit user confirmation. BSD 2-Clause license plus third-party notices for the DeCAL-derived code; catalog entry is consistent with CMake (EXTENSION_DEPENDS empty, build_dependencies empty). Remaining issues are non-blocking: Model Library ingest does not validate the database name (path traversal / writing outside the library root, unlike Atlas Builder's isSafeLibraryName), pip_uninstall of tiny3d/tiny3d-rs touches the shared Slicer environment, README/EXTENSION_ICONURL reference logo.png and Docs/Media/morphoweave.gif that I could not find in the file listing, and long pipelines run on the GUI thread with processEvents pumping and no re-entrancy guard. Review of Landmark Transfer and Surface Segmentation is partial (large files).
Not checked: MorphoWeaveSurfaceSegmentation/MorphoWeaveSurfaceSegmentation.py (38 KB) was not read at all.; Most of MorphoWeaveLandmarkTransfer/MorphoWeaveLandmarkTransfer.py (130 KB): only lines 1-330 were read; the registration, batch, projection and diagnostics code (roughly lines 330-1500) was not inspected.; MorphoWeaveModelLibrary/MorphoWeaveModelLibrary.py after line 900 (deformer precompute, RBF/biharmonic solvers) was not read.; tutorial/README.md and the test files (AtlasBuilderWorkflowTest.py, PoseEMTemplateTest.py, SSMSelectionTest.py) were not read; the exec(compile(...)) occurrences are in tests only, per search results.; ExtensionsIndex/MorphoWeave.json in the repository was not read; I relied on the catalog entry supplied in the prompt.; Licenses of the runtime pip dependencies tiny3d-rs and rustcpd were not verified.; Whether logo.png and Docs/Media/morphoweave.gif actually exist at commit 6fd9e448 (the file listing does not show them, but the automated scan reported them as present-but-unreadable).; No build, install or test run was performed; CI results for this revision were not available.
Questions for the author: Model Library ingest accepts any text as the database name; would you reuse Atlas Builder's isSafeLibraryName check there (and before removeSSMDatabase) to prevent writes/deletes outside the library root?; Do logo.png and Docs/Media/morphoweave.gif exist at the reviewed commit? The repository listing I can see does not include them, while EXTENSION_ICONURL and README reference them.; Removing the legacy tiny3d distribution affects other extensions that import tiny3d; can the confirmation dialog say so explicitly?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
MorphoWeave is cleanly structured, follows Slicer conventions, handles dependencies responsibly via pip_ensure with user prompts, and provides comprehensive functionality for atlas building, statistical shape modeling, and landmark transfer. 🟢 Recommend merge
Not checked: Full manual runtime verification in 3D Slicer

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
Reviewed the catalog entry, top-level CMake, the four module CMake files, the AtlasBuilder module in full, the PoseEMTemplate helper, and targeted searches across the Landmark Transfer, Model Library and Surface Segmentation modules. No malicious or concealed behavior, no network exfiltration, and no unsafe deserialization was found in the parts read. Package installation in Landmark Transfer is user-gated via slicer.packaging.pip_ensure, and the requested packages are tiny3d-rs and rustcpd, not PyTorch or bundled Qt/VTK. Remaining concerns are minor. The license is BSD-2 and covers the bundled SlicerDenseCorrespondenceAnalysis attribution. Several large modules were only partly read.
Not checked: Full bodies of MorphoWeaveLandmarkTransfer.py (about 2400 lines), MorphoWeaveModelLibrary.py (about 950 lines) and MorphoWeaveSurfaceSegmentation.py were not read line by line; only targeted searches were done.; The Resources/Python import path (`from Resources.Python.PoseEMTemplate import`) was not verified against the packaged install layout.; The tutorial/README.md and binary media (GIF, PNG) were not inspected.; The pinned commit 6fd9e448 was not resolved; scm_revision is 'main', so the reviewed source may differ from the catalog state.; No tests were run. Upstream licenses and content of tiny3d-rs and rustcpd PyPI packages were not checked.; Did not verify the catalog schema URL or the ExtensionsIndex validation scripts.
Questions for the author: Which Slicer version is the target for the submitted revision, and has the packaged build been tested with pip_ensure on a clean profile as Docs/ExtensionCatalogSubmission.md describes?; Is scm_revision 'main' intended? A pinned commit would make the reviewed source reproducible.


# AI review: PETReviewCompare

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/4burakfe/SlicerPETReviewCompare at commit `527d4bfdd55a65c980e2920ea616370a3325acc3`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:29:32Z; cost $0.07

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | ok |
| environment | concern | ok | minor |
| packaging | ok | ok | minor |
| license | minor | ok | concern |
| soundness | minor | ok | ok |
| utility | ok | ok | ok |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: PETReviewCompare (Epona) is a 3D Slicer extension for reading SPECT/PET with CT/MRI: fusion, MIP, reading layouts, windowing presets, spherical SUV ROIs (Max/Mean/MTV/TLG) with TSV export, and optional AI denoise/super-resolution filters using Belenos PET Denoise models. It targets nuclear-medicine readers and researchers reviewing PET/CT studies in Slicer.
- **flash-lite**: PETReviewCompare is a 3D Slicer extension providing advanced SPECT/PET and CT/MRI review capabilities, fusion, MIP, reading layouts, windowing presets, SUV measurements with spherical ROIs, and optional AI post-processing filters.
- **haiku**: Epona - SPECT/PET Review and Epona - SPECT/PET Compare: Slicer modules for reading SPECT/PET with CT/MRI (fusion, MIP, windowing, spherical SUV ROIs, ruler) plus optional AI denoising filters that run Belenos PET Denoise models. Intended for nuclear medicine researchers using Slicer.

## Disagreements (start here)

### D1. Runtime pip install into Slicer's shared Python environment (einops==0.6.1)
single; category environment; raised by deepseek
- **deepseek** (major, medium confidence, quote verified) [`Easy_fusion/Easy_fusion.py:2882`](https://github.com/4burakfe/SlicerPETReviewCompare/blob/527d4bfdd55a65c980e2920ea616370a3325acc3/Easy_fusion/Easy_fusion.py#L2882): A search of Easy_fusion found slicer.util.pip_install(requirement) at Easy_fusion.py:2882, and filters.py:65 defines FILTER_EINOPS_REQUIREMENT = "einops==0.6.1". This installs a pinned third-party package into Slicer's shared Python environment, which persists for users and other extensions. I did not read the surrounding lines, so whether the user is explicitly asked first (and whether this can run at import/startup) is unverified; if it runs without confirmation, it violates the index's environment policy.
  ```
  slicer.util.pip_install(requirement)
  ```
  Suggestion: Show an explicit confirmation dialog naming the package and version before installing, never install at import/startup, and avoid an exact pin unless required; document the install in the README.

### D2. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor

### D3. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings from some reviewers

### Hard pin of einops to an old version
minor; environment; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`Easy_fusion/EponaLib/filters.py:65`](https://github.com/4burakfe/SlicerPETReviewCompare/blob/527d4bfdd55a65c980e2920ea616370a3325acc3/Easy_fusion/EponaLib/filters.py#L65): slicer.util.pip_install installs einops==0.6.1 into Slicer's shared Python environment after user confirmation. An exact pin can conflict with other extensions that need newer einops. Only the user's consent covers this, and the pin is not justified in the code.
  ```
  FILTER_EINOPS_REQUIREMENT = "einops==0.6.1"
  ```
  Suggestion: Use a lower bound such as einops>=0.6.1 unless the model code requires the exact version, and document why.

### MIT license text names a different project ("SlicerPETDenoise")
minor; license; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`LICENSE:6`](https://github.com/4burakfe/SlicerPETReviewCompare/blob/527d4bfdd55a65c980e2920ea616370a3325acc3/LICENSE#L6): The grant in LICENSE covers 'the "SlicerPETDenoise"' rather than PETReviewCompare, apparently copied from the author's other project. The MIT terms still permit distribution, but the named subject is wrong, which creates ambiguity about what the license covers.
  ```
  of this software and associated documentation files (the "SlicerPETDenoise"), to deal
  ```
  Suggestion: Replace the project name with PETReviewCompare (or the actual extension name) in the LICENSE text.
- **haiku** (minor, high confidence, quote verified) [`LICENSE:3`](https://github.com/4burakfe/SlicerPETReviewCompare/blob/527d4bfdd55a65c980e2920ea616370a3325acc3/LICENSE#L3): The MIT grant refers to the software as "SlicerPETDenoise", not PETReviewCompare. The grant is still clear for distribution, but the wording should match this extension to avoid ambiguity about what is licensed.
  ```
  Copyright (c) 2025 Burak Demir
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "SlicerPETDenoise"), to deal
  ```
  Suggestion: Change the parenthetical to the actual project name or remove it.

### PyTorch dependency not declared although AI filters need it
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CMakeLists.txt:13`](https://github.com/4burakfe/SlicerPETReviewCompare/blob/527d4bfdd55a65c980e2920ea616370a3325acc3/CMakeLists.txt#L13): The AI filters import torch (filters.py:917) and expect the Slicer PyTorch extension to have installed it, but neither EXTENSION_DEPENDS nor the catalog's build_dependencies lists PyTorch/PyTorchUtils. Users who install only this extension get a failure when they try a filter, with no dependency hint in the catalog.
  ```
  set(EXTENSION_DEPENDS "NA") # PyTorch is optional: only the AI post-processing filters need it (installed via the PyTorch extension)
  ```
  Suggestion: Either declare PyTorchUtils in EXTENSION_DEPENDS and build_dependencies, or make the module's error message and README point clearly to the PyTorch extension.

### Sliding-window inference runs on the GUI thread
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Easy_fusion/EponaLib/filters.py:969`](https://github.com/4burakfe/SlicerPETReviewCompare/blob/527d4bfdd55a65c980e2920ea616370a3325acc3/Easy_fusion/EponaLib/filters.py#L969): The whole inference runs synchronously in the module's slot; the progress dialog only repaints via slicer.app.processEvents() (filters.py:445). On large volumes this blocks the Slicer UI for minutes and cancellation is only honoured between windows, which can look like a hang.
  ```
              with torch.no_grad():
                  predictedNoise = sliding_window_inference(
                      inputs=networkInput, roi_size=roiSize, sw_batch_size=1, predictor=predictor,
                      overlap=FILTER_WINDOW_OVERLAP, mode="gaussian", sw_device=device, device=torch.device("cpu"))
  ```
  Suggestion: Run the filter in a worker thread (or Slicer CLI) and keep the GUI responsive, or at minimum document the expected duration and keep the cancel check frequent.

### Test registration commented out
minor; packaging; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`Easy_fusion/Testing/Python/CMakeLists.txt:2`](https://github.com/4burakfe/SlicerPETReviewCompare/blob/527d4bfdd55a65c980e2920ea616370a3325acc3/Easy_fusion/Testing/Python/CMakeLists.txt#L2): Both Testing/Python CMakeLists are commented out, so CTest does not run the module tests. The tests in EponaLib/tests.py run only through the in-app self test.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Register the unit tests with slicer_add_python_unittest so CI runs them.

### Unbounded module-level cache keyed by node ID
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Easy_fusion/EponaLib/values.py:333`](https://github.com/4burakfe/SlicerPETReviewCompare/blob/527d4bfdd55a65c980e2920ea616370a3325acc3/Easy_fusion/EponaLib/values.py#L333): petValueInfo() stores an entry per volume node ID (values.py:413) and never removes entries when nodes are deleted or the scene is closed, so the dict grows for the lifetime of the Slicer session and keeps stale keys.
  ```
  _petValueInfoCache = {}  # node ID -> (cache key, PetValueInfo)
  ```
  Suggestion: Prune entries for nodes no longer in the scene (e.g. on node-removed events) or use a bounded cache.

### torch.load fallback without weights_only on downloaded model files
minor; safety; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`Easy_fusion/EponaLib/filters.py:702`](https://github.com/4burakfe/SlicerPETReviewCompare/blob/527d4bfdd55a65c980e2920ea616370a3325acc3/Easy_fusion/EponaLib/filters.py#L702): Model .pth files are downloaded from GitHub releases (filters.py:38-42) and loaded with torch.load. On PyTorch < 1.13 the code falls back to pickle-based loading without weights_only, so a replaced or tampered release asset would execute arbitrary code at load time. The SHA-256 check (filters.py:577) mitigates this, but when a release asset changes the digest is taken from the same GitHub API, so the trust root is the same.
  ```
          state = torch.load(modelPath, map_location=device, weights_only=True)
      except TypeError:  # PyTorch older than 1.13 has no weights_only
          state = torch.load(modelPath, map_location=device)
  ```
  Suggestion: Require torch >= 1.13 (the Slicer PyTorch extension provides newer versions) and remove the unsafe fallback, or refuse to load models without weights_only.

### Large binary assets committed to the repository
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`Easy_fusion/CMakeLists.txt:29`](https://github.com/4burakfe/SlicerPETReviewCompare/blob/527d4bfdd55a65c980e2920ea616370a3325acc3/Easy_fusion/CMakeLists.txt#L29): fusbanner.jpg (~3 MB), scr1.jpg (~1.1 MB) and SlicerPETReviewCompare.png (~680 KB) are committed. They are legitimate UI/screenshot resources, but they bloat the repository and every clone; the scan hint flagged the 3 MB banner.
  ```
    Resources/Icons/fusbanner.jpg
  ```
  Suggestion: Downscale the banner/screenshot or generate them at build time; keep only what the module actually displays.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Well-structured, carefully written extension: two scripted modules sharing an EponaLib package, all Python files listed in CMake, MIT license, large unit-test suite, checksum-verified model downloads from the author's own GitHub releases. Concerns: a runtime `slicer.util.pip_install` (einops==0.6.1) into Slicer's shared Python environment whose user-confirmation path I could not read; a `torch.load` fallback without `weights_only` for downloaded .pth files; LICENSE text names "SlicerPETDenoise" instead of this extension; inference runs on the GUI thread. No telemetry or uploads found. Needs confirmation of the pip-install consent path before merge.
Not checked: The context of slicer.util.pip_install at Easy_fusion.py:2882 (whether a confirmation dialog precedes it, and whether it can run at import/startup) — only the search hit was seen.; EponaCompare/EponaCompare.py and Easy_fusion/Easy_fusion.py module bodies: module structure, cleanup, and how EponaCompare imports the shared EponaLib package installed under Easy_fusion's directory.; README.md content: clinical-use disclaimer, model provenance/validation statements, and user instructions.; License terms of the downloaded Belenos PET Denoise model weights in the SlicerPETDenoise releases.; Whether the catalog's scm_revision "main" currently resolves to the reviewed commit 527d4bfdd55a65c980e2920ea616370a3325acc3 (branch reference, not pinned).; Actual build/load of the extension and its CMake install tree; no Slicer build was run.; EponaLib/display.py, layouts.py, overlays.py, registration.py, mippick.py, toolbar.py, shortcuts.py, slicescroll.py, compareviews.py, studyinfo.py were not read in detail.
Questions for the author: Is the einops install at Easy_fusion.py:2882 preceded by an explicit user confirmation dialog, and can it ever run at module import or Slicer startup?; How does EponaCompare.py import EponaLib, which CMake installs under the Easy_fusion module directory? Does it add that directory to sys.path, and does the module load when only EponaCompare is enabled?; What license covers the Belenos PET Denoise model weights downloaded from the SlicerPETDenoise releases, and does it permit redistribution/use by extension users?; Why is PyTorch not declared in EXTENSION_DEPENDS/build_dependencies when the AI filters require it?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
PETReviewCompare is a well-structured and cleanly implemented 3D Slicer extension for nuclear medicine (SPECT/PET and CT/MRI review). All codebase guidelines are respected: PyTorch is correctly handled via PyTorchUtils, additional package installations require explicit user confirmation, licensing and packaging are correct, and code architecture is robust. 🟢 Recommend merge
Not checked: Full interactive runtime testing of GUI functionality in Slicer (due to absence of local Slicer environment).

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
Reviewed the catalog entry, CMakeLists, LICENSE, README and the key code paths for AI-filter model downloads (urllib from GitHub releases, SHA-256 checked, cached), torch.load with weights_only=True, and the pip_install of monai/einops on demand. No malicious or concealed behavior seen. Concerns: the catalog entry is minimal and the LICENSE text names "SlicerPETDenoise" rather than this project; the extension installs packages into Slicer's Python environment only after user confirmation, but einops is pinned to 0.6.1 and PyTorch is correctly delegated to PyTorchUtils. Clinical-use disclaimer is present in the README. Not fully verified: the 3 MB icon, runtime behavior, and the remaining ~3,600 lines of Easy_fusion.py and EponaCompare.py.
Not checked: Did not read Easy_fusion/Easy_fusion.py or EponaCompare/EponaCompare.py in full (only targeted search and excerpts); the rest of display.py, layouts.py, mippick.py, toolbar.py, overlays.py, registration.py, slicescroll.py, compareviews.py, studyinfo.py, shortcuts.py.; Did not verify that every file listed in Easy_fusion/CMakeLists.txt exists or that the 3 MB fusbanner.jpg and other binary assets are needed in the repository.; Did not verify the license of the SlicerPETDenoise model weights downloaded at runtime, or the upstream repository state at the pinned revision (scm_revision is 'main', a moving branch).; Did not run the extension, its tests, or a Slicer build; no network checks of the GitHub release URLs or SHA-256 values.; Did not check the CI or build results for the catalog entry.
Questions for the author: Why is einops pinned to exactly 0.6.1, and does it conflict with other extensions?; Can the LICENSE copyright text be changed to the PETReviewCompare project name?; Can the unit tests be registered with slicer_add_python_unittest so CTest runs them?; Does scm_revision 'main' get replaced with a fixed commit for the catalog entry?


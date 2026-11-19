# AI review: Auto3dgm

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/ToothAndClaw/SlicerAuto3dgm at commit `23dc590af44bdb2cafb460cdc1728cf5b43cce9d`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-19T02:53:11Z; cost $0.87

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | concern | blocking |
| environment | unknown | minor | minor |
| packaging | unknown | minor | minor |
| license | unknown | blocking | blocking |
| soundness | unknown | concern | concern |
| utility | unknown | minor | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: Auto3dgm is a 3D Slicer extension for automated landmark-free alignment of biological surface meshes (a morphometrics workflow). It subsamples meshes, runs pairwise and global alignment, exports aligned meshes, landmarks and transforms, and offers a multi-view display. It also bundles an optional web mesh viewer CLI module.
- **gemini**: Auto3dgm performs automated 3D geometric morphometric analysis on collections of biological surface meshes by subsampling pseudolandmarks and computing pairwise and globalized surface alignments. It is intended for biologists and morphometrics researchers using 3D Slicer to align and compare 3D surface models.
- **gpt**: Auto3dgm automatically samples and aligns collections of 3D biological surface meshes for geometric morphometric analysis. It is intended for researchers comparing shapes and exporting aligned meshes, landmarks, and transformations.

## Disagreements (start here)

### D1. Distribution terms do not cover the wrapper and forked web viewer
single; category license; raised by gpt; outcome after cross-examination: **real, blocking (2 of 2)**
- **gpt** (blocking, high confidence, quote verified) [`meshviewer/web_view_mesh/README.md:1`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/meshviewer/web_view_mesh/README.md#L1): The available repository has an MIT license only under Auto3dgm/auto3dgm_nazar, not at the extension root or in meshviewer. The installed viewer is identified as a fork, but its README provides attribution rather than distribution terms; the wrapper Auto3dgm/Auto3dgm.py likewise has no identified license. The bundled libraries' individual notices do not grant rights to these other files.
  ```
  # web_view_mesh
  
  Fork of [Tingran Gao's](https://github.com/trgao10) (trgao10@math.duke.edu) webGL 3D mesh viewer implemented in [PuenteAligment](https://github.com/trgao10/PuenteAlignment) repository. Some modifications made by Julie Winchester (julia.winchester@duke.edu).
  ```
  Suggestion: Provide an extension-wide license covering the wrapper and author contributions, and identify and include the upstream license and any required notices for the forked viewer.
- gpt on re-check: **real: yes, blocking**: The repository supplies no identified license for the wrapper or viewer: the only project LICENSE found is Auto3dgm/auto3dgm_nazar/LICENSE:1-8, which is inside that package; meshviewer/web_view_mesh/README.md:3 says "Fork of [Tingran Gao's](https://github.com/trgao10) (trgao10@​math.duke.edu) webGL 3D mesh viewer implemented in [PuenteAligment](https://github.com/trgao10/PuenteAlignment) repository. Some modifications made by Julie Winchester (julia.winchester@​duke.edu)." The root Readme.md:1-5 supplies only a website link, and meshviewer/meshviewer.xml:8 has "<license/>". Distribution permission for these files needs clarification; upstream or separate grants were not accessible and are not ruled out.
- gemini on re-check: **rating blocking**: Checked repository file tree (`list_files`), `Auto3dgm/auto3dgm_nazar/LICENSE:1-21`, `Readme.md:1-8`, and `meshviewer/web_view_mesh/README.md:1-3`. Only `Auto3dgm/auto3dgm_nazar/LICENSE` exists (MIT for Julie Winchester et al.); there is no root license covering `Auto3dgm/Auto3dgm.py` or `meshviewer/` (which is a fork of Tingran Gao's PuenteAlignment webGL viewer with no license file). Under the rubric and AGENTS.md admission requirement 2, missing distribution terms for extension code and bundled third-party code is blocking.

### D2. Meshviewer exposes files to the network and permits path traversal
partial; category safety; raised by gemini, gpt; outcome after cross-examination: **real, blocking (2 of 2)**
- **gemini** (major, high confidence, quote verified) [`meshviewer/web_view_mesh/viewer.py:20`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/meshviewer/web_view_mesh/viewer.py#L20): The `meshviewer` CLI module starts an HTTP server bound to `""` (all network interfaces, `0.0.0.0:8000`) and overrides `SimpleHTTPRequestHandler.translate_path` with raw string concatenation (`self.ext_dir_path + path[len(self.ext_prefix):]` and `base_path + path`) without normalizing or sanitizing `..` segments. If a user runs the `meshviewer` CLI module (or calls `Auto3dgmLogic.serveWebViewer`), any host on the local network can read arbitrary files from the user's filesystem via path traversal requests to port 8000.
  ```
    def translate_path(self, path):
      if self.ext_prefix and self.path.startswith(self.ext_prefix):
        return self.ext_dir_path + path[len(self.ext_prefix):]
      else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        return base_path + path
  ```
  Suggestion: Remove the unused `meshviewer` CLI module, or bind only to `127.0.0.1` and delegate path resolution to `SimpleHTTPRequestHandler.translate_path` (or verify `os.path.realpath` stays within the allowed directory).
- **gpt** (blocking, high confidence, quote verified) [`meshviewer/web_view_mesh/viewer.py:20`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/meshviewer/web_view_mesh/viewer.py#L20): The separately installed meshviewer CLI calls serve_viewer, which listens on all interfaces without authentication. Its translate_path concatenates raw request paths without normalization or containment checks; a remote client able to reach port 8000 can use ../ components to read files accessible to the Slicer process, including files outside the selected mesh directory. The main visualization server button is commented out, but the CLI remains installed and separately invokable.
  ```
      def translate_path(self, path):
       if self.ext_prefix and self.path.startswith(self.ext_prefix):
         return self.ext_dir_path + path[len(self.ext_prefix):]
       else:
         base_path = os.path.dirname(os.path.abspath(__file__))
  ```
  Suggestion: Remove the unused server or bind only to loopback, enforce resolved-path containment for both roots, and consider authentication and lifecycle management.
- gpt on re-check: **real: yes, blocking**: meshviewer/web_view_mesh/viewer.py:20-28 uses "return self.ext_dir_path + path[len(self.ext_prefix):]" or "return base_path + path" and binds with "WebViewMeshHTTPServer((\"\", port),  WebViewMeshRequestHandler, ext_dir_path = mesh_path, ext_prefix='/mesh')". Raw ../ request components escape both directories; a reachable network client can read files accessible to the process. meshviewer/meshviewer.py:9-14 calls serve_viewer, and meshviewer/CMakeLists.txt:26-32 installs it. The UI server button is commented out, so exposure is conditional on invoking the separate CLI or logic method.
- gemini on re-check: **rating blocking**: Checked `meshviewer/web_view_mesh/viewer.py:20-29` and `meshviewer/meshviewer.py:9-15`. `serve_viewer` binds to `("", port)` (all interfaces, 0.0.0.0:8000) and `translate_path` directly concatenates `self.ext_dir_path + path[len(self.ext_prefix):]` or `base_path + path` without normalizing or stripping `..` segments or query strings, enabling arbitrary file read over the network if the installed `meshviewer` CLI or `Auto3dgmLogic.serveWebViewer` (`Auto3dgm/Auto3dgm.py:832-834`) is invoked.

### D3. Viewing results silently clears the user's existing Slicer scene
severity dispute; category safety; raised by gemini, gpt; outcome after cross-examination: **real, major (2 of 2)**
- **gemini** (minor, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:845`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L845): Clicking "View Phase 1 alignment" or "View Phase 2 alignment" calls `slicer.mrmlScene.Clear(0)` without asking the user for confirmation, destroying any existing nodes or unsaved work in the current Slicer scene.
  ```
    def viewAlignedMeshWithinSlicer(viewMeshFolder, viewLmkFolder):
        slicer.mrmlScene.Clear(0)
  ```
  Suggestion: Confirm with the user before clearing the scene, or only remove nodes created by Auto3dgm.
- **gpt** (blocking, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:845`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L845): Both View Phase buttons call this function, which removes existing scene nodes without asking the user, even before checking whether the results folder exists. Unsaved images, segmentations, markups, and other scene work can be lost when a user merely requests visualization.
  ```
    def viewAlignedMeshWithinSlicer(viewMeshFolder, viewLmkFolder):
        slicer.mrmlScene.Clear(0)
        modelDir = viewMeshFolder
        modelFileExt = "ply"
        numberOfColumns = 4
        modelFiles = list(f for f in os.listdir(modelDir) if f.endswith('.' + modelFileExt))
  ```
  Suggestion: Do not clear the scene; use isolated view nodes or explicitly ask to save and confirm before replacing existing data.
- gpt on re-check: **real: yes, blocking**: Both view handlers call the same function (Auto3dgm/Auto3dgm.py:386-401); Auto3dgm/Auto3dgm.py:845-850 starts with "slicer.mrmlScene.Clear(0)" before "modelFiles = list(f for f in os.listdir(modelDir) if f.endswith('.' + modelFileExt))". It clears existing non-singleton scene nodes without confirmation, including unsaved work, even if listing the results subsequently fails. That is a concrete data-loss path.
- gemini on re-check: **rating concern**: Checked `Auto3dgm/Auto3dgm.py:386-402` and `Auto3dgm/Auto3dgm.py:845-850`. Both `visPhase1ButtonOnLoad` and `visPhase2ButtonOnLoad` call `Auto3dgmLogic.viewAlignedMeshWithinSlicer`, which immediately executes `slicer.mrmlScene.Clear(0)` on line 846 without confirmation, destroying all nodes and unsaved work in the active Slicer scene (even before checking if `viewMeshFolder` exists).

### D4. Analysis controls for seed, iteration limit, and phase count are ignored
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (2 of 2)**
- **gpt** (major, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:260`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L260): The selected FPS seed is stored but subsample passes an empty seed dictionary and the sampler calls random.seed() without that value. The maximum iteration slider and phase choice are likewise not read by the analysis; Run all always computes both phases and the optimizer uses a hard-coded 1000 iterations. Users can believe results are reproducible or configured when they are not.
  ```
    def subStepButtonOnLoad(self):
      print("Mocking a call to the Logic service AL002.1")
      # Store the keys
      self.Auto3dgmData.phase1SampledPoints = self.phase1PointNumber.value
      self.Auto3dgmData.phase2SampledPoints = self.phase2PointNumber.value
      self.Auto3dgmData.fpsSeed=self.fpsSeed.value
  ```
  Suggestion: Pass each selected value through to the relevant algorithm, or remove unsupported controls; add tests showing the settings affect execution.
- gpt on re-check: **real: yes, major**: Auto3dgm/Auto3dgm.py:149-169 exposes the controls; lines 260-266 store fpsSeed but lines 493-495 pass "seed={}" instead. Auto3dgm/auto3dgm_nazar/mesh/subsample.py:149-150 uses "random.seed()" then "subidx = [random.randint(0, v.shape[0]-1)]". Auto3dgm/Auto3dgm.py:281-285 and 475-480 run both phases regardless of phase choice; correspondence.py:340 passes "max_iter=1000". These ignored settings undermine reproducibility and the configured workflow.
- gemini on re-check: **rating concern**: Checked `Auto3dgm/Auto3dgm.py:149-184`, `260-285`, `Auto3dgm/auto3dgm_nazar/mesh/subsample.py:38-66, 127-155`, and `Auto3dgm/auto3dgm_nazar/analysis/correspondence.py:289, 340`. `maxIterSliderWidget` and `phaseChoiceComboBox` are created in `setupSetupTab` (`Auto3dgm.py:149-171`) and never read anywhere else; `Correspondence.locgpd` uses hard-coded `max_iter=1000`. `self.Auto3dgmData.fpsSeed = self.fpsSeed.value` is stored on line 265, but `Subsample.far_point_subsample` (`subsample.py:149`) calls `random.seed()` with no argument when `seed` has no initial vertex array. (Note: `Auto3dgm/Auto3dgm.py:451-540` could not be read due to a tool error, so `Auto3dgmLogic.subsample` and `runAll` definitions were verified from call sites and `subsample.py`/`correspondence.py`.)

### D5. Export silently overwrites existing output files
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (2 of 2)**
- **gpt** (major, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:641`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L641): Exports always use fixed phase subdirectories and input-derived filenames. Existing directories are reused, and writers such as numpy.savetxt and the PLY writer write to the same paths without a collision check. Re-running or choosing a folder with prior results can silently destroy earlier files.
  ```
      exportFolder = os.path.join(outputFolder, 'phase' + str(p))
      subDirs = ['aligned_meshes', 'aligned_landmarks', 'rotation', 'scale_info', 'landmarks_OSS', 'original_meshes']
  
      Auto3dgmLogic.prepareDirs(exportFolder, subDirs)
      Auto3dgmLogic.alignOriginalMeshes(Auto3dgmData, p)
      Auto3dgmLogic.saveAlignedMeshes(Auto3dgmData, os.path.join(exportFolder, subDirs[0]))
  ```
  Suggestion: Detect collisions and ask before overwriting, or create a fresh uniquely named run directory.
- gpt on re-check: **real: yes, blocking**: Auto3dgm/Auto3dgm.py:641-648 uses "exportFolder = os.path.join(outputFolder, 'phase' + str(p))" and writes multiple fixed subdirectories; lines 804-810 reuse existing ones. Line 589 has "np.savetxt(filename+\".csv\",array,delimiter = \",\",fmt = \"%s\")", which overwrites an existing CSV without confirmation; meshexport.py:17-19 likewise writes the input-derived PLY path. The phase and run-all buttons export automatically (lines 270-285). An existing user file or prior output can be irreversibly overwritten, a concrete data-loss path.
- gemini on re-check: **rating minor**: Checked `Auto3dgm/Auto3dgm.py:588-600`, `626-652`, `745-779`. `exportData` writes into fixed subdirectories (`phase1/`, `phase2/` under user-chosen `outputFolder`) using filenames derived from input mesh names without prompting before overwriting existing exported files in that output directory. Writing deterministic output filenames into a user-selected output directory is standard behavior for export steps and is at most minor/info, not a major safety defect.

### D6. Exporting rotations mutates the stored analysis result
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (2 of 2)**
- **gpt** (major, high confidence, quote verified) [`Auto3dgm/Auto3dgm.py:720`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/Auto3dgm.py#L720): rot aliases an array in corr.globalized_alignment['r']; changing elements in place alters the saved analysis state. A subsequent export or alignment based on that state can produce different or incorrect meshes and landmarks compared with the original result, particularly when rotations have nonzero z-axis cross terms.
  ```
      for idx in range(len(m)):
        mesh = m[idx]
        rot = r[idx]
        # rot = np.linalg.inv(rot)
        # pad rot into 4 x 4 transform matrix in slicer
        rot[2][0] = -1 * rot[2][0]
  ```
  Suggestion: Copy each rotation before coordinate conversion and add a repeated-export consistency test.
- gpt on re-check: **real: yes, major**: Auto3dgm/Auto3dgm.py:717-728 assigns "r = Auto3dgmData.datasetCollection.analysis_sets[label].globalized_alignment['r']", then "rot = r[idx]" and changes four components in place. The matrices are retained in correspondence.py:166-184; later alignOriginalMeshes uses the same stored matrix at Auto3dgm/Auto3dgm.py:612-620. A later export can therefore use altered rotations and produce different aligned meshes or landmarks.
- gemini on re-check: **rating concern**: Checked `Auto3dgm/Auto3dgm.py:645-651` and `707-733`. In `exportRotations`, `r = Auto3dgmData.datasetCollection.analysis_sets[label].globalized_alignment['r']` and `rot = r[idx]`, after which lines 725-728 negate four entries (`rot[2][0]`, `rot[2][1]`, `rot[0][2]`, `rot[1][2]`) in place on the NumPy array before `np.vstack` creates a new array on line 729. This mutates the stored rotation matrices in `analysis_sets[label]`, corrupting any subsequent alignment or export using that in-memory state.

### D7. Removed `scipy.square` import breaks correspondence analysis on modern SciPy/Slicer
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, major (2 of 2)**
- **gemini** (major, high confidence, quote verified) [`Auto3dgm/auto3dgm_nazar/analysis/correspondence.py:8`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/analysis/correspondence.py#L8): `from scipy import square` fails with `ImportError: cannot import name 'square' from 'scipy'` in SciPy >= 1.8 (bundled in current 3D Slicer versions), where deprecated NumPy ufunc re-exports were removed from the top-level `scipy` namespace. Calling `Auto3dgmLogic.correspondence()` (Phase 1, Phase 2, or Run all steps) immediately raises an ImportError when importing `auto3dgm_nazar.analysis.correspondence`.
  ```
  from scipy.sparse.linalg import norm
  from scipy import square
  import numpy as np
  ```
  Suggestion: Replace `from scipy import square` with `from numpy import square` (or `np.square`).
- **gpt** (major, high confidence, quote verified) [`Auto3dgm/auto3dgm_nazar/analysis/correspondence.py:5`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/analysis/correspondence.py#L5): On SciPy versions that no longer expose square at the package top level, this raises ImportError. Importing the dataset factory first executes auto3dgm_nazar/__init__.py, which imports app.py and then this module, so even Load Data fails before analysis can start.
  ```
  from scipy.sparse import csr_matrix, identity, find, lil_matrix, coo_matrix
  from scipy.sparse.csgraph import minimum_spanning_tree, shortest_path
  from scipy import sparse as sp
  from scipy.sparse.linalg import norm
  from scipy import square
  import numpy as np
  ```
  Suggestion: Use numpy.square and test the full Load Data and analysis path against supported Slicer releases.
- gpt on re-check: **real: yes, major**: Auto3dgm/auto3dgm_nazar/analysis/correspondence.py:8-10 contains "from scipy import square"; this fails on SciPy releases without that top-level export. Auto3dgm/auto3dgm_nazar/__init__.py:1 says "from auto3dgm_nazar.app import *", and app.py:5-7 imports Correspondence, so Auto3dgm.py:483-485 loading the dataset factory also triggers it, assuming earlier imports succeed. This can prevent analysis and data loading; the actual Slicer/SciPy runtime was not available to test.
- gemini on re-check: **rating concern**: Checked `Auto3dgm/auto3dgm_nazar/analysis/correspondence.py:8-10, 302, 398` and `Auto3dgm/auto3dgm_nazar/__init__.py:1`. `correspondence.py` line 9 executes `from scipy import square`, which raises `ImportError` in SciPy >= 1.8.0 (used in modern 3D Slicer releases) where `scipy.square` was removed. Because `auto3dgm_nazar/__init__.py` imports `auto3dgm_nazar.app`, importing any `auto3dgm_nazar` submodule triggers this import chain and fails.


## Findings from some reviewers

### Missing top-level license for the extension repository
blocking; license; raised by gemini; **quote not found in source**
- **gemini** (blocking, high confidence, quote quote not found) [`Auto3dgm/auto3dgm_nazar/LICENSE:1`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/LICENSE#L1): The repository has no top-level LICENSE file covering the Slicer extension wrapper (`Auto3dgm/Auto3dgm.py` and `meshviewer/`). Only the bundled `Auto3dgm/auto3dgm_nazar/LICENSE` (MIT License, Copyright 2018 Julie Winchester et al.) and third-party JavaScript library licenses under `meshviewer/web_view_mesh/js/` are present. Clear distribution permission is required for the entire extension repository.
  ```
  Auto3dgm/auto3dgm_nazar/LICENSE
  ```
  Suggestion: Add a top-level LICENSE file in the repository root specifying the license under which the SlicerAuto3dgm extension and its modules are distributed.

### Large test fixtures and obsolete Python 3.6 binaries are committed and installed into the package
minor; packaging; raised by gemini, gpt
- **gemini** (minor, high confidence, quote verified) [`Auto3dgm/CMakeLists.txt:21`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/CMakeLists.txt#L21): `Auto3dgm/CMakeLists.txt` installs the entire `auto3dgm_nazar` directory into the runtime package, including a 16 MB test fixture (`Auto3dgm/auto3dgm_nazar/tests/fixtures/test.ply`) and a precompiled Python 3.6 Windows binary (`Auto3dgm/auto3dgm_nazar/lap_windows/_lapjv.cp36-win_amd64.pyd`). In addition, `meshviewer/CMakeLists.txt` installs the entire `web_view_mesh` directory including ~4 MB of unused textures and Python 3.6 `.pyc` files.
  ```
  install(DIRECTORY "auto3dgm_nazar"
    DESTINATION "${Slicer_INSTALL_QTSCRIPTEDMODULES_BIN_DIR}"
    COMPONENT Runtime
    USE_SOURCE_PERMISSIONS
    )
  ```
  Suggestion: Exclude `tests`, `lap_windows`, and `__pycache__` from the CMake `install(DIRECTORY ...)` rules and remove unused binary fixtures from the repository.
- **gpt** (minor, high confidence, quote verified) [`Auto3dgm/CMakeLists.txt:21`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/CMakeLists.txt#L21): This installs the entire source subtree, including the committed CPython 3.6 Windows _lapjv binary and large test fixtures, even though the active correspondence code uses SciPy and MOSEK rather than lap_windows. The binary's provenance and licensing were not independently verified and it is not suitable for other Python versions.
  ```
  install(DIRECTORY "auto3dgm_nazar"
    DESTINATION "${Slicer_INSTALL_QTSCRIPTEDMODULES_BIN_DIR}"
    COMPONENT Runtime
    USE_SOURCE_PERMISSIONS
    )
  ```
  Suggestion: Exclude tests and unused binaries from runtime packages and remove or document the binary with provenance and applicable license.

### Phase 2 does not use Phase 1 alignment, and UI parameters (Max Iterations, FPS Seed) are ignored
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified, other file) [`Auto3dgm/auto3dgm_nazar/app.py:68`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/app.py#L68): In `Auto3dgm/Auto3dgm.py` (lines 277 and 280), Phase 2 correspondence is called via `Auto3dgmLogic.correspondence(self.Auto3dgmData, self.reflectionCheckBox.checked, phase=2)`. However, `Auto3dgmLogic.correspondence` (lines 523-532) never passes Phase 1's `globalized_alignment` as `initial_alignment` to `Correspondence(...)`, nor does it pass the user's `maxIterSliderWidget` value or `fpsSeed` value (in `runAll`, `fpsSeed` is not even stored, and in `subsample`, `seed={}` is hardcoded on line 495). As a result, Phase 2 recomputes alignment from scratch without using Phase 1's alignment, and the UI controls for Maximum Iterations and FPS Seed have no effect.
  ```
      ### INITIAL SUBSAMPLE POINTS ANALYSIS ###
      ss_i_correspondence_res = Correspondence( # Correspondence should take an initial alignment object with d, p, and r arrays; also correspondence should handle bundling pairwise results into a single data structure
        meshes=self.dataset[self.ss_label_i],
        initial_alignment=None, 
        globalize=True,
        mirror=self.allow_reflection)
  ```
  Suggestion: Pass the Phase 1 `globalized_alignment` as `initial_alignment` when running Phase 2 in `Auto3dgmLogic.correspondence`, and wire `maxIterSliderWidget.value` and `fpsSeed.value` into `Correspondence` and `Subsample`.

### `.off` file parser opens hardcoded `"hammas.off"` instead of `file_path`
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified, other lines) [`Auto3dgm/auto3dgm_nazar/mesh/meshfactory.py:24`](https://github.com/ToothAndClaw/SlicerAuto3dgm/blob/23dc590af44bdb2cafb460cdc1728cf5b43cce9d/Auto3dgm/auto3dgm_nazar/mesh/meshfactory.py#L24): `MeshFactory.off_parser(file_path)` ignores its `file_path` parameter and attempts to open a hardcoded `"hammas.off"` in the current working directory, causing any `.off` mesh import to fail with `FileNotFoundError`.
  ```
    @staticmethod
    def off_parser(file_path):
        file=open("hammas.off","r")
  ```
  Suggestion: Open `file_path` using a context manager (`with open(file_path, "r") as file:`).


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
The core module has no hidden network activity, telemetry or obfuscation. The concerns are:
1. The bundled meshviewer CLI module starts an HTTP server on all interfaces with an unsanitised path mapping, so it allows path traversal.
2. "View alignment" clears the whole MRML scene without asking.
3. The extension has no top-level license, and the bundled third-party material is mixed (a GPL-2.0 JS file, a proprietary Mosek dependency).
4. Mosek is installed with pip_install when the module widget is constructed, and the algorithm needs a commercial or academic license.
5. Some code looks incompatible with current SciPy.
6. A Windows cp36 .pyd is committed.
7. Testing is essentially absent.
The catalog entry uses `scm_revision: master`, a moving branch, so the reviewed commit is not pinned.
Not checked: Large files (test.ply, textures); Contents of the 189 JS files under meshviewer/web_view_mesh/js beyond license grep; index.html and view_segments.html for external resource loading; Whether the commit 23dc590 matches current master; Runtime behavior in Slicer (nothing was executed); Remaining tests under auto3dgm_nazar/tests and lap_windows/tests

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
Auto3dgm brings automated 3D geometric morphometric surface alignment to 3D Slicer. However, there are key issues that should be addressed: (1) there is no root-level LICENSE file covering the Slicer extension wrapper code (`Auto3dgm.py` and `meshviewer/`), (2) `correspondence.py` uses `from scipy import square`, which raises an `ImportError` on SciPy >= 1.8 (used by modern Slicer builds), and (3) the legacy `meshviewer` CLI module exposes an HTTP server on all network interfaces (`0.0.0.0:8000`) with a path traversal vulnerability in `translate_path`.

🔴 Do not merge yet: missing top-level license file covering the extension repository (and `meshviewer` path-traversal HTTP server / `scipy.square` import failure).
Not checked: Binary contents of Auto3dgm/auto3dgm_nazar/tests/fixtures/test.ply (16 MB), meshviewer/web_view_mesh/textures/UVTexture_1.png (2 MB), meshviewer/web_view_mesh/textures/UVTexture_1_resized.png (2 MB), and Auto3dgm/auto3dgm_nazar/lap_windows/_lapjv.cp36-win_amd64.pyd (not imported anywhere in the acti
Questions for the author: Can you add a root-level LICENSE file covering the Slicer extension code (`Auto3dgm/` and `meshviewer/`)?; Since visualization now uses `viewAlignedMeshWithinSlicer`, can the legacy `meshviewer` CLI web server module be removed?; Can the `mosek` dependency be made optional by falling back to `scipy.optimize.linear_sum_assignment` when a MOSEK license is not installed?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The separately exposed meshviewer can serve files to the network with path traversal, and visualization clears the current Slicer scene without warning. Distribution permission is also not established for the extension wrapper and forked viewer: the MIT license is scoped to the nested analysis package. Analysis imports can fail with newer SciPy, and several controls do not affect computation. The supplied source revision and catalog accessibility were not independently verified. 🔴 Do not merge yet: fix the data-exposure and scene-loss paths and establish distribution permission; review of the exact revision and catalog remains incomplete.
Not checked: Cannot run Slicer, build, execute tests, or validate the current Slicer/SciPy versions.; The supplied commit and master branch resolution, repository accessibility, catalog schema validation, previous revision, and CI results were not independently verified.; External website, upstream fork licensing, MOSEK distribution terms and behavior, and third-party JavaScript and native binary provenance were not fully inspected.; Large binary fixtures, image assets, and compiled binaries could not be inspected as source.
Questions for the author: What license applies to the extension wrapper and viewer fork, including upstream contributions and the bundled LAP binary?; Is the meshviewer CLI still needed, and should it be distributed at all?


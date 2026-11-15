# AI review: AAL3BrainLabeling

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/niyaziacer/SlicerAAL3BrainLabeling at commit `b08789e87142603744cc02512c79a9a8f480a74b`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-15T09:58:57Z; cost $0.48

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | ok | ok | blocking |
| environment | ok | ok | minor |
| packaging | concern | ok | unknown |
| license | minor | minor | unknown |
| soundness | concern | concern | concern |
| utility | minor | minor | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: A Slicer scripted module that runs N4 bias correction, then Elastix registration of an MNI152 template to the user's MRI, and warps the AAL3 atlas into a segmentation. It exports regional volume and intensity CSVs, hemispheric asymmetry indices and a centroid-distance matrix, with batch processing of a folder.
- **gemini**: AAL3BrainLabeling is a neuroimaging extension for 3D Slicer that performs N4 bias field correction, multi-stage Elastix registration against an MNI152 template, and automated parcellation of brain MRI volumes using the AAL3 atlas. It targets neuroimaging researchers seeking regional morphometric statistics, hemispheric asymmetry indices, and centroid-based Euclidean distance matrices for single subjects or batch cohorts.
- **gpt**: AAL3BrainLabeling maps the AAL3 brain atlas to MRI volumes and exports regional morphometry and centroid-distance matrices. It is intended for neuroimaging researchers processing individual scans or batches.

## Disagreements (start here)

### D1. Result exports overwrite files and trust volume names as paths
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`AAL3BrainLabeling.py:320`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L320): Rerunning an analysis with the same volume name in the chosen results folder silently truncates the previous morphometry CSV; the matrix export similarly overwrites its prior file. MRML node names can also contain absolute paths or parent-directory components, allowing a supplied or renamed volume to direct the generated filename outside the chosen folder and overwrite a matching file there.
  ```
          fileName = f"{volName}_AAL3_Morphometry_Results.csv"
          csvPath = os.path.join(outDir, fileName)
          
          with open(csvPath, "w", newline='') as f:
  ```
  Suggestion: Generate safe basename-only output names, check containment within the selected directory, and use unique outputs or explicit overwrite confirmation for both exports.
- claude on re-check: **real: yes, minor**: AAL3BrainLabeling.py:320-323 opens f"{volName}_AAL3_Morphometry_Results.csv" with "w" in the user-chosen outDir, so a rerun overwrites the earlier CSV. Overwriting results of the same analysis is expected behaviour. Volume names come from the user's own scene or files, and I found no remote or untrusted-input path to harm. This is a hardening/robustness issue, not blocking safety.
- gpt on re-check: **real: yes, blocking**: AAL3BrainLabeling.py:163 obtains `volName = inputVolume.GetName()`; lines 320-323 use `fileName = f"{volName}_AAL3_Morphometry_Results.csv"`, `csvPath = os.path.join(outDir, fileName)`, and `with open(csvPath, "w", newline='') as f:`. Lines 368-369 similarly write the matrix with `np.savetxt`. Existing matching output is overwritten without confirmation; an absolute or traversal-containing node name can direct the suffix-constrained output outside the chosen directory. This is a concrete potential loss of user data, though the missing template visible in this checkout currently prevents reaching export.
- gemini on re-check: **real: yes, minor**: In AAL3BrainLabeling.py:320-323 and 368-369, `volName` (from `inputVolume.GetName()` at line 163) is formatted directly into `f"{volName}_AAL3_Morphometry_Results.csv"` and `f"{volName}_Connectome_Matrix.csv"` and opened with `"w"`. Rerunning with the same volume name overwrites the previous output in `outDir`, and `/` or `..` in a custom MRML node name is not sanitized. However, this is standard local file export behavior into a user-selected directory (`outDir`), not a blocking security vulnerability.

### D2. Centroid statistic is not enabled in SegmentStatisticsLogic, producing an all-zero connectome matrix
single; category soundness; raised by gemini; outcome after cross-examination: **real, major (2 of 3)**
- **gemini** (major, high confidence, quote verified) [`AAL3BrainLabeling.py:297`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L297): `volumeStatistics` computes statistics via `SegmentStatisticsLogic` using default parameters, and `connectome()` then calls `self.getCentroid(stats, sid)` which searches for `'centroid'` in the statistics keys (`for k in stats.keys(): if len(k) == 2 and k[0] == sid and 'centroid' in k[1].lower(): return stats[k]`). In Slicer's `LabelmapSegmentStatisticsPlugin`, `centroid_ras` is NOT enabled by default (`centroid_ras` must be explicitly enabled via `logic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.centroid_ras.enabled", str(True))`). Because it is not enabled, `getCentroid` always falls back to `(0.0, 0.0, 0.0)` for every region, causing the exported `*_Connectome_Matrix.csv` to be an all-zero matrix.
  ```
      def volumeStatistics(self, segmentation, volume):
          """Utilizes Slicer's SegmentStatistics module for metric computation."""
          import SegmentStatistics
          logic = SegmentStatistics.SegmentStatisticsLogic()
          logic.getParameterNode().SetParameter("Segmentation", segmentation.GetID())
          logic.getParameterNode().SetParameter("ScalarVolume", volume.GetID())
  ```
  Suggestion: Enable the centroid measurement before calling `logic.computeStatistics()`:
`logic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.centroid_ras.enabled", str(True))`
- claude on re-check: **real: yes, major**: AAL3BrainLabeling.py:297-304 and 312-316, 356-369: volumeStatistics never enables the centroid measurement. As far as I recall, the LabelmapSegmentStatisticsPlugin leaves centroid_ras off by default, though I could not run Slicer to check. If so, getCentroid falls back to (0,0,0) for every segment, and connectome() writes an all-zero matrix with no warning. The README (line 18) advertises the connectome.
- gpt on re-check: **real: unsure**: AAL3BrainLabeling.py:299-303 creates `logic = SegmentStatistics.SegmentStatisticsLogic()` and sets only `"Segmentation"` and `"ScalarVolume"` before `logic.computeStatistics()`. Lines 312-316 return the origin if no centroid key exists, and lines 360-366 calculate distances from those values. However, the Slicer SegmentStatistics implementation and its default enabled measurements are not present in the inspected repository, so I cannot verify the claim that the normal configuration always omits centroids or produces an all-zero matrix.
- gemini on re-check: **real: yes, major**: In AAL3BrainLabeling.py:297-304, `volumeStatistics()` initializes `SegmentStatistics.SegmentStatisticsLogic()` and calls `computeStatistics()` without enabling `LabelmapSegmentStatisticsPlugin.centroid_ras.enabled` (which defaults to False in Slicer's LabelmapSegmentStatisticsPlugin). Consequently, no key containing `'centroid'` is present in `stats`, `getCentroid()` (lines 312-316) always returns `(0.0, 0.0, 0.0)`, and `connectome()` (lines 356-369) produces an all-zero distance matrix.

### D3. Listed template resource may be absent from the repository
severity dispute; category packaging; raised by claude, gemini, gpt; outcome after cross-examination: **real, minor (2 of 3)**
- **claude** (major, low confidence, quote verified) [`CMakeLists.txt:35`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/CMakeLists.txt#L35): The CMake resource list includes the 10 MB MNI152 template. The file listing for Resources does not show it, although the scan hint says it exists. If it is missing, configure or install fails, or registration fails at runtime with 'Template missing'. The README tree does show the file.
  ```
  Resources/Templates/MNI152_T1_1mm.nii.gz
  ```
  Suggestion: Confirm the template is committed at the pinned revision. Alternatively download it on demand with a checksum, or use a template available from the Slicer sample data.
- **gemini** (info, high confidence, quote verified) [`CMakeLists.txt:31`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/CMakeLists.txt#L31): The repository commits a 10 MB NIfTI template (`Resources/Templates/MNI152_T1_1mm.nii.gz`) and a 1.7 MB screenshot (`Screenshots/Screenshot.png`) directly into git, and installs the template as a module resource. While functional, Slicer extensions generally prefer downloading large template/atlas data on demand (e.g., via `SampleData`) or hosting screenshots externally/in separate branches to keep git repositories and extension packages lightweight. Additionally, `Resources/Labels/AAL3_labels.csv` is installed but never referenced in `AAL3BrainLabeling.py` (and its label names for IDs 115–170 differ from the actual AAL3v1 color table in `Resources/Atlas/AAL3_ColorTable.ctbl`).
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/AAL3BrainLabeling.png
    Resources/Atlas/AAL3v1_1mm.nii.gz
    Resources/Atlas/AAL3_ColorTable.ctbl
    Resources/Templates/MNI152_T1_1mm.nii.gz
    Resources/Labels/AAL3_labels.csv
  ```
  Suggestion: Consider downloading large template files on demand with caching, and remove or reconcile the unused `Resources/Labels/AAL3_labels.csv` file.
- **gpt** (info, high confidence, quote verified) [`CMakeLists.txt:31`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/CMakeLists.txt#L31): The package includes an AAL3 atlas and MNI template, but the inspected license identifies only the extension authors and the README cites an atlas paper without identifying asset-specific redistribution terms. This does not establish that permission is absent; it leaves the third-party distribution requirement unverified.
  ```
    set(MODULE_PYTHON_RESOURCES
      Resources/AAL3BrainLabeling.png
      Resources/Atlas/AAL3v1_1mm.nii.gz
      Resources/Atlas/AAL3_ColorTable.ctbl
      Resources/Templates/MNI152_T1_1mm.nii.gz
  ```
  Suggestion: Document the exact source, copyright holders, and applicable redistribution permissions for each third-party image and derived label data.
- claude on re-check: **real: yes, blocking**: CMakeLists.txt:35 lists Resources/Templates/MNI152_T1_1mm.nii.gz. The directory listing of Resources shows no Templates folder, and the file is absent. Only the README tree (line 65) mentions it. The scripted-module macro copies listed resources, so the build or install will likely fail. If it doesn't, registration at AAL3BrainLabeling.py:203-205 fails with 'Template missing', and the core pipeline cannot run. Redistribution terms for the AAL3 atlas and the MNI template are also not stated; LICENSE.txt is MIT for the authors only. That is an unverified point, not a proven absence.
- gpt on re-check: **real: unsure**: CMakeLists.txt:31-36 includes `Resources/Templates/MNI152_T1_1mm.nii.gz`; AAL3BrainLabeling.py:201-205 checks that path and returns failure if absent. The available file listing has no Resources/Templates files, but the disputed item reports a contrary scan hint that the 10 MB file exists. The listing may not establish the complete Git contents, so absence and consequent package failure remain unverified. README.md:64-65 also lists the template. CMakeLists.txt:33 and LICENSE.txt:3-8 do not establish asset-specific atlas redistribution permission; that requires provenance and terms, not an assumption of missing permission.
- gemini on re-check: **real: yes, minor**: In CMakeLists.txt:31-37, `Resources/Templates/MNI152_T1_1mm.nii.gz` is listed in `MODULE_PYTHON_RESOURCES`, and AAL3BrainLabeling.py:201-205 requires it at runtime (`if not os.path.exists(templatePath): slicer.util.errorDisplay(...)`). Listing `Resources/` via `list_files` shows only `AAL3BrainLabeling.png`, `Atlas/AAL3_ColorTable.ctbl`, `Atlas/AAL3v1_1mm.nii.gz`, and `Labels/AAL3_labels.csv` (though the tool platform may omit ~10 MB binaries from the checkout). Even if present, bundling a 10 MB MNI template and 1.7 MB screenshot in git and lacking explicit license provenance for the bundled MNI/AAL3 assets are worth noting as minor/info points.

### D4. Missing centroid measurements silently produce fabricated distances
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`AAL3BrainLabeling.py:312`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L312): The statistics setup does not explicitly enable a centroid measurement. If the active SegmentStatistics configuration does not provide it, the pipeline substitutes the origin and exports zero or otherwise incorrect distances as successful results, with no warning.
  ```
      def getCentroid(self, stats, sid):
          """Extracts 3D spatial center coordinates for distance matrix calculations."""
          for k in stats.keys():
              if len(k) == 2 and k[0] == sid and 'centroid' in k[1].lower(): return stats[k]
          return (0.0, 0.0, 0.0)
  ```
  Suggestion: Explicitly enable the intended centroid measurement, verify each region has a valid centroid, and report missing measurements instead of substituting coordinates.
- claude on re-check: **real: yes, major**: AAL3BrainLabeling.py:312-316 returns (0.0, 0.0, 0.0) silently when no centroid key is found. Exported distances are then wrong, with no error or warning. This is the same root cause as D2.
- gpt on re-check: **real: yes, major**: AAL3BrainLabeling.py:312-316 searches for `'centroid' in k[1].lower()` and otherwise executes `return (0.0, 0.0, 0.0)`. Lines 360-369 then compute and export distances from those coordinates without a missing-measurement warning. If any centroid is absent, the matrix contains fabricated distances, including all zeros if none are present. The actual default availability of centroid measurements was not verified.
- gemini on re-check: **real: yes, major**: In AAL3BrainLabeling.py:297-304 and 312-316, `volumeStatistics()` does not enable `LabelmapSegmentStatisticsPlugin.centroid_ras.enabled`, and `getCentroid()` falls back to `(0.0, 0.0, 0.0)` without warning when no `'centroid'` key is found, causing `connectome()` (lines 356-369) to silently export an all-zero distance matrix CSV.

### D5. Non-standard CPACK override with undefined EXTENSION_NAME; missing extension config include
single; category packaging; raised by claude; outcome after cross-examination: **real, minor (2 of 3)**
- **claude** (major, medium confidence, quote verified) [`CMakeLists.txt:51`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/CMakeLists.txt#L51): The extension overrides CPACK_INSTALL_CMAKE_PROJECTS with an undefined EXTENSION_NAME and does not include Slicer_EXTENSION_GENERATE_CONFIG. This can break extension packaging in the factory build, or produce a package without the module.
  ```
  set(CPACK_INSTALL_CMAKE_PROJECTS "${CMAKE_BINARY_DIR};${EXTENSION_NAME};ALL;/")
  include(${Slicer_EXTENSION_CPACK})
  ```
  Suggestion: Follow the standard extension template: include(${Slicer_EXTENSION_GENERATE_CONFIG}) before the CPACK include, and remove the manual CPACK_INSTALL_CMAKE_PROJECTS line.
- claude on re-check: **real: yes, minor**: CMakeLists.txt:51-52 sets CPACK_INSTALL_CMAKE_PROJECTS with ${EXTENSION_NAME}, which this file never defines. It also never includes Slicer_EXTENSION_GENERATE_CONFIG. This departs from the standard template and is sloppy. The include of Slicer_EXTENSION_CPACK follows the set and, as far as I recall, defines the same variable itself, so the override is probably harmless in the factory build. Not a confirmed breakage.
- gpt on re-check: **real: unsure**: CMakeLists.txt:51-52 does set `CPACK_INSTALL_CMAKE_PROJECTS "${CMAKE_BINARY_DIR};${EXTENSION_NAME};ALL;/"` and include `${Slicer_EXTENSION_CPACK}`; the inspected file does not explicitly define EXTENSION_NAME or include Slicer_EXTENSION_GENERATE_CONFIG. But CMakeLists.txt:19-20 also loads Slicer's build environment, whose variable definitions and packaging behavior are unavailable here. These observations alone do not prove the variable is undefined or packaging fails.
- gemini on re-check: **real: yes, major**: In CMakeLists.txt:3, `project(AAL3BrainLabeling)` sets `PROJECT_NAME`, not `EXTENSION_NAME`. Line 51 sets `CPACK_INSTALL_CMAKE_PROJECTS "${CMAKE_BINARY_DIR};${EXTENSION_NAME};ALL;/"` where `EXTENSION_NAME` is undefined (evaluating to empty), prior to `include(${Slicer_EXTENSION_CPACK})` at line 52 (which normally sets `EXTENSION_NAME` to `${PROJECT_NAME}` if not defined and sets `CPACK_INSTALL_CMAKE_PROJECTS` properly). Overriding `CPACK_INSTALL_CMAKE_PROJECTS` beforehand with an empty project name can break CPack packaging.

### D6. Registration transform direction maps moving subject to fixed MNI template, warping the MNI atlas in the wrong direction
single; category soundness; raised by gemini; outcome after cross-examination: **still disputed**
- **gemini** (major, high confidence, quote verified) [`AAL3BrainLabeling.py:183`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L183): In `registration(self, volume, volName)`, Elastix registers the subject `volume` (moving) to `templateNode` (fixed: `MNI152_T1_1mm`). In Elastix/SlicerElastix, `outputTransformNode` represents the transform that maps moving (`volume`, subject space) to fixed (`templateNode`, MNI space) — i.e., in Slicer's transform convention, applying that transform to a node moves it from subject space to MNI space (or vice versa depending on Elastix's direction: Elastix computes a transform in fixed-to-moving pull / moving-to-fixed push in Slicer). Specifically, `SlicerElastix`'s `registerVolumes(movingVolumeNode=volume, fixedVolumeNode=templateNode, outputTransformNode=transformNode)` produces a transform that transforms the moving volume (`volume`, patient) into the fixed volume (`templateNode`, MNI152) space! Applying that same `transform` to `atlasNode` (which is already in MNI152 space) without inverting it (`transform.Inverse()`) warps the MNI atlas by the patient-to-MNI transform rather than the MNI-to-patient inverse transform, misaligning the atlas with the patient's anatomy. Furthermore, `regVol` returned from `registration` is just the untransformed `volN4` (`return volume, transformNode`).
  ```
          # 4. Volumetric feature extraction
          self.updateUI("Step 4/5: Computing Regional Morphometry...", 85, progress, statusLabel)
          stats = self.volumeStatistics(segmentation, regVol)
          
          # 5. Multimodal Data Export
          self.updateUI("Step 5/5: Exporting Results and Computing Matrices...", 90, progress, statusLabel)
  ```
  Suggestion: Register the MNI template (moving) to the subject volume (fixed) — i.e. `logic.registerVolumes(templateNode, volume, ...)` — or invert the transform before applying and hardening it onto `atlasNode` so that the MNI atlas is mapped into the patient's native space.
- claude on re-check: **real: no, info**: AAL3BrainLabeling.py:252 calls logic.registerVolumes(volume, templateNode, ...). SlicerElastix's signature is registerVolumes(fixedVolumeNode, movingVolumeNode, ...), so the subject is fixed and the MNI template is moving. The resulting transform maps template/atlas space onto the subject, and it is applied to the atlas at lines 280-281. That is the correct direction, so the finding is wrong.
- gpt on re-check: **real: unsure**: AAL3BrainLabeling.py:252 calls `logic.registerVolumes(volume, templateNode, parameterFilenames=paths, outputTransformNode=transformNode)` and lines 280-281 apply and harden that transform on the atlas. The SlicerElastix API signature and transform convention are not available in this checkout, so neither the finding's assignment of fixed versus moving arguments nor the alleged wrong direction is established. The pipeline's template-absence check at lines 201-205 also prevents verifying a run from these files.
- gemini on re-check: **real: yes, info**: In AAL3BrainLabeling.py:174, 207, 252, `registration()` calls `logic.registerVolumes(volume, templateNode, parameterFilenames=paths, outputTransformNode=transformNode)`. In SlicerElastix, `registerVolumes(fixedVolumeNode, movingVolumeNode, ...)` takes `fixedVolumeNode` as the first positional argument and `movingVolumeNode` as the second. Here `volume` (subject N4 volume) is passed first (fixed) and `templateNode` (MNI152) is passed second (moving), or if the author intended subject->MNI registration, the comment/README conflicts with the code; furthermore, `registration()` returns the untransformed `volume` as `regVol` (line 261), and `atlasMapping()` applies `transformNode` to `atlasNode` (lines 280-281). Because `SlicerElastix.registerVolumes(fixedVolumeNode=volume, movingVolumeNode=templateNode)` actually computes a transform that maps moving (`templateNode`/MNI) to fixed (`volume`/subject), wait—let's check SlicerElastix's `registerVolumes` signature: `def registerVolumes(self, fixedVolumeNode, movingVolumeNode, parameterFilenames=None, outputVolumeNode=None, outputTransformNode=None, ...)`. Passing `(volume, templateNode)` makes `volume` (subject) the FIXED volume and `templa

### D7. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude ok, gemini ok, gpt blocking
- claude on re-check: **real: yes, minor**: I read the whole pipeline in AAL3BrainLabeling.py. It makes no network calls, uses no eval/exec/pickle, runs no downloads or subprocesses, and only writes CSVs to a user-chosen folder and parameter files to the temporary path. The only issue is the overwrite and filename hardening from D1, which is not a concrete path to harm. I rate safety minor, not blocking.
- gpt on re-check: **rating blocking**: AAL3BrainLabeling.py:163 takes the volume node name, while lines 320-323 join it directly to the selected directory and use `with open(csvPath, "w", newline='') as f:`. Matching existing results are silently truncated and path-bearing node names can escape the directory, creating a concrete data-loss path. I inspected the module, CMakeLists.txt and repository-wide searches for network, execution, deserialization and file-writing APIs; external SlicerElastix behavior and the exact revision were not independently verified.
- gemini on re-check: **rating ok**: Inspected AAL3BrainLabeling.py, CMakeLists.txt, README.md, and LICENSE.txt. There is no network communication, telemetry, unsafe deserialization, command injection, or hidden code execution. Writing CSV results to `outDir` using `volName` (D1) is ordinary local file output, not a blocking safety issue.

### D8. Rating of packaging
rating dispute; category packaging; raised by claude, gemini, gpt; outcome after cross-examination: **settled: concern (concern)**
Ratings: claude concern, gemini ok, gpt unknown
- claude on re-check: **real: yes, blocking**: CMakeLists.txt:35 lists a resource file that is missing from the repository (no Resources/Templates directory exists). That breaks the build or install, or the module at runtime. There are also the CPACK/config oddities at lines 51-52. I rate packaging blocking. I did not check EXTENSION_DEPENDS against the catalog entry's build_dependencies.
- gpt on re-check: **rating unknown**: CMakeLists.txt:31-35 lists `Resources/Templates/MNI152_T1_1mm.nii.gz`, and AAL3BrainLabeling.py:201-205 refuses registration if it is absent. The accessible listing omits this resource, but the user reports a contrary scan hint, so its actual repository presence must be established. CMakeLists.txt:14 declares `set(EXTENSION_DEPENDS "SlicerElastix")`, but no catalog entry or dependency implementation is available to check the matching build dependency, source revision or packaging mechanics. Thus packaging admission cannot be fully assessed.
- gemini on re-check: **rating concern**: In CMakeLists.txt:51, `set(CPACK_INSTALL_CMAKE_PROJECTS "${CMAKE_BINARY_DIR};${EXTENSION_NAME};ALL;/")` uses `EXTENSION_NAME` before `include(${Slicer_EXTENSION_CPACK})` defines it, resulting in an empty project name in `CPACK_INSTALL_CMAKE_PROJECTS`. Additionally, `Resources/Templates/MNI152_T1_1mm.nii.gz` listed at line 35 is not visible in the workspace file listing.


## Findings from some reviewers

### Asymmetry results are only printed to stdout and default output path is not shown to the user
minor; soundness; raised by gemini
- **gemini** (minor, medium confidence, quote verified) [`AAL3BrainLabeling.py:106`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L106): If the user runs the pipeline without clicking `Select Results Folder`, `self.outputPath` defaults to `slicer.app.temporaryPath` (line 77), and the UI does not show where the CSV files were written or save the hemispheric asymmetry indices to a file (they are only printed to the Python console in `asymmetry()`).
  ```
      def selectOutput(self):
          """Opens dialog to select the directory for saving clinical results."""
          directory = qt.QFileDialog.getExistingDirectory()
          if directory:
              self.outputPath = directory
              self.outputButton.text = directory
  ```
  Suggestion: Display the output path in the UI and consider exporting the Hemispheric Asymmetry Indices to a CSV file alongside the morphometry and connectome CSVs.

### Bundled atlas and template redistribution terms not stated
minor; license; raised by claude
- **claude** (minor, medium confidence, quote verified) [`README.md:100`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/README.md#L100): The repository bundles the AAL3 atlas, its labels and the MNI152 template. LICENSE.txt covers only the authors' own code as MIT. The upstream licenses are not documented, and AAL3 is distributed under its own terms.
  ```
  If you use this pipeline in your research, please ensure you cite the foundational AAL3 atlas paper:
  ```
  Suggestion: Add a NOTICE or license section for the AAL3 atlas and the MNI152 template, with sources and terms.

### Distance matrix has no region identifiers
minor; utility; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`AAL3BrainLabeling.py:356`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L356): The matrix is saved as numbers only, without row or column names. Researchers cannot reliably associate its positions with anatomical regions from that file alone, particularly when regions are absent.
  ```
      def connectome(self, stats, outDir, volName):
          """Generates a comprehensive Euclidean distance structural connectome matrix."""
          ids = stats['SegmentIDs']
          n = len(ids)
          matrix = np.zeros((n, n))
          centroids = [self.getCentroid(stats, sid) for sid in ids]
  ```
  Suggestion: Write region names or IDs as row and column headers, or export an ordered companion mapping.

### License terms for bundled MNI152 template and AAL3v1 atlas volumes are not documented in LICENSE.txt
minor; license; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`LICENSE.txt:1`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/LICENSE.txt#L1): The extension's code is licensed under MIT (`LICENSE.txt`), and `README.md` cites Rolls et al. (2020) for the AAL3 atlas. However, the repository bundles third-party neuroimaging datasets (`Resources/Atlas/AAL3v1_1mm.nii.gz` and `Resources/Templates/MNI152_T1_1mm.nii.gz`) without documenting their upstream licenses or redistribution terms (e.g., the MNI152 template license and the AAL3v1 atlas distribution terms from GIN/SPM). Users and distributors need clarity on the license terms covering the bundled atlas and template data.
  ```
  MIT License
   
  Copyright (c) 2026 Mustafa Sakci, Niyazi Acer
  ```
  Suggestion: Add a section in `LICENSE.txt` or `README.md` stating the license and copyright/redistribution terms for the bundled `AAL3v1_1mm.nii.gz` atlas and `MNI152_T1_1mm.nii.gz` template.

### Manual CPACK_INSTALL_CMAKE_PROJECTS uses undefined EXTENSION_NAME variable
minor; packaging; raised by gemini
- **gemini** (minor, high confidence, quote verified, other lines) [`CMakeLists.txt:5`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/CMakeLists.txt#L5): In CMakeLists.txt, the project name is set via `project(AAL3BrainLabeling)` (which sets `PROJECT_NAME`), and `EXTENSION_NAME` is never explicitly defined before `set(CPACK_INSTALL_CMAKE_PROJECTS "${CMAKE_BINARY_DIR};${EXTENSION_NAME};ALL;/")`. Furthermore, `include(${Slicer_EXTENSION_CPACK})` already sets `CPACK_INSTALL_CMAKE_PROJECTS` appropriately using `EXTENSION_NAME` (defaulted from `PROJECT_NAME`). Setting `CPACK_INSTALL_CMAKE_PROJECTS` manually with an undefined `${EXTENSION_NAME}` before `include(${Slicer_EXTENSION_CPACK})` can result in a malformed CPack project installation entry (`"...;;ALL;/"`) or conflict with Slicer's standard extension packaging macro.
  ```
  #-----------------------------------------------------------------------------
  # Extension Packaging (Slicer_extension_build yerine standart CPACK)
  #-----------------------------------------------------------------------------
  set(CPACK_INSTALL_CMAKE_PROJECTS "${CMAKE_BINARY_DIR};${EXTENSION_NAME};ALL;/")
  include(${Slicer_EXTENSION_CPACK})
  ```
  Suggestion: Remove line 51 (`set(CPACK_INSTALL_CMAKE_PROJECTS ...)`) and rely solely on `include(${Slicer_EXTENSION_CPACK})`, which handles CPack configuration automatically.

### README inconsistent with code; no research-use disclaimer
minor; utility; raised by claude
- **claude** (minor, high confidence, quote verified) [`README.md:87`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/README.md#L87): The README names buttons and settings that differ from the code ('Run FULL Pipeline', 10,000 spatial samples; the code has 'PROCESS SINGLE VOLUME' and 15000). It describes manual installation instead of the extension manager. It does not say the output is for research only, and it gives no registration validation.
  ```
  3. Click **Run FULL Pipeline**.
  ```
  Suggestion: Align the documentation with the UI, add a research-use disclaimer and some validation or sample data.

### Registration failure handling and GUI-thread processing
minor; soundness; raised by claude
- **claude** (minor, medium confidence, quote verified, other lines) [`AAL3BrainLabeling.py:134`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L134): The Elastix exception is only printed. The caller then reports an error status, but the progress bar stays visible and no error dialog is shown. In batch mode, an exception in one file aborts the whole run. Long registration blocks the UI.
  ```
          except Exception as e:
              print(f"Elastix Error: {str(e)}")
              slicer.mrmlScene.RemoveNode(transformNode)
  ```
  Suggestion: Show errors via slicer.util.errorDisplay, wrap per-file batch processing in try/except, and use a busy cursor or run the work off the GUI thread.

### Registration fallback modifies the shared Python import path
minor; environment; raised by gpt
- **gpt** (minor, high confidence, quote verified, other lines) [`AAL3BrainLabeling.py:45`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L45): When the first import fails, registration permanently adds the Elastix module directory to the shared interpreter's import search path, potentially changing subsequent imports in other modules.
  ```
              try:
                  import Elastix
              except ImportError:
                  elastix_dir = os.path.dirname(slicer.modules.elastix.path)
                  if elastix_dir not in sys.path:
                      sys.path.append(elastix_dir)
  ```
  Suggestion: Use the supported SlicerElastix import mechanism without a permanent sys.path modification, or limit and restore any temporary path change.

### No automated module test included
info; utility; raised by gemini
- **gemini** (info, high confidence, quote verified) [`CMakeLists.txt:27`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/CMakeLists.txt#L27): The extension does not include a `ScriptedLoadableModuleTest` class or any automated self-tests in `CMakeLists.txt` or `AAL3BrainLabeling.py`.
  ```
  set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
  )
  ```
  Suggestion: Add a `AAL3BrainLabelingTest(ScriptedLoadableModuleTest)` class and register the test in `CMakeLists.txt` (`WITH_GENERIC_TESTS` or `slicer_add_python_unittest`).

### Swallowed exceptions and default output path
info; soundness; raised by claude
- **claude** (info, medium confidence, quote verified) [`AAL3BrainLabeling.py:77`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L77): The logo-loading and Segment Editor switch exceptions are silently ignored. The default output directory is the Slicer temporary path, so results can be lost without the user noticing.
  ```
          self.outputPath = slicer.app.temporaryPath
  ```
  Suggestion: Require the user to choose an output folder, or tell them where the files were written.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I found no malicious behavior, network access, package installation or unsafe deserialization. The code only uses Slicer APIs and SlicerElastix and writes CSVs to the chosen folder. The license is MIT, but the licenses of the bundled AAL3 atlas and MNI152 template are not stated. The CMake file is non-standard: it overrides CPACK_INSTALL_CMAKE_PROJECTS with an undefined EXTENSION_NAME and lacks the usual extension config include. It also lists a 10 MB template that I could not confirm is in the repository. The module runs registration on the GUI thread and hides some failures. The README has no clinical disclaimer and does not match the UI. Recommendation: 🔴 Do not merge yet. The packaging and template presence need confirming first. The review is otherwise incomplete only on the template file.
Not checked: Contents of Resources/Templates/MNI152_T1_1mm.nii.gz (not readable; not shown in the file list); Binary atlas, PNG and screenshot contents; Actual upstream license terms of AAL3 and MNI152; Build and runtime behavior inside Slicer (not executed); Whether the catalog 'main' revision equals commit b08789e at build time

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
AAL3BrainLabeling is a clean, self-contained scripted module for AAL3 brain atlas parcellation using SlicerElastix. From an Extensions Index admission perspective, it has no safety or environment issues, has an MIT license, and has a valid catalog entry matching its `CMakeLists.txt` dependencies. However, two soundness bugs in `AAL3BrainLabeling.py` should be addressed: `SegmentStatisticsLogic` does not enable `centroid_ras` (causing the exported connectome distance matrix to be all zeros), and `registerVolumes(volume, templateNode, ...)` registers moving subject to fixed MNI template without inverting the transform when warping the MNI atlas to subject space.

🟢 Recommend merge (admission requirements met; non-blocking scientific correctness fixes strongly recommended).
Not checked: Binary contents of Resources/Templates/MNI152_T1_1mm.nii.gz and Resources/Atlas/AAL3v1_1mm.nii.gz were not directly inspected.; Runtime execution in 3D Slicer with SlicerElastix was not performed (static code review only).
Questions for the author: In `registration()`, `logic.registerVolumes(volume, templateNode, ...)` passes the subject `volume` as `movingVolumeNode` and `templateNode` (MNI152) as `fixedVolumeNode`. Should `templateNode` be the moving volume and `volume` the fixed volume (or should `transform` be inverted) so that the MNI atlas is warped into the subject's native space?; Can you clarify the license and redistribution permissions for the bundled `MNI152_T1_1mm.nii.gz` and `AAL3v1_1mm.nii.gz` files in `LICENSE.txt`?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The Python module and build configuration were inspected, but the exact checkout revision, SlicerElastix, and bundled image provenance could not be verified. Exports can silently overwrite prior results and permit node names to escape the chosen output folder. The matrix also silently substitutes zero coordinates when centroid statistics are absent. 🔴 Do not merge yet: fix the destructive export behavior and provide the missing revision and third-party distribution evidence.
Not checked: Could not independently resolve the provided commit b08789e87142603744cc02512c79a9a8f480a74b or the catalog's moving main branch to the inspected checkout.; The large MNI template and binary atlas could not be inspected; their provenance, image contents, alignment and embedded notices were not verified.; SlicerElastix source, SegmentStatistics defaults, registration transform direction and behavior were not independently inspected.; No build, Slicer execution, tests, CI results, remote license terms, or previous catalog entry were available for verification.
Questions for the author: What are the precise sources and redistribution terms of the AAL3 atlas, MNI template, and associated labels?; Can you provide a build/test result for the catalog revision and verify centroid statistics and atlas registration against a known reference?


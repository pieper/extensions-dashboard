# AI review: MusculoskeletalAnalysis

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis.git at commit `cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T02:35:08Z; cost $0.07

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | minor | ok | minor |
| packaging | minor | ok | minor |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | ok | ok | minor |
| **overall** | minor issues | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer extension for musculoskeletal image quantification: it runs cortical, cancellous, bone-density and intervertebral-disc analyses on a segmented CT/micro-CT volume and appends results to tab-separated report files in a user-chosen directory. It is aimed at musculoskeletal researchers (e.g. bone morphometry, tissue mineral density, trabecular architecture).
- **flash-lite**: The MusculoskeletalAnalysis extension provides tools and scripted Slicer modules to quantify cortical bone, cancellous bone, bone density, and intervertebral discs from 3D images and segmentation masks, exporting tabular reports.
- **haiku**: Provides quantitative musculoskeletal analysis (cortical, cancellous, density, intervertebral disc metrics) from segmented 3D CT-style volumes in 3D Slicer, writing tab-separated reports to a user-chosen folder. It is aimed at musculoskeletal researchers and runs its numerical work as scripted CLI modules.

## Disagreements (start here)

### D1. Intervertebral disc center/height uses the wrong axis index
partial; category soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`CLI/IntervertebralAnalysis/IntervertebralAnalysis.py:57`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CLI/IntervertebralAnalysis/IntervertebralAnalysis.py#L57): `maskData[1]` indexes the volume instead of `np.nonzero(maskData)[1]`, so the y-center is the mean of a single 2D slice's coordinates, and if the chosen column contains no mask voxels np.max/np.min raise on an empty sequence. The disc-height result is therefore arbitrary rather than a center height. Errors surface to the user via tryWithErrorDisplay, hence minor.
  ```
      xcent = int(np.rint(np.mean(np.nonzero(maskData)[0])))
      ycent = int(np.rint(np.mean(np.nonzero(maskData[1]))))
      center = np.nonzero(maskData[xcent,ycent,:])
  ```
  Suggestion: Use `np.nonzero(maskData)[1]` for the y center and guard the empty case.
- **haiku** (major, high confidence, quote verified) [`CLI/IntervertebralAnalysis/IntervertebralAnalysis.py:58`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CLI/IntervertebralAnalysis/IntervertebralAnalysis.py#L58): ycent is computed from np.nonzero(maskData[1]), which takes the nonzero indices of the second x-slab, not the y-center of the mask. The height column is then read from an arbitrary column of the mask, so 'Disc Height' and 'Disc Height Ratio' can be wrong or zero-length, and the reported value is silently wrong.
  ```
  ycent = int(np.rint(np.mean(np.nonzero(maskData[1]))))
      center = np.nonzero(maskData[xcent,ycent,:])
  ```
  Suggestion: Compute the y-center from the nonzero coordinates of the mask in the x-slice, e.g. np.nonzero(maskData)[1], and add a regression test with a known disc phantom.

### D2. Rotating-calipers width uses wrong coordinates (distance and diameter bugs)
single; category soundness; raised by haiku
- **haiku** (major, high confidence, quote partly verified) [`CLI/MusculoskeletalAnalysisCLITools/width.py:39`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CLI/MusculoskeletalAnalysisCLITools/width.py#L39): In the n==2 branch, the distance uses hull[1][1] where it should use hull[1][1]-hull[0][1], so the y term is wrong. In the main loop, the y term uses hull[i][0]-hull[j][1] instead of hull[i][1]-hull[j][1]. Annulus and nucleus widths reported by IntervertebralAnalysis are therefore incorrect, not merely approximate.
  ```
  return math.sqrt((hull[0][0]-hull[1][0])**2+(hull[1][0]-hull[1][1])**2)
  ...
  res = max(res, math.sqrt((hull[i][0]-hull[j][0])**2+(hull[i][0]-hull[j][1])**2))
  ```
  Suggestion: Fix the coordinate differences (y terms use index 1 on both points) and add unit tests against known polygons.

### D3. crop() never applies the one-voxel margin on the low side (no-op comparison)
partial; category soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`CLI/MusculoskeletalAnalysisCLITools/crop.py:13`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CLI/MusculoskeletalAnalysisCLITools/crop.py#L13): `low==low-1` compares instead of assigning, so the low bound is never lowered. The crop still works (it just does not include the intended 1-voxel border); any measurement computed from the cropped volume is slightly tighter than documented. Not a safety issue, but the intended behavior is not implemented.
  ```
          # Leave 1 space between shape and new edge unless the shape was already on the edge
          if low > 0:
              low==low-1
  ```
  Suggestion: Use `low = low - 1` (and add a unit test for crop).
- **haiku** (major, high confidence, quote verified) [`CLI/MusculoskeletalAnalysisCLITools/crop.py:14`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CLI/MusculoskeletalAnalysisCLITools/crop.py#L14): The intent is to leave one voxel of padding before the lowest nonzero index, but '==' is a comparison, so 'low' is never decremented. The cropped array then starts exactly at the mask edge. This affects fill() boundary handling (padding-based hole filling) and the edge-sensitive thickness/width computations for all analyses that call crop, potentially changing reported values.
  ```
  if low > 0:
      low==low-1
  ```
  Suggestion: Use 'low = low - 1' and add a test that asserts the cropped shape includes the margin.

### D4. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Apply-button enablement checks a parameter (`UseDICOM`) that is never written
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Scripted/MusculoskeletalAnalysis/MusculoskeletalAnalysis.py:468`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/Scripted/MusculoskeletalAnalysis/MusculoskeletalAnalysis.py#L468): `UseDICOM` is set nowhere in the module (only `UseAlt`/`UseMan` are managed), so the condition always relies on the DICOMNode reference being present. Because initializeParameterNode() always fills DICOMNode from the first scalar volume, the Apply button is enabled even when the user has selected "Use another node for DICOM tags" with no meaningful node, and conversely a scene without any volume reference keeps Apply disabled. The stated gating (require a DICOM source when alternate tags are chosen) is not actually enforced in the GUI.
  ```
          elif self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetParameter("SegmentID") and (self._parameterNode.GetParameter("UseDICOM")=="False" or self._parameterNode.GetNodeReferenceID("DICOMNode")):
  ```
  Suggestion: Gate on `UseAlt`/`UseMan` (as process() does) and drop the stale `UseDICOM` check.

### Catalog pins to a moving branch and metadata has placeholders
minor; packaging; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`CLI/CorticalAnalysis/CorticalAnalysis.xml:8`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CLI/CorticalAnalysis/CorticalAnalysis.xml#L8): All four CLI XMLs point at `https://github.com/username/project` and have an empty `<license/>`. The extension license itself is MIT (LICENSE.txt), so this is a documentation/metadata defect only; the Help link in the module GUI goes to the correct README.
  ```
      <documentation-url>https://github.com/username/project</documentation-url>
      <license/>
  ```
  Suggestion: Point documentation-url at the README and fill the license element with MIT.
- **haiku** (minor, high confidence, quote verified) [`CLI/CorticalAnalysis/CorticalAnalysis.xml:8`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CLI/CorticalAnalysis/CorticalAnalysis.xml#L8): scm_revision is 'main', so the built extension can change without a catalog update and cannot be tied to the reviewed source commit. The CLI XML files set <documentation-url> to https://github.com/username/project, a placeholder, and have an empty <license/>.
  ```
  <documentation-url>https://github.com/username/project</documentation-url>
      <license/>
  ```
  Suggestion: Pin scm_revision to a tag or commit, replace the placeholder documentation URL with the README, and set the license to MIT.

### Cortical/cancellous/intervertebral metrics assume isotropic voxels and fixed SPL orientation
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CLI/MusculoskeletalAnalysisCLITools/reader.py:11`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CLI/MusculoskeletalAnalysisCLITools/reader.py#L11): readImg() forces SPL orientation and everything downstream uses a single scalar `voxSize`, so slice-wise areas, PMOI, and disc height computed along the third axis are wrong for anisotropic (typical clinical thick-slice) DICOM series. The GUI's manual voxel-size field is one value only, with no warning. Users could obtain silently incorrect morphometry for such scans.
  ```
      image = sitk.DICOMOrient(image, 'SPL')
  ```
  Suggestion: Read the spacing vector from the image header and use per-axis spacing, or validate that the series is isotropic and warn/refuse otherwise.

### Per-voxel Python loop in findSpheres makes cancellous/cortical analysis extremely slow and unresponsive
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CLI/MusculoskeletalAnalysisCLITools/thickness.py:11`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CLI/MusculoskeletalAnalysisCLITools/thickness.py#L11): For every bone voxel the code builds an mgrid sphere mask and does an elementwise maximum; on a typical 512x512xN micro-CT mask this is millions of Python iterations inside the CLI process. The CLI runs without wait_for_completion (MusculoskeletalAnalysis.py:734) so Slicer stays alive, but progress only advances at fixed 20/40/60/80% steps and users see an apparently frozen analysis for a long time, with no way to cancel it.
  ```
      order = np.argsort(dist[a,b,c])
      for n in order:
  ```
  Suggestion: Vectorize with a max-filter / distance-transform-based local thickness implementation, and/or register the CLI node so the user can cancel it.

### Sample-data registration references thumbnail icons that are not in Resources/Icons
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`Scripted/MusculoskeletalAnalysis/MusculoskeletalAnalysis.py:204`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/Scripted/MusculoskeletalAnalysis/MusculoskeletalAnalysis.py#L204): Resources/Icons contains Cancellous1/2, CancellousMask1/2, Cortical1/2, CorticalMask1/2, MusculoskeletalAnalysis.png and Screenshot.png, but no Intervertebral1.png or IntervertebralMask1.png (referenced at lines 204 and 220). Also `IntervertebralMaskSample1.seg.nrrd` is registered with `fileNames='IntervertebralMaskSample1.seg.nrrd'` while nodeNames is IntervertebralMask1, which is fine, but the missing thumbnails mean the tutorial's sample nodes appear without images. Cosmetic, not blocking.
  ```
          thumbnailFileName=os.path.join(iconsPath, 'Intervertebral1.png'),
  ```
  Suggestion: Add the two Intervertebral thumbnails to Resources/Icons or remove the thumbnailFileName arguments.

### Test hardcodes a Windows output path and the generic test is disabled
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`Scripted/MusculoskeletalAnalysis/MusculoskeletalAnalysis.py:825`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/Scripted/MusculoskeletalAnalysis/MusculoskeletalAnalysis.py#L825): The only scripted test writes to os.path.expanduser("~\\Documents\\MusculoskeletalAnalysisTest"), which on Linux/macOS produces a literal backslash filename in the home directory and fails. The CTest registration in Testing/Python is commented out, so the CLI-level behaviour is not covered by build-time tests.
  ```
  outputDirectory = os.path.expanduser("~\\Documents\\MusculoskeletalAnalysisTest")
  ```
  Suggestion: Use tempfile.mkdtemp() or a path under slicer.app.temporaryPath, and enable the Python test in Testing/Python.

### pip_install of unpinned packages into Slicer's interpreter on first Apply
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`Scripted/MusculoskeletalAnalysis/MusculoskeletalAnalysis.py:762`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/Scripted/MusculoskeletalAnalysis/MusculoskeletalAnalysis.py#L762): The install happens only after an explicit user confirmation and only when the user runs an analysis, and it never pins or downgrades numpy/scipy/etc. But `skimage` and `pynrrd`/`trimesh` are installed unpinned from PyPI, so their transitive requirements could upgrade/downgrade packages Slicer bundles; and because `scipy` is often present in Slicer, the check can silently skip a version check. This is the standard pattern but worth noting for a shared environment.
  ```
              if slicer.util.confirmOkCancelDisplay("The following python modules are required: " + ", ".join(names) + ". Do you want to install them?"):
                  for p in pips:
                      slicer.util.pip_install(p)
  ```
  Suggestion: Prefer declaring these in the extension's packaging or use version compatibility checks; at minimum mention the installed packages/versions in the log after install.
- **haiku** (minor, medium confidence, quote verified) [`Scripted/MusculoskeletalAnalysis/MusculoskeletalAnalysis.py:762`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/Scripted/MusculoskeletalAnalysis/MusculoskeletalAnalysis.py#L762): importRequest installs scipy, scikit-image, pynrrd and trimesh into Slicer's Python when missing. Installing scipy with no constraint could upgrade a bundled version, and the install runs synchronously on the GUI thread. The user is asked first, so this is a minor environment risk.
  ```
  if slicer.util.confirmOkCancelDisplay("The following python modules are required: " + ", ".join(names) + ". Do you want to install them?"):
                  for p in pips:
                      slicer.util.pip_install(p)
  ```
  Suggestion: Pip-install only the missing packages with compatible version bounds, and run the installs with progress or in a worker, not on the GUI thread.

### writeReport appends to existing files without telling the user which file is reused
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CLI/MusculoskeletalAnalysisCLITools/writeReport.py:9`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CLI/MusculoskeletalAnalysisCLITools/writeReport.py#L9): Reports are appended to fixed names (cortical.txt, cancellous.txt, density.txt, intervertebral.txt) in the user-chosen directory. Repeated analyses accumulate rows, and if a directory already holds a template file with different columns the data rows are appended under an unrelated header. This is documented in the README but can mix unrelated patients' results in one file; no identifier is written per row except the volume name and date.
  ```
      if os.path.exists(filepath):
          # If the file exist open and append to it
          fOut = open(filepath, "a")
  ```
  Suggestion: Offer unique filenames or write a per-run timestamp/patient column and verify the header matches before appending.

### Category and metadata mismatches
info; utility; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`CMakeLists.txt:8`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/CMakeLists.txt#L8): CMakeLists sets EXTENSION_CATEGORY to 'Analysis', the catalog uses 'Quantification', and the module's parent.categories is 'Quantification'. The module description and helpText contain TODO-style text. These are descriptive, not admission issues.
  ```
  set(EXTENSION_CATEGORY "Analysis")
  ```
  Suggestion: Align the category and clean up the TODO text in helpText and acknowledgements.

### No clinical/research-use disclaimer and no published validation of the derived metrics
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.md:193`](https://github.com/WashUMusculoskeletalCore/Slicer-MusculoskeletalAnalysis/blob/cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb/README.md#L193): The README documents usage and tutorials but gives no statement that the measurements are research tools and not validated for clinical decisions. For metrics such as SMI, connectivity density and polar moment of inertia this matters for interpretation; this is advisory only per the policy.
  ```
  The following additional python packages are required and will be installed the corresponding analysis functions are run:
  ```
  Suggestion: Add a short disclaimer and a citation for the underlying algorithms (e.g. Bouxsein et al. guidelines for micro-CT morphometry).


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): minor issues
MIT-licensed, small, readable extension with sample data, tutorials and a self-test. No concealed behavior, no telemetry, no network transmission of user data (sample data is downloaded only on explicit Sample Data request, with SHA256 checksums). PyPI packages (pynrrd, scikit-image, scipy, trimesh) are installed into Slicer's Python only after an explicit confirmation dialog; none pins or downgrades Slicer-bundled packages or pulls torch, and scipy is usually already present. There are real correctness bugs (crop's `low==low-1` no-op, per-pixel O(n) thickness loop blocking the GUI thread, wrong title sent to the CLI widget-free naming, `useDICOM` parameter never set) and some thick-slice/orientation assumptions, but no safety path to harm — non-blocking per the admission policy. One packaging detail (Intervertebral thumbnails) is cosmetic.
Not checked: Could not verify the source repository revision: the catalog entry pins scm_revision "main" (a moving branch), so the exact commit cda70c23cdc9563aa09bd6148c10d0b3c65b8aeb was not independently resolvable with the available tools; review is of the file snapshot provided.; Could not verify that the Sample Data release assets (v1.1-assets, e.g. CorticalSample1.nrrd) exist, are correctly checksummed, or that their content is de-identified; only the registration code and SHA256 strings were inspected.; Did not build the extension or run the CMake/Slicer build or the module self-test; build/loading correctness is inferred from CMake files only.; Did not inspect the upstream dependencies (pynrrd, scikit-image, trimesh, scipy) or their transitive requirement sets for Slicer-bundled package pins.; Did not check the contents of the committed PNG icons for embedded metadata.
Questions for the author: The catalog entry uses scm_revision "main"; do you intend to keep a moving branch target, or could a release tag be pinned for index stability?; Should the Intervertebral1.png / IntervertebralMask1.png thumbnails be committed, or can the thumbnailFileName arguments be removed?; Are the report files intended to be per-patient? If multiple patients share an output directory, cortical.txt etc. will interleave rows without any patient identifier.; Is the single manual voxel-size field a deliberate restriction to isotropic data? Anisotropic clinical series would yield incorrect areas, PMOI and disc height.

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The MusculoskeletalAnalysis extension is well-structured, follows Slicer conventions for scripted modules and CLI python tools, includes unit tests and sample datasets, and has clear MIT licensing. No safety or soundness issues were found. 🟢 Recommend merge
Not checked: Executing the 3D Slicer module runtime tests in a live Slicer installation

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
No malicious or concealed behavior found in the files read. Network use is limited to sample-data downloads with SHA256 checks, and runtime pip installs are gated by a confirmation dialog. The main concerns are correctness bugs that would silently produce wrong measurements: a no-op comparison in crop.py, a typo'd index in the disc height calculation, and wrong coordinates in the rotating-calipers width code. The catalog entry tracks the unpinned "main" branch, and the CLI XML files have placeholder metadata. I could not run anything or fetch the source revision, so these findings come from reading the included files only.
Not checked: Did not fetch the source repository or verify that commit cda70c23 exists; scm_revision is 'main', so the reviewed revision is unknown.; Did not run the CLI code, the unit test, or the CMake build, and did not verify the numerical outputs against the sample data.; Did not inspect the Resources/UI .ui file, the Icons binaries, or the sample-data files hosted on GitHub Releases (checksums are in code, but I did not download the files).; Did not review the full README beyond what was shown; I read it in full.; Did not verify the Slicer APIs used (slicer.cli, ExportSegmentsToLabelmapNode, pip_install) against the targeted Slicer version.


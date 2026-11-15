# AI review: AAL3BrainLabeling

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/niyaziacer/SlicerAAL3BrainLabeling at commit `b08789e87142603744cc02512c79a9a8f480a74b`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:47:21Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | minor | ok | ok |
| packaging | concern | ok | concern |
| license | concern | ok | concern |
| soundness | concern | ok | concern |
| utility | minor | ok | concern |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A Slicer module that warps the AAL3 atlas onto a patient T1 MRI (N4 bias correction + Elastix rigid/affine/B-spline registration) and exports per-region volume/intensity CSVs, hemispheric asymmetry indices and a centroid-distance connectome matrix, for neuroimaging researchers doing morphometry and cohort batch studies.
- **flash-lite**: Provides an automated AAL3 atlas-based morphometric analysis, hemispheric asymmetry, and distance-connectome pipeline for neuroimaging in 3D Slicer using N4ITK bias correction and Elastix registration.
- **haiku**: An extension that runs an AAL3 atlas-based morphometry pipeline on a user's MRI in 3D Slicer: N4 bias correction, Elastix registration of an MNI152 template, atlas mapping, SegmentStatistics volumes and intensities, asymmetry indices, and a centroid distance matrix. It is intended for neuroimaging researchers, and it depends on SlicerElastix.

## Disagreements (start here)

### D1. Bundled AAL3 atlas and MNI152 template have no stated license or provenance
partial; category license; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`LICENSE.txt:1`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/LICENSE.txt#L1): The MIT license covers only the extension's own code. The extension redistributes third-party data: Resources/Atlas/AAL3v1_1mm.nii.gz (AAL3 atlas, Rolls et al. 2020) and the MNI152 T1 template. Neither file is accompanied by a license, attribution or source URL, and README.md only asks users to cite the paper (line 100-101). Atlas and template terms are commonly research/non-commercial, so users and the index cannot tell whether redistribution inside this extension is permitted.
  ```
  MIT License
  
  Copyright (c) 2026 Mustafa Sakci, Niyazi Acer
  ```
  Suggestion: Add a NOTICE/third-party section (or per-directory license files) naming the exact source, version and license of the AAL3 atlas and the MNI152 template, and state any non-commercial/research-only restriction in the README and module help text.
- **haiku** (major, medium confidence, quote verified) [`LICENSE.txt:1`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/LICENSE.txt#L1): The MIT license covers the author's code only. The AAL3 atlas labelmap and color table, and the MNI152 template, are third-party data that the extension ships. No notice or terms for them are in the repository, so the permission to redistribute them is unclear. The README's citation request is not a license.
  ```
  MIT License
   Copyright (c) 2026 Mustafa Sakci, Niyazi Acer
  ```
  Suggestion: Add a third-party notice listing the source and license of the AAL3 atlas and MNI152 template, and confirm that redistribution is permitted, or have users fetch these files themselves.

### D2. Entire pipeline runs synchronously on the GUI thread; batch mode can freeze Slicer for hours
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`AAL3BrainLabeling.py:151`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L151): run() (line 124) and batch() (line 144) call the logic directly from the button slot, and the logic only pumps the event loop with processEvents(). N4 is run with slicer.cli.runSync (line 294) and Elastix registration with logic.registerVolumes (line 252), so the application is unresponsive for the 3-5 minutes per volume the code itself warns about (line 171), and for a whole cohort in batch mode. processEvents() also allows the user to click 'PROCESS SINGLE VOLUME' again while a run is in progress, starting a second pipeline on the same scene; there is no cancel button and no guard flag.
  ```
  def updateUI(self, msg, progress_val, progress_bar, status_label):
          """Updates UI elements and forces Slicer to process events, preventing app freezes."""
          print(msg)
          if progress_bar: progress_bar.setValue(progress_val)
          if status_label: status_label.text = msg
          slicer.app.processEvents()
  ```
  Suggestion: Run the pipeline in a slicer.util.ProgressDialog / CLI-node based asynchronous worker (or at least a background thread with queued UI updates), disable the run/batch buttons while busy, and provide cancellation.

### D3. MNI152 template resource is installed and required but absent from the repository snapshot
partial; category packaging; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`CMakeLists.txt:31`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/CMakeLists.txt#L31): CMakeLists.txt line 35 lists Resources/Templates/MNI152_T1_1mm.nii.gz as an installed resource and AAL3BrainLabeling.py line 201 loads it as the registration target. Listing the repository (root and Resources/) shows no Templates directory and no such file, while the automated scan reports a 10 MB file it could not read. If the file is really absent, the extension install step references a nonexistent file and, even if it builds, every run stops at 'CRITICAL ERROR: Template missing' (line 204) so the module does nothing. If it is present, it is a 10 MB binary committed to git that should be fetched on demand and whose provenance/license is undocumented.
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/AAL3BrainLabeling.png
    Resources/Atlas/AAL3v1_1mm.nii.gz
    Resources/Atlas/AAL3_ColorTable.ctbl
    Resources/Templates/MNI152_T1_1mm.nii.gz
  ```
  Suggestion: Confirm the file is committed at the exact path used by CMake and the code (or download it on first use with user consent and a checksum), and state its source and license.
- **haiku** (major, medium confidence, quote verified) [`CMakeLists.txt:35`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/CMakeLists.txt#L35): CMakeLists.txt line 35 passes Resources/Templates/MNI152_T1_1mm.nii.gz to slicerMacroBuildScriptedModule, and the code loads it at line 201. The repository listing shows no Resources/Templates directory. If the file is truly absent, the build fails, or the module installs without the template and every registration fails with the 'Template missing' error. The automated scan hint reports the file as 10 MB, so the snapshot may be inconsistent; this must be confirmed.
  ```
  Resources/Templates/MNI152_T1_1mm.nii.gz
  ```
  Suggestion: Confirm the template is committed on the revision in question (or downloaded at build time with a checksum). Otherwise remove it from RESOURCES and document the setup.

### D4. Registration failures are swallowed and reported only through console output
single; category soundness; raised by haiku
- **haiku** (major, high confidence, quote verified, other lines) [`AAL3BrainLabeling.py:134`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L134): Any Elastix exception is caught, printed, and turned into transformNode=None. pipeline() then calls updateUI with an error and returns None. In batch mode, the next volume continues, and volN4 from the failed run is never removed, so nodes accumulate in the scene. Users may not notice that a run produced no output.
  ```
  except Exception as e:
                  print(f"Elastix Error: {str(e)}")
                  slicer.mrmlScene.RemoveNode(transformNode)
                  transformNode = None
  ```
  Suggestion: Surface the error with slicer.util.errorDisplay or a logged message, and remove volN4 when registration fails in pipeline().

### D5. Transform direction may be wrong when the atlas is hardened onto the template-space labelmap
single; category soundness; raised by haiku
- **haiku** (major, low confidence, quote verified) [`AAL3BrainLabeling.py:252`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L252): The code registers the subject volume as fixed and the template as moving (line 252). The atlas is in template space, but the resulting transform is hardened onto the atlas at line 280 without inversion. If the output transform maps subject to template coordinates, the atlas is warped in the wrong direction, and the regional volumes and centroids would be wrong without any error. I did not run this and could not check the SlicerElastix output convention from the repository alone.
  ```
  logic.registerVolumes(volume, templateNode, parameterFilenames=paths, outputTransformNode=transformNode)
  ```
  Suggestion: Verify the transform direction against SlicerElastix conventions using a known test case, and invert the transform if needed. Add a validation step, for example by overlaying the warped atlas on the subject.

### D6. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D7. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D8. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D9. Rating of utility
rating dispute; category utility; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern


## Findings from some reviewers

### Global sys.path modification to import Elastix
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified, other lines) [`AAL3BrainLabeling.py:45`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L45): Appending the SlicerElastix module directory to sys.path mutates the shared interpreter state for the whole Slicer session, which can shadow other modules for unrelated code. The Elastix extension already exposes its Python module, so the fallback is normally unnecessary.
  ```
  try:
                  import Elastix
              except ImportError:
                  elastix_dir = os.path.dirname(slicer.modules.elastix.path)
                  if elastix_dir not in sys.path:
                      sys.path.append(elastix_dir)
  ```
  Suggestion: Drop the sys.path manipulation and rely on the declared SlicerElastix dependency, reporting a clear error if the import fails.

### Hemispheric asymmetry results are printed to the console but never saved
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AAL3BrainLabeling.py:348`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L348): README.md line 17 advertises 'Automatically computes the Asymmetry Index (AI)', but asymmetry() only prints to the Python console; nothing is written to outDir, so batch users lose the values. In addition, str.replace('_L', '_R') replaces every occurrence, which would corrupt names containing '_L' elsewhere.
  ```
  for L_name in vol_data:
              if L_name.endswith("_L"):
                  R_name = L_name.replace("_L", "_R")
                  if R_name in vol_data:
                      L, R = vol_data[L_name], vol_data[R_name]
                      ai = (L - R) / (L + R + 1e-6)
  ```
  Suggestion: Write the AI values to a CSV in outDir (e.g. <vol>_AAL3_Asymmetry.csv) and derive the right-hemisphere name by replacing only the trailing suffix.

### N4 bias correction ignores CLI status and failures propagate silently
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AAL3BrainLabeling.py:293`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L293): The return value of runSync is discarded, so a failed or cancelled N4 run leaves an empty output node that is then used as the registration input (line 174) and as the statistics volume (line 185). The user sees no error and gets plausible-looking but meaningless volumes/intensities. Similarly atlasMapping() (line 275) does not check that loadLabelVolume succeeded before calling atlasNode.GetDisplayNode().
  ```
  out = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", f"{volName}_N4_Corrected")
          slicer.cli.runSync(slicer.modules.n4itkbiasfieldcorrection, None, {"inputImageName": volume.GetID(), "outputImageName": out.GetID()})
          return out
  ```
  Suggestion: Check the returned CLI node status (and that the output volume has data) and report failures with slicer.util.errorDisplay, aborting the pipeline; guard the atlas/color-table loads.

### No clinical-use disclaimer or validation for a research pipeline that produces morphometric values
minor; utility; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`AAL3BrainLabeling.py:34`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L34): The module reports volumes, intensities, asymmetry indices, and connectomes, and the help text calls the output 'publication-quality' and 'clinical'. There is no statement that the outputs are research-only, no validation data, and no tests or sample data to check the pipeline.
  ```
  "Developed for publication-quality biophysics and neuroimaging research."
  ```
  Suggestion: Add a research-use-only disclaimer, a sample dataset or test, and a short validation note.

### No parameter node and results default to the temporary folder
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`AAL3BrainLabeling.py:74`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L74): If the user does not pick a folder, all CSVs are written into Slicer's temporary directory, which is cleared on exit, so results silently disappear. The module also keeps no parameter node, so the selected input/output are not saved with the scene and cannot be scripted or restored, contrary to Slicer conventions.
  ```
  self.outputButton = qt.QPushButton("Select Results Folder")
          self.outputButton.setStyleSheet("padding: 5px; font-weight: bold;")
          formLayout.addRow("Output Directory: ", self.outputButton)
          self.outputPath = slicer.app.temporaryPath
  ```
  Suggestion: Require an explicit output folder (or warn when using the temp path) and store input/output in a vtkMRMLScriptedModuleNode parameter node.
- **haiku** (minor, medium confidence, quote verified) [`AAL3BrainLabeling.py:77`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L77): self.outputPath is initialized to slicer.app.temporaryPath (line 77), which is cleared on Slicer exit, so results can be lost unless the user chooses a folder. Output names are fixed per volume name (lines 320, 368), so re-running overwrites earlier results with no warning.
  ```
  self.outputPath = slicer.app.temporaryPath
  ```
  Suggestion: Default to a persistent user folder, require the user to choose a folder before running, and warn before overwriting.

### No tests, no sample data, no research-use disclaimer
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:73`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/README.md#L73): The extension performs atlas-based morphometry on clinical MRI data but the README contains no statement that results are for research use only and not for diagnosis, and there is no sample dataset or automated test to let a reviewer or user verify the pipeline output. The install section also describes manual Additional Module Paths instead of the extension manager.
  ```
  1. **3D Slicer:** Version 5.10.0 or higher is recommended.
  2. **SlicerElastix:** You must install the SlicerElastix extension via the 3D Slicer Extension Manager.
  ```
  Suggestion: Add a research-use-only disclaimer, a small sample T1 dataset with expected outputs, and a basic self-test.

### README does not match the UI and the code
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`AAL3BrainLabeling.py:242`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L242): The README describes a 'Run FULL Pipeline' button and a 'Batch Process Folder' button. The code uses 'PROCESS SINGLE VOLUME' and 'PROCESS EXTERNAL FOLDER' (lines 80, 84). The README also says 10,000 spatial samples, while the code sets 15000 (line 242). The repository structure section also omits the closing code fence.
  ```
  '(NumberOfSpatialSamples 15000)\n'
  ```
  Suggestion: Align the README with the actual UI labels and parameters.

### Transform hardening uses a non-standard API call
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`AAL3BrainLabeling.py:280`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/AAL3BrainLabeling.py#L280): The documented way to reach the transform logic is slicer.modules.transforms.logic().hardenTransform(node); slicer.vtkSlicerTransformLogic() is not a module-level factory in the Slicer Python API. If it raises AttributeError, the pipeline dies after the atlas node has been added to the scene, leaving orphan nodes and no segmentation.
  ```
  atlasNode.SetAndObserveTransformNodeID(transform.GetID())
          slicer.vtkSlicerTransformLogic().hardenTransform(atlasNode)
  ```
  Suggestion: Use slicer.modules.transforms.logic().hardenTransform(atlasNode) (or slicer.util.getModuleLogic('Transforms')).

### Catalog entry is internally consistent
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`CMakeLists.txt:14`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/CMakeLists.txt#L14): EXTENSION_DEPENDS matches the entry's build_dependencies (SlicerElastix), the category matches (Neuroimaging), the schema is v1.0.1, and scm_revision 'main' is a supported branch reference. The only Python file (AAL3BrainLabeling.py) is listed in MODULE_PYTHON_SCRIPTS, so nothing imported by the module is left uninstalled apart from the missing template noted above.
  ```
  set(EXTENSION_DEPENDS "SlicerElastix")
  ```
  Suggestion: No action needed beyond resolving the template resource question.

### Installed label CSV is unused and disagrees with the color table names
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`Resources/Labels/AAL3_labels.csv:1`](https://github.com/niyaziacer/SlicerAAL3BrainLabeling/blob/b08789e87142603744cc02512c79a9a8f480a74b/Resources/Labels/AAL3_labels.csv#L1): AAL3BrainLabeling.py never reads Resources/Labels/AAL3_labels.csv, yet CMakeLists.txt line 36 installs it. Its names also differ from the color table actually applied to the atlas (Resources/Atlas/AAL3_ColorTable.ctbl line 6: '3 Frontal_Sup_2_L'), so the CSV cannot be used as a reference for the exported region names.
  ```
  ID,Name
  1,Precentral_L
  2,Precentral_R
  3,Frontal_Sup_L
  ```
  Suggestion: Either use the CSV as the single source of region names or remove it from the install list and align the color table names.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
No malicious or network behavior: no downloads, no telemetry, no pip installs, no eval/exec; outputs go to a user-chosen folder. The catalog entry is consistent (SlicerElastix in both build_dependencies and EXTENSION_DEPENDS, Neuroimaging category, tier 1). Main problems are non-safety: the MNI152 template that CMakeLists installs and the code requires is not present in the snapshot I could inspect (build/install or runtime failure), the bundled AAL3 atlas and MNI152 template carry no license/provenance statement, and the whole pipeline runs synchronously on the GUI thread with processEvents. Asymmetry results are printed but never saved.
Not checked: Resources/Templates/MNI152_T1_1mm.nii.gz could not be read (reported as a 10 MB binary by the scan hint, and absent from the file listing I could inspect), so its content, provenance and license are unverified.; Binary resources (Resources/Atlas/AAL3v1_1mm.nii.gz, Resources/AAL3BrainLabeling.png, Screenshots/Screenshot.png) were not opened; the atlas label values were not compared against the color table or the CSV.; The upstream repository at commit b08789e87142603744cc02512c79a9a8f480a74b could not be fetched, so I could not confirm whether the template file exists on the branch, check git history, issues or CI build results.; No Slicer instance was available, so the runtime behavior of slicer.vtkSlicerTransformLogic(), SegmentStatistics key names and the Elastix registerVolumes argument order were assessed from code reading only.
Questions for the author: Is Resources/Templates/MNI152_T1_1mm.nii.gz committed to the repository at that exact path? If so, what is its source and license, and why is a 10 MB binary committed instead of downloaded on demand?; Under what license is the AAL3 atlas (Resources/Atlas/AAL3v1_1mm.nii.gz) redistributed, and does it permit redistribution inside a Slicer extension?; Why is the asymmetry index only printed to the console rather than written to the output folder, and can the pipeline be moved off the GUI thread with a cancel option?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
AAL3BrainLabeling is a well-structured and implemented 3D Slicer extension providing automated AAL3 atlas-based brain labeling, morphometry, asymmetry analysis, and structural distance connectomics using SlicerElastix and N4ITK. The codebase follows Slicer conventions, includes proper license and packaging, handles resource cleanup during batch processing, and presents no safety or environment concerns. 🟢 Recommend merge.
Not checked: Full 3D Slicer runtime environment execution and GUI widget interaction (beyond code inspection)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
I read the module code, CMakeLists, README, LICENSE, the color table and the label CSV. I found no network access, telemetry, pickle/eval, or package installation, so no safety finding. The main problems are packaging and distribution: CMake and the code require Resources/Templates/MNI152_T1_1mm.nii.gz, which is absent from the file listing I could see. The MIT license covers only the code, not the bundled AAL3 atlas or the MNI template. Registration failures are swallowed, and there are soundness issues with transform direction and output location. Overall: needs fixes.
Not checked: I could not run the build, Slicer, SlicerElastix, or the pipeline, and I did not verify the registration result.; I did not read the binary atlas (Resources/Atlas/AAL3v1_1mm.nii.gz) or the color table beyond its first 8 lines, so I did not check that the label IDs match the atlas.; I did not check the MNI152 template file itself, since it is not in the listing.; I did not fetch the scm_url or the revision 'main', so the source at the pinned revision is unverified; the catalog entry pins 'main' rather than a commit.; I did not check the screenshot or the icon content.
Questions for the author: Is Resources/Templates/MNI152_T1_1mm.nii.gz committed on the revision that will be indexed? If so, what are its source and license?; What are the source and license terms for the AAL3 atlas labelmap and color table?; Was the transform direction from registerVolumes(volume, template) checked against the atlas placement? Please show a validation result on a test subject.


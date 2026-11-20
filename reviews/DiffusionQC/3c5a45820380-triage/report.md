# AI review: DiffusionQC

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/pnlbwh/SlicerDiffusionQC at commit `3c5a458203806c087193c8a822b637baba55fbb9`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-20T03:02:09Z; cost $0.09

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | concern |
| environment | concern | ok | concern |
| packaging | minor | ok | ok |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: DiffusionQC (module name GradQC) quality-checks diffusion-weighted MRI by computing KL-divergence-based distances between consecutive slices for each gradient, flagging gradients as pass/fail, and offering a Slicer GUI plus a CLI to review, keep/discard gradients and write a cleaned DWI. It targets diffusion MRI researchers using Slicer/SlicerDMRI.
- **flash-lite**: DiffusionQC provides a quality-checking algorithm for diffusion-weighted MRIs, paired with an interactive graphical review tool for 3D Slicer.
- **haiku**: DiffusionQC provides a quality-control algorithm for diffusion-weighted MRI (per-gradient KL-divergence screening, optional mask creation via SlicerDMRI) plus a GradQC scripted module for manual keep/discard review. It is aimed at diffusion MRI researchers using Slicer.

## Disagreements (start here)

### D1. Core processing hand-off uses np.save of a ragged list and default np.load, which breaks on modern numpy
single; category soundness; raised by haiku
- **haiku** (major, medium confidence, quote verified) [`diffusionqclib/diffusionqclib/gradient_process.py:131`](https://github.com/pnlbwh/SlicerDiffusionQC/blob/3c5a458203806c087193c8a822b637baba55fbb9/diffusionqclib/diffusionqclib/gradient_process.py#L131): process() saves a Python list of arrays with different shapes (mri is 4-D, M is 3-D) via np.save. Modern numpy raises on ragged input, and loading the object array needs allow_pickle=True. grad_process() and the GUI depend on this temp file, so both CLI and visual modes can fail before any QC is computed.
  ```
  mri, M, grad_axis, slice_axis, totalGradients, visualMode= np.load(dqc_temp_file)
  ```
  Suggestion: Save the arrays separately with np.savez (or pickle explicitly with allow_pickle=True on both sides), and avoid storing the data in a temp file in HOME. Test on the numpy version bundled with the target Slicer.

### D2. GUI calls exit(0) from a table-selection handler, which can terminate Slicer and lose review work
single; category soundness; raised by haiku
- **haiku** (major, high confidence, quote verified) [`SlicerDiffusionQC/gradqclib/slicerUserInteraction.py:251`](https://github.com/pnlbwh/SlicerDiffusionQC/blob/3c5a458203806c087193c8a822b637baba55fbb9/SlicerDiffusionQC/gradqclib/slicerUserInteraction.py#L251): gradientUpdate() is connected to the table's selectionChanged signal. When the selection is empty, selectedIndexes()[0] raises and the except branch calls exit(0), which terminates the whole Slicer process. Unsaved Keep/Discard/Sure decisions are lost, and the comment only says the hack is for closing the scene.
  ```
  try:
            index = self.tableHandle.selectedIndexes()[0]
          except:
            exit(0)
  ```
  Suggestion: Return from the handler when there is no selection. Do not call exit() inside Slicer; disconnect observers on scene close instead.

### D3. Unpinned --upgrade pip installs into a PYTHONPATH prefix that can shadow Slicer-bundled packages
single; category environment; raised by haiku
- **haiku** (major, medium confidence, quote verified) [`SuperBuild/External_python-diffusionqclib.cmake:18`](https://github.com/pnlbwh/SlicerDiffusionQC/blob/3c5a458203806c087193c8a822b637baba55fbb9/SuperBuild/External_python-diffusionqclib.cmake#L18): The SuperBuild installs plumbum, nibabel, and pynrrd with --upgrade into python_packages_DIR, which is prepended to Slicer's PYTHONPATH by the launcher. This can replace versions Slicer or other extensions rely on for all users, and the versions are not pinned or tested against Slicer's bundled packages.
  ```
  ${PYTHON_EXECUTABLE} -m pip install plumbum nibabel pynrrd
                                    --prefix "${python_packages_DIR_NATIVE_DIR}" --upgrade
  ```
  Suggestion: Avoid --upgrade; pin version ranges compatible with the Slicer release; check that nibabel/pynrrd are not already provided by Slicer, and document any shadowing.

### D4. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D5. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D6. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Catalog pins a moving branch rather than a reviewed commit
minor; packaging; raised by haiku; **quote not found in source**
- **haiku** (minor, high confidence, quote file not found) [`DiffusionQC.json`](https://github.com/pnlbwh/SlicerDiffusionQC/blob/3c5a458203806c087193c8a822b637baba55fbb9/DiffusionQC.json): scm_revision is 'master', so the built code can change without a catalog update. The reviewed commit 3c5a458 is not what the index will build.
  ```
  "scm_revision": "master",
  ```
  Suggestion: Pin scm_revision to a reviewed commit hash or tag for reproducible builds.

### Documentation targets Python 2.7 and old Slicer, and distutils is used
minor; utility; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`diffusionqclib/diffusionqclib/gradient_process.py:35`](https://github.com/pnlbwh/SlicerDiffusionQC/blob/3c5a458203806c087193c8a822b637baba55fbb9/diffusionqclib/diffusionqclib/gradient_process.py#L35): README says the CLI requires Python 2.7 and describes Slicer 4.9/4.10. gradient_process.py imports distutils.spawn, which is removed in Python 3.12, so the code is not validated against current Slicer Python 3.
  ```
  import distutils.spawn
  ```
  Suggestion: Use shutil.which and update the README for the supported Slicer versions.

### Output files with fixed names are overwritten without confirmation
minor; safety; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`diffusionqclib/diffusionqclib/saveResults.py:73`](https://github.com/pnlbwh/SlicerDiffusionQC/blob/3c5a458203806c087193c8a822b637baba55fbb9/diffusionqclib/diffusionqclib/saveResults.py#L73): saveDWI and saveTemporary write *_modified.nrrd, *_QC.csv, and *_QC.npy into the input or chosen output directory, replacing any existing files with the same prefix. The README states this, but the GUI gives no confirmation, so a previous review can be lost.
  ```
  nrrd.write(outPrefix+'_modified.nrrd', mri_out, header=hdr_out, compression_level = 1)
  ```
  Suggestion: Warn or ask before overwriting, or write to a timestamped name.

### Test script cannot fail and only compares one direction
minor; soundness; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`Test/run_test.py:57`](https://github.com/pnlbwh/SlicerDiffusionQC/blob/3c5a458203806c087193c8a822b637baba55fbb9/Test/run_test.py#L57): run_test.py prints pass/fail but never sets a non-zero exit code, so the CTest entry passes regardless. The difference check is one-sided (a-b).sum() > eps, and the gradient loop uses len(np.where(...)), which is always 1. The test therefore gives no regression protection.
  ```
  if (eval(attr) - eval(attr+'_test')).sum()>eps:
                    failed+=1
  ```
  Suggestion: Use sys.exit(1) on failure, compare absolute differences with np.allclose, and fix the len(np.where(csv==1)) expression.

### nibabel get_data() is removed in nibabel 5 and the unpinned upgrade can pull it in
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`diffusionqclib/diffusionqclib/gradient_process.py:59`](https://github.com/pnlbwh/SlicerDiffusionQC/blob/3c5a458203806c087193c8a822b637baba55fbb9/diffusionqclib/diffusionqclib/gradient_process.py#L59): load_mask calls img.get_data() on NIfTI masks. This method was removed in nibabel 5.0, so mask loading fails for NIfTI masks when the upgraded nibabel is installed.
  ```
  img = nib.load(str(mask))  # MRI loaded as a 256 x 256 x 176 volume
          return img.get_data()
  ```
  Suggestion: Use np.asanyarray(img.dataobj) or img.get_fdata().

### stdout is redirected without restore on error in nhdr_write
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`diffusionqclib/diffusionqclib/nhdr_write.py:72`](https://github.com/pnlbwh/SlicerDiffusionQC/blob/3c5a458203806c087193c8a822b637baba55fbb9/diffusionqclib/diffusionqclib/nhdr_write.py#L72): nhdr_write sets sys.stdout to the file and only restores it on success. Any exception raised while writing the header leaves sys.stdout pointing at a closed file for the rest of the Slicer session.
  ```
  f = open(nhdr, 'w')
      console = sys.stdout
      sys.stdout = f
  ```
  Suggestion: Write with an explicit file handle or wrap in try/finally to restore sys.stdout and close the file.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
No malicious behavior found: no network access, telemetry, downloads or obfuscation; the license (Slicer-style BSD) permits distribution and the catalog entry matches the source (EXTENSION_DEPENDS SlicerDMRI). Main problems are environment and correctness: the superbuild pip-installs unpinned plumbum/nibabel/pynrrd into the extension's site-packages (transitively pulling numpy that can shadow Slicer's numpy), nibabel's removed `get_data()` is still used, and pressing "Save" overwrites the KLdiv results file with a pickled `None`, breaking later GUI runs. Also `exit(0)` inside a Qt slot and a `nextReview` loop that can run off the end. Needs fixes before offering to users.

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
DiffusionQC is a well-structured 3D Slicer extension for quality checking diffusion-weighted MRIs. All inspection criteria are met with no blocking security or packaging concerns.
Not checked: Full execution in 3D Slicer runtime environment; Network tests

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
No malicious, network, or data-exfiltration behavior found in the inspected files; the only subprocess use is an explicit mask tool call and a test-time git-lfs pull. The main problems are soundness: the core CLI/GUI handoff saves a ragged Python list with np.save and loads it with default np.load (fails on modern numpy), the GUI calls exit(0) inside a table-selection handler (can close Slicer and lose review work), and the test never fails. The SuperBuild pip-installs unpinned, --upgrade packages into a PYTHONPATH prefix, and the catalog tracks the moving "master" branch. License is BSD-style research-only, which permits distribution. Overall: needs fixes.
Not checked: Did not execute code, install packages, or run the test; the numpy and nibabel behaviors are from knowledge, not verified in this environment.; Did not inspect the external DiffusionWeightedVolumeMasking executable from SlicerDMRI or the SlicerDMRI dependency.; Did not fetch the remote source at scm_revision master; reviewed only the file contents supplied in the submission.; Did not verify the CTest and CI build results or the Slicer version matrix.; Did not inspect the LFS-tracked binaries beyond the file listing; several Baseline files are committed directly rather than through LFS.; Did not inspect the diffusionQC/CMakeLists.txt install paths against the ExtensionsIndex build beyond reading them.


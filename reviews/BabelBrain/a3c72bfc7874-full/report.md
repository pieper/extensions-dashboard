# AI review: BabelBrain

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/ProteusMRIgHIFU/SlicerBabelBrain.git at commit `a3c72bfc7874d413739c4f4dea66b45d1e2ea73e`
- Context: pull request 2446 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-13T16:26:49Z; cost $0.33

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | ok | ok | blocking |
| environment | ok | ok | ok |
| packaging | minor | ok | unknown |
| license | ok | ok | ok |
| soundness | minor | ok | minor |
| utility | ok | ok | ok |
| **overall** | minor issues | no concerns | needs fixes |

## What each reviewer says the extension does

- **claude**: A thin Slicer front-end that launches a separately installed BabelBrain (transcranial focused ultrasound simulator) with trajectories and a T1w volume from the scene. It exchanges JSON files through ~/.BabelBrainSync and loads the resulting maps and corrected trajectories back into Slicer.
- **gemini**: SlicerBabelBrain integrates 3D Slicer with the external BabelBrain application to run transcranial focused ultrasound (tFUS) acoustic and thermal simulations for trajectories planned in Slicer. It is intended for researchers planning and evaluating tFUS neuromodulation trajectories using subject T1w MRI volumes and SimNIBS segmentations.
- **gpt**: BabelBrain connects 3D Slicer trajectories and anatomical images to a separately installed focused-ultrasound simulation application and imports its results. It is intended for researchers planning and inspecting transcranial ultrasound simulations.

## Disagreements (start here)

### D1. Synchronization input can disclose subject data to other local users
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`BabelBrain/BabelBrainLib/SyncProtocol.py:195`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrainLib/SyncProtocol.py#L195): On a shared POSIX computer, when the home directory and newly created sync directory are traversable by other users, mode 0644 lets those users read the input JSON. BuildInput includes anatomical and segmentation paths, trajectory names and positions, which may contain identifiers or sensitive subject information; chmod also overrides a restrictive umask for the file.
  ```
      os.makedirs(dirname, exist_ok=True)
      fd, tmpname = tempfile.mkstemp(dir=dirname, prefix=".tmp_", suffix=".json")
      try:
          with os.fdopen(fd, "w", encoding="utf-8") as f:
              json.dump(data, f, indent=2)
          os.chmod(tmpname, 0o644)
  ```
  Suggestion: Create or validate the sync directory as private and keep synchronization files owner-readable and writable only, ensuring the same-user BabelBrain process can still access them.
- claude on re-check: **real: yes, minor**: SyncProtocol.py:196-201 does chmod 0o644 on the JSON in ~/.BabelBrainSync (line 39). It contains file paths, trajectory names and positions. Other local users could read it only if the home directory is traversable. This is a local, low-sensitivity, minor hardening issue and not a concrete path to harm. 0600 would be better.
- gpt on re-check: **real: yes, blocking**: BabelBrain/BabelBrainLib/SyncProtocol.py:198-201 explicitly writes the JSON then sets world-readable permissions: `json.dump(data, f, indent=2)` and `os.chmod(tmpname, 0o644)`. Lines 182-188 include absolute anatomical and segmentation paths and trajectory names and positions; BabelBrain/BabelBrain.py:610-618 calls this for the sync input. If parent directories are traversable by other local users, sensitive metadata is exposed despite a restrictive file umask. Use owner-only permissions, including a private sync directory.
- gemini on re-check: **real: yes, minor**: Checked BabelBrain/BabelBrainLib/SyncProtocol.py:192-201 and 39-40. WriteJSONAtomic uses tempfile.mkstemp (which creates files with 0600 permissions) and then explicitly calls os.chmod(tmpname, 0o644) before replacing ~/.BabelBrainSync/BabelBrainInput.json. This overrides the user's umask and makes the file containing anatomical/segmentation paths and trajectory names world-readable if the user's home directory and ~/.BabelBrainSync are traversable. However, since modern Linux distros/macOS typically restrict home directory traversal or this is only file path/trajectory metadata in a user's home directory, this is a minor hardening suggestion (either omit chmod or use 0o600 / chmod 0o700 on SYNC_PATH), not a blocking issue.

### D2. T1 export can overwrite an existing image without confirmation
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`BabelBrain/BabelBrain.py:554`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrain.py#L554): When a modified volume or non-NIfTI input is run, the extension exports it to a predictable name in the selected output directory without checking whether that file already exists. An existing image at that path, potentially another subject's scan or an earlier version, can be overwritten before the later warning is shown.
  ```
          if header is None or header["affine"] is None:
              name = SP.MakeTargetNames([volumeNode.GetName()])[0]
              fname = os.path.join(outputPath, name + "_T1w.nii.gz")
              slicer.util.exportNode(volumeNode, fname)
              header = SP.ReadNiftiHeader(fname)
  ```
  Suggestion: Use a unique filename or explicitly check for an existing destination and obtain informed confirmation before replacing it.
- claude on re-check: **real: yes, minor**: BabelBrain.py:554-558 exports the volume to <outputPath>/<name>_T1w.nii.gz without an existence check. The directory is user-chosen and the file name is derived from the volume, so the file is the extension's own artifact. Overwriting it is a normal behavior and a minor bug. The code warns the user about the saved path (559-560). It is not a safety blocker.
- gpt on re-check: **real: yes, blocking**: BabelBrain/BabelBrain.py:548-560 chooses export for modified, non-NIfTI, or unsuitable-header inputs and calls `slicer.util.exportNode(volumeNode, fname)` at a predictable `<sanitized node name>_T1w.nii.gz` path with no existing-file check or confirmation. The warning is only shown after launch returns (lines 369-377), so a collision can destroy a previous image before notification. Avoid collisions or obtain confirmation before writing. Slicer's export implementation is external to this checkout and was not independently inspected or run.
- gemini on re-check: **real: yes, minor**: Checked BabelBrain/BabelBrain.py:534-563. When the volume node is not backed by an unmodified NIfTI file with a valid affine, prepareAnatomicalVolume exports it to os.path.join(outputPath, name + '_T1w.nii.gz') via slicer.util.exportNode(volumeNode, fname) without checking if that file already exists, and sets exported = fname so the informational message is shown afterward (lines 285-290). Writing derived outputs to a user-selected output directory with a deterministic name (`<VolumeName>_T1w.nii.gz`) is standard behavior in scientific/medical imaging workflows, though checking for existing files or warning before overwriting would be a nice minor UX improvement.

### D3. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude ok, gemini ok, gpt blocking
- claude on re-check: **real: no, info**: Searches of BabelBrain found no network code, pip installs or downloads. The only subprocess is Popen of the user-configured BabelBrain executable (BabelBrain.py:628). The two cited issues are minor, so safety is ok. I did not audit every file.
- gpt on re-check: **rating blocking**: Inspected the sync writer and launch path in BabelBrain/BabelBrainLib/SyncProtocol.py:169-218 and BabelBrain/BabelBrain.py:534-636, plus result handling and process launch. The explicit `os.chmod(tmpname, 0o644)` at SyncProtocol.py:200 creates a concrete conditional local disclosure of potentially identifying subject metadata; the unchecked export at BabelBrain.py:554-557 also risks destructive overwrite. Both warrant safety fixes. The separate BabelBrain application and Slicer's export implementation were not available for inspection; exact source revision was not independently verified.
- gemini on re-check: **rating ok**: Checked BabelBrain/BabelBrain.py and BabelBrain/BabelBrainLib/SyncProtocol.py. Neither D1 nor D2 is a blocking or major safety flaw: the extension communicates locally with an external BabelBrain installation via JSON in ~/.BabelBrainSync and exports a NIfTI volume into the user-chosen output directory when needed. There is no malicious behavior, unauthorized network transmission, or unsafe code execution.


## Findings from some reviewers

### Geometry mismatch warning is shown only after launching BabelBrain
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`BabelBrain/BabelBrain.py:368`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrain.py#L368): prepareT1w reports an affine mismatch that may misplace trajectories, but launch starts the external process before returning that warning. Users cannot review or cancel the mismatch before the application receives the inputs.
  ```
          exe = SP.FindExecutable(self.executableEdit.currentPath.strip())
          try:
              with slicer.util.tryWithErrorDisplay(_("Failed to start BabelBrain."), waitCursor=True):
                  warnings = self.logic.launch(self.trajectorySelector.checkedNodes(),
                                               self.t1Selector.currentNode(), m2m, outdir, [exe])
          except Exception:
  ```
  Suggestion: Validate geometry and present warnings before starting the external application, with an option to cancel.

### Stale output JSON can be loaded as results of a new session
minor; soundness; raised by claude
- **claude** (minor, medium confidence, quote verified) [`BabelBrain/BabelBrain.py:663`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrain.py#L663): findOutputFile only checks whether ~/.BabelBrainSync/BabelBrainOutput.json exists. The file is deleted only at launch, so before the next Run the Load button can load an old or unrelated session's results (including maps and _mod transforms from other trajectories).
  ```
  p = os.path.join(self.syncPath, SP.OUTPUT_JSON)
          return p if os.path.isfile(p) else None
  ```
  Suggestion: Enable loading only for the current session, or show the file's timestamp and createdBy.

### Catalog entry tracks a moving branch
info; packaging; raised by claude
- **claude** (info, high confidence, quote no quote) no file cited: scm_revision is "main", so the built source can change without a catalog update. Branch references are permitted, but the reviewed commit (a3c72bf) is not what is pinned.
  Suggestion: Optionally pin scm_revision to a commit hash or tag.

### Module category differs from extension category
info; utility; raised by claude
- **claude** (info, high confidence, quote verified) [`BabelBrain/BabelBrain.py:43`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrain.py#L43): The module sets "Focused Ultrasound" while the extension's CMake and catalog category is "Ultrasound". This is cosmetic.
  ```
  self.parent.categories = [_("Focused Ultrasound")]
  ```
  Suggestion: Align the two categories.

### Result image paths from JSON are loaded without validation
info; soundness; raised by claude
- **claude** (info, low confidence, quote verified) [`BabelBrain/BabelBrain.py:735`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrain.py#L735): Image paths in BabelBrainOutput.json are passed to slicer.util.loadVolume. The file lives in the user's home directory, so there is no privilege boundary. A tampered file could only make Slicer load arbitrary volume files.
  ```
  node = slicer.util.loadVolume(path, {"name": name, "show": False})
  ```
  Suggestion: Optionally restrict loading to .nii/.nii.gz files under the output directory.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read all the Python code, both CMake files, the LICENSE, the README and the catalog entry. I found no network access, no pip installs, no downloads and no shell use. The only subprocess is the user-selected BabelBrain executable, started with a list of arguments and no shell. The license is BSD-3. CMake installs every Python file the module imports, and build_dependencies and EXTENSION_DEPENDS are consistently empty. The remaining issues are minor: the catalog entry tracks the moving branch "main", a stale output file can enable the Load button before any run, the module category differs from the extension category, and results are loaded from paths named in the JSON. The Screenshot.png file could not be inspected. Recommend merge.
Not checked: Screenshot.png (2 MB) was not readable; The BabelBrain executable itself and its installers were not reviewed (separate project); Behaviour inside a running Slicer was not tested; The remote revision was not resolved; main was assumed to match the commit shown

### Gemini 4 Argon (`google/gemini-4-argon`): no concerns
This extension provides a clean, well-structured bridge between 3D Slicer and the external open-source BabelBrain application for transcranial focused ultrasound simulations. All Python and CMake files at commit a3c72bfc7874d413739c4f4dea66b45d1e2ea73e were inspected. It has no external Python package installations, no network activity, safe local file handling via atomic JSON writes in `~/.BabelBrainSync`, non-blocking subprocess execution, thorough self-tests, and a permissive BSD 3-Clause license. All three admission requirements (security/safety, clear distribution permission, and a mechanically usable catalog entry) are met.

🟢 Recommend merge
Not checked: External BabelBrain application binary/source (https://github.com/ProteusMRIgHIFU/BabelBrain), which users install separately.; Binary image files: Screenshot.png (2 MB), BabelBrain.png, and BabelBrain/Resources/Icons/BabelBrain.png.

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The extension has clear documentation, a BSD license, and a mock-based self-test, but its file handling can overwrite existing images and expose subject-related paths and trajectory data to other local users. The supplied source was inspected, but the catalog branch and exact commit could not be independently resolved. 🔴 Do not merge yet: fix the unintended overwrite and shared-file privacy issues, and verify the catalog revision.
Not checked: No build, Slicer runtime or tests could be run with the available read-only tools.; The source repository and catalog main branch could not be fetched or resolved independently; the supplied source is identified by the user as commit a3c72bfc7874d413739c4f4dea66b45d1e2ea73e, but that mapping is unverified.; The separately installed BabelBrain release, its dependencies and its network behavior were not available for inspection.; No PR checklist, CI results, or previous catalog entry were available.


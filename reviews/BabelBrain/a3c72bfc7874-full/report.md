# AI review: BabelBrain

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/ProteusMRIgHIFU/SlicerBabelBrain.git at commit `a3c72bfc7874d413739c4f4dea66b45d1e2ea73e`
- Context: pull request 2446 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-13T16:21:21Z; cost $0.45

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | ok | ok |
| packaging | unknown | ok | unknown |
| license | unknown | ok | ok |
| soundness | unknown | ok | minor |
| utility | unknown | ok | ok |
| **overall** | minor issues | no concerns | needs fixes |

## What each reviewer says the extension does

- **claude**: A Slicer scripted module that launches a separately installed BabelBrain (transcranial focused ultrasound simulator) with trajectories planned in Slicer. It exchanges JSON files through ~/.BabelBrainSync and loads the resulting maps and corrected trajectories back into the scene.
- **gemini**: BabelBrain integrates 3D Slicer with the external BabelBrain application to run transcranial focused ultrasound (tFUS) acoustic and thermal simulations for planned trajectories. It targets neuroscience and ultrasound researchers who plan linear transform trajectories in Slicer and want to simulate them in BabelBrain and visualize the resulting fields and corrected trajectories back in Slicer.
- **gpt**: BabelBrain connects 3D Slicer to a separately installed BabelBrain application for transcranial focused ultrasound simulations. It sends planned trajectories and anatomical inputs to the simulator and loads resulting maps and corrected trajectories for research users.

## Disagreements (start here)

### D1. Exported T1 image can overwrite an existing user file
single; category safety; raised by gpt; outcome after cross-examination: **mostly confirmed**
- **gpt** (blocking, high confidence, quote verified) [`BabelBrain/BabelBrain.py:554`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrain.py#L554): For a modified or non-NIfTI volume, export uses a predictable filename in the chosen output directory without checking whether it already exists. A previous subject's image or another user file with that name can be overwritten just by starting a run.
  ```
          if header is None or header["affine"] is None:
              name = SP.MakeTargetNames([volumeNode.GetName()])[0]
              fname = os.path.join(outputPath, name + "_T1w.nii.gz")
              slicer.util.exportNode(volumeNode, fname)
              header = SP.ReadNiftiHeader(fname)
  ```
  Suggestion: Choose a unique export path or obtain explicit confirmation before overwriting, and check export success.
- claude on re-check: **disagree** (minor): BabelBrain.py:554-558 does write `<name>_T1w.nii.gz` without an exists check. But it goes into the output directory the user chose, and the name comes from the volume being processed. It only replaces an earlier export of the same volume, or a file the user put there on purpose. It is only reached when the volume is modified or not NIfTI, and a warning shows the path. This is an ordinary robustness gap, not a concrete path to harm.
- gpt on re-check: **agree** (blocking): BabelBrain/BabelBrain.py:548-558 uses the original only for an unmodified suitable NIfTI, otherwise exports to a deterministic path with no collision check: 'fname = os.path.join(outputPath, name + "_T1w.nii.gz")' followed by 'slicer.util.exportNode(volumeNode, fname)'. The warning is issued only after launch returns (lines 370-377), so an existing file at that path can be overwritten before the user is warned.
- gemini on re-check: **agree** (minor): In BabelBrain/BabelBrain.py lines 554-558, if the volume node has no NIfTI storage or was modified, it exports the volume to `os.path.join(outputPath, name + "_T1w.nii.gz")` using `slicer.util.exportNode(volumeNode, fname)` without checking if `fname` already exists. However, since `outputPath` is the user-selected output directory for the simulation run, this is at most a minor usability/file-management issue rather than a blocking safety issue.

### D2. Repeated runs silently overwrite previous output archives
single; category safety; raised by gpt; outcome after cross-examination: **mostly confirmed**
- **gpt** (blocking, high confidence, quote verified) [`BabelBrain/BabelBrain.py:656`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrain.py#L656): Running the same named trajectories again in the same output directory overwrites the previous archived result JSON without warning. This can destroy the prior association of simulation results and corrected trajectories, including the only archived copy after the shared sync file is reset.
  ```
          src = os.path.join(self.syncPath, SP.OUTPUT_JSON)
          if self.outputPath and os.path.isfile(src):
              import shutil
              dst = os.path.join(self.outputPath, "+".join(self.targetNames) + "_" + SP.OUTPUT_JSON)
              shutil.copyfile(src, dst)
  ```
  Suggestion: Use a unique per-run archive name or explicitly ask before replacing an existing file.
- claude on re-check: **disagree** (minor): BabelBrain.py:654-660 copies the sync output JSON to `<outputPath>/<targets>_BabelBrainOutput.json`. A rerun with the same trajectory names replaces the earlier archive, which is a regeneration of derived results in the user's chosen output folder. It is a minor usability issue, not a safety blocker.
- gpt on re-check: **agree** (blocking): BabelBrain/BabelBrain.py:654-660 says 'the sync file is reset on every launch' and uses 'dst = os.path.join(self.outputPath, "+".join(self.targetNames) + "_" + SP.OUTPUT_JSON)' followed by 'shutil.copyfile(src, dst)'. A later run with the same target names and output directory overwrites the archived JSON without checking or asking. Whether another copy exists depends on the user's workflow.
- gemini on re-check: **agree** (info): In BabelBrain/BabelBrain.py lines 654-660, `archiveOutput()` copies `~/.BabelBrainSync/BabelBrainOutput.json` to `os.path.join(self.outputPath, "+".join(self.targetNames) + "_" + SP.OUTPUT_JSON)` via `shutil.copyfile(src, dst)`. Running a simulation with the same target names and output directory overwrites the previous archived output JSON, which matches how BabelBrain itself writes simulation outputs in the output directory. This is standard behavior for re-running with the same output directory and target names, or at most a minor/info point, not a blocking safety issue.

### D3. Starting a run deletes shared sync output from another session
single; category safety; raised by gpt; outcome after cross-examination: **mostly confirmed**
- **gpt** (blocking, high confidence, quote verified) [`BabelBrain/BabelBrainLib/SyncProtocol.py:214`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrainLib/SyncProtocol.py#L214): The default sync directory is shared with BabelBrain/Brainsight, but there is no cross-process ownership or active-session check. Starting this extension while another session is active removes its output JSON and can overwrite its unread input; the other session may lose its results or receive the wrong inputs.
  ```
      os.makedirs(sync_path, exist_ok=True)
      out = os.path.join(sync_path, OUTPUT_JSON)
      if os.path.isfile(out):
          os.remove(out)
      return os.path.isfile(os.path.join(sync_path, INPUT_JSON))
  ```
  Suggestion: Coordinate access across processes, refuse or explicitly resolve an active or unconsumed session, and preserve existing sync data before replacing it.
- claude on re-check: **disagree** (minor): SyncProtocol.py:208-218 removes only `~/.BabelBrainSync/BabelBrainOutput.json`, which is the extension's own protocol file. Deleting it is intentional so a stale result isn't mistaken for a new one. BabelBrain.py:616-617 logs a warning when an unread input is replaced. Two concurrent sessions would collide, but that follows from the fixed shared-path protocol. It is not data destruction of user files.
- gpt on re-check: **agree** (blocking): BabelBrain/BabelBrainLib/SyncProtocol.py:39-42 defines a per-home shared sync directory, and lines 214-218 contain 'if os.path.isfile(out):' followed by 'os.remove(out)'. BabelBrain/BabelBrain.py:599-600 checks only 'self.isRunning()', while lines 616-618 prepare the shared directory and replace its input. A second Slicer instance or separate Brainsight session can therefore lose an output or have unread input replaced; the exact downstream outcome depends on timing.
- gemini on re-check: **agree** (minor): In BabelBrain/BabelBrainLib/SyncProtocol.py lines 39-42 and 208-218, `PrepareSyncDirectory` uses the fixed path `~/.BabelBrainSync` (following the upstream BabelBrain/Brainsight protocol described in lines 4-10) and removes `BabelBrainOutput.json` before writing `BabelBrainInput.json`. While BabelBrainLogic checks `self.process` within the same Slicer instance (BabelBrain/BabelBrain.py lines 599-600), an external BabelBrain/Brainsight session sharing `~/.BabelBrainSync` could have its sync files overwritten if the user starts a second run concurrently. This is a protocol limitation worth noting as minor/info, not a blocking safety vulnerability.

### D4. Sync input JSON can expose patient-related data to other local users
single; category safety; raised by gpt; outcome after cross-examination: **mostly confirmed**
- **gpt** (blocking, high confidence, quote verified) [`BabelBrain/BabelBrainLib/SyncProtocol.py:198`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrainLib/SyncProtocol.py#L198): The input contains anatomical and segmentation paths, trajectory names and positions. The explicit 0644 mode makes it readable to other local accounts whenever the home and sync directories are traversable, as is possible with normal directory defaults; users are not asked to consent to this disclosure.
  ```
          with os.fdopen(fd, "w", encoding="utf-8") as f:
              json.dump(data, f, indent=2)
          os.chmod(tmpname, 0o644)
          os.replace(tmpname, fname)
  ```
  Suggestion: Create and verify an owner-only sync directory and use owner-only file permissions, while ensuring compatibility with the separately installed simulator.
- claude on re-check: **disagree** (info): SyncProtocol.py:200 sets 0o644 on a JSON under the user's home directory. The file holds only file paths, trajectory names and matrices, and BabelBrain consumes and renames it. It stays on the local machine. Home directories are typically not world-traversable, and nothing is sent over a network. This is hardening at most, not a blocking concern.
- gpt on re-check: **agree** (blocking): BabelBrain/BabelBrainLib/SyncProtocol.py:179-188 includes '"anatomicalPath": os.path.abspath(anatomical_path),' and trajectory names and positions; lines 198-201 contain 'os.chmod(tmpname, 0o644)' and 'os.replace(tmpname, fname)'. On POSIX systems, other local users can read the patient-related JSON if the home and sync directories are traversable. Directory permissions and platform affect actual exposure; 0644 explicitly overrides a restrictive umask for the file.
- gemini on re-check: **agree** (minor): In BabelBrain/BabelBrainLib/SyncProtocol.py lines 196-201, `WriteJSONAtomic` creates a temporary file via `tempfile.mkstemp` (which defaults to 0o600) and then explicitly calls `os.chmod(tmpname, 0o644)` before replacing `fname` in `~/.BabelBrainSync`. On shared multi-user POSIX systems where the user's home directory is world-traversable, `0o644` makes `BabelBrainInput.json` (containing local file paths and target coordinates) world-readable. Removing `os.chmod(tmpname, 0o644)` or using `0o600` (and `0o700` on `.BabelBrainSync`) is a good hardening practice, though minor in severity.

### D5. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **mostly rejected**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **disagree** (info): I searched BabelBrain for urllib, requests, pip_install, socket, eval, exec, pickle, shell=True and download. There were no matches. BabelBrain.py:628 launches a user-configured executable with a list of args and no shell. Network use and package installation were not found. I read the Python in BabelBrain.py:520-680 and SyncProtocol.py:1-260. I did not read the rest of the module, so the rating is ok and not blocking.
- gpt on re-check: **agree** (blocking): I support a blocking safety rating, not 'ok': the inspected extension has concrete unintended file-overwrite and local disclosure paths. For example, BabelBrain/BabelBrain.py:659-660 has 'dst = os.path.join(self.outputPath, "+".join(self.targetNames) + "_" + SP.OUTPUT_JSON)' and 'shutil.copyfile(src, dst)'; BabelBrain/BabelBrainLib/SyncProtocol.py:200 has 'os.chmod(tmpname, 0o644)'. I inspected the module, protocol, build files and README; the separately installed BabelBrain executable and the exact source revision were not independently verified, and no code was run.
- gemini on re-check: **disagree** (info): Checked all files in the repository (`BabelBrain/BabelBrain.py`, `BabelBrain/BabelBrainLib/SyncProtocol.py`, `CMakeLists.txt`). There is no malicious behavior, telemetry, network communication, unsafe deserialization, or command injection (subprocess is invoked as a list without `shell=True` in `BabelBrain/BabelBrain.py` lines 625-630). The items raised by gpt (D1-D4) are minor local file-handling/permission observations rather than blocking safety vulnerabilities, and the full source code is available and inspected so safety is not `unknown`. The appropriate safety rating is `ok` (or `minor`).


## Findings from some reviewers

### Coordinate mismatch warning appears after the simulator starts
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`BabelBrain/BabelBrain.py:368`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrain.py#L368): The affine mismatch warning is returned by launch only after it has written the input and started BabelBrain. Users cannot decide whether to correct a potentially misplaced trajectory before the simulator receives it.
  ```
          exe = SP.FindExecutable(self.executableEdit.currentPath.strip())
          try:
              with slicer.util.tryWithErrorDisplay(_("Failed to start BabelBrain."), waitCursor=True):
                  warnings = self.logic.launch(self.trajectorySelector.checkedNodes(),
                                               self.t1Selector.currentNode(), m2m, outdir, [exe])
          except Exception:
  ```
  Suggestion: Validate and display actionable warnings before writing the sync input and starting the external process.

### Log file handle remains open if module widget is cleaned up while process runs
info; soundness; raised by gemini; **quote not found in source**
- **gemini** (info, high confidence, quote quote not found) [`BabelBrain/BabelBrain.py:588`](https://github.com/ProteusMRIgHIFU/SlicerBabelBrain/blob/a3c72bfc7874d413739c4f4dea66b45d1e2ea73e/BabelBrain/BabelBrain.py#L588): `BabelBrainWidget.cleanup()` stops the poll timer and removes scene observers, but does not call `self.logic._closeLog()` if `self.logic` still has an open `_logHandle` when the widget is destroyed or reloaded while BabelBrain is running. A `cleanup` helper on `BabelBrainLogic` (or closing the log handle when cleaning up) would avoid leaving the log file descriptor open.
  ```
          if self.process is not None and self.process.poll() is None
  ```
  Suggestion: Close `self.logic._closeLog()` during `BabelBrainWidget.cleanup()` or in `BabelBrainLogic.__del__`.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read all the Python source, both CMakeLists files, the LICENSE and the README. I found no network access, downloads, pip installs, telemetry, or unsafe deserialization. The extension only runs a user-chosen or default BabelBrain executable with a fixed flag, using argument lists and no shell. It writes JSON to ~/.BabelBrainSync and a log to the user's output folder. The BSD-3 license is clear, and CMake installs all the Python files that are imported. The catalog entry tracks branch `main`, which is allowed. One real bug: error handling around `tryWithErrorDisplay` can raise UnboundLocalError after a failure. Documentation and tests are good, and the README carries a research-only disclaimer. 🟢 Recommend merge.

### Gemini 4 Argon (`google/gemini-4-argon`): no concerns
The BabelBrain extension provides a clean, well-structured bridge between 3D Slicer and the external BabelBrain transcranial focused ultrasound simulation application using a local JSON file protocol. All code was inspected: it makes no network calls, does not modify Slicer's Python environment, uses safe subprocess invocation (`shell=False`) and atomic file writes, includes unit and end-to-end tests, and is distributed under the BSD 3-Clause license. No blocking or major issues were found. 🟢 Recommend merge.
Not checked: External BabelBrain executable (>= 0.8.8) which is installed separately by the user; Binary image content of Screenshot.png and BabelBrain.png

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The extension has concrete privacy and data-loss risks in its shared sync and output-file handling. Its BSD-3-Clause license and listed module scripts were inspected, but the catalog branch and external simulator could not be independently verified. 🔴 Do not merge yet: protect patient-related sync data and prevent unintended overwrites and deletion.
Not checked: No network or shell access: could not resolve catalog branch main or independently verify that the supplied source tree corresponds to commit a3c72bfc7874d413739c4f4dea66b45d1e2ea73e, or inspect the actual PR and CI results.; Could not run Slicer, build the extension, execute tests, or verify runtime behavior across platforms.; The separately installed BabelBrain and SimNIBS source, releases, dependencies, and behavior were not available for inspection.


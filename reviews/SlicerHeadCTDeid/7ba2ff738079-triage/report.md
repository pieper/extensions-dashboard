# AI review: SlicerHeadCTDeid

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/payabvashlab/SlicerHeadCTDeid at commit `7ba2ff738079fa8c98c57bf1507a5865419cd52f`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T22:06:38Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | concern | concern |
| environment | blocking | blocking | blocking |
| packaging | minor | ok | ok |
| license | ok | ok | ok |
| soundness | concern | minor | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **deepseek**: SlicerHeadCTDeid is a Slicer scripted module for research de-identification of head CT DICOM series: it strips PS3.15 confidentiality-profile metadata, replaces dates and remaps UIDs, defaces 3D reconstructions by dilating air into superficial soft tissue, and masks burned-in text detected by a Florence-2 vision-language model. It targets imaging researchers and data-sharing groups who need to send head CT cohorts outside their institution.
- **flash-lite**: A 3D Slicer scripted module for de-identifying head CT DICOM files, removing facial surface features, and masking burned-in text.
- **haiku**: A 3D Slicer scripted module that de-identifies head CT DICOM series: it strips PS3.15 metadata, removes superficial facial tissue, and masks burned-in text found by a Florence-2 vision-language model. It is for researchers who need to share head CT data across institutions.

## Disagreements (start here)

### D1. Downgrade of Slicer's numpy through pip_uninstall/pip_install("numpy<2")
partial; category environment; raised by deepseek, flash-lite
- **deepseek** (blocking, high confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:2507`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L2507): If the (just reinstalled) torch is older than 2.3, the code uninstalls numpy and installs 'numpy<2' into Slicer's environment, downgrading a package Slicer bundles. Extensions and Slicer internals built against numpy 2.x can then fail to import for every user of that Slicer installation, including users who never open this module.
  ```
              if version.parse(torch.__version__) < version.parse("2.3"):
                  slicer.util.pip_uninstall("numpy")
                  slicer.util.pip_install("numpy<2")
  ```
  Suggestion: Never pin or downgrade numpy. Require a compatible torch via the PyTorch extension and refuse to run with a clear message instead of modifying the environment.
- **flash-lite** (blocking, high confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:2508`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L2508): 
  ```
      slicer.util.pip_uninstall("numpy")
      slicer.util.pip_install("numpy<2")
  ```
  Suggestion: Remove programmatic uninstallation of Slicer-bundled numpy and downgrading/pinning numpy to <2.

### D2. Florence-2 loaded with trust_remote_code=True from an unpinned community repo
single; category safety; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:68`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L68): The default model id points at a third-party 'community' mirror and the revision is left empty; on the remote-code path (lines 1033-1034, 1418-1419) weights are fetched and the repository's Python module is executed in Slicer's interpreter. Whoever controls that Hub repository (or a tag/tip change) can therefore execute arbitrary code with the user's privileges, on a machine that holds medical images. The code itself notes the model is loaded from the network on first run (~1.5 GB) without an explicit opt-in dialog.
  ```
  FLORENCE_MODEL_ID = "florence-community/Florence-2-large"
  # Set an immutable revision for a locked validation run. Empty retains legacy behavior.
  FLORENCE_MODEL_REVISION = ""
  ```
  Suggestion: Pin the model to a commit hash, prefer the native transformers Florence-2 implementation (already supported) so trust_remote_code is unnecessary, and require explicit user consent before the first download.

### D3. Full batch processing runs on the GUI thread
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:2468`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L2468): process() walks all patient folders, runs the DICOM/face pipeline and waits (wait_for_all_subprocesses timeout 7200 s) directly inside the Qt slot, so Slicer freezes for the duration of a batch and cannot process events or let the user cancel; progress bar updates are posted from the same blocked thread.
  ```
              summary = self.logic.process(
                  self.ui.inputFolderButton.directory,
  ```
  Suggestion: Run the pipeline in a slicer.util.ProcessedEvent / worker thread or CLI, with the progress bar driven by queued signals and a working Cancel.

### D4. Global warning suppression at module import
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:32`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L32): This runs when the scripted module is imported, i.e. at Slicer startup for anyone with the extension installed, and silences every Python warning for the entire Slicer session, including deprecation warnings other extensions and Slicer core rely on users/developers seeing. It is a process-wide side effect from a module the user never opened.
  ```
  warnings.filterwarnings("ignore")
  ```
  Suggestion: Use warnings.catch_warnings() with local filters around the specific third-party calls instead of a global filter.
- **haiku** (major, high confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:32`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L32): warnings.filterwarnings("ignore") runs when the module is imported, so it silences all Python warnings for the whole Slicer process, not just this module. This can hide deprecation or other warnings from other extensions and from Slicer itself.
  ```
  warnings.filterwarnings("ignore")
  ```
  Suggestion: Scope the filter to the specific code paths that need it, using catch_warnings(), or remove it.

### D5. Remote code executed from an unpinned Hugging Face repository
single; category safety; raised by haiku
- **haiku** (major, medium confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:1406`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L1406): The fallback Florence-2 load uses trust_remote_code=True. FLORENCE_MODEL_REVISION defaults to an empty string, so the code fetched from the florence-community repository is not pinned to a commit. A change to that repository would run new Python code on the user's machine with no review. This is a supply-chain risk rather than a confirmed compromise, and it depends on the transformers version installed.
  ```
  kw = {"trust_remote_code": True,
  ```
  Suggestion: Pin FLORENCE_MODEL_REVISION to a specific commit hash, verify it, and prefer the native transformers Florence2 class so that remote code is not needed.


## Findings all reviewers agree on

### Bare except handler pip-installs/removes torch and other packages in Slicer's shared environment
blocking; environment; raised by deepseek, flash-lite, haiku
- **deepseek** (blocking, high confidence, quote verified, other lines) [`HeadCTDeid/HeadCTDeid.py:598`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L598): Any exception escaping process() -- a malformed CSV, a corrupt DICOM, an out-of-memory error, or a GUI error -- falls into a catch-all that unconditionally uninstalls and reinstalls PyTorch from the PyTorch index URL, pins python-gdcm==3.0.25 and pandas==2.2.3, and reinstalls transformers/pillow/pylibjpeg in the same Python environment Slicer and all other extensions share. PyTorch is not installed through the Slicer PyTorch extension (EXTENSION_DEPENDS is "NA"), and the user is never asked for confirmation; after this an unrelated extension or Slicer itself can break for the whole installation. Worse, the handler swallows the real error, so the user sees only a 'restart Slicer' message while the actual failure (and any partially written output) is unexplained.
  ```
          except Exception:
              slicer.util.pip_install("python-gdcm==3.0.25")
              slicer.util.pip_uninstall("torch")
              slicer.util.pip_install([ "torch", "--extra-index-url", "https://download.pytorch.org/whl/cu121"])
  ```
  Suggestion: Remove the silent install block. Report the original exception to the user, and install optional dependencies only on an explicit user action with confirmation, using PyTorchUtils from the PyTorch extension for torch and without pinning packages Slicer bundles.
- **flash-lite** (blocking, high confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:2488`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L2488): 
  ```
      slicer.util.pip_uninstall("torch")
      slicer.util.pip_install([ "torch", "--extra-index-url", "https://download.pytorch.org/whl/cu121"])
  ```
  Suggestion: Remove programmatic uninstallation of Slicer-bundled PyTorch and direct pip installation of PyTorch from PyPI/PyTorch index URLs; require PyTorchUtils instead.
- **haiku** (blocking, high confidence, quote verified, other lines) [`HeadCTDeid/HeadCTDeid.py:598`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L598): Any exception during processing that is not ValueError or FileNotFoundError falls into the bare except at line 2486. It then runs pip_uninstall('torch') and reinstalls torch from the cu121 PyTorch index, pins pandas==2.2.3, uninstalls and reinstalls opencv, and runs numpy<2 when torch is older than 2.3. These steps change the Python environment that every Slicer module shares, and they run on ordinary processing errors such as a malformed DICOM. The user is only told to restart afterwards. Per the index policy, PyTorch must come from the PyTorch extension, and Slicer-bundled packages must not be downgraded.
  ```
          except Exception:
              slicer.util.pip_install("python-gdcm==3.0.25")
              slicer.util.pip_uninstall("torch")
              slicer.util.pip_install([ "torch", "--extra-index-url", "https://download.pytorch.org/whl/cu121"])
  ```
  Suggestion: Remove the automatic pip block from the exception handler. Report the error to the user with the traceback and log it. Install any missing dependencies only after explicit user confirmation, through the PyTorch extension for torch, and without pinning or downgrading numpy, pandas, or other Slicer-bundled packages.


## Findings from some reviewers

### Extension dependency declared as "NA" despite torch/transformers/PyPI requirements
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`CMakeLists.txt:13`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/CMakeLists.txt#L13): The catalog entry has an empty build_dependencies list and the CMake project declares no dependency, yet the module needs PyTorch and transformers, and attempts to install them itself. Declaring the PyTorch extension dependency would make builds/installs consistent with the catalog entry and let the installer resolve torch correctly instead of the in-module pip logic.
  ```
  set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies
  ```
  Suggestion: Add PyTorch to EXTENSION_DEPENDS and to the catalog entry's build_dependencies, and use PyTorchUtils rather than pip.

### Module-level environment variable mutation for HuggingFace cache
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:988`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L988): HF_HOME/HUGGINGFACE_HUB_CACHE are written into the process environment (also in the worker at 1299-1300, 2351-2353), so a run changes cache locations for any other HuggingFace-using extension in the same Slicer process. It only takes effect when the non-default cache dir is configured, which limits the impact.
  ```
          os.environ["HF_HOME"] = str(FLORENCE_HF_CACHE_DIR)
          os.environ["HUGGINGFACE_HUB_CACHE"] = os.path.join(str(FLORENCE_HF_CACHE_DIR), "hub")
  ```
  Suggestion: Pass cache_dir= explicitly to from_pretrained/snapshot_download instead of mutating os.environ.

### No automated tests and no sample data
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`HeadCTDeid/CMakeLists.txt:23`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/CMakeLists.txt#L23): A de-identification tool whose correctness is safety-relevant ships without any unit test (e.g. for the PS3.15 tag handling or UID remapping) and without sample data, so regressions in metadata scrubbing cannot be detected by the extension build.
  ```
  if(BUILD_TESTING)
    # No unit tests for this module
    # (slicer_add_python_unittest removed)
  ```
  Suggestion: Add at least a self-test on a synthetic DICOM with known PHI tags and a small anonymized sample series.
- **haiku** (minor, high confidence, quote verified) [`HeadCTDeid/CMakeLists.txt:24`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/CMakeLists.txt#L24): The CMake file states there are no unit tests. The README says the tool is still being validated and that independent validation is recommended. Users cannot check the de-identification output from the extension itself.
  ```
    # No unit tests for this module
    # (slicer_add_python_unittest removed)
  ```
  Suggestion: Add a small synthetic-DICOM test for the PS3.15 actions and the date handling, or document the validation performed.

### README contradicts the code on whether text-positive files are removed
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`README.md:108`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/README.md#L108): The README says the text-removal option 'removes the corresponding DICOM files', but the later Capabilities section and the code describe masking in place with no image discarded. Users relying on the README could expect different behavior from what they get.
  ```
  <b>Remove text inside dicom</b>: This feature examines for any burned-in text within the images and removes the corresponding DICOM files.
  ```
  Suggestion: Update the README so the option description matches the masking behavior described at lines 65 and 48.

### Real error replaced by a package-install message
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:2484`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L2484): Only ValueError/FileNotFoundError are surfaced as user errors; every other failure (corrupt DICOM, pandas dtype issue, disk full, GPU OOM) is not reported, which conflicts with the rubric expectation that errors reach the user. Combined with the install block this can silently produce a batch the user believes is fine.
  ```
          except (ValueError, FileNotFoundError) as exc:
              slicer.util.errorDisplay(str(exc), windowTitle="Input error")
          except Exception:
  ```
  Suggestion: Log and display the exception (traceback + processor._processing_errors), and let the per-examination summary report failures rather than masking them.

### No outbound transfer of image data found
info; safety; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`HeadCTDeid/HeadCTDeid.py:2355`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/HeadCTDeid/HeadCTDeid.py#L2355): Searches for requests/urllib/socket/telemetry returned only HuggingFace model downloads (snapshot_download, from_pretrained) and pip index URLs; I found no code uploading images, identifiers or logs, so the network traffic appears limited to fetching the model and packages. This holds for the ~2900 lines I could read, not for every one of the 5698 lines.
  ```
  from huggingface_hub import snapshot_download
  ```

### README and in-tool contact addresses disagree
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.md:12`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/README.md#L12): The README gives at4049@​cumc.columbia.edu as contact while the Apply-time warning dialog uses sp4479@​columbia.edu (HeadCTDeid.py:2458); one of them is presumably stale, which matters for users reporting de-identification failures.
  ```
  *Warning: This tool is a work in progress and is currently being validated as part of an AHA-funded research project. For more information, contact at4049@cumc.columbia.edu. Use at your own risk.*
  ```
  Suggestion: Use one current contact address in both places.

### macOS .DS_Store files committed to the repository
info; packaging; raised by deepseek
- **deepseek** (info, high confidence, quote no quote) [`DS_Store:1`](https://github.com/payabvashlab/SlicerHeadCTDeid/blob/7ba2ff738079fa8c98c57bf1507a5865419cd52f/DS_Store#L1): Two 6 KB .DS_Store files exist at the repository root and in HeadCTDeid/. They are harmless but add binary noise to the source tree; add them to .gitignore.
  Suggestion: Delete them and add .DS_Store to .gitignore.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Substantial, well-documented research tool (BSD-3-Clause, extensive README with QC/provenance notes, partial-output safety). Two blocking-level problems: on any exception the Apply handler silently reinstalls/uninstalls Slicer's shared Python packages including `torch` from a PyTorch index URL with no PyTorch extension dependency, and downgrades Slicer's numpy; and the workflow sets `trust_remote_code=True` for an unpinned community Florence-2 repo. Also `warnings.filterwarnings("ignore")` at import, processing on the GUI thread, no unit tests, `.DS_Store` files committed, and `EXTENSION_DEPENDS "NA"` despite heavy pip requirements. No telemetry or outbound data transfer of image data was found in what I inspected.
Not checked: HeadCTDeid/HeadCTDeid.py lines ~200-600, 600-2400 in full detail, and 2900-5698 (DICOM tag handling, defacing and CSV writing internals) were only sampled via regex searches, not read line by line; Whether the Florence-2 worker subprocess (FLORENCE_WORKER_SOURCE around lines 1280-1700) makes any network call other than model/processor download; The binary/pdf assets (images/*.png, documents/dicomTags.pdf) could not be read; the 10 MB images/face.png mentioned in the scan hints was not listed in the provided file inventory; Whether the referenced scm_revision 'main' tip equals the reviewed commit 7ba2ff738079fa8c98c57bf1507a5865419cd52f; The license terms of the florence-community/Florence-2-large HuggingFace repository and of the upstream Microsoft Florence-2 weights; Runtime behaviour, GUI responsiveness and platform-specific build success were not executed or verified
Questions for the author: Why does the Apply error handler install and uninstall torch, numpy and other packages instead of reporting the exception, and why is PyTorch not obtained through the Slicer PyTorch extension (EXTENSION_DEPENDS/build_dependencies)?; Can the module pin FLORENCE_MODEL_REVISION to an immutable commit and avoid trust_remote_code=True by using the native transformers Florence-2 implementation by default?; Is the numpy<2 downgrade still required, and if so, cannot the dependency be resolved without modifying Slicer's numpy?; Which contact address is current: at4049@​cumc.columbia.edu (README) or sp4479@​columbia.edu (in-module warning)?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): needs fixes
SlicerHeadCTDeid is a 3D Slicer extension designed for de-identifying head CT DICOM files, removing superficial facial features, and masking burned-in text. While the packaging and licensing are in order, the extension programmatically uninstalls and reinstalls PyTorch from a CUDA wheel index URL and uninstalls and downgrades numpy (<2) inside an `except Exception` block in `HeadCTDeid/HeadCTDeid.py`. This violates core Slicer extension policies regarding shared Python environment stability and PyTorch installation (which must be handled via `PyTorchUtils` and declared build dependencies). Therefore, the extension needs fixes before it can be accepted.
Not checked: Detailed execution behavior of the Florence-2 model subprocess and DICOM de-identification algorithms under actual Slicer runtime conditions.
Questions for the author: Why does the module execute pip uninstall and pip install for torch and numpy during error handling instead of using build_dependencies and PyTorchUtils?

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The module's core purpose is clear and the license is permissive BSD-3. However, the error handler in the module's apply path runs an unconditional sequence of pip uninstalls and installs on any unexpected exception. That includes uninstalling and reinstalling torch from a PyTorch CUDA index, downgrading numpy to <2, and pinning pandas, which affects Slicer's shared Python environment. The Florence-2 model is loaded with trust_remote_code=True and no pinned revision by default. I found no outbound transfer of patient data. The review is not complete: I did not read most of the 5,700-line module.
Not checked: Most of HeadCTDeid/HeadCTDeid.py (about 5,700 lines) was not read, including the PS3.15 tag tables, face-removal algorithm, OCR filtering, and the file-rename logic in the batch processing path.; The GitHub source at revision 'main' was not resolved, so the reviewed commit is unknown and the code may have changed since this review.; The Florence-2 model weights and their license were not checked, and the README's images/face.png link and the documents/dicomTags.pdf tag list were not opened.; Whether the referenced icon and UI files exist was not verified beyond directory listings.; No code was run. CI results were not available.
Questions for the author: Why does the exception handler at line 2486 reinstall torch, numpy, and other packages? Can this be replaced with an error message and a user-confirmed install through the PyTorch extension?; Will you pin FLORENCE_MODEL_REVISION to a specific commit, and can you explain why trust_remote_code is needed when a native Florence2 class exists?; Does text removal mask regions only, or does it remove files? The README and the code disagree (README line 108).


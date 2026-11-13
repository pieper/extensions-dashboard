# AI review: Pictologics

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/martonkolossvary/SlicerPictologics at commit `2d217f88e4fb1a78f50ec4b61370ba362de35651`
- Context: pull request 2435 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-13T17:12:29Z; cost $1.20

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | ok | ok |
| packaging | unknown | ok | unknown |
| license | unknown | ok | unknown |
| soundness | unknown | ok | minor |
| utility | unknown | ok | ok |
| **overall** | minor issues | no concerns | needs fixes |

## What each reviewer says the extension does

- **claude**: Pictologics is a Slicer extension that extracts IBSI-standardised radiomics features from 3D images and segmentations. It runs the Pictologics library in an out-of-process scripted CLI worker, and it lets users review, batch-process and export the results with provenance. It is for researchers.
- **gemini**: Pictologics is a 3D Slicer extension for researchers to extract IBSI-compliant radiomic features (intensity, morphology, and texture) from 3D scalar volumes and segmentations across single cases or study batches. It provides presets, an in-app preprocessing and filter-bank builder, provenance tracking, a read-only results browser, and full-precision CSV/JSON export.
- **gpt**: Pictologics lets Slicer users extract radiomic intensity, shape and texture features from images and segmented regions. It is intended for researchers who want to configure, review and export features with provenance.

## Disagreements (start here)

### D1. CSV export silently overwrites existing companion files
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`PictologicsSlicer/PictologicsLib/exports.py:44`](https://github.com/martonkolossvary/SlicerPictologics/blob/2d217f88e4fb1a78f50ec4b61370ba362de35651/PictologicsSlicer/PictologicsLib/exports.py#L44): The save dialog in PictologicsSlicer.py:2700-2715 only selects and confirms the main CSV. The writer at lines 3849-3870 also generates <stem>.provenance.json and <stem>_catalog.csv, and exports.py:55-58 replaces every destination. Thus exporting a new features.csv can silently destroy an unrelated existing features_catalog.csv or features.provenance.json, even when the main CSV did not exist. The temporary backups are removed after success.
  ```
          destinations = [destination.parent / path.name for path in files]
          for source, target in zip(files, destinations, strict=True):
              if target.is_symlink() or (target.exists() and not target.is_file()):
                  raise ValueError("Export destination must be a regular file, not a link or directory.")
              if target.exists():
  ```
  Suggestion: Before writing, enumerate all destinations and explicitly confirm every existing file that will be replaced, or refuse collisions and let the user select another name.
- claude on re-check: **real: yes, minor**: Verified. PictologicsSlicer.py:2700-2715 only shows the OS save dialog for the main file. writeSet (3849-3871) also writes <stem>.provenance.json and <stem>_catalog.csv, and exports.py:55-58 os.replace()s every destination after backing it up to a temp dir that is removed on success. An unrelated file with a matching name is therefore overwritten with no prompt. The companion names are derived from the chosen stem, though, and the code comment at 3862-3863 says replacing an older catalog is intentional. It also fails safe for symlinks and directories (exports.py:46-47) and rolls back on error. This is a small UX/data-loss gap that needs a coincidentally named file. It is not a concrete path to serious harm, so it is not blocking.
- gpt on re-check: **real: yes, blocking**: PictologicsSlicer/PictologicsSlicer.py:2700-2715 selects only the main filename and checks that path, not its companions; lines 3849-3873 create both companions, including `dictionaryPath = stagedPath.with_name(f"{stagedPath.stem}_catalog.csv")`. PictologicsSlicer/PictologicsLib/exports.py:44-57 backs up any existing targets then executes `os.replace(source, target)` for each; lines 76-81 delete the staging directory on success. Thus even a new features.csv can silently destroy an unrelated existing features_catalog.csv or features.provenance.json. The user guide, docs/user-guide.md:51-57, describes companion creation but does not provide collision confirmation. Confirm all existing destinations before publication.
- gemini on re-check: **real: yes, minor**: Verified in PictologicsSlicer/PictologicsSlicer.py:2700-2715 (`onExport` only checks overwrite confirmation for the main CSV path via `QFileDialog.getSaveFileName` or `path.with_suffix(".csv").exists()`), PictologicsSlicer/PictologicsSlicer.py:3849-3873 (`writeSet` always generates `<stem>.provenance.json` and `<stem>_catalog.csv` alongside `<stem>.csv` and notes in line 3862-3863: "Always write it, so that an empty catalog replaces the one of an older export"), and PictologicsSlicer/PictologicsLib/exports.py:44-58 (`export_file_set` calls `os.replace(source, target)` for every file in the set). While the code does replace existing `<stem>.provenance.json` and `<stem>_catalog.csv` without separate prompts if `<stem>.csv` didn't exist, these are tightly named sidecar files (`<stem>.provenance.json` and `<stem>_catalog.csv`) in a user-selected save directory during an explicit export action. Prompting before overwriting pre-existing sidecars when the main file doesn't exist would be a nice minor UX improvement, not a blocking safety issue.

### D2. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **real: yes, minor**: The only safety issue I verified is the unconfirmed overwrite of companion export files (exports.py:44-58, PictologicsSlicer.py:3849-3871). That issue is minor and deliberate, with backup and rollback. I did not do a full audit for network access, downloads or deserialization, so I rate this minor rather than blocking. The cited evidence does not support blocking.
- gpt on re-check: **rating blocking**: The verified unconfirmed companion-file overwrite in D1 is a concrete path to user data loss, so safety is blocking rather than ok or unknown: PictologicsSlicer/PictologicsSlicer.py:3849-3873 generates companions and PictologicsSlicer/PictologicsLib/exports.py:55-57 calls `os.replace(source, target)`. I also checked the export dialog at PictologicsSlicer/PictologicsSlicer.py:2691-2742 and searched the GUI and CLI sources for network, process-execution, deserialization and deletion APIs; this is not a complete audit. The downloaded Pictologics package and exact repository revision were not independently verified.
- gemini on re-check: **rating ok**: The extension performs local radiomics feature extraction and export using staged atomic writes (`PictologicsSlicer/PictologicsLib/exports.py:19-81`, `PictologicsSlicer/PictologicsSlicer.py:3849-3874`), checks for symlinks/non-files before writing (`exports.py:46-47`), and has no malicious behavior, hidden network calls, or unsafe deserialization. Writing the companion `<stem>.provenance.json` and `<stem>_catalog.csv` files during a user-initiated CSV export is minor at most and does not warrant a blocking safety rating.


## Findings from some reviewers

### Configuration validation blocks the Slicer GUI
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified, other lines) [`PictologicsSlicer/PictologicsSlicer.py:224`](https://github.com/martonkolossvary/SlicerPictologics/blob/2d217f88e4fb1a78f50ec4b61370ba362de35651/PictologicsSlicer/PictologicsSlicer.py#L224): The Validate handler calls this method directly on the GUI thread (lines 1825-1829). If the helper is slow or stuck, communicate blocks the event loop for up to five minutes; the timeout limits the duration but does not keep the UI responsive.
  ```
          try:
              output, _ = process.communicate(timeout=300)
          except subprocess.TimeoutExpired:
              # Never let a stuck helper process freeze Slicer.
              process.kill()
              process.communicate()
  ```
  Suggestion: Run the check asynchronously or poll the process while reporting progress and supporting cancellation.

### Multiple large derivative branding assets committed to the source repository
info; packaging; raised by gemini; **quote not found in source**
- **gemini** (info, high confidence, quote quote not found) [`assets/branding/pictologics/README.md:13`](https://github.com/martonkolossvary/SlicerPictologics/blob/2d217f88e4fb1a78f50ec4b61370ba362de35651/assets/branding/pictologics/README.md#L13): The repository includes 22 derivative branding files in `assets/branding/pictologics/` (including a ~2 MB `.icns`, ~2 MB `.tiff`, ~1.7 MB master PNG, ~1.2 MB 4096px PNG, ~1.1 MB `.eps`, ~1.1 MB `.webp`, ~1.1 MB 1024px PNG, and ~0.9 MB `.svg`), totaling ~13 MB in the git checkout. While CMake properly excludes these from the built Slicer extension archive, committing multiple multi-megabyte master and print-format derivatives increases repository clone size for the Extensions Index build system and contributors.
  ```
  assets/branding/pictologics/raster/pictologics-master-1254.png  (1675535 bytes, binary)
  assets/branding/pictologics/raster/pictologics-master-1254.webp  (1144018 bytes, binary)
  assets/branding/pictologics/raster/pictologics-vector-render-4096.png  (1223228 bytes, binary)
  assets/branding/pictologics/raster/pictologics-white-1254.jpg  (597284 bytes, binary)
  ```
  Suggestion: Consider keeping only the catalog/module PNG icons and the master source (or generating derivatives on demand with `scripts/export_branding_assets.py`) to keep the git repository lightweight.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I reviewed the catalog entry, the CMake files, the dependency-management code, the worker's environment isolation and the helper scripts. I did not read the 180 KB GUI module line by line. The extension installs Pictologics only after a user confirmation that states the destination folder, about 600 MB of disk use, and network access. The install goes into an extension-private folder through `pip --target`, with wheel-only installs and exact constraints. Slicer's shared Python is not modified, there is no install at import or startup, and I found no telemetry, network service or unsafe deserialization. Apache-2.0 licensing is clear. Remaining concerns are minor: the catalog entry tracks the moving `main` branch, the constraints carry no hashes, and the pip index is not pinned.
Not checked: 
<parameter name="item">The full contents of PictologicsSlicer.py (180 KB) beyond the dependency-install path and the grep results

### Gemini 4 Argon (`google/gemini-4-argon`): no concerns
Pictologics is a remarkably well-engineered radiomics extension for 3D Slicer. It meets all three admission requirements: (1) safety and environment isolation are exemplary, installing pinned wheel-only dependencies into an extension-private directory only after explicit user consent and running all computations in an isolated subprocess without mutating Slicer's shared Python packages; (2) licensing is clear under Apache-2.0 with proper `NOTICE` and dataset attributions; and (3) the catalog entry and CMake build configuration are complete and consistent.

🟢 Recommend merge
Not checked: External PyPI wheel contents for pictologics==1.0.1 and its transitive dependencies (not bundled in this repository; installed at runtime after user consent).; Binary contents of the three 2 MB image files (pictologics.icns, pictologics-master-1254.tiff, and docs/screenshots/pictologics-workflow.png).; Live runtime execution inside 3D Slicer (static source inspection only).

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The wrapper isolates its scientific dependencies and asks before installation, and the source includes documentation and tests. However, CSV export can silently overwrite existing companion files. External runtime wheels and their complete licensing were not available for inspection, and the catalog revision could not be independently resolved. 🔴 Do not merge yet: fix the unintended overwrite and complete the external-payload and revision review.
Not checked: No code, tests, Slicer build, factory package or CI checks were executed.; No network tools were available to independently resolve the catalog's main branch or verify that the inspected snapshot matches the stated commit 2d217f88e4fb1a78f50ec4b61370ba362de35651.; The separately downloaded Pictologics 1.0.1 wheel, its transitive dependency artifacts, their runtime behavior and complete license notices were not accessible.; Large binary branding and screenshot files were not inspected.


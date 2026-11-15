# AI review: ZebrafishEmbryoAnalyzer

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer.git at commit `a6b1b6e93dee7e00f5e5eccb698ec4100423781d`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:41:51Z; cost $0.08

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | minor |
| environment | concern | ok | concern |
| packaging | concern | ok | concern |
| license | concern | ok | concern |
| soundness | minor | ok | minor |
| utility | ok | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer module for batch morphometry of 2-D zebrafish embryo microscopy images: it segments body/eye/edema/swim-bladder with Segformer models, measures body length, curvature class, length/straight-line ratio and eye metrics, and exports results to CSV/Excel. It targets zebrafish researchers doing high-throughput developmental/toxicology screening, not clinicians.
- **flash-lite**: The ZebrafishEmbryoAnalyzer extension for 3D Slicer provides batch segmentation, body length, curvature classification, and eye/edema/swim bladder metrics for 2D zebrafish microscopy images using PyTorch-based neural network models.
- **haiku**: Analyzes zebrafish embryo 2-D microscopy images in 3D Slicer (body length, curvature class, length/straight-line ratio, eye, edema and swim-bladder metrics) using locally run segmentation and classification models. Intended for research users who install it from the Extensions Index; the models are downloaded from Hugging Face on first use after user confirmation.

## Disagreements (start here)

### D1. All model weights are marked LICENSE_PENDING in the manifest
partial; category license; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/model_manifest.py:58`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/model_manifest.py#L58): The module's core function depends on ten model files downloaded from huggingface.co/markdanielarndt/*, and the manifest's own header (line 11) says 'Licenses are "LICENSE_PENDING" until confirmed'. README.md:322-325 defers to the model cards. Distribution permission for the material the extension fetches is therefore unconfirmed by the submission itself; the code is Apache-2.0 but the weights are the substance of the tool.
  ```
  "license": "LICENSE_PENDING",
  ```
  Suggestion: Confirm and record the license of each Hugging Face model repository (or state explicitly that the author owns them and releases them under a named license), and replace LICENSE_PENDING with the actual identifier.
- **haiku** (major, high confidence, quote verified) [`ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/model_manifest.py:58`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/model_manifest.py#L58): All model entries are marked LICENSE_PENDING. The README says the weights have their own license terms and points to Hugging Face model cards, but the manifest does not record what those terms are. Users have no verified permission for the weights they download and use, and the extension's Apache-2.0 license does not cover them.
  ```
  "license": "LICENSE_PENDING",
  ```
  Suggestion: Confirm the license on each Hugging Face model card (markdanielarndt/Zebrafish_Segmentation and markdanielarndt/Classification), record the SPDX identifier in model_manifest.py, and state any non-commercial or research-only restriction in the README and the Slicer help text.

### D2. Catalog entry build_dependencies is empty while the extension declares EXTENSION_DEPENDS "PyTorch"
partial; category packaging; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`CMakeLists.txt:11`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/CMakeLists.txt#L11): The submitted catalog entry has "build_dependencies": [], but the extension's own CMakeLists declares PyTorch as an extension dependency. The index uses build_dependencies to build/package dependency extensions, so the entry and the source disagree about what the extension needs; the packaged extension can be produced without the PyTorch extension it depends on, and the mismatch is exactly the kind of 'demonstrably wrong setting' the admission rules ask to block on.
  ```
  set(EXTENSION_DEPENDS "PyTorch")
  ```
  Suggestion: Set "build_dependencies": ["PyTorch"] in the catalog entry (or drop EXTENSION_DEPENDS if PyTorch is only a runtime, user-installed dependency — but then the runtime install path must be the only one).
- **haiku** (major, high confidence, quote verified) [`CMakeLists.txt:11`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/CMakeLists.txt#L11): CMakeLists.txt declares a runtime dependency on the PyTorch extension, and the module requires PyTorchUtils to install torch. The catalog entry sets build_dependencies to [], so the index may not build or configure the extension against PyTorch, and the dependency declaration is inconsistent between the two places.
  ```
  set(EXTENSION_DEPENDS "PyTorch")
  ```
  Suggestion: Add "PyTorch" to build_dependencies in the catalog entry so it matches EXTENSION_DEPENDS, or justify the difference.

### D3. macOS install path downgrades numpy, which Slicer bundles and shares with all extensions
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/dependency_installer.py:43`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/dependency_installer.py#L43): On macOS, install_packages() appends "numpy<2" to the pip requirements (lines 282-283) and runs slicer.util.pip_install on Slicer's own interpreter. Any user who confirms the install dialog gets numpy replaced in the shared environment, which affects every other extension and Slicer itself, not just this module. The code comments acknowledge the PyTorch extension applies the same constraint, but doing it from a third-party extension means the downgrade happens even for users who never open the module again after one run.
  ```
  NUMPY_TORCH_SPEC = "numpy<2"
  ```
  Suggestion: Let PyTorchUtils/the PyTorch extension own the numpy constraint (it already does), or at minimum surface the numpy downgrade explicitly in the confirmation dialog text and restrict it to the torch install step rather than the general requirements list.
- **haiku** (major, medium confidence, quote verified) [`ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/dependency_installer.py:282`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/dependency_installer.py#L282): On darwin, the installer appends numpy<2 to the pip install. This downgrades or pins numpy, which Slicer bundles, in the shared Slicer Python environment, affecting every extension and the Slicer session. The change is user-confirmed, but it is a shared-environment change that persists after the module is closed.
  ```
  if _numpy_must_stay_v1() and (requirements or _numpy_major() >= 2):
          requirements.append(NUMPY_TORCH_SPEC)
  ```
  Suggestion: Prefer the PyTorch extension's own numpy constraint, which the README says it already applies. Otherwise, make the numpy downgrade an explicit, separately-confirmed step, and tell the user that it affects Slicer's shared environment.

### D4. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D5. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D6. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Global monkey-patch of a third-party library function
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/logic.py:68`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/logic.py#L68): The extension replaces zebrafish_measure.seg._load_unet_model process-wide and stashes the original on the library module to survive reloads. Any other code in the same Slicer process that uses zebrafish_measure gets the cached wrapper and an unbounded _MODEL_CACHE of ~180 MB models. It is confined to a third-party library rather than Slicer/VTK, and analysis runs in a worker subprocess, so impact is limited, but it is a global side effect that is not undone.
  ```
  _seg_module._load_unet_model = _cached_load_unet
  ```
  Suggestion: Pass a cache/loader explicitly to segmentation_pipeline if the library allows it, or bound the cache and restore the original on module cleanup.
- **haiku** (minor, medium confidence, quote verified) [`ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/logic.py:68`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/logic.py#L68): _install_model_cache replaces _load_unet_model inside the third-party zebrafish_measure.seg module. The patch is applied in the worker subprocess and in the in-process run_analysis path. It caches models by path and changes the behavior of any other code in the same process that uses that library.
  ```
  _seg_module._load_unet_model = _cached_load_unet
  ```
  Suggestion: Pass the cached loader explicitly through the library's API if it exposes one, or limit the patch to the worker process and document it.

### Module import evicts modules from sys.modules at import time
minor; soundness; raised by haiku
- **haiku** (minor, low confidence, quote verified) [`ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzer.py:48`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzer.py#L48): On import, the extension pops its own module names from sys.modules to force reloads. The work is confined to the extension's own names, so the impact is limited, but it is a global side effect that runs before the module is used.
  ```
  def _evict_reload_modules():
      for _m in _RELOAD_MODULES:
          sys.modules.pop(_m, None)
  ```
  Suggestion: Keep the eviction to setup() and enter() only, and document why it is needed for Slicer reload.

### README says the extension is not available in the Extensions Manager
minor; utility; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`README.md:56`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/README.md#L56): Once the catalog entry is live this instruction is wrong and will confuse users; the rest of the README (tutorial, screenshots, measurement reference, research-use disclaimer) is otherwise strong.
  ```
  The extension is not yet available through the Extensions Manager and must be installed manually from this repository.
  ```
  Suggestion: Update the installation section to the Extensions Manager flow when the entry is published.
- **haiku** (minor, high confidence, quote verified) [`README.md:56`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/README.md#L56): The installation section tells users to add the module path by hand, which conflicts with the catalog submission and could confuse users once the extension is listed.
  ```
  The extension is not yet available through the Extensions Manager and must be installed manually from this repository.
  ```
  Suggestion: Update the installation section to describe installation from the Extensions Manager once the entry is accepted.

### Results are sorted by path but originals are re-attached by index
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/logic.py:429`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/logic.py#L429): analyse_images() iterates over sorted(image_paths), so the returned list order is alphabetical, not the order the user loaded the images. InferenceController._merge_originals (inference_runner.py:296-300) then pairs results[i] with originals[i] positionally. If the widget collects originals in load order, a result row can be displayed with another image's pixels, i.e. wrong measurements shown against the wrong picture. I could not read widget.py to confirm the originals ordering, so this is a suspected rather than verified mismatch.
  ```
  for _loop_i, image_path in enumerate(sorted(image_paths)):
  ```
  Suggestion: Either drop the sort (preserve caller order) or key the merge on image_path/filename instead of list index.

### cv2 imported at module level in overlay.py, so the gallery needs OpenCV before any analysis
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/overlay.py:8`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/overlay.py#L8): gallery_tab.populate() calls make_overlay() for every result, including placeholders for images that have not been analysed, so merely listing loaded images requires OpenCV. The dependency_installer comments acknowledge this ('Showing images at all needs OpenCV'), which means the 'images' purpose pulls a package the user may not need; it is a usability wart rather than a defect.
  ```
  import numpy as np
  import cv2
  ```
  Suggestion: Import cv2 lazily inside make_full_overlay and fall back to a plain numpy thumbnail when it is unavailable.

### PyTorchUtils.installTorch is called with askConfirmation=False
info; environment; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/dependency_installer.py:205`](https://github.com/MarkDanielArndt/SlicerZebrafishEmbryoAnalyzer/blob/a6b1b6e93dee7e00f5e5eccb698ec4100423781d/ZebrafishEmbryoAnalyzer/ZebrafishEmbryoAnalyzerLib/dependency_installer.py#L205): The PyTorch extension's own confirmation is suppressed, but the extension shows its own confirmOkCancelDisplay before calling install_packages (widget.py:1249), so the user still opts in. The Windows-only torchVersionRequirement "<2.13.0" is a cap passed through PyTorchUtils rather than a direct pip pin, which is the sanctioned route.
  ```
  if torch_logic.installTorch(
          askConfirmation=False,
          torchVersionRequirement=_windows_torch_version_requirement(),
      ) is None:
  ```
  Suggestion: Consider passing askConfirmation=True so the PyTorch extension's own dialog (which names the download size) is not bypassed.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Well-engineered, unusually careful code: no data leaves the machine, model weights are fetched from pinned Hugging Face revisions and SHA-256 verified, np.load uses allow_pickle=False, no eval/exec, and package installation is behind an explicit confirmation dialog with torch routed through the PyTorch extension. Three issues need fixing: the catalog entry's empty build_dependencies contradicts EXTENSION_DEPENDS "PyTorch"; on macOS the installer appends "numpy<2", downgrading a package Slicer bundles for every extension; and every model entry still carries "license": "LICENSE_PENDING". Recommendation: 🔴 Do not merge yet.
Not checked: The PyPI package zebrafish-measure==0.2.0 (installed with --no-deps) is not in this repository; its actual torch.load calls, preprocessing and license could not be inspected, so the weights_only=True guarantee asserted by tests/test_safe_checkpoint_loading.py covers only this repo's source.; The Hugging Face model repositories markdanielarndt/Zebrafish_Segmentation and markdanielarndt/Classification (licenses, model cards, whether the pinned revisions and SHA-256 values match) could not be fetched.; widget.py, zoom_view.py, detail_tab.py and results_tab.py were only searched, not read in full; the originals-ordering question behind the sorted() finding is therefore unconfirmed.; CI results (.github/workflows/ci.yml) and any actual Slicer build/load of the extension were not run or observed.; The catalog entry file itself is not part of the inspected repository; the build_dependencies mismatch was assessed from the entry text supplied with the request plus CMakeLists.txt.
Questions for the author: Why does the catalog entry declare no build_dependencies while CMakeLists.txt sets EXTENSION_DEPENDS "PyTorch"?; Can the macOS numpy<2 constraint be left entirely to the PyTorch extension instead of being applied by this extension's pip call?; What are the licenses of the ten model files, and when will LICENSE_PENDING be replaced with the actual terms?; Does the widget pass originals to InferenceController in the same order as image_paths, given that analyse_images() sorts the paths?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
🟢 Recommend merge. The ZebrafishEmbryoAnalyzer extension is exceptionally well-structured, follows Slicer scripted module conventions and best practices (such as lazy imports, robust MRML integration, proper cleanup of observers, and careful PyTorch integration via PyTorchUtils), includes a comprehensive test suite, and meets all safety, packaging, and licensing requirements.
Not checked: Executing code inside a live 3D Slicer session or running CTest suite (tests/ are present and extensive, but executed via static review of code and cmake configuration).

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
Reviewed the catalog entry, CMakeLists, the main module, MRML/logic/worker code, dependency installer, model manifest and downloader, and README. I found no malicious or concealed behavior: no telemetry, data upload or network calls outside user-confirmed model/package downloads; models are SHA-256 verified against pinned Hugging Face revisions; analysis runs in a QProcess subprocess. Main issues: EXTENSION_DEPENDS names PyTorch but the catalog entry has empty build_dependencies, the model weights carry no confirmed license (LICENSE_PENDING), and the installer downgrades numpy on macOS. I could not inspect the zebrafish-measure library, the remaining widget code, or the model files themselves.
Not checked: zebrafish-measure==0.2.0 PyPI package contents, including whether its loader uses torch.load with weights_only and what it does at import.; Model file contents and whether the pinned Hugging Face revisions match the sha256 values; no network access.; The actual scm_url revision (main) and the full commit contents; I read only the files given.; widget.py in full, detail_tab.py, results_tab.py, zoom_view.py, and the remaining parts of model_downloader.py (the verification and cleanup paths).; The test suite under tests/ and the ZebrafishEmbryoAnalyzerTest self-test were only listed, not run.; The Apache-2.0 LICENSE text beyond its first 30 lines, and any copyright holder line.; No CI results were available for this submission beyond the ci.yml workflow definition.
Questions for the author: Which license applies to each Hugging Face model (markdanielarndt/Zebrafish_Segmentation and markdanielarndt/Classification)? Please record it in model_manifest.py and the README.; Should build_dependencies include "PyTorch" to match EXTENSION_DEPENDS?; Why is numpy<2 needed on macOS when the PyTorch extension already applies its own constraint? Can the downgrade be avoided?; Does zebrafish-measure 0.2.0 load weights with torch.load(weights_only=True) or an equivalent safe loader? The model files are loaded from disk after checksum verification.


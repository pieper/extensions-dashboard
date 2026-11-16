# AI review: ASLtoolkit

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/LOAMRI/Slicer-ASLtoolkit.git at commit `b805616adc86eb902505f27dd58764d83647228c`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T10:19:47Z; cost $0.06

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | concern |
| environment | concern | ok | concern |
| packaging | ok | ok | minor |
| license | ok | ok | ok |
| soundness | concern | ok | minor |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: ASLtoolkit provides two Slicer CLI modules (CBF/ATT ASL and Multi Echo ASL) that reconstruct quantitative cerebral blood flow, arterial transit time and T1 blood-gray-matter maps from Arterial Spin Labeling MRI, aimed at neuroimaging researchers.
- **flash-lite**: The ASLtoolkit extension provides 3D Slicer scripted CLI modules (CBF/ATT ASL and Multi Echo ASL) for processing Arterial Spin Labeling (ASL) MRI images using the 'asltk' Python package.
- **haiku**: Provides Slicer CLI modules (CBF/ATT ASL and Multi Echo ASL) that wrap the external asltk Python package to compute perfusion (CBF, ATT) and T1 blood-GM maps from arterial spin labelling MRI. It is aimed at MRI researchers working with ASL data in 3D Slicer.

## Disagreements (start here)

### D1. T2 Blood and T2 Gray Matter parameters are accepted but never used in the computation
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`Multi_Echo_ASL/Multi_Echo_ASL.py:116`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/Multi_Echo_ASL/Multi_Echo_ASL.py#L116): `args.t2b` and `args.t2gm` are parsed from the CLI (lines 245-246) and echoed in the verbose output (lines 108-109), but neither ASLData nor MultiTE_ASLMapping receives them; the only other occurrences in the file are those four lines. A user who changes 'T2 Blood (ms)' or 'T2 Gray Matter (ms)' in the GUI gets identical results, silently, which for a quantitative mapping tool can lead to misinterpreted output values.
  ```
    data = ASLData(
     pcasl=args.asl, m0=args.m0, ld_values=ld, pld_values=pld, te_values=te,
     average_m0=True
     )
  ```
  Suggestion: Pass the T2 values to the reconstruction (e.g. as arguments to MultiTE_ASLMapping/create_map) or remove the parameters from the XML so users are not misled.

### D2. asltk installed into Slicer's shared Python environment at module run without user confirmation
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:32`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L32): The identical block exists in Multi_Echo_ASL/Multi_Echo_ASL.py:32-34. The first time a user runs either module, the script silently pip-installs `asltk==1.1.3` (plus its transitive dependencies) into the Slicer Python environment shared by all extensions and by users who never open this module. There is no confirmation dialog and no progress/size information; the only disclosure is a sentence in README.md:14 and docs/index.md:69. The exact `==1.1.3` pin can also force a specific version of a dependency that Slicer bundles (numpy/scipy/nibabel class packages) if asltk declares one, which can break other extensions.
  ```
  except ModuleNotFoundError:
      import slicer.util
      slicer.util.pip_install("asltk==1.1.3")
  ```
  Suggestion: Ask the user before installing (e.g. a qt.QMessageBox / ctk confirmation in the module, or ship the dependency via the extension build), avoid exact pins of packages Slicer bundles, and state the download size and target environment in the prompt.
- **haiku** (major, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:32`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L32): When asltk is missing, the module silently installs a pinned package and its transitive dependencies into the shared Slicer environment, affecting other extensions and users who never open the module. Nothing asks for consent, and failures are not handled. The same pattern is in Multi_Echo_ASL/Multi_Echo_ASL.py lines 32-34. The transitive dependency set was not verified, so conflicts or bundled Qt/VTK/torch packages are possible.
  ```
  except ModuleNotFoundError:
      import slicer.util
      slicer.util.pip_install("asltk==1.1.3")
  ```
  Suggestion: Ask the user for confirmation before installing, show the package list, handle pip failures with a clear message, and prefer declaring the dependency in the extension's install step or documentation. Verify asltk's transitive dependencies against Slicer-bundled packages.

### D3. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek ok, flash-lite ok, haiku concern

### D4. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D5. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor


## Findings from some reviewers

### Catalog tracks moving branch 'main' rather than a fixed revision
minor; packaging; raised by haiku
- **haiku** (minor, medium confidence, quote verified, other lines) [`CMakeLists.txt:13`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CMakeLists.txt#L13): The catalog entry sets scm_revision to 'main', so the code built by the index can change without review. Per policy this is not a finding by itself, but the reviewed commit b805616 is not pinned.
  ```
  set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies
  ```
  Suggestion: Pin scm_revision to the reviewed commit or a release tag for reproducible builds.

### Default brain mask is a numpy array while a user mask is an ImageIO object
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:65`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L65): `recon.set_brain_mask(mask_img)` therefore receives two different types depending on whether a mask was supplied, and the default path assumes a 5-D ASL array (indexing [0,0,:,:,:]) which raises IndexError for 4-D input. Same pattern in Multi_Echo_ASL.py:66-68.
  ```
    mask_img = np.ones(asl_img.get_as_numpy()[0, 0, :, :, :].shape)
    if args.mask != '':
        mask_img = ImageIO(args.mask)
  ```
  Suggestion: Build the default mask from the M0 image geometry as an ImageIO-compatible object and derive the shape without hard-coded 5-D indexing.

### Empty license element in module descriptors
minor; license; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.xml:14`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.xml#L14): The repository has a valid MIT LICENSE and MIT headers in the scripts, but the CLI metadata shown in Slicer's module information panel is empty, so users do not see the terms where they look for them. Same in Multi_Echo_ASL/Multi_Echo_ASL.xml:14.
  ```
    <license/>
  ```
  Suggestion: Fill in the license field (e.g. 'MIT') in both XML files.
- **haiku** (minor, low confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.xml:14`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.xml#L14): The module XML lists no license, while the root LICENSE file is MIT. This is a descriptive inconsistency only and does not block distribution.
  ```
  <license/>
  ```
  Suggestion: Fill in the license element with MIT to match the LICENSE file.

### No automated tests and documentation inconsistencies
minor; utility; raised by haiku
- **haiku** (minor, medium confidence, quote verified, other lines) [`Multi_Echo_ASL/Multi_Echo_ASL.xml:100`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/Multi_Echo_ASL/Multi_Echo_ASL.xml#L100): The t2gm parameter description says 'blood' when it refers to gray matter. No unit tests or sample-data test cases are present in the repository, so regressions in the CLI parsing and validation logic are not caught. The README image points to the develop branch while CMake uses main.
  ```
  <description><![CDATA[The T2 value for the blood. By default, the value of 75 ms is assumed.]]></description>
  ```
  Suggestion: Fix the t2gm description, add tests for argument parsing and validation, and align documentation branch references.

### No tests, no clinical-use disclaimer, sample data hosted externally without stated license
minor; utility; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`docs/index.md:52`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/docs/index.md#L52): The repository contains no test or self-test, and the tutorial depends on a Google Drive file whose license/redistribution terms are not stated. Quantitative CBF/ATT maps are clinically suggestive, but neither the README nor the module XML carries a research-use-only disclaimer.
  ```
  1. Download the sample data (hosted at a [public link from Google Drive](https://drive.google.com/file/d/1agtHY9SLvC9975L6H0RL6PfIHATnJKcI/view))
  ```
  Suggestion: Add a short self-test or sample-data download through Slicer's Sample Data mechanism, state the sample-data license, and add a research-use-only notice.

### Output folder is validated but never used; XML text about a home-directory default is misleading
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:233`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L233): `out_folder` is only checked for existence (line 148) and never used to build output paths; outputs go to the paths Slicer passes for the output image nodes. The XML description (CBF_ATT_ASL.xml:11) tells users the home directory is used when --outputFolder is omitted, which does not match the code.
  ```
        out_folder=parsed.get('outputFolder', os.path.expanduser('~')),
  ```
  Suggestion: Either use out_folder to resolve relative output names or remove the parameter and the corresponding description text.
- **haiku** (minor, medium confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:233`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L233): out_folder is only validated. Output files are written to out_cbf and out_att exactly as given (lines 130-133), so a relative output name is resolved against the process working directory. The XML description (CBF_ATT_ASL.xml lines 8-11) says the home directory is assumed when outputFolder is absent, which does not match what the code does. Multi_Echo_ASL.py has the same gap.
  ```
  out_folder=parsed.get('outputFolder', os.path.expanduser('~')),
  ```
  Suggestion: Join output file names with out_folder when they are relative, or correct the documentation.

### Smoothing-parameter validation in the CBF module can never trigger
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:187`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L187): The XML enumeration supplies 'None'/'Gaussian'/'Median' (CBF_ATT_ASL.xml:96-98), so the lowercase comparisons at lines 187 and 192 are always False and invalid sigma/kernel values (e.g. sigma <= 0, even median size) reach asltk unchecked. Multi_Echo_ASL.py:192,197 uses the correct capitalisation, so the two modules behave differently.
  ```
    if args.smoothMethod == 'gaussian' and args.smoothParameter <= 0:
  ```
  Suggestion: Compare against 'Gaussian'/'Median' (or lower-case args.smoothMethod once, as is done at line 81).
- **haiku** (minor, high confidence, quote partly verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:181`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L181): The GUI passes 'Gaussian' (CBF XML line 97), but the check compares against lowercase 'gaussian', so a non-positive sigma is not rejected here. Downstream code may then fail or produce wrong output. Multi_Echo_ASL.py uses the correct capitalized comparison on line 192.
  ```
  valid_smooth_methods = ['None', 'Gaussian', 'Median']
  ...
  if args.smoothMethod == 'gaussian' and args.smoothParameter <= 0:
  ```
  Suggestion: Compare against 'Gaussian' and 'Median' consistently, or normalize case before validation.

### requirements.txt pins a different asltk version than the code installs
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`requirements.txt:1`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/requirements.txt#L1): The documentation build (readthedocs) installs asltk 1.1.0 while both modules install 1.1.3 at runtime, so the documented API and the executed API can diverge; the file is also not used by the CMake build, so it is easy to leave stale.
  ```
  asltk==1.1.0
  ```
  Suggestion: Keep a single version pin shared by requirements.txt and the pip_install call.
- **haiku** (minor, high confidence, quote verified) [`requirements.txt:1`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/requirements.txt#L1): The modules install asltk==1.1.3 at runtime (CBF_ATT_ASL.py line 34, Multi_Echo_ASL.py line 34), but requirements.txt pins asltk==1.1.0. Documentation and the tested version are therefore unclear, which makes reproducibility harder.
  ```
  asltk==1.1.0
  ```
  Suggestion: Align requirements.txt and the runtime pin, and record the tested asltk version in the docs.

### rich.print interprets bracketed text in messages as markup
minor; soundness; raised by deepseek
- **deepseek** (minor, low confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:40`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L40): `print` is replaced by rich's markup-aware version, so messages such as the validation text at line 184 containing `['None', 'Gaussian', 'Median']` or file paths containing '[' are parsed as style tags and can raise a markup/style error instead of printing the diagnostic, hiding the real error from the user.
  ```
  from rich import print
  ```
  Suggestion: Use rich.print with markup=False (or the builtin print) for diagnostics and for echoing user-supplied paths.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Two thin ScriptedCLI wrappers around the third-party `asltk` PyPI package. No telemetry, network transmission, obfuscation or destructive file handling was found; the MIT LICENSE covers the extension itself and the catalog entry/CMake are consistent. Two issues should be fixed: the modules silently `pip install asltk==1.1.3` into Slicer's shared Python environment on first run without any user confirmation, and the Multi Echo module's T2 Blood / T2 Gray Matter GUI parameters are parsed and printed but never passed to the reconstruction, so user input is silently ignored. Remaining items (validation bug in the CBF module, requirements.txt version mismatch, no tests, no clinical disclaimer) are non-blocking.
Not checked: The `asltk` PyPI package (v1.1.3) itself was not inspected: its dependency list (whether it pulls torch, or pins numpy/scipy/nibabel that Slicer bundles), its license, and its own network/file behaviour are unknown.; Whether `rich` is bundled with the targeted Slicer version, or only arrives as an asltk dependency, could not be verified.; The Google Drive sample dataset referenced in docs/index.md:52 was not accessed, so its license and content are unverified.; No build or runtime test was possible; behaviour of asltk's ImageIO/save_image and set_brain_mask with the types passed here is inferred from the code only.; The catalog entry uses scm_revision "main" (a moving branch); the exact commit b805616adc86eb902505f27dd58764d83647228c named in the review request could not be resolved or diffed against the working tree.
Questions for the author: Can the asltk installation be made explicit (user confirmation dialog) and moved out of the shared Slicer environment, or at least documented with download size and target environment?; Should the T2 Blood / T2 Gray Matter parameters be forwarded to MultiTE_ASLMapping, or removed from the Multi Echo ASL interface?; What are the license terms of the sample dataset hosted on Google Drive?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The ASLtoolkit extension is a well-structured 3D Slicer neuroimaging extension providing two scripted CLI modules: CBF/ATT ASL and Multi Echo ASL. It relies on the 'asltk' Python library, installing it via pip at runtime if needed. The source code, CMake configuration, XML CLI definitions, and licensing (MIT) comply with Slicer standards and admission requirements. 🟢 Recommend merge.
Not checked: Detailed execution tests of the external Python package 'asltk' in a running 3D Slicer instance.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The code is a thin wrapper around asltk with no network transmission, credentials, or obfuscation in the files reviewed. The main concern is that both modules pip-install asltk==1.1.3 into Slicer's shared Python environment at first use, without user confirmation and with unvetted transitive dependencies. Secondary issues: the version differs from requirements.txt (1.1.0), a smoothing-validation case mismatch means that check never fires, the outputFolder flag is never applied to outputs, the catalog tracks the moving branch "main", and there are no tests. The repository content is untrusted and contains no embedded instructions. Overall: needs fixes, none blocking on safety.
Not checked: The asltk 1.1.3 PyPI package and its transitive dependencies (e.g., whether it pulls torch, opencv-python, or Qt/VTK-bundling packages) were not inspected.; The upstream source at scm_revision 'main' was not resolved; the reviewed commit b805616 was not verified against the files shown.; The Slicer CMake macros, the docs site, and the sample dataset on Google Drive were not accessible.; No CI or build results were available; the modules were not run.; asltk's license terms were not checked; the extension's own MIT license was verified from the LICENSE file only.


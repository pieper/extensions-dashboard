# AI review: ASLtoolkit

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/LOAMRI/Slicer-ASLtoolkit.git at commit `b805616adc86eb902505f27dd58764d83647228c`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-17T03:18:59Z; cost $0.37

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | ok | ok | unknown |
| environment | concern | minor | blocking |
| packaging | ok | ok | unknown |
| license | ok | ok | unknown |
| soundness | concern | concern | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | minor issues | needs fixes |

## What each reviewer says the extension does

- **claude**: ASLtoolkit adds two scripted CLI modules to 3D Slicer for Arterial Spin Labeling MRI. One computes CBF and ATT maps, and the other computes a multi-echo T1 blood-GM map. Both wrap the third-party `asltk` PyPI package and are meant for neuroimaging researchers.
- **gemini**: ASLtoolkit provides two 3D Slicer scripted CLI modules (`CBF_ATT_ASL` and `Multi_Echo_ASL`) for reconstructing quantitative Cerebral Blood Flow (CBF), Arterial Transit Time (ATT), and T1 blood-GM maps from Arterial Spin Labeling (ASL) MRI data. It is intended for neuroimaging researchers analyzing multi-PLD and multi-TE ASL acquisitions using the `asltk` Python library.
- **gpt**: ASLtoolkit provides Slicer CLI modules for reconstructing cerebral blood flow, arterial transit time, and multi-echo ASL maps. It is intended for researchers processing arterial spin labeling MRI data.

## Disagreements (start here)

### D1. Multi-echo T2 values are accepted and printed but not used
partial; category soundness; raised by claude, gpt; outcome after cross-examination: **real, major (3 of 3)**
- **claude** (minor, medium confidence, quote verified) [`Multi_Echo_ASL/Multi_Echo_ASL.py:127`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/Multi_Echo_ASL/Multi_Echo_ASL.py#L127): `t2b` and `t2gm` are exposed in the GUI with defaults and ranges, but they are only printed in verbose output. They are not passed to `MultiTE_ASLMapping` or `create_map`. Changing them therefore has no effect on the result, which misleads users.
  ```
  recon = MultiTE_ASLMapping(data)
    recon.set_brain_mask(mask_img)
    
    # This is the long-running operation
    maps = recon.create_map(
  ```
  Suggestion: Pass the T2 values to asltk, for example via its setter or constructor options, or remove the parameters from the XML.
- **gpt** (major, high confidence, quote verified) [`Multi_Echo_ASL/Multi_Echo_ASL.py:125`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/Multi_Echo_ASL/Multi_Echo_ASL.py#L125): The XML exposes T2 Blood and T2 Gray Matter controls, and the script parses and logs them, but neither value is passed to ASLData, MultiTE_ASLMapping or create_map. Changing these controls therefore cannot affect the computed map, potentially misleading researchers about the parameters used. This is a non-blocking correctness issue under the index policy.
  ```
      print('<filter-progress>0.5</filter-progress>')
      print('<filter-comment>Computing T blood-GM map...</filter-comment>')
      recon = MultiTE_ASLMapping(data)
      recon.set_brain_mask(mask_img)
      
      # This is the long-running operation
  ```
  Suggestion: Pass both values through the appropriate asltk API, or remove the controls if they are unsupported; add a test showing that non-default values reach reconstruction.
- claude on re-check: **real: yes, minor**: Multi_Echo_ASL.py:108-109 only prints args.t2b/t2gm. Lines 115-134 build ASLData, MultiTE_ASLMapping and create_map without them. The XML (lines 79-93) exposes both, so editing them does nothing. This is an ordinary soundness bug that misleads users, not a safety issue, so I rate it minor.
- gpt on re-check: **real: yes, major**: Multi_Echo_ASL/Multi_Echo_ASL.xml:78-82 and 90-94 expose two controls, including `<label>T2 Blood (ms)</label>` and `<label>T2 Gray Matter (ms)</label>`. Multi_Echo_ASL/Multi_Echo_ASL.py:108-109 prints both, but lines 115-134 pass neither to the reconstruction: `recon = MultiTE_ASLMapping(data)` and `smoothing_params=smoothParameter)`. Consequently changing either control cannot change the computed map; silent disregard of analysis parameters can invalidate research results. This is a non-blocking correctness finding under the index admission policy.
- gemini on re-check: **real: yes, major**: In Multi_Echo_ASL/Multi_Echo_ASL.xml lines 78-101, t2b and t2gm are defined as UI parameters. In Multi_Echo_ASL/Multi_Echo_ASL.py lines 245-246 they are parsed into args.t2b and args.t2gm, and printed at lines 108-109, but never passed to ASLData (lines 116-124), MultiTE_ASLMapping (line 127), or recon.create_map (lines 131-134). Changing these parameters in the UI silently has no effect on the computed map, making it a major soundness bug.

### D2. `t2b` and `t2gm` parameters in `Multi_Echo_ASL` are parsed and logged but never used in computation
single; category soundness; raised by gemini; outcome after cross-examination: **real, major (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`Multi_Echo_ASL/Multi_Echo_ASL.py:107`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/Multi_Echo_ASL/Multi_Echo_ASL.py#L107): In `Multi_Echo_ASL/Multi_Echo_ASL.py`, the `t2b` (T2 Blood) and `t2gm` (T2 Gray Matter) parameters exposed in `Multi_Echo_ASL.xml` are parsed into `args.t2b` and `args.t2gm` (lines 245-246) and printed in verbose output (lines 108-109), but are never passed to `ASLData`, `MultiTE_ASLMapping`, or `recon.create_map`. Any changes the user makes to `T2 Blood (ms)` or `T2 Gray Matter (ms)` in the UI have no effect on the computed map.
  ```
        print('---- Advanced Options ----')
        print('T2 Blood: ' + str(args.t2b))
        print('T2 GM: ' + str(args.t2gm))
        print('Average M0: ' + str(args.average_m0))
  ```
  Suggestion: Pass `args.t2b` and `args.t2gm` to `MultiTE_ASLMapping` or `recon.create_map` (e.g., via its `t2b` / `t2gm` parameters or setter methods in `asltk`).
- claude on re-check: **real: yes, minor**: This is the same behaviour as D1. Multi_Echo_ASL.py:108-109 print t2b/t2gm, and 245-246 parse them. Lines 115-134 never pass them on. It is real, but it is a non-blocking correctness issue and the severity is not major.
- gpt on re-check: **real: yes, major**: Duplicate of D1. Multi_Echo_ASL/Multi_Echo_ASL.py:245-246 parses `t2b=float(parsed.get('t2b', '165.0')),` and `t2gm=float(parsed.get('t2gm', '75.0')),`; lines 107-109 only print them, and lines 115-134 show neither passed to ASLData or reconstruction. The exposed controls therefore silently have no effect on computed results; this is a serious research-correctness issue, not a blocking safety finding.
- gemini on re-check: **real: yes, major**: Same underlying defect as D1: in Multi_Echo_ASL/Multi_Echo_ASL.py, args.t2b and args.t2gm are parsed (lines 245-246) and logged (lines 108-109), but never passed to ASLData (lines 116-124), MultiTE_ASLMapping (line 127), or recon.create_map (lines 131-134). Exposing scientific parameters in the UI that silently do nothing is a major soundness defect.

### D3. Rating of environment
rating dispute; category environment; raised by claude, gemini, gpt; outcome after cross-examination: **settled: concern (concern, blocking, con**
Ratings: claude concern, gemini minor, gpt blocking
- claude on re-check: **rating concern**: Multi_Echo_ASL.py:34 and CBF_ATT_ASL.py:34 call slicer.util.pip_install("asltk==1.1.3") from a ModuleNotFoundError fallback. This installs into Slicer's shared Python without asking the user. It runs when the CLI module is first executed, not at Slicer startup or import, so it only affects users who run the module. asltk's transitive dependencies could pin or replace Slicer-bundled packages, and I could not check them. The exact pin is on asltk itself, not on a bundled package. CMakeLists.txt sets EXTENSION_DEPENDS to NA, and I found no torch install. This calls for a consent prompt and a check of asltk's dependencies, but I found no concrete harm, so I rate it concern rather than blocking.
- gpt on re-check: **rating blocking**: Both CLI scripts install into Slicer's Python environment without confirmation on an import failure. Multi_Echo_ASL/Multi_Echo_ASL.py:28-34 has `except ModuleNotFoundError:` followed by `slicer.util.pip_install("asltk==1.1.3")`; CBF_ATT_ASL/CBF_ATT_ASL.py:28-34 has the same code. This top-level installation runs whenever the script is imported or invoked and the import fails, potentially changing the shared environment for other extensions. The policy expressly requests changes for installation at module import. README.md:14 documents runtime installation but is not user confirmation. The external package's dependency requirements and whether Slicer invokes the CLI during discovery were not available to verify.
- gemini on re-check: **rating concern**: In both CBF_ATT_ASL/CBF_ATT_ASL.py (lines 28-37) and Multi_Echo_ASL/Multi_Echo_ASL.py (lines 28-37), top-level module code attempts to call slicer.util.pip_install("asltk==1.1.3") on ModuleNotFoundError without user confirmation. Because these are SlicerMacroBuildScriptedCLI modules executed via python-real in a separate process (often during CLI discovery with --xml or on CLI invocation where the slicer module is not even importable), top-level pip installation and installing a package that pulls in its own dependencies (numpy, scipy, SimpleITK, rich, etc.) into Slicer's shared Python environment without prompt warrants a 'concern' rating.


## Findings all reviewers agree on

### Unconfirmed package installation runs at CLI script import
blocking; environment; raised by claude, gemini, gpt
- **claude** (major, medium confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:32`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L32): If `asltk` is missing, the CLI script calls `slicer.util.pip_install("asltk==1.1.3")` straight away. This installs asltk and all its transitive dependencies into Slicer's shared Python with no prompt, even though the download may be large. Those dependencies may pin or replace packages Slicer bundles (numpy, scipy, SimpleITK, pydicom), and I did not verify them. The install happens inside a `python-real` subprocess, so the user sees nothing in the UI. The README mentions it only in a note. The `slicer` package may also not be fully usable from `python-real`, so the fallback may simply fail.
  ```
  except ModuleNotFoundError:
      import slicer.util
      slicer.util.pip_install("asltk==1.1.3")
  ```
  Suggestion: Add a scripted module with a GUI that tells the user which packages will be installed and asks for confirmation before calling `pip_install`. Check that asltk's dependency requirements do not pin or downgrade Slicer-bundled packages. Apply the same change to the Multi_Echo_ASL script.
- **gemini** (major, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:28`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L28): Both `CBF_ATT_ASL.py` and `Multi_Echo_ASL.py` are configured as `SlicerMacroBuildScriptedCLI` modules running under `#!/usr/bin/env python-real`. When Slicer executes a Scripted CLI module, it launches a standalone `python-real` subprocess rather than executing inside the embedded Slicer Python interpreter. In a standalone `python-real` process, `import slicer.util` is not available (`ModuleNotFoundError: No module named 'slicer'`), so the automatic installation fallback for `asltk==1.1.3` will fail with an unhandled exception whenever `asltk` is not already installed. Furthermore, installing packages silently during CLI execution without prior user confirmation violates Slicer's convention for third-party Python package installation.
  ```
  try:
      from asltk.asldata import ASLData
      from asltk.reconstruction import CBFMapping
      from asltk.utils.io import ImageIO
  except ModuleNotFoundError:
      import slicer.util
  ```
  Suggestion: Either invoke `pip` via `subprocess.check_call([sys.executable, "-m", "pip", "install", "asltk==1.1.3"])` in the `python-real` CLI script, or provide a ScriptedLoadableModule wrapper that asks the user for confirmation before calling `slicer.util.pip_install("asltk==1.1.3")`. Also synchronize the version in `requirements.txt` (`asltk==1.1.0`) with the version installed in the scripts (`asltk==1.1.3`).
- **gpt** (blocking, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:28`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L28): When the script is imported or executed and an asltk import fails, it immediately downloads and installs asltk and its dependencies into the shared Slicer Python environment, without asking the user. This can change packages used by other extensions; a missing transitive import also triggers the same installation. Multi_Echo_ASL/Multi_Echo_ASL.py:28-37 contains the same pattern. The precise discovery/startup behavior and transitive packages could not be verified.
  ```
  try:
      from asltk.asldata import ASLData
      from asltk.reconstruction import CBFMapping
      from asltk.utils.io import ImageIO
  except ModuleNotFoundError:
      import slicer.util
  ```
  Suggestion: Move dependency installation out of module import into an explicit, informed user-confirmed setup step; inspect its dependencies and avoid modifying Slicer-bundled packages incompatibly.

### Smoothing-parameter validation in CBF module compares wrong case and never triggers
minor; soundness; raised by claude, gemini, gpt
- **claude** (minor, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:187`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L187): Valid methods are 'Gaussian' and 'Median', but the checks compare against lowercase 'gaussian' and 'median'. Invalid sigma or kernel sizes, such as an even median size, therefore pass validation and fail later inside asltk or give wrong results. The Multi_Echo module uses the correct case.
  ```
  if args.smoothMethod == 'gaussian' and args.smoothParameter <= 0:
  ```
  Suggestion: Compare against 'Gaussian' and 'Median', matching the Multi_Echo module.
- **gemini** (minor, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:180`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L180): In `CBF_ATT_ASL/CBF_ATT_ASL.py`, `checkUpParameters` validates `args.smoothMethod` against `['None', 'Gaussian', 'Median']` (capitalized), but then checks `if args.smoothMethod == 'gaussian'` (line 187) and `if args.smoothMethod == 'median'` (line 192) in lowercase before `args.smoothMethod` has been lowercased. As a result, invalid smoothing parameters (such as an even or non-positive kernel size for Median filtering) bypass validation in `CBF_ATT_ASL.py`.
  ```
    # Checks the smoothing Method and Parameters
    valid_smooth_methods = ['None', 'Gaussian', 'Median']
    if args.smoothMethod not in valid_smooth_methods:
      print(
          f'Smoothing method "{args.smoothMethod}" is not valid. Please select one of the following methods: {valid_smooth_methods}.'
      )
  ```
  Suggestion: Check against `'Gaussian'` and `'Median'` (as done in `Multi_Echo_ASL.py` lines 192 and 197) or compare `args.smoothMethod.lower()`.
- **gpt** (minor, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:180`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L180): The accepted and GUI-provided names are capitalized, while the Gaussian and Median validation branches test lowercase strings. Consequently invalid sigma or kernel sizes pass this validation and reach reconstruction, potentially failing or producing unintended smoothing.
  ```
    # Checks the smoothing Method and Parameters
    valid_smooth_methods = ['None', 'Gaussian', 'Median']
    if args.smoothMethod not in valid_smooth_methods:
      print(
          f'Smoothing method "{args.smoothMethod}" is not valid. Please select one of the following methods: {valid_smooth_methods}.'
      )
  ```
  Suggestion: Normalize the method once before both validation and dispatch, and test invalid Gaussian and Median parameters.


## Findings from some reviewers

### Documented outputFolder option does not control output location
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:127`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L127): The XML's command-line example specifies --outputFolder and relative output names, but the script only checks that folder exists and saves directly to the output arguments. Relative names thus resolve against the process working directory, not the selected output folder. The multi-echo script has the same issue.
  ```
    print('<filter-progress>0.9</filter-progress>')
    print('<filter-comment>Saving output files...</filter-comment>')
    if args.norm_cbf:
      maps['cbf_norm'].save_image(args.out_cbf)
    else:
      maps['cbf'].save_image(args.out_cbf)
  ```
  Suggestion: Join relative output paths to the chosen output folder, or remove the option and correct the documentation.

### Mixed vector formats silently truncate timing values
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified, other lines) [`CBF_ATT_ASL/CBF_ATT_ASL.py:28`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L28): If one timing vector is space-separated and another is comma-separated, conversion of the first triggers the fallback, which reads only element zero of both vectors. For example, a comma-separated LD list loses all but its first value. The multi-echo module uses the same fallback for three vectors.
  ```
    try:
        pld = [float(s) for s in args.pld]
        ld = [float(s) for s in args.ld]
    except:
        pld = [float(s) for s in str(args.pld[0]).split()]
        ld = [float(s) for s in str(args.ld[0]).split()]
  ```
  Suggestion: Parse each vector independently, supporting the documented separators without discarding elements, and validate its length against the acquisition.

### Overriding `print` with `rich.print` can interfere with Slicer CLI XML progress tags
minor; soundness; raised by gemini
- **gemini** (minor, medium confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:39`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L39): Both CLI scripts override Python's built-in `print` with `rich.print`. Slicer's CLI process runner parses standard output for XML progress tags such as `<filter-start>`, `<filter-progress>0.1</filter-progress>`, and `<filter-end>`. Because `rich.print` interprets angle-bracket tags as Rich console markup and applies terminal formatting/word wrapping, it can strip or alter the XML progress tags expected by Slicer.
  ```
  import numpy as np
  from rich import print
  ```
  Suggestion: Use Python's built-in `print` (and `sys.stdout.flush()`) for Slicer `<filter-...>` XML progress reporting.

### Same silent pip install in the Multi_Echo_ASL module
minor; environment; raised by claude
- **claude** (minor, medium confidence, quote verified) [`Multi_Echo_ASL/Multi_Echo_ASL.py:33`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/Multi_Echo_ASL/Multi_Echo_ASL.py#L33): The identical pattern is repeated, so either module can trigger a silent installation into the shared environment.
  ```
      import slicer.util
      slicer.util.pip_install("asltk==1.1.3")
  ```
  Suggestion: Centralize and gate the installation behind a user confirmation.

### Unchecking `normalizedCBF` in the GUI has no effect because omitted CLI boolean flags default to `'true'`
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.py:239`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.py#L239): In Slicer's CLI execution model, `<boolean>` parameters are passed as a flag (`--normalizedCBF`) when checked (`true`) and omitted entirely from the command-line arguments when unchecked (`false`). Because `CBF_ATT_ASL.py` defaults `parsed.get('normalizedCBF', 'true')` to `'true'` when the flag is absent, unchecking "Set CBF to mL/100 g/min scale" in the Slicer GUI still results in `args.norm_cbf == True`. Consequently, users cannot disable CBF normalization from the GUI.
  ```
          out_cbf=parsed.get('outputCBF', ''),
          norm_cbf=parse_bool(parsed.get('normalizedCBF', 'true')),
          out_att=parsed.get('outputATT', ''),
  ```
  Suggestion: Default missing boolean flags to `'false'` (`parsed.get('normalizedCBF', 'false')`) when invoked by Slicer's CLI launcher, or use standard Slicer CLI argument parsing.

### Input images are declared as disk `<file>` parameters rather than scene `<image>` nodes
info; utility; raised by gemini
- **gemini** (info, high confidence, quote verified) [`CBF_ATT_ASL/CBF_ATT_ASL.xml:48`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/CBF_ATT_ASL/CBF_ATT_ASL.xml#L48): Both `CBF_ATT_ASL.xml` and `Multi_Echo_ASL.xml` declare `inputASL`, `inputM0`, and `labelMask` as `<file>` parameters restricted to `.nii,.nii.gz` on disk rather than `<image>` parameters, whereas the outputs (`outputCBF`, `outputATT`, `outputVolume`) are declared as `<image channel="output">`. This prevents users from selecting input volumes that are already loaded in the Slicer scene.
  ```
      <file fileExtensions=".nii,.nii.gz">
      <name>inputASL</name>
        <label>Input ASL file</label>
        <longflag>inputASL</longflag>
        <description><![CDATA[Input ASL file path in .nii or nii.gz format]]></description>
      </file>
  ```
  Suggestion: Consider using `<image>` parameters for input volumes if `asltk` supports the file formats Slicer uses for CLI volume exchange, or document that inputs must be selected as external NIfTI files from disk while outputs are loaded into the scene.

### No tests, no research-use disclaimer; docs and requirements inconsistent; sample data on Google Drive
info; utility; raised by claude
- **claude** (info, medium confidence, quote verified) [`requirements.txt:1`](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/b805616adc86eb902505f27dd58764d83647228c/requirements.txt#L1): The repository has no automated tests. `requirements.txt` pins asltk==1.1.0 while the scripts install 1.1.3. The tutorial sample data is on a personal Google Drive link. There is no statement that the maps are for research use only. The catalog entry tracks the moving branch `main`.
  ```
  asltk==1.1.0
  ```
  Suggestion: Align the versions, add a research-use note, host the sample data in a stable location, and consider pinning `scm_revision` to a commit or tag.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I read the full source: both CLI scripts, their XML files, the CMake files, the license and the docs. I found no malicious behavior, no network use beyond pip, and no data exfiltration. The license is MIT and the catalog entry is consistent with the CMake settings. The main concern is that `asltk==1.1.3` is pip-installed silently into Slicer's shared Python the first time a module runs, from inside the CLI subprocess. This is undocumented in the UI and has no confirmation. It also depends on `slicer.util` being importable in `python-real`, and I could not verify that `asltk`'s dependency pins are compatible with Slicer's bundled packages. There are also ordinary bugs: unused T2 parameters, and validation that never triggers in the CBF module. Overall: needs fixes (non-blocking under the admission policy).
Not checked: Contents and dependency pins of the asltk 1.1.3 PyPI package (no network access); Runtime behavior in Slicer, including whether pip_install works from python-real; Whether the `main` branch tip still matches the reviewed code; Google Drive sample data; Correctness of the ASL quantification itself
Questions for the author: What are the declared dependencies of asltk 1.1.3, and do they pin or downgrade numpy, scipy, SimpleITK or pydicom in Slicer's Python?; Does `import slicer.util` and `pip_install` actually work inside a `python-real` CLI subprocess? Have you tested a clean install?; Why are the T2 blood and T2 GM parameters not passed to the reconstruction?

### Gemini 4 Argon (`google/gemini-4-argon`): minor issues
ASLtoolkit is an MIT-licensed neuroimaging extension providing two scripted CLI modules (`CBF_ATT_ASL` and `Multi_Echo_ASL`) wrapping the `asltk` library for Arterial Spin Labeling MRI reconstruction. The code is clean and safe, with a valid catalog entry and CMake configuration. There are several non-blocking functional issues in the scripted CLI implementation: `slicer.util.pip_install` is called inside a standalone `python-real` CLI script where `slicer` is unavailable, `t2b`/`t2gm` parameters in `Multi_Echo_ASL` are parsed but never used, `normalizedCBF` in `CBF_ATT_ASL` cannot be unchecked from the GUI due to CLI flag parsing defaults, and `rich.print` is used where Slicer expects raw XML progress tags.

🟢 Recommend merge
Not checked: Transitive dependency tree and version constraints of `asltk==1.1.3` on PyPI (could not verify without network access whether `asltk==1.1.3` pins or upgrades packages bundled with Slicer such as `SimpleITK`, `numpy`, or `scipy`, or pulls in `torch` or GUI packages).; Contents of the external Google Drive sample dataset linked in `docs/index.md`.
Questions for the author: Does `asltk==1.1.3` impose strict version pins on packages already bundled in 3D Slicer (such as `numpy`, `scipy`, or `SimpleITK`)?; How is `slicer.util.pip_install("asltk==1.1.3")` expected to succeed when `CBF_ATT_ASL.py` and `Multi_Echo_ASL.py` are executed as `SlicerMacroBuildScriptedCLI` scripts inside a standalone `python-real` process where the `slicer` module is not initialized?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The supplied source snapshot installs a Python package into Slicer's shared environment at script import without confirmation. The external package and its dependencies could not be inspected, and the catalog's moving branch could not be resolved independently. Several reconstruction options also do not behave as documented; those correctness findings are non-blocking. 🔴 Do not merge yet: fix the unconfirmed import-time installation; review incomplete pending inspection of the downloaded package and verification of the catalog revision.
Not checked: Independent resolution of catalog scm_revision main and confirmation that it points to the supplied b805616adc86eb902505f27dd58764d83647228c snapshot; the commit is provided by the requester, not independently verified.; Source, distribution license, package metadata and transitive dependencies of downloaded asltk 1.1.3, including any image transmission or environment changes.; Actual Slicer build, module discovery and execution, CLI argument serialization, numerical results, and platform compatibility; only listing, reading and searching were available.; Sample-data link, dataset terms and contents, maintenance history, prior catalog revision, submission checklist and CI results.


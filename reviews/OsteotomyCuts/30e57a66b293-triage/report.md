# AI review: OsteotomyCuts

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/cmfsx/SlicerOsteotomyCuts.git at commit `30e57a66b293667b6949d72207c1a0c38320cea2`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-15T02:33:59Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | ok | ok | ok |
| packaging | ok | ok | minor |
| license | ok | ok | ok |
| soundness | ok | ok | minor |
| utility | ok | ok | minor |
| **overall** | minor issues | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: OsteotomyCuts is a 3D Slicer scripted module for virtual osteotomies in orthognathic and craniofacial surgical planning: the user draws osteotomy lines on a bone model, sets saw direction, blade thickness and cut depth, and the bone is split into closed, watertight segments with checks of model quality and of clearance to nerve canals and tooth roots. It targets oral and maxillofacial surgeons and planning clinicians; it is explicitly research/planning software, not a medical device.
- **flash-lite**: OsteotomyCuts is a 3D Slicer extension providing virtual osteotomy tools for orthognathic and craniofacial surgical planning (e.g., multi-segment cuts, saw blade thickness, cut depth, model quality checks, and proximity checks to nerve canals and tooth roots).
- **haiku**: OsteotomyCuts is a scripted 3D Slicer module (Planning category) for virtual osteotomy planning in orthognathic and craniofacial surgery: the user draws cut lines on a bone model and the bone is split into closed segments, with distance checks to nerve canals and tooth roots. It is aimed at surgeons and researchers using Slicer on de-identified or research models.

## Findings from some reviewers

### CLA is marked as an unreviewed draft
minor; license; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`CLA.md:1`](https://github.com/cmfsx/SlicerOsteotomyCuts/blob/30e57a66b293667b6949d72207c1a0c38320cea2/CLA.md#L1): CONTRIBUTING.md and the PR template require every contributor to sign this CLA, and README relies on it to keep dual licensing possible, but the document itself is marked as an unreviewed draft. This does not restrict distribution of the extension (the code is GPL-3.0-or-later with a full LICENSE), so it is not an admission blocker, but contributors are being asked to sign terms the author has not finalised.
  ```
  > **Draft — to be reviewed by a legal professional.**
  ```
  Suggestion: Have the CLA reviewed and remove the draft banner before enforcing it on pull requests.
- **haiku** (minor, high confidence, quote verified) [`CLA.md:1`](https://github.com/cmfsx/SlicerOsteotomyCuts/blob/30e57a66b293667b6949d72207c1a0c38320cea2/CLA.md#L1): CLA.md, which contributors are asked to sign, says it has not been reviewed by a lawyer. Contributors may be unsure what they are granting, and the project's dual-licence model depends on this text. This does not affect distribution under GPL-3.0, which is covered by the full LICENSE file.
  ```
  > **Draft — to be reviewed by a legal professional.**
  ```
  Suggestion: Have the CLA reviewed before the dual-licence offer is relied on, or remove the draft banner once it is approved.

### Catalog entry tracks branch 'main' while the author's notes describe an unreleased pre-release on another branch
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`CLAUDE.md:24`](https://github.com/cmfsx/SlicerOsteotomyCuts/blob/30e57a66b293667b6949d72207c1a0c38320cea2/CLAUDE.md#L24): The entry sets scm_revision to "main", so whatever is on main at install time is what users get, and the reviewed commit 30e57a6 cannot be pinned from the entry. CLAUDE.md says the v1.0.0 release is on branch `release` and that nothing is to be published or put into a pull request until the author types GO RELEASE. Whether main currently holds the approved release is unclear, so the code users receive may not match what was reviewed or released.
  ```
  - v1.0.0 pre-release (branch `release`, from 3a7458d = Phase 2, no Phase 3):
    Parts 0-10 of the user's to-do list, done in order, stopping after each
    for testing in Slicer. Phase 3 work continues on `master` and is merged
    after the release (Part 10). Nothing is pushed publicly, tagged or put
  ```
  Suggestion: Ask the author to confirm which commit is the intended release, and pin scm_revision to that commit or a tag in the catalog entry.

### Extra test scripts are not registered with CMake, so ctest only runs the in-file test class
minor; packaging; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`OsteotomyCuts/Testing/Python/CMakeLists.txt:6`](https://github.com/cmfsx/SlicerOsteotomyCuts/blob/30e57a66b293667b6949d72207c1a0c38320cea2/OsteotomyCuts/Testing/Python/CMakeLists.txt#L6): OsteotomyCuts/CMakeLists.txt registers the unittest subclass inside OsteotomyCuts.py (line 33) and adds the Testing subdirectory, but Testing/Python/CMakeLists.txt only contains a commented-out registration referring to a non-existent ${MODULE_NAME}ModuleTest.py. Consequently run_headless_tests.py, run_benchmark.py and run_real_models.py are never installed or executed by the extension build/ctest, so the 87 tests and the benchmark quoted in RELEASE_NOTES.md are not exercised by the index's automated build.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Register the headless runner (or the test class it drives) with slicer_add_python_unittest so the extension build actually runs the tests, and drop the stale commented line.
- **haiku** (info, high confidence, quote verified) [`OsteotomyCuts/Testing/Python/CMakeLists.txt:6`](https://github.com/cmfsx/SlicerOsteotomyCuts/blob/30e57a66b293667b6949d72207c1a0c38320cea2/OsteotomyCuts/Testing/Python/CMakeLists.txt#L6): OsteotomyCuts/Testing/Python/CMakeLists.txt only has the test line commented out, so no module-specific ctest is registered. The main module CMakeLists still runs slicer_add_python_unittest on OsteotomyCuts.py when BUILD_TESTING is set, so the impact is limited.
  ```
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Remove the dead line or register the headless test runner as a ctest.

### Developer/AI-assistant notes file with local paths is committed to the public repository
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`CLAUDE.md:83`](https://github.com/cmfsx/SlicerOsteotomyCuts/blob/30e57a66b293667b6949d72207c1a0c38320cea2/CLAUDE.md#L83): CLAUDE.md is a working-notes file for an AI coding assistant: it records the author's local Windows paths, the release workflow ("Nothing is pushed publicly, tagged or put into a pull request until the user types exactly: GO RELEASE.") and instructions such as "SAFETY_NOTE and the Help / Acknowledgement texts are the user's exact wording: do not reword them." These are instructions to the author's own tooling, not to reviewers, and I found no attempt to influence review or to conceal behaviour; the file is untrusted content that I did not act on. It is only an information-disclosure/hygiene issue.
  ```
  - Windows 11. Project: C:\Dev\OsteotomyCuts
  - 3D Slicer 5.13.0 (preview build, 2026-06-30, r34833), installed for all users
  ```
  Suggestion: Move CLAUDE.md out of the published repository (or into a git-ignored local file) so local paths and internal workflow notes are not shipped.

### Only external process invocation is a local git query, verified benign
info; safety; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`OsteotomyCuts/OsteotomyCuts.py:4332`](https://github.com/cmfsx/SlicerOsteotomyCuts/blob/30e57a66b293667b6949d72207c1a0c38320cea2/OsteotomyCuts/OsteotomyCuts.py#L4332): The provenance feature records the module's git commit. The call uses an argument list (no shell), a fixed command, a 5 s timeout and a working directory inside the extension, and failures are swallowed into "unknown". No user input reaches it, so there is no command-injection path; recorded here because it is the only process spawn in the module.
  ```
  result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=os.path.dirname(__file__),
                          capture_output=True, text=True, timeout=5,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
  ```
  Suggestion: No change needed.
- **haiku** (info, high confidence, quote verified) [`OsteotomyCuts/OsteotomyCuts.py:4332`](https://github.com/cmfsx/SlicerOsteotomyCuts/blob/30e57a66b293667b6949d72207c1a0c38320cea2/OsteotomyCuts/OsteotomyCuts.py#L4332): moduleGitHash runs `git rev-parse` in the module's folder with a 5 s timeout to record provenance. It is read-only and local, and it falls back to 'unknown' on error. It is noted for transparency only.
  ```
  result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=os.path.dirname(__file__),
                                          capture_output=True, text=True, timeout=5,
  ```
  Suggestion: No change required. Optionally drop the subprocess call from the shipped module.

### Whole module implemented in one 7,396-line Python file
info; soundness; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`OsteotomyCuts/CMakeLists.txt:9`](https://github.com/cmfsx/SlicerOsteotomyCuts/blob/30e57a66b293667b6949d72207c1a0c38320cea2/OsteotomyCuts/CMakeLists.txt#L9): All geometry, GUI, provenance and test code lives in OsteotomyCuts.py (408 KB, 7,396 lines). This is not a defect and does not affect users, but it makes review and maintenance harder and means the test class is shipped inside the module script.
  ```
  set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    )
  ```
  Suggestion: Consider splitting the pure-geometry logic into a separate module file installed by CMake, keeping the ScriptedLoadableModule classes in OsteotomyCuts.py.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): minor issues
No blocking issues found. The module is a single scripted module whose only imports are Slicer-bundled (numpy, vtk, qt, slicer); scipy is imported lazily behind a guard and no pip installs, network access, telemetry or downloads exist. The one subprocess call runs local `git rev-parse` without a shell. CMake installs the module script, UI files, icon and requirements.txt; EXTENSION_DEPENDS "NA" matches the empty build_dependencies. GPL-3.0-or-later with LICENSE, SPDX headers and a clear not-a-medical-device disclaimer. Remaining items are non-blocking: a draft CLA, a committed AI-assistant notes file, and commented-out registration of the extra test scripts.
Not checked: The bulk of OsteotomyCuts.py (lines ~400-4300 and ~4400-5160, ~5160-7396) was not read line by line; the cutting, capping, solid-model, clearance and mirroring algorithms were only assessed through the module docstrings, CLAUDE.md's description and the test scripts.; os.remove(scenePath) at lines 5923, 6025, 6969, 7184 and 7211 was not inspected in context; I could not confirm that these paths are temporary scene files created by the tests rather than user files.; The .ui files (OsteotomyCuts.ui, Disclaimer.ui) and the binary assets (icons, screenshots, SVG logos) were not inspected for embedded content.; The extension was not built or run; no CMake configure, ctest, headless test run or Slicer load was performed, so the claimed 87 passing tests and the watertightness benchmark are unverified.; The catalog entry's scm_revision "main" was not resolved to a commit and the upstream repository was not fetched; the review is based on the file snapshot provided.
Questions for the author: Are the paths passed to os.remove() at lines 5923, 6025, 6969, 7184 and 7211 always temporary scene files created by the module's own tests, and never a user-chosen path?; Should the headless test runner be registered with slicer_add_python_unittest so the extension build runs the tests, rather than leaving Testing/Python/CMakeLists.txt with only a commented-out line?; Would you consider removing CLAUDE.md (local paths and internal release workflow) from the published repository?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
OsteotomyCuts is a well-designed, meticulously documented, and thoroughly tested 3D Slicer extension for virtual osteotomy planning in orthognathic and craniofacial surgery. It follows Slicer architectural guidelines (ScriptedLoadableModule, parameter node wrappers, headless-capable logic, clean observer removal), includes robust error handling and guarded optional imports (SciPy), features comprehensive testing and benchmarking scripts, and adheres strictly to the GPL-3.0-or-later license with prominent safety disclaimers. 🟢 Recommend merge.
Not checked: We did not execute the code locally inside 3D Slicer, as the environment does not provide Slicer or Python runtime for running external modules.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
I found no malicious or concealed behaviour and no data egress. The only network-related code is a local read-only `git rev-parse` call, and there are no URL fetches, pip installs, or pickle/eval use in the module. Test-code `os.remove` calls only delete the test's own temp scene. Packaging is simple (no build dependencies, EXTENSION_DEPENDS "NA" consistent with the entry). The GPL-3.0 LICENSE is present in full. Main concerns are process: the catalog tracks `main` while the author's notes say the v1.0.0 release is not yet authorised, and the CLA is marked as an unreviewed draft. I could not inspect the 408 KB module fully, the .ui files, or the remote commit.
Not checked: Most of the 7,396-line OsteotomyCuts.py was not read (only targeted searches and about 100 lines); the cutting algorithm, GUI code and tests were not reviewed in full.; The Resources/UI/*.ui files and Resources/Icons/OsteotomyCuts.png were not inspected, so their existence and content were not verified.; The remote repository at scm_url and revision 30e57a6 were not accessed; the main branch tip was not compared with the reviewed commit.; Test scripts referenced in the docs (run_headless_tests.py etc.) were not opened; no tests were run and no build was attempted.; Clinical validity of distance checks and the cut algorithm were not assessed; no model or patient data was read.


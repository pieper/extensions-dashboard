# AI review: AstmPhantomTest

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/Atracsys/SlicerAstmPhantomTest.git at commit `de04b3a2137407f38eff5f468a1331975a364b5e`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-17T03:30:56Z; cost $0.07

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | concern |
| environment | minor | ok | minor |
| packaging | minor | ok | ok |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | ok |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A guided assistant for performing the ASTM F2554 tracking-accuracy tests: it connects to an optical tracker over OpenIGTLink, calibrates a phantom, guides the user through single-point, rotation and multi-point tests, and writes JSON/HTML accuracy reports. Intended for metrology/QA engineers qualifying Atracsys and NDI trackers, not for clinical use.
- **flash-lite**: AstmPhantomTest is a 3D Slicer scripted loadable module extension that assists in performing tracking accuracy tests of a tracking system as described in the ASTM standard F2554 (providing visual guidance, navigation, and statistical analysis).
- **haiku**: An ASTM F2554 tracking-accuracy assistant for 3D Slicer. It guides a user through phantom calibration, working-volume placement, single-point, rotation and multi-point measurements from an OpenIGTLink tracker, then writes JSON and HTML reports to a user-selected folder.

## Disagreements (start here)

### D1. Hidden developer unlock that bypasses calibration and injects simulated target hits
partial; category safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:640`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L640): Typing the operator ID whose salted SHA-256 matches the hardcoded hash enables the 'dev shortcuts' panel, which includes hackCalib (injects calibration points from defaultCalibs.txt, AstmPhantomTest.py:823-842) and hackX/skipTest (AstmPhantomTest.py:1410-1412). The generated JSON/HTML report (EndSession, lines 1693-1946) records the operator as '******' but never records that shortcuts were used, so an accuracy report can be produced without real measurements and looks legitimate. This is not malicious, but it is concealed privileged behavior in a metrology tool whose output is used to qualify trackers.
  ```
        pw = '8ee930e3474f1b9a4a0d7524f3527b93f1ff2e4fa89a385f1ede01a15d7cc9e4'
        salt = '68835c9b8f744414b1e1d2f262e7a911'
        if pw == hashlib.sha256(salt.encode() + opId.encode()).hexdigest():
          self.logic.operatorId = "******"
  ```
  Suggestion: Remove the hash gate or make the shortcut mode explicit and recorded in the report (e.g. a 'shortcuts used' field), and log it prominently.
- **haiku** (major, medium confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:640`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L640): Typing a passphrase into the operator field unlocks 'dev shortcuts' (hackCalib, hackCL/BL/TL/LL/RL, skipTest). The SkipCalib operator ID also sets skipCalibMode. These paths fire calibration and target-hit events with values from a local file or from the phantom's nominal positions, not from the tracker. A session run with them can produce a report that looks like a valid ASTM F2554 test. The check is a client-side hash, so it is an access control in name only. This is not a data exfiltration risk, but it is a concealed behaviour in a shipped measurement tool and the reports carry no marker that shortcuts were used.
  ```
  pw = '8ee930e3474f1b9a4a0d7524f3527b93f1ff2e4fa89a385f1ede01a15d7cc9e4'
  salt = '68835c9b8f744414b1e1d2f262e7a911'
  if pw == hashlib.sha256(salt.encode() + opId.encode()).hexdigest():
  ```
  Suggestion: Remove the dev shortcuts from production builds or gate them behind a developer-only build flag. If kept, record in the report JSON and HTML that shortcuts were used, and document the unlock in the README.

### D2. NameError in no-sample error path of point acquisition
partial; category soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTestClasses/Pointer.py:280`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTestClasses/Pointer.py#L280): When a 1-frame acquisition finishes with an empty accumulator, the intended warning dialog instead raises AttributeError inside the Qt timer slot, so the user is never told why the acquisition failed and the exception surfaces in the Slicer Python console.
  ```
            msgBox = qt.QMessageBox()
            msgBox.setText("No sample taken during timer duration for point acquisition. Restart module and try again with increased duration.")
            msgBoxsgBox.setIcon(qt.QMessageBox().Warning)
            msgBoxsgBox.setStandardButtons(qt.QMessageBox().Ok)
  ```
  Suggestion: Rename msgBoxsgBox to msgBox on both lines.
- **haiku** (major, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTestClasses/Pointer.py:281`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTestClasses/Pointer.py#L281): When the acquisition timer ends with zero samples, the code references `msgBoxsgBox`, which is never defined (the variable is `msgBox`). The result is an uncaught NameError inside a Qt timer callback, so the user never sees the intended warning and the acquisition state is not reset.
  ```
  msgBox.setText("No sample taken during timer duration for point acquisition. Restart module and try again with increased duration.")
  msgBoxsgBox.setIcon(qt.QMessageBox().Warning)
  ```
  Suggestion: Replace `msgBoxsgBox` with `msgBox` on both lines, and add a test or manual check for the zero-sample case.

### D3. Scene and transform observers plus the OpenIGTLink connector are never released
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:253`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L253): The scene observer is added with slicer.mrmlScene.AddObserver (not self.addObserver), and the transform-node observers are added directly on the nodes (lines 736-745: self.ptrRefNode.AddObserver(...)). cleanup() only calls self.removeObservers() (lines 796-800), so after the module widget is destroyed the scene still invokes onNodeAdded/onNodeChanged on a dead widget, which raises exceptions or can crash Slicer when nodes are added later. The connector created at lines 267-273 is also never Stop()ed or removed, so the OpenIGTLink connection stays alive after the module is closed.
  ```
      slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
  ```
  Suggestion: Register all observers through self.addObserver, remove the node observers in cleanup(), and call self.cnode.Stop()/RemoveNode in cleanup().

### D4. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek minor, flash-lite ok, haiku concern

### D5. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Cancelling the output-folder dialog leaves the module with no logic and no UI wiring
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:124`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L124): The whole widget setup (logic creation, all signal connections, file selectors, OpenIGTLink connector) is inside this if-block. If the user presses Cancel in the folder dialog that pops up every time the module is opened, the module shows an empty panel with no explanation and no way to recover except reopening the module; any later callback that assumes self.logic exists would fail.
  ```
      if self.saveDialog.exec():
        # Path where the ouput files (including the log) will be saved
        savePath = self.saveDialog.selectedFiles()[0]
  ```
  Suggestion: Ask for the folder lazily (e.g. when the session starts) or show an explicit message and a button to re-open the dialog when it is cancelled.
- **haiku** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:121`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L121): The whole module setup, including the logic object and all signal connections, runs only inside `if self.saveDialog.exec():`. If the user cancels, no error is shown and the module UI is non-functional with no guidance on how to recover.
  ```
  self.saveDialog = qt.QFileDialog()
   self.saveDialog.setFileMode(qt.QFileDialog().DirectoryOnly)
  
   if self.saveDialog.exec():
  ```
  Suggestion: Show an explicit message when the dialog is cancelled, or move the output-folder choice into a parameter-node setting that the user can change later.

### Root logger FileHandler added on every module open and never removed
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:129`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L129): Each time the module is opened a new handler is attached to the root logger and never detached, so log lines are duplicated N times after N module opens, file handles accumulate, and the handler keeps writing to a folder the user may have since deleted.
  ```
        fh = logging.FileHandler(savePath + "/AstmPhantomTest_log_" + datetime.now().strftime("%Y.%m.%d") + ".log")
        fh.setLevel(logging.INFO)
        logging.getLogger().addHandler(fh)
  ```
  Suggestion: Store the handler on the widget and remove/close it in cleanup().

### self.modelId used before assignment when the parameter file has no MODEL line
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTestClasses/Phantom.py:55`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTestClasses/Phantom.py#L55): modelId is only created inside readGroundTruthFile when a MODEL line is present (Phantom.py:93-94); WorkingVolume.py:172 has the same pattern. A user-supplied ground-truth or working-volume file without MODEL therefore raises AttributeError instead of showing the intended error dialog, and the module state is left half-initialized.
  ```
      if not self.modelId:
        msg = f"Trying to (re)load phantom model, but no model id was provided."
  ```
  Suggestion: Initialize self.modelId = None in __init__ of both classes.

### setup() permanently changes Slicer main window size limits and all view-node display settings
minor; environment; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:73`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L73): These global settings are applied when the module is opened and never restored in exit()/cleanup(). After a user opens the module once, the Slicer main window cannot be resized beyond 1920x1080 and every view node in the scene has axis labels and the orientation box turned off (lines 105-108), which affects all other modules for the rest of the session. The custom layout 401 is also registered and activated globally.
  ```
      slicer.util.mainWindow().setMaximumHeight(1080)
      slicer.util.mainWindow().setMaximumWidth(1920)
      slicer.util.mainWindow().showMaximized()
  ```
  Suggestion: Save and restore the previous window maximum size and view-node settings in exit()/cleanup(), or avoid changing them at all.
- **haiku** (minor, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:73`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L73): Setup forces the Slicer main window to a fixed maximum size and maximizes it, changing the host application for all modules. It also adds a root-logger FileHandler each time setup runs, with no removal on cleanup, so logging is duplicated and redirected for the whole Slicer session.
  ```
  slicer.util.mainWindow().setMaximumHeight(1080)
  slicer.util.mainWindow().setMaximumWidth(1920)
  slicer.util.mainWindow().showMaximized()
  ```
  Suggestion: Do not change the main window geometry or constrain it globally. Attach the FileHandler to a module-specific logger and remove it in cleanup().

### No automated tests despite importing unittest
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:2`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L2): The standard ScriptedLoadableModule test class has been removed, so the extension ships no self-test and the index build cannot exercise it. For a tool whose purpose is quantitative accuracy measurement, at least a logic-level test (e.g. on Utils.Dist/RMS/Span and the parameter-file parsers) would be valuable.
  ```
  import unittest
  ```
  Suggestion: Add a ScriptedLoadableModuleTest covering the file parsers and statistics helpers.

### OpenIGTLink connector started automatically at module setup with default settings
info; safety; raised by deepseek
- **deepseek** (info, low confidence, quote verified) [`AstmPhantomTest/AstmPhantomTest.py:267`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/AstmPhantomTest.py#L267): The module opens a network connection as soon as it is opened, without asking the user for host/port, and never stops it. With OpenIGTLinkIF defaults this is a client connection to localhost, so no port is exposed and no data leaves the machine, but the behavior is implicit and the connection outlives the module.
  ```
      self.cnode = slicer.vtkMRMLIGTLConnectorNode()
      self.cnode.SetName('PointerConnector')
      slicer.mrmlScene.AddNode(self.cnode)
      if self.cnode.Start() != 1:
  ```
  Suggestion: Let the user configure/confirm the connection and stop it in cleanup().

### Research-only restriction is only in the license text
info; license; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`License.txt:147`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/License.txt#L147): Part B §4 of the Slicer agreement says the software is for research use and not clinically approved. The README and module help text do not carry a visible disclaimer, so users may take reports as clinical results.
  ```
  The Software has been designed for research purposes only and has
   not been reviewed or approved by the Food and Drug Administration
  ```
  Suggestion: Add a short research-use disclaimer to the module help text and README.

### Resource file present in the repository but not installed by CMake
info; packaging; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`AstmPhantomTest/CMakeLists.txt:27`](https://github.com/Atracsys/SlicerAstmPhantomTest/blob/de04b3a2137407f38eff5f468a1331975a364b5e/AstmPhantomTest/CMakeLists.txt#L27): AstmPhantomTest/Resources/wv/PolarisVegaExt_ftk500Locs.txt exists in the source tree but is absent from RESOURCES_FILES, so it is not installed and never appears in the working-volume selector. Harmless, but the file is dead weight or was forgotten.
  ```
    Resources/wv/FusionTrack250.txt
    Resources/wv/FusionTrack500.txt
    Resources/wv/PolarisVega.txt
    Resources/wv/PolarisVegaExtend.txt
  ```
  Suggestion: Add it to RESOURCES_FILES or remove it from the repository.

### scm_revision tracks a moving branch
info; packaging; raised by haiku
- **haiku** (info, high confidence, quote no quote) no file cited: The catalog entry uses scm_revision 'master', so the built code can change without a catalog update. I could not resolve the commit, so the reviewed source is only the one named in the task.
  Suggestion: Pin scm_revision to a tag or commit hash that was reviewed.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
No malicious behavior found: no downloads, no pip installs, no telemetry, no eval/exec, and all output goes to a user-chosen folder. The Slicer BSD-style license is present and the catalog entry matches the CMake (EXTENSION_DEPENDS = SlicerOpenIGTLink, category IGT, all Python classes installed). Main problems are robustness and global side effects: setup() permanently constrains the Slicer main window size and hides axis labels on all view nodes, the scene/transform observers and the OpenIGTLink connector are never released in cleanup(), the module is unusable if the user cancels the folder dialog, and a hardcoded password hash unlocks a hidden "dev shortcut" mode that can fake calibration and skip tests without being recorded in the report.
Not checked: README.md was only searched, not read in full; I did not verify whether it contains a clinical-use/regulatory disclaimer or license section.; The two large phantom models (Resources/models/phantom2018_RAS.stl, phantom2022_RAS.stl) referenced by AstmPhantomTest/CMakeLists.txt:13-14 could not be listed or read, so I could not confirm they are present in the repository at the reviewed revision; the directory listing returned only 7 model fil; The remaining ~150 lines of License.txt (lines 41-199) were not read; only the BSD-style Slicer license header was inspected.; AstmPhantomTest/Resources/UI/AstmPhantomTest.ui, the icon, the sound WAV files and the .github/workflows/github-repo-stats.yml workflow were not inspected.; AnalyzePhantomJSON.m (MATLAB helper at the repository root) was not read; it is not installed by CMake.; The exact source revision could not be resolved: the catalog entry pins scm_revision 'master', so the reviewed content is whatever the branch tip was when the files were fetched, not a fixed commit.; I could not run Slicer, so runtime behavior (observer leak consequences, connector default type, VTK subclass initialization in Measurements.py classes that do not call super().__init__()) is inferred from code reading only.
Questions for the author: Is the hardcoded password hash at AstmPhantomTest.py:640 intended to stay in released builds, and if so, is the use of the dev shortcuts recorded anywhere in the generated report?; Why are the scene NodeAdded observer and the transform-node observers not removed in cleanup(), and why is the OpenIGTLink connector never stopped?; Should the main window maximum size and the view-node axis-label/box settings be restored when the user leaves the module?; Are the bundled Atracsys tracker/pointer STL models and the phantom STL models covered by terms that permit redistribution with the extension?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The AstmPhantomTest extension is well-structured, follows Slicer scripted module conventions, correctly packages its resources and python classes via CMake, includes clear distribution licensing, and raises no safety or environmental concerns. 🟢 Recommend merge
Not checked: Exact remote repository files for model weights and datasets beyond what is in the catalog entry.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
I read the catalog entry, CMakeLists, the main module, Utils.py, the parts of Pointer.py and Phantom.py that matter, and the License.txt. I found no network calls, no exfiltration, no package installs and no shell/eval use, so there is no safety block. Issues: a NameError (`msgBoxsgBox`) in the no-sample error path, a hidden developer unlock that can bypass calibration and inject simulated hits into reports, and global side effects on the main window and root logger. The license is the 3D Slicer BSD-style agreement, which permits distribution. I could not run the module or inspect the other class files in full.
Not checked: Pointer.py, Targets.py, Measurements.py and WorkingVolume.py were only partly read, so their logic and any further bugs are unverified.; The UI .ui file, the CI workflow and the README beyond the search hits were not read in full.; Binary assets (STL models, WAV sounds, PNG icons) were not inspected for content or provenance.; No revision was resolved and the module was not loaded or run in Slicer, so behaviour was judged from the code alone.; The large files flagged by the scan (phantom STL, GIFs) were not read.
Questions for the author: Should the dev shortcuts and SkipCalib mode exist in the released extension? If so, will reports record that they were used?; Please confirm the source of the bundled STL models and whether their licence allows redistribution.; Is there an intended pinned revision rather than 'master'?


# AI review: RemoteView

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/dolegadolegowski/SlicerRemoteView.git at commit `ebe397a89efd47c0ec60df7a4d5446cdd96b8367`
- Context: pull request 2439 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-13T17:08:22Z; cost $1.40

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | minor | minor |
| packaging | unknown | ok | unknown |
| license | unknown | ok | ok |
| soundness | unknown | ok | concern |
| utility | unknown | ok | minor |
| **overall** | minor issues | no concerns | needs fixes |

## What each reviewer says the extension does

- **claude**: RemoteView is a Slicer scripted module that exports the visible models and segments as GLB and streams them through a user-specified relay server. Phones, tablets and Meta Quest headsets join the session with a 5-character code or QR link. The relay and web viewer live in the same monorepo.
- **gemini**: RemoteView is a 3D Slicer extension for clinicians, researchers, and educators to stream visible 3D models and segmentations from Slicer's 3D view to mobile browsers and Meta Quest headsets via a user-specified WebSocket relay server and a 5-character session code. It exports visible surface meshes as quantized, budget-decimated GLB snapshots and pushes incremental visual, transform, and geometry updates in real time.
- **gpt**: RemoteView lets 3D Slicer users stream visible models, segments, and live scene changes to a user-selected relay. Remote viewers can join from a browser or Quest headset using a session code.

## Disagreements (start here)

### D1. Start disclosure omits identifying names and IDs sent to the relay
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (2 of 2)**
- **gpt** (blocking, high confidence, quote verified) [`slicer-plugin/RemoteView/remoteview_core/consent.py:53`](https://github.com/dolegadolegowski/SlicerRemoteView/blob/ebe397a89efd47c0ec60df7a4d5446cdd96b8367/slicer-plugin/RemoteView/remoteview_core/consent.py#L53): The disclosure adjacent to Start says models and segments are sent, but does not say their names and segment IDs can contain patient identifiers, or that later opened scenes are also shared. The linked help is not necessarily opened before Start. PanelController creates LiveUpdates without an anonymization argument (panel.py 936–952), so its False default (live.py 216) is used; names and IDs can therefore be sent to the chosen relay and anyone joining without adequately informed opt-in.
  ```
      return (
          "Nothing leaves this computer before you click Start session. Then RemoteView sends the models and "
          f"segments shown in the 3D view, and every later change to them, to {relay}. {transport} "
          f'{MORE} <a href="{PROJECT_URL}">{PROJECT_URL}</a>'
  ```
  Suggestion: Before Start, explicitly disclose names, IDs, future loaded scenes, and who can access them; provide a functional name-hiding control before transmission or clearly state that names cannot be hidden.
- gpt on re-check: **real: yes, blocking**: The panel's actual pre-Start text, consent.py:53–56, says "segments shown in the 3D view, and every later change to them" but does not disclose transmitted names, segment IDs, viewers, or later scenes. The more complete Help (RemoteView.py:75–84) is not required to be opened. panel.py:936–952 constructs LiveUpdates without anonymize_names, and live.py:216,235 defaults it to False. names.py:113–120 returns the sanitized real name; ids.py:113–120 returns the raw segment ID. observers.py:625–629 and live.py:485–487 reset for a new scene rather than ending the session. Users can therefore transmit patient-identifying labels or a subsequently loaded scene to their chosen relay and code holders without sufficiently specific pre-transfer disclosure. Explicitly disclose identifiers, recipients and continuing sharing including new scenes before Start. The user does choose the relay; this is not an unsolicited background connection.
- gemini on re-check: **real: yes, minor**: In slicer-plugin/RemoteView/remoteview_core/consent.py:53-56, consent_text() states that RemoteView sends "the models and segments shown in the 3D view, and every later change to them, to {relay}" with a link to the project URL, while the more detailed explanation of names, segment IDs, and newly loaded scenes is placed in RemoteView.py:75-87 (Help & Acknowledgement tab) rather than in the inline label itself. However, the user must explicitly enter a relay URL (DEFAULT_RELAY_URL = "" in RemoteView.py:41) and click "Start session", the inline consent label clearly states that models/segments and later changes leave the computer to the named relay without E2E encryption, and the module's Help tab explicitly details all exported metadata. This is at most a minor disclosure wording suggestion, not a blocking safety issue.

### D2. Help advertises a name-hiding option that the panel cannot enable
single; category soundness; raised by gpt; outcome after cross-examination: **real, minor (2 of 2)**
- **gpt** (major, high confidence, quote verified) [`slicer-plugin/RemoteView/RemoteView.py:75`](https://github.com/dolegadolegowski/SlicerRemoteView/blob/ebe397a89efd47c0ec60df7a4d5446cdd96b8367/slicer-plugin/RemoteView/RemoteView.py#L75): The UI has no Hide node names control, and the panel creates LiveUpdates without setting anonymize_names, which defaults to False. A user trying to follow this help cannot activate the described protection, and names and segment IDs remain included when a session starts.
  ```
  Shows the 3D scene on phones, tablets and Meta Quest headsets that join with a 5-character code.
  Nothing leaves this computer until you click <b>Start session</b>. From then on the relay server
  shown in the panel receives: the surface meshes of the models and segments shown in 3D (no images
  or volumes), their names (unless <i>Hide node names</i> is on), MRML IDs and segment IDs, colours,
  opacity, visibility and transforms, and the Slicer, extension and operating-system versions.
  ```
  Suggestion: Wire a pre-session name-hiding control through PanelController to LiveUpdates, or remove the claim and warn that identifying names will be sent.
- gpt on re-check: **real: yes, major**: RemoteView.py:77–78 promises "their names (unless <i>Hide node names</i> is on)". I inspected the complete panel UI, Resources/UI/RemoteView.ui:1–317, and the connections in RemoteView.py:245–264; there is no such control. panel.py:936–952 supplies no anonymize_names argument, and live.py:216 defaults it to False. names.py:118–120 sends sanitized real names when false, and ids.py:113–120 includes raw segment IDs. The advertised privacy option cannot be activated through the panel, so users cannot use that protection. Fix the control and plumbing or remove the promise and clearly disclose actual behavior. This is important but an ordinary soundness finding, non-blocking under the index admission policy independently of D1.
- gemini on re-check: **real: yes, minor**: In slicer-plugin/RemoteView/RemoteView.py:75-79, helpText mentions "their names (unless <i>Hide node names</i> is on)". However, RemoteView.ui (lines 56-67, 225-245) has no "Hide node names" checkbox yet (docs/testing/slicer.md:1093 notes "*Hide node names* has no panel toggle yet (SLC-18)"), and PanelController._go_live in panel.py:936-952 constructs LiveUpdates without passing anonymize_names, leaving it at its default False (live.py:216). Because the help text documents a UI option that is not yet wired into the panel UI, this is a real minor documentation/UI mismatch.

### D3. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt blocking
- gpt on re-check: **rating blocking**: Safety is blocking because the specific exposure in D1 is verified: consent.py:53–56 omits names and segment IDs while names.py:113–120 and ids.py:113–120 show they can be exported. Help provides details at RemoteView.py:75–84 but is not a mandatory confirmation. In addition, repository content .claude/agents/reviewer.md:7–9 instructs reviewers, "You review changes for SlicerRemoteView. You do not edit files. Read `CLAUDE.md` and `docs/protocol.md`," and CLAUDE.md:48 instructs AI interaction language; under the given security instruction, repository text addressing AI reviewers must also be flagged as blocking. These appear to be project-development guidance, not proof of a malicious attempt, and were not followed. I inspected the disclosure, UI, panel/live export flow, dependency consent and relay URL validation, not all components or external dependencies; the exact checkout revision was not independently verified.
- gemini on re-check: **rating ok**: Checked RemoteView.py, consent.py, panel.py, and live.py. The extension performs no network activity at import or startup, has no default relay URL (DEFAULT_RELAY_URL = ""), requires the user to configure a relay and click "Start session", enforces TLS (wss://) for non-loopback hosts, and clearly discloses in the UI and Help tab that 3D scene models/segments are sent to the configured relay. There is no concealed data transmission or unsafe behavior.

### D4. Rating of soundness
rating dispute; category soundness; raised by claude, gemini, gpt; outcome after cross-examination: **settled: minor (concern, minor)**
Ratings: claude unknown, gemini ok, gpt concern
- gpt on re-check: **rating concern**: The cited Help explicitly describes "their names (unless <i>Hide node names</i> is on)" (RemoteView.py:77–78), but the full Resources/UI/RemoteView.ui:1–317 has no such control, and panel.py:936–952 omits the live.py:216 anonymize_names argument whose default is False. This advertised protection is unavailable in the normal UI. I also inspected the widget connections and cleanup in RemoteView.py:245–318 and the session start flow at 340–370; tests and Slicer runtime behavior were not executed. The concern rating is non-blocking soundness feedback under the admission policy.
- gemini on re-check: **rating minor**: The extension is well-structured, separates pure logic into remoteview_core, defers heavy imports until session start, and cleans up timers, sessions, and observers in cleanup() (RemoteView.py:289-319). The only soundness issue is the minor mismatch in RemoteView.py:78 where the help text mentions the "Hide node names" option before its checkbox has been added to the panel UI (RemoteView.ui:231-234).


## Findings from some reviewers

### Adds a toolbar to Slicer's main window at application startup
minor; environment; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`slicer-plugin/RemoteView/RemoteView.py:92`](https://github.com/dolegadolegowski/SlicerRemoteView/blob/ebe397a89efd47c0ec60df7a4d5446cdd96b8367/slicer-plugin/RemoteView/RemoteView.py#L92): When Slicer finishes starting up, `RemoteView.__init__` connects `startupCompleted()` to `self.addToolbar()`, which adds a `RemoteView` toolbar (`Send scene now` button and `Send changes:` combo box) to Slicer's main window even if the user never opens the RemoteView module. While lightweight (no network or heavy imports), modifying the global main window UI at startup affects all users who have the extension installed.
  ```
            if not slicer.app.commandOptions().noMainWindow:
                slicer.app.connect("startupCompleted()", self.addToolbar)
  ```
  Suggestion: Consider creating or showing the toolbar only when the user first opens the `RemoteView` module or starts a session, or providing a setting to hide it by default.

### Runtime dependency pins can replace another extension's packages
minor; environment; raised by gemini, gpt
- **gemini** (info, high confidence, quote verified) [`slicer-plugin/RemoteView/remoteview_core/deps.py:55`](https://github.com/dolegadolegowski/SlicerRemoteView/blob/ebe397a89efd47c0ec60df7a4d5446cdd96b8367/slicer-plugin/RemoteView/remoteview_core/deps.py#L55): When the user clicks Start session, `ensure_runtime_deps` checks whether `websockets==17.2` and `segno==1.6.6` are installed in those exact versions, and if another version is installed in Slicer's environment, prompts the user to replace or downgrade it. While neither package is bundled by Slicer and the dialog explicitly warns the user before installing, exact `==` pins on shared PyPI packages can cause version conflicts if another extension requires a different compatible version of `websockets` or `segno`.
  ```
  PACKAGES: tuple[Package, ...] = (
      Package("websockets", "17.2", "the secure connection to the relay"),
      Package("segno", "1.6.6", "the QR code of the join link"),
  )
  ```
  Suggestion: Consider accepting compatible version ranges (e.g. `websockets>=15,<18`) while installing a tested version when missing.
- **gpt** (minor, high confidence, quote verified) [`slicer-plugin/RemoteView/remoteview_core/deps.py:53`](https://github.com/dolegadolegowski/SlicerRemoteView/blob/ebe397a89efd47c0ec60df7a4d5446cdd96b8367/slicer-plugin/RemoteView/remoteview_core/deps.py#L53): A different installed version is treated as missing and can be replaced or downgraded in Slicer's shared environment after the user confirms, potentially breaking another extension that requires a different version. These are not the numpy and VTK development-only pins from the scan hint.
  ```
  #: In the order the dialog lists them. ``websockets`` 17.2 is the tested release (ADR 0009 item 7; the transport
  #: refuses a version below 15). ``segno`` 1.6.6 is the newest release when SLC-10 was written; SLC-11 tests against it.
  PACKAGES: tuple[Package, ...] = (
      Package("websockets", "17.2", "the secure connection to the relay"),
      Package("segno", "1.6.6", "the QR code of the join link"),
  )
  ```
  Suggestion: Accept compatible versions where feasible, or isolate runtime dependencies; retain the existing disclosure when replacement is unavoidable.

### Unconditional 1 ms sleep on the Qt main thread in the 50 ms pump timer
info; soundness; raised by gemini
- **gemini** (info, high confidence, quote verified) [`slicer-plugin/RemoteView/RemoteView.py:440`](https://github.com/dolegadolegowski/SlicerRemoteView/blob/ebe397a89efd47c0ec60df7a4d5446cdd96b8367/slicer-plugin/RemoteView/RemoteView.py#L440): `onPump` runs on the Qt main thread every 50 ms while a session is active and calls `time.sleep(0.001)` at the end of every tick. Although 1 ms is small, sleeping unconditionally on the GUI thread blocks Qt event processing for 2% of wall time whenever a session is active.
  ```
          # let the transport thread take the GIL (architecture §6, docs/research/slicer.md §3)
          time.sleep(0.001)
  ```
  Suggestion: Python releases the GIL during I/O and regularly at bytecode intervals (`sys.getswitchinterval()`); if yielding is needed only during heavy numpy/VTK work, consider yielding only when the transport thread actually has pending work or during snapshot preparation.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read the root and module CMake files, RemoteView.py, deps.py, consent.py, links.py, the vendored protocol, and a search of the module for dangerous calls. I found no subprocess use, eval/exec, pickle, disabled TLS verification, or startup side effects. Nothing is sent before the user clicks Start session. There is no default relay URL, and the consent text names the relay host. The pip install of websockets and segno is confirmed in a dialog and happens after Start, not at import. The CMake file lists match the module tree, and the MIT license is present. Remaining points are minor: exact pins on two non-bundled packages, a moving `main` revision, a large monorepo, and a dependence on a user-run relay. I did not read transport.py, panel.py or the other core modules in full.
Not checked: transport.py, panel.py, protocol_client.py, live.py and the other core modules were not read in full; relay-server, web-viewer and other npm components were not audited; No build, load or runtime test was possible; The linked README and user-guide content were not checked; The AI-agent configuration files (.claude, CLAUDE.md, prompts) were not read for instructions aimed at reviewers

### Gemini 4 Argon (`google/gemini-4-argon`): no concerns
RemoteView is a well-engineered 3D Slicer extension for sharing 3D surface models and segmentations with mobile devices and Meta Quest headsets over a user-specified WebSocket relay. All three admission requirements are met: (1) Safety and privacy are rigorously designed—nothing is installed or transmitted until the user clicks Start session, there is no default relay server, TLS is strictly verified, and potential PHI in node names or IDs is sanitized and kept out of logs; (2) the repository is under the MIT License; and (3) the catalog entry and root/submodule CMakeLists.txt files are complete and consistent. The heuristic flags for `numpy` and `vtk` pins are false positives from offline dev/test files. 🟢 Recommend merge.
Not checked: shared/fixtures/glb/large-synthetic.glb (4 MB binary test fixture not installed by CMake); Runtime execution in 3D Slicer 5.12 and live relay connection

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The source provides TLS transport, an explicit Start action, and a separate package-install prompt. However, the in-panel consent omits potentially identifying names and IDs, while the help describes a name-hiding control that is not wired into the panel. Runtime pins may also replace packages used by other extensions. The supplied catalog selects the moving main branch; its current resolution and build could not be verified. 🔴 Do not merge yet: fix the privacy disclosure/control and verify the catalog revision and build.
Not checked: The repository and main branch could not be resolved over the network, so the supplied commit ebe397a89efd47c0ec60df7a4d5446cdd96b8367 and its relationship to the catalog's main revision were not independently verified.; No Slicer build, module execution, tests, or remote relay deployment were run; available CI status was not inspected.; External PyPI package contents, transitive dependencies, and their license terms were not independently inspected.; The complete relay and web-viewer implementation, committed binary fixture, and all repository files were not exhaustively audited.


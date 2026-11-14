# AI review: SlicerConnect

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/pka420/SlicerConnect.git at commit `93e12e0d6d9b3456e64779b89855355264e8346f`
- Context: pull request 2331 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-14T21:49:55Z; cost $0.50

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | blocking | blocking |
| environment | unknown | minor | concern |
| packaging | unknown | ok | minor |
| license | unknown | ok | ok |
| soundness | unknown | concern | concern |
| utility | unknown | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: SlicerConnect is a three-module extension (Login, Project Hub, Editor) for real-time multi-user segmentation editing. It syncs labelmap deltas through a hosted backend at slicerconnect.from-delhi.net.
- **gemini**: SlicerConnect provides real-time, multi-user collaborative medical image segmentation in 3D Slicer with role-based access control. It targets researchers and clinicians who want to simultaneously edit and synchronize segmentations over a central backend server.
- **gpt**: SlicerConnect lets Slicer users collaborate on segmentation projects through a hosted service. It provides login, project and collaborator management, and real-time segmentation synchronization.

## Disagreements (start here)

### D1. An incoming full sync can erase an unrelated segmentation in the scene
single; category safety; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`SlicerConnectEditor/SlicerConnectEditor.py:691`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnectEditor/SlicerConnectEditor.py#L691): When the collaborative node does not exist, an incoming full sync adopts the first pre-existing segmentation, even if it belongs to another case. Lines 837–845 then call RemoveAllSegments on that node before importing the remote data, destroying unsaved local segmentations without confirmation; a failed import can also leave the adopted node empty.
  ```
      def _getOrCreateSegmentationNode(self):
          nodeName = "CollaborativeSegmentation"
          node = slicer.mrmlScene.GetFirstNodeByName(nodeName)
          
          if not node:
              # Check if any segmentation node exists to adopt it
  ```
  Suggestion: Create and track a dedicated session-owned node rather than adopting arbitrary scene nodes; stage and validate incoming data before replacing any existing data, with an explicit recovery path.
- claude on re-check: **real: yes, major**: SlicerConnectEditor.py:691-699 adopts and renames the first vtkMRMLSegmentationNode when no 'CollaborativeSegmentation' node exists. Line 841 then calls RemoveAllSegments() on it without any confirmation. This is real data loss of unsaved local work, but it only happens during a user-initiated collaboration session and only when the scene already has an unrelated segmentation. I rate it major, not blocking.
- gpt on re-check: **rating blocking**: SlicerConnectEditor/SlicerConnectEditor.py:403-414 dispatches a received full segmentation to handleFullSegmentation. Lines 695-699 adopt and rename the first existing segmentation when no node with the collaborative name exists: `node = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")` and `node.SetName(nodeName)`. Lines 837-845 then execute `segmentationNode.GetSegmentation().RemoveAllSegments()` before importing the remote labelmap. Thus an unrelated unsaved segmentation can be destroyed without confirmation; an import failure after removal can also leave it empty.
- gemini on re-check: **real: yes, major**: In `SlicerConnectEditor/SlicerConnectEditor.py:691-703`, `_getOrCreateSegmentationNode` checks for a node named `"CollaborativeSegmentation"`, and if not found, calls `slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")` and renames it. Then in `handleFullSegmentation` (`SlicerConnectEditor/SlicerConnectEditor.py:837-846`), it calls `segmentationNode.GetSegmentation().RemoveAllSegments()` before importing the incoming labelmap. However, this is an ordinary logic/design flaw when a user explicitly connects to a collaborative session, rather than a blocking safety vulnerability, so `major` (or `minor`) is more appropriate than `blocking`.

### D2. Unencrypted WebSocket (ws://) transmits authentication tokens and segmentation data in cleartext
partial; category safety; raised by gemini, gpt; outcome after cross-examination: **real, blocking (3 of 3)**
- **gemini** (blocking, high confidence, quote verified) [`SlicerConnectEditor/SlicerConnectEditor.py:339`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnectEditor/SlicerConnectEditor.py#L339): Despite the README claiming that all communication uses HTTPS and Secure WebSockets (WSS), `SlicerConnectEditorLogic` hardcodes an unencrypted `ws://` WebSocket endpoint (`ws://slicerconnect.from-delhi.net/collaboration/sessions`). In `connect()`, the user's authentication token is appended as a query parameter (`wsUrl = f"{self.WS_BASE_URL}/{sessionId}/ws?token={token}"`), and all segmentation voxel data and deltas are transmitted over this connection. This exposes both the bearer token and potentially sensitive medical segmentation data in cleartext over the network. Furthermore, the server URL is hardcoded in `SlicerConnectEditorLogic` and `SlicerConnectLoginLogic` rather than configurable by the user.
  ```
  class SlicerConnectEditorLogic(ScriptedLoadableModuleLogic):
      def __init__(self):
          ScriptedLoadableModuleLogic.__init__(self)
          self.WS_BASE_URL = "ws://slicerconnect.from-delhi.net/collaboration/sessions"
  ```
  Suggestion: Use `wss://` for WebSocket connections and read the server base URL from a user-configurable setting (matching `SlicerConnectServerURL` in `SlicerConnect.py`) rather than hardcoding an unencrypted `ws://` URL.
- **gpt** (blocking, high confidence, quote verified) [`SlicerConnectEditor/SlicerConnectEditor.py:339`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnectEditor/SlicerConnectEditor.py#L339): The connect method at lines 365–369 places the bearer token in this WebSocket URL, and full segmentations and deltas are sent over that connection. Anyone able to observe or modify network traffic can obtain the token and segmentation data or tamper with updates. README.md lines 32–35 incorrectly says all communication uses secure WebSockets, so users are not informed of this exposure.
  ```
  class SlicerConnectEditorLogic(ScriptedLoadableModuleLogic):
      def __init__(self):
          ScriptedLoadableModuleLogic.__init__(self)
          self.WS_BASE_URL = "ws://slicerconnect.from-delhi.net/collaboration/sessions"
  ```
  Suggestion: Require certificate-verified wss:// end to end, ensure the service supports it, and correct the security documentation.
- claude on re-check: **real: yes, blocking**: SlicerConnectEditor.py:342 hardcodes WS_BASE_URL as ws://slicerconnect.from-delhi.net/..., and line 367 appends ?token={token} to it. The bearer token and segmentation data therefore travel unencrypted. README.md line 34 describes the server with an https URL, so users are not told the WebSocket is cleartext. Medical segmentation data plus credentials sent in the clear is a concrete exposure.
- gpt on re-check: **rating blocking**: SlicerConnectEditor/SlicerConnectEditor.py:342 sets `self.WS_BASE_URL = "ws://slicerconnect.from-delhi.net/collaboration/sessions"`; lines 365-369 append `?token={token}` and connect. Lines 610-612 and 617-632 encode and send full voxel data; lines 560-588 send voxel deltas. An observer or active network attacker can read or tamper with these messages and steal the token. README.md:35 incorrectly states `* **Encryption**: All communication is performed over HTTPS and Secure WebSockets (WSS).`
- gemini on re-check: **real: yes, blocking**: In `SlicerConnectEditor/SlicerConnectEditor.py:342`, `self.WS_BASE_URL = "ws://slicerconnect.from-delhi.net/collaboration/sessions"` uses unencrypted `ws://`, and in `connect` (`lines 365-369`), the bearer token is passed in the URL (`wsUrl = f"{self.WS_BASE_URL}/{sessionId}/ws?token={token}"`). All full segmentations and deltas are transmitted over this cleartext connection, directly contradicting `README.md:35` which promises "All communication is performed over HTTPS and Secure WebSockets (WSS)." Exposing authentication tokens and potentially sensitive medical segmentation data in cleartext despite explicit documentation claiming WSS encryption is a blocking safety issue.

### D3. Connection URL logs the authentication bearer token
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`SlicerConnectEditor/SlicerConnectEditor.py:365`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnectEditor/SlicerConnectEditor.py#L365): Each connection prints the complete bearer token to Slicer's Python output or application logs. Anyone receiving a troubleshooting log containing it can potentially impersonate the user; query-string tokens may also be retained in server or proxy access logs even after transport is secured.
  ```
      def connect(self, sessionId, token):
          """Connect to WebSocket server with session ID and token"""
          wsUrl = f"{self.WS_BASE_URL}/{sessionId}/ws?token={token}"
          print(f"Connecting to: {wsUrl}")
          self.wsHandler.connectToServer(wsUrl)
  ```
  Suggestion: Never print credentials; authenticate with an authorization header or another mechanism that avoids URLs and logs.
- claude on re-check: **real: yes, minor**: SlicerConnectEditor.py:368 runs print(f"Connecting to: {wsUrl}"), and wsUrl includes ?token=. The token is printed to the Python console and log. This is a real leak into logs, but it stays local and is much less serious than the cleartext transport in D2. The token-in-URL problem is part of D2.
- gpt on re-check: **rating concern**: SlicerConnectEditor/SlicerConnectEditor.py:365-369 constructs `wsUrl = f"{self.WS_BASE_URL}/{sessionId}/ws?token={token}"` and then runs `print(f"Connecting to: {wsUrl}")`. The token is consequently exposed in Python output and potentially in shared diagnostic logs; URL query parameters can also be recorded by intermediaries, though their logging configuration was not inspected.
- gemini on re-check: **real: yes, minor**: In `SlicerConnectEditor/SlicerConnectEditor.py:367-368`, `connect()` constructs `wsUrl = f"{self.WS_BASE_URL}/{sessionId}/ws?token={token}"` and calls `print(f"Connecting to: {wsUrl}")`, which writes the full bearer token to Slicer's console/log files. Passing the token in the URL query string also risks exposure in server/proxy logs. This is a real issue, best rated `minor` (or `major`) as local log exposure of a session token.

### D4. Login redirects to non-existent module `CollaborativeSegmentation`
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`SlicerConnectLogin/SlicerConnectLogin.py:149`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnectLogin/SlicerConnectLogin.py#L149): After a successful login in `SlicerConnectLoginWidget.onLoginComplete`, the code calls `slicer.util.selectModule("CollaborativeSegmentation")`. However, the module included in this extension is named `SlicerConnect`, not `CollaborativeSegmentation`. This causes switching to the project hub module after login to fail.
  ```
              self._update_ui("Login successful")
              slicer.util.selectModule("CollaborativeSegmentation")
          else:
              self._update_ui(message)
  ```
  Suggestion: Change `"CollaborativeSegmentation"` to `"SlicerConnect"`.
- **gpt** (minor, high confidence, quote verified) [`SlicerConnectLogin/SlicerConnectLogin.py:144`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnectLogin/SlicerConnectLogin.py#L144): The installed module is named SlicerConnect, not CollaborativeSegmentation. Successful login therefore cannot perform the intended automatic transition to the project hub; users must navigate there manually.
  ```
              slicer.app.settings().setValue("SlicerConnectToken", token)
              slicer.app.settings().sync()
              self.ui.loginEmail.setText("")
              self.ui.loginPassword.setText("")
              self.ui.regPassword.setText("")
              self._update_ui("Login successful")
  ```
  Suggestion: Select SlicerConnect and test the login-to-project workflow.
- claude on re-check: **real: yes, minor**: SlicerConnectLogin.py:150 calls selectModule("CollaborativeSegmentation"). No module has that name; the modules are SlicerConnect, SlicerConnectLogin and SlicerConnectEditor. The automatic switch after login therefore fails, and the user has to open the hub manually.
- gpt on re-check: **rating minor**: SlicerConnectLogin/SlicerConnectLogin.py:149-150 runs `self._update_ui("Login successful")` followed by `slicer.util.selectModule("CollaborativeSegmentation")`. CMakeLists.txt:21-23 includes SlicerConnectLogin, SlicerConnect and SlicerConnectEditor, and SlicerConnect/CMakeLists.txt:4 says `set(module_name SlicerConnect)`. The intended project hub is not registered under the requested name by this extension, so the automatic transition fails; the user can select SlicerConnect manually.
- gemini on re-check: **real: yes, major**: In `SlicerConnectLogin/SlicerConnectLogin.py:150`, `onLoginComplete` calls `slicer.util.selectModule("CollaborativeSegmentation")`, whereas the hub module in this repository is named `SlicerConnect` (`SlicerConnect/SlicerConnect.py`). Because the automatic redirect after login fails and raises an error or fails to switch modules, this is a real soundness bug (`major` or `minor`; since the user can still manually switch modules in the Slicer toolbar, `minor` or `major` is appropriate—`major` because it breaks the primary post-login workflow step).

### D5. NameError (`local_path=Null`) breaks segmentation download
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`SlicerConnect/SlicerConnect.py:487`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnect/SlicerConnect.py#L487): In `onDownloadSegClicked`, `local_path=Null` uses `Null` instead of Python's `None`. When the user clicks the "Download Segmentation" button, Python raises `NameError: name 'Null' is not defined` before the `try` block even executes, completely breaking segmentation downloads. Additionally, in the `finally` block (`if os.path.exists(local_path):`), if `download_segmentation` fails and `local_path` is `None`, `os.path.exists(None)` raises a `TypeError`.
  ```
          seg_id = selectedSegs[0].data(qt.Qt.UserRole)
          local_path=Null
          try:
              local_path = self.api_client.download_segmentation(seg_id)
  ```
  Suggestion: Initialize `local_path = None` and check `if local_path and os.path.exists(local_path):` in the `finally` block.
- **gpt** (minor, high confidence, quote verified) [`SlicerConnect/SlicerConnect.py:487`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnect/SlicerConnect.py#L487): Null is not a Python name, so selecting a segmentation and pressing Download raises NameError before the try block and never downloads the file. Replacing it with None also requires guarding the cleanup path when download fails.
  ```
          seg_id = selectedSegs[0].data(qt.Qt.UserRole)
          local_path=Null
          try:
              local_path = self.api_client.download_segmentation(seg_id)
              self.logic.load_segmentation(local_path, selectedSegs[0].text())
  ```
  Suggestion: Initialize to None and remove the temporary file only when a valid path exists.
- claude on re-check: **real: yes, minor**: SlicerConnect.py:488 has local_path=Null, which raises NameError before the try block, so every segmentation download fails. The finally block at line 495 would also fail with os.path.exists(None) if the download raised. This is an ordinary bug in one feature. It is minor-to-major, and I rate it minor because it is not a safety issue.
- gpt on re-check: **rating concern**: SlicerConnect/SlicerConnect.py:487-490 has `local_path=Null` before the `try:` and download call. No definition of Null was found in the repository, so with a selected segmentation this raises NameError and prevents the download. Lines 494-495 say `finally:` and `if os.path.exists(local_path):`; if the initializer is changed to None, that cleanup would also need a guard when download fails. This is an ordinary correctness issue, not a safety admission blocker.
- gemini on re-check: **real: yes, major**: In `SlicerConnect/SlicerConnect.py:488`, `onDownloadSegClicked` has `local_path=Null` outside the `try` block. Because `Null` is not defined in Python, clicking Download Segmentation immediately raises `NameError: name 'Null' is not defined`. Furthermore, in the `finally` block at line 495 (`if os.path.exists(local_path):`), if `local_path` were initialized to `None` and `download_segmentation` failed, `os.path.exists(None)` would raise a `TypeError`. Because this completely breaks the segmentation download feature in the project hub, it is a `major` soundness bug.

### D6. Stray identifier `m` in `_try_refresh_token` causes NameError on token refresh
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`SlicerConnect/SlicerConnect.py:65`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnect/SlicerConnect.py#L65): In `BackendAPIClient._try_refresh_token()`, line 66 contains a stray `m` statement. When a 401 response triggers token refresh and the server responds with HTTP 200, executing line 66 raises `NameError: name 'm' is not defined`, which is caught by `except Exception` on line 80, causing token refresh to always fail.
  ```
              if response.status_code == 200:
                  m
                  data = response.json()
                  self.token = data.get("access_token")
  ```
  Suggestion: Remove the stray `m` on line 66.
- **gpt** (minor, high confidence, quote verified) [`SlicerConnect/SlicerConnect.py:65`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnect/SlicerConnect.py#L65): If a refresh token is present and the server returns 200, the standalone undefined name m raises NameError, which is caught and treated as refresh failure. Expired sessions therefore cannot be renewed through this path.
  ```
              if response.status_code == 200:
                  m
                  data = response.json()
                  self.token = data.get("access_token")
                  new_refresh = data.get("refresh_token")
  ```
  Suggestion: Remove the stray name and test the complete login, refresh, and retry flow.
- claude on re-check: **real: yes, minor**: SlicerConnect.py:66 contains a bare 'm' on its own line inside the HTTP 200 branch of _try_refresh_token. It raises NameError, and the surrounding try/except treats that as a failed refresh. Token refresh therefore never works. It is a contained functional bug.
- gpt on re-check: **rating minor**: SlicerConnect/SlicerConnect.py:53-66 reads the refresh token and contains `if response.status_code == 200:` followed by the standalone undefined name `m`. Lines 80-82 catch the resulting NameError and return False; lines 36-42 then treat the 401 as authentication failure. A successful refresh response cannot renew the session on this path.
- gemini on re-check: **real: yes, major**: In `SlicerConnect/SlicerConnect.py:65-67`, inside `_try_refresh_token()`, immediately after `if response.status_code == 200:` there is a standalone undefined identifier `m` on line 66. Executing this line raises `NameError: name 'm' is not defined`, which is caught by `except Exception as e:` on line 80 and causes token refresh to always return `False`. This completely breaks automatic session token refresh and is a `major` soundness issue.

### D7. Unprompted pip_install of websocket-client on logic instantiation
single; category environment; raised by gemini; outcome after cross-examination: **real, minor (3 of 3)**
- **gemini** (major, high confidence, quote verified) [`SlicerConnectEditor/SlicerConnectEditor.py:927`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnectEditor/SlicerConnectEditor.py#L927): `SlicerConnectEditorLogic.__init__()` instantiates `WebSocketHandler()`, which immediately calls `self.ensureDependencies()` and runs `slicer.util.pip_install("websocket-client")` without user confirmation. This happens whenever `SlicerConnectEditorWidget.setup()` runs (opening the module) or when `SlicerConnectEditorTest` instantiates `SlicerConnectEditorLogic()`. Installing packages into Slicer's shared Python environment when a module is opened or tested—without asking the user first—violates Slicer's environment rules.
  ```
      def test_SlicerConnectEditor1(self):
          self.delayDisplay("Starting the test")
          logic = SlicerConnectEditorLogic()
          segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
  ```
  Suggestion: Prompt the user for confirmation (e.g., via `slicer.util.confirmOkCancelDisplay`) before calling `slicer.util.pip_install("websocket-client")`, and defer the check until the user actually initiates a connection rather than in `__init__`.
- claude on re-check: **real: yes, minor**: SlicerConnectEditor.py:269-271 calls ensureDependencies() in WebSocketHandler.__init__, and lines 257-266 pip_install websocket-client if it is missing. The install has no confirmation prompt. It happens when the Editor logic is created, not at Slicer startup. The package is small, is not one Slicer bundles, and brings no Qt, VTK or torch. SlicerConnectLogin.py:157-169 does the same for requests. This breaks the convention of asking first, but the impact is low.
- gpt on re-check: **rating concern**: SlicerConnectEditor/SlicerConnectEditor.py:40-42 constructs `self.logic = SlicerConnectEditorLogic()` during widget setup; line 349 constructs `self.wsHandler = WebSocketHandler()`. Lines 257-271 call `self.ensureDependencies()` and, on ImportError, `slicer.util.pip_install("websocket-client")` without a confirmation dialog. This modifies the shared environment when the editor is opened if the package is missing; lines 927-929 also instantiate the logic during the test. It is not an import-time or unconditional installation.
- gemini on re-check: **real: yes, minor**: In `SlicerConnectEditor/SlicerConnectEditor.py:257-271`, `WebSocketHandler.__init__` immediately calls `self.ensureDependencies()`, which runs `slicer.util.pip_install("websocket-client")` if `websocket` is not installed (`line 264`). `SlicerConnectEditorLogic.__init__` (`line 349`) instantiates `WebSocketHandler()`, and `SlicerConnectEditorWidget.setup()` instantiates `SlicerConnectEditorLogic()`. While it does not run at module import/Slicer startup, installing a lightweight pure-Python package (`websocket-client`) when the user opens the module widget without a confirmation dialog is a `minor` environment/usability issue (the rubric specifically flags package installation at import/startup or without user confirmation for large downloads).


## Findings from some reviewers

### Dependencies are installed without a user confirmation
minor; environment; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`SlicerConnectEditor/SlicerConnectEditor.py:257`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnectEditor/SlicerConnectEditor.py#L257): Opening the editor constructs WebSocketHandler and, if the package is missing, installs it into Slicer's shared environment without asking. Login similarly installs requests when missing. These are conditional on opening the modules, not module-import or startup installs.
  ```
      def ensureDependencies(self):
          """Checks and installs websocket-client if missing."""
          try:
              import websocket
              self.websocket = websocket
          except ImportError:
  ```
  Suggestion: Explain the dependency and request confirmation before installation, with a way to decline.

### Inconsistent collaborator keys and role casing in `ManageCollaboratorsDialog`
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified, other lines) [`SlicerConnect/SlicerConnect.py:45`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnect/SlicerConnect.py#L45): In `ManageCollaboratorsDialog._refresh()`, line 662 reads `collab.get('user_id')` for each collaborator in the table, whereas line 673 collects `existing_ids = {collab.get('id') for collab in collaborators}`. In `_onRemove`, line 712 reads `username = self.userCombo.currentText` (which is the combo box from the "Add Collaborator" tab, not the removed collaborator's name). And in `_onAdd`, `role = self.roleCombo.currentText` sends the capitalized role (`"Editor"` or `"Viewer"`) instead of lowercase (`"editor"` or `"viewer"`).
  ```
          try:
              all_users = self.api_client.get_all_users()
              existing_ids = {collab.get('id') for collab in collaborators}
              self.userCombo.clear()
  ```
  Suggestion: Use consistent collaborator user ID keys, pass `role.lower()` in `_onAdd`, and display the removed collaborator's actual username in `_onRemove`.

### Login spinner is not listed as an installed resource
minor; packaging; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`SlicerConnectLogin/CMakeLists.txt:6`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnectLogin/CMakeLists.txt#L6): The login widget loads UI/spinner.gif, which exists in the source tree but is not listed in the module's CMake resources. In a packaged installation the loading animation will be unavailable; the primary UI and script are listed.
  ```
  slicerMacroBuildScriptedModule(
    NAME ${module_name}
    SCRIPTS ${module_name}.py
    RESOURCES "Resources/Icons/${module_name}.png;Resources/UI/${module_name}.ui"
  )
  ```
  Suggestion: Include Resources/UI/spinner.gif in the resource list.

### Missing `json` import and unclosed file handle in `create_segmentation`
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`SlicerConnect/SlicerConnect.py:140`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/SlicerConnect/SlicerConnect.py#L140): `SlicerConnect.py` does not import `json`, so calling `json.dumps(data)` in `create_segmentation` will raise `NameError: name 'json' is not defined`. Furthermore, the file handle opened with `open(file_path, "rb")` is never closed.
  ```
      def create_segmentation(self, project_id: str, name: str, color: str, file_path: str) -> Dict:
          import os
          files = {"file": (os.path.basename(file_path), open(file_path, "rb"), "application/octet-stream")}
          data = {"name": name, "color": color}
  
          return self._make_request(
  ```
  Suggestion: Import `json` in `SlicerConnect.py` and use a `with open(file_path, "rb") as f:` context manager.

### Catalog `icon_url` points to a non-existent root path
info; packaging; raised by gemini; **quote not found in source**
- **gemini** (info, high confidence, quote quote not found) [`CMakeLists.txt:9`](https://github.com/pka420/SlicerConnect/blob/93e12e0d6d9b3456e64779b89855355264e8346f/CMakeLists.txt#L9): In the catalog entry JSON, `icon_url` is set to `https://raw.githubusercontent.com/pka420/SlicerConnect/main/SlicerConnect.png`, which does not exist at the repository root. The actual icon in the repository is at `SlicerConnect/Resources/Icons/SlicerConnect.png` (as correctly set in `CMakeLists.txt` line 10).
  ```
    "homepage": "https://github.com/pka420/SlicerConnect",
    "icon_url": "https://raw.githubusercontent.com/pka420/SlicerConnect/main/SlicerConnect.png",
    "build_dependencies": [],
  ```
  Suggestion: Update `icon_url` in the catalog entry to `https://raw.githubusercontent.com/pka420/SlicerConnect/main/SlicerConnect/Resources/Icons/SlicerConnect.png`.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
I found no malicious code, but the extension has several real defects. Segmentation data and the auth token go over unencrypted ws://, while the README claims WSS. The code also has crash-level bugs: an undefined `Null` and a missing `json` import break segmentation download and upload, and a stray `m` breaks token refresh. A PyPI package is installed without asking. `spinner.gif` is not installed by CMake. The catalog entry pins `main` instead of a commit. The service is a single-author hosted backend whose source is not in this repo. Data leaves the machine only after explicit user actions, and the README discloses this. The license is BSD-3 and acceptable.
Not checked: Backend server source (separate repository) and its security; UI .ui files and binary resources; Runtime behavior inside Slicer; Whether the main branch HEAD equals the reviewed commit

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
🔴 Do not merge yet: SlicerConnect implements real-time collaborative segmentation across three scripted modules under a 3-Clause BSD license. However, there is a blocking safety issue: despite the README stating that all communication is encrypted over HTTPS and Secure WebSockets (WSS), `SlicerConnectEditorLogic` hardcodes an unencrypted `ws://slicerconnect.from-delhi.net/collaboration/sessions` URL, transmitting authentication tokens (in query parameters) and medical segmentation data in cleartext. Additionally, `websocket-client` is pip-installed without user confirmation when `SlicerConnectEditorLogic` is instantiated, and several runtime bugs (`NameError` on `Null` when downloading segmentations, `NameError` on stray `m` during token refresh, and redirecting to a non-existent `CollaborativeSegmentation` module after login) break core functionality.
Not checked: Live backend server behavior at https://slicerconnect.from-delhi.net and its external repository https://github.com/pka420/SlicerConnectBackend; Runtime testing inside 3D Slicer
Questions for the author: Can you make the backend server URL configurable in the Login and Editor modules (instead of hardcoded to `slicerconnect.from-delhi.net`) so institutions can self-host the backend without modifying code?; Why does `onJoinSessionClicked` store `self.current_project` (project ID) into `SlicerConnectSessionId` without calling `start_session` or selecting a segmentation?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The supplied source shows two blocking safety issues: collaboration uses plaintext WebSockets despite the documented encryption claim, and incoming full syncs can erase an unrelated existing segmentation. Bearer tokens are also printed, and missing dependencies are installed without confirmation. Several ordinary workflow and packaging defects are non-blocking. The supplied source snapshot was inspected, but the moving catalog revision and backend could not be independently verified. 🔴 Do not merge yet: secure the collaboration transport and prevent unintended segmentation destruction.
Not checked: Could not independently resolve the catalog's moving main branch or verify that the provided snapshot is commit 93e12e0d6d9b3456e64779b89855355264e8346f.; Could not inspect or run the separate backend, verify its authorization, storage, retention or WebSocket TLS configuration, or assess its source and deployment against each other.; Could not run Slicer, build the extension, execute tests, access CI results, or verify catalog schema and remote repository availability.; Binary images and animation were not inspected; external dependency distributions and their licensing were not independently fetched.
Questions for the author: Can the backend accept secure WebSockets and authorization headers, and can credentials already exposed in logs or traffic be revoked?; How should concurrent changes and existing local segmentations be protected and recovered during full synchronization?


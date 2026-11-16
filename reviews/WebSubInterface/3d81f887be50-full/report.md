# AI review: WebSubInterface

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/mbellehumeur/SlicerWebSub.git at commit `3d81f887be5063a6154bda396124983c31eb66d2`
- Context: pull request 2426 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-16T20:43:43Z; cost $1.70

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | concern | blocking |
| environment | unknown | minor | concern |
| packaging | unknown | blocking | blocking |
| license | unknown | ok | unknown |
| soundness | unknown | blocking | concern |
| utility | unknown | ok | minor |
| **overall** | needs fixes | needs fixes | needs fixes |

## What each reviewer says the extension does

- **claude**: WebSubInterface is a Slicer scripted module that connects 3D Slicer, as an "Image Display" client, to a FHIRcast/WebSub-style messaging hub. Browser worklists send it studies to open. It can also start a bundled local FastAPI hub as a subprocess and download browser clients (SPAs) from the author's GitHub release.
- **gemini**: WebSubInterface connects 3D Slicer as an Image Display client to a FHIRcast/WebSub-style messaging hub (cloud or local) for worklist-driven study loading, live scene synchronization, and multi-user conferencing, and can also run a local FastAPI/uvicorn hub server and download browser SPA clients.
- **gpt**: WebSubInterface provides a messaging hub and a Slicer image-display client for connecting imaging worklists, viewers and other applications. It is intended for researchers and educators using collaborative medical-imaging workflows.

## Disagreements (start here)

### D1. A valid ordinary user token grants privileged admin access
single; category safety; raised by gpt; outcome after cross-examination: **real, major (2 of 2)**
- **gpt** (blocking, high confidence, quote verified) [`WebSubInterface/hub/Lib/oauth_tokens.py:422`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/hub/Lib/oauth_tokens.py#L422): In OIDC mode HUB_REQUIRE_AUTH is always true, and any valid bearer token is accepted as an admin without checking an admin role, even when a separate admin token is configured. Consequently any authenticated user can read all users' subscription and audit contexts through /api/hub/admin/snapshot or reset all sessions via /api/admin/reset (routes/admin.py:78-119, 133-148).
  ```
          for token in ordered:
              if HUB_ADMIN_TOKEN and _token_matches_admin(token):
                  return {"admin": True, "via": "admin_token"}
              try:
                  claims = verify_bearer_token(token)
                  return claims_to_identity(claims)
  ```
  Suggestion: Require an explicit admin authorization claim or the configured admin secret for privileged endpoints, separately from ordinary user authentication.
- gpt on re-check: **real: yes, blocking**: WebSubInterface/hub/Lib/oauth_tokens.py:43-50 sets OIDC authentication required, and lines 402-427 accept either the admin token or any successfully verified client JWT, without testing an admin role: 'return claims_to_identity(claims)'. WebSubInterface/hub/Lib/http_util.py:93-101 performs no further role check, and routes/admin.py:78-119, 133-148 exposes the snapshot and resets all hub state. This permits an ordinary authenticated user to access other users' audit contexts and disconnect all sessions.
- gemini on re-check: **real: yes, major**: Verified in WebSubInterface/hub/Lib/oauth_tokens.py:407-433 (validate_admin_access) and WebSubInterface/hub/Lib/routes/admin.py:78-119, 133-148. When HUB_REQUIRE_AUTH is True (always true in OIDC mode, line 47), validate_admin_access accepts any valid bearer JWT via verify_bearer_token(token) and returns claims_to_identity(claims) without checking any admin role or requiring HUB_ADMIN_TOKEN, granting access to /api/hub/admin/snapshot and /api/admin/reset. While the standalone hub is primarily a development/collaborative component, in multi-user OIDC mode this allows any authenticated user to read all subscriptions/audit logs and reset the hub.

### D2. Any OIDC user can join other users' topics to extract their data
single; category safety; raised by gpt; outcome after cross-examination: **real, blocking (2 of 2)**
- **gpt** (blocking, high confidence, quote verified) [`WebSubInterface/hub/Lib/routes/conference.py:61`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/hub/Lib/routes/conference.py#L61): The authenticated identity is discarded and host/attendee topics are accepted without ownership checks or participant consent. hub_request.py:45-59 expands a request to every conference participant, so an authenticated attacker can create a conference involving a victim and request the victim's local DICOM worklist or studies; the client returns patient names and publishes DICOM bytes to the request topic. Conference publish fan-out similarly forwards payloads to all listed attendees (publish.py:219-248). This bypasses OIDC topic isolation.
  ```
  @router.post("/api/hub/conference")
  async def post_conference(request: Request):
      """Create a conference"""
      _enforce_bearer_auth(request)
      try:
          data = await _parse_request_body(request)
  ```
  Suggestion: Bind conference operations to the authenticated identity, require recipient authorization or consent before adding topics, and enforce per-request and per-payload access checks.
- gpt on re-check: **real: yes, blocking**: WebSubInterface/hub/Lib/routes/conference.py:61-90 calls '_enforce_bearer_auth(request)' but discards its identity and accepts caller-supplied host and participant topics. WebSubInterface/hub/Lib/hub_request.py:44-60, 143-171 expands a request from the attacker's own topic to connected participants, and lines 306-322 preserve the requester's topic in the forwarded event. image_display/lib/image_display_client_requests.py:115-162 returns local studies, and lines 295-335 exports DICOM and publishes it. hub/Lib/routes/hub_api.py:27-33 allows authenticated multipart publishing without a topic match, and hub/Lib/publish.py:219-248 fans conference messages out. The attack requires the victim's image-display client to be connected and the requester to have a matching connected subscription; it can expose patient data without the victim consenting to that conference.
- gemini on re-check: **real: yes, blocking**: Verified in WebSubInterface/hub/Lib/routes/conference.py:61-91 (post_conference), WebSubInterface/hub/Lib/hub_request.py:44-60 (_request_allowed_topics), WebSubInterface/hub/Lib/publish.py:219-248, and WebSubInterface/image_display/lib/image_display_client_requests.py:102-133, 295-335. post_conference calls _enforce_bearer_auth(request) without capturing the identity or calling _enforce_topic_match, and adds any specified attendee topics to hub.conferences without participant opt-in. Because _request_allowed_topics expands requests on a conference participant's topic to all conference participant topics, any authenticated user can create a conference including another user's topic and send status-request or dicom-request on their own topic, causing the victim's connected Slicer client to return local DICOM worklist metadata (including patient names) or publish DICOM files.

### D3. Client dependency is imported before the installation prompt
single; category packaging; raised by gpt; outcome after cross-examination: **real, blocking (2 of 2)**
- **gpt** (blocking, high confidence, quote verified) [`WebSubInterface/python_client/src/hub_client/client.py:167`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/python_client/src/hub_client/client.py#L167): WebSubInterface.py imports ImageDisplayClient at module import; that imports hub_client, whose __init__ immediately imports this file. If aiohttp is absent in Slicer's Python, the entire module fails to load before the user can reach HubServer's Start button and its dependency confirmation. The separately installed python_client tree does not install its pip dependencies.
  ```
  
  
  import aiohttp
  
  LOGGER = logging.getLogger(__name__)
  ```
  Suggestion: Defer the client import until after a user-confirmed dependency check, or provide a supported dependency mechanism that makes aiohttp available before module import.
- gpt on re-check: **rating blocking**: WebSubInterface/WebSubInterface.py:17-18 imports both widgets at module import; Lib/ImageDisplayClient.py:15 imports hub_client, python_client/src/hub_client/__init__.py:7 imports its client, and client.py:167 says 'import aiohttp'. Lib/HubServer.py:47-68 and 339-351 show installation occurs only after the Start action and confirmation. WebSubInterface/CMakeLists.txt:54-59 copies the client tree, while python_client/pyproject.toml:11-13 declares aiohttp but the copy does not install it. If aiohttp is absent, module loading fails before the prompt; the separate missing spa_download import in D5 can fail first. not_checked: whether every targeted Slicer distribution already bundles aiohttp; runtime behavior and exact checkout revision were not independently verified.
- gemini on re-check: **real: yes, blocking**: Verified in WebSubInterface/WebSubInterface.py:18, WebSubInterface/Lib/ImageDisplayClient.py:15, WebSubInterface/python_client/src/hub_client/__init__.py:7, and WebSubInterface/python_client/src/hub_client/client.py:167. WebSubInterface.py imports Lib.ImageDisplayClient at top level, which imports hub_client, which immediately imports hub_client.client where 'import aiohttp' executes at module import time. Because aiohttp is not bundled with Slicer and is only installed when clicking Start in HubServer.py:47-60 (_ensure_hub_deps), importing WebSubInterface at Slicer startup fails with ModuleNotFoundError before the module UI can load.

### D4. Default local hub exposes patient data and controls to the network
partial; category safety; raised by gemini, gpt; outcome after cross-examination: **real, blocking (2 of 2)**
- **gemini** (major, high confidence, quote verified) [`WebSubInterface/hub/hub.py:261`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/hub/hub.py#L261): When the user starts the local Hub from Slicer (`HubServer.py:367`), `hub.py` is launched with only `--port`, so `--host` defaults to `0.0.0.0` (all network interfaces) and `HUB_AUTH_MODE` defaults to `mock` with `HUB_REQUIRE_AUTH=False`. In addition, when connected to a hub (local or cloud), `image_display_client_requests.py` responds to `status-request` events on the subscribed topic with `list_local_dicom_worklist_studies()` (which includes `PatientName`, `StudyDescription`, `StudyDate`, and `StudyInstanceUID` from `slicer.dicomDatabase`) and responds to `dicom-request` events by reading and publishing the raw DICOM files from `slicer.dicomDatabase` (`local_dicom_export.py`). While the UI shows a PHI warning when creating a conference, connecting to a shared/cloud hub or starting the local hub on `0.0.0.0` can expose local DICOM database metadata and images to other subscribers on the same topic or local network without a prompt before Connect or Start.
  ```
      parser = argparse.ArgumentParser(description="Standalone Slicer WebSub Server")
      parser.add_argument("--port", type=int, default=2018, help="Server port (default: 2018)")
      parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host (default: 0.0.0.0)")
      args = parser.parse_args()
  ```
  Suggestion: Bind the local embedded Slicer hub to `127.0.0.1` by default in `HubServer.py` (e.g., passing `--host 127.0.0.1` unless the user explicitly opts in to LAN listening), and require explicit user confirmation before connecting the Image Display Client or allowing remote `dicom-request` / `status-request` access to `slicer.dicomDatabase`.
- **gpt** (blocking, high confidence, quote verified) [`WebSubInterface/hub/hub.py:261`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/hub/hub.py#L261): The Slicer Start button passes no host override (Lib/HubServer.py:365-368), while oauth_tokens.py:43-50 defaults to mock mode with authentication disabled. Any network peer, and potentially a website through the permissive CORS policy, can use the hub APIs and read the admin snapshot, whose audit contains event contexts. A connected image-display client also responds to requests with local patient names and can publish complete DICOM studies (image_display_client_requests.py:115-162, 295-335). Starting what the UI calls a local hub therefore exposes sensitive data without informed protection.
  ```
      parser = argparse.ArgumentParser(description="Standalone Slicer WebSub Server")
      parser.add_argument("--port", type=int, default=2018, help="Server port (default: 2018)")
      parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host (default: 0.0.0.0)")
      args = parser.parse_args()
  ```
  Suggestion: Bind to loopback by default, make network exposure an explicit informed choice, and require effective authentication and authorization before enabling sensitive operations.
- gpt on re-check: **real: yes, blocking**: WebSubInterface/Lib/HubServer.py:365-367 runs the server with only '--port'; hub/hub.py:261-264 defaults the host to '0.0.0.0', and hub/Lib/oauth_tokens.py:33-50 defaults to mock mode and no required authentication. The UI calls it a local server (HubServer.py:155-160). routes/admin.py:78-119 exposes audit data and lines 133-148 reset sessions. When an image-display client is connected, image_display/lib/image_display_client_requests.py:115-162 and 295-335 automatically return worklist data and export requested DICOM; local_dicom_worklist.py:92-116 includes patient name and study UID. Network reachability depends on firewall and the hub actually starting; client connection and an accessible DICOM database are required for that data path. Default CORS is wildcard (hub/Lib/env.py:20-31), but browser access also depends on browser network restrictions. Exposure of identifiable medical data is blocking.
- gemini on re-check: **real: yes, blocking**: Verified in WebSubInterface/Lib/HubServer.py:365-368, WebSubInterface/hub/hub.py:223-232, 261-264, WebSubInterface/hub/Lib/oauth_tokens.py:43-50, and WebSubInterface/image_display/lib/image_display_client_requests.py:115-133, 295-335. Clicking Start in HubServer.py launches hub.py with only '--port', so '--host' defaults to '0.0.0.0' (listening on all network interfaces) with HUB_AUTH_MODE='mock', HUB_REQUIRE_AUTH=False, and CORS allow_origins=['*']. When Slicer's Image Display Client is connected to this local hub (or any hub), it automatically responds to 'status-request' with all patient names and study descriptions from slicer.dicomDatabase (local_dicom_worklist.py:98-120) and responds to 'dicom-request' by reading and publishing raw DICOM files from slicer.dicomDatabase (local_dicom_export.py:96-119). This exposes local patient data to any peer on the local network (and via CORS to websites in the local browser) without explicit user warning or opt-in.

### D5. Missing `Lib/spa_download.py` in `MODULE_PYTHON_SCRIPTS` breaks module loading in installed builds
partial; category packaging; raised by gemini, gpt; outcome after cross-examination: **real, blocking (2 of 2)**
- **gemini** (blocking, high confidence, quote verified) [`WebSubInterface/CMakeLists.txt:4`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/CMakeLists.txt#L4): `WebSubInterface/Lib/HubServer.py` imports `from .spa_download import (...)` at module import time (lines 23-30), which is triggered when `WebSubInterface.py` imports `HubServerWidget` at Slicer startup. However, `Lib/spa_download.py` is omitted from `MODULE_PYTHON_SCRIPTS` in `WebSubInterface/CMakeLists.txt` (and there is no `install(DIRECTORY Lib ...)` rule). As a result, an installed package built by CMake will not include `Lib/spa_download.py`, causing `WebSubInterface` to fail to load with `ModuleNotFoundError: No module named 'Lib.spa_download'`.
  ```
  set(MODULE_PYTHON_SCRIPTS
    WebSubInterface.py
    Lib/HubServer.py
    Lib/ImageDisplayClient.py
    Lib/ConferenceDialog.py
    Lib/hub_presets.py
  ```
  Suggestion: Add `Lib/spa_download.py` to `MODULE_PYTHON_SCRIPTS` in `WebSubInterface/CMakeLists.txt`.
- **gpt** (blocking, high confidence, quote verified) [`WebSubInterface/CMakeLists.txt:4`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/CMakeLists.txt#L4): Lib/HubServer.py:23 imports .spa_download during module import, but Lib/spa_download.py is absent from this SCRIPTS list. The separate install rules only cover hub, python_client and image_display/lib, so the installed extension cannot import the module even if its other dependencies are present.
  ```
  set(MODULE_PYTHON_SCRIPTS
    WebSubInterface.py
    Lib/HubServer.py
    Lib/ImageDisplayClient.py
    Lib/ConferenceDialog.py
    Lib/hub_presets.py
  ```
  Suggestion: Add Lib/spa_download.py to MODULE_PYTHON_SCRIPTS and verify loading from an installed extension package.
- gpt on re-check: **rating blocking**: WebSubInterface/WebSubInterface.py:17 imports HubServerWidget, and WebSubInterface/Lib/HubServer.py:23-30 imports '.spa_download' at module load. WebSubInterface/CMakeLists.txt:4-13 lists Lib scripts but omits Lib/spa_download.py; lines 49-68 install only hub, python_client and image_display/lib separately. Thus the normal CMake-installed module lacks the imported file and cannot load. not_checked: an actual Slicer build or installation.
- gemini on re-check: **real: yes, blocking**: Verified in WebSubInterface/CMakeLists.txt:4-13, 49-68 and WebSubInterface/Lib/HubServer.py:23-30. Lib/HubServer.py imports from .spa_download at top level (imported by WebSubInterface.py:17), but Lib/spa_download.py is missing from MODULE_PYTHON_SCRIPTS in CMakeLists.txt and there is no install(DIRECTORY) rule for Lib/. Consequently, an installed build of the extension will fail to load WebSubInterface due to ModuleNotFoundError: No module named 'Lib.spa_download'.

### D6. Top-level import of `aiohttp` via `hub_client` causes module load failure at Slicer startup
single; category soundness; raised by gemini; outcome after cross-examination: **real, blocking (2 of 2)**
- **gemini** (blocking, high confidence, quote verified) [`WebSubInterface/Lib/ImageDisplayClient.py:15`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/Lib/ImageDisplayClient.py#L15): `WebSubInterface.py` imports `Lib.ImageDisplayClient` at module import time (Slicer startup), which imports `hub_client`, which in turn executes `import aiohttp` at the top level (`WebSubInterface/python_client/src/hub_client/client.py:167`). `aiohttp` is not bundled in Slicer's standard Python environment and is only installed when the user clicks the local Hub "Start" button (`_ensure_hub_deps()` in `Lib/HubServer.py`). On a fresh Slicer installation, `WebSubInterface` will fail to import at startup before the user can open the module or trigger dependency installation. Furthermore, if a user only uses the "Image Display Client" section with a cloud hub and never starts a local hub, nothing prompts to install `aiohttp`.
  ```
  from hub_client import IMAGINGSTUDY_OPEN, generate_subscriber_name
  from .conference import hub_endpoint_for_name
  from .ConferenceDialog import ConferenceDialog
  ```
  Suggestion: Defer importing `hub_client` and `image_display_client_hub` until the user clicks Connect (or enters the module), and ensure `aiohttp` is checked and installed (with user confirmation via `slicer.util.confirmYesNoDisplay`) before connecting the Image Display Client as well as before starting the local Hub.
- gpt on re-check: **rating concern**: WebSubInterface/WebSubInterface.py:17-18 imports ImageDisplayClient at load, Lib/ImageDisplayClient.py:15 imports hub_client, python_client/src/hub_client/__init__.py:7 imports client, and client.py:167 imports aiohttp unconditionally. HubServer.py:47-68 and 339-351 defer the install prompt until Start, so missing aiohttp prevents reaching it. This duplicates D3: broken loading when the dependency is missing is blocking for packaging; the soundness criterion is concern, with ordinary robustness feedback non-blocking under the index policy. not_checked: whether aiohttp is absent in a particular fresh Slicer build, or remote-only use in a running Slicer instance.
- gemini on re-check: **real: yes, blocking**: Verified in WebSubInterface/WebSubInterface.py:18, WebSubInterface/Lib/ImageDisplayClient.py:15, WebSubInterface/python_client/src/hub_client/__init__.py:7, and WebSubInterface/python_client/src/hub_client/client.py:167. Duplicate of D3: top-level import of hub_client in ImageDisplayClient.py triggers top-level 'import aiohttp' in hub_client/client.py:167 at Slicer startup before _ensure_hub_deps() in Lib/HubServer.py can ever run, causing the scripted module to fail to load on a clean Slicer environment.

### D7. Unvalidated `zipfile.extractall` when loading zip payloads from hub events
single; category safety; raised by gemini; outcome after cross-examination: **still disputed**
- **gemini** (major, high confidence, quote verified) [`WebSubInterface/image_display/lib/image_display_client_load.py:138`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/image_display/lib/image_display_client_load.py#L138): In `WebSubInterface/image_display/lib/image_display_client_load.py` (lines 142 and 163), zip archives received from a hub `imagingstudy-open` event are extracted using `archive.extractall(extract_dir)` without validating member paths against `..` or absolute paths (unlike `Lib/spa_download.py`, which uses `_safe_extract_zip`). On Python versions without PEP 706 enforcement or with crafted zip entries, a malicious publisher on the hub topic could write files outside `extract_dir`.
  ```
          if _is_zip_name(local_path):
              extract_dir = os.path.join(temp_dir, f"zip-{index}")
              os.makedirs(extract_dir, exist_ok=True)
              with zipfile.ZipFile(local_path, "r") as archive:
                  archive.extractall(extract_dir)
  ```
  Suggestion: Validate zip member paths before extraction (reuse the `_safe_extract_zip` logic from `Lib/spa_download.py`) instead of calling `archive.extractall()` directly.
- gpt on re-check: **real: no**: WebSubInterface/image_display/lib/image_display_client_load.py:138-142 and 159-163 do use 'archive.extractall(extract_dir)' on incoming ZIPs, but the claimed traversal outside that directory is not established: Python's zipfile extraction removes absolute prefixes and '..' path components; PEP 706 concerns tarfile, not zipfile. The absence of an explicit path validation wrapper alone does not demonstrate the asserted file escape. not_checked: resource-exhaustion risks such as ZIP bombs, alternative Python implementations, and an actual runtime exploit.
- gemini on re-check: **real: yes, major**: Verified in WebSubInterface/image_display/lib/image_display_client_load.py:138-143 and 159-163. When handling an imagingstudy-open event with a zip file payload or URL, _download_hub_file_entry calls archive.extractall(extract_dir) directly without validating member paths (unlike _safe_extract_zip in WebSubInterface/Lib/spa_download.py:109-121). A malicious or compromised publisher on the subscribed topic could supply a zip archive with path traversal entries to write arbitrary files outside the temporary directory.


## Findings from some reviewers

### Generic package and module paths inserted at the front of `sys.path` at Slicer startup
minor; environment; raised by gemini, gpt
- **gemini** (minor, high confidence, quote verified) [`WebSubInterface/Lib/repo_paths.py:23`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/Lib/repo_paths.py#L23): `ensure_monorepo_import_paths()` is called at the top level of `WebSubInterface.py` during Slicer startup and prepends `WebSubInterface` (which contains a top-level `Lib/` package) and `image_display/lib` directly to `sys.path[0]`. Note that in `WebSubInterface.py`, `from Lib.repo_paths import ...` relies on Slicer adding the scripted module directory to `sys.path`, which exposes the generic top-level package name `Lib` across Slicer's shared Python environment and can collide with other Slicer modules that use a `Lib` subdirectory.
  ```
  def ensure_monorepo_import_paths() -> Path:
      """Add python_client, service-provider runtime, and image-display lib to sys.path."""
      root = repo_root()
      extras = (
          root,
          root / "python_client" / "src",
  ```
  Suggestion: Namespace the helper libraries under a module-specific package name (e.g., `WebSubInterfaceLib`) rather than a generic `Lib` package and flat `sys.path` entries.
- **gpt** (minor, high confidence, quote verified) [`WebSubInterface/Lib/repo_paths.py:25`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/Lib/repo_paths.py#L25): WebSubInterface.py calls this at import, before the module is opened. Prepending directories containing generic top-level modules and the package name Lib can shadow similarly named modules in other extensions for the rest of the Slicer process.
  ```
      root = repo_root()
      extras = (
          root,
          root / "python_client" / "src",
          root / "image_display" / "lib",
      )
  ```
  Suggestion: Use uniquely named packages and avoid prepending generic module directories to the process-wide import path.

### Hub dependency check omits mandatory PyJWT
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`WebSubInterface/Lib/HubServer.py:33`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/Lib/HubServer.py#L33): hub.py unconditionally imports oauth_tokens, which imports jwt and PyJWKClient at module import (oauth_tokens.py:14-15). When PyJWT is not already installed, accepting the offered package installation still leaves the hub subprocess unable to start.
  ```
  # pip spec -> import name (Slicer pip_install accepts one package per call).
  _HUB_PIP_PACKAGES = (
      ("fastapi", "fastapi"),
      ("uvicorn[standard]", "uvicorn"),
      ("python-multipart", "multipart"),
      ("aiohttp", "aiohttp"),
  ```
  Suggestion: Include PyJWT with its needed crypto support in the confirmed dependency check and test on a clean Slicer environment.

### Study downloads block Slicer's GUI thread
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified, other lines) [`WebSubInterface/image_display/lib/image_display_client_handler.py:100`](https://github.com/mbellehumeur/SlicerWebSub/blob/3d81f887be5063a6154bda396124983c31eb66d2/WebSubInterface/image_display/lib/image_display_client_handler.py#L100): The callback is queued on the main thread at line 168, while the loading path performs URL downloads and archive extraction (image_display_client_load.py:126-163). Slow or stalled servers can freeze the Slicer interface despite the displayed progress dialog.
  ```
              _clear_hub_loaded_study(connection)
  
              if _is_stale_open_load(connection, load_generation):
                  return
  
              result = load_imaging_study_open(context)
  ```
  Suggestion: Perform network download and extraction in a cancellable worker, scheduling only Slicer scene operations on the main thread.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): needs fixes
The extension is MIT-licensed, has no obfuscation, and no reviewer-directed text. Pip installs are gated by a confirmation dialog. I found one likely load-breaking packaging defect: Lib/spa_download.py is imported at module load but is not in the CMake SCRIPTS list. Other concerns: the module imports aiohttp at load time, before any install prompt; the local hub binds 0.0.0.0 by default with mock auth and a known default JWT secret; the hub's PyJWT dependency is not in the install list; and downloaded SPA zips are unverified. The catalog entry uses scm_revision "main", which is allowed but moving. Review is partial: I did not read many hub and client files in full.
Not checked: 
<parameter name="">Did not read most of hub/Lib/routes/*, binary_publish.py, payload_store.py or client.py in full.
Questions for the author: 
<parameter name="">Is aiohttp available in Slicer's Python without a separate install? If not, how is the module expected to load before the user clicks Start?

### Gemini 4 Argon (`google/gemini-4-argon`): needs fixes
🔴 Do not merge yet: `WebSubInterface` has two blocking module-loading defects in an installed Slicer environment: (1) `WebSubInterface/CMakeLists.txt` omits `Lib/spa_download.py` from `MODULE_PYTHON_SCRIPTS`, even though `Lib/HubServer.py` imports it at startup; and (2) `Lib/ImageDisplayClient.py` imports `hub_client` (which imports `aiohttp`) at module load time before the user is ever prompted to install dependencies. Additionally, `image_display_client_load.py` calls `zipfile.extractall()` without path-traversal checks on downloaded archives, the local hub binds to `0.0.0.0` by default, and connecting to a hub exposes `slicer.dicomDatabase` metadata/files to `status-request`/`dicom-request` events without prior confirmation.
Not checked: External SPA client zip bundles downloaded on demand from GitHub release `spa-clients` (https://github.com/mbellehumeur/SlicerWebSub/releases/download/spa-clients/) were not fetched or inspected.; Cloud hub deployments at `bellehumeur-engineering.com` and `oidc.bellehumeur-engineering.com` were not tested.
Questions for the author: Should the local Hub started from inside Slicer bind to `127.0.0.1` by default rather than `0.0.0.0`?; Should users be prompted before exposing their local `slicer.dicomDatabase` study list and DICOM instances to hub `status-request` and `dicom-request` events on Connect (not just when creating a conference)?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The local hub exposes unauthenticated APIs on all interfaces, and OIDC mode has authorization gaps that can expose DICOM data. The packaged module also omits a required helper and imports aiohttp before its installation prompt. The supplied source was inspected, but the catalog's moving revision and downloaded client assets could not be independently verified. 🔴 Do not merge yet: fix the security and loading defects and verify the referenced revision and downloaded assets.
Not checked: No code was executed, built, or tested in Slicer; no CI results were available.; The supplied source snapshot was reviewed, but commit 3d81f887be5063a6154bda396124983c31eb66d2 and the catalog's main branch were not independently resolved or compared.; The floating GitHub SPA release assets, their source, integrity and third-party distribution notices were not available for inspection.; Not every bundled Python file, deployment script, or external service was fully audited.
Questions for the author: Can you provide the exact source revision selected by the catalog and provenance, checksums, and distribution notices for the downloadable SPA assets?


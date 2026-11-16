# AI review: UniGradICON

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/uncbiag/SlicerUniGradICON at commit `7a0bfeae3470994753ff45f4b31ac8edca13a5dc`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T10:20:50Z; cost $0.05

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | concern | ok | concern |
| environment | concern | ok | concern |
| packaging | minor | ok | minor |
| license | ok | ok | minor |
| soundness | minor | ok | ok |
| utility | minor | ok | ok |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A 3D Slicer module that performs medical image registration with the uniGradICON/multiGradICON foundation models, either locally (PyTorch in Slicer) or by uploading images to a UniGradICON registration server, with optional masking, segmentation guidance and label propagation. It is aimed at researchers and clinicians doing inter-/intra-subject image registration in Slicer.
- **flash-lite**: UniGradICON is a 3D Slicer extension that performs medical image registration using the GradICON family of foundational deep learning registration models, supporting both local execution (via PyTorch/uniGradICON) and remote server processing.
- **haiku**: UniGradICON is a Slicer module that runs uniGradICON/multiGradICON deep learning image registration, either locally in the user's Slicer (via the PyTorch extension) or on a remote registration server. It also includes a standalone FastAPI registration server that a Slicer instance can host for other clients.

## Disagreements (start here)

### D1. Module can downgrade Slicer's bundled NumPy to <2
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified, other lines) [`UniGradICON/UniGradICONLib/logic.py:42`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONLib/logic.py#L42): When an installed PyTorch reports a NumPy ABI mismatch, _checkPyTorchNumPyCompatibility offers to pip-install numpy<2 into Slicer's shared Python. This downgrades a package Slicer bundles, affecting every other module and extension in that Slicer installation, not only users of UniGradICON. It is behind a confirmation dialog and a restart is requested, which limits the harm, but the recommended path is to let the PyTorch extension provide a matching build rather than changing NumPy.
  ```
  slicer.util.pip_install("numpy<2")
  ```
  Suggestion: Do not modify NumPy; instead report the incompatibility and point users to the PyTorch extension / remote processing (as detectLocalBackendProblem already does).
- **haiku** (minor, high confidence, quote verified) [`UniGradICON/UniGradICONLib/logic.py:42`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONLib/logic.py#L42): When PyTorch reports a NumPy ABI mismatch, the module offers to run pip install numpy<2 in the shared Slicer Python. This changes a package Slicer bundles and affects other extensions after restart. It is confirmed by the user first, but the module triggers it.
  ```
  slicer.util.pip_install("numpy<2")
  ```
  Suggestion: Avoid downgrading NumPy. Point the user to a compatible PyTorch build or to remote processing, as the module already does in detectLocalBackendProblem.

### D2. Server can bind to all interfaces from the GUI with no access token by default
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote partly verified) [`UniGradICON/UniGradICONLib/server.py:365`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONLib/server.py#L365): startServer() constructs RegistrationServerProcess without a host, so the default 0.0.0.0 applies and the FastAPI server is reachable from the whole network. The token comes from a free-text field that is empty by default; UniGradICONServer/server.py check_token() only enforces auth when a token is set, and /jobs accepts arbitrarily large multipart uploads with no size cap. A user who clicks "Start server" on a hospital or campus network therefore exposes an unauthenticated endpoint that accepts files and runs GPU inference, and can be used to fill the disk. The UI does warn afterwards ("It has no token: anyone who can reach this computer can use it."), but the safe default (127.0.0.1, or refusing to start without a token) is not used.
  ```
  def __init__(self, port, token=None, weightsDir=None, host="0.0.0.0", jobsPerGpu=1, logCallback=None,
        self.address = f"{socket.gethostname() if host == '0.0.0.0' else host}:{port}"
  ```
  Suggestion: Default the Slicer-launched server to 127.0.0.1, or require a non-empty token before binding to 0.0.0.0, and add a request/upload size limit in the server.
- **haiku** (major, high confidence, quote verified) [`UniGradICON/UniGradICONLib/server.py:365`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONLib/server.py#L365): RegistrationServerProcess defaults to host 0.0.0.0, and the GUI starts it with whatever token is typed, which may be empty. Anyone on the network who can reach the port can submit images and use the GPU, and read result transforms and warped images. The UI and log warn about this, but nothing blocks an empty token.
  ```
  def __init__(self, port, token=None, weightsDir=None, host="0.0.0.0", jobsPerGpu=1, logCallback=None,
  ```
  Suggestion: Default the GUI to 127.0.0.1 or require a token before binding to a non-loopback address. Keep the warning.

### D3. pip-installs an exactly pinned unigradicon whose dependency chain includes torch
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`UniGradICON/UniGradICONLib/logic.py:117`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONLib/logic.py#L117): UNIGRADICON_REQUIREMENT is "unigradicon==1.0.6" (UniGradICONHelpers/segmentation.py line 7). unigradicon depends on icon_registration and torch, so pip resolves torch from PyPI inside Slicer's environment; if the installed torch does not satisfy unigradicon's requirement, pip can replace the PyTorch-extension-provided torch (and its CUDA build) for all extensions. The install is user-confirmed, but the resulting environment is no longer the one the PyTorch extension manages.
  ```
  slicer.util.pip_install(UNIGRADICON_REQUIREMENT)
  ```
  Suggestion: Install with --no-deps and check/declare the required torch and icon_registration versions explicitly, or vendor the needed code, so torch is never resolved from PyPI.
- **haiku** (minor, low confidence, quote verified) [`UniGradICON/UniGradICONLib/logic.py:117`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONLib/logic.py#L117): The local backend is installed with pip_install(unigradicon==1.0.6). Its dependency tree (icon_registration, possibly torch and itk) is not verified here. Such installs can replace or upgrade PyTorch or ITK outside PyTorchUtils, which the AGENTS policy flags. The install is confirmed by the user, but the dependency tree is unverified.
  ```
  slicer.util.pip_install(UNIGRADICON_REQUIREMENT)
  ```
  Suggestion: Install with --no-deps for the pinned package and check its dependencies against Slicer's bundled packages and PyTorchUtils, or document the exact resulting changes.

### D4. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D5. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Model weights are downloaded without any integrity check
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified, other lines) [`UniGradICON/UniGradICONHelpers/registration.py:62`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONHelpers/registration.py#L62): Weights come from GitHub release URLs over HTTPS but are not verified against a known hash before being loaded. A compromised or replaced release asset would be used silently. The impact is limited because the file is loaded with torch.load(..., weights_only=True) (line 99), so no arbitrary code execution, but a tampered model would produce wrong registrations without any signal.
  ```
  urllib.request.urlretrieve(url, partial_path)
        os.replace(partial_path, path)
  ```
  Suggestion: Pin and verify a SHA-256 of each weights file before os.replace().
- **haiku** (minor, medium confidence, quote verified) [`UniGradICON/UniGradICONHelpers/registration.py:62`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONHelpers/registration.py#L62): uniGradICON weights are fetched with urlretrieve and no checksum is verified before the file is published into the weights folder. Compromise of the release asset would feed into a torch.load of the file. weights_only=True limits the risk, but the weights are not verified.
  ```
  urllib.request.urlretrieve(url, partial_path)
  ```
  Suggestion: Pin and verify a SHA-256 for each weights file before publishing it.

### No research-use / clinical disclaimer
minor; utility; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`README.md:5`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/README.md#L5): The module runs a deep-learning registration model on clinical images and writes transforms/volumes into the scene, but the README and module help text contain no statement that results are for research use and must be verified before clinical use. Model provenance (papers, weights source) is otherwise well documented.
  ```
  This is the official Slicer extension for [uniGradICON and multiGradICON](https://github.com/uncbiag/uniGradICON), foundation models for medical image registration.
  ```
  Suggestion: Add a short research-use-only disclaimer to README.md and to the module helpText/acknowledgementText.

### PyTorch extension is required for local registration but not declared as a dependency
minor; packaging; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`CMakeLists.txt:13`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/CMakeLists.txt#L13): UniGradICONLib/logic.py imports PyTorchUtils and raises "This module requires PyTorch extension. Install it from the Extensions Manager." when it is missing, and the catalog entry has build_dependencies []. Users who install UniGradICON for local registration therefore get a runtime error instead of the PyTorch extension being installed with it. Remote-only use works without it, so this is not a loading failure.
  ```
  set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies
  ```
  Suggestion: Declare PyTorch in EXTENSION_DEPENDS and in the catalog entry's build_dependencies, or state clearly in the module UI that local registration needs a separate install.

### Remote client silently upgrades bare addresses to plain HTTP for medical image uploads
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`UniGradICON/UniGradICONHelpers/remote.py:28`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONHelpers/remote.py#L28): Entering "host:8899" sends the fixed/moving images, masks and segmentations unencrypted over the network; the README does advise an SSH tunnel or HTTPS outside a trusted network, but the client neither warns nor requires TLS. On an untrusted network this exposes patient images and the access token in transit.
  ```
  self.url = url.strip().rstrip("/")
      if "://" not in self.url:
        self.url = "http://" + self.url
  ```
  Suggestion: Warn in the UI when the configured server URL is plain http and not localhost, or support/encourage https.
- **haiku** (minor, medium confidence, quote verified) [`UniGradICON/UniGradICONHelpers/remote.py:29`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONHelpers/remote.py#L29): A bare hostname gets an http:// scheme. The access token and all uploaded medical images then travel in cleartext unless the user types https://. The server README mentions this only as a general caution.
  ```
  if "://" not in self.url:
          self.url = "http://" + self.url
  ```
  Suggestion: Warn in the UI when a token or patient images would go over http, or default to https where supported.

### Runtime dependency on PyTorch extension not declared in catalog or CMake
minor; packaging; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`UniGradICON/UniGradICON.py:40`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICON.py#L40): The module requires PyTorchUtils for local registration, but parent.dependencies is empty and EXTENSION_DEPENDS is "NA". The module handles the missing extension at runtime, so this is not a load failure, but Slicer will not install PyTorch automatically.
  ```
  self.parent.dependencies = []
  ```
  Suggestion: Declare PyTorch (or PyTorchUtils) as a dependency in CMake and in the catalog's build_dependencies if the index build should install it, or confirm this is intended.

### Server packages installed into Slicer's Python on demand
minor; environment; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`UniGradICON/UniGradICONLib/server.py:296`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONLib/server.py#L296): Starting the local server installs fastapi/uvicorn/python-multipart into Slicer's shared environment after a confirmation dialog. This is user-initiated and confirmed, but it adds unpinned web-server packages to every module in that Slicer, and a later version change can break the server without notice.
  ```
  slicer.util.pip_install("fastapi uvicorn python-multipart")
  ```
  Suggestion: Pin compatible versions and document that these packages are added to Slicer's Python.

### Test module imported by the runtime entry point
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`UniGradICON/UniGradICON.py:23`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICON.py#L23): The main module imports the self-test class at load time, so test code and its dependencies load whenever the module loads. This adds import-time cost and a coupling risk. It is not a safety issue.
  ```
  from UniGradICONTests.slicer_tests import UniGradICONTest
  ```
  Suggestion: Import the test class lazily or only when the self-test is run.

### Downloaded model weights' license not stated
info; license; raised by haiku
- **haiku** (info, low confidence, quote verified) [`UniGradICON/UniGradICONHelpers/registration.py:15`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONHelpers/registration.py#L15): The extension's code is Apache 2.0, but the uniGradICON weights it downloads at runtime are not covered by a license in this repository. Redistribution is not done by the extension, but users' terms are unclear.
  ```
  "unigradicon": (
        "unigradicon_weights.pth",
  ```
  Suggestion: Cite the weights' license terms in the README.

### Downloaded weights are loaded with weights_only=True
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`UniGradICON/UniGradICONHelpers/registration.py:99`](https://github.com/uncbiag/SlicerUniGradICON/blob/7a0bfeae3470994753ff45f4b31ac8edca13a5dc/UniGradICON/UniGradICONHelpers/registration.py#L99): Positive observation: the downloaded checkpoint is deserialized with weights_only=True, so a tampered file cannot execute code through pickle. No eval/exec, no telemetry, and no reviewer-directed instructions were found in the inspected files.
  ```
  model.regis_net.load_state_dict(torch.load(weights_path, map_location=torch_device, weights_only=True))
  ```


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Well-structured, documented extension: Apache-2.0, all Python files installed by CMake, heavy imports deferred, registration off the GUI thread, temp dirs used, weights loaded with torch.load(weights_only=True), no telemetry or obfuscation. Main concerns are environment and network defaults: the bundled registration server binds 0.0.0.0 with an optional (often empty) token and no upload limits, the module can downgrade Slicer's bundled NumPy to <2, and it pip-installs an exactly pinned unigradicon whose dependency chain includes torch. PyTorchUtils is used correctly but the PyTorch extension is not declared in EXTENSION_DEPENDS. No blocking issue found; fixes recommended before wide distribution.
Not checked: UniGradICONLib/comparison.py, UniGradICONLib/registration.py, UniGradICONLib/segmentation.py, UniGradICONHelpers/icon_helper.py and the three test modules were not read line by line.; The license of the uniGradICON model weights (GitHub release assets) and of the pip packages unigradicon/icon_registration was not verified.; Whether unigradicon==1.0.6's declared requirements actually pin or replace torch/numpy in Slicer's environment (no package metadata access).; The exact source at commit 7a0bfeae3470994753ff45f4b31ac8edca13a5dc was not fetched; I reviewed the file tree provided for that revision.; CI/build results for the catalog entry and whether the extension builds on all supported platforms.; Runtime behavior of the FastAPI server (no execution possible in this environment).
Questions for the author: Why does the Slicer-launched registration server default to host 0.0.0.0 instead of 127.0.0.1, and can it require a token before binding to all interfaces?; Does unigradicon==1.0.6 declare a torch requirement that could cause pip to replace the PyTorch-extension-provided torch in Slicer's Python?; Can the NumPy<2 downgrade be replaced by an error message pointing to the PyTorch extension or remote processing?; Should the PyTorch extension be declared in EXTENSION_DEPENDS/build_dependencies given that local registration needs PyTorchUtils?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
UniGradICON is a well-structured and robust 3D Slicer extension for deep learning-based image registration using GradICON models. It correctly uses PyTorchUtils for optional local backend installation, implements robust remote and local task execution with proper cancellation and cleanup, adheres to Slicer conventions, and packages all necessary scripts and resources correctly.
Not checked: Full runtime test execution with actual PyTorch/GPU hardware and weights download

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
I read the entry, CMake files, main module, logic, server control, remote client, task/worker code, and the server's token and bind handling. No malicious or concealed behavior was found. Weights come from GitHub over HTTPS and load with weights_only=True. Main concerns: the server can be started on 0.0.0.0 with no token from the GUI, remote calls default to plain HTTP, and the module runs pip installs and a NumPy downgrade in the shared Slicer environment, with user confirmation. Catalog dependencies do not declare the PyTorch extension. The rest of the packaging looks consistent. Not verified: the readiness/registration/segmentation Lib modules, the weights license, and any build run.
Not checked: UniGradICONLib/readiness.py, registration.py, segmentation.py, comparison.py, and UniGradICONHelpers/segmentation.py and icon_helper.py were not read.; UniGradICONServer/server.py was only partly read (the bind and token section), and the job, upload, and cleanup paths were not reviewed.; Test files (slicer_tests.py, workflow_tests.py, segmentation_tests.py, Testing/Python) were not read, and no tests were run.; No network access: the upstream repos, the weights and their license, and the pinned unigradicon 1.0.6 dependency tree were not checked.; The source at the catalog revision 'main' was not resolved to a commit. No CI results were available.; The README's clinical-use and disclaimer wording was not fully reviewed beyond the parts read.
Questions for the author: Should the GUI-started server default to 127.0.0.1, or refuse to bind 0.0.0.0 without a token?; Which dependencies does unigradicon==1.0.6 pull in, and can installing it change the PyTorch or ITK already in Slicer?; What license governs the downloaded uniGradICON/multiGradICON weights?; Should the PyTorch extension be declared as a build or runtime dependency?


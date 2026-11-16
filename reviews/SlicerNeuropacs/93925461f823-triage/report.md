# AI review: SlicerNeuropacs

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/neuropacs/SlicerNeuropacs at commit `93925461f8232b1039c271124e5ce78efcaea225`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T10:23:04Z; cost $0.03

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | blocking | ok | concern |
| environment | concern | ok | concern |
| packaging | concern | ok | ok |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: SlicerNeuropacs is a thin Slicer client for the commercial neuropacs™ cloud service: it lets a user with an API key pick a DICOM series from Slicer's DICOM database, upload it to neuropacs' AWS backend for atypical-Parkinsonism (MSAp/PSP) analysis, and download the resulting report (PNG/TXT/JSON/XML). It targets neuroradiologists and neurologists.
- **flash-lite**: Provides a 3D Slicer scripted module for uploading diffusion MRI data to the neuropacs cloud service, tracking processing jobs, and downloading/displaying biomarker reports for Parkinsonism differentiation.
- **haiku**: SlicerNeuropacs is a Slicer scripted module that sends DICOM diffusion MRI datasets from the user's machine to the neuropacs cloud service (hosted AWS API) and displays returned Parkinsonism (MSAp/PSP) analysis reports. It is intended for neuroradiologists and neurologists who have a neuropacs API key.

## Disagreements (start here)

### D1. Identifiable DICOM data uploaded to a third-party cloud endpoint without de-identification or explicit consent
single; category safety; raised by deepseek
- **deepseek** (blocking, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:585`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L585): selectedFolderPath comes from Slicer's DICOM database (line 461: `dataset_folder = os.path.dirname(first_file_path)`), i.e. the raw .dcm files including PatientName, PatientID, birth date and study metadata. The whole folder is sent to the hard-coded endpoint `https://jdfkdttvlf.execute-api.us-east-1.amazonaws.com/prod` (line 502). A search of the repository for 'de-identif', 'anonym', 'consent', 'HIPAA', 'privacy' or 'PHI' returns no matches, and the UI (Resources/UI/NeuropacsScriptedModule.ui) contains no notice or confirmation dialog. A clinician clicking 'Run analysis' therefore transmits identifiable patient imaging to a third party with no informed opt-in and no way to know what is included in the payload.
  ```
                      # Create a new neuropacs order               
                      orderId = self.npcs.new_job()
                      logging.info(f"neuropacs order '{orderId}' created")
  
                      # Upload dataset
                      self.npcs.upload_dataset_from_path(orderId, selectedFolderPath)
  ```
  Suggestion: Add an explicit, one-time consent/notice dialog that names the destination, lists the data sent, and states whether identifiers are included; offer de-identification (e.g. DICOM anonymization before upload) or document that the service requires identifiable data and that the user is responsible for consent; document the endpoint and privacy policy in the README and module help.

### D2. Core upload behaviour is delegated to a PyPI package fetched and auto-upgraded at runtime
partial; category safety; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified, other lines) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:143`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L143): The code that actually serialises and uploads the DICOM data (`neuropacs.init`, `upload_dataset_from_path`, `get_results`) is not in this repository; it is installed from PyPI at runtime and, worse, always upgraded to whatever version PyPI reports as latest (line 224 `slicer.util.pip_install(f"neuropacs=={latest_version}")`). The reviewed source therefore does not determine what is transmitted, where, or with which dependencies, and the behaviour can change without any change to this repository or to the catalog revision.
  ```
          try:
              response = requests.get("https://pypi.org/pypi/neuropacs/json")
              latest_version = response.json()["info"]["version"]
          except Exception:
              print("Error fetching the latest version of neuropacs from PyPI.")
              return
  ```
  Suggestion: Pin a reviewed version of the neuropacs client (or vendor the upload code), remove the automatic 'latest' upgrade, and show the user a confirmation before installing/upgrading anything.
- **haiku** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:211`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L211): requests.get is called without a timeout (line 211). A stalled network can hang the GUI thread. On any exception the function returns silently (lines 213-215), so the subsequent 'import neuropacs' can run against an older or missing package without the user being told.
  ```
  response = requests.get("https://pypi.org/pypi/neuropacs/json")
  ```
  Suggestion: Add a timeout, run the install off the GUI thread with progress, and surface a clear error when the package is missing or outdated.

### D3. Help PDF is not installed by CMake, so the Help button fails in the packaged extension
single; category packaging; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`NeuropacsScriptedModule/CMakeLists.txt:9`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/CMakeLists.txt#L9): The module resolves its help file at runtime as `os.path.join(modulePath, 'Resources', 'Docs', 'neuropacs_instructions.pdf')` (NeuropacsScriptedModule.py:534) and shows 'PDF not found' if missing (line 541). Resources/Docs/neuropacs_instructions.pdf exists in the repository but is not listed in MODULE_PYTHON_RESOURCES, so it is not installed into the extension build and the Help button is broken for every catalog user.
  ```
  set(MODULE_PYTHON_RESOURCES
    Resources/Icons/${MODULE_NAME}.png
    Resources/UI/${MODULE_NAME}.ui
    )
  ```
  Suggestion: Add `Resources/Docs/neuropacs_instructions.pdf` to MODULE_PYTHON_RESOURCES (and the Examples PNG if it should ship).

### D4. Medical data is sent to a hosted third-party endpoint with no disclosure or opt-in beyond an API key
single; category safety; raised by haiku
- **haiku** (major, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:502`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L502): The hard-coded AWS API endpoint receives DICOM data from the user's machine (lines 502 and 590). Nothing in the UI, the README or the module warns that images leave the computer, where they go, or how they are retained. The only gate is the 'Run analysis' click. Clinicians could upload identifiable patient data without informed consent or knowledge of the data-processing terms.
  ```
  self.npcs = neuropacs.init("https://jdfkdttvlf.execute-api.us-east-1.amazonaws.com/prod", enteredKey, "Slicer")
  ```
  Suggestion: Add an explicit informed-consent dialog before the first upload that names the destination, the data sent (including identifiers in DICOM headers) and the retention terms. Link to the privacy policy and document the transmission in the README.

### D5. Patient names are stored in plaintext in a config file in Documents
partial; category safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:242`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L242): `selectedPatient` is the DICOM patient name (line 464 `self.ui.datasetComboBox.addItem(patientName, dataset_folder)`), and it is written unencrypted to `slicer_neuropacs.config` in the user's Documents folder (default at line 73) and displayed in the order table. On a shared clinical workstation this leaves PHI at rest in a plain file with no access control or warning.
  ```
      def storeNeuropacsOrder(self, patientId, orderId):
          """Associate an orderId with the patient."""
          self.neuropacsOrderMap[orderId] = patientId  # Store the order associated with the dataset
          self.save_config()  # Save the updated map to a file
  ```
  Suggestion: Store only the order ID and a non-identifying label (or a hash), or warn the user that the config file contains patient identifiers and where it is written.
- **haiku** (major, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:244`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L244): storeNeuropacsOrder writes orderId -> patient name (from DICOM PatientName via the dropdown text) to slicer_neuropacs.config in the user's Documents folder (lines 244, 604, 228-231). This persists protected health information in an unencrypted file that is not mentioned to the user, and the file is kept indefinitely after the analysis.
  ```
  self.neuropacsOrderMap[orderId] = patientId  # Store the order associated with the dataset
          self.save_config()  # Save the updated map to a file
  ```
  Suggestion: Store only the neuropacs order ID, or a pseudonymous label, and not the patient name. Document the file and its contents if it must be kept.

### D6. Runtime pip install into Slicer's shared Python environment without user confirmation
partial; category environment; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:222`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L222): Pressing 'Validate' silently installs/upgrades a third-party package into the Slicer Python environment shared by all extensions, with no confirmation prompt and no visibility into the package's declared requirements. If `neuropacs` pins or downgrades packages Slicer bundles (numpy, scipy, SimpleITK, requests, ...) or pulls heavy dependencies, every other extension in that Slicer installation is affected. The transitive dependency set could not be inspected from this repository.
  ```
          if needToInstallNeuropacs:
              print(f"Upgrading neuropacs to version {latest_version}...")
              slicer.util.pip_install(f"neuropacs=={latest_version}")
  ```
  Suggestion: Ask the user before installing, use slicer.util.pip_install only after explicit confirmation, and verify/declare the dependency set (e.g. a requirements file) so bundled-package pins can be reviewed.
- **haiku** (major, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:222`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L222): On API key validation, the module queries PyPI and calls slicer.util.pip_install(f'neuropacs=={latest_version}') with no user prompt (lines 222-224). This changes Slicer's shared Python environment for all modules, and the package's own dependencies are installed without a pin or review. The package is fetched from PyPI at run time rather than declared through the extension build, so the installed version is whatever is latest at that moment.
  ```
  if needToInstallNeuropacs:
              print(f"Upgrading neuropacs to version {latest_version}...")
              slicer.util.pip_install(f"neuropacs=={latest_version}")
  ```
  Suggestion: Ask for confirmation before installing, and document the package and version. Check that its dependencies do not downgrade or bring their own Qt, VTK or torch. Avoid the unbounded PyPI lookup with no timeout (line 211) and handle failure explicitly.

### D7. Uploads may send an entire DICOM storage folder, not the selected series, to a third-party cloud
single; category safety; raised by haiku
- **haiku** (major, medium confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:461`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L461): The dataset path is derived as the parent directory of the first file of the first series of each study (lines 455-461). Slicer's DICOM database typically stores many patients' files in one flat directory, so dirname(first_file) can contain other patients' data. onNeuropacsButton then uploads that whole folder with upload_dataset_from_path (line 590). Unrelated patients' medical images could leave the machine, and the user would not know the scope.
  ```
  dataset_folder = os.path.dirname(first_file_path)
  
  # Add the dataset name and file path to the dropdown
  self.ui.datasetComboBox.addItem(patientName, dataset_folder)
  ```
  Suggestion: Upload only the files of the selected series or study, for example by copying them to a temporary folder or passing an explicit file list. Show the exact upload scope to the user before transmitting.

### D8. Widget adds to self.layout in __init__, before setup() creates it
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, medium confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:76`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L76): load_npcs_file_selector (lines 111-114) does `self.layout.addWidget(parametersCollapsibleButton)`, but in Slicer's ScriptedLoadableModuleWidget `self.layout` is assigned in setup() (`self.layout = self.parent.layout()`), not in __init__. Constructing the widget therefore raises AttributeError before the UI is built, so the module panel would fail to appear. I could not execute Slicer to confirm, but the ordering is inconsistent with the base class contract.
  ```
          self.neuropacsConfigPath = default_path
          #     # self.load_npcs_file_selector(qt.QStandardPaths.writableLocation(qt.QStandardPaths.DocumentsLocation) + "/slicer_neuropacs.config")
          # else:
          #     self.load_npcs_file_selector(last_used_path)
          #     self.neuropacsConfigPath = last_used_path
          self.load_npcs_file_selector(default_path)
  ```
  Suggestion: Move the config-file selector creation into setup() after `ScriptedLoadableModuleWidget.setup(self)` and after the .ui widget is added.
- **haiku** (minor, low confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:81`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L81): __init__ calls load_npcs_file_selector, which adds a collapsible button and form to self.layout (lines 81, 112-114). The layout is normally created in setup(), so this call may fail or add widgets to the wrong place. A second, unused configPathFileSelector is also created here.
  ```
  self.load_npcs_file_selector(default_path)
  ```
  Suggestion: Move widget construction into setup() after ScriptedLoadableModuleWidget.setup(self) and remove the dead code.

### D9. Rating of safety
rating dispute; category safety; raised by deepseek, flash-lite, haiku
Ratings: deepseek blocking, flash-lite ok, haiku concern

### D10. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern

### D11. Rating of packaging
rating dispute; category packaging; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku ok

### D12. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Malformed logging call in the analysis error handler
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified, other lines) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:147`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L147): `logging.error` is called with two positional arguments and no format placeholder, which raises a logging TypeError and hides the real error; the user only sees 'Failed to run analysis.' with no detail.
  ```
              except Exception as e:
                  self.ui.infoLabel.setText("Failed to run analysis.")
                  qt.QApplication.processEvents()
                  logging.error("Failed to run neuropacs analysis: ", str(e))
  ```
  Suggestion: Use `logging.error("Failed to run neuropacs analysis: %s", e)` and surface the message to the user.
- **haiku** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:618`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L618): logging.error("Failed to run neuropacs analysis: ", str(e)) passes an extra positional argument with no format placeholder, so the logging module reports an internal formatting error and the real message is lost. Several handlers (e.g. the validate and delete paths) catch Exception and only log or print, so users see a generic failure with no detail.
  ```
  logging.error("Failed to run neuropacs analysis: ", str(e))
  ```
  Suggestion: Use logging.error("Failed to run neuropacs analysis: %s", e) or an f-string, and show the error to the user with slicer.util.errorDisplay.

### No meaningful automated test
minor; utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:641`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L641): The registered unittest contains no assertions, and NeuropacsScriptedModule/Testing/Python/CMakeLists.txt has its only test line commented out, so the extension's CI provides no functional coverage of the module.
  ```
      def test_NeuropacsScriptedModule1(self):
          """Integration tests"""
  
          self.delayDisplay("Starting the test")
  
          self.delayDisplay("Test passed")
  ```
  Suggestion: Add at least a widget-creation test (which would also catch the self.layout problem) and a config-file round-trip test.
- **haiku** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:646`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L646): NeuropacsScriptedModuleTest.test_NeuropacsScriptedModule1 only calls delayDisplay and asserts nothing. The Testing/Python CMake registration is commented out. The module's logic (config handling, order map, dataset selection) has no automated tests.
  ```
  self.delayDisplay("Test passed")
  ```
  Suggestion: Add unit tests for the config and order-map logic with a mocked neuropacs client, and register them in CMake.

### Report PNG loaded as a Slicer volume
minor; soundness; raised by flash-lite
- **flash-lite** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:291`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L291): When downloading a report in PNG format, the code attempts to load it via slicer.util.loadVolume and display it in the red slice viewer. However, `slicer.util.loadVolume` interprets 2D PNG images (such as biomarker reports) as scalar volumes/architectures, which can cause unexpected volume registration, scaling issues, or clutter the MRML scene with non-imaging report artifacts. While not a security concern, it is a soundness/correctness issue in how reports are rendered.
  ```
      def display_png_in_slicer(self, file_path):
          # Load the PNG as a volume
          success, volume_node = slicer.util.loadVolume(file_path, returnNode=True)
          
          if success:
              # Set up the slice viewer to show the PNG image
  ```
  Suggestion: Use a suitable document or image viewer widget (or save/display appropriately) rather than loading report PNGs into the 3D Slicer volume hierarchy as anatomical volumes.

### Report download uses file_path even when the user cancels the save dialog
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:267`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L267): When the user cancels, file_path is empty and the code still calls display_png_in_slicer('') / display_text_in_slicer('') (lines 282-285), which fails to load and then reports 'downloaded successfully at ' (line 289). The report is also fetched from the server before the user chooses a destination.
  ```
              file_dialog = qt.QFileDialog()
              file_path = file_dialog.getSaveFileName(None, "Save Report", f"neuropacs_{orderId}.{format}")
  
              if file_path:
  ```
  Suggestion: Return early when the dialog is cancelled and only fetch/display after a valid path is chosen.

### Report text is injected into the Slicer main window layout
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:314`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L314): Adding a QTextEdit to the main window's central widget layout modifies Slicer's global UI from a module and can leave a stray widget (or a re-parented layout) behind after the module is closed, affecting the whole application session.
  ```
          main_window = slicer.util.mainWindow()
          central_widget = main_window.centralWidget()
  
          # Create a layout if not already present
          layout = central_widget.layout()
  ```
  Suggestion: Show the report in a module-owned dialog or in the module panel instead of the main window layout.

### Unbound `status` when check_status raises an unexpected error
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified, other lines) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:143`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L143): Any exception other than 'Bucket not found' (network error, expired API key, server error) falls through with `status` undefined, so populateOrderTable raises UnboundLocalError and the whole table refresh fails instead of reporting the problem.
  ```
              try:
                  status = self.npcs.check_status(order)  
              except Exception as e:
                  if ("Bucket not found") in str(e):
                      exp_orders.append(order)
                      continue
  ```
  Suggestion: Handle the general exception case (continue with an error status or re-raise with a user-visible message).
- **haiku** (minor, high confidence, quote verified, other lines) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:147`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L147): If check_status raises an exception other than one containing 'Bucket not found', the except block does nothing and execution continues to use 'status'. That variable is either undefined (NameError, aborting the table refresh) or left over from the previous row (wrong data shown). The error is not reported to the user.
  ```
  except Exception as e:
                  if ("Bucket not found") in str(e):
                      exp_orders.append(order)
                      continue
  
              status_info = self.__extractInfoFromStatus(status)
  ```
  Suggestion: Handle the other exception paths explicitly, for example by logging the error and continuing to the next order, and do not reuse the previous status.

### Unchecked indexing of series/files and only the first series of the first study is offered
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:451`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L451): `series[0]` and `files[0]` raise IndexError for patients/studies with no series or an empty series, aborting the whole dropdown population. Also only the first series of the first study is listed, so for a diffusion MRI study with several series the user cannot choose which series is uploaded, and the uploaded folder is whatever directory the first file happens to live in.
  ```
                  series = dicomDatabase.seriesForStudy(study)
  
                  first_series = series[0]
  
                  files = dicomDatabase.filesForSeries(first_series)
  ```
  Suggestion: Guard empty lists and list series (with descriptions) rather than a single arbitrary series.

### Upload and analysis run synchronously on the GUI thread
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:570`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L570): The DICOM upload (line 590) and status polling in populateOrderTable run on the GUI thread with only a wait cursor and processEvents calls; for a multi-hundred-MB diffusion dataset Slicer will appear frozen and cannot be cancelled, and there is no progress reporting.
  ```
          with slicer.util.tryWithErrorDisplay(_("Failed to run neuropacs analysis."), waitCursor=True):
              try:
              # Get the folder path associated with the selected item in the dropdown
                  selectedFolderPath = self.ui.datasetComboBox.currentData
  ```
  Suggestion: Run the upload in a worker thread (slicer.util.ProgressDialog / qSlicerCLIProgressBar style) and report progress.

### _checkCanNeuropacs references an undefined parameter node
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`NeuropacsScriptedModule/NeuropacsScriptedModule.py:251`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/NeuropacsScriptedModule/NeuropacsScriptedModule.py#L251): `self._parameterNode` is never assigned anywhere in the class (no parameter node is created), so this method raises AttributeError if it is ever connected. It is currently dead code, which also means the module keeps no state in a parameter node as Slicer conventions suggest.
  ```
      def _checkCanNeuropacs(self, caller=None, event=None) -> None:
          """Can neuropacs be pressed""" 
          if self._parameterNode:
  ```
  Suggestion: Remove the method or implement a real parameter node and connect it.

### No statement of regulatory status or privacy policy for the cloud service
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.md:5`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/README.md#L5): The extension advertises a clinical decision-support use (MSAp/PSP differentiation) but the README and module help give no regulatory clearance status, no privacy policy or data-retention statement for the uploaded data, and no model validation information. Users cannot judge whether the service is cleared for clinical use in their jurisdiction.
  ```
  The neuropacs™ system is a software application intended to receive and analyze
  diffusion MRI data from patients aged 40 years and older presenting with Parkinson’s
  disease (PD) symptoms.
  ```
  Suggestion: Add a short section on intended use, regulatory status, data handling/privacy policy link, and any published validation of the model.

### README clone URL points to a different repository
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`README.md:60`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/README.md#L60): The documented clone URL uses the account name 'neuropacman' instead of 'neuropacs', so the local-install instructions fail for users following the README.
  ```
  1. Clone the repository
  
     git clone https://github.com/neuropacman/SlicerNeuropacs
  ```
  Suggestion: Correct the URL to https://github.com/neuropacs/SlicerNeuropacs.

### scm_revision is the branch 'main' rather than a pinned commit
info; soundness; raised by haiku
- **haiku** (info, high confidence, quote verified) [`SlicerNeuropacs.json:6`](https://github.com/neuropacs/SlicerNeuropacs/blob/93925461f8232b1039c271124e5ce78efcaea225/SlicerNeuropacs.json#L6): The catalog entry tracks a moving branch, so the code users get can change without review. Allowed by policy, but the reviewed source is only the commit named in the request.
  ```
  "scm_revision": "main",
  ```
  Suggestion: Pin scm_revision to a reviewed commit hash for future updates.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
The extension is a client for a commercial cloud diagnostic service. The blocking problem is data handling: the module uploads the selected DICOM series from Slicer's DICOM database to a hard-coded third-party AWS endpoint with no de-identification, no consent dialog and no disclosure of what identifiers are sent; the actual upload code lives in a PyPI package that is auto-upgraded to whatever "latest" is at runtime via `slicer.util.pip_install`, so the reviewed code does not determine what leaves the machine. Secondary issues: patient names are written in plaintext to a config file, the widget appears to use `self.layout` before `setup()` (likely failing to load), the Help PDF is not installed by CMake, and several ordinary bugs (unbound `status`, `series[0]`/`files[0]` indexing, use of `file_path` after a cancelled save dialog, GUI-thread uploads). MIT license is present.
Not checked: The `neuropacs` PyPI package (the code that actually uploads data and talks to the AWS endpoint) is not in this repository and could not be inspected; its license, dependencies and payload contents are unknown.; The bundled binary Resources/Docs/neuropacs_instructions.pdf (1.3 MB) could not be read, so any privacy/regulatory statements inside it are unverified.; The AWS API Gateway endpoint https://jdfkdttvlf.execute-api.us-east-1.amazonaws.com/prod could not be probed; the server side, data retention and authentication handling are unknown.; No Slicer installation was available, so the claim that `self.layout` is undefined in __init__ (and the deprecated `returnNode=True` call at line 293) could not be executed/confirmed.; The exact commit 93925461f8232b1039c271124e5ce78efcaea225 was not resolved; the catalog entry selects the moving branch `main`, so the reviewed content is the snapshot provided.
Questions for the author: What exactly is uploaded to https://jdfkdttvlf.execute-api.us-east-1.amazonaws.com/prod — are DICOM identifiers (PatientName, PatientID, dates) included, and is the data de-identified before transmission?; Where is the consent/notice that tells the user identifiable patient data leaves their machine, and what is the service's data retention and privacy policy?; Why is the neuropacs client auto-upgraded to the latest PyPI version at runtime instead of being pinned to a reviewed version?; Which dependencies does the `neuropacs` package declare, and does it pin or downgrade any package Slicer bundles (numpy, scipy, SimpleITK, requests)?; Is Resources/Docs/neuropacs_instructions.pdf intentionally omitted from MODULE_PYTHON_RESOURCES, given that the Help button reads it from the installed module directory?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
SlicerNeuropacs is a well-packaged Slicer extension providing integration with the neuropacs cloud-based Parkinsonism differentiation analysis service. The extension is properly structured, uses standard Slicer APIs, has a clear MIT license, and follows good coding practices. One minor soundness note exists regarding report PNG loading into the volume MRML scene, but overall the extension meets all criteria for approval.
Not checked: Remote AWS API endpoints and neuropacs python package backend behavior.

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
The module is a small, MIT-licensed scripted module with no build dependencies. Its main concern is the data path: selected DICOM folders are uploaded to a third-party cloud endpoint, the upload target is the parent folder of the first file rather than the selected series, and patient names are written to a plaintext config file. At runtime it also pip-installs the neuropacs package from PyPI on button press without a confirmation. Tests are placeholders and there is no disclosure of data transmission in the UI. I would not accept this until the upload scope, privacy disclosure and install behavior are fixed. I could only read the files listed; I did not inspect the neuropacs PyPI package or the remote service.
Not checked: The neuropacs PyPI package and its dependencies were not inspected, so I could not check what it installs or sends.; The remote AWS endpoint and its data-handling terms were not inspected.; The .ui file, the Docs PDF, the example PNG and the CodeQL workflow contents were not read.; I did not verify that scm_revision 'main' resolves, or that the extension builds and loads in Slicer.; The Slicer API behavior for ScriptedLoadableModuleWidget.__init__ and the layout attribute was not verified.
Questions for the author: Does the upload send only the selected series, or the whole DICOM storage folder? Please state the exact scope.; What data does the neuropacs service receive, how long is it retained, and what consent do users give before the first upload?; Why is the patient name stored in slicer_neuropacs.config, and is it needed?; Should the PyPI install require user confirmation, and which neuropacs version is expected to be installed?; Can you add tests that exercise the config and order logic without a live API key?


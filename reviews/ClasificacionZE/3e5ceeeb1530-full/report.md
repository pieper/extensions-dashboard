# AI review: ClasificacionZE

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/juan2812006-arch/SlicerClasificacionZE.git at commit `3e5ceeeb1530e322769e853b1a90407fcc9122ca`
- Context: pull request 2440 to the Extensions Index
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-13T17:04:27Z; cost $1.51

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | blocking |
| environment | unknown | minor | minor |
| packaging | unknown | ok | unknown |
| license | unknown | ok | unknown |
| soundness | unknown | ok | minor |
| utility | unknown | ok | ok |
| **overall** | minor issues | minor issues | needs fixes |

## What each reviewer says the extension does

- **claude**: Slicer module (Spanish UI) that runs a FreeSurfer recon-all-style pipeline on a T1 MRI. It then predicts epileptogenic cortical regions (Destrieux atlas) from sEEG features with a bundled ExtraTrees model, and shows them in 3D with scalp EEG and SEEG electrodes. It is meant for research groups working on epilepsy surgery planning.
- **gemini**: ClasificacionZE is a Spanish-language 3D Slicer extension for epilepsy research that runs a 31-step FreeSurfer cortical reconstruction on a patient's T1 MRI, predicts epileptogenic cortical parcels (Destrieux atlas) from sEEG biomarkers using a pre-trained Extra Trees model, and visualizes the resulting cortical probability map in 3D alongside scalp EEG (10-20) and depth SEEG electrodes.
- **gpt**: ClasificacionZE reconstructs cortical anatomy from a T1 MRI with FreeSurfer and visualizes predicted epileptogenic regions alongside EEG and sEEG electrodes. It is intended for epilepsy researchers using 3D Slicer.

## Disagreements (start here)

### D1. Patient IDs '.' and '..' escape the intended patient directory
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`Visualizacion/Visualizacion.py:74`](https://github.com/juan2812006-arch/SlicerClasificacionZE/blob/3e5ceeeb1530e322769e853b1a90407fcc9122ca/Visualizacion/Visualizacion.py#L74): The form validation at lines 980–988 accepts both '.' and '..', and lines 1696–1698 join the ID to the chosen results folder. '.' targets the results root and '..' its parent rather than a patient subfolder; copying, deletion, FreeSurfer outputs and prediction writes can then affect pre-existing files outside the intended subject directory. The same join is used in the processed-patient workflow.
  ```
  # El ID da nombre a una carpeta y se pasa a FreeSurfer.
  ID_VALIDO = re.compile(r"^[A-Za-z0-9._-]+$")
  ```
  Suggestion: Reject '.' and '..' explicitly, resolve the resulting path, and require it to be a dedicated child of the selected results directory before any write or deletion.
- claude on re-check: **real: yes, minor**: Visualizacion.py:75 `ID_VALIDO = re.compile(r"^[A-Za-z0-9._-]+$")` and the check at 984 do accept '.' and '..'. subjectDir = subjectsDir / subjectId (1643-1646, 1696-1698), so the paths resolve to the results folder or its parent. This is a real validation gap. However, the user picks both the folder and the ID in their own session, and there is no remote or untrusted input. The only files touched are the extension's own named outputs, plus FreeSurfer outputs the user asked for. It is a robustness bug, not a path to harm, so not blocking.
- gpt on re-check: **real: yes, blocking**: Visualizacion/Visualizacion.py:74–75 defines `ID_VALIDO = re.compile(r"^[A-Za-z0-9._-]+$")`, and lines 980–988 reject only empty or nonmatching IDs, so both `.` and `..` pass. Lines 1696–1698 use `subjectDir = subjectsPath / subjectId`; lines 1643–1648 use the same join for processed patients. Thus `.` targets the results root and `..` its parent. Subject copying/deletion at lines 1558–1581 and prediction deletion at Inferencia/inferencia_ml.py:146–154 can affect existing files there. Full processing has a confirmation and sometimes an overwrite warning (Visualizacion.py:1748–1772), but neither prevents targeting the wrong directory. Reject special components and verify containment before writes.
- gemini on re-check: **real: yes, minor**: Checked Visualizacion/Visualizacion.py lines 74-75 (`ID_VALIDO = re.compile(r"^[A-Za-z0-9._-]+$")`), lines 980-988 (form validation checking `ID_VALIDO.match(formulario["subjectId"])`), and lines 1014-1017, 1643-1646, and 1696-1698 (`subjectDir = subjectsPath / subjectId`). The regex indeed matches "." and "..", which resolve to the results root or its parent directory when joined with `Path`. However, `subjectId` is typed by the local user into a GUI text field on their own machine (not untrusted external input), and in the full pipeline `onRunPipeline` displays the resolved `subjectDir` in a confirmation dialog before proceeding. Under the review policy, an edge-case validation omission on a user's own local input is a minor validation bug, not a blocking safety issue.

### D2. Visualizing an existing patient silently deletes or replaces their electrode files
single; category safety; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (blocking, high confidence, quote verified, other lines) [`Visualizacion/Visualizacion.py:91`](https://github.com/juan2812006-arch/SlicerClasificacionZE/blob/3e5ceeeb1530e322769e853b1a90407fcc9122ca/Visualizacion/Visualizacion.py#L91): The processed-patient action calls copiarArchivosSujeto without a confirmation (lines 1598–1649). If either optional electrode input is left empty, lines 1579–1581 unlink an existing EEG or SEEG file in the patient's directory; selecting a different file overwrites the existing copy through shutil.copy2. A user merely visualizing an existing subject can thus permanently lose prior electrode data.
  ```
          """
          Copia características, EEG y SEEG a la carpeta del paciente. Si
          EEG o SEEG no se seleccionaron, borra la copia de una ejecución
          anterior para no mostrar electrodos de otra sesión.
          """
  ```
  Suggestion: Never delete or overwrite existing patient inputs during visualization without explicit file-specific confirmation; use per-run output directories or retain existing inputs when optional fields are blank.
- claude on re-check: **real: yes, minor**: copiarArchivosSujeto (1550-1592) does unlink an existing electrode copy (1579-1581) when the field is empty, and copy2 overwrites it. But these are only the extension's own copies (electrodos/eeg_superficie.csv, seeg_dipolos.tsv) inside the patient folder. The originals the user selected are untouched, and the docstring documents the behavior. Neither the docstring nor the UI asks for confirmation, which is a UX weakness. This is not unintended destruction of user data, so it is minor.
- gpt on re-check: **real: yes, blocking**: Visualizacion/Visualizacion.py:497–518 describes EEG and SEEG as optional and says leaving them empty merely means electrodes are not drawn. The processed-patient handler calls `self.copiarArchivosSujeto(formulario, subjectDir)` at lines 1643–1649 without a destructive-action confirmation. Lines 1558–1561 identify the patient electrode files and lines 1579–1581 execute `elif destino.exists():` followed by `destino.unlink()`. If a different input is selected, lines 1542–1547 call `shutil.copy2(origen, destino)`, replacing the existing copy. The original source may still exist elsewhere, but it need not: a previously selected file may itself be the patient copy. Preserve existing data or explicitly confirm destructive changes.
- gemini on re-check: **real: yes, major**: Checked Visualizacion/Visualizacion.py lines 1550-1592 (`copiarArchivosSujeto`) and lines 1598-1650 (`onVisualizarProcesado`). When `onVisualizarProcesado` runs, it calls `copiarArchivosSujeto(formulario, subjectDir)` without a confirmation prompt. In `copiarArchivosSujeto` (lines 1558-1581), if `formulario["eeg"]` or `formulario["seeg"]` is empty and the corresponding target file (`<subjectDir>/electrodos/eeg_superficie.csv` or `seeg_dipolos.tsv`) exists, `destino.unlink()` deletes that copy, and if a file is selected, `shutil.copy2` overwrites `destino` (unless `origen` and `destino` resolve to the same file, lines 1542-1543). While this is intentional per the docstring (lines 1552-1555) to avoid displaying stale electrodes from a previous session, someone re-running `onVisualizarProcesado` on an existing patient folder without re-selecting the optional electrode files will have the cached copy in `<subjectDir>/electrodos/` deleted without warning. Because this can unexpectedly delete existing files in a pre-processed subject directory when the user only intends to visualize, it is a real concern (major), though usually the original files remain at their source path unless the us

### D3. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (ok, blocking, minor)**
Ratings: claude unknown, gemini ok, gpt blocking
- claude on re-check: **rating ok**: I searched the repo for network calls, eval/exec, pickle and shell=True and found no data exfiltration, servers, or downloaded executables. subprocess calls are used to run FreeSurfer, and the form blocks shell-dangerous characters (973). pip_install at Visualizacion.py:2246 runs only after an explicit consent dialog (2220-2226) and only for missing packages. joblib loads only the bundled model. The D1 and D2 issues are minor bugs, not safety blockers, so I rate safety ok. I did not audit every Pipeline script in depth.
- gpt on re-check: **rating blocking**: Inspected ID validation, processed and new-patient workflows, copying, inference output deletion, and representative pipeline invocation. The concrete unintended data-loss paths in D1 and D2 justify blocking safety: Visualizacion/Visualizacion.py:1579–1581 has `elif destino.exists():` and `destino.unlink()`, while lines 74–75 and 1696–1698 permit `..` to target the results folder's parent. Binary joblib payload contents and the exact repository revision could not be verified using the available text-reading tools; the safety assessment is not a complete audit.
- gemini on re-check: **rating minor**: Checked Visualizacion/Visualizacion.py, Inferencia/inferencia_ml.py, Inferencia/soz_inferencia.py, and Pipeline/input_t1.py. There is no malicious behavior, hidden telemetry, or arbitrary code execution from untrusted sources (the bundled model `Inferencia/soz_extratrees_sEEG_15pacientes.joblib` is part of the repo and loaded locally via `joblib.load` in `Inferencia/soz_inferencia.py:39`, shell characters in paths are checked via `CARACTERES_PELIGROSOS` in `Visualizacion/Visualizacion.py:79,973`, and package installation in `Visualizacion/Visualizacion.py:2246` asks for user confirmation first). However, there are minor/non-blocking safety-related edge cases in file handling: `onVisualizarProcesado` (`Visualizacion/Visualizacion.py:1579-1581, 1648`) silently unlinks existing cached electrode files `<subjectDir>/electrodos/eeg_superficie.csv` and `seeg_dipolos.tsv` when the optional form fields are left blank, and `ID_VALIDO` (`Visualizacion/Visualizacion.py:75`) does not reject `.` or `..`. Thus `minor` is the appropriate rating for safety.


## Findings from some reviewers

### Exact pin `scikit-learn==1.9.1` may fail to resolve on PyPI or conflict with Slicer's environment
minor; environment; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`Inferencia/inferencia_ml.py:23`](https://github.com/juan2812006-arch/SlicerClasificacionZE/blob/3e5ceeeb1530e322769e853b1a90407fcc9122ca/Inferencia/inferencia_ml.py#L23): `Inferencia/inferencia_ml.py` pins `scikit-learn==1.9.1`. As of April 2026, scikit-learn 1.9.1 does not exist on PyPI (and if a different version is already installed in Slicer's shared Python environment, `dependenciasFaltantes()` will attempt to replace it with `1.9.1`, or `pip_install` will fail with `No matching distribution found for scikit-learn==1.9.1`). Additionally, installing an exact pin of `scikit-learn` can trigger upgrades or downgrades of `numpy` or `scipy` that Slicer bundles.
  ```
  VERSION_SKLEARN = "1.9.1"
  
  # distribución de pip -> requisito que se instala si falta.
  DEPENDENCIAS = {
      "pandas": "pandas",
      "joblib": "joblib",
  ```
  Suggestion: Verify the exact scikit-learn version on PyPI (e.g. `1.6.1` or `>=1.5`) or relax the hard `==` pin in `DEPENDENCIAS` (relying on the runtime warning in `soz_inferencia.cargar_modelo` if versions differ) so `pip_install` does not fail or alter Slicer's bundled `numpy`/`scipy`.

### Unnamespaced runtime directories remain at the front of the shared import path
minor; environment; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`Visualizacion/Visualizacion.py:2167`](https://github.com/juan2812006-arch/SlicerClasificacionZE/blob/3e5ceeeb1530e322769e853b1a90407fcc9122ca/Visualizacion/Visualizacion.py#L2167): After a user runs inference, this extension's directory remains first on the process-wide import path, so later imports with the same module names in other extensions can resolve to these files instead. The visualization directory is inserted similarly.
  ```
          inferenciaDirString = str(self.inferenciaDir)
  
          if inferenciaDirString not in sys.path:
  
              sys.path.insert(
                  0,
  ```
  Suggestion: Package helper modules under an extension-specific namespace instead of permanently prepending their directories to sys.path.

### Licensed under PolyForm Noncommercial License 1.0.0 (non-commercial use only)
info; license; raised by gemini
- **gemini** (info, high confidence, quote verified) [`LICENSE.txt:3`](https://github.com/juan2812006-arch/SlicerClasificacionZE/blob/3e5ceeeb1530e322769e853b1a90407fcc9122ca/LICENSE.txt#L3): The extension and its bundled `.joblib` model are licensed under the PolyForm Noncommercial License 1.0.0 (`LICENSE.txt` and `CMakeLists.txt`). This explicitly permits distribution and modification for noncommercial purposes (including by the Slicer Extensions Index and academic/public health institutions), while prohibiting commercial use. Users in commercial settings should be aware of this restriction.
  ```
  # PolyForm Noncommercial License 1.0.0
  
  <https://polyformproject.org/licenses/noncommercial/1.0.0>
  ```
  Suggestion: No change required; the noncommercial restriction is already clearly noted in `CMakeLists.txt`, `README.md`, and `LICENSE.txt`.

### Temporary status directory created by `tempfile.mkdtemp` is not cleaned up after pipeline finishes
info; soundness; raised by gemini
- **gemini** (info, high confidence, quote verified) [`Visualizacion/Visualizacion.py:1883`](https://github.com/juan2812006-arch/SlicerClasificacionZE/blob/3e5ceeeb1530e322769e853b1a90407fcc9122ca/Visualizacion/Visualizacion.py#L1883): In `onRunPipeline`, a temporary directory (`runDir`) is created with `tempfile.mkdtemp` to hold `pipeline_status.txt`, `pipeline_current.txt`, and `pipeline.log`. After `finishPipeline()` copies `pipeline.log` to the subject folder, `runDir` is never removed (`shutil.rmtree`), leaving small temporary directories behind in the system temp folder after each FreeSurfer run.
  ```
          runDir = Path(
              tempfile.mkdtemp(
                  prefix="Visualizacion_epilepsia_"
              )
          )
  ```
  Suggestion: Remove `runDir` with `shutil.rmtree(runDir, ignore_errors=True)` at the end of `finishPipeline` and `cleanup`.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read the CMake files, the pipeline scripts, the inference bridge and the installation, subprocess and sys.path code in Visualizacion.py. I found no malicious behavior, network transmission of data, or startup installs. The pip install of pandas, joblib, scikit-learn==1.9.1 and nibabel only happens after a consent dialog. Shell command injection is mitigated by ID and path validation. The packaging looks sound. Remaining points are non-blocking: scikit-learn is pinned exactly, generic module names are inserted into sys.path, the model comes from only 15 patients with no validation shown, the license is non-commercial, and `scm_revision` is `main`. The extension needs an external FreeSurfer install. Not exhaustively read: the 108 KB Visualizacion.py, the VisualizacionML files and soz_inferencia.py. Overall: minor issues.
Not checked: 
<parameter name="0">Most of Visualizacion.py (about 3,700 lines) was read only through targeted searches and excerpts.
Questions for the author: 
<parameter name="0">What is the training and validation provenance of the 15-patient ExtraTrees model, and may the model and demo data be redistributed under PolyForm Noncommercial?

### Gemini 4 Argon (`google/gemini-4-argon`): minor issues
ClasificacionZE is a well-structured extension for processing T1 MRI with FreeSurfer, predicting epileptogenic zones from sEEG markers, and visualizing cortical regions and EEG/SEEG electrodes in 3D. It meets all three Slicer Extensions Index admission requirements: (1) no safety or security issues were found (shell inputs are sanitized and pip installs require user confirmation); (2) `LICENSE.txt` (PolyForm Noncommercial 1.0.0) explicitly permits redistribution for non-commercial purposes; and (3) the catalog entry and CMake build configuration install all required files. One non-blocking concern was noted: `Inferencia/inferencia_ml.py` pins `scikit-learn==1.9.1`, which may fail to resolve on PyPI.

🟢 Recommend merge
Not checked: Binary contents of Inferencia/soz_extratrees_sEEG_15pacientes.joblib (1.44 MB binary joblib/pickle file; cannot be inspected with text-only tools); Runtime execution of the 31-step FreeSurfer pipeline (requires local FreeSurfer installation and license.txt); PyPI availability of scikit-learn==1.9.1 from Slicer's target Python version (no network/shell access in review environment)
Questions for the author: Was the model trained with a pre-release/nightly build of scikit-learn (`1.9.1`), or is `VERSION_SKLEARN = "1.9.1"` in `Inferencia/inferencia_ml.py` and `Visualizacion/Resources/requirements.txt` a typo (for example for `1.6.1` or `1.5.1`)? If `1.9.1` is not published on PyPI, `slicer.util.pip_install` will fail when users try to install dependencies.

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The processed-patient workflow can silently delete or overwrite existing patient files, and patient IDs of '.' and '..' escape the intended subject subdirectory. These data-loss risks need fixes. The module asks before installing Python dependencies, and documentation describes the research-only intended use and model validation. Review of the bundled executable-deserialization model and packaged license notices remains incomplete; the supplied commit and branch were not independently resolved. 🔴 Do not merge yet: fix the data-loss risks and complete verification of the bundled model and distribution notices.
Not checked: No commands, Slicer build, tests, inference, or FreeSurfer processing were executed.; The source checkout's exact Git revision, the availability of the catalog's main branch, and index CI results could not be independently verified with the available tools.; The binary joblib model was not inspected or deserialized; its executable pickle contents, provenance, and integrity were not independently verified.; The installed extension package was not inspected to confirm that PolyForm terms and the required copyright notice accompany it; Slicer CPack behavior was not available here.; The actual PyPI dependency metadata, FreeSurfer installation and license, and reported model validation results were not independently verified.
Questions for the author: Can you provide a safe, reproducible provenance and integrity verification for the bundled joblib model, including the training/export source?; Can you confirm that the distributed extension package includes the full PolyForm terms or their URL and the required copyright notice?


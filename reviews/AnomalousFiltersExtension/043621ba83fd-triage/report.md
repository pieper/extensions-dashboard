# AI review: AnomalousFiltersExtension

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/CSIM-Toolkits/AnomalousFiltersExtension.git at commit `043621ba83fde1f88b53fc11e5149f23f8752866`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-17T03:26:53Z; cost $0.05

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | ok | ok | ok |
| packaging | minor | ok | minor |
| license | ok | ok | ok |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | minor issues |

## What each reviewer says the extension does

- **deepseek**: Provides four C++/ITK command-line modules (AAD, IAD, AAD for DWI, AAD for EPI/fMRI data) that denoise scalar MRI volumes and diffusion-weighted/EPI 4D data with anisotropic and isotropic anomalous-diffusion filters, exposed to Slicer users through the Filtering category.
- **flash-lite**: AnomalousFiltersExtension is a 3D Slicer C++ extension providing C++ ITK filters and Slicer Execution Model (SEM) CLI modules for anisotropic and isotropic anomalous diffusion filtering (porous media equation / Tsallis statistics) applied to scalar MRI volumes, DWI, EPI data, and DTI datasets.
- **haiku**: Provides four ITK/SlicerExecutionModel command-line filters (Anisotropic and Isotropic Anomalous Diffusion, applied to MRI, EPI fMRI/ASL, and diffusion-weighted volumes) for denoising medical images, aimed at Slicer users in the Filtering category. Source is an Apache-2.0 licensed CMake/C++ project with per-module CLI XML, a shared automatic-conductance calculator, and ExternalData-based tests.

## Disagreements (start here)

### D1. AAD module exposes a 'Homogeneity Level' parameter that is never applied
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`AADImageFilter/AADImageFilter.xml:131`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/AADImageFilter.xml#L131): AADImageFilter.cxx (read in full, 194 lines) never references `homoLevel` and never calls `filter->SetH(...)`, so the value stays at the class default m_H = 0.98 (itkAnisotropicAnomalousDiffusionImageFilter.hxx line 28). A user who moves the slider for the Logistic edge function sees no change in the result, which is misleading for a parameter documented as controlling smoothing of homogeneous regions.
  ```
        <name>homoLevel</name>
        <longflag>--homogeneity</longflag>
        <label>Homogeneity Level</label>
  ```
  Suggestion: Add `filter->SetH(homoLevel);` in AADImageFilter.cxx, or remove the parameter from the XML.

### D2. AADEPIData is hard-wired to 4D input but its test feeds a 3D volume
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`AADEPIData/AADEPIData.cxx:34`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADEPIData/AADEPIData.cxx#L34): The reader is `itk::ImageFileReader<itk::Image<float,4>>` and `numberOfImages = size[3]`, so a 3D input either throws in the reader or yields an undefined volume count. The test (AADEPIData/Testing/Cxx/CMakeLists.txt line 20) passes `CTHeadAxial.nhdr`, a 3D scalar volume, so this test cannot succeed. The XML also never tells the user that a 4D (multi-volume) input is required, so a user selecting a normal T1 volume gets an opaque ITK exception.
  ```
      const unsigned int Dimension = 4;
  ```
  Suggestion: Ship a 4D EPI test volume for this module, and state the 4D input requirement in AADEPIData.xml (or handle 3D input gracefully).

### D3. All four bundled tests pass a --sigma argument that no module XML declares
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`AADImageFilter/Testing/Cxx/CMakeLists.txt:20`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/Testing/Cxx/CMakeLists.txt#L20): The identical line appears in AADImageFilter, IADImageFilter, AADDiffusionWeightedData and AADEPIData Testing/Cxx/CMakeLists.txt. None of the four .xml files defines a `sigma` parameter (AADImageFilter.xml has iterations/q/timeStep/conductance/optFunction/edgeFunction/homoLevel; IADImageFilter.xml has D/iterations/timeStep/q). SlicerExecutionModel's generated PARSE_ARGS rejects unknown long flags, so every test exits with a parse error and the extension's test suite fails on every platform, giving no regression protection at all.
  ```
    --sigma 2.5 DATA{${INPUT}/CTHeadAxial.nhdr,CTHeadAxial.raw.gz} ${TEMP}/${CLP}Test.nhdr
  ```
  Suggestion: Replace `--sigma 2.5` with parameters that actually exist for each module (e.g. `--iterations 1 --anomalousparameter 1.2`), and give each module its own appropriate input/baseline.
- **haiku** (minor, medium confidence, quote verified) [`AADImageFilter/Testing/Cxx/CMakeLists.txt:17`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/Testing/Cxx/CMakeLists.txt#L17): The ExternalData test command passes '--sigma 2.5' to ModuleEntryPoint, but none of the module XML files define a 'sigma' parameter, so the CLI parser will likely reject the argument and the test will fail. Tests for all four modules appear to be copied from a template without adjustment. I did not run the tests, so this is inferred from reading the XML and CMake.
  ```
  --compare DATA{${BASELINE}/${CLP}Test.nhdr,${CLP}Test.raw}
      ${TEMP}/${CLP}Test.nhdr
      ModuleEntryPoint
      --sigma 2.5 DATA{${INPUT}/CTHeadAxial.nhdr,CTHeadAxial.raw.gz} ${TEMP}/${CLP}Test.nhdr
  ```
  Suggestion: Verify the test runs under ctest; if it fails, replace '--sigma 2.5' with a parameter that exists (e.g. '--iterations' / '--conductance') and regenerate the baseline, or drop the stale test. Apply the same fix to the IAD, AADEPIData, and AADDiffusionWeightedData test CMake files.

### D4. DWI module reuses one rescaler for all volumes, so every output volume is the last filtered volume
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`AADDiffusionWeightedData/AADDiffusionWeightedData.cxx:214`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADDiffusionWeightedData/AADDiffusionWeightedData.cxx#L214): The same `rescaler` object is created once per loop iteration but `scalar2vector->SetInput(vol, rescaler->GetOutput())` stores a pointer to that one filter's output image for every `vol`. When `scalar2vector->Update()` runs after the loop, all N inputs resolve to the rescaler's current output, i.e. the last filtered volume. A user filtering a DWI dataset silently gets an output where every gradient volume is a copy of the last one, which destroys the diffusion information while reporting success. The sibling module AADEPIData.cxx handles exactly this case correctly with `aux->DisconnectPipeline();` (lines 147-149), which shows the intended pattern.
  ```
          rescaler->SetInput(filter->GetOutput());
          rescaler->SetOutputMaximum(imgValues->GetMaximum());
          rescaler->SetOutputMinimum(imgValues->GetMinimum());
          rescaler->Update();
  
          scalar2vector->SetInput(vol, rescaler->GetOutput());
  ```
  Suggestion: Call `rescaler->GetOutput()->DisconnectPipeline()` (or allocate a fresh rescaler per volume) before passing the image to `scalar2vector->SetInput(vol, ...)`, as AADEPIData.cxx does.

### D5. DWI module test uses a non-diffusion input and always returns failure
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`AADDiffusionWeightedData/AADDiffusionWeightedData.cxx:131`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADDiffusionWeightedData/AADDiffusionWeightedData.cxx#L131): The test for this module also uses `CTHeadAxial.nhdr`, which has no `DWMRI_b-value`/`DWMRI_gradient` metadata, so the module exits with EXIT_FAILURE before doing any work. The test therefore fails by construction and never exercises the filter.
  ```
      if(!readb0)
      {
          std::cerr << "BValue not specified in header file" << std::endl;
          return EXIT_FAILURE;
      }
  ```
  Suggestion: Provide a small DWI NRRD with DWMRI_b-value and DWMRI_gradient headers as test input and a matching baseline.

### D6. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Clinical-adjacent use cases documented without a research-use disclaimer
minor; utility; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`docs/index.md:35`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/docs/index.md#L35): The documentation markets the filters for downstream diagnostic-adjacent tasks (MS lesion segmentation, tissue classification) but neither README.md nor docs/index.md states that the output is for research use and not validated for clinical decision making. Users may treat the denoised volume as a validated preprocessing step.
  ```
    - **Use Case 3:** Noise reduction as part of image processing pipeline
        
        - Could offer a better segmentation and classification on specific brain image analysis such as in Multiple Sclerosis lesion segmentation
  ```
  Suggestion: Add a short research-use-only / not-for-clinical-diagnosis statement to README.md and docs/index.md.

### Conductance of 0 divides by zero in the edge-weight function
minor; soundness; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`AADImageFilter/itkAnisotropicAnomalousDiffusionImageFilter.hxx:172`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/itkAnisotropicAnomalousDiffusionImageFilter.hxx#L172): `conductance` is declared in AADImageFilter.xml (lines 75-82) as a plain float with no `<constraints>` minimum, so a user can enter 0 (or a negative value). m_Conductance is then used as a divisor, producing inf/NaN that propagate into the output volume and are written to disk without any warning.
  ```
          return  GeneralizedDiffCurve()*exp((-1.0)*pow(static_cast<InputPixelType>(abs((idxValue - centerValue)))/static_cast<InputPixelType>(m_Conductance),  2.0));
  ```
  Suggestion: Add a minimum constraint (e.g. 0.001) to the conductance parameter and/or guard against non-positive conductance in the filter.

### Dead duplicated branch in AADEPIData automatic-conductance handling
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AADEPIData/AADEPIData.cxx:129`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADEPIData/AADEPIData.cxx#L129): Both branches do exactly the same thing, so the q-dependent conductance scaling that the DWI module applies (AADDiffusionWeightedData.cxx lines 201-207) is missing here. Either the branch is a leftover or the intended q-scaling was lost; in the latter case EPI results differ from the documented behaviour.
  ```
              if (q!=1.0) {
                  filter->SetConductance(optKappa->GetKappa());
                  std::cout<<"Optimum kappa value estimate: "<<optKappa->GetKappa()<<std::endl;
              }else {
                  filter->SetConductance(optKappa->GetKappa());
  ```
  Suggestion: Remove the redundant branch or restore the intended q-dependent scaling.

### README describes the modules inconsistently with the extension description and DWI module
minor; utility; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`README.md:3`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/README.md#L3): README says the modules are for scalar MRI volumes and that DWI/DTI support is future work, but the CMake extension description and the AADDiffusionWeightedData module state DWI/DTI is already supported. Users may pick the wrong module or assume DWI support is absent.
  ```
  At the moment, the Modules available are suppose to be used on scalar volumes, mainly MRI strucutral images namely T1 and T2 weighted images. Future developments will add new functionalities in order to attenuate image noise in other imaging modalities, such as diffusion weighted images (DWI and DTI).
  ```
  Suggestion: Align README, docs/index.md, and the CMake EXTENSION_DESCRIPTION on which modalities are supported and state validation status for DWI.

### Uninitialized gradient components if sscanf fails on malformed DWMRI_gradient metadata
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, medium confidence, quote verified) [`AADDiffusionWeightedData/AADDiffusionWeightedData.cxx:101`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADDiffusionWeightedData/AADDiffusionWeightedData.cxx#L101): `x`, `y`, `z` are not initialized and the sscanf return value is ignored. A DWI file with a truncated or differently formatted gradient string yields undefined gradient directions that are then written back into the output NRRD header, silently corrupting the diffusion geometry of the result.
  ```
          double x,y,z;
          itk::ExposeMetaData<std::string> (imgMetaDictionary, *itKey, metaString);
          if (itKey->find("DWMRI_gradient") != std::string::npos)
          {
              std::cout << *itKey << " ---> " << metaString << std::endl;
              sscanf(metaString.c_str(), "%lf %lf %lf\n", &x, &y, &z);
  ```
  Suggestion: Initialize x=y=z=0 and check that sscanf returns 3, reporting an error otherwise.
- **haiku** (info, medium confidence, quote verified) [`AADDiffusionWeightedData/AADDiffusionWeightedData.cxx:106`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADDiffusionWeightedData/AADDiffusionWeightedData.cxx#L106): The gradient parser uses sscanf without checking the return value; malformed DWMRI_gradient metadata leaves x, y, z uninitialized and feeds garbage directions into the reconstruction. Only affects malformed input files, with no safety impact.
  ```
  sscanf(metaString.c_str(), "%lf %lf %lf\n", &x, &y, &z);
              vect3d[0] = x; vect3d[1] = y; vect3d[2] = z;
  ```
  Suggestion: Check sscanf returns 3 and report an error otherwise.

### Unsupported pixel type reported as success without writing output
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`AADImageFilter/AADImageFilter.cxx:180`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/AADImageFilter.cxx#L180): After the switch falls through, `main` returns EXIT_SUCCESS (line 193) even though no output file was produced. The same pattern is in IADImageFilter.cxx (lines 146-150) and AADDiffusionWeightedData.cxx (lines 290-294). Slicer will show the CLI as completed successfully while the output node stays empty, which is confusing rather than an error message.
  ```
          case itk::ImageIOBase::UNKNOWNCOMPONENTTYPE:
          default:
              std::cout << "unknown component type" << std::endl;
              break;
  ```
  Suggestion: Return EXIT_FAILURE (and print to stderr) in the default case.

### CLI XML declares <license>Slicer</license> while the project is Apache-2.0
info; license; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`AADImageFilter/AADImageFilter.xml:8`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/AADImageFilter.xml#L8): All four module XMLs use the generic Slicer CLI placeholder even though the repository LICENSE is Apache 2.0. This is a common Slicer convention and does not restrict distribution, but it is inconsistent with the actual terms shown to users in the module panel.
  ```
      <license>Slicer</license>
  ```
  Suggestion: Use `Apache-2.0` (or the full license name) in the <license> element of each module XML.
- **haiku** (info, high confidence, quote verified) [`AADImageFilter/AADImageFilter.xml:8`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/AADImageFilter.xml#L8): Each CLI XML declares the license as 'Slicer' while the repository LICENSE and source headers are Apache-2.0. This is descriptive metadata only and does not block distribution, but it is inconsistent.
  ```
  <license>Slicer</license>
  ```
  Suggestion: Change the per-module <license> to Apache-2.0 (or the license actually intended) to match LICENSE.

### Catalog pins a moving branch rather than a commit
info; packaging; raised by haiku; **quote not found in source**
- **haiku** (info, medium confidence, quote file not found) [`AnomalousFiltersExtension.json:1`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AnomalousFiltersExtension.json#L1): scm_revision is 'main', so the built code can change without a catalog update. This is permitted by index policy but means the reviewed source cannot be tied to a fixed revision; I did not resolve the branch to a commit.
  ```
  "scm_revision": "main",
  ```
  Suggestion: Consider pinning scm_revision to a reviewed commit hash for reproducible builds.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Pure C++/ITK CLI extension: no Python, no network, no downloads, no telemetry, no environment changes — safety and environment look clean, and Apache-2.0 licensing is clear. Packaging is mechanically usable (all four modules are added in CMakeLists.txt, ExternalData stubs are tiny, no EXTENSION_DEPENDS needed since build_dependencies is empty). The main problems are correctness: the DWI module reuses one rescaler for every volume so all output volumes end up identical, the AAD module's "Homogeneity Level" parameter is never applied, and all four bundled tests pass a `--sigma` argument that no XML defines (and feed 3D non-DWI data to 4D/DWI-only modules), so the tests cannot pass. Non-blocking per index policy, but should be fixed.
Not checked: Could not build the extension or run its tests; the test failures reported are inferred from reading the CMakeLists.txt and XML parameter definitions, not from an actual build log.; Could not resolve the ExternalData .md5 stubs (AADImageFilter/Data/Input/CTHeadAxial.nhdr.md5 etc.) to their actual content, so the provenance and license of the test data (presumably ITK/Slicer CT head data) are unverified.; The catalog entry pins scm_revision to the branch 'main'; the reviewed snapshot is the provided commit 043621ba83fde1f88b53fc11e5149f23f8752866, but I could not verify that this is the current tip of main or inspect any later commits.; Did not inspect the binary PNG assets (AnomalousFiltersExtension.png, docs/assets/*.png) beyond their sizes.; Did not verify whether the four duplicated copies of itkAnisotropicAnomalousDiffusionImageFilter.hxx / itkAutomaticConductanceImageCalculator.hxx compile against the current Slicer ITK version (e.g. ITK_DELETE_FUNCTION and DynamicMultiThreadingOff deprecations).
Questions for the author: AADDiffusionWeightedData.cxx passes `rescaler->GetOutput()` to `scalar2vector->SetInput(vol, ...)` for every volume without disconnecting the pipeline (unlike AADEPIData.cxx). Is the resulting all-volumes-identical output a known bug?; All four Testing/Cxx/CMakeLists.txt pass `--sigma 2.5`, but no module XML defines a sigma parameter. Was this copied from a template and never updated?; AADImageFilter.xml exposes `homoLevel` (--homogeneity) but AADImageFilter.cxx never calls SetH. Is the parameter intentionally inert?; AADEPIData requires 4D input (Dimension = 4) but its test and XML documentation use a 3D volume. Should the module reject 3D input with a clear message, or support it?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
AnomalousFiltersExtension is a well-structured C++ Slicer extension that implements anisotropic and isotropic anomalous diffusion filtering (porous media equation) for medical images through Slicer Execution Model (SEM) CLI modules. Static inspection of the repository reveals clean CMake configuration, proper use of ITK filters, standard exception handling, a clear Apache 2.0 license, and no unsafe or malicious behaviors. The catalog entry is mechanically valid. Recommend merge.
Not checked: Exact compilation and runtime execution inside 3D Slicer environment (beyond static code inspection and review of CMake build configuration/ITK filters).

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): minor issues
I found no malicious, network, or environment-changing behavior. The code is pure ITK CLI filtering with file reads and writes only to user-chosen paths, no pip installs, no Python, and no downloads at runtime. The main concerns are soundness and documentation: the CLI test invocation passes a `--sigma` argument that the module XML does not define, the README contradicts the extension description about DWI support, and the module XML license tag says "Slicer" while the repo is Apache-2.0. I did not compile or run anything; the review covers the CMake files, CLI XMLs, and the main .cxx files, not the full .hxx implementations or test data.
Not checked: Did not read the full .hxx implementations (AADImageFilter, AADDiffusionWeightedData, AADEPIData, IADImageFilter) beyond the first 60 lines of one file, so numerical correctness and loop bounds were not verified.; Did not read the Testing/Cxx *Test.cxx files other than the test main stubs, nor the Data/Input and Data/Baseline content (.sha512 or ExternalData hashes), so test data provenance and whether tests pass were not verified.; Did not resolve scm_url or scm_revision; the exact commit reviewed is unknown.; Did not read docs/index.md, mkdocs.yml, .github/FUNDING.yml, or .readthedocs.yaml beyond what was included.; Did not verify the ITK component list (e.g. whether itkDiffusionTensor3DReconstructionImageFilter needs an extra ITK module in AADDiffusionWeightedData) or compile anything.


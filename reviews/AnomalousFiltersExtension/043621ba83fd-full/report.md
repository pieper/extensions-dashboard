# AI review: AnomalousFiltersExtension

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/CSIM-Toolkits/AnomalousFiltersExtension.git at commit `043621ba83fde1f88b53fc11e5149f23f8752866`
- Context: Extensions Index catalog entry
- Panel: full (Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`), GPT-6.1 Terra (`openai/gpt-6.1-terra`), Gemini 4 Argon (`google/gemini-4-argon`))
- Reviewed 2026-11-18T03:14:52Z; cost $0.75

## Overall

| Criterion | claude | gemini | gpt |
|---|---|---|---|
| safety | unknown | ok | concern |
| environment | unknown | ok | ok |
| packaging | unknown | ok | unknown |
| license | unknown | ok | ok |
| soundness | unknown | minor | concern |
| utility | unknown | ok | minor |
| **overall** | minor issues | minor issues | needs fixes |

## What each reviewer says the extension does

- **claude**: A set of four Slicer C++ CLI modules (AAD image filter, IAD image filter, AAD for diffusion-weighted data, AAD for 4D EPI data). They denoise MRI volumes with numerical solutions of Tsallis anomalous (porous-media) diffusion.
- **gemini**: AnomalousFiltersExtension provides four C++ ITK-based CLI modules for denoising medical images (particularly structural MRI, EPI/fMRI, and DWI/DTI volumes) using isotropic and anisotropic anomalous diffusion filters based on the porous media (Tsallis Fokker-Planck) equation. It is intended for researchers and neuroimaging users performing noise attenuation as a pre-processing step in 3D Slicer.
- **gpt**: This extension provides isotropic and anisotropic anomalous-diffusion filters for denoising MRI volumes, including diffusion-weighted and EPI data. It is intended for Slicer users preparing images for visualization and analysis.

## Disagreements (start here)

### D1. DWI gradient metadata can drive an out-of-bounds image read
single; category safety; raised by gpt; outcome after cross-examination: **real, minor (3 of 3)**
- **gpt** (blocking, high confidence, quote verified) [`AADDiffusionWeightedData/AADDiffusionWeightedData.cxx:157`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADDiffusionWeightedData/AADDiffusionWeightedData.cxx#L157): The loop's i is bounded by numberOfImages, counted from DWMRI_gradient metadata at lines 99–109, rather than by the VectorImage component count. A malformed or untrusted NRRD with more gradient keys than actual components makes this access cross pixel boundaries and eventually the image allocation, causing undefined behavior, potentially a crash or disclosure of process memory through derived output.
  ```
          while (!it.IsAtEnd())
          {
              it.Set(dwiit.Get()[i]);
              ++it;
              ++dwiit;
  ```
  Suggestion: Before indexing, require an exact match between valid, sequential gradient entries and img->GetNumberOfComponentsPerPixel(), and reject malformed gradient values; add malformed-input tests.
- claude on re-check: **real: yes, minor**: AADDiffusionWeightedData.cxx:99-109 counts numberOfImages from DWMRI_gradient keys, and lines 147-162 index `dwiit.Get()[i]` with no check against img->GetNumberOfComponentsPerPixel(). A malformed NRRD with more gradient keys than components would read out of bounds. Impact is a crash or garbage in the output file the user asked for. The input is a local file the user chose, and there is no network path or privilege boundary. It is an input-validation bug, not a blocking safety issue.
- gpt on re-check: **real: yes, blocking**: AADDiffusionWeightedData/AADDiffusionWeightedData.cxx:99-109 counts keys containing "DWMRI_gradient" with "++numberOfImages;"; lines 146-159 loop on that count and read "it.Set(dwiit.Get()[i]);" without checking the vector component count. If the ITK reader accepts a NRRD with excess gradient keys, this indexes beyond the pixel vector and, for the final pixel, potentially beyond the image buffer: undefined behavior and a concrete memory-safety risk. Validate the count before splitting. I could not run a crafted input or inspect the specific ITK reader/indexing implementation; a crash or memory disclosure is possible, not demonstrated, and the later pipeline cycle may prevent output.
- gemini on re-check: **real: yes, minor**: In AADDiffusionWeightedData/AADDiffusionWeightedData.cxx lines 99-109, numberOfImages is incremented for every metadata key matching "DWMRI_gradient". At lines 147-162, the loop runs for i < numberOfImages and indexes dwiit.Get()[i] without checking img->GetNumberOfComponentsPerPixel(). However, this is an ordinary missing-bounds-check bug on local file metadata rather than malicious behavior or an exploitable security vulnerability under the rubric, so its severity is minor (and belongs under soundness rather than blocking safety).

### D2. DWI and EPI filters create a cyclic ITK pipeline
single; category soundness; raised by gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gpt** (major, high confidence, quote verified) [`AADDiffusionWeightedData/AADDiffusionWeightedData.cxx:214`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADDiffusionWeightedData/AADDiffusionWeightedData.cxx#L214): The same filter was connected to rescaler->GetOutput() at line 186. Reconnecting that rescaler to the filter output creates a cycle, so updating it can recurse rather than produce an output. AADEPIData/AADEPIData.cxx lines 114 and 142–145 constructs the same cycle.
  ```
          rescaler->SetInput(filter->GetOutput());
          rescaler->SetOutputMaximum(imgValues->GetMaximum());
          rescaler->SetOutputMinimum(imgValues->GetMinimum());
          rescaler->Update();
  ```
  Suggestion: Use separate input and output rescalers, or disconnect a materialized intermediate image from its pipeline, and test both modules with representative 4D data.
- claude on re-check: **real: yes, minor**: AADDiffusionWeightedData.cxx:186 sets filter input to rescaler->GetOutput(). Lines 214-217 then call rescaler->SetInput(filter->GetOutput()), which makes a rescaler->filter->rescaler cycle. AADEPIData.cxx:114 and 142-145 do the same. The cycle is real. I could not confirm the consequence, because ITK's pipeline has loop handling and I cannot run it. The likely effect is a redundant re-execution or odd rescaling, not a definite failure. It is a bad pattern that should be fixed with a second rescaler, but I have no evidence that it breaks.
- gpt on re-check: **real: yes, major**: AADDiffusionWeightedData/AADDiffusionWeightedData.cxx:186 connects "filter->SetInput(rescaler->GetOutput());", and lines 214-217 reconnect the same rescaler with "rescaler->SetInput(filter->GetOutput());" followed by "rescaler->Update();". AADEPIData/AADEPIData.cxx:114,142-145 does the same; its DisconnectPipeline at 147-148 is after the update. The resulting cyclic graph is a serious functional defect affecting both modules. Infinite recursion versus another ITK failure mode was not runtime-verified; use a second rescaler or disconnect the first output before reconnecting. This is a non-blocking correctness issue under the index admission policy.
- gemini on re-check: **real: yes, major**: In AADDiffusionWeightedData/AADDiffusionWeightedData.cxx lines 180-217 and AADEPIData/AADEPIData.cxx lines 108-145, the same RescaleIntensityImageFilter instance (`rescaler`) has its output connected as the input to `filter` (`filter->SetInput(rescaler->GetOutput())`), and then after `filter->Update()`, `rescaler->SetInput(filter->GetOutput())` is called followed by `rescaler->Update()`. Because `filter`'s input is still `rescaler->GetOutput()`, this forms a cycle in the ITK pipeline (`rescaler -> filter -> rescaler`), which causes infinite recursion in `PropagateRequestedRegion` / `UpdateOutputInformation` when `rescaler->Update()` is invoked. This is a major soundness bug.

### D3. Parallel iterations read output while other threads write it
partial; category soundness; raised by gemini, gpt; outcome after cross-examination: **real, major (3 of 3)**
- **gemini** (minor, high confidence, quote verified) [`AADImageFilter/itkAnisotropicAnomalousDiffusionImageFilter.hxx:113`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/itkAnisotropicAnomalousDiffusionImageFilter.hxx#L113): In `AnisotropicAnomalousDiffusionImageFilter` (across `AADImageFilter`, `AADEPIData`, and `AADDiffusionWeightedData`) and `IsotropicAnomalousDiffusionImageFilter`, the filter implements `ThreadedGenerateData`, meaning ITK splits the output image into subregions across worker threads. Inside `ThreadedGenerateData`, the filter performs multiple diffusion iterations (`m_Iterations`) copying `aux` back to `output` within each thread's subregion without inter-thread synchronization between iterations, and reads boundary neighbors from adjacent thread regions concurrently while other threads are writing to `output`. This causes a data race along thread region boundaries and mathematically inconsistent multi-iteration results when `m_Iterations > 1` and multiple threads are used.
  ```
          for(int i=0; i<m_Iterations; i++){
              auxIt.GoToBegin();
              laplaceIt.GoToBegin();
  ```
  Suggestion: Either override `GenerateData()` (single-threaded outer iteration loop invoking a single-step `ThreadedGenerateData` or `FiniteDifferenceImageFilter` pattern) or set `this->SetNumberOfWorkUnits(1)` in the constructor so that multi-iteration updates are synchronized across the whole image.
- **gpt** (major, high confidence, quote verified) [`AADImageFilter/itkAnisotropicAnomalousDiffusionImageFilter.hxx:105`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/itkAnisotropicAnomalousDiffusionImageFilter.hxx#L105): ThreadedGenerateData runs on separate regions but the neighborhood iterator reads the shared output across region boundaries while each thread initializes and later overwrites its region at lines 97–103 and 144–150. With multiple work units, the result can depend on scheduling and contain seams or inconsistent values; the other filter implementations use the same pattern.
  ```
      typedef itk::LaplacianOperator< OutputPixelType , OutputImageDimension > LaplacianOperatorType;
      LaplacianOperatorType laplaceOp;
      itk::Size<OutputImageDimension> radius;
      radius.Fill(1);
      laplaceOp.CreateToRadius(radius);
      NeighborIteratorType      laplaceIt(laplaceOp.GetRadius(), output,  region);
  ```
  Suggestion: Use synchronized full-image iteration buffers, or restrict the filter to one work unit until a thread-safe implementation is available. Compare outputs across thread counts.
- claude on re-check: **real: yes, major**: itkAnisotropicAnomalousDiffusionImageFilter.hxx:32 calls DynamicMultiThreadingOff and line 38 implements ThreadedGenerateData(region). Lines 97-103 copy input into the shared output within the thread's region. Line 110 builds a neighborhood iterator over the shared `output`, which reads across region borders. Lines 113-150 run all iterations inside each thread and write back to output. Nothing synchronizes threads between iterations or before reads, so boundary pixels can be uninitialized or stale. The result depends on thread scheduling and can show seams. It is a real correctness bug, but not a safety issue.
- gpt on re-check: **real: yes, major**: AADImageFilter/itkAnisotropicAnomalousDiffusionImageFilter.hxx:32,38 uses legacy threaded generation; lines 97-110 initialize the shared output per region and create a neighborhood iterator on it, lines 122-124 read neighbors, and lines 144-150 copy each worker's results back without an iteration barrier: "outputIt.Set(auxIt.Get());". Other workers can still initialize or read adjacent regions, producing data races and schedule-dependent image values even on the first iteration. IADImageFilter/itkIsotropicAnomalousDiffusionImageFilter.hxx:28-34,56-68,71-100 and both DWI/EPI filter copies show the same pattern. This affects core results when multiple work units are used; it is a non-blocking correctness issue under the admission policy. Runtime behavior was not tested.
- gemini on re-check: **real: yes, major**: In AADImageFilter/itkAnisotropicAnomalousDiffusionImageFilter.hxx (lines 38, 89-103, 110-151), AADDiffusionWeightedData/itkAnisotropicAnomalousDiffusionImageFilter.hxx (lines 33, 48-62, 69-110), AADEPIData/itkAnisotropicAnomalousDiffusionImageFilter.hxx, and IADImageFilter/itkIsotropicAnomalousDiffusionImageFilter.hxx (lines 34, 49-62, 68-101), the filters implement `ThreadedGenerateData` over thread subregions while performing `m_Iterations` diffusion steps in a loop. Each thread reads neighbor pixels from the shared `output` image via `laplaceIt` (which crosses subregion boundaries into adjacent threads' regions) while other threads concurrently initialize and overwrite their regions of `output` without any barrier synchronization between iterations. Furthermore, in AADImageFilter/itkAnisotropicAnomalousDiffusionImageFilter.hxx line 83, `maxGrad` (a member variable) is written unsynchronized across threads. This causes data races and thread-scheduling-dependent artifacts along subregion boundaries, making it a major soundness issue.

### D4. Rating of safety
rating dispute; category safety; raised by claude, gemini, gpt; outcome after cross-examination: **still disputed (blocking, ok)**
Ratings: claude unknown, gemini ok, gpt concern
- claude on re-check: **real: no, info**: I searched for network, subprocess, eval/exec, pip_install and download. The only URLs are metadata, docs and icons in CMakeLists.txt and README. The code is C++ ITK CLI filters that read and write local files. There is no telemetry, no downloading, no secrets, and no obfuscation. The LICENSE is Apache 2.0. The only memory-safety issue is the malformed-NRRD index (D1), which is an ordinary bug. I rate safety ok.
- gpt on re-check: **rating blocking**: The D1 unchecked metadata-derived component index is a concrete memory-safety concern, not merely an ordinary imaging correctness bug: AADDiffusionWeightedData/AADDiffusionWeightedData.cxx:103-109 counts gradient metadata and lines 146-159 use "it.Set(dwiit.Get()[i]);" without checking actual component count. This warrants a blocking safety rating pending a bounds check; successful exploitation or disclosure was not demonstrated. I also inspected the four CLI entry points, filter implementations, top-level and module CMake files, and repository-wide searches for network, execution and deletion APIs. I could not run the extension, verify behavior of the external ITK implementation, or independently resolve the supplied commit.
- gemini on re-check: **rating ok**: I inspected the C++ CLI modules and headers across the repository (AADDiffusionWeightedData, AADEPIData, AADImageFilter, IADImageFilter). There is no malicious or concealed behavior, no network communication, no telemetry, no command injection or unsafe deserialization, and no environment manipulation. The out-of-bounds read in D1 if a NRRD header has more DWMRI_gradient keys than pixel components is an ordinary input-validation bug on a local image file, not a safety concern under the rubric.


## Findings from some reviewers

### CLI parameter `homoLevel` is never passed to the filter in AADImageFilter.cxx
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`AADImageFilter/AADImageFilter.cxx:97`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/AADImageFilter.cxx#L97): `AADImageFilter.xml` defines the `homoLevel` (`--homogeneity`) parameter for the Logistic edge function, and `itkAnisotropicAnomalousDiffusionImageFilter.h` defines `itkSetMacro(H, float)`, but `AADImageFilter.cxx` never passes `homoLevel` to `filter->SetH(homoLevel)`. Consequently, changes to "Homogeneity Level" in the GUI have no effect (it always uses the default `0.98`).
  ```
      //Selecting the edge function
      if (edgeFunction=="Exponential") {
          filter->SetEdgeFunction(FilterType::EXPONENTIAL);
      }else if (edgeFunction=="Fractional") {
          filter->SetEdgeFunction(FilterType::FRACTIONAL);
      }else if (edgeFunction=="Logistic") {
  ```
  Suggestion: Call `filter->SetH(homoLevel);` when configuring `filter` in `AADImageFilter.cxx`.

### CTest configurations pass non-existent `--sigma` flag from CLI template
minor; utility; raised by gemini, gpt
- **gemini** (minor, high confidence, quote verified) [`AADImageFilter/Testing/Cxx/CMakeLists.txt:16`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/Testing/Cxx/CMakeLists.txt#L16): All four module `Testing/Cxx/CMakeLists.txt` files retain the template test invocation passing `--sigma 2.5`, which is not a valid CLI flag for any of the four modules (`AADImageFilter`, `IADImageFilter`, `AADEPIData`, `AADDiffusionWeightedData`). Running CTest will fail on argument parsing.
  ```
    ExternalData_add_test(${CLP}Data NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
      --compare DATA{${BASELINE}/${CLP}Test.nhdr,${CLP}Test.raw}
      ${TEMP}/${CLP}Test.nhdr
      ModuleEntryPoint
      --sigma 2.5 DATA{${INPUT}/CTHeadAxial.nhdr,CTHeadAxial.raw.gz} ${TEMP}/${CLP}Test.nhdr
      )
  ```
  Suggestion: Update the test command arguments in each module's `Testing/Cxx/CMakeLists.txt` to pass flags defined in the respective module XML (and appropriate 4D/DWI test inputs for `AADEPIData` and `AADDiffusionWeightedData`).
- **gpt** (minor, high confidence, quote verified) [`AADImageFilter/Testing/Cxx/CMakeLists.txt:16`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/Testing/Cxx/CMakeLists.txt#L16): AADImageFilter.xml does not declare --sigma, so the generated CLI parser cannot accept this test invocation. The same test command is copied to the other modules, and the 3D CT fixture is not representative of the DWI and EPI inputs.
  ```
  ExternalData_add_test(${CLP}Data NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
    --compare DATA{${BASELINE}/${CLP}Test.nhdr,${CLP}Test.raw}
    ${TEMP}/${CLP}Test.nhdr
    ModuleEntryPoint
    --sigma 2.5 DATA{${INPUT}/CTHeadAxial.nhdr,CTHeadAxial.raw.gz} ${TEMP}/${CLP}Test.nhdr
  ```
  Suggestion: Replace the copied invocation with valid module-specific arguments and fixtures, and execute the tests in CI.

### Histogram lowerBound and upperBound sized to binsPerDimension instead of MeasurementVectorSize
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`AADImageFilter/itkAutomaticConductanceImageCalculator.hxx:94`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/itkAutomaticConductanceImageCalculator.hxx#L94): In `AutomaticConductanceImageCalculator::ComputeCanny`, `lowerBound` and `upperBound` are initialized with size `binsPerDimension` (256) instead of `MeasurementVectorSize` (1), whereas `size` has length `MeasurementVectorSize` (1). In ITK's `ImageToHistogramFilter`, the measurement vector length must match the number of components (1 for scalar images).
  ```
      typedef itk::Statistics::ImageToHistogramFilter< TInputImage >        ImageToHistogramFilterType;
      typename ImageToHistogramFilterType::HistogramType::MeasurementVectorType     lowerBound(binsPerDimension);
      lowerBound.Fill(0);
  
      typename ImageToHistogramFilterType::HistogramType::MeasurementVectorType     upperBound(binsPerDimension);
  ```
  Suggestion: Initialize `lowerBound(MeasurementVectorSize)` and `upperBound(MeasurementVectorSize)` instead of `binsPerDimension`.

### Homogeneity control is not passed to the anisotropic filter
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified, other lines) [`AADImageFilter/AADImageFilter.xml:45`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/AADImageFilter.xml#L45): The CLI advertises this parameter, but AADImageFilter.cxx never calls the filter's SetH with homoLevel. Users selecting the logistic edge function get the hard-coded default regardless of their chosen homogeneity level.
  ```
      <double>
        <name>homoLevel</name>
        <longflag>--homogeneity</longflag>
        <label>Homogeneity Level</label>
        <description><![CDATA[A double value that regulates how much the logistic curve will smooth the non-edge structures in the image. Value close to 1.0 will strongly smooth those homogenous ares in the image, which, on the other hand, values close to 0.5 will flat the contrast of the image (i.e. vanishs the image contrast levels)]]></description>
        <default>0.98</default>
  ```
  Suggestion: Pass homoLevel to filter->SetH and test that changing it affects the logistic result.

### Integer images are quantized before the original intensity range is restored
minor; soundness; raised by gpt
- **gpt** (minor, high confidence, quote verified) [`AADImageFilter/AADImageFilter.cxx:118`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/AADImageFilter.cxx#L118): The filter operates on values rescaled to 0–255, but lines 110–111 cast those floating-point results to the original output type before this rescaling. For integer inputs, fractional values are discarded before expansion to the original range, reducing output precision; IADImageFilter uses the same ordering.
  ```
      typename RescalerOutputFilterType::Pointer output_rescaler = RescalerOutputFilterType::New();
      output_rescaler->SetInput(cast->GetOutput());
      output_rescaler->SetOutputMinimum(imgValues->GetMinimum());
      output_rescaler->SetOutputMaximum(imgValues->GetMaximum());
  ```
  Suggestion: Restore the original range in floating point and cast only as the final output step.

### Unconstrained conductance and regularization factor allow division by zero
minor; soundness; raised by gemini
- **gemini** (minor, high confidence, quote verified) [`AADImageFilter/AADImageFilter.cxx:88`](https://github.com/CSIM-Toolkits/AnomalousFiltersExtension/blob/043621ba83fde1f88b53fc11e5149f23f8752866/AADImageFilter/AADImageFilter.cxx#L88): In `AADImageFilter.xml`, `conductance` and `kappaRegFactor` have no `<constraints>` preventing `0.0`. In `AADImageFilter.cxx`, dividing by `kappaRegFactor` when it is `0` or setting `conductance` to `0` results in division by zero in `EdgeWeightedController` (`.../ static_cast<InputPixelType>(m_Conductance)`).
  ```
          if (useConductanceRegularization) {
              filter->SetConductance(optKappa->GetKappa()/kappaRegFactor);
          }
  ```
  Suggestion: Add positive minimum constraints in the XML files for `conductance` and `kappaRegFactor`, and guard against zero in the C++ code.


## Reviewer summaries

### Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`): minor issues
I read the CMake files, all four CLI sources and XML descriptors, the ITK filter headers and implementations, and the README and LICENSE. I found no network access, no Python and no package installs. The only file I/O is reading the input volume and writing the output volume. The Apache-2.0 license is clear. The catalog entry is valid but pins `main`, a moving branch, instead of a commit. Several minor correctness problems affect usability: a silent success on unknown pixel types, a test command with a nonexistent `--sigma` flag, and 2D neighbor indices applied to 3D data. Nothing here blocks admission. Recommend merge.
Not checked: 
<parameter name="item">AADDiffusionWeightedData/itkAnisotropicAnomalousDiffusionImageFilter.hxx (not read; same as the AADEPIData version by size)

### Gemini 4 Argon (`google/gemini-4-argon`): minor issues
AnomalousFiltersExtension is a C++ CLI extension providing four ITK-based anomalous diffusion denoising filters for structural MRI, EPI, and DWI data. It is licensed under Apache 2.0, has no external dependencies beyond Slicer/ITK, does not modify the Python environment, and poses no security or safety concerns. Several non-blocking soundness and testing issues were noted (such as performing multiple iterations inside `ThreadedGenerateData` without thread synchronization, `homoLevel` not being wired up in `AADImageFilter.cxx`, and unadapted `--sigma` flags in the CTest files).

🟢 Recommend merge
Not checked: Build and runtime execution of the C++ CLI modules against Slicer superbuild; ExternalData test payloads referenced by .md5 files
Questions for the author: In `AADImageFilter.cxx`, was `homoLevel` (`--homogeneity`) intended to be passed to `filter->SetH(homoLevel)`?

### GPT-6.1 Terra (`openai/gpt-6.1-terra`): needs fixes
The inspected C++ modules contain an unchecked diffusion-metadata-derived vector index, which can read outside the input buffer. Separate non-blocking correctness issues include a cyclic ITK pipeline, unsynchronized threaded iterations, integer precision loss, and invalid test arguments. The source snapshot is attributed to commit 043621ba83fde1f88b53fc11e5149f23f8752866, but the catalog's moving main branch and repository access could not be independently resolved. 🔴 Do not merge yet: fix the out-of-bounds read and verify the catalog source revision and build.
Not checked: Could not independently access the remote repository or resolve the catalog's main branch to the supplied commit; the inspected snapshot is attributed to 043621ba83fde1f88b53fc11e5149f23f8752866 by the supplied context.; Could not run Slicer, compile the extension, execute its tests, or inspect CI results.; Could not inspect the contents, provenance, or distribution terms of the externally referenced test-data blobs.; No previous catalog entry, reviewed baseline, or submission checklist was available.


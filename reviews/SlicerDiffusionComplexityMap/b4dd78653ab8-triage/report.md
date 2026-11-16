# AI review: SlicerDiffusionComplexityMap

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap.git at commit `b4dd78653ab80be20a0d3bec7334ad641d277d25`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T02:51:13Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | ok | ok | ok |
| environment | ok | ok | ok |
| packaging | minor | ok | minor |
| license | ok | ok | concern |
| soundness | concern | ok | concern |
| utility | minor | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: A C++ Slicer CLI module that computes a "Diffusion Complexity" (LMC statistical-complexity) scalar map from a DWI/DTI NRRD sequence, for neuroimaging researchers who want a complement to FA/ADC maps.
- **flash-lite**: SlicerDiffusionComplexityMap is a 3D Slicer extension that provides an ITK-based C++ CLI module to calculate Diffusion Complexity (DC) maps from diffusion-weighted imaging (DWI) sequences using statistical complexity metrics.
- **haiku**: Provides a Slicer CLI module (Diffusion > Quantify) that computes a Diffusion Complexity map (LMC-based, with Euclidean/Wootters/Kullback-Leibler/Jensen disequilibrium options and a Tsallis-style q parameter) from a DWI NRRD sequence and a brain mask. It is aimed at diffusion MRI researchers who want a complexity-based alternative to FA/ADC maps.

## Disagreements (start here)

### D1. CTest case is a leftover template and passes arguments the module does not accept
partial; category utility; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`DiffusionComplexityMap/Testing/Cxx/CMakeLists.txt:24`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/Testing/Cxx/CMakeLists.txt#L24): DiffusionComplexityMap.xml defines no 'sigma' parameter, so the CLI parser rejects '--sigma 2.5' and the test fails immediately; additionally the input is a CT head volume with no DWMRI_gradient/DWMRI_b-value metadata, so even without the flag the filter would find zero gradients and fail. The extension therefore has no working automated verification of its output.
  ```
    ModuleEntryPoint
    --sigma 2.5 DATA{${INPUT}/CTHeadAxial.nhdr,CTHeadAxial.raw.gz} ${TEMP}/${CLP}Test.nrrd
  ```
  Suggestion: Replace the test invocation with the real parameters (--diseq/--qvalue/--numBins) and a small DWI NRRD with proper DWMRI metadata, and regenerate the baseline.
- **haiku** (major, high confidence, quote verified) [`DiffusionComplexityMap/Testing/Cxx/CMakeLists.txt:21`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/Testing/Cxx/CMakeLists.txt#L21): The test runs DiffusionComplexityMapTest with '--sigma 2.5' and a CT head image (CTHeadAxial). The module has no --sigma parameter, and the command omits the required brain-mask argument, so the test would fail or pass only by accident. It also compares against a baseline that is not described. The test provides no real validation of the DC algorithm.
  ```
  ExternalData_add_test(${SEM_DATA_MANAGEMENT_TARGET} NAME ${testname} COMMAND ${SEM_LAUNCH_COMMAND} $<TARGET_FILE:${CLP}Test>
      --compare DATA{${BASELINE}/${CLP}Test.nrrd}
      ${TEMP}/${CLP}Test.nrrd
      ModuleEntryPoint
      --sigma 2.5 DATA{${INPUT}/CTHeadAxial.nhdr,CTHeadAxial.raw.gz} ${TEMP}/${CLP}Test.nrrd
  ```
  Suggestion: Replace with a DWI test case that supplies inputVolume, maskVolume and outputVolume with the real parameter names, and document the expected baseline generation.

### D2. Documented "leave mask blank" path fails: mask is always read
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`DiffusionComplexityMap/DiffusionComplexityMap.cxx:37`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/DiffusionComplexityMap.cxx#L37): DiffusionComplexityMap.xml line 26 promises "If left blank, the entire input image will be used as input", and the filter has a no-mask branch (itkDiffusionComplexityMappingImageFilter.hxx line 119: 'if (this->GetNumberOfIndexedInputs()==1)'). But the CLI unconditionally sets and updates the mask reader, so an empty maskVolume makes itk::ImageFileReader throw and the CLI exits with EXIT_FAILURE. The no-mask code path is unreachable, so users following the documented workflow get an error instead of a whole-image result.
  ```
    reader->SetFileName(inputVolume.c_str());
    readerMask->SetFileName(maskVolume.c_str());
    reader->Update();
    readerMask->Update();
  ```
  Suggestion: Only create/update the mask reader and call SetDiffusionSpace when maskVolume is non-empty; otherwise leave the filter with a single input so the existing whole-image branch is used.
- **haiku** (major, high confidence, quote verified) [`DiffusionComplexityMap/DiffusionComplexityMap.cxx:36`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/DiffusionComplexityMap.cxx#L36): The XML description says 'If left blank, the entire input image will be used as input', but the parameter is declared as a plain <image type="label"> with no optional flag, and main() always calls readerMask->SetFileName(maskVolume) and Update() before filter->SetDiffusionSpace(readerMask->GetOutput()). With an empty mask name, ITK throws, the exception is caught in main, and the module returns EXIT_FAILURE. The documented fallback path (GenerateData's GetNumberOfIndexedInputs()==1 branch) is therefore unreachable from the CLI.
  ```
  ReaderMaskType::Pointer readerMask = ReaderMaskType::New();
    reader->SetFileName(inputVolume.c_str());
    readerMask->SetFileName(maskVolume.c_str());
    reader->Update();
    readerMask->Update();
  ```
  Suggestion: Only call SetDiffusionSpace when maskVolume is non-empty, or make the mask optional in the XML and document the behavior accordingly.

### D3. Histogram frequencies indexed by gradient index instead of bin index
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx:449`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx#L449): The histogram was initialized with m_HistogramBins bins (line 434), but the entropy sum loops over the number of gradient components and calls GetFrequency(j) with that index. When the number of gradient volumes exceeds the number of bins (e.g. --numBins 4 with a 30-direction DWI, or a small diffusion range with the automatic bin estimate), GetFrequency reads past the end of the DenseFrequencyContainer2 vector (undefined behaviour / garbage or crash), and even when in range the entropy is summed over the wrong bins, so the reported DC values are wrong. The same pattern is repeated in calculatesDisequilibriumMapping (lines 548-550).
  ```
                for (int j = 0; j < diffImg->GetNumberOfComponentsPerPixel(); ++j) {
                    p = static_cast<double>(diffusionProbability->GetFrequency(j))/static_cast<double>(diffusionProbability->GetTotalFrequency());
  ```
  Suggestion: Iterate over the histogram bins (e.g. HistogramType::Iterator or GetSize()[0]) when accumulating p, and keep the gradient loop only for filling the histogram.

### D4. Mask/input geometry mismatch causes out-of-bounds write into usedMaskSpace
single; category soundness; raised by deepseek
- **deepseek** (major, high confidence, quote verified) [`DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx:129`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx#L129): usedMaskSpace is allocated with the DWI's requested region (lines 113-117) but the loop is bounded by the mask's own region. If the user supplies a mask with a different size (e.g. a mask from another series, or a label map with a different slice count), usedMaskIt runs past the end of its buffer and writes out of bounds. ITK iterators do not bounds-check in release builds, so this is memory corruption / a crash of the CLI process rather than a clean error message.
  ```
            while (!inputMaskIt.IsAtEnd()) {
                usedMaskIt.Set(inputMaskIt.Get());
                ++inputMaskIt;
                ++usedMaskIt;
            }
  ```
  Suggestion: Verify that the mask's LargestPossibleRegion and spacing/origin/direction match the input image and report a clear error otherwise (or resample the mask); iterate over the intersection region only.

### D5. Rating of license
rating dispute; category license; raised by deepseek, flash-lite, haiku
Ratings: deepseek ok, flash-lite ok, haiku concern

### D6. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Automatic bin estimate can return 0 bins, then p_e = 1/0
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx:398`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx#L398): numberOfBins is an unsigned int computed from a double division; if max == min (constant or all-zero diffusion values inside the mask) the result is 0. Histogram::Initialize is then called with size 0 and, in calculatesDisequilibriumMapping line 545, 'p_e = 1.0/m_HistogramBins' divides by zero, producing inf/NaN output or an ITK exception.
  ```
        if (noise_variance < 0){
            // If noise variance estimate is negative, then use the least data point in the regression data
            numberOfBins = diffusion_range/std::sqrt(0.000000001);
        }else{
            numberOfBins = diffusion_range/std::sqrt(noise_variance);
        }
  ```
  Suggestion: Clamp the computed bin count to a sane minimum (e.g. 4, matching the XML constraint) and guard against max == min before building the histogram.

### Conflicting license notices: Apache-2.0 headers vs MIT LICENSE
minor; license; raised by haiku
- **haiku** (minor, high confidence, quote verified) [`DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.h:2`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.h#L2): The filter sources state Apache-2.0 with a different copyright holder, while the repository LICENSE and README say MIT. Both permit distribution, so this is not blocking, but users and packagers cannot tell which terms apply to the filter code.
  ```
  Copyright 2017 Antonio Carlos da Silva Senra Filho and Fabricio Henrique Simozo
  
     Licensed under the Apache License, Version 2.0 (the "License");
  ```
  Suggestion: Clarify in LICENSE or the headers which license covers the ITK filter files, and make the copyright holders consistent.

### Debug output always enabled in the CLI
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DiffusionComplexityMap/DiffusionComplexityMap.cxx:70`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/DiffusionComplexityMap.cxx#L70): DebugModeOn() is hard-coded, so every run prints the NRRD metadata keys, gradient counts and bin counts to stdout. This clutters the Slicer CLI output window for all users and cannot be turned off from the GUI.
  ```
    filter->DebugModeOn();
    filter->Update();
  ```
  Suggestion: Expose debug mode as a boolean CLI parameter defaulting to false, or remove the call.

### Division by zero when the DWI has no b0 volume
minor; soundness; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx:299`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx#L299): numberOfReferenceImages is derived from the number of components minus the number of non-zero gradients; a DWI without a b0 volume (or with headers lacking DWMRI_gradient tags, as in the bundled test data) makes it 0, so the mean S0 becomes inf/NaN and every downstream diffusion value and the whole DC map are NaN. The missing b-value case is only printed as a warning (line 200-203) and processing continues.
  ```
            meanNonDiff/=numberOfReferenceImages;
            weights[0]=meanNonDiff;
  ```
  Suggestion: Validate that at least one b0 volume and at least one gradient exist and abort with a clear error message otherwise.
- **haiku** (minor, medium confidence, quote verified) [`DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx:299`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx#L299): createDiffusionSpace divides by numberOfReferenceImages, which is zero when the header has no b=0 volumes, producing NaN for every voxel. histogramBinByDiffusionVarianceRegression can return 0 bins for a small range, and calculatesEntropyMapping/calculatesDisequilibriumMapping then compute 1.0/m_HistogramBins (division by zero). The automatic bin count is also not clamped, unlike the manual range 4-500 in the XML. The missing b0 case only prints to cerr and continues, so the user gets a silently wrong map instead of an error.
  ```
  meanNonDiff/=numberOfReferenceImages;
      weights[0]=meanNonDiff;
  ```
  Suggestion: Validate numberOfReferenceImages > 0 and b0 > 0 and throw itk::ExceptionObject otherwise; clamp the automatic bin count to a sane minimum (e.g. >= 4) before use.

### ITK components may not cover all headers used
minor; packaging; raised by haiku
- **haiku** (minor, low confidence, quote verified) [`DiffusionComplexityMap/CMakeLists.txt:16`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/CMakeLists.txt#L16): The code includes itkDiffusionTensor3DReconstructionImageFilter.h and itkNrrdImageIO.h, but only ITKIOImageBase and ITKSmoothing are requested in find_package. Depending on the ITK build, the link or include could fail. Not verified by building.
  ```
  set(${PROJECT_NAME}_ITK_COMPONENTS
      ITKIOImageBase
      ITKSmoothing
      )
  ```
  Suggestion: Add the ITK modules that provide the DTI reconstruction and NRRD IO headers (for example ITKDiffusionTensorImage / ITKIONRRD) and confirm a clean build.

### Missing b-value leads to silent division by zero
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx:200`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx#L200): If the DWMRI_b-value key is absent, b0 stays 0 and createDiffusionWeightedValues divides by it, yielding inf/NaN gradient values. The code prints only 'BValue not specified in header file' to cerr and proceeds, so the module reports success with a corrupt output.
  ```
  if(!readb0)
      {
          std::cerr << "BValue not specified in header file" << std::endl;
      }
  ```
  Suggestion: Raise an exception instead of continuing when the b-value is missing.

### Stray '>' in the mask image element of the CLI XML
minor; packaging; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`DiffusionComplexityMap/DiffusionComplexityMap.xml:21`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/DiffusionComplexityMap.xml#L21): The extra '>' becomes character data inside the <image> element. It is well-formed XML so the module still loads, but it is a malformed parameter declaration that can confuse the SlicerExecutionModel parser and any tooling that reads the XML.
  ```
      <image type="label">>
  ```
  Suggestion: Remove the stray '>' so the line reads '<image type="label">'.
- **haiku** (minor, high confidence, quote verified) [`DiffusionComplexityMap/DiffusionComplexityMap.xml:21`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/DiffusionComplexityMap.xml#L21): The image element for the mask has a stray '>' character in its content, and the disequilibrium enum uses the misspelled labels 'desiquilibriumFunction' and 'Kullback-Leiber'. These are cosmetic but affect the user-facing UI and the parameter name.
  ```
  <image type="label">>
  ```
  Suggestion: Remove the stray '>' and correct the spelling of the labels and parameter name (keeping compatibility if the parameter name is already used by saved scenes).

### Uninitialized values when gradient string has fewer than three numbers
minor; soundness; raised by haiku
- **haiku** (minor, medium confidence, quote verified) [`DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx:161`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx#L161): x, y, z are declared without initialization and passed to sscanf. If a DWMRI_gradient metadata value is malformed, the vector gets indeterminate values, and the gradient is then used in the reference-vs-gradient decision.
  ```
  double x,y,z;
           itk::ExposeMetaData<std::string> (imgMetaDictionary, *itKey, metaString);
           if (itKey->find("DWMRI_gradient") != std::string::npos)
  ```
  Suggestion: Initialize x, y, z to zero and check that sscanf returns 3.

### log() of zero/negative values guarded with '||' instead of '&&'
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx:366`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/itkDiffusionComplexityMappingImageFilter.hxx#L366): The guard passes whenever either value is non-zero, so a zero gradient value with a non-zero b0 (common in background/noisy voxels) yields log(0) = -inf, and negative values yield NaN. These propagate into the histogram range estimate and the entropy/disequilibrium maps; only isinf is filtered later, NaN is not.
  ```
                if (rawDiffIt.Get()[0]!=0 || rawDiffIt.Get()[n]!=0) {
                    diffValues[index]=std::abs((std::log(rawDiffIt.Get()[n]) - std::log(rawDiffIt.Get()[0]))/static_cast<OutputPixelType>(b0));
  ```
  Suggestion: Require both values to be strictly positive (and b0 > 0) before taking the logarithm, and set the diffusion value to 0 otherwise.

### CLI XML declares license 'Slicer' while the code is MIT/Apache-2.0
info; license; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`DiffusionComplexityMap/DiffusionComplexityMap.xml:8`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/DiffusionComplexityMap/DiffusionComplexityMap.xml#L8): The repository LICENSE is MIT and the ITK filter files are Apache-2.0; the XML metadata shown in the Slicer module panel states a different license, which is misleading for users checking terms. Distribution permission itself is clear.
  ```
      <license>Slicer</license>
  ```
  Suggestion: Set the XML license field to 'MIT' (and note the Apache-2.0 filter files in the acknowledgements or a NOTICE).

### Leftover project name in mkdocs configuration
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`mkdocs.yml:3`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/mkdocs.yml#L3): The docs site header shows another project's repository name, which is confusing for users looking for the source of this extension. Cosmetic only.
  ```
  repo_name: LOAMRI/Slicer-ASLtoolkit
  ```
  Suggestion: Set repo_name to CSIM-Toolkits/SlicerDiffusionComplexityMap.

### No research-use disclaimer and no user tutorial or sample DWI data
info; utility; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`docs/index.md:46`](https://github.com/CSIM-Toolkits/SlicerDiffusionComplexityMap/blob/b4dd78653ab80be20a0d3bec7334ad641d277d25/docs/index.md#L46): The documentation is a single page covering installation and example images; it does not explain the required NRRD DWMRI metadata, the meaning of the q value / disequilibrium functions, or provide sample data, and there is no statement that the DC map is a research metric not validated for clinical diagnosis. Users must infer the workflow from the XML tooltips.
  ```
  ### Diffusion Complexity map
  
  This module is able to reconstruct the `Diffusion Complexity`  map from a standard Diffusion-Weighted MRI imaging acquisition.
  ```
  Suggestion: Add a short usage walkthrough with a downloadable DWI sample, describe the parameters, and add a research-use-only disclaimer.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Pure C++/ITK CLI extension: no Python, no network, no telemetry, no downloads at runtime, MIT license plus Apache-2.0 headers on the ITK filter — the three admission requirements (safety, distribution permission, usable catalog entry) are met, so I recommend merge. However the filter has real correctness/memory-safety bugs that should be fixed soon: the documented "leave mask blank" path throws, a mask whose geometry differs from the input causes an out-of-bounds write, and histogram frequencies are indexed by gradient index instead of bin index (out-of-bounds read and wrong entropy). The bundled test cannot pass (passes a nonexistent --sigma flag and a CT image instead of DWI).
Not checked: Could not verify that the catalog revision exists or resolve commit b4dd78653ab80be20a0d3bec7334ad641d277d25 (no network access); the catalog entry itself pins scm_revision 'main', so the reviewed source is the tip of main at review time.; Could not build the extension or run its test, so compilation against Slicer's ITK (including whether itkDiffusionTensor3DReconstructionImageFilter.h is available without an explicit ITK component) and the ExternalData download of the test data are unverified.; Could not inspect the binary PNG assets or the ExternalData payloads (CTHeadAxial.nhdr/raw.gz, DiffusionComplexityMapTest.nrrd) beyond their hash files.; Could not verify the published paper's claims or the numerical validity of the DC metric against the cited reference.
Questions for the author: Should the mask really be optional? The XML says leaving it blank uses the whole image, but the CLI always reads it — is that intended to be fixed?; Is the entropy loop over gradient components (GetFrequency(j)) intentional, or should it iterate over histogram bins?; Can the bundled test be updated to use a real DWI with DWMRI metadata and the actual CLI flags instead of '--sigma 2.5'?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
The SlicerDiffusionComplexityMap extension is a clean, well-structured C++ Slicer CLI module implementing diffusion complexity mapping using ITK. All inspected files, including CMake configuration, ITK filters, CLI metadata, license, and documentation, meet Slicer extensions index standards and guidelines without any safety or packaging issues. 🟢 Recommend merge
Not checked: Exact build test on remote CI infrastructure (not runnable in review environment)

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
Small, self-contained C++ ITK CLI with no network access, no Python environment changes, no downloads at runtime, and an MIT LICENSE. Main concerns are soundness: the XML declares the brain mask as optional and the docs say a blank mask uses the whole image, but the CLI always reads the mask and would throw on an empty name; the CTest entry passes arguments the program does not accept (--sigma, no mask); and the filter has unguarded divisions (zero reference images, zero automatic bin count). The filter sources carry Apache-2.0 headers that conflict with the MIT LICENSE and need clarification. Not verified by building or running.
Not checked: Did not build or run the CLI or the CTest; did not access the ITK/SlicerExecutionModel build environment.; Did not resolve scm_revision 'main' to a specific commit, nor inspect the git history of the upstream repository.; Did not verify the ExternalData test data (only md5/sha256 files were listed).; Did not verify the referenced paper, the algorithm's scientific validity, or the documentation website.; Did not check the Slicer extension description/icon/screenshot URLs.


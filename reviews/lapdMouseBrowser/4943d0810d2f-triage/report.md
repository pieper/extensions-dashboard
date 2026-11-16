# AI review: lapdMouseBrowser

> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when there is one, is shown on the dashboard.

- Source: https://github.com/lapdMouse/Slicer-lapdMouseBrowser.git at commit `4943d0810d2ff91c4b07e938102015d91725e875`
- Context: Extensions Index catalog entry
- Panel: triage (Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`), Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`), DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`))
- Reviewed 2026-11-16T10:30:22Z; cost $0.04

## Overall

| Criterion | deepseek | flash-lite | haiku |
|---|---|---|---|
| safety | minor | ok | ok |
| environment | concern | ok | minor |
| packaging | minor | ok | ok |
| license | ok | ok | minor |
| soundness | concern | ok | concern |
| utility | ok | ok | minor |
| **overall** | needs fixes | no concerns | needs fixes |

## What each reviewer says the extension does

- **deepseek**: lapdMouseBrowser lets Slicer users browse the lapdMouse (mouse lung anatomy + aerosol deposition) archive hosted at NIEHS, download datasets to a local cache folder, and load them into Slicer with preconfigured display settings; a second module converts *.meta airway trees and *.csv compartment measurements into mesh models. It targets researchers working with these mouse lung datasets.
- **flash-lite**: lapdMouseBrowser is a 3D Slicer extension that lets users browse the lapdMouse data archive, download dataset files (such as aerosol deposition volumes and lung models), and visualize airway tree structures and compartment measurements.
- **haiku**: Provides a Slicer browser for the lapdMouse lung-anatomy and aerosol-deposition data archive (NIEHS CEBS). It downloads selected dataset files over HTTPS, caches them locally, and loads them into Slicer with preset color tables, plus a visualizer that turns *.meta airway trees and *.csv measurement tables into models. Intended for researchers using the lapdMouse archive.

## Disagreements (start here)

### D1. Interrupted downloads are left on disk and later treated as complete
single; category soundness; raised by haiku
- **haiku** (major, high confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:67`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L67): _downloadURLStreaming opens the destination file and streams into it with no try/finally and no size or checksum verification (lines 68-76). downloadFiles then decides success only with os.path.exists(localName) (line 451). If the connection drops mid-stream, a truncated file remains and is counted as 'downloaded' in the status column and skipped on later downloads (line 446). The user then loads a corrupt .mha/.vtk/.nrrd, and an exception from the read at line 449 is not caught there and aborts the whole loop. The archive provides MD5SUMS (line 26), but it is never used.
  ```
  def _downloadURLStreaming(self,response,destination):
      if response.getcode() == 200:
        destinationFile = open(destination, "wb")
        bufferSize = 1024*1024
        while True:
  ```
  Suggestion: Write to a temporary name and rename on success; wrap the transfer in try/except that deletes the partial file; compare size (Content-Length) or MD5 from MD5SUMS before marking the file as downloaded.

### D2. Registered unit test depends on files in ~/Documents and fails on every build machine
partial; category soundness; raised by deepseek, haiku
- **deepseek** (major, high confidence, quote verified) [`lapdMouseVisualizer/lapdMouseVisualizer.py:513`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseVisualizer/lapdMouseVisualizer.py#L513): lapdMouseVisualizer/CMakeLists.txt registers this test with slicer_add_python_unittest; _internalTest() unconditionally loads a table and a *.meta tree from a fixed path in the developer's home directory. On CI or any other machine the load returns nothing, so slicer.util.getFirstNodeByClassByName('vtkMRMLTableNode','test_LobesDeposition') is None and logic.measurementsTable2Model(None) raises AttributeError. Every build's test run therefore reports a failure that is unrelated to real regressions, and the test verifies nothing about the module on the machines that matter.
  ```
      measurementsFile =  os.path.join(os.path.expanduser("~"),\
                                       'Documents/data/lapdMouseTest/test/test_LobesDeposition.csv')
      slicer.util.loadNodeFromFile(measurementsFile, 'TableFile')
  ```
  Suggestion: Ship the two small test files under lapdMouseVisualizer/Testing/Data, register them with slicer_add_test / --testing-data-dir, and skip or fail gracefully when they are absent.
- **haiku** (minor, high confidence, quote verified) [`lapdMouseVisualizer/lapdMouseVisualizer.py:513`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseVisualizer/lapdMouseVisualizer.py#L513): The CMake test registration is commented out (Testing/Python/CMakeLists.txt line 2). The visualizer test reads ~/Documents/data/lapdMouseTest files that a user will not have, so the test fails outside the author's machine. The DBBrowser test only calls delayDisplay.
  ```
  measurementsFile =  os.path.join(os.path.expanduser("~"),\
                                         'Documents/data/lapdMouseTest/test/test_LobesDeposition.csv')
  ```
  Suggestion: Add small sample fixtures inside the repository and register real unit tests.

### D3. Rating of environment
rating dispute; category environment; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku minor

### D4. Rating of soundness
rating dispute; category soundness; raised by deepseek, flash-lite, haiku
Ratings: deepseek concern, flash-lite ok, haiku concern


## Findings from some reviewers

### Colour-table nodes are added to the MRML scene when the module is registered, not when it is used
minor; environment; raised by deepseek
- **deepseek** (minor, medium confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:743`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L743): Slicer instantiates every scripted module class during startup registration, so loadColorTables() (lines 748-813) runs for all users with the extension installed, even those who never open lapdMouse or use the module. It adds 'lapdMouseLobes', 'lapdMouseSegments' and 'lapdMouseOutlets' nodes, two of them with 5000 colours, into every new scene; these are hidden from editors but are still scene content that gets serialized into saved .mrb/.mrml files of unrelated user scenes.
  ```
      self.parent.acknowledgementText = """
      This work was supported in part by NIH project R01ES023863.
  """ # replace with organization, grant and thanks.
      lapdMouseDBBrowser.loadColorTables()
  ```
  Suggestion: Create the colour tables lazily (on first use in loadFiles/the browser window) or check for an existing scene and only add them when data is actually being loaded.

### Downloads and loading run synchronously on the GUI thread, and Cancel does not interrupt a download
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:447`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L447): The per-file download runs inside the button slot, kept responsive only by slicer.app.processEvents() in the loop; pd.wasCanceled is tested only between files, so cancelling a multi-GB file has no effect. During a large transfer the UI remains fragile (re-entrant events, possible frozen window) and the progress dialog reports file counts rather than bytes.
  ```
        print('Downloading '+remoteName)
        t0 = time.time()
        lapdMouseDBUtil(self.remoteFolderUrl).downloadFile(remoteName, localName)
  ```
  Suggestion: Move the transfer to a worker thread or slicer.cli-style background task with a real cancellation check inside the read loop and byte-level progress.

### Global RNG reseeded and color tables created at module instantiation
minor; environment; raised by haiku
- **haiku** (minor, medium confidence, quote verified, other lines) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:526`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L526): random.seed(3) reseeds Python's global random module, which can affect other code in the same Slicer process. loadColorTables() runs in the DBBrowser __init__ (line 746), so it creates two 5000-entry color tables and one 6-entry table in the scene whenever the module is instantiated, even if the user never opens the browser.
  ```
      lapdMouseDBBrowser.loadColorTables()
        
    @staticmethod
    def loadColorTables():
  ```
  Suggestion: Use a local random.Random(3) instance instead of seeding the global RNG, and create color tables lazily when a file is loaded.

### Opening external files with write mode r+ unnecessarily
minor; soundness; raised by flash-lite, haiku
- **flash-lite** (minor, high confidence, quote verified) [`lapdMouseVisualizer/lapdMouseVisualizer.py:213`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseVisualizer/lapdMouseVisualizer.py#L213): 
  ```
      for line in open(filename,'r+'):
  ```
  Suggestion: Change 'r+' (read/write) to 'r' (read-only) when opening external user files like *.meta tree structures.
- **haiku** (minor, high confidence, quote verified) [`lapdMouseVisualizer/lapdMouseVisualizer.py:213`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseVisualizer/lapdMouseVisualizer.py#L213): readMetaTree opens the user's input file with 'r+', which requires write permission and could modify the file if the code were extended. It only reads, so 'r' is correct. Read-only files will fail to load.
  ```
      for line in open(filename,'r+'):
  ```
  Suggestion: Use open(filename, 'r') with a context manager.

### Prefix matching in remote listing can return wrong entries
minor; soundness; raised by deepseek, haiku
- **deepseek** (info, medium confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:89`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L89): _listFolderRemote('') computes remainingPath = name[1:], dropping the first character of the name; the depth filter then accidentally still works only because every entry has the same 1-character offset. Any archive with differently shaped top-level names, or a caller passing a trailing separator, would list the wrong entries.
  ```
      if (dirname == '.' or os.path.commonprefix([dirname,oneFile['name']]) == dirname):
        remainingPath = oneFile['name'][len(dirname)+1:]
  ```
  Suggestion: Normalize the prefix (strip separators) before slicing, and use a path-component comparison rather than os.path.commonprefix.
- **haiku** (minor, medium confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:89`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L89): _listFolderRemote uses os.path.commonprefix on strings, so dirname 'm01' also matches 'm010/...' and the 'remainingPath' slicing assumes a separator after dirname. Current dataset names are fixed, so the impact is limited, but the logic is fragile.
  ```
  if (dirname == '.' or os.path.commonprefix([dirname,oneFile['name']]) == dirname):
            remainingPath = oneFile['name'][len(dirname)+1:]
  ```
  Suggestion: Compare path components, e.g. name.startswith(dirname + '/').

### SSL context enables legacy server connect option
minor; safety; raised by deepseek, haiku
- **deepseek** (info, medium confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:26`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L26): The archive publishes per-dataset MD5SUMS (present throughout Resources/allfiles.json, e.g. 'm01/MD5SUMS'), but the code only checks HTTP 200 for m01/MD5SUMS and never validates downloaded content; truncated or corrupted transfers are detected only by os.path.exists before the file is loaded, and Slicer then reports a load error instead of a clear integrity error.
  ```
      httpCode = urllib.request.urlopen(self.gdriveURL+'m01/MD5SUMS',context=ctx).getcode()
  ```
  Suggestion: Fetch MD5SUMS per dataset and verify hash after download, retrying or reporting a checksum mismatch.
- **haiku** (minor, medium confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:22`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L22): The access check sets OP_LEGACY_SERVER_CONNECT, which allows connections to servers without secure renegotiation. The context is also only passed to the access check (line 26), not to the actual data downloads (line 56), so the setting is inconsistent and gives no protection where it is used. This is a weakening, not a direct exploit, and the default context is used for downloads.
  ```
  ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
  
        try:
          httpCode = urllib.request.urlopen(self.gdriveURL+'m01/MD5SUMS',context=ctx).getcode()
  ```
  Suggestion: Remove the legacy-connect flag; rely on default secure SSL options and use one consistent context.

### Seeds the global random module from a colour-table helper
minor; environment; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:789`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L789): random.seed(3) reseeds Python's global RNG shared with all other Slicer modules and scripts (repeated in setupOutletsColorTable at line 810). Any other code relying on random for e.g. sampling or shuffling gets a deterministic, correlated state after Slicer starts with this extension installed, which is a global side effect for users who never open the module.
  ```
      import random
      random.seed(3) # seed 3: nothing too dark and first few generations reasonably well contrasted
      for i in range (1,numSegments):
        colors.SetColor(i, str(i),random.uniform(0.0,1.0),random.uniform(0.0,1.0),random.uniform(0.0,1.0),1)
  ```
  Suggestion: Use a private instance, e.g. rng = random.Random(3) and rng.uniform(...).

### deleteFiles removes user files with no confirmation and no way to undo
minor; safety; raised by deepseek, haiku
- **deepseek** (minor, high confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:466`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L466): Clicking 'delete selected files' permanently deletes the selected files from the user's cache folder without any Qt confirmation dialog, and the storage folder is freely configurable via ctkDirectoryButton (line 865-870), so a mis-click or a folder pointed at a data directory deletes previously downloaded multi-GB data irrecoverably. Deletion is at least confined to <cache>/<dataset>/<name>.
  ```
    def deleteFiles(self, datasetname, files):
      for f in files:
        remoteName = os.path.join(datasetname,f.replace('/',os.sep))
        localName = os.path.join(self.localCacheFolder,remoteName)
        if os.path.exists(localName):
          print("deleting file "+localName)
  ```
  Suggestion: Ask for confirmation listing the files before deleting, and refuse to delete anything outside the configured cache folder.
- **haiku** (minor, medium confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:466`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L466): deleteFiles removes the selected files from the cache folder with os.remove, and onDeleteSelectedDataset calls it with no confirmation prompt. This is user-initiated and limited to the cache folder, so the risk is accidental data loss only.
  ```
  def deleteFiles(self, datasetname, files):
        for f in files:
          remoteName = os.path.join(datasetname,f.replace('/',os.sep))
          localName = os.path.join(self.localCacheFolder,remoteName)
          if os.path.exists(localName):
            print("deleting file "+localName)
  ```
  Suggestion: Ask for confirmation before deleting multiple files.

### testDBAccess calls an instance method on the class, so it always fails
minor; soundness; raised by deepseek, haiku
- **deepseek** (info, high confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:193`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L193): _canAccess is called on the class without an instance, raising TypeError (missing self). Similarly downloadItem/getStatus/summarizeItems (lines 117-191) read item['localName'], item['remoteName'] and item['status'], keys that do not exist in Resources/allfiles.json (entries only have name/isFolder/size/modificationTimestamp, e.g. lines 2-7). This is leftover CLI code; if it were ever called it would silently fail or raise, so it should be removed or fixed.
  ```
    def testDBAccess(db):
      serverStatus = 'unknown'
      if lapdMouseDBUtil._canAccess():
  ```
  Suggestion: Delete the unused module-level helpers or port them to the dictionary structure actually produced by _listFolderRemote.
- **haiku** (minor, high confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:193`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L193): _canAccess is an instance method (line 20) but is called on the class with no self (line 195). This raises TypeError. The function is currently unused, but if it is wired up it would crash rather than report server status.
  ```
  def testDBAccess(db):
    serverStatus = 'unknown'
    if lapdMouseDBUtil._canAccess():
  ```
  Suggestion: Call db._canAccess() on the passed instance, or remove the dead function.

### updateForm() proceeds with no dataset selected and reads datasets[-1]
minor; soundness; raised by deepseek
- **deepseek** (minor, high confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:344`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L344): The 'clear form' branch is a no-op: execution continues and self.datasets[-1] is used, which shows the last dataset when nothing is selected and raises IndexError when the dataset list is empty (e.g. the archive is unreachable so only local folders were scanned and none exist). Called from onDatasetChanged, updateForm and after downloads.
  ```
      if datasetId==-1: # clear form
        pass
      datasetname = self.datasets[datasetId]
      self.customFormName.text = datasetname
  ```
  Suggestion: return after clearing the widgets when datasetId==-1.

### Catalog pins a moving branch rather than a commit
info; packaging; raised by haiku; **quote not found in source**
- **haiku** (info, high confidence, quote file not found) [`lapdMouseBrowser.json:1`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseBrowser.json#L1): scm_revision is 'master', so the source built and installed can change without a catalog update. This is allowed by policy, but it means the reviewed code may differ from what users receive.
  ```
  "scm_revision": "master",
  ```
  Suggestion: Consider pinning a reviewed commit hash for reproducibility.

### Modules register under a custom category while the extension is listed as Informatics
info; utility; raised by deepseek
- **deepseek** (info, medium confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:736`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L736): Both modules declare categories = ["lapdMouse"] whereas the catalog entry says Informatica/Informatics; users looking in the Informatics category will not find the modules and README.md tells them to look under 'lapdMouse', so behaviour is inconsistent with the catalog metadata.
  ```
      self.parent.title = "lapdMouseDBBrowser"
      self.parent.categories = ["lapdMouse"]
  ```
  Suggestion: Use ['Informatics'] or a category consistent with the catalog entry.

### README references a non-existent module name
info; utility; raised by haiku
- **haiku** (info, high confidence, quote verified) [`README.md:56`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/README.md#L56): The README says the visualizer is 'lapdMouseDBVisualizer', but the module is lapdMouseVisualizer. This could confuse users following the install steps.
  ```
  make sure both `lapdMouseDBBrowser` and
     `lapdMouseDBVisualizer` are checked and click Yes.
  ```
  Suggestion: Correct the module name to lapdMouseVisualizer.

### TLS context enables legacy renegotiation in the availability check
info; safety; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`lapdMouseDBBrowser/lapdMouseDBBrowser.py:22`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/lapdMouseDBBrowser.py#L22): OP_LEGACY_SERVER_CONNECT (0x4) re-allows insecure renegotiation in this context, weakening TLS against renegotiation-style attacks. Impact is small because the context is used only in _canAccess, which is itself only reached from the broken module-level testDBAccess() (line 193-200) and by default downloads use a normal validating context.
  ```
      ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
      ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
  ```
  Suggestion: Drop the option, or set it only after an explicit legacy-server failure and document why.

### Terms for the downloaded archive data are not stated
info; license; raised by haiku
- **haiku** (info, medium confidence, quote verified) [`README.md:178`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/README.md#L178): The BSD license covers the code. The lapdMouse data files that the extension downloads and redistributes into users' caches have no stated license or usage terms in the repository. The user should check the archive's terms.
  ```
  ## License
  
  **lapdMouseBrowser** is distributed under [3-clause BSD license](License.txt).
  ```
  Suggestion: State the terms under which the archive data may be used, or link to the archive's data-use policy.

### Tests are placeholders and the Python test CMake file is commented out
info; utility; raised by deepseek
- **deepseek** (info, high confidence, quote verified) [`lapdMouseDBBrowser/Testing/Python/CMakeLists.txt:2`](https://github.com/lapdMouse/Slicer-lapdMouseBrowser/blob/4943d0810d2ff91c4b07e938102015d91725e875/lapdMouseDBBrowser/Testing/Python/CMakeLists.txt#L2): Both Testing/Python/CMakeLists.txt files only reference a commented-out test whose file does not exist in the repository, and lapdMouseDBBrowserTest.test_lapdMouseDBBrowser1 is a no-op ('self.delayDisplay("Test passed!")', line 915-916). No test covers the download path, JSON-based listing, or the .meta/.csv conversion beyond the file-dependent visualizer test.
  ```
  
  #slicer_add_python_unittest(SCRIPT ${MODULE_NAME}ModuleTest.py)
  ```
  Suggestion: Add a hermetic unit test for readMetaTree/tree2Mesh and for the listing logic using the bundled allfiles.json.


## Reviewer summaries

### DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash-1017`): needs fixes
Two scripted modules plus a bundled file index (allfiles.json). All network access is HTTPS to a fixed NIH host, downloads are user-confirmed with size shown, nothing is installed, no credentials, telemetry or code execution; license is BSD-3-Clause. Main problems are quality: a registered unit test that depends on files under ~/Documents and will fail on every build machine, broken dead helper functions, an updateForm IndexError path, downloads run on the GUI thread, and MRML colour-table nodes added to the scene at module registration (affects users who never open the module). No blocking admission issue found.
Not checked: The full 9590-line Resources/allfiles.json was only sampled and searched (patterns for '..', 'http', script/exec) rather than read end to end.; Binary files (lapdMouseBrowser.png, Screenshots/*.png, Resources/Icons/*.png) were not inspected; their content and provenance are unverified.; I did not verify that commit 4943d0810d2ff91c4b07e938102015d91725e875 actually matches the file contents provided, nor the current state of the master branch referenced by scm_revision.; Behaviour of the remote NIEHS cebs-ext.niehs.nih.gov endpoints (HTTP status codes, redirects, whether the file URLs return the expected payloads, and the archive's own data terms of use) could not be checked without network access.; No build, ctest run or Slicer launch was possible, so it is unverified whether the studio's tests, CMake packaging and Python 3 syntax work in practice.; Whether ~/Documents/data/lapdMouseTest test data exists on the extension build machine is unknown; the finding assumes a standard clean machine.
Questions for the author: Could the visualizer test data be bundled under Testing/Data so the registered ctest passes on clean machines?; Is it necessary to create the lapdMouse colour tables during module registration, or can they be created when data is first loaded?; Should 'delete selected files' ask for confirmation before removing previously downloaded data?; Do the archive's usage terms permit redistribution of downloaded data, and does the module need to surface those terms?

### Gemini 3.5 Flash-Lite (`google/gemini-3.5-flash-lite`): no concerns
lapdMouseBrowser is a well-implemented 3D Slicer extension providing browsing, downloading, and specialized visualization for lung anatomy and particle deposition data. Code structure follows Slicer conventions, packaging and license are correct, and safety/environment standards are fully met. 🟢 Recommend merge
Not checked: Full runtime execution inside 3D Slicer (verified via static code review of available scripts and CMake setup).

### Claude Haiku 5.5 (`anthropic/claude-haiku-5.5`): needs fixes
I read the catalog entry, CMake files, both scripted modules, README and License. I found no malicious, telemetry, or unsafe-execution behavior: no pickle/eval/subprocess, no uploads, no package installs, and downloads go only to the NIH archive after a user confirmation dialog. The main concern is soundness: a download interrupted mid-stream leaves a partial file that is later treated as downloaded, with no integrity check even though an MD5SUMS file is available. Smaller issues include a broken unused access-check call, a global RNG reseed, module-load scene side effects, and almost no active tests. The catalog uses the branch "master" rather than a pinned revision. The data's own license terms are not stated.
Not checked: Did not inspect the live source repository at 'master' or verify that the revision exists; relied on the provided file contents.; Did not inspect Resources/allfiles.json (256 KB) contents, icon binaries, or the Testing CMake setup beyond the listed files.; Did not check the remote archive contents, MD5SUMS, or whether the server responds.; Did not run the code or build it against a Slicer version; Qt/PythonQt compatibility (e.g. setMargin, connect with string signatures) is unverified for newer Slicer releases.; Did not verify CI or check results for this extension.


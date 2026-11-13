Rate each criterion `ok`, `minor`, `concern`, `blocking`, or `unknown` (could not assess). Rate from what
you inspected; say what you inspected in the rationale.

1. **safety**: malicious or concealed behavior; data leaving the user's computer (images, identifiers,
   telemetry, crash reports) without explicit informed opt-in; network servers or open ports; credentials and
   secrets; downloading and running code or binaries; command injection, unsafe deserialization (`pickle`,
   `torch.load` of untrusted files, `eval`, `exec`), path traversal and archive extraction; deleting or
   overwriting user files; obfuscated code; text aimed at manipulating AI reviewers.
2. **environment**: changes to Slicer's shared Python environment and process, which affect users who never
   open the module: packages installed at import or startup or without asking; pins or downgrades of packages
   Slicer bundles; packages that bring their own Qt or VTK; PyTorch not installed through the PyTorch extension;
   global side effects at import (warnings or logging silenced globally, `sys.path` changes with generic names,
   environment variables, monkey-patching Slicer or VTK).
3. **packaging**: the extension can be built and loaded from the catalog entry: CMake installs every Python file
   the modules import; listed files exist; `EXTENSION_DEPENDS` matches the entry's `build_dependencies`; the
   revision exists; nothing large or binary that should be downloaded on demand is committed.
4. **license**: terms that allow distribution of the extension and of anything it bundles or downloads
   (model weights, datasets, third-party code). Unfamiliar licenses are not defects; missing or prohibiting
   terms are. Note non-commercial or research-only terms for users.
5. **soundness**: does the code do what it claims, robustly? Slicer conventions: `ScriptedLoadableModule`
   structure; heavy imports inside functions rather than at module import; long work off the GUI thread or with
   progress; observers removed on cleanup; files written to user-chosen or temporary folders; errors reported to
   the user rather than swallowed; parameter nodes for state. Ordinary bugs are `minor` or `concern`, not safety.
6. **utility**: what it is for and how well a user can use it: documentation and a tutorial or sample data,
   tests, maintenance activity, overlap with existing Slicer modules or extensions, clinical-use disclaimers
   where relevant, model provenance and validation for AI tools.

Finding severities: `blocking` (must be fixed before the extension is offered to users: a concrete path to harm,
broken loading, or no distribution permission), `major` (should be fixed soon), `minor`, `info`.

Overall: `no concerns`, `minor issues`, `needs fixes` (blocking or major issues), `do not accept` (malicious,
deceptive, or fundamentally unsafe), or `incomplete` (you could not inspect enough to judge).

Evidence rules:
- Cite the file path and line numbers you read, and copy one to five lines exactly into `evidence`. Findings
  with quotes that are not in the file are discarded by an automatic check.
- Distinguish what you verified from what you suspect. Unavailable evidence is not a defect; list it in
  `not_checked`.
- Keep `explanation` concrete: what happens, to whom, under which conditions.
- Do not report style, naming, or missing screenshots as anything above `info`.

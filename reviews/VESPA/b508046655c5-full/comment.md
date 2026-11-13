> *This review was done by AI models (Claude Sonnet 5.5, GPT-6.1 Terra, Gemini 4 Argon) through the Slicer extensions dashboard, and checked by the maintainer posting it. The extension source was read, not executed. Full review: https://pieper.github.io/extensions-dashboard/review.html?ext=VESPA&dir=b508046655c5-full*

Thanks for VESPA!

Suggestions for a later update:

- `SlicerVESPA/vespaRepairMesh.xml`: The CLI identifies its license as LGPL, whereas README.md lines 65–69 says the distributed CGAL-linked CLI binaries are GPLv3. The other CLI XML files have the same LGPL label, potentially misleading users about binary redistribution obligations. Align the displayed CLI license metadata with the actual executable license and include the appropriate license notices in distribution materials.
- `SlicerVESPA/vespaRepairMesh.h`: The repaired polydata contains only rebuilt geometry; input point, cell, and field data arrays are not copied. Users processing models with scalar measurements, labels, or other attributes receive a mesh without those arrays. Preserve or remap attributes where feasible, and explicitly warn users about arrays that cannot be retained across topology changes.
- `SlicerVESPA/vespaRepairMesh.cxx`: When repair cannot close an input surface, the CLI only logs a warning and returns success if the output writes, although its XML describes a closed output. A user can consequently mistake an open surface for a successfully repaired closed one. Return an explicit failure for a nonclosed result, or clearly expose partial success and describe that closure is not guaranteed.

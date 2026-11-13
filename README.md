# Slicer extensions dashboard

A public dashboard for the [Slicer Extensions Index](https://github.com/Slicer/ExtensionsIndex) with two parts:

- **Pull request triage** for maintainers: every open extension pull request, whose turn it is, what the next
  step is, and mechanical checks of each new submission's source.
- **AI reviews** for maintainers and the Slicer community: several AI models from different vendors review each
  extension independently. Their disagreements are shown first, for a human to settle.

Site: https://pieper.github.io/extensions-dashboard/ · Reviews: https://pieper.github.io/extensions-dashboard/reviews.html

This is an experiment by Steve Pieper, built with Claude (Anthropic's AI assistant). If the Slicer developers find
it useful, it may move to the Slicer organization.

## How the AI reviews work

1. **What gets reviewed.** Every new or updated extension pull request gets the *full panel*: three capable models
   from different vendors. The 278 extensions already in the catalog get a cheaper *first pass*: three smaller
   models, in priority order (developers outside the long-standing Slicer groups first, newest first). Anything the
   first pass flags, or where its models disagree, goes on to the full panel. Maintainers can request a review of
   any extension by running the *AI reviews* workflow with its name.
2. **How a model reviews.** Each model gets the review policy of the Extensions Index
   ([AGENTS.md](https://github.com/Slicer/ExtensionsIndex/blob/main/AGENTS.md), fetched fresh for every review),
   this repository's [rubric](review/rubric.md), the catalog entry, and the extension's files. It can list, read
   and search files, and nothing else. **Extension code is never run, installed or imported.** It must submit a
   structured review: ratings for safety, environment, packaging, license, soundness and utility, plus findings
   that each cite a file, lines and an exact quote.
3. **Checking the models.** Every quoted line is looked up in the source automatically; findings whose quotes
   are not there are marked *unverified*. Findings from different models are matched up and sorted into: all
   models agree, some models raised it, and disputed (different severities, or a serious finding only one model
   raised). For disputes, each full-panel model sees the others' findings and must agree or disagree after
   checking the code.
4. **Human review.** Each full-panel review opens an issue in this repository listing the disputed findings.
   A maintainer checks them, comments, adds a `verdict: ok`, `verdict: concerns` or `verdict: blocking` label and
   closes the issue. The dashboard shows a verdict only once a maintainer has given one; until then reviews are
   labeled as unreviewed AI output. Nothing is posted to the Extensions Index automatically.

Results are committed under [`reviews/`](reviews) (one folder per extension and commit) and published with the site.

## Cost and keys

Reviews use [OpenRouter](https://openrouter.ai) with the `OPENROUTER_API_KEY` repository secret. The key has a
spending limit on OpenRouter, and [`review/panels.json`](review/panels.json) sets a monthly budget: catalog work
is spread evenly over the month, and pull request reviews come first. Each review page shows what it cost.

## Security

- The review job is the only one with the OpenRouter key. It has read-only repository access, downloads each
  extension as an archive, and only reads it.
- The publish job, which commits results and opens issues, never sees the key or the extension source. It treats
  the review job's output as untrusted: it checks names and fields and rebuilds the reports itself.
- Text written by models is shown as text on the site, never as HTML, and is kept from mentioning people or
  linking issues when posted on GitHub.
- Workflows run on a schedule or by hand; nobody outside the repository can trigger them.

## Layout

- `dashboard/`: the page generator (`generate.py`), the static site (`site/`), and `maintainers.txt`.
- `review/`: the review pipeline (`plan.py` → `run_queue.py`/`run_review.py` → `publish.py`), the read-only
  reviewer (`agent.py`), the comparison (`compare.py`), the rubric, and the model panels.
- `.github/workflows/`: `dashboard.yml` (every 10 minutes), `review.yml` (hourly, or on demand), `models.yml`
  (lists the models OpenRouter offers and checks the panels).

## Run locally

```
python3 dashboard/generate.py --out /tmp/site --reviews reviews/index.json
cp dashboard/site/* /tmp/site/ && cp -r reviews /tmp/site/
python3 -m http.server -d /tmp/site 8000
```

A GitHub token comes from `GITHUB_TOKEN` or `gh auth token`. To review one extension locally, set
`OPENROUTER_API_KEY` and run `review/run_review.py --item item.json --panel triage --out /tmp/out`.

## License

Apache 2.0.

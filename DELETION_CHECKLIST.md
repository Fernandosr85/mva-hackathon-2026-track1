# Data deletion checklist

Compliance record for the Data Use terms of *Rare Disease, Real Kid: MVA Hackathon 2026*.

**Deadline:** deletion within **30 days of the hackathon close (24 October 2026)** —
that is, **by 23 November 2026**.

**Attestation:** once every item below is done, email
`RarediseaserealkidMVAhackathon2026@synapse.org` stating the systems cleared and naming
the provider and data-handling configuration of every external tool used. The Official
Rules take precedence over the dataset README, which lists a different address and is
out of date.

**Scope.** Deletion must cover every environment under the submitter's control: local
machines, cloud instances, notebooks, private repositories, and any intermediate or
derived dataset.

This file contains no patient data. It is process documentation and is committed
deliberately.

---

## 1. Controlled data on local disk — `C:\KID`

| | Item | Contents |
|---|---|---|
| `[ ]` | `C:\KID\results.zip` | VCF, tabix index, phenotype `.docx`, `panel_variants.tsv`, HF cache |
| `[ ]` | `C:\KID\results (1).zip` | same contents as above |
| `[ ]` | `C:\KID\rare-disease-real-kid.ipynb` | executed notebook; genotype tables in saved cell outputs |

Deleted on: ____________  ·  Verified empty by: ____________

## 2. Duplicate copies in synced storage — `C:\Users\admin\OneDrive\Área de Trabalho\KID`

**Status as of 2 September 2026: still present.** The move to `C:\KID` was a copy, not a
move. Both locations hold byte-identical files (same sizes, same modification times), so
the synced copy still exists and OneDrive may hold server-side copies of it.

| | Item |
|---|---|
| `[ ]` | `...\OneDrive\Área de Trabalho\KID\results.zip` |
| `[ ]` | `...\OneDrive\Área de Trabalho\KID\results (1).zip` |
| `[ ]` | `...\OneDrive\Área de Trabalho\KID\rare-disease-real-kid.ipynb` |

Deleted on: ____________  ·  Verified empty by: ____________

## 3. Environments outside those folders

| | Environment | What to confirm |
|---|---|---|
| `[ ]` | `/kaggle/working/data/` | Removed with the session, but confirm no session still holds it |
| `[ ]` | Kaggle saved notebook versions | Confirm **no committed Kaggle notebook version carries saved outputs**. Outputs embed per-variant genotype tables. Delete or re-save cleared any version that does |
| `[ ]` | OneDrive server-side recycle bin | Empty it after the section 2 deletion — deleting a synced file leaves a server copy |
| `[ ]` | OneDrive version history | Check retained previous versions of the section 2 files on the server |
| `[ ]` | Windows Recycle Bin | Empty after the local deletions in sections 1 and 2 |

Completed on: ____________

## 4. Attestation

| | Step |
|---|---|
| `[ ]` | All items in sections 1–3 complete and verified |
| `[ ]` | Attestation email sent to `RarediseaserealkidMVAhackathon2026@synapse.org` |
| `[ ]` | Email states the systems cleared |
| `[ ]` | Email names the provider and data-handling configuration of each external tool (Ensembl REST; Anthropic API, Claude, commercial terms, no training on customer content) |
| `[ ]` | Copy of the sent attestation retained |

Sent on: ____________

## 5. Not on the DELETE list — retained deliberately

For the record, so that a later reader does not assume these were missed. None contains
patient-derived data.

- `C:\KID\fernandosr85_mva_track1_*.ipynb` (v3–v9, `audited`, `(3)`, `(1)`) — draft
  notebooks, all with cell outputs cleared. Source only.
- `C:\KID\fernandosr85_track1_report.md` and `fernandosr85_track1_report_final.md` —
  methods reports, named variants only.
- This repository — code, report, and the three KEEP-list submission CSVs, which carry
  annotation and disposition but no genotype, depth, allele-fraction or phase fields.

Per the Official Rules, code, models and results may be shared publicly at any time. The
deletion obligation applies to the controlled dataset and material derived from it, not
to this repository.

## 6. Repository visibility

| | Step |
|---|---|
| `[ ]` | Repository is **private** until the hackathon closes |
| `[ ]` | Switch to public after the close, once sections 1–3 are complete |
| `[ ]` | Re-run `python scripts/strip_outputs.py --check notebooks/mva_track1_analysis.ipynb` before making the repository public |

# Rare Disease, Real Kid: MVA Hackathon 2026 — Track 1

Candidate variant identification in a proband with Mosaic Variegated Aneuploidy: a
pathogenic *BUB1B* allele recovered independently from single-sample WGS. *BUB1B*/MVA1
is strongly favoured as the etiologic locus; the causal second allele and phase remain
unresolved.

**Submitter:** Fernando (Hugging Face: `fernandosr85`) — Independent Researcher, São Paulo, Brazil
**Approach:** `bub1b-panel-acmg` — spindle-checkpoint panel triage with calibrated ACMG/AMP interpretation
**Reference build:** GRCh38
**Licence:** [CC BY 4.0](LICENSE)

---

## Data access notice

**This repository contains no patient data.**

The genomic data for this challenge comes from a real child and is controlled. It is
released under a WCG IRB protocol and is available only through the hackathon's gated
Hugging Face dataset (`SageBio/mva-hackathon-2026-data`). Nothing derived from the
child's genome is tracked here: no VCF or tabix index, no BAM/CRAM or FASTQ, no
phenotype document, no per-variant genotype tables, and no notebook cell outputs.

Anyone reproducing this work must **request access to the dataset and accept the terms
themselves**. Access cannot be obtained from this repository, and the data must not be
redistributed. Participants agree, among other conditions, not to attempt to recontact
the data subject, the family, or any point of contact at the MVA Society.

`.gitignore` blocks the relevant file types, including archives, which would otherwise
hide every other rule. `scripts/strip_outputs.py --check` re-verifies the notebook
before any future commit.

## Result

Two rows are submitted. Both share the same established first allele.

| Rank | Established allele | Candidate second allele | EPCR |
|---|---|---|---|
| 1 | `chr15:40209701 T>G` — `c.2210T>G` `p.Leu737Ter` | `chr15:40220612 T>G` — `c.3006T>G` `p.Asn1002Lys` (missense) | 0.60 |
| 2 | `chr15:40209701 T>G` (same allele) | `chr15:40216470 A>G` — `c.2679-1026A>G` (deep intronic) | 0.25 |

**These are competing hypotheses about the same second allele, not two independent
findings.** They are mutually exclusive, which is why their probabilities sum to less
than one. The residual **0.15** is the probability that the second allele is neither of
them — an uncalled variant, a CNV/SV, a regulatory change, or a locus outside the panel.

The analysis keeps three evidence states separate, and the distinction is the substance
of the result:

- **Established** — a pathogenic *BUB1B* allele is present, recovered independently from
  the raw WGS. `c.2210T>G` `p.Leu737Ter` is a nonsense variant in exon 17 of 23,
  predicted to trigger nonsense-mediated decay, in a gene where loss of function is the
  established MVA1 mechanism. PVS1 applies on the sequence evidence alone: 8 points on
  the Tavtigian scale, Likely Pathogenic. NCBI ClinVar separately classifies this exact
  variant as Pathogenic for MVA syndrome 1 (Variation ID 533901, rs759242053); that
  external assertion is reported alongside the internal score, not folded into it.
- **Strongly favoured, incomplete** — *BUB1B*/MVA1 is the leading etiologic model.
- **Unresolved** — which second allele is causal, and whether either is *in trans*.

Both second-allele candidates are classified **VUS**. This is deliberately not phrased as
proven compound heterozygosity.

## Repository contents

```
notebooks/mva_track1_analysis.ipynb   analysis, committed with all outputs cleared
submission/fernandosr85_bub1b-panel-acmg_audited.csv  ranked candidate list, as scored
submission/fernandosr85_track1_report_v2.md           methods report, as submitted
submission/fernandosr85_methods_description.xlsx      methods description form, as submitted
submission/track1_submission_manifest.json            manifest: frozen filenames and SHA-256
submission/annotated_candidates.csv   KEEP-list annotation artefact
submission/deep_intronic_candidate.csv KEEP-list annotation artefact
scripts/strip_outputs.py              notebook output stripper and pre-commit check
```

The three submitted artefacts are kept under the exact filenames the manifest freezes,
and their bytes are unmodified, so every declared SHA-256 verifies against the files in
this repository:

```bash
sha256sum submission/fernandosr85_track1_report_v2.md submission/fernandosr85_methods_description.xlsx submission/fernandosr85_bub1b-panel-acmg_audited.csv
```

Compare the three digests against `report_sha256`, `methods_sha256` and
`predictions_sha256` in `submission/track1_submission_manifest.json`.

The predictions file is the scored submission, moved to this path but never
regenerated. Rebuilding it from the notebook could reorder rows or reformat floats and
produce a different file with no visible change, which is why the manifest permits
renaming and forbids regeneration.

The manifest records one reissue. The methods workbook carried a third party's name in
its document metadata, left there by the template; it was removed before submission, so
`methods_sha256` changed and the superseded digest is kept in the manifest alongside the
reason. The 13 Track 1 and 11 Track 2 answers are byte-identical across that edit.

## Reproducing the analysis

1. **Request access** to the gated dataset `SageBio/mva-hackathon-2026-data` on Hugging
   Face and accept the terms. This is a decision each user makes for themselves.
2. **Set `HF_TOKEN`** in Kaggle Secrets (Add-ons → Secrets) and enable Internet in the
   notebook settings. The notebook reads the token from Secrets into the environment;
   never paste a token into a cell, since cell source is saved with the notebook.
   Outside Kaggle, set the `HF_TOKEN` environment variable directly and skip that cell.
3. **Run the notebook top to bottom.**

Two things about the run are worth knowing in advance:

- It downloads **~318 MB** — the VCF, its tabix index, the phenotype document and the
  dataset README. It **deliberately skips the 8 FASTQ lanes (~85 GB)**, which this
  analysis does not need. There is no BAM/CRAM in the release, so aligned-read
  inspection would require realignment from FASTQ; the variant-ranking workflow does not
  depend on it.
- It makes **live Ensembl REST calls** for gene structure and VEP annotation. Panel
  completeness is asserted rather than warned about: if the 22-gene panel does not fully
  resolve, the notebook **raises** rather than continuing. This exists because an earlier
  run silently resolved 20 of 22 genes after two transient API errors, shifted every
  downstream count, and reported success.

Dependencies are in [`requirements.txt`](requirements.txt). `kaggle_secrets` is supplied
by the Kaggle runtime, not by pip.

## Submission artefacts, and why they are publishable

The three CSVs in `submission/` carry **annotation and disposition only**: gene,
coordinate, consequence, HGVS, gnomAD frequency, rsID, REVEL, entry route, audit status
and the reason for it. They contain **no genotype, depth, allele-fraction or phase
fields**.

That distinction is what makes them KEEP-list material rather than DELETE-list material.
A handful of named variants reported as findings is a result; a full per-variant genotype
table is the dataset in another file format. The genotype table this analysis builds
(`panel_variants.tsv`) is written to the controlled-data directory, is ignored by git,
and is not in this repository.

- `annotated_candidates.csv` — the corrected shortlist. Each variant carries its entry
  route (`rarity`, `clinical_flag_only`, or both), an explicit disposition, and the
  reason for that disposition, plus any variant the superseded dbSNP-gated filter
  admitted that the corrected filter drops.
- `deep_intronic_candidate.csv` — the single named deep-intronic hypothesis, with an
  explicit statement that no splice prediction was obtained.

### Notebook outputs

The notebook is committed with **every code cell output removed and every
`execution_count` reset to null**. This is a compliance requirement, not an oversight:
executed outputs embed per-variant genotype tables, which are DELETE-list material, and
this repository becomes public after the hackathon closes.

Verify before any future commit:

```bash
python scripts/strip_outputs.py --check notebooks/mva_track1_analysis.ipynb
```

It exits non-zero if any output remains, so it can be wired into a pre-commit hook. To
strip a notebook:

```bash
python scripts/strip_outputs.py in.ipynb out.ipynb
```

## Limitations

Stated plainly, because the boundary between what is established and what is inferred is
the point of this submission.

- **Phase is unresolved.** The two coding candidates are **10,911 bp apart** and share no
  read-backed `PID` phase block. Short reads from a single sample cannot span that
  distance. *Trans* is inferred from mechanism and recessive phenotype; **it is not
  demonstrated.** This is a property of the data, not a pipeline failure. Trio
  sequencing, long reads or linked reads would resolve it directly. `PM3` is not applied.
- **The second allele has two competing hypotheses that current computational tools
  cannot discriminate.** The missense `p.Asn1002Lys` has a REVEL of 0.472, which on the
  full Pejaver ladder qualifies for no criterion at any evidence strength on either side
  — PP3 and BP4 are both withheld rather than forced. The deep-intronic
  `c.2679-1026A>G` has no splice criterion assigned, because the public Ensembl REST
  endpoint does not expose the SpliceAI plugin and returned `invalid_field`. Pseudo-exon
  activation remains an untested mechanistic hypothesis. The discriminating experiments
  differ: a mitotic-checkpoint functional assay for the missense, dedicated splice
  prediction plus patient RNA-seq or a minigene assay for the deep-intronic candidate.
- **No CNV/SV caller was run.** A large intragenic *BUB1B* deletion is argued against
  from marker patterns, not excluded: with a median inter-marker gap of 3.9 kb, a focal
  deletion smaller than that can sit between markers undetected.
- **Allele balance does not prove germline origin**, and it does not test the chromosomal
  mosaicism that defines MVA.
- **Negative findings are scoped to what was actually tested.** No qualifying coding or
  splice candidate was found for *CEP57* or *TRIP13*, but the analysis covers short
  variants only; this is not a genetic exclusion of MVA2 or MVA3.

## Tooling declaration

In the format requested by the Sage Privacy Office. Both external services are
**processors, not recipients**: each returns a result, acquires no rights over the input,
and cannot use it for its own purposes.

- **Ensembl REST** (`rest.ensembl.org`) — gene structure and VEP annotation, including
  gnomAD frequency, `check_existing`, and REVEL via dbNSFP. Public academic API. Gene
  symbols and variant coordinates only.
- **Anthropic API, Claude** — analysis design and code review. Commercial terms; no
  training on customer content.
- **No external splice-prediction service was called.** That capability is present in the
  notebook but disabled by default and requires an explicit operator decision after a
  terms review.

## Data retention and embargo

- **Deletion.** All artefacts derived from the child's genome are confined to a single
  working directory and will be deleted **within 30 days of the hackathon close**, across
  every environment controlled by the submitter — local machines, cloud instances,
  notebooks, private repositories, and any intermediate or derived dataset. Deletion will
  be attested by email to `RarediseaserealkidMVAhackathon2026@synapse.org`, stating the
  systems cleared and naming the provider and data-handling configuration of every
  external tool used. The inventory and its status are tracked in
  [`DELETION_CHECKLIST.md`](DELETION_CHECKLIST.md).
- **Embargo.** Code, models and results may be shared publicly at any time. A
  peer-reviewed manuscript using this dataset may **not** be submitted until the
  organisers publish their summary report or preprint. Conference abstracts and posters
  require prior written approval.

## Citation and acknowledgement

This work was made possible through the Hackathon, organized by Sage Bionetworks in
partnership with the MVA Society, Hugging Face, and BEACON (The Benchmarking,
Evaluation, and Assessment Consortium for Science), with prize sponsorship from AWS and
Anthropic. We are deeply grateful to the child and their family who generously
contributed their data and their story to advance research into this rare disease. We
acknowledge their trust in making this Hackathon possible.

**Dataset citation.** Any publication arising from this work must cite the dataset using
the reference given on the hackathon's Synapse page as it stands at the time of
publication.

**Re-identification.** No public communication about this work may include information
capable of re-identifying the child or the family beyond what the family has already made
public through their own posts.

Hackathon submissions, including this one, are released under **CC BY 4.0**.

## References

Full reference list in [`submission/fernandosr85_track1_report_v2.md`](submission/fernandosr85_track1_report_v2.md). The primary
sources are Hanks et al. (*Nat Genet* 2004) for biallelic *BUB1B* and MVA, Richards et
al. (*Genet Med* 2015) for ACMG/AMP, Tavtigian et al. (*Genet Med* 2018) for the point
framework, and Pejaver et al. (*Am J Hum Genet* 2022) for the REVEL calibration ladder.

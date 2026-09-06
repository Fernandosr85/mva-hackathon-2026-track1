# Rare Disease, Real Kid — MVA Hackathon 2026 · Track 1 Report

**Submitter:** Fernando (HF: `fernandosr85`) · Independent Researcher, São Paulo, Brazil
**Approach:** `bub1b-panel-acmg` — spindle-checkpoint panel triage with calibrated ACMG/AMP interpretation
**Reference build:** GRCh38
**Repository:** `https://github.com/Fernandosr85/mva-hackathon-2026-track1` *(private at submission; see Repository access below)*

---

## 1. Summary

A pathogenic *BUB1B* allele was recovered independently from the WGS. *BUB1B* / MVA1
is strongly favoured as the etiologic locus. **The dataset does not resolve the causal
second allele, and it does not establish phase.**

| Rank | Established allele | Candidate second allele | EPCR |
|---|---|---|---|
| 1 | `chr15:40209701 T>G` — `c.2210T>G` `p.Leu737Ter` | `chr15:40220612 T>G` — `c.3006T>G` `p.Asn1002Lys` | 0.60 |
| 2 | `chr15:40209701 T>G` (same allele) | `chr15:40216470 A>G` — `c.2679-1026A>G` | 0.25 |

Residual probability that the second allele is neither of these: **0.15**. The two rows
are mutually exclusive hypotheses about the same allele, so their probabilities sum to
less than one and the remainder is reserved for an uncalled variant, a CNV/SV, a
regulatory change, or a locus outside the panel.

This is deliberately not phrased as proven compound heterozygosity. Three evidence
states are kept separate throughout:

- **Established** — a pathogenic *BUB1B* allele is present, independently recovered.
- **Strongly favoured, incomplete** — *BUB1B*/MVA1 is the leading etiologic model.
- **Unresolved** — which second allele is causal, and whether either is *in trans*.

## 2. Framing

The clinical diagnosis was supplied, so the task was locus and allele discrimination
rather than disease discovery. Recessive MVA is genetically heterogeneous; a useful
analysis has to distinguish among candidate loci and then determine whether the data
support a complete biallelic genotype. The second half of that is where this case
stops, and saying so precisely is the substance of the result.

## 3. Data and reference audit

Of the ~85 GB release the analysis used 318 MB: the VCF, its tabix index, the
phenotype document and the README. No BAM/CRAM is provided, so aligned-read inspection
would require realignment from FASTQ, which the variant-ranking workflow did not need.

The header names the exact reference —
`GCA_000001405.15_GRCh38_no_alt_analysis_set_plus_hs38d1_maskedGRC_exclusions_v2_no_chr.fasta`
— a no-alt GRCh38 analysis set with hs38d1 decoy, no `chr` prefix, `M` for
mitochondria, called with Sentieon 202308.02 and filtered with GATK VariantFiltration.

Two header facts constrained the design. The VCF carries **caller metrics only**: its
`AF` field is the within-sample allele fraction with AN=2, never a population
frequency, so filtering on it for rarity would silently remove nothing. And `PGT`/`PID`
are present, which in a single sample without parental data is the only available route
to *cis*/*trans*.

## 4. A design failure, and what correcting it exposed

The first version of this pipeline used dbSNP membership (`DB`) as a proxy for rarity.
That proxy is invalid, and it failed in the most consequential way possible: the lead
pathogenic variant **is** rs759242053, yet this VCF carries `DB=False` at that site. A
correctly populated flag would have removed the answer. The shortlist survived by
accident.

The corrected design annotates first and filters afterwards. All 61 PASS coding and
canonical splice-region calls across the panel go to Ensembl VEP with gnomAD frequency
and `check_existing`; rarity is decided on the returned population frequency; `DB` is
retained only as diagnostic metadata and never participates in selection.

**Removing the gate surfaced a candidate the old filter had hidden**, and the second
finding is about annotation itself.

*MAD1L1* `c.175C>T` `p.Arg59Cys` (rs121908982) entered the shortlist — a variant in
MVA7, an established MVA locus, carrying a Pathogenic token in VEP's `clin_sig`. It
entered on that clinical token, not on rarity.

Two independent reasons remove it, and the order is worth stating because only one of
them is what the algorithm acted on.

**Population frequency was decisive.** At a gnomAD frequency of 0.46%, Hardy–Weinberg
predicts ~169,000 homozygotes worldwide against a stated MVA prevalence ceiling of
fewer than 50 cases — a discrepancy of roughly 3,400-fold. No fully penetrant recessive
allele for this disease can be that common, whatever a database asserts. Its REVEL of
0.267 reaches only BP4_Supporting, which on its own would **not** have excluded it.

**Clinical context was something the automated field could not convey.** Direct review
shows the Pathogenic assertion on this allele is recorded in OMIM 602686 as allelic
variant .0002, *"PROSTATE CANCER, SOMATIC"* (Tsukasaki et al., 2001). The *MAD1L1*
alleles reported for MVA7 are different variants entirely (.0003 Gln66Ter, .0004
Glu628Ter). VEP's `clin_sig` is allele-specific but neither condition-specific nor
origin-specific, so a somatic cancer submission is indistinguishable in that field from
a germline assertion for the disease under study.

The pipeline was changed because of this. A pathogenic token now **flags a variant for
review** and records its entry route (`rarity`, `clinical_flag_only`, or both); it
cannot rescue a variant on its own. Confirmation of germline status and a relevant
condition is a recorded human decision in an explicit, initially empty allowlist. Under
the old logic, a rare variant admitted solely by a somatic-context assertion would have
been carried forward silently.

There is also no second *MAD1L1* allele, so no biallelic genotype exists there to
evaluate.

## 5. Locus-level QC: three signals, three different resolutions

Per-gene heterozygosity is a measurement, not an exclusion rule. Low heterozygosity can
reflect hemizygosity, autozygosity, LD, paralogy, mapping failure or copy loss, and
these were separated before any label was applied.

**Chromosome complement.** From the VCF call pattern alone: chr15 heterozygous fraction
0.614 at median depth 43; chrX 0.062 at median depth 21; chrY 9,732 PASS non-reference
calls. X-to-autosome depth ratio 0.488. This is an **XY-like** pattern, reported as a
call-pattern observation rather than a clinical sex determination.

That resolves *STAG2*, whose heterozygous fraction of 0.008 an earlier version of this
analysis wrongly labelled a mapping artefact. *STAG2* is X-linked; in an XY proband it
is hemizygous, and a diploid caller represents hemizygosity as homozygosity. The
retraction does not retire the locus — hemizygosity means any loss-of-function allele
there would be unbuffered — so it was checked rather than assumed: *STAG2* contributed
**0** PASS coding/splice calls to the annotation pool. That is now a stated negative.

**Copy number inside homozygosity blocks.** An intragenic LOH scan found long
homozygous runs, and gene-level mean depth cannot settle what causes them: a deletion
confined to part of a gene is diluted by the rest of the gene's coverage. The
discriminating measurement is local — depth inside the block against its immediate 50 kb
flanks. A heterozygous deletion removes one haplotype and halves depth; copy-neutral
homozygosity leaves it intact.

| Gene | Block | Markers | Size | DP inside / flank | Ratio | Call |
|---|---|---|---|---|---|---|
| STAG2 | chrX:124,188,083–124,409,624 | 137 | 221.5 kb | 21.0 / 21.0 | 1.000 | copy-neutral |
| KNL1 | chr15:40,595,787–40,627,946 | 47 | 32.2 kb | 37.0 / 42.0 | 0.881 | copy-neutral |
| NDC80 | chr18:2,568,166–2,572,688 | 19 | 4.5 kb | 39.5 / 42.0 | 0.940 | copy-neutral |
| MAD1L1 | chr7:1,944,487–1,950,088 | 29 | 5.6 kb | 38.0 / 41.0 | 0.927 | copy-neutral |

All four are copy-neutral. *STAG2* carries a caveat: on an already hemizygous
chromosome a deletion drives depth toward zero rather than toward half, so a ratio near
1.0 there means the block is uniform within a single-copy chromosome, not that a
haplotype is intact.

**KNL1 is therefore a localized homozygosity signal of resolved copy number and
unresolved mechanism.** 47 consecutive apparently homozygous markers spanning 32.2 kb,
copy-neutral, in a diploid autosomal region. It is **not** called a run of homozygosity:
conventional ROH analysis uses minimum segments of several hundred kb to megabases,
precisely so that short haplotype and LD blocks are not mislabelled as autozygosity, and
32 kb is far below that. A local homozygous haplotype, LD structure and true autozygosity
all remain compatible. All **6** *KNL1* coding/splice calls entered the corrected
annotation pool and none survived the shortlist.

## 6. The lead allele

*BUB1B* `c.2210T>G` `p.Leu737Ter` is a nonsense variant in exon 17 of 23, sufficiently
upstream of the penultimate junction for predicted nonsense-mediated decay, in a gene
where loss of function is the established MVA1 mechanism. **PVS1** applies on the
sequence evidence alone: 8 points on the Tavtigian scale, **Likely Pathogenic**.

`PM2` is deliberately withheld. The current ClinVar record warns that population
frequency at this position is unreliable, and resting a criterion on a third party's
claim about data quality would be weak grounds. The decision was therefore tested
rather than asserted: with PM2_Supporting the score is 9 points, without it 8, and the
classification is Likely Pathogenic either way. The call does not depend on that
judgement.

Separately, NCBI ClinVar classifies this exact variant as **Pathogenic for Mosaic
Variegated Aneuploidy syndrome 1** (rs759242053, Variation ID 533901, RCV000641226.9).
This is reported as an external clinical assertion and is **not** double-counted as an
ACMG criterion in the internal score. Keeping the two separate matters here: the
analysis recovered the correct known pathogenic allele from raw WGS independently,
while preserving the distinction between its own evidence calculation and a database
classification.

## 7. The second allele: two hypotheses, two different missing evidence layers

**`c.3006T>G` `p.Asn1002Lys`** — missense, absent from gnomAD, PM2_Supporting only,
**VUS**. REVEL is 0.472, which on the full Pejaver ladder qualifies for **no criterion
at any evidence strength on either side** — it fails PP3_Supporting (≥0.644) and
BP4_Supporting (≤0.290) alike. That is a stronger statement than falling below a
cut-off: a predictor calibrated at four strengths per side has nothing to say about
this variant. PP3 and BP4 are both withheld rather than forced. No hypomorphic effect
is claimed; an earlier version of this report argued from exon position and
nonsense-mediated decay, which is not a valid argument for a missense substitution and
has been removed.

**`c.2679-1026A>G`** — deep intronic, 1,026 bp from the intron 20 acceptor, absent from
gnomAD/dbSNP, PM2_Supporting only, **VUS**. No splice criterion is assigned. An earlier
version attributed this to SpliceAI's `-D=50` setting being a ±50 bp window from the
exon; that is incorrect — `-D` is the maximum distance between the variant and a
gained or lost splice site, and a deep-intronic variant creating a cryptic site near
itself is scoreable. The actual limitation is that the public Ensembl REST endpoint does
not expose the SpliceAI plugin and returned `invalid_field`. Pseudo-exon activation
remains a mechanistic hypothesis, untested for this nucleotide change.

The distinguishing experiments are different for each: a **mitotic-checkpoint functional
assay** for the missense, **dedicated splice prediction plus patient RNA-seq or a
minigene assay** for the deep-intronic candidate.

## 8. Phase — a physical limit, stated as one

The two coding candidates are **10,911 bp apart** and share no read-backed `PID` phase
block. Short reads from a single sample cannot span that distance. This is a property of
the data, not a pipeline failure.

*Trans* is inferred from mechanism and recessive phenotype. **It is not demonstrated.**
Trio sequencing, long reads or linked reads would resolve it directly.

`PM3` is treated carefully rather than used to close the gap. Its strength depends on
the classification of the other allele and on phase evidence; with the second allele
unresolved and *trans* unestablished, it is not applied. The earlier framing that this
case is "one point short of Pathogenic" oversimplified the criterion and has been
withdrawn.

## 9. Negatives, each scoped to what was actually tested

- **CEP57 / TRIP13** — no qualifying coding or splice candidate under the corrected
  filter. This is not a genetic exclusion of MVA2 or MVA3: the analysis covers short
  variants only and does not address CNV/SV or untested deep-intronic mechanisms.
- **STAG2** — the "mapping artefact" label is withdrawn; the profile is explained by
  X hemizygosity in an XY-like complement, and the locus contributed no coding call.
- **KNL1** — copy-neutral localized homozygosity; six coding calls evaluated, none
  surviving. Mechanism unnamed.
- **A large intragenic deletion in *BUB1B* is argued against.** 16 markers across
  64.2 kb, heterozygous calls interleaved throughout, longest homozygous run 2 markers
  covering 4.8 kb (7.5% of the marker span). No extended homozygous block exists. The
  honest limit: with a median inter-marker gap of 3.9 kb, a focal deletion smaller than
  that can sit between markers undetected, and no depth-based CNV caller was run.
- **Allele balance is compatible with constitutional heterozygosity.** All three
  candidates were tested against a binomial expectation of 0.5 and placed in the
  empirical distribution of 1,583 high-quality heterozygous panel calls (median 0.500;
  5th/95th percentile 0.356/0.630). All p > 0.01, the lowest being the deep-intronic
  candidate at 18/46 reads (p = 0.184, 10th percentile). This does **not** prove
  germline origin, and it does not test the chromosomal mosaicism that defines MVA.
- **A frequency-filter failure was caught internally.** A *BUB3* 3′UTR deletion passed
  the original "absent from dbSNP" filter because the `DB` flag does not reliably
  annotate indels; VEP showed it at 21% in gnomAD. It is dropped by the corrected filter
  and recorded as such in the audit artefact.
- ***SGO1* `p.Thr425Ala` is excluded on positive benign evidence**, not on absence of
  pathogenic evidence: REVEL 0.011 reaches BP4_Strong on the Pejaver ladder.

## 10. Phenotype and family history

Rhabdomyosarcoma, severe intrauterine growth restriction and very low birth weight,
short stature, failure to thrive with skeletal muscle atrophy, nephrocalcinosis,
prematurity, and recurrent parental miscarriage.

Biallelic *BUB1B* deficiency gives a coherent mechanistic account of the chromosomal
instability and cancer predisposition. The recurrent pregnancy-loss history — flagged by
the organisers as phenotypic input rather than background — is biologically compatible
with a chromosome-segregation disturbance in a heterozygous carrier parent. It is used
as **supportive mechanistic context, not as proof**; the contribution of heterozygous
*BUB1B* variants to recurrent pregnancy loss remains uncertain in the literature.

Two features stay open rather than being absorbed into the model. **Microcephaly is
absent** from the supplied phenotype despite being frequent in MVA1. **Congenital
nephrocalcinosis** is not a canonical *BUB1B* feature and may represent a secondary
finding.

## 11. Reproducibility, auditability and data handling

The notebook carries **no saved cell outputs**. That is a compliance choice, not a
missing step: executed outputs contain per-variant genotype tables, which are DELETE-list
material under the challenge data-use regime, and the repository becomes public after the
hackathon closes.

Auditability is preserved through small named-variant KEEP-list artefacts:

- `annotated_candidates.csv` — the corrected shortlist, each variant carrying its entry
  route, an explicit disposition and the reason for it, plus any variant the old
  dbSNP-gated filter admitted that the corrected filter drops.
- `deep_intronic_candidate.csv` — the single named deep-intronic hypothesis with its
  annotation and an explicit statement that no splice prediction was obtained.

Neither contains genotype, depth, allele-fraction or phase fields. Both are findings
rather than a genotype table.

Two internal-consistency measures are worth naming because they closed real defects
found during audit. The Pejaver threshold ladder is **defined once** and consulted by
both candidate triage and ACMG interpretation, so the two cannot disagree about where a
threshold sits. And EPCR values are **computed and asserted in code**, with an assertion
that mutually exclusive hypotheses cannot sum above 1.0, so the prose and the submission
file cannot drift apart.

**Tooling declaration.** External services used here are processors, not recipients,
under the test set out by the Sage Privacy Office: each returns a result, acquires no
rights over the input and cannot use it for its own purposes.

- **Ensembl REST** (`rest.ensembl.org`) — gene structure and VEP annotation, including
  gnomAD frequency, `check_existing` and REVEL via dbNSFP. Public academic API; gene
  symbols and variant coordinates only.
- **Anthropic API, Claude, commercial terms, no training on customer content** —
  analysis design and code review.
- **No external splice-prediction service was called.** That capability is present in
  the notebook but disabled by default and requires an explicit operator decision after
  a terms review.

All artefacts derived from the child's genome are confined to a single working
directory. Deletion will be attested to `RarediseaserealkidMVAhackathon2026@synapse.org`
within 30 days of the hackathon close.

## 12. Scalability

Nothing here is specific to this proband. The pipeline is a phenotype-driven gene panel,
live coordinate resolution with build assertion, per-gene call-profile QC, chromosome
complement determination before interpreting sex-linked loci, population-frequency-first
annotation, marker-based and depth-based copy-number proxies, and calibrated ACMG
scoring — applicable to any suspected recessive Mendelian condition given a phenotype and
a single-sample VCF.

Four components are the most transferable, and each exists because it caught a real
error during this analysis:

1. **Annotate before filtering.** Database membership flags are not population
   frequency. Using one as a rarity proxy nearly discarded the correct answer.
2. **Aggregate clinical labels flag, they do not rescue.** `CLIN_SIG` is neither
   condition- nor origin-specific; a somatic cancer assertion from 2001 is
   indistinguishable in that field from a germline assertion for the disease in hand.
3. **Test copy number locally, and match the claim to the segment length.** Gene-level
   mean depth hides a focal deletion, and a 32 kb homozygous block is not a run of
   autozygosity.
4. **Assert completeness, not just validity.** A late run resolved 20 of 22 panel genes
   — two failed on transient API errors — and the notebook printed
   `gene structures resolved: 20/22 (all GRCh38)` and carried on. Every downstream count
   shifted by about 3%, the top-line result was unchanged, and nothing in the output
   signalled that two genes had been dropped. The existing assertion checked that the
   resolved genes were the right *build*; it never checked that they were *all there*.
   Panel completeness now raises rather than warns, and the retry logic honours
   `Retry-After` with exponential backoff.

The recurring pattern is that the most dangerous failures were the silent ones — a filter
that removed the answer, an annotation field that meant something other than it appeared
to, a summary statistic that concealed the thing it was being used to exclude, a
validity check that said nothing about completeness. In each case the pipeline ran to
completion and reported success. Each is now an explicit, re-derivable check rather than
an assumption, and each failure mode is one that would be invisible in a result table.

## 13. References

- Hanks S, et al. Constitutional aneuploidy and cancer predisposition caused by biallelic mutations in *BUB1B*. *Nat Genet* 2004.
- Tsukasaki K, et al. Mutations in the mitotic check point gene, *MAD1L1*, in human cancers. *Oncogene* 2001.
- Richards S, et al. Standards and guidelines for the interpretation of sequence variants. *Genet Med* 2015.
- Tavtigian SV, et al. Modeling the ACMG/AMP variant classification guidelines as a Bayesian classification framework. *Genet Med* 2018.
- Pejaver V, et al. Calibration of computational tools for missense variant pathogenicity classification. *Am J Hum Genet* 2022.
- ClinGen Sequence Variant Interpretation Working Group. PVS1, PM2 and PM3 recommendations.
- NCBI ClinVar. `NM_001211.6(BUB1B):c.2210T>G (p.Leu737Ter)` and MVA1; Variation ID 533901; RCV000641226.9. Accessed 2 September 2026.
- OMIM 602686, *MAD1L1*, allelic variants .0002 (prostate cancer, somatic), .0003 and .0004 (MVA7).
- Ensembl VEP documentation: co-located variants, `check_existing`, and REST annotation options.

> **Repository access.** The accompanying repository
> `https://github.com/Fernandosr85/mva-hackathon-2026-track1` is private at the time of
> submission. Access can be granted to the review panel on request. The methods description is
> reproduced in full as Appendix A of this report so that the methodology can be assessed
> without repository access.


---

# Appendix A — Methods Description (Track 1)

*Responses to the official Methods description template (Excel, last updated 28 Aug 2026).*
*The same answers are provided as `METHODS_DESCRIPTION.xlsx` in the repository. They are*
*reproduced here because the submission form has no upload field for the workbook.*


### A1. Team name

fernandosr85


### A2. Model number (fill out this form once per model/approach submitted; up to 6)

Model 1 (single approach submitted: bub1b-panel-acmg)


### A3. Please describe your model/approach in detail.

Approach: selective acquisition -> panel-bounded reduction -> QC -> complete coding/splice annotation -> allele-aware rarity -> consequence prioritisation -> inheritance-aware pair reasoning -> direct evidence adjudication -> executable audit.

1. SELECTIVE ACQUISITION. Of the ~85 GB release we downloaded 318 MB: the VCF, its tabix index, the phenotype document and the README. The 8 FASTQ lanes were deliberately skipped; no realignment was needed for variant ranking.

2. HEADER AUDIT. Three facts were established before any filtering, each constraining the design. The reference is named in the header (GRCh38 no-alt analysis set with hs38d1 decoy, no 'chr' prefix, M for mitochondria), called with Sentieon 202308.02. The VCF is UNANNOTATED - INFO carries caller metrics only, and its AF field is the within-sample allele fraction with AN=2, never a population frequency. PGT/PID are present, the only route to cis/trans in a single sample.

3. PANEL. 22 genes: the four established MVA loci (BUB1B, CEP57, TRIP13, MAD1L1) plus the wider spindle-assembly-checkpoint and cohesion machinery. Coordinates resolved live from Ensembl with assembly asserted to be GRCh38 and panel completeness asserted, so a partial resolution fails loudly. PAD=5000 for promoter/UTR/near-splice.

4. LOCUS QC BEFORE INTERPRETATION. Chromosome-complement pattern determined from the VCF call pattern alone (X/autosome depth ratio 0.488, X het fraction 0.062, 9,732 Y calls -> XY-like), because STAG2 is X-linked and its low heterozygosity would otherwise be misread. Intragenic LOH scan as a CNV proxy, followed by LOCAL depth inside each homozygosity block against its flanks - gene-level mean depth cannot detect a focal deletion.

5. ANNOTATION THEN FILTERING, not the reverse. All 61 PASS coding/splice calls annotated through Ensembl VEP with gnomAD frequency, check_existing and REVEL; rarity applied to the returned population frequency.

6. TRIAGE WITH DERIVED TESTS. Population frequency assessed by Hardy-Weinberg against the stated MVA prevalence ceiling; computational evidence by the full Pejaver REVEL ladder, defined once and consulted by both triage and ACMG interpretation.

7. ACMG/AMP interpretation on the Tavtigian point framework, with internal evidence kept separate from external ClinVar assertions.

Reduction: 85 GB -> 318 MB -> 22 gene regions -> all non-reference PASS calls in panel -> 61 coding/splice calls -> 4 shortlisted candidates -> 1 ranked pair with a competing alternative.


### A4. If commercially-available Generative AI was used, record the provider, the plan or tier, and the relevant setting in your methods description. A line is enough, for example, "Anthropic API, Claude Sonnet, commercial terms, no training on customer content."

Anthropic API, Claude, commercial terms, no training on customer content. Used for pipeline design, code review and report drafting. Ensembl REST (gene structure and VEP annotation) was the only other external service; gene symbols and variant coordinates only. No external splice-prediction service was called - that capability exists in the notebook but is disabled by default and requires an explicit operator decision after a terms review.


### A5. Please state whether the submission file is the automated output of your computational approach (preferred), or if it has undergone downstream manual review and curation.

Automated reduction with auditable human adjudication at predefined decision points.

Variant extraction, annotation, filtering and QC were automated and reproducible: the notebook runs top to bottom and re-derives every threshold decision. Candidate GENERATION was machine-derived. Final hypothesis ranking and EPCR calibration underwent explicit human adjudication, and deliberately so - condition-specific ClinVar interpretation, undetermined phase and conflicting evidence cannot safely be reduced to a single automated label, and the EPCR values themselves encode a judgement about how much probability mass the data leave unassigned.

The manual component was restricted to the four-variant shortlist, not the genome. Everything upstream of that is machine-derived and re-executable.


### A6. Please describe any downstream manual review in detail.

Three adjudications, each recorded in the notebook with its reason.

(a) MAD1L1 p.Arg59Cys entered the shortlist on an aggregate CLIN_SIG pathogenic token. The algorithm rejected it on population frequency (gnomAD 0.46% predicts ~169,000 homozygotes worldwide against a ceiling of <50 cases). Direct review then showed WHY the annotation conflicted: the Pathogenic assertion is recorded in OMIM 602686 as allelic variant .0002, 'PROSTATE CANCER, SOMATIC' (Tsukasaki 2001). The MVA7 alleles are different variants. VEP's clin_sig is allele-specific but neither condition- nor origin-specific.

(b) PM2 was WITHHELD on the lead allele because the ClinVar record warns that gnomAD quality at that position is unreliable. Rather than rest on a third party's data-quality claim, the classification was computed both ways - 9 points with PM2, 8 without, Likely Pathogenic either way. The call does not depend on the judgement.

(c) EPCR values were assigned by hand across two competing second-allele hypotheses, with an assertion in code that mutually exclusive hypotheses cannot sum above 1.0 and an explicit residual of 0.15 for 'the second allele is something else'.


### A7. Please state whether your approach only used publicly available data (preferred) or if proprietary data was also used. If proprietary data were used, where possible, please also include a submission based only on publicly available data.

The primary case inputs were the challenge-provided CONTROLLED data: the single-sample VCF and its tabix index, and the clinical phenotype document. These are governed by the hackathon Data Use Terms and are not publicly available.

All external reference resources were publicly available - Ensembl REST and VEP, gnomAD frequencies and REVEL returned through VEP, NCBI ClinVar, OMIM and published literature. No proprietary external dataset or subscription database was used.

Controlled data will be deleted within 30 days of the hackathon close across every environment under our control, with attestation to RarediseaserealkidMVAhackathon2026@synapse.org.


### A8. Please describe any public data used in detail (e.g., reference panels, population databases, literature).

Ensembl REST for gene structure and canonical transcripts, and Ensembl VEP for annotation, returning gnomAD genome and exome frequencies, co-located known variants via check_existing, and REVEL scores via dbNSFP. NCBI ClinVar and OMIM consulted directly for the shortlist variants. Literature: Hanks 2004 (biallelic BUB1B in MVA), Richards 2015 (ACMG/AMP), Tavtigian 2018 (point framework), Pejaver 2022 (REVEL calibration), ClinGen SVI recommendations for PVS1/PM2/PM3.

The hackathon VCF and phenotype document were the only case data used; HPO terms were extracted from the supplied .docx, which is KEEP-list under the data-use terms.


### A9. Please describe any proprietary data used in detail.

None.


### A10. Is your approach able to output proposed pairs of compound heterozygous candidate variants, or only single candidate variants?

Yes - pairs are the native output. The submission contains two rows, both sharing the established nonsense allele and differing in the proposed second allele, because the data do not resolve which is causal.

Phase is reported honestly: the two coding candidates are 10,911 bp apart with no shared read-backed PID block, so cis/trans is NOT demonstrated. A biallelic interpretation is biologically coherent with recessive MVA1 but is inferred from mechanism, not shown. Allele balance was tested against a binomial expectation of 0.5 in the empirical distribution of 1,583 high-quality heterozygous panel calls; all three candidates are compatible with constitutional heterozygosity, which does not prove germline origin and does not test the chromosomal mosaicism that defines MVA.


### A11. How did you handle secondary or incidental findings, if any? (See the finding_type column in your submission.)

The analysis was purpose-limited to a predefined 22-gene MVA/spindle-checkpoint panel. Secondary or incidental findings outside that disease-focused search were NOT systematically evaluated or reported, and no row in the submission carries finding_type 'secondary'.

This is a deliberate scope decision rather than an omission: a genome-wide secondary-findings analysis on a child's data raises consent and reporting questions that the hackathon framing does not settle, and reporting such findings without a clinical pathway would not serve the family.


### A12. Please provide an estimate of run time and cost for your approach (if possible).

Runtime, on a free Kaggle notebook with internet enabled:
  - download of the 318 MB subset: ~1-2 minutes
  - panel extraction over 22 gene regions: <1 minute
  - chromosome-complement QC (full-chromosome scans of 15, X, Y): ~3-5 minutes
  - VEP annotation of 61 coding/splice calls plus 11 intronic: ~1-2 minutes (rate-limited)
  - LOH scan, local depth profiling, allele balance, ACMG scoring: <1 minute
  Total end-to-end: approximately 10 minutes.

Cost. Notebook execution cost is zero: free Kaggle compute and public Ensembl APIs, with no paid service in the pipeline's execution path. The Anthropic API was used separately for pipeline design, code review and drafting; it is not required to run the pipeline and its cost is not included in this execution estimate. A third party re-running the notebook incurs no charge.

The computational point worth noting is that the 85 GB release was never treated as a monolithic problem. Selective acquisition of 318 MB plus panel-bounded extraction is what makes the runtime trivial, and the same structure would apply to any phenotype-driven panel on any single-sample VCF.


### A13. Provide a method abstract (up to 500 words). Please include strengths and limitations of your method as well as methodological detail.

We recovered the BUB1B pair later confirmed by the Track 1 evaluation, using a small, auditable, phenotype-driven pipeline over single-sample WGS. The WGS alone does not independently establish the second allele or phase, and treating that boundary - between what the data show and what is inferred - as the deliverable is the point of the method.

METHOD. Selective acquisition (318 MB of 85 GB) -> header audit establishing reference, annotation state and phasing availability -> 22-gene panel resolved live with build and completeness asserted -> locus QC before interpretation -> complete VEP annotation of all 61 coding/splice calls -> allele-aware rarity gate -> triage by derived tests -> calibrated ACMG/AMP scoring -> submission with explicit residual probability mass.

RESULT. c.2210T>G p.Leu737Ter supports PVS1 independently (8 points, Likely Pathogenic); NCBI ClinVar classifies the same variant as Pathogenic for MVA1, reported separately and not double-counted. Two competing second alleles are submitted with EPCR 0.60 and 0.25 and a 0.15 residual, because phase is not demonstrated and no CNV/SV caller was run.

STRENGTHS - and the most original part. The pipeline produced the correct answer while containing defects that an audit exposed, and each became an executable check:
  (1) dbSNP membership was used as a rarity proxy. The lead pathogenic variant IS rs759242053 yet carries DB=False in this VCF; a correctly populated flag would have DELETED the answer. Fixed by annotating before filtering.
  (2) An aggregate CLIN_SIG pathogenic token nearly rescued a variant whose Pathogenic assertion is for somatic prostate cancer, not germline MVA7. Fixed: the token now flags for review and records its entry route; it cannot rescue alone.
  (3) Gene-level mean depth was used to argue against a deletion. A focal deletion is diluted by the rest of the gene. Fixed with local depth inside each block against its flanks.
  (4) An assertion checked that resolved genes were the right BUILD but not that they were ALL THERE. A run resolved 20 of 22 and printed success; every count shifted. Fixed: completeness now raises.
Each failure ran to completion and reported success. None would appear in a results table. The generalisable principle is that conclusion scope must not exceed verified observation scope, enforced by executable invariants rather than by attention.

LIMITATIONS. Phase is not demonstrated - the coding candidates are 10.9 kb apart with no shared PID block, so trans is inferred from mechanism. No CNV/SV caller was run; the LOH scan argues against a broad intragenic deletion but cannot exclude a focal one below the 3.9 kb median marker gap. No SpliceAI score was obtained for the deep-intronic candidate, so no splice criterion is assigned and pseudo-exon activation remains untested. Short variants only. Analysis limited to a 22-gene panel, so a causal variant elsewhere would be missed. Allele balance is compatible with constitutional heterozygosity but does not prove germline origin and does not test the mosaicism that defines MVA.

# Critical Source-Group Arithmetic Reconciliation — Stage 8.9.56

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Mathematical Resolution

Section 5 of the Stage 8.9.56 charter mandated an independent investigation into the apparent source-group arithmetic discrepancy reported in Stage 8.9.55:
- Reported scream source groups: **77**
- Reported hard-negative source groups: **191**
- Category sum: **$77 + 191 = 268$**
- Reported unique source groups: **246**
- Arithmetic discrepancy: **$268 - 246 = 22$**

### Forensic Audit Verdict:
**THE ARITHMETIC DISCREPANCY IS 100% MATHEMATICALLY EXPLAINED AND PROVEN BY SET THEORY.**  
The discrepancy of 22 is **NOT** an error, miscalculation, or documentation flaw. It is the exact number of **shared (mixed-label) source groups** that contain both authentic scream recordings and hard-negative recordings from the same uploaders/sessions.

---

## 2. Set-Theoretic Mathematical Proof

By the Principle of Inclusion-Exclusion for finite sets:
$$\left|\mathcal{SG}_{\text{total}}\right| = \left|\mathcal{SG}_{\text{pos}}\right| + \left|\mathcal{SG}_{\text{neg}}\right| - \left|\mathcal{SG}_{\text{pos}} \cap \mathcal{SG}_{\text{neg}}\right|$$

Evaluating directly on the 450 frozen recordings from `integrity/frozen_test_manifest.json`:
- Positive Scream Source Groups ($\left|\mathcal{SG}_{	ext{pos}}ight|$): **77**
- Hard-Negative Source Groups ($\left|\mathcal{SG}_{	ext{neg}}ight|$): **191**
- Shared Mixed-Label Source Groups ($\left|\mathcal{SG}_{	ext{pos}} \cap \mathcal{SG}_{	ext{neg}}ight|$): **22**
- Unique Union of Source Groups:
  $$\text{Unique Union} = 77 + 191 - 22 = 268 - 22 = \mathbf{246}$$

The calculated unique union matches the reported **246 unique source groups** with mathematical precision ($246 = 246$).

---

## 3. Source-Group Classification Breakdown

| Source Group Classification Type | Unique Source Groups | Total Recordings | Positive Recordings | Negative Recordings | Share of Cohort |
|---|---|---|---|---|---|
| **Positive-Only Source Groups** | 55 | 103 | 103 | 0 | 22.9% |
| **Negative-Only Source Groups** | 169 | 223 | 0 | 223 | 49.6% |
| **Mixed-Label (Shared) Source Groups** | **22** | **124** | **47** | **77** | **27.6%** |
| **Total Independent Cohort** | **246** | **450** | **150** | **300** | **100.0%** |

---

## 4. Inventory of the 22 Mixed-Label Source Groups

The 22 source groups containing both positive and negative recordings originate from authentic multi-sound field recordings (e.g., sound effects libraries or field recordists capturing diverse vocalizations including both screams and shouting/crying/laughter):

| # | Source Group ID | Total Clips | Screams (Pos) | Negatives (Neg) | Negative Categories Represented |
|---|---|---|---|---|---|
| 1 | `fsd50k_user_11linda` | 6 | 1 | 5 | CHILD_ADULT_CRYING|SHOUTING_EXCITED_SPEECH |
| 2 | `fsd50k_user_adam_n` | 5 | 2 | 3 | CROWD_CHEERING|INFANT_CRYING|SIREN_ALARM |
| 3 | `fsd50k_user_artmasterrich` | 3 | 1 | 2 | SPEECH_NORMAL |
| 4 | `fsd50k_user_benjaminharveydesign` | 6 | 2 | 4 | MUSIC_SINGING|SHOUTING_EXCITED_SPEECH |
| 5 | `fsd50k_user_corsica_s` | 13 | 2 | 11 | CHILD_SPEECH|CROWD_CHEERING|INFANT_CRYING|SHOUTING_EXCITED_SPEECH|SPEECH_NORMAL |
| 6 | `fsd50k_user_dobroide` | 10 | 1 | 9 | CROWD_CHEERING|LAUGHTER|MUSIC_SINGING|SHOUTING_EXCITED_SPEECH|SIREN_ALARM|SPEECH_NORMAL |
| 7 | `fsd50k_user_dream4dreamtheater` | 3 | 1 | 2 | SHOUTING_EXCITED_SPEECH |
| 8 | `fsd50k_user_ecfike` | 5 | 2 | 3 | CHILD_ADULT_CRYING|CHILD_SPEECH|LAUGHTER |
| 9 | `fsd50k_user_freqman` | 2 | 1 | 1 | CROWD_CHEERING |
| 10 | `fsd50k_user_hello_flowers` | 3 | 2 | 1 | SIREN_ALARM |
| 11 | `fsd50k_user_jorickhoofd` | 6 | 4 | 2 | SHOUTING_EXCITED_SPEECH |
| 12 | `fsd50k_user_klankbeeld` | 9 | 1 | 8 | CROWD_CHEERING|INFANT_CRYING|MUSIC_SINGING|SHOUTING_EXCITED_SPEECH |
| 13 | `fsd50k_user_littlerobotsoundfactory` | 6 | 4 | 2 | SPEECH_NORMAL |
| 14 | `fsd50k_user_peridactyloptrix` | 2 | 1 | 1 | CROWD_CHEERING |
| 15 | `fsd50k_user_qubodup` | 5 | 1 | 4 | CROWD_CHEERING|INFANT_CRYING|SHOUTING_EXCITED_SPEECH|SPEECH_NORMAL |
| 16 | `fsd50k_user_reitanna` | 16 | 12 | 4 | CHILD_ADULT_CRYING|LAUGHTER|SHOUTING_EXCITED_SPEECH |
| 17 | `fsd50k_user_rfhache` | 2 | 1 | 1 | SPEECH_NORMAL |
| 18 | `fsd50k_user_rutgermuller` | 3 | 2 | 1 | SHOUTING_EXCITED_SPEECH |
| 19 | `fsd50k_user_sonsdebarcelona` | 3 | 1 | 2 | CROWD_CHEERING|SHOUTING_EXCITED_SPEECH |
| 20 | `fsd50k_user_theuncertainman` | 4 | 1 | 3 | SHOUTING_EXCITED_SPEECH|SPEECH_NORMAL |
| 21 | `fsd50k_user_wjoojoo` | 5 | 1 | 4 | CHILD_SPEECH|INFANT_CRYING|SPEECH_NORMAL |
| 22 | `fsd50k_user_xtrgamr` | 7 | 3 | 4 | CROWD_CHEERING|SHOUTING_EXCITED_SPEECH |

---

## 5. Methodological & Cluster-Resampling Implications

Because 22 source groups contain both positive and negative recordings:
1. Resampling individual source groups in cluster bootstrapping inherently resamples both positive and negative clips from these 22 groups simultaneously, preserving true session correlation.
2. In Phase 4, the cluster bootstrap will be evaluated under both unstratified source-group resampling and stratified positive/negative cluster resampling to test sensitivity.
3. Complete record-by-record profiles are saved in `source_group_reconciliation.csv`.

# Choosing a template

Start from `templates/INDEX.md` (or `python3 scripts/fill_template.py list --search WORDS`). Match on three things, in this order:

1. **Purpose**: what the document must do (notify, request, demand, plead, move, agree, report).
2. **Forum and posture**: which court, if any, and the stage of the case. A template whose `court` is "Virginia Circuit Court" is drafted for that court only. "Not court-specific" means correspondence or an agreement.
3. **Scope line**: every template's `scope` says what it covers and what it excludes. If the user's facts fall outside it (minor, estate, wrongful death, government defendant, federal court, another state), say so before drafting.

If the request matches an entry in `templates/ROUTES.md` instead, do not draft a substitute. Tell the user what that entry says to do (official form, clerk-issued process, agency process, specialist work, a choice between two templates, or an alias).

## Commonly confused templates

The distinctions below come from each template's scope and reasoning file.

### Pleadings and responses

| Need | Use | Not |
|---|---|---|
| Initial Circuit Court complaint, ordinary motor-vehicle negligence, one adult plaintiff, one individual defendant | `/complaint` | Not for minors, estates, government defendants, malpractice or extra counts without adaptation |
| Paragraph-by-paragraph response to a Circuit Court complaint | `/answer` | Not a general denial |
| Defense in General District Court | `/grounds` | |
| Defenses that accompany a responsive pleading | `/affirmative-defenses` | Not a stand-alone pleading |
| Legal-sufficiency challenge to a pleading | `/demurrer`, or `/demurrer-amended` for the current amended complaint | Not a federal plausibility motion |
| Defendant's claim against the plaintiff (Rule 3:9) | `/counterclaim` | |
| Defendant's claim against a co-defendant (Rule 3:10) | `/crossclaim` | |
| Claim against a nonparty who may owe the defending party's liability | `/third-party` | |
| Unsure whether counterclaim or cross-claim | See `/cross-complaint` in ROUTES.md | |

### Insurance and pre-suit

| Need | Use | Not |
|---|---|---|
| Statutory pre-suit motor-vehicle policy-limits disclosure request (§ 8.01-417(C)) | `/limits` | Excludes the wrongful-death subsection |
| Offer to settle for the liability limits | `/policylimits` | Not the statutory disclosure request |
| Ordinary settlement demand | `/demand`; reply to an offer with `/counter` | |
| Demand under the client's UM/UIM policy | `/umuim-demand`; open the claim with `/umuim` | |
| Settlement-opportunity letter to a liability insurer | `/badfaith` | Assumes no direct third-party bad-faith claim |
| Representation notice to the other driver's insurer | `/rep-adverse` | |
| Representation notice to the client's own insurer | `/rep-first` | |
| First preservation demand | `/preservation` | |
| Follow-up after a documented preservation concern | `/spoliation` | Assumes no finding of misconduct |
| Written promise not to plead limitations while negotiating (§ 8.01-232(A)) | `/tolling` | Not a universal suspension of deadlines |

### Discovery

| Need | Use | Not |
|---|---|---|
| Party request for production | `/rfp` (`/rfd` is an alias) | Not a nonparty subpoena |
| Production request served with a party deposition notice | `/rfd-with-depo` | |
| Attorney-issued nonparty business-records subpoena (Rule 4:9A) | `/subpoena-biz` | Excludes medical records |
| Notice to parties of nonparty records process | `/nod-records` | Not itself a subpoena |
| Deposition of an individual | `/depo-notice`; a party: `/nod-party`; a nonparty witness: `/nod-witness` | |
| Organization deposition with particular topics (Rule 4:5(b)(6)) | `/nod-corporate` | |
| Testifying expert deposition | `/nod-expert` | |
| Audiovisual recording notice | `/depo-video` | |
| Answering served discovery | `/discovery-responses`; specific objections with responses: `/objections` | Only against the actual served requests |
| Counsel-to-counsel conferral | `/meet-confer-deficient`; conferral that may request a local judicial conference if the court offers one: `/meet-confer-idc` | |
| Court relief | `/compel`, `/protective`, `/sanctions` | |

### Liens and benefit recovery

| Need | Use |
|---|---|
| Medicare: representation notice, claim notice, updated conditional payments, dispute, settlement report, relief request, payment transmittal, client status, closure documents | `/medicare-bcrc`, `/medicare-notice`, `/medicare-cpl`, `/medicare-dispute`, `/medicare-settlement-report`, `/medicare-compromise`, `/medicare-clearance-bcrc`, `/medicare-clearance-client`, `/lien-payoff-docs-medicare` |
| Virginia Medicaid: notice, itemization, compromise, payment, client status, satisfaction documents | `/medicaid-notice`, `/medicaid-conditional`, `/medicaid-reduction`, `/medicaid-payment-agency`, `/medicaid-payment-client`, `/lien-payoff-docs-medicaid` |
| ERISA or health plan: notice, plan documents, compromise, payment, satisfaction documents | `/erisa`, `/erisa-plan-docs`, `/erisa-negotiation`, `/erisa-payment`, `/lien-payoff-docs-erisa` |
| Hospital lien | `/hospital-lien`, `/hospital-payment`, `/lien-payoff-docs-hospital` |
| Private provider balance or lien reduction | `/provider-lien` (not Medicare, Medicaid, ERISA or Commonwealth claims) |
| Letter of protection: the undertaking, notice of an existing one, payoff and release | `/lop`, `/lop-notice`, `/lop-payoff-confirmation`, `/lop-payoff-reduction`, `/lop-payoff-release`, `/lien-payoff-docs-lop` |
| Med-pay reimbursement claim: first response, objection, conditional proposal | `/medpay`, `/medpay-response-decline`, `/medpay-response-negotiate` |
| PIP recovery claims | `/pip-coordination-atfault`, `/pip-coordination-nofault` |
| TRICARE and VA recovery | `/tricare-notice`, `/tricare-payment-tricare`, `/tricare-payment-va` |
| Workers' compensation: first notice, proposed settlement notice, compromise, credit agreement, payment | `/workers`, `/wc-notice`, `/wc-compromise`, `/wc-credit`, `/wc-payment` |

Agency-issued documents (Medicare recovery demand, Rights and Responsibilities letter, WCMSA submission) are routes, not templates. See ROUTES.md.

### Settlement

| Need | Use | Not |
|---|---|---|
| Client's written settlement instruction | `/settlement-auth` | Not a release or court approval |
| Adult private settlement agreement | `/settlement` | Not a minor, wrongful-death, structured or UIM package |
| Release of identified claims | `/release` | No automatic universal release |
| Covenant not to sue; limited indemnity | `/covenant`; `/hold-harmless` | |
| Closing accounting and distribution | `/disbursement`, `/itemized-bill`, `/trust-ledger`, `/client-check` | Not a payment instruction |
| Minor settlement deposit order; guardian ad litem appointment | `/blocked-account`; `/gal-appointment` | GAL report is the GAL's own work |
| Dismissal after settlement | `/order-dismissal` | Not a nonsuit (`/nonsuit`) |
| Structured settlement, trusts, qualified settlement funds, MSAs | `/structured-settlement` for the payment addendum only; the rest are specialist routes in ROUTES.md | |

### Trial, post-trial and appeal

| Need | Use | Not |
|---|---|---|
| Motion to strike the evidence at trial (Rule 1:11 per source) | `/strike` | Not a federal directed verdict |
| Set aside verdict for legal insufficiency (§ 8.01-430) | `/jnov` | Not federal Rule 50 |
| New trial; excessive verdict | `/newtrial`; `/remittitur` | |
| Court of Appeals opening, response and reply briefs | `/opening-brief`, `/appellee-brief`, `/reply-brief` | Not Supreme Court briefs |
| Supreme Court of Virginia petition for appeal | `/cert-petition` | Not a U.S. Supreme Court certiorari petition |
| Notice of appeal | Official form route `/notice-appeal` in ROUTES.md | |

## When nothing fits

Say so. Offer the closest template with the specific changes it would need, and mark those changes for attorney review. Do not stretch a template beyond its scope silently, and do not write a new document from scratch presented as one of these reviewed templates.

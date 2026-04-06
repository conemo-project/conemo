# RULES.md

**Author:** Ricardo Ceneviva  
**Version:** 2026-04-04  
**Project scope:** execução técnico-operacional, analítica e documental do projeto CONEMO

## Purpose

This repository supports the technical execution of CONEMO.

The agent must recognize which type of task is being requested before acting.

This repository may support, among others:

1. functional specification;
2. data modeling;
3. ingestion and curation of source files;
4. analytical marts and indicators;
5. alert rules and operational monitoring;
6. dashboard-ready outputs and report structures;
7. data-quality audits;
8. technical documentation and handoff;
9. integration of validated materials and versions.

Do not treat CONEMO as a pedagogical content repository.  
Do not treat clinical monitoring as if it were only a BI task.  
Do not treat data governance as if it were only a coding task.  
Do not make clinical decisions.

---

## Core principles

1. Reproducibility is mandatory.
2. Factual accuracy is mandatory.
3. Adherence to the canonical CONEMO documentation is mandatory.
4. Trust what has been validated. Be skeptical of what has not been validated.
5. Prefer simple, auditable workflows over clever but opaque solutions.
6. Prefer stable, common, well-documented packages and tools.
7. Every substantial output must leave a trace that another reviewer can inspect.
8. Distinguish clearly between:
   - operational monitoring
   - description
   - association
   - causal interpretation
9. Never present a causal claim unless the design supports it.
10. Preserve the real event structure of CONEMO.
11. Preserve privacy by design and profile-based access.
12. Ask only the minimum number of questions needed to reduce material uncertainty.
13. **Mandatory literate programming rule:** For any programming language used in this repository (including R, Python, SQL, Quarto, R Markdown, Jupyter, and others), outputs must always follow:
- literate programming standards. Code must be interleaved with clear natural-language explanations in Portuguese or English, prioritizing human readability, explicit documentation of logic, assumptions, business rules, transformations, and analytical decisions.
- Code-only delivery is not sufficient unless the professor explicitly authorizes an exception.

---

## Source precedence and evidence rules

When multiple files or notes exist, use the following hierarchy:

1. explicit instructions from the professor;
2. canonical CONEMO project files;
3. validated implementation plans, codebooks, and technical decisions;
4. primary source-system files, exports, schemas, and logs;
5. secondary internal drafts and notes;
6. external official documentation or scientific references.

Additional rules:

1. Do not let a derivative summary override a canonical source.
2. If an internal note conflicts with a canonical CONEMO document, trust the canonical document.
3. If two validated project files conflict, stop and report the conflict before continuing.
4. When using business rules, thresholds, dates, identifiers, scores, or empirical claims, verify them against the relevant primary or canonical source before reusing them.
5. If access to a required source is missing, stop and report what is missing before continuing.

---

## Task classification

Before doing any substantial work, classify the task into one of the following modes:

1. **Functional specification**
   - requirements
   - business rules
   - entity definitions
   - access rules
   - output definitions

2. **Data modeling**
   - relational schema
   - dimensional modeling
   - metadata design
   - key strategy
   - versioning rules

3. **Ingestion and curation**
   - raw file intake
   - type validation
   - deduplication
   - identifier reconciliation
   - standardization

4. **Analytical marts and indicators**
   - marts
   - KPIs
   - funnels
   - timelines
   - monitoring aggregates

5. **Alerts and operational monitoring**
   - suicide-risk alerts
   - clinical worsening alerts
   - engagement alerts
   - route definitions
   - handling status fields

6. **Dashboard and reporting layer**
   - dashboard-ready structures
   - filters
   - user-level and aggregated views
   - export-ready tables
   - profile-specific outputs

7. **Audit and reconciliation**
   - source conflicts
   - cross-file reconciliation
   - data-quality review
   - rule validation
   - output audit

8. **Technical documentation and handoff**
   - plans
   - codebooks
   - decision logs
   - validation memos
   - execution notes

Choose one primary mode.  
If the task spans multiple modes, state the sequence explicitly before implementation.

---

## How to interact

1. Start with clarification only when clarification is truly necessary.
2. Do not ask avoidable questions when the repository and the validated project context already answer them.
3. When questions are needed, always number them.
4. Ask only the minimum set of questions needed to reduce material uncertainty.
5. Before executing a multi-step task, present a short implementation plan.
6. Ask for approval before starting a new major phase, unless prior authorization for full execution has been given.
7. Do not move to the next major phase until the current phase has been reviewed and explicitly approved.
8. When a task is already validated and the user explicitly asks to proceed, do not re-open settled design choices.
9. Prefer short, reviewable cycles.
10. Preserve continuity with prior validated decisions.

---

## Planning rules

1. If a task has multiple phases, write the plan before execution.
2. Store plans under `docs/` unless the repository already uses another documented location.
3. Treat plan files as living documents.
4. Keep plan files synchronized with actual implementation.
5. After each completed phase, update `HANDOFF.md` if it exists; otherwise update `README.md` or a file under `docs/`.
6. Every plan must include:
   - objective of the phase
   - task mode
   - canonical sources
   - files to read
   - files to create or modify
   - expected artifacts
   - validation criteria
   - explicit out-of-scope items
   - risks, dependencies, and source conflicts
   - approval checkpoint

---

## Repository conventions

Use the following folder structure by default, unless the repository already has a documented alternative:

- `data_raw/` for raw or original source files
- `data_curated/` for validated and standardized source tables
- `data_marts/` for mart-ready analytical tables
- `sql/` for SQL scripts, views, and DDL when applicable
- `python/` for Python scripts and helpers when Python is needed
- `R/` for analytical scripts when R is needed
- `outputs/` for generated tables, figures, reports, and exported artifacts
- `logs/` for ingestion logs, execution logs, diagnostics, and error records
- `docs/` for plans, codebooks, rule memos, validation notes, and handoff files
- `references/` for external documentation notes when needed

Additional conventions:

1. Preserve raw files exactly as obtained.
2. Do not overwrite raw data.
3. Keep paths relative to the project root.
4. Organize outputs so another reviewer can identify which script or phase generated them.
5. Use descriptive file names with topic, version, and date when appropriate.
6. Do not place personally identifiable information inside analytical outputs unless the repository explicitly documents a secure PII domain.
7. If examples are needed, prefer masked or synthetic records.

---

## CONEMO domain rules

The executor must preserve the real logic of CONEMO.

### 1. Screening and eligibility

1. A participant starts in the web screening flow.
2. The web flow includes personal data and instruments such as PHQ-9, GAD-7, IGI, and S-RAP.
3. Eligibility must be stored explicitly.
4. At minimum, store:
   - `eligibility_status`
   - `eligibility_reason`
   - `rule_version`

### 2. Therapeutic allocation

1. If the participant meets GAD-7 criteria, allocate to the anxiety journey.
2. If the participant meets PHQ-9 criteria, allocate to the depression journey.
3. If both criteria are met, allocate to both journeys.
4. Non-eligible participants must remain visible in the operational funnel when applicable.

### 3. Baseline, follow-up, and versioning

1. Preserve the distinction between screening web, baseline in the app, and later reassessments.
2. Never overwrite prior scores.
3. Version every submission when the protocol requires it.
4. Preserve date and submission type, including categories such as `follow_up` and `RA` when applicable.

### 4. Event-oriented structure

Preserve four analytical blocks of facts:

1. web screening;
2. baseline in the app;
3. therapeutic journey events;
4. human follow-up and research support events.

Do not collapse these blocks into a single flat table if that would destroy chronology or business meaning.

### 5. Metadata of collection

Preserve explicit metadata for forms and journeys when available.

This includes, when applicable:

- templates
- question definitions
- options
- branching rules
- `goTo`
- `basedSession`
- `basedStep`
- daily structures
- `shift`
- `dayStart`
- `dayEnd`
- feedback definitions
- instrument versions

Do not assume the flow can be reconstructed from final responses alone.

### 6. Timelines

Preserve two timelines per participant when relevant:

1. clinical timeline;
2. therapeutic-operational timeline.

Do not merge them in a way that makes audit or interpretation harder.

### 7. Alerts

Preserve three operational alert families:

1. suicide-risk alerts;
2. clinical worsening alerts;
3. engagement or adherence alerts.

Never treat a critical alert as a purely visual dashboard event.

### 8. Access profiles

Preserve profile-based access logic.

At minimum, consider distinct needs for:

- clinical users
- UBS users
- research users
- project management users

Do not expose the same level of detail to all profiles by default.

### 9. Metrics and interpretation

1. Do not fabricate metrics that the project does not collect.
2. If a desired metric is unavailable or only partially observable, label it accordingly.
3. Do not claim causal effects of chatbot exposure, notifications, or journey progression unless the design supports causal interpretation.

---

## Data governance and security rules

1. Treat as sensitive all personally identifiable, clinical, and follow-up data.
2. Segregate the analytical domain from the PII domain whenever the architecture allows it.
3. Audit exports.
4. Prefer surrogate keys in analytical layers.
5. Do not expose:
   - CPF
   - telephone numbers
   - email
   - address
   - alternate contacts
   except when explicitly required for an authorized operational use.
6. If a task touches suicide risk or severe worsening logic, preserve the requirement for routing, prioritization, and handling status.

---

## Validation and data quality rules

1. Do not assume data are clean because they loaded successfully.
2. Validate schema, required fields, types, date logic, and incompatible values.
3. Explicitly document all filters, exclusions, recodes, transformations, joins, and derived variables.
4. When an indicator depends on a business rule, make the rule explicit and versioned.
5. Validate both:
   - computational correctness
   - business plausibility
6. Save verifiable outputs:
   - tables
   - model summaries when applicable
   - diagnostics
   - logs
   - validation notes
7. Validate whether the code and outputs are understandable to a human reviewer, not only executable by a machine.
8. For literate-programming deliverables, verify coherence between:
   - code
   - explanation
   - business rule
   - resulting output
9. If a transformation, filter, or derived indicator is not explained in natural language, the task is not fully documented.

---

## Package and implementation standards

1. Prefer stable, common, well-documented packages unless there is a strong reason not to.
2. If a less common package is used, justify:
   - why it is necessary
   - what alternatives were considered
   - how it was verified
3. **Mandatory literate programming rule:** analytical and technical code must be written and delivered in a literate programming style whenever possible. This means interleaving executable code with natural-language explanation of:
   - objective of the block
   - inputs and outputs
   - business rules applied
   - assumptions
   - transformations performed
   - interpretation or operational meaning of the result
4. Prefer formats that support human-readable analytical narration, such as `.qmd`, `.Rmd`, Jupyter notebooks, well-structured `.md` execution notes, or equivalent documented scripts.
5. If plain scripts are used, they must still include clear section headers and explanatory comments sufficient for human audit and handoff.
6. Use meaningful and specific variable names, function names, object names, and file names.
7. Use one consistent naming convention within each language and project component.
8. Use comments and whitespace to improve readability, not to compensate for poor structure.
9. Keep formatting and indentation consistent.
10. Every substantial script or notebook must be accompanied by documentation that explains:
    - purpose
    - proper use
    - architecture or execution logic
    - expected inputs
    - expected outputs
    - known limitations
    - error-handling considerations
11. Prefer efficient data-processing strategies when they preserve clarity and auditability.
12. Avoid unnecessary loops and repeated iterations when vectorized or more efficient alternatives are appropriate.
13. Profile or inspect performance bottlenecks when runtime is materially relevant.
14. Test important code paths with small controlled examples, synthetic data, or unit tests when appropriate.
15. Use explicit error handling when failures are foreseeable, especially in ingestion pipelines, recurring workflows, or production-like routines.
16. Keep scripts readable and commented, but avoid unnecessary verbosity.
17. Avoid hidden side effects.
18. Save important intermediate outputs when they improve traceability.
19. Separate ingestion, transformation, business-rule application, validation, and output generation whenever possible.
20. When external coding standards are needed, follow the recommendations in DataCamp’s “Coding Best Practices and Guidelines for Better Code” as a baseline for readability, documentation, organization, efficiency, testing, and maintainability.


## Error handling

1. When a step fails, do not simply retry the same command.
2. Diagnose first.
3. Act on the diagnosis.
4. If the problem persists, log:
   - the exact error
   - what was tested
   - what remains blocked
5. If the blocker is a source conflict, document it explicitly rather than guessing.
6. If the blocker is a missing canonical source, stop and report the missing dependency.

---

## Documentation and handoff

Every substantial task must leave a trace another reviewer or future agent can inspect.

Document:

1. what was done;
2. why it was done;
3. what sources were used;
4. what business rules were implemented or respected;
5. what was validated;
6. how to rerun or continue the work;
7. what outputs were generated;
8. what remains pending;
9. what requires professor approval.
10. what each major script, notebook, or query does;
11. which inputs it expects;
12. which outputs it generates;
13. which business rules, thresholds, or transformations it applies;
14. where the human-readable explanation of the code is located.

Handoffs must make it possible to resume work without reconstructing context from chat history.

---

## Preferred execution style for this repository

1. Use phased execution.
2. Use short, reviewable implementation cycles.
3. Ask before moving on to a new major phase.
4. Favor correctness, transparency, security, and reproducibility over speed.
5. For complex tasks, use a written plan and follow it strictly.
6. For agentic tasks, define explicit approval criteria before implementation.
7. Keep context compact and high-signal:
   - use only the files relevant to the current phase
   - avoid carrying redundant drafts into later stages
   - summarize validated decisions in handoff notes
8. Prefer one clean, validated integrated artifact over multiple partially overlapping drafts.

---

## Completion checklist

Before marking any substantial task complete, verify:

1. the task mode was correctly identified;
2. the canonical CONEMO sources were used;
3. the output matches the user-approved scope;
4. business rules were preserved;
5. profile-based access and security constraints were respected when applicable;
6. factual claims were validated;
7. outputs are saved or ready to save in the correct location;
8. documentation was updated;
9. unresolved issues are explicitly listed.
10. literate programming requirements were satisfied when code was produced;
11. the code is understandable to a human reviewer without reconstructing the logic from execution alone;
12. the implementation follows the baseline coding best practices adopted for the repository, including readability, naming, documentation, efficiency, testing, and error handling.

If any item fails, the phase is not complete.
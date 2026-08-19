# LEAP Databricks Job Cluster Governance

Use this reference for Databricks job clusters governed by LEAP standards. Confirm project-specific values before using them; cost center, department, domain, app, process type, policy, and ACLs vary by project.

## Job Cluster Semantics

- A job cluster is ephemeral, isolated, and created exclusively for one Databricks Job Workflow run.
- It is deleted immediately after the workflow run finishes, whether the run succeeds or fails.
- Cluster configuration is defined during workflow delivery, not through a separate cluster request.
- Expected start time is around 5 minutes.
- Autostop happens at the end of the process.
- Processing cost is documented as roughly half of an equivalent interactive cluster.
- Always select a policy and change only the policy-exposed parameters needed for the workload, such as Databricks Runtime, worker count, Photon enablement, and VM type.

## LEAP Job Naming

Composition:

```text
PP_[CENTRO_DE_CUSTO]_[TIPO]_[FERRAMENTA]_[NOME_PROCESSO]_[PERIODICIDADE]
```

Example:

```text
PP_AAES_NR_EXEMPLO_NOME_JOB
```

Rules:

- Uppercase only.
- Maximum length: 40 characters.
- Validation regex from the LEAP material: `^PP_[A-Z0-9_]+_(NR|ST|CT)_[A-Z0-9_]+$`.
- `PP`: fixed prefix.
- `CENTRO_DE_CUSTO`: required cost-center acronym.
- `TIPO`: required process type:
  - `NR`: normal process, stabilization phase, or engineering-owned.
  - `ST`: sustainment process owned by the iD support team.
  - `CT`: sustainment process owned by the OTI support team.
- `NOME_PROCESSO`: required and project-defined; target max 21 characters.
- `FERRAMENTA`: optional; examples include `DBW`, `SPRK`, `SHEL`, `HIVE`, `TDCH`, `BTEQ`, `PYTH`, `SCAL`, `OTHR`.
- `PERIODICIDADE`: optional; examples include `C`, `D`, `M`, `A`, `N`, `F`.

## LEAP Tags

Databricks processing resources must use tags in the pattern `dbw.<escopo>.<tag>`.

Scopes:

- `wkf`: workflow
- `cls`: cluster
- `pool`: pool
- `dlt`: Delta Live Tables
- `msv`: Model Serving
- `svl`: serverless

Use distinct workflow and cluster tags; otherwise allocation tags can be overwritten. For FinOps and incident handling, LEAP uses the workflow tag first and the cluster tag second. If both exist and differ, the workflow value wins.

Required tags for workflow and cluster scopes:

- `dbw.<escopo>.centro_de_custo`: required; cost-center acronym, lowercase.
- `dbw.<escopo>.dominio`: required; served domain, lowercase.
- `dbw.<escopo>.app`: required; application/module name, lowercase, words separated only by underscore.

Common optional tags:

- `dbw.<escopo>.departamento`: department code, lowercase, pattern like `d_0000`.
- `dbw.<escopo>.criticidade`: business impact; values:
  - `5`: extreme, critical high-impact process.
  - `4`: high, very important moderate-impact process.
  - `3`: moderate, important moderate-impact process.
  - `2`: low, important low-impact process.
  - `1`: irrelevant, low-importance no-impact process.

Restricted cost centers:

- `aaca`: exclusive for Azure resource deployment; do not use for Databricks processes/clusters or microservices.
- `aadg`: on-premise only.

Model Serving uses hyphenated tags because it cannot follow the same dot-scope pattern:

- `dbw-msv-centro_de_custo`
- `dbw-msv-dominio`
- `dbw-msv-app`

## Quarantine And Deletion Risk

Out-of-standard Databricks jobs in development, homologation, and exploratory environments are checked daily at 12:00, Monday through Friday.

When a job is out of standard:

- It enters quarantine and its name changes to `NOME_JOB_QUARENTENA`.
- The job is paused so it cannot run.
- A tag is added with the quarantine entry date.
- Users are notified by email.
- Users have 1 day, or 24 hours, to regularize the job.
- After the quarantine period, the job is deleted.

Regularization steps:

- Fix the job name, tags, and policy according to the standards.
- If quarantined, remove `_QUARENTENA` from the job name after making it compliant.
- Add at least the mandatory tags.
- Remove `dbw.wkf.quarentena`.

Treat quarantine markers as release blockers in generated YAML.

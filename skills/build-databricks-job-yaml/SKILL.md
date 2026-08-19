---
name: build-databricks-job-yaml
description: Build, modify, review, or validate Databricks job and job-cluster YAML, including Databricks Asset Bundle resources/jobs YAML, notebook task wiring, job_clusters/new_cluster configuration, resource sizing choices for CPU, Spark, GPU, vLLM inference, and distributed training jobs, LEAP/enterprise naming and tag standards, policy IDs, usage policies, quarantine avoidance, parameters, and access-control requirements. Use when Codex is asked to create properly formatted Databricks job YAML, choose cluster resources for a pipeline, check job names/tags/policies/ACLs, or adapt bank-llm/carteira-data pipeline job defaults to another workspace or project.
---

# Build Databricks Job YAML

## Core Workflow

1. Inspect the target repo before writing YAML: existing `resources/jobs/*.yml`, `databricks.yml`, generated job builders, notebook widgets, README deployment notes, and tests.
2. Identify the YAML flavor:
   - Databricks Asset Bundle: `resources.jobs.<job_key>`.
   - Direct Databricks job YAML: top-level `name`, `tasks`, `job_clusters`.
   Preserve the flavor already used by the file or pipeline.
3. Ask or confirm project-specific governance before finalizing enterprise defaults. Do not assume AACR, `d_4852`, policy IDs, usage policy IDs, domains, ACL groups, service principals, or process type (`NR`, `ST`, `CT`) transfer to another project.
4. Classify each job's resource type from the actual workload:
   - CPU-only utility: small CPU node, no ML runtime unless required.
   - Spark ETL/SQL/parquet/metadata: multi-worker Spark cluster sized by data volume and shuffle.
   - Single-node GPU PyTorch train/eval/inference: one GPU node, `num_workers: 0`, single-node Spark conf.
   - vLLM/LLM inference server: GPU driver/server cluster; Spark task GPU amounts may be `0` when GPU is consumed by the driver process.
   - Distributed training: multi-node GPU workers, `TorchDistributor`/DDP, one process per GPU, modest per-process DataLoader workers.
5. Generate YAML with explicit `tasks`, `job_clusters`, `tags`, `queue`, `parameters`, and `usage_policy_id`. Add ACLs only from confirmed project values.
6. Validate the YAML structurally and semantically before delivering it. Treat names containing `_QUARENTENA` or tags like `dbw.wkf.quarentena` as blockers that must be regularized.

## Required Checks

- Job name/key: follow the target repo convention. LEAP job names are uppercase, max 40 characters, and follow `PP_[CENTRO_DE_CUSTO]_[TIPO]_[FERRAMENTA]_[NOME_PROCESSO]_[PERIODICIDADE]` where `FERRAMENTA` and `PERIODICIDADE` may be project-dependent. Generated carteira-data job keys may normalize a display name to lowercase snake case.
- Task graph: every `depends_on.task_key` and `job_cluster_key` must reference an existing task/cluster; task keys must be unique.
- Parameters: every `{{job.parameters.NAME}}` reference must have a matching job parameter. Prefer uppercase job parameter names; keep Databricks job parameter defaults as strings, especially numbers and booleans.
- Notebook paths: use `${workspace.file_path}/...` for bundle-owned notebooks unless the project intentionally uses absolute `/Workspace/...` paths.
- Cluster config: use a cluster policy and include `spark_version`, `node_type_id`, `policy_id`, `data_security_mode`, `runtime_engine`, `kind`, and required custom tags. Add `driver_node_type_id` when the local convention uses it.
- Single-node clusters: use `is_single_node: true`, `num_workers: 0` when the target convention expects it, and the single-node Spark conf/tags already used by the repo.
- GPU clusters: use ML runtime when PyTorch/vLLM needs it; choose A100 node sizes based on model size, batch size, and distributed process count.
- Tags: apply distinct workflow (`dbw.wkf.*`) and cluster (`dbw.cls.*`) tags so cost allocation is not overwritten. Required LEAP tags are `centro_de_custo`, `dominio`, and `app`; `departamento` and `criticidade` are commonly present and should be confirmed per project.
- Access control: do not fabricate users, groups, service principals, or permissions. If the repo lacks ACL examples, ask for the desired ACL model or explicitly state that ACLs are inherited/out of scope.

## LEAP Governance Reference

Read `references/leap-job-cluster-governance.md` whenever the target workspace follows LEAP Databricks rules or when validating naming, tags, policies, quarantine risk, or Model Serving tags.

## bank-llm/carteira-data Reference

For this repo family, read `references/bank-llm-standards.md` before creating or changing YAML. It captures observed formats, tags, policy IDs, resource profiles, and project-specific defaults from `/Users/kunumi/Repos/kunumi-bank-llm`.

## Validation Script

Use the bundled validator after creating or editing YAML:

```bash
python /Users/kunumi/Documents/agent-skills/skills/build-databricks-job-yaml/scripts/validate_databricks_job_yaml.py path/to/job.yml --profile generic
```

Use `--profile leap-job-cluster` for LEAP naming/tag/quarantine checks. Use `--profile aacr-bank-llm` for the observed AACR/bank-llm conventions. Add `--require-acl` only when the target project requires explicit YAML-managed permissions.

The script validates structure, references, parameters, tags, policies, and likely resource class. Treat warnings about governance defaults as prompts to confirm project-specific values.

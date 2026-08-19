# bank-llm and carteira-data Databricks Job YAML Standards

This reference reflects the job YAMLs and builders found under `/Users/kunumi/Repos/kunumi-bank-llm`, primarily `bank-llm-metadata-upgrade/resources/jobs/*.yml`, plus `carteira-data/src/carteira_data/processing/*/assemble_job.py`.

## Formats

- `bank-llm` authored jobs use Databricks Asset Bundle shape:

```yaml
resources:
  jobs:
    PP_AACR_NR_PYTH_JOB_BANK_LLM_ENCODER:
      name: PP_AACR_NR_PYTH_JOB_BANK_LLM_ENCODER
      max_concurrent_runs: 3
      tasks: [...]
      job_clusters: [...]
      tags: {...}
      queue:
        enabled: true
      parameters: [...]
      usage_policy_id: d20ef375-1b5f-4a95-b98f-838cd18f43c2
```

- `carteira-data` generator functions also emit `resources.jobs.<job_key>`, but derive `job_key` from `job_name` by replacing non-alphanumerics with underscores and lowercasing.
- `carteira-data/src/carteira_data/processing/inference_engine/job_template.yaml` is a direct job YAML reference intended for UI paste, but its assembler emits bundle-style YAML.
- Legacy/personal jobs such as `encoder_jw.yml` contain useful resource experiments but are not the clean standard: they use absolute user workspace notebook paths, older Spark runtime, missing usage policy, and user-specific notifications.

## Project-Specific Governance Defaults

Confirm these before using them outside this project:

- Job name prefix follows LEAP naming: `PP_AACR_NR_...`; authored bank-llm job resource keys usually equal `name`.
- `AACR` is the observed center cost for this repo. Ask before using it in another project.
- Cluster policy: `policy_id: 0012C45789C4AF8B`.
- Usage policy: `usage_policy_id: d20ef375-1b5f-4a95-b98f-838cd18f43c2`.
- Security/runtime: `data_security_mode: SINGLE_USER`, `runtime_engine: STANDARD`, `kind: CLASSIC_PREVIEW`.
- Spark runtime for current authored jobs: `spark_version: 17.3.x-scala2.13`.
- Common cluster tags:
  - `dbw.cls.centro_de_custo: aacr`
  - `dbw.cls.criticidade: "1"`
  - `dbw.cls.dominio: adqemp`
  - `dbw.cls.departamento: d_4852`
  - `dbw.cls.app: kunumi`
- Common workflow tags:
  - `dbw.wkf.aap: kunumi` in bank-llm jobs
  - `dbw.wkf.app: transpj` in bank-llm jobs; `kunumi` in carteira-data generated jobs
  - `dbw.wkf.centro_de_custo: aacr`
  - `dbw.wkf.criticidade: "1"`
  - `dbw.wkf.departamento: d_4852`
  - `dbw.wkf.dominio: adqemp`

No explicit ACL/access-control blocks are present in the observed clean jobs. Ask for the target project's users/groups/service principals and permission levels before adding ACLs.

## Resource Profiles Observed

CPU-only utility:

- Example: `sync_repos.yml`.
- Node: `Standard_DS3_v2`.
- Single node: `is_single_node: true`, `num_workers: 0`.
- Spark conf:
  - `spark.databricks.cluster.profile: singleNode`
  - `spark.master: local[*, 4]`
- No `use_ml_runtime` unless the utility requires ML libraries.

Single-node GPU PyTorch train/eval/proposal:

- Examples: `encoder.yml`, `decoder.yml`, `encoder_value_only_eval.yml`.
- Runtime: `17.3.x-scala2.13`, ML runtime enabled.
- Single node: `is_single_node: true`, `num_workers: 0`.
- Spark conf:
  - `spark.databricks.cluster.profile: singleNode`
  - `spark.master: local[*, 4]`
- Tags include `ResourceClass: SingleNode`.
- Encoder train/eval and encoder value-only eval use `Standard_NC24ads_A100_v4`.
- Decoder train uses `Standard_NC48ads_A100_v4`; decoder eval/proposals use `Standard_NC24ads_A100_v4`.

Distributed encoder training:

- Example: `encoder_distributed.yml`.
- Only encoder has a distributed path; decoder DDP is not wired.
- Uses `TorchDistributor` and GPU workers.
- Cluster `encoder-ddp-4gpu`:
  - `node_type_id: Standard_NC48ads_A100_v4`
  - `driver_node_type_id: Standard_NC24ads_A100_v4`
  - `spark.task.resource.gpu.amount: "1"`
  - `num_workers: 2`
  - task `num_processes: "4"`
- Cluster `encoder-ddp-8gpu`:
  - same node/driver types
  - `num_workers: 4`
  - task `num_processes: "8"`
- Do not add single-node Spark conf or `ResourceClass: SingleNode` to DDP clusters.
- Keep `NUM_WORKERS` modest; it is per distributed process, so total loader workers are approximately `world_size * NUM_WORKERS`.

Spark ETL/timeline generation:

- Example builder: `carteira_data.processing.timeline_v2.assemble_job`.
- Current generated cluster key: `yelp`.
- `spark.task.resource.gpu.amount: "0"`.
- `num_workers: 8`.
- Uses `Standard_NC48ads_A100_v4` in the observed builder even though Spark tasks do not request GPU. Confirm whether this is intentional before copying it; a CPU Spark node family may be a better default for another project.

vLLM/LLM inference:

- Example builder/template: `carteira_data.processing.inference_engine`.
- Cluster key: `llm_inf_a100`.
- `Standard_NC24ads_A100_v4` driver/node with ML runtime.
- `is_single_node: true`, `enable_elastic_disk: true`, `performance_target: PERFORMANCE_OPTIMIZED`.
- Spark conf sets GPU resource amounts to `0` because vLLM consumes the GPU on the driver process, not as Spark task GPU resources:
  - `spark.executor.resource.gpu.amount: "0"`
  - `spark.task.resource.gpu.amount: "0"`
  - `spark.executor.cores: "24"`
  - `spark.task.cpus: "1"`
- The assembler adds routing condition tasks for inference vs postprocessing, plus `for_each_task.concurrency`.

## Job Defaults By Pipeline

Encoder bundle:

- Job name/key: `PP_AACR_NR_PYTH_JOB_BANK_LLM_ENCODER`.
- `max_concurrent_runs: 3`.
- Tasks: `train_encoder` on `encoder-train-gpu`; `evaluate_encoder` and `create_encoder_credit_proposals` on `encoder-infer-gpu`.
- Defaults: model `small`, `MAX_LENGTH=320`, `NUM_EPOCHS=20`, train batch `128`, eval/proposal batch `256`, train workers `8`, eval/proposal workers `4`, `LR=2e-4`, devices `cuda`.

Decoder bundle:

- Job name/key: `PP_AACR_NR_PYTH_JOB_BANK_LLM_DECODER`.
- `max_concurrent_runs: 3`.
- Tasks: `train_decoder` on `decoder-train-gpu`; `evaluate_decoder` and `create_decoder_credit_proposals` on `decoder-infer-gpu`.
- Defaults: model `small`, `MAX_LENGTH=400`, `HISTORY_MONTHS=12`, `NUM_EPOCHS=10`, train batch `64`, eval batch `128`, proposal batch `64`, workers `4`, `LR=3e-4`, devices `cuda`.

Encoder distributed bundle:

- Job name/key: `PP_AACR_NR_PYTH_JOB_BANK_LLM_ENCODER_DISTRIBUTED`.
- This observed name exceeds the LEAP 40-character cap. Shorten it before creating a new governed workflow, for example by dropping redundant words while preserving `PP_AACR_NR_...`.
- `max_concurrent_runs: 1`.
- Sequential tasks: medium -> large -> xlarge.
- Medium/large use 4 processes on `encoder-ddp-4gpu`; xlarge uses 8 processes on `encoder-ddp-8gpu`.
- Defaults: `MAX_LENGTH=320`, `NUM_WORKERS=2`, JSON logging on, MLflow off, validation layout off, learned position encoding.
- Batch/LR by model: medium `64` and `3e-4`; large `8` and `1e-4`; xlarge `4` and `8e-5`.

Sync repos:

- Job name/key: `PP_AACR_NR_PYTH_JOB_SYNC_REPOS`.
- `max_concurrent_runs: 1`.
- CPU-only single-node `Standard_DS3_v2`.

## YAML Authoring Rules

- Keep authored bank-llm job resource key and `name` identical.
- Prefer `${workspace.file_path}/notebooks/...` for bundle notebooks.
- Put common knobs in `parameters` and reference them with `{{job.parameters.NAME}}`.
- Ensure every parameter referenced by a task exists in `parameters`; remove unused parameters unless intentionally reserved.
- Keep job parameter defaults quoted as strings for numbers and booleans.
- Use `queue.enabled: true`.
- Keep `cluster_name: ""` for job clusters.
- Add `depends_on` for sequential training only where needed.
- For append writes to existing Delta tables, require a unique `run_tag`; default `write_mode` is usually `overwrite`.
- Do not use decoder distributed training unless the codebase gains a real DDP decoder entrypoint.
- Avoid quarantine markers: names containing `_QUARENTENA` or tags such as `dbw.wkf.quarentena` mean the job is noncompliant and at deletion risk after the 24-hour quarantine window.

#!/usr/bin/env python3
"""Validate Databricks job YAML structure and LEAP/bank-llm conventions."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PARAM_REF_RE = re.compile(r"\{\{\s*job\.parameters\.([A-Za-z0-9_]+)\s*\}\}")
TASK_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
LEAP_JOB_NAME_RE = re.compile(r"^PP_[A-Z0-9_]+_(NR|ST|CT)_[A-Z0-9_]+$")
LOWER_RE = re.compile(r"^[a-z0-9_]+$")
APP_TAG_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
DEPARTMENT_RE = re.compile(r"^d_[0-9]{4}$")

AACR_POLICY_ID = "0012C45789C4AF8B"
AACR_USAGE_POLICY_ID = "d20ef375-1b5f-4a95-b98f-838cd18f43c2"
RESTRICTED_COST_CENTERS = {"aaca", "aadg"}
LEAP_NAME_MAX_LENGTH = 40

REQUIRED_JOB_TAG_KEYS = {
    "generic": {
        "dbw.wkf.app",
        "dbw.wkf.centro_de_custo",
        "dbw.wkf.dominio",
    },
    "leap-job-cluster": {
        "dbw.wkf.app",
        "dbw.wkf.centro_de_custo",
        "dbw.wkf.dominio",
    },
    "aacr-bank-llm": {
        "dbw.wkf.aap",
        "dbw.wkf.app",
        "dbw.wkf.centro_de_custo",
        "dbw.wkf.criticidade",
        "dbw.wkf.departamento",
        "dbw.wkf.dominio",
    },
}
REQUIRED_CLUSTER_TAG_KEYS = {
    "generic": {
        "dbw.cls.app",
        "dbw.cls.centro_de_custo",
        "dbw.cls.dominio",
    },
    "leap-job-cluster": {
        "dbw.cls.app",
        "dbw.cls.centro_de_custo",
        "dbw.cls.dominio",
    },
    "aacr-bank-llm": {
        "dbw.cls.app",
        "dbw.cls.centro_de_custo",
        "dbw.cls.criticidade",
        "dbw.cls.departamento",
        "dbw.cls.dominio",
    },
}

LEAP_PROFILES = {"leap-job-cluster", "aacr-bank-llm"}


class Reporter:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def note(self, message: str) -> None:
        self.info.append(message)


def _load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore[import-not-found]

        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except ModuleNotFoundError:
        ruby = shutil.which("ruby")
        if ruby is None:
            raise RuntimeError(
                "YAML parsing requires PyYAML (`python -m pip install pyyaml`) "
                "or Ruby with stdlib yaml/json available."
            )
        script = (
            "require 'yaml'; require 'json'; "
            "obj = YAML.load_file(ARGV[0]); "
            "puts JSON.generate(obj)"
        )
        proc = subprocess.run(
            [ruby, "-e", script, str(path)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "Ruby YAML parser failed")
        return json.loads(proc.stdout)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _iter_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            strings.extend(_iter_strings(item))
    elif isinstance(value, list):
        for item in value:
            strings.extend(_iter_strings(item))
    return strings


def _param_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    for text in _iter_strings(value):
        refs.update(PARAM_REF_RE.findall(text))
    return refs


def _resource_class(cluster: dict[str, Any], tasks: list[dict[str, Any]]) -> str:
    node = str(cluster.get("node_type_id", ""))
    conf = _as_dict(cluster.get("spark_conf"))
    workers = cluster.get("num_workers")
    task_text = " ".join(_iter_strings(tasks)).lower()
    gpu_node = any(token in node.upper() for token in ("NC", "A100", "GPU"))
    spark_gpu = str(conf.get("spark.task.resource.gpu.amount", "")).strip() == "1"

    if "train_encoder_distributed" in task_text or "torchdistributor" in task_text:
        return "distributed-gpu-training"
    if "vllm" in task_text or "llm_inference" in task_text or "01_start_llm" in task_text:
        return "llm-gpu-inference"
    if gpu_node and (cluster.get("is_single_node") is True or workers in (0, "0", None)):
        return "single-node-gpu"
    if gpu_node and spark_gpu:
        return "spark-gpu"
    if workers not in (None, 0, "0"):
        return "spark"
    return "cpu-only"


def _extract_jobs(data: Any, path: Path, reporter: Reporter) -> dict[str, dict[str, Any]]:
    if not isinstance(data, dict):
        reporter.error(f"{path}: YAML root must be a mapping")
        return {}
    jobs = data.get("resources", {}).get("jobs") if isinstance(data.get("resources"), dict) else None
    if isinstance(jobs, dict):
        return {str(key): _as_dict(value) for key, value in jobs.items()}
    if {"name", "tasks", "job_clusters"}.intersection(data):
        return {str(data.get("name") or path.stem): _as_dict(data)}
    reporter.error(f"{path}: expected resources.jobs or direct Databricks job YAML")
    return {}


def _validate_tags(
    *,
    tags: dict[str, Any],
    required: set[str],
    label: str,
    reporter: Reporter,
) -> None:
    missing = sorted(required - set(tags))
    if missing:
        reporter.error(f"{label}: missing required tags: {', '.join(missing)}")
    for key, value in tags.items():
        if value is None or str(value) == "":
            reporter.error(f"{label}: tag {key!r} has an empty value")


def _tag_value(tags: dict[str, Any], key: str) -> str | None:
    if key not in tags:
        return None
    return str(tags[key]).strip()


def _validate_leap_tag_values(
    *,
    job_tags: dict[str, Any],
    cluster_tags: dict[str, Any],
    label: str,
    reporter: Reporter,
) -> None:
    for scope, tags in (("wkf", job_tags), ("cls", cluster_tags)):
        tag_label = f"{label}:{scope}"
        for field in ("centro_de_custo", "dominio"):
            key = f"dbw.{scope}.{field}"
            value = _tag_value(tags, key)
            if value is not None and not LOWER_RE.match(value):
                reporter.error(f"{tag_label}: {key} must be lowercase alnum/underscore")
        app_key = f"dbw.{scope}.app"
        app_value = _tag_value(tags, app_key)
        if app_value is not None and not APP_TAG_RE.match(app_value):
            reporter.error(
                f"{tag_label}: {app_key} must be lowercase words separated only by underscores"
            )
        dept_key = f"dbw.{scope}.departamento"
        dept_value = _tag_value(tags, dept_key)
        if dept_value is not None and not DEPARTMENT_RE.match(dept_value):
            reporter.error(f"{tag_label}: {dept_key} should match d_0000")
        crit_key = f"dbw.{scope}.criticidade"
        crit_value = _tag_value(tags, crit_key)
        if crit_value is not None and crit_value not in {"1", "2", "3", "4", "5"}:
            reporter.error(f"{tag_label}: {crit_key} must be one of 1, 2, 3, 4, 5")
        cost_value = _tag_value(tags, f"dbw.{scope}.centro_de_custo")
        if cost_value and cost_value.lower() in RESTRICTED_COST_CENTERS:
            reporter.error(
                f"{tag_label}: centro_de_custo {cost_value!r} is restricted for Databricks"
            )

    wkf_cost = _tag_value(job_tags, "dbw.wkf.centro_de_custo")
    cls_cost = _tag_value(cluster_tags, "dbw.cls.centro_de_custo")
    if wkf_cost and cls_cost and wkf_cost != cls_cost:
        reporter.warn(
            f"{label}: workflow and cluster centro_de_custo differ; LEAP FinOps uses workflow first"
        )

    if "dbw.wkf.quarentena" in job_tags:
        reporter.error(f"{label}: remove quarantine tag dbw.wkf.quarentena")
    if "dbw.cls.quarentena" in cluster_tags:
        reporter.error(f"{label}: remove quarantine tag dbw.cls.quarentena")


def _validate_acl(job: dict[str, Any], label: str, require_acl: bool, reporter: Reporter) -> None:
    has_acl = any(key in job for key in ("permissions", "access_control_list"))
    if require_acl and not has_acl:
        reporter.error(f"{label}: missing permissions/access_control_list")
    elif not has_acl:
        reporter.warn(
            f"{label}: no YAML-managed ACL found; confirm inherited permissions or add project-specific ACLs"
        )


def _validate_job(
    *,
    path: Path,
    key: str,
    job: dict[str, Any],
    profile: str,
    require_acl: bool,
    reporter: Reporter,
) -> None:
    label = f"{path}:{key}"
    name = str(job.get("name", "")).strip()
    if not name:
        reporter.error(f"{label}: missing job name")
    if profile in LEAP_PROFILES:
        if name and len(name) > LEAP_NAME_MAX_LENGTH:
            reporter.error(f"{label}: LEAP job name exceeds {LEAP_NAME_MAX_LENGTH} characters")
        if name and name.upper() != name:
            reporter.error(f"{label}: LEAP job name must be uppercase")
        if name and not LEAP_JOB_NAME_RE.match(name):
            reporter.error(f"{label}: LEAP job name should match {LEAP_JOB_NAME_RE.pattern}")
        if "QUARENTENA" in name:
            reporter.error(f"{label}: remove _QUARENTENA after regularizing the job")
    if profile == "aacr-bank-llm":
        if name and not name.startswith("PP_AACR_"):
            reporter.warn(f"{label}: observed bank-llm jobs use AACR; confirm project cost center")
        if key != name:
            reporter.warn(f"{label}: authored bank-llm jobs usually keep resource key equal to name")

    tasks = [_as_dict(task) for task in _as_list(job.get("tasks"))]
    if not tasks:
        reporter.error(f"{label}: missing tasks")
    task_keys = [str(task.get("task_key", "")) for task in tasks]
    for task_key in task_keys:
        if not task_key:
            reporter.error(f"{label}: task missing task_key")
        elif not TASK_KEY_RE.match(task_key):
            reporter.error(f"{label}: invalid task_key {task_key!r}")
    if len(task_keys) != len(set(task_keys)):
        reporter.error(f"{label}: duplicate task_key values")

    clusters = [_as_dict(cluster) for cluster in _as_list(job.get("job_clusters"))]
    cluster_map = {str(cluster.get("job_cluster_key")): _as_dict(cluster.get("new_cluster")) for cluster in clusters}
    if not clusters:
        reporter.error(f"{label}: missing job_clusters")
    if len(cluster_map) != len(clusters):
        reporter.error(f"{label}: duplicate or missing job_cluster_key values")

    for task in tasks:
        task_key = str(task.get("task_key", "<missing>"))
        used_cluster = task.get("job_cluster_key")
        if used_cluster is None:
            used_cluster = _as_dict(_as_dict(task.get("for_each_task")).get("task")).get("job_cluster_key")
        if used_cluster is not None and str(used_cluster) not in cluster_map:
            reporter.error(f"{label}:{task_key}: unknown job_cluster_key {used_cluster!r}")
        for dep in _as_list(task.get("depends_on")):
            dep_key = _as_dict(dep).get("task_key")
            if dep_key and str(dep_key) not in task_keys:
                reporter.error(f"{label}:{task_key}: unknown depends_on task_key {dep_key!r}")

    parameters = [_as_dict(param) for param in _as_list(job.get("parameters"))]
    param_names = {str(param.get("name")) for param in parameters if param.get("name")}
    for param in parameters:
        param_name = str(param.get("name", ""))
        if not re.match(r"^[A-Z0-9_]+$", param_name):
            reporter.warn(f"{label}: job parameter {param_name!r} is not uppercase snake case")
        if "default" not in param:
            reporter.error(f"{label}: parameter {param_name!r} missing default")
        elif not isinstance(param.get("default"), str):
            reporter.warn(f"{label}: parameter {param_name!r} default is not a string")

    refs = _param_refs(tasks)
    missing_params = sorted(refs - param_names)
    if missing_params:
        reporter.error(f"{label}: missing parameter definitions for refs: {', '.join(missing_params)}")
    unused = sorted(param_names - refs)
    if unused:
        reporter.warn(f"{label}: parameters not referenced by tasks: {', '.join(unused)}")

    job_tags = _as_dict(job.get("tags"))
    _validate_tags(
        tags=job_tags,
        required=REQUIRED_JOB_TAG_KEYS[profile],
        label=f"{label}:job tags",
        reporter=reporter,
    )
    _validate_acl(job, label, require_acl, reporter)

    if profile == "aacr-bank-llm":
        if job.get("usage_policy_id") != AACR_USAGE_POLICY_ID:
            reporter.error(f"{label}: expected usage_policy_id {AACR_USAGE_POLICY_ID}")

    if _as_dict(job.get("queue")).get("enabled") is not True:
        reporter.warn(f"{label}: queue.enabled is not true")

    for cluster_key, cluster in cluster_map.items():
        cluster_label = f"{label}:cluster {cluster_key}"
        for required_key in (
            "spark_version",
            "node_type_id",
            "policy_id",
            "data_security_mode",
            "runtime_engine",
            "kind",
        ):
            if not cluster.get(required_key):
                reporter.error(f"{cluster_label}: missing {required_key}")
        if profile == "aacr-bank-llm" and cluster.get("policy_id") != AACR_POLICY_ID:
            reporter.error(f"{cluster_label}: expected policy_id {AACR_POLICY_ID}")
        cluster_tags = _as_dict(cluster.get("custom_tags"))
        _validate_tags(
            tags=cluster_tags,
            required=REQUIRED_CLUSTER_TAG_KEYS[profile],
            label=f"{cluster_label}:custom_tags",
            reporter=reporter,
        )
        if profile in LEAP_PROFILES:
            _validate_leap_tag_values(
                job_tags=job_tags,
                cluster_tags=cluster_tags,
                label=cluster_label,
                reporter=reporter,
            )
        if cluster.get("cluster_name") not in ("", None):
            reporter.warn(f"{cluster_label}: job cluster cluster_name is usually blank")
        if cluster.get("is_single_node") is True:
            if cluster.get("num_workers") not in (0, "0", None):
                reporter.error(f"{cluster_label}: single-node cluster should not have workers")
            conf = _as_dict(cluster.get("spark_conf"))
            if conf.get("spark.databricks.cluster.profile") != "singleNode":
                reporter.warn(f"{cluster_label}: single-node cluster missing spark.databricks.cluster.profile=singleNode")
        cluster_tasks = [
            task
            for task in tasks
            if str(task.get("job_cluster_key")) == cluster_key
            or str(_as_dict(_as_dict(task.get("for_each_task")).get("task")).get("job_cluster_key")) == cluster_key
        ]
        reporter.note(f"{cluster_label}: resource_class={_resource_class(cluster, cluster_tasks)}")


def validate_file(path: Path, profile: str, require_acl: bool) -> Reporter:
    reporter = Reporter()
    try:
        data = _load_yaml(path)
    except Exception as exc:
        reporter.error(f"{path}: failed to parse YAML: {exc}")
        return reporter
    jobs = _extract_jobs(data, path, reporter)
    for key, job in jobs.items():
        _validate_job(
            path=path,
            key=key,
            job=job,
            profile=profile,
            require_acl=require_acl,
            reporter=reporter,
        )
    return reporter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Databricks job YAML files")
    parser.add_argument(
        "--profile",
        choices=("generic", "leap-job-cluster", "aacr-bank-llm"),
        default="generic",
        help="Validation profile for project-specific conventions",
    )
    parser.add_argument("--require-acl", action="store_true", help="Fail if job ACLs are absent")
    args = parser.parse_args(argv)

    all_errors: list[str] = []
    all_warnings: list[str] = []
    all_info: list[str] = []
    for path in args.paths:
        reporter = validate_file(path, args.profile, args.require_acl)
        all_errors.extend(reporter.errors)
        all_warnings.extend(reporter.warnings)
        all_info.extend(reporter.info)

    for message in all_info:
        print(f"INFO: {message}")
    for message in all_warnings:
        print(f"WARN: {message}", file=sys.stderr)
    for message in all_errors:
        print(f"ERROR: {message}", file=sys.stderr)

    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s), {len(all_warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"OK: 0 error(s), {len(all_warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

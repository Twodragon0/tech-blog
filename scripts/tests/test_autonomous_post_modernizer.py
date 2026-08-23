"""Unit tests for autonomous_post_modernizer.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from scripts import autonomous_post_modernizer as modernizer


def test_analyze_post_needs_clean_post(tmp_path):
    post = tmp_path / "2026-08-23-Clean_Post.md"
    content = (
        "---\n"
        "title: 'Kubernetes DevSecOps Hardening'\n"
        "category: kubernetes\n"
        "image: /assets/images/2026-08-23-Clean_Post.svg\n"
        "---\n\n"
        "## Overview\n\n"
        "Detailed architecture description for enterprise Kubernetes clusters.\n"
        + ("Substantial technical context and detailed security configurations. " * 60)
        + "\n\n"
        "```mermaid\ngraph TD\nA-->B\n```\n\n"
        "| Service | Role |\n|---|---|\n| API | Gate |\n\n"
        "```bash\nkubectl get pods -n kube-system\n```\n\n"
        "## Checklist\n\n"
        "- [ ] Check pod security admission\n"
    )
    post.write_text(content, encoding="utf-8")

    score, issues = modernizer.analyze_post_needs(post)
    # Image might be missing on disk in temp dir, but length/mermaid/table/code/checklist are present
    assert "Missing Mermaid architecture diagram" not in issues
    assert "Missing comparison or configuration table" not in issues
    assert "Missing actionable checklist (- [ ])" not in issues


def test_analyze_post_needs_flags_faq_and_missing_diagram(tmp_path):
    post = tmp_path / "2026-08-23-Thin_Post.md"
    content = (
        "---\n"
        "title: 'Sample Post'\n"
        "---\n\n"
        "Short text.\n\n"
        "## 자주 묻는 질문\n"
        "Q: What is this?\n"
    )
    post.write_text(content, encoding="utf-8")

    score, issues = modernizer.analyze_post_needs(post)
    assert score < 60
    assert "Contains prohibited FAQ section/schema" in issues
    assert "Missing Mermaid architecture diagram" in issues


def test_generate_mermaid_for_topic():
    k8s_diag = modernizer.generate_mermaid_for_topic(
        "Kubernetes Pod Security", "kubernetes"
    )
    assert "graph TD" in k8s_diag
    assert "Admission Controller" in k8s_diag

    aws_diag = modernizer.generate_mermaid_for_topic("AWS Cloud Security", "cloud")
    assert "flowchart LR" in aws_diag
    assert "AWS WAF" in aws_diag

    sec_diag = modernizer.generate_mermaid_for_topic("Incident Response", "incident")
    assert "sequenceDiagram" in sec_diag


def test_enhance_post_content(tmp_path):
    post = tmp_path / "2026-08-23-Improve_Target.md"
    content = (
        "---\n"
        "layout: post\n"
        "title: 'Kubernetes Ingress Hardening'\n"
        "date: 2026-08-23 09:00:00 +0900\n"
        "category: kubernetes\n"
        "image: /assets/images/2026-08-23-Improve_Target.svg\n"
        "---\n\n"
        "## 1. 개요 및 보안 아키텍처\n\n"
        "쿠버네티스 인그레스 컨트롤러 보안 설정 가이드입니다.\n\n"
        "## 2. 자주 묻는 질문\n"
        "FAQ 내용입니다.\n"
    )
    post.write_text(content, encoding="utf-8")

    score, issues = modernizer.analyze_post_needs(post)
    enhanced = modernizer.enhance_post_content(post, issues)
    assert enhanced is True

    new_content = post.read_text(encoding="utf-8")
    assert "자주 묻는 질문" not in new_content
    assert "```mermaid" in new_content
    assert "- [ ]" in new_content
    assert "| 통제 영역 |" in new_content

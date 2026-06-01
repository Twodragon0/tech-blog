import pytest
from pathlib import Path
from scripts.generate_post_images import _route_l22_band, generate_l22_digest_svg


@pytest.mark.parametrize("topic,expected_visual,expected_label", [
    ("Bithumb $44B 비트코인 오송금",            "v_wallet_forensic", "EXCHANGE"),
    ("빗썸 운영 보안 실패",                       "v_wallet_forensic", "EXCHANGE"),
    ("Upbit hot wallet incident",               "v_wallet_forensic", "EXCHANGE"),
    ("비트코인 $71,000 회복",                    "v_price_chart",     "CRYPTO MARKET"),
    ("Chainalysis Hexagate - MegaETH",          "v_wallet_forensic", "CHAIN INTEL"),
    ("CNCF Project Velocity 2025",              "v_cloud_k8s",       "CNCF CLOUD"),
    ("CNCF Project Velocity 2025 - 클라우드 네이티브 미래 전망", "v_cloud_k8s", "CNCF CLOUD"),  # Critic cond #3 — collision guard
    ("GitOps platform rollout",                 "v_code_bars",       "GITOPS"),
    # Guards: existing routes must still win
    ("Kubernetes 1.30 release",                 "v_cloud_k8s",       "KUBERNETES"),
    ("Bitcoin $60K 저점 반등",                   "v_price_chart",     "CRYPTO MARKET"),
    ("blockchain analytics overview",           "v_wallet_forensic", "BLOCKCHAIN"),
])
def test_l22_keyword_routing(topic, expected_visual, expected_label):
    route = _route_l22_band(topic, used_themes=set())
    assert route["visual_name"] == expected_visual
    assert route["label"] == expected_label


REPO = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("post_name,expected_labels", [
    ("2026-02-09-Blockchain_Tech_Digest_Bithumb_Bitcoin.md", {"EXCHANGE"}),
    ("2026-02-10-DevOps_Blockchain_Digest_CNCF_Chainalysis_Bitcoin.md", {"CNCF CLOUD", "CHAIN INTEL"}),
])
def test_l22_digest_render_contains_expected_labels(tmp_path, post_name, expected_labels):
    md = (REPO / "_posts" / post_name).read_text(encoding="utf-8")
    post_info = {
        "title": post_name.replace(".md", "").replace("_", " "),
        "filename": post_name,
        "content": md,
        "category": "security",
    }
    out = tmp_path / "cover.svg"
    assert generate_l22_digest_svg(post_info, out) is True
    svg = out.read_text(encoding="utf-8")
    for label in expected_labels:
        assert label in svg, f"missing band label {label!r} in rendered SVG"

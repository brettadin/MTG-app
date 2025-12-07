import pathlib


def test_mtg_fundamentals_presence():
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    integrated_main = repo_root / "app" / "ui" / "integrated_main_window.py"
    agent_guidance = repo_root / "doc" / "AGENT_GUIDANCE.md"
    readme = repo_root / "README.md"

    assert integrated_main.exists(), "integrated_main_window.py should exist"
    content = integrated_main.read_text(encoding="utf-8")
    assert "MTG_FUNDEMENTALS_AND_GUIDE.txt" in content, "integrated_main_window.py should include the MTG fundamentals doc reference"

    assert agent_guidance.exists(), "AGENT_GUIDANCE.md should exist"
    guidance = agent_guidance.read_text(encoding="utf-8")
    assert "MTG_FUNDEMENTALS_AND_GUIDE.txt" in guidance, "AGENT_GUIDANCE.md should reference MTG fundamentals"

    assert readme.exists(), "README.md should exist"
    r = readme.read_text(encoding="utf-8")
    assert "MTG_FUNDEMENTALS_AND_GUIDE.txt" in r, "README.md should point agents to MTG fundamentals"

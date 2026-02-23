import os

import context


def test_context_output(fixtures, capsys, tmp_path):
    # Write a fake conventions file
    conv = tmp_path / "conventions.txt"
    conv.write_text("Use descriptive names\nKeep it simple\n")
    os.environ["SEM_CONVENTIONS"] = str(conv)

    try:
        context.main(
            fixtures["views"],
            fixtures["inventory"],
            fixtures["environment"],
            fixtures["repositories"],
            fixtures["keys"],
            fixtures["projects"],
            "1",
        )
    finally:
        os.environ.pop("SEM_CONVENTIONS", None)

    out = capsys.readouterr().out

    assert "Project: Demo Project (#1)" in out
    assert "Views:" in out
    assert "All" in out
    assert "Web" in out
    assert "Inventories:" in out
    assert "All Hosts" in out
    assert "Environments:" in out
    assert "Cloudflare Secrets" in out
    assert "Repositories:" in out
    assert "demo-ansible" in out
    assert "Keys:" in out
    assert "infra-ssh" in out
    assert "Conventions:" in out
    assert "Use descriptive names" in out


def test_context_no_conventions(fixtures, capsys):
    os.environ.pop("SEM_CONVENTIONS", None)

    context.main(
        fixtures["views"],
        fixtures["inventory"],
        fixtures["environment"],
        fixtures["repositories"],
        fixtures["keys"],
        fixtures["projects"],
        "1",
    )

    out = capsys.readouterr().out
    assert "Conventions: (no conventions.txt found)" in out


def test_context_unknown_project(fixtures, capsys):
    os.environ.pop("SEM_CONVENTIONS", None)

    context.main(
        fixtures["views"],
        fixtures["inventory"],
        fixtures["environment"],
        fixtures["repositories"],
        fixtures["keys"],
        fixtures["projects"],
        "999",
    )

    out = capsys.readouterr().out
    assert "Project: Unknown (#999)" in out

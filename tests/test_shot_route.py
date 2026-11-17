"""build.py on the shot route: it writes pages and prints the shot lines, it never
draws a PNG or starts a process itself.

Each test runs build.py as `__main__` in a copy of the site under tmp_path, with
every process-starting call patched to raise.
"""

import os
import runpy
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import fluxstyle

REPO = Path(__file__).resolve().parent.parent
HEADING = "shot jobs:"


def _site_copy(root):
    root.mkdir(parents=True, exist_ok=True)
    for name in ("build.py", "content.yaml"):
        shutil.copyfile(REPO / name, root / name)
    shutil.copytree(REPO / "sections", root / "sections")
    shutil.copytree(REPO / "assets" / "images", root / "assets" / "images")
    return root


def _no_process(*args, **kwargs):
    raise AssertionError(f"build.py started a process: {args!r}")


def _run(root, monkeypatch, capsys, *flags):
    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, _no_process)
    monkeypatch.setattr(os, "system", _no_process)
    monkeypatch.chdir(root)
    monkeypatch.setattr(sys, "argv", ["build.py", *flags])
    try:
        runpy.run_path(str(root / "build.py"), run_name="__main__")
    except SystemExit as exc:
        assert exc.code in (0, None), f"build.py exited {exc.code}"
    return capsys.readouterr().out.splitlines()


def _jobs(lines):
    assert HEADING in lines, f"no {HEADING!r} line in:\n" + "\n".join(lines)
    return lines[len(lines) - 1 - lines[::-1].index(HEADING) + 1:]


def test_missing_icons_print_jobs_and_stop_before_index(tmp_path, monkeypatch, capsys):
    root = _site_copy(tmp_path / "site")
    images = root / "assets" / "images"
    (images / "icon-thermal-capture.png").unlink()
    (images / "icon-regulation-mandates.png").unlink()

    lines = _run(root, monkeypatch, capsys)
    jobs = _jobs(lines)

    assert len(jobs) == 2
    for line, name in zip(jobs, ("icon-thermal-capture", "icon-regulation-mandates")):
        argv = shlex.split(line)
        png = (images / f"{name}.png").resolve()
        assert argv[:3] == [str(fluxstyle.SHOT), str(png.with_name(png.name + ".html")), str(png)]
        assert argv[3:] == ["--width", "400", "--height", "400", "--transparent"]
        assert png.with_name(png.name + ".html").is_file()
        assert not png.exists()
    assert not (root / "index.html").exists()
    assert any("python3 build.py" in line and "rerun" in line.lower() for line in lines)
    assert not any("Built index.html" in line for line in lines)


def test_icons_flag_lists_all_nine_and_keeps_pngs(tmp_path, monkeypatch, capsys):
    root = _site_copy(tmp_path / "site")
    images = root / "assets" / "images"
    before = {p.name: p.read_bytes() for p in images.glob("icon-*.png")}
    assert len(before) == 9

    jobs = _jobs(_run(root, monkeypatch, capsys, "--icons"))

    assert len(jobs) == 9
    assert [Path(shlex.split(j)[2]).name for j in jobs] == [
        "icon-thermal-capture.png", "icon-acoustic-amplification.png",
        "icon-solid-state-conversion.png", "icon-ai-optimization.png",
        "icon-seamless-integration.png", "icon-heat-modulation.png",
        "icon-economic-compulsion.png", "icon-commercial-validation.png",
        "icon-regulation-mandates.png"]
    assert {p.name: p.read_bytes() for p in images.glob("icon-*.png")} == before


def test_complete_build_writes_the_tracked_index_and_no_jobs(tmp_path, monkeypatch, capsys):
    root = _site_copy(tmp_path / "site")
    lines = _run(root, monkeypatch, capsys)
    assert lines[-1] == HEADING
    assert (root / "index.html").read_bytes() == (REPO / "index.html").read_bytes()
    assert not list((root / "assets" / "images").glob("*.png.html"))


def test_html_only_does_what_a_plain_run_does(tmp_path, monkeypatch, capsys):
    outs = []
    for flags in ((), ("--html-only",)):
        root = _site_copy(tmp_path / ("plain" if not flags else "html-only"))
        (root / "assets" / "images" / "icon-heat-modulation.png").unlink()
        lines = _run(root, monkeypatch, capsys, *flags)
        outs.append([line.replace(str(root.resolve()), "<root>") for line in lines])
    assert outs[0] == outs[1]
    assert len(_jobs(outs[0])) == 1


@pytest.mark.parametrize("bad", ["it's", "a$b", "a`b", "a;b", "a\nb"])
def test_a_path_with_a_shell_character_is_refused(tmp_path, monkeypatch, capsys, bad):
    root = _site_copy(tmp_path / bad / "site")
    (root / "assets" / "images" / "icon-thermal-capture.png").unlink()
    with pytest.raises(ValueError, match="build.py refuses the shot path"):
        _run(root, monkeypatch, capsys)
    assert not list((root / "assets" / "images").glob("*.png.html"))


def test_an_unknown_flag_is_refused(tmp_path, monkeypatch, capsys):
    root = _site_copy(tmp_path / "site")
    with pytest.raises(SystemExit) as exc:
        monkeypatch.chdir(root)
        monkeypatch.setattr(sys, "argv", ["build.py", "--icon"])
        runpy.run_path(str(root / "build.py"), run_name="__main__")
    assert exc.value.code == 2

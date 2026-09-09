from pathlib import Path

from scripts.check_release import audit


def test_current_prototype_is_refused_as_manufacturing_release():
    root = Path(__file__).parents[1]
    errors = audit(root)
    assert "PCB is explicitly marked UNVALIDATED" in errors
    assert any("fabrication blockers" in error for error in errors)


def test_missing_files_are_named(tmp_path):
    errors = audit(tmp_path)
    assert "missing required file: hardware/edf-esc.kicad_pcb" in errors
    assert "missing required file: validation/ledger.csv" in errors

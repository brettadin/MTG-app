import pytest

from PySide6.QtWidgets import QApplication


@pytest.mark.usefixtures("qtbot")
def test_documentation_dialog_opens(qtbot):
    from app.ui.documentation_dialog import DocumentationDialog
    docs = [("Getting Started", "doc/GETTING_STARTED.md")]
    dlg = DocumentationDialog(docs)
    qtbot.addWidget(dlg)
    # Show the dialog and ensure it renders at least one doc
    dlg._load_doc("doc/GETTING_STARTED.md")
    assert dlg.viewer is not None
    assert dlg.viewer.toPlainText() != ""


@pytest.mark.usefixtures("qtbot")
def test_tutorial_dialog(qtbot):
    from app.ui.tutorial_dialog import TutorialDialog

    dlg = TutorialDialog()
    qtbot.addWidget(dlg)

    # Ensure it has steps and a description
    assert dlg.steps_list.count() > 0
    assert dlg.description.toPlainText() != ""

    # Navigate through steps
    dlg._next()
    dlg._prev()
    dlg._on_step_changed(0)
    assert dlg.steps_list.currentRow() == 0

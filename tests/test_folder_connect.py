from pathlib import Path

from src.vectordb import FolderDocumentIndexer


def test_supported_files_are_discovered(tmp_path):
    (tmp_path / "notes.txt").write_text("hello world", encoding="utf-8")
    (tmp_path / "report.md").write_text("# Hello", encoding="utf-8")
    (tmp_path / "image.jpg").write_text("ignore me", encoding="utf-8")

    files = FolderDocumentIndexer.list_supported_files(tmp_path)

    assert len(files) == 2
    assert {file.name for file in files} == {"notes.txt", "report.md"}


def test_folder_documents_turn_into_langchain_documents(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "notes.txt").write_text("This is a sample document.", encoding="utf-8")

    documents = FolderDocumentIndexer.load_documents(folder)

    assert len(documents) == 1
    assert "sample document" in documents[0].page_content.lower()
    assert documents[0].metadata["source_file"].endswith("notes.txt")

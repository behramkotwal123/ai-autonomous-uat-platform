import re
from pathlib import Path


DOCS_PATH = Path("docs")


def load_document():

    document_path = DOCS_PATH / "travel_api.md"

    if not document_path.exists():

        raise FileNotFoundError(
            f"API documentation not found: {document_path}"
        )

    return document_path.read_text(
        encoding="utf-8"
    )


def retrieve_relevant_documentation(
    query,
    max_sections=2
):

    document = load_document()

    sections = re.split(
        r"\n(?=# )",
        document
    )

    query_words = set(
        re.findall(
            r"\b[a-zA-Z0-9_]+\b",
            query.lower()
        )
    )

    scored_sections = []

    for section in sections:

        section_words = set(
            re.findall(
                r"\b[a-zA-Z0-9_]+\b",
                section.lower()
            )
        )

        score = len(
            query_words.intersection(
                section_words
            )
        )

        scored_sections.append(
            (
                score,
                section
            )
        )

    scored_sections.sort(
        key=lambda item: item[0],
        reverse=True
    )

    relevant_sections = [
        section
        for score, section in scored_sections[:max_sections]
        if score > 0
    ]

    return "\n\n".join(
        relevant_sections
    )

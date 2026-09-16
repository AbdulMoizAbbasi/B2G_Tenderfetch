import json
from pathlib import Path

from openpyxl import Workbook


INPUT_FILE = Path(
    "data/federal/relevant_tenders.json"
)

OUTPUT_FILE = Path(
    "data/federal/relevant_tenders.xlsx"
)


def json_to_excel():

    # Check JSON exists
    if not INPUT_FILE.exists():
        print(
            f"JSON file not found: {INPUT_FILE}"
        )
        return

    # Load JSON
    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        tenders = json.load(file)

    if not tenders:
        print("No tenders found in JSON.")
        return

    # Create workbook
    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Relevant Tenders"

    # Excel columns
    headers = [
        "Tender Number",
        "Tender Details",
        "Organization Details",
        "Status",
        "Advertised Date",
        "Closing Date",
        "Detail URL",
        "Classification",
        "Final Score",
        "Keyword Score",
        "Semantic Score",
        "Matched Keywords",
        "Matched Phrases",
        "Best Capability",
    ]

    worksheet.append(headers)

    # Add tender data
    for item in tenders:

        tender = item.get(
            "tender",
            {}
        )

        relevance = item.get(
            "relevance",
            {}
        )

        matched_keywords = relevance.get(
            "matched_keywords",
            []
        )

        matched_phrases = relevance.get(
            "matched_phrases",
            []
        )

        row = [
            tender.get("tender_number", ""),
            tender.get("tender_details", ""),
            tender.get("organization_details", ""),
            tender.get("status", ""),
            tender.get("advertised_date", ""),
            tender.get("closing_date", ""),
            tender.get("detail_url", ""),
            relevance.get("classification", ""),
            relevance.get("final_score", ""),
            relevance.get("keyword_score", ""),
            relevance.get("semantic_score", ""),
            ", ".join(matched_keywords),
            ", ".join(matched_phrases),
            relevance.get("best_capability", ""),
        ]

        worksheet.append(row)

    # Make columns readable
    column_widths = {
        "A": 20,
        "B": 50,
        "C": 40,
        "D": 20,
        "E": 18,
        "F": 18,
        "G": 60,
        "H": 18,
        "I": 15,
        "J": 15,
        "K": 15,
        "L": 30,
        "M": 40,
        "N": 30,
    }

    for column, width in column_widths.items():
        worksheet.column_dimensions[column].width = width

    # Freeze header row
    worksheet.freeze_panes = "A2"

    # Enable filters
    worksheet.auto_filter.ref = worksheet.dimensions

    # Save Excel file
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    workbook.save(
        OUTPUT_FILE
    )

    print(
        f"Excel file created successfully:"
    )
    print(OUTPUT_FILE)
    print(
        f"Total tenders exported: {len(tenders)}"
    )


if __name__ == "__main__":
    json_to_excel()
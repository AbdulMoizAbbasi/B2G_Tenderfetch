from scrapers.federal import scrape_federal_tenders
from relevance.text_builder import build_tender_text
from relevance.keyword_matcher import find_keyword_matches


def main():

    result = scrape_federal_tenders(
        date_from="2026-09-01",
        date_to="2026-09-07",
    )

    tenders = result.get(
        "tenders",
        []
    )

    print("\n" + "=" * 80)
    print("TENDERS CONTAINING CONFIGURED KEYWORDS")
    print("=" * 80)

    count = 0

    for tender in tenders:

        text = build_tender_text(
            tender
        )

        keyword_result = find_keyword_matches(
            text
        )

        matched = keyword_result[
            "matched_keywords"
        ]

        if not matched:
            continue

        count += 1

        print("\n" + "-" * 80)

        print(
            f"Tender Number: "
            f"{tender.get('tender_number')}"
        )

        print(
            f"Matched Keywords: "
            f"{matched}"
        )

        print(
            f"Keyword Score: "
            f"{keyword_result['keyword_score']}"
        )

        print(
            f"Matched Phrases: "
            f"{keyword_result.get('matched_phrases', [])}"
        )

        print("\nTender Text:")
        print(text)

        # Only inspect first 20
        if count >= 20:
            break

    print("\n" + "=" * 80)
    print(
        f"Showing {count} keyword-matching tenders"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
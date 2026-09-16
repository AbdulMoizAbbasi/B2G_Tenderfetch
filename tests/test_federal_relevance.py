from scrapers.federal import scrape_federal_tenders
from relevance.engine import analyze_tender
from storage.json_storage import save_relevant_tenders
from storage.normalizer import normalize_tender


def main():

    print("=" * 70)
    print("FEDERAL PPRA - RELEVANCE ANALYSIS")
    print("=" * 70)

    # Run the existing Federal scraper
    result = scrape_federal_tenders(
        date_from="2026-09-01",
        date_to="2026-09-07",
    )

    tenders = result.get(
        "tenders",
        []
    )

    print(f"\nTotal tenders fetched: {len(tenders)}")

    high = []
    medium = []
    low = []

    # Analyze every tender
    for tender in tenders:

        analysis = analyze_tender(tender)

        relevance = analysis["relevance"]

        classification = relevance["classification"]

        if classification == "HIGH":

            normalized = normalize_tender(
                tender,
                "Federal PPRA",
                relevance,
            )

            high.append(normalized)

        elif classification == "MEDIUM":

            normalized = normalize_tender(
                tender,
                "Federal PPRA",
                relevance,
            )

            medium.append(normalized)

        else:

            low.append(analysis)

    # Summary
    print("\n" + "=" * 70)
    print("RELEVANCE SUMMARY")
    print("=" * 70)

    print(f"Total:   {len(tenders)}")
    print(f"HIGH:    {len(high)}")
    print(f"MEDIUM:  {len(medium)}")
    print(f"LOW:     {len(low)}")

    print(
        f"\nKept:     {len(high) + len(medium)}"
    )

    print(
        f"Discarded: {len(low)}"
    )

    print("=" * 70)

    # Combine relevant tenders
    relevant = high + medium

    # Save relevant tenders to common JSON
    save_relevant_tenders(
        relevant
    )

    # Show a few relevant tenders for inspection
    print("\nTOP RELEVANT TENDERS")
    print("=" * 70)

    for tender in relevant[:10]:

        relevance = tender["relevance"]

        print("\nTender Number:")
        print(
            tender.get("tender_number")
        )

        print("Title:")
        print(
            tender.get("title")
        )

        print("Classification:")
        print(
            relevance["classification"]
        )

        print("Final Score:")
        print(
            relevance["final_score"]
        )

        print("Keyword Score:")
        print(
            relevance["keyword_score"]
        )

        print("Semantic Score:")
        print(
            relevance["semantic_score"]
        )

        print("Matched Keywords:")
        print(
            relevance["matched_keywords"]
        )

        print("-" * 70)


if __name__ == "__main__":
    main()
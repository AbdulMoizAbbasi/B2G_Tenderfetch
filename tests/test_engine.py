from relevance.engine import analyze_tender


tender = {
    "tender_number": "TS0000012466E",
    "tender_details": (
        "Procurement of dedicated internet connectivity "
        "and fiber optic network services."
    ),
    "organization_details": (
        "Government Department"
    ),
    "status": "Open",
}


result = analyze_tender(tender)

print("=" * 70)
print("TENDER ANALYSIS")
print("=" * 70)

print("Tender Number:")
print(
    result["tender"]["tender_number"]
)

print("\nRelevance:")
print(
    result["relevance"]
)
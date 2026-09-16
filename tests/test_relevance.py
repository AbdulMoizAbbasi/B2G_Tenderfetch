from relevance.scorer import calculate_relevance_score


TEST_TENDERS = [

    {
        "name": "Internet Connectivity",
        "text": """
        Procurement of dedicated internet connectivity
        and fiber optic network services for government offices.
        """,
    },

    {
        "name": "Office Furniture",
        "text": """
        Procurement of office furniture including desks,
        chairs, cabinets and conference tables.
        """,
    },

    {
        "name": "Firewall",
        "text": """
        Procurement, installation and configuration of
        enterprise firewall and network security equipment.
        """,
    },

    {
        "name": "ERP Software",
        "text": """
        Supply, implementation and maintenance of an
        enterprise resource planning software solution.
        """,
    },

    {
        "name": "Vehicle Purchase",
        "text": """
        Procurement of official vehicles for government
        department field operations.
        """,
    },

    {
        "name": "Cloud Infrastructure",
        "text": """
        Provision of cloud computing infrastructure,
        virtual machines and hosted data center services.
        """,
    },

    {
        "name": "Building Construction",
        "text": """
        Construction of a new government office building
        including civil works and architectural services.
        """,
    },

    {
        "name": "GPU Computing",
        "text": """
        Procurement of GPU servers and high-performance
        computing infrastructure for artificial intelligence
        workloads.
        """,
    },
]


for tender in TEST_TENDERS:

    result = calculate_relevance_score(
        tender["text"]
    )

    print("\n" + "=" * 70)

    print(
        f"Tender: {tender['name']}"
    )

    print(
        f"Classification: {result['classification']}"
    )

    print(
        f"Final Score: {result['final_score']}"
    )

    print(
        f"Keyword Score: {result['keyword_score']}"
    )

    print(
        f"Semantic Score: {result['semantic_score']}"
    )

    print(
        f"Matched Keywords: "
        f"{result['matched_keywords']}"
    )

    print(
        f"Best Capability: "
        f"{result['best_capability']}"
    )
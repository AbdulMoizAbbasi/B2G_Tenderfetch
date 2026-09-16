import json
import html
from pathlib import Path
from datetime import datetime

import gradio as gr


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = Path("data/relevant_tenders.json")

APP_TITLE = "Tender Intelligence"
APP_SUBTITLE = "Government Procurement Intelligence Platform"

REFRESH_INTERVAL = 300


# ============================================================
# DATA
# ============================================================

def load_tenders():
    """
    Load normalized relevant tenders from the master JSON.
    """

    if not DATA_FILE.exists():
        return []

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return []

    if not isinstance(data, list):
        return []

    return [
        tender
        for tender in data
        if isinstance(tender, dict)
    ]


# ============================================================
# HELPERS
# ============================================================

def safe_text(value):
    if value is None:
        return ""

    return html.escape(
        str(value)
    )


def get_relevance(tender):
    relevance = tender.get(
        "relevance",
        {},
    )

    if not isinstance(
        relevance,
        dict,
    ):
        return {}

    return relevance


def get_score(tender):
    relevance = get_relevance(
        tender
    )

    try:
        return float(
            relevance.get(
                "final_score",
                0,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0


def get_classification(tender):
    relevance = get_relevance(
        tender
    )

    return str(
        relevance.get(
            "classification",
            "LOW",
        )
    ).upper()


def get_source(tender):
    return str(
        tender.get(
            "source",
            "Unknown",
        )
    )


def get_title(tender):
    title = tender.get(
        "title",
        "",
    )

    if title:
        return str(title)

    return "Untitled Tender"


def get_keywords(tender):
    relevance = get_relevance(
        tender
    )

    keywords = relevance.get(
        "matched_keywords",
        [],
    )

    if not isinstance(
        keywords,
        list,
    ):
        return []

    return [
        str(keyword)
        for keyword in keywords
        if keyword
    ]


def get_phrases(tender):
    relevance = get_relevance(
        tender
    )

    phrases = relevance.get(
        "matched_phrases",
        [],
    )

    if not isinstance(
        phrases,
        list,
    ):
        return []

    return [
        str(phrase)
        for phrase in phrases
        if phrase
    ]


def get_capability(tender):
    relevance = get_relevance(
        tender
    )

    capability = relevance.get(
        "best_capability"
    )

    if capability:
        return str(
            capability
        )

    return ""


def normalize_date_for_sort(value):
    if not value:
        return datetime.min

    text = str(value).strip()

    formats = [
        "%Y-%m-%d",
        "%d %b %Y",
        "%d %B %Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
    ]

    for date_format in formats:

        try:

            return datetime.strptime(
                text,
                date_format,
            )

        except ValueError:
            continue

    return datetime.min


def format_date(value):
    if not value:
        return "Not available"

    text = str(value).strip()

    parsed = normalize_date_for_sort(
        text
    )

    if parsed == datetime.min:
        return safe_text(text)

    return parsed.strftime(
        "%d %b %Y"
    )


def truncate_text(
    text,
    max_length=180,
):
    if not text:
        return ""

    text = str(text)

    if len(text) <= max_length:
        return text

    return (
        text[:max_length].rstrip()
        + "..."
    )


def score_percentage(score):
    score = max(
        0.0,
        min(
            1.0,
            float(score),
        ),
    )

    return round(
        score * 100
    )


# ============================================================
# FILTERING
# ============================================================

def filter_tenders(
    tenders,
    search_text="",
    source_filter="All Sources",
    relevance_filter="All Relevance",
    min_score=0.0,
):
    search_text = (
        search_text
        or ""
    ).strip().lower()

    filtered = []

    for tender in tenders:

        source = get_source(
            tender
        )

        classification = get_classification(
            tender
        )

        score = get_score(
            tender
        )

        # ----------------------------------------------------
        # Source
        # ----------------------------------------------------

        if (
            source_filter
            and source_filter != "All Sources"
            and source != source_filter
        ):
            continue

        # ----------------------------------------------------
        # Relevance
        # ----------------------------------------------------

        if (
            relevance_filter
            and relevance_filter != "All Relevance"
            and classification != relevance_filter
        ):
            continue

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        if score < float(
            min_score
        ):
            continue

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        if search_text:

            searchable_parts = [
                tender.get(
                    "title",
                    "",
                ),
                tender.get(
                    "tender_number",
                    "",
                ),
                tender.get(
                    "organization",
                    "",
                ),
                tender.get(
                    "advertised_date",
                    "",
                ),
                tender.get(
                    "closing_date",
                    "",
                ),
                source,
            ]

            searchable_parts.extend(
                get_keywords(
                    tender
                )
            )

            searchable_parts.extend(
                get_phrases(
                    tender
                )
            )

            searchable_text = " ".join(
                str(value)
                for value in searchable_parts
                if value
            ).lower()

            if search_text not in searchable_text:
                continue

        filtered.append(
            tender
        )

    filtered.sort(
        key=lambda tender: (
            get_score(tender),
            normalize_date_for_sort(
                tender.get(
                    "advertised_date",
                    "",
                )
            ),
        ),
        reverse=True,
    )

    return filtered


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics(tenders):
    total = len(
        tenders
    )

    high = sum(
        1
        for tender in tenders
        if get_classification(
            tender
        ) == "HIGH"
    )

    medium = sum(
        1
        for tender in tenders
        if get_classification(
            tender
        ) == "MEDIUM"
    )

    federal = sum(
        1
        for tender in tenders
        if get_source(
            tender
        ) == "Federal PPRA"
    )

    punjab = sum(
        1
        for tender in tenders
        if get_source(
            tender
        ) == "Punjab PPRA"
    )

    return {
        "total": total,
        "high": high,
        "medium": medium,
        "federal": federal,
        "punjab": punjab,
    }


# ============================================================
# UI HTML
# ============================================================

def stat_card(
    label,
    value,
    description,
    icon,
    accent="blue",
):
    return f"""
    <div class="stat-card {accent}">
        <div class="stat-top">
            <div class="stat-icon">
                {icon}
            </div>
            <div class="stat-label">
                {safe_text(label)}
            </div>
        </div>

        <div class="stat-value">
            {safe_text(value)}
        </div>

        <div class="stat-description">
            {safe_text(description)}
        </div>
    </div>
    """


def build_header():
    return """
    <div class="hero">

        <div class="hero-glow"></div>

        <div class="hero-content">

            <div class="brand-row">

                <div class="brand-mark">
                    <span class="brand-mark-inner">J</span>
                </div>

                <div>
                    <div class="eyebrow">
                        JAZZWORLD · B2G
                    </div>

                    <div class="brand-name">
                        Tender Intelligence
                    </div>
                </div>

            </div>

            <div class="hero-title">
                Government Procurement
                <span>Intelligence</span>
            </div>

            <div class="hero-description">
                Discover relevant government procurement opportunities
                across Pakistan — automatically filtered and ranked
                for business relevance.
            </div>

            <div class="hero-badges">

                <div class="hero-badge">
                    <span class="live-dot"></span>
                    LIVE DATA
                </div>

                <div class="hero-badge">
                    AI RELEVANCE
                </div>

                <div class="hero-badge">
                    PHASE 1
                </div>

            </div>

        </div>

    </div>
    """


def build_stats(tenders):
    stats = calculate_statistics(
        tenders
    )

    return f"""
    <div class="stats-grid">

        {
            stat_card(
                "Relevant Tenders",
                stats["total"],
                "Opportunities currently in intelligence database",
                "◈",
                "blue",
            )
        }

        {
            stat_card(
                "High Priority",
                stats["high"],
                "Highest-confidence opportunities",
                "◆",
                "purple",
            )
        }

        {
            stat_card(
                "Medium Priority",
                stats["medium"],
                "Potentially relevant opportunities",
                "◇",
                "cyan",
            )
        }

        {
            stat_card(
                "Procurement Sources",
                len(
                    set(
                        get_source(tender)
                        for tender in tenders
                    )
                ),
                "Government procurement portals monitored",
                "◎",
                "green",
            )
        }

    </div>
    """


def build_source_overview(tenders):
    source_counts = {}

    for tender in tenders:

        source = get_source(
            tender
        )

        source_counts[source] = (
            source_counts.get(
                source,
                0,
            )
            + 1
        )

    if not source_counts:
        return ""

    cards = []

    source_icons = {
        "Federal PPRA": "◆",
        "Punjab PPRA": "◇",
    }

    for source, count in sorted(
        source_counts.items()
    ):

        icon = source_icons.get(
            source,
            "◎",
        )

        cards.append(
            f"""
            <div class="source-mini-card">

                <div class="source-mini-icon">
                    {icon}
                </div>

                <div class="source-mini-info">

                    <div class="source-mini-name">
                        {safe_text(source)}
                    </div>

                    <div class="source-mini-count">
                        {count} relevant opportunities
                    </div>

                </div>

            </div>
            """
        )

    return f"""
    <div class="section-heading">
        <div>
            <div class="section-kicker">
                PROCUREMENT NETWORK
            </div>

            <div class="section-title">
                Intelligence Sources
            </div>
        </div>
    </div>

    <div class="source-grid">
        {"".join(cards)}
    </div>
    """


def build_tender_card(tender, index):
    title = safe_text(
        get_title(tender)
    )

    source = safe_text(
        get_source(tender)
    )

    organization = safe_text(
        tender.get(
            "organization",
            "",
        )
        or "Organization not available"
    )

    tender_number = safe_text(
        tender.get(
            "tender_number",
            "",
        )
        or "No tender number"
    )

    advertised = format_date(
        tender.get(
            "advertised_date",
            "",
        )
    )

    closing = format_date(
        tender.get(
            "closing_date",
            "",
        )
    )

    score = get_score(
        tender
    )

    percentage = score_percentage(
        score
    )

    classification = get_classification(
        tender
    )

    keywords = get_keywords(
        tender
    )

    capability = get_capability(
        tender
    )

    keyword_html = ""

    for keyword in keywords[:5]:

        keyword_html += (
            f'<span class="keyword-chip">'
            f'{safe_text(keyword)}'
            f'</span>'
        )

    if not keyword_html:

        keyword_html = (
            '<span class="keyword-chip muted">'
            'Semantic match'
            '</span>'
        )

    priority_class = classification.lower()

    return f"""
    <div class="tender-card">

        <div class="tender-card-top">

            <div class="source-pill">
                <span class="source-dot"></span>
                {source}
            </div>

            <div class="priority-pill {priority_class}">
                {classification}
            </div>

        </div>

        <div class="tender-card-title">
            {title}
        </div>

        <div class="tender-card-org">
            <span class="meta-icon">⌂</span>
            {organization}
        </div>

        <div class="tender-card-divider"></div>

        <div class="tender-meta-grid">

            <div class="meta-block">

                <div class="meta-label">
                    TENDER NUMBER
                </div>

                <div class="meta-value">
                    {tender_number}
                </div>

            </div>

            <div class="meta-block">

                <div class="meta-label">
                    PUBLISHED
                </div>

                <div class="meta-value">
                    {advertised}
                </div>

            </div>

            <div class="meta-block">

                <div class="meta-label">
                    CLOSING
                </div>

                <div class="meta-value closing">
                    {closing}
                </div>

            </div>

            <div class="meta-block">

                <div class="meta-label">
                    CAPABILITY
                </div>

                <div class="meta-value">
                    {safe_text(capability) or "—"}
                </div>

            </div>

        </div>

        <div class="relevance-row">

            <div class="relevance-label">
                <span>AI RELEVANCE</span>
                <strong>{percentage}%</strong>
            </div>

            <div class="progress-track">
                <div
                    class="progress-fill {priority_class}"
                    style="width: {percentage}%"
                ></div>
            </div>

        </div>

        <div class="keyword-row">
            {keyword_html}
        </div>

        <div class="card-index">
            #{index:02d}
        </div>

    </div>
    """


def build_tender_grid(tenders):
    if not tenders:

        return """
        <div class="empty-state">

            <div class="empty-icon">
                ◌
            </div>

            <div class="empty-title">
                No opportunities found
            </div>

            <div class="empty-description">
                Try changing your search or filters.
            </div>

        </div>
        """

    cards = []

    for index, tender in enumerate(
        tenders,
        start=1,
    ):

        cards.append(
            build_tender_card(
                tender,
                index,
            )
        )

    return f"""
    <div class="results-header">

        <div>
            <div class="section-kicker">
                OPPORTUNITIES
            </div>

            <div class="section-title">
                Relevant Tenders
            </div>
        </div>

        <div class="result-count">
            {len(tenders)} RESULTS
        </div>

    </div>

    <div class="tender-grid">
        {"".join(cards)}
    </div>
    """


# ============================================================
# DETAIL VIEW
# ============================================================

def build_detail_view(tender):
    if not tender:

        return """
        <div class="detail-empty">
            Select a tender to inspect its details.
        </div>
        """

    title = safe_text(
        get_title(tender)
    )

    source = safe_text(
        get_source(tender)
    )

    organization = safe_text(
        tender.get(
            "organization",
            "",
        )
        or "Not available"
    )

    tender_number = safe_text(
        tender.get(
            "tender_number",
            "",
        )
        or "Not available"
    )

    advertised = format_date(
        tender.get(
            "advertised_date",
            "",
        )
    )

    closing = format_date(
        tender.get(
            "closing_date",
            "",
        )
    )

    status = safe_text(
        tender.get(
            "status",
            "",
        )
        or "Not available"
    )

    url = (
        tender.get(
            "tender_url",
            "",
        )
        or ""
    )

    score = get_score(
        tender
    )

    percentage = score_percentage(
        score
    )

    classification = get_classification(
        tender
    )

    keywords = get_keywords(
        tender
    )

    phrases = get_phrases(
        tender
    )

    capability = get_capability(
        tender
    )

    keyword_html = ""

    for keyword in keywords:

        keyword_html += (
            f'<span class="detail-chip">'
            f'{safe_text(keyword)}'
            f'</span>'
        )

    phrase_html = ""

    for phrase in phrases:

        phrase_html += (
            f'<span class="detail-chip phrase">'
            f'{safe_text(phrase)}'
            f'</span>'
        )

    other = tender.get(
        "other",
        {},
    )

    if not isinstance(
        other,
        dict,
    ):
        other = {}

    other_html = ""

    for key, value in other.items():

        if not value:
            continue

        label = (
            str(key)
            .replace(
                "_",
                " ",
            )
            .upper()
        )

        other_html += f"""
        <div class="detail-field">

            <div class="detail-field-label">
                {safe_text(label)}
            </div>

            <div class="detail-field-value">
                {safe_text(value)}
            </div>

        </div>
        """

    if url:

        url_button = f"""
        <a
            class="open-tender-button"
            href="{safe_text(url)}"
            target="_blank"
            rel="noopener noreferrer"
        >
            <span>↗</span>
            Open Original Tender
        </a>
        """

    else:

        url_button = """
        <div class="no-url">
            Original tender URL unavailable
        </div>
        """

    return f"""
    <div class="detail-panel">

        <div class="detail-header">

            <div>

                <div class="detail-source">
                    {source}
                </div>

                <div class="detail-title">
                    {title}
                </div>

            </div>

            <div class="detail-priority {classification.lower()}">
                {classification}
            </div>

        </div>

        <div class="detail-score-panel">

            <div class="score-ring">

                <div class="score-number">
                    {percentage}%
                </div>

                <div class="score-caption">
                    AI MATCH
                </div>

            </div>

            <div class="score-info">

                <div class="score-heading">
                    Relevance Assessment
                </div>

                <div class="score-description">
                    This opportunity was automatically evaluated
                    against JazzWorld's configured capabilities
                    using keyword and semantic matching.
                </div>

                <div class="detail-progress">
                    <div
                        class="detail-progress-fill"
                        style="width: {percentage}%"
                    ></div>
                </div>

            </div>

        </div>

        <div class="detail-section">

            <div class="detail-section-title">
                Procurement Information
            </div>

            <div class="detail-fields">

                <div class="detail-field">

                    <div class="detail-field-label">
                        TENDER NUMBER
                    </div>

                    <div class="detail-field-value">
                        {tender_number}
                    </div>

                </div>

                <div class="detail-field">

                    <div class="detail-field-label">
                        ORGANIZATION
                    </div>

                    <div class="detail-field-value">
                        {organization}
                    </div>

                </div>

                <div class="detail-field">

                    <div class="detail-field-label">
                        PUBLISHED
                    </div>

                    <div class="detail-field-value">
                        {advertised}
                    </div>

                </div>

                <div class="detail-field">

                    <div class="detail-field-label">
                        CLOSING
                    </div>

                    <div class="detail-field-value closing">
                        {closing}
                    </div>

                </div>

                <div class="detail-field">

                    <div class="detail-field-label">
                        STATUS
                    </div>

                    <div class="detail-field-value">
                        {status}
                    </div>

                </div>

                <div class="detail-field">

                    <div class="detail-field-label">
                        BEST CAPABILITY
                    </div>

                    <div class="detail-field-value">
                        {safe_text(capability) or "Not available"}
                    </div>

                </div>

            </div>

        </div>

        <div class="detail-section">

            <div class="detail-section-title">
                Intelligence Signals
            </div>

            <div class="detail-signal-box">

                <div class="signal-label">
                    MATCHED KEYWORDS
                </div>

                <div class="detail-chips">
                    {
                        keyword_html
                        or
                        '<span class="signal-muted">No direct keyword match — semantic similarity contributed to the score.</span>'
                    }
                </div>

            </div>

            <div class="detail-signal-box">

                <div class="signal-label">
                    MATCHED PHRASES
                </div>

                <div class="detail-chips">
                    {
                        phrase_html
                        or
                        '<span class="signal-muted">No strong phrase match.</span>'
                    }
                </div>

            </div>

        </div>

        {
            f'''
            <div class="detail-section">
                <div class="detail-section-title">
                    Portal Information
                </div>

                <div class="detail-fields">
                    {other_html}
                </div>
            </div>
            '''
            if other_html
            else ""
        }

        <div class="detail-action">
            {url_button}
        </div>

    </div>
    """


# ============================================================
# EVENT HANDLERS
# ============================================================

def refresh_dashboard():
    tenders = load_tenders()

    sources = sorted(
        set(
            get_source(tender)
            for tender in tenders
        )
    )

    source_choices = [
        "All Sources"
    ] + sources

    stats_html = build_stats(
        tenders
    )

    source_html = build_source_overview(
        tenders
    )

    results_html = build_tender_grid(
        tenders
    )

    return (
        stats_html,
        source_html,
        results_html,
        gr.update(
            choices=source_choices,
            value="All Sources",
        ),
    )


def apply_filters(
    search_text,
    source_filter,
    relevance_filter,
    min_score,
):
    tenders = load_tenders()

    filtered = filter_tenders(
        tenders=tenders,
        search_text=search_text,
        source_filter=source_filter,
        relevance_filter=relevance_filter,
        min_score=min_score,
    )

    return build_tender_grid(
        filtered
    )


def select_tender(
    tender_index,
    search_text,
    source_filter,
    relevance_filter,
    min_score,
):
    tenders = load_tenders()

    filtered = filter_tenders(
        tenders=tenders,
        search_text=search_text,
        source_filter=source_filter,
        relevance_filter=relevance_filter,
        min_score=min_score,
    )

    try:

        index = int(
            tender_index
        )

    except (
        TypeError,
        ValueError,
    ):

        return build_detail_view(
            None
        )

    # User sees 1-based result numbers.
    index -= 1

    if index < 0:
        return build_detail_view(
            None
        )

    if index >= len(
        filtered
    ):

        return build_detail_view(
            None
        )

    return build_detail_view(
        filtered[index]
    )


# ============================================================
# CUSTOM CSS
# ============================================================

CSS = """

/* ============================================================
   GLOBAL
   ============================================================ */

:root {
    --bg: #07111f;
    --bg-2: #0a1627;
    --surface: rgba(15, 29, 49, 0.82);
    --surface-2: rgba(19, 36, 60, 0.74);
    --border: rgba(122, 171, 225, 0.14);
    --border-bright: rgba(94, 173, 255, 0.30);
    --text: #f4f8ff;
    --muted: #8fa6c0;
    --blue: #4da3ff;
    --cyan: #50d9ff;
    --purple: #9a7cff;
    --green: #50d5a4;
    --red: #ff7188;
}

body,
.gradio-container {
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(46, 127, 255, 0.11),
            transparent 32%
        ),
        radial-gradient(
            circle at 92% 12%,
            rgba(126, 83, 255, 0.10),
            transparent 30%
        ),
        linear-gradient(
            145deg,
            #050c17 0%,
            #07111f 48%,
            #091728 100%
        ) !important;

    color: var(--text) !important;

    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif !important;
}

.gradio-container {
    max-width: 1500px !important;
    margin: 0 auto !important;
    padding: 0 32px 60px !important;
}

footer {
    display: none !important;
}

* {
    box-sizing: border-box;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    position: relative;
    overflow: hidden;

    margin: 20px 0 26px;

    min-height: 330px;

    border:
        1px solid
        rgba(105, 170, 239, 0.16);

    border-radius: 28px;

    background:
        linear-gradient(
            135deg,
            rgba(15, 37, 66, 0.94),
            rgba(7, 17, 31, 0.97)
        );

    box-shadow:
        0 30px 80px rgba(0, 0, 0, 0.32),
        inset 0 1px 0 rgba(255,255,255,0.035);
}

.hero::before {
    content: "";

    position: absolute;

    inset: 0;

    background-image:
        linear-gradient(
            rgba(105, 170, 239, 0.035) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(105, 170, 239, 0.035) 1px,
            transparent 1px
        );

    background-size: 40px 40px;

    mask-image:
        linear-gradient(
            to bottom,
            black,
            transparent
        );

    pointer-events: none;
}

.hero-glow {
    position: absolute;

    width: 500px;
    height: 500px;

    right: -170px;
    top: -250px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(71, 154, 255, 0.25),
            transparent 68%
        );

    filter: blur(20px);
}

.hero-content {
    position: relative;

    z-index: 2;

    padding: 46px 54px;
}

.brand-row {
    display: flex;

    align-items: center;

    gap: 13px;

    margin-bottom: 34px;
}

.brand-mark {
    width: 44px;
    height: 44px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 13px;

    background:
        linear-gradient(
            145deg,
            #5ab4ff,
            #316bff
        );

    box-shadow:
        0 8px 30px rgba(55, 133, 255, 0.32);
}

.brand-mark-inner {
    font-size: 22px;
    font-weight: 800;
    color: white;
}

.eyebrow {
    font-size: 10px;
    font-weight: 800;

    letter-spacing: 2px;

    color: #6dafff;
}

.brand-name {
    margin-top: 2px;

    font-size: 15px;
    font-weight: 700;

    color: #e9f2ff;
}

.hero-title {
    max-width: 800px;

    font-size: clamp(
        36px,
        5vw,
        62px
    );

    line-height: 1.02;

    letter-spacing: -2.8px;

    font-weight: 800;

    color: #f5f9ff;
}

.hero-title span {
    background:
        linear-gradient(
            90deg,
            #58b4ff,
            #8d86ff,
            #52dcff
        );

    -webkit-background-clip: text;
    background-clip: text;

    color: transparent;
}

.hero-description {
    max-width: 720px;

    margin-top: 20px;

    color: #93a9c1;

    font-size: 15px;

    line-height: 1.7;
}

.hero-badges {
    display: flex;

    gap: 9px;

    flex-wrap: wrap;

    margin-top: 25px;
}

.hero-badge {
    display: flex;

    align-items: center;

    gap: 7px;

    padding: 7px 11px;

    border-radius: 999px;

    border:
        1px solid
        rgba(105, 170, 239, 0.16);

    background:
        rgba(74, 145, 220, 0.07);

    color: #8eb2d8;

    font-size: 9px;
    font-weight: 800;

    letter-spacing: 1.2px;
}

.live-dot {
    width: 6px;
    height: 6px;

    border-radius: 50%;

    background: #52dda8;

    box-shadow:
        0 0 12px #52dda8;
}


/* ============================================================
   STATS
   ============================================================ */

.stats-grid {
    display: grid;

    grid-template-columns:
        repeat(
            4,
            minmax(0, 1fr)
        );

    gap: 15px;

    margin-bottom: 30px;
}

.stat-card {
    position: relative;

    overflow: hidden;

    padding: 22px;

    min-height: 150px;

    border-radius: 19px;

    border:
        1px solid
        var(--border);

    background:
        linear-gradient(
            145deg,
            rgba(17, 34, 56, 0.82),
            rgba(10, 22, 39, 0.80)
        );

    box-shadow:
        0 15px 40px rgba(0, 0, 0, 0.16);
}

.stat-card::after {
    content: "";

    position: absolute;

    width: 130px;
    height: 130px;

    right: -60px;
    bottom: -70px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(77, 163, 255, 0.12),
            transparent 70%
        );
}

.stat-card.purple::after {
    background:
        radial-gradient(
            circle,
            rgba(154, 124, 255, 0.14),
            transparent 70%
        );
}

.stat-card.cyan::after {
    background:
        radial-gradient(
            circle,
            rgba(80, 217, 255, 0.14),
            transparent 70%
        );
}

.stat-card.green::after {
    background:
        radial-gradient(
            circle,
            rgba(80, 213, 164, 0.14),
            transparent 70%
        );
}

.stat-top {
    display: flex;

    align-items: center;

    gap: 10px;
}

.stat-icon {
    width: 32px;
    height: 32px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 10px;

    background:
        rgba(77, 163, 255, 0.10);

    color: #63b5ff;

    font-size: 14px;
}

.purple .stat-icon {
    background:
        rgba(154, 124, 255, 0.11);

    color: #a893ff;
}

.cyan .stat-icon {
    background:
        rgba(80, 217, 255, 0.10);

    color: #5ee0ff;
}

.green .stat-icon {
    background:
        rgba(80, 213, 164, 0.10);

    color: #5ee2b0;
}

.stat-label {
    color: #8ca5bf;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: 1.1px;
}

.stat-value {
    margin-top: 15px;

    font-size: 35px;

    font-weight: 800;

    letter-spacing: -1.5px;

    color: #f4f8ff;
}

.stat-description {
    margin-top: 2px;

    max-width: 230px;

    color: #70869e;

    font-size: 11px;

    line-height: 1.45;
}


/* ============================================================
   SECTIONS
   ============================================================ */

.section-heading,
.results-header {
    display: flex;

    align-items: end;

    justify-content: space-between;

    gap: 20px;

    margin: 36px 0 17px;
}

.section-kicker {
    color: #5faeff;

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 1.8px;
}

.section-title {
    margin-top: 4px;

    font-size: 24px;

    font-weight: 750;

    letter-spacing: -0.6px;

    color: #eef5ff;
}

.result-count {
    padding: 7px 10px;

    border:
        1px solid
        rgba(89, 169, 246, 0.15);

    border-radius: 8px;

    color: #7793af;

    background:
        rgba(72, 145, 220, 0.05);

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 1px;
}


/* ============================================================
   SOURCES
   ============================================================ */

.source-grid {
    display: grid;

    grid-template-columns:
        repeat(
            2,
            minmax(0, 1fr)
        );

    gap: 14px;

    margin-bottom: 12px;
}

.source-mini-card {
    display: flex;

    align-items: center;

    gap: 14px;

    padding: 17px;

    border-radius: 15px;

    border:
        1px solid
        rgba(105, 170, 239, 0.11);

    background:
        rgba(13, 28, 48, 0.63);
}

.source-mini-icon {
    width: 39px;
    height: 39px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 12px;

    background:
        rgba(76, 157, 243, 0.09);

    color: #62b2ff;

    font-size: 14px;
}

.source-mini-name {
    color: #e8f1fb;

    font-size: 13px;

    font-weight: 700;
}

.source-mini-count {
    margin-top: 3px;

    color: #7189a4;

    font-size: 10px;
}


/* ============================================================
   FILTERS
   ============================================================ */

.filter-panel {
    padding: 18px;

    margin: 27px 0 10px;

    border-radius: 18px;

    border:
        1px solid
        rgba(105, 170, 239, 0.12);

    background:
        rgba(12, 25, 43, 0.74);

    backdrop-filter: blur(20px);
}

.filter-title {
    margin-bottom: 13px;

    color: #91abc4;

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 1.6px;
}

.search-input input,
.filter-select input,
.filter-select select {
    background:
        rgba(7, 17, 30, 0.72) !important;

    border:
        1px solid
        rgba(104, 163, 218, 0.14) !important;

    color: #eaf3ff !important;

    border-radius: 11px !important;
}

.search-input input:focus {
    border-color:
        rgba(77, 163, 255, 0.45) !important;

    box-shadow:
        0 0 0 3px
        rgba(77, 163, 255, 0.07) !important;
}

.filter-select label,
.search-input label {
    color: #7e97b1 !important;

    font-size: 9px !important;

    font-weight: 800 !important;

    letter-spacing: 1px !important;
}


/* ============================================================
   TENDER GRID
   ============================================================ */

.tender-grid {
    display: grid;

    grid-template-columns:
        repeat(
            2,
            minmax(0, 1fr)
        );

    gap: 16px;
}

.tender-card {
    position: relative;

    overflow: hidden;

    padding: 22px;

    min-height: 340px;

    border-radius: 20px;

    border:
        1px solid
        rgba(111, 169, 225, 0.13);

    background:
        linear-gradient(
            150deg,
            rgba(17, 34, 57, 0.88),
            rgba(10, 21, 37, 0.91)
        );

    box-shadow:
        0 18px 45px rgba(0, 0, 0, 0.17);

    transition:
        transform 0.18s ease,
        border-color 0.18s ease,
        box-shadow 0.18s ease;
}

.tender-card:hover {
    transform:
        translateY(-3px);

    border-color:
        rgba(87, 169, 249, 0.30);

    box-shadow:
        0 24px 55px rgba(0, 0, 0, 0.25),
        0 0 40px rgba(62, 146, 255, 0.045);
}

.tender-card-top {
    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 10px;
}

.source-pill {
    display: inline-flex;

    align-items: center;

    gap: 7px;

    color: #7994b0;

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 0.8px;

    text-transform: uppercase;
}

.source-dot {
    width: 6px;
    height: 6px;

    border-radius: 50%;

    background: #54b4ff;

    box-shadow:
        0 0 10px rgba(84, 180, 255, 0.6);
}

.priority-pill {
    padding: 5px 8px;

    border-radius: 6px;

    font-size: 8px;

    font-weight: 900;

    letter-spacing: 1px;
}

.priority-pill.medium {
    color: #67cfff;

    background:
        rgba(80, 195, 255, 0.09);

    border:
        1px solid
        rgba(80, 195, 255, 0.16);
}

.priority-pill.high {
    color: #aa96ff;

    background:
        rgba(154, 124, 255, 0.10);

    border:
        1px solid
        rgba(154, 124, 255, 0.18);
}

.tender-card-title {
    margin-top: 18px;

    min-height: 66px;

    color: #f1f6fd;

    font-size: 16px;

    line-height: 1.45;

    font-weight: 720;

    letter-spacing: -0.25px;
}

.tender-card-org {
    display: flex;

    align-items: center;

    gap: 7px;

    margin-top: 10px;

    color: #7892ad;

    font-size: 10px;

    line-height: 1.4;
}

.meta-icon {
    color: #559fe5;
}

.tender-card-divider {
    height: 1px;

    margin: 18px 0;

    background:
        rgba(122, 169, 214, 0.10);
}

.tender-meta-grid {
    display: grid;

    grid-template-columns:
        1.25fr
        1fr;

    gap: 15px 18px;
}

.meta-label {
    color: #607995;

    font-size: 7px;

    font-weight: 800;

    letter-spacing: 1.15px;
}

.meta-value {
    margin-top: 4px;

    color: #c2d2e3;

    font-size: 10px;

    line-height: 1.35;

    word-break: break-word;
}

.meta-value.closing {
    color: #68c7ff;
}

.relevance-row {
    margin-top: 20px;
}

.relevance-label {
    display: flex;

    justify-content: space-between;

    margin-bottom: 7px;

    color: #647d98;

    font-size: 8px;

    font-weight: 800;

    letter-spacing: 1px;
}

.relevance-label strong {
    color: #6ebdff;

    font-size: 10px;
}

.progress-track {
    width: 100%;
    height: 4px;

    overflow: hidden;

    border-radius: 999px;

    background:
        rgba(111, 150, 190, 0.10);
}

.progress-fill {
    height: 100%;

    border-radius: 999px;

    background:
        linear-gradient(
            90deg,
            #3f8fff,
            #54d5ff
        );

    box-shadow:
        0 0 13px rgba(74, 164, 255, 0.35);
}

.progress-fill.high {
    background:
        linear-gradient(
            90deg,
            #7c67ff,
            #bb86ff
        );
}

.keyword-row {
    display: flex;

    gap: 6px;

    flex-wrap: wrap;

    margin-top: 15px;
}

.keyword-chip {
    padding: 5px 8px;

    border-radius: 6px;

    border:
        1px solid
        rgba(78, 166, 244, 0.13);

    color: #77bdf2;

    background:
        rgba(72, 158, 239, 0.055);

    font-size: 8px;

    font-weight: 700;
}

.keyword-chip.muted {
    color: #778ba1;

    border-color:
        rgba(120, 145, 170, 0.11);

    background:
        rgba(120, 145, 170, 0.04);
}

.card-index {
    position: absolute;

    right: 20px;
    bottom: 17px;

    color: rgba(116, 145, 174, 0.22);

    font-size: 10px;

    font-weight: 900;

    letter-spacing: 1px;
}


/* ============================================================
   EMPTY
   ============================================================ */

.empty-state {
    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    min-height: 260px;

    padding: 50px;

    border:
        1px dashed
        rgba(110, 163, 211, 0.15);

    border-radius: 20px;

    background:
        rgba(11, 24, 41, 0.48);
}

.empty-icon {
    font-size: 38px;

    color: #467da8;
}

.empty-title {
    margin-top: 10px;

    color: #b4c8dd;

    font-size: 15px;

    font-weight: 700;
}

.empty-description {
    margin-top: 5px;

    color: #657d97;

    font-size: 11px;
}


/* ============================================================
   DETAIL PANEL
   ============================================================ */

.detail-panel {
    margin-top: 24px;

    padding: 30px;

    border-radius: 22px;

    border:
        1px solid
        rgba(105, 170, 239, 0.15);

    background:
        linear-gradient(
            145deg,
            rgba(15, 32, 54, 0.91),
            rgba(8, 19, 34, 0.94)
        );

    box-shadow:
        0 25px 70px rgba(0, 0, 0, 0.23);
}

.detail-header {
    display: flex;

    justify-content: space-between;

    align-items: flex-start;

    gap: 20px;
}

.detail-source {
    color: #5cafff;

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 1.5px;
}

.detail-title {
    max-width: 950px;

    margin-top: 9px;

    color: #f3f7fd;

    font-size: 25px;

    line-height: 1.3;

    font-weight: 760;

    letter-spacing: -0.6px;
}

.detail-priority {
    padding: 8px 12px;

    border-radius: 8px;

    font-size: 9px;

    font-weight: 900;

    letter-spacing: 1.2px;

    white-space: nowrap;
}

.detail-priority.medium {
    color: #65ccff;

    background:
        rgba(78, 193, 255, 0.08);

    border:
        1px solid
        rgba(78, 193, 255, 0.18);
}

.detail-priority.high {
    color: #ad98ff;

    background:
        rgba(154, 124, 255, 0.09);

    border:
        1px solid
        rgba(154, 124, 255, 0.18);
}

.detail-score-panel {
    display: flex;

    align-items: center;

    gap: 24px;

    margin-top: 30px;

    padding: 20px;

    border-radius: 16px;

    background:
        rgba(61, 128, 203, 0.045);

    border:
        1px solid
        rgba(87, 164, 239, 0.09);
}

.score-ring {
    width: 92px;
    height: 92px;

    flex-shrink: 0;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    border-radius: 50%;

    border:
        5px solid
        rgba(78, 166, 247, 0.15);

    box-shadow:
        0 0 30px rgba(64, 158, 248, 0.08);
}

.score-number {
    color: #71c2ff;

    font-size: 23px;

    font-weight: 850;

    letter-spacing: -1px;
}

.score-caption {
    margin-top: 1px;

    color: #637f9c;

    font-size: 6px;

    font-weight: 900;

    letter-spacing: 1.1px;
}

.score-info {
    flex: 1;
}

.score-heading {
    color: #dce9f7;

    font-size: 14px;

    font-weight: 720;
}

.score-description {
    max-width: 700px;

    margin-top: 6px;

    color: #718aa4;

    font-size: 10px;

    line-height: 1.55;
}

.detail-progress {
    height: 5px;

    margin-top: 14px;

    overflow: hidden;

    border-radius: 999px;

    background:
        rgba(110, 148, 185, 0.10);
}

.detail-progress-fill {
    height: 100%;

    border-radius: 999px;

    background:
        linear-gradient(
            90deg,
            #438fff,
            #55d9ff
        );
}

.detail-section {
    margin-top: 30px;
}

.detail-section-title {
    margin-bottom: 14px;

    color: #8ea9c3;

    font-size: 9px;

    font-weight: 850;

    letter-spacing: 1.6px;
}

.detail-fields {
    display: grid;

    grid-template-columns:
        repeat(
            2,
            minmax(0, 1fr)
        );

    gap: 1px;

    overflow: hidden;

    border-radius: 14px;

    border:
        1px solid
        rgba(107, 155, 202, 0.10);

    background:
        rgba(105, 155, 205, 0.07);
}

.detail-field {
    padding: 15px;

    min-height: 67px;

    background:
        rgba(9, 21, 36, 0.70);
}

.detail-field-label {
    color: #5f7894;

    font-size: 7px;

    font-weight: 850;

    letter-spacing: 1.1px;
}

.detail-field-value {
    margin-top: 5px;

    color: #c6d6e7;

    font-size: 11px;

    line-height: 1.4;

    word-break: break-word;
}

.detail-field-value.closing {
    color: #65c9ff;
}

.detail-signal-box {
    margin-top: 10px;

    padding: 14px 15px;

    border-radius: 12px;

    border:
        1px solid
        rgba(99, 157, 212, 0.10);

    background:
        rgba(8, 20, 35, 0.60);
}

.signal-label {
    color: #607c98;

    font-size: 7px;

    font-weight: 850;

    letter-spacing: 1.1px;
}

.detail-chips {
    display: flex;

    flex-wrap: wrap;

    gap: 6px;

    margin-top: 8px;
}

.detail-chip {
    padding: 6px 9px;

    border-radius: 7px;

    color: #75c1fa;

    border:
        1px solid
        rgba(82, 173, 247, 0.14);

    background:
        rgba(67, 153, 237, 0.06);

    font-size: 8px;

    font-weight: 750;
}

.detail-chip.phrase {
    color: #a895ff;

    border-color:
        rgba(157, 133, 255, 0.15);

    background:
        rgba(157, 133, 255, 0.06);
}

.signal-muted {
    color: #607993;

    font-size: 9px;

    line-height: 1.5;
}

.detail-action {
    display: flex;

    justify-content: flex-end;

    margin-top: 28px;
}

.open-tender-button {
    display: inline-flex;

    align-items: center;

    gap: 9px;

    padding: 11px 17px;

    border-radius: 10px;

    color: white !important;

    background:
        linear-gradient(
            135deg,
            #438fff,
            #3675e7
        );

    box-shadow:
        0 9px 25px
        rgba(51, 121, 236, 0.20);

    text-decoration: none !important;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: 0.2px;

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease;
}

.open-tender-button:hover {
    transform:
        translateY(-1px);

    box-shadow:
        0 13px 30px
        rgba(51, 121, 236, 0.30);
}

.no-url {
    padding: 11px 14px;

    border-radius: 9px;

    color: #71869d;

    background:
        rgba(105, 135, 165, 0.06);

    font-size: 9px;
}

.detail-empty {
    margin-top: 24px;

    padding: 50px;

    text-align: center;

    border-radius: 20px;

    border:
        1px dashed
        rgba(110, 163, 211, 0.14);

    color: #7189a3;

    background:
        rgba(11, 24, 41, 0.45);

    font-size: 12px;
}


/* ============================================================
   BUTTONS
   ============================================================ */

button {
    border-radius: 10px !important;
}

.refresh-button {
    border:
        1px solid
        rgba(81, 168, 246, 0.18) !important;

    background:
        rgba(65, 139, 220, 0.08) !important;

    color: #79bdff !important;

    font-weight: 700 !important;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 900px) {

    .gradio-container {
        padding:
            0 15px 40px !important;
    }

    .hero-content {
        padding:
            34px 27px;
    }

    .hero-title {
        font-size: 40px;

        letter-spacing: -1.8px;
    }

    .stats-grid {
        grid-template-columns:
            repeat(
                2,
                minmax(0, 1fr)
            );
    }

    .tender-grid {
        grid-template-columns:
            1fr;
    }

    .source-grid {
        grid-template-columns:
            1fr;
    }

    .detail-fields {
        grid-template-columns:
            1fr;
    }
}

@media (max-width: 560px) {

    .stats-grid {
        grid-template-columns:
            1fr;
    }

    .hero {
        min-height: 380px;
    }

    .hero-title {
        font-size: 34px;
    }

    .detail-score-panel {
        flex-direction: column;

        align-items: flex-start;
    }

    .detail-title {
        font-size: 20px;
    }

    .tender-card {
        padding: 18px;
    }
}

"""


# ============================================================
# INITIAL DATA
# ============================================================

INITIAL_TENDERS = load_tenders()

INITIAL_SOURCES = sorted(
    set(
        get_source(tender)
        for tender in INITIAL_TENDERS
    )
)

SOURCE_CHOICES = [
    "All Sources"
] + INITIAL_SOURCES


# ============================================================
# APPLICATION
# ============================================================

# IMPORTANT:
# In Gradio 6.x, theme and CSS are passed to launch(),
# not to the Blocks constructor.

with gr.Blocks(
    title=APP_TITLE,
) as app:

    # --------------------------------------------------------
    # State
    # --------------------------------------------------------

    selected_index = gr.State(
        value=-1
    )

    # --------------------------------------------------------
    # Hero
    # --------------------------------------------------------

    gr.HTML(
        build_header()
    )

    # --------------------------------------------------------
    # Executive Stats
    # --------------------------------------------------------

    stats = gr.HTML(
        value=build_stats(
            INITIAL_TENDERS
        )
    )

    # --------------------------------------------------------
    # Source Overview
    # --------------------------------------------------------

    source_overview = gr.HTML(
        value=build_source_overview(
            INITIAL_TENDERS
        )
    )

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    gr.HTML(
        """
        <div class="filter-panel">

            <div class="filter-title">
                INTELLIGENCE FILTERS
            </div>

        </div>
        """
    )

    with gr.Row():

        search_box = gr.Textbox(
            label="SEARCH",
            placeholder=(
                "Search title, organization, "
                "tender number, keyword..."
            ),
            scale=3,
            elem_classes=[
                "search-input"
            ],
        )

        source_dropdown = gr.Dropdown(
            label="SOURCE",
            choices=SOURCE_CHOICES,
            value="All Sources",
            scale=1,
            elem_classes=[
                "filter-select"
            ],
        )

        relevance_dropdown = gr.Dropdown(
            label="RELEVANCE",
            choices=[
                "All Relevance",
                "HIGH",
                "MEDIUM",
            ],
            value="All Relevance",
            scale=1,
            elem_classes=[
                "filter-select"
            ],
        )

        min_score_slider = gr.Slider(
            label="MIN AI SCORE",
            minimum=0.0,
            maximum=1.0,
            value=0.0,
            step=0.01,
            scale=1,
        )

    with gr.Row():

        refresh_button = gr.Button(
            "↻  Refresh Intelligence",
            elem_classes=[
                "refresh-button"
            ],
            scale=1,
        )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    results = gr.HTML(
        value=build_tender_grid(
            sorted(
                INITIAL_TENDERS,
                key=get_score,
                reverse=True,
            )
        )
    )

    # --------------------------------------------------------
    # Detail selection
    # --------------------------------------------------------

    gr.Markdown(
        "### Tender Inspection"
    )

    with gr.Row():

        tender_selector = gr.Number(
            label=(
                "Tender result number "
                "(1 = first result)"
            ),
            value=1,
            minimum=1,
            precision=0,
            scale=1,
        )

        inspect_button = gr.Button(
            "Inspect Tender →",
            variant="primary",
            scale=1,
        )

    detail = gr.HTML(
        value=build_detail_view(
            None
        )
    )

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    gr.HTML(
        """
        <div style="
            text-align:center;
            margin-top:50px;
            padding-top:25px;
            border-top:1px solid rgba(105,170,239,0.08);
            color:#526b85;
            font-size:9px;
            letter-spacing:1px;
        ">
            JAZZWORLD · B2G · TENDER INTELLIGENCE
            &nbsp;&nbsp;•&nbsp;&nbsp;
            AI-POWERED PROCUREMENT DISCOVERY
        </div>
        """
    )

    # ========================================================
    # EVENTS
    # ========================================================

    filter_inputs = [
        search_box,
        source_dropdown,
        relevance_dropdown,
        min_score_slider,
    ]

    for component in filter_inputs:

        component.change(
            fn=apply_filters,
            inputs=filter_inputs,
            outputs=results,
        )

    refresh_button.click(
        fn=refresh_dashboard,
        inputs=[],
        outputs=[
            stats,
            source_overview,
            results,
            source_dropdown,
        ],
    )

    inspect_button.click(
        fn=select_tender,
        inputs=[
            tender_selector,
            search_box,
            source_dropdown,
            relevance_dropdown,
            min_score_slider,
        ],
        outputs=detail,
    )


# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("TENDER INTELLIGENCE DASHBOARD")
    print("=" * 70)

    print(
        f"Data file: {DATA_FILE}"
    )

    print(
        f"Relevant tenders: "
        f"{len(INITIAL_TENDERS)}"
    )

    print(
        "Dashboard URL: "
        "http://127.0.0.1:7860"
    )

    print("=" * 70)
    print()

    # IMPORTANT:
    # Gradio 6.x expects theme and CSS here.
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True,
        inbrowser=True,
        theme=gr.themes.Base(
            primary_hue="blue",
            neutral_hue="slate",
        ),
        css=CSS,
    )
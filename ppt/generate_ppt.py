import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


# ── Color palette ─────────────────────────────────────────────────────────────
DARK_BG    = RGBColor(0x05, 0x0D, 0x1F)
CARD_BG    = RGBColor(0x0F, 0x1E, 0x3C)
ACCENT     = RGBColor(0x63, 0x66, 0xF1)
ACCENT2    = RGBColor(0x81, 0x8C, 0xF8)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
GRAY       = RGBColor(0x94, 0xA3, 0xB8)
GREEN      = RGBColor(0x10, 0xB9, 0x81)
AMBER      = RGBColor(0xF5, 0x9E, 0x0B)
RED        = RGBColor(0xEF, 0x44, 0x44)
VIOLET     = RGBColor(0xA7, 0x8B, 0xFA)

W = Inches(13.33)
H = Inches(7.5)


def new_prs():
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H
    return prs


def blank_slide(prs):
    layout = prs.slide_layouts[6]   # completely blank
    return prs.slides.add_slide(layout)


def bg(slide, color=DARK_BG):
    from pptx.util import Emu
    shape = slide.shapes.add_shape(1, 0, 0, W, H)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.zorder = 0


def add_text(slide, text, left, top, width, height,
             size=18, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, wrap=True):
    txb = slide.shapes.add_textbox(left, top, width, height)
    txb.word_wrap = wrap
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txb


def rect(slide, left, top, width, height, fill_color, line_color=None, radius=None):
    shape = slide.shapes.add_shape(1, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def header_bar(slide, title, subtitle=None):
    rect(slide, 0, 0, W, Inches(1.1), CARD_BG)
    add_text(slide, title,
             Inches(0.5), Inches(0.18), Inches(10), Inches(0.6),
             size=28, bold=True, color=WHITE)
    if subtitle:
        add_text(slide, subtitle,
                 Inches(0.5), Inches(0.72), Inches(10), Inches(0.35),
                 size=13, color=GRAY)
    # accent line
    rect(slide, 0, Inches(1.1), W, Pt(3), ACCENT)


def card(slide, left, top, width, height, fill=CARD_BG, border=ACCENT):
    return rect(slide, left, top, width, height, fill, border)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def slide_title(prs):
    sl = blank_slide(prs)
    bg(sl)
    # gradient overlay shape (simulated)
    rect(sl, 0, 0, W, Inches(0.5), RGBColor(0x1E, 0x1B, 0x4B))

    add_text(sl, "GEO Analytics Platform",
             Inches(1), Inches(1.2), Inches(11), Inches(1),
             size=44, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, "Product Strategy & Monetization Roadmap  |  2025–2026",
             Inches(1), Inches(2.3), Inches(11), Inches(0.6),
             size=22, color=ACCENT2, align=PP_ALIGN.CENTER)
    add_text(sl,
             "Generative Engine Optimization · AI Visibility · LLM Search Analytics",
             Inches(1), Inches(3.0), Inches(11), Inches(0.5),
             size=14, color=GRAY, align=PP_ALIGN.CENTER)

    # Bottom bar
    rect(sl, 0, Inches(6.8), W, Inches(0.7), CARD_BG)
    add_text(sl, "Confidential  |  GEO Team  |  May 2025",
             Inches(0.5), Inches(6.85), Inches(12), Inches(0.4),
             size=11, color=GRAY, align=PP_ALIGN.RIGHT)


def slide_agenda(prs):
    sl = blank_slide(prs)
    bg(sl)
    header_bar(sl, "Agenda", "What we'll cover today")

    items = [
        ("01", "The AI Search Revolution",     "Current state of LLM-driven search"),
        ("02", "What is GEO?",                 "vs. traditional SEO — the paradigm shift"),
        ("03", "Featured Feature Deep-Dive",   "LLM Visibility Intelligence Suite"),
        ("04", "Competitor Landscape",         "Profound, Peec AI, Otterly, Semrush & more"),
        ("05", "3-Month Roadmap",              "Foundation, adoption & quick wins"),
        ("06", "12-Month Roadmap",             "Scale, differentiate & enterprise"),
        ("07", "Monetization Strategy",        "Freemium → Pro → Enterprise tiers"),
        ("08", "KPIs & Success Metrics",       "How we measure what matters"),
    ]

    col_w = Inches(5.8)
    for i, (num, title, sub) in enumerate(items):
        col = i % 2
        row = i // 2
        left = Inches(0.5) + col * (col_w + Inches(0.4))
        top  = Inches(1.4) + row * Inches(1.3)
        c = card(sl, left, top, col_w, Inches(1.1))
        add_text(sl, num,  left + Inches(0.15), top + Inches(0.1),  Inches(0.5),  Inches(0.35), size=13, bold=True, color=ACCENT2)
        add_text(sl, title, left + Inches(0.6),  top + Inches(0.08), Inches(5),    Inches(0.42), size=14, bold=True, color=WHITE)
        add_text(sl, sub,   left + Inches(0.6),  top + Inches(0.55), Inches(5),    Inches(0.42), size=11, color=GRAY)


def slide_ai_revolution(prs):
    sl = blank_slide(prs)
    bg(sl)
    header_bar(sl, "The AI Search Revolution", "The structural shift brands can't ignore")

    stats = [
        ("40%", "of Google searches\nnow return AI Overviews",    ACCENT),
        ("30-40%", "CAGR projected for\nGEO services market",     GREEN),
        ("$1T+", "digital ad spend\nat risk from zero-click",     AMBER),
        ("5+", "major LLMs now act\nas primary search engines",   VIOLET),
    ]
    sw = Inches(2.8)
    for i, (val, label, col) in enumerate(stats):
        left = Inches(0.5) + i * (sw + Inches(0.22))
        c = card(sl, left, Inches(1.4), sw, Inches(1.8))
        add_text(sl, val,   left + Inches(0.2), Inches(1.55), sw - Inches(0.3), Inches(0.7),
                 size=30, bold=True, color=col, align=PP_ALIGN.CENTER)
        add_text(sl, label, left + Inches(0.2), Inches(2.3),  sw - Inches(0.3), Inches(0.7),
                 size=11, color=GRAY, align=PP_ALIGN.CENTER)

    # Shift diagram
    add_text(sl, "The Paradigm Shift",
             Inches(0.5), Inches(3.5), Inches(12), Inches(0.4),
             size=16, bold=True, color=WHITE)

    shifts = [
        ("Traditional SEO", "LLM / GEO", "Keyword Rankings", "Brand Citations in AI Answers",
         "Blue-link SERP clicks", "Zero-click AI synthesis", "Backlinks & Domain Authority", "Entity Trust & Factual Density"),
    ]
    for (old_t, new_t, a, b, c2, d, e, f) in shifts:
        card(sl, Inches(0.5), Inches(4.0), Inches(5.5), Inches(2.8), fill=RGBColor(0x1A,0x08,0x08), border=RED)
        add_text(sl, "❌  " + old_t, Inches(0.7), Inches(4.1), Inches(5), Inches(0.4), size=14, bold=True, color=RED)
        for j, txt in enumerate([a, c2, e]):
            add_text(sl, "• " + txt, Inches(0.8), Inches(4.55) + j * Inches(0.55),
                     Inches(5), Inches(0.45), size=11, color=GRAY)

        card(sl, Inches(7.2), Inches(4.0), Inches(5.5), Inches(2.8), fill=RGBColor(0x04,0x1F,0x12), border=GREEN)
        add_text(sl, "✅  " + new_t, Inches(7.4), Inches(4.1), Inches(5), Inches(0.4), size=14, bold=True, color=GREEN)
        for j, txt in enumerate([b, d, f]):
            add_text(sl, "• " + txt, Inches(7.5), Inches(4.55) + j * Inches(0.55),
                     Inches(5), Inches(0.45), size=11, color=GRAY)

        add_text(sl, "→", Inches(6.1), Inches(5.1), Inches(1), Inches(0.6),
                 size=28, bold=True, color=ACCENT2, align=PP_ALIGN.CENTER)


def slide_feature(prs):
    sl = blank_slide(prs)
    bg(sl)
    header_bar(sl, "Featured Feature: LLM Visibility Intelligence Suite",
               "Proposed new feature for the GEO platform")

    # Left col — what it is
    card(sl, Inches(0.4), Inches(1.3), Inches(5.8), Inches(5.6))
    add_text(sl, "What It Does", Inches(0.6), Inches(1.45), Inches(5.4), Inches(0.4),
             size=15, bold=True, color=ACCENT2)
    features = [
        "🔍  Real-time brand mention tracking across ChatGPT, Gemini, Claude, Perplexity",
        "📊  Share-of-Voice dashboard vs. competitors in AI-generated answers",
        "🏷️  Sentiment scoring: positive / neutral / negative brand portrayal per LLM",
        "⚡  Citation source analysis — which URLs LLMs cite for your brand",
        "🔔  Alerts when brand drops below visibility threshold",
        "📈  Historical trend tracking with weekly change detection",
    ]
    for i, f in enumerate(features):
        add_text(sl, f, Inches(0.6), Inches(1.95) + i * Inches(0.7),
                 Inches(5.4), Inches(0.6), size=11, color=GRAY)

    # Right col — user journey
    card(sl, Inches(6.5), Inches(1.3), Inches(6.4), Inches(5.6))
    add_text(sl, "User Journey", Inches(6.7), Inches(1.45), Inches(6), Inches(0.4),
             size=15, bold=True, color=ACCENT2)
    steps = [
        ("1", "Connect Brand",   "Enter brand name, keywords & competitors"),
        ("2", "Define Prompts",  "Set industry-relevant queries to track"),
        ("3", "Auto-Scan LLMs",  "Scheduled polling across 5+ AI engines"),
        ("4", "Dashboard View",  "Share of Voice, citations, sentiment"),
        ("5", "Action Briefs",   "AI-generated content recommendations"),
    ]
    for i, (n, title, desc) in enumerate(steps):
        top = Inches(1.95) + i * Inches(0.95)
        rect(sl, Inches(6.6), top, Inches(0.45), Inches(0.45), ACCENT)
        add_text(sl, n, Inches(6.6), top + Inches(0.05), Inches(0.45), Inches(0.4),
                 size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text(sl, title, Inches(7.15), top, Inches(2.5), Inches(0.38),
                 size=12, bold=True, color=WHITE)
        add_text(sl, desc, Inches(7.15), top + Inches(0.38), Inches(5.5), Inches(0.45),
                 size=10, color=GRAY)


def slide_competitors(prs):
    sl = blank_slide(prs)
    bg(sl)
    header_bar(sl, "Competitor Landscape", "GEO & AI Visibility Analytics Tools — 2025")

    headers = ["Tool", "Focus", "LLMs Covered", "Pricing", "Differentiator", "Gap"]
    rows = [
        ["Profound",     "Enterprise AEO",         "5+",  "$399+/mo",  "Content generation + SOC2",  "High cost, no PDF checks"],
        ["Peec AI",      "Regional precision",      "4+",  "€85+/mo",   "115+ languages, UI scraping","Limited actionability"],
        ["Otterly AI",   "SMB monitoring",          "4",   "$29+/mo",   "Easy setup, GEO audits",     "No competitive intel"],
        ["Semrush AI",   "Integrated SEO+AI",       "3",   "Add-on",    "Unified SEO+AI workflow",    "Shallow AI-specific depth"],
        ["BrightEdge",   "Enterprise SEO",          "3",   "Custom",    "Generative Parser",          "Enterprise-only pricing"],
        ["Riff Analytics","Multi-model coverage",   "5+",  "Contact",   "Deep multi-LLM tracking",    "Early stage, no content tools"],
        ["Our GEO ✨",   "Full-stack visibility",   "6+",  "Freemium",  "LLM Suite + Fact-check layer","— Opportunity —"],
    ]

    col_widths = [Inches(1.5), Inches(1.8), Inches(1.3), Inches(1.1), Inches(2.9), Inches(2.4)]
    row_h = Inches(0.68)
    top_start = Inches(1.3)

    # Header row
    left = Inches(0.25)
    for j, (h, w) in enumerate(zip(headers, col_widths)):
        rect(sl, left, top_start, w, Inches(0.45), ACCENT)
        add_text(sl, h, left + Inches(0.05), top_start + Inches(0.05),
                 w - Inches(0.1), Inches(0.35), size=11, bold=True, color=WHITE)
        left += w

    for i, row in enumerate(rows):
        row_top = top_start + Inches(0.45) + i * row_h
        fill = RGBColor(0x1A, 0x2A, 0x4A) if row[0].startswith("Our") else CARD_BG
        bdr  = GREEN if row[0].startswith("Our") else ACCENT
        cell_left = Inches(0.25)
        for j, (cell, cw) in enumerate(zip(row, col_widths)):
            rect(sl, cell_left, row_top, cw, row_h - Inches(0.04), fill, bdr)
            cell_col = GREEN if row[0].startswith("Our") else (WHITE if j == 0 else GRAY)
            add_text(sl, cell, cell_left + Inches(0.05), row_top + Inches(0.12),
                     cw - Inches(0.1), row_h - Inches(0.18), size=9, color=cell_col)
            cell_left += cw


def slide_roadmap_3m(prs):
    sl = blank_slide(prs)
    bg(sl)
    header_bar(sl, "Short-Term Roadmap: 0–3 Months", "Q3 2025 — Foundation & Adoption Sprint")

    months = [
        ("Month 1\nFoundation",   ACCENT,  [
            "Launch LLM Visibility Intelligence Suite (beta)",
            "Integrate ChatGPT, Gemini, Perplexity tracking",
            "Onboard 50 beta brands with white-glove support",
            "Establish baseline Share-of-Voice benchmarks",
        ]),
        ("Month 2\nGrowth",       GREEN,   [
            "Add Claude & Llama model coverage",
            "Launch competitor benchmarking module",
            "Release weekly email digest reports",
            "Hit 200 paying customers (Pro tier)",
        ]),
        ("Month 3\nOptimization", AMBER,   [
            "Release AI-generated content recommendation briefs",
            "Introduce citation source optimization guide",
            "API access for enterprise integrations (beta)",
            "Achieve $25K MRR milestone",
        ]),
    ]

    col_w = Inches(3.9)
    for i, (title, col, bullets) in enumerate(months):
        left = Inches(0.35) + i * (col_w + Inches(0.3))
        card(sl, left, Inches(1.35), col_w, Inches(5.6))
        rect(sl, left, Inches(1.35), col_w, Inches(0.55), col)
        add_text(sl, title, left + Inches(0.15), Inches(1.38),
                 col_w - Inches(0.2), Inches(0.5), size=14, bold=True,
                 color=WHITE, align=PP_ALIGN.CENTER)
        for j, b in enumerate(bullets):
            add_text(sl, "▸  " + b,
                     left + Inches(0.2), Inches(2.1) + j * Inches(0.9),
                     col_w - Inches(0.3), Inches(0.8), size=11, color=GRAY)


def slide_roadmap_12m(prs):
    sl = blank_slide(prs)
    bg(sl)
    header_bar(sl, "Long-Term Roadmap: 3–12 Months", "Q4 2025 – Q3 2026 — Scale & Differentiate")

    phases = [
        ("Q4 2025\nMonths 4–6",   ACCENT,  [
            "GA launch of LLM Suite",
            "Enterprise SSO & SOC 2 compliance",
            "White-label API for agencies",
            "500 paying brands · $75K MRR",
        ]),
        ("Q1 2026\nMonths 7–9",   VIOLET,  [
            "Multimodal tracking (images, video)",
            "Predictive visibility scoring with ML",
            "Salesforce / HubSpot CRM integrations",
            "1,000 brands · $180K MRR",
        ]),
        ("Q2–Q3 2026\nMonths 10–12", GREEN, [
            "Self-serve content optimization engine",
            "Industry benchmark reports (public)",
            "Series A fundraising readiness",
            "2,500 brands · $450K MRR",
        ]),
    ]

    col_w = Inches(3.9)
    for i, (title, col, bullets) in enumerate(phases):
        left = Inches(0.35) + i * (col_w + Inches(0.3))
        card(sl, left, Inches(1.35), col_w, Inches(5.6))
        rect(sl, left, Inches(1.35), col_w, Inches(0.55), col)
        add_text(sl, title, left + Inches(0.15), Inches(1.38),
                 col_w - Inches(0.2), Inches(0.5), size=14, bold=True,
                 color=WHITE, align=PP_ALIGN.CENTER)
        for j, b in enumerate(bullets):
            add_text(sl, "▸  " + b,
                     left + Inches(0.2), Inches(2.1) + j * Inches(0.9),
                     col_w - Inches(0.3), Inches(0.8), size=11, color=GRAY)


def slide_monetization(prs):
    sl = blank_slide(prs)
    bg(sl)
    header_bar(sl, "Monetization Strategy", "Three-tier model: Freemium → Pro → Enterprise")

    tiers = [
        ("🆓 Freemium", "$0/mo", GRAY, [
            "1 brand tracked",
            "3 LLMs (ChatGPT, Gemini, Perplexity)",
            "Weekly reports only",
            "5 tracked queries",
            "Community support",
        ]),
        ("⚡ Pro", "$99/mo", ACCENT, [
            "5 brands + 3 competitors",
            "All 6+ LLMs covered",
            "Daily real-time reports",
            "50 tracked queries",
            "Content recommendation briefs",
            "Email alerts & Slack integration",
            "Priority support",
        ]),
        ("🏢 Enterprise", "Custom", GREEN, [
            "Unlimited brands & competitors",
            "Custom LLM coverage",
            "White-label reports",
            "API access (full)",
            "SSO + SOC 2 compliance",
            "Dedicated CSM",
            "SLA guarantees",
        ]),
    ]

    col_w = Inches(3.9)
    for i, (name, price, col, bullets) in enumerate(tiers):
        left = Inches(0.35) + i * (col_w + Inches(0.3))
        is_pro = name.startswith("⚡")
        bdr = ACCENT if is_pro else col
        card(sl, left, Inches(1.35), col_w, Inches(5.7), border=bdr)

        if is_pro:
            rect(sl, left, Inches(1.32), col_w, Inches(0.06), ACCENT)

        add_text(sl, name,  left + Inches(0.2), Inches(1.5), col_w - Inches(0.3), Inches(0.45),
                 size=16, bold=True, color=col)
        add_text(sl, price, left + Inches(0.2), Inches(2.0), col_w - Inches(0.3), Inches(0.5),
                 size=26, bold=True, color=WHITE)

        rect(sl, left + Inches(0.2), Inches(2.52), col_w - Inches(0.3), Pt(1), col)

        for j, b in enumerate(bullets):
            add_text(sl, "✓  " + b,
                     left + Inches(0.25), Inches(2.65) + j * Inches(0.58),
                     col_w - Inches(0.4), Inches(0.5), size=10, color=GRAY)


def slide_kpis(prs):
    sl = blank_slide(prs)
    bg(sl)
    header_bar(sl, "KPIs & Success Metrics", "How we measure product success")

    kpis = [
        ("📈", "Share of Voice",       "% of AI answers mentioning brand",        "Target: 15%+ for tracked queries"),
        ("👥", "Paying Brands",         "# of active Pro + Enterprise accounts",    "Target: 500 by Month 6"),
        ("💰", "MRR Growth",            "Monthly Recurring Revenue",                "Target: $75K by Q4 2025"),
        ("⏱️", "Time-to-First-Insight", "Minutes from signup to first dashboard",   "Target: < 5 minutes"),
        ("🔄", "NPS Score",             "Net Promoter Score from customer surveys", "Target: 50+"),
        ("📉", "Churn Rate",            "Monthly subscription cancellations",       "Target: < 3% monthly"),
    ]

    col_w = Inches(5.8)
    for i, (icon, title, desc, target) in enumerate(kpis):
        col = i % 2
        row = i // 2
        left = Inches(0.4) + col * (col_w + Inches(0.5))
        top  = Inches(1.4) + row * Inches(1.65)
        card(sl, left, top, col_w, Inches(1.48))
        add_text(sl, icon + "  " + title,
                 left + Inches(0.2), top + Inches(0.12),
                 col_w - Inches(0.3), Inches(0.45), size=14, bold=True, color=WHITE)
        add_text(sl, desc,
                 left + Inches(0.2), top + Inches(0.58),
                 col_w - Inches(0.3), Inches(0.38), size=11, color=GRAY)
        add_text(sl, target,
                 left + Inches(0.2), top + Inches(0.95),
                 col_w - Inches(0.3), Inches(0.38), size=11, bold=True, color=ACCENT2)


def slide_closing(prs):
    sl = blank_slide(prs)
    bg(sl)

    add_text(sl, "GEO is the next SEO.",
             Inches(1), Inches(1.5), Inches(11), Inches(1.2),
             size=40, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, "Brands that invest in LLM visibility today will dominate AI search tomorrow.",
             Inches(1.5), Inches(2.8), Inches(10), Inches(0.8),
             size=18, color=GRAY, align=PP_ALIGN.CENTER)

    card(sl, Inches(2.5), Inches(3.8), Inches(8), Inches(2.2))
    add_text(sl, "Next Steps",
             Inches(2.7), Inches(3.95), Inches(7.5), Inches(0.4),
             size=16, bold=True, color=ACCENT2, align=PP_ALIGN.CENTER)
    nexts = ["✅  Approve LLM Visibility Intelligence Suite for Q3 sprint",
             "✅  Allocate budget for Tavily + Gemini API integrations",
             "✅  Begin beta outreach to 50 target brands"]
    for i, n in enumerate(nexts):
        add_text(sl, n, Inches(2.8), Inches(4.45) + i * Inches(0.45),
                 Inches(7.5), Inches(0.4), size=12, color=GRAY, align=PP_ALIGN.CENTER)

    rect(sl, 0, Inches(6.8), W, Inches(0.7), CARD_BG)
    add_text(sl, "GEO Platform  |  Product Strategy 2025  |  Confidential",
             Inches(0.5), Inches(6.85), Inches(12), Inches(0.4),
             size=11, color=GRAY, align=PP_ALIGN.CENTER)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def build_ppt(output_path: str):
    prs = new_prs()
    slide_title(prs)
    slide_agenda(prs)
    slide_ai_revolution(prs)
    slide_feature(prs)
    slide_competitors(prs)
    slide_roadmap_3m(prs)
    slide_roadmap_12m(prs)
    slide_monetization(prs)
    slide_kpis(prs)
    slide_closing(prs)
    prs.save(output_path)
    print(f"[OK] Saved: {output_path}  ({prs.slides.__len__()} slides)")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "GEO_Strategy_Roadmap.pptx"
    build_ppt(out)

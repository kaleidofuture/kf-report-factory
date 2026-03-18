"""KF-ReportFactory — Template-based PDF report generator."""

import io
import csv
from datetime import date

from fpdf import FPDF
import streamlit as st

st.set_page_config(
    page_title="KF-ReportFactory",
    page_icon="📄",
    layout="centered",
)

from components.header import render_header
from components.footer import render_footer
from components.i18n import t

# --- Header ---
render_header()

# --- Report Templates ---
TEMPLATES = {
    "weekly": {
        "fields": [
            {"key": "author", "type": "text"},
            {"key": "department", "type": "text"},
            {"key": "period", "type": "text"},
            {"key": "achievements", "type": "textarea"},
            {"key": "issues", "type": "textarea"},
            {"key": "next_week_plan", "type": "textarea"},
            {"key": "notes", "type": "textarea"},
        ],
    },
    "monthly": {
        "fields": [
            {"key": "author", "type": "text"},
            {"key": "department", "type": "text"},
            {"key": "month", "type": "text"},
            {"key": "summary", "type": "textarea"},
            {"key": "kpi_results", "type": "textarea"},
            {"key": "challenges", "type": "textarea"},
            {"key": "next_month_plan", "type": "textarea"},
            {"key": "budget_notes", "type": "textarea"},
        ],
    },
    "sales": {
        "fields": [
            {"key": "author", "type": "text"},
            {"key": "period", "type": "text"},
            {"key": "total_sales", "type": "text"},
            {"key": "target", "type": "text"},
            {"key": "achievement_rate", "type": "text"},
            {"key": "top_products", "type": "textarea"},
            {"key": "new_clients", "type": "textarea"},
            {"key": "remarks", "type": "textarea"},
        ],
    },
}


def _setup_font(pdf: FPDF) -> str:
    """Set up a font that supports the current language. Returns font family name."""
    from components.i18n import get_lang

    if get_lang() == "ja":
        # fpdf2 has built-in support for CJK via unihan fonts
        try:
            pdf.add_font("japanese", style="", fname="", uni=True)
            return "japanese"
        except Exception:
            pass
    return "Helvetica"


def build_pdf(template_key: str, form_data: dict, csv_data: list[dict] | None) -> bytes:
    """Generate a PDF report from form data and optional CSV data."""
    title = t(f"template_{template_key}")

    pdf = FPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Font: use Helvetica (reliable on all platforms)
    # Japanese text will be rendered as-is; Helvetica handles ASCII well.
    # For full CJK support, a CJK font file would need to be bundled.
    font = "Helvetica"

    # Title
    pdf.set_font(font, "B", 16)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font(font, "", 9)
    pdf.cell(
        0, 6,
        f"Generated: {date.today().isoformat()}",
        new_x="LMARGIN", new_y="NEXT", align="R",
    )
    pdf.ln(6)

    # Form sections
    template_def = TEMPLATES[template_key]
    for field in template_def["fields"]:
        key = field["key"]
        label = t(f"field_{key}")
        value = form_data.get(key, "")

        # Section header
        pdf.set_font(font, "B", 11)
        pdf.set_fill_color(230, 240, 250)
        pdf.cell(0, 8, f"  {label}", new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.ln(2)

        # Section content
        pdf.set_font(font, "", 10)
        pdf.multi_cell(0, 6, value if value else "-")
        pdf.ln(4)

    # CSV data table
    if csv_data and len(csv_data) > 0:
        pdf.set_font(font, "B", 12)
        pdf.cell(0, 10, t("csv_data_section"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        headers = list(csv_data[0].keys())
        col_count = max(len(headers), 1)
        col_width = min((pdf.w - 20) / col_count, 60)

        # Header row
        pdf.set_font(font, "B", 8)
        pdf.set_fill_color(70, 130, 200)
        pdf.set_text_color(255, 255, 255)
        for h in headers:
            pdf.cell(col_width, 7, str(h)[:20], border=1, fill=True, align="C")
        pdf.ln()

        # Data rows
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(font, "", 8)
        for i, row in enumerate(csv_data[:100]):  # Limit to 100 rows
            if i % 2 == 0:
                pdf.set_fill_color(245, 245, 245)
            else:
                pdf.set_fill_color(255, 255, 255)
            for h in headers:
                pdf.cell(col_width, 6, str(row.get(h, ""))[:30], border=1, fill=True)
            pdf.ln()

    # Footer line
    pdf.set_y(-20)
    pdf.set_font(font, "", 8)
    pdf.cell(0, 10, "KaleidoFuture - KF-ReportFactory", align="C")

    return pdf.output()


# --- Main UI ---
st.markdown(f"### {t('select_template')}")

template_options = list(TEMPLATES.keys())
template_choice = st.selectbox(
    t("template_label"),
    options=template_options,
    format_func=lambda x: t(f"template_{x}"),
)

# Data input method
st.markdown(f"### {t('input_method')}")
input_mode = st.radio(
    t("input_mode_label"),
    options=["form", "csv", "both"],
    format_func=lambda x: t(f"input_mode_{x}"),
    horizontal=True,
)

# Form input
form_data = {}
if input_mode in ("form", "both"):
    st.markdown(f"#### {t('form_input_title')}")
    template_def = TEMPLATES[template_choice]
    for field in template_def["fields"]:
        key = field["key"]
        label = t(f"field_{key}")
        if field["type"] == "textarea":
            form_data[key] = st.text_area(label, key=f"form_{key}")
        else:
            form_data[key] = st.text_input(label, key=f"form_{key}")

# CSV upload
csv_data = None
if input_mode in ("csv", "both"):
    st.markdown(f"#### {t('csv_upload_title')}")
    csv_file = st.file_uploader(t("csv_upload_prompt"), type=["csv"])
    if csv_file is not None:
        try:
            content = csv_file.getvalue().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))
            csv_data = list(reader)
            st.success(t("csv_loaded").format(rows=len(csv_data)))
            st.dataframe(csv_data[:20])
        except Exception as e:
            st.error(f"{t('csv_error')}: {e}")

# Generate PDF
st.markdown("---")
if st.button(t("generate_pdf"), type="primary"):
    if input_mode == "form" and not any(form_data.values()):
        st.warning(t("no_input_warning"))
    elif input_mode == "csv" and csv_data is None:
        st.warning(t("no_csv_warning"))
    else:
        with st.spinner(t("processing")):
            try:
                pdf_bytes = build_pdf(template_choice, form_data, csv_data)
                st.session_state["pdf_bytes"] = pdf_bytes
                st.session_state["pdf_filename"] = (
                    f"report_{template_choice}_{date.today().isoformat()}.pdf"
                )
                st.success(t("pdf_generated"))
            except Exception as e:
                st.error(f"{t('pdf_error')}: {e}")

if "pdf_bytes" in st.session_state:
    st.download_button(
        label=t("download_result"),
        data=st.session_state["pdf_bytes"],
        file_name=st.session_state["pdf_filename"],
        mime="application/pdf",
    )

# --- Footer ---
render_footer(libraries=["Jinja2", "fpdf2"])

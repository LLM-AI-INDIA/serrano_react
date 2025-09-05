import streamlit as st
import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Dinesh\Projects\Python_projects\video\sarreno_app\sarreno_app\service_account.json"

import pandas as pd
from sqlalchemy import create_engine
import traceback
from google.cloud import bigquery
import pymysql
import shutil
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import RGBColor, Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn
from dotenv import load_dotenv
load_dotenv()

# ✅ BigQuery client
client = bigquery.Client()

# ✅ UI → Actual column names mapping
FIELD_MAP = {
    "Name": "Name of the youth",
    "Medical ID": "Medical ID Number",
    "Release Date": "Actual release date",
    "Appointments": "Scheduled Appointments",
    "Housing": "Housing",
    "Employment": "Employment",
    "Income": "Income and benefits",
    "Food & Clothing": "Food & Clothing",
    "Transportation": "Transportation",
    "ID Docs": "Identification documents",
    "Life Skills": "Life skills",
    "Family": "Family and children",
    "Court Dates": "Court dates",
    "Service Referrals": "Service referrals",
    "Home Modifications": "Home Modifications",
    "Durable Equipment": "Durable Medical Equipment",
    "Case Notes": "Case Notes"
}

def set_table_borders(table, color_rgb=(0, 0, 0)):
    """Apply borders to a table manually (works even without Word styles)."""
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")

    for border_name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        border = OxmlElement(f"w:{border_name}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "6")  # thickness
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "{:02X}{:02X}{:02X}".format(*color_rgb))
        borders.append(border)

    tblPr.append(borders)

# ---------- NEW: Font helpers to force Century Gothic everywhere ----------

def _set_run_font(run, name="Century Gothic", size_pt=None, color_rgb=None):
    """
    Force a run's font (including East Asia paths) to a specific font.
    """
    r = run._r
    rPr = r.get_or_add_rPr()
    rFonts = rPr.rFonts or OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rFonts.set(qn('w:eastAsia'), name)
    if rPr.rFonts is None:
        rPr.append(rFonts)

    # python-docx logical name (helps in Word UI)
    run.font.name = name

    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if color_rgb is not None:
        run.font.color.rgb = RGBColor(*color_rgb)


def force_document_font(doc, name="Century Gothic"):
    """
    Apply the desired font to:
      - Normal style (document default)
      - All existing paragraphs/runs
      - All existing tables (headers + cells)
    """
    # Default Normal style
    base = doc.styles['Normal']
    base.font.name = name
    # Ensure East Asia defaults also use the same font
    rPr = base._element.get_or_add_rPr()
    rFonts = rPr.rFonts or OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rFonts.set(qn('w:eastAsia'), name)
    if rPr.rFonts is None:
        rPr.append(rFonts)

    # Existing paragraphs
    for p in doc.paragraphs:
        for run in p.runs:
            _set_run_font(run, name=name)

    # Existing tables (headers + cells)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        _set_run_font(run, name=name)

# -------------------------------------------------------------------------


def generate_reentry_care_plan(selected_fields, person_input):
    """
    Fetches data from Excel, Cloud SQL, and BigQuery,
    merges it based on selected fields, and returns a BytesIO Word document.
    Also saves a copy to data/reentry_output.docx
    """
    try:
        # ✅ Fetch Excel data
        file_data = pd.read_excel("ExcelFiles/row_1.xlsx")
        excel_dict = file_data.to_dict(orient='records')[0]

        # ✅ Fetch SQL + BigQuery Data
        sql_record = read_cloud_sql(person_input)
        bq_record = read_bigquery(person_input)

        # ✅ Rename SQL columns for consistency
        sql_record = sql_record.rename(columns={
            'youth_name': 'Name of the youth',
            'medical_id_number': 'Medical ID Number',
            'actual_release_date': 'Actual release date',
            'scheduled_appointments': 'Scheduled Appointments',
            'housing': 'Housing',
            'employment': 'Employment',
            'income_and_benefits': 'Income and benefits',
            'food_and_clothing': 'Food & Clothing',
            'transportation': 'Transportation',
            'identification_documents': 'Identification documents',
            'life_skills': 'Life skills',
            'family_and_children': 'Family and children',
            'court_dates': 'Court dates',
            'service_referrals': 'Service referrals',
            'home_modifications': 'Home Modifications',
            'durable_medical_equipment': 'Durable Medical Equipment',
            'case_notes': 'Case Notes'
        })

        sql_dict = sql_record.to_dict(orient='records')[0] if not sql_record.empty else {}
        bq_dict = bq_record.to_dict(orient='records')[0] if not bq_record.empty else {}

        # ✅ Merge precedence: Excel < SQL < BigQuery
        merged_dict = {**excel_dict, **sql_dict, **bq_dict}
        merged_dict.pop('id', None)

        print("FINAL MERGED DATA - ", merged_dict)
        print("\n🔑 Keys in merged_dict:", list(merged_dict.keys()))
        print("📋 Selected fields:", selected_fields)

        # ✅ Save to template
        source_file = "data/Template.docx"
        destination_file = "data/reentry_output.docx"
        shutil.copy(source_file, destination_file)

        doc = Document(destination_file)

        # 🔤 Ensure the entire document uses Century Gothic up front
        force_document_font(doc, name="Century Gothic")

        # Title
        title_paragraph = doc.add_paragraph(f"{person_input}'s Reentry Care Plan")
        title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_paragraph.runs[0]
        title_run.bold = True
        _set_run_font(title_run, name="Century Gothic", size_pt=16, color_rgb=(0, 0, 0))

        doc.add_paragraph("")

        # ✅ Main Info Table
        table = doc.add_table(rows=1, cols=2)

        try:
            table.style = "Table Grid"
        except KeyError:
            pass  # no style in template, keep default

        # Apply custom borders if no style
        set_table_borders(table)

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Data Field Name'
        hdr_cells[1].text = 'Value'

        # ✅ Style header text (bold, size, and font)
        for cell in hdr_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    _set_run_font(run, name="Century Gothic", size_pt=12, color_rgb=(0, 0, 0))

        # ✅ Normalize keys (case-insensitive lookup)
        normalized_dict = {k.strip().lower(): v for k, v in merged_dict.items()}

        for key in selected_fields:
            # Remove suffix like " (CM)" if present
            clean_key = key.split(" (")[0].strip()
            actual_key = FIELD_MAP.get(clean_key, clean_key)  # map UI → DB field
            lookup_key = actual_key.strip().lower()

            value = normalized_dict.get(lookup_key, "Not Available")

            row_cells = table.add_row().cells
            row_cells[0].text = str(actual_key)
            row_cells[1].text = str(value)

            # Enforce Century Gothic on the new row
            for c in row_cells:
                for p in c.paragraphs:
                    for run in p.runs:
                        _set_run_font(run, name="Century Gothic")

        # ✅ Append Case Notes at the end if not already added
        if "Case Notes" not in [FIELD_MAP.get(k.split(" (")[0].strip(), k) for k in selected_fields]:
            case_notes = sql_dict.get("Case Notes", bq_dict.get("Case Notes", "No case notes available."))
            row_cells = table.add_row().cells
            row_cells[0].text = "Case Notes"
            row_cells[1].text = str(case_notes).strip()
            for c in row_cells:
                for p in c.paragraphs:
                    for run in p.runs:
                        _set_run_font(run, name="Century Gothic")

        # Final sweep in case the template had leftover styles
        force_document_font(doc, name="Century Gothic")

        # ✅ Save both to disk and to memory
        doc.save(destination_file)  # Save permanent copy on disk

        doc_io = BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)

        print(f"✅ Reentry Care Plan saved at {destination_file}")
        return doc_io

    except Exception as e:
        print("❌ Error in generate_reentry_care_plan:", str(e))
        st.error(f"Failed to generate care plan: {e}")
        return None


def read_cloud_sql(person_input):
    # ✅ Connection parameters
    user = os.environ["CLOUD_SQL_USER"]
    password = os.environ["CLOUD_SQL_PASSWORD"]
    host = os.environ["CLOUD_SQL_HOST"]
    database = 'serrano'

    connection_url = f"mysql+pymysql://{user}:{password}@{host}/{database}"
    engine = create_engine(connection_url)

    query = f"SELECT * FROM SocialEconomicLogistics_backup WHERE youth_name='{person_input}'"
    df = pd.read_sql(query, engine)
    return df


def read_bigquery(person_input):
    query = """
        SELECT * 
        FROM `genai-poc-424806.SerranoAdvisorsBQ.scalablefeaturesforBQ`
        WHERE youth_name = @name
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("name", "STRING", person_input)
        ]
    )

    df = client.query(query, job_config=job_config).to_dataframe()
    return df


# ✅ DB CONFIG
DB_CONFIG = {
    "host": "34.44.69.178",
    "user": "root",
    "password": "SQLsql$123",
    "database": "serrano"
}

# ✅ Test DB connection on import
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT id FROM SocialEconomicLogistics_backup LIMIT 3")
rows = cursor.fetchall()
print("✅ rows:", rows)
cursor.close()
conn.close()
# scripts/report_generator.py
import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

def generate_country_policy_report(country_name: str, summary_data: dict, output_path="reports") -> str:
    """
    Generates a PDF report for a given country's policy simulation summary.
    Args:
        country_name (str): Name of the country
        summary_data (dict): Key metrics from simulator (emissions, cost, etc)
        output_path (str): Directory to save report
    Returns:
        str: Full path to saved report
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_name = f"Policy_Report_{country_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(output_path, file_name)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Climate Policy Report: {country_name}", ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"This report summarizes the forecasted impact and cost of climate policy interventions for {country_name}.")

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Key Policy Metrics:", ln=True)

    pdf.set_font("Arial", '', 12)
    for key, value in summary_data.items():
        pdf.cell(0, 10, f"- {key}: {value}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 10, "Note: These projections are based on simplified simulation logic. Real-world outcomes may vary depending on implementation, externalities, and technology adoption.")

    pdf.output(file_path)
    return file_path

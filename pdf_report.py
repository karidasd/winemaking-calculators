"""PDF Report Generator for Winemaking Calculators"""
from fpdf import FPDF
from datetime import datetime
import io


class WinePDF(FPDF):
    def header(self):
        self.set_fill_color(80, 15, 30)
        self.rect(0, 0, 210, 22, 'F')
        self.set_text_color(220, 180, 120)
        self.set_font("Helvetica", "B", 14)
        self.set_y(6)
        self.cell(0, 10, "  Winemaking Calculators — Session Report", align="L")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(180, 130, 90)
        self.set_y(14)
        self.cell(0, 6, f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  github.com/karidasd/winemaking-calculators", align="L")
        self.ln(14)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 100, 80)
        self.cell(0, 10, f"Page {self.page_no()} | For educational purposes only — verify with a certified oenologist", align="C")

    def section_title(self, title: str):
        self.set_fill_color(60, 10, 25)
        self.set_text_color(200, 150, 100)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {title}", fill=True, ln=True)
        self.ln(2)

    def result_row(self, label: str, value: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 30, 20)
        self.set_fill_color(250, 245, 240)
        self.cell(90, 7, f"  {label}", fill=True)
        self.set_text_color(100, 40, 30)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 7, f"  {value}", fill=False, ln=True)
        self.ln(1)

    def note_box(self, text: str, color: tuple = (40, 80, 50)):
        self.set_fill_color(240, 250, 243)
        self.set_draw_color(*color)
        self.set_text_color(*color)
        self.set_font("Helvetica", "I", 9)
        self.multi_cell(0, 6, f"  Note: {text}", fill=True, border="L")
        self.ln(3)


def generate_pdf(calculations: list) -> bytes:
    """Generate a PDF report from a list of calculation results."""
    pdf = WinePDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Cover info
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(80, 15, 30)
    pdf.ln(5)
    pdf.cell(0, 12, "Winemaking Session Report", align="C", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(120, 80, 60)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%B %d, %Y')}", align="C", ln=True)
    pdf.ln(8)

    # Horizontal line
    pdf.set_draw_color(120, 40, 60)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(8)

    if not calculations:
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(150, 100, 80)
        pdf.cell(0, 10, "No calculations recorded in this session.", align="C", ln=True)
    else:
        for calc in calculations:
            pdf.section_title(calc.get("title", "Calculation"))
            for k, v in calc.get("results", {}).items():
                pdf.result_row(str(k), str(v))
            if calc.get("note"):
                pdf.note_box(calc["note"])
            pdf.ln(4)

    return bytes(pdf.output())

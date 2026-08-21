"""
Synthetic Lab Report Generator.
Generates realistic, clinical-grade, 100% synthetic laboratory PDF reports for early cancer detection panels.
All data is purely synthetic and contains zero real Protected Health Information (PHI).
"""

import os
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Adds page numbers and running synthetic disclaimer footer to ReportLab documents."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#718096"))
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 0.5 * inch, 0.35 * inch, page_text)
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#C53030"))
        disclaimer_text = "SYNTHETIC LABORATORY REPORT - FOR TESTING PURPOSES ONLY - ZERO REAL PATIENT DATA / NO PHI"
        self.drawString(0.5 * inch, 0.35 * inch, disclaimer_text)
        
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(0.5 * inch, 0.50 * inch, letter[0] - 0.5 * inch, 0.50 * inch)
        self.restoreState()


def get_synthetic_notice_table():
    """Returns a prominent synthetic test banner flowable."""
    notice_style = ParagraphStyle(
        'SynNotice', fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=colors.HexColor("#742A2A"), alignment=1
    )
    notice_text = (
        "100% SYNTHETIC TEST REPORT - NOT A REAL PATIENT RECORD - ZERO PROTECTED HEALTH INFORMATION (NO PHI)<br/>"
        "Generated strictly for automated testing and validation of clinical FHIR interoperability pipelines."
    )
    t = Table([[Paragraph(notice_text, notice_style)]], colWidths=[7.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF5F5")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FEB2B2")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    return t


def build_synthetic_mced_negative_pdf(output_path: str):
    """Generates a Multi-Cancer Early Detection (MCED) Negative Synthetic Report PDF."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.65 * inch
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'RepTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15,
        leading=18, textColor=colors.HexColor("#1A365D"), spaceAfter=2
    )
    sub_title_style = ParagraphStyle(
        'RepSubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5,
        textColor=colors.HexColor("#4A5568"), spaceAfter=6
    )
    sec_heading = ParagraphStyle(
        'SecHead', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10,
        leading=13, textColor=colors.HexColor("#2B6CB0"), spaceBefore=6, spaceAfter=3
    )
    body_style = ParagraphStyle(
        'RepBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5,
        leading=11.5, textColor=colors.HexColor("#2D3748")
    )
    body_bold = ParagraphStyle(
        'RepBodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5,
        leading=11.5, textColor=colors.HexColor("#2D3748")
    )
    banner_text = ParagraphStyle(
        'BannerTxt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12,
        leading=15, textColor=colors.HexColor("#22543D")
    )
    
    story = []
    story.append(get_synthetic_notice_table())
    story.append(Spacer(1, 6))
    
    # Header
    story.append(Paragraph("PACIFIC PRECISION GENOMICS LAB (SYNTHETIC FACILITY)", ParagraphStyle('LabName', fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor("#1A365D"))))
    story.append(Paragraph("1000 Synthetic Innovation Way, Suite 400, Fictional City, CA 94000 | CLIA ID: 00D9981245 | Lab Director: Dr. Eleanor Hayes, MD, PhD, FCAP (Synthetic)", sub_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A365D"), spaceAfter=6))
    
    story.append(Paragraph("Multi-Cancer Early Detection Screening Report", title_style))
    story.append(Paragraph("Next-Generation Sequencing cfDNA Methylation Profiling (Synthetic Demonstration)", sub_title_style))
    
    # Demographics Table
    demo_data = [
        [
            Paragraph("<b>Patient Information</b>", sec_heading),
            Paragraph("<b>Provider Information</b>", sec_heading),
            Paragraph("<b>Specimen Information</b>", sec_heading)
        ],
        [
            Paragraph("Name: Robert T. Sample<br/>DOB: 11/23/1968<br/>Sex: Male<br/>Patient ID: SYN-MRN-8849102", body_style),
            Paragraph("Provider: Dr. Marcus Vance<br/>Facility: Bay Area Health System<br/>NPI: 9982736450<br/>Location: Fictional City, CA", body_style),
            Paragraph("Specimen ID: SYN-SPEC-MCED-4491<br/>Collection Date: Aug 1, 2026<br/>Received Date: Aug 2, 2026<br/>Report Date: Aug 6, 2026<br/>Specimen Type: Blood / Plasma", body_style)
        ]
    ]
    t_demo = Table(demo_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_demo)
    story.append(Spacer(1, 8))
    
    # Result Banner
    banner_data = [[
        Paragraph("Result: Cancer Signal Not Detected", banner_text),
        Paragraph("<b>Status:</b> Final<br/><b>Assay:</b> cfDNA Methylation NGS", body_style)
    ]]
    t_banner = Table(banner_data, colWidths=[5.2*inch, 2.3*inch])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#C6F6D5")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#38A169")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 6))
    
    # Summary Narrative
    story.append(Paragraph("<b>Test Result Summary:</b> No cancer signal was detected in this synthetic cell-free DNA (cfDNA) blood sample. Methylation patterns analyzed across target genomic regions are consistent with non-malignant profiles. This result does not completely rule out the presence of all types of malignancy.", body_style))
    story.append(Spacer(1, 8))
    
    # Clinical Observations Table
    story.append(Paragraph("Laboratory Observations & Biomarkers", sec_heading))
    obs_data = [
        [Paragraph("<b>Test / Analyte</b>", body_bold), Paragraph("<b>LOINC</b>", body_bold), Paragraph("<b>Result</b>", body_bold), Paragraph("<b>Reference Range</b>", body_bold), Paragraph("<b>Interpretation</b>", body_bold)],
        [Paragraph("Cancer Signal Status", body_style), Paragraph("94076-7", body_style), Paragraph("Cancer Signal Not Detected", body_style), Paragraph("Cancer Signal Not Detected", body_style), Paragraph("Normal", body_style)],
        [Paragraph("Predicted Cancer Signal Origin 1", body_style), Paragraph("94077-5", body_style), Paragraph("None Detected", body_style), Paragraph("None", body_style), Paragraph("Normal", body_style)],
        [Paragraph("cfDNA Concentration", body_style), Paragraph("Local", body_style), Paragraph("8.4 ng/mL", body_style), Paragraph("5.0 - 25.0 ng/mL", body_style), Paragraph("Normal", body_style)],
        [Paragraph("Sequencing QC Pass Rate", body_style), Paragraph("Local", body_style), Paragraph("99.4%", body_style), Paragraph(">= 95.0%", body_style), Paragraph("Normal", body_style)]
    ]
    t_obs = Table(obs_data, colWidths=[2.2*inch, 0.9*inch, 1.9*inch, 1.5*inch, 1.0*inch])
    t_obs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_obs)
    story.append(Spacer(1, 10))
    
    # Clinical Interpretation
    story.append(Paragraph("Clinical Interpretation", sec_heading))
    story.append(Paragraph("A 'Cancer Signal Not Detected' result indicates that the targeted cell-free DNA methylation signatures associated with 50+ cancer types were not identified at actionable thresholds in this specimen. Routine preventative health examinations and age-appropriate standard screening guidelines (such as colonoscopy, mammography, and cervical cytology) should continue as medically indicated.", body_style))
    story.append(Spacer(1, 8))
    
    # Methodology & Limitations
    story.append(Paragraph("Methodology & Limitations", sec_heading))
    story.append(Paragraph("<b>Methodology:</b> Plasma cfDNA is extracted and treated with targeted bisulfite conversion followed by deep Next-Generation Sequencing (NGS) on Illumina NovaSeq systems. Epigenetic methylation patterns are evaluated using proprietary machine-learning classification models calibrated across multi-organ tissue datasets.", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Limitations:</b> A negative result does not completely eliminate the risk of cancer. Certain indolent tumors or cancers shedding low levels of cfDNA may not be detected. This test is validated for adult screening and is not intended for recurrence monitoring.", body_style))
    
    doc.build(story, canvasmaker=NumberedCanvas)


def build_synthetic_colorectal_ctdna_pdf(output_path: str):
    """Generates a Liquid Biopsy Colorectal ctDNA Screening Synthetic Report PDF."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.65 * inch
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CTTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=colors.HexColor("#742A2A"))
    sub_title_style = ParagraphStyle('CTSub', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor("#4A5568"), spaceAfter=6)
    sec_heading = ParagraphStyle('CTSec', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#9B2C2C"), spaceBefore=6, spaceAfter=3)
    body_style = ParagraphStyle('CTBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=colors.HexColor("#2D3748"))
    body_bold = ParagraphStyle('CTBodyB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=colors.HexColor("#2D3748"))
    banner_pos = ParagraphStyle('BannerPos', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#9B2C2C"))

    story = []
    story.append(get_synthetic_notice_table())
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("BEACON ONCOLOGY REFERENCE LABORATORY (SYNTHETIC FACILITY)", ParagraphStyle('LabB', fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor("#742A2A"))))
    story.append(Paragraph("450 Synthetic Technology Parkway, Cambridge, MA 02100 | CLIA ID: 00D8874123 | Director: Dr. Arthur Sterling, MD, FCAP (Synthetic)", sub_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#742A2A"), spaceAfter=6))
    
    story.append(Paragraph("Liquid Biopsy Colorectal ctDNA Early Screening Report", title_style))
    story.append(Paragraph("Circulating Tumor DNA Methylation & Somatic Mutation Targeted Panel (Synthetic Demonstration)", sub_title_style))
    
    # Demographics
    demo_data = [
        [
            Paragraph("<b>Patient Demographics</b>", sec_heading),
            Paragraph("<b>Ordering Clinician</b>", sec_heading),
            Paragraph("<b>Specimen Details</b>", sec_heading)
        ],
        [
            Paragraph("Name: Harold K. Sample<br/>DOB: 04/18/1964<br/>Sex: Male<br/>Patient ID: SYN-MRN-5529184", body_style),
            Paragraph("Provider: Dr. Sophia Alvarez<br/>Facility: New England Cancer Center<br/>NPI: 9457896321<br/>Location: Boston, MA", body_style),
            Paragraph("Specimen ID: SYN-SPEC-CRC-7731<br/>Collection Date: Jul 28, 2026<br/>Received Date: Jul 29, 2026<br/>Report Date: Aug 4, 2026<br/>Specimen Type: Blood / Plasma", body_style)
        ]
    ]
    t_demo = Table(demo_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF5F5")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FEB2B2")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_demo)
    story.append(Spacer(1, 8))
    
    # Result Banner
    banner_data = [[
        Paragraph("Result: Positive (Elevated Risk for Colorectal Malignancy)", banner_pos),
        Paragraph("<b>Status:</b> Final<br/><b>Panel:</b> Colorectal ctDNA Multi-Marker", body_style)
    ]]
    t_banner = Table(banner_data, colWidths=[5.2*inch, 2.3*inch])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FED7D7")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#E53E3E")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Test Result Summary:</b> Elevated circulating tumor DNA (ctDNA) markers detected in synthetic sample. Aberrant SEPT9 promoter hypermethylation and somatic mutations in KRAS and TP53 were identified in plasma cfDNA.", body_style))
    story.append(Spacer(1, 8))
    
    # Observations Table
    story.append(Paragraph("Quantitative and Qualitative Biomarker Findings", sec_heading))
    obs_data = [
        [Paragraph("<b>Target Marker</b>", body_bold), Paragraph("<b>LOINC</b>", body_bold), Paragraph("<b>Result</b>", body_bold), Paragraph("<b>Reference Range</b>", body_bold), Paragraph("<b>Interpretation</b>", body_bold)],
        [Paragraph("SEPT9 Methylation", body_style), Paragraph("77983-5", body_style), Paragraph("Positive", body_style), Paragraph("Negative", body_style), Paragraph("Abnormal (Positive)", body_style)],
        [Paragraph("KRAS Mutation Analysis", body_style), Paragraph("48018-6", body_style), Paragraph("p.G12D (VAF: 1.8%)", body_style), Paragraph("Not Detected (< 0.05%\nVAF)", body_style), Paragraph("Abnormal", body_style)],
        [Paragraph("BRAF Mutation Analysis", body_style), Paragraph("48018-6", body_style), Paragraph("Not Detected", body_style), Paragraph("Not Detected (< 0.05%\nVAF)", body_style), Paragraph("Normal", body_style)],
        [Paragraph("TP53 Mutation Analysis", body_style), Paragraph("48018-6", body_style), Paragraph("p.R273H (VAF: 2.3%)", body_style), Paragraph("Not Detected (< 0.05%\nVAF)", body_style), Paragraph("Abnormal", body_style)],
        [Paragraph("Total ctDNA Fraction", body_style), Paragraph("Local", body_style), Paragraph("2.1%", body_style), Paragraph("< 0.1%", body_style), Paragraph("Abnormal", body_style)]
    ]
    t_obs = Table(obs_data, colWidths=[2.2*inch, 0.9*inch, 1.9*inch, 1.5*inch, 1.0*inch])
    t_obs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_obs)
    story.append(Spacer(1, 8))
    
    # Clinical Interpretation
    story.append(Paragraph("Clinical Interpretation", sec_heading))
    story.append(Paragraph("The presence of circulating tumor DNA with SEPT9 promoter methylation and concurrent KRAS p.G12D and TP53 p.R273H variants strongly indicates the presence of shed colorectal neoplastic DNA. Diagnostic colonoscopy with high-definition mucosal inspection and radiological abdominal evaluation is urgently recommended. Clinical correlation with patient symptoms and family history is required.", body_style))
    story.append(Spacer(1, 8))
    
    # Methodology & Limitations
    story.append(Paragraph("Methodology & Limitations", sec_heading))
    story.append(Paragraph("<b>Methodology:</b> Plasma ctDNA undergoes dual-chemistry extraction. Methylation of Septin 9 is quantified using real-time PCR with fluorescent hybridization probes. Somatic variant profiling across hotspot exons of KRAS, BRAF, and TP53 is performed using ultra-deep amplicon NGS (minimum 20,000x coverage depth) on Illumina NextSeq.", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Limitations:</b> False-positive methylation or mutations may rarely occur due to clonal hematopoiesis of indeterminate potential (CHIP). Liquid biopsy results should be verified by endoscopic visualization and tissue histology.", body_style))
    
    doc.build(story, canvasmaker=NumberedCanvas)


def build_synthetic_hereditary_ngs_pdf(output_path: str):
    """Generates a Hereditary Cancer Multi-Gene NGS Panel Synthetic Report PDF."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.65 * inch
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('NGSTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=colors.HexColor("#2C5282"))
    sub_title_style = ParagraphStyle('NGSSub', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor("#4A5568"), spaceAfter=6)
    sec_heading = ParagraphStyle('NGSSec', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#2B6CB0"), spaceBefore=6, spaceAfter=3)
    body_style = ParagraphStyle('NGSBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=colors.HexColor("#2D3748"))
    body_bold = ParagraphStyle('NGSBodyB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=colors.HexColor("#2D3748"))
    banner_alert = ParagraphStyle('BannerAlert', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#9B2C2C"))

    story = []
    story.append(get_synthetic_notice_table())
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("GENOMEPATH CLINICAL DIAGNOSTICS (SYNTHETIC FACILITY)", ParagraphStyle('LabG', fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor("#2C5282"))))
    story.append(Paragraph("3600 Synthetic Boulevard, Suite 500, Philadelphia, PA 19100 | CLIA ID: 00D7654321 | Director: Dr. Sarah Jenkins, MD, FCAP (Synthetic)", sub_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2C5282"), spaceAfter=6))
    
    story.append(Paragraph("Hereditary Cancer Risk 15-Gene NGS Panel", title_style))
    story.append(Paragraph("Germline Sequence and Deletion/Duplication Analysis (Synthetic Demonstration)", sub_title_style))
    
    # Demographics
    demo_data = [
        [
            Paragraph("<b>Patient Demographics</b>", sec_heading),
            Paragraph("<b>Ordering Geneticist</b>", sec_heading),
            Paragraph("<b>Specimen Details</b>", sec_heading)
        ],
        [
            Paragraph("Name: Brenda S. Sample<br/>DOB: 09/30/1985<br/>Sex: Female<br/>Patient ID: SYN-MRN-9912048", body_style),
            Paragraph("Provider: Dr. Ethan Ross<br/>Facility: Pennsylvania Genetics Institute<br/>NPI: 9847392015<br/>Location: Philadelphia, PA", body_style),
            Paragraph("Specimen ID: SYN-SPEC-NGS-2098<br/>Collection Date: Jul 15, 2026<br/>Received Date: Jul 16, 2026<br/>Report Date: Jul 24, 2026<br/>Specimen Type: Whole Blood", body_style)
        ]
    ]
    t_demo = Table(demo_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BEE3F8")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_demo)
    story.append(Spacer(1, 8))
    
    # Banner
    banner_data = [[
        Paragraph("Result: Pathogenic Variant Identified", banner_alert),
        Paragraph("<b>Status:</b> Final<br/><b>Gene:</b> BRCA1 (Heterozygous)", body_style)
    ]]
    t_banner = Table(banner_data, colWidths=[5.2*inch, 2.3*inch])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FED7D7")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#E53E3E")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Test Result Summary:</b> A heterozygous pathogenic frameshift variant was identified in the BRCA1 gene in this synthetic sample. No other pathogenic alterations or copy number variants were detected in the remaining 14 genes tested.", body_style))
    story.append(Spacer(1, 8))
    
    # Observations Table
    story.append(Paragraph("Detailed Genetic Variant Findings", sec_heading))
    obs_data = [
        [Paragraph("<b>Gene Tested</b>", body_bold), Paragraph("<b>LOINC</b>", body_bold), Paragraph("<b>Classification & HGVS Variant</b>", body_bold), Paragraph("<b>Zygosity</b>", body_bold), Paragraph("<b>Interpretation</b>", body_bold)],
        [Paragraph("BRCA1 Genetic Analysis", body_style), Paragraph("69548-6", body_style), Paragraph("Pathogenic - c.5266dupC\n(p.Gln1756Profs*74)", body_style), Paragraph("Heterozygous", body_style), Paragraph("Abnormal (Pathogenic)", body_style)],
        [Paragraph("BRCA2 Genetic Analysis", body_style), Paragraph("69548-6", body_style), Paragraph("Negative / No Pathogenic Variant", body_style), Paragraph("N/A", body_style), Paragraph("Normal", body_style)],
        [Paragraph("PALB2 Genetic Analysis", body_style), Paragraph("69548-6", body_style), Paragraph("Negative / No Pathogenic Variant", body_style), Paragraph("N/A", body_style), Paragraph("Normal", body_style)],
        [Paragraph("TP53 Genetic Analysis", body_style), Paragraph("69548-6", body_style), Paragraph("Negative / No Pathogenic Variant", body_style), Paragraph("N/A", body_style), Paragraph("Normal", body_style)],
        [Paragraph("CHEK2 Genetic Analysis", body_style), Paragraph("69548-6", body_style), Paragraph("Negative / No Pathogenic Variant", body_style), Paragraph("N/A", body_style), Paragraph("Normal", body_style)],
        [Paragraph("CDH1 Genetic Analysis", body_style), Paragraph("69548-6", body_style), Paragraph("Negative / No Pathogenic Variant", body_style), Paragraph("N/A", body_style), Paragraph("Normal", body_style)]
    ]
    t_obs = Table(obs_data, colWidths=[1.8*inch, 0.9*inch, 2.6*inch, 1.1*inch, 1.1*inch])
    t_obs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_obs)
    story.append(Spacer(1, 8))
    
    # Clinical Interpretation
    story.append(Paragraph("Clinical Interpretation", sec_heading))
    story.append(Paragraph("The BRCA1 c.5266dupC (p.Gln1756Profs*74) variant is a well-characterized founder mutation in the BRCA1 tumor suppressor gene that results in premature protein truncation. This finding confirms a diagnosis of Hereditary Breast and Ovarian Cancer (HBOC) syndrome. High-risk surveillance protocols (e.g. annual breast MRI, risk-reducing salpingo-oophorectomy discussions) and cascade testing for at-risk first-degree relatives are strongly indicated.", body_style))
    story.append(Spacer(1, 8))
    
    # Methodology & Limitations
    story.append(Paragraph("Methodology & Limitations", sec_heading))
    story.append(Paragraph("<b>Methodology:</b> Genomic DNA is extracted from whole blood. Target enrichment of all coding exons and +/- 20bp flanking intronic boundaries of 15 hereditary cancer predisposition genes is performed using custom hybridization probes, followed by paired-end NextGen sequencing (Illumina NovaSeq). Copy number variations (CNVs) are called using normalized read-depth algorithms.", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Limitations:</b> This assay does not detect deep intronic mutations outside the targeted regions, complex chromosomal rearrangements, or low-level somatic mosaicism.", body_style))
    
    doc.build(story, canvasmaker=NumberedCanvas)


def build_synthetic_prostate_phi_pdf(output_path: str):
    """Generates a Prostate Health Index (phi) Early Cancer Detection Panel Synthetic Report PDF."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.65 * inch
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('PHITitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=colors.HexColor("#234E52"))
    sub_title_style = ParagraphStyle('PHISub', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor("#4A5568"), spaceAfter=6)
    sec_heading = ParagraphStyle('PHISec', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#285E61"), spaceBefore=6, spaceAfter=3)
    body_style = ParagraphStyle('PHIBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=colors.HexColor("#2D3748"))
    body_bold = ParagraphStyle('PHIBodyB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=colors.HexColor("#2D3748"))
    banner_alert = ParagraphStyle('BannerWarn', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#9C4221"))

    story = []
    story.append(get_synthetic_notice_table())
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("APEX UROLOGIC REFERENCE LABORATORY (SYNTHETIC FACILITY)", ParagraphStyle('LabA', fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor("#234E52"))))
    story.append(Paragraph("7700 Synthetic Parkway, Suite 300, Minneapolis, MN 55400 | CLIA ID: 00D1122334 | Director: Dr. Keith Carlson, MD, FCAP (Synthetic)", sub_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#234E52"), spaceAfter=6))
    
    story.append(Paragraph("Prostate Health Index and Early Cancer Biomarker Panel", title_style))
    story.append(Paragraph("Multi-Analyte Immunoassay Panel for Prostate Cancer Risk Stratification (Synthetic Demonstration)", sub_title_style))
    
    # Demographics
    demo_data = [
        [
            Paragraph("<b>Patient Demographics</b>", sec_heading),
            Paragraph("<b>Ordering Urologist</b>", sec_heading),
            Paragraph("<b>Specimen Details</b>", sec_heading)
        ],
        [
            Paragraph("Name: Arthur B. Sample<br/>DOB: 02/14/1959<br/>Sex: Male<br/>Patient ID: SYN-MRN-3341890", body_style),
            Paragraph("Provider: Dr. David Reynolds<br/>Facility: Northstar Urologic Clinic<br/>NPI: 9092837465<br/>Location: Minneapolis, MN", body_style),
            Paragraph("Specimen ID: SYN-SPEC-PHI-8821<br/>Collection Date: Aug 10, 2026<br/>Received Date: Aug 11, 2026<br/>Report Date: Aug 12, 2026<br/>Specimen Type: Serum", body_style)
        ]
    ]
    t_demo = Table(demo_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E6FFFA")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#B2F5EA")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_demo)
    story.append(Spacer(1, 8))
    
    # Banner
    banner_data = [[
        Paragraph("Result: Elevated Risk (High Risk for Prostate Cancer)", banner_alert),
        Paragraph("<b>Status:</b> Final<br/><b>Index (phi):</b> 47.8", body_style)
    ]]
    t_banner = Table(banner_data, colWidths=[5.2*inch, 2.3*inch])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEEBC8")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#DD6B20")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Test Result Summary:</b> Patient has an elevated Prostate Health Index (phi = 47.8) in this synthetic test result, indicating an elevated probability of clinically significant prostate cancer (Gleason Score >= 7) on biopsy.", body_style))
    story.append(Spacer(1, 8))
    
    # Observations Table
    story.append(Paragraph("Quantitative Immunoassay Biomarkers", sec_heading))
    obs_data = [
        [Paragraph("<b>Biomarker / Assay</b>", body_bold), Paragraph("<b>LOINC</b>", body_bold), Paragraph("<b>Result</b>", body_bold), Paragraph("<b>Units</b>", body_bold), Paragraph("<b>Reference Range</b>", body_bold), Paragraph("<b>Flag</b>", body_bold)],
        [Paragraph("Total PSA", body_style), Paragraph("2857-1", body_style), Paragraph("5.6", body_style), Paragraph("ng/mL", body_style), Paragraph("0.0 - 4.0", body_style), Paragraph("High (H)", body_style)],
        [Paragraph("Free PSA", body_style), Paragraph("10886-0", body_style), Paragraph("0.58", body_style), Paragraph("ng/mL", body_style), Paragraph("N/A", body_style), Paragraph("Normal", body_style)],
        [Paragraph("% Free PSA", body_style), Paragraph("19195-7", body_style), Paragraph("10.4", body_style), Paragraph("%", body_style), Paragraph("> 25.0 %", body_style), Paragraph("Low (L)", body_style)],
        [Paragraph("[-2]proPSA", body_style), Paragraph("72304-9", body_style), Paragraph("19.2", body_style), Paragraph("pg/mL", body_style), Paragraph("N/A", body_style), Paragraph("Normal", body_style)],
        [Paragraph("Prostate Health Index (phi)", body_style), Paragraph("72305-6", body_style), Paragraph("47.8", body_style), Paragraph("{score}", body_style), Paragraph("< 27.0 (Low Risk)", body_style), Paragraph("High (H)", body_style)]
    ]
    t_obs = Table(obs_data, colWidths=[1.9*inch, 0.8*inch, 0.9*inch, 0.8*inch, 1.8*inch, 1.3*inch])
    t_obs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_obs)
    story.append(Spacer(1, 8))
    
    # Clinical Interpretation
    story.append(Paragraph("Clinical Interpretation", sec_heading))
    story.append(Paragraph("The Prostate Health Index is calculated via the formula: phi = ([-2]proPSA / Free PSA) * sqrt(Total PSA). A phi value >= 36.0 is associated with a 36.0% to 55.0% probability of cancer on biopsy. In men aged 50 and older with total PSA in the 4.0 to 10.0 ng/mL diagnostic gray zone, this elevated score provides strong clinical justification for mpMRI and targeted prostate biopsy.", body_style))
    story.append(Spacer(1, 8))
    
    # Methodology & Limitations
    story.append(Paragraph("Methodology & Limitations", sec_heading))
    story.append(Paragraph("<b>Methodology:</b> Total PSA, Free PSA, and [-2]proPSA are quantitatively measured in serum using Beckman Coulter Access chemiluminescent immunoassays calibrated against WHO standards. The phi score is derived mathematically.", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Limitations:</b> phi results should be evaluated in conjunction with digital rectal examination (DRE), prostate volume, family history, and clinical risk factors.", body_style))
    
    doc.build(story, canvasmaker=NumberedCanvas)


def generate_all_synthetic_reports(output_dir: str):
    """Generates all synthetic PDF test reports in the target directory."""
    os.makedirs(output_dir, exist_ok=True)
    
    reports = [
        ("synthetic_mced_negative.pdf", build_synthetic_mced_negative_pdf),
        ("synthetic_colorectal_ctdna.pdf", build_synthetic_colorectal_ctdna_pdf),
        ("synthetic_hereditary_ngs_panel.pdf", build_synthetic_hereditary_ngs_pdf),
        ("synthetic_prostate_phi_panel.pdf", build_synthetic_prostate_phi_pdf),
    ]
    
    created_paths = []
    for filename, builder_fn in reports:
        target_path = os.path.join(output_dir, filename)
        builder_fn(target_path)
        created_paths.append(target_path)
        
    return created_paths


if __name__ == "__main__":
    import sys
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "reports"
    created = generate_all_synthetic_reports(out_dir)
    print(f"Successfully generated {len(created)} synthetic PDF reports in '{out_dir}'.")

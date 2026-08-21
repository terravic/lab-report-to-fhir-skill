"""
FHIR Lab Report Visualizer.
Generates an interactive, responsive Canvas UI Dashboard from HL7 FHIR R4 Bundles.
Supports dual clinical dashboard and raw FHIR JSON inspection with synchronized element highlighting.
"""

import os
import json
import webbrowser
from typing import Dict, Any, Optional


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HL7 FHIR Clinical Diagnostic Dashboard & Inspector</title>
  <style>
    :root {
      --bg-main: #f8fafc;
      --bg-card: #ffffff;
      --bg-subtle: #f1f5f9;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-light: #94a3b8;
      --border-color: #e2e8f0;
      --border-focus: #3b82f6;
      
      --primary: #0284c7;
      --primary-dark: #0369a1;
      --primary-light: #e0f2fe;
      
      --success: #16a34a;
      --success-bg: #dcfce7;
      --success-border: #86efac;
      
      --danger: #dc2626;
      --danger-bg: #fee2e2;
      --danger-border: #fca5a5;
      
      --warning: #d97706;
      --warning-bg: #fef3c7;
      --warning-border: #fcd34d;
      
      --info: #2563eb;
      --info-bg: #dbeafe;
      --info-border: #93c5fd;

      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      --font-mono: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
      --radius: 8px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg-main);
      color: var(--text-main);
      line-height: 1.5;
      font-size: 14px;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }

    /* Top Notice Banner */
    .synthetic-banner {
      background-color: #fff1f2;
      color: #9f1239;
      border-bottom: 1px solid #fecdd3;
      padding: 6px 16px;
      font-size: 12px;
      font-weight: 600;
      text-align: center;
      letter-spacing: 0.02em;
    }

    /* App Header */
    header {
      background-color: var(--bg-card);
      border-bottom: 1px solid var(--border-color);
      padding: 10px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-shrink: 0;
    }

    .brand-section {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brand-title {
      font-size: 16px;
      font-weight: 700;
      color: var(--text-main);
    }

    .brand-badge {
      background-color: var(--primary-light);
      color: var(--primary-dark);
      font-size: 11px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;
      border: 1px solid #bae6fd;
    }

    .controls-section {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .select-label {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
    }

    select, button {
      font-family: var(--font-sans);
      font-size: 13px;
      padding: 6px 12px;
      border-radius: var(--radius);
      border: 1px solid var(--border-color);
      background-color: var(--bg-card);
      color: var(--text-main);
      cursor: pointer;
      transition: all 0.15s ease;
    }

    select:focus, button:focus {
      outline: none;
      border-color: var(--border-focus);
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }

    button:hover {
      background-color: var(--bg-subtle);
    }

    .btn-primary {
      background-color: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }
    .btn-primary:hover {
      background-color: var(--primary-dark);
    }

    .view-toggle {
      display: flex;
      background-color: var(--bg-subtle);
      padding: 2px;
      border-radius: var(--radius);
      border: 1px solid var(--border-color);
    }

    .view-toggle button {
      border: none;
      background: transparent;
      padding: 4px 10px;
      font-size: 12px;
      border-radius: 6px;
    }

    .view-toggle button.active {
      background-color: var(--bg-card);
      font-weight: 600;
      box-shadow: var(--shadow-sm);
    }

    /* Main Container */
    main {
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 1fr;
      overflow: hidden;
      background-color: var(--bg-main);
    }

    main.view-clinical-only {
      grid-template-columns: 1fr 0px;
    }
    main.view-clinical-only #fhir-inspector {
      display: none;
    }

    main.view-json-only {
      grid-template-columns: 0px 1fr;
    }
    main.view-json-only #clinical-dashboard {
      display: none;
    }

    /* Clinical Dashboard Column */
    #clinical-dashboard {
      overflow-y: auto;
      padding: 20px;
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    /* FHIR Inspector Column */
    #fhir-inspector {
      overflow-y: auto;
      background-color: #0f172a;
      color: #f8fafc;
      display: flex;
      flex-direction: column;
      height: 100%;
    }

    /* Cards */
    .card {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      padding: 16px;
      box-shadow: var(--shadow-sm);
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
      cursor: pointer;
    }

    .card:hover {
      border-color: #94a3b8;
      box-shadow: var(--shadow-md);
    }

    .card.active-resource {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.25);
    }

    /* Diagnostic Result Banner Card */
    .result-banner {
      padding: 16px 20px;
      border-radius: var(--radius);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      border: 1px solid transparent;
      cursor: pointer;
    }

    .result-banner.status-abnormal, .result-banner.status-pathogenic {
      background-color: var(--danger-bg);
      border-color: var(--danger-border);
      color: #7f1d1d;
    }

    .result-banner.status-normal {
      background-color: var(--success-bg);
      border-color: var(--success-border);
      color: #14532d;
    }

    .result-banner.status-elevated {
      background-color: var(--warning-bg);
      border-color: var(--warning-border);
      color: #78350f;
    }

    .result-title {
      font-size: 18px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .result-subtitle {
      font-size: 13px;
      margin-top: 2px;
      opacity: 0.9;
    }

    .tag-badge {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 4px 10px;
      border-radius: 9999px;
      border: 1px solid currentColor;
      white-space: nowrap;
    }

    /* Demographics Grid */
    .demographics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
    }

    .info-card {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      padding: 12px 14px;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .info-card:hover {
      border-color: var(--primary);
    }

    .info-card.active-resource {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.2);
    }

    .info-card-header {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .info-card-value {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-main);
      margin-bottom: 2px;
    }

    .info-card-sub {
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.4;
    }

    .fhir-pill {
      font-family: var(--font-mono);
      font-size: 10px;
      padding: 1px 6px;
      border-radius: 4px;
      background-color: var(--bg-subtle);
      color: var(--text-muted);
      border: 1px solid var(--border-color);
    }

    /* Section Title */
    .section-title {
      font-size: 14px;
      font-weight: 700;
      color: var(--text-main);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 4px;
    }

    /* Biomarkers Table & Gauges */
    .biomarkers-container {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .biomarker-row {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .biomarker-row:hover {
      border-color: var(--primary);
      box-shadow: var(--shadow-sm);
    }

    .biomarker-row.active-resource {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.25);
    }

    .biomarker-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .biomarker-name {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-main);
    }

    .biomarker-code-badge {
      font-family: var(--font-mono);
      font-size: 11px;
      background-color: #f1f5f9;
      color: #475569;
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid #cbd5e1;
    }

    .biomarker-result-val {
      font-size: 15px;
      font-weight: 700;
      display: flex;
      align-items: baseline;
      gap: 4px;
    }

    .biomarker-unit {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-muted);
    }

    .flag-badge {
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
    }
    .flag-normal { background-color: var(--success-bg); color: var(--success); }
    .flag-high, .flag-abnormal { background-color: var(--danger-bg); color: var(--danger); }
    .flag-low { background-color: var(--warning-bg); color: var(--warning); }

    /* Visual Range Gauge */
    .range-gauge {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-top: 4px;
    }

    .gauge-bar-track {
      height: 8px;
      background: linear-gradient(to right, #86efac 0%, #86efac 65%, #fca5a5 65%, #fca5a5 100%);
      border-radius: 4px;
      position: relative;
    }

    .gauge-pointer {
      position: absolute;
      top: -4px;
      width: 6px;
      height: 16px;
      background-color: #0f172a;
      border: 1px solid #ffffff;
      border-radius: 3px;
      transform: translateX(-50%);
      box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    .gauge-labels {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }

    /* Narrative Box */
    .narrative-box {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      padding: 14px 16px;
      font-size: 13px;
      line-height: 1.6;
      color: #334155;
    }

    /* FHIR Inspector Header */
    .inspector-header {
      background-color: #1e293b;
      padding: 10px 16px;
      border-bottom: 1px solid #334155;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-shrink: 0;
    }

    .inspector-title {
      font-size: 13px;
      font-weight: 700;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .resource-tabs {
      display: flex;
      gap: 4px;
      overflow-x: auto;
      padding: 8px 16px;
      background-color: #1e293b;
      border-bottom: 1px solid #334155;
      flex-shrink: 0;
    }

    .tab-btn {
      font-family: var(--font-mono);
      font-size: 11px;
      background-color: #0f172a;
      color: #94a3b8;
      border: 1px solid #334155;
      padding: 4px 10px;
      border-radius: 4px;
      white-space: nowrap;
    }

    .tab-btn.active {
      background-color: #0284c7;
      color: #ffffff;
      border-color: #38bdf8;
      font-weight: 600;
    }

    /* JSON Display */
    .json-code-container {
      flex: 1;
      padding: 16px;
      overflow: auto;
      font-family: var(--font-mono);
      font-size: 12px;
      line-height: 1.6;
    }

    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-all;
    }

    .json-key { color: #38bdf8; font-weight: 600; }
    .json-string { color: #4ade80; }
    .json-number { color: #f59e0b; }
    .json-boolean { color: #ec4899; font-weight: 600; }
    .json-null { color: #94a3b8; font-style: italic; }

    /* Drag & Drop Overlay */
    .dropzone-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background-color: rgba(15, 23, 42, 0.85);
      z-index: 1000;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 20px;
      font-weight: 700;
      border: 4px dashed #38bdf8;
      pointer-events: none;
    }

    body.drag-over .dropzone-overlay {
      display: flex;
    }

    /* Responsive */
    @media (max-width: 900px) {
      main {
        grid-template-columns: 1fr;
        grid-template-rows: 1fr 1fr;
      }
      #clinical-dashboard {
        border-right: none;
        border-bottom: 1px solid var(--border-color);
      }
    }
  </style>
</head>
<body>

  <!-- Top Synthetic Notice -->
  <div class="synthetic-banner">
    100% SYNTHETIC CLINICAL TEST RECORD - ZERO PROTECTED HEALTH INFORMATION (NO PHI) - FOR TESTING AND INTEROPERABILITY ONLY
  </div>

  <!-- Header -->
  <header>
    <div class="brand-section">
      <span class="brand-title">HL7 FHIR Lab Report Dashboard</span>
      <span class="brand-badge">FHIR R4</span>
    </div>

    <div class="controls-section">
      <span class="select-label">Preset Report:</span>
      <select id="preset-selector" onchange="loadPresetReport(this.value)">
        <option value="synthetic_cancer_lab_report">MCED Cancer Signal Detected (Jane Q. Sample)</option>
        <option value="synthetic_mced_negative">MCED Signal Not Detected (Robert T. Sample)</option>
        <option value="synthetic_colorectal_ctdna">Colorectal ctDNA Liquid Biopsy (Harold K. Sample)</option>
        <option value="synthetic_hereditary_ngs_panel">Hereditary Cancer 15-Gene NGS (Brenda S. Sample)</option>
        <option value="synthetic_prostate_phi_panel">Prostate Health Index Panel (Arthur B. Sample)</option>
      </select>

      <input type="file" id="file-input" accept=".json" style="display: none;" onchange="handleFileSelect(event)">
      <button onclick="document.getElementById('file-input').click()">Upload Custom JSON</button>

      <div class="view-toggle">
        <button id="btn-view-split" class="active" onclick="setViewMode('split')">Split View</button>
        <button id="btn-view-clinical" onclick="setViewMode('clinical')">Clinical</button>
        <button id="btn-view-json" onclick="setViewMode('json')">FHIR JSON</button>
      </div>

      <button class="btn-primary" onclick="copyActiveJson()">Copy JSON</button>
    </div>
  </header>

  <!-- Main Content -->
  <main id="main-container">
    
    <!-- Left: Clinical Dashboard -->
    <section id="clinical-dashboard">
      
      <!-- Diagnostic Result Banner -->
      <div id="diagnostic-banner" class="result-banner status-abnormal" onclick="inspectResource('DiagnosticReport')">
        <div>
          <div class="result-title" id="banner-title">Cancer Signal Detected</div>
          <div class="result-subtitle" id="banner-subtitle">Next-Generation Sequencing cfDNA Methylation Profiling</div>
        </div>
        <div class="tag-badge" id="banner-flag">Abnormal Finding</div>
      </div>

      <!-- Patient & Facility Demographics Grid -->
      <div class="demographics-grid">
        <div class="info-card" id="card-patient" onclick="inspectResource('Patient')">
          <div class="info-card-header">
            <span>Patient Demographics</span>
            <span class="fhir-pill">Patient</span>
          </div>
          <div class="info-card-value" id="patient-name">Jane Q. Sample</div>
          <div class="info-card-sub" id="patient-details">DOB: 1972-05-12 (Female) | ID: P-44556677</div>
        </div>

        <div class="info-card" id="card-specimen" onclick="inspectResource('Specimen')">
          <div class="info-card-header">
            <span>Specimen Tracking</span>
            <span class="fhir-pill">Specimen</span>
          </div>
          <div class="info-card-value" id="specimen-type">Blood / Plasma (cfDNA)</div>
          <div class="info-card-sub" id="specimen-details">ID: SYN-992834-X | Collected: 2026-08-07</div>
        </div>

        <div class="info-card" id="card-provider" onclick="inspectResource('Practitioner')">
          <div class="info-card-header">
            <span>Ordering Clinician</span>
            <span class="fhir-pill">Practitioner</span>
          </div>
          <div class="info-card-value" id="provider-name">Dr. Avery Sterling</div>
          <div class="info-card-sub" id="provider-details">NPI: 1234567890 | Aurora Health Institute</div>
        </div>

        <div class="info-card" id="card-organization" onclick="inspectResource('Organization')">
          <div class="info-card-header">
            <span>Testing Facility</span>
            <span class="fhir-pill">Organization</span>
          </div>
          <div class="info-card-value" id="org-name">Nexus Precision Diagnostics</div>
          <div class="info-card-sub" id="org-details">CLIA ID: 00D1234567 | Fictional Heights, CA</div>
        </div>
      </div>

      <!-- Biomarkers & Test Findings -->
      <div class="section-title">
        <span>Discrete Biomarkers & Observations</span>
        <span class="fhir-pill" id="obs-count-badge">3 Observations</span>
      </div>

      <div class="biomarkers-container" id="biomarkers-list">
        <!-- Dynamically Populated -->
      </div>

      <!-- Clinical Narrative & Conclusion -->
      <div class="section-title">
        <span>Clinical Interpretation & Diagnostic Conclusion</span>
      </div>
      <div class="narrative-box" id="clinical-narrative" onclick="inspectResource('DiagnosticReport')">
        A cancer signal was detected in this blood sample. This result indicates that cell-free DNA (cfDNA) methylation patterns associated with cancer were identified. Further clinical evaluation, such as imaging or other diagnostic tests, is required to confirm the presence of cancer and determine the location.
      </div>

    </section>

    <!-- Right: Interactive FHIR Resource Inspector -->
    <section id="fhir-inspector">
      <div class="inspector-header">
        <div class="inspector-title">
          <span>FHIR Resource Inspector</span>
          <span class="fhir-pill" id="inspected-resource-type">Bundle</span>
        </div>
        <div style="font-size: 11px; color: #94a3b8;" id="inspected-resource-id">Transaction Bundle</div>
      </div>

      <div class="resource-tabs" id="resource-tabs-bar">
        <!-- Dynamically Populated Tabs -->
      </div>

      <div class="json-code-container">
        <pre id="json-display"></pre>
      </div>
    </section>

  </main>

  <!-- Drag & Drop Visual Overlay -->
  <div class="dropzone-overlay">
    Drop any FHIR R4 JSON Bundle file here to inspect
  </div>

  <script>
    // Embedded Default Datasets
    const PRESET_DATASETS = __PRESET_DATASETS_PLACEHOLDER__;

    let currentBundle = null;
    let currentSelectedResource = null;

    // Syntax Highlight JSON
    function syntaxHighlightJson(jsonObj) {
      const jsonStr = JSON.stringify(jsonObj, null, 2);
      return jsonStr.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(
        /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
        function (match) {
          let cls = 'json-number';
          if (/^"/.test(match)) {
            if (/:$/.test(match)) {
              cls = 'json-key';
            } else {
              cls = 'json-string';
            }
          } else if (/true|false/.test(match)) {
            cls = 'json-boolean';
          } else if (/null/.test(match)) {
            cls = 'json-null';
          }
          return '<span class="' + cls + '">' + match + '</span>';
        }
      );
    }

    // Load Bundle into Dashboard
    function loadBundle(bundle) {
      currentBundle = bundle;
      if (!bundle || !bundle.entry) return;

      const resources = bundle.entry.map(e => e.resource).filter(Boolean);
      
      const diagReport = resources.find(r => r.resourceType === 'DiagnosticReport') || {};
      const patient = resources.find(r => r.resourceType === 'Patient') || {};
      const practitioner = resources.find(r => r.resourceType === 'Practitioner') || {};
      const organization = resources.find(r => r.resourceType === 'Organization') || {};
      const specimen = resources.find(r => r.resourceType === 'Specimen') || {};
      const observations = resources.filter(r => r.resourceType === 'Observation');

      // 1. Diagnostic Banner
      const conclusion = diagReport.conclusion || (diagReport.code && diagReport.code.text) || 'Diagnostic Report';
      const isPathogenic = /positive|pathogenic|detected|elevated/i.test(conclusion) && !/not detected|negative/i.test(conclusion);
      const isNormal = /not detected|negative|normal/i.test(conclusion);
      
      const banner = document.getElementById('diagnostic-banner');
      const bannerTitle = document.getElementById('banner-title');
      const bannerSubtitle = document.getElementById('banner-subtitle');
      const bannerFlag = document.getElementById('banner-flag');

      banner.className = 'result-banner ' + (isNormal ? 'status-normal' : (isPathogenic ? 'status-abnormal' : 'status-elevated'));
      bannerTitle.textContent = (diagReport.code && diagReport.code.text) ? diagReport.code.text : 'Laboratory Diagnostic Panel';
      bannerSubtitle.textContent = conclusion.length > 120 ? conclusion.substring(0, 120) + '...' : conclusion;
      bannerFlag.textContent = isNormal ? 'Normal / Negative' : (isPathogenic ? 'Abnormal / Pathogenic' : 'Elevated Risk');

      // 2. Demographics Cards
      const patName = (patient.name && patient.name[0] && patient.name[0].text) || 'Unknown Patient';
      const patDob = patient.birthDate || 'N/A';
      const patGender = (patient.gender || 'Unknown').toUpperCase();
      const patMrn = (patient.identifier && patient.identifier[0] && patient.identifier[0].value) || 'N/A';
      document.getElementById('patient-name').textContent = patName;
      document.getElementById('patient-details').textContent = `DOB: ${patDob} (${patGender}) | MRN: ${patMrn}`;

      const specType = (specimen.type && specimen.type.text) || 'Biological Specimen';
      const specId = (specimen.identifier && specimen.identifier[0] && specimen.identifier[0].value) || 'N/A';
      const specDate = (specimen.collection && specimen.collection.collectedDateTime) || 'N/A';
      document.getElementById('specimen-type').textContent = specType;
      document.getElementById('specimen-details').textContent = `Specimen ID: ${specId} | Collected: ${specDate}`;

      const docName = (practitioner.name && practitioner.name[0] && practitioner.name[0].text) || 'Ordering Physician';
      const docNpi = (practitioner.identifier && practitioner.identifier[0] && practitioner.identifier[0].value) || 'N/A';
      document.getElementById('provider-name').textContent = docName;
      document.getElementById('provider-details').textContent = `NPI: ${docNpi}`;

      const orgName = organization.name || 'Testing Laboratory';
      const orgClia = (organization.identifier && organization.identifier[0] && organization.identifier[0].value) || 'N/A';
      document.getElementById('org-name').textContent = orgName;
      document.getElementById('org-details').textContent = `CLIA ID: ${orgClia}`;

      // 3. Biomarkers List
      document.getElementById('obs-count-badge').textContent = `${observations.length} Observations`;
      const obsContainer = document.getElementById('biomarkers-list');
      obsContainer.innerHTML = '';

      observations.forEach((obs, idx) => {
        const obsName = (obs.code && obs.code.text) || (obs.code && obs.code.coding && obs.code.coding[0] && obs.code.coding[0].display) || `Observation ${idx+1}`;
        const loincCode = (obs.code && obs.code.coding && obs.code.coding[0] && obs.code.coding[0].code) || 'Local';
        
        let displayVal = 'N/A';
        let unit = '';
        let numVal = null;
        if (obs.valueQuantity) {
          numVal = obs.valueQuantity.value;
          displayVal = String(obs.valueQuantity.value);
          unit = obs.valueQuantity.unit || '';
        } else if (obs.valueString) {
          displayVal = obs.valueString;
        }

        const interpCode = (obs.interpretation && obs.interpretation[0] && obs.interpretation[0].coding && obs.interpretation[0].coding[0] && obs.interpretation[0].coding[0].code) || 'N';
        const interpText = (obs.interpretation && obs.interpretation[0] && obs.interpretation[0].text) || (interpCode === 'A' ? 'Abnormal' : (interpCode === 'H' ? 'High' : (interpCode === 'L' ? 'Low' : 'Normal')));
        
        const isFlagAbnormal = interpCode === 'A' || interpCode === 'H';
        const isFlagLow = interpCode === 'L';
        const flagClass = isFlagAbnormal ? 'flag-high' : (isFlagLow ? 'flag-low' : 'flag-normal');

        const row = document.createElement('div');
        row.className = 'biomarker-row';
        row.id = `obs-card-${obs.id}`;
        row.onclick = () => inspectResourceObject(obs, `Observation: ${obsName}`);

        let rangeGaugeHtml = '';
        if (obs.referenceRange && obs.referenceRange[0] && numVal !== null) {
          const rr = obs.referenceRange[0];
          const low = rr.low ? rr.low.value : 0;
          const high = rr.high ? rr.high.value : (numVal * 1.5);
          
          let pct = 50;
          if (high > low) {
            pct = Math.max(5, Math.min(95, ((numVal - low) / (high - low)) * 65));
          }
          if (interpCode === 'H') pct = Math.max(72, Math.min(96, 65 + ((numVal - high) / high) * 30));

          rangeGaugeHtml = `
            <div class="range-gauge">
              <div class="gauge-bar-track">
                <div class="gauge-pointer" style="left: ${pct}%;"></div>
              </div>
              <div class="gauge-labels">
                <span>Ref: ${rr.text || `${low} - ${high} ${unit}`}</span>
                <span>Result: ${numVal} ${unit}</span>
              </div>
            </div>
          `;
        }

        row.innerHTML = `
          <div class="biomarker-header">
            <div>
              <span class="biomarker-name">${obsName}</span>
              <span class="biomarker-code-badge">LOINC: ${loincCode}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <div class="biomarker-result-val">${displayVal} <span class="biomarker-unit">${unit}</span></div>
              <span class="flag-badge ${flagClass}">${interpText}</span>
            </div>
          </div>
          ${rangeGaugeHtml}
        `;
        obsContainer.appendChild(row);
      });

      // 4. Clinical Narrative
      document.getElementById('clinical-narrative').textContent = diagReport.conclusion || 'No conclusion text provided.';

      // 5. Build Resource Tabs
      buildResourceTabs(bundle);

      // 6. Default view in inspector
      inspectResource('DiagnosticReport');
    }

    // Resource Navigation Tabs
    function buildResourceTabs(bundle) {
      const tabsBar = document.getElementById('resource-tabs-bar');
      tabsBar.innerHTML = '';

      // All Bundle tab
      const btnAll = document.createElement('button');
      btnAll.className = 'tab-btn active';
      btnAll.textContent = 'Bundle (Full)';
      btnAll.onclick = () => inspectBundle();
      tabsBar.appendChild(btnAll);

      bundle.entry.forEach(e => {
        const r = e.resource;
        if (!r) return;
        const btn = document.createElement('button');
        btn.className = 'tab-btn';
        btn.id = `tab-${r.id}`;
        
        let label = r.resourceType;
        if (r.resourceType === 'Observation') {
          label = (r.code && r.code.text) ? `Obs: ${r.code.text.substring(0, 14)}...` : 'Observation';
        }
        btn.textContent = label;
        btn.onclick = () => inspectResourceObject(r, label);
        tabsBar.appendChild(btn);
      });
    }

    function inspectBundle() {
      currentSelectedResource = currentBundle;
      document.getElementById('inspected-resource-type').textContent = 'Bundle';
      document.getElementById('inspected-resource-id').textContent = currentBundle.id || 'Transaction';
      document.getElementById('json-display').innerHTML = syntaxHighlightJson(currentBundle);
      setActiveTab('Bundle');
      clearActiveCards();
    }

    function inspectResource(type) {
      if (!currentBundle || !currentBundle.entry) return;
      const entry = currentBundle.entry.find(e => e.resource && e.resource.resourceType === type);
      if (entry) {
        inspectResourceObject(entry.resource, type);
      }
    }

    function inspectResourceObject(resource, label) {
      currentSelectedResource = resource;
      document.getElementById('inspected-resource-type').textContent = resource.resourceType;
      document.getElementById('inspected-resource-id').textContent = resource.id || 'id: N/A';
      document.getElementById('json-display').innerHTML = syntaxHighlightJson(resource);
      setActiveTab(resource.id);
      highlightCard(resource);
    }

    function setActiveTab(idOrLabel) {
      document.querySelectorAll('.tab-btn').forEach(btn => {
        if (btn.id === `tab-${idOrLabel}` || (idOrLabel === 'Bundle' && btn.textContent.startsWith('Bundle'))) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    function highlightCard(resource) {
      clearActiveCards();
      if (resource.resourceType === 'Patient') document.getElementById('card-patient').classList.add('active-resource');
      if (resource.resourceType === 'Practitioner') document.getElementById('card-provider').classList.add('active-resource');
      if (resource.resourceType === 'Organization') document.getElementById('card-organization').classList.add('active-resource');
      if (resource.resourceType === 'Specimen') document.getElementById('card-specimen').classList.add('active-resource');
      if (resource.resourceType === 'DiagnosticReport') document.getElementById('diagnostic-banner').classList.add('active-resource');
      if (resource.resourceType === 'Observation' && resource.id) {
        const row = document.getElementById(`obs-card-${resource.id}`);
        if (row) row.classList.add('active-resource');
      }
    }

    function clearActiveCards() {
      document.querySelectorAll('.active-resource').forEach(el => el.classList.remove('active-resource'));
    }

    function setViewMode(mode) {
      const main = document.getElementById('main-container');
      document.getElementById('btn-view-split').classList.toggle('active', mode === 'split');
      document.getElementById('btn-view-clinical').classList.toggle('active', mode === 'clinical');
      document.getElementById('btn-view-json').classList.toggle('active', mode === 'json');

      main.className = mode === 'clinical' ? 'view-clinical-only' : (mode === 'json' ? 'view-json-only' : '');
    }

    function copyActiveJson() {
      if (!currentSelectedResource) return;
      const str = JSON.stringify(currentSelectedResource, null, 2);
      navigator.clipboard.writeText(str).then(() => {
        alert('FHIR JSON copied to clipboard!');
      });
    }

    function loadPresetReport(presetKey) {
      if (PRESET_DATASETS[presetKey]) {
        loadBundle(PRESET_DATASETS[presetKey]);
      }
    }

    function handleFileSelect(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const parsed = JSON.parse(e.target.result);
          loadBundle(parsed);
        } catch (err) {
          alert('Error parsing JSON file: ' + err.message);
        }
      };
      reader.readAsText(file);
    }

    // Drag and drop listeners
    window.addEventListener('dragover', (e) => {
      e.preventDefault();
      document.body.classList.add('drag-over');
    });

    window.addEventListener('dragleave', (e) => {
      if (e.clientX <= 0 || e.clientY <= 0) {
        document.body.classList.remove('drag-over');
      }
    });

    window.addEventListener('drop', (e) => {
      e.preventDefault();
      document.body.classList.remove('drag-over');
      if (e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const parsed = JSON.parse(event.target.result);
            loadBundle(parsed);
          } catch (err) {
            alert('Error parsing dropped JSON: ' + err.message);
          }
        };
        reader.readAsText(file);
      }
    });

    // Initialize with first preset
    window.addEventListener('DOMContentLoaded', () => {
      const initialKey = Object.keys(PRESET_DATASETS)[0];
      if (initialKey) {
        loadBundle(PRESET_DATASETS[initialKey]);
      }
    });
  </script>
</body>
</html>
"""


def load_all_preset_bundles(output_dir: str = "output") -> Dict[str, Any]:
    """Loads all existing output FHIR bundles for embedding into the visualizer."""
    presets = {}
    preset_files = [
        ("synthetic_cancer_lab_report", os.path.join(output_dir, "synthetic_cancer_lab_report_fhir.json")),
        ("synthetic_mced_negative", os.path.join(output_dir, "synthetic_mced_negative_fhir.json")),
        ("synthetic_colorectal_ctdna", os.path.join(output_dir, "synthetic_colorectal_ctdna_fhir.json")),
        ("synthetic_hereditary_ngs_panel", os.path.join(output_dir, "synthetic_hereditary_ngs_panel_fhir.json")),
        ("synthetic_prostate_phi_panel", os.path.join(output_dir, "synthetic_prostate_phi_panel_fhir.json")),
    ]

    for key, path in preset_files:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    presets[key] = json.load(f)
            except Exception:
                pass
    return presets


def generate_html_dashboard(bundle: Optional[Dict[str, Any]] = None, output_html_path: str = "ui/fhir_viewer.html", presets: Optional[Dict[str, Any]] = None) -> str:
    """
    Generates a standalone HTML file containing the interactive FHIR dashboard and inspector.
    
    Args:
        bundle: Optional single FHIR bundle to load as the primary dataset.
        output_html_path: Destination path for the generated HTML file.
        presets: Optional dictionary of pre-loaded bundles.
        
    Returns:
        Absolute path to the created HTML file.
    """
    if presets is None:
        presets = load_all_preset_bundles()

    if bundle is not None:
        presets["active_custom_report"] = bundle

    presets_json_str = json.dumps(presets, indent=None)
    rendered_html = HTML_TEMPLATE.replace("__PRESET_DATASETS_PLACEHOLDER__", presets_json_str)

    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    return os.path.abspath(output_html_path)


def open_in_browser(html_path: str):
    """Opens the generated HTML visualizer in the default system web browser."""
    webbrowser.open(f"file://{os.path.abspath(html_path)}")

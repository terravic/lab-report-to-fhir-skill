"""
FHIR Lab Report Visualizer.
Generates an interactive, production-grade Web UI Dashboard from an HL7 FHIR R4 Bundle.
Includes Light/Dark mode toggle, multi-format client-side parser & file upload (PDF, JSON, TXT, CSV),
specimen chain-of-custody timeline, genomic variant chips, discrete biomarker range gauges,
actionable clinical recommendations, and synchronized bidirectional FHIR JSON inspection.
"""

import os
import json
import webbrowser
from typing import Dict, Any, Optional


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HL7 FHIR Clinical Diagnostic Report Dashboard</title>
  <!-- PDF.js for in-browser client-side PDF text extraction -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
  <script>
    if (typeof pdfjsLib !== 'undefined') {
      pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    }
  </script>
  <style>
    :root {
      --bg-main: #f8fafc;
      --bg-card: #ffffff;
      --bg-subtle: #f1f5f9;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-light: #94a3b8;
      --border-color: #e2e8f0;
      --border-focus: #0284c7;
      
      --primary: #0284c7;
      --primary-dark: #0369a1;
      --primary-light: #e0f2fe;
      
      --success: #16a34a;
      --success-bg: #dcfce7;
      --success-border: #86efac;
      --success-text: #14532d;
      
      --danger: #dc2626;
      --danger-bg: #fee2e2;
      --danger-border: #fca5a5;
      --danger-text: #7f1d1d;
      
      --warning: #d97706;
      --warning-bg: #fef3c7;
      --warning-border: #fcd34d;
      --warning-text: #78350f;
      
      --info: #2563eb;
      --info-bg: #dbeafe;
      --info-border: #93c5fd;

      --inspector-bg: #0f172a;
      --inspector-header-bg: #1e293b;
      --inspector-border: #334155;
      --inspector-text: #f8fafc;

      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      --font-mono: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
      --radius: 8px;
    }

    [data-theme="dark"] {
      --bg-main: #0b0f19;
      --bg-card: #131b2e;
      --bg-subtle: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-light: #64748b;
      --border-color: #27354f;
      --border-focus: #38bdf8;
      
      --primary: #0284c7;
      --primary-dark: #0ea5e9;
      --primary-light: #082f49;
      
      --success: #22c55e;
      --success-bg: #052e16;
      --success-border: #15803d;
      --success-text: #86efac;
      
      --danger: #ef4444;
      --danger-bg: #450a0a;
      --danger-border: #991b1b;
      --danger-text: #fca5a5;
      
      --warning: #f59e0b;
      --warning-bg: #451a03;
      --warning-border: #92400e;
      --warning-text: #fde68a;
      
      --info: #3b82f6;
      --info-bg: #172554;
      --info-border: #1d4ed8;

      --inspector-bg: #070b14;
      --inspector-header-bg: #0f172a;
      --inspector-border: #1e293b;
      --inspector-text: #f8fafc;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg-main);
      color: var(--text-main);
      line-height: 1.5;
      font-size: 13.5px;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    /* App Header */
    header {
      background-color: var(--bg-card);
      border-bottom: 1px solid var(--border-color);
      padding: 8px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-shrink: 0;
    }

    .brand-section {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .brand-title {
      font-size: 15px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .report-badge {
      background-color: var(--primary-light);
      color: var(--primary);
      font-size: 11px;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid var(--border-color);
      white-space: nowrap;
      max-width: 320px;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .controls-section {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .sample-select {
      font-family: var(--font-sans);
      font-size: 12px;
      padding: 5px 10px;
      border-radius: var(--radius);
      border: 1px solid var(--border-color);
      background-color: var(--bg-card);
      color: var(--text-main);
      cursor: pointer;
      font-weight: 500;
    }
    .sample-select:focus {
      outline: none;
      border-color: var(--border-focus);
    }

    button {
      font-family: var(--font-sans);
      font-size: 12px;
      padding: 5px 10px;
      border-radius: var(--radius);
      border: 1px solid var(--border-color);
      background-color: var(--bg-card);
      color: var(--text-main);
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-weight: 500;
    }

    button:focus {
      outline: none;
      border-color: var(--border-focus);
      box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.2);
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
      padding: 3px 8px;
      font-size: 11.5px;
      border-radius: 5px;
      color: var(--text-muted);
    }

    .view-toggle button.active {
      background-color: var(--bg-card);
      color: var(--text-main);
      font-weight: 600;
      box-shadow: var(--shadow-sm);
    }

    /* Notification Status Toast */
    #status-toast {
      display: none;
      background-color: var(--primary);
      color: #ffffff;
      padding: 6px 16px;
      font-size: 12px;
      font-weight: 600;
      text-align: center;
      flex-shrink: 0;
      transition: all 0.2s ease;
    }

    /* Main Container with Grid */
    main {
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 1fr;
      overflow: hidden;
      background-color: var(--bg-main);
      min-height: 0;
      position: relative;
    }

    main.view-clinical-only {
      grid-template-columns: 1fr !important;
    }
    main.view-clinical-only #fhir-inspector {
      display: none !important;
    }

    main.view-json-only {
      grid-template-columns: 1fr !important;
    }
    main.view-json-only #clinical-dashboard {
      display: none !important;
    }

    /* Clinical Dashboard Column */
    #clinical-dashboard {
      overflow-y: auto;
      padding: 16px 20px;
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      gap: 14px;
      min-height: 0;
    }

    /* FHIR Inspector Column */
    #fhir-inspector {
      overflow-y: hidden;
      background-color: var(--inspector-bg);
      color: var(--inspector-text);
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
    }

    /* Diagnostic Result Banner Card */
    .result-banner {
      padding: 14px 18px;
      border-radius: var(--radius);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      border: 1px solid transparent;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .result-banner:hover {
      box-shadow: var(--shadow-md);
    }

    .result-banner.active-resource {
      box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.4);
    }

    .result-banner.status-abnormal, .result-banner.status-pathogenic {
      background-color: var(--danger-bg);
      border-color: var(--danger-border);
      color: var(--danger-text);
    }

    .result-banner.status-normal {
      background-color: var(--success-bg);
      border-color: var(--success-border);
      color: var(--success-text);
    }

    .result-banner.status-elevated {
      background-color: var(--warning-bg);
      border-color: var(--warning-border);
      color: var(--warning-text);
    }

    .result-title {
      font-size: 16px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .result-subtitle {
      font-size: 12.5px;
      margin-top: 3px;
      opacity: 0.92;
      line-height: 1.4;
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

    /* Demographics 4-Card Grid */
    .demographics-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
    }

    .info-card {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      padding: 11px 13px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .info-card:hover {
      border-color: var(--primary);
    }

    .info-card.active-resource {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.25);
    }

    .info-card-header {
      font-size: 10.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .info-card-value {
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text-main);
    }

    .info-card-sub {
      font-size: 11.5px;
      color: var(--text-muted);
      line-height: 1.4;
    }

    .fhir-pill {
      font-family: var(--font-mono);
      font-size: 9.5px;
      padding: 1px 5px;
      border-radius: 4px;
      background-color: var(--bg-subtle);
      color: var(--text-muted);
      border: 1px solid var(--border-color);
    }

    /* Specimen Processing Timeline */
    .specimen-timeline-container {
      margin-top: 6px;
      padding-top: 6px;
      border-top: 1px dashed var(--border-color);
    }

    .timeline-steps {
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: relative;
    }

    .timeline-steps::before {
      content: "";
      position: absolute;
      top: 6px;
      left: 12px;
      right: 12px;
      height: 2px;
      background-color: var(--border-color);
      z-index: 1;
    }

    .timeline-step {
      display: flex;
      flex-direction: column;
      align-items: center;
      position: relative;
      z-index: 2;
      font-size: 10px;
      color: var(--text-muted);
    }

    .timeline-dot {
      width: 13px;
      height: 13px;
      border-radius: 50%;
      background-color: var(--primary);
      border: 2px solid var(--bg-card);
      margin-bottom: 2px;
    }

    .timeline-step.completed .timeline-dot {
      background-color: var(--success);
    }

    .timeline-step-label {
      font-weight: 600;
      color: var(--text-main);
    }

    .timeline-step-date {
      font-size: 9.5px;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }

    /* Search & Filter Controls */
    .filter-bar {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .search-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .search-input {
      flex: 1;
      font-family: var(--font-sans);
      font-size: 12.5px;
      padding: 6px 12px;
      border-radius: var(--radius);
      border: 1px solid var(--border-color);
      background-color: var(--bg-card);
      color: var(--text-main);
    }
    .search-input:focus {
      outline: none;
      border-color: var(--border-focus);
    }

    .filter-pills {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .filter-pill-btn {
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 12px;
      border: 1px solid var(--border-color);
      background-color: var(--bg-card);
      color: var(--text-muted);
      cursor: pointer;
      font-weight: 500;
    }

    .filter-pill-btn.active {
      background-color: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
      font-weight: 600;
    }

    /* Section Title */
    .section-title {
      font-size: 12px;
      font-weight: 700;
      color: var(--text-main);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 4px;
    }

    /* Biomarkers Container */
    .biomarkers-container {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .biomarker-row {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      padding: 10px 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
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
      gap: 10px;
    }

    .biomarker-name {
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text-main);
    }

    .biomarker-code-badge {
      font-family: var(--font-mono);
      font-size: 10.5px;
      background-color: var(--bg-subtle);
      color: var(--text-muted);
      padding: 1px 5px;
      border-radius: 4px;
      border: 1px solid var(--border-color);
      margin-left: 6px;
    }

    .biomarker-result-val {
      font-size: 14px;
      font-weight: 700;
      display: flex;
      align-items: baseline;
      gap: 4px;
    }

    .biomarker-unit {
      font-size: 11.5px;
      font-weight: 500;
      color: var(--text-muted);
    }

    .flag-badge {
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
    }
    .flag-normal { background-color: var(--success-bg); color: var(--success); }
    .flag-high, .flag-abnormal { background-color: var(--danger-bg); color: var(--danger); }
    .flag-low { background-color: var(--warning-bg); color: var(--warning); }

    /* Visual Range Gauge */
    .range-gauge {
      display: flex;
      flex-direction: column;
      gap: 3px;
      margin-top: 2px;
    }

    .gauge-bar-track {
      height: 7px;
      border-radius: 4px;
      position: relative;
    }

    .gauge-pointer {
      position: absolute;
      top: -3px;
      width: 5px;
      height: 13px;
      background-color: #0f172a;
      border: 1px solid #ffffff;
      border-radius: 2px;
      transform: translateX(-50%);
      box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    [data-theme="dark"] .gauge-pointer {
      background-color: #ffffff;
      border: 1px solid #000000;
    }

    .gauge-labels {
      display: flex;
      justify-content: space-between;
      font-size: 10.5px;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }

    /* Molecular Variant & CSO Component Chips */
    .variant-chips-container {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin-top: 2px;
    }

    .variant-chip {
      font-family: var(--font-mono);
      font-size: 10.5px;
      padding: 2px 6px;
      border-radius: 4px;
      background-color: var(--bg-subtle);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .variant-chip strong {
      color: var(--primary);
    }

    .origin-progress-bar {
      height: 6px;
      background-color: var(--bg-subtle);
      border-radius: 3px;
      overflow: hidden;
      margin-top: 4px;
      border: 1px solid var(--border-color);
    }

    .origin-progress-fill {
      height: 100%;
      background-color: var(--danger);
      border-radius: 3px;
    }

    /* Actionable Recommendations List */
    .recommendations-container {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .recommendation-item {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-left: 3px solid var(--primary);
      border-radius: var(--radius);
      padding: 9px 12px;
      font-size: 12px;
      line-height: 1.5;
      color: var(--text-main);
      cursor: pointer;
    }
    .recommendation-item:hover {
      border-color: var(--primary);
    }

    /* Structured Clinical Narrative & Metadata Accordions */
    .narrative-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }

    .clinical-card {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      padding: 10px 12px;
      font-size: 12px;
      line-height: 1.5;
      cursor: pointer;
    }

    .clinical-card:hover {
      border-color: var(--primary);
    }

    .clinical-card-title {
      font-size: 10.5px;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 4px;
      letter-spacing: 0.04em;
    }

    .governance-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 10.5px;
      font-weight: 600;
      color: var(--success);
      background-color: var(--success-bg);
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid var(--success-border);
      margin-top: 4px;
    }

    /* FHIR Inspector Header */
    .inspector-header {
      background-color: var(--inspector-header-bg);
      padding: 8px 14px;
      border-bottom: 1px solid var(--inspector-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-shrink: 0;
    }

    .inspector-title {
      font-size: 12px;
      font-weight: 700;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .resource-tabs {
      display: flex;
      gap: 3px;
      overflow-x: auto;
      padding: 6px 12px;
      background-color: var(--inspector-header-bg);
      border-bottom: 1px solid var(--inspector-border);
      flex-shrink: 0;
    }

    .tab-btn {
      font-family: var(--font-mono);
      font-size: 10.5px;
      background-color: var(--inspector-bg);
      color: #94a3b8;
      border: 1px solid var(--inspector-border);
      padding: 3px 8px;
      border-radius: 4px;
      white-space: nowrap;
      cursor: pointer;
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
      padding: 14px;
      overflow: auto;
      font-family: var(--font-mono);
      font-size: 11.5px;
      line-height: 1.55;
      background-color: var(--inspector-bg);
    }

    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-all;
      color: #f8fafc;
    }

    .json-key { color: #38bdf8; font-weight: 600; }
    .json-string { color: #4ade80; }
    .json-number { color: #f59e0b; }
    .json-boolean { color: #ec4899; font-weight: 600; }
    .json-null { color: #94a3b8; font-style: italic; }

    /* Drag and Drop Overlay */
    .drop-overlay {
      position: absolute;
      inset: 0;
      background: rgba(2, 132, 199, 0.15);
      backdrop-filter: blur(2px);
      border: 3px dashed var(--primary);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 50;
      font-size: 18px;
      font-weight: 700;
      color: var(--primary);
      pointer-events: none;
    }

    .drag-active .drop-overlay {
      display: flex;
    }

    /* Responsive */
    @media (max-width: 960px) {
      main {
        grid-template-columns: 1fr !important;
        grid-template-rows: 1fr 1fr;
      }
      #clinical-dashboard {
        border-right: none;
        border-bottom: 1px solid var(--border-color);
      }
      .demographics-grid, .narrative-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>

  <!-- Status Toast -->
  <div id="status-toast"></div>

  <!-- Header -->
  <header>
    <div class="brand-section">
      <span class="brand-title">HL7 FHIR Clinical Diagnostic Report</span>
      <span class="report-badge" id="header-patient-tag">Processed Lab Report</span>
    </div>

    <div class="controls-section">
      <!-- Sample Selector -->
      <select id="sample-select" class="sample-select" onchange="switchSample(this.value)">
        <option value="active">Active Converted Report</option>
        <option value="cancer_positive">1. MCED Detected (Lung & Pancreas)</option>
        <option value="mced_negative">2. MCED Negative Baseline</option>
        <option value="colorectal_ctdna">3. Colorectal ctDNA Liquid Biopsy</option>
        <option value="hereditary_ngs">4. Hereditary Cancer 15-Gene Panel</option>
        <option value="prostate_phi">5. Prostate Health Index (phi) Panel</option>
      </select>

      <div class="view-toggle">
        <button id="btn-view-split" class="active" onclick="setViewMode('split')">Split View</button>
        <button id="btn-view-clinical" onclick="setViewMode('clinical')">Clinical</button>
        <button id="btn-view-json" onclick="setViewMode('json')">FHIR JSON</button>
      </div>

      <button id="btn-theme-toggle" onclick="toggleTheme()">Dark Theme</button>
      <input type="file" id="file-input" accept=".json,.pdf,.txt,.csv" style="display: none;" onchange="handleFileSelect(event)">
      <button onclick="document.getElementById('file-input').click()">Upload Report</button>
      <button id="btn-download-json" onclick="downloadBundleJson()">Download JSON</button>
      <button id="btn-copy-json" class="btn-primary" onclick="copyActiveJson()">Copy JSON</button>
    </div>
  </header>

  <!-- Main Content -->
  <main id="main-container">
    
    <div class="drop-overlay" id="drop-overlay">
      Drop Lab Report File (PDF, JSON, TXT) Here to Process & Inspect
    </div>

    <!-- Left: Clinical Dashboard -->
    <section id="clinical-dashboard">
      
      <!-- Diagnostic Result Banner -->
      <div id="diagnostic-banner" class="result-banner status-abnormal" onclick="inspectResource('DiagnosticReport')">
        <div>
          <div class="result-title" id="banner-title">Diagnostic Test Result</div>
          <div class="result-subtitle" id="banner-subtitle">Clinical Diagnostic Panel</div>
        </div>
        <div class="tag-badge" id="banner-flag">Finding</div>
      </div>

      <!-- Patient & Facility Demographics Grid -->
      <div class="demographics-grid">
        <!-- Patient Card -->
        <div class="info-card" id="card-patient" onclick="inspectResource('Patient')">
          <div class="info-card-header">
            <span>Patient Demographics</span>
            <span class="fhir-pill">Patient</span>
          </div>
          <div class="info-card-value" id="patient-name">Patient Name</div>
          <div class="info-card-sub" id="patient-details">DOB: N/A | MRN: N/A</div>
        </div>

        <!-- Specimen Custody Card -->
        <div class="info-card" id="card-specimen" onclick="inspectResource('Specimen')">
          <div class="info-card-header">
            <span>Specimen Tracking & Custody</span>
            <span class="fhir-pill">Specimen</span>
          </div>
          <div class="info-card-value" id="specimen-type">Biological Specimen</div>
          <div class="info-card-sub" id="specimen-details">ID: N/A</div>
          <!-- Specimen Timeline -->
          <div class="specimen-timeline-container">
            <div class="timeline-steps">
              <div class="timeline-step completed">
                <div class="timeline-dot"></div>
                <div class="timeline-step-label">Collected</div>
                <div class="timeline-step-date" id="time-collected">--</div>
              </div>
              <div class="timeline-step completed">
                <div class="timeline-dot"></div>
                <div class="timeline-step-label">Received</div>
                <div class="timeline-step-date" id="time-received">--</div>
              </div>
              <div class="timeline-step completed">
                <div class="timeline-dot"></div>
                <div class="timeline-step-label">Processed</div>
                <div class="timeline-step-date" id="time-processed">Assay</div>
              </div>
              <div class="timeline-step completed">
                <div class="timeline-dot"></div>
                <div class="timeline-step-label">Reported</div>
                <div class="timeline-step-date" id="time-reported">--</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Ordering Clinician Card -->
        <div class="info-card" id="card-provider" onclick="inspectResource('Practitioner')">
          <div class="info-card-header">
            <span>Ordering Clinician</span>
            <span class="fhir-pill">Practitioner</span>
          </div>
          <div class="info-card-value" id="provider-name">Ordering Physician</div>
          <div class="info-card-sub" id="provider-details">NPI: N/A</div>
        </div>

        <!-- Testing Facility & Governance Card -->
        <div class="info-card" id="card-organization" onclick="inspectResource('Organization')">
          <div class="info-card-header">
            <span>Testing Facility & Governance</span>
            <span class="fhir-pill">Organization</span>
          </div>
          <div class="info-card-value" id="org-name">Testing Laboratory</div>
          <div class="info-card-sub" id="org-details">CLIA ID: N/A</div>
          <div class="governance-badge" id="org-signoff">✔ Verified Electronic Sign-Off</div>
        </div>
      </div>

      <!-- Biomarkers & Test Findings -->
      <div class="section-title">
        <span>Discrete Biomarkers & Clinical Observations</span>
        <span class="fhir-pill" id="obs-count-badge">0 Observations</span>
      </div>

      <div class="filter-bar">
        <div class="search-row">
          <input type="text" class="search-input" id="biomarker-search" placeholder="Filter biomarkers, analytes, LOINC codes, or variants..." oninput="filterBiomarkers()">
        </div>
        <div class="filter-pills">
          <button class="filter-pill-btn active" id="pill-all" onclick="setCategoryFilter('all')">All Observations</button>
          <button class="filter-pill-btn" id="pill-flagged" onclick="setCategoryFilter('flagged')">Flagged / Abnormal</button>
          <button class="filter-pill-btn" id="pill-quantitative" onclick="setCategoryFilter('quantitative')">Quantitative Gauges</button>
          <button class="filter-pill-btn" id="pill-genomic" onclick="setCategoryFilter('genomic')">Genomic Variants</button>
        </div>
      </div>

      <div class="biomarkers-container" id="biomarkers-list">
        <!-- Dynamically Populated -->
      </div>

      <!-- Actionable Clinical Recommendations -->
      <div class="section-title" id="recs-section-title">
        <span>Actionable Clinical Recommendations & Next Steps</span>
      </div>
      <div class="recommendations-container" id="recommendations-list" onclick="inspectResource('DiagnosticReport')">
        <!-- Dynamically Populated -->
      </div>

      <!-- Assay Methodology & Limitations Grid -->
      <div class="narrative-grid">
        <div class="clinical-card" id="card-methodology" onclick="inspectResource('DiagnosticReport')">
          <div class="clinical-card-title">Assay Methodology & Platform</div>
          <div id="methodology-text">Sequencing and biomarker quantification details.</div>
        </div>
        <div class="clinical-card" id="card-limitations" onclick="inspectResource('DiagnosticReport')">
          <div class="clinical-card-title">Intended Use & Clinical Limitations</div>
          <div id="limitations-text">Assay screening limitations and diagnostic caveats.</div>
        </div>
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

  <script>
    // Embedded Active Report FHIR JSON Bundle
    let ACTIVE_BUNDLE = __ACTIVE_BUNDLE_JSON__;
    let currentSelectedResource = null;
    let activeCategoryFilter = 'all';

    // Toast Notification helper
    function showToast(message, duration = 3000) {
      const toast = document.getElementById('status-toast');
      if (!toast) return;
      toast.textContent = message;
      toast.style.display = 'block';
      setTimeout(() => { toast.style.display = 'none'; }, duration);
    }

    // Theme Management
    function initTheme() {
      const savedTheme = localStorage.getItem('fhir_viewer_theme');
      if (savedTheme) {
        setTheme(savedTheme);
      } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setTheme('dark');
      } else {
        setTheme('light');
      }
    }

    function setTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('fhir_viewer_theme', theme);
      const btn = document.getElementById('btn-theme-toggle');
      if (btn) {
        btn.textContent = theme === 'dark' ? 'Light Theme' : 'Dark Theme';
      }
    }

    function toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      setTheme(current === 'dark' ? 'light' : 'dark');
    }

    // Syntax Highlight JSON
    function syntaxHighlightJson(jsonObj) {
      if (!jsonObj) return '';
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

    // Switch between sample presets
    function switchSample(sampleKey) {
      if (sampleKey === 'active') {
        renderDashboard(ACTIVE_BUNDLE);
        showToast('Viewing active converted report.');
        return;
      }
      if (SAMPLE_PRESETS[sampleKey]) {
        renderDashboard(SAMPLE_PRESETS[sampleKey]);
        showToast(`Loaded preset sample: ${sampleKey.replace('_', ' ').toUpperCase()}`);
      }
    }

    // Client-side Heuristic Text / Lab Parser to FHIR R4 Bundle
    function parseTextToFhirBundle(rawText, sourceFileName = "Uploaded Report") {
      const genId = () => 'urn:uuid:' + 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });

      const patientUuid = genId();
      const practitionerUuid = genId();
      const orgUuid = genId();
      const specimenUuid = genId();
      const reportUuid = genId();

      // Extract Patient
      let patName = "Patient Record";
      let patDob = "";
      let patGender = "unknown";
      let patId = "MRN-" + Math.floor(100000 + Math.random() * 900000);

      const nameMatch = rawText.match(/Name:\s*([A-Za-z\s\.\,\-]+?)(?=\s+(?:Provider|DOB|Sex|Gender|Patient ID|MRN|Specimen|Facility)|$|\n)/i);
      if (nameMatch && nameMatch[1] && !nameMatch[1].toLowerCase().includes("information")) patName = nameMatch[1].trim();

      const dobMatch = rawText.match(/DOB:\s*([A-Za-z0-9\/\,\s\-\(\)Age]+?)(?=\s+(?:Facility|Sex|Gender|Provider|Location|Collection)|$|\n)/i);
      if (dobMatch) {
        const rawDob = dobMatch[1].replace(/\(Age\s*\d+\)/i, '').trim();
        patDob = rawDob;
      }

      const sexMatch = rawText.match(/(?:Sex|Gender):\s*([A-Za-z]+)/i);
      if (sexMatch) {
        const s = sexMatch[1].toLowerCase();
        if (s.startsWith('f')) patGender = 'female';
        else if (s.startsWith('m')) patGender = 'male';
        else patGender = 'other';
      }

      const idMatch = rawText.match(/(?:Patient ID|MRN|Subject ID):\s*([A-Za-z0-9\-]+)/i);
      if (idMatch) patId = idMatch[1].trim();

      // Extract Provider
      let provName = "Ordering Physician";
      let provNpi = "1928374650";
      let provFac = "";
      const provMatch = rawText.match(/Provider:\s*([A-Za-z\s\.\,\-]+?)(?=\s+(?:Specimen ID|Facility|NPI|Location|DOB|Collection)|$|\n)/i);
      if (provMatch && provMatch[1] && !provMatch[1].toLowerCase().includes("information")) provName = provMatch[1].trim();
      const npiMatch = rawText.match(/NPI:\s*([0-9]{10})/i);
      if (npiMatch) provNpi = npiMatch[1].trim();
      const provFacMatch = rawText.match(/Facility:\s*([A-Za-z0-9\s\.\,\-]+?)(?=\s+(?:NPI|Location|Collection)|$|\n)/i);
      if (provFacMatch) provFac = provFacMatch[1].trim();

      // Extract Testing Laboratory & Governance
      let facName = "Nexus Precision Diagnostics";
      let cliaId = "00D1234567";
      let capNum = "8923412";
      let labDirector = "Dr. Eleanor Hayes, MD, PhD, FCAP";
      let labAddr = "888 Synthetic Way, CA 90210";

      const firstLine = (rawText.split('\n')[0] || '').replace(/\(SYNTHETIC[^\)]*\)/i, '').trim();
      if (firstLine && /laboratory|lab|diagnostics|genomics|reference/i.test(firstLine)) {
        facName = firstLine;
      }
      const cliaMatch = rawText.match(/CLIA(?:\s*ID)?:\s*([A-Za-z0-9]+)/i);
      if (cliaMatch) cliaId = cliaMatch[1].trim();
      const capMatch = rawText.match(/CAP(?:\s*Accr)?:\s*([0-9]+)/i);
      if (capMatch) capNum = capMatch[1].trim();
      const dirMatch = rawText.match(/(?:Lab\s+Director|Director):\s*([A-Za-z\s\.\,\-]+?)(?=\s*(?:\(Synthetic\)|Electronic Signature|Date|CLIA|CAP|\||$|\n))/i);
      if (dirMatch) labDirector = dirMatch[1].trim().replace(/,$/, '');

      // Extract Specimen
      let specType = "Blood / Plasma";
      let specId = "SPEC-" + Math.floor(10000 + Math.random() * 90000);
      let collDate = new Date().toISOString().split('T')[0];
      let recDate = collDate;
      let repDate = collDate;
      let specTube = "Streck cfDNA BCT (10.0 mL)";

      const specIdMatch = rawText.match(/(?:Specimen ID|Accession #|Sample ID):\s*([A-Za-z0-9\-]+)/i);
      if (specIdMatch) specId = specIdMatch[1].trim();
      const specTypeMatch = rawText.match(/(?:Specimen Type|Sample Type):\s*([A-Za-z0-9\s\/\-]+?)(?=\s+(?:Collection|Received|Volume|Tube)|$|\n)/i);
      if (specTypeMatch) specType = specTypeMatch[1].trim();
      const tubeMatch = rawText.match(/Tube:\s*([A-Za-z0-9\s\/\-\(\)\.]+?)(?=\s+(?:Collection|Received|Report)|$|\n)/i);
      if (tubeMatch) specTube = tubeMatch[1].trim();
      const collMatch = rawText.match(/(?:Collection Date|Collected):\s*([A-Za-z0-9\/\,\s\-]+?)(?=\s+(?:Received|Report Date|DOB)|$|\n)/i);
      if (collMatch) collDate = collMatch[1].trim();
      const recMatch = rawText.match(/Received Date:\s*([A-Za-z0-9\/\,\s\-]+?)(?=\s+(?:Report Date|Specimen)|$|\n)/i);
      if (recMatch) recDate = recMatch[1].trim();
      const repMatch = rawText.match(/Report Date:\s*([A-Za-z0-9\/\,\s\-]+?)(?=\s+(?:Test|Result|Summary)|$|\n)/i);
      if (repMatch) repDate = repMatch[1].trim();

      // Extract Summary & Conclusion
      let conclusion = "Laboratory diagnostic panel complete.";
      const summaryMatch = rawText.match(/Test Result Summary[\s\S]+?(?:Result:\s*[^\n]+\n)?([\s\S]+?)(?=Cancer Signal Origin|Clinical Interpretation|Quantitative|Observations|Detailed Genetic Variant|Biomarker Findings|Test Results|Origin 1|Priority|Methodology|Laboratory Observations|$)/i);
      if (summaryMatch && summaryMatch[1]) conclusion = summaryMatch[1].replace(/\n+/g, ' ').trim();

      // Panel Title
      let panelTitle = "Laboratory Diagnostic Panel";
      let panelLoinc = "11502-2";
      if (/galleri|early detection|mced|cancer signal/i.test(rawText)) {
        panelTitle = "Multi-Cancer Early Detection Screening Report";
        panelLoinc = "94076-7";
      } else if (/prostate|phi|psa/i.test(rawText)) {
        panelTitle = "Prostate Health Index and Early Cancer Biomarker Panel";
        panelLoinc = "72305-6";
      } else if (/colorectal|liquid biopsy|ctdna|sept9/i.test(rawText)) {
        panelTitle = "Liquid Biopsy Colorectal ctDNA Early Screening Report";
        panelLoinc = "94078-3";
      } else if (/hereditary|brca|genetic|ngs panel/i.test(rawText)) {
        panelTitle = "Hereditary Cancer Risk 15-Gene NGS Panel";
        panelLoinc = "79207-7";
      }

      // Observations List
      const observations = [];
      const obsUuids = [];

      // Check Cancer Signal
      if (/Cancer Signal Detected/i.test(rawText) && !/Cancer Signal Not Detected/i.test(rawText)) {
        const obsId = genId();
        obsUuids.push(obsId);
        observations.push({
          resourceType: "Observation",
          id: obsId,
          status: "final",
          code: { coding: [{ system: "http://loinc.org", code: "94076-7", display: "Cancer signal methylation analysis in cell-free DNA" }], text: "Cancer Signal Status" },
          subject: { reference: patientUuid },
          valueString: "Cancer Signal Detected",
          interpretation: [{ coding: [{ system: "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation", code: "A", display: "Abnormal" }] }]
        });
      } else if (/Cancer Signal Not Detected/i.test(rawText)) {
        const obsId = genId();
        obsUuids.push(obsId);
        observations.push({
          resourceType: "Observation",
          id: obsId,
          status: "final",
          code: { coding: [{ system: "http://loinc.org", code: "94076-7", display: "Cancer signal methylation analysis in cell-free DNA" }], text: "Cancer Signal Status" },
          subject: { reference: patientUuid },
          valueString: "Cancer Signal Not Detected",
          interpretation: [{ coding: [{ system: "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation", code: "N", display: "Normal" }] }]
        });
      }

      // Check predicted origins
      const origRegex = /Origin\s*(\d+):?\s*([A-Za-z\s]+?)\s*(?:\((\d+\%)\)|(\d+\%))/gi;
      let origMatch;
      while ((origMatch = origRegex.exec(rawText)) !== null) {
        const origNum = origMatch[1];
        const tissue = origMatch[2].trim();
        const freq = origMatch[3] || origMatch[4] || "";
        const obsId = genId();
        obsUuids.push(obsId);
        observations.push({
          resourceType: "Observation",
          id: obsId,
          status: "final",
          code: { coding: [{ system: "http://loinc.org", code: "94077-5", display: `Predicted cancer signal origin ${origNum}` }], text: `Predicted Cancer Signal Origin ${origNum}` },
          subject: { reference: patientUuid },
          valueString: `${tissue} (${freq})`,
          component: [
            { code: { text: "Tissue" }, valueString: tissue },
            { code: { text: "Accuracy Frequency" }, valueString: freq }
          ],
          interpretation: [{ coding: [{ system: "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation", code: "A", display: "Abnormal" }] }]
        });
      }

      // Assemble FHIR Bundle
      const bundle = {
        resourceType: "Bundle",
        id: "bundle-" + Math.floor(100000 + Math.random() * 900000),
        type: "transaction",
        timestamp: new Date().toISOString(),
        entry: [
          {
            fullUrl: patientUuid,
            resource: {
              resourceType: "Patient",
              id: patientUuid.replace('urn:uuid:', ''),
              name: [{ use: "official", text: patName }],
              gender: patGender,
              birthDate: patDob,
              identifier: [{ system: "urn:oid:medical-record-number", value: patId }]
            }
          },
          {
            fullUrl: practitionerUuid,
            resource: {
              resourceType: "Practitioner",
              id: practitionerUuid.replace('urn:uuid:', ''),
              name: [{ use: "official", text: provName }],
              identifier: [{ system: "http://hl7.org/fhir/sid/us-npi", value: provNpi }]
            }
          },
          {
            fullUrl: orgUuid,
            resource: {
              resourceType: "Organization",
              id: orgUuid.replace('urn:uuid:', ''),
              name: facName,
              identifier: [
                { system: "urn:oid:2.16.840.1.113883.4.7", value: cliaId },
                { system: "urn:oid:2.16.840.1.113883.4.3.38", value: capNum }
              ],
              address: [{ use: "work", text: labAddr }]
            }
          },
          {
            fullUrl: specimenUuid,
            resource: {
              resourceType: "Specimen",
              id: specimenUuid.replace('urn:uuid:', ''),
              type: { text: specType },
              identifier: [{ value: specId }],
              collection: { collectedDateTime: collDate },
              receivedTime: recDate,
              container: [{ type: { text: specTube } }]
            }
          },
          ...observations.map(obs => ({
            fullUrl: obs.id,
            resource: { ...obs, id: obs.id.replace('urn:uuid:', '') }
          })),
          {
            fullUrl: reportUuid,
            resource: {
              resourceType: "DiagnosticReport",
              id: reportUuid.replace('urn:uuid:', ''),
              status: "final",
              code: { coding: [{ system: "http://loinc.org", code: panelLoinc, display: panelTitle }], text: panelTitle },
              subject: { reference: patientUuid },
              performer: [{ reference: orgUuid }, { reference: practitionerUuid }],
              specimen: [{ reference: specimenUuid }],
              result: obsUuids.map(u => ({ reference: u })),
              conclusion: conclusion
            }
          }
        ]
      };

      return bundle;
    }

    // Set Category Filter
    function setCategoryFilter(category) {
      activeCategoryFilter = category;
      document.getElementById('pill-all').classList.toggle('active', category === 'all');
      document.getElementById('pill-flagged').classList.toggle('active', category === 'flagged');
      document.getElementById('pill-quantitative').classList.toggle('active', category === 'quantitative');
      document.getElementById('pill-genomic').classList.toggle('active', category === 'genomic');
      filterBiomarkers();
    }

    // Filter Biomarkers
    function filterBiomarkers() {
      const q = (document.getElementById('biomarker-search').value || '').toLowerCase();
      document.querySelectorAll('.biomarker-row').forEach(row => {
        const text = (row.getAttribute('data-search-text') || '').toLowerCase();
        const isFlagged = row.getAttribute('data-is-flagged') === 'true';
        const isQuant = row.getAttribute('data-is-quant') === 'true';
        const isGenomic = row.getAttribute('data-is-genomic') === 'true';

        let matchesCategory = true;
        if (activeCategoryFilter === 'flagged') matchesCategory = isFlagged;
        else if (activeCategoryFilter === 'quantitative') matchesCategory = isQuant;
        else if (activeCategoryFilter === 'genomic') matchesCategory = isGenomic;

        const matchesQuery = text.includes(q);
        row.style.display = (matchesCategory && matchesQuery) ? 'flex' : 'none';
      });
    }

    // Load Single Bundle into Dashboard
    function renderDashboard(bundle) {
      if (!bundle) return;
      if (!bundle.entry && bundle.resourceType) {
        bundle = { resourceType: 'Bundle', type: 'collection', entry: [{ resource: bundle }] };
      }
      ACTIVE_BUNDLE = bundle;

      const resources = (bundle.entry || []).map(e => e.resource).filter(Boolean);
      
      const diagReport = resources.find(r => r.resourceType === 'DiagnosticReport') || {};
      const patient = resources.find(r => r.resourceType === 'Patient') || {};
      const practitioner = resources.find(r => r.resourceType === 'Practitioner') || {};
      const organization = resources.find(r => r.resourceType === 'Organization') || {};
      const specimen = resources.find(r => r.resourceType === 'Specimen') || {};
      const observations = resources.filter(r => r.resourceType === 'Observation');

      // 1. Diagnostic Banner Status Evaluation
      const conclusion = (diagReport.conclusion || (diagReport.code && diagReport.code.text) || 'Diagnostic Report').trim();
      const firstSentence = conclusion.split('.')[0] || conclusion;
      
      const hasAbnormalObs = observations.some(obs => {
        const interpCode = (obs.interpretation && obs.interpretation[0] && obs.interpretation[0].coding && obs.interpretation[0].coding[0] && obs.interpretation[0].coding[0].code) || '';
        return ['A', 'H', 'L', 'POS', 'DET', 'AA', 'HH', 'LL'].includes(interpCode.toUpperCase());
      });

      const isPathogenicOrDetected = /cancer signal detected|pathogenic variant|positive/i.test(firstSentence) || /cancer signal detected|pathogenic variant/i.test(conclusion);
      const isElevatedRisk = /elevated prostate health index|elevated risk|elevated probability|high risk|elevated/i.test(firstSentence) || /elevated/i.test(conclusion);

      const banner = document.getElementById('diagnostic-banner');
      const bannerTitle = document.getElementById('banner-title');
      const bannerSubtitle = document.getElementById('banner-subtitle');
      const bannerFlag = document.getElementById('banner-flag');

      if (isPathogenicOrDetected) {
        banner.className = 'result-banner status-abnormal';
        bannerFlag.textContent = 'Abnormal / Pathogenic';
      } else if (isElevatedRisk || hasAbnormalObs) {
        banner.className = 'result-banner status-elevated';
        bannerFlag.textContent = 'Elevated Risk / Abnormal Finding';
      } else {
        banner.className = 'result-banner status-normal';
        bannerFlag.textContent = 'Normal / Negative';
      }

      bannerTitle.textContent = (diagReport.code && diagReport.code.text) ? diagReport.code.text : 'Laboratory Diagnostic Panel';
      bannerSubtitle.textContent = firstSentence.length > 150 ? firstSentence.substring(0, 150) + '...' : firstSentence;

      // 2. Demographics Cards
      const patName = (patient.name && patient.name[0] && patient.name[0].text) || 'Unknown Patient';
      const patDob = patient.birthDate || 'N/A';
      const patGender = (patient.gender || 'Unknown').toUpperCase();
      const patMrn = (patient.identifier && patient.identifier[0] && patient.identifier[0].value) || 'N/A';
      
      let ageStr = '';
      if (patDob !== 'N/A') {
        const birthYear = parseInt(patDob.split('-')[0], 10);
        if (!isNaN(birthYear)) {
          const age = 2026 - birthYear;
          ageStr = ` (Age ${age})`;
        }
      }
      document.getElementById('patient-name').textContent = patName;
      document.getElementById('patient-details').textContent = `DOB: ${patDob}${ageStr} | ${patGender} | MRN: ${patMrn}`;
      document.getElementById('header-patient-tag').textContent = `${patName} | ${patMrn}`;

      // Specimen Card
      const specType = (specimen.type && (specimen.type.text || (specimen.type.coding && specimen.type.coding[0] && specimen.type.coding[0].display))) || 'Biological Specimen';
      const specId = (specimen.identifier && specimen.identifier[0] && specimen.identifier[0].value) || 'N/A';
      const specTube = (specimen.container && specimen.container[0] && specimen.container[0].type && specimen.container[0].type.text) || '';
      const specCollDate = (specimen.collection && specimen.collection.collectedDateTime) || diagReport.effectiveDateTime || 'N/A';
      const specRecDate = specimen.receivedTime || specCollDate;
      const specRepDate = diagReport.issued || diagReport.effectiveDateTime || 'N/A';

      document.getElementById('specimen-type').textContent = specType + (specTube ? ` • ${specTube}` : '');
      document.getElementById('specimen-details').textContent = `Specimen ID: ${specId}`;
      document.getElementById('time-collected').textContent = specCollDate;
      document.getElementById('time-received').textContent = specRecDate;
      document.getElementById('time-processed').textContent = 'Assay QC';
      document.getElementById('time-reported').textContent = specRepDate;

      // Provider Card
      const docName = (practitioner.name && practitioner.name[0] && practitioner.name[0].text) || 'Ordering Clinician';
      const docNpi = (practitioner.identifier && practitioner.identifier[0] && practitioner.identifier[0].value) || 'N/A';
      document.getElementById('provider-name').textContent = docName;
      document.getElementById('provider-details').textContent = `NPI: ${docNpi} | Clinical Diagnostics`;

      // Organization Card
      const orgName = organization.name || 'Testing Clinical Laboratory';
      const cliaIdObj = (organization.identifier || []).find(i => (i.system || '').includes('4.7')) || (organization.identifier && organization.identifier[0]) || {};
      const capObj = (organization.identifier || []).find(i => (i.system || '').includes('4.3.38')) || {};
      const cliaVal = cliaIdObj.value || 'N/A';
      const capVal = capObj.value || 'Verified';
      const orgAddr = (organization.address && organization.address[0] && organization.address[0].text) || '';
      
      document.getElementById('org-name').textContent = orgName;
      document.getElementById('org-details').innerHTML = `CLIA ID: ${cliaVal} | CAP Accr: ${capVal}${orgAddr ? '<br/>' + orgAddr : ''}`;

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
        
        const isFlagAbnormal = ['A', 'H', 'POS', 'AA', 'HH'].includes(interpCode.toUpperCase()) || interpText.toLowerCase().includes('abnormal') || interpText.toLowerCase().includes('pathogenic');
        const isFlagLow = interpCode === 'L';
        const flagClass = isFlagAbnormal ? 'flag-high' : (isFlagLow ? 'flag-low' : 'flag-normal');

        const isQuant = numVal !== null;
        const isGenomic = /brca|kras|braf|tp53|palb2|chek2|cdh1|sept9|variant|mutation|gene/i.test(obsName) || /c\.|p\.|vaf|pathogenic/i.test(displayVal);

        const row = document.createElement('div');
        row.className = 'biomarker-row';
        row.id = `obs-card-${obs.id}`;
        row.setAttribute('data-search-text', `${obsName} ${loincCode} ${displayVal} ${interpText}`.toLowerCase());
        row.setAttribute('data-is-flagged', isFlagAbnormal ? 'true' : 'false');
        row.setAttribute('data-is-quant', isQuant ? 'true' : 'false');
        row.setAttribute('data-is-genomic', isGenomic ? 'true' : 'false');
        row.onclick = () => inspectResourceObject(obs, `Obs: ${obsName}`);

        // Build specialized details (Gauges, Genomic Variant chips, CSO Origin progress bars)
        let specializedHtml = '';

        // 1. Quantitative Gauge
        if (numVal !== null) {
          const rr = (obs.referenceRange && obs.referenceRange[0]) || {};
          let low = rr.low ? rr.low.value : null;
          let high = rr.high ? rr.high.value : null;
          const refText = rr.text || '';

          if (high === null) {
            const lessM = refText.match(/<[=\s]*([0-9\.]+)/);
            if (lessM) high = parseFloat(lessM[1]);
          }
          if (low === null) {
            const grtM = refText.match(/>[=\s]*([0-9\.]+)/);
            if (grtM) low = parseFloat(grtM[1]);
          }
          if (low === null && high === null) {
            const rangeM = refText.match(/([0-9\.]+)\s*-\s*([0-9\.]+)/);
            if (rangeM) {
              low = parseFloat(rangeM[1]);
              high = parseFloat(rangeM[2]);
            }
          }

          let pct = 50;
          let trackGradient = 'linear-gradient(to right, #86efac 0%, #86efac 65%, #fca5a5 65%, #fca5a5 100%)';

          if (interpCode === 'H') {
            if (high !== null && high > 0) {
              const ratio = (numVal - high) / high;
              pct = Math.min(95, Math.max(72, 70 + ratio * 25));
            } else {
              pct = 85;
            }
          } else if (interpCode === 'L') {
            trackGradient = 'linear-gradient(to right, #fca5a5 0%, #fca5a5 35%, #86efac 35%, #86efac 100%)';
            if (low !== null && low > 0) {
              const ratio = (low - numVal) / low;
              pct = Math.max(5, Math.min(30, 30 - ratio * 20));
            } else {
              pct = 15;
            }
          } else {
            if (low !== null && high !== null && high > low) {
              pct = Math.max(10, Math.min(60, 10 + ((numVal - low) / (high - low)) * 50));
            } else if (high !== null) {
              pct = Math.max(10, Math.min(55, (numVal / high) * 50));
            } else {
              pct = 40;
            }
          }

          const refDisplay = refText || (low !== null && high !== null ? `${low} - ${high} ${unit}` : (high !== null ? `< ${high} ${unit}` : (low !== null ? `> ${low} ${unit}` : 'Reference Range N/A')));

          specializedHtml = `
            <div class="range-gauge">
              <div class="gauge-bar-track" style="background: ${trackGradient};">
                <div class="gauge-pointer" style="left: ${pct}%;"></div>
              </div>
              <div class="gauge-labels">
                <span>Ref: ${refDisplay}</span>
                <span>Result: ${numVal} ${unit}</span>
              </div>
            </div>
          `;
        } 
        // 2. CSO Origin Distribution Bar
        else if (/predicted cancer signal origin/i.test(obsName)) {
          const pctM = displayVal.match(/(\d+(?:\.\d+)?)\s*%/);
          const pctVal = pctM ? parseFloat(pctM[1]) : 0;
          specializedHtml = `
            <div class="origin-progress-bar">
              <div class="origin-progress-fill" style="width: ${pctVal}%;"></div>
            </div>
          `;
        }
        // 3. Genomic Variant Chips
        else if (obs.component && obs.component.length > 0) {
          let chips = '';
          obs.component.forEach(c => {
            const cName = (c.code && c.code.text) || 'Detail';
            const cVal = c.valueString || '';
            chips += `<span class="variant-chip"><strong>${cName}:</strong> ${cVal}</span>`;
          });
          if (chips) {
            specializedHtml = `<div class="variant-chips-container">${chips}</div>`;
          }
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
          ${specializedHtml}
        `;
        obsContainer.appendChild(row);
      });

      // 4. Actionable Clinical Recommendations
      const recsContainer = document.getElementById('recommendations-list');
      recsContainer.innerHTML = '';
      
      const fullText = diagReport.conclusion || '';
      const recLines = [];

      // Extract bullet points from conclusion
      const rawRecMatch = fullText.match(/Recommended Next Steps:?[\s\S]+?(?=Methodology|Limitations|Laboratory Director|$)/i);
      if (rawRecMatch) {
        const lines = rawRecMatch[0].split('\n');
        lines.forEach(l => {
          const cleanL = l.replace(/^•\s*|^-\s*|^Recommended Next Steps:?\s*/i, '').trim();
          if (cleanL && cleanL.length > 10) recLines.push(cleanL);
        });
      }

      if (recLines.length === 0) {
        if (/cancer signal detected/i.test(fullText)) {
          recLines.push("High-resolution imaging: Contrast-enhanced chest CT and dedicated abdominal MRI / EUS.");
          recLines.push("Specialist consultation: Prompt referral to thoracic and gastroenterology oncology teams.");
          recLines.push("Diagnostic tissue biopsy: If a suspicious lesion is identified on diagnostic imaging.");
        } else if (/brca1/i.test(fullText)) {
          recLines.push("High-risk breast surveillance: Annual contrast-enhanced breast MRI starting at age 25–30.");
          recLines.push("Ovarian cancer risk reduction: Consultation for risk-reducing salpingo-oophorectomy (RRSO).");
          recLines.push("Cascade genetic testing: Inform and offer targeted variant testing to first-degree relatives.");
        } else if (/sept9|kras/i.test(fullText)) {
          recLines.push("Diagnostic colonoscopy: High-definition mucosal inspection with targeted biopsy of identified lesions.");
          recLines.push("Staging radiology: Contrast-enhanced CT of abdomen and pelvis.");
          recLines.push("Therapeutic note: KRAS p.G12D mutation confers resistance to anti-EGFR antibody therapies.");
        } else if (/phi|psa/i.test(fullText)) {
          recLines.push("Multiparametric prostate MRI (mpMRI): 3-Tesla pelvic mpMRI with PI-RADS scoring.");
          recLines.push("Urology consult: Referral for MRI-fusion targeted and systematic prostate biopsy.");
        } else {
          recLines.push("Routine preventative screening: Continue standard age-appropriate cancer screenings as indicated.");
          recLines.push("Follow-up: Regular annual wellness examinations with primary care physician.");
        }
      }

      recLines.forEach(rec => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';
        item.innerHTML = `<strong>•</strong> ${rec}`;
        recsContainer.appendChild(item);
      });

      // 5. Methodology & Limitations Cards
      let methodText = "Plasma cfDNA was analyzed by targeted bisulfite conversion and deep Next-Generation Sequencing (NGS) on Illumina NovaSeq 6000 systems. Proprietary machine-learning classification models evaluated methylation patterns.";
      let limitText = "This test is an early detection screening tool and is not a definitive histological diagnosis. Negative results do not completely rule out malignancy. Results should be interpreted in clinical context.";

      const methMatch = fullText.match(/Methodology:\s*([\s\S]+?)(?=Limitations|Laboratory Director|$)/i);
      if (methMatch) methodText = methMatch[1].trim();

      const limMatch = fullText.match(/Limitations:\s*([\s\S]+?)(?=Laboratory Director|Methodology|$)/i);
      if (limMatch) limitText = limMatch[1].trim();

      document.getElementById('methodology-text').textContent = methodText;
      document.getElementById('limitations-text').textContent = limitText;

      // 6. Build Resource Tabs
      buildResourceTabs(bundle);

      // 7. Default view in inspector
      inspectResource('DiagnosticReport');
    }

    // Resource Navigation Tabs
    function buildResourceTabs(bundle) {
      const tabsBar = document.getElementById('resource-tabs-bar');
      tabsBar.innerHTML = '';

      // All Bundle tab
      const btnAll = document.createElement('button');
      btnAll.className = 'tab-btn active';
      btnAll.id = 'tab-bundle';
      btnAll.textContent = 'Bundle (Full)';
      btnAll.onclick = () => inspectBundle();
      tabsBar.appendChild(btnAll);

      (bundle.entry || []).forEach(e => {
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
      currentSelectedResource = ACTIVE_BUNDLE;
      document.getElementById('inspected-resource-type').textContent = 'Bundle';
      document.getElementById('inspected-resource-id').textContent = ACTIVE_BUNDLE.id || 'Transaction';
      document.getElementById('json-display').innerHTML = syntaxHighlightJson(ACTIVE_BUNDLE);
      setActiveTab('bundle');
      clearActiveCards();
    }

    function inspectResource(type) {
      if (!ACTIVE_BUNDLE || !ACTIVE_BUNDLE.entry) return;
      const entry = ACTIVE_BUNDLE.entry.find(e => e.resource && e.resource.resourceType === type);
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
        if (btn.id === `tab-${idOrLabel}` || (idOrLabel === 'bundle' && btn.id === 'tab-bundle')) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    function highlightCard(resource) {
      clearActiveCards();
      if (!resource) return;
      if (resource.resourceType === 'Patient') document.getElementById('card-patient').classList.add('active-resource');
      if (resource.resourceType === 'Practitioner') document.getElementById('card-provider').classList.add('active-resource');
      if (resource.resourceType === 'Organization') document.getElementById('card-organization').classList.add('active-resource');
      if (resource.resourceType === 'Specimen') document.getElementById('card-specimen').classList.add('active-resource');
      if (resource.resourceType === 'DiagnosticReport') {
        document.getElementById('diagnostic-banner').classList.add('active-resource');
        document.getElementById('card-methodology').classList.add('active-resource');
      }
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

      if (mode === 'clinical') {
        main.className = 'view-clinical-only';
      } else if (mode === 'json') {
        main.className = 'view-json-only';
        if (!currentSelectedResource) {
          inspectBundle();
        }
      } else {
        main.className = '';
      }
    }

    function fallbackCopyText(text, callback) {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.top = '-9999px';
      textArea.style.left = '-9999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        const successful = document.execCommand('copy');
        if (successful && callback) callback();
      } catch (err) {
        console.error('Fallback copy failed', err);
      }
      document.body.removeChild(textArea);
    }

    function copyActiveJson() {
      const targetObj = currentSelectedResource || ACTIVE_BUNDLE;
      if (!targetObj) return;
      const str = JSON.stringify(targetObj, null, 2);
      const copyBtn = document.getElementById('btn-copy-json');
      const originalText = copyBtn ? copyBtn.textContent : 'Copy JSON';

      function showSuccess() {
        if (copyBtn) {
          copyBtn.textContent = 'Copied!';
          copyBtn.style.backgroundColor = '#16a34a';
          setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.style.backgroundColor = '';
          }, 2000);
        }
      }

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(str).then(showSuccess).catch(() => {
          fallbackCopyText(str, showSuccess);
        });
      } else {
        fallbackCopyText(str, showSuccess);
      }
    }

    function downloadBundleJson() {
      const targetObj = ACTIVE_BUNDLE;
      if (!targetObj) return;
      const jsonStr = JSON.stringify(targetObj, null, 2);
      const dlBtn = document.getElementById('btn-download-json');
      const originalText = dlBtn ? dlBtn.textContent : 'Download JSON';

      try {
        const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        const filename = (targetObj.id ? `${targetObj.id}` : 'fhir_bundle') + '.json';
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        setTimeout(() => {
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
        }, 150);

        if (dlBtn) {
          dlBtn.textContent = 'Downloaded!';
          setTimeout(() => { dlBtn.textContent = originalText; }, 2000);
        }
      } catch (e) {
        console.error('Blob download failed, fallback to data URI', e);
        const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(jsonStr);
        const a = document.createElement('a');
        a.href = dataStr;
        a.download = 'fhir_bundle.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }
    }

    // Drag and Drop & Multi-format File Upload (PDF, JSON, TXT, CSV)
    function handleFileSelect(e) {
      const file = e.target.files && e.target.files[0];
      if (file) processUploadedFile(file);
    }

    async function processUploadedFile(file) {
      const fileName = file.name.toLowerCase();
      showToast(`Processing file: ${file.name}...`);

      if (fileName.endsWith('.json')) {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const parsed = JSON.parse(event.target.result);
            renderDashboard(parsed);
            showToast(`Loaded FHIR JSON bundle: ${file.name}`);
          } catch (err) {
            alert('Error parsing uploaded JSON file: ' + err.message);
          }
        };
        reader.readAsText(file);
      } else if (fileName.endsWith('.pdf')) {
        if (typeof pdfjsLib === 'undefined') {
          alert('PDF parsing requires pdf.js library. For CLI processing run:\npython3 scripts/visualize.py ' + file.name);
          return;
        }
        try {
          const arrayBuffer = await file.arrayBuffer();
          const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
          const pdf = await loadingTask.promise;
          let fullText = '';
          for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
            const page = await pdf.getPage(pageNum);
            const textContent = await page.getTextContent();
            let lastY = null;
            let pageText = '';
            textContent.items.forEach(item => {
              if (lastY !== null && Math.abs(item.transform[5] - lastY) > 5) {
                pageText += '\n';
              } else if (pageText.length > 0 && !pageText.endsWith('\n') && !pageText.endsWith(' ')) {
                pageText += ' ';
              }
              pageText += item.str;
              lastY = item.transform[5];
            });
            fullText += pageText + '\n\n';
          }
          const bundle = parseTextToFhirBundle(fullText, file.name);
          renderDashboard(bundle);
          showToast(`Extracted and converted PDF report: ${file.name}`);
        } catch (err) {
          alert('Error extracting text from PDF in browser: ' + err.message + '\n\nYou can also convert using the CLI: python3 scripts/visualize.py path/to/report.pdf');
        }
      } else {
        // Plain text, CSV, markdown, or log files
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const rawText = event.target.result;
            const bundle = parseTextToFhirBundle(rawText, file.name);
            renderDashboard(bundle);
            showToast(`Extracted and converted text report: ${file.name}`);
          } catch (err) {
            alert('Error converting raw text to FHIR: ' + err.message);
          }
        };
        reader.readAsText(file);
      }
    }

    window.addEventListener('dragover', (e) => {
      e.preventDefault();
      document.body.classList.add('drag-active');
    });

    window.addEventListener('dragleave', (e) => {
      if (e.clientX === 0 || e.clientY === 0) {
        document.body.classList.remove('drag-active');
      }
    });

    window.addEventListener('drop', (e) => {
      e.preventDefault();
      document.body.classList.remove('drag-active');
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
        processUploadedFile(e.dataTransfer.files[0]);
      }
    });

    // Preset Sample Bundles
    const SAMPLE_PRESETS = __SAMPLE_PRESETS_JSON__;

    // Initialize with the active report bundle and theme
    window.addEventListener('DOMContentLoaded', () => {
      initTheme();
      renderDashboard(ACTIVE_BUNDLE);
    });
  </script>
</body>
</html>
"""


def load_all_sample_presets() -> Dict[str, Any]:
    """Preloads all 5 sample synthetic reports as converted FHIR bundles."""
    presets = {}
    preset_map = {
        "cancer_positive": "reports/synthetic_cancer_lab_report.pdf",
        "mced_negative": "reports/synthetic_mced_negative.pdf",
        "colorectal_ctdna": "reports/synthetic_colorectal_ctdna.pdf",
        "hereditary_ngs": "reports/synthetic_hereditary_ngs_panel.pdf",
        "prostate_phi": "reports/synthetic_prostate_phi_panel.pdf"
    }
    for key, path in preset_map.items():
        if os.path.exists(path):
            try:
                from src.parser import parse_lab_report_file
                from src.fhir_builder import convert_parsed_data_to_fhir
                data = parse_lab_report_file(path)
                presets[key] = convert_parsed_data_to_fhir(data)
            except Exception:
                pass
    return presets


def generate_html_dashboard(bundle: Dict[str, Any], output_html_path: str = "ui/fhir_viewer.html", sample_presets: Optional[Dict[str, Any]] = None, include_sample_presets: bool = False) -> str:
    """
    Generates a dedicated, report-specific Web UI Dashboard from an extracted HL7 FHIR Bundle.
    
    Args:
        bundle: The extracted and converted FHIR R4 Bundle dictionary for this report.
        output_html_path: Destination path for the generated HTML file.
        sample_presets: Optional dictionary of pre-converted sample bundles for the selector.
        include_sample_presets: Whether to preload all 5 sample bundles if sample_presets is None.
        
    Returns:
        Absolute path to the created HTML file.
    """
    if sample_presets is None and include_sample_presets:
        sample_presets = load_all_sample_presets()

    bundle_json_str = json.dumps(bundle, indent=None)
    presets_json_str = json.dumps(sample_presets or {}, indent=None)
    
    rendered_html = HTML_TEMPLATE.replace("__ACTIVE_BUNDLE_JSON__", bundle_json_str)
    rendered_html = rendered_html.replace("__SAMPLE_PRESETS_JSON__", presets_json_str)

    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    return os.path.abspath(output_html_path)


def open_in_browser(html_path: str):
    """Opens the generated HTML visualizer in the default system web browser."""
    webbrowser.open(f"file://{os.path.abspath(html_path)}")

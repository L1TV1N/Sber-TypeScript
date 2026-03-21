from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

ui_router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
ASSETS_DIR = BASE_DIR / "assets"


def _asset_path(filename: str) -> Path:
    path = ASSETS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Asset not found: {filename}")
    return path


@ui_router.get("/assets/{filename:path}")
def asset_file(filename: str):
    path = _asset_path(filename)
    media_type = None

    suffix = path.suffix.lower()
    if suffix == ".svg":
        media_type = "image/svg+xml"
    elif suffix == ".png":
        media_type = "image/png"
    elif suffix in [".jpg", ".jpeg"]:
        media_type = "image/jpeg"

    return FileResponse(path=str(path), media_type=media_type, filename=path.name)


@ui_router.get("/", response_class=HTMLResponse)
def ui_landing():
    html = """
<!doctype html>
<html lang="ru" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TypeScript Generator</title>
  <style>
    :root {
      --safe-space: 20px;
      --header-h: 86px;
      --radius-xl: 24px;
      --radius-lg: 18px;
      --radius-md: 14px;
      --shadow-lg: 0 20px 50px rgba(0, 0, 0, 0.22);

      --green: #21A038;
      --green-2: #20BB5A;
      --teal: #00A3A6;
      --blue: #007DFF;
      --success: #22C55E;
      --warning: #FBBF24;
      --danger: #FF6B6B;
    }

    html[data-theme="dark"] {
      --bg:
        radial-gradient(circle at 0% 0%, rgba(33,160,56,0.18), transparent 18%),
        radial-gradient(circle at 100% 0%, rgba(0,125,255,0.14), transparent 18%),
        linear-gradient(180deg, #081019 0%, #0B1017 42%, #0C1016 100%);
      --card: rgba(19, 24, 32, 0.92);
      --card-2: rgba(14, 18, 25, 0.96);
      --border: rgba(255,255,255,0.08);
      --border-strong: rgba(255,255,255,0.12);
      --text: #F4F7FB;
      --muted: #AAB5C4;
      --surface: rgba(255,255,255,0.04);
      --surface-2: rgba(255,255,255,0.03);
      --code-bg: linear-gradient(180deg, #0D131B, #0A0F16);
      --code-text: #DCE7F9;
      --logo-bg: rgba(255,255,255,0.03);
      --logo-border: rgba(255,255,255,0.06);
    }

    html[data-theme="light"] {
      --bg:
        radial-gradient(circle at 0% 0%, rgba(33,160,56,0.10), transparent 18%),
        radial-gradient(circle at 100% 0%, rgba(0,125,255,0.08), transparent 18%),
        linear-gradient(180deg, #F4F8F6 0%, #EEF4F8 44%, #EEF2F7 100%);
      --card: rgba(255,255,255,0.92);
      --card-2: rgba(250,252,255,0.96);
      --border: rgba(17,24,39,0.08);
      --border-strong: rgba(17,24,39,0.14);
      --text: #132033;
      --muted: #617084;
      --surface: rgba(17,24,39,0.035);
      --surface-2: rgba(17,24,39,0.03);
      --code-bg: linear-gradient(180deg, #F7FAFF, #F1F6FC);
      --code-text: #0F2138;
      --logo-bg: rgba(17,24,39,0.025);
      --logo-border: rgba(17,24,39,0.06);
      --shadow-lg: 0 16px 40px rgba(17, 24, 39, 0.08);
    }

    * {
      box-sizing: border-box;
    }

    html, body {
      margin: 0;
      min-height: 100%;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, Segoe UI, Arial, sans-serif;
      overflow-x: hidden;
      transition: background 0.25s ease, color 0.25s ease;
    }

    body::before {
      content: "";
      position: fixed;
      inset: auto;
      top: -10vh;
      right: -12vw;
      width: 36vw;
      height: 36vw;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(0,163,166,0.16), transparent 62%);
      filter: blur(28px);
      pointer-events: none;
      z-index: 0;
    }

    .app {
      position: relative;
      z-index: 1;
      max-width: 1440px;
      margin: 0 auto;
      padding: 18px 18px 26px;
    }

    .topbar {
      position: sticky;
      top: 10px;
      z-index: 30;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      min-height: var(--header-h);
      padding: 14px 18px;
      margin-bottom: 16px;
      background: linear-gradient(180deg, var(--card), var(--card-2));
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: var(--shadow-lg);
      backdrop-filter: blur(14px);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 16px;
      min-width: 0;
    }

    .logo-safe-box {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: var(--safe-space);
      border-radius: 18px;
      background: var(--logo-bg);
      border: 1px solid var(--logo-border);
      flex: 0 0 auto;
    }

    .logo-safe-box img {
      display: block;
      width: 176px;
      max-width: 100%;
      height: auto;
    }

    .brand-copy {
      min-width: 0;
    }

    .brand-title {
      margin: 0 0 4px;
      font-size: 26px;
      line-height: 1.06;
      letter-spacing: -0.03em;
    }

    .brand-subtitle {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
      max-width: 720px;
    }

    .topbar-right {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .meta-badge,
    .theme-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      height: 36px;
      padding: 0 12px;
      border-radius: 999px;
      border: 1px solid var(--border-strong);
      background: var(--surface);
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }

    .meta-badge b {
      color: var(--text);
    }

    .theme-btn {
      cursor: pointer;
      transition: 0.18s ease;
    }

    .theme-btn:hover {
      transform: translateY(-1px);
      border-color: rgba(33,160,56,0.28);
    }

    .collapsible-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
      align-items: stretch;
    }

    details.compact-panel {
      border-radius: 20px;
      overflow: hidden;
      background: linear-gradient(180deg, var(--card), var(--card-2));
      border: 1px solid var(--border);
      box-shadow: var(--shadow-lg);
      min-height: 96px;
      height: 96px;
      transition: height 0.22s ease;
    }

    details.compact-panel[open] {
      height: 228px;
    }

    details.compact-panel > summary {
      list-style: none;
      cursor: pointer;
      padding: 14px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      user-select: none;
      height: 96px;
    }

    details.compact-panel > summary::-webkit-details-marker {
      display: none;
    }

    .summary-left {
      display: flex;
      flex-direction: column;
      gap: 4px;
      min-width: 0;
    }

    .summary-title {
      font-size: 15px;
      font-weight: 800;
      line-height: 1.2;
    }

    .summary-subtitle {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }

    .summary-arrow {
      flex: 0 0 auto;
      width: 36px;
      height: 36px;
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: var(--surface);
      border: 1px solid var(--border);
      transition: transform 0.2s ease;
    }

    details[open] .summary-arrow {
      transform: rotate(180deg);
    }

    .panel-content {
      padding: 0 16px 16px;
      border-top: 1px solid var(--border);
      height: calc(228px - 96px);
      overflow-y: auto;
      overflow-x: hidden;
    }

    .panel-content::-webkit-scrollbar {
      width: 8px;
    }

    .panel-content::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,0.14);
      border-radius: 999px;
    }

    .hint-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-top: 14px;
    }

    .hint-chip {
      padding: 11px 12px;
      border-radius: 14px;
      background: var(--surface-2);
      border: 1px solid var(--border);
      min-height: 72px;
    }

    .hint-chip strong {
      display: block;
      margin-bottom: 6px;
      font-size: 12px;
      color: var(--text);
    }

    .hint-chip span {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }

    .assistant-inline {
      display: grid;
      grid-template-columns: 78px 1fr;
      gap: 14px;
      align-items: center;
      margin-top: 14px;
      min-height: 70px;
    }

    .assistant-inline img {
      width: 78px;
      height: 78px;
      object-fit: contain;
      filter: drop-shadow(0 14px 28px rgba(0,0,0,0.2));
      animation: floatCat 4.5s ease-in-out infinite;
    }

    @keyframes floatCat {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-5px); }
    }

    .assistant-note {
      padding: 12px 14px;
      border-radius: 16px;
      background: var(--surface-2);
      border: 1px solid var(--border);
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }

    .assistant-note b {
      color: var(--text);
    }

    .workspace {
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 16px;
      align-items: start;
    }

    .card {
      background: linear-gradient(180deg, var(--card), var(--card-2));
      border: 1px solid var(--border);
      border-radius: 22px;
      box-shadow: var(--shadow-lg);
    }

    .sidebar-card,
    .result-card {
      padding: 18px;
    }

    .panel-title {
      margin: 0 0 6px;
      font-size: 18px;
      line-height: 1.2;
    }

    .panel-subtitle {
      margin: 0 0 16px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }

    .field {
      margin-bottom: 14px;
    }

    .field label {
      display: block;
      margin-bottom: 8px;
      font-size: 13px;
      font-weight: 800;
    }

    .field small {
      display: block;
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }

    .file-zone {
      border-radius: 16px;
      padding: 14px;
      background: linear-gradient(180deg, var(--surface), var(--surface-2));
      border: 1px dashed var(--border-strong);
      transition: 0.2s ease;
    }

    .file-zone:hover {
      border-color: rgba(33,160,56,0.38);
      box-shadow: 0 0 0 1px rgba(33,160,56,0.12) inset;
    }

    input[type="file"] {
      display: block;
      width: 100%;
      color: var(--text);
      font-size: 13px;
    }

    input[type="file"]::file-selector-button {
      margin-right: 12px;
      border: 0;
      border-radius: 12px;
      padding: 10px 14px;
      background: linear-gradient(135deg, rgba(33,160,56,0.25), rgba(0,125,255,0.18));
      color: white;
      cursor: pointer;
      font-weight: 800;
    }

    .main-action {
      width: 100%;
      border: 0;
      border-radius: 16px;
      padding: 14px 16px;
      font-size: 15px;
      font-weight: 800;
      cursor: pointer;
      color: white;
      background: linear-gradient(135deg, var(--green), var(--teal));
      box-shadow: 0 10px 24px rgba(33,160,56,0.18);
      transition: transform 0.18s ease, opacity 0.18s ease;
      margin-top: 4px;
    }

    .main-action:hover {
      transform: translateY(-1px);
    }

    .main-action:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    .status {
      margin-top: 16px;
      padding: 14px 15px;
      border-radius: 16px;
      border: 1px solid var(--border);
      background: var(--surface-2);
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
      white-space: pre-wrap;
    }

    .status.ok {
      border-color: rgba(34,197,94,0.28);
      background: rgba(34,197,94,0.08);
      color: #D9FFE9;
    }

    .status.error {
      border-color: rgba(255,107,107,0.28);
      background: rgba(255,107,107,0.08);
      color: #FFE6E6;
    }

    .status.warning {
      border-color: rgba(251,191,36,0.28);
      background: rgba(251,191,36,0.08);
      color: #FFF1C9;
    }

    .team-sign {
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px solid var(--border);
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }

    .team-sign b {
      color: var(--text);
    }

    .result-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 14px;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }

    .result-meta {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 12px;
      border-radius: 999px;
      background: var(--surface);
      border: 1px solid var(--border);
      font-size: 12px;
      font-weight: 800;
      color: var(--muted);
    }

    .badge.ok {
      background: rgba(34,197,94,0.08);
      border-color: rgba(34,197,94,0.24);
      color: #D8FFE8;
    }

    .badge.warning {
      background: rgba(251,191,36,0.08);
      border-color: rgba(251,191,36,0.24);
      color: #FFF0C3;
    }

    .code-frame {
      border-radius: 18px;
      overflow: hidden;
      background: var(--code-bg);
      border: 1px solid var(--border);
    }

    .code-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--border);
      background: linear-gradient(180deg, var(--surface), var(--surface-2));
      flex-wrap: wrap;
    }

    .traffic {
      display: flex;
      gap: 8px;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }

    .dot.red { background: #FF5F57; }
    .dot.yellow { background: #FEBC2E; }
    .dot.green { background: #28C840; }

    .toolbar-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .toolbar-btn {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 9px 12px;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      transition: 0.18s ease;
      background: var(--surface);
      color: var(--text);
    }

    .toolbar-btn.primary {
      background: linear-gradient(135deg, rgba(33,160,56,0.22), rgba(0,163,166,0.20));
      color: white;
    }

    .toolbar-btn:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }

    pre {
      margin: 0;
      padding: 18px 20px 22px;
      min-height: 68vh;
      max-height: 75vh;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      color: var(--code-text);
      font-size: 13px;
      line-height: 1.56;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }

    details.output-panel {
      margin-top: 12px;
      border-radius: 16px;
      overflow: hidden;
      background: var(--surface-2);
      border: 1px solid var(--border);
    }

    details.output-panel > summary {
      cursor: pointer;
      list-style: none;
      padding: 13px 14px;
      font-size: 13px;
      font-weight: 800;
    }

    details.output-panel > summary::-webkit-details-marker {
      display: none;
    }

    .details-body {
      padding: 0 14px 14px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.55;
      white-space: pre-wrap;
      word-break: break-word;
      max-height: 220px;
      overflow: auto;
    }

    @media (max-width: 1160px) {
      .workspace {
        grid-template-columns: 1fr;
      }

      .collapsible-row {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 900px) {
      .topbar {
        align-items: flex-start;
        flex-direction: column;
      }

      .brand {
        width: 100%;
      }

      .topbar-right {
        width: 100%;
        justify-content: flex-start;
      }

      .hint-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      details.compact-panel,
      details.compact-panel[open] {
        height: auto;
        min-height: 96px;
      }

      .panel-content {
        height: auto;
        overflow: visible;
      }
    }

    @media (max-width: 640px) {
      .app {
        padding: 12px;
      }

      .brand-title {
        font-size: 21px;
      }

      .logo-safe-box img {
        width: 150px;
      }

      .hint-grid {
        grid-template-columns: 1fr;
      }

      pre {
        min-height: 54vh;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <header class="topbar">
      <div class="brand">
        <div class="logo-safe-box" aria-label="Логотип Сбер Банка">
          <img src="/assets/%D0%A1%D0%91%D0%95%D0%A0_%D0%91%D0%90%D0%9D%D0%9A_%D0%B3%D1%80%D0%B0%D0%B4%D0%B8%D0%B5%D0%BD%D1%82.svg" alt="Сбер Банк" />
        </div>

        <div class="brand-copy">
          <h1 class="brand-title">TypeScript Generator</h1>
          <p class="brand-subtitle">
            Загрузка исходного файла и JSON-примера с генерацией TypeScript-кода под целевую структуру.
          </p>
        </div>
      </div>

      <div class="topbar-right">
        <div class="meta-badge">by <b>CyberPink228</b></div>
        <button id="themeBtn" class="theme-btn" type="button" aria-label="Переключить тему">☀️ Светлая тема</button>
      </div>
    </header>

    <section class="collapsible-row">
      <details class="compact-panel">
        <summary>
          <div class="summary-left">
            <span class="summary-title">О проекте</span>
            <span class="summary-subtitle">
              Краткое описание сценария и быстрый путь для защиты решения.
            </span>
          </div>
          <div class="summary-arrow">⌃</div>
        </summary>

        <div class="panel-content">
          <div class="hint-grid">
            <div class="hint-chip">
              <strong>Вход</strong>
              <span>crmData.csv и crm.json</span>
            </div>
            <div class="hint-chip">
              <strong>Выход</strong>
              <span>TypeScript-конвертер</span>
            </div>
            <div class="hint-chip">
              <strong>Backend</strong>
              <span>/api/v1/prediction</span>
            </div>
            <div class="hint-chip">
              <strong>Команда</strong>
              <span>CyberPink228</span>
            </div>
          </div>
        </div>
      </details>

      <details class="compact-panel">
        <summary>
          <div class="summary-left">
            <span class="summary-title">Подсказка от СберКота</span>
            <span class="summary-subtitle">
              Быстрый сценарий демо без лишних действий.
            </span>
          </div>
          <div class="summary-arrow">⌃</div>
        </summary>

        <div class="panel-content">
          <div class="assistant-inline">
            <img src="/assets/image%201699%201.svg" alt="СберКот" />
            <div class="assistant-note">
              <b>Шаги:</b> загрузи <b>crmData.csv</b>, затем <b>crm.json</b>, нажми
              <b>«Сгенерировать TypeScript»</b>, после чего проверь код и скачай
              <b>generated_converter.ts</b>.
            </div>
          </div>
        </div>
      </details>
    </section>

    <section class="workspace">
      <aside class="card sidebar-card">
        <h2 class="panel-title">Входные данные</h2>
        <p class="panel-subtitle">
          Загружаем исходный файл и пример JSON, на выходе получаем TypeScript-код преобразования.
        </p>

        <div class="field">
          <label for="csvFile">Файл с табличными данными</label>
          <div class="file-zone">
            <input id="csvFile" type="file" accept=".csv,.xls,.xlsx,.pdf,.docx,.png,.jpg,.jpeg" />
          </div>
          <small>Рекомендуется использовать <b>crmData.csv</b>.</small>
        </div>

        <div class="field">
          <label for="jsonFile">Пример целевого JSON</label>
          <div class="file-zone">
            <input id="jsonFile" type="file" accept=".json" />
          </div>
          <small>Рекомендуется использовать <b>crm.json</b>.</small>
        </div>

        <button id="generateBtn" class="main-action">Сгенерировать TypeScript</button>

        <div id="status" class="status">Готов к генерации.</div>

        <div class="team-sign">
          Сделано командой <b>CyberPink228</b>
        </div>
      </aside>

      <main class="card result-card">
        <div class="result-head">
          <div>
            <h2 class="panel-title">Сгенерированный TypeScript</h2>
            <p class="panel-subtitle" style="margin-bottom: 0;">
              Основной результат. Все действия с кодом собраны в одном месте без дублирования.
            </p>
          </div>

          <div class="result-meta">
            <div id="validBadge" class="badge">Ожидание генерации</div>
            <div class="badge">CyberPink228</div>
          </div>
        </div>

        <div class="code-frame">
          <div class="code-toolbar">
            <div class="traffic">
              <span class="dot red"></span>
              <span class="dot yellow"></span>
              <span class="dot green"></span>
            </div>

            <div class="toolbar-actions">
              <button id="copyBtn" class="toolbar-btn" disabled>Скопировать</button>
              <button id="downloadBtn" class="toolbar-btn primary" disabled>Скачать TS</button>
              <button id="clearBtn" class="toolbar-btn" type="button">Очистить</button>
            </div>
          </div>

          <pre id="codeOutput">// Здесь появится TypeScript-код</pre>
        </div>

        <details class="output-panel">
          <summary>Показать extracted preview</summary>
          <div id="previewOutput" class="details-body">Пока пусто.</div>
        </details>

        <details class="output-panel">
          <summary>Показать raw LLM response</summary>
          <div id="rawOutput" class="details-body">Пока пусто.</div>
        </details>
      </main>
    </section>
  </div>

  <script>
    const htmlEl = document.documentElement;
    const csvFileInput = document.getElementById("csvFile");
    const jsonFileInput = document.getElementById("jsonFile");
    const generateBtn = document.getElementById("generateBtn");
    const downloadBtn = document.getElementById("downloadBtn");
    const copyBtn = document.getElementById("copyBtn");
    const clearBtn = document.getElementById("clearBtn");
    const statusEl = document.getElementById("status");
    const codeOutput = document.getElementById("codeOutput");
    const previewOutput = document.getElementById("previewOutput");
    const rawOutput = document.getElementById("rawOutput");
    const validBadge = document.getElementById("validBadge");
    const themeBtn = document.getElementById("themeBtn");

    let latestCode = "";

    function setStatus(message, kind = "") {
      statusEl.className = "status" + (kind ? " " + kind : "");
      statusEl.textContent = message;
    }

    function setBadge(message, kind = "") {
      validBadge.className = "badge" + (kind ? " " + kind : "");
      validBadge.textContent = message;
    }

    function toggleCodeActions(enabled) {
      copyBtn.disabled = !enabled;
      downloadBtn.disabled = !enabled;
    }

    function readFileAsText(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result));
        reader.onerror = reject;
        reader.readAsText(file, "utf-8");
      });
    }

    function readFileAsBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const result = String(reader.result);
          const base64 = result.split(",")[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    }

    function applyTheme(theme) {
      htmlEl.setAttribute("data-theme", theme);
      localStorage.setItem("ui-theme", theme);
      themeBtn.textContent = theme === "dark" ? "☀️ Светлая тема" : "🌙 Тёмная тема";
    }

    async function generate() {
      const csvFile = csvFileInput.files[0];
      const jsonFile = jsonFileInput.files[0];

      if (!csvFile) {
        setStatus("Выбери файл с табличными данными.", "error");
        return;
      }

      if (!jsonFile) {
        setStatus("Выбери JSON-файл с примером целевой структуры.", "error");
        return;
      }

      generateBtn.disabled = true;
      toggleCodeActions(false);
      latestCode = "";

      codeOutput.textContent = "// Генерация...";
      previewOutput.textContent = "Загрузка...";
      rawOutput.textContent = "Загрузка...";
      setBadge("Идёт генерация");
      setStatus("Считываю файлы и отправляю запрос в backend...");

      try {
        const [fileBase64, targetJsonText] = await Promise.all([
          readFileAsBase64(csvFile),
          readFileAsText(jsonFile),
        ]);

        const payload = {
          file_name: csvFile.name,
          file_base64: fileBase64,
          target_json_example: targetJsonText,
        };

        const response = await fetch("/api/v1/prediction", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || "Ошибка backend");
        }

        latestCode = data.content || "";
        codeOutput.textContent = latestCode || "// Пустой ответ";
        previewOutput.textContent = data.extracted_preview || "Нет preview";
        rawOutput.textContent = data.raw_content || "Нет raw ответа";

        if (data.valid_ts) {
          setBadge("TS похож на валидный", "ok");
          setStatus("TypeScript-код успешно сгенерирован.", "ok");
        } else {
          setBadge("Нужна проверка", "warning");
          setStatus("Код получен, но его лучше проверить вручную.", "warning");
        }

        toggleCodeActions(Boolean(latestCode));
      } catch (error) {
        console.error(error);
        codeOutput.textContent = "// Ошибка генерации";
        previewOutput.textContent = "Ошибка";
        rawOutput.textContent = String(error);
        setBadge("Ошибка", "warning");
        setStatus("Ошибка: " + error.message, "error");
      } finally {
        generateBtn.disabled = false;
      }
    }

    function downloadTs() {
      if (!latestCode) return;

      const blob = new Blob([latestCode], { type: "text/typescript;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "generated_converter.ts";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    }

    async function copyCode() {
      if (!latestCode) return;

      try {
        await navigator.clipboard.writeText(latestCode);
        setStatus("Код скопирован в буфер обмена.", "ok");
      } catch (error) {
        setStatus("Не удалось скопировать код: " + error.message, "error");
      }
    }

    function clearAll() {
      csvFileInput.value = "";
      jsonFileInput.value = "";
      latestCode = "";
      codeOutput.textContent = "// Здесь появится TypeScript-код";
      previewOutput.textContent = "Пока пусто.";
      rawOutput.textContent = "Пока пусто.";
      toggleCodeActions(false);
      setBadge("Ожидание генерации");
      setStatus("Готов к генерации.");
    }

    generateBtn.addEventListener("click", generate);
    downloadBtn.addEventListener("click", downloadTs);
    copyBtn.addEventListener("click", copyCode);
    clearBtn.addEventListener("click", clearAll);
    themeBtn.addEventListener("click", () => {
      const next = htmlEl.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
    });

    const savedTheme = localStorage.getItem("ui-theme");
    applyTheme(savedTheme === "light" ? "light" : "dark");
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html)
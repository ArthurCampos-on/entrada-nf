"""
dashboard.py
------------
Servidor Flask com dashboard dark-mode completo e controlável.
Acesse: http://localhost:8080
"""

import threading
from typing import Optional

try:
    from flask import Flask, render_template_string, jsonify, request
    from flask_cors import CORS
except ImportError:
    raise ImportError("Execute: pip install flask flask-cors")

from src.rastreador import Rastreador
from src.logger import log

_HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agent de Notas — Monitor</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg0:#0d1117;--bg1:#161b22;--bg2:#21262d;--bg3:#2d333b;
  --border:#30363d;--border2:#444c56;
  --txt1:#e6edf3;--txt2:#8b949e;--txt3:#6e7681;
  --blue:#58a6ff;--blue2:#1f6feb;
  --green:#3fb950;--red:#f85149;--yellow:#e3b341;--purple:#bc8cff;
  --sw:220px;--swc:64px;--hh:60px;
}
body{font-family:'Inter',system-ui,sans-serif;background:var(--bg0);color:var(--txt1);min-height:100vh;font-size:14px;line-height:1.5}

/* ── Sidebar ── */
.sb{position:fixed;top:0;left:0;bottom:0;width:var(--sw);background:var(--bg1);border-right:1px solid var(--border);display:flex;flex-direction:column;transition:width .25s;z-index:100;overflow:hidden}
.sb.col{width:var(--swc)}
.sb-logo{display:flex;align-items:center;gap:12px;padding:18px 20px;border-bottom:1px solid var(--border);min-height:var(--hh);white-space:nowrap;overflow:hidden}
.sb-logo svg{flex-shrink:0;width:24px;height:24px}
.logo-t{font-size:15px;font-weight:600;color:var(--txt1);letter-spacing:-.3px}
.logo-s{font-size:11px;color:var(--txt2);margin-top:1px}
.nav{flex:1;padding:12px 0;overflow-y:auto;overflow-x:hidden}
.ni{display:flex;align-items:center;gap:12px;padding:10px 20px;color:var(--txt2);cursor:pointer;transition:all .15s;white-space:nowrap;position:relative;text-decoration:none}
.ni:hover{color:var(--txt1);background:var(--bg2)}
.ni.act{color:var(--blue);background:rgba(88,166,255,.08)}
.ni.act::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--blue);border-radius:0 2px 2px 0}
.ni svg{flex-shrink:0;width:18px;height:18px}
.ni-lbl{font-size:13.5px;font-weight:500}
.sb.col .ni-lbl,.sb.col .logo-t,.sb.col .logo-s,.sb.col .ns{display:none}
.sb.col .ni{justify-content:center;padding:10px}
.ns{font-size:10.5px;font-weight:600;letter-spacing:.8px;text-transform:uppercase;color:var(--txt3);padding:16px 20px 6px;white-space:nowrap}
.sb-tog{display:flex;align-items:center;justify-content:center;padding:14px;border-top:1px solid var(--border);cursor:pointer;color:var(--txt3);transition:color .15s}
.sb-tog:hover{color:var(--txt1)}

/* ── Main ── */
.main{margin-left:var(--sw);transition:margin-left .25s;display:flex;flex-direction:column;min-height:100vh}
.main.col{margin-left:var(--swc)}

/* ── Topbar ── */
.topbar{height:var(--hh);display:flex;align-items:center;justify-content:space-between;padding:0 28px;border-bottom:1px solid var(--border);background:var(--bg0);position:sticky;top:0;z-index:90}
.page-title{font-size:16px;font-weight:600}
.tb-r{display:flex;align-items:center;gap:12px}
.pill{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--green);background:rgba(63,185,80,.1);border:1px solid rgba(63,185,80,.25);border-radius:20px;padding:5px 12px}
.pulse{width:7px;height:7px;border-radius:50%;background:var(--green);animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.85)}}
.upd-btn{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--txt2);background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:6px 12px;cursor:pointer;transition:all .15s;font-family:inherit}
.upd-btn:hover{color:var(--txt1);border-color:var(--border2)}
.upd-btn svg{width:14px;height:14px}
.upd-btn.spin svg{animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── Content ── */
.content{flex:1;padding:28px;display:flex;flex-direction:column;gap:28px}
.page{display:none}
.page.act{display:flex;flex-direction:column;gap:24px}

/* ── Stats ── */
.sgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}
.sc{background:var(--bg1);border:1px solid var(--border);border-radius:12px;padding:20px 22px;position:relative;overflow:hidden;transition:border-color .2s}
.sc::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--ac,var(--blue));opacity:.7}
.sc:hover{border-color:var(--border2)}
.si{width:36px;height:36px;border-radius:9px;display:flex;align-items:center;justify-content:center;background:var(--ab,rgba(88,166,255,.12));margin-bottom:14px}
.si svg{width:18px;height:18px;color:var(--ac,var(--blue))}
.sl{font-size:11.5px;color:var(--txt2);font-weight:500;letter-spacing:.3px;margin-bottom:6px}
.sv{font-size:26px;font-weight:600;font-family:'JetBrains Mono',monospace;letter-spacing:-1px;line-height:1}
.su{font-size:11.5px;color:var(--txt3);margin-top:6px}
.sfx{font-size:14px;font-weight:400;color:var(--txt2);margin-left:3px}

/* ── Section header ── */
.sh{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.st{display:flex;align-items:center;gap:9px;font-size:14px;font-weight:600}
.st svg{width:16px;height:16px;color:var(--blue)}
.sbadge{font-size:11px;font-weight:500;background:var(--bg2);border:1px solid var(--border);border-radius:20px;padding:2px 9px;color:var(--txt2)}

/* ── Chart ── */
.cc{background:var(--bg1);border:1px solid var(--border);border-radius:12px;padding:22px 24px}
.cw{position:relative;height:220px}

/* ── Table ── */
.tc{background:var(--bg1);border:1px solid var(--border);border-radius:12px;overflow:hidden}
.tsearch{padding:14px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px}
.sinput{flex:1;background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:7px 12px;color:var(--txt1);font-family:inherit;font-size:13px;outline:none;transition:border-color .15s}
.sinput::placeholder{color:var(--txt3)}
.sinput:focus{border-color:var(--blue)}
.tbl{width:100%;border-collapse:collapse;font-size:13px}
.tbl th{padding:10px 16px;text-align:left;font-size:11px;font-weight:600;letter-spacing:.5px;color:var(--txt3);text-transform:uppercase;background:var(--bg2);border-bottom:1px solid var(--border)}
.tbl td{padding:11px 16px;border-bottom:1px solid rgba(48,54,61,.6);vertical-align:middle}
.tbl tr:last-child td{border-bottom:none}
.tbl tr:hover td{background:rgba(255,255,255,.02)}
.badge{display:inline-flex;align-items:center;gap:5px;font-size:11.5px;font-weight:500;border-radius:6px;padding:3px 9px}
.bd{width:6px;height:6px;border-radius:50%;background:currentColor;flex-shrink:0}
.b-relatorio{background:rgba(88,166,255,.12);color:#58a6ff}
.b-fabrica{background:rgba(63,185,80,.12);color:#3fb950}
.b-transferencia{background:rgba(227,179,65,.12);color:#e3b341}
.b-entrada_cte{background:rgba(248,81,73,.12);color:#f85149}
.b-sucesso{background:rgba(63,185,80,.12);color:#3fb950}
.b-parcial{background:rgba(227,179,65,.12);color:#e3b341}
.b-falha{background:rgba(248,81,73,.12);color:#f85149}
.mono{font-family:'JetBrains Mono',monospace;font-size:12.5px;color:var(--txt2)}
.dur{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--blue)}

/* ── Notas ── */
.dia-card{background:var(--bg1);border:1px solid var(--border);border-radius:12px;overflow:hidden}
.dia-h{display:flex;align-items:center;justify-content:space-between;padding:13px 18px;background:var(--bg2);border-bottom:1px solid var(--border);cursor:pointer;transition:background .15s}
.dia-h:hover{background:var(--bg3)}
.dia-ht{display:flex;align-items:center;gap:9px;font-size:13px;font-weight:600}
.dia-ht svg{width:15px;height:15px;color:var(--blue)}
.dia-cnt{font-size:12px;color:var(--txt2)}
.chev{transition:transform .2s;color:var(--txt3)}
.chev.open{transform:rotate(180deg)}
.dia-b{padding:16px 18px;display:grid;gap:12px}
.tipo-row{display:flex;align-items:flex-start;gap:10px}
.nchips{display:flex;flex-wrap:wrap;gap:6px}
.nchip{font-family:'JetBrains Mono',monospace;font-size:11.5px;font-weight:500;background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:4px 9px;color:var(--txt2);transition:all .15s;cursor:default}
.nchip:hover{border-color:var(--blue);color:var(--blue);background:rgba(88,166,255,.06)}

/* ── Menu ── */
.mgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.mitem{background:var(--bg1);border:1px solid var(--border);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:10px;transition:all .2s}
.mitem:hover{border-color:var(--blue);background:rgba(88,166,255,.04);transform:translateY(-2px)}
.micon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center}
.micon svg{width:20px;height:20px}
.mname{font-size:13.5px;font-weight:600}
.mdesc{font-size:12px;color:var(--txt2);line-height:1.4}
.mshort{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--txt3);background:var(--bg2);border:1px solid var(--border);border-radius:5px;padding:2px 7px;width:fit-content}

/* ── CONTROLE ── */
.rpa-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.rpa-btn{background:var(--bg1);border:2px solid var(--border);border-radius:12px;padding:18px 14px;cursor:pointer;transition:all .2s;text-align:center;user-select:none}
.rpa-btn:hover{border-color:var(--border2);transform:translateY(-2px)}
.rpa-btn.sel{border-color:var(--sel-c,var(--blue));background:var(--sel-bg,rgba(88,166,255,.08))}
.rpa-ic{width:44px;height:44px;border-radius:11px;display:flex;align-items:center;justify-content:center;margin:0 auto 12px}
.rpa-ic svg{width:22px;height:22px}
.rpa-nm{font-size:13px;font-weight:600;color:var(--txt1)}
.rpa-ds{font-size:11px;color:var(--txt2);margin-top:4px;line-height:1.4}

.exec-box{background:var(--bg1);border:1px solid var(--border);border-radius:12px;padding:22px}
.exec-label{font-size:12px;font-weight:600;color:var(--txt2);letter-spacing:.3px;text-transform:uppercase;margin-bottom:8px}
.exec-input{width:100%;background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:11px 14px;color:var(--txt1);font-family:'JetBrains Mono',monospace;font-size:13.5px;outline:none;transition:border-color .15s}
.exec-input:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(88,166,255,.12)}
.exec-input::placeholder{color:var(--txt3);font-family:'Inter',sans-serif}
.exec-btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:13px;background:var(--blue);color:#fff;border:none;border-radius:9px;font-size:14px;font-weight:600;cursor:pointer;transition:all .2s;margin-top:14px;font-family:inherit;letter-spacing:.2px}
.exec-btn:hover:not(:disabled){background:#388bfd;transform:translateY(-1px);box-shadow:0 4px 12px rgba(88,166,255,.3)}
.exec-btn:disabled{background:var(--bg3);color:var(--txt3);cursor:not-allowed;transform:none;box-shadow:none}
.exec-btn svg{width:16px;height:16px}
.exec-btn.running{background:var(--red)}
.exec-btn.running:hover{background:#e03e38}

.status-bar{background:var(--bg1);border:1px solid var(--border);border-radius:10px;padding:14px 18px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.sb-left{display:flex;align-items:center;gap:10px}
.sdot{width:9px;height:9px;border-radius:50%;flex-shrink:0;transition:background .3s}
.sdot.idle{background:var(--txt3)}
.sdot.running{background:var(--blue);animation:pulse 1.2s infinite}
.sdot.paused{background:var(--yellow);animation:pulse .8s infinite}
.sdot.error{background:var(--red)}
.sdot.success{background:var(--green)}
.sb-txt{font-size:13px;font-weight:500;color:var(--txt1)}
.sb-sub{font-size:12px;color:var(--txt2)}
.sb-ts{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--txt3)}

.log-view{background:#010409;border:1px solid var(--border);border-radius:10px;padding:14px 16px;height:300px;overflow-y:auto;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7}
.ll{display:flex;gap:10px;border-bottom:1px solid rgba(48,54,61,.3);padding:3px 0}
.ll:last-child{border-bottom:none}
.ll-ts{color:var(--txt3);flex-shrink:0;width:58px}
.ll-msg{}
.ll .INFO{color:var(--txt2)}
.ll .SUCCESS{color:var(--green)}
.ll .ERROR{color:var(--red)}
.ll .WARNING{color:var(--yellow)}
.ll .PAUSE{color:var(--purple)}
.ll .CRITICAL{color:var(--red)}
.log-empty{color:var(--txt3);text-align:center;padding:40px 0;font-family:'Inter',sans-serif;font-size:13px}

/* ── Modal de pausa ── */
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.8);display:flex;align-items:center;justify-content:center;z-index:999;padding:20px;backdrop-filter:blur(4px)}
.modal-box{background:var(--bg1);border:1px solid var(--border2);border-radius:16px;padding:30px;width:100%;max-width:420px;box-shadow:0 24px 48px rgba(0,0,0,.5);animation:fadeIn .2s ease}
@keyframes fadeIn{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:scale(1)}}
.modal-icon{width:48px;height:48px;background:rgba(188,140,255,.12);border-radius:12px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px}
.modal-icon svg{width:24px;height:24px;color:var(--purple)}
.modal-titulo{font-size:15px;font-weight:600;color:var(--txt1);text-align:center;margin-bottom:6px}
.modal-sub{font-size:12.5px;color:var(--txt2);text-align:center;margin-bottom:22px}
.modal-opts{display:flex;flex-direction:column;gap:10px}
.modal-btn{padding:13px 16px;border-radius:9px;font-size:13.5px;font-weight:500;cursor:pointer;border:1px solid var(--border);background:var(--bg2);color:var(--txt1);font-family:inherit;transition:all .15s;text-align:left;display:flex;align-items:center;gap:10px}
.modal-btn:hover{background:var(--bg3);border-color:var(--border2);color:var(--blue)}
.modal-btn svg{width:16px;height:16px;flex-shrink:0;opacity:.6}

/* ── Empty ── */
.empty{text-align:center;padding:48px 20px;color:var(--txt3)}
.empty svg{width:40px;height:40px;margin:0 auto 14px;display:block;opacity:.4}
.empty p{font-size:13px}

/* ── Footer ── */
footer{border-top:1px solid var(--border);padding:14px 28px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.fcopy{font-size:11.5px;color:var(--txt3)}
.fver{font-size:11px;font-family:'JetBrains Mono',monospace;color:var(--txt3);background:var(--bg2);border:1px solid var(--border);border-radius:5px;padding:2px 8px}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--border2)}

/* ── Responsive ── */
@media(max-width:768px){
  .sb{width:var(--swc)}
  .sb .ni-lbl,.sb .logo-t,.sb .logo-s,.sb .ns{display:none}
  .sb .ni{justify-content:center;padding:10px}
  .main{margin-left:var(--swc)}
  .content{padding:16px}
  .sgrid{grid-template-columns:1fr 1fr}
  .tbl th:nth-child(3),.tbl td:nth-child(3){display:none}
  .rpa-grid{grid-template-columns:1fr 1fr}
  .log-view{height:220px}
}
@media(max-width:480px){
  .sgrid{grid-template-columns:1fr 1fr}
  .sv{font-size:22px}
  .rpa-grid{grid-template-columns:1fr 1fr}
  .content{padding:12px}
  .exec-btn{font-size:13px}
}
</style>
</head>
<body>

<!-- Sidebar -->
<aside class="sb" id="sb">
  <div class="sb-logo">
    <svg viewBox="0 0 24 24" fill="none" stroke="#58a6ff" stroke-width="1.8" stroke-linecap="round">
      <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>
    </svg>
    <div><div class="logo-t">NBS Agent</div><div class="logo-s">Monitor de automações</div></div>
  </div>
  <nav class="nav">
    <div class="ns">Principal</div>
    <a class="ni act" onclick="goPage('overview',this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
      <span class="ni-lbl">Visão Geral</span>
    </a>
    <a class="ni" onclick="goPage('controle',this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07M8.46 8.46a5 5 0 0 0 0 7.07"/></svg>
      <span class="ni-lbl">Controle</span>
    </a>
    <a class="ni" onclick="goPage('execucoes',this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
      <span class="ni-lbl">Execuções</span>
    </a>
    <a class="ni" onclick="goPage('notas',this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
      <span class="ni-lbl">Notas</span>
    </a>
    <div class="ns">Sistema</div>
    <a class="ni" onclick="goPage('menu',this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      <span class="ni-lbl">Menu RPA</span>
    </a>
  </nav>
  <div class="sb-tog" onclick="toggleSb()" title="Colapsar">
    <svg id="tog-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" style="width:16px;height:16px">
      <polyline points="15 18 9 12 15 6"/><polyline points="9 18 3 12 9 6"/>
    </svg>
  </div>
</aside>

<!-- Main -->
<div class="main" id="main">
  <header class="topbar">
    <span class="page-title" id="ptitle">Visão Geral</span>
    <div class="tb-r">
      <div class="pill"><div class="pulse"></div>Online</div>
      <button class="upd-btn" id="rbtn" onclick="refreshAll()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
        Atualizar
      </button>
    </div>
  </header>

  <div class="content">

    <!-- ── VISÃO GERAL ── -->
    <div class="page act" id="page-overview">
      <div class="sgrid">
        <div class="sc" style="--ac:#58a6ff;--ab:rgba(88,166,255,.1)">
          <div class="si"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
          <div class="sl">Total de Execuções</div>
          <div class="sv" id="s-total">—</div>
          <div class="su" id="s-total-u">carregando...</div>
        </div>
        <div class="sc" style="--ac:#3fb950;--ab:rgba(63,185,80,.1)">
          <div class="si"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg></div>
          <div class="sl">Taxa de Sucesso</div>
          <div class="sv" id="s-taxa">—<span class="sfx">%</span></div>
          <div class="su" id="s-taxa-u">carregando...</div>
        </div>
        <div class="sc" style="--ac:#e3b341;--ab:rgba(227,179,65,.1)">
          <div class="si"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
          <div class="sl">Tempo Médio Geral</div>
          <div class="sv" id="s-tempo">—<span class="sfx">s</span></div>
          <div class="su" id="s-tempo-u">carregando...</div>
        </div>
        <div class="sc" style="--ac:#bc8cff;--ab:rgba(188,140,255,.1)">
          <div class="si"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
          <div class="sl">Última Execução</div>
          <div class="sv" id="s-ult" style="font-size:15px;letter-spacing:0;font-weight:500">—</div>
          <div class="su" id="s-ult-u">—</div>
        </div>
      </div>
      <div class="cc">
        <div class="sh">
          <div class="st"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>Tempo médio por RPA</div>
          <span class="sbadge" id="ch-badge">—</span>
        </div>
        <div class="cw"><canvas id="chart-tempo"></canvas></div>
      </div>
      <div>
        <div class="sh">
          <div class="st"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>Execuções recentes</div>
          <span class="sbadge" id="ov-badge">—</span>
        </div>
        <div class="tc"><div id="ov-tbl"></div></div>
      </div>
    </div>

    <!-- ── CONTROLE ── -->
    <div class="page" id="page-controle">

      <!-- Seleção de RPA -->
      <div>
        <div class="sh">
          <div class="st"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>Selecione a automação</div>
        </div>
        <div class="rpa-grid">
          <div class="rpa-btn" data-tipo="fabrica" style="--sel-c:#3fb950;--sel-bg:rgba(63,185,80,.08)" onclick="selecionarRPA('fabrica',this)">
            <div class="rpa-ic" style="background:rgba(63,185,80,.12)"><svg style="color:#3fb950" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg></div>
            <div class="rpa-nm">Fábrica</div>
            <div class="rpa-ds">Lançamento de notas de fábrica</div>
          </div>
          <div class="rpa-btn" data-tipo="transferencia" style="--sel-c:#e3b341;--sel-bg:rgba(227,179,65,.08)" onclick="selecionarRPA('transferencia',this)">
            <div class="rpa-ic" style="background:rgba(227,179,65,.12)"><svg style="color:#e3b341" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="1" y="3" width="15" height="13" rx="1"/><path d="M16 8l4 2v4"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg></div>
            <div class="rpa-nm">Transferência</div>
            <div class="rpa-ds">Lançamento de notas de transferência</div>
          </div>
          <div class="rpa-btn" data-tipo="entrada_cte" style="--sel-c:#f85149;--sel-bg:rgba(248,81,73,.08)" onclick="selecionarRPA('entrada_cte',this)">
            <div class="rpa-ic" style="background:rgba(248,81,73,.12)"><svg style="color:#f85149" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg></div>
            <div class="rpa-nm">Entrada CT-e</div>
            <div class="rpa-ds">Entrada de notas fiscais CT-e</div>
          </div>
          <div class="rpa-btn" data-tipo="relatorio" style="--sel-c:#58a6ff;--sel-bg:rgba(88,166,255,.08)" onclick="selecionarRPA('relatorio',this)">
            <div class="rpa-ic" style="background:rgba(88,166,255,.12)"><svg style="color:#58a6ff" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 3h18v18H3z"/><path d="M3 9h18M3 15h18M9 3v18"/></svg></div>
            <div class="rpa-nm">Relatório</div>
            <div class="rpa-ds">Gera relatório diário de compras</div>
          </div>
        </div>
      </div>

      <!-- Input + Executar -->
      <div class="exec-box">
        <div id="input-notas">
          <div class="exec-label">Números das notas</div>
          <input id="inp-notas" class="exec-input" type="text" placeholder="123456, 234567, 345678  (separadas por vírgula)">
        </div>
        <div id="input-qtd" style="display:none">
          <div class="exec-label">Quantidade de notas CT-e</div>
          <input id="inp-qtd" class="exec-input" type="number" min="1" max="50" value="1">
        </div>
        <div id="input-relatorio" style="display:none">
          <div class="exec-label">Relatório diário</div>
          <div style="font-size:13px;color:var(--txt2);padding:10px 0">Gera o relatório de compras do dia anterior automaticamente. Nenhum campo necessário.</div>
        </div>
        <button class="exec-btn" id="exec-btn" onclick="executar()" disabled>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          Selecione uma automação
        </button>
      </div>

      <!-- Status -->
      <div class="status-bar" id="ctrl-status-bar">
        <div class="sb-left">
          <div class="sdot idle" id="sdot"></div>
          <div>
            <div class="sb-txt" id="sb-txt">Aguardando</div>
            <div class="sb-sub" id="sb-sub">Nenhuma automação em execução</div>
          </div>
        </div>
        <div class="sb-ts" id="sb-ts">—</div>
      </div>

      <!-- Logs -->
      <div>
        <div class="sh">
          <div class="st"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>Log em tempo real</div>
          <button onclick="limparLogs()" style="font-size:11px;color:var(--txt3);background:none;border:1px solid var(--border);border-radius:6px;padding:3px 9px;cursor:pointer;font-family:inherit;transition:all .15s" onmouseover="this.style.color='var(--txt1)'" onmouseout="this.style.color='var(--txt3)'">Limpar</button>
        </div>
        <div class="log-view" id="log-view">
          <div class="log-empty">Logs aparecerão aqui durante a execução</div>
        </div>
      </div>
    </div>

    <!-- ── EXECUÇÕES ── -->
    <div class="page" id="page-execucoes">
      <div class="sh">
        <div class="st"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>Todas as Execuções</div>
        <span class="sbadge" id="ex-badge">—</span>
      </div>
      <div class="tc">
        <div class="tsearch">
          <svg style="width:15px;height:15px;color:var(--txt3);flex-shrink:0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input class="sinput" id="sinput" type="text" placeholder="Filtrar por tipo, data ou nota..." oninput="filtrarExec()">
        </div>
        <div id="ex-tbl"></div>
      </div>
    </div>

    <!-- ── NOTAS ── -->
    <div class="page" id="page-notas">
      <div class="sh">
        <div class="st"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Histórico de Notas</div>
        <span class="sbadge">Últimos 7 dias</span>
      </div>
      <div id="notas-grid" style="display:flex;flex-direction:column;gap:16px"></div>
    </div>

    <!-- ── MENU ── -->
    <div class="page" id="page-menu">
      <div class="sh">
        <div class="st"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>Automações disponíveis</div>
      </div>
      <div class="mgrid">
        <div class="mitem">
          <div class="micon" style="background:rgba(63,185,80,.12)"><svg style="color:#3fb950" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg></div>
          <div class="mname">Lançamento Fábrica</div>
          <div class="mdesc">Lança notas de fábrica com fluxo completo de 25 passos.</div>
          <div class="mshort">menu → 1</div>
        </div>
        <div class="mitem">
          <div class="micon" style="background:rgba(227,179,65,.12)"><svg style="color:#e3b341" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="1" y="3" width="15" height="13" rx="1"/><path d="M16 8l4 2v4"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg></div>
          <div class="mname">Lançamento Transferência</div>
          <div class="mdesc">Lança notas de transferência com 16 passos automatizados.</div>
          <div class="mshort">menu → 2</div>
        </div>
        <div class="mitem">
          <div class="micon" style="background:rgba(248,81,73,.12)"><svg style="color:#f85149" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
          <div class="mname">Entrada CT-e</div>
          <div class="mdesc">Lança notas CT-e no módulo Fiscal. Suporte a lotes.</div>
          <div class="mshort">menu → 3</div>
        </div>
        <div class="mitem">
          <div class="micon" style="background:rgba(88,166,255,.12)"><svg style="color:#58a6ff" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 3h18v18H3z"/><path d="M3 9h18M3 15h18M9 3v18"/></svg></div>
          <div class="mname">Relatório Diário</div>
          <div class="mdesc">Gera relatório de compras do dia anterior automaticamente.</div>
          <div class="mshort">menu → 4 / 08:00 automático</div>
        </div>
      </div>
    </div>

  </div><!-- /content -->

  <footer>
    <span class="fcopy">Todos os direitos reservados a Arthur Campos Eugenio</span>
    <span class="fver" id="fver">v1.0</span>
  </footer>
</div>

<!-- Modal de pausa -->
<div class="modal-bg" id="modal" style="display:none">
  <div class="modal-box">
    <div class="modal-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
    </div>
    <div class="modal-titulo" id="modal-titulo">Aguardando ação</div>
    <div class="modal-sub" id="modal-sub">A automação está aguardando sua resposta para continuar</div>
    <div class="modal-opts" id="modal-opts"></div>
  </div>
</div>

<script>
// ── Estado ──────────────────────────────────────────────
let sbCol = false;
let rpaAtual = null;
let allExec = [];
let chart = null;
let ultimoLogLen = 0;

// ── Navegação ────────────────────────────────────────────
function goPage(id, el) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('act'));
  document.querySelectorAll('.ni').forEach(n => n.classList.remove('act'));
  document.getElementById('page-' + id).classList.add('act');
  el.classList.add('act');
  const titulos = {overview:'Visão Geral',controle:'Controle',execucoes:'Execuções',notas:'Notas',menu:'Menu RPA'};
  document.getElementById('ptitle').textContent = titulos[id] || id;
}

function toggleSb() {
  sbCol = !sbCol;
  document.getElementById('sb').classList.toggle('col', sbCol);
  document.getElementById('main').classList.toggle('col', sbCol);
  const ico = document.getElementById('tog-ico');
  ico.innerHTML = sbCol
    ? '<polyline points="9 18 15 12 9 6"/><polyline points="15 18 21 12 15 6"/>'
    : '<polyline points="15 18 9 12 15 6"/><polyline points="9 18 3 12 9 6"/>';
}

// ── Controle: seleção de RPA ─────────────────────────────
function selecionarRPA(tipo, el) {
  rpaAtual = tipo;
  document.querySelectorAll('.rpa-btn').forEach(b => b.classList.remove('sel'));
  el.classList.add('sel');

  document.getElementById('input-notas').style.display    = ['fabrica','transferencia'].includes(tipo) ? 'block' : 'none';
  document.getElementById('input-qtd').style.display      = tipo === 'entrada_cte' ? 'block' : 'none';
  document.getElementById('input-relatorio').style.display = tipo === 'relatorio' ? 'block' : 'none';

  const btn = document.getElementById('exec-btn');
  btn.disabled = false;
  const nomes = {fabrica:'Fábrica',transferencia:'Transferência',entrada_cte:'Entrada CT-e',relatorio:'Relatório Diário'};
  btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:16px;height:16px"><polygon points="5 3 19 12 5 21 5 3"/></svg> Executar ${nomes[tipo]}`;
}

// ── Controle: executar ───────────────────────────────────
async function executar() {
  if (!rpaAtual) return;

  const body = { tipo: rpaAtual };

  if (['fabrica','transferencia'].includes(rpaAtual)) {
    const val = document.getElementById('inp-notas').value.trim();
    if (!val) { alertMsg('Digite pelo menos um número de nota.'); return; }
    body.notas = val.split(',').map(n => n.trim()).filter(Boolean);
  }

  if (rpaAtual === 'entrada_cte') {
    body.quantidade = parseInt(document.getElementById('inp-qtd').value) || 1;
  }

  const btn = document.getElementById('exec-btn');
  btn.disabled = true;
  btn.innerHTML = '<svg style="width:16px;height:16px;animation:spin .8s linear infinite" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg> Iniciando...';

  try {
    const r = await fetch('/api/executar', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(body),
    });
    const d = await r.json();
    if (!d.ok) {
      alertMsg(d.erro || 'Erro ao iniciar execução.');
      btn.disabled = false;
      selecionarRPA(rpaAtual, document.querySelector(`.rpa-btn[data-tipo="${rpaAtual}"]`));
    }
  } catch(e) {
    alertMsg('Erro de conexão com o servidor.');
    btn.disabled = false;
  }
}

// ── Controle: responder pausa ────────────────────────────
async function responder(valor) {
  document.getElementById('modal').style.display = 'none';
  await fetch('/api/responder', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({valor}),
  });
}

// ── Controle: polling de estado ──────────────────────────
function limparLogs() {
  ultimoLogLen = 0;
  document.getElementById('log-view').innerHTML = '<div class="log-empty">Logs aparecerão aqui durante a execução</div>';
}

const COR = {INFO:'#8b949e',SUCCESS:'#3fb950',ERROR:'#f85149',WARNING:'#e3b341',PAUSE:'#bc8cff',CRITICAL:'#f85149',DEBUG:'#6e7681'};
const STATUS_TXT = {idle:'Aguardando',running:'Executando',paused:'Pausado — aguardando resposta',error:'Erro na execução'};
const STATUS_SUB = {
  idle:'Nenhuma automação em execução',
  running:'Automação em andamento no PC',
  paused:'Responda a pergunta abaixo para continuar',
  error:'Veja o log para detalhes do erro',
};

async function pollEstado() {
  try {
    const r = await fetch('/api/estado');
    const d = await r.json();

    // Status bar
    const dot   = document.getElementById('sdot');
    const stxt  = document.getElementById('sb-txt');
    const ssub  = document.getElementById('sb-sub');
    const sts   = document.getElementById('sb-ts');
    dot.className = `sdot ${d.status}`;
    stxt.textContent = STATUS_TXT[d.status] || d.status;
    ssub.textContent = d.tipo ? `RPA: ${d.tipo}` : STATUS_SUB[d.status] || '';
    sts.textContent  = d.iniciado_em ? `iniciado ${d.iniciado_em}` : '—';

    // Botão executar
    const btn = document.getElementById('exec-btn');
    if (d.status === 'idle' || d.status === 'error') {
      if (btn.disabled && rpaAtual) {
        selecionarRPA(rpaAtual, document.querySelector(`.rpa-btn[data-tipo="${rpaAtual}"]`));
      }
    } else {
      btn.disabled = true;
    }

    // Logs
    const logs = d.logs || [];
    if (logs.length !== ultimoLogLen) {
      ultimoLogLen = logs.length;
      const lv = document.getElementById('log-view');
      if (!logs.length) {
        lv.innerHTML = '<div class="log-empty">Logs aparecerão aqui durante a execução</div>';
      } else {
        lv.innerHTML = logs.map(l => `
          <div class="ll">
            <span class="ll-ts">${l.ts}</span>
            <span class="ll-msg ${l.nivel}" style="color:${COR[l.nivel]||'#8b949e'}">${escHtml(l.msg)}</span>
          </div>`).join('');
        lv.scrollTop = lv.scrollHeight;
      }
    }

    // Modal de pausa
    const modal = document.getElementById('modal');
    if (d.acao_pendente) {
      document.getElementById('modal-titulo').textContent = d.acao_pendente.titulo;
      const isCont = d.acao_pendente.tipo === 'confirmacao';
      document.getElementById('modal-sub').textContent = isCont
        ? 'Confirme para continuar a automação'
        : 'Selecione uma opção para continuar';
      document.getElementById('modal-opts').innerHTML = (d.acao_pendente.opcoes || []).map(o => `
        <button class="modal-btn" onclick="responder('${o.chave}')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:16px;height:16px;flex-shrink:0;opacity:.6"><polyline points="9 18 15 12 9 6"/></svg>
          ${escHtml(o.descricao)}
        </button>`).join('');
      modal.style.display = 'flex';
    } else {
      modal.style.display = 'none';
    }
  } catch(e) { /* silencioso */ }
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Visão geral ──────────────────────────────────────────
async function carregarResumo() {
  try {
    const r = await fetch('/api/resumo');
    const d = await r.json();
    animNum('s-total', d.total_execucoes || 0);
    animNum('s-taxa',  d.taxa_sucesso_geral || 0, 1);
    animNum('s-tempo', d.tempo_medio_geral || 0, 1);
    document.getElementById('s-ult').textContent   = d.ultima_execucao || '—';
    document.getElementById('s-total-u').textContent = 'execuções registradas';
    document.getElementById('s-taxa-u').textContent  = 'das execuções';
    document.getElementById('s-tempo-u').textContent = 'por execução';
    document.getElementById('s-ult-u').textContent   = 'última automação';
    allExec = d.ultimas || [];
    renderTbl('ov-tbl', allExec.slice(0, 8));
    renderTbl('ex-tbl', allExec);
    document.getElementById('ov-badge').textContent = `${Math.min(allExec.length, 8)} recentes`;
    document.getElementById('ex-badge').textContent = `${allExec.length} execuções`;
    ts();
  } catch(e) {}
}

async function carregarChart() {
  try {
    const r = await fetch('/api/tempo-medio');
    const d = await r.json();
    const entries = Object.entries(d);
    document.getElementById('ch-badge').textContent = `${entries.length} tipos`;
    if (!entries.length) return;
    const COLS = ['#58a6ff','#3fb950','#e3b341','#f85149','#bc8cff'];
    if (chart) chart.destroy();
    chart = new Chart(document.getElementById('chart-tempo'), {
      type: 'bar',
      data: {
        labels: entries.map(([k]) => k),
        datasets: [{
          label: 'Tempo médio (s)',
          data: entries.map(([,v]) => parseFloat(v.toFixed(1))),
          backgroundColor: entries.map((_,i) => COLS[i%COLS.length]+'26'),
          borderColor:     entries.map((_,i) => COLS[i%COLS.length]),
          borderWidth: 1.5, borderRadius: 6, borderSkipped: false,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: {display:false},
          tooltip: {backgroundColor:'#161b22',borderColor:'#30363d',borderWidth:1,titleColor:'#e6edf3',bodyColor:'#8b949e',padding:10,callbacks:{label:ctx=>` ${ctx.parsed.y.toFixed(1)}s`}},
        },
        scales: {
          x: {grid:{color:'rgba(48,54,61,.6)',drawBorder:false},ticks:{color:'#8b949e',font:{family:'Inter'}}},
          y: {grid:{color:'rgba(48,54,61,.6)',drawBorder:false},ticks:{color:'#8b949e',font:{family:'Inter'},callback:v=>v+'s'},beginAtZero:true},
        }
      }
    });
  } catch(e) {}
}

async function carregarNotas() {
  try {
    const r = await fetch('/api/notas-por-tipo/7');
    const d = await r.json();
    const el = document.getElementById('notas-grid');
    const datas = Object.keys(d);
    if (!datas.length) {
      el.innerHTML = '<div class="empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><p>Nenhuma nota lançada nos últimos 7 dias</p></div>';
      return;
    }
    const TC = {fabrica:'b-fabrica',transferencia:'b-transferencia',relatorio:'b-relatorio',entrada_cte:'b-entrada_cte'};
    el.innerHTML = datas.map((dt, i) => {
      const tipos = d[dt];
      const tot = Object.values(tipos).reduce((a,v) => a + v.length, 0);
      const dtF = new Date(dt+'T12:00').toLocaleDateString('pt-BR',{weekday:'short',day:'2-digit',month:'short',year:'numeric'});
      const body = Object.entries(tipos).map(([tipo, notas]) =>
        `<div class="tipo-row">
          <span class="badge ${TC[tipo]||'b-relatorio'}" style="margin-top:2px">${tipo}</span>
          <div class="nchips">${notas.map(n => `<span class="nchip">${n}</span>`).join('')}</div>
        </div>`).join('');
      return `<div class="dia-card">
        <div class="dia-h" onclick="toggleDia(this)">
          <div class="dia-ht"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>${dtF}</div>
          <div style="display:flex;align-items:center;gap:12px">
            <span class="dia-cnt">${tot} nota${tot!==1?'s':''}</span>
            <svg class="chev ${i===0?'open':''}" style="width:15px;height:15px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg>
          </div>
        </div>
        <div class="dia-b" ${i===0?'':'style="display:none"'}>${body}</div>
      </div>`;
    }).join('');
  } catch(e) {}
}

function toggleDia(h) {
  const b = h.nextElementSibling;
  const c = h.querySelector('.chev');
  const open = b.style.display !== 'none';
  b.style.display = open ? 'none' : 'grid';
  c.classList.toggle('open', !open);
}

// ── Tabela de execuções ──────────────────────────────────
function renderTbl(id, data) {
  const el = document.getElementById(id);
  if (!data || !data.length) {
    el.innerHTML = '<div class="empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg><p>Nenhuma execução registrada</p></div>';
    return;
  }
  el.innerHTML = `<table class="tbl"><thead><tr>
    <th>Tipo</th><th>Data / Hora</th><th>Duração</th><th>Status</th><th>Notas</th>
  </tr></thead><tbody>${data.map(ex => `<tr>
    <td><span class="badge b-${ex.tipo}">${ex.tipo}</span></td>
    <td><span class="mono">${ex.data} ${ex.hora}</span></td>
    <td><span class="dur">${ex.duracao}</span></td>
    <td><span class="badge b-${ex.status}"><span class="bd"></span>${ex.status}</span></td>
    <td><span class="mono">${ex.notas||'—'}</span></td>
  </tr>`).join('')}</tbody></table>`;
}

function filtrarExec() {
  const q = document.getElementById('sinput').value.toLowerCase();
  const f = q ? allExec.filter(e =>
    e.tipo.includes(q)||e.data.includes(q)||e.hora.includes(q)||
    e.status.includes(q)||(e.notas&&e.notas.toLowerCase().includes(q))
  ) : allExec;
  renderTbl('ex-tbl', f);
  document.getElementById('ex-badge').textContent = `${f.length} execuções`;
}

// ── Helpers ──────────────────────────────────────────────
function animNum(id, target, dec=0) {
  const el = document.getElementById(id);
  const dur = 800, t0 = performance.now();
  const step = now => {
    const p = Math.min((now-t0)/dur, 1);
    const e = 1 - Math.pow(1-p, 3);
    el.textContent = dec ? (target*e).toFixed(dec) : Math.round(target*e);
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function alertMsg(msg) {
  const prev = document.getElementById('_alert');
  if (prev) prev.remove();
  const div = document.createElement('div');
  div.id = '_alert';
  div.style.cssText = 'position:fixed;top:20px;right:20px;background:#f85149;color:#fff;padding:12px 18px;border-radius:10px;font-size:13px;font-weight:500;z-index:9999;box-shadow:0 8px 24px rgba(0,0,0,.4);max-width:320px';
  div.textContent = msg;
  document.body.appendChild(div);
  setTimeout(() => div.remove(), 4000);
}

function ts() {
  const now = new Date();
  document.getElementById('fver').textContent =
    'v1.0 · ' + now.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
}

// ── Refresh ──────────────────────────────────────────────
async function refreshAll() {
  const btn = document.getElementById('rbtn');
  btn.classList.add('spin');
  await Promise.all([carregarResumo(), carregarChart(), carregarNotas()]);
  btn.classList.remove('spin');
}

// ── Init ─────────────────────────────────────────────────
refreshAll();
setInterval(refreshAll, 30000);
setInterval(pollEstado, 2000);
</script>
</body>
</html>"""


class DashboardServer:

    def __init__(
        self,
        rastreador: Rastreador,
        controlador=None,
        host: str = "127.0.0.1",
        porta: int = 8080,
    ) -> None:
        self.rastreador = rastreador
        self.controlador = controlador
        self.host = host
        self.porta = porta
        self.app = Flask(__name__)
        CORS(self.app)
        self._thread: Optional[threading.Thread] = None
        self._configurar_rotas()

    def _configurar_rotas(self) -> None:

        @self.app.route("/")
        def index():
            return render_template_string(_HTML)

        # ── Monitoramento ──
        @self.app.route("/api/resumo")
        def api_resumo():
            return jsonify(self.rastreador.resumo_execucoes_recentes(50))

        @self.app.route("/api/tempo-medio")
        def api_tempo_medio():
            return jsonify(self.rastreador.tempo_medio_por_tipo())

        @self.app.route("/api/taxa-sucesso")
        def api_taxa_sucesso():
            return jsonify(self.rastreador.taxa_sucesso_por_tipo())

        @self.app.route("/api/notas/<int:dias>")
        def api_notas(dias=7):
            return jsonify(self.rastreador.historico_notas(dias))

        @self.app.route("/api/notas-por-tipo/<int:dias>")
        def api_notas_por_tipo(dias=7):
            return jsonify(self.rastreador.notas_por_tipo_e_data(dias))

        # ── Controle ──
        @self.app.route("/api/executar", methods=["POST"])
        def api_executar():
            if not self.controlador:
                return jsonify({"ok": False, "erro": "Controlador não configurado. Veja DASHBOARD_INTEGRACAO.md"})
            data = request.get_json() or {}
            ok, erro = self.controlador.executar(
                tipo=data.get("tipo", ""),
                notas=data.get("notas"),
                quantidade=data.get("quantidade"),
            )
            return jsonify({"ok": ok, "erro": erro})

        @self.app.route("/api/estado")
        def api_estado():
            if not self.controlador:
                return jsonify({"status": "idle", "tipo": None, "iniciado_em": None, "logs": [], "acao_pendente": None})
            return jsonify(self.controlador.get_estado())

        @self.app.route("/api/responder", methods=["POST"])
        def api_responder():
            if not self.controlador:
                return jsonify({"ok": False})
            data = request.get_json() or {}
            ok = self.controlador.responder(data.get("valor", ""))
            return jsonify({"ok": ok})

    def iniciar(self) -> None:
        import logging
        logging.getLogger('werkzeug').setLevel(logging.ERROR)  # silencia logs HTTP
        self._thread = threading.Thread(
            target=lambda: self.app.run(
                host=self.host, port=self.porta,
                debug=False, use_reloader=False,
            ),
            daemon=True,
        )
        self._thread.start()
        log.info(f"Dashboard iniciado em http://{self.host}:{self.porta}")

    def parar(self) -> None:
        log.info("Dashboard parado.")

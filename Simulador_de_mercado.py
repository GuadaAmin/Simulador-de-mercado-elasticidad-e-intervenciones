"""
Simulador de Mercado — Economía para Ingenieros 2026
UNSTA · TP 2 · v3
Alumnas: Abregú Candela · Amin Guadalupe · Pasteris Luciana
Prof. Raúl García
"""

import io
import datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Configurar fuente que soporte emojis (Windows)
plt.rcParams['font.family'] = 'Segoe UI Symbol'  

import streamlit as st

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, Image as RLImage, PageBreak,
)

# ══════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Simulador de Mercados - UNSTA",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
# CSS — mismo estilo base v2 + mejoras de profundidad visual
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Fondo general levemente gris-azulado ── */
.stApp { background-color: #f0f2f6; }

/* ── Contenedor principal con fondo blanco y sombra ── */
.block-container {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.4rem 2rem 2rem 2rem !important;
    box-shadow: 0 2px 16px rgba(30,50,100,0.07);
    margin-top: 0.6rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #1e2a45 !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stRadio label { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .stSuccess { background: #166534 !important; }
[data-testid="stSidebar"] input {
    background: #2d3f63 !important;
    color: #f1f5f9 !important;
    border: 1px solid #3b547a !important;
}

/* ── Métricas ── */
[data-testid="metric-container"] {
    background: #f8faff;
    border: 1px solid #dbeafe;
    border-radius: 10px;
    padding: 10px 14px;
    box-shadow: 0 1px 4px rgba(37,99,235,0.06);
}

/* ── Tabs más modernas ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 6px 16px;
    font-size: 0.85rem;
    transition: background 0.2s;
}
.stTabs [aria-selected="true"] {
    background: #2563eb !important;
    color: white !important;
}

/* ── Caja-info ── */
.caja-info {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 0.9rem;
    line-height: 1.5;
}
.caja-warn {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 0.9rem;
}
.caja-ok {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 0.9rem;
}

/* ── Separadores de módulo ── */
.mod-header {
    background: linear-gradient(90deg,#1e3a8a 0%,#2563eb 100%);
    color: white !important;
    padding: 7px 18px;
    border-radius: 8px;
    margin: 18px 0 10px 0;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

/* ── Botón de descarga PDF ── */
.stDownloadButton > button {
    background: linear-gradient(90deg,#1e3a8a,#2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    font-weight: 600 !important;
    transition: opacity 0.2s !important;
}
.stDownloadButton > button:hover { opacity: 0.88 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ENCABEZADO
# ══════════════════════════════════════════════════════════════════
st.title("📊 Simulador de Mercados — Economía para Ingenieros 2026")
st.markdown("**UNSTA · Trabajo Práctico 2** · Elasticidad e intervenciones del Estado")
st.markdown("**Alumnas**: Abregú Candela · Amin Guadalupe · Pasteris Luciana &nbsp;|&nbsp; **Prof.** Raúl García")
st.divider()


# ══════════════════════════════════════════════════════════════════
# PALETA DE COLORES (idéntica a v2)
# ══════════════════════════════════════════════════════════════════
COLOR_DEMANDA  = '#1a56db'
COLOR_OFERTA   = '#057a55'
COLOR_EQ       = '#e02424'
COLOR_NUEVO_EQ = '#7e3af2'
COLOR_INTERV   = '#e3a008'
COLOR_ESCASEZ  = '#f59e0b'
COLOR_PERDIDA  = '#ef4444'
COLOR_RECAUD   = '#6366f1'
COLOR_GRIS     = '#9ca3af'


# ══════════════════════════════════════════════════════════════════
# VALIDACIONES (idénticas a v2)
# ══════════════════════════════════════════════════════════════════

def validar_demanda(a, b):
    errs = []
    if b <= 0:
        errs.append("❌ La pendiente de demanda debe ser POSITIVA (Qd = a − b·P, con b > 0)")
    if a <= 0:
        errs.append("❌ El intercepto (a) debe ser positivo para que exista demanda a precio cero")
    return errs

def validar_oferta(c, d):
    errs = []
    if d <= 0:
        errs.append("❌ La pendiente de oferta debe ser POSITIVA (Qo = c + d·P, con d > 0)")
    return errs

def validar_puntos_demanda(P1, Q1, P2, Q2):
    errs = []
    if P2 == P1:
        errs.append("❌ Los precios no pueden ser iguales"); return errs
    pend = (Q2 - Q1) / (P2 - P1)
    if pend >= 0:
        errs.append(f"❌ Pendiente = {pend:.2f} (debe ser NEGATIVA). Ley de demanda violada.")
    if Q1 < 0 or Q2 < 0:
        errs.append("⚠️ Las cantidades demandadas no pueden ser negativas")
    return errs

def validar_puntos_oferta(P1, Q1, P2, Q2):
    errs = []
    if P2 == P1:
        errs.append("❌ Los precios no pueden ser iguales"); return errs
    pend = (Q2 - Q1) / (P2 - P1)
    if pend <= 0:
        errs.append(f"❌ Pendiente = {pend:.2f} (debe ser POSITIVA). Ley de oferta violada.")
    if Q1 < 0 or Q2 < 0:
        errs.append("⚠️ Las cantidades ofrecidas no pueden ser negativas")
    return errs


# ══════════════════════════════════════════════════════════════════
# FUNCIONES ECONÓMICAS (idénticas a v2)
# ══════════════════════════════════════════════════════════════════

def equilibrio(a, b, c, d):
    if b + d == 0: return None, None
    P = (a - c) / (b + d)
    Q = a - b * P
    if P < 0 or Q < 0: return None, None
    return P, Q

def elasticidad_punto_medio(P1, Q1, P2, Q2):
    if abs(P1 - P2) < 0.001: return None
    dQ = Q2 - Q1; dP = P2 - P1
    mQ = (Q1 + Q2) / 2; mP = (P1 + P2) / 2
    if abs(mP) < 0.001 or abs(mQ) < 0.001: return None
    return abs((dQ / mQ) / (dP / mP))

def rango_precios(a, b, P_eq, margen=0.25):
    a = float(a) if a is not None else 0.0
    b = float(b) if b is not None else 0.0
    P_eq = float(P_eq) if P_eq is not None else 0.0
    Ptop = max((a / b) if b > 0 else P_eq * 2, P_eq) * (1 + margen)
    if Ptop <= 0:
        Ptop = 100.0
    return np.linspace(0, Ptop, 300)


# ══════════════════════════════════════════════════════════════════
# HELPERS MATPLOTLIB (idénticos a v2)
# ══════════════════════════════════════════════════════════════════

def _estilo_base(ax, titulo):
    ax.set_xlabel('Cantidad (Q)', fontsize=11, color='#374151')
    ax.set_ylabel('Precio (P)',   fontsize=11, color='#374151')
    ax.set_title(titulo, fontsize=13, fontweight='bold', color='#111827', pad=10)
    ax.grid(True, alpha=0.25, linestyle='--', color='#d1d5db')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(left=0); ax.set_ylim(bottom=0)
    ax.tick_params(labelsize=9, colors='#374151')

def _leyenda(ax, n=12):
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[:n], l[:n], loc='upper right', fontsize=8,
              framealpha=0.92, edgecolor='#e5e7eb', fancybox=True)

def _lineas_eq(ax, P, Q):
    ax.axhline(P, linestyle=':', alpha=0.5, color=COLOR_GRIS, linewidth=1)
    ax.axvline(Q, linestyle=':', alpha=0.5, color=COLOR_GRIS, linewidth=1)


# ══════════════════════════════════════════════════════════════════
# GRAFICADORES (idénticos a v2, con fig devuelto para PDF)
# ══════════════════════════════════════════════════════════════════

def graficar_mercado(a, b, c, d, P_eq, Q_eq, titulo="Equilibrio de Mercado"):
    fig, ax = plt.subplots(figsize=(8, 5))
    Pr = rango_precios(a, b, P_eq)
    Qd = np.maximum(a - b * Pr, 0)
    Qo = np.maximum(c + d * Pr, 0)
    # Filtrar solo tramos donde cada curva tiene valores positivos
    mask_d = Qd > 0
    mask_o = Qo > 0
    ax.plot(Qd[mask_d], Pr[mask_d], color=COLOR_DEMANDA, lw=2.5, label='Demanda')
    ax.plot(Qo[mask_o], Pr[mask_o], color=COLOR_OFERTA,  lw=2.5, label='Oferta')
    if P_eq is not None and Q_eq is not None and Q_eq > 0:
        _lineas_eq(ax, P_eq, Q_eq)
        ax.plot(Q_eq, P_eq, 'o', color=COLOR_EQ, ms=9, zorder=5,
                label=f'Equilibrio  P*={P_eq:.2f}  Q*={Q_eq:.0f}')
        offset_q = max(Q_eq * 0.08, 5)
        offset_p = max(P_eq * 0.08, 0.5)
        ax.annotate(f'E(P={P_eq:.2f}, Q={Q_eq:.0f})',
                    xy=(Q_eq, P_eq), xytext=(Q_eq + offset_q, P_eq + offset_p),
                    fontsize=8, color=COLOR_EQ,
                    arrowprops=dict(arrowstyle='->', color=COLOR_EQ, lw=1))
    _estilo_base(ax, titulo); _leyenda(ax); fig.tight_layout()
    return fig

def graficar_precio_maximo(a, b, c, d, P_eq, Q_eq, P_max, efectivo=True):
    fig, ax = plt.subplots(figsize=(8, 5))
    Pr = rango_precios(a, b, P_eq)
    ax.plot(np.maximum(a-b*Pr,0), Pr, color=COLOR_DEMANDA, lw=2.5, label='Demanda')
    ax.plot(np.maximum(c+d*Pr,0), Pr, color=COLOR_OFERTA,  lw=2.5, label='Oferta')
    _lineas_eq(ax, P_eq, Q_eq)
    ax.plot(Q_eq, P_eq, 'o', color=COLOR_EQ, ms=8, zorder=5, label=f'Equilibrio libre  P*={P_eq:.2f}')
    if efectivo:
        # Precio máximo DEBAJO del equilibrio → escasez real
        Qd = max(0, a-b*P_max); Qo = max(0, c+d*P_max); esc = Qd - Qo
        ax.axhline(P_max, color=COLOR_PERDIDA, lw=2, label=f'P máx = {P_max:.2f}')
        ax.plot(Qd, P_max, 's', color=COLOR_DEMANDA, ms=7, zorder=5, label=f'Qd = {Qd:.0f}')
        ax.plot(Qo, P_max, 's', color=COLOR_OFERTA,  ms=7, zorder=5, label=f'Qo = {Qo:.0f}')
        if esc > 0:
            ax.axvspan(Qo, Qd, alpha=0.25, color=COLOR_ESCASEZ, label=f'Escasez = {esc:.0f}')
            ax.annotate('Escasez', xy=((Qo+Qd)/2, P_max),
                        xytext=((Qo+Qd)/2, P_max+P_eq*0.12), ha='center', fontsize=8,
                        color='#92400e', arrowprops=dict(arrowstyle='->', color='#92400e', lw=1))
        titulo = 'Precio Máximo (Techo) — EFECTIVO ⚠️'
    else:
        # Precio máximo ENCIMA del equilibrio → NO tiene efecto
        # Solo mostramos la línea punteada gris para indicar que está por encima
        ax.axhline(P_max, color=COLOR_GRIS, lw=1.8, linestyle='--',
                   label=f'P máx = {P_max:.2f} (no efectivo)')
        ax.annotate('No altera el equilibrio', xy=(Q_eq * 0.5, P_max),
                    xytext=(Q_eq * 0.5, P_max + P_eq * 0.08),
                    ha='center', fontsize=8, color=COLOR_GRIS,
                    arrowprops=dict(arrowstyle='->', color=COLOR_GRIS, lw=1))
        titulo = 'Precio Máximo (Techo) — NO RELEVANTE ✅'
    _estilo_base(ax, titulo); _leyenda(ax); fig.tight_layout()
    return fig

def graficar_precio_minimo(a, b, c, d, P_eq, Q_eq, P_min, efectivo=True):
    fig, ax = plt.subplots(figsize=(8, 5))
    # Rango de precios que cubra tanto el equilibrio como P_min
    P_ref = max(P_eq, P_min) if P_min else P_eq
    Pr = rango_precios(a, b, P_ref, margen=0.3)
    Qd_curve = np.maximum(a - b * Pr, 0)
    Qo_curve = np.maximum(c + d * Pr, 0)
    mask_d = Qd_curve > 0
    mask_o = Qo_curve > 0
    ax.plot(Qd_curve[mask_d], Pr[mask_d], color=COLOR_DEMANDA, lw=2.5, label='Demanda')
    ax.plot(Qo_curve[mask_o], Pr[mask_o], color=COLOR_OFERTA,  lw=2.5, label='Oferta')
    _lineas_eq(ax, P_eq, Q_eq)
    ax.plot(Q_eq, P_eq, 'o', color=COLOR_EQ, ms=8, zorder=5,
            label=f'Equilibrio libre  P*={P_eq:.2f}')
    if efectivo:
        # Precio mínimo ENCIMA del equilibrio → excedente real
        Qd_min = max(0.0, a - b * P_min)
        Qo_min = max(0.0, c + d * P_min)
        exc = Qo_min - Qd_min
        ax.axhline(P_min, color='#16a34a', lw=2.2, linestyle='-',
                   label=f'P mín = {P_min:.2f}', zorder=4)
        ax.plot(Qd_min, P_min, 's', color=COLOR_DEMANDA, ms=8, zorder=6,
                label=f'Qd = {Qd_min:.0f}')
        ax.plot(Qo_min, P_min, 's', color=COLOR_OFERTA,  ms=8, zorder=6,
                label=f'Qo = {Qo_min:.0f}')
        if exc > 1e-3:
            ax.axvspan(Qd_min, Qo_min, alpha=0.25, color='#fca5a5',
                       label=f'Excedente = {exc:.0f}')
            mid_x = (Qd_min + Qo_min) / 2
            offset_p = max(P_eq * 0.12, 1.0)
            ax.annotate('Excedente',
                        xy=(mid_x, P_min),
                        xytext=(mid_x, P_min + offset_p),
                        ha='center', fontsize=8, color='#991b1b',
                        arrowprops=dict(arrowstyle='->', color='#991b1b', lw=1))
        titulo = 'Precio Mínimo (Piso) — EFECTIVO ⚠️'
    else:
        # Precio mínimo DEBAJO del equilibrio → NO tiene efecto
        ax.axhline(P_min, color=COLOR_GRIS, lw=1.8, linestyle='--',
                   label=f'P mín = {P_min:.2f} (no efectivo)')
        ax.annotate('No altera el equilibrio', xy=(Q_eq * 0.5, P_min),
                    xytext=(Q_eq * 0.5, P_min - P_eq * 0.12),
                    ha='center', fontsize=8, color=COLOR_GRIS,
                    arrowprops=dict(arrowstyle='->', color=COLOR_GRIS, lw=1))
        titulo = 'Precio Mínimo (Piso) — NO RELEVANTE ✅'
    # Ajustar ejes para que P_min siempre quede visible
    ax.set_ylim(bottom=0, top=max(Pr) * 1.05)
    ax.set_xlim(left=0)
    _estilo_base(ax, titulo); _leyenda(ax); fig.tight_layout()
    return fig

def graficar_impuesto(a, b, c, d, P_eq, Q_eq, t, sobre_vendedores=True):
    fig, ax = plt.subplots(figsize=(8, 5))
    Pr = rango_precios(a, b, P_eq, margen=0.4)
    Qd0 = np.maximum(a-b*Pr, 0); Qo0 = np.maximum(c+d*Pr, 0)
    ax.plot(Qd0, Pr, color=COLOR_DEMANDA, lw=2.5, label='Demanda')
    ax.plot(Qo0, Pr, color=COLOR_OFERTA,  lw=2.5, label='Oferta original')
    
    if sobre_vendedores:
        ax.plot(np.maximum(c+d*(Pr-t),0), Pr, color=COLOR_OFERTA, lw=2, ls='--',
                label='Oferta c/impuesto (↑)')
        Pc = (a-c+d*t)/(b+d); Qn = max(0,a-b*Pc); Pv = Pc - t
    else:
        ax.plot(np.maximum(a-b*(Pr+t),0), Pr, color=COLOR_DEMANDA, lw=2, ls='--',
                label='Demanda c/impuesto (↓)')
        Pv = (a-b*t-c)/(b+d); Qn = max(0,c+d*Pv); Pc = Pv + t
    
    rec = t*Qn; dw = 0.5*t*abs(Q_eq-Qn)
    
    # Calcular cargas correctamente
    carga_comprador = Pc - P_eq if Pc > P_eq else 0
    carga_vendedor = P_eq - Pv if P_eq > Pv else 0
    
    # Porcentajes sobre el impuesto total
    pct_comprador = (carga_comprador / t) * 100 if t > 0 else 50
    pct_vendedor = (carga_vendedor / t) * 100 if t > 0 else 50
    
    _lineas_eq(ax, P_eq, Q_eq)
    ax.plot(Q_eq, P_eq, 'o', color=COLOR_EQ, ms=8, zorder=5, label=f'Equilibrio orig.  P*={P_eq:.2f}')
    
    if Qn > 0:
        ax.plot(Qn, Pc, 'o', color=COLOR_NUEVO_EQ, ms=9, zorder=6, label=f'Precio comprador  Pc={Pc:.2f}')
        ax.plot(Qn, max(0,Pv), 'o', color='#0891b2', ms=7, zorder=6, label=f'Precio vendedor  Pv={max(0,Pv):.2f}')
        
        if Pc > max(0,Pv):
            # Línea vertical completa (fondo gris claro)
            ax.vlines(Qn, ymin=max(0,Pv), ymax=Pc, colors='#cbd5e1', lw=3, alpha=0.5, zorder=3)
            
            # El punto P_eq divide la barra
            # Desde Pv hasta P_eq = carga del vendedor
            # Desde P_eq hasta Pc = carga del comprador
            if P_eq > max(0,Pv):
                ax.vlines(Qn, ymin=max(0,Pv), ymax=P_eq,
                         colors='#3b82f6', lw=3, alpha=0.9, zorder=5,
                         label=f'Carga vendedor ({pct_vendedor:.1f}%)')
            
            if Pc > P_eq:
                ax.vlines(Qn, ymin=P_eq, ymax=Pc,
                         colors='#ef4444', lw=3, alpha=0.9, zorder=5,
                         label=f'Carga comprador ({pct_comprador:.1f}%)')
            
            ax.fill_betweenx([max(0,Pv), Pc], 0, Qn, alpha=0.08, color=COLOR_RECAUD,
                           label=f'Recaudación ${rec:.0f}')
        
        if Qn < Q_eq:
            Pd_n = (a-Qn)/b if b!=0 else Pc
            Po_n = (Qn-c)/d if d!=0 else Pv
            ax.fill([Q_eq, Qn, Qn], [P_eq, Po_n, Pd_n], alpha=0.25, color=COLOR_PERDIDA,
                    label=f'Pérdida social (DWL) ${dw:.0f}')
        
        ax.axhline(P_eq, ls=':', alpha=0.35, color=COLOR_GRIS, lw=1)
        ax.axvline(Qn, ls=':', alpha=0.35, color=COLOR_GRIS, lw=1)
    
    _estilo_base(ax, f"Impuesto sobre {'vendedores' if sobre_vendedores else 'compradores'}  t={t:.2f}")
    _leyenda(ax)
    fig.tight_layout()
    return fig, rec, dw, Pc, max(0,Pv), Qn

def graficar_subsidio(a, b, c, d, P_eq, Q_eq, s):
    fig, ax = plt.subplots(figsize=(8, 5))
    Pr = rango_precios(a, b, P_eq, margen=0.4)
    Qd0 = np.maximum(a-b*Pr, 0); Qo0 = np.maximum(c+d*Pr, 0)
    ax.plot(Qd0, Pr, color=COLOR_DEMANDA, lw=2.5, label='Demanda')
    ax.plot(Qo0, Pr, color=COLOR_OFERTA,  lw=2.5, label='Oferta original')
    ax.plot(np.maximum(c+d*(Pr+s),0), Pr, color=COLOR_OFERTA, lw=2, ls='--',
            label='Oferta c/subsidio (↓)')
    Pcs = (a-c-d*s)/(b+d); Qs = max(0,a-b*Pcs); Pvs = Pcs+s
    ct = s*Qs; dws = 0.5*s*abs(Qs-Q_eq)
    
    # Calcular beneficios correctamente
    beneficio_comprador = P_eq - Pcs if P_eq > Pcs else 0
    beneficio_vendedor = Pvs - P_eq if Pvs > P_eq else 0
    
    # Porcentajes sobre el subsidio total
    pct_comprador = (beneficio_comprador / s) * 100 if s > 0 else 50
    pct_vendedor = (beneficio_vendedor / s) * 100 if s > 0 else 50
    
    _lineas_eq(ax, P_eq, Q_eq)
    ax.plot(Q_eq, P_eq, 'o', color=COLOR_EQ, ms=8, zorder=5, label=f'Equilibrio orig.  P*={P_eq:.2f}')
    
    if Qs > 0:
        ax.plot(Qs, max(0,Pcs), 'o', color=COLOR_NUEVO_EQ, ms=9, zorder=6,
                label=f'Precio comprador  Pc={max(0,Pcs):.2f}')
        ax.plot(Qs, Pvs, 'o', color='#0891b2', ms=7, zorder=6,
                label=f'Precio vendedor  Pv={Pvs:.2f}')
        
        if Pvs > max(0,Pcs):
            # Línea vertical completa (fondo gris claro)
            ax.vlines(Qs, ymin=max(0,Pcs), ymax=Pvs, colors='#cbd5e1', lw=3, alpha=0.5, zorder=3)
            
            # El punto P_eq divide la barra en dos partes
            # Desde Pcs hasta P_eq = beneficio del comprador
            # Desde P_eq hasta Pvs = beneficio del vendedor
            if P_eq > max(0,Pcs):
                ax.vlines(Qs, ymin=max(0,Pcs), ymax=P_eq,
                         colors='#059669', lw=3, alpha=0.9, zorder=5,
                         label=f'Beneficio comprador ({pct_comprador:.1f}%)')
            
            if Pvs > P_eq:
                ax.vlines(Qs, ymin=P_eq, ymax=Pvs,
                         colors='#10b981', lw=3, alpha=0.9, zorder=5,
                         label=f'Beneficio vendedor ({pct_vendedor:.1f}%)')
            
            ax.fill_betweenx([max(0,Pcs), Pvs], 0, Qs, alpha=0.08, color='#10b981',
                           label=f'Costo fiscal ${ct:.0f}')
        
        if Qs > Q_eq:
            Pd_s = (a-Qs)/b if b!=0 else Pcs
            Po_s = (Qs-c)/d if d!=0 else Pvs
            ax.fill([Q_eq, Qs, Qs], [P_eq, Po_s, Pd_s], alpha=0.25, color=COLOR_PERDIDA,
                    label=f'Pérdida social (DWL) ${dws:.0f}')
        
        ax.axhline(P_eq, ls=':', alpha=0.35, color=COLOR_GRIS, lw=1)
        ax.axvline(Qs, ls=':', alpha=0.35, color=COLOR_GRIS, lw=1)
    
    _estilo_base(ax, f'Subsidio por Unidad  s={s:.2f}')
    _leyenda(ax)
    fig.tight_layout()
    return fig, ct, max(0,Pcs), Pvs, Qs

def graficar_cuota(a, b, c, d, P_eq, Q_eq, cuota):
    fig, ax = plt.subplots(figsize=(8, 5))
    Pr = rango_precios(a, b, P_eq)
    ax.plot(np.maximum(a-b*Pr,0), Pr, color=COLOR_DEMANDA, lw=2.5, label='Demanda')
    ax.plot(np.maximum(c+d*Pr,0), Pr, color=COLOR_OFERTA,  lw=2.5, label='Oferta')
    _lineas_eq(ax, P_eq, Q_eq)
    ax.plot(Q_eq, P_eq, 'o', color=COLOR_EQ, ms=8, zorder=5, label=f'Equilibrio libre  P*={P_eq:.2f}')
    Pd = (a-cuota)/b if b!=0 else 0
    Po = (cuota-c)/d if d!=0 else 0
    ax.axvline(cuota, color='#7c3aed', lw=2, label=f'Cuota = {cuota:.0f}')
    
    if Pd > 0: 
        ax.plot(cuota, Pd, 'D', color=COLOR_DEMANDA, ms=8, zorder=6, label=f'Pd = ${Pd:.2f}')
    if Po > 0: 
        ax.plot(cuota, Po, 'D', color=COLOR_OFERTA,  ms=8, zorder=6, label=f'Po = ${Po:.2f}')
    
    ru = max(0, Pd-Po)
    if ru > 0 and Pd > 0 and Po > 0:
        # Línea vertical de renta por unidad
        ax.vlines(cuota, ymin=Po, ymax=Pd, colors='#8b5cf6', lw=3, alpha=0.9, zorder=5,
                 label=f'Renta por unidad = ${ru:.2f}')
        ax.fill_betweenx([Po, Pd], 0, cuota, alpha=0.1, color=COLOR_INTERV,
                       label=f'Renta total = ${ru*cuota:.0f}')
    
    if cuota < Q_eq and Pd > 0 and Po > 0 and ru > 0:
        perdida_social = 0.5 * ru * (Q_eq - cuota)
        ax.fill([cuota, cuota, Q_eq], [Po, Pd, P_eq], alpha=0.25, color=COLOR_PERDIDA,
                label=f'Pérdida social (DWL) = ${perdida_social:.0f}')
    
    ax.axhline(P_eq, ls=':', alpha=0.35, color=COLOR_GRIS, lw=1)
    _estilo_base(ax, f'Cuota = {cuota:.0f} unidades')
    _leyenda(ax)
    fig.tight_layout()
    return fig, Pd, Po, ru

def graficar_elasticidad(a, b, P_A, Q_A, P_B, Q_B, P_eq, Q_eq):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    Pr = rango_precios(a, b, P_eq, margen=0.3)
    ax1.plot(np.maximum(a-b*Pr,0), Pr, color=COLOR_DEMANDA, lw=2.5, label='Curva de demanda')
    for Pi, Qi, col, lbl in [(P_A,Q_A,'#f59e0b','A'),(P_B,Q_B,'#7c3aed','B')]:
        ax1.plot([0,Qi],[Pi,Pi], ls=':', color=col, lw=1.2, alpha=0.7)
        ax1.plot([Qi,Qi],[0,Pi], ls=':', color=col, lw=1.2, alpha=0.7)
        ax1.plot(Qi, Pi, 'o', color=col, ms=11, zorder=6, label=f'Punto {lbl}  P={Pi:.2f}, Q={Qi:.0f}')
        ax1.text(Qi, Pi+P_eq*0.06, lbl, ha='center', fontsize=10, fontweight='bold', color=col)
    xdP = max(min(Q_A,Q_B)*0.12+max(Q_A,Q_B)*0.05, Q_eq*0.08)
    Pl, Ph = min(P_A,P_B), max(P_A,P_B)
    ax1.annotate('', xy=(xdP,Ph), xytext=(xdP,Pl),
                 arrowprops=dict(arrowstyle='<->', color='#7c3aed', lw=1.8))
    ax1.text(xdP*1.35, (Pl+Ph)/2, f'ΔP={abs(P_B-P_A):.2f}', fontsize=8, color='#7c3aed', va='center')
    ydQ = max(min(P_A,P_B)*0.18, P_eq*0.06)
    Ql, Qh = min(Q_A,Q_B), max(Q_A,Q_B)
    ax1.annotate('', xy=(Qh,ydQ), xytext=(Ql,ydQ),
                 arrowprops=dict(arrowstyle='<->', color='#f59e0b', lw=1.8))
    ax1.text((Ql+Qh)/2, ydQ*1.6, f'ΔQ={abs(Q_B-Q_A):.0f}', fontsize=8, color='#f59e0b', ha='center')
    _estilo_base(ax1, 'Movimiento sobre la curva de demanda')
    ax1.legend(fontsize=8, loc='upper right', framealpha=0.9, edgecolor='#e5e7eb')
    ITA, ITB = P_A*Q_A, P_B*Q_B
    bars = ax2.bar([f'Punto A\nP={P_A:.2f}',f'Punto B\nP={P_B:.2f}'],
                   [ITA,ITB], color=['#f59e0b','#7c3aed'],
                   width=0.45, edgecolor='white', lw=1.5, alpha=0.85)
    for bar, v in zip(bars,[ITA,ITB]):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(ITA,ITB)*0.02,
                 f'${v:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#111827')
    dIT = ITB - ITA
    ax2.text(0.5, 0.93, f"Variación IT: {'↑' if dIT>=0 else '↓'} ${abs(dIT):.0f}",
             transform=ax2.transAxes, ha='center', fontsize=10,
             color='#059669' if dIT>=0 else '#dc2626', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#f9fafb',
                       edgecolor='#059669' if dIT>=0 else '#dc2626', alpha=0.9))
    ax2.set_ylabel('Ingreso Total Vendedores (P × Q)', fontsize=11, color='#374151')
    ax2.set_title('Ingreso Total Vendedores: A vs B', fontsize=13, fontweight='bold', color='#111827', pad=10)
    ax2.set_ylim(0, max(ITA,ITB)*1.22)
    ax2.grid(True, axis='y', alpha=0.25, ls='--', color='#d1d5db')
    ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)
    ax2.tick_params(labelsize=9, colors='#374151')
    fig.tight_layout(pad=2.5)
    return fig


# ══════════════════════════════════════════════════════════════════
# GRÁFICO COMPARATIVO (nuevo — Módulo 4)
# ══════════════════════════════════════════════════════════════════

def graficar_comparativo(escenarios_sel, datos):
    """Barras lado a lado: Precio y Cantidad por escenario seleccionado."""
    nombres  = [esc_d['nombre'] for esc_d in datos if esc_d['nombre'] in escenarios_sel]
    precios  = [esc_d['precio']   for esc_d in datos if esc_d['nombre'] in escenarios_sel]
    cantids  = [esc_d['cantidad'] for esc_d in datos if esc_d['nombre'] in escenarios_sel]
    colores  = [esc_d['color']    for esc_d in datos if esc_d['nombre'] in escenarios_sel]

    if not nombres:
        return None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    x = np.arange(len(nombres)); w = 0.55

    bars1 = ax1.bar(x, precios, width=w, color=colores, alpha=0.82,
                    edgecolor='white', linewidth=1.5)
    for bar, v in zip(bars1, precios):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(precios)*0.01,
                 f'${v:.2f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax1.set_xticks(x); ax1.set_xticklabels(nombres, rotation=20, ha='right', fontsize=8)
    ax1.set_ylabel('Precio ($)', fontsize=10)
    ax1.set_title('Precio de mercado por escenario', fontsize=12, fontweight='bold', color='#111827')
    ax1.grid(True, axis='y', alpha=0.25, ls='--'); ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False); ax1.set_ylim(0, max(precios)*1.2)

    bars2 = ax2.bar(x, cantids, width=w, color=colores, alpha=0.82,
                    edgecolor='white', linewidth=1.5)
    for bar, v in zip(bars2, cantids):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(cantids)*0.01,
                 f'{v:.0f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax2.set_xticks(x); ax2.set_xticklabels(nombres, rotation=20, ha='right', fontsize=8)
    ax2.set_ylabel('Cantidad', fontsize=10)
    ax2.set_title('Cantidad transada por escenario', fontsize=12, fontweight='bold', color='#111827')
    ax2.grid(True, axis='y', alpha=0.25, ls='--'); ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False); ax2.set_ylim(0, max(cantids)*1.2)

    fig.tight_layout(pad=2.5)
    return fig


# ══════════════════════════════════════════════════════════════════
# HELPER: figura → bytes PNG (para PDF)
# ══════════════════════════════════════════════════════════════════

def fig_to_png_bytes(fig, dpi=120):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════
# GENERADOR DE PDF
# ══════════════════════════════════════════════════════════════════

AZUL     = rl_colors.HexColor('#1e3a8a')
AZUL_MED = rl_colors.HexColor('#2563eb')
GRIS_OSC = rl_colors.HexColor('#374151')
GRIS_CLR = rl_colors.HexColor('#f3f4f6')
BLANCO   = rl_colors.white
ROJO_RL  = rl_colors.HexColor('#dc2626')
VERDE_RL = rl_colors.HexColor('#059669')

def _pdf_styles():
    base = getSampleStyleSheet()
    estilos = {
        'titulo': ParagraphStyle('titulo', parent=base['Title'],
                                 fontSize=20, textColor=BLANCO, alignment=TA_CENTER,
                                 spaceAfter=4, fontName='Helvetica-Bold'),
        'subtitulo': ParagraphStyle('subtitulo', parent=base['Normal'],
                                    fontSize=11, textColor=BLANCO, alignment=TA_CENTER,
                                    spaceAfter=2),
        'h1': ParagraphStyle('h1', parent=base['Heading1'],
                              fontSize=13, textColor=AZUL, fontName='Helvetica-Bold',
                              spaceBefore=14, spaceAfter=4,
                              borderPad=4, leading=16),
        'h2': ParagraphStyle('h2', parent=base['Heading2'],
                              fontSize=11, textColor=AZUL_MED, fontName='Helvetica-Bold',
                              spaceBefore=8, spaceAfter=3),
        'body': ParagraphStyle('body', parent=base['Normal'],
                               fontSize=9.5, textColor=GRIS_OSC,
                               spaceAfter=4, leading=14),
        'caption': ParagraphStyle('caption', parent=base['Normal'],
                                  fontSize=8, textColor=rl_colors.HexColor('#6b7280'),
                                  alignment=TA_CENTER, spaceAfter=6),
        'formula': ParagraphStyle('formula', parent=base['Normal'],
                                  fontSize=10, fontName='Courier',
                                  textColor=AZUL, leftIndent=18,
                                  spaceAfter=3, leading=14),
        'footer': ParagraphStyle('footer', parent=base['Normal'],
                                 fontSize=7.5, textColor=rl_colors.HexColor('#9ca3af'),
                                 alignment=TA_CENTER),
    }
    return estilos

def _tabla_datos(filas, col_widths=None, header_bg=AZUL):
    """Crea una tabla estilizada para el PDF."""
    t = Table(filas, colWidths=col_widths)
    style = [
        ('BACKGROUND', (0,0), (-1,0), header_bg),
        ('TEXTCOLOR',  (0,0), (-1,0), BLANCO),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,0), 9),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BLANCO, GRIS_CLR]),
        ('FONTSIZE',   (0,1), (-1,-1), 8.5),
        ('TEXTCOLOR',  (0,1), (-1,-1), GRIS_OSC),
        ('GRID',       (0,0), (-1,-1), 0.4, rl_colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('ROUNDEDCORNERS', [4]),
    ]
    t.setStyle(TableStyle(style))
    return t

def generar_pdf(params):
    """
    params: dict con todos los datos del simulador para incluir en el PDF.
    Devuelve bytes del PDF.
    """
    es = _pdf_styles()
    buf_pdf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf_pdf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    story = []
    W = A4[0] - 4*cm   # ancho útil

    # ── PORTADA ──────────────────────────────────────────────────
    header_data = [[
        Paragraph("SIMULADOR DE MERCADOS", es['titulo']),
    ],[
        Paragraph("Economía para Ingenieros · UNSTA 2026", es['subtitulo']),
    ],[
        Paragraph(f"Alumnas: {params['alumnas']}", es['subtitulo']),
    ],[
        Paragraph(f"Profesor: {params['profesor']}  |  Fecha: {params['fecha']}", es['subtitulo']),
    ]]
    tbl_header = Table(header_data, colWidths=[W])
    tbl_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AZUL),
        ('TOPPADDING',    (0,0),(-1,-1), 8),
        ('BOTTOMPADDING', (0,0),(-1,-1), 8),
        ('LEFTPADDING',   (0,0),(-1,-1), 16),
        ('RIGHTPADDING',  (0,0),(-1,-1), 16),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(tbl_header)
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', thickness=1.5, color=AZUL_MED))
    story.append(Spacer(1, 0.3*cm))

    # ── SECCIÓN 1: PARÁMETROS ────────────────────────────────────
    story.append(Paragraph("1. Parámetros del Mercado", es['h1']))
    story.append(Paragraph(
        f"Método de ingreso demanda: <b>{params['metodo_dem']}</b>  ·  "
        f"Método de ingreso oferta: <b>{params['metodo_of']}</b>", es['body']))

    filas_ec = [
        ['Ecuación', 'Función', 'Parámetros'],
        ['Demanda', f"Qd = {params['a']:.2f} − {params['b']:.2f}·P",
         f"a = {params['a']:.2f}  |  b = {params['b']:.2f}"],
        ['Oferta',  f"Qo = {params['c']:.2f} + {params['d']:.2f}·P",
         f"c = {params['c']:.2f}  |  d = {params['d']:.2f}"],
    ]
    story.append(_tabla_datos(filas_ec, col_widths=[W*0.2, W*0.45, W*0.35]))
    story.append(Spacer(1, 0.3*cm))

    # ── SECCIÓN 2: EQUILIBRIO ────────────────────────────────────
    story.append(Paragraph("2. Equilibrio de Mercado", es['h1']))
    story.append(Paragraph(
        f"Igualando Qd = Qo → P* = (a − c) / (b + d) = "
        f"({params['a']:.2f} − {params['c']:.2f}) / ({params['b']:.2f} + {params['d']:.2f})", es['formula']))

    filas_eq = [
        ['Variable', 'Valor', 'Interpretación'],
        ['Precio de equilibrio P*', f"${params['P_eq']:.2f}", 'Precio al que Qd = Qo'],
        ['Cantidad de equilibrio Q*', f"{params['Q_eq']:.0f} unidades", 'Cantidad intercambiada'],
    ]
    story.append(_tabla_datos(filas_eq, col_widths=[W*0.35, W*0.25, W*0.40]))

    # Gráfico mercado
    if params.get('fig_mercado'):
        story.append(Spacer(1, 0.25*cm))
        png = fig_to_png_bytes(params['fig_mercado'])
        story.append(RLImage(png, width=W*0.85, height=W*0.52))
        story.append(Paragraph("Gráfico 1 — Equilibrio de mercado competitivo", es['caption']))

    # ── SECCIÓN 3: ELASTICIDAD ───────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("3. Elasticidad de la Demanda", es['h1']))
    story.append(Paragraph(
        "Método del punto medio (Mankiw): "
        "η = (ΔQ / Q̄) / (ΔP / P̄)", es['formula']))

    e = params.get('elasticidad')
    tipo_e = ("ELÁSTICA (|η| > 1)" if e and e > 1 else
              "INELÁSTICA (|η| < 1)" if e and e < 1 else
              "UNITARIA (|η| = 1)" if e else "No calculada")
    filas_el = [
        ['Variable', 'Punto A', 'Punto B'],
        ['Precio',    f"${params['P_A']:.2f}",  f"${params['P_B']:.2f}"],
        ['Cantidad',  f"{params['Q_A']:.0f}",   f"{params['Q_B']:.0f}"],
        ['Ing. Total',f"${params['P_A']*params['Q_A']:.0f}",
                      f"${params['P_B']*params['Q_B']:.0f}"],
        ['|η| (elasticidad)', f"{e:.3f}" if e else '—', tipo_e],
    ]
    story.append(_tabla_datos(filas_el, col_widths=[W*0.35, W*0.25, W*0.40]))
    if params.get('fig_elasticidad'):
        story.append(Spacer(1, 0.25*cm))
        png = fig_to_png_bytes(params['fig_elasticidad'])
        story.append(RLImage(png, width=W*0.95, height=W*0.40))
        story.append(Paragraph("Gráfico 2 — Elasticidad y variación de Ingreso Total de los vendedores", es['caption']))

    # ── SECCIÓN 4: INTERVENCIONES ────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("4. Intervenciones del Estado", es['h1']))

    # 4a Precio máximo
    story.append(Paragraph("4.1  Precio Máximo", es['h2']))
    pm = params['precio_max']
    filas_pm = [
        ['Concepto', 'Valor'],
        ['Precio máximo fijado', f"${pm['P_max']:.2f}"],
        ['Cantidad demandada',   f"{pm['Qd']:.0f}"],
        ['Cantidad ofrecida',    f"{pm['Qo']:.0f}"],
        ['Escasez',              f"{pm['escasez']:.0f} unidades"],
        ['Efectivo',             '✓ Sí' if pm['efectivo'] else '✗ No'],
    ]
    story.append(_tabla_datos(filas_pm, col_widths=[W*0.55, W*0.45]))
    if params.get('fig_pmax'):
        png = fig_to_png_bytes(params['fig_pmax'])
        story.append(RLImage(png, width=W*0.80, height=W*0.48))
        story.append(Paragraph("Gráfico 3 — Precio máximo", es['caption']))

    story.append(Spacer(1, 0.3*cm))

    # 4b Precio mínimo
    story.append(Paragraph("4.2  Precio Mínimo", es['h2']))
    pn = params['precio_min']
    filas_pn = [
        ['Concepto', 'Valor'],
        ['Precio mínimo fijado', f"${pn['P_min']:.2f}"],
        ['Cantidad demandada',   f"{pn['Qd']:.0f}"],
        ['Cantidad ofrecida',    f"{pn['Qo']:.0f}"],
        ['Excedente',            f"{pn['excedente']:.0f} unidades"],
        ['Efectivo',             '✓ Sí' if pn['efectivo'] else '✗ No'],
    ]
    story.append(_tabla_datos(filas_pn, col_widths=[W*0.55, W*0.45]))
    if params.get('fig_pmin'):
        png = fig_to_png_bytes(params['fig_pmin'])
        story.append(RLImage(png, width=W*0.80, height=W*0.48))
        story.append(Paragraph("Gráfico 4 — Precio mínimo", es['caption']))

    # 4c Impuesto
    story.append(PageBreak())
    story.append(Paragraph("4.3  Impuesto por Unidad", es['h2']))
    imp = params['impuesto']
    filas_imp = [
        ['Concepto', 'Valor'],
        ['Impuesto por unidad (t)',       f"${imp['t']:.2f}"],
        ['Aplicado sobre',               imp['sobre']],
        ['Precio que paga el comprador', f"${imp['Pc']:.2f}"],
        ['Precio que recibe el vendedor',f"${imp['Pv']:.2f}"],
        ['Nueva cantidad',               f"{imp['Q']:.1f}"],
        ['Recaudación fiscal',           f"${imp['recaudacion']:.2f}"],
        ['Pérdida social (DWL)',         f"${imp['perdida']:.2f}"],
        ['Carga sobre comprador',        f"{imp['pct_comp']:.1f}%"],
        ['Carga sobre vendedor',         f"{imp['pct_vend']:.1f}%"],
    ]
    story.append(_tabla_datos(filas_imp, col_widths=[W*0.55, W*0.45]))
    if params.get('fig_impuesto'):
        png = fig_to_png_bytes(params['fig_impuesto'])
        story.append(RLImage(png, width=W*0.80, height=W*0.48))
        story.append(Paragraph("Gráfico 5 — Impuesto por unidad", es['caption']))

    # 4d Subsidio
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("4.4  Subsidio por Unidad", es['h2']))
    sub = params['subsidio']
    filas_sub = [
        ['Concepto', 'Valor'],
        ['Subsidio por unidad (s)',       f"${sub['s']:.2f}"],
        ['Precio que paga el comprador',  f"${sub['Pc']:.2f}"],
        ['Precio que recibe el vendedor', f"${sub['Pv']:.2f}"],
        ['Nueva cantidad',                f"{sub['Q']:.0f}"],
        ['Costo fiscal total',            f"${sub['costo']:.2f}"],
    ]
    story.append(_tabla_datos(filas_sub, col_widths=[W*0.55, W*0.45]))
    if params.get('fig_subsidio'):
        png = fig_to_png_bytes(params['fig_subsidio'])
        story.append(RLImage(png, width=W*0.80, height=W*0.48))
        story.append(Paragraph("Gráfico 6 — Subsidio por unidad", es['caption']))

    # 4e Cuota
    story.append(PageBreak())
    story.append(Paragraph("4.5  Cuota de Producción", es['h2']))
    cuo = params['cuota']
    filas_cuo = [
        ['Concepto', 'Valor'],
        ['Cuota fijada',                f"{cuo['cuota']:.0f} unidades"],
        ['Precio de mercado (Pd)',       f"${cuo['Pd']:.2f}"],
        ['Precio al productor (Po)',     f"${cuo['Po']:.2f}"],
        ['Renta por unidad',            f"${cuo['renta_u']:.2f}"],
        ['Renta total',                 f"${cuo['renta_total']:.0f}"],
        ['Efectiva',                    '✓ Sí' if cuo['efectiva'] else '✗ No'],
    ]
    story.append(_tabla_datos(filas_cuo, col_widths=[W*0.55, W*0.45]))
    if params.get('fig_cuota'):
        png = fig_to_png_bytes(params['fig_cuota'])
        story.append(RLImage(png, width=W*0.80, height=W*0.48))
        story.append(Paragraph("Gráfico 7 — Cuota de producción", es['caption']))

    # ── SECCIÓN 5: COMPARATIVO ───────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("5. Tabla Comparativa de Escenarios", es['h1']))
    filas_cmp = [
        ['Escenario','Precio ($)','Cantidad','Escasez/Excedente','Recaudación/Costo','Pérdida Social'],
        ['Mercado libre',
         f"${params['P_eq']:.2f}", f"{params['Q_eq']:.0f}", '—', '—', '—'],
        ['P. Máximo',
         f"${pm['P_max']:.2f}", f"{pm['Qo']:.0f}",
         f"{pm['escasez']:.0f} esc." if pm['efectivo'] else '—', '—', '—'],
        ['P. Mínimo',
         f"${pn['P_min']:.2f}", f"{pn['Qd']:.0f}",
         f"{pn['excedente']:.0f} exc." if pn['efectivo'] else '—', '—', '—'],
        ['Impuesto',
         f"${imp['Pc']:.2f}", f"{imp['Q']:.0f}", '—',
         f"${imp['recaudacion']:.0f}", f"${imp['perdida']:.0f}"],
        ['Subsidio',
         f"${sub['Pc']:.2f}", f"{sub['Q']:.0f}", '—',
         f"${sub['costo']:.0f}", '—'],
        ['Cuota',
         f"${cuo['Pd']:.2f}", f"{cuo['cuota']:.0f}", '—',
         f"${cuo['renta_total']:.0f} renta", '—'],
    ]
    story.append(_tabla_datos(filas_cmp,
                              col_widths=[W*0.17,W*0.13,W*0.13,W*0.18,W*0.20,W*0.19]))

    # ── SECCIÓN 6: CONCLUSIONES ──────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("6. Conclusiones Automáticas", es['h1']))

    e_tipo = ("elástica" if e and e > 1 else "inelástica" if e and e < 1 else "unitaria")
    carga_mayor = "compradores" if imp.get('pct_comp',50) >= 50 else "vendedores"

    conclusiones = [
        f"• El mercado alcanza equilibrio en <b>P* = ${params['P_eq']:.2f}</b> y "
        f"<b>Q* = {params['Q_eq']:.0f} unidades</b>. En este punto el bienestar total es máximo.",

        f"• La demanda es <b>{e_tipo}</b> (|η| = {e:.3f}) entre los puntos A y B analizados. "
        f"{'Un aumento de precio reduce el ingreso total de los vendedores.' if e and e > 1 else 'Un aumento de precio incrementa el ingreso total de los vendedores.' if e and e < 1 else 'El ingreso total de los vendedores no varía ante cambios de precio.'}",

        f"• El precio máximo de ${pm['P_max']:.2f} {'genera una escasez de ' + str(int(pm['escasez'])) + ' unidades.' if pm['efectivo'] else 'no tiene efecto real (está por encima del equilibrio).'}",

        f"• El precio mínimo de ${pn['P_min']:.2f} {'genera un excedente de ' + str(int(pn['excedente'])) + ' unidades.' if pn['efectivo'] else 'no tiene efecto real (está por debajo del equilibrio).'}",

        f"• El impuesto de ${imp['t']:.2f}/ud$ genera una recaudación de <b>${imp['recaudacion']:.0f}</b> "
        f"y una pérdida social de <b>${imp['perdida']:.0f}</b>. "
        f"La mayor carga recae sobre los <b>{carga_mayor}</b> ({max(imp['pct_comp'],imp['pct_vend']):.1f}%).",

        f"• El subsidio de ${sub['s']:.2f}/ud implica un costo fiscal de <b>${sub['costo']:.0f}</b> "
        f"para el Estado y aumenta la cantidad transada a {sub['Q']:.0f} unidades.",

        ("• La cuota de " + f"{cuo['cuota']:.0f}" + " unidades " +
         ("genera una renta total de $" + f"{cuo['renta_total']:.0f}" + " para los productores autorizados."
          if cuo['efectiva'] else "no restringe el mercado (es mayor al equilibrio).")),

        "• <b>Regla general:</b> la incidencia impositiva depende de las elasticidades relativas, "
        "no de sobre quién se legisla el impuesto.",
    ]
    for c_txt in conclusiones:
        story.append(Paragraph(c_txt, es['body']))
        story.append(Spacer(1, 0.15*cm))

    # ── PIE ──────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', thickness=0.8, color=rl_colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"UNSTA 2026 · Economía para Ingenieros · "
        f"Alumnas: {params['alumnas']} · Prof. {params['profesor']} · "
        f"Generado: {params['fecha']}",
        es['footer']))

    doc.build(story)
    buf_pdf.seek(0)
    return buf_pdf.read()


# ══════════════════════════════════════════════════════════════════
# SIDEBAR: INGRESO DE DATOS (idéntico a v2)
# ══════════════════════════════════════════════════════════════════

st.sidebar.header("📥 Ingreso de datos del mercado")
metodo_demanda = st.sidebar.radio(
    "Método para la **DEMANDA**:",
    ("Ecuación lineal (Qd = a − bP)", "Dos puntos (P, Qd)"),
    key="metodo_demanda")
metodo_oferta = st.sidebar.radio(
    "Método para la **OFERTA**:",
    ("Ecuación lineal (Qo = c + dP)", "Dos puntos (P, Qo)"),
    key="metodo_oferta")
st.sidebar.divider()

a, b, c, d = 1000.0, 30.0, 20.0, 20.0
errores_validacion = []

st.sidebar.subheader("📉 Demanda")
if metodo_demanda == "Ecuación lineal (Qd = a − bP)":
    a = st.sidebar.number_input("a (intercepto demanda)", value=1000.0, step=50.0, format="%.2f", key="a_dem")
    b = st.sidebar.number_input("b (pendiente demanda, >0)", value=30.0, step=5.0, min_value=0.1, format="%.2f", key="b_dem")
    errores_validacion.extend(validar_demanda(a, b))
    if not errores_validacion:
        st.sidebar.success(f"✅ Qd = {a:.2f} − {b:.2f}·P")
else:
    st.sidebar.markdown("**Dos puntos observados:**")
    col1_dem, col2_dem = st.sidebar.columns(2)
    P1  = col1_dem.number_input("P₁",  value=10.0,  step=5.0,  format="%.2f", key="P1_dem")
    Q1d = col1_dem.number_input("Qd₁", value=700.0, step=50.0, format="%.2f", key="Q1_dem")
    P2  = col2_dem.number_input("P₂",  value=20.0,  step=5.0,  format="%.2f", key="P2_dem")
    Q2d = col2_dem.number_input("Qd₂", value=400.0, step=50.0, format="%.2f", key="Q2_dem")
    errores_validacion.extend(validar_puntos_demanda(P1, Q1d, P2, Q2d))
    if not errores_validacion:
        pend = (Q2d-Q1d)/(P2-P1); b = -pend; a = Q1d+b*P1
        st.sidebar.success(f"✅ Qd = {a:.2f} − {b:.2f}·P")

st.sidebar.subheader("📈 Oferta")
if metodo_oferta == "Ecuación lineal (Qo = c + dP)":
    c = st.sidebar.number_input("c (intercepto oferta)", value=20.0, step=10.0, format="%.2f", key="c_of")
    d = st.sidebar.number_input("d (pendiente oferta, >0)", value=20.0, step=5.0, min_value=0.1, format="%.2f", key="d_of")
    errores_validacion.extend(validar_oferta(c, d))
    if not errores_validacion:
        st.sidebar.success(f"✅ Qo = {c:.2f} + {d:.2f}·P")
else:
    st.sidebar.markdown("**Dos puntos observados:**")
    col1_of, col2_of = st.sidebar.columns(2)
    P1o = col1_of.number_input("P₁",  value=10.0,  step=5.0,  format="%.2f", key="P1_of")
    Q1o = col1_of.number_input("Qo₁", value=200.0, step=50.0, format="%.2f", key="Q1_of")
    P2o = col2_of.number_input("P₂",  value=20.0,  step=5.0,  format="%.2f", key="P2_of")
    Q2o = col2_of.number_input("Qo₂", value=400.0, step=50.0, format="%.2f", key="Q2_of")
    errores_validacion.extend(validar_puntos_oferta(P1o, Q1o, P2o, Q2o))
    if not errores_validacion:
        d = (Q2o-Q1o)/(P2o-P1o); c = Q1o-d*P1o
        st.sidebar.success(f"✅ Qo = {c:.2f} + {d:.2f}·P")

if errores_validacion:
    st.error("⚠️ **Errores de validación económica:**")
    for e_msg in errores_validacion: st.error(e_msg)
    st.stop()

st.sidebar.divider()
st.sidebar.markdown("### 📊 Funciones activas")
st.sidebar.latex(rf"Q_d = {a:.2f} - {b:.2f}P")
st.sidebar.latex(rf"Q_o = {c:.2f} + {d:.2f}P")
st.sidebar.caption("Leyes económicas verificadas ✓")


# ══════════════════════════════════════════════════════════════════
# EQUILIBRIO BASE
# ══════════════════════════════════════════════════════════════════

P_eq_original, Q_eq_original = equilibrio(a, b, c, d)
if P_eq_original is None or Q_eq_original is None or Q_eq_original <= 0:
    st.error("⚠️ Las curvas no se intersectan en el primer cuadrante.")
    st.info("💡 Revisá los parámetros ingresados.")
    st.stop()


# ══════════════════════════════════════════════════════════════════
# MÓDULO 1: MERCADO COMPETITIVO
# ══════════════════════════════════════════════════════════════════

st.markdown('<div class="mod-header">🏪 Módulo 1 — Mercado Competitivo</div>', unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("⚖️ Precio de Equilibrio",   f"${P_eq_original:.2f}")
    st.metric("📦 Cantidad de Equilibrio", f"{Q_eq_original:.0f} unidades")
with col_m2:
    st.markdown("**Demanda:**")
    st.latex(rf"Q_d = {a:.2f} - {b:.2f}P")
    st.caption(f"Método: {metodo_demanda.split('(')[0].strip()}")
with col_m3:
    st.markdown("**Oferta:**")
    st.latex(rf"Q_o = {c:.2f} + {d:.2f}P")
    st.caption(f"Método: {metodo_oferta.split('(')[0].strip()}")

fig_mercado = graficar_mercado(a, b, c, d, P_eq_original, Q_eq_original)
st.pyplot(fig_mercado)


# ══════════════════════════════════════════════════════════════════
# MÓDULO 2: ELASTICIDAD
# ══════════════════════════════════════════════════════════════════

st.markdown('<div class="mod-header">📏 Módulo 2 — Elasticidad de la Demanda (Método Punto Medio)</div>', unsafe_allow_html=True)
st.markdown("Seleccioná dos puntos sobre la curva de demanda para calcular la elasticidad-precio.")

P_A_default = max(1.0, round(P_eq_original * 0.6, 1))
P_B_default = round(P_eq_original * 1.4, 1)
P_max_curva = round(a / b * 0.97, 1) if b > 0 else P_eq_original * 2

col_e1, col_e2 = st.columns(2)
with col_e1:
    st.markdown("**Punto A**")
    P_A = st.slider("Precio en A", min_value=0.5, max_value=float(P_max_curva),
                    value=float(P_A_default), step=0.5, key="PA_slider")
    Q_A = max(0.0, a - b * P_A)
    st.metric("Cantidad en A", f"{Q_A:.0f} unidades")
    st.metric("Ingreso Total de los vendedores en A", f"${P_A * Q_A:.0f}")
with col_e2:
    st.markdown("**Punto B**")
    P_B = st.slider("Precio en B", min_value=0.5, max_value=float(P_max_curva),
                    value=float(P_B_default), step=0.5, key="PB_slider")
    Q_B = max(0.0, a - b * P_B)
    st.metric("Cantidad en B", f"{Q_B:.0f} unidades")
    st.metric("Ingreso Total de los vendedores en B", f"${P_B * Q_B:.0f}")

elasticidad = elasticidad_punto_medio(P_A, Q_A, P_B, Q_B)
fig_elasticidad = None

if not elasticidad:
    st.warning("⚠️ Los precios A y B son muy similares. Separá más los puntos.")
else:
    col_elast1, col_elast2 = st.columns([1, 2])
    with col_elast1:
        st.metric("Elasticidad-precio |η|", f"{elasticidad:.3f}")
    with col_elast2:
        if elasticidad > 1:
            st.success("📈 Demanda **ELÁSTICA**  (|η| > 1)")
            st.markdown('<div class="caja-info">Los consumidores son <b>muy sensibles</b> al precio. El Ingreso Total de los vendedores <b>disminuye</b> cuando el precio sube.</div>', unsafe_allow_html=True)
        elif elasticidad < 1:
            st.warning("📉 Demanda **INELÁSTICA**  (|η| < 1)")
            st.markdown('<div class="caja-info">Los consumidores son <b>poco sensibles</b> al precio. El Ingreso Total de los vendedores <b>aumenta</b> cuando el precio sube.</div>', unsafe_allow_html=True)
        else:
            st.info("⚖️ Demanda **UNITARIA**  (|η| = 1)")
            st.markdown('<div class="caja-info">El Ingreso Total de los vendedores <b>no varía</b> ante cambios de precio.</div>', unsafe_allow_html=True)

    with st.expander("🔢 Ver cálculo paso a paso"):
        dQ = Q_B-Q_A; dP = P_B-P_A
        mQ = (Q_A+Q_B)/2; mP = (P_A+P_B)/2
        pQ = (dQ/mQ)*100 if mQ!=0 else 0
        pP = (dP/mP)*100 if mP!=0 else 0
        st.markdown(f"""
| Paso | Cálculo | Resultado |
|---|---|---|
| ΔQ | Q_B − Q_A | {dQ:+.2f} |
| ΔP | P_B − P_A | {dP:+.2f} |
| Q̄  | (Q_A + Q_B) / 2 | {mQ:.2f} |
| P̄  | (P_A + P_B) / 2 | {mP:.2f} |
| %ΔQ | ΔQ / Q̄ | {pQ:.2f}% |
| %ΔP | ΔP / P̄ | {pP:.2f}% |
| **|η|** | **|%ΔQ / %ΔP|** | **{elasticidad:.4f}** |
""")

    fig_elasticidad = graficar_elasticidad(a, b, P_A, Q_A, P_B, Q_B, P_eq_original, Q_eq_original)
    st.pyplot(fig_elasticidad)


# ══════════════════════════════════════════════════════════════════
# MÓDULO 3: INTERVENCIONES
# ══════════════════════════════════════════════════════════════════

st.markdown('<div class="mod-header">🏛️ Módulo 3 — Intervenciones del Estado</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💰 Precio Máximo","💎 Precio Mínimo","🏷️ Impuesto","🎁 Subsidio","📉 Cuota"])

# ── TAB 1: PRECIO MÁXIMO ─────────────────────────────────────────
with tab1:
    st.subheader("Precio Máximo (Techo de Precio)")
    st.caption("Un precio máximo efectivo está POR DEBAJO del precio de equilibrio.")
    P_max_def = max(5.0, round(P_eq_original * 0.6, 1))

    P_max = st.slider("Precio máximo ($)", 
        min_value=1.0,
        max_value=float(P_eq_original * 1.5), 
        value=float(P_max_def),
        step=0.5, 
        key="pmax_slider")

    Qd_pmax = max(0.0, a-b*P_max); Qo_pmax = max(0.0, c+d*P_max)
    escasez = max(0.0, Qd_pmax-Qo_pmax); efectivo_pm = P_max < P_eq_original
    col1,col2,col3 = st.columns(3)
    col1.metric("Cantidad Demandada", f"{Qd_pmax:.0f}")
    col2.metric("Cantidad Ofrecida",  f"{Qo_pmax:.0f}")
    col3.metric("Escasez", f"{escasez:.0f} unidades",
                delta="⚠️ P_máx < P* → activa" if efectivo_pm else "✅ P_máx ≥ P* → sin efecto", delta_color="off")
    if efectivo_pm:
        st.markdown(f'<div class="caja-warn">⚠️ <b>Precio máximo efectivo</b> — está por debajo del equilibrio (${P_eq_original:.2f}). Genera escasez de <b>{escasez:.0f} unidades</b>. La cantidad intercambiada es Qo = {Qo_pmax:.0f}.</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="caja-info">ℹ️ El precio máximo ingresado (<b>${P_max:.2f}</b>) es mayor o igual al precio de equilibrio '
            f'(<b>${P_eq_original:.2f}</b>). Por lo tanto, la medida <b>NO es relevante</b> y el mercado '
            f'permanece en equilibrio libre (P* = ${P_eq_original:.2f}, Q* = {Q_eq_original:.0f}). '
            f'No se produce escasez.</div>',
            unsafe_allow_html=True
        )
    fig_pmax = graficar_precio_maximo(a, b, c, d, P_eq_original, Q_eq_original, P_max, efectivo=efectivo_pm)
    st.pyplot(fig_pmax)
    with st.expander("📖 Explicación económica"):
        if efectivo_pm:
            st.markdown("**¿Qué ocurre?** El techo fija el precio por debajo del equilibrio. Los compradores demandan más de lo que los vendedores ofrecen → escasez.\n\n**Gana:** compradores que logran comprar. **Pierde:** vendedores y compradores excluidos.\n\n**Consecuencias:** colas, mercado negro, deterioro de calidad.")
        else:
            st.markdown("**¿Por qué no tiene efecto?** Si el gobierno dice 'el máximo es $150$' pero el mercado libre ya fija el precio en $100, la ley no prohíbe nada. Las fuerzas de oferta y demanda siguen operando normalmente. **Un precio máximo solo es relevante cuando se ubica POR DEBAJO del equilibrio.**")

# ── TAB 2: PRECIO MÍNIMO ─────────────────────────────────────────
with tab2:
    st.subheader("Precio Mínimo (Piso de Precio)")
    st.caption("Un precio mínimo efectivo está POR ENCIMA del precio de equilibrio.")
    P_min_def = round(P_eq_original * 1.4, 1)

    P_min = st.slider("Precio mínimo ($)", 
        min_value=1.0,
        max_value=float(P_eq_original * 2.5), 
        value=float(P_min_def),
        step=0.5, 
        key="pmin_slider")

    Qd_pmin = max(0.0, a-b*P_min); Qo_pmin = max(0.0, c+d*P_min)
    excedente = max(0.0, Qo_pmin-Qd_pmin); efectivo_pn = P_min > P_eq_original
    col1,col2,col3 = st.columns(3)
    col1.metric("Cantidad Demandada", f"{Qd_pmin:.0f}")
    col2.metric("Cantidad Ofrecida",  f"{Qo_pmin:.0f}")
    col3.metric("Excedente", f"{excedente:.0f} unidades",
                delta="⚠️ P_mín > P* → activo" if efectivo_pn else "✅ P_mín ≤ P* → sin efecto", delta_color="off")
    if efectivo_pn:
        st.markdown(f'<div class="caja-warn">⚠️ <b>Precio mínimo efectivo</b> — está por encima del equilibrio (${P_eq_original:.2f}). Genera excedente de <b>{excedente:.0f} unidades</b>. La cantidad intercambiada es Qd = {Qd_pmin:.0f}.</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="caja-info">ℹ️ El precio mínimo ingresado (<b>${P_min:.2f}</b>) es menor o igual al precio de equilibrio '
            f'(<b>${P_eq_original:.2f}</b>). Por lo tanto, la medida <b>NO es relevante</b> y el mercado '
            f'permanece en equilibrio libre (P* = ${P_eq_original:.2f}, Q* = {Q_eq_original:.0f}). '
            f'No se produce excedente.</div>',
            unsafe_allow_html=True
        )
    fig_pmin = graficar_precio_minimo(a, b, c, d, P_eq_original, Q_eq_original, P_min, efectivo=efectivo_pn)
    st.pyplot(fig_pmin)
    with st.expander("📖 Explicación económica"):
        if efectivo_pn:
            st.markdown("**¿Qué ocurre?** El piso fija el precio por encima del equilibrio. Los vendedores ofrecen más de lo que los compradores demandan → excedente.\n\n**Gana:** vendedores que logran vender. **Pierde:** compradores y vendedores excluidos.\n\n**Casos reales:** salario mínimo, precios sostén agropecuarios.")
        else:
            st.markdown("**¿Por qué no tiene efecto?** Si el equilibrio es $100$ y el gobierno dice 'nadie puede cobrar menos de $60', a nadie le importa porque ya se cobra $100. **Un precio mínimo solo es relevante cuando se ubica POR ENCIMA del equilibrio.**")

# ── TAB 3: IMPUESTO ──────────────────────────────────────────────
with tab3:
    st.subheader("Impuesto por Unidad")
    col_tipo, col_sl = st.columns([1,2])
    with col_tipo:
        sobre_vendedores = st.radio("Impuesto sobre:", ["Vendedores","Compradores"], key="tax_sobre") == "Vendedores"
        st.caption("La carga se distribuye según elasticidades, no según la legislación.")
    with col_sl:
        t = st.slider("Impuesto por unidad ($)", min_value=0.0,
                      max_value=float(P_eq_original*0.8),
                      value=round(float(P_eq_original*0.12),1), step=0.5, key="tax_slider")
    P_eq_tax = (a-c+d*t)/(b+d); Q_eq_tax = max(0.0,a-b*P_eq_tax)
    P_vendedor = max(0.0, P_eq_tax-t); recaudacion = t*Q_eq_tax
    inc_c = (P_eq_tax-P_eq_original)*Q_eq_tax; inc_v = (P_eq_original-P_vendedor)*Q_eq_tax
    tot = inc_c+inc_v; pct_c = (inc_c/tot*100) if tot>0 else 50; pct_v = 100-pct_c
    perdida_imp = 0.5*t*abs(Q_eq_original-Q_eq_tax)
    col1,col2 = st.columns(2)
    with col1:
        st.metric("Precio que PAGA el comprador", f"${P_eq_tax:.2f}", delta=f"+${P_eq_tax-P_eq_original:.2f}")
        st.metric("Precio que RECIBE el vendedor",f"${P_vendedor:.2f}", delta=f"-${P_eq_original-P_vendedor:.2f}")
        st.metric("Cantidad transada", f"{Q_eq_tax:.1f} unidades")
    with col2:
        st.metric("Recaudación del Estado", f"${recaudacion:.2f}")
        st.metric("Pérdida social (DWL)",   f"${perdida_imp:.2f}")
        st.metric("Carga sobre comprador",  f"{pct_c:.1f}%")
        st.metric("Carga sobre vendedor",   f"{pct_v:.1f}%")
    st.markdown(f'<div class="caja-info">📊 <b>Incidencia:</b> comprador {pct_c:.1f}% · vendedor {pct_v:.1f}%. La carga recae sobre el lado <b>menos elástico</b> del mercado.</div>', unsafe_allow_html=True)
    fig_imp, _, _, _, _, _ = graficar_impuesto(a,b,c,d,P_eq_original,Q_eq_original,t,sobre_vendedores)
    st.pyplot(fig_imp)
    with st.expander("📖 Explicación económica"):
        st.markdown(f"El impuesto de ${t:.2f}/ud$ desplaza la curva, genera brecha entre Pc y Pv, recaudación de ${recaudacion:.0f}$ y pérdida social de ${perdida_imp:.0f}.")

# ── TAB 4: SUBSIDIO ──────────────────────────────────────────────
with tab4:
    st.subheader("Subsidio por Unidad (a los vendedores)")
    s = st.slider("Subsidio por unidad ($)", min_value=0.0,
                  max_value=float(P_eq_original*0.8),
                  value=round(float(P_eq_original*0.10),1), step=0.5, key="subs_slider")
    P_eq_subs = (a-c-d*s)/(b+d); Q_eq_subs = max(0.0,a-b*P_eq_subs)
    P_vend_subs = P_eq_subs+s; costo_fiscal = s*Q_eq_subs
    col1,col2 = st.columns(2)
    with col1:
        st.metric("Precio comprador", f"${max(0,P_eq_subs):.2f}", delta=f"-${max(0,P_eq_original-P_eq_subs):.2f}")
        st.metric("Precio vendedor",  f"${P_vend_subs:.2f}",      delta=f"+${max(0,P_vend_subs-P_eq_original):.2f}")
    with col2:
        st.metric("Nueva cantidad",    f"{Q_eq_subs:.0f} unidades")
        st.metric("Costo fiscal total",f"${costo_fiscal:.2f}")
    st.markdown(f'<div class="caja-info">💡 Costo fiscal <b>${costo_fiscal:.0f}</b>. Genera pérdida de bienestar neta por sobreproducción.</div>', unsafe_allow_html=True)
    fig_sub, _, _, _, _ = graficar_subsidio(a,b,c,d,P_eq_original,Q_eq_original,s)
    st.pyplot(fig_sub)
    with st.expander("📖 Explicación económica"):
        st.markdown(f"El subsidio de ${s:.2f}/unidad$ desplaza la oferta hacia abajo. El precio baja para compradores y sube para vendedores. El Estado asume un costo de ${costo_fiscal:.0f}.")

# ── TAB 5: CUOTA ─────────────────────────────────────────────────
with tab5:
    st.subheader("Cuota de Producción")
    st.caption("Limita la cantidad máxima que puede ofrecerse en el mercado.")
    cuota_def = round(Q_eq_original*0.7, 0)
    cuota = st.slider("Límite de cantidad ofrecida (unidades)", min_value=1.0,
                      max_value=float(Q_eq_original*1.5), value=float(cuota_def),
                      step=5.0, key="cuota_slider")
    if b == 0:
        st.error("Demanda vertical: no se puede calcular el precio.")
    else:
        P_cuota    = (a-cuota)/b
        P_of_cuota = (cuota-c)/d if d!=0 else 0
        renta_u    = max(0.0, P_cuota-P_of_cuota)
        renta_tot  = renta_u*cuota
        ef_cuota   = cuota < Q_eq_original
        col1,col2 = st.columns(2)
        with col1:
            st.metric("Precio de mercado", f"${max(0,P_cuota):.2f}",
                      delta=f"+${max(0,P_cuota-P_eq_original):.2f}" if ef_cuota else "Sin cambio")
            st.metric("Cantidad transada", f"{cuota:.0f} unidades")
        with col2:
            st.metric("Precio al productor",    f"${max(0,P_of_cuota):.2f}")
            st.metric("Renta por unidad",       f"${renta_u:.2f}")
            st.metric("Renta total productores",f"${renta_tot:.0f}")
        if ef_cuota:
            st.markdown(f'<div class="caja-warn">⚠️ <b>Cuota efectiva</b> — renta total <b>${renta_tot:.0f}</b> para productores autorizados.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="caja-ok">✅ No efectiva — el mercado opera libremente.</div>', unsafe_allow_html=True)
        fig_cuota, _, _, _ = graficar_cuota(a,b,c,d,P_eq_original,Q_eq_original,cuota)
        st.pyplot(fig_cuota)
        with st.expander("📖 Explicación económica"):
            st.markdown(f"La cuota de **{cuota:.0f} unidades** restringe la oferta. Sube el precio a ${max(0,P_cuota):.2f}. Los productores autorizados capturan la renta.")


# ══════════════════════════════════════════════════════════════════
# MÓDULO 4: COMPARACIÓN DE ESCENARIOS  (NUEVO)
# ══════════════════════════════════════════════════════════════════

st.markdown('<div class="mod-header">📊 Módulo 4 — Comparación de Escenarios</div>', unsafe_allow_html=True)
st.markdown("Compará el efecto de cada intervención sobre precio, cantidad y bienestar.")

# Calcular todos los valores con parámetros actuales de los sliders
_Pc_imp = (a-c+d*t)/(b+d) if 't' in dir() else P_eq_original
_Q_imp  = max(0.0, a-b*_Pc_imp)
_P_cuota_val = (a-cuota)/b if b!=0 and 'cuota' in dir() else P_eq_original
_cuota_val   = cuota if 'cuota' in dir() else Q_eq_original

datos_esc = [
    {'nombre':'Mercado libre', 'precio':P_eq_original,        'cantidad':Q_eq_original,
     'escasez':0,'excedente':0,'recaudacion':0,'perdida':0,
     'color':'#1a56db'},
    {'nombre':'Precio Máximo', 'precio':P_max if 'P_max' in dir() else P_eq_original*0.6,
     'cantidad':max(0,c+d*(P_max if 'P_max' in dir() else P_eq_original*0.6)),
     'escasez':escasez if 'escasez' in dir() else 0,'excedente':0,'recaudacion':0,'perdida':0,
     'color':'#ef4444'},
    {'nombre':'Precio Mínimo', 'precio':P_min if 'P_min' in dir() else P_eq_original*1.4,
     'cantidad':max(0,a-b*(P_min if 'P_min' in dir() else P_eq_original*1.4)),
     'escasez':0,'excedente':excedente if 'excedente' in dir() else 0,'recaudacion':0,'perdida':0,
     'color':'#16a34a'},
    {'nombre':'Impuesto',      'precio':_Pc_imp, 'cantidad':_Q_imp,
     'escasez':0,'excedente':0,
     'recaudacion':t*_Q_imp if 't' in dir() else 0,
     'perdida':0.5*(t if 't' in dir() else 0)*abs(Q_eq_original-_Q_imp),
     'color':'#7e3af2'},
    {'nombre':'Subsidio',      'precio':max(0,P_eq_subs) if 'P_eq_subs' in dir() else P_eq_original,
     'cantidad':Q_eq_subs if 'Q_eq_subs' in dir() else Q_eq_original,
     'escasez':0,'excedente':0,
     'recaudacion':-(costo_fiscal if 'costo_fiscal' in dir() else 0),
     'perdida':0.5*(s if 's' in dir() else 0)*abs(Q_eq_subs - Q_eq_original) if 's' in dir() and 'Q_eq_subs' in dir() else 0,
     'color':'#0891b2'},
    {'nombre':'Cuota',         'precio':max(0,_P_cuota_val),
     'cantidad':_cuota_val,
     'escasez':0,'excedente':0,'recaudacion':0,
     'perdida':0.5 * max(0, (a-_cuota_val)/b - (_cuota_val-c)/d) * (Q_eq_original - _cuota_val) if 'cuota' in dir() and _cuota_val < Q_eq_original else 0,
     'color':'#e3a008'},
]

todos_nombres = [esc_d['nombre'] for esc_d in datos_esc]
sel = st.multiselect("Seleccioná los escenarios a comparar:",
                     todos_nombres, default=todos_nombres, key="comp_sel")

if sel:
    datos_fil = [esc_d for esc_d in datos_esc if esc_d['nombre'] in sel]

    # Tabla resumen
    st.markdown("#### Tabla comparativa")
    filas_tabla = [["Escenario","Precio ($)","Cantidad","Escasez / Excedente","Recaudación / Costo","Pérdida Social"]]
    for esc_d in datos_fil:
        esc_exc = (f"Esc. {esc_d['escasez']:.0f}" if esc_d['escasez']>0 else
                   f"Exc. {esc_d['excedente']:.0f}" if esc_d['excedente']>0 else "—")
        rec = f"${abs(esc_d['recaudacion']):.0f}" + (" ❌" if esc_d['recaudacion']<0 else "")
        filas_tabla.append([
            esc_d['nombre'], f"${esc_d['precio']:.2f}", f"{esc_d['cantidad']:.0f}",
            esc_exc, rec if esc_d['recaudacion']!=0 else "—",
            f"${esc_d['perdida']:.0f}" if esc_d['perdida']>0 else "—"
        ])
    # Renderizar como tabla markdown
    hdr = "| " + " | ".join(filas_tabla[0]) + " |"
    sep = "| " + " | ".join(["---"]*len(filas_tabla[0])) + " |"
    rows = "\n".join("| " + " | ".join(r) + " |" for r in filas_tabla[1:])
    st.markdown(f"{hdr}\n{sep}\n{rows}")

    # Gráfico comparativo
    fig_comp = graficar_comparativo(sel, datos_esc)
    if fig_comp:
        st.pyplot(fig_comp)

    # Métricas rápidas
    st.markdown("#### Resumen rápido")
    n_col = min(len(datos_fil), 6)
    cols_comp = st.columns(n_col)
    for i, esc_d in enumerate(datos_fil[:n_col]):
        with cols_comp[i]:
            delta_p = esc_d['precio'] - P_eq_original
            st.metric(esc_d['nombre'], f"${esc_d['precio']:.2f}",
                      delta=f"{delta_p:+.2f} vs libre",
                      delta_color="inverse" if delta_p>0 else "normal")
else:
    st.info("Seleccioná al menos un escenario para ver la comparación.")


# ══════════════════════════════════════════════════════════════════
# RESUMEN ECONÓMICO (idéntico a v2)
# ══════════════════════════════════════════════════════════════════

st.markdown('<div class="mod-header">📖 Resumen Económico</div>', unsafe_allow_html=True)
st.markdown("""
### ¿Qué ocurre con cada intervención?

| Intervención | Efecto principal | Quién gana | Quién pierde |
|---|---|---|---|
| **Precio máximo** | Escasez | Compradores que logran comprar | Vendedores y excluidos |
| **Precio mínimo** | Excedente | Vendedores que logran vender | Compradores y excluidos |
| **Impuesto** | Cantidad cae | Estado (recauda) | Compradores y vendedores |
| **Subsidio** | Cantidad sube | Compradores y vendedores | Estado (contribuyentes) |
| **Cuota** | Restricción | Productores con cuota | Consumidores |

### Elasticidad e incidencia impositiva
- **Demanda inelástica** → compradores soportan **más** del impuesto
- **Demanda elástica** → vendedores soportan **más** del impuesto
- **Oferta inelástica** → vendedores soportan **más** del impuesto
- **Oferta elástica** → compradores soportan **más** del impuesto

> La carga tributaria real depende de las elasticidades, **no** de sobre quién se legisla.
""")


# ══════════════════════════════════════════════════════════════════
# EXPORTAR PDF  (NUEVO)
# ══════════════════════════════════════════════════════════════════

st.markdown('<div class="mod-header">📄 Exportar Informe PDF</div>', unsafe_allow_html=True)
st.markdown("Generá un informe académico completo con todos los resultados y gráficos.")

col_pdf1, col_pdf2 = st.columns([3, 1])
with col_pdf1:
    st.markdown(
        "El PDF incluye: parámetros, ecuaciones, equilibrio, elasticidad, "
        "todas las intervenciones, tabla comparativa y conclusiones automáticas."
    )
with col_pdf2:
    generar_btn = st.button("⚙️ Preparar PDF", type="primary", use_container_width=True)

if generar_btn:
    with st.spinner("Generando informe PDF..."):

        # Preparar todos los gráficos (regenerar para que estén limpios)
        _fig_mercado    = graficar_mercado(a,b,c,d,P_eq_original,Q_eq_original)
        _fig_elasticidad= (graficar_elasticidad(a,b,P_A,Q_A,P_B,Q_B,P_eq_original,Q_eq_original)
                           if elasticidad else None)
        _fig_pmax       = graficar_precio_maximo(a,b,c,d,P_eq_original,Q_eq_original,P_max, efectivo=efectivo_pm)
        _fig_pmin       = graficar_precio_minimo(a,b,c,d,P_eq_original,Q_eq_original,P_min, efectivo=efectivo_pn)
        _fig_imp,_rec,_dw,_Pc,_Pv,_Qn = graficar_impuesto(a,b,c,d,P_eq_original,Q_eq_original,t,sobre_vendedores)
        _fig_sub,_ct,_Pcs,_Pvs,_Qs    = graficar_subsidio(a,b,c,d,P_eq_original,Q_eq_original,s)
        _fig_cuo,_Pd_c,_Po_c,_ru_c    = graficar_cuota(a,b,c,d,P_eq_original,Q_eq_original,cuota)

        _P_eq_tax2 = (a-c+d*t)/(b+d); _Q_eq_tax2 = max(0.0,a-b*_P_eq_tax2)
        _Pv2       = max(0.0,_P_eq_tax2-t); _rec2 = t*_Q_eq_tax2
        _inc_c2    = (_P_eq_tax2-P_eq_original)*_Q_eq_tax2
        _inc_v2    = (P_eq_original-_Pv2)*_Q_eq_tax2
        _tot2      = _inc_c2+_inc_v2
        _pc_c2     = (_inc_c2/_tot2*100) if _tot2>0 else 50
        _dw2       = 0.5*t*abs(Q_eq_original-_Q_eq_tax2)

        params_pdf = {
            'alumnas'  : 'Abregú Candela · Amin Guadalupe · Pasteris Luciana',
            'profesor' : 'Raúl García',
            'fecha'    : datetime.date.today().strftime('%d/%m/%Y'),
            'metodo_dem': metodo_demanda.split('(')[0].strip(),
            'metodo_of' : metodo_oferta.split('(')[0].strip(),
            'a':a,'b':b,'c':c,'d':d,
            'P_eq':P_eq_original,'Q_eq':Q_eq_original,
            'P_A':P_A,'Q_A':Q_A,'P_B':P_B,'Q_B':Q_B,
            'elasticidad': elasticidad,
            'precio_max': {'P_max':P_max,'Qd':Qd_pmax,'Qo':Qo_pmax,
                           'escasez':escasez,'efectivo':efectivo_pm},
            'precio_min': {'P_min':P_min,'Qd':Qd_pmin,'Qo':Qo_pmin,
                           'excedente':excedente,'efectivo':efectivo_pn},
            'impuesto':   {'t':t,'sobre':'Vendedores' if sobre_vendedores else 'Compradores',
                           'Pc':_P_eq_tax2,'Pv':_Pv2,'Q':_Q_eq_tax2,
                           'recaudacion':_rec2,'perdida':_dw2,
                           'pct_comp':_pc_c2,'pct_vend':100-_pc_c2},
            'subsidio':   {'s':s,'Pc':_Pcs,'Pv':_Pvs,'Q':_Qs,'costo':_ct},
            'cuota':      {'cuota':cuota,'Pd':_Pd_c,'Po':_Po_c,
                           'renta_u':_ru_c,'renta_total':_ru_c*cuota,
                           'efectiva':cuota<Q_eq_original},
            'fig_mercado'    : _fig_mercado,
            'fig_elasticidad': _fig_elasticidad,
            'fig_pmax'       : _fig_pmax,
            'fig_pmin'       : _fig_pmin,
            'fig_impuesto'   : _fig_imp,
            'fig_subsidio'   : _fig_sub,
            'fig_cuota'      : _fig_cuo,
        }

        pdf_bytes = generar_pdf(params_pdf)

        # Cerrar todas las figuras para liberar memoria
        for _f in [_fig_mercado,_fig_elasticidad,_fig_pmax,_fig_pmin,
                   _fig_imp,_fig_sub,_fig_cuo]:
            if _f: plt.close(_f)

    st.success("✅ PDF listo para descargar.")
    nombre_archivo = f"Informe_Mercado_UNSTA_{datetime.date.today().strftime('%Y%m%d')}.pdf"
    st.download_button(
        label="📄 Descargar Informe PDF",
        data=pdf_bytes,
        file_name=nombre_archivo,
        mime="application/pdf",
        use_container_width=True,
    )


# ══════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════

st.divider()
st.caption(
    "UNSTA 2026 · Economía para Ingenieros · "
    "Alumnas: Abregú Candela · Amin Guadalupe · Pasteris Luciana · "
    "Prof. Raúl García"
)

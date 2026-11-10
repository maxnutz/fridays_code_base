import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")

with app.setup:
    import matplotlib.dates as mdates
    import matplotlib.patheffects as pe
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np
    import pandas as pd
    from matplotlib.axes import Axes


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Inflation im Euroraum – getrieben von Energiepreisen

    Daten: Eurostat HICP, Euroraum (`prc_hicp_minr`, `prc_hicp_ctr`),
    Jan 2019 – Okt 2026.
    Okt 2026 ist eine Schnellschätzung, Beiträge dafür sind noch nicht veröffentlicht.
    Details: `../resources/Windkraft/euro_area_inflation_README.md`.
    """)
    return


@app.cell
def _():
    DATA_CSV = "resources/Windkraft/euro_area_inflation_2019-2026.csv"
    OUTPUT_HEADLINE_PNG = "Windkraft/output/inflation_euroraum.png"
    OUTPUT_BEITRAEGE_PNG = "Windkraft/output/inflation_beitraege_energie.png"

    df = pd.read_csv(DATA_CSV)
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    df = df.set_index("month")
    df
    return OUTPUT_BEITRAEGE_PNG, OUTPUT_HEADLINE_PNG, df


@app.cell
def _():
    # Gemeinsame Optik für beide Grafiken (dunkle Schrift für helle Folien)
    FIGSIZE = (11, 5.5)
    TEXT = "#1F2933"
    FARBE_HEADLINE = "#1F2933"
    FARBE_ZIEL = "#6B7280"

    # Energie hervorgehoben (warm), alles andere zurückhaltend in Grautönen
    BEITRAEGE = {
        "energy_pp": ("Energie", "#D1495B"),
        "food_alcohol_tobacco_pp": ("Lebensmittel, Alkohol, Tabak", "#C99A2E"),
        "non_energy_industrial_goods_pp": ("Industriegüter (ohne Energie)", "#3A6EA5"),
        "services_pp": ("Dienstleistungen", "#5FA8A3"),
    }
    return BEITRAEGE, FARBE_HEADLINE, FARBE_ZIEL, FIGSIZE, TEXT


@app.function(hide_code=True)
def prozent(wert: float) -> str:
    """Formatiert einen Prozentwert deutsch, z. B. 10.6 -> '10,6 %'."""
    return f"{wert:.1f} %".replace(".", ",")


@app.function(hide_code=True)
def style_axes(ax: Axes, titel: str, text: str = "#1F2933") -> None:
    """Einheitliche, entschlackte Optik für beide Inflationsgrafiken."""
    ax.set_title(titel, fontsize=19, fontweight="bold", pad=18, color=text)
    ax.set_ylabel("Inflation gegenüber Vorjahr", fontsize=12, color=text)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda y, _: f"{y:.0f} %".replace("-", "−"))
    )
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(pd.Timestamp("2018-11-15"), pd.Timestamp("2027-01-31"))
    ax.axhline(0, color=text, linewidth=0.8, zorder=2)
    ax.grid(axis="y", color="#D9DCE1", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "bottom"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(text)
    ax.tick_params(axis="both", labelsize=12, length=0, colors=text)


@app.cell
def _(FARBE_HEADLINE, FARBE_ZIEL, FIGSIZE, OUTPUT_HEADLINE_PNG, TEXT, df):
    # --- Grafik 1: Gesamtinflation ---
    fig_headline, ax_h = plt.subplots(figsize=FIGSIZE, dpi=130)

    ax_h.plot(
        df.index,
        df["headline_inflation_pct"],
        color=FARBE_HEADLINE,
        linewidth=2.5,
        zorder=4,
    )
    ax_h.axhline(2, color=FARBE_ZIEL, linewidth=1.2, linestyle="--", zorder=3)
    ax_h.text(
        df.index[0], 2.25, "EZB-Ziel 2 %", color=FARBE_ZIEL, fontsize=11, va="bottom"
    )

    # Höchstwert markieren
    peak_monat = df["headline_inflation_pct"].idxmax()
    peak_wert = df.loc[peak_monat, "headline_inflation_pct"]
    ax_h.scatter([peak_monat], [peak_wert], s=60, color=FARBE_HEADLINE, zorder=5)
    ax_h.annotate(
        f"{prozent(peak_wert)}\n{peak_monat:%m/%Y}",
        xy=(peak_monat, peak_wert),
        xytext=(14, -4),
        textcoords="offset points",
        fontsize=13,
        fontweight="bold",
        color=TEXT,
        va="top",
    )

    # Letzten Wert beschriften
    letzter_monat = df.index[-1]
    letzter_wert = df.loc[letzter_monat, "headline_inflation_pct"]
    ax_h.annotate(
        prozent(letzter_wert),
        xy=(letzter_monat, letzter_wert),
        xytext=(6, 0),
        textcoords="offset points",
        fontsize=12,
        fontweight="bold",
        color=TEXT,
        va="center",
    )

    style_axes(ax_h, "Inflation im Euroraum 2019–2026", TEXT)
    ax_h.set_ylim(-2, 12)

    fig_headline.tight_layout()
    fig_headline.savefig(
        OUTPUT_HEADLINE_PNG, dpi=200, bbox_inches="tight", transparent=True
    )
    fig_headline
    return


@app.cell
def _(BEITRAEGE, FARBE_HEADLINE, FIGSIZE, OUTPUT_BEITRAEGE_PNG, TEXT, df):
    # --- Grafik 2: Beiträge zur Inflation, Energie hervorgehoben ---
    fig_beitraege, ax_b = plt.subplots(figsize=FIGSIZE, dpi=130)

    beitraege = df[list(BEITRAEGE)].dropna()
    breite = 24  # Tage, damit zwischen Monatsbalken eine Lücke bleibt
    # Energie zuerst, damit sie direkt an der Nulllinie sitzt
    pos_basis = pd.Series(0.0, index=beitraege.index)
    neg_basis = pos_basis.copy()
    for spalte, (label, farbe) in BEITRAEGE.items():
        werte = beitraege[spalte]
        pos = werte.clip(lower=0)
        neg = werte.clip(upper=0)
        ax_b.bar(
            beitraege.index,
            pos,
            width=breite,
            bottom=pos_basis,
            color=farbe,
            label=label,
            zorder=3,
        )
        ax_b.bar(
            beitraege.index, neg, width=breite, bottom=neg_basis, color=farbe, zorder=3
        )
        pos_basis = pos_basis + pos
        neg_basis = neg_basis + neg

    ax_b.plot(
        df.index,
        df["headline_inflation_pct"],
        color=FARBE_HEADLINE,
        linewidth=2.5,
        label="Gesamtinflation",
        zorder=4,
        path_effects=[pe.Stroke(linewidth=5, foreground="white"), pe.Normal()],
    )

    # Energieanteil am Höchststand und im letzten Monat mit Beiträgen beschriften
    peak = df["headline_inflation_pct"].idxmax()
    letzter = beitraege.index[-1]
    for monat, text_pos in ((peak, (2023.9, 9.6)), (letzter, (2024.6, 6.2))):
        energie = df.loc[monat, "energy_pp"]
        anteil = energie / df.loc[monat, "headline_inflation_pct"] * 100
        x_text = pd.Timestamp(year=int(text_pos[0]), month=1, day=1) + pd.Timedelta(
            days=(text_pos[0] % 1) * 365
        )
        ax_b.annotate(
            f"{monat:%m/%Y}: Energie {prozent(energie).replace(' %', '')} Pp.\n"
            f"≈ {anteil:.0f} % der Inflation",
            xy=(monat, energie * 0.6),
            xytext=(x_text, text_pos[1]),
            fontsize=12,
            fontweight="bold",
            color=TEXT,
            arrowprops={"arrowstyle": "->", "color": TEXT, "linewidth": 1.2},
            zorder=6,
        )

    style_axes(ax_b, "Was treibt die Inflation? Der Einfluss der Energie", TEXT)
    ax_b.set_ylim(-2, 12)
    legende = ax_b.legend(loc="upper left", frameon=False, fontsize=11, labelcolor=TEXT)
    legende.set_zorder(5)

    fig_beitraege.tight_layout()
    fig_beitraege.savefig(
        OUTPUT_BEITRAEGE_PNG, dpi=200, bbox_inches="tight", transparent=True
    )
    fig_beitraege
    return


@app.cell
def _(FIGSIZE, TEXT):
    # --- Grafik 3: Wertschöpfung in Österreich, Erneuerbare vs. Fossile ---
    WERTSCHOEPFUNG_CSV = "resources/Windkraft/wertschoepfung_ee_fe.csv"
    OUTPUT_WERTSCHOEPFUNG_PNG = "Windkraft/output/wertschoepfung_ee_fe.png"
    FARBE_EE = "#2E8B57"
    FARBE_EE_GESAMT = "#1B5E3A"
    FARBE_FOSSIL = "#9CA3AF"

    ws = pd.read_csv(WERTSCHOEPFUNG_CSV).sort_values(
        "Wertschoepfung_Oesterreich_Mio_EUR"
    )
    farben = [
        FARBE_FOSSIL
        if t == "Fossile"
        else FARBE_EE_GESAMT
        if t == "Erneuerbare gesamt"
        else FARBE_EE
        for t in ws["Technologie"]
    ]

    fig_ws, ax_w = plt.subplots(figsize=FIGSIZE, dpi=130)
    ax_w.barh(
        ws["Technologie"],
        ws["Wertschoepfung_Oesterreich_Mio_EUR"],
        color=farben,
        height=0.65,
        zorder=3,
    )
    for y, wert in enumerate(ws["Wertschoepfung_Oesterreich_Mio_EUR"]):
        ax_w.text(
            wert + 0.015,
            y,
            f"{wert:.2f}".replace(".", ","),
            va="center",
            fontsize=12,
            fontweight="bold",
            color=TEXT,
        )

    ee = ws.set_index("Technologie")["Wertschoepfung_Oesterreich_Mio_EUR"]
    faktor = ee["Erneuerbare gesamt"] / ee["Fossile"]
    ax_w.set_title(
        f"Höhere lokale Wertschöpfung bei Betrieb Erneuerbarer Energien",
        fontsize=19,
        fontweight="bold",
        pad=18,
        color=TEXT,
        loc="left",
    )
    ax_w.set_xlabel(
        "Wertschöpfung in Österreich pro eingesetztem Euro", fontsize=12, color=TEXT
    )
    ax_w.set_xlim(0, ws["Wertschoepfung_Oesterreich_Mio_EUR"].max() * 1.12)
    ax_w.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x:.1f}".replace(".", ","))
    )
    ax_w.grid(axis="x", color="#D9DCE1", linewidth=0.8, zorder=0)
    ax_w.set_axisbelow(True)
    for spine in ("top", "right", "bottom"):
        ax_w.spines[spine].set_visible(False)
    ax_w.spines["left"].set_color(TEXT)
    ax_w.tick_params(axis="both", labelsize=12, length=0, colors=TEXT)

    fig_ws.tight_layout()
    fig_ws.savefig(
        OUTPUT_WERTSCHOEPFUNG_PNG, dpi=200, bbox_inches="tight", transparent=True
    )
    fig_ws
    return


@app.cell
def _(TEXT):
    # --- Grafik 4: Plakativ – wie viel von jedem Euro bleibt in Österreich ---
    ws_kurz = pd.read_csv("resources/Windkraft/wertschoepfung_ee_fe.csv").set_index(
        "Technologie"
    )["Wertschoepfung_Oesterreich_Mio_EUR"]
    balken = [
        ("Erneuerbare", ws_kurz["Erneuerbare gesamt"], "#2E8B57"),
        ("Fossile", ws_kurz["Fossile"], "#6B7280"),
    ]

    fig_euro, ax_e = plt.subplots(figsize=(7, 6.5), dpi=130)
    for _x, (_name, _wert, _farbe) in enumerate(balken):
        euro_balken(ax_e, _x, _wert, _farbe, breite=0.7, fontsize=30)
        ax_e.text(_x, -0.06, _name, ha="center", va="top", fontsize=18, color=TEXT)

    ax_e.set_title(
        "Von jedem Euro bleiben in Österreich …",
        fontsize=20,
        fontweight="bold",
        pad=52,
        color=TEXT,
    )
    ax_e.text(
        0.5,
        1.02,
        "Werte für den Betrieb: Wertschöpfung je 1 € Betriebskosten.",
        transform=ax_e.transAxes,
        ha="center",
        va="bottom",
        fontsize=12,
        color="#6B7280",
    )
    ax_e.set_xlim(-0.5, 1.5)
    ax_e.set_ylim(-0.15, 1.05)
    ax_e.axis("off")

    fig_euro.tight_layout()
    fig_euro.savefig(
        "Windkraft/output/wertschoepfung_euro.png",
        dpi=200,
        bbox_inches="tight",
        transparent=True,
    )
    fig_euro
    return


@app.function(hide_code=True)
def euro_balken(
    ax: Axes, x: float, wert: float, farbe: str, breite: float, fontsize: float
) -> None:
    """Zeichnet einen Euro-Balken: Umriss = 1 €, Füllung = Anteil in Österreich."""
    ax.bar(x, 1, width=breite, color="none", edgecolor="#D9DCE1", linewidth=2)
    ax.bar(x, wert, width=breite, color=farbe, zorder=3)
    ax.text(
        x,
        wert - 0.04,
        f"{wert * 100:.0f} Cent",
        ha="center",
        va="top",
        fontsize=fontsize,
        fontweight="bold",
        color="white",
        zorder=4,
    )


@app.cell
def _(TEXT):
    # --- Grafik 4b: wie Grafik 4, zusätzlich mit Investitionskosten ---
    def _lade(pfad: str) -> pd.Series:
        return pd.read_csv(pfad).set_index("Technologie")[
            "Wertschoepfung_Oesterreich_Mio_EUR"
        ]

    ws_betrieb = _lade("resources/Windkraft/wertschoepfung_ee_fe.csv")
    ws_inv = _lade("resources/Windkraft/wertschoepfung_ee_fe_inv.csv")
    gruppen = [
        ("Erneuerbare", "Erneuerbare gesamt", "#2E8B57", "#7CC49A"),
        ("Fossile", "Fossile", "#6B7280", "#A7ADB7"),
    ]
    _breite = 0.38

    fig_euro_inv, ax_ei = plt.subplots(figsize=(9, 6.5), dpi=130)
    for _x, (_name, _tech, _farbe_b, _farbe_i) in enumerate(gruppen):
        for _dx, _art, _wert, _farbe in (
            (-0.21, "Betrieb", ws_betrieb[_tech], _farbe_b),
            (0.21, "Investition", ws_inv[_tech], _farbe_i),
        ):
            euro_balken(ax_ei, _x + _dx, _wert, _farbe, breite=_breite, fontsize=22)
            ax_ei.text(
                _x + _dx, -0.03, _art, ha="center", va="top", fontsize=12, color=TEXT
            )
        ax_ei.text(_x, -0.1, _name, ha="center", va="top", fontsize=18, color=TEXT)

    ax_ei.set_title(
        "Von jedem Euro bleiben in Österreich …",
        fontsize=20,
        fontweight="bold",
        pad=40,
        color=TEXT,
    )
    ax_ei.text(
        0.5,
        1.02,
        "Wertschöpfung je 1 € Betriebs- bzw. Investitionskosten",
        transform=ax_ei.transAxes,
        ha="center",
        va="bottom",
        fontsize=12,
        color="#6B7280",
    )
    ax_ei.set_xlim(-0.5, 1.5)
    ax_ei.set_ylim(-0.2, 1.05)
    ax_ei.axis("off")

    fig_euro_inv.tight_layout()
    fig_euro_inv.savefig(
        "Windkraft/output/wertschoepfung_euro_betrieb_investition.png",
        dpi=200,
        bbox_inches="tight",
        transparent=True,
    )
    fig_euro_inv
    return


@app.cell
def _(TEXT):
    # --- Grafik 5: Anteil Erneuerbarer in Österreich 2025 ---
    # Quellen:
    # - Statistik Austria, Energiebilanzen (Stand 10.11.2026):
    #   https://www.statistik.at/statistiken/energie-und-umwelt/energie/energiebilanzen
    #   -> Anteil Erneuerbarer am Bruttoendenergieverbrauch 2025: 44,0 %
    # - Oesterreichs Energie, Stromstatistik 2026 (Daten 2025):
    #   https://oesterreichsenergie.at/fileadmin/user_upload/Oesterreichs_Energie/Grafik/Stromstatistik/Stromstatistik_2026.pdf
    #   -> Erzeugung Erneuerbare 2025: 60.200 GWh,
    #      Inlandsstromverbrauch (exkl. Pumpspeicherung) 2025: 71.516 GWh
    ANTEIL_EE_ENERGIE = 44.0
    STROM_EE_GWH = 60_200
    STROM_INLANDSVERBRAUCH_GWH = 71_516
    ANTEIL_EE_STROM = 75 # E-Control EAG Monitoringbereicht 2026

    torten = [
        ("Gesamtenergieverbrauch", ANTEIL_EE_ENERGIE),
        ("Inlandsstromverbrauch", ANTEIL_EE_STROM),
    ]

    fig_ee, axes_ee = plt.subplots(1, 2, figsize=(11, 6), dpi=130)
    for _ax, (_titel, _anteil) in zip(axes_ee, torten):
        _ax.pie(
            [_anteil, 100 - _anteil],
            colors=["#2E8B57", "#9CA3AF"],
            startangle=90,
            counterclock=False,
            wedgeprops={"edgecolor": "white", "linewidth": 2},
        )
        # Beschriftung mittig im grünen Segment (Start 12 Uhr, im Uhrzeigersinn)
        _winkel = np.deg2rad(90 - _anteil * 3.6 / 2)
        _ax.text(
            0.55 * np.cos(_winkel),
            0.55 * np.sin(_winkel),
            prozent(_anteil),
            ha="center",
            va="center",
            fontsize=28,
            fontweight="bold",
            color="white",
        )
        _ax.set_title(_titel, fontsize=16, fontweight="bold", color=TEXT)

    fig_ee.suptitle(
        "Anteil Erneuerbarer in Österreich 2025",
        fontsize=20,
        fontweight="bold",
        color=TEXT,
    )
    fig_ee.text(
        0.5,
        0.02,
        "Quellen: Statistik Austria, Energiebilanzen (Bruttoendenergieverbrauch); "
        "Oesterreichs Energie, Stromstatistik 2026",
        ha="center",
        fontsize=10,
        color="#6B7280",
    )

    fig_ee.tight_layout(rect=(0, 0.05, 1, 0.93))
    fig_ee.savefig(
        "Windkraft/output/anteil_erneuerbare_2025.png",
        dpi=200,
        bbox_inches="tight",
        transparent=True,
    )
    fig_ee
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()

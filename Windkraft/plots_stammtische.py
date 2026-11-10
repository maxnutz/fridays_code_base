import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import pandas as pd
    from matplotlib.patches import PathPatch, Rectangle
    from matplotlib.path import Path

    return Path, PathPatch, Rectangle, mticker, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Elektroauto vs. Verbrenner – was kostet 100 km?

    Beispiel **VW Golf** (gleiches Auto, einmal Diesel, einmal elektrisch).
    Verglichen werden nur die **Energiekosten** pro 100 km.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Annahmen

    | Größe | Wert |
    |---|---|
    | Verbrauch Diesel | 6,0 l / 100 km |
    | Verbrauch Strom | 15 kWh / 100 km |
    | Dieselpreis | 2,30 € / l |
    | Strompreis (aktuell) | 35 ct / kWh |
    | Strompreis (günstig) | 20 ct / kWh |
    """)
    return


@app.cell
def _():
    # --- Annahmen (alle Preise in Euro) ---
    DIESEL_L_PER_100KM = 6.0
    STROM_KWH_PER_100KM = 15.0

    DIESEL_PREIS = 2.30  # € pro Liter
    STROM_PREIS_AKTUELL = 0.35  # € pro kWh
    STROM_PREIS_GUENSTIG = 0.20  # € pro kWh

    # Kosten pro 100 km
    kosten = {
        "Diesel": DIESEL_L_PER_100KM * DIESEL_PREIS,
        "Strom\n(35 ct/kWh)": STROM_KWH_PER_100KM * STROM_PREIS_AKTUELL,
        "Strom günstig\n(20 ct/kWh)": STROM_KWH_PER_100KM * STROM_PREIS_GUENSTIG,
    }
    return DIESEL_L_PER_100KM, STROM_KWH_PER_100KM, kosten


@app.cell
def _(kosten, mticker, plt):
    # Farben: Diesel warm/rot, Strom in Grüntönen
    farben = ["#D1495B", "#2A9D8F", "#1D6F63"]
    labels = list(kosten.keys())
    werte = list(kosten.values())

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=130)

    balken = ax.bar(labels, werte, color=farben, width=0.6, zorder=3)

    # Werte über den Balken beschriften
    for b, w in zip(balken, werte):
        ax.text(
            b.get_x() + b.get_width() / 2,
            w + max(werte) * 0.02,
            euro(w),
            ha="center",
            va="bottom",
            fontsize=15,
            fontweight="bold",
            color="black",
        )

    ax.set_title(
        "Was kostet es, 100 km zu fahren?",
        fontsize=19,
        fontweight="bold",
        pad=18,
        color="black",
    )
    ax.set_ylabel("Kosten pro 100 km", fontsize=12, color="black")
    ax.set_ylim(0, max(werte) * 1.18)

    # Euro-Formatierung der y-Achse
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: euro(x)))

    # Optik entschlacken
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("black")
    ax.tick_params(axis="both", labelsize=12, length=0, colors="black")

    fig.tight_layout()
    fig.savefig("ev_vs_ice.png", transparent=True)
    return (fig,)


@app.function(hide_code=True)
def euro(betrag: float) -> str:
    """Formatiert einen Eurobetrag deutsch, z. B. 13.8 -> '13,80 €'."""
    return f"{betrag:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


@app.function(hide_code=True)
def mrd(betrag_mio: float) -> str:
    """Formatiert einen Betrag in Mio € als 'X,Y Mrd €' (deutsch)."""
    text = f"{betrag_mio / 1000:,.1f} Mrd €"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


@app.function(hide_code=True)
def prozent(anteil: float) -> str:
    """Formatiert einen Prozentanteil deutsch; unter 1 % mit 2 Nachkommastellen."""
    nachkomma = 2 if anteil < 1 else 1
    return f"{anteil:.{nachkomma}f} %".replace(".", ",")


@app.function(hide_code=True)
def mwh(betrag: float) -> str:
    """Formatiert einen Energiebetrag deutsch, z. B. 7.79 -> '7,79 MWh'."""
    return f"{betrag:,.2f} MWh".replace(",", "X").replace(".", ",").replace("X", ".")


@app.function(hide_code=True)
def energie_kette(
    end_mwh: float, wirkungsgrad_vorkette: float, wirkungsgrad_nutzung: float
) -> tuple[float, float, float]:
    """(Primär-, End-, Nutzenergie) in MWh aus Endenergie und Wirkungsgraden."""
    return end_mwh / wirkungsgrad_vorkette, end_mwh, end_mwh * wirkungsgrad_nutzung


@app.cell(hide_code=True)
def _(fig):
    # Diagramm als PNG für die Präsentation speichern
    OUTPUT_PNG = "output/kosten_pro_100km.png"
    fig.savefig(OUTPUT_PNG, dpi=200, bbox_inches="tight")
    OUTPUT_PNG
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Energie für 11.000 km – Primär- vs. Endenergie

    Gleicher VW Golf, gleiche Strecke (**11.000 km**, ca. ein Fahr­jahr). Verglichen
    wird, **wie viel Energie** hineinfließt – einmal mit **Rohöl → Diesel**, einmal
    mit **Strom** als Input. Jede Kette wird als Mini-Sankey vom **Primärenergie**-
    Einsatz über die **Endenergie** (im Tank bzw. an der Ladesäule) bis zur
    **Nutzenergie** (Bewegung) dargestellt; die Verluste zweigen nach unten ab.

    So wird der Kernpunkt der großen Österreich-Sankey sichtbar: *Primärenergie ist
    nicht Endenergie* – der Verbrenner braucht ein Vielfaches an Primärenergie, um
    dieselbe Nutzenergie auf die Straße zu bringen.

    ### Annahmen

    | Größe | Wert | Stufe |
    |---|---|---|
    | Verbrauch Diesel | 6,0 l / 100 km | → Endenergie |
    | Heizwert Diesel | 9,8 kWh / l | Umrechnung |
    | Vorkette Rohöl → Diesel (Well-to-Tank) | 83 % | Primär → End |
    | Antrieb Verbrenner (Tank-to-Wheel) | 20 % | End → Nutz |
    | Verbrauch Strom | 15 kWh / 100 km | → Endenergie |
    | Netz/Verteilung Kraftwerk → Ladesäule | 94 % | Primär → End |
    | Laden + Antrieb E-Auto (Charge-to-Wheel) | 78 % | End → Nutz |

    Quellen:

    - Durchschnittliche Pkw-Fahrleistung in Österreich (~11.000 km/Jahr): **VCÖ** –
      https://www.vcoe.at
    - Methodik Primär- / End- / Nutzenergie: **BMWET**, *„Energie in Zahlen"* –
      https://www.bmwet.gv.at/Services/Publikationen/publikationen-energie/zahlen.html
    - Verbrauchswerte (6,0 l Diesel bzw. 15 kWh Strom / 100 km): Herstellerangaben
      nach WLTP (siehe Abschnitt „was kostet 100 km")
    - Heizwert Diesel (~9,8 kWh/l) und Wirkungsgrade (Well-to-Tank, Tank-to-Wheel,
      Netz, Charge-to-Wheel): typische Literaturwerte (reale Fahrpraxis)
    """)
    return


@app.cell
def _(DIESEL_L_PER_100KM, STROM_KWH_PER_100KM):
    # --- Annahmen für die Energiebilanz 11.000 km ---
    KM = 11_000  # Fahrleistung (ca. ein Fahrjahr in Österreich)

    DIESEL_KWH_PER_L = 9.8  # Heizwert Diesel
    WTT_DIESEL = 0.83  # Rohöl -> Diesel (Well-to-Tank)
    TTW_DIESEL = 0.20  # Tank-to-Wheel (realer Verbrennerwirkungsgrad)
    GRID_EFF = 0.94  # Kraftwerk -> Ladesäule (Netz/Verteilung)
    CTW_EV = 0.78  # Charge-to-Wheel (Laden + Antrieb E-Auto)

    # Endenergie (im Tank bzw. an der Ladesäule), in MWh
    diesel_end_mwh = KM / 100 * DIESEL_L_PER_100KM * DIESEL_KWH_PER_L / 1000
    strom_end_mwh = KM / 100 * STROM_KWH_PER_100KM / 1000

    d_prim, d_end, d_nutz = energie_kette(diesel_end_mwh, WTT_DIESEL, TTW_DIESEL)
    e_prim, e_end, e_nutz = energie_kette(strom_end_mwh, GRID_EFF, CTW_EV)
    return d_end, d_nutz, d_prim, e_end, e_nutz, e_prim


@app.cell
def _(
    Path,
    PathPatch,
    Rectangle,
    d_end,
    d_nutz,
    d_prim,
    e_end,
    e_nutz,
    e_prim,
    plt,
):
    # Mini-Sankey-Geometrie: oben flache Kante, Verluste zweigen nach unten ab.
    # Beide Diagramme teilen denselben Maßstab (value / HMAX), damit die
    # Diesel-Kette die Strom-Kette sichtbar überragt.
    MOVETO, CURVE4, LINETO, CLOSE = (
        Path.MOVETO,
        Path.CURVE4,
        Path.LINETO,
        Path.CLOSEPOLY,
    )
    GREY = "#8A8F98"
    Y_TOP = 0.72  # Bandoberkante tiefer -> mehr Luft unter den Unterüberschriften
    X0, X1, X2, NW = 0.12, 0.50, 0.88, 0.014

    def h_ribbon(ax, xs, xe, ys0, ys1, ye0, ye1, color, alpha):
        """Waagrechtes Flussband zwischen zwei senkrechten Öffnungen."""
        cx = (xs + xe) / 2
        verts = [
            (xs, ys1),
            (cx, ys1),
            (cx, ye1),
            (xe, ye1),
            (xe, ye0),
            (cx, ye0),
            (cx, ys0),
            (xs, ys0),
            (xs, ys1),
        ]
        codes = [MOVETO, CURVE4, CURVE4, CURVE4, LINETO, CURVE4, CURVE4, CURVE4, CLOSE]
        ax.add_patch(PathPatch(Path(verts, codes), fc=color, ec="none", alpha=alpha))

    def loss_ribbon(ax, xs, ya, yb, xc, yt, color, alpha):
        """Verlustband: biegt vom Flussboden nach unten zu einem Stummel ab."""
        t = yb - ya
        xl, xr = xc - t / 2, xc + t / 2
        dx = (xc - xs) * 0.55
        dy = (yb - yt) * 0.45
        verts = [
            (xs, yb),
            (xs + dx, yb),
            (xr, yt + dy),
            (xr, yt),
            (xl, yt),
            (xl, yt + dy),
            (xs + dx, ya),
            (xs, ya),
            (xs, yb),
        ]
        codes = [MOVETO, CURVE4, CURVE4, CURVE4, LINETO, CURVE4, CURVE4, CURVE4, CLOSE]
        ax.add_patch(PathPatch(Path(verts, codes), fc=color, ec="none", alpha=alpha))

    def node_label(ax, x, stage, value):
        ax.text(
            x + NW / 2,
            Y_TOP + 0.085,
            stage,
            ha="center",
            va="bottom",
            fontsize=11.5,
            fontweight="bold",
            color="white",
        )
        ax.text(
            x + NW / 2,
            Y_TOP + 0.03,
            value,
            ha="center",
            va="bottom",
            fontsize=11.5,
            color="white",
        )

    def loss_label(ax, xc, yt, text, value):
        ax.text(
            xc,
            yt - 0.035,
            text + "\n" + value,
            ha="center",
            va="top",
            fontsize=10,
            linespacing=1.6,
            color="#C9CDD4",
        )

    def draw_sankey(ax, prim, end, nutz, color, hmax, hscale, names, losslbl):
        hP, hE, hN = (v / hmax * hscale for v in (prim, end, nutz))
        bP, bE = Y_TOP - hP, Y_TOP - hE
        for x, h in ((X0, hP), (X1, hE), (X2, hN)):
            ax.add_patch(Rectangle((x, Y_TOP - h), NW, h, color=color, zorder=5))
        # Primär -> End (obere Scheibe) + Vorketten-Verlust nach unten
        h_ribbon(ax, X0 + NW, X1, Y_TOP - hE, Y_TOP, bE, Y_TOP, color, 0.80)
        loss_ribbon(ax, X0 + NW, bP, bE, (X0 + X1) / 2 + 0.03, bP - 0.14, GREY, 0.6)
        # End -> Nutz (obere Scheibe) + Antriebs-Verlust nach unten
        h_ribbon(ax, X1 + NW, X2, Y_TOP - hN, Y_TOP, Y_TOP - hN, Y_TOP, color, 0.80)
        loss_ribbon(
            ax, X1 + NW, bE, Y_TOP - hN, (X1 + X2) / 2 + 0.03, bE - 0.18, GREY, 0.6
        )
        node_label(ax, X0, names[0], mwh(prim))
        node_label(ax, X1, names[1], mwh(end))
        node_label(ax, X2, names[2], mwh(nutz))
        loss_label(ax, (X0 + X1) / 2 + 0.03, bP - 0.14, losslbl[0], mwh(prim - end))
        loss_label(ax, (X1 + X2) / 2 + 0.03, bE - 0.18, losslbl[1], mwh(end - nutz))

    fig_sankey, (axd, axe) = plt.subplots(2, 1, figsize=(10, 8.4), dpi=130)
    HMAX = d_prim  # größter Wert -> gemeinsamer Maßstab beider Diagramme
    for ax_s in (axd, axe):
        ax_s.set_xlim(0, 1)
        ax_s.set_ylim(0, 1)
        ax_s.axis("off")

    axd.text(
        0.5,
        0.98,
        "Verbrenner  ·  Diesel",
        ha="center",
        fontsize=15,
        fontweight="bold",
        color="#D1495B",
        va="top",
    )
    draw_sankey(
        axd,
        d_prim,
        d_end,
        d_nutz,
        "#D1495B",
        HMAX,
        0.44,
        ("Primärenergie (Rohöl)", "Endenergie (Diesel)", "1 Jahr Auto fahren"),
        ("Vorketten-\nverluste", "Motor-/Antriebsverluste"),
    )

    axe.text(
        0.5,
        0.98,
        "E-Auto  ·  Strom",
        ha="center",
        fontsize=15,
        fontweight="bold",
        color="#2A9D8F",
        va="top",
    )
    draw_sankey(
        axe,
        e_prim,
        e_end,
        e_nutz,
        "#2A9D8F",
        HMAX,
        0.44,
        ("Primärenergie (Strom)", "Endenergie (Strom)", "1 Jahr Auto fahren"),
        ("Netz-/Ladeverluste", "Antriebsverluste"),
    )

    fig_sankey.suptitle(
        "1 Jahr Auto fahren – unterschiedlich viel Primärenergie",
        fontsize=19,
        fontweight="bold",
        color="white",
        y=0.995,
    )
    fig_sankey.text(
        0.5,
        0.945,
        "Quellen: VCÖ, BMWET, Herstellerangaben VW",
        ha="center",
        fontsize=10,
        fontstyle="italic",
        color="#CCCCCC",
    )
    fig_sankey.tight_layout(rect=(0, 0, 1, 0.93))
    return (fig_sankey,)


@app.cell(hide_code=True)
def _(fig_sankey):
    # Diagramm als PNG für die Präsentation speichern
    OUTPUT_SANKEY_PNG = "output/energie_11000km_sankey.png"
    fig_sankey.savefig(
        OUTPUT_SANKEY_PNG, dpi=200, bbox_inches="tight", transparent=True
    )
    OUTPUT_SANKEY_PNG
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Was uns fossile Energie kostet

    Österreich **importiert** Öl, Gas und Kohle fast vollständig aus dem Ausland.
    Jedes Jahr fließen dadurch **Milliarden Euro an Kaufkraft** ab – Geld, das im
    Inland für Wertschöpfung und erneuerbare Energie fehlt.

    Quellen:
    - https://www.statistik.at/statistiken/internationaler-handel/internationaler-warenhandel/importe-und-exporte-von-guetern
    - https://www.energyagency.at/aktuelles/tag-der-fossilen-abhaengigkeit-2023
    - https://www.energyagency.at/aktuelles/energieabhaengigkeit-ab-dem-31-mai-lebt-oesterreich-von-fossilen-importen
    """)
    return


@app.cell
def _(pd):
    imports_df = pd.read_csv("../resources/Windkraft/nettoimports_to_at.csv", sep=";")
    imports_df
    return (imports_df,)


@app.cell
def _(imports_df, mticker, plt):
    jahre = imports_df["Jahr"].astype(str).tolist()
    import_werte = imports_df["Nettoimport_Oel_Gas_Kohle_Mio_EUR"].tolist()

    # Spitzenjahr (Energiekrise 2022) farblich hervorheben
    max_i = import_werte.index(max(import_werte))
    import_farben = ["#C0586B"] * len(import_werte)
    import_farben[max_i] = "#D1495B"

    fig_imp, ax_imp = plt.subplots(figsize=(9, 5.5), dpi=130)
    balken_imp = ax_imp.bar(
        jahre, import_werte, color=import_farben, width=0.7, zorder=3
    )

    # Werte über den Balken beschriften
    for b, w in zip(balken_imp, import_werte):
        ax_imp.text(
            b.get_x() + b.get_width() / 2,
            w + max(import_werte) * 0.02,
            mrd(w),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color="white",
        )

    ax_imp.set_title(
        "Kaufkraft-Verlust durch Netto-Importe von Öl, Gas & Kohle",
        fontsize=16,
        fontweight="bold",
        pad=32,
        color="white",
    )
    # Untertitel / Quelle
    ax_imp.text(
        0.5,
        1.015,
        "Quelle: Statistik Austria, 2025 vorläufig",
        transform=ax_imp.transAxes,
        ha="center",
        va="bottom",
        fontsize=11,
        fontstyle="italic",
        color="#CCCCCC",
    )

    ax_imp.set_ylabel("Netto-Importe pro Jahr", fontsize=12, color="white")
    ax_imp.set_ylim(0, max(import_werte) * 1.18)
    ax_imp.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: mrd(x)))

    # Optik entschlacken (gleicher Stil wie oben)
    ax_imp.grid(axis="y", color="#DDDDDD", linewidth=0.8, zorder=0)
    ax_imp.set_axisbelow(True)
    for spine in ("top", "right"):
        ax_imp.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax_imp.spines[spine].set_color("white")
    ax_imp.tick_params(axis="both", labelsize=11, length=0, colors="white")

    fig_imp.tight_layout()
    fig_imp.savefig("output/fossil_imports.png", transparent=True)
    return (fig_imp,)


@app.cell(hide_code=True)
def _(fig_imp):
    # Diagramm als PNG für die Präsentation speichern
    OUTPUT_IMPORTS_PNG = "output/nettoimporte_oel_gas_kohle.png"
    fig_imp.savefig(OUTPUT_IMPORTS_PNG, dpi=200, bbox_inches="tight", transparent=True)
    OUTPUT_IMPORTS_PNG
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Woran Vögel wirklich sterben

    Windkraftanlagen stehen oft im Verdacht, ein großer „Vogelkiller" zu sein.
    Die Zahlen zeigen ein anderes Bild: Am **Anteil aller Vogelopfer** haben
    Hauskatzen, Glasscheiben und der Verkehr den mit Abstand größten Beitrag –
    Windräder machen nur einen **Bruchteil eines Prozents** aus.

    Dargestellt ist der **prozentuale Anteil** jeder Ursache an den geschätzten
    Vogelopfern pro Jahr in Deutschland. Wo eine Bandbreite vorliegt, ist der
    Mittelwert verwendet.

    Quelle: [NABU](https://www.nabu.de/tiere-und-pflanzen/voegel/gefaehrdungen/24661.html)
    """)
    return


@app.cell
def _(pd):
    birds_df = pd.read_csv("resources/Windkraft/birds_death.csv")
    birds_df
    return (birds_df,)


@app.cell
def _(birds_df, plt):
    # Mittelwert, wo eine Bandbreite vorliegt, sonst der Einzelwert
    bird_repr = (
        birds_df["low_per_year"]
        + birds_df["high_per_year"].fillna(birds_df["low_per_year"])
    ) / 2

    # Anteil jeder Ursache an allen Vogelopfern (in Prozent)
    bird_anteil = bird_repr / bird_repr.sum() * 100

    labels_de = {
        "Domestic cats": "Hauskatzen",
        "Glass collisions": "Glasscheiben",
        "Road and rail traffic": "Straßen- & Bahnverkehr",
        "Power line collisions": "Stromleitungen (Kollision)",
        "Power line electrocution": "Stromschlag",
        "Wind turbines": "Windkraftanlagen",
        "Hunting": "Jagd",
    }

    # Nach Anteil absteigend sortieren
    bird_plot = (
        birds_df.assign(anteil=bird_anteil)
        .sort_values("anteil", ascending=False)
        .reset_index(drop=True)
    )
    bird_werte = bird_plot["anteil"].tolist()

    # Windkraft grün hervorheben, übrige Ursachen in Rottönen
    # (dunkel = großer Anteil)
    rot_ramp = ["#8C2F39", "#A8384A", "#C0586B", "#D86072", "#E68A6E", "#EEB4A3"]
    bird_farben = []
    rot_i = 0
    for s in bird_plot["source"]:
        if s == "Wind turbines":
            bird_farben.append("#2A9D8F")
        else:
            bird_farben.append(rot_ramp[rot_i])
            rot_i += 1

    # Prozent in die Legende schreiben – im Kuchen würden winzige Segmente
    # wie die Windkraft (< 0,1 %) sonst überlappen
    legenden_labels = [
        f"{labels_de[s]} – {prozent(a)}"
        for s, a in zip(bird_plot["source"], bird_werte)
    ]

    fig_birds, ax_birds = plt.subplots(figsize=(10, 6), dpi=130)
    wedges, _ = ax_birds.pie(
        bird_werte,
        colors=bird_farben,
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.42, "edgecolor": "black", "linewidth": 1.2},
    )
    ax_birds.set_aspect("equal")

    ax_birds.set_title(
        "Anteil an allen Vogelopfern",
        fontsize=18,
        fontweight="bold",
        pad=24,
        color="black",
    )
    # Untertitel / Quelle
    ax_birds.text(
        0.5,
        1.02,
        "nach direkt zurückführbarer Ursache – Deutschland · Quelle: NABU",
        transform=ax_birds.transAxes,
        ha="center",
        va="bottom",
        fontsize=11,
        fontstyle="italic",
        color="black",
    )

    ax_birds.legend(
        wedges,
        legenden_labels,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=False,
        fontsize=11,
        labelcolor="black",
    )

    fig_birds.tight_layout()
    fig_birds.savefig(
        "output/voegel_todesursachen.png", transparent=True, bbox_inches="tight"
    )
    return (fig_birds,)


@app.cell(hide_code=True)
def _(fig_birds):
    # Diagramm als PNG für die Präsentation speichern
    OUTPUT_BIRDS_PNG = "output/voegel_todesursachen.png"
    fig_birds.savefig(OUTPUT_BIRDS_PNG, dpi=200, bbox_inches="tight", transparent=True)
    OUTPUT_BIRDS_PNG
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fledermausschutz: Windräder schalten sich gezielt ab

    Moderne Windkraftanlagen laufen nicht einfach durch. Ein
    **Abschaltalgorithmus** prüft laufend Wetterdaten wie Windgeschwindigkeit,
    Temperatur und Niederschlag sowie Tages- und Jahreszeit. Sobald die
    Bedingungen darauf hindeuten, dass Fledermäuse aktiv sein könnten
    (schwacher Wind, warme Abende, kein Regen), wird die Anlage gestoppt –
    auch wenn sie Strom erzeugen könnte.

    Dargestellt ist ein Tag (6. August 2026) einer Anlage in 10-Minuten-Werten.
    Die rot hinterlegten Zeiträume zeigen, wann die Anlage zum Schutz der
    Fledermäuse stillstand.
    """)
    return


@app.cell
def _(pd):
    bats_df = pd.read_excel("resources/Windkraft/Fledermäuse-grafII.xlsx")
    bats_df.columns = ["zeit", "regen", "temperatur", "wind", "betrieb"]
    bats_df
    return (bats_df,)


@app.cell
def _(bats_df, plt):
    import matplotlib.dates as mdates

    STOPP_FARBE = "#C0586B"
    zeit = bats_df["zeit"]
    schritt = zeit.diff().median()
    # Zusammenhängende Stillstandsphasen (betrieb == 0) finden
    gruppe = (bats_df["betrieb"] != bats_df["betrieb"].shift()).cumsum()
    stopps = [
        (g["zeit"].iloc[0], g["zeit"].iloc[-1] + schritt)
        for _, g in bats_df[bats_df["betrieb"] == 0].groupby(gruppe)
    ]

    fig_bats, achsen = plt.subplots(
        4,
        1,
        figsize=(11, 8),
        dpi=130,
        sharex=True,
        gridspec_kw={"height_ratios": [3, 2, 2, 0.8]},
    )
    ax_wind, ax_temp, ax_regen, ax_status = achsen

    ax_wind.plot(zeit, bats_df["wind"], color="#2A9D8F", lw=2)
    ax_wind.set_ylabel("Wind\n[m/s]")
    ax_temp.plot(zeit, bats_df["temperatur"], color="#E68A6E", lw=2)
    ax_temp.set_ylabel("Temperatur\n[°C]")
    ax_regen.bar(zeit, bats_df["regen"], width=schritt, color="#4A7FB5", align="edge")
    ax_regen.set_ylabel("Regen\n[mm/h]")

    # Statusband: grün = in Betrieb, rot = gestoppt
    ax_status.bar(
        zeit,
        1,
        width=schritt,
        align="edge",
        color=["#2A9D8F" if _b == 1 else "none" for _b in bats_df["betrieb"]],
    )
    ax_status.set_yticks([])
    ax_status.set_ylabel("Anlage", rotation=0, ha="right", va="center")

    for _start, _ende in stopps:
        for _ax in (ax_wind, ax_temp, ax_regen, ax_status):
            _ax.axvspan(_start, _ende, color=STOPP_FARBE, alpha=0.35, lw=0)

    for _ax in achsen:
        _ax.spines[["top", "right"]].set_visible(False)
        _ax.grid(axis="y", alpha=0.3)
    ax_status.spines[["left"]].set_visible(False)
    ax_status.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax_status.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_status.set_xlim(zeit.iloc[0], zeit.iloc[-1] + schritt)
    ax_status.set_xlabel("Uhrzeit (6. August 2026)")

    ax_wind.set_title(
        "Windrad stoppt, wenn Fledermäuse fliegen könnten",
        fontsize=16,
        fontweight="bold",
        pad=28,
    )
    ax_wind.text(
        0.5,
        1.04,
        "Wetterdaten und Betriebszustand einer Anlage · rot = Stillstand "
        f"({(bats_df['betrieb'] == 0).sum() * 10} Minuten)",
        transform=ax_wind.transAxes,
        ha="center",
        va="bottom",
        fontsize=11,
        fontstyle="italic",
    )

    fig_bats.tight_layout()
    fig_bats
    return (fig_bats,)


@app.cell(hide_code=True)
def _(fig_bats):
    # Diagramm als PNG für die Präsentation speichern
    OUTPUT_BATS_PNG = "output/fledermaus_abschaltung.png"
    fig_bats.savefig(OUTPUT_BATS_PNG, dpi=200, bbox_inches="tight", transparent=True)
    OUTPUT_BATS_PNG
    return


if __name__ == "__main__":
    app.run()

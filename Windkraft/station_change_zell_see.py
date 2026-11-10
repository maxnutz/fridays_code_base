import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Stationswechsel Zell am See — Effekt auf die Temperaturreihe

    Die Datei `stations-data_zell_see.csv` enthält Tageswerte für
    Mitteltemperatur (`tl_mittel`), Minimum (`tlmin`) und Maximum (`tlmax`)
    von **zwei** Messstationen, die zu unterschiedlichen Zeiten betrieben wurden.

    Ziel dieses Notebooks: zeigen, dass ein **Stationswechsel** die Zeitreihe
    verfälschen kann — und dass man bei falsch gewählten Vergleichszeiträumen
    sogar eine *Abkühlung über die Zeit* "nachweisen" kann, obwohl diese nur
    durch den Standortwechsel zustande kommt.

    **Aufbau:**

    1. Wie sehen die Reihen der beiden Stationen aus, wann ist der Wechsel?
    2. Kann ein späteres Mittel (neue Station) niedriger sein als ein früheres
       Mittel (alte Station)? — mit Vergleichsgrafik.
    3. Liegt das am Standortwechsel? — harter Schnitt + Niveauvergleich.
    4. Haben beide Stationen gleichzeitig gemessen? Lässt sich der neue
       Standort als *kälter* belegen?
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from pathlib import Path

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    return Path, np, pd, plt


@app.cell
def _(Path, pd):
    CSV_PATH = Path("../resources/Windkraft/stations-data_zell_see.csv")
    OUTPUT_DIR = Path("output")
    OUTPUT_DIR.mkdir(exist_ok=True)

    _raw = pd.read_csv(CSV_PATH, parse_dates=["time"])
    # drop timezone for simple plotting / grouping
    _raw["time"] = _raw["time"].dt.tz_localize(None)

    # long form, only rows with a valid mean temperature
    df = _raw.dropna(subset=["tl_mittel"]).copy()
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    return (df,)


@app.cell
def _(df):
    # Identify the two stations and order them by first valid measurement.
    _coverage = (
        df.groupby("station")["time"]
        .agg(first="min", last="max", n_days="count")
        .sort_values("first")
    )
    station_old = int(_coverage.index[0])
    station_new = int(_coverage.index[1])
    switch_date = _coverage.loc[station_new, "first"]
    coverage = _coverage
    return coverage, station_new, station_old, switch_date


@app.cell(hide_code=True)
def _(coverage, mo, station_new, station_old, switch_date):
    o_first, o_last = (
        coverage.loc[station_old, "first"].date(),
        coverage.loc[station_old, "last"].date(),
    )
    n_first, n_last = (
        coverage.loc[station_new, "first"].date(),
        coverage.loc[station_new, "last"].date(),
    )
    o_n, n_n = coverage.loc[station_old, "n_days"], coverage.loc[station_new, "n_days"]
    mo.md(
        f"""
        ## 1 — Die Reihen der beiden Stationen und der Wechsel

        | | Station {station_old} (alt) | Station {station_new} (neu) |
        |---|---|---|
        | erster Messtag | {o_first} | {n_first} |
        | letzter Messtag | {o_last} | {n_last} |
        | Tage mit Messwert | {o_n:,} | {n_n:,} |

        Die alte Station **{station_old}** misst bis ~**{switch_date.date()}**, danach
        übernimmt die neue Station **{station_new}**. Der Wechsel ist ein harter
        Schnitt in der Reihe.
        """
    )
    return


@app.cell
def _(df, plt, station_new, station_old, switch_date):
    # Smooth daily series with a 365-day rolling mean per station so the level
    # difference becomes visible instead of the seasonal noise. Require a nearly
    # full window (min_periods) so the incomplete-window ramp at each series
    # start is dropped instead of showing extreme artefact values.
    fig1, ax1 = plt.subplots(figsize=(11, 4.5))

    for _st, _color in ((station_old, "tab:blue"), (station_new, "tab:red")):
        _s = df[df["station"] == _st].set_index("time")["tl_mittel"].sort_index()
        ax1.plot(_s.index, _s.values, color=_color, alpha=0.18, lw=0.5)
        ax1.plot(
            _s.index,
            _s.rolling("365D", min_periods=360).mean().values,
            color=_color,
            lw=2.2,
            label=f"Station {_st} (365-Tage-Mittel)",
        )

    ax1.axvline(switch_date, color="black", ls="--", lw=1.2)
    ax1.annotate(
        f"Stationswechsel\n{switch_date.date()}",
        xy=(switch_date, ax1.get_ylim()[1]),
        xytext=(-10, -8),
        textcoords="offset points",
        ha="right",
        va="top",
        fontsize=9,
    )
    ax1.set_ylabel("Mitteltemperatur [°C]")
    ax1.set_title("Zell am See — Tagesmittel und gleitendes Jahresmittel je Station")
    ax1.legend(loc="lower left")
    fig1.tight_layout()
    fig1
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2 — Cherry-Picking: späteres Mittel niedriger als früheres

    Wir bilden das Mittel über ein Fenster von **2–5 Jahren** auf der **alten**
    Station und vergleichen es mit einem **späteren** Fenster auf der **neuen**
    Station. Wählt man die Zeiträume "passend", liegt das spätere Mittel
    *unter* dem früheren — es sieht nach Abkühlung aus.

    Die Regler steuern Fensterlänge und Startjahre.
    """)
    return


@app.cell
def _(df, mo, station_new, station_old):
    _old_years = sorted(df[df["station"] == station_old]["year"].unique())
    _new_years = sorted(df[df["station"] == station_new]["year"].unique())

    win = mo.ui.slider(2, 5, value=4, label="Fensterlänge [Jahre]")
    old_start = mo.ui.slider(
        _old_years[0],
        _old_years[-1],
        value=2015,
        label=f"Startjahr altes Fenster (Station {station_old})",
    )
    new_start = mo.ui.slider(
        _new_years[0],
        _new_years[-1],
        value=2020,
        label=f"Startjahr neues Fenster (Station {station_new})",
    )
    controls = mo.vstack([win, old_start, new_start])
    controls
    return new_start, old_start, win


@app.cell
def _(df, new_start, old_start, station_new, station_old, win):
    def _period_mean(station: int, start_year: int, n_years: int) -> tuple:
        """Mean tl_mittel over full calendar years [start, start+n_years)."""
        end_year = start_year + n_years - 1
        mask = (
            (df["station"] == station)
            & (df["year"] >= start_year)
            & (df["year"] <= end_year)
        )
        sub = df[mask]
        return float(sub["tl_mittel"].mean()), start_year, end_year

    old_mean, old_y0, old_y1 = _period_mean(station_old, old_start.value, win.value)
    new_mean, new_y0, new_y1 = _period_mean(station_new, new_start.value, win.value)
    delta = new_mean - old_mean
    return delta, new_mean, new_y0, new_y1, old_mean, old_y0, old_y1


@app.cell(hide_code=True)
def _(
    delta,
    mo,
    new_mean,
    new_y0,
    new_y1,
    old_mean,
    old_y0,
    old_y1,
    station_new,
    station_old,
):
    _old_lbl = f"{old_y0}–{old_y1}"
    _new_lbl = f"{new_y0}–{new_y1}"
    _verdict = (
        f"➡️ Das **spätere** Mittel ist **{abs(delta):.2f} °C niedriger** — es sieht "
        f"nach Abkühlung aus, obwohl global erwärmt wird."
        if delta < 0
        else (
            f"Hier ist das spätere Mittel {delta:.2f} °C höher "
            "(kein Abkühlungs-Artefakt in dieser Wahl)."
        )
    )
    mo.md(
        f"""
        - altes Fenster **{_old_lbl}** (Station {station_old}): **{old_mean:.2f} °C**
        - neues Fenster **{_new_lbl}** (Station {station_new}): **{new_mean:.2f} °C**
        - Differenz (neu − alt): **{delta:+.2f} °C**

        {_verdict}
        """
    )
    return


@app.cell
def _(
    df,
    new_mean,
    new_y0,
    new_y1,
    old_mean,
    old_y0,
    old_y1,
    plt,
    station_new,
    station_old,
):
    # Annual means over the whole timeline, with the two chosen comparison
    # windows shaded and their means drawn as horizontal levels.
    _annual = df.groupby(["station", "year"])["tl_mittel"].mean().reset_index()

    fig2, ax2 = plt.subplots(figsize=(11, 4.5))
    for _st, _color in ((station_old, "tab:blue"), (station_new, "tab:red")):
        _a = _annual[_annual["station"] == _st]
        ax2.plot(
            _a["year"], _a["tl_mittel"], "o-", color=_color, label=f"Station {_st}"
        )

    # shaded windows + level lines
    ax2.axvspan(old_y0 - 0.4, old_y1 + 0.4, color="tab:blue", alpha=0.12)
    ax2.axvspan(new_y0 - 0.4, new_y1 + 0.4, color="tab:red", alpha=0.12)
    ax2.hlines(
        old_mean,
        old_y0 - 0.4,
        old_y1 + 0.4,
        color="tab:blue",
        lw=3,
    )
    ax2.hlines(
        new_mean,
        new_y0 - 0.4,
        new_y1 + 0.4,
        color="tab:red",
        lw=3,
    )
    ax2.annotate(
        f"{old_mean:.2f} °C",
        xy=((old_y0 + old_y1) / 2, old_mean),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        color="tab:blue",
        fontweight="bold",
    )
    ax2.annotate(
        f"{new_mean:.2f} °C",
        xy=((new_y0 + new_y1) / 2, new_mean),
        xytext=(0, -14),
        textcoords="offset points",
        ha="center",
        color="tab:red",
        fontweight="bold",
    )
    ax2.set_xlabel("Jahr")
    ax2.set_ylabel("Jahresmittel-Temperatur [°C]")
    ax2.set_title("Vergleich zweier Zeiträume — spätes Mittel kann unter frühem liegen")
    ax2.legend(loc="lower right")
    fig2.tight_layout()
    fig2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3 — Liegt es am Standortwechsel? Harter Schnitt + Niveauvergleich

    Wir vergleichen das Niveau **unmittelbar vor** dem Wechsel (letzte volle
    Jahre der alten Station) mit dem Niveau **unmittelbar nach** dem Wechsel
    (erste volle Jahre der neuen Station). Ein Sprung nach unten am Wechsel
    deutet auf einen *kälteren Standort*, nicht auf Klimaabkühlung.
    """)
    return


@app.cell
def _(df, station_new, station_old, switch_date):
    N_ERA = 5  # full years each side of the switch for the level comparison

    _old_years = sorted(df[df["station"] == station_old]["year"].unique())
    _new_years = sorted(df[df["station"] == station_new]["year"].unique())

    # last N full years before the switch (exclude the partial switch year)
    era_old_years = [y for y in _old_years if y < switch_date.year][-N_ERA:]
    # first N full years after the switch (exclude the partial switch year)
    era_new_years = [y for y in _new_years if y > switch_date.year][:N_ERA]

    era_old_mean = float(
        df[(df["station"] == station_old) & (df["year"].isin(era_old_years))][
            "tl_mittel"
        ].mean()
    )
    era_new_mean = float(
        df[(df["station"] == station_new) & (df["year"].isin(era_new_years))][
            "tl_mittel"
        ].mean()
    )
    era_delta = era_new_mean - era_old_mean
    return era_delta, era_new_mean, era_new_years, era_old_mean, era_old_years


@app.cell
def _(
    df,
    era_new_mean,
    era_new_years,
    era_old_mean,
    era_old_years,
    plt,
    station_new,
    station_old,
    switch_date,
):
    fig3, ax3 = plt.subplots(figsize=(11, 4.5))

    for _st, _color in ((station_old, "tab:blue"), (station_new, "tab:red")):
        _s = (
            df[df["station"] == _st]
            .set_index("time")["tl_mittel"]
            .sort_index()
            .rolling("365D", min_periods=360)
            .mean()
        )
        ax3.plot(_s.index, _s.values, color=_color, lw=2, label=f"Station {_st}")

    ax3.axvline(switch_date, color="black", ls="--", lw=1.2, label="Wechsel")

    # era level lines
    ax3.hlines(
        era_old_mean,
        df[df["year"].isin(era_old_years)]["time"].min(),
        switch_date,
        color="tab:blue",
        lw=3,
        ls=":",
    )
    ax3.hlines(
        era_new_mean,
        switch_date,
        df[df["year"].isin(era_new_years)]["time"].max(),
        color="tab:red",
        lw=3,
        ls=":",
    )
    ax3.set_ylabel("Mitteltemperatur [°C] (gleitendes Jahresmittel)")
    ax3.set_title("Harter Schnitt am Stationswechsel — Niveausprung des Standorts")
    ax3.legend(loc="lower left")
    fig3.tight_layout()
    fig3
    return


@app.cell(hide_code=True)
def _(
    era_delta,
    era_new_mean,
    era_new_years,
    era_old_mean,
    era_old_years,
    mo,
    station_new,
    station_old,
):
    _msg = (
        f"➡️ Der neue Standort ist im Mittel **{abs(era_delta):.2f} °C kälter** — "
        "ein Standort-Effekt, keine Klimaabkühlung."
        if era_delta < 0
        else f"Der neue Standort ist {era_delta:.2f} °C wärmer."
    )
    mo.md(
        f"""
        - Station {station_old}, Jahre {era_old_years[0]}–{era_old_years[-1]}:
          **{era_old_mean:.2f} °C**
        - Station {station_new}, Jahre {era_new_years[0]}–{era_new_years[-1]}:
          **{era_new_mean:.2f} °C**
        - Sprung am Wechsel (neu − alt): **{era_delta:+.2f} °C**

        {_msg} Zum Vergleich: der globale Erwärmungstrend liegt im Bereich von
        ~0,2 °C pro Jahrzehnt — der Standortsprung übertrifft das deutlich.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4 — Haben beide Stationen gleichzeitig gemessen?

    Idealerweise überlappen sich beide Stationen (Parallelmessung), dann ließe
    sich der Standort-Offset direkt Tag-für-Tag berechnen. Wir prüfen das.
    """)
    return


@app.cell
def _(df, station_new, station_old):
    # Days where BOTH stations have a valid mean temperature.
    _wide = df.pivot_table(index="time", columns="station", values="tl_mittel")
    overlap = _wide.dropna(subset=[station_old, station_new])
    has_overlap = len(overlap) > 0
    overlap_diff = (
        float((overlap[station_new] - overlap[station_old]).mean())
        if has_overlap
        else float("nan")
    )
    return has_overlap, overlap, overlap_diff


@app.cell
def _(df, np, station_new, station_old):
    # Seasonality-controlled fallback: compare monthly climatologies of two
    # comparable windows (works even without overlapping measurements).
    CLIM_OLD = range(2014, 2019)  # last 5 full years of the old station
    CLIM_NEW = range(2020, 2025)  # first 5 full years of the new station

    def _clim(station: int, years: range) -> "np.ndarray":
        sub = df[(df["station"] == station) & (df["year"].isin(list(years)))]
        return sub.groupby("month")["tl_mittel"].mean().reindex(range(1, 13)).values

    clim_old = _clim(station_old, CLIM_OLD)
    clim_new = _clim(station_new, CLIM_NEW)
    clim_offset = float(np.nanmean(clim_new - clim_old))
    return CLIM_NEW, CLIM_OLD, clim_new, clim_offset, clim_old


@app.cell
def _(
    CLIM_NEW,
    CLIM_OLD,
    clim_new,
    clim_old,
    np,
    plt,
    station_new,
    station_old,
):
    _months = np.arange(1, 13)
    fig4, (ax4a, ax4b) = plt.subplots(
        1, 2, figsize=(12, 4.3), gridspec_kw={"width_ratios": [2, 1]}
    )

    ax4a.plot(
        _months,
        clim_old,
        "o-",
        color="tab:blue",
        label=f"Station {station_old} ({CLIM_OLD.start}–{CLIM_OLD.stop - 1})",
    )
    ax4a.plot(
        _months,
        clim_new,
        "o-",
        color="tab:red",
        label=f"Station {station_new} ({CLIM_NEW.start}–{CLIM_NEW.stop - 1})",
    )
    ax4a.set_xticks(_months)
    ax4a.set_xlabel("Monat")
    ax4a.set_ylabel("mittlere Monatstemperatur [°C]")
    ax4a.set_title("Monats-Klimatologie (saisonbereinigter Vergleich)")
    ax4a.legend()

    _diff = clim_new - clim_old
    _colors = ["tab:red" if d < 0 else "tab:green" for d in _diff]
    ax4b.bar(_months, _diff, color=_colors)
    ax4b.axhline(0, color="black", lw=0.8)
    ax4b.set_xticks(_months)
    ax4b.set_xlabel("Monat")
    ax4b.set_ylabel("Differenz neu − alt [°C]")
    ax4b.set_title("Standort-Offset je Monat")
    fig4.tight_layout()
    fig4
    return


@app.cell(hide_code=True)
def _(
    clim_offset,
    has_overlap,
    mo,
    overlap,
    overlap_diff,
    station_new,
    station_old,
):
    if has_overlap:
        _txt = (
            f"Es gibt **{len(overlap)} Tage mit Parallelmessung**. Direkt berechneter "
            f"Offset (neu − alt): **{overlap_diff:+.2f} °C** — der neue Standort ist "
            f"{'kälter' if overlap_diff < 0 else 'wärmer'}."
        )
    else:
        _txt = (
            "Es gibt **keinen einzigen Tag mit Parallelmessung** — die Stationen "
            "lösen sich nahtlos ab. Ein direkter Tag-für-Tag-Vergleich ist daher "
            "nicht möglich.\n\n"
            "Stattdessen vergleichen wir die **Monats-Klimatologien** zweier "
            "vergleichbarer Fenster (saisonbereinigt). Geschätzter Standort-Offset "
            f"(neu − alt): **{clim_offset:+.2f} °C** — der neue Standort "
            f"({station_new}) ist über (fast) alle Monate **kälter** als der alte "
            f"({station_old})."
        )
    mo.md(
        f"""
        {_txt}

        **Fazit:** Der Rückgang in Zeitreihen über den Wechsel hinweg ist primär ein
        **Standort-Artefakt**, kein Klimasignal. Zeitreihen über einen
        Stationswechsel hinweg müssen homogenisiert werden, bevor man Trends
        interpretiert.
        """
    )
    return


if __name__ == "__main__":
    app.run()

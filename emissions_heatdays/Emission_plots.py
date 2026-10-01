import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    # '%matplotlib notebook' command supported automatically in marimo

    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np

    plt.style.use("seaborn-darkgrid")
    return np, pd, plt


@app.cell
def _(plt):
    print(plt.style.available)
    return


@app.cell
def _(pd):
    df = pd.read_csv("../resources/emissions_heatdays/TAG_Schnee_StPoelten.csv")
    return (df,)


@app.cell
def _(df, pd):
    df["date"] = pd.to_datetime(df["time"].astype("datetime64"), format="%Y-%m-%d")
    return


@app.cell
def _(df, np):
    df["is_snow"] = np.where(df["schnee"] > 0.1, 1, 0)
    return


@app.cell
def _(df):
    for index in df.index:
        if df["schnee"][index] > 0.1:
            df["is_snow"][index] = 1
        elif df["schnee"][index] <= 0.1:
            df["is_snow"][index] = 0
    return (index,)


@app.cell
def _(df):
    df.set_index("date", drop=False, inplace=True)
    return


@app.cell
def _(df):
    df_sum = df[["is_snow", "date"]]
    return (df_sum,)


@app.cell
def _(df_sum):
    df_sum["year"] = df_sum["date"].dt.year
    return


@app.cell
def _(df_sum, pd):
    summiert = df_sum.groupby(pd.Grouper(key="date", axis=0, freq="5Y")).sum()
    summiert = summiert[["is_snow"]][1:]
    return


@app.cell
def _(df_sum):
    summiert_1 = df_sum.groupby(df_sum.index.year // 10 * 10).sum()
    return (summiert_1,)


@app.cell
def _(summiert_1):
    summiert_1["Schneetage/Jahr"] = summiert_1["is_snow"] / 10
    return


@app.cell
def _(summiert_1):
    summiert_1["Schneetage/Jahr"][2020] = summiert_1["is_snow"][2020] / 3
    return


@app.cell
def _(summiert_1):
    summiert_1["Jahre"] = [
        "vor 1950",
        "1950-1959",
        "1960-1969",
        "1970-1979",
        "1980-1989",
        "1990-1999",
        "2000-2009",
        "2010-2019",
        "2020-2022",
    ]
    summiert_1.set_index("Jahre", drop=True, inplace=True)
    return


@app.cell
def _(plt, summiert_1):
    summiert_1["Schneetage/Jahr"][1:].plot.bar()
    plt.title("Durchschnittliche Anzahl der Tage mit Schnee in St. Pölten", fontsize=17)
    return


@app.cell
def _(df, index, pd):
    df.groupby(pd.Grouper(key=index, axis=0, freq="10Y")).sum()
    return


@app.cell
def _(df_sum, pd):
    summiert_20a = df_sum.groupby(pd.Grouper(key="date", axis=0, freq="20Y")).sum()
    return (summiert_20a,)


@app.cell
def _(summiert_20a):
    summiert_20a["is_snow"][1:].plot.bar()
    return


if __name__ == "__main__":
    app.run()

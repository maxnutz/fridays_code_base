import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import pandas as pd
    from datetime import datetime
    import matplotlib.pyplot as plt

    data = pd.read_csv(
        "../resources/emissions_heatdays/TAG_Krems_19400101_20211231.csv"
    )
    return data, datetime, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Set index for time and year
    """)
    return


@app.cell
def _(data, datetime):
    for i in range(0, data.index.size):
        data.time[i] = datetime.strptime(data.time[i], "%Y-%m-%d")
        data["year"] = 0
    for j in range(0, data.index.size):
        data["year"][j] = data.time[j].strftime("%Y")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Calculate heatdays in Krems
    """)
    return


app._unparsable_cell(
    r"""
    data['heatday'] = 0
    data['frosttage'] = 0
    data['good_night'] = 0
    for k in range(0, data.index.size):
        if data.tmax[k] > 29.9:
            data['heatday'][k] = 1
        else:
            data['heatday'][k] = 0
        if data.tmin[k] < 20:b
            data['good_night'][k] = 1
        else:
            data['good_night'][k] = 0
        if data.tmin[k] < 0:
            data['frosttage'][k] = 1
        else:
            data['frosttage'][k] = 0
    """,
    name="_",
)


@app.cell
def _(data):
    data["extreme_heat"] = 0
    for k in range(0, data.index.size):
        if data.tmax[k] > 35:
            data["extreme_heat"][k] = 1
        else:
            data["extreme_heat"][k] = 0
    return


@app.cell
def _(grouped_df, plt):
    plt.figure(figsize=(12, 4))
    grouped_df["extreme_heat"][10:].plot(kind="bar", color="r")
    plt.ylim(0, 10)
    plt.title("Number of heatdays in Krems", fontsize=20)
    return


@app.cell
def _(data):
    grouped_df = data.groupby("year").sum()
    # grouped_df['frosttage'].plot(kind = 'bar')
    # grouped_df['frosttage'].plot(kind = 'bar', ax=ax, color = "b")
    return (grouped_df,)


@app.cell
def _(data):
    data_1 = data.drop(["station"], axis=1)
    data_1 = data_1.drop(["substation"], axis=1)
    return (data_1,)


@app.cell
def _(data_1):
    data_2 = data_1.sort_values("time")
    data_2 = data_2.set_index("time")
    return (data_2,)


@app.cell
def _(data_2):
    data_2.plot(figsize=(20, 5))
    return


@app.cell
def _(data_2):
    data_2["year"] = data_2
    return


@app.cell
def _(data_2):
    # for i in range(0, data.index.size):
    #   data['year'][i] = data.index[i][:4]
    data_2["year"] = data_2.index
    return


@app.cell
def _(data_2):
    for i_1 in range(0, data_2.index.size):
        data_2["year"][i_1] = data_2["year"][i_1][:4]
    return


@app.cell
def _(data_2):
    data_2["heatday"] = data_2["tmax"]
    data_2
    return


@app.cell
def _(data_2):
    data_2["heatday"] = data_2["tmax"]
    for i_2 in range(0, data_2.index.size):
        if data_2["heatday"][i_2] > 29:
            data_2["heatday"][i_2] = 1
            print("heatday!")
        else:
            data_2["heatday"][i_2] = 0
    return


@app.cell
def _(data_2):
    yearly = data_2.groupby("year").sum()
    return (yearly,)


@app.cell
def _(yearly):
    yearly_1 = yearly.drop(["tmax"], axis=1)
    return (yearly_1,)


@app.cell
def _(yearly_1):
    yearly_1.plot()
    return


@app.cell
def _():
    246 - 234
    return


if __name__ == "__main__":
    app.run()

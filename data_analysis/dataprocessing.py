import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def load_df(filepath):
    df = pd.read_csv(filepath, sep=";", low_memory=False)
    df.columns = [
        x.replace("obj_", "").replace("ga_", "").replace("geo_", "") for x in df.columns
    ]
    df = df.drop_duplicates(subset="scoutId")
    return df


def create_rent_df(date):
    rent_filepath = "../data/mieten" + date + ".csv"
    rent_df = load_df(rent_filepath)
    rent_df["rent_m2"] = rent_df["baseRent"] / rent_df["livingSpace"]
    return rent_df


def create_sale_df(date):
    sale_filepath = "../data/kaufen" + date + ".csv"
    sale_df = load_df(sale_filepath)
    sale_df["price_m2"] = sale_df["purchasePrice"] / sale_df["livingSpace"]
    return sale_df


def remove_nan_inf(df, allowed_nan_percentage_cols):
    df.replace([np.inf, -np.inf], np.nan)
    df = df.loc[:, df.isnull().sum() < allowed_nan_percentage_cols * df.shape[0]]
    df = df[~df.isin([np.nan, np.inf, -np.inf]).any(1)]
    return df


def create_combined_df(date):
    rent_df = create_rent_df(date)
    sale_df = create_sale_df(date)
    g = rent_df.groupby("zipCode")["rent_m2"].median()
    g.name = "rent_m2_zipCode"
    sale_df = sale_df.join(g, on="zipCode").copy()
    sale_df["yearly_ROI"] = sale_df["rent_m2_zipCode"] * 12 / sale_df["price_m2"]

    group = "zipCode"
    combined_df = pd.concat(
        [
            sale_df.groupby(group)["yearly_ROI"].median(),
            rent_df.groupby(group)["rent_m2"].median(),
            rent_df.groupby(group)["rent_m2"].size(),
            sale_df.groupby(group)["price_m2"].median(),
            sale_df.groupby(group)["price_m2"].size(),
        ],
        axis=1,
        keys=[
            "median_yearly_ROI " + date,
            "median_rent_m2 " + date,
            "num_rent " + date,
            "median_price_m2 " + date,
            "num_sale " + date,
        ],
    ).copy()
    return combined_df


def compute_change(df, df_column, startdate, enddate):
    return df[df_column + enddate] / df[df_column + startdate]


def plot_1feature(df, attr, dates, feature1):
    x = dates
    y1 = [df.loc[attr][f"{feature1} {date}"] for date in x]
    color1 = "orange"

    fig, ax = plt.subplots()
    fig.suptitle(f"{feature1} in {attr}")

    ax.set_xlabel("date")
    ax.set_ylabel(feature1, color=color1)
    ax.plot(x, y1, color=color1, label=feature1)
    ax.set_xticklabels(x, rotation=90)

    ax.legend()
    plt.show()


def plot_2features(df, rentsale_type, attr, dates, feature1, feature2):
    x = dates
    y1 = [df.loc[attr][f"{feature1} {date}"] for date in x]
    y2 = [df.loc[attr][f"{feature2} {date}"] for date in x]
    color1 = "blue"
    color2 = "green"

    fig, ax1 = plt.subplots()
    fig.suptitle(f"Apartments for {rentsale_type} in {attr}")

    ax1.set_xlabel("date")
    ax1.set_ylabel(feature1, color=color1)
    ax1.xaxis.set_major_locator(plt.MaxNLocator(7))
    ax1.plot(x, y1, color=color1, label=feature1)
    ax1.set_xticklabels(x, rotation=90)

    ax2 = ax1.twinx()
    ax2.set_ylabel(feature2, color=color2)
    ax2.xaxis.set_major_locator(plt.MaxNLocator(7))
    ax2.plot(x, y2, linestyle="--", color=color2, label=feature2)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2)

    plt.savefig(f"{rentsale_type}_timeseries_plot.png", bbox_inches="tight")
    plt.show()

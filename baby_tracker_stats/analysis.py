"""Define analytical methods to run on baby stats here."""

import pandas as pd

MAX_DAYTIME_DT_HOURS = 6


def analyze_daytime_sleep(
    df: pd.DataFrame, last_n_weeks: int
) -> tuple[pd.DataFrame, str]:
    min_timestamp = (
        pd.Timestamp.utcnow() - pd.Timedelta(weeks=last_n_weeks)
    ).to_datetime64()
    sub_df = df.loc[
        (df["daytime"])
        & (df["dt_hours"] < MAX_DAYTIME_DT_HOURS)
        & (df["Time"] >= min_timestamp)
    ]
    summary = (
        f"Mean +/- 95% confidence interval: {sub_df['dt_hours'].mean():.2f} "
        f"+/- {1.96*sub_df['dt_hours'].std():.2f}"
    )
    return sub_df, summary


def predict_number_of_night_wakings():
    """Predict the number of times that baby will wake based on monitored data.

    TODO: implement
    """
    pass

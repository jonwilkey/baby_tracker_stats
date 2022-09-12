from dataclasses import dataclass
from io import BytesIO
from typing import Optional
from zipfile import ZipFile

import pandas as pd

DESIRED_COLUMNS = {"Time", "dt_hours", "daytime", "Duration", "feed_type", "sleep_end"}


@dataclass
class BabyStats:
    sleep: pd.DataFrame
    nursing: pd.DataFrame
    pumped: pd.DataFrame
    all_feeding: Optional[pd.DataFrame] = None


def extract_zip_data(file: BytesIO) -> BabyStats:
    input_zip = ZipFile(file=file)
    stats = BabyStats(
        **{
            key: _parse_to_dataframe(name, input_zip)
            for name in input_zip.namelist()
            for key in BabyStats.__annotations__.keys()
            if key in name
        }
    )
    stats.all_feeding = pd.concat([stats.nursing, stats.pumped], ignore_index=True)
    stats.all_feeding = stats.all_feeding.sort_values(by="Time").reset_index(drop=True)
    return stats


def _parse_to_dataframe(name: str, input_zip: ZipFile) -> pd.DataFrame:
    df = pd.read_csv(input_zip.open(name))
    df["Time"] = df["Time"].apply(pd.Timestamp)
    df["daytime"] = df["Time"].apply(_is_daytime)
    df.sort_values(by="Time", inplace=True)
    if "sleep" in name:
        df = _clean_sleep_df(df)
    elif "nursing" in name:
        df["feed_type"] = "nursing"
    elif "pumped" in name:
        df["feed_type"] = "pumped"
    return df[[col for col in df.columns if col in DESIRED_COLUMNS]].reset_index(
        drop=True
    )


def _is_daytime(ts: pd.Timestamp, morning: int = 7, night: int = 19) -> bool:
    return morning <= ts.hour < night


def _convert_duration_string(duration_str: str) -> float:
    hours = 0
    parts = duration_str.split(" ")
    for n in range(0, len(parts), 2):
        if parts[n + 1] == "hr" or parts[n + 1] == "hrs":
            hours += float(parts[n])
        elif parts[n + 1] == "min":
            hours += float(parts[n]) / 60
        else:
            raise ValueError(f"{parts[n]} does not match 'hr' or 'min'.")
    return pd.Timedelta(hours=hours)


def _clean_sleep_df(sleep_df: pd.DataFrame) -> pd.DataFrame:
    df = sleep_df.loc[~pd.isnull(sleep_df["Duration"])].copy()
    df["Duration"] = df["Duration"].apply(_convert_duration_string)
    df["sleep_end"] = df["Time"] + df["Duration"]
    df["dt_hours"] = _calculate_timedelta(df["Time"] - df["sleep_end"].shift(periods=1))
    return df


def _calculate_timedelta(ts: pd.Series) -> pd.Series:
    return ts.apply(lambda x: x.total_seconds() / 3600)

import pandas as pd

# ?
def to_df(input) -> pd.DataFrame:
    return pd.DataFrame(input)


def write_csv(df : pd.DataFrame, filepath : str) -> None:
    df.to_csv(filepath, index=False)

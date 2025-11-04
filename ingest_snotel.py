from datetime import datetime
from metloom.pointdata import SnotelPointData

# Get Butte SNOTEL data
snotel_point = SnotelPointData("380:CO:SNTL", "Butte")
df = snotel_point.get_daily_data(
    datetime(2021, 10, 1),
    datetime(2023, 9, 30),
    [snotel_point.ALLOWED_VARIABLES.SWE, snotel_point.ALLOWED_VARIABLES.TEMP]
).droplevel("site")

# convert SWE -> mm
df["SWE"] = df["SWE"] * 25.4
df["PRECIP"] = df["SWE"].diff().shift(-1)
df["AIR TEMP"] = (5 / 9) * (df["AIR TEMP"] - 32)

df = df.drop(columns=["geometry", "SWE_units", "AIR TEMP_units", "datasource"])

df.to_csv("./data/snotel.csv")

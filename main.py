import pandas as pd
from model import run_model, ModelParams
import matplotlib.pyplot as plt


snotel_data = pd.read_csv("./data/snotel.csv")
rad_data = pd.read_csv("./data/11557_lat_38.8714_lon_-106.9784_2025-11-03_142833.csv")

data = snotel_data
data["DAYLIGHT"] = rad_data["dayl (s)"]
data["SHORT_RAD"] = rad_data["srad (W/m^2)"]

params = ModelParams()
model_df = run_model(data, params)
model_df = model_df.set_index("datetime")
model_df.index = pd.to_datetime(model_df.index)

# Plot summary results
# fig, axes = plt.subplots(nrows=5, figsize=(7, 12))

# axes[0].plot(model_df["SWE"], label="SWE")
# axes[0].plot(model_df["SWE_model"], label="Modeled SWE")
# axes[0].legend()
# axes[0].set_title("SWE")

# axes[1].plot(model_df["PRCP"], label="Total Precip")
# axes[1].plot(model_df["prcp_snow_mm"], label="Snow")
# axes[1].legend()
# axes[1].set_title("Precip")

# axes[2].plot(model_df["albedo"])
# axes[2].set_title("Albedo")

# axes[3].plot(model_df["AIR TEMP"])
# axes[3].set_title("Air Temp")

# axes[4].plot(model_df["SHORT_RAD"])
# axes[4].set_title("Shortwave Radiation")

# plt.tight_layout()
# plt.show()

plt.figure(figsize=(7,4))
plt.plot(model_df["SWE"], label="Measured", color="black")
plt.plot(model_df["SWE_model"], label="Modeled", color="blue")
plt.title("Snow Water Equivalent, Butte SNOTEL")
plt.ylabel("mm")
plt.legend()

plt.show()


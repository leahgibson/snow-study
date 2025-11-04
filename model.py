"""
Hybrid degree day + shortwave radiation single-layer snow model.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd

# Physical constants
DENSITY_W = 1000.0 # kg m^-3
LATENT_HEAT = 3.34e5 # J kg^-1
SECONDS_PER_DAY = 86400

@dataclass
class ModelParams:
    DDF: float = 2.0 # mm C^-1 day^-1 (degree day factor)
    T_melt: float = 0.0 # C (melt threshold)
    T_air_threshold: float = 5.0 # C (air temp when we assume snowpack temp is 0 C)
    albedo_init: float = 0.75 # initial albedo
    albedo_min: float = 0.50 # min albedo as snow ages
    albedo_decay: float = 7 # decay timescale (days) for albedo
    prcp_snow_threshold: float = 0.0 # temp threshold for snow
    prcip_transition_width: float = 1.0 # C

class SnowModel:
    def __init__(self, params: ModelParams):
        self.p = params
        self.SWE = 0.0
        self.days_since_snow = 9999
        self.history = {
            "SWE": [],
            "melt_mm": [],
            "prcp_mm": [],
            "albedo": []
        }
    
    def precip_partition(self, temp: float, prcp_mm:float):
        """
        Partition liquid-equivalent precipitation into snow (mm) and rain (mm)
        using a linear transition band.

        prcp_snow = f(T) * prcp_total
        prcp_rain = (1-f(T)) * prcp_total

        where f(T) is linear
        """

        width = self.p.prcip_transition_width
        threshold_temp = self.p.prcp_snow_threshold

        if width <= 0:
            prcp_snow = prcp_mm if temp <= threshold_temp else 0.0
        
        else:
            if temp <= (threshold_temp - width):
                frac = 1.0
            elif temp >= (threshold_temp + width):
                frac = 0.0
            else:
                # linear interpolation
                frac = (threshold_temp + width - temp) / (2 * width)
            prcp_snow = prcp_mm * frac
        
        return prcp_snow

    def compute_albedo(self, new_snow: float):
        """
        Manage albedo state. If new snow, reset albedo.
        Otherwise, albedo exponentially decays until albedo_min

        albedo = albedo_init * (albedo_min / albedo_init)^(x / decay)
        """

        if new_snow > 0:
            self.days_since_snow = 0
            albedo = self.p.albedo_init
        else:
            self.days_since_snow += 1
            if self.days_since_snow <= self.p.albedo_decay:
                albedo = self.p.albedo_init * ((self.p.albedo_min / self.p.albedo_init)**(self.days_since_snow / self.p.albedo_decay))
            else:
                albedo = self.p.albedo_min
        
        return albedo
                                               
    def step(self, temp: float, prcp: float, short_rad: float, daylight: float):
        """
        Compute daily
        
        Returns: SWE, melt, prcp_snow, runoff
        """
        SWE_t0 = self.SWE # current SWE

        # Partition the precip
        prcp_snow = self.precip_partition(temp, prcp)


        # Only compute melt if there is something to melt
        if SWE_t0 > 0 or prcp_snow > 0:

            # Update albedo
            albedo = self.compute_albedo(prcp_snow)

            # Melt forced by temperature
            if temp > self.p.T_melt:
                melt_temp = self.p.DDF * (temp - self.p.T_melt)
            else:
                melt_temp = 0.0
            
            # Melt forced by rad only if air temp > 5
            # This (hopefully) isolates forcing to spring
            if temp > self.p.T_air_threshold:
                melt_rad = (((1 - albedo) * short_rad * daylight) / (DENSITY_W * LATENT_HEAT)) * 1000
            else:
                melt_rad = 0.0
            

            # Total melt
            melt_total = max(0.0, melt_temp + melt_rad)
        else:
            melt_total = 0.0
            albedo = 0.0

        # Update mass balance 
        SWE_t1 = SWE_t0 + prcp_snow - melt_total

        if SWE_t1 < 0: # everything melted
            SWE_t1 = 0.0
 
        
        # Store new states
        self.SWE = SWE_t1
        self.history["SWE"].append(self.SWE)
        self.history["melt_mm"].append(melt_total)
        self.history["prcp_mm"].append(prcp_snow)
        self.history["albedo"].append(albedo)

        return self.SWE, melt_total, prcp_snow, albedo


def run_model(df: pd.DataFrame, params: ModelParams) -> pd.DataFrame:
    """
    Run SnowModel for given data with daily parameters.
    """

    required_cols = {"SWE", "AIR TEMP", "PRCP", "DAYLIGHT", "SHORT_RAD"}
    if not required_cols.issubset(set(df.columns)):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Input dataframe missing required columns: {missing}")

    model = SnowModel(params)
    model.SWE = df["SWE"][0]

    for i, row in df.iterrows():
        model.step(
            temp=row["AIR TEMP"],
            prcp=row["PRCP"],
            short_rad=row["SHORT_RAD"],
            daylight=row["DAYLIGHT"]
        )
    
    df_model = df.copy()
    df_model["SWE_model"] = model.history["SWE"]
    df_model["melt"] = model.history["melt_mm"]
    df_model["prcp_snow_mm"] = model.history["prcp_mm"]
    df_model["albedo"] = model.history["albedo"]

    return df_model


   











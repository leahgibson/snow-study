## Overview

This model is a simplified, one layer, physically based snowmelt model that tracks snow water equivalent (SWE) through time by accounting for accumulation from snowfall and losses from melt driven by energy inputs.
Here, I model the 2022 and 2023 water years in Crested Butte, using the Butte SNOTEL data as input.

## Model and Assumptions

We begin with the snow water equivalent mass balance equation:
$$
    \frac{d\text{SWE}}{dt} = P_{\text{snow}} - M
$$
where $P_{snow}$ is the liquid water equivalent precipitation due to snowfall and $M$ is melt, both in mm. 

The amount of snowfall is determined by partitioning measured SWE into snow and rain contribution using air temperature such that
$$ P_{\text{snow}} = f(T) P_{\text{total}} $$
where $f(T)$ is a linear function spanning the transitioin in temperature between rain and snow.

Melt is separated into melt forced by temperature and melt forced by shortwave radiation. Melt forced by temperature, $M_{\text{temp}}$ uses a degree-day forcing (DDF) assumption of 2 degrees C, and thus is the mean air temperature, $T_{\text{mean}}$ is above 0 degrees C, then the melt forces by temperature, $M_{\text{temp}}$ is
$$M_{\text{temp}} = DDF(T_{\text{mean}}).$$

The melt forced by shortwave radiation is given by
$$M_{\text{rad}} = \frac{(1-\alpha)_{in}t_{\text{day}}}{\rho_w L_f}$$
where $\alpha$ is spectral albedo, $S_{in}$ is shortwave radiation, and $t_{\text{day}}$ is the amount of daylight. Albedo follows an exponential decay to account for snow aging.

I used forward Euler with a daily timestep to model the evolution of SWE:
$$SWE_{t+1} = SWT_t + P_{\text{snow}} - M.$$



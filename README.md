# wx
by [Moritz Wunderwald](mailto:code@moritzwunderwald.de), 2025

Visual feedback system for parameter settings in windowed cross-correlation, optimized for IBI and EDA data. Validate data, set parameters, run batches and rp analysis.

# Setup

The software is in the subdirectory 'src'. After downloading, follow these steps:

+ switch into ./src
+ create a virtual environment
+ install the requirements using requirements.txt
+ run the app: python3 -m app.py

👩‍💻 ... adding more detail soon

# References

## Windowed Cross-Correlation

[About WCC](https://www.researchgate.net/publication/11148356_Windowed_cross-correlation_and_peak_picking_for_the_analysis_of_variability_in_the_association_between_behavioral_time_series)
[WCC GUI Tool](https://measurement.psy.miami.edu/wcc.phtml)
[WCC plot](https://www.researchgate.net/figure/Computation-and-basic-plot-of-the-windowed-cross-correlation-between-two-time-series-The_fig6_290016090)

- zero-order correlation coefficients of the two time-series along the midpoint of the display
- correlations between the previous behavior of one partner and the subsequent behavior of the other partner

## UI

[customTkinter](https://github.com/TomSchimansky/CustomTkinter)
[customTkinter docs](https://customtkinter.tomschimansky.com/documentation)

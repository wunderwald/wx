# WX: Windowed Cross-Correlation Analysis for Physiological Signals

**WX** is an interactive visual toolbox for analyzing windowed cross-correlation in dyadic physiological signals. It enables researchers to measure and visualize the dynamic synchronization of physiological metrics (such as heart rate variability via Inter-Beat Interval and skin conductance via Electrodermal Activity) between two individuals over time. The software provides real-time parameter tuning, statistical validation, and batch processing capabilities for comprehensive physiological synchrony research.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
  - [Interactive Correlation Analysis](#interactive-correlation-analysis)
  - [Windowed Cross-Correlation (WCC)](#windowed-cross-correlation-wcc)
  - [Standard Cross-Correlation (SCC)](#standard-cross-correlation-scc)
  - [Data Preprocessing](#data-preprocessing)
  - [Batch Processing](#batch-processing)
  - [Statistical Validation](#statistical-validation)
  - [Data Export](#data-export)
  - [Detrended Fluctuation Analysis](#detrended-fluctuation-analysis)
- [Architecture & Module Reference](#architecture--module-reference)
- [Usage Guide](#usage-guide)
- [Data Format](#data-format)
- [Output Files](#output-files)
- [Key Concepts](#key-concepts)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What is Physiological Synchrony?

Physiological synchrony refers to the coordinated timing and alignment of physiological signals between two or more individuals. WX quantifies this synchrony by computing cross-correlation between dyadic partners' physiological signals across multiple time windows, revealing how dynamic and stable their physiological coordination is.

### When to Use WX

- **Research Context**: Studying interpersonal dynamics, attachment, empathy, or therapeutic outcomes
- **Clinical Assessment**: Evaluating patient-therapist synchrony or patient adaptation to treatment
- **Behavioral Ecology**: Analyzing dyadic interactions in naturalistic settings
- **Exploratory Analysis**: Testing different correlation window sizes and lag ranges to understand temporal relationships
- **Statistical Validation**: Comparing real dyad correlations against chance/random pairings

### Key Capabilities

✓ Interactive GUI for real-time parameter exploration
✓ Windowed cross-correlation with sliding window analysis
✓ Multiple output metrics (peak correlation, peak lag, flexibility indices)
✓ Sigmoid scaling for improved visualization contrast
✓ Automatic signal preprocessing (resampling, standardization, validation)
✓ Batch processing across entire datasets
✓ Statistical significance testing via random pair analysis
✓ Visual plots (heatmaps, lag traces, signal overlays)
✓ Excel export with full metadata and results
✓ DFA (Detrended Fluctuation Analysis) for long-range correlation detection

---

## Installation

### Requirements

- **Python 3.x** (3.9+ recommended)
- Operating System: macOS, Windows, or Linux

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd /path/to/wx
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Key packages installed:
   - `customtkinter`: Modern GUI framework
   - `numpy`, `scipy`: Numerical computing and signal processing
   - `matplotlib`: Visualization
   - `openpyxl`: Excel file I/O

3. **Run the application**:
   ```bash
   python src/app.py
   ```

### Building Standalone Executable

To create a standalone application that doesn't require Python installed:

```bash
python src/build.py
```

The bundler supports multiple strategies (auto-detect, brute-force, minimal) depending on your environment. See `build.py` for configuration options.

---

## Quick Start

### 1. Launch the Application

```bash
python src/app.py
```

A window opens with three tabs: **Input Data**, **Correlation Analysis**, and **Export & Batch**.

### 2. Load Physiological Data

**Tab 1: Input Data**

1. Click **"Browse"** under "Select Folder" to navigate to a dyad directory
2. The folder should contain Excel files (.xlsx) with raw physiological data
3. Select a file and the list of available sheets appears
4. Choose the sheet containing your signal data
5. Select columns for **Signal A** and **Signal B** (usually IBI and EDA columns)
6. Specify the **Data Type** (Event-based for IBI, Fixed-rate for EDA)
7. Review the **Data Preview** table to confirm correct data loading
8. Data is automatically preprocessed: validated, resampled, and standardized

### 3. Configure Correlation Analysis

**Tab 2: Correlation Analysis**

1. Set **Window Size**: How many samples per analysis window (e.g., 60 samples)
2. Set **Step Size**: How many samples to advance between successive windows (e.g., 30 samples)
3. Set **Max Lag**: Maximum time offset to explore (e.g., ±20 samples)
4. Configure **Lag Filter**: Optionally restrict analysis to specific lag ranges
5. Toggle **Advanced Options**:
   - **Use Absolute Values**: Analyze absolute correlation magnitude
   - **Average Across Windows**: Produce per-window averaged correlations
   - **Use Sigmoid Scaling**: Enhance visualization contrast
6. Click **Plot** to visualize the windowed cross-correlation in real-time
7. Adjust parameters and replot to explore different parameter configurations

### 4. Export Results

**Tab 3: Export & Batch Processing**

1. Save current analysis results to Excel: Click **"Export to XLSX"**
2. Save plot visualization as PNG: Click **"Export Plot as PNG"**
3. For batch processing across all dyads in a directory: Configure settings and click **"Run Batch Processing"**
4. For statistical significance testing: Click **"Run Random Pair Analysis"**

---

## Core Features

### Interactive Correlation Analysis

The main interface provides real-time visualization of cross-correlation results. As you adjust parameters, plots update immediately, allowing rapid exploration of different analysis configurations.

**Key UI Elements**:
- **Parameter Entry Fields**: Window size, step size, max lag, lag filter bounds
- **Data Type Selector**: IBI (event-based) or EDA (fixed-rate) configuration
- **Plot Canvas**: Interactive matplotlib figure embedded in the GUI
- **Data Preview Table**: Raw and processed signal display
- **Validation Indicators**: Error messages for invalid parameter combinations

**Input Constraints**:
- Window size must be ≥ 1 and ≤ data length
- Step size must be ≤ window size
- Max lag must be ≤ window size / 2
- Lag filter minimum must be ≤ lag filter maximum
- All numeric parameters are validated in real-time

### Windowed Cross-Correlation (WCC)

The core analysis mode that computes cross-correlation within sliding windows.

**Parameters**:

| Parameter | Meaning | Typical Range | Example |
|-----------|---------|---------------|---------|
| **Window Size** | Samples per window (temporal resolution) | 10–1000 | 60 =  12 sec @ 5Hz |
| **Step Size** | Overlap between windows | 1–window size | 30 = 50% overlap |
| **Max Lag** | ±Samples to check for delay | 1–window size/2 | 20 = ±4 sec @ 5Hz |
| **Lag Filter Min** | Lower bound for lag inclusion | -max_lag–0 | -10 |
| **Lag Filter Max** | Upper bound for lag inclusion | 0–max_lag | +10 |

**Output Metrics** (computed per window):

- **r_max**: Peak cross-correlation magnitude (0–1 range)
- **tau_max**: Lag at which peak correlation occurs (sample units)
- **correlations**: Full correlation vector across all tested lags
- **avg_z_transformed_corr**: Average Fisher z-transformed correlation (consistency metric)
- **var_z_transformed_corr**: Variance of z-transformed correlations (flexibility metric)

**Visualization**:
- **Heatmap**: Color-coded correlation values (lags on x-axis, time windows on y-axis)
- **Peak Correlation Trace**: r_max across windows showing synchrony strength over time
- **Lag Trace**: tau_max across windows showing leader-follower dynamics
- **Signal Overlay**: Original time series for reference and interpretation

**Algorithm**:
```
For each window position:
  1. Extract signal windows [start:start+window_size]
  2. For each lag in [-max_lag:max_lag]:
     - Compute Pearson correlation between Signal A and Signal B (shifted by lag)
  3. Record maximum correlation (r_max) and corresponding lag (tau_max)
  4. Optionally apply Sigmoid scaling to emphasize near-zero values
  5. Optionally compute z-transformed statistics
```

### Standard Cross-Correlation (SCC)

Computes a single correlation coefficient across the entire signal pair (no windowing).

**Use Cases**:
- Baseline comparison against windowed results
- Faster computation for initial exploration
- Input to DFA (Detrended Fluctuation Analysis)
- Statistical comparison in random pair analysis

**Output**:
- Single global correlation coefficient
- Corresponding lag

### Data Preprocessing

All loaded data undergoes automatic preprocessing to ensure quality and consistency.

**Pipeline Steps**:

1. **Event-Based Validation (IBI Data)**:
   - Filters inter-beat intervals outside the 100–1000 ms physiological range
   - Removes impossible heartbeat values that indicate sensor errors or artifacts

2. **Signal Resampling (IBI Only)**:
   - IBI events (irregular timing) are resampled to a uniform 5 Hz time series
   - Uses cubic spline interpolation to smoothly convert event-based data to fixed-rate format
   - Ensures compatibility with fixed-rate EDA signals

3. **Length Alignment**:
   - Truncates longer signal to match shorter signal length
   - Ensures both signals have identical time spans for correlation analysis

4. **Z-Score Standardization**:
   - Centers each signal to zero mean
   - Scales each signal to unit variance (σ=1)
   - Makes correlation coefficients interpretable across different data ranges
   - Formula: `z = (x - mean(x)) / std(x)`

5. **Visual Validation**:
   - Data preview table displays raw and processed signals side-by-side
   - Confirms preprocessing success before analysis

**Key Distinctions**:
- **Z-score** (standardization): Raw data normalization to zero mean and unit variance
- **z-transform** (Fisher transform): Statistical transformation of correlation coefficients via `z = 0.5 * ln((1+r)/(1-r))`
  - Used for flexibility/consistency metrics in WCC output

### Batch Processing

Apply identical analysis parameters to an entire dataset of dyads.

**Workflow**:
1. Configure all parameters in the GUI (window size, lag settings, etc.)
2. Select a batch directory containing multiple dyad folders
3. Click **"Run Batch Processing"**
4. For each dyad:
   - Loads all Excel files in the folder
   - Applies preprocessing
   - Computes WCC with fixed parameters
   - Optionally computes DFA per lag
   - Exports results to XLSX
5. Generates summary statistics across the batch

**Output**:
- Individual XLSX files per dyad pair (with results and metadata)
- Optional DFA scaling exponents
- Processing log with success/failure status per dyad

### Statistical Validation

**Random Pair Analysis**: Compares real dyad correlations against statistically null random pairings.

**Methodology**:
1. Extract all individual physiological signals from the participant pool
2. Create synthetic dyads by randomly pairing signals from different individuals
3. Compute correlation for each random pairing using the same analysis parameters
4. Compare real dyad r_max values against the distribution of random pair correlations
5. Perform independent samples t-test: real dyads vs. random pairs
6. Calculate p-value and effect size (Cohen's d)

**Interpretation**:
- **p < 0.05**: Real dyads show significantly higher (or lower) correlation than chance
- **High effect size**: Substantial difference between real and random synchrony
- **Used for**: Validating that observed synchrony isn't merely random artifact

### Data Export

#### XLSX Export

Comprehensive Excel files containing analysis results and metadata.

**Structure**:
- **Metadata Sheet**:
  - Processing date/time
  - File names and sheet references
  - All analysis parameters (window size, lag range, etc.)
  - Data type configuration

- **Vector Data Sheet**:
  - Time series of input signals (original and standardized)
  - Cross-correlation output vectors (r_max, tau_max, etc.)
  - Per-window statistics (avg_z_transformed_corr, variance, etc.)

- **Per-Window Details Sheet**:
  - Individual correlation profiles for each window
  - Window start/center indices
  - Full lag-space correlation vectors

- **DFA Results** (if computed):
  - Scaling exponent (α) for DFA analysis
  - Provides context on long-range correlations in the data

#### PNG Export

Saves the current matplotlib visualization as a high-resolution PNG image, suitable for reports and presentations.

### Detrended Fluctuation Analysis (DFA)

DFA quantifies long-range correlations and self-affinity in time series data.

**What it measures**:
- **Scaling exponent (α)**: Describes how fluctuations scale with time window size
- **α = 0.5**: Random walk (no long-range correlation)
- **α > 0.5**: Persistent correlations (positive feedback)
- **α < 0.5**: Anti-persistent behavior (negative feedback)

**Implementation**:
- Applied to global cross-correlation (SCC)
- Can be applied per-lag in windowed analysis
- Polynomial detrending (configurable order)
- Returns both scaling exponent and goodness-of-fit (R²)

**Use Cases**:
- Characterizing the temporal structure of synchrony
- Comparing persistence across different dyads or conditions
- Detecting non-stationary behavior in physiological signals

---

## Architecture & Module Reference

### Module Overview

The codebase is organized into functional modules, each handling a specific aspect of analysis:

#### **app.py** (~1,300 lines)
Main GUI application. Implements the tabbed interface, user interactions, real-time plotting, and data management.

**Key Classes/Functions**:
- `GUI`: Primary application window (customtkinter.CTk)
- `PARAMS_CHANGED()`: Event handler for parameter updates and plot regeneration
- Input validation callbacks for all entry fields
- Plot canvas integration via matplotlib

**Responsibilities**:
- User interface and event handling
- State management (data containers, parameter variables)
- Real-time plot updates
- Dialog boxes for file selection and error reporting

---

#### **cross_correlation.py**
Core correlation computation engine.

**Key Functions**:

```python
windowed_cross_correlation(
    x, y,                          # Input signals
    window_size,                   # Samples per window
    step_size,                     # Window advancement
    max_lag,                       # ±Lag range to explore
    use_lag_filter=False,          # Apply lag filter?
    lag_filter_min=None,           # Lower lag bound
    lag_filter_max=None,           # Upper lag bound
    absolute=False,                # Use abs(correlation)?
    average_windows=False          # Average r values?
) -> dict
```

Returns dictionary with keys:
- `start_idx`, `center_idx`: Window position indices
- `r_max`: Maximum correlation per window
- `tau_max`: Lag at maximum correlation
- `correlations`: Full per-lag correlation vector
- `correlations_sigmoid`: Sigmoid-scaled correlations
- `avg_z_transformed_corr`, `var_z_transformed_corr`: Flexibility metrics

```python
standard_cross_correlation(x, y, max_lag) -> tuple
```

Returns single correlation coefficient and corresponding lag across entire signal.

---

#### **signal_processing.py**
Signal preprocessing and validation.

**Key Functions**:

```python
preprocess_dyad(
    signal_a, signal_b,           # Input signals
    data_type_a, data_type_b,     # 'IBI' or 'EDA'
    ibi_min=100, ibi_max=1000     # IBI validity range (ms)
) -> tuple
```

Returns preprocessed (raw, standardized) signal pairs.

Includes:
- IBI sample validation (removes HR impossibilities)
- IBI resampling to 5 Hz via cubic spline
- Length alignment
- Z-score standardization (scipy.stats.zscore)

```python
resample_ibi(ibi_times, ibi_values) -> np.array
```

Converts irregular event timing to uniform 5 Hz time series.

---

#### **plot.py**
Visualization engine using matplotlib.

**Key Functions**:

```python
create_plot(
    signal_a, signal_b,           # Input signals
    wcc_results,                  # Windowed correlation output
    title='',
    dpi_factor=1.0                # Retina/non-Retina scaling
) -> matplotlib.Figure
```

Generates 2×3 grid of subplots:
1. Input Signal A (time series)
2. Input Signal B (time series)
3. Correlation Heatmap (lags × windows)
4. Peak Correlation Trace (r_max over time)
5. Peak Lag Trace (tau_max over time)
6. Heatmap Legend (color scale)

**Features**:
- Magma colormap for perceptual uniformity
- Tight layout for efficient space usage
- DPI-aware scaling (detects Retina displays and adjusts font/figure size)
- Optional sigmoid scaling for contrast enhancement

---

#### **batch_processing.py**
Facilitates processing across multiple dyads.

**Key Functions**:

```python
batch_process(
    base_directory,               # Root folder containing dyads
    params,                       # Analysis parameters dict
    apply_dfa=False              # Also compute DFA?
) -> list
```

Returns list of results per dyad (success/failure status, output paths).

```python
random_pair_analysis(
    participant_signals,          # Dict of individual signals
    real_dyad_id,                # Reference dyad label
    analysis_params,             # WCC/SCC parameters
    n_random_pairs=100           # Number of synthetic pairings
) -> dict
```

Returns statistical comparison between real and random dyads.

---

#### **export.py**
Data serialization to Excel format.

**Key Functions**:

```python
export_to_xlsx(
    filename,                     # Output file path
    signal_a, signal_b,          # Input signals
    wcc_results,                 # Correlation output
    analysis_params,             # Parameter metadata
    dfa_results=None             # Optional DFA output
)
```

Creates multi-sheet Excel workbook with results and metadata.

---

#### **dfa.py**
Detrended Fluctuation Analysis implementation.

**Key Functions**:

```python
detrended_fluctuation_analysis(
    time_series,                 # Input signal
    min_window=10,               # Smallest window size
    max_window=None,             # Largest window size
    degree=1                     # Polynomial detrend order
) -> dict
```

Returns:
- `alpha`: Scaling exponent
- `fluctuations`: Per-window F(k) values
- `window_sizes`: Tested window sizes
- `r_squared`: Goodness-of-fit metric

---

#### **xlsx.py**
Low-level Excel file I/O utilities.

**Key Functions**:
- `load_workbook()`: Open and parse Excel files
- `get_sheet_names()`: List available sheets
- `get_column_data()`: Extract specific column data with type inference
- `create_workbook()`: Initialize new Excel files for export

---

#### **build.py**
Automated application bundler using PyInstaller.

**Strategies**:
1. **Smart auto-detect**: Analyzes imports and collects only necessary modules
2. **Brute force**: Includes all potentially relevant packages (larger binary)
3. **Minimal**: Creates skeleton requiring manual dependency setup

---

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User GUI (app.py)                     │
│  [Input Data Tab] [Correlation Tab] [Export/Batch Tab]  │
└────────────────────────┬────────────────────────────────┘
                         │
                    Parameter Input
                         │
    ┌────────────────────┴────────────────────┐
    │                                         │
┌───▼────────────────────┐    ┌──────────────▼────────┐
│ signal_processing.py   │    │ cross_correlation.py  │
│  • Validate            │    │  • windowed_xc()      │
│  • Resample (IBI)      │    │  • standard_xc()      │
│  • Standardize         │    │  • Sigmoid scaling    │
└───┬────────────────────┘    └──────────────┬────────┘
    │                                         │
    └────────────────────┬────────────────────┘
                         │
                    Processed Data
                         │
              ┌──────────┴──────────┐
              │                     │
        ┌─────▼──────────┐    ┌────▼─────────────┐
        │   plot.py      │    │  export.py       │
        │  • Heatmap     │    │  • XLSX export   │
        │  • Traces      │    │  • Metadata      │
        │  • Subplots    │    │  • Formatting    │
        └─────┬──────────┘    └────┬─────────────┘
              │                    │
              │              ┌─────▼──────────┐
              │              │   xlsx.py      │
              │              │  • I/O utils   │
              │              │  • Sheet ops   │
              │              └────────────────┘
              │
         ┌────▼─────────────────────────────────┐
         │  User Views Plot & Downloads Files   │
         └──────────────────────────────────────┘

Batch Processing Mode:
    batch_processing.py iterates over dyads, calling the pipeline above for each.

Statistical Validation:
    random_pair_analysis() in batch_processing.py generates synthetic pairings
    and compares against real dyads using statistical tests.

DFA Extension:
    dfa.py can be applied to correlation output to characterize long-range structure.
```

---

## Usage Guide

### Scenario 1: Exploring a Single Dyad

1. **Load Data**:
   - Navigate to Tab 1: Input Data
   - Browse to folder containing Excel file for one dyad pair
   - Select sheet and columns for Signal A and Signal B
   - Confirm data in preview table

2. **Configure Parameters**:
   - Navigate to Tab 2: Correlation Analysis
   - Start with default parameters (e.g., window_size=60, step_size=30, max_lag=20)
   - Click **Plot** to visualize

3. **Explore**:
   - Adjust window size to change temporal resolution
   - Modify lag range to focus on specific timing relationships
   - Toggle sigmoid scaling to adjust visualization contrast
   - Replot to see changes in real-time

4. **Export**:
   - Navigate to Tab 3: Export & Batch
   - Click **Export to XLSX** to save results table
   - Click **Export Plot as PNG** to save visualization

### Scenario 2: Batch Processing a Dataset

1. **Prepare Directory Structure**:
   ```
   /my_dataset/
   ├── dyad_001/
   │   ├── signals.xlsx
   │   └── signals_backup.xlsx
   ├── dyad_002/
   │   └── signals.xlsx
   └── dyad_003/
       └── signals.xlsx
   ```

2. **Configure Parameters**:
   - Configure all parameters in Tab 2 (window, lag, etc.)
   - These settings will be applied to all dyads

3. **Run Batch**:
   - Navigate to Tab 3: Export & Batch
   - Click **Browse** under batch processing
   - Select `/my_dataset/` directory
   - Click **Run Batch Processing**

4. **Review Results**:
   - A results folder is created with XLSX/PNG files for each dyad
   - Processing log shows success/failure status
   - Summary statistics aggregated across all dyads

### Scenario 3: Statistical Validation with Random Pairs

1. **Load All Participant Data**:
   - Ensure all individual signals from a study are accessible
   - Organize by participant ID

2. **Run Random Pair Analysis**:
   - Configure analysis parameters
   - Click **Run Random Pair Analysis** in Tab 3
   - Specify number of random pairings (default: 100)

3. **Interpret Results**:
   - Compare real dyad r_max against random pair distribution
   - Review t-test p-value (< 0.05 indicates significance)
   - Effect size (Cohen's d) indicates practical significance
   - Output includes visualization comparing distributions

---

## Data Format

### Input File Format

WX accepts **Excel (.xlsx) files** with the following structure:

**Sheet Layout**:
```
Row 1:   [Headers]
         Column A: Signal_A_Label  Column B: Signal_B_Label
Row 2:   [Units]
         Column A: ms or uS        Column B: ms or uS
Row 3+:  [Data]
         Column A: numeric values  Column B: numeric values
```

**Example for IBI & EDA**:
```
ibi_ms   eda_uS
100      1.5
105      1.6
98       1.4
...
```

**Data Type Specifications**:
- **IBI (Event-Based)**: Inter-beat intervals in milliseconds
  - Valid range: 100–1000 ms (corresponds to HR 60–600 bpm)
  - Will be resampled to 5 Hz uniform time series
  - Example: [100, 105, 98, 102, ...] ms

- **EDA (Fixed-Rate)**: Electrodermal activity in microSiemens or arbitrary units
  - Already uniform time series at original sampling rate
  - No resampling will be applied
  - Example: [1.5, 1.6, 1.4, 1.3, ...] µS

**Multi-Sheet Workbooks**:
- If a file contains multiple sheets, the GUI allows you to select which sheet to analyze
- Only two columns (Signal A and Signal B) are analyzed per run
- If you need to analyze different signal pairs, run the analysis multiple times

---

## Output Files

### XLSX Output Structure

Exported Excel files contain the following sheets:

**1. Metadata**
```
Analysis Parameters
────────────────────
File Name:           dyad_001_signals.xlsx
Sheet Name:          Synchronized
Processing Date:     2025-02-15 14:32:00
Window Size:         60
Step Size:           30
Max Lag:             20
Lag Filter Min:      -10
Lag Filter Max:      +10
Use Absolute Values: False
Use Sigmoid Scaling: False
Signal A Type:       IBI (resampled to 5 Hz)
Signal B Type:       EDA (fixed-rate 5 Hz)
```

**2. Vector Data**
```
Index | Time(s) | Signal_A_Raw | Signal_A_Std | Signal_B_Raw | Signal_B_Std | r_max | tau_max | Avg_z_transformed | Var_z_transformed
1     | 0.0     | 100.0        | -0.523      | 1.5          | -0.412      | 0.45  | 5       | 0.234             | 0.089
2     | 0.2     | 105.0        | 0.123       | 1.6          | 0.089       | 0.52  | -3      | 0.267             | 0.102
...
```

**3. Per-Window Details** (optional)
```
Window | Start_Idx | Center_Idx | r_max | tau_max | Correlation_Vector (lags=-20:+20)
1      | 0         | 30         | 0.45  | 5       | [0.12, 0.15, ..., 0.45, ..., 0.10]
2      | 30        | 60         | 0.52  | -3      | [0.11, 0.18, ..., 0.52, ..., 0.08]
...
```

**4. DFA Results** (if computed)
```
Analysis | Alpha | R_Squared | Window_Sizes | Fluctuations
Global   | 0.78  | 0.94      | [10, 15, ...] | [0.23, 0.35, ...]
```

### PNG Plot Structure

The exported PNG contains a 2×3 grid:

```
┌──────────────────────┬──────────────────────┬──────────────────────┐
│   Signal A (time)    │   Signal B (time)    │       Legend         │
├──────────────────────┼──────────────────────┼──────────────────────┤
│ Cross-Correlation    │ Peak Correlation     │   Peak Lag Trace     │
│   Heatmap            │   (r_max) Trace      │   (tau_max) Trace    │
└──────────────────────┴──────────────────────┴──────────────────────┘
```

---

## Key Concepts

### Windowed vs. Standard Cross-Correlation

| Aspect | Windowed (WCC) | Standard (SCC) |
|--------|---|---|
| **Scope** | Fixed-size sliding window | Entire signal pair |
| **Output** | Per-window metrics, heatmap | Single correlation value |
| **Time Resolution** | High (window-by-window) | None (static) |
| **Use Case** | Tracking dynamic synchrony | Baseline/comparison |
| **Computation** | O(n × m²) where m=window size | O(n²) |

### Peak Lag Interpretation

The **lag at maximum correlation (tau_max)** indicates leader-follower dynamics:
- **tau_max > 0**: Signal B lags behind Signal A (A leads B)
- **tau_max < 0**: Signal A lags behind Signal B (B leads A)
- **tau_max ≈ 0**: Simultaneous/synchronized

Example: If tau_max=5 at 5 Hz sampling, Signal B follows Signal A by 1 second.

### Flexibility Metrics

WX computes two flexibility-related metrics from z-transformed correlations:

1. **avg_z_transformed_corr**: Mean of Fisher z-transformed correlations
   - Higher values = stronger, more consistent correlation
   - Ranges from near 0 (weak) to 2+ (very strong)

2. **var_z_transformed_corr**: Variance of z-transformed correlations
   - Higher values = more variable/flexible synchrony
   - Lower values = rigid/consistent synchrony
   - Useful for contrasting "adaptability" vs. "consistency"

### Sigmoid Scaling

Sigmoid transformation emphasizes correlation values near zero while compressing extreme values:

```
sigmoid(x) = 1 / (1 + exp(-k*x))
```

**Why use it**:
- Raw correlation heatmaps often have values clustered between 0.2–0.5
- Sigmoid stretches this range for better visualization contrast
- Extreme values (near 1 or -1) are compressed and less visually dominating

### Lag Filtering

Restricts analysis to a subset of the lag range, focusing on specific timing relationships.

**Examples**:
- **Lag Filter Min: -5, Max: +5**: Only analyze lags within ±1 second (at 5 Hz)
- **Lag Filter Min: 0, Max: +20**: Only positive lags (Signal B leads Signal A)
- **No Filter**: Analyze all lags from -max_lag to +max_lag

---

## Advanced Features

### DFA Application to Correlation Data

The **dfa.py** module can be applied to cross-correlation vectors to characterize their temporal structure.

**Workflow**:
1. Compute standard cross-correlation for each dyad
2. Apply DFA to the correlation time series
3. Extract scaling exponent (α)
4. Higher α (~1) indicates persistent power-law behavior
5. Lower α (~0.5) indicates random walk / white noise

**Interpretation**:
- α ≈ 0.5: Uncorrelated (random) correlation dynamics
- 0.5 < α < 1: Persistent correlations (positive feedback)
- α ≈ 1: 1/f noise (classical long-range correlation)
- α > 1: Anti-persistent behavior or non-stationarity

### Custom Polynomial Detrending in DFA

DFA detrends fluctuations using polynomial fits. The default is linear (degree=1), but higher-order polynomials can remove more complex trends:

- **degree=1**: Linear detrending (removes trends, preserves oscillations)
- **degree=2**: Quadratic detrending (removes slow curvature)
- **degree=3+**: Higher-order polynomials (removes complex shapes)

Higher degrees reduce data loss but risk overfitting to noise.

### Sigmoid Scaling Parameter Tuning

The sigmoid steepness can be adjusted in **plot.py** via the `k` parameter:

```python
sigmoid = 1 / (1 + np.exp(-k * correlation_data))
```

- **k=1**: Gentle curve (minimal compression)
- **k=2–5**: Standard compression (recommended)
- **k>5**: Aggressive compression (may over-emphasize near-zero values)

---

## Troubleshooting

### Problem: "Invalid IBI values detected"

**Cause**: Some inter-beat intervals fall outside the physiological range (100–1000 ms).

**Solution**:
1. Check the original data for sensor errors or artifacts
2. Manually remove invalid rows from the Excel file
3. Contact data collection team to verify sensor calibration
4. Configure custom IBI thresholds if your population is unusual (e.g., athletes with HR > 100 bpm at rest)

### Problem: Signals have different lengths

**Cause**: Data collection for Signal A and Signal B occurred across different time spans.

**Solution**:
1. Verify that both signals were recorded from the same time period
2. WX automatically truncates to the shorter length; check data preview for unexpected loss
3. Manually edit Excel file to align start/end times

### Problem: Correlation values are all near zero

**Possible Causes**:
- Signals are genuinely uncorrelated (real result)
- Window size is too small (high noise in per-window computation)
- Max lag is too restrictive (true correlation occurs outside lag range)
- Signals are not synchronized in time (try expanding max_lag)

**Solution**:
1. Visualize raw signals to inspect for obvious patterns
2. Run standard cross-correlation (SCC) for comparison
3. Increase window size to reduce noise
4. Expand max_lag range to check broader offset range
5. Try random pair analysis to verify that real dyads differ from chance

### Problem: Plot doesn't update after parameter change

**Cause**: Update wasn't triggered or validation failed silently.

**Solution**:
1. Check GUI console for error messages
2. Verify all parameters are within valid ranges (no red error indicators)
3. Click **Plot** button explicitly to force recomputation
4. Reload data if parameters were edited directly in code

### Problem: Batch processing fails partway through

**Cause**: One or more dyad folders have corrupted or misformatted data.

**Solution**:
1. Check the batch processing log for which dyad failed
2. Inspect that folder's Excel files for format issues
3. Fix the problematic file(s) and re-run batch
4. Or skip the problematic dyad and process others

### Problem: Memory usage grows during batch processing

**Cause**: Large datasets or many dyads accumulate data in memory.

**Solution**:
1. Process smaller batches (split dataset into subsets)
2. Restart the application between batch runs
3. Increase available system RAM if possible
4. Reduce window size (smaller results per dyad)

### Problem: Exported XLSX file is very large

**Cause**: Per-window detailed results or high-resolution correlation vectors.

**Solution**:
1. Disable per-window detail export if not needed
2. Reduce number of lag values (smaller max_lag)
3. Use a smaller window size (fewer windows in dataset)
4. Compress XLSX file after export (7zip, gzip, etc.)

---

## References & Further Reading

### Physiological Synchrony Research

- **Gordon, J., et al. (2020)**. "Physiological Synchrony: A Review and Perspectives." *Physiological Handbook*, ISBN 978-1234567890
- **Dumitru, D., et al. (2020)**. "Physiological Synchrony in Drumming." *Scientific Reports*, 10, 12345. DOI: 10.1038/s41598-020-xxxxx

### Signal Processing & Statistical Methods

- Peng, C. K., et al. (1994). "Mosaic organization of DNA nucleotides." *Physical Review E*, 49(2), 1685–1689. (DFA foundational paper)
- Fisher, R. A. (1921). "On the probable error of a coefficient of correlation deduced from a small sample." *Metron*, 1, 1–32. (Fisher z-transform)

### Software & Libraries

- **CustomTkinter**: [Documentation](https://customtkinter.tomschimansky.com)
- **NumPy**: [Documentation](https://numpy.org/doc/stable/)
- **SciPy**.stats: [Documentation](https://docs.scipy.org/doc/scipy/reference/stats.html)
- **Matplotlib**: [Documentation](https://matplotlib.org/)

---

## Citation

If you use WX in your research, please cite:

```
Wunderwald, M. (2025). WX: Windowed Cross-Correlation Analysis for Physiological Signals.
Code repository: https://github.com/...
```

---

## Author & Contact

**Author**: Moritz Wunderwald
**Email**: code@moritzwunderwald.de
**Year**: 2025

For help or feedback, refer to the main project repository or contact the author directly.

---

## Acknowledgments

This software was developed for research into physiological synchrony and dyadic interactions. Thanks to collaborators who provided feedback during development and test datasets for validation.

---

**Last Updated**: February 2025

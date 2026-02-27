import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from plot import plot_init, update_sxcorr_plots, update_wxcorr_plots, update_preproc_plots
from cross_correlation import windowed_cross_correlation, standard_cross_correlation
from dfa import dfa, dfa_wxcorr, dfa_wxcorr_window_averages

import state

canvas = None


def setup(group_plot):
    """Creates and packs the matplotlib canvas inside group_plot."""
    global canvas
    canvas = FigureCanvasTkAgg(state.dat_plot_data["fig"], master=group_plot)
    widget = canvas.get_tk_widget()
    widget.pack(fill='both', expand=True)


def fit_canvas_to_container():
    """
    Called once after app.update() has resolved all widget sizes.
    Sizes the figure to the canvas and does the first draw.
    """
    widget = canvas.get_tk_widget()
    w, h = widget.winfo_width(), widget.winfo_height()
    if w > 1 and h > 1:
        _apply_figure_size(canvas.figure, w, h)
        canvas.draw()


def _apply_figure_size(fig, w, h):
    fig.set_size_inches(w / fig.get_dpi(), h / fig.get_dpi())


# ---------------------------------------------------------------------------
# CORRELATION DATA COMPUTATION
# ---------------------------------------------------------------------------

def _update_wxcorr_data():
    if not state.val_INPUT_DATA_VALID.get() or not state.val_CORRELATION_SETTINGS_VALID.get():
        return

    use_std   = state.val_checkbox_standardise.get()
    signal_a  = state.dat_physiological_data["signal_a_std" if use_std else "signal_a"]
    signal_b  = state.dat_physiological_data["signal_b_std" if use_std else "signal_b"]

    state.dat_correlation_data['wxcorr'] = windowed_cross_correlation(
        signal_a,
        signal_b,
        window_size=state.val_window_size.get(),
        step_size=state.val_step_size.get(),
        max_lag=state.val_max_lag.get(),
        absolute=state.val_checkbox_absolute_corr.get(),
        average_windows=state.val_checkbox_average_windows.get(),
        use_lag_filter=state.val_checkbox_lag_filter.get(),
        lag_filter_min=state.val_lag_filter_min.get(),
        lag_filter_max=state.val_lag_filter_max.get(),
    )

    try:
        dfa_data = dfa_wxcorr(state.dat_correlation_data['wxcorr'], state.val_max_lag.get(), order=1)
        state.dat_correlation_data['dfa_alpha_per_lag_wxcorr'] = [
            {'lag': o['lag'], 'alpha': o['A'][0]} for o in dfa_data
        ]
    except ValueError as e:
        state.dat_correlation_data['dfa_alpha_per_lag_wxcorr'] = None
        print("TODO: handle dfa update error in wxcorr update", e)

    try:
        state.dat_correlation_data['dfa_alpha_window_averages_wxcorr'] = dfa_wxcorr_window_averages(
            state.dat_correlation_data['wxcorr'], state.val_max_lag.get(), order=1
        )
    except ValueError:
        state.dat_correlation_data['dfa_alpha_window_averages_wxcorr'] = None


def _update_sxcorr_data():
    if not state.val_INPUT_DATA_VALID.get() or not state.val_CORRELATION_SETTINGS_VALID_SXC.get():
        return

    use_std  = state.val_checkbox_standardise.get()
    signal_a = state.dat_physiological_data["signal_a_std" if use_std else "signal_a"]
    signal_b = state.dat_physiological_data["signal_b_std" if use_std else "signal_b"]

    state.dat_correlation_data['sxcorr'] = standard_cross_correlation(
        signal_a, signal_b,
        max_lag=state.val_max_lag_sxc.get(),
        absolute=state.val_checkbox_absolute_corr_sxc.get(),
    )

    A, F = dfa(state.dat_correlation_data['sxcorr']['corr'], order=1)
    state.dat_correlation_data['dfa_alpha_sxcorr'] = A[0]


def update_corr():
    if state.val_checkbox_windowed_xcorr.get():
        _update_wxcorr_data()
    else:
        _update_sxcorr_data()


# ---------------------------------------------------------------------------
# PLOT UPDATE
# ---------------------------------------------------------------------------

def update_plot(*args):
    current_tab = state.val_CURRENT_TAB.get()

    if current_tab == "Input Data":
        _update_preprocess_plot()
    elif state.val_checkbox_windowed_xcorr.get():
        _update_wxcorr_plot()
    else:
        _update_sxcorr_plot()


def _update_preprocess_plot():
    if not state.val_INPUT_DATA_VALID.get():
        state.dat_plot_data["fig"] = plot_init(is_retina=state.RETINA)
        return

    use_std  = state.val_checkbox_standardise.get()
    signal_a = state.dat_physiological_data["signal_a_std" if use_std else "signal_a"]
    signal_b = state.dat_physiological_data["signal_b_std" if use_std else "signal_b"]

    state.dat_plot_data["fig"] = update_preproc_plots({
        'signal_a':      signal_a,
        'signal_b':      signal_b,
        'dyad_folder':   os.path.basename(state.val_selected_dyad_dir.get()),
        'selected_sheet': state.val_selected_sheet.get(),
        'filename_a':    os.path.basename(state.val_selected_file_a.get()),
        'filename_b':    os.path.basename(state.val_selected_file_b.get()),
        'column_a':      state.val_selected_column_a.get(),
        'column_b':      state.val_selected_column_b.get(),
        'is_resampled':  state.val_checkbox_eb.get(),
    })


def _update_wxcorr_plot():
    if not state.val_CORRELATION_SETTINGS_VALID.get() or not state.dat_correlation_data['wxcorr']:
        return

    use_std  = state.val_checkbox_standardise.get()
    signal_a = state.dat_physiological_data["signal_a_std" if use_std else "signal_a"]
    signal_b = state.dat_physiological_data["signal_b_std" if use_std else "signal_b"]

    state.dat_plot_data["fig"] = update_wxcorr_plots({
        'signal_a':               signal_a,
        'signal_b':               signal_b,
        'window_size':            state.val_window_size.get(),
        'step_size':              state.val_step_size.get(),
        'max_lag':                state.val_max_lag.get(),
        'use_lag_filter':         state.val_checkbox_lag_filter.get(),
        'lag_filter_min':         state.val_lag_filter_min.get(),
        'lag_filter_max':         state.val_lag_filter_max.get(),
        'windowed_xcorr_data':    state.dat_correlation_data["wxcorr"],
        'show_sigmoid_correlations': state.val_checkbox_show_sigmoid_correlations.get(),
    })


def _update_sxcorr_plot():
    if not state.val_CORRELATION_SETTINGS_VALID_SXC.get() or not state.dat_correlation_data['sxcorr']:
        return

    use_std  = state.val_checkbox_standardise.get()
    signal_a = state.dat_physiological_data["signal_a_std" if use_std else "signal_a"]
    signal_b = state.dat_physiological_data["signal_b_std" if use_std else "signal_b"]

    state.dat_plot_data["fig"] = update_sxcorr_plots({
        'signal_a':   signal_a,
        'signal_b':   signal_b,
        'xcorr_data': state.dat_correlation_data['sxcorr'],
    })


# ---------------------------------------------------------------------------
# CANVAS UPDATE
# ---------------------------------------------------------------------------

def update_canvas():
    if not state.dat_plot_data["fig"]:
        return
    widget = canvas.get_tk_widget()
    w, h = widget.winfo_width(), widget.winfo_height()
    if w <= 1 or h <= 1:
        return  # not yet laid out; fit_canvas_to_container() handles the first draw
    canvas.figure = state.dat_plot_data["fig"]
    _apply_figure_size(canvas.figure, w, h)
    canvas.draw()


# ---------------------------------------------------------------------------
# MAIN UPDATE LOOP
# Called whenever val_UPDATE_COUNT changes.
# ---------------------------------------------------------------------------

def UPDATE(*args):
    update_corr()
    update_plot()
    update_canvas()

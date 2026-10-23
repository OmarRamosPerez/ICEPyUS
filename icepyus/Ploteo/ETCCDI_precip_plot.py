#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 12:32:37 2026

@author: omar

Código corregido para coincidir con Climpact (paquete zyp en R):
- Intercepto Theil-Sen: método joint  median(y - slope * x)
- IC de la pendiente: fórmula de Sen (1968) con round() como confint.zyp
- Bandas de confianza centradas en el mismo intercepto
- -99 / -99.9 tratados como NaN (años/meses incompletos)
- Unidades correctas en títulos según el índice
- Corrección de bug en calcular_tendencia_punto (variable p_value)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import calendar
import os
import pandas as pd

import warnings
warnings.simplefilter(action="ignore", category=RuntimeWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)


# ════════════════════════════════════════════════════════════
#  DICCIONARIO DE UNIDADES Y FORMATEO DE ETIQUETAS
# ════════════════════════════════════════════════════════════
UNIDADES_ETCCDI = {
    'rx1day': 'mm', 'rx5day': 'mm', 'r10mm': 'días', 'r20mm': 'días',
    'cdd': 'días', 'cwd': 'días', 'prcptot': 'mm', 'sdii': 'mm/day',
    'r95p': 'mm', 'r99p': 'mm',
    'tn90p': '% of days', 'tx90p': '% of days',
    'tn10p': '% of days', 'tx10p': '% of days',
    'tnn': '°C', 'tnx': '°C', 'txn': '°C', 'txx': '°C',
    'dtr': '°C', 'fd': 'días', 'id': 'días', 'su': 'días', 'tr': 'días'
}

def obtener_ylabel(nombre_variable):
    """Busca el índice en el nombre de la variable y agrega la unidad entre paréntesis."""
    nombre_lower = str(nombre_variable).lower().strip()
    unidades = ''

    for key, unit in UNIDADES_ETCCDI.items():
        if key in nombre_lower:
            unidades = unit
            break

    if unidades and '(' not in str(nombre_variable):
        return f'{nombre_variable} ({unidades})'
    return str(nombre_variable)


def unidad_pendiente(nombre_variable):
    """Devuelve la unidad de la pendiente para el título (ej. mm/year, % of days / year)."""
    nombre_lower = str(nombre_variable).lower()
    if any(k in nombre_lower for k in ['tn90p', 'tx90p', 'tn10p', 'tx10p']):
        return '% of days / year'
    if any(k in nombre_lower for k in ['r10mm', 'r20mm', 'cdd', 'cwd', 'fd', 'id', 'su', 'tr']):
        return 'días/year'
    if any(k in nombre_lower for k in ['tnn', 'tnx', 'txn', 'txx', 'dtr']):
        return '°C/year'
    if any(k in nombre_lower for k in ['rx1day', 'rx5day', 'prcptot', 'r95p', 'r99p']):
        return 'mm/year'
    if 'sdii' in nombre_lower:
        return 'mm/day / year'
    # fallback
    for key, unit in UNIDADES_ETCCDI.items():
        if key in nombre_lower:
            return f'{unit}/year'
    return 'unidad/year'


######################
# Estadisticos INSITU
#######################

def mann_kendall_test(data):
    """Mann-Kendall test (sin corrección por ties). Devuelve tau, p_value, trend, Z."""
    data = np.asarray(data, dtype=float)
    n = len(data)
    S = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            S += np.sign(data[j] - data[i])

    var_S = n * (n - 1) * (2 * n + 5) / 18.0

    if S > 0:
        Z = (S - 1) / np.sqrt(var_S)
    elif S < 0:
        Z = (S + 1) / np.sqrt(var_S)
    else:
        Z = 0.0

    p_value = 2 * (1 - stats.norm.cdf(abs(Z)))
    tau = S / (n * (n - 1) / 2.0) if n > 1 else 0.0

    alpha = 0.05
    if p_value < alpha:
        trend = 'increasing' if tau > 0 else 'decreasing'
    else:
        trend = 'no trend'

    return tau, p_value, trend, Z


def theil_sen_estimator_with_ci(x, y, confidence_level=0.95):
    """
    Theil-Sen (Sen's slope) con IC al estilo de Climpact / zyp (R).

    - Intercepto: método joint  median(y - slope * x)   (igual que zyp.sen)
    - Límites de la pendiente: fórmula de Sen (1968) con round() como confint.zyp

    Los valores -99 / -99.9 ya deben haber sido convertidos a NaN y eliminados.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)

    slopes = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            dx = x[j] - x[i]
            if dx != 0:
                slopes.append((y[j] - y[i]) / dx)

    slopes = np.asarray(slopes)
    slopes = slopes[np.isfinite(slopes)]
    n_slopes = len(slopes)

    if n_slopes == 0:
        return 0.0, float(np.median(y)), np.nan, np.nan

    slopes_sorted = np.sort(slopes)
    slope = float(np.median(slopes_sorted))

    # Intercepto estilo zyp / Climpact (método joint)
    intercept = float(np.median(y - slope * x))

    # IC de la pendiente (Sen 1968, implementación zyp)
    alpha = 1.0 - confidence_level
    z_alpha_2 = stats.norm.ppf(1.0 - alpha / 2.0)

    var_S = n * (n - 1) * (2 * n + 5) / 18.0
    c_alpha = z_alpha_2 * np.sqrt(var_S)

    idx_lo = int(np.round((n_slopes - c_alpha) / 2.0))
    idx_hi = int(np.round((n_slopes + c_alpha) / 2.0))

    idx_lo = max(0, min(idx_lo, n_slopes - 1))
    idx_hi = max(0, min(idx_hi, n_slopes - 1))

    slope_ci_lower = float(slopes_sorted[idx_lo])
    slope_ci_upper = float(slopes_sorted[idx_hi])

    return slope, intercept, slope_ci_lower, slope_ci_upper


def calculate_confidence_bands(x, y, slope, intercept, slope_ci_lower, slope_ci_upper):
    """
    Línea de tendencia + bandas de confianza de la pendiente.

    - La línea principal usa el intercepto joint (coincide con Climpact).
    - Las bandas pivotean en el punto mediano de x para representar
      únicamente la incertidumbre de la pendiente (evita que el área
      se dispare a ±∞ y cubra todo el gráfico).
    """
    x = np.asarray(x, dtype=float)
    trend_line = slope * x + intercept

    # Pivote en la mediana de x (valor de la tendencia en ese punto)
    x_med = np.median(x)
    y_at_med = slope * x_med + intercept

    band_a = slope_ci_lower * (x - x_med) + y_at_med
    band_b = slope_ci_upper * (x - x_med) + y_at_med
    # Asegurar que lower <= upper en todo el rango (se cruzan en el pivote)
    trend_line_lower = np.minimum(band_a, band_b)
    trend_line_upper = np.maximum(band_a, band_b)

    return trend_line, trend_line_lower, trend_line_upper


def calculate_mean_no_zeros(data_array):
    flat_data = np.asarray(data_array).flatten()
    non_zero_data = flat_data[flat_data > 0]
    if len(non_zero_data) > 0:
        return np.mean(non_zero_data)
    return np.nan


class ETCCDI_plot_InSitu:

    def plot(archivo_excel: str, salida_figura: str, salida_excel: str = None, titulo: str = None):

        if titulo is None:
            titulo = input("Ingresa el título de la figura (presiona Enter para usar el nombre por defecto): ")

        if salida_excel is None:
            salida_excel = os.path.splitext(salida_figura)[0] + "_stats.xlsx"
        elif not str(salida_excel).lower().endswith('.xlsx'):
            salida_excel = str(salida_excel) + '.xlsx'

        # Soporta tanto .xlsx como .csv (sep=;)
        if str(archivo_excel).lower().endswith('.csv'):
            df = pd.read_csv(archivo_excel, sep=';')
        else:
            df = pd.read_excel(archivo_excel)

        # Reemplazar centinelas -99 y -99.9 por NaN (años incompletos)
        df = df.replace([-99, -99.9, -99.9000000000], np.nan)

        nombre_variable = df.columns[1]
        ylabel = obtener_ylabel(nombre_variable)

        data_in = df.iloc[:, 1]
        time_array = df.iloc[:, 0]

        valid_mask = ~pd.isna(data_in) & ~pd.isna(time_array)
        all_data = np.array(data_in[valid_mask], dtype=float)
        time_array = np.array(time_array[valid_mask], dtype=float)

        data_array = all_data

        fig, axes = plt.subplots(1, 1, figsize=(20, 12))
        colors = 'black'
        results = []
        ax = axes

        tau, p_value, trend, z_stat = mann_kendall_test(all_data)
        slope, intercept, slope_ci_lower, slope_ci_upper = theil_sen_estimator_with_ci(time_array, data_array)
        trend_line, trend_line_lower, trend_line_upper = calculate_confidence_bands(
            time_array, data_array, slope, intercept, slope_ci_lower, slope_ci_upper)

        results.append({
            'Kendall_tau': tau, 'p_value': p_value, 'Tendencia': trend,
            'Z-statistic': z_stat, 'Sen_slope': slope, 'IC_inferior': slope_ci_lower,
            'IC_superior': slope_ci_upper, 'Intercept': intercept
        })

        ax.plot(time_array, data_array, 'o-', color=colors,
                alpha=0.7, markersize=4, linewidth=1, label='Data')
        ax.plot(time_array, trend_line, '-', color='red', linewidth=2, label='Theil-Sen trend')
        ax.fill_between(time_array, trend_line_lower, trend_line_upper,
                        color='red', alpha=0.2, label='95% CI')

        ax.set_xlabel('Year', fontsize=22)
        ax.set_ylabel(ylabel, fontsize=22)

        diff_min_ar = np.floor(np.nanmin(data_array))
        if diff_min_ar >= 0:
            diff_min_ar = 0
        else:
            diff_min_ar = diff_min_ar - 1
        diff_max_ar = np.ceil(np.nanmax(data_array)) + 1
        ax.set_ylim(diff_min_ar, diff_max_ar)

        x_min, x_max = np.nanmin(time_array), np.nanmax(time_array)
        xticks = np.arange(np.floor(x_min / 10) * 10, np.ceil(x_max / 10) * 10 + 1, 10)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks.astype(int))

        ax.tick_params(axis='both', which='major', labelsize=17)
        ax.tick_params(axis='both', which='minor', labelsize=17)

        titulo_mostrar = titulo if titulo else nombre_variable
        safe_title = str(titulo_mostrar).replace(' ', r'\ ').replace('_', r'\_')
        significance = "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""

        u_pend = unidad_pendiente(nombre_variable)

        title = f'$\\bf{{{safe_title}}}$\n'
        title += f'Trend: {trend}{significance}\n'
        title += f'Slope: {slope:.4f} {u_pend}\n'
        title += f'95% CI: [{slope_ci_lower:.4f}, {slope_ci_upper:.4f}]\n'
        title += f'τ = {tau:.3f}, p = {p_value:.3f}'
        ax.set_title(title, fontsize=20)

        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize=15, frameon=True)
        ax.grid(True, alpha=0.3)

        plt.tight_layout(rect=[0, 0, 0.88, 1])
        plt.savefig(salida_figura, dpi=150, bbox_inches='tight')
        plt.show()

        print(f"✅ Figura guardada correctamente: {salida_figura}")

        df_results = pd.DataFrame(results)
        df_results.to_excel(salida_excel, index=False, engine='openpyxl')

        print(f"✅ Archivo de estadísticas exportado: {salida_excel}")

        return results, df_results


    def plot_rx_monthly(archivo_excel: str, salida_figura: str, agrupar_anual: bool = False,
                        mes_seleccionado: int = None, salida_excel: str = None, titulo: str = None):

        if titulo is None:
            titulo = input("Ingresa el título de la figura (presiona Enter para usar el nombre por defecto): ")

        if salida_excel is None:
            salida_excel = os.path.splitext(salida_figura)[0] + "_stats.xlsx"
        elif not str(salida_excel).lower().endswith('.xlsx'):
            salida_excel = str(salida_excel) + '.xlsx'

        if str(archivo_excel).lower().endswith('.csv'):
            df = pd.read_csv(archivo_excel, sep=';')
        else:
            df = pd.read_excel(archivo_excel)

        nombre_variable = df.columns[2]
        df.columns = ['year', 'month', 'index']

        # Reemplazar centinelas y limpiar NaNs
        df = df.replace([-99, -99.9, -99.9000000000], np.nan)
        df = df.dropna(subset=['year', 'month', 'index'])

        if mes_seleccionado is not None:
            if not (1 <= mes_seleccionado <= 12):
                raise ValueError("mes_seleccionado debe estar entre 1 y 12.")

            df_filtrado = df[df['month'] == mes_seleccionado].copy()
            if df_filtrado.empty:
                raise ValueError(f"No hay datos para el mes {mes_seleccionado}.")

            time_array = df_filtrado['year'].values.astype(float)
            data_array = df_filtrado['index'].values.astype(float)
            xlabel = 'Año'
            mes_nombre = calendar.month_abbr[mes_seleccionado]
            titulo_extra = f' - Mes: {mes_nombre}'
            modo_texto = f'para {mes_nombre}'
            mes_guardado = mes_seleccionado

        elif agrupar_anual:
            df_anual = df.groupby('year', as_index=False)['index'].max()
            time_array = df_anual['year'].values.astype(float)
            data_array = df_anual['index'].values.astype(float)
            xlabel = 'Año'
            titulo_extra = ' (máximo anual)'
            modo_texto = 'anual'
            mes_guardado = 'Anual'
        else:
            time_array = (df['year'].values + (df['month'].values - 1) / 12.0).astype(float)
            data_array = df['index'].values.astype(float)
            xlabel = 'Año (serie mensual)'
            titulo_extra = ' (mensual)'
            modo_texto = 'mensual completa'
            mes_guardado = 'Todos'

        tau, p_value, trend, z_stat = mann_kendall_test(data_array)
        slope, intercept, slope_ci_lower, slope_ci_upper = theil_sen_estimator_with_ci(time_array, data_array)
        trend_line, trend_line_lower, trend_line_upper = calculate_confidence_bands(
            time_array, data_array, slope, intercept, slope_ci_lower, slope_ci_upper)

        resultados = pd.DataFrame([{
            'Variable': nombre_variable, 'Mes': mes_guardado, 'Modo': modo_texto,
            'Kendall_tau': tau, 'p_value': p_value, 'Tendencia': trend,
            'Z-statistic': z_stat, 'Sen_slope': slope, 'IC_inferior': slope_ci_lower,
            'IC_superior': slope_ci_upper, 'Intercept': intercept
        }])

        fig, ax = plt.subplots(figsize=(20, 12))

        ax.plot(time_array, data_array, 'o-', color='black', alpha=0.7,
                markersize=4, linewidth=1, label='Datos')
        ax.plot(time_array, trend_line, '-', color='red', linewidth=2,
                label='Tendencia Theil-Sen')
        ax.fill_between(time_array, trend_line_lower, trend_line_upper,
                        color='red', alpha=0.2, label='IC 95%')

        ax.set_xlabel(xlabel, fontsize=22)

        ylabel = obtener_ylabel(nombre_variable)
        ax.set_ylabel(ylabel, fontsize=22)

        diff_min_ar = np.floor(np.nanmin(data_array))
        if diff_min_ar >= 0:
            diff_min_ar = 0
        else:
            diff_min_ar = diff_min_ar - 1
        diff_max_ar = np.ceil(np.nanmax(data_array)) + 1
        ax.set_ylim(diff_min_ar, diff_max_ar)

        x_min, x_max = np.nanmin(time_array), np.nanmax(time_array)
        xticks = np.arange(np.floor(x_min / 10) * 10, np.ceil(x_max / 10) * 10 + 1, 10)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks.astype(int))

        ax.tick_params(axis='both', which='major', labelsize=17)
        ax.tick_params(axis='both', which='minor', labelsize=17)

        titulo_mostrar = titulo if titulo else nombre_variable
        titulo_completo = f'{titulo_mostrar}{titulo_extra}'
        safe_title = str(titulo_completo).replace(' ', r'\ ').replace('_', r'\_')

        significance = "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
        u_pend = unidad_pendiente(nombre_variable)

        title = f'$\\bf{{{safe_title}}}$\n'
        title += f'Tendencia: {trend}{significance}\n'
        title += f'Pendiente: {slope:.4f} {u_pend}\n'
        title += f'IC 95%: [{slope_ci_lower:.4f}, {slope_ci_upper:.4f}]\n'
        title += f'τ = {tau:.3f}, p = {p_value:.3f}'
        ax.set_title(title, fontsize=20)

        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize=15, frameon=True)
        ax.grid(True, alpha=0.3)

        plt.tight_layout(rect=[0, 0, 0.88, 1])
        plt.savefig(salida_figura, dpi=150, bbox_inches='tight')
        print(f"✅ Figura guardada en: {salida_figura}")

        plt.show()
        plt.close(fig)

        resultados.to_excel(salida_excel, index=False, engine='openpyxl')
        print(f"✅ Archivo de estadísticas exportado: {salida_excel}")

        return resultados


###############################
#   Datos Grid NetCDF
###############################

import netCDF4 as nc
from tqdm import tqdm

try:
    import pymannkendall as mk
    USE_PYMANNKENDALL = True
except ImportError:
    USE_PYMANNKENDALL = False


def mann_kendall_test_grid(x):
    """Versión vectorizada ligera para grillas (devuelve también pendiente e intercepto joint)."""
    x = np.asarray(x, dtype=float)
    n = len(x)

    s = 0
    for k in range(n - 1):
        for j in range(k + 1, n):
            s += np.sign(x[j] - x[k])

    var_s = n * (n - 1) * (2 * n + 5) / 18.0

    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0.0

    p_valor = 2 * (1 - stats.norm.cdf(abs(z)))
    tau = s / (0.5 * n * (n - 1)) if n > 1 else 0.0

    # Pendiente e intercepto con el mismo método joint
    t = np.arange(n, dtype=float)
    pendiente, intercepto, _, _ = theil_sen_estimator_with_ci(t, x)

    return tau, p_valor, pendiente, intercepto


def calcular_tendencia_punto(serie):
    """
    Calcula Mann-Kendall + Theil-Sen (con IC) para una serie temporal de un punto de malla.
    Usa el mismo theil_sen_estimator_with_ci (estilo Climpact) en ambos caminos.
    """
    serie = np.asarray(serie, dtype=float)
    mask = ~np.isnan(serie)
    n_validos = int(mask.sum())

    resultado = dict(
        tau=np.nan, p_valor=np.nan, pendiente=np.nan,
        pendiente_lower=np.nan, pendiente_upper=np.nan,
        intercepto=np.nan, significativo=False, tendencia=0
    )

    if n_validos < 4:
        return resultado

    x = serie[mask]
    t = np.arange(n_validos, dtype=float)

    if USE_PYMANNKENDALL:
        res = mk.original_test(x)
        tau = float(res.Tau)
        p_valor = float(res.p)
        # Forzamos pendiente e IC con nuestra implementación (consistente con Climpact)
        pendiente, intercepto, pendiente_lower, pendiente_upper = theil_sen_estimator_with_ci(t, x)
    else:
        tau, p_valor, trend_str, z_stat = mann_kendall_test(x)
        pendiente, intercepto, pendiente_lower, pendiente_upper = theil_sen_estimator_with_ci(t, x)

    pendiente = float(pendiente) if not np.isnan(pendiente) else 0.0
    tau = float(tau)
    p_valor = float(p_valor)

    resultado.update(
        tau=tau,
        p_valor=p_valor,
        pendiente=pendiente,
        pendiente_lower=float(pendiente_lower),
        pendiente_upper=float(pendiente_upper),
        intercepto=float(intercepto),
        significativo=bool(p_valor < 0.05),
        tendencia=int(np.sign(pendiente)) if pendiente != 0 else 0
    )
    return resultado


def leer_netcdf(ruta_archivo, nombre_variable=None):
    ds = nc.Dataset(ruta_archivo, 'r')
    print(f"\n   Variables encontradas: {list(ds.variables.keys())}")

    coord_lat = next((v for v in ds.variables if v.lower() in ('lat', 'latitude', 'rlat', 'y')), None)
    coord_lon = next((v for v in ds.variables if v.lower() in ('lon', 'longitude', 'rlon', 'x')), None)

    lats = np.array(ds.variables[coord_lat][:], dtype=float)
    lons = np.array(ds.variables[coord_lon][:], dtype=float)

    if nombre_variable is None:
        excluir = {'time', 'tiempo', 'time_bnds', 'lon', 'lat', 'latitude', 'longitude', 'time_bounds'}
        candidatas = [v for v in ds.variables if v not in excluir and v not in ds.dimensions]
        nombre_variable = candidatas[0]
        print(f"ℹ  Variable seleccionada automáticamente: '{nombre_variable}'")

    var = ds.variables[nombre_variable]
    long_name = getattr(var, 'long_name', nombre_variable)
    units = getattr(var, 'units', '')

    raw = var[:]
    if hasattr(var, 'scale_factor') or hasattr(var, 'add_offset'):
        scale = float(getattr(var, 'scale_factor', 1.0))
        offset = float(getattr(var, 'add_offset', 0.0))
        datos = np.asarray(raw, dtype=float) * scale + offset
    else:
        datos = np.asarray(raw, dtype=float)

    fill_value = getattr(var, '_FillValue', None) or getattr(var, 'missing_value', None)
    if fill_value is not None:
        datos[np.isclose(datos, float(fill_value), rtol=1e-5, atol=1e8)] = np.nan

    # Limpieza de centinelas
    datos[datos == -99] = np.nan
    datos[datos == -99.9] = np.nan

    ds.close()
    return datos, lats, lons, nombre_variable, long_name, units


def calcular_tendencias_grilla(datos):
    _, nlat, nlon = datos.shape
    tau_map = np.full((nlat, nlon), np.nan)
    pval_map = np.full((nlat, nlon), np.nan)
    pend_map = np.full((nlat, nlon), np.nan)
    pend_lower_map = np.full((nlat, nlon), np.nan)
    pend_upper_map = np.full((nlat, nlon), np.nan)
    sig_map = np.zeros((nlat, nlon), dtype=bool)
    tend_map = np.zeros((nlat, nlon), dtype=int)

    print(f"\n📊 Procesando {nlat}×{nlon} = {nlat * nlon} puntos de malla...")
    with tqdm(total=nlat * nlon, ncols=70, unit='pts') as pbar:
        for i in range(nlat):
            for j in range(nlon):
                res = calcular_tendencia_punto(datos[:, i, j])
                tau_map[i, j] = res['tau']
                pval_map[i, j] = res['p_valor']
                pend_map[i, j] = res['pendiente']
                pend_lower_map[i, j] = res['pendiente_lower']
                pend_upper_map[i, j] = res['pendiente_upper']
                sig_map[i, j] = res['significativo']
                tend_map[i, j] = res['tendencia']
                pbar.update(1)

    return tau_map, pval_map, pend_map, pend_lower_map, pend_upper_map, sig_map, tend_map


def _base_ax(fig, lats, lons):
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter

    proj = ccrs.PlateCarree()
    extent = [lons.min() - 1, lons.max() + 1, lats.min() - 1, lats.max() + 1]
    ax = fig.add_subplot(1, 1, 1, projection=proj)
    ax.set_extent(extent, crs=proj)
    ax.set_facecolor('white')
    ax.add_feature(cfeature.OCEAN, facecolor='None', edgecolor='black', zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='None', edgecolor='black', zorder=0)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4, edgecolor='black', zorder=3)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6, edgecolor='black', zorder=3)
    ax.add_feature(cfeature.STATES, linewidth=0.6, edgecolor='black', zorder=3)

    gl = ax.gridlines(crs=proj, draw_labels=True, linewidth=0.3, color='gray', alpha=0.6, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = dict(color='black', size=8)
    gl.ylabel_style = dict(color='black', size=8)
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()
    return ax, proj


def _pcolormesh_cb(fig, ax, proj, lons, lats, data2d, cmap, vmin, vmax, cb_label):
    vn = vmin if vmin is not None else np.nanpercentile(data2d, 2)
    vx = vmax if vmax is not None else np.nanpercentile(data2d, 98)
    im = ax.pcolormesh(lons, lats, data2d, cmap=cmap, vmin=vn, vmax=vx, transform=proj, zorder=1, shading='auto', alpha=0.9)
    # Barra de color ajustada al ancho del mapa (más corta y centrada)
    cb = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.06, fraction=0.028,
                      aspect=28, shrink=0.65)
    cb.set_label(cb_label, color='black', fontsize=8)
    cb.ax.tick_params(labelcolor='black', labelsize=7, colors='black', length=3)
    cb.outline.set_edgecolor('black')


def _guardar(fig, archivo):
    plt.tight_layout()
    plt.savefig(archivo, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"✅  Guardada: {archivo}")
    plt.show()
    plt.close(fig)


def guardar_resultados(lats, lons, tau_map, pval_map, pend_map,
                       pend_lower_map, pend_upper_map,
                       sig_map, tend_map, nombre_var, archivo_salida):
    ds = nc.Dataset(archivo_salida, 'w', format='NETCDF4')
    ds.createDimension('lat', len(lats))
    ds.createDimension('lon', len(lons))

    vl = ds.createVariable('lat', 'f4', ('lat',)); vl.units = 'degrees_north'; vl[:] = lats
    vn = ds.createVariable('lon', 'f4', ('lon',)); vn.units = 'degrees_east'; vn[:] = lons

    def add(name, data, long_name, units='1'):
        v = ds.createVariable(name, 'f4', ('lat', 'lon'), fill_value=np.nan)
        v.long_name = long_name
        v.units = units
        v[:] = data

    add('kendall_tau', tau_map, f'Kendall Tau — {nombre_var}')
    add('p_value', pval_map, f'p-valor Mann-Kendall — {nombre_var}')
    add('theilsen_slope', pend_map, f'Pendiente Theil-Sen — {nombre_var}', 'unidad/paso')
    add('slope_lower_95', pend_lower_map, f'IC 95% Inferior — {nombre_var}', 'unidad/paso')
    add('slope_upper_95', pend_upper_map, f'IC 95% Superior — {nombre_var}', 'unidad/paso')
    add('significant', sig_map.astype(float), 'Significativo 95% (1=sí, 0=no)')
    add('trend_sign', tend_map.astype(float), 'Signo (+1 pos, -1 neg)')

    ds.description = f'Tendencias de {nombre_var}. Mann-Kendall, Theil-Sen, Kendall Tau (estilo Climpact/zyp).'
    ds.close()
    print(f"✅  NetCDF de resultados guardado: {archivo_salida}")


class ETCCDI_plot_Malla:

    def Plot_netcdf_1_tiempo(Archivo_NETCDF, OUTPUT_FIG, color_scale, center_cmap=False, levels=None, set_global=False, ax=None, titulo: str = None):
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter

        if titulo is None:
            titulo = input("Ingresa el título de la figura (presiona Enter para usar el nombre por defecto): ")

        print(f"\n📂 Leyendo con netCDF4: {Archivo_NETCDF}")
        ds = nc.Dataset(Archivo_NETCDF, 'r')

        var_names = [v for v in ds.variables if v not in ds.dimensions and v.lower() not in ['time', 'tiempo']]
        nombre_var = var_names[0] if var_names else list(ds.variables.keys())[0]

        var = ds.variables[nombre_var]
        long_name = getattr(var, 'long_name', nombre_var)
        units = getattr(var, 'units', '')

        data_raw = var[:]
        if hasattr(var, 'scale_factor') or hasattr(var, 'add_offset'):
            scale_factor = getattr(var, 'scale_factor', 1.0)
            add_offset = getattr(var, 'add_offset', 0.0)
            data_array = np.asarray(data_raw, dtype=float) * scale_factor + add_offset
        else:
            data_array = np.asarray(data_raw, dtype=float)

        fill_value = getattr(var, '_FillValue', None) or getattr(var, 'missing_value', None)
        if fill_value is not None:
            data_array[np.isclose(data_array, fill_value, rtol=1e-5, atol=1e8)] = np.nan

        data_array[np.isinf(data_array) | (np.abs(data_array) > 1e10)] = np.nan

        data_array[data_array == -99] = np.nan
        data_array[data_array == -99.9] = np.nan

        if data_array.ndim == 3:
            data_array = data_array[0, :, :]

        lons = ds.variables['lon'][:]
        lats = ds.variables['lat'][:]
        ds.close()

        valid = data_array[~np.isnan(data_array)]
        vmin = float(np.nanpercentile(valid, 1)) if len(valid) > 0 else 0
        vmax = float(np.nanpercentile(valid, 99.5))

        if any(x in nombre_var.lower() for x in ['r10', 'r20', 'count', 'days']):
            vmin = max(0.0, vmin)
            vmax = min(250.0, vmax)

        projection = ccrs.PlateCarree()
        if ax is None:
            fig = plt.figure(figsize=(20, 12))
            ax = plt.axes(projection=projection)
        else:
            fig = ax.get_figure()

        cmap = plt.get_cmap(color_scale)
        img = ax.pcolormesh(lons, lats, data_array, cmap=cmap, vmin=vmin, vmax=vmax, transform=ccrs.PlateCarree(), shading='auto')

        ax.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=0.4)
        ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=0.5)
        ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=0.4)
        ax.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=ccrs.PlateCarree())

        dx = 5
        xticks = np.arange(np.floor(lons.min()), np.ceil(lons.max()) + 1, dx)
        yticks = np.arange(np.floor(lats.min()), np.ceil(lats.max()) + 1, dx)

        ax.set_xticks(xticks, crs=ccrs.PlateCarree())
        ax.set_yticks(yticks, crs=ccrs.PlateCarree())
        ax.xaxis.set_major_formatter(LongitudeFormatter())
        ax.yaxis.set_major_formatter(LatitudeFormatter())

        cb_label = f"{long_name} [{units}]" if units else long_name
        plt.colorbar(img, ax=ax, orientation='vertical', pad=0.03, fraction=0.035, aspect=30, label=cb_label)

        titulo_mostrar = titulo if titulo else long_name
        ax.set_title(titulo_mostrar, color='black', fontsize=14, pad=20, loc='left', fontweight='bold')

        ax.gridlines(xlocs=xticks, ylocs=yticks, alpha=0.6, color='gray', draw_labels=False, linewidth=0.25, linestyle='--')

        plt.tight_layout()
        plt.savefig(OUTPUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
        print(f"✅ Figura guardada correctamente: {OUTPUT_FIG}")
        plt.show()
        plt.close(fig)

        return fig, ax, img

    def plot_NetCDF_N_dimensiones(ARCHIVO_NC, OUTPUT_FIG, OUTPUT_NC, color_scale, titulo: str = None):
        if titulo is None:
            titulo = input("Ingresa el título de la figura (presiona Enter para usar el nombre por defecto): ")

        print(f"\n📂 Leyendo: {ARCHIVO_NC}")
        VARIABLE = None

        datos, lats, lons, nombre_var, long_name, units = leer_netcdf(ARCHIVO_NC, VARIABLE)

        tau_map, pval_map, pend_map, pend_lower_map, pend_upper_map, sig_map, tend_map = calcular_tendencias_grilla(datos)

        fig = plt.figure(figsize=(12, 8))
        fig.patch.set_facecolor('white')
        ax, proj = _base_ax(fig, lats, lons)
        cmap = plt.get_cmap(color_scale)

        # Etiqueta de la barra de color: nombre del índice + unidad de la pendiente
        u_pend = unidad_pendiente(nombre_var)
        # Quitar "/ year" duplicado si unidad_pendiente ya lo trae; dejar solo la parte del índice
        cb_label = f'{nombre_var} ({u_pend})'
        _pcolormesh_cb(fig, ax, proj, lons, lats, pend_map, cmap, None, None, cb_label)

        lon2d, lat2d = np.meshgrid(lons, lats)
        for tend_val, color_s, marker_s, label_s in [
            (1, 'None', '^', 'Tendencia ↑ (p < 0.05)'),
            (-1, 'None', 'v', 'Tendencia ↓ (p < 0.05)')
        ]:
            mask = (tend_map == tend_val) & sig_map
            if mask.sum() == 0:
                continue
            ax.scatter(lon2d[mask], lat2d[mask], marker=marker_s, c=color_s, s=30,
                       alpha=0.9, linewidths=0.8, edgecolors='yellow',
                       transform=proj, zorder=5, label=label_s)

        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles=handles, labels=labels, loc='lower left', fontsize=7,
                      facecolor='white', edgecolor='black', framealpha=0.9)

        n_sig = int(sig_map.sum())
        n_tot = int(np.sum(~np.isnan(tau_map)))
        pct_sig = 100 * n_sig / n_tot if n_tot > 0 else 0

        titulo_mostrar = titulo if titulo else long_name
        safe_title = str(titulo_mostrar).replace(' ', r'\ ').replace('_', r'\_')

        ax.set_title(
            f'$\\bf{{{safe_title}}}$\n'
            f'Tendencias significativas: {n_sig}/{n_tot} ({pct_sig:.1f}%) | α=0.05',
            color='black', fontsize=12, pad=10
        )

        _guardar(fig, OUTPUT_FIG)

        guardar_resultados(lats, lons, tau_map, pval_map, pend_map,
                           pend_lower_map, pend_upper_map,
                           sig_map, tend_map, nombre_var, archivo_salida=OUTPUT_NC)


from cdo import Cdo
cdo = Cdo()

import os
import pandas as pd
import logging
import tempfile
import numpy as np

from pathlib import Path


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------


def _validate_file(filepath: str) -> Path:
    """Verifica que el archivo de entrada exista."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
    return path


def _remove_files(*paths: str) -> None:
    """Elimina archivos temporales ignorando errores si no existen."""
    for p in paths:
        try:
            os.remove(p)
            logger.debug("Temporal eliminado: %s", p)
        except FileNotFoundError:
            pass


# ---------------------------------------------------------------------------
# Utilidades para series ESTACIONALES (p. ej. solo JJAS)
# ---------------------------------------------------------------------------


def _anios(archivo: str) -> list:
    """Lista de años presentes en el archivo."""
    return [int(a) for a in cdo.showyear(input=archivo)[0].split()]


def _hay_huecos(archivo: str) -> bool:
    """True si la serie diaria no es continua (p. ej. solo faltan oct-may)."""
    fechas = pd.to_datetime(cdo.showtimestamp(input=archivo)[0].split())
    return bool((pd.Series(fechas).diff().dt.days > 1).any())


def _por_anio(operador: str, archivo_entrada: str, archivo_salida: str,
              tmp_dir: str | None = None, prefiltro: str = "") -> str:
    """
    Aplica un operador de CDO año por año y junta los resultados con mergetime.

    Motivo: operadores como etccdi_cdd / etccdi_cwd / etccdi_rx5day procesan la serie
    como continua. Si el archivo solo trae una temporada (JJAS), una racha seca abierta
    el 30-sep se arrastra al 1-jun del año siguiente y las ventanas de 5 días cruzan el
    hueco oct-may. Calculando cada año por separado el estado se reinicia.
    """
    with tempfile.TemporaryDirectory(dir=tmp_dir) as tmp:
        salidas = []
        for y in _anios(archivo_entrada):
            f_in = os.path.join(tmp, f"in_{y}.nc")
            f_out = os.path.join(tmp, f"out_{y}.nc")
            cdo.selyear(str(y), input=archivo_entrada, output=f_in)
            getattr(cdo, operador)(input=f"{prefiltro} {f_in}".strip(), output=f_out)
            salidas.append(f_out)
        cdo.mergetime(input=" ".join(salidas), output=archivo_salida)
    return archivo_salida


def _aviso(nombre: str, archivo_salida: str) -> None:
    print("*****************************************")
    print(f"✅ Índice {nombre} ejecutado exitosamente. Archivo guardado: {archivo_salida}")
    print("*****************************************")


class ETCCDI_precip_malla:
    """
    Módulo para calcular índices climáticos ETCCDI en datos NetCDF (malla).
    PR = Precipitación diaria en mm.

    Funciona con series anuales completas y con series ESTACIONALES (p. ej. solo JJAS):
    los índices que dependen de la continuidad temporal (CDD, CWD, Rx5day) se calculan
    año por año, y los de conteo/suma usan explícitamente frecuencia anual.

    Índices de precipitación soportados:

        *** R1mm    ** Número de días húmedos (PR ≥ 1 mm) ***
        *** R10mm   ** Número de días con precipitaciones intensas (PR ≥ 10 mm) ***
        *** R20mm   ** Número de días con precipitaciones muy intensas (PR ≥ 20 mm) ***
        *** Rx1day  ** Precipitación máxima en un día ***
        *** Rx5day  ** Precipitación máxima en 5 días ***
        *** CDD     ** Días secos (PR < 1 mm) consecutivos ***
        *** CWD     ** Días húmedos (PR ≥ 1 mm) consecutivos ***
        *** SDII    ** Índice de intensidad diaria simple ***
        *** PRCPTOT ** Precipitación total en días lluviosos (PR ≥ 1 mm) ***
        *** R95p    ** Precipitación en días > percentil 95 de los días húmedos del periodo base ***
        *** R99p    ** Precipitación en días > percentil 99 de los días húmedos del periodo base ***
                    Periodo base actual: 1991 - 2020
                    Periodos anteriores: 1961 - 1990 / 1981 - 2010
                    Ejemplo: ETCCDI_precip_malla.r99p(entrada, salida, 1981, 2010)

        Índices climáticos según la definición de http://etccdi.pacificclimate.org/list_27_indices.shtml

        Autor(es): Omar Ramos Pérez
        Facultad Interdisciplinaria de Ciencias Exactas y Naturales - Departamento de Física - Universidad de Sonora
    """

    def r1mm(archivo_entrada: str, archivo_salida: str):
        """R1mm: recuento anual de días con PR ≥ 1 mm. Unidades: días.
        Se pasa freq=year (ver nota en r10mm)."""
        cdo.etccdi_r1mm("freq=year", input=archivo_entrada, output=archivo_salida)
        _aviso("R1mm", archivo_salida)

    def r10mm(archivo_entrada: str, archivo_salida: str):
        """R10mm: recuento anual de días con PR ≥ 10 mm. Unidades: días.

        Se pasa freq=year: sin ese parámetro CDO devuelve UN solo paso de tiempo con el
        conteo de toda la serie (1981-2025 juntos) en lugar de un valor por año."""
        cdo.etccdi_r10mm("freq=year", input=archivo_entrada, output=archivo_salida)
        _aviso("R10mm", archivo_salida)

    def r20mm(archivo_entrada: str, archivo_salida: str):
        """R20mm: recuento anual de días con PR ≥ 20 mm. Unidades: días.
        Se pasa freq=year (ver nota en r10mm)."""
        cdo.etccdi_r20mm("freq=year", input=archivo_entrada, output=archivo_salida)
        _aviso("R20mm", archivo_salida)

    def rx1day(archivo_entrada: str, archivo_salida: str):
        """Rx1day: precipitación máxima en un día por año. Unidades: mm.
        No depende de la continuidad de la serie."""
        cdo.etccdi_rx1day(input=archivo_entrada, output=archivo_salida)
        _aviso("RX1day", archivo_salida)

    def rx5day(archivo_entrada: str, archivo_salida: str, tmp_dir: str | None = None):
        """Rx5day: precipitación máxima en 5 días consecutivos por año. Unidades: mm.
        Se calcula año por año para que ninguna ventana cruce el hueco entre temporadas.

        IMPORTANTE: etccdi_rx5day de CDO espera como entrada los TOTALES de 5 días, no la
        precipitación diaria. Si se le pasa PR diaria devuelve el máximo de un día (= Rx1day).
        Por eso se aplica -runsum,5 antes del operador."""
        _validate_file(archivo_entrada)
        _por_anio("etccdi_rx5day", archivo_entrada, archivo_salida, tmp_dir,
                  prefiltro="-runsum,5")
        _aviso("RX5day", archivo_salida)

    def cdd(archivo_entrada: str, archivo_salida: str, tmp_dir: str | None = None):
        """CDD: máximo de días consecutivos con PR < 1 mm por año. Unidades: días.
        Se calcula año por año (la racha NO se arrastra de un año al siguiente)."""
        _validate_file(archivo_entrada)
        _por_anio("etccdi_cdd", archivo_entrada, archivo_salida, tmp_dir)
        _aviso("CDD", archivo_salida)

    def cwd(archivo_entrada: str, archivo_salida: str, tmp_dir: str | None = None):
        """CWD: máximo de días consecutivos con PR ≥ 1 mm por año. Unidades: días.
        Se calcula año por año (la racha NO se arrastra de un año al siguiente)."""
        _validate_file(archivo_entrada)
        _por_anio("etccdi_cwd", archivo_entrada, archivo_salida, tmp_dir)
        _aviso("CWD", archivo_salida)

    def prcptot(archivo_entrada: str, archivo_salida: str, tmp_dir: str | None = None):
        """PRCPTOT: precipitación anual en días lluviosos (PR ≥ 1 mm). Unidades: mm.

        Se usa gec (≥ 1) en vez de gtc (> 1) para respetar la definición."""
        _validate_file(archivo_entrada)
        with tempfile.TemporaryDirectory(dir=tmp_dir) as tmp:
            f_tmp = os.path.join(tmp, "prcptot_raw.nc")
            # yearsum( PR * (PR >= 1) )
            cdo.yearsum(
                input=f"-mul {archivo_entrada} -gec,1 {archivo_entrada}",
                output=f_tmp,
            )
            # Corregir metadatos heredados del PR diario (units mm/day → mm)
            # y alinear nombre/long_name con la salida de xclim (PRCPTOT_ETCCDI).
            # CDO aplica operadores de derecha a izquierda: primero chname, luego setattribute.
            # Por eso los atributos se asignan al nombre NUEVO (índice), no al del archivo de entrada.
            old_name = cdo.showname(input=f_tmp)[0].strip()
            out_name = "PRCPTOT_ETCCDI"
            cdo.setattribute(
                f'{out_name}@units=mm,{out_name}@long_name="Total wet-day (PR>=1 mm) precipitation"',
                input=f"-chname,{old_name},{out_name} {f_tmp}",
                output=archivo_salida,
            )
        _aviso("PRCPTOT", archivo_salida)


    def sdii(archivo_entrada: str, archivo_salida: str, tmp_dir: str | None = None):
        """SDII: PRCPTOT / R1mm por año. Unidades: mm/día.
        (etccdi_sdii de CDO devuelve un solo valor de toda la serie, por eso se arma
        a partir de la suma anual y del número de días húmedos por año.)"""
        _validate_file(archivo_entrada)
        with tempfile.TemporaryDirectory(dir=tmp_dir) as tmp:
            f_tot = os.path.join(tmp, "prcptot.nc")
            f_n = os.path.join(tmp, "r1mm.nc")
            f_raw = os.path.join(tmp, "sdii_raw.nc")
            cdo.yearsum(input=f"-mul {archivo_entrada} -gec,1 {archivo_entrada}", output=f_tot)
            cdo.etccdi_r1mm("freq=year", input=archivo_entrada, output=f_n)
            cdo.div(input=f"{f_tot} {f_n}", output=f_raw)  # 0 días húmedos -> faltante
            # CDO aplica operadores de derecha a izquierda: primero chname, luego setattribute.
            # Por eso los atributos se asignan al nombre NUEVO (índice), no al del archivo de entrada.
            old_name = cdo.showname(input=f_raw)[0].strip()
            out_name = "SDII_ETCCDI"
            cdo.setattribute(
                f'{out_name}@units=mm/day,{out_name}@long_name="Simple Daily Intensity Index (PRCPTOT/R1mm)"',
                input=f"-chname,{old_name},{out_name} {f_raw}",
                output=archivo_salida,
            )
        _aviso("SDII", archivo_salida)

    # -- percentiles ------------------------------------------------------------------
    @staticmethod
    def _umbral_percentil_humedos(archivo_base: str, archivo_umbral: str, pct: int) -> None:
        """
        Umbral = percentil `pct` de los días húmedos (PR ≥ 1 mm) del archivo base,
        un valor por píxel. Usa numpy.nanquantile (método linear), igual que xclim,
        en lugar de cdo timpctl (histograma que sesga la cola P95/P99).

        Solo netCDF4 + numpy (sin xarray) para evitar el error
        packaging.version.InvalidVersion: 'unknown' en entornos Anaconda/dask.
        """
        try:
            from netCDF4 import Dataset
        except ImportError as exc:
            raise ImportError(
                "R95p/R99p requieren netCDF4. Instala con: pip install netCDF4"
            ) from exc

        with Dataset(archivo_base, "r") as src:
            # Variable de precipitación (excluir time_bnds y similares)
            skip = {"time_bnds", "lat_bnds", "lon_bnds"}
            pr_names = [
                n for n, v in src.variables.items()
                if n not in src.dimensions and n not in skip and len(v.dimensions) >= 1
            ]
            if not pr_names:
                raise ValueError(f"No se encontró variable de precipitación en {archivo_base}")
            pr_name = pr_names[0]
            pr_var = src.variables[pr_name]
            dims = pr_var.dimensions  # p. ej. ('time', 'lat', 'lon')
            data = np.asarray(pr_var[:], dtype=np.float64)

            # Coordenadas espaciales a copiar
            spatial_dims = [d for d in dims if d != "time"]
            coord_data = {}
            for d in spatial_dims:
                if d in src.variables:
                    coord_data[d] = np.asarray(src.variables[d][:])
                else:
                    coord_data[d] = np.arange(src.dimensions[d].size)

            units = getattr(pr_var, "units", "mm/day")

        # Días secos o inválidos → NaN
        data = np.where(np.isfinite(data) & (data >= 1.0), data, np.nan)

        # Percentil a lo largo del tiempo (eje 0)
        with np.errstate(all="ignore"):
            thr_vals = np.nanquantile(data, pct / 100.0, axis=0).astype(np.float64)

        # Escribir NetCDF solo espacial (CDO lo retransmite al hacer -gt)
        with Dataset(archivo_umbral, "w", format="NETCDF4") as dst:
            for d in spatial_dims:
                dst.createDimension(d, coord_data[d].shape[0])
                cv = dst.createVariable(d, coord_data[d].dtype, (d,))
                cv[:] = coord_data[d]

            vv = dst.createVariable(
                pr_name, "f8", tuple(spatial_dims), fill_value=np.nan
            )
            vv[:] = thr_vals
            vv.long_name = (
                f"Percentile {pct} of wet-day (PR>=1 mm) precipitation"
            )
            vv.units = units

    def _rXXp(nombre: str, pct: int, archivo_entrada: str, archivo_salida: str,
              base_inicio: int, base_fin: int, tmp_dir: str | None = None) -> str:
        """
        Definición ETCCDI de precipitación muy/extremadamente húmeda:
          1) umbral = UN percentil por píxel, calculado con los días HÚMEDOS (≥ 1 mm)
             del periodo base (sin ventana móvil ni umbral por día del año);
          2) índice anual = suma de PR en los días con PR > umbral.

        El umbral se calcula con numpy.quantile (método linear), idéntico a xclim,
        porque cdo timpctl usa un histograma que introduce sesgo en P95/P99.

        Nota: no se aplica el bootstrap de Zhang et al. (2005) para los años dentro del
        periodo base (igual que la configuración de xclim usada en la comparación).
        """
        _validate_file(archivo_entrada)
        with tempfile.TemporaryDirectory(dir=tmp_dir) as tmp:
            f_base = os.path.join(tmp, "base.nc")
            f_thr = os.path.join(tmp, f"umbral_p{pct}.nc")
            f_tmp = os.path.join(tmp, f"r{pct}_raw.nc")
            f_masked = os.path.join(tmp, f"r{pct}_masked.nc")

            logger.info("%s | Paso 1: periodo base %d–%d", nombre, base_inicio, base_fin)
            cdo.selyear(f"{base_inicio}/{base_fin}", input=archivo_entrada, output=f_base)

            logger.info(
                "%s | Paso 2–3: percentil %d de días húmedos (≥ 1 mm)",
                nombre,
                pct,
            )
            ETCCDI_precip_malla._umbral_percentil_humedos(f_base, f_thr, pct)

            logger.info("%s | Paso 4: suma anual de PR en días > umbral", nombre)
            cdo.yearsum(
                input=f"-mul {archivo_entrada} -gt {archivo_entrada} {f_thr}",
                output=f_tmp,
            )

            # Donde el umbral es faltante (sin días húmedos en el base) → NaN
            # (cdo yearsum puede devolver 0; xclim deja NaN)
            cdo.ifthen(input=f"{f_thr} {f_tmp}", output=f_masked)

            # CDO aplica operadores de derecha a izquierda: primero chname, luego setattribute.
            # Por eso los atributos se asignan al nombre NUEVO (índice), no al del archivo de entrada.
            old_name = cdo.showname(input=f_masked)[0].strip()
            out_name = f"R{pct}P_ETCCDI"
            # long_name alineado con convención ETCCDI / Climpact
            # R95p → Very wet days  (Total precipitation from days > 95th percentile)
            # R99p → Extremely wet days  (Total precipitation from days > 99th percentile)
            if pct == 95:
                long_name = "Very wet days"
            elif pct == 99:
                long_name = "Extremely wet days"
            else:
                long_name = (
                    f"Total precipitation from days > {pct}th percentile"
                )
            cdo.setattribute(
                f'{out_name}@units=mm,{out_name}@long_name="{long_name}"',
                input=f"-chname,{old_name},{out_name} {f_masked}",
                output=archivo_salida,
            )
        _aviso(nombre, archivo_salida)
        return archivo_salida

    def r95p(archivo_entrada: str, archivo_salida: str, base_inicio: int,
             base_fin: int, tmp_dir: str | None = None) -> str:
        """R95p: precipitación anual en días > P95 de los días húmedos del periodo base. Unidades: mm."""
        return ETCCDI_precip_malla._rXXp("R95p", 95, archivo_entrada, archivo_salida,
                                         base_inicio, base_fin, tmp_dir)

    def r99p(archivo_entrada: str, archivo_salida: str, base_inicio: int,
             base_fin: int, tmp_dir: str | None = None) -> str:
        """R99p: precipitación anual en días > P99 de los días húmedos del periodo base. Unidades: mm."""
        return ETCCDI_precip_malla._rXXp("R99p", 99, archivo_entrada, archivo_salida,
                                         base_inicio, base_fin, tmp_dir)


#/////////////////////////////////////////////////////////////////////////////////////////////////////////
from calendar import isleap

class   ETCCDI_precip_in_situ:
    """
    Módulo para calcular índices climáticos ETCCDI usando datos --in situ-- (estación meteorológica) en formato .txt 
    
    Índices soportados:
        Precipitación :        Función del módulo:

        *** ID      ** Nombre Indicador   ***             
        
        *** R10mm   ** Número de días con precipitaciones intensas (PR ≥ 10 mm) ***                  
                    Ejemplo: ETCCDI_in_situ.r10mm(archivo_entrada: str, archivo_salida: str)  
        
        *** R20mm   ** Número de días con precipitaciones muy intensas (PR es ≥ 20 mm) ***                
                    Ejemplo: ETCCDI_in_situ.r20mm(archivo_entrada: str, archivo_salida: str) 
        
        *** Rx1day  ** Precipitación máxima en un día ***  
                    Ejemplo: ETCCDI_in_situ.rx1day(archivo_entrada: str, archivo_salida: str) 
                        
        *** Rx5day  ** Precipitación máxima en 5 días ***    
                    Ejemplo: ETCCDI_in_situ.rx5day(archivo_entrada: str, archivo_salida: str)  
                        
        *** CDD     ** Días secos (PR < 1 mm) consecutivos ***
                    Ejemplo: ETCCDI_in_situ.cdd(archivo_entrada: str, archivo_salida: str) 
                        
        *** CWD     ** Días húmedos (PR ≥ 1 mm) consecutivos ***   
                    Ejemplo: ETCCDI_in_situ.cwd(archivo_entrada: str, archivo_salida: str) 
                        
        *** SDII    ** Índice de intensidad diaria simple ***  
                    Ejemplo: ETCCDI_in_situ.sdii(archivo_entrada: str, archivo_salida: str) 

        *** PRCPTOT    **** Precipitación total anual en días lluviosos (PR ≥ 1 mm) *** 
                    Ejemplo: ETCCDI_in_situ.prcptot(archivo_entrada: str, archivo_salida: str)

        *** R95p    ** Días muy húmedos (días > Percentil 95th) ***
                    Periodo base actual: 1991 - 2020
                    Periodos anteriores: 1961 - 1990
                                         1981 - 2010
                                         
                    Ejemplo: ETCCDI_in_situ.r95p(archivo_entrada, archivo_salida, base_inicio, base_fin)
                    
            
        *** R99p    ** Días muy húmedos (días > Percentil 99th) ***
                    Periodo base actual: 1991 - 2020
                    Periodos anteriores: 1961 - 1990
                                         1981 - 2010
                    Ejemplo: ETCCDI_in_situ.r99p(archivo_entrada, archivo_salida, base_inicio, base_fin)
                                 
    
        *** Cada función tiene su descripción ***

        
        Índices climáticos según la definición de http://etccdi.pacificclimate.org/list_27_indices.shtml
        
        Autor(es): Omar Ramos Pérez
        Facultad Interdisciplinaria de Ciencias Exactas y Naturales - Departamento de Física - Universidad de Sonora
    
        Basado en el https://github.com/ioannidispanagiotis/Climate-Indices-ETCCDI/blob/main/cdd_y_climex_1.0.py
    
    """


    def r10mm(archivo_entrada:str, archivo_salida:str): 
        """
        Índice climático:   R10mm [Número de días con precipitaciones intensas].
        Definición:         Recuento anual de días en los que PR >= 10 mm.
        Unidades:           días
        
        archivo_entrada: Ruta del archivo .txt de la estación
            
        Formato del archivo de texto de la estación             
        Columnas: Año, Mes, Día, PR, TX, TN 
        
                    1901    1          1          -99.9    -3.1      -6.8
                    1901    1          2          -99.9    -1.3      -3.6
                    1901    1          3          -99.9    -0.5      -7.9
                    1901    1          4          -99.9    -1.0      -9.1
                    1901    1          5          -99.9    -1.8      -8.4

        mes y día deben ser números enteros.
        Las unidades de PR (Precipitación) son milímetros.        
        Las unidades de TX (Temperatura Máxima)/TN (Temperatura Mínima) son grados Celsius.
            
        archivo_salida: Ruta donde se guarda el archivo Excel (.xlsx)

        """
        
        df = pd.read_csv(archivo_entrada, sep=r'\s+')

        years = sorted(df['Year'].unique())
        r10_lst = []
        year_lst = []

        for y in years:
            year_data = df[df['Year'] == y]
            # Solo días válidos (PR >= 0); -99.9 u otros negativos se ignoran
            valid = year_data.loc[year_data['PR'] >= 0, 'PR']
            r10 = (valid >= 10).sum()
            r10_lst.append(int(r10))
            year_lst.append(y)

        df_out = pd.DataFrame({'Year': year_lst, 'Indice_R10mm': r10_lst})
        df_out.to_excel(archivo_salida, index=False)

        print("***************************************")
        print(f"✅ Índice R10mm ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("***************************************")



    def r20mm(archivo_entrada:str, archivo_salida:str): 
        """
        Índice climático:    R20 [Número de días con precipitaciones muy intensas]
        Definición:          Recuento anual de días en los que PR >= 20 mm.        
        Unidades:            Días

        archivo_entrada: Ruta del archivo .txt de la estación.
                    
        Formato del archivo de texto de la estación             
        Columnas: Año, Mes, Día, PR, TX, TN 
                    
                    1901    1          1          -99.9    -3.1      -6.8
                    1901    1          2          -99.9    -1.3      -3.6
                    1901    1          3          -99.9    -0.5      -7.9
                    1901    1          4          -99.9    -1.0      -9.1
                    1901    1          5          -99.9    -1.8      -8.4
                
        mes y día deben ser números enteros.
        Las unidades de PR (Precipitación) son milímetros.
        Las unidades de TX (Temperatura Máxima)/TN (Temperatura Mínima) son grados Celsius.

        archivo_salida: Ruta donde se guarda el archivo Excel (.xlsx)

        """
        
        df = pd.read_csv(archivo_entrada, sep=r'\s+')

        years = sorted(df['Year'].unique())
        r20_lst = []
        year_lst = []

        for y in years:
            df_year = df[df['Year'] == y]
            valid = df_year.loc[df_year['PR'] >= 0, 'PR']
            r20 = (valid >= 20).sum()
            r20_lst.append(int(r20))
            year_lst.append(y)

        df_out_r20 = pd.DataFrame({'Year': year_lst, 'Indice_R20mm': r20_lst})
        df_out_r20.to_excel(archivo_salida, index=False)
        
        print("**************************")        
        print(f"✅ Índice R20mm ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")



    def  rx1day(archivo_entrada:str, archivo_salida:str): 
        """
        Índice climático:   RX1day [Precipitación máxima en un día]
        Definición:         Precipitación máxima mensual en un día.
        Unidades:           mm

        archivo_entrada: Ruta del archivo .txt de la estación.
            
        Formato del archivo de texto de la estación             
        Columnas: Año, Mes, Día, PR, TX, TN 
                 
                    1901    1          1          -99.9    -3.1      -6.8                   
                    1901    1          2          -99.9    -1.3      -3.6
                    1901    1          3          -99.9    -0.5      -7.9
                    1901    1          4          -99.9    -1.0      -9.1
                    1901    1          5          -99.9    -1.8      -8.4
        
        Mes y Día deben ser números enteros.
        Las unidades de PR (Precipitación) son milímetros.
        Las unidades de TX (Temperatura Máxima)/TN (Temperatura Mínima) son grados Celsius.
  
        archivo_salida: Ruta donde se guarda el archivo Excel (.xlsx) 
        
        """
        
        df = pd.read_csv(archivo_entrada, sep=r'\s+')
        years = sorted(df['Year'].unique())
        rx1day_lst = []
        year_lst = []
        month_lst = []

        for y in years:
            df_year = df[df['Year'] == y]
            for m in range(1, 13):
                df_month = df_year[df_year['Month'] == m]
                valid = df_month.loc[df_month['PR'] >= 0, 'PR']
                if len(valid) > 0:
                    rx1day = float(valid.max())
                else:
                    rx1day = np.nan
                rx1day_lst.append(rx1day)
                year_lst.append(y)
                month_lst.append(m)

        df_out_rx1day = pd.DataFrame({
            'Year': year_lst,
            'Month': month_lst,
            'Indice_rx1daymm': rx1day_lst
        })
        df_out_rx1day.to_excel(archivo_salida, index=False)

        print("**************************")        
        print(f"✅ Índice RX1day ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")        
                



    def rx5day(archivo_entrada:str, archivo_salida:str):  
        """
        Índice climático:   RX5day [Precipitación máxima en 5 días]
        Definición:         Precipitación máxima mensual en 5 días.
        Unidades:           mm
        
        archivo_entrada: Ruta del archivo .txt de la estación  
                    
        Formato del archivo de texto de la estación             
        Columnas: Año, Mes, Día, PR, TX, TN 
       
                    1901    1          1          -99.9    -3.1      -6.8                   
                    1901    1          2          -99.9    -1.3      -3.6
                    1901    1          3          -99.9    -0.5      -7.9
                    1901    1          4          -99.9    -1.0      -9.1
                    1901    1          5          -99.9    -1.8      -8.4
                
        Mes y Día deben ser números enteros.
        Las unidades de PR (Precipitación) son milímetros.
        Las unidades de TX (Temperatura Máxima)/TN (Temperatura Mínima) son grados Celsius.
        
        archivo_salida: Ruta donde se guarda el archivo Excel (.xlsx)                    
        
        """
        
        df = pd.read_csv(archivo_entrada, sep=r'\s+')
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        df = df.sort_values('Date').reset_index(drop=True)

        years = sorted(df['Year'].unique())
        rx5day_lst = []
        year_lst = []
        month_lst = []

        for y in years:
            df_year = df[df['Year'] == y]
            for m in range(1, 13):
                df_month = df_year[df_year['Month'] == m].reset_index(drop=True)
                if len(df_month) < 5:
                    rx5day_lst.append(np.nan)
                else:
                    consecutive_5_day_rr = []
                    pr = df_month['PR'].values
                    for q in range(len(pr) - 4):
                        window = pr[q:q+5]
                        # Solo considerar la ventana si todos los valores son válidos (PR >= 0)
                        if np.all(window >= 0):
                            consecutive_5_day_rr.append(window.sum())
                    if consecutive_5_day_rr:
                        rx5day_lst.append(round(max(consecutive_5_day_rr), 2))
                    else:
                        rx5day_lst.append(np.nan)
                year_lst.append(y)
                month_lst.append(m)

        df_out_rx5day = pd.DataFrame({
            'Year': year_lst,
            'Month': month_lst,
            'Indice_rx5daymm': rx5day_lst
        })
        df_out_rx5day.to_excel(archivo_salida, index=False)

        print("**************************")        
        print(f"✅ Índice RX5day ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")        
                  
    
        
    def cdd(archivo_entrada: str, archivo_salida: str, aplicar_criterio_climpact: bool = True):
        """
        Índice climático:   CDD [Días secos (PR < 1 mm) consecutivos]
        Definición:         Número máximo de días consecutivos con PR < 1 mm al año.
        Unidades:           Días

        archivo_entrada: Ruta del archivo .txt de la estación
        archivo_salida:  Ruta donde se guarda el archivo Excel (.xlsx)

        aplicar_criterio_climpact : bool
            Si True (por defecto), aplica el criterio de completitud de Climpact:
            - máximo 3 días faltantes por mes
            - máximo 15 días faltantes por año
            Si se supera → el año se marca como NaN (igual que Climpact).

        Notas de implementación (alineado con ETCCDI / Climpact):
        - Se construye un calendario diario completo para cada año.
        - Los días ausentes en el archivo se tratan como faltantes (-99.9).
        - PR < 1 mm  → día seco (incrementa la racha).
        - PR >= 1 mm → día húmedo (rompe la racha).
        - PR < 0 o NaN → valor faltante (rompe la racha).
        - El índice es el máximo de las rachas dentro del año calendario.
        """
        df = pd.read_csv(archivo_entrada, sep=r'\s+')
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        df = df.set_index('Date').sort_index()

        years = sorted(df.index.year.unique())
        cdd_lst = []
        year_lst = []

        for y in years:
            # Calendario completo del año
            start = pd.Timestamp(year=y, month=1, day=1)
            end   = pd.Timestamp(year=y, month=12, day=31)
            full_idx = pd.date_range(start, end, freq='D')

            # Reindexar: días ausentes → NaN (luego se tratan como faltantes)
            s = df.loc[df.index.year == y, 'PR'].reindex(full_idx)

            # Contar faltantes
            missing_mask = s.isna() | (s < 0)
            n_missing = int(missing_mask.sum())

            # Criterio de completitud de Climpact
            if aplicar_criterio_climpact:
                # Faltantes por mes
                monthly_missing = missing_mask.groupby(full_idx.month).sum()
                if (monthly_missing > 3).any() or n_missing > 15:
                    cdd_lst.append(np.nan)
                    year_lst.append(y)
                    continue

            # Contar rachas de días secos
            max_streak = 0
            current = 0
            for pr in s.values:
                if pd.isna(pr) or pr < 0:          # faltante → interrumpe
                    current = 0
                elif pr < 1.0:                     # día seco
                    current += 1
                    if current > max_streak:
                        max_streak = current
                else:                              # día húmedo
                    current = 0

            cdd_lst.append(int(max_streak) if max_streak > 0 else 0)
            year_lst.append(y)

        df_out_cdd = pd.DataFrame({'Year': year_lst, 'Indice_cdd': cdd_lst})
        df_out_cdd.to_excel(archivo_salida, index=False)

        print("**************************")
        print(f"✅ Índice CDD ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")
    


    def cwd(archivo_entrada: str, archivo_salida: str, aplicar_criterio_climpact: bool = True):
        """
        Índice climático:   CWD [Días consecutivos con precipitación]
        Definición:         Número máximo de días consecutivos con PR >= 1 mm al año.
        Unidades:           días

        archivo_entrada: Ruta del archivo .txt de la estación
        archivo_salida:  Ruta donde se guarda el archivo Excel (.xlsx)

        aplicar_criterio_climpact : bool
            Si True (por defecto), aplica el criterio de completitud de Climpact:
            - máximo 3 días faltantes por mes
            - máximo 15 días faltantes por año
            Si se supera → el año se marca como NaN.

        Notas de implementación (alineado con ETCCDI / Climpact):
        - Se construye un calendario diario completo para cada año.
        - Los días ausentes en el archivo se tratan como faltantes (-99.9).
        - PR >= 1 mm → día húmedo (incrementa la racha).
        - PR < 1 mm  → día seco (rompe la racha).
        - PR < 0 o NaN → valor faltante (rompe la racha).
        """
        df = pd.read_csv(archivo_entrada, sep=r'\s+')
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        df = df.set_index('Date').sort_index()

        years = sorted(df.index.year.unique())
        cwd_lst = []
        year_lst = []

        for y in years:
            start = pd.Timestamp(year=y, month=1, day=1)
            end   = pd.Timestamp(year=y, month=12, day=31)
            full_idx = pd.date_range(start, end, freq='D')

            s = df.loc[df.index.year == y, 'PR'].reindex(full_idx)

            missing_mask = s.isna() | (s < 0)
            n_missing = int(missing_mask.sum())

            if aplicar_criterio_climpact:
                monthly_missing = missing_mask.groupby(full_idx.month).sum()
                if (monthly_missing > 3).any() or n_missing > 15:
                    cwd_lst.append(np.nan)
                    year_lst.append(y)
                    continue

            max_streak = 0
            current = 0
            for pr in s.values:
                if pd.isna(pr) or pr < 0:
                    current = 0
                elif pr >= 1.0:
                    current += 1
                    if current > max_streak:
                        max_streak = current
                else:
                    current = 0

            cwd_lst.append(int(max_streak) if max_streak > 0 else 0)
            year_lst.append(y)

        df_out_cwd = pd.DataFrame({'Year': year_lst, 'Indice_cwd': cwd_lst})
        df_out_cwd.to_excel(archivo_salida, index=False)

        print("**************************")
        print(f"✅ Índice CWD ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")



    def sdii(archivo_entrada:str, archivo_salida:str): 
        """
        Índice climático:   SDII [Índice de intensidad diaria simple]
        Definición:         Precipitación total anual dividida por el
                            número de días lluviosos del año. 
                            Se considera un día lluvioso cuando PR >= 1 mm.        
        Unidades:           mm/día
        
        archivo_entrada: Ruta del archivo .txt de la estación
                    
        Formato del archivo de texto de la estación             
        Columnas: Año, Mes, Día, PR, TX, TN
                                  
                    1901    1          1          -99.9    -3.1      -6.8
                    1901    1          2          -99.9    -1.3      -3.6
                    1901    1          3          -99.9    -0.5      -7.9
                    1901    1          4          -99.9    -1.0      -9.1
                    1901    1          5          -99.9    -1.8      -8.4

        Mes y Día deben ser números enteros.
        Las unidades de PR (Precipitación) son milímetros.
        Las unidades de TX (Temperatura Máxima)/TN (Temperatura Mínima) son grados Celsius.
        
        archivo_salida: Ruta donde se guarda el archivo Excel (.xlsx)
                    
        """
        
        df = pd.read_csv(archivo_entrada, sep=r'\s+')
        years = sorted(df['Year'].unique())
        sdii_lst = []
        year_lst = []

        for y in years:
            df_year = df[df['Year'] == y]
            wet = df_year.loc[(df_year['PR'] >= 1.0) & (df_year['PR'] >= 0), 'PR']
            wet_days = len(wet)
            if wet_days > 0:
                annual_precip = wet.sum()
                sdii = round(annual_precip / wet_days, 2)
            else:
                sdii = np.nan
            sdii_lst.append(sdii)
            year_lst.append(y)

        df_out_sdii = pd.DataFrame({'Year': year_lst, 'Indice_sdii': sdii_lst})
        df_out_sdii.to_excel(archivo_salida, index=False)
        
        print("**************************")        
        print(f"✅ Índice SDII ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")        
                   

    def prcptot(archivo_entrada:str, archivo_salida:str): 
        """
        Índice climático:   PRCPTOT [Precipitación total anual en días con lluvia (PR >= 1 mm)]
        Definición:         Precipitación total anual en días con lluvia.
                            Se considera que hay un día con lluvia cuando PR >= 1 mm.
        Unidades:           mm

        archivo_entrada: Ruta del archivo .txt de la estación
                    
        Formato del archivo de texto de la estación             
        Columnas: Año, Mes, Día, PR, TX, TN 
                                  
                    1901    1          1          -99.9    -3.1      -6.8
                    1901    1          2          -99.9    -1.3      -3.6
                    1901    1          3          -99.9    -0.5      -7.9
                    1901    1          4          -99.9    -1.0      -9.1
                    1901    1          5          -99.9    -1.8      -8.4

        Mes y Día deben ser números enteros.
        Las unidades de PR (Precipitación) son milímetros.
        Las unidades de TX (Temperatura Máxima)/TN (Temperatura Mínima) son grados Celsius.
        
        archivo_salida: Ruta donde se guarda el archivo Excel (.xlsx)

        """

        df = pd.read_csv(archivo_entrada, sep=r'\s+')
        years = sorted(df['Year'].unique())
        prcptot_lst = []
        year_lst = []

        for y in years:
            df_year = df[df['Year'] == y]
            # Solo días válidos y húmedos (PR >= 1)
            wet = df_year.loc[(df_year['PR'] >= 1.0) & (df_year['PR'] >= 0), 'PR']
            prcptot = round(wet.sum(), 2) if len(wet) > 0 else 0.0
            prcptot_lst.append(prcptot)
            year_lst.append(y)

        df_out_prcptot = pd.DataFrame({'Year': year_lst, 'Indice_prcptot': prcptot_lst})
        df_out_prcptot.to_excel(archivo_salida, index=False)
        
        print("**************************")   
        print(f"✅ Índice PRCPTOT ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")   



    def r95p(archivo_entrada: str, archivo_salida: str,
             base_inicio: int, base_fin: int,
             aplicar_criterio_climpact: bool = True):
        """
        Índice climático:   R95p
        Definición ETCCDI:  Suma anual de la precipitación en días húmedos (PR ≥ 1 mm)
                            que superan el percentil 95 de los días húmedos del periodo base.
        Unidades:           mm

        Parámetros
        ----------
        archivo_entrada : str
        archivo_salida  : str
        base_inicio, base_fin : int   Periodo de referencia (p. ej. 1981, 2010)
        aplicar_criterio_climpact : bool
            Si True, años con >15 días faltantes o >3 faltantes en algún mes → NaN.

        Notas
        -----
        - El umbral es UN solo valor (percentil 95 de todos los días húmedos del base).
        - Para años dentro del periodo base se aplica bootstrap (Zhang et al. 2005)
          para evitar tendencias artificiales.
        """
        WET_THRESH = 1.0
        PERCENTILE = 95

        df = pd.read_csv(archivo_entrada, sep=r'\s+')
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        df = df.set_index('Date').sort_index()

        # Solo días válidos y húmedos
        df_wet = df[(df['PR'] >= WET_THRESH) & (df['PR'] >= 0)][['PR']].copy()
        bp = df_wet[(df_wet.index.year >= base_inicio) &
                    (df_wet.index.year <= base_fin)].copy()

        if len(bp) < 10:
            raise ValueError(
                f"Muy pocos días húmedos en el periodo base {base_inicio}-{base_fin}. "
                "Revisa los datos o el periodo base."
            )

        # Umbral de referencia (todos los días húmedos del base)
        threshold_ref = float(np.percentile(bp['PR'].values, PERCENTILE))

        def _year_completeness_ok(y: int) -> bool:
            """Criterio Climpact: ≤3 faltantes/mes y ≤15 faltantes/año."""
            if not aplicar_criterio_climpact:
                return True
            start = pd.Timestamp(year=y, month=1, day=1)
            end   = pd.Timestamp(year=y, month=12, day=31)
            full  = pd.date_range(start, end, freq='D')
            s = df.loc[df.index.year == y, 'PR'].reindex(full)
            missing = s.isna() | (s < 0)
            if missing.sum() > 15:
                return False
            monthly = missing.groupby(full.month).sum()
            return not (monthly > 3).any()

        def _r95p_one_year(yr_wet: pd.DataFrame, thresh: float) -> float:
            """Suma de precipitación de días húmedos que superan el umbral."""
            if yr_wet.empty:
                return 0.0
            exceed = yr_wet.loc[yr_wet['PR'] > thresh, 'PR']
            return float(exceed.sum()) if len(exceed) else 0.0

        years_all = sorted(df.index.year.unique())
        results = {}

        # Años FUERA del periodo base → umbral fijo
        for y in years_all:
            if base_inicio <= y <= base_fin:
                continue
            if not _year_completeness_ok(y):
                results[y] = np.nan
                continue
            yr_wet = df_wet[df_wet.index.year == y]
            results[y] = round(_r95p_one_year(yr_wet, threshold_ref), 1)

        # Años DENTRO del periodo base → bootstrap
        bp_years = sorted(bp.index.year.unique())
        for o in bp_years:
            if not _year_completeness_ok(o):
                results[o] = np.nan
                continue
            # 29 umbrales dejando fuera el año o (y duplicando otro)
            boot_vals = []
            others = [yy for yy in bp_years if yy != o]
            for p in others:
                # periodo bootstrap = (base sin o) + año p duplicado
                boot_df = pd.concat([
                    bp[bp.index.year != o],
                    bp[bp.index.year == p]
                ])
                thr = float(np.percentile(boot_df['PR'].values, PERCENTILE))
                yr_o = bp[bp.index.year == o]
                boot_vals.append(_r95p_one_year(yr_o, thr))
            results[o] = round(float(np.mean(boot_vals)), 1) if boot_vals else 0.0

        # Ordenar y exportar
        out_years = sorted(results.keys())
        df_out = pd.DataFrame({
            'Date': out_years,
            'R95p (mm)': [results[y] for y in out_years]
        })
        df_out.to_excel(archivo_salida, index=False)

        print("**************************")
        print(f"✅ Índice R95p ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print(f"   Umbral 95p del periodo base {base_inicio}-{base_fin}: {threshold_ref:.2f} mm")
        print("**************************")

    def r99p(archivo_entrada: str, archivo_salida: str,
             base_inicio: int, base_fin: int,
             aplicar_criterio_climpact: bool = True):
        """
        Índice climático:   R99p
        Definición ETCCDI:  Suma anual de la precipitación en días húmedos (PR ≥ 1 mm)
                            que superan el percentil 99 de los días húmedos del periodo base.
        Unidades:           mm

        Parámetros
        ----------
        archivo_entrada : str
        archivo_salida  : str
        base_inicio, base_fin : int   Periodo de referencia (p. ej. 1981, 2010)
        aplicar_criterio_climpact : bool
            Si True, años con >15 días faltantes o >3 faltantes en algún mes → NaN.

        Notas
        -----
        - El umbral es UN solo valor (percentil 99 de todos los días húmedos del base).
        - Para años dentro del periodo base se aplica bootstrap (Zhang et al. 2005).
        """
        WET_THRESH = 1.0
        PERCENTILE = 99

        df = pd.read_csv(archivo_entrada, sep=r'\s+')
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        df = df.set_index('Date').sort_index()

        df_wet = df[(df['PR'] >= WET_THRESH) & (df['PR'] >= 0)][['PR']].copy()
        bp = df_wet[(df_wet.index.year >= base_inicio) &
                    (df_wet.index.year <= base_fin)].copy()

        if len(bp) < 10:
            raise ValueError(
                f"Muy pocos días húmedos en el periodo base {base_inicio}-{base_fin}. "
                "Revisa los datos o el periodo base."
            )

        threshold_ref = float(np.percentile(bp['PR'].values, PERCENTILE))

        def _year_completeness_ok(y: int) -> bool:
            if not aplicar_criterio_climpact:
                return True
            start = pd.Timestamp(year=y, month=1, day=1)
            end   = pd.Timestamp(year=y, month=12, day=31)
            full  = pd.date_range(start, end, freq='D')
            s = df.loc[df.index.year == y, 'PR'].reindex(full)
            missing = s.isna() | (s < 0)
            if missing.sum() > 15:
                return False
            monthly = missing.groupby(full.month).sum()
            return not (monthly > 3).any()

        def _r99p_one_year(yr_wet: pd.DataFrame, thresh: float) -> float:
            if yr_wet.empty:
                return 0.0
            exceed = yr_wet.loc[yr_wet['PR'] > thresh, 'PR']
            return float(exceed.sum()) if len(exceed) else 0.0

        years_all = sorted(df.index.year.unique())
        results = {}

        for y in years_all:
            if base_inicio <= y <= base_fin:
                continue
            if not _year_completeness_ok(y):
                results[y] = np.nan
                continue
            yr_wet = df_wet[df_wet.index.year == y]
            results[y] = round(_r99p_one_year(yr_wet, threshold_ref), 1)

        bp_years = sorted(bp.index.year.unique())
        for o in bp_years:
            if not _year_completeness_ok(o):
                results[o] = np.nan
                continue
            boot_vals = []
            others = [yy for yy in bp_years if yy != o]
            for p in others:
                boot_df = pd.concat([
                    bp[bp.index.year != o],
                    bp[bp.index.year == p]
                ])
                thr = float(np.percentile(boot_df['PR'].values, PERCENTILE))
                yr_o = bp[bp.index.year == o]
                boot_vals.append(_r99p_one_year(yr_o, thr))
            results[o] = round(float(np.mean(boot_vals)), 1) if boot_vals else 0.0

        out_years = sorted(results.keys())
        df_out = pd.DataFrame({
            'Date': out_years,
            'R99p (mm)': [results[y] for y in out_years]
        })
        df_out.to_excel(archivo_salida, index=False)

        print("**************************")
        print(f"✅ Índice R99p ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print(f"   Umbral 99p del periodo base {base_inicio}-{base_fin}: {threshold_ref:.2f} mm")
        print("**************************")

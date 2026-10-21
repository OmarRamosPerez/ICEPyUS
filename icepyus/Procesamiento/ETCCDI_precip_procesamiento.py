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


class ETCCDI_precip_malla:
    """
    Módulo para calcular índices climáticos ETCCDI en datos NetCDF (malla).
    PR = Precipitación diaria en mm.
    
    Índices de precipitación soportados:
        
        *** ID      ** Nombre Indicador   ***             
        
        *** R10mm   ** Número de días con precipitaciones intensas (PR ≥ 10 mm) ***                  
                    Ejemplo: ETCCDI_malla.r10mm_malla(infile: str, output_file: str)
        
        *** R20mm   ** Número de días con precipitaciones muy intensas (PR es ≥ 20 mm) ***                
                    Ejemplo: ETCCDI_malla.r20mm(infile: str, output_file: str)
        
        *** Rx1day  ** Precipitación máxima en un día ***  
                    Ejemplo: ETCCDI_malla.rx1day(infile: str, output_file: str)
                        
        *** Rx5day  ** Precipitación máxima en 5 días ***    
                    Ejemplo: ETCCDI_malla.rx5day(infile: str, output_file: str) 
                        
        *** CDD     ** Días secos (PR < 1 mm) consecutivos ***
                    Ejemplo: ETCCDI_malla.cdd(infile: str, output_file: str)
                        
        *** CWD     ** Días húmedos (PR ≥ 1 mm) consecutivos ***   
                    Ejemplo: ETCCDI_malla.cwd(infile: str, output_file: str)
                        
        *** SDII    ** Índice de intensidad diaria simple ***  
                    Ejemplo: ETCCDI_malla.sdii(infile: str, output_file: str)

        *** PRCPTOT    **** Precipitación total anual en días lluviosos (PR ≥ 1 mm) *** 
                    Ejemplo: ETCCDI_malla.prcptot(infile: str, output_file: str)

        *** R95p    ** Días muy húmedos (días > Percentil 95th) ***
                    Periodo base actual: 1991 - 2020
                    Periodos anteriores: 1961 - 1990
                                         1981 - 2010
                    Ejemplo: ETCCDI_malla.r95p(input_file, output_file, base_start, base_end)
    
    
        *** Cada función tiene su descripción ***

        Índices climáticos según la definición de http://etccdi.pacificclimate.org/list_27_indices.shtml
        
        Autor(es): Omar Ramos Pérez
        Facultad Interdisciplinaria de Ciencias Exactas y Naturales - Departamento de Física - Universidad de Sonora
        
    """

    def r10mm(archivo_entrada: str, archivo_salida: str):
        """ Esta función calcula el Índice ETCCDI R10 para un archivo netcdf
        
        Índice climático:   R10 [Número de días con precipitaciones intensas]
        Definición:         Recuento anual de días en los que PR es ≥ 10 mm
        Unidades:           días
        
        archivo_entrada:    Ruta del archivo netcdf
        archivo_salida:     Ruta donde se guardará el archivo NetCDF con el índice correspondiente.         
                    
        """
    
        cdo.etccdi_r10mm(input=archivo_entrada, output=archivo_salida)
        print("*****************************************")
        print(f"✅ Índice R10mm ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("*****************************************")


    def r20mm(archivo_entrada: str, archivo_salida: str):
        """ Esta función calcula el índice ETCCDI R20 para un archivo netcdf
        
        Índice climático:   R20 [Número de días con precipitaciones muy intensas]
        Definición:         Recuento anual de días en los que PR es ≥ 20 mm
        Unidades:           días

        archivo_entrada:    Ruta del archivo netcdf
        archivo_salida:     Ruta donde se guardará el archivo NetCDF con el índice correspondiente.         
 
        """
        
        cdo.etccdi_r20mm(input=archivo_entrada, output=archivo_salida)
        print("*****************************************")
        print(f"✅ Índice R20mm ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("*****************************************")


    def rx1day(archivo_entrada: str, archivo_salida: str):
        """ Esta función calcula el índice ETCCDI RX1day para un archivo netcdf
        
        Índice climático:   RX1day [Precipitación máxima en un día]
        Definición:         Precipitación máxima mensual en un día.
        Unidades:           mm    

        archivo_entrada:    Ruta del archivo netcdf
        archivo_salida:     Ruta donde se guardará el archivo NetCDF con el índice correspondiente.         
 
        """
        cdo.etccdi_rx1day(input=archivo_entrada, output=archivo_salida)
        print("*****************************************")
        print(f"✅ Índice RX1day ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("*****************************************")


    def rx5day(archivo_entrada: str, archivo_salida: str):
        """ Esta función calcula el índice ETCCDI RX5day para un archivo netcdf
        
        Índice climático:   RX5day [Precipitación máxima en 5 días].
        Definición:         Precipitación máxima mensual en 5 días
        Unidades:           mm

        archivo_entrada:    Ruta del archivo netcdf
        archivo_salida:     Ruta donde se guardará el archivo NetCDF con el índice correspondiente.         
 
        """
        
        cdo.etccdi_rx5day(input=archivo_entrada, output=archivo_salida)
        print("*****************************************")
        print(f"✅ Índice RX5day ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("*****************************************")


    def cdd(archivo_entrada: str, archivo_salida: str):
        """ Esta función calcula el índice ETCCDI CDD para un archivo netcdf
        
        Índice climático:   CDD [Días secos consecutivos]
        Definición:         Número máximo de días consecutivos en los que PR < 1 mm 
        Unidades:           días

        archivo_entrada:    Ruta del archivo netcdf
        archivo_salida:     Ruta donde se guardará el archivo NetCDF con el índice correspondiente.         
 
        """

        cdo.etccdi_cdd(input=archivo_entrada, output=archivo_salida)
        print("*****************************************")
        print(f"✅ Índice CDD ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("*****************************************")

        
    def cwd(archivo_entrada: str, archivo_salida: str):
        """ Esta función calcula el índice ETCCDI CWD para un archivo netcdf
        
        Índice climático:   CWD [Días húmedos consecutivos]
        Definición:         Número máximo de días consecutivos en los que PR ≥ a 1 mm 
        Unidades:           días

        archivo_entrada:    Ruta del archivo netcdf
        archivo_salida:     Ruta donde se guardará el archivo NetCDF con el índice correspondiente.         
 
        """

        cdo.etccdi_cwd(input=archivo_entrada, output=archivo_salida)
        print("*****************************************")
        print(f"✅ Índice CWD ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("*****************************************")


    def sdii(archivo_entrada: str, archivo_salida: str):
        """ Esta función calcula el índice ETCCDI SDII para un archivo netcdf
        
        Índice climático:   SDII [Índice de intensidad diaria simple]. 
        Definición:         Se calcula dividiendo la precipitación total anual 
                            entre el número de días con lluvia (PR ≥ 1 mm) en el año.         
        Unidades:           mm/día

        archivo_entrada:    Ruta del archivo netcdf
        archivo_salida:     Ruta donde se guardará el archivo NetCDF con el índice correspondiente.         
                 
        """

        cdo.etccdi_sdii(input=archivo_entrada, output=archivo_salida)
        print("*****************************************")
        print(f"✅ Índice SDII ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("*****************************************")


    def prcptot(archivo_entrada: str, archivo_salida: str):
        """ Esta función calcula el Indice ETCCDI PRCPTOT para un archivo netcdf
 
        Índice climático:   PRCPTOT [Precipitación total anual en días lluviosos]
        Definición:         Precipitación total anual en días lluviosos (PR ≥ 1 mm).
        Unidades:           mm    
        
        archivo_entrada:    Ruta del archivo netcdf
        archivo_salida:     Ruta donde se guardará el archivo NetCDF con el índice correspondiente.         
 
        """
# Paso 1: máscara de días húmedos (pr >= 1 mm/día) → archivo temporal
        tmp_mask = "/tmp/mask_wet_days.nc"
        cdo.gtc(1, input=archivo_entrada, output=tmp_mask)

# Paso 2: multiplicar precipitación original por la máscara
        tmp_mul = "/tmp/pr_wet_days.nc"
        cdo.mul(input=f"{archivo_entrada} {tmp_mask}", output=tmp_mul)

# Paso 3: suma anual → PRCPTOT
        cdo.yearsum(input=tmp_mul, output=archivo_salida)
        
        print("*****************************************")
        print(f"✅ Índice PRCPTOT calculado exitosamente. Archivo guardado:  {archivo_salida}")
        print("*****************************************")




    def r95p( archivo_entrada: str,
    archivo_salida: str,
    base_inicio: int ,
    base_fin:   int ,
    tmp_dir:    str | None = None,
    ) -> str:
        """
    Calcula el índice ETCCDI R95p para un archivo netcdf
    
    Índice climático:   R95p [Días muy húmedos]
    Definición:         Suma anual de precipitación en los días en que la precipitación supera
                        el percentil 95 del período de referencia (solo días húmedos ≥ 1 mm).
    Unidades:           mm

        R95p = Σ RRij   donde  RRij > RR95p  y  RRij ≥ 1 mm

    Parámetros
    ----------
    archivo_entrada : str        Archivo NetCDF de precipitación diaria (mm/día).
    archivo_salida : str       Archivo NetCDF de salida con R95p anual.
    base_start : int        Año inicio del período de referencia (p. ej.,   1981).
    base_end : int          Año fin del período de referencia (p. ej., 2010).
    tmp_dir : str | None    Directorio para temporales (None → carpeta del sistema).

    """
        _validate_file(archivo_entrada)
        tmp = tmp_dir or tempfile.gettempdir()

        f_base   = os.path.join(tmp, "r95p_base.nc")
        f_pct95  = os.path.join(tmp, "r95p_pct95.nc")
        f_wet    = os.path.join(tmp, "r95p_wet.nc")
        f_mask   = os.path.join(tmp, "r95p_mask.nc")
        f_masked = os.path.join(tmp, "r95p_masked.nc")

        try:
            logger.info("R95p | Paso 1: Extrayendo período base %d–%d", base_inicio, base_fin)
            cdo.selyear(
            f"{base_inicio}/{base_fin}",
            input=archivo_entrada,
            output=f_base,
            )

            logger.info("R95p | Paso 2: Calculando percentil 95 estacional")
            cdo.ydrunpctl(
            "95,5",
            input=f"{f_base} -ydrunmin,5 {f_base} -ydrunmax,5 {f_base}",
            output=f_pct95,
            )

            logger.info("R95p | Paso 3: Máscara días húmedos (≥ 1 mm)")
            cdo.gtc(
            "1.0",
            input=archivo_entrada,
            output=f_wet,
            )

            logger.info("R95p | Paso 4: Máscara días > percentil 95")
        # cdo sub resta el percentil (365 pasos) a cada día de la serie completa
        # usando la lógica de día-del-año; luego gtc,0 devuelve 1 donde pr > pct95
            f_sub95 = f_base.replace("r95p_base", "r95p_sub95")
            cdo.ydaysub(
            input=f"{archivo_entrada} {f_pct95}",
            output=f_sub95,
            )
            cdo.gtc(
            "0",
            input=f_sub95,
            output=f_mask,
            )

            logger.info("R95p | Paso 5: Precipitación filtrada (húmedo AND > pct95)")
            cdo.mul(
            input=f"{archivo_entrada} -mul {f_wet} {f_mask}",
            output=f_masked,
            )

            logger.info("R95p | Paso 6: Suma anual → R95p")
            cdo.yearsum(
            input=f_masked,
            output=archivo_salida,
            )

 #           logger.info("✅ R95p calculado → %s", archivo_salida)
            print("*****************************************")
            print(f"✅ Índice R95P calculado exitosamente. Archivo guardado:  {archivo_salida}")
            print("*****************************************")


        finally:
            _remove_files(f_base, f_pct95, f_wet, f_mask, f_masked,
                      f_base.replace('r95p_base', 'r95p_sub95'))

        return archivo_salida
    

    def r99p(
    archivo_entrada: str,
    archivo_salida: str,
    base_inicio: int ,
    base_fin:   int ,
    tmp_dir:    str | None = None,
    ) -> str:
        """
    Calcula el índice ETCCDI R99p para un archivo netcdf

    Índice Climático:   R99p [Días extremadamente húmedos]
    Definición:         Suma anual de precipitación en los días en que la precipitación supera
                        el percentil 99 del período de referencia (solo días húmedos ≥ 1 mm).
    Unidades:           mm
    
        R99p = Σ RRij   donde  RRij > RR99p  y  RRij ≥ 1 mm

    Parámetros
    ----------
    input_file : str        Archivo NetCDF de precipitación diaria (mm/día).
    output_file : str       Archivo NetCDF de salida con R99p anual.
    base_start : int        Año inicio del período de referencia (default 1981).
    base_end : int          Año fin del período de referencia (default 2010).
    tmp_dir : str | None    Directorio para temporales (None → carpeta del sistema).

    """
        _validate_file(archivo_entrada)
        tmp = tmp_dir or tempfile.gettempdir()

        f_base   = os.path.join(tmp, "r99p_base.nc")
        f_pct99  = os.path.join(tmp, "r99p_pct99.nc")
        f_wet    = os.path.join(tmp, "r99p_wet.nc")
        f_mask   = os.path.join(tmp, "r99p_mask.nc")
        f_masked = os.path.join(tmp, "r99p_masked.nc")

        try:
            logger.info("R99p | Paso 1: Extrayendo período base %d–%d", base_inicio, base_fin)
            cdo.selyear(
            f"{base_inicio}/{base_fin}",
            input=archivo_entrada,
            output=f_base,
            )

            logger.info("R99p | Paso 2: Calculando percentil 99 estacional")
            cdo.ydrunpctl(
            "99,5",
            input=f"{f_base} -ydrunmin,5 {f_base} -ydrunmax,5 {f_base}",
            output=f_pct99,
            )

            logger.info("R99p | Paso 3: Máscara días húmedos (≥ 1 mm)")
            cdo.gtc(
            "1.0",
            input=archivo_entrada,
            output=f_wet,
            )

            logger.info("R99p | Paso 4: Máscara días > percentil 99")
            f_sub99 = f_base.replace("r99p_base", "r99p_sub99")
            cdo.ydaysub(
            input=f"{archivo_entrada} {f_pct99}",
            output=f_sub99,
            )
            cdo.gtc(
            "0",
            input=f_sub99,
            output=f_mask,
            )

            logger.info("R99p | Paso 5: Precipitación filtrada (húmedo AND > pct99)")
            cdo.mul(
            input=f"{archivo_entrada} -mul {f_wet} {f_mask}",
            output=f_masked,
            )

            logger.info("R99p | Paso 6: Suma anual → R99p")
            cdo.yearsum(
            input=f_masked,
            output=archivo_salida,
            )

        #logger.info("✅ R99p calculado → %s", output_file)
        
            print("*****************************************")
            print(f"✅ Índice R99P calculado exitosamente. Archivo guardado:  {archivo_salida}")
            print("*****************************************")


        finally:
            _remove_files(f_base, f_pct99, f_wet, f_mask, f_masked,
                      f_base.replace('r99p_base', 'r99p_sub99'))

        return archivo_salida



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
                    Ejemplo: ETCCDI_in_situ.     (infile: str, output_file: str)

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
        
        df = pd.read_csv(archivo_entrada, sep='\s+')  # Data import

        r10_lst = []
        for y in df['Year'].unique():
            year_data = df[df['Year'] == y]
            r10 = (year_data['PR'] >= 10).sum()
            r10_lst.append(r10)
            
        R10_out = np.array(r10_lst) 

        dates_r10 = pd.date_range(start=str(df['Year'].min()), end=str(df['Year'].max() + 1), freq="YE")
        df_out = pd.DataFrame({'Year': dates_r10.year, 'Indice_R10mm': R10_out})

        # 3. Save the DataFrame to an Excel file (.xlsx)
        # Set index=False to avoid writing the DataFrame index as an extra column in Excel
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
        
        df = pd.read_csv(archivo_entrada, sep='\s+')  # Data import

        r20_lst = []
        for y in df['Year'].unique():
            df_year = df[df['Year'] == y]                   # ✅ Filtra por columna Year
            if not df_year.empty:
                     # Counting days of precipitation greater than or equal to 20 mm
                    r20 = (df_year['PR'] >= 20).sum()
                    r20_lst.append(r20)
            else:
                    r20 = float("NaN")
                    r20_lst.append(r20)          


        r20_out = np.array(r20_lst) 

        dates_r20 = pd.date_range(start=str(df['Year'].min()), end=str(df['Year'].max() + 1), freq="YE")
        df_out_r20 = pd.DataFrame({'Year': dates_r20.year, 'Indice_R20mm': r20_out} )


        # 3. Save the DataFrame to an Excel file (.xlsx)
        # Set index=False to avoid writing the DataFrame index as an extra column in Excel
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
        
        df = pd.read_csv(archivo_entrada, sep='\s+')  # Data import
        rx1day_lst = []  # List to save index values per year

        for y in df['Year'].unique():
            df_year = df[df['Year'] == y]                   # ✅ Filtra por columna Year
            if not df_year.empty:
                for m in range(1, 13):
                    df_month = df_year[df_year['Month'] == m]  # ✅ Filtra por columna Month
                    if not df_month.empty:
                        rx1day = df_month['PR'].max()          # ✅ Máximo de precipitación
                        rx1day_lst.append(rx1day)
                    else:
                        rx1day_lst.append(float("NaN"))
            else:
                rx1day_lst.append(float("NaN"))
                
                
        rx1day_out = np.array(rx1day_lst)        


        dates_rx1day = pd.date_range(start=str(df['Year'].min()), end=str(df['Year'].max() + 1), freq="ME")


        df_out_rx1day = pd.DataFrame({'Year': dates_rx1day.year, 'Month': dates_rx1day.month, 'Indice_rx1daymm': rx1day_out})


        # 3. Save the DataFrame to an Excel file (.xlsx)
        # Set index=False to avoid writing the DataFrame index as an extra column in Excel
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
        
        df = pd.read_csv(archivo_entrada, sep='\s+')  # Data import
    
        rx5day_lst = []  # List to save index values per year

        for y in df['Year'].unique():
            df_year = df[df['Year'] == y]
            if not df_year.empty:
                for m in range(1, 13):
                    df_month = df_year[df_year['Month'] == m].reset_index(drop=True)  # reset para índices 0,1,2,...
                    if not df_month.empty:
                        consecutive_5_day_rr = []
                        q = 0
                        # Iterar mientras haya al menos 5 días desde la posición q
                        while q <= len(df_month) - 5:
                            rx5day_m = df_month['PR'].iloc[q:q+5].sum()  # suma de 5 días consecutivos
                            consecutive_5_day_rr.append(rx5day_m)
                            q += 1
                        if consecutive_5_day_rr:
                            rx5day_lst.append(round(max(consecutive_5_day_rr), 2))
                        else:
                            rx5day_lst.append(float("NaN"))
                    else:
                        rx5day_lst.append(float("NaN"))  # ← también estaba mal (usaba rx1day_lst)
            else:
                rx5day_lst.append(float("NaN"))  # ← ídem
                
                
        rx5day_out = np.array(rx5day_lst)        
                
        dates_rx5day = pd.date_range(start=str(df['Year'].min()), end=str(df['Year'].max() + 1), freq="ME")
         
                
        df_out_rx5day = pd.DataFrame({'Year': dates_rx5day.year, 'Month': dates_rx5day.month,  'Indice_rx5daymm': rx5day_out})


        # 3. Save the DataFrame to an Excel file (.xlsx)
        # Set index=False to avoid writing the DataFrame index as an extra column in Excel
        df_out_rx5day.to_excel(archivo_salida, index=False)

        print("**************************")        
        print(f"✅ Índice RX5day ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")        
                  
    
        
    def cdd(archivo_entrada:str, archivo_salida:str):  
        """
        Índice climático:   CDD [Días secos (PR < 1 mm) consecutivos]
        Definición:         Número máximo de días consecutivos con PR < 1 mm al año.
        Unidades:           Días
           
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
        
        df = pd.read_csv(archivo_entrada, sep='\s+')  # Data import

        cdd_lst = []  # List to save index values per year

        for y in df['Year'].unique():
            df_year = df[df['Year'] == y]
            if not df_year.empty:        
                    # Yearly count of consecutive days with daily precipitation < 1 mm
                    cdd_df = df_year[df_year['PR'] < 1].dropna().reset_index(drop=True)
                    count = 0
                    count_lst = []
                    for q in range(1, len(cdd_df)):
                        if (cdd_df['Day'].iloc[q] - cdd_df['Day'].iloc[q-1]) != 1:   # ← compara columna Day
                            count = 0
                        else:
                            count = count + 1
                        count_lst.append(count)
                    if len(count_lst) == 0:  # Added in order to avoid error in finding the max() of an empty list
                         pass
                    else:
                         cdd = max(count_lst) + 1
                    cdd_lst.append(cdd)
            else:
                 cdd = float("NaN")
                 cdd_lst.append(cdd)
                
                
                
        cdd_out = np.array(cdd_lst) 

        dates_cdd = pd.date_range(start=str(df['Year'].min()), end=str(df['Year'].max() + 1), freq="YE")
        df_out_cdd = pd.DataFrame({'Year': dates_cdd.year, 'Indice_cdd': cdd_out} )   



        ## 3. Save the DataFrame to an Excel file (.xlsx)
        # Set index=False to avoid writing the DataFrame index as an extra column in Excel
        df_out_cdd.to_excel(archivo_salida, index=False)

        print("**************************")
        print(f"✅ Índice CDD ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")    
    


    def cwd(archivo_entrada:str, archivo_salida:str): 
        """
        Índice climático:   CWD [Días consecutivos con precipitación]
        Definición:         Número máximo de días consecutivos con PR >= 1 mm al año.
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
        
        cwd_lst = []  # List to save index values per year
    
        df = pd.read_csv(archivo_entrada, sep='\s+') # import

        for y in df['Year'].unique():
            df_year = df[df['Year'] == y]
            if not df_year.empty:        
                    # Yearly count of consecutive days with daily precipitation > 1 mm
                    cwd_df = df_year[df_year['PR'] > 1].dropna().reset_index(drop=True)
                    count = 0
                    count_lst = []
                    for q in range(1, len(cwd_df)):
                        if (cwd_df['Day'].iloc[q] - cwd_df['Day'].iloc[q-1]) != 1:   # ← compara columna Day
                            count = 0
                        else:
                            count = count + 1
                        count_lst.append(count)
                    if len(count_lst) == 0:  # Added in order to avoid error in finding the max() of an empty list
                         pass
                    else:
                         cdd = max(count_lst) + 1
                    cwd_lst.append(cdd)
            else:
                 cwd = float("NaN")
                 cwd_lst.append(cwd)
                
        cwd_out = np.array(cwd_lst) 

        dates_cwd = pd.date_range(start=str(df['Year'].min()), end=str(df['Year'].max() + 1), freq="YE")
        df_out_cwd = pd.DataFrame({'Year': dates_cwd.year, 'Indice_cwd': cwd_out} )   


        ## 3. Save the DataFrame to an Excel file (.xlsx)
        # Set index=False to avoid writing the DataFrame index as an extra column in Excel
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
        
        sdii_lst = []  # List to save index values per year
        df = pd.read_csv(archivo_entrada, sep='\s+') # import

        for y in df['Year'].unique():
            df_year = df[df['Year'] == y]
            if not df_year.empty:        
                    wet_days_df = df_year[df_year['PR'] >= 1].dropna()  # Days with daily precipitation >= 1 mm        
                    annual_precip = wet_days_df['PR'].sum()  # Calculates the sum of precipitation in wet days
                    wet_days = len(df_year[df_year['PR'] >= 1].dropna())
                    sdii = annual_precip / wet_days
                    sdii_lst.append(round(sdii, 2))
            else:
                sdii = float("NaN")
                sdii_lst.append(sdii)

                    

        sdii_out = np.array(sdii_lst) 

        dates_sdii = pd.date_range(start=str(df['Year'].min()), end=str(df['Year'].max() + 1), freq="YE")
        df_out_sdii = pd.DataFrame({'Year': dates_sdii.year, 'Indice_sdii': sdii_out} )        
                
               
        ## 3. Save the DataFrame to an Excel file (.xlsx)
        # Set index=False to avoid writing the DataFrame index as an extra column in Excel
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

        prcptot_lst = []  # List to save index values per year
        df = pd.read_csv(archivo_entrada, sep='\s+') # import
        
        
        for y in df['Year'].unique():
            df_year = df[df['Year'] == y]
            if not df_year.empty:      
                wet_days_df = df_year[df_year >= 1].dropna()  # Days with daily precipitation >= 1 mm
                prcptot = wet_days_df['PR'].sum()  # Calculates the sum of precipitation in wet days
                prcptot_lst.append(round(prcptot, 2))
            else:
                prcptot = float("NaN")
                prcptot_lst.append(prcptot)


        prcptot_out = np.array(prcptot_lst) 

        dates_prcptot = pd.date_range(start=str(df['Year'].min()), end=str(df['Year'].max() + 1), freq="YE")
        df_out_prcptot = pd.DataFrame({'Year': dates_prcptot.year, 'Indice_prcptot': prcptot_out} )   

## 3. Save the DataFrame to an Excel file (.xlsx)
# Set index=False to avoid writing the DataFrame index as an extra column in Excel
        df_out_prcptot.to_excel(archivo_salida, index=False)
        
        print("**************************")   
        print(f"✅ Índice PRCPTOT ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")   



    def r95p(archivo_entrada:str, archivo_salida:str, base_inicio: int, base_fin: int):
        """
        Índice climático:   R95p [Precipitación total anual cuando la precipitación es superior al percentil 95]
        Definición:         Sea PRwj la cantidad de precipitación diaria en un día lluvioso
                            w (PR ≥ 1,0 mm) en el período i y sea PRwn95 el percentil 95 de la precipitación en días lluviosos
                            en el período base.
                            Periodo base actual: 1991 - 2020
                            Periodos anteriores: 1961 - 1990
                                                 1981 - 2010
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

        VARIABLE   = 'PR'
        PERCENTILE = 95
        WET_THRESH = 1.0

        def leap_year(y):
            return "True" if isleap(y) else "False"

# ─────────────────────────────────────────────────────────────────────────────
# 1. Carga y preparación
# ─────────────────────────────────────────────────────────────────────────────
        df = pd.read_csv(archivo_entrada, sep=r'\s+')
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        df = df.set_index('Date').sort_index()

        df_wet = df[df[VARIABLE] >= WET_THRESH][[VARIABLE]].copy()
        bp     = df_wet[(df_wet.index.year >= base_inicio) & (df_wet.index.year <= base_fin)].copy()

# ─────────────────────────────────────────────────────────────────────────────
        def window_values_with_initial(source_df, m, d, years_range):
            """
    Replica exactamente el patrón del original:
      1. Filtra source_df en [ancla-2, ancla+2] (ancla = primer (m,d) en source_df)
      2. Itera sobre years_range y concatena la ventana de cada año
    Devuelve array 1-D con todos los valores acumulados.
    """
            mask_md = (source_df.index.month == m) & (source_df.index.day == d)
            if not mask_md.any():
                return np.array([])

            anchor = source_df.index[mask_md][0]
            d1_init = anchor - pd.DateOffset(days=2)
            d2_init = anchor + pd.DateOffset(days=2)

    # Bloque inicial (ancla, primer año)
            mask_init = (source_df.index >= d1_init) & (source_df.index <= d2_init)
            parts = [source_df.loc[mask_init, VARIABLE].to_numpy(dtype=float)]

    # Loop sobre los años del rango
            for yr in years_range:
                try:
                    d1 = d1_init.replace(year=yr)
                    d2 = d1 + pd.DateOffset(days=4)
                    mask = (source_df.index >= d1) & (source_df.index <= d2)
                    arr = source_df.loc[mask, VARIABLE].to_numpy(dtype=float)
                    if len(arr) > 0:
                        parts.append(arr)
                except Exception:
                    pass  # e.g. feb-29 en año no bisiesto

            return np.concatenate(parts) if parts else np.array([])

        def build_r95p(source_df, years_range_func):
            """
    Construye la lista r95p igual que el original:
    itera m=1..12, d=1..32, solo añade entrada cuando d existe como día húmedo.
    years_range_func(source_df) → el rango de años para el loop.
    """
            r95p_list = []
            first = source_df.index.year.unique()[0]
            last  = source_df.index.year.unique()[-1]

            for m in range(1, 13):
                df_month = source_df[source_df.index.month == m]
                for d in range(1, 32):
                    if d not in df_month.index.day:
                        continue

                    if m == 2 and d == 29:
                # Caso feb-29: loop while t < last_base desde primer bisiesto
                # → reproducimos con la lista de años bisiestos en [first, last)
                        leap_years = [y for y in range(first, last) if isleap(y)]
                        vals = window_values_with_initial(source_df, m, d, leap_years[1:] if leap_years else [])
                # El original comienza con t=primer_bisiesto y hace t+=4 mientras t<1990
                # → lo reproducimos con los bisiestos a partir del segundo
                    elif m == 12 and d in [30, 31]:
                        yr_range = range(first + 1, last + 1)
                        vals = window_values_with_initial(source_df, m, d, yr_range)
                    elif m == 1 and d in [1, 2]:
                        yr_range = range(first, last)
                        vals = window_values_with_initial(source_df, m, d, yr_range)
                    else:
                        yr_range = range(first, last)   # ← EXCLUYE last, igual que el original
                        vals = window_values_with_initial(source_df, m, d, yr_range)

                    if len(vals) > 0:
                        r95p_list.append(float(np.percentile(vals, PERCENTILE)))

            return r95p_list


# ─────────────────────────────────────────────────────────────────────────────
# 3. Percentil de referencia (para años fuera del período base)
# ─────────────────────────────────────────────────────────────────────────────
  #      print("Calculando el percentil de referencia del período base...")
        r95p = build_r95p(bp, None)
  #      print(f"  → {len(r95p)} entradas en r95p")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Helper: calcular R95p de un año dado r95p como lista
#    Reproduce exactamente el original: itera días húmedos, compara con r95p[doy-1]
# ─────────────────────────────────────────────────────────────────────────────
        def calc_r95p_year(df_year, pct_list, is_leap):
            pct_use = pct_list if is_leap else (pct_list[:59] + pct_list[60:])
            count = 0.0
            for ts in df_year.index:
                doy = ts.dayofyear
                val = float(df_year.loc[ts, VARIABLE])
                idx = doy - 1
            if idx < len(pct_use) and val > pct_use[idx]:
                count += val
            return count

# ─────────────────────────────────────────────────────────────────────────────
# 5. Índice para años fuera del período base
# ─────────────────────────────────────────────────────────────────────────────
        df_out   = pd.concat([df_wet[df_wet.index.year < base_inicio],
                      df_wet[df_wet.index.year > base_fin]])
        out_years, out_values = [], []

 #       print(f"Calculando R95p para {len(df_out.index.year.unique())} años fuera del período base...")
        for yr in sorted(df_out.index.year.unique()):
            yr_data = df_out[df_out.index.year == yr]
            out_values.append(calc_r95p_year(yr_data, r95p, leap_year(yr) == "True"))
            out_years.append(yr)

        df_output_out = pd.DataFrame({"Date": out_years, "R95p (mm)": out_values})

# ─────────────────────────────────────────────────────────────────────────────
# 6. Bootstrap para años del período base
#    Reproduce exactamente el original: para cada año o, itera sobre los 29
#    años restantes, construye df_bootstrap = año_p duplicado + boot (29 años),
#    calcula r95p_bootstrap con build_r95p, evalúa el año o y promedia.
# ─────────────────────────────────────────────────────────────────────────────
        base_year_lst, index_base_list = [], []
        bp_years = sorted(bp.index.year.unique())

#print(f"Bootstrap para {len(bp_years)} años del período base...")
        for idx_o, o in enumerate(bp_years):
            df_boot    = bp[bp.index.year != o]
            iter_years = sorted(df_boot.index.year.unique())   # 29 años
            index_lst  = []

            for p in iter_years:
        # df_bootstrap = año p + los 29 restantes (30 años total, con p duplicado)
                df_bootstrap = pd.concat([df_boot[df_boot.index.year == p], df_boot])
                df_bootstrap = df_bootstrap.sort_index()

                r95p_bootstrap = build_r95p(df_bootstrap, None)

                df_o    = bp[bp.index.year == o]
                counter = calc_r95p_year(df_o, r95p_bootstrap, leap_year(o) == "True")
                index_lst.append(counter)

            base_year_lst.append(o)
            index_base_list.append(float(np.mean(index_lst)))
 #   print(f"  [{idx_o+1:2d}/{len(bp_years)}] Año {o} → R95p = {index_base_list[-1]:.2f} mm")

        df_output_base = pd.DataFrame({"Date": base_year_lst, "R95p (mm)": index_base_list})

# ─────────────────────────────────────────────────────────────────────────────
# 7. Unir y exportar
# ─────────────────────────────────────────────────────────────────────────────
        df_output = (pd.concat([df_output_base, df_output_out])
               .sort_values(by="Date")
               .reset_index(drop=True))

        df_output.to_excel(archivo_salida, index=False)
        
        print("**************************")   
        print(f"\n✅ Índice R95p ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")   



    def r99p(archivo_entrada:str, archivo_salida:str, base_inicio: int, base_fin: int):
        """
        Índice climático: R99p [Precipitación total anual (PRCP) cuando PR > percentil 99]
        Definición:  Sea PRwj la cantidad de precipitación diaria en un día lluvioso
             w (PR ≥ 1,0 mm) en el período i y sea PRwn99 el percentil 99 de la precipitación en días lluviosos
             en el período de referencia.
                             Periodo base actual: 1991-2020
                             Periodos anteriores: 1981-2010
                                                  1961-1990
    
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


        VARIABLE   = 'PR'
        PERCENTILE = 99
        WET_THRESH = 1.0

        def leap_year(y):
            return "True" if isleap(y) else "False"

# ─────────────────────────────────────────────────────────────────────────────
# 1. Carga y preparación
# ─────────────────────────────────────────────────────────────────────────────
        df = pd.read_csv(archivo_entrada, sep=r'\s+')
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        df = df.set_index('Date').sort_index()

        df_wet = df[df[VARIABLE] >= WET_THRESH][[VARIABLE]].copy()
        bp     = df_wet[(df_wet.index.year >= base_inicio) & (df_wet.index.year <= base_fin)].copy()

# ─────────────────────────────────────────────────────────────────────────────
        def window_values_with_initial(source_df, m, d, years_range):
            """
    Replica exactamente el patrón del original:
      1. Filtra source_df en [ancla-2, ancla+2] (ancla = primer (m,d) en source_df)
      2. Itera sobre years_range y concatena la ventana de cada año
    Devuelve array 1-D con todos los valores acumulados.
    """
            mask_md = (source_df.index.month == m) & (source_df.index.day == d)
            if not mask_md.any():
                return np.array([])

            anchor = source_df.index[mask_md][0]
            d1_init = anchor - pd.DateOffset(days=2)
            d2_init = anchor + pd.DateOffset(days=2)

    # Bloque inicial (ancla, primer año)
            mask_init = (source_df.index >= d1_init) & (source_df.index <= d2_init)
            parts = [source_df.loc[mask_init, VARIABLE].to_numpy(dtype=float)]

    # Loop sobre los años del rango
            for yr in years_range:
                try:
                    d1 = d1_init.replace(year=yr)
                    d2 = d1 + pd.DateOffset(days=4)
                    mask = (source_df.index >= d1) & (source_df.index <= d2)
                    arr = source_df.loc[mask, VARIABLE].to_numpy(dtype=float)
                    if len(arr) > 0:
                        parts.append(arr)
                except Exception:
                    pass  # e.g. feb-29 en año no bisiesto

            return np.concatenate(parts) if parts else np.array([])

        def build_r99p(source_df, years_range_func):
            """
    Construye la lista r99p igual que el original:
    itera m=1..12, d=1..32, solo añade entrada cuando d existe como día húmedo.
    years_range_func(source_df) → el rango de años para el loop.
    """
            r99p_list = []
            first = source_df.index.year.unique()[0]
            last  = source_df.index.year.unique()[-1]

            for m in range(1, 13):
                df_month = source_df[source_df.index.month == m]
                for d in range(1, 32):
                    if d not in df_month.index.day:
                        continue

                    if m == 2 and d == 29:
                # Caso feb-29: loop while t < last_base desde primer bisiesto
                # → reproducimos con la lista de años bisiestos en [first, last)
                        leap_years = [y for y in range(first, last) if isleap(y)]
                        vals = window_values_with_initial(source_df, m, d, leap_years[1:] if leap_years else [])
                # El original comienza con t=primer_bisiesto y hace t+=4 mientras t<1990
                # → lo reproducimos con los bisiestos a partir del segundo
                    elif m == 12 and d in [30, 31]:
                        yr_range = range(first + 1, last + 1)
                        vals = window_values_with_initial(source_df, m, d, yr_range)
                    elif m == 1 and d in [1, 2]:
                        yr_range = range(first, last)
                        vals = window_values_with_initial(source_df, m, d, yr_range)
                    else:
                        yr_range = range(first, last)   # ← EXCLUYE last, igual que el original
                        vals = window_values_with_initial(source_df, m, d, yr_range)

                    if len(vals) > 0:
                        r99p_list.append(float(np.percentile(vals, PERCENTILE)))

            return r99p_list


# ─────────────────────────────────────────────────────────────────────────────
# 3. Percentil de referencia (para años fuera del período base)
# ─────────────────────────────────────────────────────────────────────────────
 #       print("Calculando el percentil de referencia del período base...")
        r99p = build_r99p(bp, None)
#        print(f"  → {len(r99p)} entradas en r99p")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Helper: calcular r99p de un año dado r99p como lista
#    Reproduce exactamente el original: itera días húmedos, compara con r99p[doy-1]
# ─────────────────────────────────────────────────────────────────────────────
        def calc_r99p_year(df_year, pct_list, is_leap):
            pct_use = pct_list if is_leap else (pct_list[:59] + pct_list[60:])
            count = 0.0
            for ts in df_year.index:
                doy = ts.dayofyear
                val = float(df_year.loc[ts, VARIABLE])
                idx = doy - 1
                if idx < len(pct_use) and val > pct_use[idx]:
                    count += val
            return count

# ─────────────────────────────────────────────────────────────────────────────
# 5. Índice para años fuera del período base
# ─────────────────────────────────────────────────────────────────────────────
        df_out   = pd.concat([df_wet[df_wet.index.year < base_inicio],
                      df_wet[df_wet.index.year > base_fin]])
        out_years, out_values = [], []

 #       print(f"Calculando r99p para {len(df_out.index.year.unique())} años fuera del período base...")
        for yr in sorted(df_out.index.year.unique()):
            yr_data = df_out[df_out.index.year == yr]
            out_values.append(calc_r99p_year(yr_data, r99p, leap_year(yr) == "True"))
            out_years.append(yr)

        df_output_out = pd.DataFrame({"Date": out_years, "r99p (mm)": out_values})

# ─────────────────────────────────────────────────────────────────────────────
# 6. Bootstrap para años del período base
#    Reproduce exactamente el original: para cada año o, itera sobre los 29
#    años restantes, construye df_bootstrap = año_p duplicado + boot (29 años),
#    calcula r99p_bootstrap con build_r99p, evalúa el año o y promedia.
# ─────────────────────────────────────────────────────────────────────────────
        base_year_lst, index_base_list = [], []
        bp_years = sorted(bp.index.year.unique())

#print(f"Bootstrap para {len(bp_years)} años del período base...")
        for idx_o, o in enumerate(bp_years):
            df_boot    = bp[bp.index.year != o]
            iter_years = sorted(df_boot.index.year.unique())   # 29 años
            index_lst  = []

            for p in iter_years:
        # df_bootstrap = año p + los 29 restantes (30 años total, con p duplicado)
                df_bootstrap = pd.concat([df_boot[df_boot.index.year == p], df_boot])
                df_bootstrap = df_bootstrap.sort_index()

                r99p_bootstrap = build_r99p(df_bootstrap, None)

                df_o    = bp[bp.index.year == o]
                counter = calc_r99p_year(df_o, r99p_bootstrap, leap_year(o) == "True")
                index_lst.append(counter)

            base_year_lst.append(o)
            index_base_list.append(float(np.mean(index_lst)))
 #   print(f"  [{idx_o+1:2d}/{len(bp_years)}] Año {o} → r99p = {index_base_list[-1]:.2f} mm")

        df_output_base = pd.DataFrame({"Date": base_year_lst, "r99p (mm)": index_base_list})

# ─────────────────────────────────────────────────────────────────────────────
# 7. Unir y exportar
# ─────────────────────────────────────────────────────────────────────────────
        df_output = (pd.concat([df_output_base, df_output_out])
               .sort_values(by="Date")
               .reset_index(drop=True))

        df_output.to_excel(archivo_salida, index=False)
        
        print("**************************")   
        print(f"\n ✅ Índice R99p ejecutado exitosamente. Archivo guardado: {archivo_salida}")
        print("**************************")   
        

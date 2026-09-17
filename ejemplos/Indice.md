# Índices ETCCDI de Precipitación — 

Los índices ETCCDI (Equipo de Expertos en Detección e Índices de Cambio Climático) son un conjunto estandarizado de 27 métricas climáticas. De ellos, 11 están enfocados en la "precipitación" y permiten evaluar la frecuencia, intensidad y duración de eventos extremos (como sequías o lluvias torrenciales).

Estos índices se dividen en las siguientes categorías principales:

| Categoría | ID | Nombre | Definición | Unidades |
|-----------|----|--------|------------|----------|
|**Frecuencia**|**R10mm**| Número de días de precipitación intensa | Conteo anual o estacional cuando PR ≥ 10 mm/año | días |
|              |**R20mm**| Número de días de precipitación muy intensa | Conteo anual o estacional cuando con PR ≥ 20 mm/año | días |
|-----------|----|--------|------------|----------|
|**Absolutos**|**Rx1day**| Máx. precipitación en 1 día  | Precip. máxima mensual en 1 día | mm |
|             |**Rx5day**| Máx. precipitación en 5 días | Precip. máxima mensual en 5 días | mm |
|             |**SDII**| Índice de intensidad diaria simple | Precip. total / días húmedos | mm/día |
|             |**PRCPTOT**| Precipitación total anual en días húmedos | Precip. total anual de días húmedos (≥ 1 mm)  | mm |
|-----------|----|--------|------------|----------|
|**Duración**|**CDD**| Días secos consecutivos |     Máx. número de días consecutivos cuando PR < 1 mm | días |
|            |**CWD**| Días húmedos consecutivos  | Máx. número de días consecutivos cuando PR ≥ 1 mm | días |
|-----------|----|--------|------------|----------|
|**Percentiles**|**R95p**| Días muy húmedos | Precip. total anual o estacional acumulada en días > percentil 95 | mm |
|               |**R99p**| Días extremadamente húmedos | Precip. total anual o estacional acumulada en días > percentil 99 | mm |


Definiciones según [ETCCDI](http://etccdi.pacificclimate.org/list_27_indices.shtml)

<br><br>
<!--
Este notebook muestra cómo importar y usar las funciones del paquete .
-->

El paquete `ETCCDI_precipitacion` contiene **dos módulos principales**:

| Módulo | Función | Descripción |
|--------|-------|-------------|
| `Procesamiento` | `ETCCDI_precip_malla` | Índices sobre datos en malla NetCDF (usa CDO) |
|  | `ETCCDI_precip_in_situ` | Índices sobre datos de estación (`.txt` → `.xlsx`) |
| `Graficamiento` | `ETCCDI_precip_plot_in_situ` | Gráficas de series temporales con tendencia (in situ) |
|  | `ETCCDI_precip_plot_malla` | Mapas de índices y tendencias (NetCDF) |

---
**Kernel recomendado:** `ETCCDI_precipitacion`
    
<br><br>
# Datos

Para los ejemplos de procesamiento y graficamiento. 

<!-- Los datos se pueden descargar de [Google Drive](https://drive.google.com/drive/folders/1zQotdaKFL3T5ik-g8XgVgNiNfvbWxYvJ?usp=drive_link)-->

<br><br>
# Procesamiento de datos -
    
## Malla
- Frecuencia <!--[Ejemplos](Indices_frecuencia_malla.ipynb)-->
- Absolutos 
- Duración <!--[Ejemplos](Indices_duracion_malla.ipynb) -->
- Percentiles <!--[Ejemplos](Indices_percentiles_malla.ipynb) -->

  
## In Situ
- Frecuencia <!--[Ejemplos](Indices_frecuencia_in_situ.ipynb) -->
- Duración <!--[Ejemplos](Indices_duracion_in_situ.ipynb) -->
- Absolutos
- Percentiles <!--[Ejemplos](Indices_percentiles_in_situ.ipynb) -->


<br><br>
# Graficamiento de datos -
 Malla
- Frecuencia <!--[Ejemplos](Indices_frecuencia_ploteo_malla.ipynb) -->
- Absolutos
- Duración <!--[Ejemplos](Indices_Duracion_ploteo_malla.ipynb) --> 
- Percentiles <!--[Ejemplos](Indices_percentiles_ploteo_malla.ipynb) -->
      
# In Situ
- Frecuencia <!--[Ejemplos](Indices_frecuencia_ploteo_in_situ.ipynb) -->
- Absolutos
- Duración <!--[Ejemplos](Indices_duracion_ploteo_in_situ.ipynb) -->
- Percentiles <!--[Ejemplos](Indices_percentiles_ploteo_in_situ.ipynb) -->



<br><br>
<!--# Replicar cuadernos de Jupyter de los ejemplos -

[Pasos](Pasos_replicar_ejemplos.md) -->

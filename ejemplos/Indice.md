# Índices ETCCDI de Precipitación — 

Los índices ETCCDI (Equipo de Expertos en Detección e Índices de Cambio Climático) son un conjunto estandarizado de 27 métricas climáticas. De ellos, 11 están enfocados en la "precipitación" y permiten evaluar la frecuencia, intensidad y duración de eventos extremos (como sequías o lluvias torrenciales).

Estos índices se dividen en las siguientes categorías principales:

| Categoría | ID | Nombre | Definición | Unidades |
|-----------|----|--------|------------|----------|
|**Umbral o Frecuencia**|**R10mm**| Número de días de precipitación intensa | Conteo anual o estacional cuando PR ≥ 10 mm/año | días |
|              |**R20mm**| Número de días de precipitación muy intensa | Conteo anual o estacional cuando con PR ≥ 20 mm/año | días |
|-----------|----|--------|------------|----------|
|**Absolutos**|**RX1day**| Máx. precipitación en 1 día  | Precip. máxima mensual en 1 día | mm |
|             |**RX5day**| Máx. precipitación en 5 días | Precip. máxima mensual en 5 días | mm |
|-----------|----|--------|------------|----------|
|**Básicos**|**SDII**| Índice de intensidad diaria simple | Precip. total / días húmedos | mm/día |
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

Para los ejemplos de procesamiento. 

Los datos se pueden descargar de [Google Drive](https://drive.google.com/drive/folders/1wbFDAn4ynhvvTR0ZgC6kDK7mfvIKsHIN?usp=drive_link)

<br><br>
# Procesamiento de datos -
    
## Malla
- Frecuencia [Ejemplos](Indices_Frecuencia_Malla.ipynb)
- Absolutos [Ejemplos](Indices_Absolutos_Malla.ipynb)
- Duración [Ejemplos](Indices_Duracion_Malla.ipynb)
- Básicos  [Ejemplos](Indices_Basicos_Malla.ipynb)
- Percentiles [Ejemplos](Indices_Percentiles_Malla.ipynb)

  
## In Situ
- Frecuencia [Ejemplos](Indices_Frecuencia_In_Situ.ipynb)
- Duración [Ejemplos](Indices_Duracion_In_Situ.ipynb)
- Absolutos [Ejemplos](Indices_Absolutos_In_Situ.ipynb)
- Básicos   [Ejemplos](Indices_Basicos_In_Situ.ipynb)
- Percentiles [Ejemplos](Indices_Percentiles_In_Situ.ipynb)


<br><br>
# Graficamiento de datos -
 Malla
- Frecuencia [Ejemplos](Indices_Frecuencia_Malla_Plot.ipynb)
- Absolutos [Ejemplos](Indices_Absolutos_Malla_Plot.ipynb)
- Duración [Ejemplos](Indices_Duracion_Malla_Plot.ipynb)
- Básicos [Ejemplos](Indices_Basicos_Malla_Plot.ipynb)
- Percentiles [Ejemplos](Indices_Percentiles_Malla_Ploteo.ipynb)
      
# In Situ
- Frecuencia [Ejemplos](Indices_frecuencia_In_Situ_Plot.ipynb)
- Absolutos [Ejemplos](Indices_Absolutos_In_Situ_Plot.ipynb)
- Duración [Ejemplos](Indices_Duracion_In_Situ_Plot.ipynb)
- Básicos [Ejemplos](Indices_Basicos_In_Situ_Plot.ipynb)
- Percentiles [Ejemplos](Indices_percentiles_In_Situ_Plot.ipynb)



<br><br>
<!--# Replicar cuadernos de Jupyter de los ejemplos -

[Pasos](Pasos_replicar_ejemplos.md) -->

# xlseries-condatos2015
Material para el taller de extracción de series de tiempo de archivos excel con `xlseries`.

## Preparar el entorno de trabajo

```python
# crear el entorno virtual
virtualenv xlseries

# activarlo
source xlseries/bin/activate

# instalar las dependencias de este workshop
pip install -r requirements.txt
```

Alternativamente, para aquellos que usen Anaconda como instalación de python

```python
# crear el entorno virtual
conda create -n xlseries

# activarlo
source activate xlseries  # en Windows sólo `activate xlseries`

# instalar las dependencias de este workshop
pip install -r requirements.txt
```

## Partes del repositorio

1. Ejemplos de uso de xlseries [1-explorar_ejemplos.ipynb](1-explorar_ejemplos.ipynb.ipynb)
    * Aprender a usar [xlseries](https://github.com/abenassi/xlseries)
    * Comenzar a usar `DataFrame` de [pandas](http://pandas.pydata.org/index.html)
2. Base de datos actualizable de series de tiempo [2-construir_base.ipynb](2-construir_base.ipynb.ipynb)
    * Se usan los métodos del módulo [build_database.py](build_database.py)
    * Ver una posible estructura sencilla para compilar una base de datos de series de tiempo
    * Utilizar [dataset](https://dataset.readthedocs.org/en/latest/) como una forma rápida y fácil de crear una base de datos
3. Crawler para scrapear todos los archivos excel de un sitio web [3-scrapear_links.ipynb](3-scrapear_links.ipynb)
    * Se usan los métodos del módulo [xl_links_scraper.py](xl_links_scraper.py)
    * Descargar y almacenar todos los arcivos excel de un sitio web

*`utils.py` reúne algunos métodos auxiliares en un módulo aparte para focalizar la atención en lo más importante*

## ¿Por qué este taller? (contexto del problema)

Investigadores, estudiantes, consultores y activistas civiles que utilizan datos públicos pierden mucho tiempo en la búsqueda, la descarga, el análisis, la transformación, la comparación, la estructuración y, en última instancia, la actualización de los datos que necesitan utilizar en su trabajo. 

El proceso puede ser tan demandante de tiempo/esfuerzo que disminuye notoriamente la capacidad de un equipo o un individuo de llevar adelate el verdadero trabajo de análisis con los datos. 

Como consecuencia, la calidad y alcance del trabajo con datos se resiente: 

* Datos valiosos no se utilizan por falta de recursos para procesarlos
* Se cometen errores evitables
* Existe duplicidad de trabajo entre personas, equipos y organizaciones diferentes que realizan regularmente las mismas tareas de limpieza con los mismos datos
* La historia de las reestimaciones de las series de tiempo se pierde muy a menudo y demanda demasiado esfuerzo recuperarla
* Datos similares no se comparan
* Y por último, el verdadero análisis se realiza con menos tiempo, paciencia y recursos de los que debería hacerse

Una herramienta como [xlseries](https://github.com/abenassi/xlseries) apunta a automatizar el proceso de limpieza y estructuración de series de tiempo publicadas en archivos excel organizados de las maneras más diversas e incluso con errores humanos.

### Organismos internacionales

Existen varios organismos públicos (en general, organismos internacionales) que hacen un gran trabajo en este campo centralizando la publicación de series de tiempo de muchos países, pero muy a menudo estas fuentes no son lo suficientemente buenas para los investigadores que trabajan en problemáticas específicas de países en vías de desarrollo debido a varios problemas:

* Los datos de países en vías de desarrollo son con frecuencia escasos, incompletos o dudosos tal como están publicados en estos grandes organismos recopiladores de datos. Estos suelen ser mejores fuentes de datos para países desarrollados.
* Los organismos internacionales generalmente no utilizan una gran cantidad de datos valiosos procedentes de fuentes no oficiales que son clave para los investigadores.
* Los organismos internacionales deben tomar decisiones sobre los datos para presentar un producto final consistente y homogéneo. De esta manera, muchas comparaciones, análisis y consideraciones específicas de cierta problemática o investigador, no se pueden hacer si se proporciona una sola versión de una serie de tiempo.
* Los organismos internacionales suelen tener el objetivo de lograr la comparabilidad internacional en su actividad de recolección de datos, lo que hace que puedan tomar decisiones metodológicas no tan pertinentes para investigadores en temáticas nacionales.

Algunas de las mejores instituciones que recopilan y organizan datos son:

* FRED (Datos Económicos de la Reserva Federal): Ofrece un complemento para Excel, búsqueda web y toda la base de datos descargable.
* Banco Mundial: Ofrece una API, una librería en python, una librería en stata, búsqueda web y toda la base de datos descargable.
* OCDE: Ofrece una API y búsqueda web.

### Problemas frecuentes que se encuentran en datos de países en vías de desarrollo (y en otros también)

* Normalmente, los datos están disponibles en formato excel. No hay APIs estructuradas para acceder a los datos programáticamente.
* Los diseños de publicación en Excel pueden ser muy diferentes, incluso entre publicaciones de una misma fuente, y con frecuencia complicados de analizar programáticamente.
* Series de tiempo similares de diferentes oficinas públicas muestran diferentes números.
* Los datos se muestran en una o más transformaciones decididas de antemano, generalmente no se ofrecen herramientas para adquirir los datos con una determina transformación elegida.
* Los datos cambian significativamente en el tiempo debido a re-estimaciones y no existe un registro de estos cambios. Una vez que se hacen, los datos originales se pierden o es complicado recuperarlos y utilizarlos.
* La actualización de datos utilizados previamente requiere repetir la descarga y el proceso de datos, lo que implica casi duplicar el trabajo previo de limpieza realizado originalmente.
* Las series de datos pueden tener varios errores de tipeo cuando el mecanismo de generación y publicación de los excels no es automático.

### ¿Qué es xlseries?

El paquete [xlseries](https://github.com/abenassi/xlseries) realiza un análisis de los archivos excel a partir de algunos parámetros ingresados por el usuario para extraer series de tiempo y convertirlas al formato [pandas.DataFrame](http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.html). 

Una vez que las series de datos están disponibles en este formato es muy sencillo convertirla a otros formatos como CSV, Excel (devolviendo una tabla propiamente estrucurada), diccionario de python, html, json, latex, stata y muchos otros más, o desarrollar aplicaciones en python que los utilicen para actualizar bases de datos. 

El análisis de datos también puede realizarse directamente en python. La librería [pandas](http://pandas.pydata.org/pandas-docs/dev/index.html) es una excelente herramienta para realizar todo tipo de análisis de datos.

Cualquier usuario intensivo de series de tiempo publicadas en excel (tanto individual como institucional) puede incrementar significativamente la potencia y el alcance de sus actividades automatizando buena parte de las tareas de limpieza, estructuración y actualización de sus bases de datos.

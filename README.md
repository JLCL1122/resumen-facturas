# Analizador de CFDI XML (México)

Script en Python para analizar facturas **CFDI 4.0** en formato XML y generar un reporte en Excel con **ingresos, egresos, IVA y complementos de pago**.

---

## 🚀 Características

* Lee múltiples archivos XML de CFDI
* Soporte para CFDI 4.0
* Clasifica **ingresos y egresos** según el RFC
* Calcula **IVA**
* Maneja **complementos de pago** (CFDI tipo P)
* Genera un **reporte en Excel** con:

  * Detalle de facturas
  * Pagos relacionados
  * Resumen mensual

---

## 📂 Estructura del proyecto

```
cfdi-xml-analyzer/
├─ main.py
├─ requirements.txt
├─ .gitignore
├─ facturas_xml/
└─ output/
```

---

## ⚙️ Requisitos

* Python 3.9 o superior
* pandas
* openpyxl

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

---

## ▶️ Uso

1. Coloca los archivos XML dentro de la carpeta `facturas_xml/`
2. Define tu RFC como variable de entorno:

**Linux / Mac:**

```bash
export MI_RFC=TU_RFC_AQUI
```

**Windows (CMD):**

```cmd
set MI_RFC=TU_RFC_AQUI
```

3. Ejecuta el script:

```bash
python main.py
```

---

## 📊 Salida

El script genera un archivo Excel con el nombre:

```
resumen_YYYY-MM.xlsx
```

El archivo contiene:

* **Detalle Facturas**: información de cada CFDI
* **Pagos**: relación de complementos de pago
* **Resumen**: ingresos, egresos, balance e IVA

---

## 🛡️ Buenas prácticas

* No subas XML reales con información sensible
* Usa variables de entorno para datos como el RFC
* Revisa el archivo `.gitignore` antes de hacer commit

---

## 🛣️ Mejoras futuras

* Validación con el SAT
* Selección automática de periodo
* Dashboard de visualización
* Análisis con inteligencia artificial

---

📌 Proyecto creado como parte de un portafolio de automatización en Python.
# 📊 Analizador de CFDI XML (México)

Script en Python para analizar facturas **CFDI 4.0** en formato XML y generar un **reporte automático en Excel**
con **ingresos, egresos, IVA y complementos de pago**, orientado a automatización contable y financiera.

---

## 🚀 Características

- Lectura de múltiples archivos XML de CFDI
- Soporte para **CFDI 4.0**
- Clasificación automática de **ingresos y egresos** según el RFC configurado
- Cálculo de **IVA** por periodo
- Manejo de **complementos de pago (CFDI tipo P)**
- Relación de pagos con sus facturas originales
- Generación de un reporte en Excel con:
  - Detalle de facturas
  - Pagos relacionados
  - Resumen mensual

---

## 📂 Estructura del proyecto

```text
cfdi-xml-analyzer/
├── main.py
├── requirements.txt
├── .gitignore
├── src/
│   ├── config.py
│   └── cfdi_parser.py
└── README.md
⚠️ La carpeta facturas_xml/ se usa localmente para colocar los CFDI y está excluida del repositorio por seguridad.

⚙️ Requisitos
Python 3.9 o superior

Dependencias:

pandas

openpyxl

Instalación de dependencias:
  pip install -r requirements.txt

▶️ Uso
Crear una carpeta llamada facturas_xml en la raíz del proyecto

Colocar dentro los archivos XML de las facturas CFDI

Definir el RFC como variable de entorno:

Linux / macOS
  export MI_RFC=TU_RFC_AQUI

Windows (CMD / PowerShell)
  set MI_RFC=TU_RFC_AQUI

Ejecutar el script:
  python main.py

📊 Salida
El script genera automáticamente un archivo Excel con el nombre:
  resumen_YYYY-MM.xlsx

El archivo contiene:

Detalle Facturas: información completa de cada CFDI

Pagos: relación de complementos de pago (CFDI tipo P)

Resumen: ingresos, egresos, balance e IVA del periodo

🛡️ Buenas prácticas
No subir XML reales con información sensible al repositorio

Utilizar variables de entorno para datos críticos como el RFC

Mantener actualizado el archivo .gitignore

Ejecutar el script en un entorno virtual cuando sea posible

🛣️ Mejoras futuras
Validación de CFDI contra el SAT

Selección automática de periodo y rangos de fechas

Dashboard de visualización financiera

Análisis de facturación con inteligencia artificial

Integración con sistemas contables o mensajería (WhatsApp / Telegram)

📌 Autor
Proyecto desarrollado por Jorge Castro
Como parte de un portafolio de automatización de procesos en Python, enfocado en soluciones contables y financieras.
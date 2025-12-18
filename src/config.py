import os
from datetime import datetime

# Ruta base del proyecto (resumen-facturas/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carpeta donde están los XML
FACTURAS_FOLDER = os.path.join(BASE_DIR, "facturas_xml")

# RFC propio
MI_RFC = os.getenv("MI_RFC", "TU_RFC_AQUI")

# Periodo actual YYYY-MM
PERIODO = datetime.today().strftime("%Y-%m")
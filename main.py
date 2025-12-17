import pandas as pd
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# 🟢 Configuración
facturas_folder = "facturas_xml/"
MI_RFC = os.getenv("MI_RFC", "TU_RFC_AQUI") # Reemplaza con tu RFC o usa variable de entorno
PERIODO = datetime.today().strftime("%Y-%m")  # Año-mes actual

def to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0

def get_namespaces(root):
    if root.tag.startswith("{"):
        uri = root.tag[1:].split("}", 1)[0]
    else:
        uri = "http://www.sat.gob.mx/cfd/4"
    return {"cfdi": uri, "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"}

def parse_cfdi(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = get_namespaces(root)

    # 🟢 Fecha en DD/MM/YYYY
    fecha_raw = root.attrib.get("Fecha")
    fecha = ""
    if fecha_raw:
        try:
            fecha_obj = datetime.fromisoformat(fecha_raw.replace("T", " "))
            fecha = fecha_obj.strftime("%d/%m/%Y")
        except ValueError:
            fecha = fecha_raw

    tipo_cfdi = root.attrib.get("TipoDeComprobante")
    subtotal = to_float(root.attrib.get("SubTotal"))

    # Método de pago, Serie y Folio
    metodo_pago = root.attrib.get("MetodoPago", "")
    serie = root.attrib.get("Serie", "")
    folio = root.attrib.get("Folio", "")

    # Emisor/Receptor
    emisor = root.find("cfdi:Emisor", ns)
    receptor = root.find("cfdi:Receptor", ns)
    emisor_rfc = emisor.attrib.get("Rfc") if emisor is not None else ""
    receptor_rfc = receptor.attrib.get("Rfc") if receptor is not None else ""

    # UUID
    uuid = ""
    tfd = root.find(".//tfd:TimbreFiscalDigital", ns)
    if tfd is not None:
        uuid = tfd.attrib.get("UUID", "")

    # 🟢 Complemento de pagos: facturas relacionadas y suma de pagos (solo tipo P)
    facturas_relacionadas = []
    subtotal_pago = 0.0

    if tipo_cfdi == "P":
        complemento = root.find("cfdi:Complemento", ns)
        if complemento is not None:
            pagos_ns = {"pago10": "http://www.sat.gob.mx/Pagos20"}
            for pago in complemento.findall(".//pago10:Pago", pagos_ns):
                importe_pago = to_float(pago.attrib.get("Monto", 0.0))
                subtotal_pago += importe_pago
                for doc in pago.findall("pago10:DoctoRelacionado", pagos_ns):
                    facturas_relacionadas.append({
                        "uuid": doc.attrib.get("IdDocumento", ""),
                        "serie": doc.attrib.get("Serie", ""),
                        "folio": doc.attrib.get("Folio", "")
                    })

    # 🟢 Ajuste para CFDI tipo P
    if tipo_cfdi == "P" and subtotal_pago > 0:
        subtotal = subtotal_pago / 1.16  # antes de IVA
        iva = subtotal * 0.16
        total = subtotal + iva
    else:
        iva = subtotal * 0.16
        total = subtotal + iva

    # 🟢 Clasificación con MI_RFC
    if emisor_rfc == MI_RFC:
        tipo_label = "ingreso"
        monto = subtotal
        if tipo_cfdi == "E":  # Nota de crédito
            monto = -subtotal
            iva = -iva
            total = -(subtotal + iva)
    elif receptor_rfc == MI_RFC:
        tipo_label = "egreso"
        monto = subtotal
    else:
        tipo_label = "otro"
        monto = subtotal

    return {
        "uuid": uuid,
        "fecha": fecha,
        "tipo_cfdi": tipo_cfdi,
        "tipo": tipo_label,
        "emisor_rfc": emisor_rfc,
        "receptor_rfc": receptor_rfc,
        "subtotal": subtotal,
        "iva": iva,
        "total": total,
        "metodo_pago": metodo_pago,
        "serie": serie,
        "folio": folio,
        "facturas_relacionadas_obj": facturas_relacionadas  # lista de objetos
    }

# 🟢 Leer XML
rows = []
errores = []
for fname in os.listdir(facturas_folder):
    if fname.lower().endswith(".xml"):
        path = os.path.join(facturas_folder, fname)
        try:
            data = parse_cfdi(path)
            fecha_obj = datetime.strptime(data["fecha"], "%d/%m/%Y")
            if fecha_obj.strftime("%Y-%m") == PERIODO:
                rows.append(data)
        except Exception as e:
            errores.append(f"{fname}: {e}")

if errores:
    print("⚠️ Algunos archivos no se pudieron procesar:")
    for err in errores:
        print(err)

# 🟢 DataFrame completo
facturas = pd.DataFrame(rows)
if facturas.empty:
    raise FileNotFoundError(f"No se encontraron facturas para {PERIODO}.")

# 🟢 Totales
ingresos = facturas.loc[facturas["tipo"] == "ingreso", "subtotal"].sum()
egresos = facturas.loc[facturas["tipo"] == "egreso", "subtotal"].sum()
iva_ingresos = facturas.loc[facturas["tipo"] == "ingreso", "iva"].sum()
iva_egresos = facturas.loc[facturas["tipo"] == "egreso", "iva"].sum()
balance = ingresos - egresos
iva_a_pagar = iva_ingresos - iva_egresos

# 🟢 Resumen
resumen = pd.DataFrame({
    "Periodo": [PERIODO],
    "Total Ingresos": [ingresos],
    "Total Egresos": [egresos],
    "Balance": [balance],
    "IVA Ingresos": [iva_ingresos],
    "IVA Egresos": [iva_egresos],
    "IVA a Pagar": [iva_a_pagar]
})

# 🟢 Crear DataFrame de pagos tipo P con referencia al XML origen
pagos_rows = []
for _, row in facturas.iterrows():
    if row["tipo_cfdi"] == "P" and row["facturas_relacionadas_obj"]:
        for f in row["facturas_relacionadas_obj"]:
            pagos_rows.append({
                "xml_uuid_pago": row["uuid"],
                "xml_serie_pago": row["serie"],
                "xml_folio_pago": row["folio"],
                "fecha": row["fecha"],
                "metodo_pago": row["metodo_pago"],
                "serie_factura": f["serie"],
                "folio_factura": f["folio"],
                "uuid_factura": f["uuid"]
            })

pagos_df = pd.DataFrame(pagos_rows)

# 🟢 Excel final
with pd.ExcelWriter(f"resumen_{PERIODO}.xlsx") as writer:
    facturas.drop(columns=["facturas_relacionadas_obj"]).to_excel(writer, sheet_name="Detalle Facturas", index=False)
    pagos_df.to_excel(writer, sheet_name="Pagos", index=False)
    resumen.to_excel(writer, sheet_name="Resumen", index=False)

print(f"Archivo 'resumen_{PERIODO}.xlsx' generado con éxito.")
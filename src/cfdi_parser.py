import os
import xml.etree.ElementTree as ET
from datetime import datetime

from src.config import FACTURAS_FOLDER, MI_RFC, PERIODO


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

    metodo_pago = root.attrib.get("MetodoPago", "")
    serie = root.attrib.get("Serie", "")
    folio = root.attrib.get("Folio", "")

    emisor = root.find("cfdi:Emisor", ns)
    receptor = root.find("cfdi:Receptor", ns)
    emisor_rfc = emisor.attrib.get("Rfc") if emisor is not None else ""
    receptor_rfc = receptor.attrib.get("Rfc") if receptor is not None else ""

    uuid = ""
    tfd = root.find(".//tfd:TimbreFiscalDigital", ns)
    if tfd is not None:
        uuid = tfd.attrib.get("UUID", "")

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

    if tipo_cfdi == "P" and subtotal_pago > 0:
        subtotal = subtotal_pago / 1.16
        iva = subtotal * 0.16
        total = subtotal + iva
    else:
        iva = subtotal * 0.16
        total = subtotal + iva

    if emisor_rfc == MI_RFC:
        tipo_label = "ingreso"
        if tipo_cfdi == "E":
            subtotal, iva, total = -subtotal, -iva, -total
    elif receptor_rfc == MI_RFC:
        tipo_label = "egreso"
    else:
        tipo_label = "otro"

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
        "facturas_relacionadas_obj": facturas_relacionadas
    }


def procesar_facturas():
    rows, errores = [], []

    for fname in os.listdir(FACTURAS_FOLDER):
        if fname.lower().endswith(".xml"):
            try:
                data = parse_cfdi(os.path.join(FACTURAS_FOLDER, fname))
                fecha_obj = datetime.strptime(data["fecha"], "%d/%m/%Y")
                if fecha_obj.strftime("%Y-%m") == PERIODO:
                    rows.append(data)
            except Exception as e:
                errores.append(f"{fname}: {e}")

    return rows, errores
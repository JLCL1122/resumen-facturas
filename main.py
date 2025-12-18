import pandas as pd
from src.cfdi_parser import procesar_facturas
from src.config import PERIODO


def main():
    rows, errores = procesar_facturas()

    if errores:
        print("⚠️ Errores al procesar algunos XML:")
        for e in errores:
            print(e)

    facturas = pd.DataFrame(rows)
    if facturas.empty:
        raise FileNotFoundError(f"No se encontraron facturas para {PERIODO}")

    ingresos = facturas.loc[facturas["tipo"] == "ingreso", "subtotal"].sum()
    egresos = facturas.loc[facturas["tipo"] == "egreso", "subtotal"].sum()
    iva_ingresos = facturas.loc[facturas["tipo"] == "ingreso", "iva"].sum()
    iva_egresos = facturas.loc[facturas["tipo"] == "egreso", "iva"].sum()

    resumen = pd.DataFrame({
        "Periodo": [PERIODO],
        "Total Ingresos": [ingresos],
        "Total Egresos": [egresos],
        "Balance": [ingresos - egresos],
        "IVA a Pagar": [iva_ingresos - iva_egresos]
    })

    with pd.ExcelWriter(f"resumen_{PERIODO}.xlsx") as writer:
        facturas.drop(columns=["facturas_relacionadas_obj"]).to_excel(
            writer, sheet_name="Detalle", index=False
        )
        resumen.to_excel(writer, sheet_name="Resumen", index=False)

    print("✅ Reporte generado correctamente")


if __name__ == "__main__":
    main()
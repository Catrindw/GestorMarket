# GM-03 — errores de lectura y cobertura
Estado: **PROBADO EN RAMA LOCAL**, sin publicación ni activación. Fecha: 2026-11-12.
Base PR2 bfc2f6c928de02f957c53d3fd37e18c912a806a8. El blob del parser ca208ec2acf647d535cd1c958dcb271b9ab975ec coincide con la instalación Ubuntu observada. No se rehace su diagnóstico.

Antes, si todas las consultas fallaban, el proceso devolvía éxito y podía decir que no había hallazgos. Se reproduce con dobles de red. La corrección cuenta perfiles/artículos leídos, informa revisión fallida o incompleta y retorna 1 ante errores de transporte. Conserva los hallazgos parciales disponibles. Una respuesta recibida cuenta como leída, no como HTML correctamente interpretado.

Validación: python -m unittest discover -s tests -v. **14 casos: 13 PASS y 1 fallo esperado**. Incluye moneda europea, texto de fila no interpretable como precio, país/cantidad, umbral relativo, profesionales, mínimo, error total/parcial/de artículo, cobertura y falta de configuración.
La primera ejecución de la suite inicial falló en 3 casos de errores/cobertura. Después pasan. La prueba del parser sigue explícitamente expectedFailure.

Todas las pruebas bloquean requests.Session.request y reemplazan lectura de páginas y configuración. Correos y webhooks fallarían si se intentasen. Solo example.invalid y datos sintéticos. Sin lectura de .env real, consultas Cardmarket, cron ni cambios de precios.

## Pendientes
GM-01 parser: falta HTML saneado y representativo de perfil/ofertas para fijar selectores separados de precio, cantidad, ventas, país, vendedor y condición profesional. La tabla sintética demuestra la carencia, no certifica el DOM del proveedor; no se han inventado selectores.
GM-02: decidir si 300 ventas significa umbral absoluto o 300 más que las propias. Se conserva la regla actual relativa; profesionales requieren superar las ventas propias.
GM-04: el cron existente apunta a /workspace/GestorMarket, ruta ausente en Ubuntu. No se ha modificado ni activado.
El resultado no permite afirmar que una página vacía de parsing no contiene ofertas. No es aprobación para producción. Reversión: no integrar esta rama; no hay estado real que recuperar.

## Publicación posterior — 12/11/2026
Rama publicada en [PR3 en borrador](https://github.com/Catrindw/GestorMarket/pull/3), incremental sobre PR2. El estado «sin publicación» anterior es histórico. Código y 14 pruebas intactos; [contrato mínimo pendiente y búsqueda realizada](CONTRATO_HTML_PENDIENTE.md). No se ha activado el monitor.

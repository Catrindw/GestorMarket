# Contrato HTML pendiente del parser

Actualización 14/11/2026: continúa el bloqueo por HTML representativo. La
[clasificación de cobertura](COBERTURA_OFFLINE_2026-11-14.md) evita ahora tratar
HTML desconocido como ausencia de ofertas. Resultado actual: 37 casos, 36 PASS y
1 fallo esperado del parser conservado. El resto de este documento describe la
evidencia y el cierre de la tanda anterior.

Estado: **BLOQUEADO POR EJEMPLO REPRESENTATIVO**, 12/11/2026. [PR3 en borrador](https://github.com/Catrindw/GestorMarket/pull/3), incremental sobre PR2. La corrección de errores/cobertura de 37a086b se conserva; el parser y su expectedFailure no se han modificado.

Se buscaron archivos HTML/HTM/HAR y fixtures en las copias de desarrollo, documentos y descargas locales pertinentes y en el proyecto Ubuntu y ubicaciones de análisis conocidas. No se encontró una captura saneada y utilizable que acreditase el DOM real. No se recorrieron sesiones de navegador ni se hizo una consulta a Cardmarket. La tabla sintética existente prueba el fallo al tratar una fila completa como precio y al mezclar sus cifras; no acredita clases o selectores del proveedor.

## Ejemplo mínimo que falta

Una muestra de perfil/stock y una página de ofertas, conservadas de una navegación autorizada, con el contenedor y los ancestros necesarios para seleccionar filas. Basta reemplazar nombres y enlaces de usuario por valores sintéticos; conservar etiquetas, atributos estructurales y distribución real:
- Perfil: dos artículos con nombre, enlace de producto, cantidad y precio separados; resultado esperado anotado.
- Ofertas: dos vendedores españoles, uno profesional y otro particular, con ventas, unidades y precio diferentes; incluir un vendedor de otro país como control.
- Casos representativos: separador decimal de coma, millares, espacios Unicode si existen y campo opcional ausente.
- Estado de lista vacía legítima y estado de acceso/login/bloqueo, para distinguir «cero ofertas» de «no interpretado».

Anotar fecha, tipo de página, idioma de interfaz y si el HTML es inicial o posterior a ejecución de JavaScript. Acompañar los valores esperados por fila. No aportar cookies, cabeceras Authorization, tokens CSRF, correos, direcciones, pedidos, datos de cuenta ni archivos HAR sin saneamiento. No se necesita una sesión utilizable.

Con ese contrato: extraer cada campo por separado, rechazar filas incompletas/ambiguas, validar contra fixture y añadir cobertura de página no interpretable. La prueba esperada solo pasará a ser una prueba normal cuando el defecto esté corregido conservando sus condiciones. No sustituirla por un fixture que copie selectores inventados.

## Estado y decisión de ventas

Validación conservada: 14 casos, 13 PASS y 1 expectedFailure. Red, correo y webhooks bloqueados por las pruebas. La cobertura cuenta respuestas recibidas, no certeza de parsing. No se puede interpretar una página vacía del parser como ausencia real de ofertas.

La implementación actual exige para particulares ventas >= nuestras ventas + 300. Un mínimo absoluto de 300 tendría un resultado distinto: con 100 ventas propias, un vendedor de 350 cumpliría el absoluto pero no el relativo (400). La elección sigue pendiente; la prueba solo protege el comportamiento vigente. La regla de profesionales (> ventas propias) también se conserva.

No se activó scraping, cron, correo, webhook ni modificación de precios. La programación existente no se reparó.


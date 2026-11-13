# Distinguir transporte, interpretación y lista vacía

Una respuesta HTTP correcta con HTML desconocido acababa como «sin hallazgos».
Ahora se cuentan por separado las páginas recibidas y las interpretadas. Una
página desconocida o parcial produce revisión incompleta y salida 2; no se
analizan precios ni se siguen artículos extraídos de un perfil sin acreditar.
Los errores de consulta conservan salida 1 y tienen prioridad si coinciden con
errores de interpretación. La salida 0 queda reservada a cobertura acreditada.

| Estado | Evidencia disponible | Consecuencia |
| --- | --- | --- |
| Consulta fallida | Excepción de transporte/HTTP | Salida 1; no equivale a vacío |
| UNKNOWN_HTML | Sin filas reconocidas y sin contrato revisado | Salida 2; no concluir ausencia |
| PARTIAL | Filas candidatas o extraídas, con cobertura/campos sin acreditar | Salida 2; no analizar esos precios |
| EMPTY_CONFIRMED | Contrato revisado vinculado a la respuesta, cero esperado y vacío explícito | Vacío acreditado, sin hallazgos |
| READY | Contrato revisado, campos y paginación acreditados, recuentos coincidentes | Puede analizarse la página |

**No existe todavía un adaptador revisado del HTML real.** `inspect_page` usa
los selectores que ya tenía el parser como diagnóstico y no entrega READY ni
EMPTY_CONFIRMED. El monitor real se detendrá en revisión incompleta aunque la
heurística extraiga alguna fila. Esto es intencionado mientras falte el contrato;
no es una versión lista para activar consultas o recomendaciones.

`ReviewedPageEvidence` permite probar la clasificación sin inventar el formato
del proveedor. Solo un futuro adaptador revisado podrá aportar esas afirmaciones.
El hash vincula las afirmaciones a una respuesta, pero no acredita por sí mismo
su significado. HTML, atributos, variables de entorno y mensajes como «No offers»
no pueden certificar una lista vacía. No se ha añadido un interruptor para omitir
esta comprobación.

## Validación offline

Base PR3: 14 casos, 13 PASS y 1 fallo esperado reproducido. Candidato: **37 casos,
36 PASS y 1 fallo esperado**. La prueba esperada del parser conserva sus mismas
aserciones: leer toda la fila como precio y mezclar ventas/unidades sigue siendo
un defecto. Las 23 pruebas nuevas cubren estados, filas perdidas, paginación sin
acreditar, evidencia de otra respuesta, vacío contradictorio y prevención de
consultas/análisis derivados de perfiles inciertos. Se actualizan dos expectativas
anteriores que confundían respuesta recibida con interpretación satisfactoria.

Ejecución Python 3.12 en Linux, con archivos de código/pruebas copiados a carpeta
aislada y SHA256 contrastados. Red real y notificaciones bloqueadas por dobles de
prueba; configuración sintética, sin lectura de .env real. No se han instalado
dependencias ni modificado el entorno del monitor. Windows no tenía `requests`
en el intérprete aislado y no se ha alterado ese entorno para esta validación.

## Bloqueo pendiente

La búsqueda acotada de HTML/HTM/HAR en el repositorio y proyecto Ubuntu no encontró
muestras. Se conserva la búsqueda previa de carpetas autorizadas y no se accedió
a cookies, perfiles de navegador o sesiones privadas. Las tablas sintéticas son
demostraciones semánticas, no capturas del proveedor.

Faltan muestras saneadas de stock, ofertas, lista realmente vacía, acceso fallido
y paginación, con valores esperados por fila. Deben conservar la estructura de
precio, vendedor, ventas, cantidad, país, profesional, idioma y estado cuando
esos campos estén presentes. El idioma/estado de la carta no se deduce del idioma
de la interfaz. El [contrato mínimo pendiente](CONTRATO_HTML_PENDIENTE.md) mantiene
las condiciones de saneamiento. No se decide el umbral absoluto/relativo de 300
ventas ni se activa scraping, correo, webhooks o tareas.

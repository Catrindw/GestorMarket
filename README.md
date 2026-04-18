# Gestor de precios Cardmarket

Automatización para revisar el stock público de Cardmarket (Yu-Gi-Oh y Pokémon), comparar precios con vendedores españoles relevantes y generar alertas.

## Qué hace

- Revisa tu stock público en:
  - `https://www.cardmarket.com/es/YuGiOh/Users/sakurakawaii-va`
  - `https://www.cardmarket.com/es/Pokemon/Users/sakurakawaii-va`
- Compara cada carta con vendedores de España que cumplan:
  - Misma cantidad o más unidades, y
  - Si son tienda: más ventas que nosotros.
  - Si no son tienda: al menos `+300` ventas sobre nosotros.
- Respeta precio mínimo de Cardmarket (`0,02€`):
  - No propone bajar de `0,02€`.
  - Si estamos en `0,02€`, solo alerta si hay oportunidad de subir precio.
- Permite ignorar cartas permanentemente mediante archivo local.
- Envía informe por consola y opcionalmente por correo.

## Estructura

- `src/cardmarket_monitor.py`: script principal.
- `.env.example`: variables de entorno de configuración.
- `ignored_cards.txt`: URLs de cartas que no se deben volver a revisar.
- `cron/cardmarket-monitor.cron`: ejemplo de programación en Linux.
- `scripts/run_monitor_linux.sh`: ejecución manual asistida en Ubuntu/Linux.
- `scripts/run_monitor_windows.ps1`: ejecución manual asistida en Windows.

---



## Ubuntu: prueba completa (copiar y pegar)

> Esta sección está pensada para hacerlo **sin conocimientos técnicos**.

### 1) Abrir Terminal

- En Ubuntu, pulsa la tecla **Super/Windows**, escribe `Terminal` y ábrela.

### 2) Entrar en la carpeta del proyecto

Copia y pega (ajusta la ruta si tu carpeta está en otro sitio):

```bash
cd /workspace/GestorMarket
```

Para confirmar que estás en el sitio correcto:

```bash
pwd
```

Deberías ver: `/workspace/GestorMarket`

### 3) Ejecutar todo automático (primera prueba)

Copia y pega:

```bash
bash scripts/run_monitor_linux.sh
```

Qué pasará automáticamente:
- Se crea el entorno Python (`.venv`) si no existe.
- Se instalan dependencias.
- Si no existe `.env`, se crea desde `.env.example`.
- Se lanza la revisión de precios.

### 4) Configurar tus datos (muy importante)

Abre el archivo de configuración:

```bash
nano .env
```

Busca y cambia como mínimo:

- `OUR_TOTAL_SALES=0`  → pon aquí tus ventas reales.
- Si quieres correo, cambia `EMAIL_ENABLED=false` a `EMAIL_ENABLED=true` y completa `SMTP_*`.

Guardar en `nano`:
- `Ctrl + O` (guardar), Enter para confirmar.
- `Ctrl + X` (salir).

### 5) Ejecutar otra vez ya con tu configuración

```bash
bash scripts/run_monitor_linux.sh
```

### 6) Si falla, copiar el error para revisarlo

Ejecuta en modo manual con más detalle:

```bash
source .venv/bin/activate
python src/cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt --verbose
```

### 7) Verificar rápidamente que "funciona"

Si todo va bien, verás alguno de estos resultados:
- `No se detectaron cartas con precio a corregir...`
- Un listado con cartas y recomendación de `bajar` o `subir`.

### 8) Programarlo a las 08:00 y 16:30 (cuando ya esté probado)

Instala la programación:

```bash
crontab cron/cardmarket-monitor.cron
```

Comprueba que quedó guardado:

```bash
crontab -l
```

### 9) Ver logs de ejecuciones automáticas

```bash
tail -n 100 logs/cardmarket-monitor.log
```

## Guía rápida para probar (sin experiencia técnica)

> Si no sabes por dónde empezar, sigue **exactamente** estos pasos.

### Opción A: Ubuntu / Linux

1. Abre una terminal en la carpeta del proyecto.
2. Ejecuta:

```bash
bash scripts/run_monitor_linux.sh
```

3. Si es la primera vez:
   - Se creará `.venv`.
   - Se instalarán dependencias.
   - Se copiará `.env` desde `.env.example`.
4. Edita el archivo `.env` y revisa mínimo:
   - `OUR_TOTAL_SALES` (ventas totales de tu cuenta).
   - `EMAIL_ENABLED=true` y SMTP si quieres correo.
5. Vuelve a ejecutar el mismo comando para lanzar la revisión real.

### Opción B: Windows (PowerShell)

1. Abre **PowerShell** dentro de la carpeta del proyecto.
2. Ejecuta:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_monitor_windows.ps1
```

3. Si es la primera vez:
   - Se creará `.venv`.
   - Se instalarán dependencias.
   - Se copiará `.env` desde `.env.example`.
4. Edita `.env` con tus datos (`OUR_TOTAL_SALES`, correo SMTP opcional).
5. Ejecuta otra vez el mismo comando para probar con tu configuración.

---

## Instalación manual (alternativa)

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 src/cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt --verbose
```

### Windows

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3 -m pip install -r requirements.txt
Copy-Item .env.example .env
py -3 src\cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt --verbose
```

---

## Programación automática dos veces al día

### Ubuntu/Linux con cron (08:00 y 16:30)

```bash
crontab cron/cardmarket-monitor.cron
```

Luego verifica:

```bash
crontab -l
```

### Windows con Programador de tareas

Crea **2 tareas** que llamen al script PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File C:\ruta\a\GestorMarket\scripts\run_monitor_windows.ps1
```

- Tarea 1: todos los días a las **08:00**.
- Tarea 2: todos los días a las **16:30**.

Consejo: marca “Ejecutar tanto si el usuario inició sesión como si no”.

---

## Ignorar una carta para siempre

Añade la URL del artículo a `ignored_cards.txt` (una por línea). El script no la volverá a incluir.

---

## Nota importante

Cardmarket puede cambiar estructura HTML o requerir anti-bot/cookies en ciertas páginas. El parser está diseñado para ser robusto y configurable, pero puede requerir ajustes de selectores si Cardmarket cambia el marcado.


## Prompt listo para Codex (Ubuntu, sin tocar nada manual)

Copia y pega este prompt en Codex para que te lo haga él solo en Ubuntu:

```text
Quiero que ejecutes TODO por mí en Ubuntu en este repositorio, paso a paso y sin preguntarme nada salvo que sea imprescindible.

Objetivo:
1) Preparar entorno Python.
2) Instalar dependencias.
3) Crear `.env` desde `.env.example` si no existe.
4) Enseñarme el `.env` y pedirme SOLO los datos mínimos que faltan (`OUR_TOTAL_SALES` y si quiero correo SMTP).
5) Ejecutar el monitor en modo verbose.
6) Confirmar si funcionó y mostrar resumen de resultados.
7) Programarlo con cron a las 08:00 y 16:30.
8) Verificar cron (`crontab -l`) y mostrar cómo ver logs (`tail -n 100 logs/cardmarket-monitor.log`).

Comandos que debes ejecutar tú (Codex) automáticamente:
- `cd /workspace/GestorMarket`
- `bash scripts/run_monitor_linux.sh`
- Si falta configuración: editar `.env` conmigo y volver a ejecutar `bash scripts/run_monitor_linux.sh`
- `source .venv/bin/activate && python src/cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt --verbose`
- `crontab cron/cardmarket-monitor.cron`
- `crontab -l`
- `tail -n 100 logs/cardmarket-monitor.log`

Quiero que al final me des:
- qué comandos corriste,
- cuáles pasaron/fallaron,
- y qué tengo que revisar si algo falla.
```

Consejo: si quieres, puedes cambiar solo la ruta `cd /workspace/GestorMarket` por la ruta real donde tengas el proyecto.

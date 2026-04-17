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

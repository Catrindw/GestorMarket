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
- `scripts/run_monitor_auto_linux.sh`: ejecución Linux con detección automática de ruta del repo.

---







## GitHub con “Continuar con Google” (sin contraseña de GitHub)

Si entraste con Google, es normal que **no tengas una contraseña de GitHub para usar en `git clone/push` por HTTPS**.

Tienes 2 opciones sencillas:

### Opción A (recomendada): autenticar con GitHub CLI en navegador

1) Instala GitHub CLI (si no lo tienes):

```bash
sudo apt update
sudo apt install -y gh
```

2) Inicia sesión con navegador:

```bash
gh auth login -h github.com -p https -w
```

3) Comprueba sesión:

```bash
gh auth status
```

4) Clona el repo:

```bash
git clone https://github.com/Catrindw/GestorMarket.git ~/proyectos/GestorMarket
```



### Si te aparece el código de un solo uso (ejemplo `46FC-7C0B`)

Cuando veas:

- `First copy your one-time code: XXXX-XXXX`
- `Press Enter to open github.com in your browser...`

haz esto exactamente:

1) Copia el código (por ejemplo `46FC-7C0B`).
2) Pulsa **Enter** en la terminal.
3) Se abrirá GitHub en el navegador.
4) Pega el código cuando GitHub te lo pida.
5) Autoriza `GitHub CLI`.
6) Vuelve a terminal y verifica:

```bash
gh auth status
```

Si `gh auth status` muestra tu usuario, ya está autenticado correctamente.



> **¿Dónde se pega el código?**
>
> No se pega en el Dashboard normal de GitHub. Se pega en la página de verificación de dispositivos:
>
> `https://github.com/login/device`
>
> Pasos rápidos:
> 1. En terminal, cuando salga `First copy your one-time code`, copia el código.
> 2. Pulsa Enter.
> 3. Si no te abre bien la página, entra manualmente a `https://github.com/login/device`.
> 4. Pega el código en el campo **Device code** y confirma.
> 5. Autoriza `GitHub CLI`.

### Opción B: usar token personal (PAT)

- En GitHub crea un token en: `Settings -> Developer settings -> Personal access tokens`.
- Cuando Git pida contraseña en terminal, pega el token (no tu contraseña de Google).

## Caso real: Ubuntu vacío (solo GitHub, sin nada local)

Si te sale este error:

```bash
bash: scripts/run_monitor_auto_linux.sh: No such file or directory
```

significa que **todavía no estás dentro del repositorio clonado** en tu PC.

### Opción recomendada (carpeta fuera de raíz)

Usaremos `~/proyectos/GestorMarket` (dentro de tu HOME, no en `/`).

1) Crea carpeta de trabajo:

```bash
mkdir -p ~/proyectos
cd ~/proyectos
```

2) Clona tu repo de GitHub:

```bash
git clone https://github.com/Catrindw/GestorMarket.git
```

3) Entra en el repo:

```bash
cd ~/proyectos/GestorMarket
```

4) Ahora sí ejecuta el automatismo:

```bash
bash scripts/run_monitor_auto_linux.sh
```

---



## Si clona bien pero no existe `scripts/run_monitor_auto_linux.sh`

Esto suele pasar cuando el repo local está en un commit/rama antigua.

Ejecuta estos comandos dentro de `~/proyectos/GestorMarket`:

```bash
cd ~/proyectos/GestorMarket
git remote -v
git branch -a
git pull --all --prune
ls -la
ls -la scripts
```

Si `scripts/run_monitor_auto_linux.sh` sigue sin aparecer, puedes probar igualmente **sin script**:

```bash
cd ~/proyectos/GestorMarket
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python src/cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt --verbose
```

Con eso confirmamos que el monitor funciona aunque no esté el helper script.

## Ubuntu: prueba completa (copiar y pegar)

> Esta sección está pensada para hacerlo **sin conocimientos técnicos**.

### 1) Abrir Terminal

- En Ubuntu, pulsa la tecla **Super/Windows**, escribe `Terminal` y ábrela.

### 2) Entrar en la carpeta del proyecto

Copia y pega (ajusta la ruta si tu carpeta está en otro sitio):

```bash
cd ~/proyectos/GestorMarket
```

Para confirmar que estás en el sitio correcto:

```bash
pwd
```

Deberías ver: `.../proyectos/GestorMarket`

### 3) Ejecutar todo automático (primera prueba)

Copia y pega:

```bash
bash scripts/run_monitor_linux.sh
```

Si no estás seguro de la ruta real del proyecto, usa este comando (autodetecta el repo):

```bash
bash scripts/run_monitor_auto_linux.sh
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

Copia y pega este prompt en Codex para que lo haga él solo, incluso si la ruta `/workspace/GestorMarket` no existe:

```text
Quiero que ejecutes TODO por mí en Ubuntu en este repositorio, paso a paso y sin pedirme la ruta del proyecto salvo que no haya forma automática de detectarla.

Objetivo:
1) Si no existe repo local, crear `~/proyectos`, clonar ahí el repo y entrar en `~/proyectos/GestorMarket`.
2) Detectar automáticamente la ruta del repo (buscar `src/cardmarket_monitor.py` en rutas típicas como `$PWD`, `$HOME`, `/workspace`, `/opt`).
3) Preparar entorno Python.
4) Instalar dependencias.
5) Crear `.env` desde `.env.example` si no existe.
6) Pedirme SOLO los datos mínimos que faltan (`OUR_TOTAL_SALES` y si quiero correo SMTP).
7) Ejecutar el monitor en modo verbose.
8) Confirmar si funcionó y mostrar resumen de resultados.
9) Programarlo con cron a las 08:00 y 16:30.
10) Verificar cron (`crontab -l`) y mostrar logs (`tail -n 100 logs/cardmarket-monitor.log`).

Reglas:
- No uses `/` (raíz) para alojar el proyecto salvo que yo lo pida.
- Prioriza `~/proyectos/GestorMarket`.
- No te detengas por defecto si `/workspace/GestorMarket` no existe; intenta clonar/autodetectar primero.
- Si existe `scripts/run_monitor_auto_linux.sh`, úsalo.
- Si no existe, implementa autodetección con `find` limitado y continúa.

Comandos preferidos:
- `mkdir -p ~/proyectos && cd ~/proyectos`
- `git clone https://github.com/Catrindw/GestorMarket.git GestorMarket` (solo si no existe local)
- `cd ~/proyectos/GestorMarket`
- `bash scripts/run_monitor_auto_linux.sh`
- Si falla autodetección: `bash scripts/run_monitor_auto_linux.sh ~/proyectos/GestorMarket`
- `source .venv/bin/activate && python src/cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt --verbose`
- `crontab cron/cardmarket-monitor.cron`
- `crontab -l`
- `tail -n 100 logs/cardmarket-monitor.log`

Al final dame:
- comandos ejecutados,
- cuáles pasaron/fallaron,
- y qué revisar si algo falla.
```

Consejo: para evitar líos de ruta, usa directamente `bash scripts/run_monitor_auto_linux.sh`.

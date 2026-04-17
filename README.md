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
- `cron/cardmarket-monitor.cron`: ejemplo de programación dos veces al día.

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` con tus datos (especialmente `OUR_TOTAL_SALES` y credenciales SMTP si quieres correo).

## Uso manual

```bash
python3 src/cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt
```

## Programación (08:00 y 16:30)

```bash
crontab cron/cardmarket-monitor.cron
```

> Asegúrate de ajustar la ruta absoluta al repositorio y al Python del entorno virtual dentro del fichero de cron.

## Ignorar una carta para siempre

Añade la URL del artículo a `ignored_cards.txt` (una por línea). El script no la volverá a incluir.

## Nota importante

Cardmarket puede cambiar estructura HTML o requerir anti-bot/cookies en ciertas páginas. El parser está diseñado para ser robusto y configurable, pero puede requerir ajustes de selectores si Cardmarket cambia el marcado.

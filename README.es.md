# Taza inteligente VSITOO para Home Assistant

Consultá la temperatura de tu bebida y controlá el calentador de la taza desde Home Assistant por Bluetooth de bajo consumo (BLE).

[![Abrir en HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=crisflashin&repository=ha-vsitoo-smart-mug&category=integration)

[English](README.md) · [Solución de problemas](#solución-de-problemas)

| Entidad | Qué muestra o controla |
| --- | --- |
| Termostato | Enciende o apaga el calentador y ajusta la temperatura objetivo de 44 a 66 °C en pasos de 1 °C |
| Temperatura de la bebida | Temperatura actual en °C |
| Batería | Porcentaje de carga |
| Cargando | Indica si la taza está cargando |
| Voltaje de batería y voltaje TDV | Dos sensores en mV |

La integración funciona de forma local. Si la taza pierde la conexión, las entidades figuran como no disponibles y Home Assistant vuelve a intentar conectarse automáticamente.

## Instalación

1. Activá [Bluetooth en Home Assistant](https://www.home-assistant.io/integrations/bluetooth/) y usá un adaptador local o un proxy con **conexiones BLE activas**, como un proxy Bluetooth de ESPHome.
2. Usá el botón de HACS de arriba. También podés ir a **HACS → ⋮ → Repositorios personalizados**, agregar `https://github.com/crisflashin/ha-vsitoo-smart-mug` y elegir **Integración**.
3. Buscá **VSITOO Smart Mug**, descargala y reiniciá Home Assistant.

Para instalarla manualmente, copiá [`custom_components/vsitoo`](custom_components/vsitoo/) a la carpeta de configuración de Home Assistant, de modo que el manifiesto quede en `config/custom_components/vsitoo/manifest.json`. Reiniciá Home Assistant.

## Agregar la taza

1. Despertá la taza, acercala al adaptador o proxy y desconectala de la app VSITOO del celular.
2. Abrí **Ajustes → Dispositivos y servicios → Añadir integración** y buscá **VSITOO Smart Mug**.
3. Elegí la taza de la lista. Si el formulario muestra un campo de texto, ingresá su dirección MAC Bluetooth.
4. Para manejar el calentador desde un panel, agregá una tarjeta **Termostato** y seleccioná la entidad de clima de VSITOO.

Si ya tenías instalada la integración, actualizala desde HACS o reemplazá los archivos manualmente y reiniciá Home Assistant.

## Solución de problemas

| Síntoma | Qué revisar |
| --- | --- |
| La taza no aparece en la lista | Despertala, acercala al adaptador o proxy y volvé a abrir el formulario. Si aparece un campo de texto, ingresá la MAC. |
| Las entidades siguen como no disponibles | Desconectá la app del celular y verificá que el adaptador o proxy admita conexiones activas. La integración reintenta en segundo plano. |
| VSITOO no aparece al añadir una integración | Confirmá la descarga o revisá la ruta del manifiesto, y reiniciá Home Assistant. |

Si el problema sigue, [abrí un issue](https://github.com/crisflashin/ha-vsitoo-smart-mug/issues/new) con el modelo de taza, la versión de Home Assistant, el tipo de adaptador o proxy y los mensajes relevantes de **Ajustes → Sistema → Registros**. Quitá las direcciones Bluetooth y otros datos privados antes de compartirlos.

Esta integración es independiente de VSITOO. La compatibilidad puede variar según el modelo y el firmware.

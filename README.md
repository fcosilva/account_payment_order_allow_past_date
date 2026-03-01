# Account Payment Order - Allow Past Date

Este módulo para Odoo 17.0 extiende la funcionalidad de las órdenes de pago (`account_payment_order`) para proporcionar mayor flexibilidad en la gestión de fechas y la integración con informes de gastos.

## Resumen

Este módulo introduce dos características principales:
1.  **Permite confirmar órdenes de pago con fechas en el pasado**, una funcionalidad controlada a través de los ajustes de contabilidad.
2.  **Integra los informes de gastos de empleados (`hr.expense`)**, permitiendo añadirlos directamente a una orden de pago para su reembolso.

## Características Principales

### Fechas de Pago Pasadas
Por defecto, OCA y el módulo base `account_payment_order` previenen la confirmación de órdenes de pago cuya fecha de ejecución sea anterior a la fecha actual. Este módulo anula esa restricción si se activa la configuración correspondiente, lo cual es útil para registrar pagos que se realizaron en una fecha anterior pero que no se asentaron en el sistema a tiempo.

### Integración con Informes de Gastos
Añade un flujo de trabajo para simplificar el reembolso de gastos a empleados. Aparecerá un nuevo botón en los informes de gastos aprobados que permite al usuario añadirlos a una orden de pago existente o nueva, agilizando el proceso de pago.

## Configuración

Para habilitar la funcionalidad de fechas pasadas:
1.  Ve a `Contabilidad > Configuración > Ajustes`.
2.  Busca la sección `Pagos` y activa la opción **"Permitir fechas pasadas en Órdenes de Pago"**.
3.  Guarda los cambios.

![config-option](https://i.imgur.com/your-screenshot-url.png) <!-- Reemplaza con una URL de captura de pantalla si lo deseas -->

## Uso

### Crear una Orden de Pago con Fecha Pasada
1.  Asegúrate de que la opción de configuración esté activada.
2.  Crea una nueva Orden de Pago (`Contabilidad > Pagos > Órdenes de Pago`).
3.  Establece la `Fecha Programada` a una fecha en el pasado.
4.  Añade las líneas de pago y procede a confirmar la orden. El sistema ya no mostrará un error de validación por la fecha.

### Añadir Informes de Gastos a una Orden de Pago
1.  Ve a `Gastos > Mis Informes de Gastos`.
2.  Abre un informe que esté en estado "Aprobado" o "Listo para Pagar".
3.  Haz clic en el botón **"Añadir a Orden de Pago"**.
4.  Se abrirá un asistente que te permitirá seleccionar una orden de pago existente o crear una nueva para procesar el reembolso.

## Dependencias

Este módulo depende de los siguientes módulos de Odoo:
*   `account_payment_order`
*   `hr_expense`

## Licencia

Este módulo está licenciado bajo AGPL-3.

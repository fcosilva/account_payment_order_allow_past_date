from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_past_payment_order_date = fields.Boolean(
        string="Permitir fechas pasadas en Órdenes de Pago",
        config_parameter="account_payment_order.allow_past_date",
        help="If enabled, payment orders can be confirmed with dates in the past.",
    )

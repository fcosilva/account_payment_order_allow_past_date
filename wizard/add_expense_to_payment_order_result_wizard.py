from odoo import _, fields, models


class AddExpenseToPaymentOrderResultWizard(models.TransientModel):
    _name = "add.expense.to.payment.order.result.wizard"
    _description = "Add Expense to Payment Order Result"

    order_id = fields.Many2one("account.payment.order", string="Orden de Pago", required=True)
    summary_message = fields.Char(string="Resumen", readonly=True, required=True)

    def action_open_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Orden de Pago"),
            "res_model": "account.payment.order",
            "views": [(False, "form")],
            "view_mode": "form",
            "res_id": self.order_id.id,
            "target": "current",
        }

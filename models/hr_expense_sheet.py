from odoo import _, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def action_open_add_to_payment_order_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Add to Payment Order"),
            "res_model": "add.expense.to.payment.order.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": "hr.expense.sheet",
                "active_ids": self.ids,
            },
        }

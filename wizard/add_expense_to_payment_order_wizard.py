from odoo import _, fields, models
from odoo.exceptions import AccessError, UserError


class AddExpenseToPaymentOrderWizard(models.TransientModel):
    _name = "add.expense.to.payment.order.wizard"
    _description = "Add Expense Reports to Payment Order"

    option = fields.Selection(
        [("existing", "Usar orden de pago existente"), ("new", "Crear nueva orden de pago")],
        default="existing",
        required=True,
    )

    order_id = fields.Many2one(
        "account.payment.order",
        string="Orden de Pago",
        domain="[('state','=','draft'),('payment_type','=','outbound')]",
    )

    payment_mode_id = fields.Many2one("account.payment.mode", string="Modo de Pago")
    date_scheduled = fields.Date(string="Fecha Programada", default=fields.Date.context_today)

    def _get_sheets(self):
        sheets = self.env["hr.expense.sheet"].browse(self.env.context.get("active_ids", []))
        sheets = sheets.exists()
        invalid = sheets.filtered(lambda s: s.state not in ("post", "done"))
        if invalid or not sheets:
            raise UserError(_("Solo los reportes de gastos contabilizados pueden agregarse."))
        # enforce same company
        if len(set(sheets.mapped("company_id").ids)) > 1:
            raise UserError(_("Los reportes de gastos seleccionados deben pertenecer a la misma compañía."))
        return sheets

    def action_apply(self):
        self.ensure_one()
        sheets = self._get_sheets()
        created_new_order = False

        if self.option == "existing":
            if not self.order_id:
                raise UserError(_("Seleccione una orden de pago."))
            order = self.order_id
        else:
            if not self.payment_mode_id:
                raise UserError(_("Configure el modo de pago."))
            journal = self.payment_mode_id.fixed_journal_id
            if not journal:
                raise UserError(_("El Modo de Pago seleccionado no tiene un diario configurado."))
            order = self.env["account.payment.order"].create({
                "payment_type": "outbound",
                "payment_mode_id": self.payment_mode_id.id,
                "journal_id": journal.id,
                "date_prefered": "fixed",
                "date_scheduled": self.date_scheduled,
                "company_id": sheets[0].company_id.id,
            })
            created_new_order = True

        if order.company_id != sheets[0].company_id:
            raise UserError(_("La compañía de la orden de pago no coincide con la de los reportes de gastos."))

        selected_reports_count = len(sheets)
        omitted_reports_count = 0
        created_lines_count = 0
        existing_move_line_ids = set(order.payment_line_ids.mapped("move_line_id").ids)
        for sheet in sheets:
            moves = sheet.account_move_ids.filtered(lambda m: m.state == "posted")
            if not moves:
                raise UserError(_("El reporte de gastos '%s' no tiene un asiento contable publicado.") % sheet.name)
            move = moves[0]

            lines_created_for_sheet = 0
            payable_lines = move.line_ids.filtered(
                lambda l: l.account_id.account_type == "liability_payable"
                and not l.reconciled
                and (l.amount_residual or l.amount_residual_currency)
            )
            for line in payable_lines:
                if line.id in existing_move_line_ids:
                    continue
                amount = abs(line.amount_residual_currency) if line.currency_id else abs(line.amount_residual)
                if not amount:
                    continue
                self.env["account.payment.line"].create({
                    "order_id": order.id,
                    "partner_id": line.partner_id.id,
                    "move_line_id": line.id,
                    "currency_id": line.currency_id.id or order.currency_id.id,
                    "amount_currency": amount,
                    "date": self.date_scheduled,
                    "communication": move.name or sheet.name or "",
                })
                created_lines_count += 1
                lines_created_for_sheet += 1
                existing_move_line_ids.add(line.id)
            if not lines_created_for_sheet:
                omitted_reports_count += 1

        # Avoid leaving a new empty payment order when all selected reports are already paid/reconciled.
        if created_new_order and not created_lines_count:
            order.unlink()
            raise UserError(
                _(
                    "No se creó la orden de pago porque los reportes seleccionados no tienen líneas pendientes por pagar."
                )
            )

        open_order_action = {
            "type": "ir.actions.act_window",
            "res_model": "account.payment.order",
            "views": [(False, "form")],
            "view_mode": "form",
            "res_id": order.id,
            "target": "current",
        }

        if omitted_reports_count:
            message = _(
                "Se agregaron %(lines)s líneas y se omitieron %(omitted)s informes sin líneas pendientes o ya incluidas en la orden.",
                lines=created_lines_count,
                omitted=omitted_reports_count,
            )
            try:
                result_wizard = self.env["add.expense.to.payment.order.result.wizard"].create({
                    "order_id": order.id,
                    "summary_message": message,
                })
                return {
                    "type": "ir.actions.act_window",
                    "name": _("Resultado de la operación"),
                    "res_model": "add.expense.to.payment.order.result.wizard",
                    "views": [(False, "form")],
                    "view_mode": "form",
                    "res_id": result_wizard.id,
                    "target": "new",
                    "context": {"dialog_size": "medium"},
                }
            except AccessError:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Resultado de la operación"),
                        "message": message,
                        "type": "warning",
                        "sticky": False,
                        "next": open_order_action,
                    },
                }

        return open_order_action

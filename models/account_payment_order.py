from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    @api.constrains("date_scheduled")
    def check_date_scheduled(self):
        allow_past = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account_payment_order.allow_past_date")
        )
        if allow_past:
            return
        return super().check_date_scheduled()

    def draft2open(self):
        allow_past = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account_payment_order.allow_past_date")
        )
        if not allow_past:
            return super().draft2open()

        today = fields.Date.context_today(self)

        for order in self:
            if not order.journal_id:
                raise ValidationError(_("Missing journal on payment order %s") % order.name)

            if (
                order.payment_method_id.bank_account_required
                and not order.journal_id.bank_account_id
            ):
                raise ValidationError(_("Missing bank account on journal for order %s") % order.name)

            if not order.payment_line_ids:
                raise ValidationError(_("No payment lines on order %s") % order.name)

            order.payment_ids.action_draft()
            order.payment_ids.action_cancel()
            order.payment_ids.unlink()

            payline_err_text = []
            group_paylines = {}

            for payline in order.payment_line_ids:
                try:
                    payline.draft2open_payment_line_check()
                except Exception as e:
                    payline_err_text.append(e.args[0])

                # Compute requested payment date
                if order.date_prefered == "due":
                    requested_date = payline.ml_maturity_date or payline.date or today
                elif order.date_prefered == "fixed":
                    requested_date = order.date_scheduled or today
                else:
                    requested_date = today

                # IMPORTANT: OCA forces max(today, requested_date). We remove it when allow_past is enabled.

                # inbound: check option no_debit_before_maturity
                if (
                    order.payment_type == "inbound"
                    and order.payment_mode_id.no_debit_before_maturity
                    and payline.ml_maturity_date
                    and requested_date < payline.ml_maturity_date
                ):
                    payline_err_text.append(
                        _(
                            "The payment mode '%(pmode)s' has the option "
                            "'Disallow Debit Before Maturity Date'. The "
                            "payment line %(pline)s has a maturity date %(mdate)s "
                            "which is after the computed payment date %(pdate)s.",
                            pmode=order.payment_mode_id.name,
                            pline=payline.name,
                            mdate=payline.ml_maturity_date,
                            pdate=requested_date,
                        )
                    )

                payline.date = requested_date

                hashcode = (
                    payline.payment_line_hashcode()
                    if order.payment_mode_id.group_lines
                    else payline.id
                )

                if hashcode in group_paylines:
                    group_paylines[hashcode]["paylines"] += payline
                    group_paylines[hashcode]["total"] += payline.amount_currency
                else:
                    group_paylines[hashcode] = {
                        "paylines": payline,
                        "total": payline.amount_currency,
                    }

            if payline_err_text:
                raise ValidationError(
                    _("There's at least one validation error:\n")
                    + "\n".join(payline_err_text)
                )

            order.env.flush_all()

            payment_vals = []
            for paydict in list(group_paylines.values()):
                if paydict["total"] <= 0:
                    raise ValidationError(
                        _(
                            "The amount for Partner '%(partner)s' is negative "
                            "or null (%(amount).2f) !",
                            partner=paydict["paylines"][0].partner_id.name,
                            amount=paydict["total"],
                        )
                    )
                payment_vals.append(
                    paydict["paylines"]._prepare_account_payment_vals()
                )

            self.env["account.payment"].create(payment_vals)

        self.write({"state": "open"})
        return True

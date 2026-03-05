{
    "name": "Account Payment Order - Allow Past Date",
    "version": "17.0.5.0.0",
    "summary": "Allow confirming payment orders with past dates (configurable) and add expense reports to payment orders",
    "author": "Openlab Ecuador",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": [
        "account_payment_order",
        "hr_expense"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_view.xml",
        "views/hr_expense_sheet_action.xml",
        "views/hr_expense_menu.xml",
        "wizard/add_expense_to_payment_order_wizard_view.xml",
        "wizard/add_expense_to_payment_order_result_wizard_view.xml"
    ],
    "installable": True
}

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # POS Access Control Fields
    pos_allow_closing = fields.Boolean(
        string='Allow POS Closing',
        default=True,
        help='Allow employee to close POS session'
    )
    
    pos_allow_order_delete = fields.Boolean(
        string='Allow Order Deletion',
        default=True,
        help='Allow employee to delete or cancel orders'
    )
    
    pos_allow_orderline_delete = fields.Boolean(
        string='Allow Order Line Deletion',
        default=True,
        help='Allow employee to delete order lines'
    )
    
    pos_allow_payment = fields.Boolean(
        string='Allow Order Payment',
        default=True,
        help='Allow employee to process payments'
    )
    
    pos_allow_discount = fields.Boolean(
        string='Allow Discount Application',
        default=True,
        help='Allow employee to apply discounts'
    )
    
    pos_allow_price_change = fields.Boolean(
        string='Allow Price Change',
        default=True,
        help='Allow employee to change product prices'
    )
    
    pos_allow_qty_decrease = fields.Boolean(
        string='Allow Decreasing Quantity',
        default=True,
        help='Allow employee to decrease product quantity'
    )
    
    pos_allow_cash_inout = fields.Boolean(
        string='Allow Cash In/Out',
        default=True,
        help='Allow employee to perform cash in/out operations'
    )
    
    pos_allow_create_product = fields.Boolean(
        string='Allow Create Product',
        default=True,
        help='Allow employee to create new products from POS'
    )
    
    pos_allow_fiscal_position = fields.Boolean(
        string='Allow Fiscal Position/Tax',
        default=True,
        help='Allow employee to change fiscal position or taxes'
    )
    
    pos_allow_pricelist = fields.Boolean(
        string='Allow Pricelist Change',
        default=True,
        help='Allow employee to change pricelist'
    )
    
    pos_allow_refund = fields.Boolean(
        string='Allow Refund',
        default=True,
        help='Allow employee to process refunds'
    )

    @api.model
    def get_pos_employee_access(self, employee_id):
        """Get POS access permissions for an employee"""
        employee = self.browse(employee_id)
        if not employee.exists():
            return {}
        
        return {
            'pos_allow_closing': employee.pos_allow_closing,
            'pos_allow_order_delete': employee.pos_allow_order_delete,
            'pos_allow_orderline_delete': employee.pos_allow_orderline_delete,
            'pos_allow_payment': employee.pos_allow_payment,
            'pos_allow_discount': employee.pos_allow_discount,
            'pos_allow_price_change': employee.pos_allow_price_change,
            'pos_allow_qty_decrease': employee.pos_allow_qty_decrease,
            'pos_allow_cash_inout': employee.pos_allow_cash_inout,
            'pos_allow_create_product': employee.pos_allow_create_product,
            'pos_allow_fiscal_position': employee.pos_allow_fiscal_position,
            'pos_allow_pricelist': employee.pos_allow_pricelist,
            'pos_allow_refund': employee.pos_allow_refund,
        }
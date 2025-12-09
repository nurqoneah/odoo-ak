# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
# -*- coding: utf-8 -*-
# © 2025 ehuerta _at_ ixer.mx
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)
    
class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    # Override field untuk membuat UoM editable
    product_uom_id = fields.Many2one(
        'uom.uom', 
        string='Product UoM', 
        related='',
        store=True,
        readonly=False,
        required=True
    )
    
    # PENTING: Tambahkan store=True dan depends yang lengkap
    unit_cost = fields.Float(
        string='Unit Cost', 
        compute='_compute_unit_cost', 
        # store=True,  # HARUS store=True agar disimpan di database
        digits='Product Price',
        # readonly=True
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        # Pastikan product_uom_id dan unit_cost terload
        if 'product_uom_id' not in params:
            params.append('product_uom_id')
        if 'unit_cost' not in params:
            params.append('unit_cost')
        return params

    @api.model_create_multi
    def create(self, vals_list):
        """Set default UoM jika tidak ada"""
        for vals in vals_list:
            if 'product_id' in vals and 'product_uom_id' not in vals:
                product = self.env['product.product'].browse(vals['product_id'])
                vals['product_uom_id'] = product.uom_id.id
        return super().create(vals_list)

    def write(self, vals):
        """Update UoM jika product berubah dan UoM tidak diset manual"""
        if 'product_id' in vals and 'product_uom_id' not in vals:
            for line in self:
                product = self.env['product.product'].browse(vals['product_id'])
                if not vals.get('product_uom_id'):
                    vals['product_uom_id'] = product.uom_id.id
        return super().write(vals)

    @api.depends('total_cost', 'qty', 'product_uom_id', 'product_id', 'is_total_cost_computed')
    def _compute_unit_cost(self):
        """Hitung unit cost berdasarkan UoM yang dipilih"""
        for line in self:
            if not line.qty or not line.product_uom_id or not line.is_total_cost_computed:
                line.unit_cost = 0.0
                continue
                
            try:
                # Konversi dari base UoM ke UoM yang dipilih
                if line.product_id.uom_id and line.product_id.uom_id != line.product_uom_id:
                    # total_cost dalam base qty, perlu konversi ke selected UoM
                    # Hitung berapa base qty untuk 1 unit selected UoM
                    base_qty_per_unit = line.product_uom_id._compute_quantity(
                        1.0, 
                        line.product_id.uom_id,
                        raise_if_failure=False
                    )
                    if base_qty_per_unit:
                        # Cost per base unit
                        cost_per_base_unit = line.total_cost / (line.qty * base_qty_per_unit) if line.qty else 0.0
                        # Cost per selected unit
                        line.unit_cost = cost_per_base_unit * base_qty_per_unit
                    else:
                        line.unit_cost = 0.0
                else:
                    # Jika UoM sama, langsung bagi
                    line.unit_cost = line.total_cost / line.qty if line.qty else 0.0
            except Exception as e:
                _logger.warning(f"Error computing unit_cost for line {line.id}: {e}")
                line.unit_cost = 0.0

    @api.depends('price_subtotal', 'total_cost', 'product_uom_id', 'qty', 'product_id')
    def _compute_margin(self):
        """Override margin calculation untuk memperhitungkan UoM conversion"""
        for line in self:
            if line.product_id.type == 'combo':
                line.margin = 0
                line.margin_percent = 0
                continue

            # Gunakan total_cost yang sudah benar (dalam base qty)
            # price_subtotal sudah dalam selected UoM * qty
            line.margin = line.price_subtotal - line.total_cost
            line.margin_percent = (
                line.margin / line.price_subtotal 
                if not float_is_zero(
                    line.price_subtotal, 
                    precision_rounding=line.currency_id.rounding
                ) 
                else 0
            )

    def _compute_total_cost(self, stock_moves):
        """Override untuk mempertimbangkan UoM conversion dalam cost calculation"""
        for line in self.filtered(lambda l: not l.is_total_cost_computed):
            product = line.product_id
            cost_currency = product.sudo().cost_currency_id
            
            # Konversi qty ke base UoM untuk perhitungan cost
            try:
                if line.product_uom_id and line.product_uom_id != product.uom_id:
                    base_qty = line.product_uom_id._compute_quantity(
                        line.qty,
                        product.uom_id,
                        raise_if_failure=False
                    )
                else:
                    base_qty = line.qty
            except Exception as e:
                _logger.warning(f"Error converting UoM for line {line.id}: {e}")
                base_qty = line.qty

            if line._is_product_storable_fifo_avco() and stock_moves:
                product_cost = product._compute_average_price(
                    0, 
                    base_qty, 
                    line._get_stock_moves_to_consider(stock_moves, product)
                )
                if (cost_currency.is_zero(product_cost) and 
                    line.order_id.shipping_date and 
                    line.refunded_orderline_id):
                    product_cost = (
                        line.refunded_orderline_id.total_cost / 
                        line.refunded_orderline_id.qty if line.refunded_orderline_id.qty else 0.0
                    )
            else:
                product_cost = product.standard_price

            # Total cost dihitung dalam base UoM qty
            line.total_cost = base_qty * cost_currency._convert(
                from_amount=product_cost,
                to_currency=line.currency_id,
                company=line.company_id or self.env.company,
                date=line.order_id.date_order or fields.Date.today(),
                round=False,
            )
            line.is_total_cost_computed = True

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Set default UoM ketika product berubah"""
        res = super()._onchange_product_id()
        if self.product_id and not self.product_uom_id:
            self.product_uom_id = self.product_id.uom_id
        return res

    @api.onchange('product_uom_id')
    def _onchange_product_uom_id(self):
        """Recalculate prices when UoM changes"""
        if self.product_uom_id and self.product_id:
            # Trigger recalculation
            self._onchange_qty()

    def _prepare_base_line_for_taxes_computation(self):
        """Override untuk mempertimbangkan UoM dalam tax calculation"""
        self.ensure_one()
        res = super()._prepare_base_line_for_taxes_computation()
        
        # Update UoM di tax computation
        if self.product_uom_id:
            res['uom_id'] = self.product_uom_id
        
        return res

    def _prepare_procurement_values(self, group_id=False):
        """Override untuk UoM dalam procurement"""
        res = super()._prepare_procurement_values(group_id=group_id)
        
        # Untuk procurement, pastikan menggunakan base UoM dan qty yang benar
        if self.product_uom_id and self.product_id.uom_id:
            if self.product_uom_id != self.product_id.uom_id:
                # Konversi ke base UoM
                base_qty = self.product_uom_id._compute_quantity(
                    self.qty,
                    self.product_id.uom_id,
                    raise_if_failure=False
                )
                res['product_qty'] = base_qty
                res['product_uom'] = self.product_id.uom_id
        
        return res


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_product_aml_dict(self, base_line_vals, update_base_line_vals, rate, sign):
        """Override untuk mempertimbangkan UoM di accounting lines"""
        res = super()._prepare_product_aml_dict(
            base_line_vals, 
            update_base_line_vals, 
            rate, 
            sign
        )
        
        order_line = base_line_vals['record']
        
        # Update quantity dengan UoM conversion jika perlu
        if order_line.product_uom_id and order_line.product_id.uom_id:
            if order_line.product_uom_id != order_line.product_id.uom_id:
                # Untuk accounting, gunakan base UoM
                try:
                    base_qty = order_line.product_uom_id._compute_quantity(
                        order_line.qty,
                        order_line.product_id.uom_id,
                        raise_if_failure=False
                    )
                    res['quantity'] = base_qty * sign
                except Exception as e:
                    _logger.warning(f"Error converting UoM for accounting: {e}")
        
        return res
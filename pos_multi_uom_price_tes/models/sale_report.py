
# -*- coding: utf-8 -*-
from odoo import api, models

class SaleReport(models.Model):
    _inherit = "sale.report"

    def _select_pos(self):
        select_ = f"""
            -MIN(l.id) AS id,
            l.product_id AS product_id,
            NULL AS line_invoice_status,
            t.uom_id AS product_uom,
            CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty / u.factor * u2.factor) ELSE 0 END AS product_uom_qty,
            CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_delivered / u.factor * u2.factor) ELSE 0 END AS qty_delivered,
            CASE WHEN l.product_id IS NOT NULL THEN SUM((l.qty - l.qty_delivered) / u.factor * u2.factor) ELSE 0 END AS qty_to_deliver,
            CASE WHEN pos.state = 'invoiced' THEN SUM(l.qty / u.factor * u2.factor) ELSE 0 END AS qty_invoiced,
            CASE WHEN pos.state != 'invoiced' THEN SUM(l.qty / u.factor * u2.factor) ELSE 0 END AS qty_to_invoice,
            AVG(l.price_unit)
                / MIN({self._case_value_or_one('pos.currency_rate')})
                * {self._case_value_or_one('account_currency_table.rate')}
            AS price_unit,
            SUM(l.price_subtotal_incl)
                / MIN({self._case_value_or_one('pos.currency_rate')})
                * {self._case_value_or_one('account_currency_table.rate')}
            AS price_total,
            SUM(l.price_subtotal)
                / MIN({self._case_value_or_one('pos.currency_rate')})
                * {self._case_value_or_one('account_currency_table.rate')}
            AS price_subtotal,
            (CASE WHEN pos.state != 'invoiced' THEN SUM(l.price_subtotal) ELSE 0 END)
                / MIN({self._case_value_or_one('pos.currency_rate')})
                * {self._case_value_or_one('account_currency_table.rate')}
            AS amount_to_invoice,
            (CASE WHEN pos.state = 'invoiced' THEN SUM(l.price_subtotal) ELSE 0 END)
                / MIN({self._case_value_or_one('pos.currency_rate')})
                * {self._case_value_or_one('account_currency_table.rate')}
            AS amount_invoiced,
            count(*) AS nbr,
            pos.name AS name,
            pos.date_order AS date,
            (CASE WHEN pos.state = 'done' THEN 'sale' ELSE pos.state END) AS state,
            NULL as invoice_status,
            pos.partner_id AS partner_id,
            pos.user_id AS user_id,
            pos.company_id AS company_id,
            NULL AS campaign_id,
            NULL AS medium_id,
            NULL AS source_id,
            t.categ_id AS categ_id,
            pos.pricelist_id AS pricelist_id,
            pos.crm_team_id AS team_id,
            p.product_tmpl_id,
            partner.commercial_partner_id AS commercial_partner_id,
            partner.country_id AS country_id,
            partner.industry_id AS industry_id,
            partner.state_id AS state_id,
            partner.zip AS partner_zip,
            CASE WHEN l.product_id IS NOT NULL THEN SUM(p.weight * l.qty / u.factor * u2.factor) ELSE 0 END AS weight,
            CASE WHEN l.product_id IS NOT NULL THEN SUM(p.volume * l.qty / u.factor * u2.factor) ELSE 0 END AS volume,
            l.discount AS discount,
            SUM((l.price_unit * l.discount * l.qty / 100.0
                / {self._case_value_or_one('pos.currency_rate')}
                * {self._case_value_or_one('account_currency_table.rate')}))
            AS discount_amount,
            concat('pos.order', ',', pos.id) AS order_reference"""

        # Tambahan kolom ekstra dari parent
        additional_fields = self._select_additional_fields()
        additional_fields_info = self._fill_pos_fields(additional_fields)
        template = """,
            %s AS %s"""
        for fname, value in additional_fields_info.items():
            select_ += template % (value, fname)
        print("hello")
        return select_

    def _from_pos(self):
        currency_table = self.env['res.currency']._get_simple_currency_table(self.env.companies)
        return """
            pos_order_line l
            JOIN pos_order pos ON l.order_id = pos.id
            LEFT JOIN res_partner partner ON (pos.partner_id=partner.id OR pos.partner_id = NULL)
            LEFT JOIN product_product p ON l.product_id = p.id
            LEFT JOIN product_template t ON p.product_tmpl_id = t.id
            LEFT JOIN uom_uom u ON u.id = l.product_uom_id    -- gunakan UoM produk untuk konversi
            LEFT JOIN uom_uom u2 ON u2.id = t.uom_id   -- tetap sama (karena l.uom_id tidak ada)
            LEFT JOIN pos_session session ON session.id = pos.session_id
            LEFT JOIN pos_config config ON config.id = session.config_id
            LEFT JOIN stock_picking_type picking ON picking.id = config.picking_type_id
            JOIN {currency_table} ON account_currency_table.company_id = pos.company_id
        """.format(
            currency_table=self.env.cr.mogrify(currency_table).decode(self.env.cr.connection.encoding),
        )

    
    def _group_by_pos(self):
        return """
            l.order_id,
            l.product_id,
            l.price_unit,
            l.discount,
            l.qty,
            t.uom_id,
            t.categ_id,
            pos.id,
            pos.name,
            pos.date_order,
            pos.partner_id,
            pos.user_id,
            pos.state,
            pos.company_id,
            pos.pricelist_id,
            p.product_tmpl_id,
            partner.commercial_partner_id,
            partner.country_id,
            partner.industry_id,
            partner.state_id,
            partner.zip,
            u.factor,
            u2.factor,
            pos.crm_team_id,
            account_currency_table.rate,
            picking.warehouse_id"""



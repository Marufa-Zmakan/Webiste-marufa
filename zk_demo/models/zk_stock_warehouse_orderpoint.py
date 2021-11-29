from odoo import fields, models, api, _
from odoo.tools import add, float_compare, frozendict, split_every, format_date
import logging
_logger = logging.getLogger(__name__)
from odoo.osv import expression


class ReorderingRulesInherit(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    one_or_multi_stock = fields.Selection([('one', 'One Stock'), ('multi', 'Multi Stock')],
                                          default='one', string='Chose One Or Multi Stock')

    warehouse_ids = fields.Many2many(comodel_name='stock.warehouse', string='Warehouses')
    location_ids = fields.Many2many(comodel_name='stock.location', string='Locations')

    @api.depends('qty_multiple', 'qty_forecast', 'product_min_qty', 'product_max_qty')
    def _compute_qty_to_order(self):
        for orderpoint in self:
            if orderpoint.one_or_multi_stock == 'one':
                return super(ReorderingRulesInherit, self)._compute_qty_to_order()
            else:
                if orderpoint.location_ids:
                    params = []
                    sql = "SELECT SUM(quantity) FROM stock_quant WHERE location_id IN %s;"
                    params.append(tuple(orderpoint.location_ids.ids))
                    self.env.cr.execute(sql, params)
                    result = self.env.cr.dictfetchone()
                    if result['sum'] <= orderpoint.product_min_qty:
                        orderpoint.qty_to_order = orderpoint.product_max_qty - result['sum']

    @api.depends('warehouse_id', 'warehouse_ids')
    def _compute_allowed_location_ids(self):
        for orderpoint in self:
            if orderpoint.one_or_multi_stock == 'one':
                return super(ReorderingRulesInherit, self)._compute_allowed_location_ids()
            else:
                loc_domain = [('usage', 'in', ('internal', 'view'))]
                other_warehouses = self.env['stock.warehouse'].search([('id', 'not in', tuple(orderpoint.warehouse_ids.ids))])
                for view_location_id in other_warehouses.mapped('view_location_id'):
                    loc_domain = expression.AND([loc_domain, ['!', ('id', 'child_of', view_location_id.id)]])
                    loc_domain = expression.AND(
                        [loc_domain, ['|', ('company_id', '=', False), ('company_id', '=', orderpoint.company_id.id)]])
                orderpoint.allowed_location_ids = self.env['stock.location'].search(loc_domain)



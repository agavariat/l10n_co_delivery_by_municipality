# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class ResPartner(models.Model):
#     _inherit = 'res.partner'

#     check_delivery_flag = fields.Boolean(string='Check Delivery Method Flag', compute="_compute_check_delivery_flag", store=True)

#     @api.depends('country_id', 'state_id', 'xcity', 'property_delivery_carrier_id')
#     def _compute_check_delivery_flag(self):
#         quotation_obj = self.env['sale.order'].sudo()
#         for partner in self:
#             partner.check_delivery_flag = False
#             if type(partner.id) is int:
#                 partner_ids = [partner.id]
#                 if partner.parent_id:
#                     partner_ids.append(partner.parent_id.id)
#                 quotations = quotation_obj.search([('carrier_id', '!=', False), ('partner_id', 'in', partner_ids), ('state', '=', 'draft'), ('website_id', '!=', False)])
#                 if quotations:
#                     quotations._remove_delivery_line()
#                     quotations.write({'carrier_id': False})
#                     quotations._compute_available_carrier()
#                     for quote in quotations:
#                         quote._check_carrier_quotation()
#                 quotations = quotation_obj.search([('carrier_id', '!=', False), ('partner_shipping_id', 'in', partner_ids), ('state', '=', 'draft'), ('website_id', '!=', False)])
#                 if quotations:
#                     quotations._remove_delivery_line()
#                     quotations.write({'carrier_id': False})
#                     quotations._compute_available_carrier()
#                     for quote in quotations:
#                         quote._check_carrier_quotation()


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    municipality_ids = fields.Many2many('res.country.state.city', string='Municipalities')

    def available_carriers(self, partner):
        flag_municipality = False
        for delivery in self:
            if delivery.municipality_ids and partner.xcity and partner.xcity.id in delivery.municipality_ids.ids:
                flag_municipality = delivery
                break
        if flag_municipality:
            return flag_municipality
        else:
            return self.filtered(lambda c: c._match_address(partner))


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_carrier_quotation(self, force_carrier_id=None):
        self.ensure_one()
        DeliveryCarrier = self.env['delivery.carrier']

        if self.only_services:
            self.write({'carrier_id': None})
            self._remove_delivery_line()
            return True
        else:
            # attempt to use partner's preferred carrier
            if not force_carrier_id and self.partner_shipping_id.property_delivery_carrier_id:
                force_carrier_id = self.partner_shipping_id.property_delivery_carrier_id.id

            carrier = force_carrier_id and DeliveryCarrier.browse(force_carrier_id) or self.carrier_id
            available_carriers = self._get_delivery_methods()
            if carrier:
                if carrier not in available_carriers:
                    carrier = DeliveryCarrier
                else:
                    # set the forced carrier at the beginning of the list to be verfied first below
                    available_carriers -= carrier
                    available_carriers = carrier + available_carriers
            if force_carrier_id or not carrier or carrier not in available_carriers:
                flag_municipality = False
                for delivery in available_carriers:
                    if delivery.municipality_ids and self.partner_shipping_id.xcity and self.partner_shipping_id.xcity.id in delivery.municipality_ids.ids:
                        flag_municipality = delivery
                        break
                if flag_municipality:
                    carrier = flag_municipality
                else:
                    for delivery in available_carriers:
                        verified_carrier = delivery._match_address(self.partner_shipping_id)
                        if verified_carrier:
                            carrier = delivery
                            break

                # for delivery in available_carriers:
                #     verified_carrier = delivery._match_address(self.partner_shipping_id)
                #     if verified_carrier:
                #         carrier = delivery
                #         break
                self.write({'carrier_id': carrier.id})
            self._remove_delivery_line()
            if carrier:
                self.get_delivery_price()
                if self.delivery_rating_success:
                    self.set_delivery_line()

        return bool(carrier)

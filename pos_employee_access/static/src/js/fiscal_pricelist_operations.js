/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PartnerList } from "@point_of_sale/app/screens/partner_list/partner_list";

// Patch PartnerList to control pricelist and fiscal position changes
patch(PartnerList.prototype, {
    async clickPartner(partner) {
        const currentOrder = this.pos.get_order();

        if (currentOrder) {
            // Check if partner change will affect pricelist
            if (partner.property_product_pricelist &&
                partner.property_product_pricelist.id !== currentOrder.pricelist_id?.id) {
                if (!this.pos.checkAccess('pos_allow_pricelist')) {
                    this.pos.showAccessDeniedAlert(_t("Change Pricelist"));
                    return;
                }
            }

            // Check if partner change will affect fiscal position
            if (partner.property_account_position_id &&
                partner.property_account_position_id.id !== currentOrder.fiscal_position_id?.id) {
                if (!this.pos.checkAccess('pos_allow_fiscal_position')) {
                    this.pos.showAccessDeniedAlert(_t("Change Fiscal Position"));
                    return;
                }
            }
        }

        return super.clickPartner(...arguments);
    },
});


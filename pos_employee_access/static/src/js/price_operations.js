/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";

// Patch OrderSummary to control price change
patch(OrderSummary.prototype, {
    async setLinePrice(line, price) {
        const originalPrice = line.get_unit_price();
        if (price !== originalPrice) {
            if (!this.pos.checkAccess('pos_allow_price_change')) {
                this.pos.showAccessDeniedAlert(_t("Change Price"));
                return;
            }
        }
        return super.setLinePrice(...arguments);
    },
});


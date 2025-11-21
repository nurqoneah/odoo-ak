/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PosStore } from "@point_of_sale/app/store/pos_store";

// Patch PosStore to control discount application
patch(PosStore.prototype, {
    async setDiscountFromUI(line, val) {
        // Check if discount is being applied or increased
        const currentDiscount = line.get_discount() || 0;
        if (val > currentDiscount && val > 0) {
            if (!this.checkAccess('pos_allow_discount')) {
                this.showAccessDeniedAlert(_t("Apply Discount"));
                return;
            }
        }
        return super.setDiscountFromUI(...arguments);
    },
});


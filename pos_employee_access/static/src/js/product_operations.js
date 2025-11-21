/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

// Patch ProductScreen to control product creation
patch(ProductScreen.prototype, {
    async onClickCreateProduct() {
        if (!this.pos.checkAccess('pos_allow_create_product')) {
            this.pos.showAccessDeniedAlert(_t("Create Product"));
            return;
        }
        
        // Call parent method if it exists
        if (super.onClickCreateProduct) {
            return super.onClickCreateProduct(...arguments);
        }
    },
});


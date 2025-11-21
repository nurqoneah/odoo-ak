/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";

// Patch PaymentScreen to control payment validation
patch(PaymentScreen.prototype, {
    async validateOrder() {
        if (!this.pos.checkAccess('pos_allow_payment')) {
            this.pos.showAccessDeniedAlert(_t("Process Payment"));
            return;
        }
        return super.validateOrder(...arguments);
    }
});

// Patch ActionpadWidget to control payment button
patch(ActionpadWidget.prototype, {
    async submitOrder() {
        if (!this.pos.checkAccess('pos_allow_payment')) {
            this.pos.showAccessDeniedAlert(_t("Process Payment"));
            return;
        }
        return super.submitOrder(...arguments);
    }
});
/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

// Patch PosStore to control order deletion
patch(PosStore.prototype, {
    async onDeleteOrder(order) {
        if (!this.checkAccess('pos_allow_order_delete')) {
            this.showAccessDeniedAlert(_t("Delete Order"));
            return false;
        }
        return super.onDeleteOrder(...arguments);
    },
});

// Patch PosOrderline to control line deletion
patch(PosOrderline.prototype, {
    delete() {
        if (!this.pos.checkAccess('pos_allow_orderline_delete')) {
            this.pos.showAccessDeniedAlert(_t("Delete Order Line"));
            return;
        }
        return super.delete(...arguments);
    },
});


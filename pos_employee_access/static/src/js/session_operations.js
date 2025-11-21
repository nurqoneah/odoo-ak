/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { CashMovePopup } from "@point_of_sale/app/navbar/cash_move_popup/cash_move_popup";

// Patch CashMovePopup to control cash in/out
patch(CashMovePopup.prototype, {
    async confirm() {
        if (!this.pos.checkAccess('pos_allow_cash_inout')) {
            this.pos.showAccessDeniedAlert(_t("Cash In/Out"));
            this.props.close();
            return;
        }
        return super.confirm(...arguments);
    },
});


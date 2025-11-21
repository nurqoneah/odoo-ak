/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";

// Patch TicketScreen to control refund button
patch(TicketScreen.prototype, {
    async onDoRefund() {
        if (!this.pos.checkAccess('pos_allow_refund')) {
            this.pos.showAccessDeniedAlert(_t("Refund"));
            return;
        }
        return super.onDoRefund(...arguments);
    },

    // Control the visibility/availability of refund button
    getHighlightedButtons() {
        const buttons = super.getHighlightedButtons ? super.getHighlightedButtons(...arguments) : [];

        // Filter out refund button if no access
        if (!this.pos.checkAccess('pos_allow_refund')) {
            return buttons.filter(btn => btn.name !== 'refund');
        }

        return buttons;
    }
});
/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

// Patch PosStore to load employee access permissions
patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);
        this.employeeAccess = {};
    },

    async after_load_server_data() {
        await super.after_load_server_data(...arguments);
        await this.loadEmployeeAccess();
    },

    async loadEmployeeAccess() {
        const cashier = this.get_cashier();
        console.log('[POS Employee Access] Loading access for cashier:', cashier);
        console.log('[POS Employee Access] module_pos_hr:', this.config.module_pos_hr);

        let employeeId = null;

        // If pos_hr module is active, cashier is hr.employee
        // Otherwise, cashier is res.users and we need to get employee from user
        if (this.config.module_pos_hr) {
            // cashier is already hr.employee
            employeeId = cashier?.id;
        } else {
            // cashier is res.users, need to find employee
            // Try to find employee by user_id
            if (cashier && cashier.id) {
                const employees = this.models["hr.employee"]?.filter(emp => emp.user_id?.id === cashier.id);
                if (employees && employees.length > 0) {
                    employeeId = employees[0].id;
                }
            }
        }

        console.log('[POS Employee Access] Employee ID:', employeeId);

        if (employeeId) {
            try {
                const result = await this.data.call(
                    'hr.employee',
                    'get_pos_employee_access',
                    [employeeId]
                );
                this.employeeAccess = result || {};
                console.log('[POS Employee Access] Loaded permissions:', this.employeeAccess);
            } catch (error) {
                console.error('[POS Employee Access] Failed to load employee access:', error);
                // Set all permissions to true as default on error
                this.employeeAccess = {
                    pos_allow_closing: true,
                    pos_allow_order_delete: true,
                    pos_allow_orderline_delete: true,
                    pos_allow_payment: true,
                    pos_allow_discount: true,
                    pos_allow_price_change: true,
                    pos_allow_qty_decrease: true,
                    pos_allow_cash_inout: true,
                    pos_allow_create_product: true,
                    pos_allow_fiscal_position: true,
                    pos_allow_pricelist: true,
                    pos_allow_refund: true,
                };
            }
        } else {
            console.log('[POS Employee Access] No employee found, allowing all permissions');
            // Set all permissions to true as default when no employee
            this.employeeAccess = {
                pos_allow_closing: true,
                pos_allow_order_delete: true,
                pos_allow_orderline_delete: true,
                pos_allow_payment: true,
                pos_allow_discount: true,
                pos_allow_price_change: true,
                pos_allow_qty_decrease: true,
                pos_allow_cash_inout: true,
                pos_allow_create_product: true,
                pos_allow_fiscal_position: true,
                pos_allow_pricelist: true,
                pos_allow_refund: true,
            };
        }
    },

    async setSelectedCashier(cashierId) {
        await super.setSelectedCashier(cashierId);
        await this.loadEmployeeAccess();
    },

    checkAccess(permission) {
        if (!this.employeeAccess || Object.keys(this.employeeAccess).length === 0) {
            console.log('[POS Employee Access] No permissions loaded, allowing by default');
            return true; // Default allow if not loaded
        }
        const hasAccess = this.employeeAccess[permission] !== false;
        console.log(`[POS Employee Access] Checking ${permission}: ${hasAccess}`, this.employeeAccess);
        return hasAccess;
    },

    showAccessDeniedAlert(operation) {
        this.dialog.add(AlertDialog, {
            title: _t("Access Denied"),
            body: _t("You don't have permission to perform this operation: ") + operation,
        });
    },

    // Control POS Session closing
    async closeSession() {
        if (!this.checkAccess('pos_allow_closing')) {
            this.showAccessDeniedAlert(_t("Close POS Session"));
            return;
        }
        return super.closeSession(...arguments);
    },
});

// Patch PosOrder for access control
patch(PosOrder.prototype, {
    // Control pricelist change
    set_pricelist(pricelist) {
        if (pricelist && pricelist.id !== this.pricelist_id?.id) {
            if (!this.pos.checkAccess('pos_allow_pricelist')) {
                this.pos.showAccessDeniedAlert(_t("Change Pricelist"));
                return;
            }
        }
        return super.set_pricelist(...arguments);
    },

    // Control fiscal position
    set_fiscal_position(fiscalPosition) {
        if (fiscalPosition && fiscalPosition.id !== this.fiscal_position_id?.id) {
            if (!this.pos.checkAccess('pos_allow_fiscal_position')) {
                this.pos.showAccessDeniedAlert(_t("Change Fiscal Position/Tax"));
                return;
            }
        }
        return super.set_fiscal_position(...arguments);
    },
});

// Patch PosOrderline for access control
patch(PosOrderline.prototype, {
    // Control quantity change (including decrease)
    set_quantity(quantity) {
        const currentQty = this.qty;
        if (quantity < currentQty && currentQty > 0) {
            if (!this.pos.checkAccess('pos_allow_qty_decrease')) {
                this.pos.showAccessDeniedAlert(_t("Decrease Quantity"));
                return;
            }
        }
        return super.set_quantity(...arguments);
    },
});
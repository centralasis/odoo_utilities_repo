import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { _t } from "@web/core/l10n/translation";
import {
  makeAwaitable,
  ask,
} from "@point_of_sale/app/utils/make_awaitable_dialog";

patch(PosOrder.prototype, {
  getName() {
    super.getName();
    let name = this.partner_id?.name || this.floatingOrderName || "";
    if (this.isRefund) {
      name += _t(" (Refud)");
    }
    return name;
  },

  setPartner(partner) {
    super.setPartner(partner);
    this.setToInvoice(false);
  },
});

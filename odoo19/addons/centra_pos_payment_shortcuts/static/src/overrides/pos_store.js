import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";

patch(PosStore.prototype, {
  // this is how is to auto validate order the ammount is in the argument

  async pay(autoValidateOrder = false) {
    const currentOrder = this.getOrder();

    if (!currentOrder.canPay()) {
      return;
    }

    if (
      currentOrder.lines.some(
        (line) =>
          line.getProduct().tracking !== "none" && !line.hasValidProductLot()
      ) &&
      (this.pickingType.use_create_lots || this.pickingType.use_existing_lots)
    ) {
      const confirmed = await ask(this.env.services.dialog, {
        title: _t("Some Serial/Lot Numbers are missing"),
        body: _t(
          "You are trying to sell products with serial/lot numbers, but some of them are not set.\nWould you like to proceed anyway?"
        ),
      });
      if (confirmed) {
        this.mobile_pane = "right";
        this.navigate("PaymentScreen", {
          orderUuid: this.selectedOrderUuid,
          autoValidateOrder: autoValidateOrder,
        });
      }
    } else {
      this.mobile_pane = "right";
      this.navigate("PaymentScreen", {
        orderUuid: this.selectedOrderUuid,
        autoValidateOrder: autoValidateOrder,
      });
    }
  },
});

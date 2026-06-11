import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { markup } from "@odoo/owl";
import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";

patch(PaymentScreen.prototype, {
  onClickRegister() {
    let order = this.pos.getOrder();

    if (!order) {
      order = this.pos.addNewOrder();
    }

    this.pos.navigateToOrderScreen(order);
  },

  async validateOrder(isForceValidate = false) {
    const validation = new OrderPaymentValidation({
      pos: this.pos,
      orderUuid: this.currentOrder.uuid,
    });
		
	await validation.validateOrder(isForceValidate);		
    const is_valid = true;

    if (is_valid) {
      const change = Math.abs(this.currentOrder.change);
      const order_uuid = this.props.orderUuid;

      // Change Notification
      this.notification.add(
        markup(
          `<div><p style='font-size: 20px;'>Change Due: <strong style="font-size:24px;" class="text-success">${this.env.utils.formatCurrency(
            change,
          )}</strong></p></div>`,
        ),
        {
          autocloseDelay: 10000,
          type: "info",
          buttons: [
            {
              name: "Refund",
              onClick: () => {
                this.pos.navigate("TicketScreen", {
                  stateOverride: {
                    filter: "SYNCED",
                    selectedOrderUuid: order_uuid,
                  },
                });
              },
              // class: "btn-primary",   // Optional if needed
            },
            {
              name: "Print Receipt", // REQUIRED key
              onClick: () => {
                this.pos.printReceipt({
                  order: this.pos.models["pos.order"].getBy("uuid", order_uuid),
                });
              },
              // class: "btn-primary",   // Optional if needed
            },
          ],
        },
      );
    }
  },
});

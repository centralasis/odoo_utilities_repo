import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { patch } from "@web/core/utils/patch";

patch(ActionpadWidget, {
  props: {
    ...ActionpadWidget.props,
    cashValidateAmount: { optional: true },
    change: { optional: true },
  },
});

patch(ActionpadWidget.prototype, {
  setup() {
    super.setup(...arguments);
  },

  getScreen() {
    const screen = this.pos.router.state.current;
    if (screen === "TicketScreen") {
      return false;
    }
    return true;
  },
});

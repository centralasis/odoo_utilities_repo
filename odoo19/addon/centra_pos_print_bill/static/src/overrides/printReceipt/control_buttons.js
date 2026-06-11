import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { useService } from "@web/core/utils/hooks";
import { useAsyncLockedMethod } from "@point_of_sale/app/hooks/hooks";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons.prototype, {
  setup() {
    super.setup(...arguments);
    this.printer = useService("printer");
    this.clickPrintBill = useAsyncLockedMethod(this.clickPrintBill);
  },
  async clickPrintBill() {
    // Need to await to have the result in case of automatic skip screen.
    await this.pos.printReceipt({
      printBillActionTriggered: true,
    });
  },
});

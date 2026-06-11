import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";
import { useState } from "@odoo/owl";

patch(ProductScreen.prototype, {
  setup() {
    super.setup(...arguments);
    this.precision5 = this.sugestedPaymentAmount(5);
    this.precision10 = this.sugestedPaymentAmount(10);
    this.precision20 = this.sugestedPaymentAmount(20);
    this.change = useState({
      isChange: false,
      toggleChange: this.toggleChange.bind(this),
    });
  },

  toggleChange() {
    this.change.isChange = !this.change.isChange;
  },

  autoValidateOrder(amount = false) {
    const pos = usePos();
    pos.pay(amount);
  },

  getvalues() {
    if (this.change?.isChange) {
      return Math.round(((this.currentOrder?.totalDue || 0) % 1) * 100) || 0;
    }
    return this.currentOrder?.totalDue || 0;
  },

  proccessPayment(amount) {
    if (this.change?.isChange) {
      const decimalPart = parseFloat(amount.replace("X", ""));
      return Math.floor(this.currentOrder?.totalDue || 0) + decimalPart;
    }
    return amount;
  },

  sugestedPaymentAmount(precision) {
    const totalDue = this.getvalues();
    const value = Math.ceil(totalDue / precision) * precision;
    if (value === 0) {
      return;
    }
    if (this.change?.isChange && Number.isInteger(totalDue)) {
      if (value >= 100) {
        return;
      }
      return `${"X"}.${value == 5 ? "05" : value}`;
    }
    return Math.ceil(totalDue / precision) * precision;
  },

  cashValidate() {
    const totalDue = this.currentOrder?.totalDue || 0;
    if (this.change?.isChange) {
      return {
        text: "Cash +",
        cashPaid: Math.ceil(totalDue),
      };
    } else {
      return { text: "Cash", cashPaid: totalDue };
    }
  },
  getCashValidationButtons() {
    const denominations = [5, 10, 20, 50, 100]
      .map((item) => this.sugestedPaymentAmount(item))
      .filter((v) => v !== undefined)
      .sort((a, b) => a - b);
    const changeDenominations = [5, 10, 20, 25]
      .map((item) => this.sugestedPaymentAmount(item))
      .filter((v) => v !== undefined)
      .sort((a, b) => a - b);
    const list_denominations = [
      ...new Set(this.change?.isChange ? changeDenominations : denominations),
    ];

    return list_denominations;
  },
});

import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";

const { DateTime } = luxon;

patch(TicketScreen.prototype, {
  async onDoRefund(autoValidateOrder = false) {
    const order = this.getSelectedOrder();

    if (order && this._doesOrderHaveSoleItem(order)) {
      if (!this._prepareAutoRefundOnOrder(order)) {
        // Don't proceed on refund if preparation returned false.
        return;
      }
    }

    if (!order || !this.getHasItemsToRefund()) {
      return;
    }

    const partner = order.getPartner();
    // The order that will contain the refund orderlines.
    // We select the order if it is empty, else we create a new one.
    const destinationOrder = this._getEmptyOrder(partner);

    destinationOrder.is_refund = true;
    destinationOrder.pricelist_id = order.pricelist_id;
    // Add orderline for each toRefundDetail to the destinationOrder.
    const lines = [];
    for (const refundDetail of this._getRefundableDetails(partner, order)) {
      const refundLine = refundDetail.line;
      const alreadyRefundedLots = refundLine.refund_orderline_ids
        .filter((item) => !["cancel", "draft"].includes(item.order_id.state))
        .flatMap((item) => item.pack_lot_ids)
        .map((pack_lot) => pack_lot.lot_name);
      const options = refundLine.pack_lot_ids
        .map((p) => p.lot_name)
        .filter((lotName) => !alreadyRefundedLots.includes(lotName));
      const line = this.pos.models["pos.order.line"].create({
        qty: -refundDetail.qty,
        price_unit: refundLine.price_unit,
        product_id: refundLine.product_id,
        order_id: destinationOrder,
        discount: refundLine.discount,
        tax_ids: refundLine.tax_ids.map((tax) => ["link", tax]),
        refunded_orderline_id: refundLine,
        // Only include as many pack_lot_ids as the refunded quantity requires.
        pack_lot_ids: options
          .slice(0, refundDetail.qty)
          .map((lotName) => ["create", { lot_name: lotName }]),
        price_type: "automatic",
      });
      lines.push(line);
      refundDetail.destination_order_uuid = destinationOrder.uuid;
    }
    // link the refund combo lines
    const refundComboParentLines = lines.filter(
      (l) => l.refunded_orderline_id.combo_line_ids.length > 0
    );
    for (const refundComboParent of refundComboParentLines) {
      const children = refundComboParent.refunded_orderline_id.combo_line_ids
        .map((l) => l.refund_orderline_ids)
        .flat();
      refundComboParent.combo_line_ids = [["link", ...children]];
    }

    //Add a check too see if the fiscal position exist in the pos
    if (order.fiscal_position_not_found) {
      this.dialog.add(AlertDialog, {
        title: _t("Fiscal Position not found"),
        body: _t(
          "The fiscal position used in the original order is not loaded. Make sure it is loaded by adding it in the pos configuration."
        ),
      });
      return;
    }

    if (order.fiscal_position_id) {
      destinationOrder.fiscal_position_id = order.fiscal_position_id;
    }
    // Set the partner to the destinationOrder.
    this.setPartnerToRefundOrder(partner, destinationOrder);
    destinationOrder.refunded_order_id = order;
    this.pos.setOrder(destinationOrder);
    await this.addAdditionalRefundInfo(order, destinationOrder);

    this.postRefund(destinationOrder);
    this.pos.ticket_screen_mobile_pane = "left";
    destinationOrder.setScreenData({ name: "PaymentScreen" });
    this.pos.navigate("PaymentScreen", {
      orderUuid: destinationOrder.uuid,
    });
  },
});

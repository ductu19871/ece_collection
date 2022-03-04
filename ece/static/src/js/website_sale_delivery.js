odoo.define('ece.checkout', function (require) {
    'use strict';
    // var Checkout = require('website_sale_delivery.checkout');
    
    var core = require('web.core');
    var publicWidget = require('web.public.widget');

    var _t = core._t;
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();


    publicWidget.registry.websiteSaleDelivery.include({
        
        start: function () {
            // console.log('1232131231231232((d4))')
            var self = this;
            var $carriers = $('input[name1="delivery_type"]');
            // console.log('**$carriers  find in publicWidget.registry.websiteSaleDelivery',$carriers)
            var $payButton = $('#o_payment_form_pay');
            // Workaround to:
            // - update the amount/error on the label at first rendering
            // - prevent clicking on 'Pay Now' if the shipper rating fails
            console.log("$carriers.length > 0", $carriers.length > 0,$carriers.length )
            if ($carriers.length > 0) {
                if ($carriers.filter(':checked').length === 0) {
                    $payButton.prop('disabled', true);
                    var disabledReasons = $payButton.data('disabled_reasons') || {};
                    disabledReasons.carrier_selection = true;
                    $payButton.data('disabled_reasons', disabledReasons);
                }
                // $carriers.filter(':checked').off('click'); tắt đoạn này
                console.log("$carriers.length > 0", $carriers.length > 0,$carriers.length )
                $carriers.filter(':checked').off('click');
            }
    
            // Asynchronously retrieve every carrier price
            _.each($carriers, function (carrierInput, k) {
                self._showLoading($(carrierInput));
                self._rpc({
                    route: '/shop/carrier_rate_shipment',
                    params: {
                        'carrier_id': carrierInput.value,
                        'company_id':parseInt($(carrierInput).attr('company'))
                    },
                }).then(self._handleCarrierUpdateResultBadge.bind(self));
            });
    
            // return this._super.apply(this, arguments); tắt đoạn này
        },

        _handleCarrierUpdateResult: function (result) {
            // console.log('_handleCarrierUpdateResult this', this)
            // console.log('000000000000000000*** this.event',this.event)
            // console.log('111111111111*** this.event',this.event)
            // console.log('222222222222', this.event.currentTarget)
            this._handleCarrierUpdateResultBadge(result);
            var $payButton = $('#o_payment_form_pay');
            var $amountDelivery = $('#order_delivery .monetary_field');
            var $amountUntaxed = $('#order_total_untaxed .monetary_field');
            var $amountTax = $('#order_total_taxes .monetary_field');
            var $amountTotal = $('#order_total .monetary_field');
    
            if (result.status === true) {
                $amountDelivery.html(result.total_new_amount_delivery);
                $amountUntaxed.html(result.new_amount_untaxed);
                $amountTax.html(result.new_amount_tax);
                $amountTotal.html(result.new_amount_total);
                var disabledReasons = $payButton.data('disabled_reasons') || {};
                disabledReasons.carrier_selection = false;
                $payButton.data('disabled_reasons', disabledReasons);
                $payButton.prop('disabled', _.contains($payButton.data('disabled_reasons'), true));
            } else {
                $amountDelivery.html(result.new_amount_delivery);
                $amountUntaxed.html(result.new_amount_untaxed);
                $amountTax.html(result.new_amount_tax);
                $amountTotal.html(result.new_amount_total);
            }
        },

        _handleCarrierUpdateResultBadge: function (result) {
        
            // console.log('result.company_id in _handleCarrierUpdateResultBadge************', result.company_id)
            // delivery_carrier
            var $carrierBadge = $('div#delivery_carrier input[value=' + result.carrier_id + ']'+ '[company=' + result.company_id + '] ~ .o_wsale_delivery_badge_price');
            // console.log('$carrierBadge',$carrierBadge )
            if (result.status === true) {
                 // if free delivery (`free_over` field), show 'Free', not '$0'
                 if (result.is_free_delivery) {
                     $carrierBadge.text(_t('Free'));
                 } else {
                     $carrierBadge.html(result.new_amount_delivery);
                 }
                 $carrierBadge.removeClass('o_wsale_delivery_carrier_error');
            } else {
                $carrierBadge.addClass('o_wsale_delivery_carrier_error');
                $carrierBadge.text(result.error_message);
            }
        },


        _onCarrierClick: function (ev) {
            // console.log('ev.currentTarget***', ev.currentTarget)
            var $radio = $(ev.currentTarget).find('input[type="radio"]');
            // console.log('$radio.company',$radio.attr('company'))
            this._showLoading($radio);
            $radio.prop("checked", true);
            var $payButton = $('#o_payment_form_pay');
            $payButton.prop('disabled', true);
            var disabledReasons = $payButton.data('disabled_reasons') || {};
            disabledReasons.carrier_selection = true;
            $payButton.data('disabled_reasons', disabledReasons);
            dp.add(this._rpc({
                route: '/shop/update_carrier',
                params: {
                    carrier_id: $radio.val(),
                    company_id:$radio.attr('company')
                },
            })).then(this._handleCarrierUpdateResult.bind(this));
        },





    })
    
  

});

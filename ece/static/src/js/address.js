odoo.define('ece.address', function (require) {
    'use strict';
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var VariantMixin = require('sale.VariantMixin');
    var _t = core._t;
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();

    publicWidget.registry.WebsiteSale.include({
        events: _.extend({}, publicWidget.registry.WebsiteSale.events || {}, {
            'change select[name="state_id"]': '_onChangeState'
        }),
    }

    )

}
)
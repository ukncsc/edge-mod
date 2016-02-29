define([
    "knockout",
    "dcl/dcl",
    "common/cert-identity-shim",
    "common/cert-identity_showmodal-shim"
], function (ko, declare, EdgeIdentity, EdgeIdentityShowModal) {
    "use strict";


    return declare(EdgeIdentity, {
        declaredClass: "CERTIdentity",

        constructor: declare.superCall(function (sup) {
            return function (options) {
                sup.call(this, options);
                if (!options || !options.name) {
                    this.name("");
                }
                this.displayName = ko.computed(function () {
                    return this.name() ? this.name() : "Click To Edit";
                }, this);

                //Remove lines below when not using EdgeIdentity anymore;
                //it was the only way to override cancel to correct behaviour on cancel dialog
                this.cancel = function () {
                    this.restoreSnapshot();
                    this.modal.close();
                }.bind(this);

                this.template = "identity-element-popup";
            }
        }),

        ModelUI: function () {
            return EdgeIdentityShowModal({viewModel: this});
        },

        cancel: function () {
            this.restoreSnapshot();
            this.modal.close();
        }
    });
});

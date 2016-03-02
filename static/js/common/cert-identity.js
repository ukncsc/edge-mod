define([
    "knockout",
    "dcl/dcl",
    "common/identity",
    "common/cert-identity_showmodal-shim"
], function (ko, declare, EdgeIdentity, EdgeIdentityShowModal) {
    "use strict";

    var CERTIdentity = declare(EdgeIdentity, {
        declaredClass: "CERTIdentity",

        constructor: function () {
            this.template = "cert-identity-element-popup";
        },

        ModelUI: function () {
            return EdgeIdentityShowModal({viewModel: this});
        },

        cancel: function () {
            this.restoreSnapshot();
            this.modal.close();
        }
    });

    return CERTIdentity;
});

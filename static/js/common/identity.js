define([
    "knockout",
    "dcl/dcl",
    "common/cert-identity",
    "common/edge-identity",
    "common/cert-identity_showmodal",
    "text!config-service"
], function (ko, declare, CERTIdentity, EdgeIdentity, IdentityShowModal, ConfigService) {
    "use strict";

    var isEnabled = false;

    var config = Object.freeze(JSON.parse(ConfigService));
    var crm_config = config.crm_config;
    if (crm_config != undefined) {
        isEnabled = crm_config.enabled
    }

    var CERTIdentity = declare(CERTIdentity, {
        declaredClass: "CERTIdentity",

        constructor: function () {
            this.template = "cert-identity-element-popup";
        },

        ModelUI: function () {
            return IdentityShowModal({viewModel: this});
        }

    });

    var EdgeIdentity = declare(EdgeIdentity, {
        declaredClass: "EdgeIdentity",

        constructor: function () {
            this.template = "edge-identity-element-popup";
        },

        ModelUI: function () {
            return IdentityShowModal({viewModel: this});
        }

    });

    if (isEnabled) {
        return CERTIdentity;
    }

    return EdgeIdentity;

});

define([
    "knockout",
    "dcl/dcl",
    "common/identity",
    "common/edge-identity",
    "common/cert-identity_showmodal",
    "text!config-service"
], function (ko, declare, CRMIdentity, OriginalIdentity, IdentityShowModal, ConfigService) {
    "use strict";

    var config = Object.freeze(JSON.parse(ConfigService));
    var crm_config = config.crm_config;
    var isEnabled = crm_config.enabled;


    var CERTIdentity = declare(CRMIdentity, {
        declaredClass: "CERTIdentity",

        constructor: function () {
            this.template = "cert-identity-element-popup";
        },

        ModelUI: function () {
            return IdentityShowModal({viewModel: this});
        }

    });

    var EdgeIdentity = declare(OriginalIdentity, {
        declaredClass: "EdgeIdentity",

        constructor: function () {
            this.template = "identity-element-popup";
        },

        ModelUI: function () {
            return IdentityShowModal({viewModel: this});
        }

    });

    if (isEnabled) {
        return CERTIdentity;
    } else {
        return EdgeIdentity;
    }


});

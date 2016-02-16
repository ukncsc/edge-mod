define([
    "dcl/dcl",
    "knockout",
    "common/identity",
    "common/cert-identity_showmodal-shim",
    "common/cert-build-functions"
], function (declare, ko, EdgeIdentity, EdgeIdentityShowModal, buildFunctions) {
    "use strict";

     function CERTIdentity() {
        CERTIdentity.super.constructor.call(this);
    }


    buildFunctions.extend(CERTIdentity, EdgeIdentity);

    CERTIdentity.prototype.ModelUI  = function (model) {
        model.viewModel.template  = "cert-identity-element-popup";
        return EdgeIdentityShowModal({viewModel: model.viewModel});
    };


    return  CERTIdentity;
});

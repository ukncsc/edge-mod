define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "config/base-config"
], function (declare, ko, Modal, BaseConfig) {
    "use strict";

    return declare(BaseConfig, {
        declaredClass: "BacklinkConfig",

        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "Backlink rebuild", "mod_bl_task", "");
            }
        }),
        getConfig: function () {
        },
        onSave: function (reset) {
        } ,
        changesPending: function() {
            return false;
        }
    });
});

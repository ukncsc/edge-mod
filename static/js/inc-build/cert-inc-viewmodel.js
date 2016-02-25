define([
    "dcl/dcl",
    "knockout",
    "inc-build/cert-incident-builder-shim",
    "common/cert-build-base-view-model",
    "inc-build/cert-inc-build-section",
], function (declare, ko, incident_builder, BaseViewModel, Section) {
    "use strict";

    var IncidentViewModel = declare(BaseViewModel, {
        declaredClass: "IncidentViewModel",

        constructor: declare.superCall(function (sup) {
                return function () {
                    sup.call(this, incident_builder['ajax_uri'], Section);
                    this.stixtype = ko.observable("inc");
                }
            }
        ),
        getPublishResult: function (data, onResponseCallback) {
            postJSON(this.buildRestUrl("create_incident"), data, onResponseCallback);
        },

    });


    return IncidentViewModel;
});

define([
    "dcl/dcl",
    "inc-build/cert-incident-builder-shim",
    "common/cert-build-base-view-model",
    "inc-build/cert-inc-build-section",
], function (declare, incident_builder, BaseViewModel, Section) {
    "use strict";

    return declare(BaseViewModel, {
        declaredClass: "IncidentViewModel",

        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(
                    this,
                    incident_builder['ajax_uri'],
                    Section,
                    "Incident",
                    "create_incident",
                    "inc");
            }
        }),
    });
});

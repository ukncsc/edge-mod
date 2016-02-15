// When the DOM is ready, set up the viewmodel...

define([
    "dcl/dcl",
    "knockout",
    "inc-build/cert-incident-builder-shim",
    "inc-build/cert-inc-build-section",
    "common/cert-build-mode",
    "inc-build/cert-inc-viewmodel"
], function (declare, ko, incident_builder, section, BuildMode, ViewModel) {
    "use strict";
    var vm = new ViewModel();
    vm.loadStatic({
        "tlps_list": incident_builder.tlps_list,
        "trustgroups_list": incident_builder.trustgroups_list,
        "statuses_list": incident_builder.statuses_list,
        "confidence_list": incident_builder.confidence_list,
        "discovery_methods_list": incident_builder.discovery_methods_list,
        "intended_effects_list": incident_builder.intended_effects_list,
        "effects_list": incident_builder.effects_list
    });

    vm.id(incident_builder.id);

    if (incident_builder.mode == "Build") {
        vm.mode().value(BuildMode.prototype.MODES.CREATE);
        vm.initDraft(incident_builder["default_tlp"]);
        vm.id_ns(incident_builder.id_ns);
    } else if (incident_builder.mode == "Edit") {
        vm.mode().value(builder.BuildMode.prototype.MODES.EDIT);
        vm.loadObject(incident_builder.id);
    } else {
        vm.mode().value(builder.BuildMode.prototype.MODES.VIEW);
        vm.loadObject(incident_builder.id);
    }

    ko.applyBindings(vm);
});

require([
    "knockout",
    "ind-build/builder-shim",
    "ind-build/indicator-builder-shim",
    "ind-build/change-tracker",
    "ind-build/cert-ind-build-viewmodel",
    "ind-build/custom-observables",
    "ind-build/custom-builder-sections"
], function (ko, builder, indicator_builder, ChangeTracker, ViewModel) {
    "use strict";

    // ind-build-viewmodel-setup
    indicator_builder.vm = new ViewModel();
    indicator_builder.vm.tracker = ChangeTracker.create(indicator_builder.vm.section().options());

    // ind-build-ready
    indicator_builder.vm.loadStatic({
        "tlps_list": indicator_builder.tlps_list,
        "trustgroups_list": indicator_builder.trustgroups_list,
        "indicatorTypes": indicator_builder.indicatorTypes,
        "confidence_list": indicator_builder.confidence_list,
        "kill_chain_phase_list": indicator_builder.kill_chain_phase_list
    });

    indicator_builder.vm.id(indicator_builder.id);

    if (indicator_builder.mode == "Build") {
        indicator_builder.vm.mode().value(builder.BuildMode.prototype.MODES.CREATE);
        indicator_builder.vm.initDraft(indicator_builder["default_tlp"]);
        indicator_builder.vm.id_ns(indicator_builder.id_ns);
    } else if (indicator_builder.mode == "Edit") {
        indicator_builder.vm.mode().value(builder.BuildMode.prototype.MODES.EDIT);
        indicator_builder.vm.loadObject(indicator_builder.id);
    } else {
        indicator_builder.vm.mode().value(builder.BuildMode.prototype.MODES.VIEW);
        indicator_builder.vm.loadObject(indicator_builder.id);
    }

    // ind-build-ko-setup
    ko.applyBindings(indicator_builder.vm);

    setTimeout(function () {
        document.getElementById("content").style.visibility = "visible";
    }, 10);
});

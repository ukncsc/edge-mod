require([
    "knockout",
    "cert-ind-build/builder-shim",
    "cert-ind-build/indicator-builder-shim",
    "cert-ind-build/change-tracker",
    "cert-ind-build/custom-builder-sections",
    "cert-ind-build/custom-observables"
], function (ko, builder, indicator_builder, ChangeTracker) {
    "use strict";

    // ind-build-viewmodel-setup
    indicator_builder.vm = new indicator_builder.viewModel();
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

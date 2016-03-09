require([
    "knockout",
    "ind-build/builder-shim",
    "ind-build/indicator-builder-shim",
    "common/change-tracker",
    "ind-build/cert-ind-build-viewmodel",
    "ind-build/custom-observables",
    "ind-build/custom-builder-sections"
], function (ko, builder, indicator_builder, ChangeTracker, ViewModel) {
    "use strict";

    // ind-build-viewmodel-setup
    indicator_builder.vm = new ViewModel();
    var vm = indicator_builder.vm;

    vm.tracker = ChangeTracker.create(vm.section().options());

    // ind-build-ready
    vm.loadStatic({
        "tlps_list": indicator_builder.tlps_list,
        "trustgroups_list": indicator_builder.trustgroups_list,
        "indicatorTypes": indicator_builder.indicatorTypes,
        "confidence_list": indicator_builder.confidence_list,
        "kill_chain_phase_list": indicator_builder.kill_chain_phase_list
    });

    vm.id(indicator_builder.id);

    if (indicator_builder.mode == "Build") {
        vm.mode().value(builder.BuildMode.prototype.MODES.CREATE);
        vm.initDraft(indicator_builder["default_tlp"]);
        vm.id_ns(indicator_builder.id_ns);
        if (indicator_builder.draft_id) {
            vm.loadDraft(indicator_builder.draft_id);
        }
    } else if (indicator_builder.mode == "Edit") {
        vm.mode().value(builder.BuildMode.prototype.MODES.EDIT);
        vm.loadObject(indicator_builder.id);
    } else {
        vm.mode().value(builder.BuildMode.prototype.MODES.VIEW);
        vm.loadObject(indicator_builder.id);
    }

    // ind-build-ko-setup
    ko.applyBindings(indicator_builder.vm);

    setTimeout(function () {
        document.getElementById("content").style.visibility = "visible";
    }, 10);
});

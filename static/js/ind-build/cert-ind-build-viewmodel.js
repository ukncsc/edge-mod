define([
    "dcl/dcl",
    "knockout",
    "ind-build/indicator-builder-shim",
    "common/cert-build-base-view-model"
], function (declare, ko, indicator_builder, BaseViewModel) {
    "use strict";

    return declare(BaseViewModel, {
        declaredClass: "IndicatorViewModel",

        constructor: declare.superCall(function (sup) {
                return function () {
                    sup.call(this, indicator_builder['ajax_uri'], indicator_builder.Section, "Indicator", "create_indicator", "ind");
                    this.compositionType = ko.observable("OR");
                    this.builderMode = ko.observable(new indicator_builder.ObservableBuildMode());
                }
            }
        ),

        selectBatchBuildMode: function () {
            var observables = this.section().findByLabel("Observables");
            this.section().select(observables());
            this.builderMode().value(indicator_builder.ObservableBuildMode.prototype.MODES.BATCH);
            observables().showCandidateItems();
        },

        _serialize: declare.superCall(function (sup) {
                return function () {
                    var data = sup.call(this);
                    data.composition_type = this.compositionType();
                    return data;
                }
            }
        ),

        _serializeFromServer: declare.superCall(function (sup) {
                return function (dataItemName, response) {
                    sup.call(this, dataItemName, response);
                    this.compositionType(response[dataItemName]["composition_type"] || "OR");
                }
            }
        )
    });
});

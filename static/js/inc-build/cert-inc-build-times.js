define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "inc-build/cert-inc-build-time"
], function (declare, ko, AbstractBuilderForm, Time) {
    "use strict";


    var Times = declare(AbstractBuilderForm, {
        declaredClass: "Times",

        constructor: declare.superCall(function(sup) {
                return function () {
                    sup.call(this, "Times");

                    this.time_types_list = ko.observableArray([]);
                    this.time_zones_list = ko.observableArray([]);
                    this.time_types = ko.observableArray([]);
                }
            }),

        loadStatic: function(optionsList) {
            this.time_types_list(optionsList['time_types_list']);
            this.time_zones_list(optionsList['time_zones_list']);

        },

        removeTimeType : function(a) {
            this.time_types.remove(a);
        },

        addTimeType : function() {
            var newTime = new Time();
            this.time_types.push(newTime);
        }
            }
        )
    return Times;
    });




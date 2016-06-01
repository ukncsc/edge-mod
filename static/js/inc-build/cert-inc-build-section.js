define([
    "knockout",
    "dcl/dcl",
    "inc-build/cert-inc-build-attributed-actors",
    "inc-build/cert-inc-build-time-panel",
    "inc-build/cert-inc-build-categories",
    "inc-build/cert-inc-build-discovery-methods",
    "inc-build/cert-inc-build-effects",
    "inc-build/cert-inc-build-general",
    "inc-build/cert-inc-build-intended-effects",
    "inc-build/cert-inc-build-leveraged-ttps",
    "inc-build/cert-inc-build-related-incidents",
    "inc-build/cert-inc-build-related-indicators",
    "inc-build/cert-inc-build-related-observables",
    "inc-build/cert-inc-build-trust-groups",
    "inc-build/cert-inc-build-victims",
    "inc-build/cert-inc-build-responders",
    "inc-build/cert-inc-build-coordinators",
    "inc-build/cert-inc-build-external-ids",
    "common/cert-messages"
], function (ko, declare, AttributedActors, Times, Categories, DiscoveryMethods, Effects, General, IntendedEffects, LeveragedTTPs, RelatedIncidents, RelatedIndicators, RelatedObservables, TrustGroups, Victims, Responders, Coordinators, ExternalIds, Messages) {
    "use strict";
    function indexBy(items, pname) {
        var indexed = {};
        ko.utils.arrayForEach(items(), function (item) {
            indexed[item()[pname]()] = item;
        });
        return indexed;
    }

    return declare(null, {
        declaredClass: "Section",
        constructor: function () {
            this.options = ko.observableArray([
                ko.observable(new General()),
                ko.observable(new Times()),
                ko.observable(new Categories()),
                ko.observable(new TrustGroups()),
                ko.observable(new Effects()),
                ko.observable(new Coordinators()),
                ko.observable(new Victims()),
                ko.observable(new Responders()),
                ko.observable(new DiscoveryMethods()),
                ko.observable(new IntendedEffects()),
                ko.observable(new RelatedIndicators()),
                ko.observable(new RelatedObservables()),
                ko.observable(new LeveragedTTPs()),
                ko.observable(new AttributedActors()),
                ko.observable(new RelatedIncidents()),
                ko.observable(new ExternalIds())
            ]);
            this._byLabel = indexBy(this.options, "label");
            this.value = ko.observable(
                this.options()[0]()
            );
        },

        loadStatic: function (optionLists) {
            ko.utils.arrayForEach(this.options(), function (option) {
                option().loadStatic(optionLists);
            });
        },

        load: function (data) {
            ko.utils.arrayForEach(this.options(), function (option) {
                option().load(data);
            });
        },

        doValidation: function () {
            var msgs = new Messages();
            ko.utils.arrayForEach(this.options(), function (option) {
                var optionMsgs = option().doValidation();
                if (optionMsgs instanceof Messages && optionMsgs.hasMessages()) {
                    msgs.addMessages(optionMsgs);
                }
            });
            return msgs;
        },

        save: function () {
            var data = {};
            ko.utils.arrayForEach(this.options(), function (option) {
                var optionData = option().save();
                if (optionData instanceof Object) {
                    ko.utils.objectForEach(optionData, function (name, value) {
                        data[name] = value;
                    });
                }
            });
            return data;
        },

        findByLabel: function (label) {
            return this._byLabel[label];
        },

        select: function (item) {
            this.value(item);
        },


        counts: function (item) {
            return +(item.count()) || "";
        },

    });
})
;

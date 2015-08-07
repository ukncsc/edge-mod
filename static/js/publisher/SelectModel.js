define(["knockout", "dcl/dcl"], function (ko, declare) {
    "use strict";

    var TYPES = Object.freeze({
        "coa": {"collection": "courses_of_action", "label": "Course Of Action", "code": "coa"},
        "ttp": {"collection": "ttps.ttps", "label": "TTP", "code": "ttp"},
        "incident": {"collection": "incidents", "label": "Incident", "code": "inc"},
        "indicator": {"collection": "indicators", "label": "Indicator", "code": "ind"},
        "observable": {"collection": "observables.observables", "label": "Observable", "code": "obs"}
    });

    function findType (/*String*/ id) {
        var pattern = new RegExp(
            "^[a-z\d-]+:([a-z\d]+)-[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$"
        );
        var match = pattern.exec(id.toLowerCase());
        return TYPES[match && match[1]];
    }

    function findById (/*Object*/ stixPackage, /*String*/ id) {
        if (!(stixPackage && typeof id === "string")) {
            return null;
        }
        var listToSearch = safeGet(stixPackage, findType(id).collection) || [];
        if (!listToSearch) {
            return null;
        }
        return ko.utils.arrayFirst(listToSearch, function (item) {
            return item.id === id;
        }, this);
    }

    function safeGet (/*Object*/ object, /*String*/ propertyPath) {
        var propertyNames = propertyPath.split(".");
        var current = object;
        for (var i = 0, len = propertyNames.length; current && i < len; i++) {
            var p = propertyNames[i];
            if (p in current) {
                current = current[p];
            } else {
                current = null;
                break;
            }
        }
        return current;
    }

    function safeArrayGet(/*Object*/ object, /*String*/ propertyPath, /*function*/ itemCallback) {
        var collection = safeGet(object, propertyPath);
        return collection instanceof Array && collection.length > 0
            ? ko.utils.arrayMap(collection, itemCallback)
            : null;
    }

    function safeListGet (/*Object*/ object, /*String*/ propertyPath, /*String?*/ valueKey, /*String?*/ delimiter) {
        var itemPropertyPath = valueKey || "value";
        return (safeArrayGet(object, propertyPath, function (item) {
            return safeGet(item, itemPropertyPath);
        }) || []).join(delimiter || ", ");
    }

    function safeReferenceArrayGet (
        /*Object*/ object, /*String*/ propertyPath,
        /*Object*/ stixPackage, /*String*/ idrefKey,
        /*function*/ modelBuilderCallback
    ) {
        return safeArrayGet(object, propertyPath, function (item) {
            return modelBuilderCallback(findById(stixPackage, safeGet(item, idrefKey)));
        });
    }

    function buildTTP (/*Object*/ ttp) {
        return ko.observable({
            id: safeGet(ttp, "id"),
            title: safeGet(ttp, "title"),
            tlp: safeGet(ttp, "handling.0.marking_structures.0.color"),
            intendedEffects: safeListGet(ttp, "intended_effects", "value.value")
        });
    }

    function buildIncident (/*Object*/ incident) {
        return ko.observable({
            id: safeGet(incident, "id"),
            title: safeGet(incident, "title"),
            tlp: safeGet(incident, "handling.0.marking_structures.0.color"),
            intendedEffects: safeListGet(incident, "intended_effects", "value.value")
        });
    }

    function buildIndicator (/*Object*/ indicator) {
        return ko.observable({
            id: safeGet(indicator, "id"),
            title: safeGet(indicator, "title"),
            tlp: safeGet(indicator, "handling.0.marking_structures.0.color"),
            types: safeListGet(indicator, "indicator_types")
        });
    }

    function buildObservable (/*Object*/ observable) {
        var propertyList = ko.observableArray([]);
        var properties = safeGet(observable, "object.properties");
        ko.utils.objectForEach(properties, function (name, value) {
            if (name !== "xsi:type" && typeof value === "string" && value.length > 0) {
                propertyList.push({label: name, value: value});
            }
        });
        return ko.observable({
            id: safeGet(observable, "id"),
            title: safeGet(observable, "title"),
            type: safeGet(properties, "xsi:type"),
            properties: propertyList
        });
    }

    function buildCOA (/*Object*/ coa) {
        var propertyList = ko.utils.arrayFilter([
            { label: "stage", value: safeGet(coa, "stage.value")},
            { label: "type", value: safeGet(coa, "type.value")},
            { label: "objective", value: safeGet(coa, "objective.description")},
            { label: "impact", value: safeGet(coa, "impact.description")},
            { label: "efficacy", value: safeGet(coa, "efficacy.description")},
            { label: "cost", value: safeGet(coa, "cost.description")}
        ], function (property) {
            return typeof property.value === "string" && property.value.length > 0;
        });
        return ko.observable({
            id: safeGet(coa, "id"),
            title: safeGet(coa, "title"),
            tlp: safeGet(coa, "handling.0.marking_structures.0.color"),
            properties: ko.observableArray(propertyList)
        });
    }

    return declare(null, {

        constructor: function (rootId, stixPackage) {
//console.log(rootId);
//console.dir(stixPackage);
            this.rootId = ko.observable(rootId);
            this.stixPackage = ko.observable(stixPackage);

            this.root = ko.computed(function () {
                return findById(this.stixPackage(), this.rootId());
            }, this);
            this.type = ko.computed(function () {
                return findType(this.rootId());
            }, this);
            this.typeCode = ko.computed(function () {
                return this.type().code;
            }, this);
            this.typeText = ko.computed(function () {
                return this.type().label;
            }, this);

            this.title = ko.computed(function () {
                return safeGet(this.root(), "title");
            }, this);
            this.shortDescription = ko.computed(function () {
                return safeGet(this.root(), "short_description");
            }, this);
            this.description = ko.computed(function () {
                return safeGet(this.root(), "description");
            }, this);
            this.tlp = ko.computed(function () {
                return safeGet(this.root(), "handling.0.marking_structures.0.color");
            }, this);

            this.status = ko.computed(function () {
                return safeGet(this.root(), "status.value");
            }, this);
            this.reporter = ko.computed(function () {
                return safeGet(this.root(), "reporter.identity.name");
            }, this);
            this.confidence = ko.computed(function () {
                return safeGet(this.root(), "confidence.value.value");
            }, this);
            this.responders = ko.computed(function () {
                return safeListGet(this.root(), "responders", "identity.name");
            }, this);
            this.intendedEffects = ko.computed(function () {
                return safeListGet(this.root(), "intended_effects", "value.value");
            }, this);
            this.discoveryMethods = ko.computed(function () {
                return safeListGet(this.root(), "discovery_methods");
            }, this);
            this.impactAssessment = ko.computed(function () {
                return safeListGet(this.root(), "impact_assessment.effects");
            }, this);
            this.leveragedTTPs = ko.computed(function () {
                return safeReferenceArrayGet(this.root(), "leveraged_ttps.ttps", this.stixPackage(), "ttp.idref", buildTTP);
            }, this);
            this.relatedIncidents = ko.computed(function () {
                return safeReferenceArrayGet(this.root(), "related_incidents.incidents", this.stixPackage(), "incident.idref", buildIncident);
            }, this);
            this.relatedIndicators = ko.computed(function () {
                return safeReferenceArrayGet(this.root(), "related_indicators.indicators", this.stixPackage(), "indicator.idref", buildIndicator)
                    || safeReferenceArrayGet(this.root(), "related_indicators.related_indicators", this.stixPackage(), "indicator.idref", buildIndicator);
            }, this);
            this.relatedObservables = ko.computed(function () {
                return safeReferenceArrayGet(this.root(), "related_observables.observables", this.stixPackage(), "observable.idref", buildObservable);
            }, this);
            this.producer = ko.computed(function () {
                return safeGet(this.root(), "producer.identity.name");
            }, this);
            this.indicatorTypes = ko.computed(function () {
                return safeListGet(this.root(), "indicator_types");
            }, this);
            this.observable = ko.computed(function () {
                return findById(this.stixPackage(), safeGet(this.root(), "observable.idref"));
            }, this);
            this.observables = ko.computed(function () {
                return safeReferenceArrayGet(this.observable(), "observable_composition.observables", this.stixPackage(), "idref", buildObservable);
            }, this);
            this.suggestedCOAs = ko.computed(function () {
                return safeReferenceArrayGet(this.root(), "suggested_coas.suggested_coas", this.stixPackage(), "course_of_action.idref", buildCOA);
            }, this);
//console.dir(this.root());
        },

        onPublish: function () {
            if (confirm("Are you absolutely sure you want to publish this package?")) {
                postJSON("/adapter/publisher/ajax/publish/", {
                    root_id: this.rootId()
                }, this._onPublishResponseReceived.bind(this));
            }
        },

        _onPublishResponseReceived: function (response) {
            var message = response["success"] ? "The package was successfully published." : response["error_message"];
            alert(message);
        }
    });
});

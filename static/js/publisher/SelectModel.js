define(["knockout", "dcl/dcl"], function (ko, declare) {
    "use strict";

    var TYPES = Object.freeze({
        "coa": {"collection": "courses_of_action", "label": "Course Of Action", "code": "coa"},
        "ttp": {"collection": "ttps", "label": "TTP", "code": "ttp"},
        "incident": {"collection": "incidents", "label": "Incident", "code": "inc"},
        "indicator": {"collection": "indicators", "label": "Indicator", "code": "ind"},
        "observable": {"collection": "observables", "label": "Observable", "code": "obs"}
    });

    function findType (/*String*/ id) {
        var pattern = new RegExp(
            "^[a-z\d-]+:([a-z\d]+)-[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$"
        );
        var match = pattern.exec(id.toLowerCase());
        return TYPES[match && match[1]];
    }

    function findById (/*String*/ id) {
        var listToSearch = this.stixPackage()[findType(id).collection];
        return ko.utils.arrayFirst(listToSearch, function (item) {
            return item.id === id;
        }, this);
    }

    function safeGet (/*Object*/ object, /*String*/ propertyPath) {
        var propertyNames = propertyPath.split(".");
        var current = object;
        for (var i = 0, len = propertyNames.length; i < len; i++) {
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

    function safeListGet (/*Object*/ object, /*String*/ propertyPath, /*String?*/ valueKey, /*String?*/ delimiter) {
        var list = safeGet(object, propertyPath);
        var itemPropertyPath = valueKey || "value";
        return list instanceof Array && list.length > 0
            ? ko.utils.arrayMap(list, function (item) {
                return safeGet(item, itemPropertyPath);
            }).join(delimiter || ", ")
            : null;
    }

    return declare(null, {

        constructor: function (rootId, stixPackage) {
//console.log(rootId);
//console.dir(stixPackage);
            this.rootId = ko.observable(rootId);
            this.stixPackage = ko.observable(stixPackage);

            this.root = ko.computed(findById.bind(this, this.rootId()));
            this.type = ko.computed(findType.bind(this, this.rootId()));
            this.typeCode = ko.computed(function () {
                return this.type().code;
            }, this);
            this.typeText = ko.computed(function () {
                return this.type().label;
            }, this);

            // core properties
            this.title = ko.computed(safeGet.bind(this, this.root(), "title"));
            this.shortDescription = ko.computed(safeGet.bind(this, this.root(), "short_description"));
            this.description = ko.computed(safeGet.bind(this, this.root(), "description"));
            this.tlp = ko.computed(safeGet.bind(this, this.root(), "handling.0.marking_structures.0.color"));

            // incident properties
            this.status = ko.computed(safeGet.bind(this, this.root(), "status.value"));
            this.reporter = ko.computed(safeGet.bind(this, this.root(), "reporter.identity.name"));
            this.confidence = ko.computed(safeGet.bind(this, this.root(), "confidence.value.value"));
            this.intendedEffects = ko.computed(safeListGet.bind(this, this.root(), "intended_effects", "value.value"));
            this.discoveryMethods = ko.computed(safeListGet.bind(this, this.root(), "discovery_methods"));
            this.impactAssessment = ko.computed(safeListGet.bind(this, this.root(), "impact_assessment.effects"));

console.dir(this.root());
        },

        onPublish: function () {
            postJSON("/adapter/publisher/ajax/publish/", {
                root_id: this.rootId()
            }, this._onPublishResponseReceived.bind(this));
        },

        _onPublishResponseReceived: function (response) {
            var message = response["success"] ? "The package was successfully published." : response["error_message"];
            alert(message);
        }
    });
});

define([
    "dcl/dcl",
    "knockout",
    "stix/CourseOfAction",
    "stix/Incident",
    "stix/Indicator",
    "stix/Observable",
    "stix/TTP"
], function (declare, ko, CourseOfAction, Incident, Indicator, Observable, TTP) {
    "use strict";

    var TYPES = Object.freeze({
        "coa": {"class": CourseOfAction, "collection": "courses_of_action", "label": "Course Of Action", "code": "coa"},
        "ttp": {"class": TTP, "collection": "ttps.ttps", "label": "TTP", "code": "ttp"},
        "incident": {"class": Incident, "collection": "incidents", "label": "Incident", "code": "inc"},
        "indicator": {"class": Indicator, "collection": "indicators", "label": "Indicator", "code": "ind"},
        "observable": {"class": Observable, "collection": "observables.observables", "label": "Observable", "code": "obs"}
    });
    var TYPE_ALIASES = Object.freeze({
        "courseofaction": "coa"
    });

    function resolveAlias(type) {
        return TYPE_ALIASES[type] || type;
    }

    function findType(/*String*/ id) {
        var pattern = new RegExp(
            "^[a-z\\d-]+:([a-z\\d]+)-[a-f\\d]{8}-[a-f\\d]{4}-[a-f\\d]{4}-[a-f\\d]{4}-[a-f\\d]{12}$"
        );
        var match = pattern.exec(id.toLowerCase());
        if (!match) {
            throw new Error("Unable to derive type from id: " + id);
        }
        var type = TYPES[resolveAlias(match[1])];
        if (!type) {
            throw new TypeError("Unknown type: " + match[1]);
        }
        return type;
    }

    return declare(null, {
        constructor: function (stixPackage, rootId) {
            if (!(stixPackage instanceof Object)) {
                throw new Error("STIX package cannot be null or undefined");
            }
            this._data = stixPackage;
            this.root = this.findById(rootId);
            this.type = findType(rootId);
        },

        findById: function (/*String*/ id) {
            if (!(typeof id === "string")) {
                throw new Error("Identifier cannot be null or undefined");
            }
            var type = findType(id);
            var listToSearch = this.safeGet(this._data, type.collection);
            if (!listToSearch) {
                throw new Error("Object not found with id: " + id);
            }
            var data = ko.utils.arrayFirst(listToSearch, function (item) {
                return item.id === id;
            }, this);
            if (!data) {
                throw new Error("Object not found with id: " + id);
            }
            return new type.class(data, this);
        },

        safeGet: function (/*Object*/ stixObject, /*String*/ propertyPath) {
            var propertyNames = propertyPath.split(".");
            var current = stixObject;
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
        },

        safeArrayGet: function (/*Object*/ object, /*String*/ propertyPath,
                                /*function*/ itemCallback, /*Object?*/ itemCallbackBinding) {
            var collection = this.safeGet(object, propertyPath);
            var cb = itemCallbackBinding ? itemCallback.bind(itemCallbackBinding) : itemCallback;
            return collection instanceof Array && collection.length > 0
                ? ko.utils.arrayMap(collection, cb)
                : null;
        },

        safeListGet: function (/*Object*/ object, /*String*/ propertyPath,
                               /*String?*/ valueKey, /*String?*/ delimiter) {
            var itemPropertyPath = valueKey || "value";
            return (this.safeArrayGet(object, propertyPath, function (item) {
                return this.safeGet(item, itemPropertyPath);
            }, this) || []).join(delimiter || ", ");
        },

        safeReferenceArrayGet: function (/*Object*/ object, /*String*/ propertyPath,
                                         /*String*/ idrefKey) {
            return this.safeArrayGet(object, propertyPath, function (item) {
                return this.findById(this.safeGet(item, idrefKey));
            }, this);
        }

    });
});

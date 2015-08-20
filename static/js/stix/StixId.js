define([
    "dcl/dcl",
    "./CourseOfAction",
    "./Incident",
    "./Indicator",
    "./Observable",
    "./TTP"
], function (declare, CourseOfAction, Incident, Indicator, Observable, TTP) {
    "use strict";

    var TYPES = Object.freeze({
        "coa": {
            "class": CourseOfAction, "collection": "courses_of_action", "label": "Course Of Action", "code": "coa"
        },
        "ttp": {
            "class": TTP, "collection": "ttps.ttps", "label": "TTP", "code": "ttp"
        },
        "incident": {
            "class": Incident, "collection": "incidents", "label": "Incident", "code": "inc"
        },
        "indicator": {
            "class": Indicator, "collection": "indicators", "label": "Indicator", "code": "ind"
        },
        "observable": {
            "class": Observable, "collection": "observables.observables", "label": "Observable", "code": "obs"
        }
    });

    var TYPE_ALIASES = Object.freeze({
        "courseofaction": "coa"
    });

    function resolveAlias(type) {
        return TYPE_ALIASES[type] || type;
    }

    function findType(/*String*/ id) {
        var pattern = new RegExp(
            "^[a-z][\\w\\d-]+:([a-z]+)-[a-f\\d]{8}-[a-f\\d]{4}-[a-f\\d]{4}-[a-f\\d]{4}-[a-f\\d]{12}$"
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
        declaredClass: "StixId",
        constructor: function (id) {
            this._id = id;
            this._type = findType(id);
        },
        id: function () {
            return this._id;
        },
        type: function () {
            return this._type;
        }
    });
});

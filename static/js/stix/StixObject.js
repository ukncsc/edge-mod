define([
    "dcl/dcl",
    "knockout",
    "./ReviewValue",
    "kotemplate!labelled-field:./templates/labelled-field.html",
    "kotemplate!labelled-list-field:./templates/labelled-list-field.html",
    "kotemplate!optional-labelled-field:./templates/optional-labelled-field.html",
    "kotemplate!optional-labelled-list-field:./templates/optional-labelled-list-field.html",
    "kotemplate!grid-field:./templates/grid-field.html",
    "kotemplate!grid-properties-field:./templates/grid-properties-field.html",
    "kotemplate!common-fields:./templates/common.html"
], function (declare, ko, ReviewValue) {
    "use strict";

    function getNamespaceIfExists(id) {
        if (id != null) {
            return id.split(":", 2)[0]
        } else {
            return id
        }
    }

    return declare(null, {
        DEFER_EVALUATION: {
            deferEvaluation: true
        },
        constructor: function (data, stixPackage) {

            this.id = ko.observable(stixPackage.safeGet(data, "id"));

            var validation = stixPackage.validations().findByProperty(this.id(), "namespace");
            this.namespace = ko.observable(new ReviewValue(getNamespaceIfExists(this.id()), validation.state, validation.message));

            this.title = ko.observable(stixPackage.safeValueGet(this.id(), data, "title"));

            this.shortDescription = ko.observable(stixPackage.safeValueGet(this.id(), data, "short_description"));

            this.description = ko.observable(stixPackage.safeValueGet(this.id(), data, "description"));

            this.trustGroups = ko.observable(new ReviewValue(stixPackage.trustGroups(), null, null));

        }
    });
});

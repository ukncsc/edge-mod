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
        if(id != null ) {
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
            this.data = ko.observable(data);
            this.id = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "id");
            }, this);
            this.namespace = ko.computed(function () {
                var validation = stixPackage.validations().findByProperty(this.id(), "namespace");
                return new ReviewValue(getNamespaceIfExists(this.id()), validation.state, validation.message);
            }, this);
            this.title = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "title");
            }, this);
            this.shortDescription = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "short_description");
            }, this);
            this.description = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "description");
            }, this);
        }
    });
});

define([
    "dcl/dcl",
    "knockout",
    "./StixId",
    "./ReviewValue",
    "./ValidationInfo"
], function (declare, ko, StixId, ReviewValue, ValidationInfo) {
    "use strict";

    return declare(null, {
        declaredClass: "StixPackage",
        constructor: function (stixPackage, rootId, validationInfo) {
            if (!(stixPackage instanceof Object)) {
                throw new Error("STIX package cannot be null or undefined");
            }
            this._data = stixPackage;
            this._rootId = new StixId(rootId);
            this._validationInfo = new ValidationInfo(validationInfo || {});
            this.root = this.findById(this._rootId);
            this.type = this._rootId.type();
        },

        findById: function (stixId) {
            if (!(stixId instanceof StixId)) {
                throw new Error("Identifier must be a StixId: " + stixId);
            }
            var id = stixId.id();
            var type = stixId.type();
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

        findByStringId: function (/*String*/ id) {
            return this.findById(new StixId(id));
        },

        header: function () {
            return this._data["stix_header"] || {};
        },

        validations: function () {
            return this._validationInfo;
        },

        safeGet: function (/*Object*/ stixObject, /*String*/ propertyPath) {
            var propertyNames = propertyPath.split(".");
            var current = stixObject;
            for (var i = 0, len = propertyNames.length; current && i < len; i++) {
                var p = propertyNames[i];
                if (current.hasOwnProperty(p)) {
                    current = current[p];
                } else {
                    current = null;
                    break;
                }
            }
            return current;
        },

        safeValueGet: function(/*String*/ id, /*Object*/ object, /*String*/ propertyPath) {
            var simpleValue = this.safeGet(object, propertyPath);
            var validation = this._validationInfo.findByProperty(id, propertyPath);
            return new ReviewValue(simpleValue, validation.state, validation.message);
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
            var listValue = (this.safeArrayGet(object, propertyPath, function (item) {
                return this.safeGet(item, itemPropertyPath);
            }, this) || []).join(delimiter || ", ");
            // TODO: add id to method signature (or change safeValueGet to work this way)
            var id = typeof object.id === "function" ? object.id() : object.id;
            var validation = this._validationInfo.findByProperty(id, propertyPath);
            return new ReviewValue(listValue, validation.state, validation.message);
        },

        safeReferenceArrayGet: function (/*Object*/ object, /*String*/ propertyPath,
                                         /*String*/ idrefKey) {
            return this.safeArrayGet(object, propertyPath, function (item) {
                return this.findById(new StixId(this.safeGet(item, idrefKey)));
            }, this);
        }

    });
});

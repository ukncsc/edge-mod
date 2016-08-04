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
            this._cache = {};
            this.root = this.findById(this._rootId);
            this.type = this._rootId.type();
        },

        findById: function (stixId) {
            if (!(stixId instanceof StixId)) {
                throw new Error("Identifier must be a StixId: " + stixId);
            }
            var id = stixId.id();
            var stixObject = null;
            if (id in this._cache) {
                stixObject = this._cache[id];
            } else {
                var type = stixId.type();
                if (id === this._data.id) { //Show this package.
                    data = this._data;
                } else {
                    var listToSearch = this.safeGet(this._data, type.collection);
                    if (listToSearch) {
                        // Need to refactor, should be able to pass in actual collection but each package is wrapped as an object
                        // with the key package. if can't change input then refactor into parameterised helper method
                        if (type.label == "Package") {
                            var data = ko.utils.arrayFirst(listToSearch, function (item) {
                                return item.package.id === id;
                            }, this);
                        } else {
                            var data = ko.utils.arrayFirst(listToSearch, function (item) {
                                return item.id === id;
                            }, this);
                        }
                        if (data === null) {
                            data = {
                                id: id,
                                title: "(External)"
                            };
                        }
                    }
                }
                //same problem as above.
                if (type.label == "Package") {
                    stixObject = new type.class(data.package, this);
                } else {
                    stixObject = new type.class(data, this);
                }

                this._cache[id] = stixObject;
            }
            return stixObject;
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

        safeValueGet: function (/*String*/ id, /*Object*/ object, /*String*/ propertyPath, /*String?*/ validationPath) {
            var simpleValue = this.safeGet(object, propertyPath);
            var validation = this._validationInfo.findByProperty(id, validationPath || propertyPath);
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

        safeListGet: function (/*String*/ id, /*Object*/ object, /*String*/ propertyPath,
                               /*String?*/ valueKey, /*String?*/ validationPath, /*String?*/ delimiter) {
            var itemPropertyPath = valueKey || "value";
            var listValue = (this.safeArrayGet(object, propertyPath, function (item) {
                return (itemPropertyPath === ".") ? item : this.safeGet(item, itemPropertyPath);
            }, this) || []).join(delimiter || ", ");
            var validation = this._validationInfo.findByProperty(id, validationPath || propertyPath);
            return new ReviewValue(listValue, validation.state, validation.message);
        },

        safeReferenceArrayGet: function (/*String*/ id, /*Object*/ object, /*String*/ propertyPath,
                                         /*String*/ idrefKey, /*String?*/ validationPath) {
            var values = this.safeArrayGet(object, propertyPath, function (item) {
                return this.findById(new StixId(this.safeGet(item, idrefKey)));
            }, this);
            var validation = this._validationInfo.findByProperty(id, validationPath || propertyPath);
            return new ReviewValue(values, validation.state, validation.message);
        }
    });
});

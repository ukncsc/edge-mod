define([
    "dcl/dcl",
    "knockout",
    "./StixId",
    "./ReviewValue",
    "./AsyncReviewValue",
    "./ValidationInfo",
    "common/cert-identity",
    "text!config-service"
], function (declare, ko, StixId, ReviewValue, AsyncReviewValue, ValidationInfo, Identity, configService) {
    "use strict";

    var crmIsEnabled = false;

    var config = Object.freeze(JSON.parse(configService));
    var crm_config = config.crm_config;
    if (crm_config) {
        crmIsEnabled = crm_config.value.enabled;
    }

    return declare(null, {
        declaredClass: "StixPackage",
        constructor: function (stixPackage, rootId, trustGroups, validationInfo, edges) {
            if (!(stixPackage instanceof Object)) {
                throw new Error("STIX package cannot be null or undefined");
            }
            this._data = stixPackage;
            this._edges = edges;
            this._rootId = new StixId(rootId, this._edges);
            this._trustGroups = trustGroups;
            this._validationInfo = new ValidationInfo(validationInfo || {});
            this._cache = {};
            this.root = this.findById(this._rootId);
            this.type = this._rootId.type();
        },

        _mockExternalData: function (id) {
            return {
                id: id,
                title: "(External)"
            };
        },

        _findPackage: function (listToSearch, id) {
            var data = ko.utils.arrayFirst(listToSearch, function (item) {
                return item.package.id === id;
            }, this);
            if (data !== null) {
                return data.package
            }
            return null
        },

        _findStixObject: function (listToSearch, id) {
            return ko.utils.arrayFirst(listToSearch, function (item) {
                return item.id === id;
            }, this);
        },

        searchForStixData: function (listToSearch, type, id) {
            var data = null;
            if (type.label == "Package") {
                data = this._findPackage(listToSearch, id)
            } else {
                data = this._findStixObject(listToSearch, id);
            }
            if (data == null) {
                data = this._mockExternalData(id);
            }
            return data
        },

        findById: function (stixId) {
            if (!(stixId instanceof StixId)) {
                throw new Error("Identifier must be a StixId: " + stixId);
            }
            var id = stixId.id();

            if (id in this._cache) {
                return this._cache[id];
            }

            var stixObject = null;
            var type = stixId.type();
            var listToSearch = this.safeGet(this._data, type.collection);
            if (listToSearch) {
                var data = this.searchForStixData(listToSearch, type, id)
                stixObject = new type.class(data, this);
            } else {
                stixObject = new type.class(this._mockExternalData(id), this);
            }


            this._cache[id] = stixObject;

            return stixObject;
        },

        findByStringId: function (/*String*/ id) {
            return this.findById(new StixId(id, this._edges));
        },

        header: function () {
            return this._data["stix_header"] || {};
        },

        validations: function () {
            return this._validationInfo;
        },

        trustGroups: function () {
            return this._trustGroups;
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

        safeConcatenatedListGet: function (/*String*/ id, /*Object*/ object, /*String*/ propertyPath,
                                           /*String*/ valueKey, /*String*/secondValueKey, /*String?*/ validationPath) {
            var listValue = (this.safeArrayGet(object, propertyPath, function (item) {
                var value1 = (valueKey === ".") ? item : this.safeGet(item, valueKey);
                var value2 = (secondValueKey === ".") ? item : this.safeGet(item, secondValueKey);
                return value1 + "(" + value2 + ")"
            }, this) || []).join(", ");
            var validation = this._validationInfo.findByProperty(id, validationPath || propertyPath);
            return new ReviewValue(listValue, validation.state, validation.message);
        },

        safeReferenceArrayGet: function (/*String*/ id, /*Object*/ object, /*String*/ propertyPath,
                                         /*String*/ idrefKey, /*String?*/ validationPath) {
            var values = this.safeArrayGet(object, propertyPath, function (item) {
                return this.findById(new StixId(this.safeGet(item, idrefKey), this._edges));
            }, this);
            var validation = this._validationInfo.findByProperty(id, validationPath || propertyPath);
            return new ReviewValue(values, validation.state, validation.message);
        },

        safeIdentityGet: function (/*String*/ id, /*Object*/ object, /*String*/ propertyPath, /*String?*/ validationPath) {
            if (crmIsEnabled !== false) {
                var identityName = this.retrieveIdentity(object, propertyPath);
                var validation = this._validationInfo.findByProperty(id, validationPath || propertyPath);
                return new AsyncReviewValue(identityName, validation.state, validation.message);
            } else {
                return this.safeValueGet(id, object, propertyPath, validationPath);
            }
        },

        retrieveIdentity: function (/*Object*/object, /*String*/ propertyPath) {
            var identity = new Identity();
            var uuidValue = this.safeGet(object, propertyPath);
            if (uuidValue != null) {
                identity.getNameFromCRM(uuidValue);
                return identity.name;
            } else {
                return "(Missing)"
            }

        },

        safeIdentityListGet: function (/*String*/ id, /*Object*/ object, /*String*/ propertyPath,
                                       /*String?*/ valueKey, /*String?*/ validationPath, /*String?*/ delimiter) {
            if (crmIsEnabled != "") {
                var itemPropertyPath = valueKey || "value";
                var obsArrayIds = ko.observableArray(this.safeArrayGet(object, propertyPath, function (item) {
                        return this.retrieveIdentity(item, itemPropertyPath);
                    }, this) || []);

                var computedStringRepresentation = this.concatenateIdentities(obsArrayIds);
                var validation = this._validationInfo.findByProperty(id, validationPath || propertyPath);
                return new AsyncReviewValue(computedStringRepresentation, validation.state, validation.message);
            } else {
                return this.safeListGet(id, object, propertyPath, valueKey, validationPath, delimiter)
            }
        },

        concatenateIdentities: function (observableIdArray) {
            return ko.computed(function () {
                var result = "";
                ko.utils.arrayForEach(observableIdArray(), function (id) {
                    result = result + id() + ",";
                });
                return result.length > 0 ? result : null;
            });
        }
    });
});

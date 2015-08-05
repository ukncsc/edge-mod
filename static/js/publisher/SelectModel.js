define(["knockout", "dcl/dcl"], function (ko, declare) {
    "use strict";

    var TYPES = Object.freeze({
        "coa": {"collection": "courses_of_action", "label": "Course Of Action", "code": "coa"},
        "ttp": {"collection": "ttps", "label": "TTP", "code": "ttp"},
        "incident": {"collection": "incidents", "label": "Incident", "code": "inc"},
        "indicator": {"collection": "indicators", "label": "Indicator", "code": "ind"},
        "observable": {"collection": "observables", "label": "Observable", "code": "obs"}
    });

    function findType(/*String*/ id) {
        var pattern = new RegExp(
            "^[a-z\d-]+:([a-z\d]+)-[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$"
        );
        var match = pattern.exec(id.toLowerCase());
        return TYPES[match && match[1]];
    }

    function findById(/*String*/ id) {
        var listToSearch = this.stixPackage()[findType(id).collection];
        return ko.utils.arrayFirst(listToSearch, function (item) {
            return item.id === id;
        }, this);
    }

    function findRoot() {
        return findById.bind(this)(this.rootId());
    }

    return declare(null, {

        constructor: function (rootId, stixPackage) {
console.log(rootId);
console.dir(stixPackage);
            this.rootId = ko.observable(rootId);
            this.stixPackage = ko.observable(stixPackage);

            this.root = ko.computed(findRoot, this);

            this.type = ko.computed(function () {
                return findType(this.rootId());
            }, this);

            this.typeCode = ko.computed(function () {
                return this.type().code;
            }, this);

            this.typeText = ko.computed(function () {
                return this.type().label;
            }, this);
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

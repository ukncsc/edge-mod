define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "ExternalId",

        constructor: function () {
            this.source = ko.observable('');
            this.id = ko.observable('');
        },
        load: function (source, id) {
            this.source(source);
            this.id(id);
        },
        to_json: function () {
            return {
                source: this.source(),
                id: this.id()
            }

        }
    });
});

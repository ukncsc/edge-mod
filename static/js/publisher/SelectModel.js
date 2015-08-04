define(["knockout", "dcl/dcl"], function (ko, declare) {
    "use strict";

    return declare(null, {
        constructor: function (root_id, root_type, stix_package) {
console.log(root_type, root_id);
console.dir(stix_package);
            this.root_id = ko.observable(root_id);
            this.root_type = ko.observable(root_type);
            this.stix_package = ko.observable(stix_package);

            this.stix_id = ko.computed(function () {
                return stix_package.id;
            });

            this.incidents = ko.computed(function () {
                return stix_package["incidents"];
            });

            this.ttps = ko.computed(function () {
                return stix_package["ttps"]["ttps"];
            });

            this.coas = ko.computed(function () {
                return stix_package["courses_of_action"];
            });
        }
    });
});

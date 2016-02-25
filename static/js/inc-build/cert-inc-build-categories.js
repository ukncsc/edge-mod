define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-selects"
], function (declare, ko, listSelects) {
    "use strict";


    var DiscoveryMethods = declare(listSelects, {
        declaredClass: "Categories",

        constructor: declare.superCall(function (sup) {
                return function () {
                    sup.call(this, "Categories", {
                        selectChoice: 'categories_list',
                        saveKey: 'categories',
                        required: true,
                        displayName: 'Category'
                    });
                }
            }
        )
    });

    return  DiscoveryMethods;
});

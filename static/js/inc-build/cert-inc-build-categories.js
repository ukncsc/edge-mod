define([
    "dcl/dcl",
    "common/cert-build-list-selects"
], function (declare, ListSelects) {
    "use strict";

    return declare(ListSelects, {
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
        })
    });
});

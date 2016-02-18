define([
    "dcl/dcl",
    "knockout",
    "common/cert-build-list-selects"
], function (declare, ko, listSelects) {
    "use strict";


    var DummyList = declare(listSelects, {
        declaredClass: "DummyList",

        constructor: declare.superCall(function (sup) {
                return function () {
                    sup.call(this, "Dummy List", {
                        selectChoice: 'dummy_list',
                        saveKey: 'dummylist'
                    });

                }
            }
        )
    });


    return DummyList;
});

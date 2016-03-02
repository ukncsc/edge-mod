if (typeof window === "undefined") {
    window = {};
}
define([
    "dcl/dcl",
    "knockout",
    "dummy-list"
], function (declare, ko, DummyList) {
    "use strict";

    var ViewModel = declare(null, {
            declaredClass: "ViewModel",

            constructor: function () {
                this.aDummyList = ko.observable(new DummyList());
                this.aDummyList().loadStatic({dummy_list : ['1', '2', '3', '4']})
            }
        }
    )

    window.vm = new ViewModel();
    ko.applyBindings(window.vm);

});



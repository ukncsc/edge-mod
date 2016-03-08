// When the DOM is ready, set up the viewmodel...

define([
    "common/load-draft",
    "common/window-shim"
], function (ko, window) {
    "use strict";

    return function (id) {

        var params = {'id': id};
        postJSON(ajax_uri + 'load_draft/', params, function (r) {
            if (r['success']) {
                window.vm.populateGuiFomJson(r['draft']);
                window.vm.tracker().markCurrentStateAsClean();
            } else {
                alert(r['message']);
            }
        })
    };
});

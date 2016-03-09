define([
    "common/window-shim"
], function (window) {
    "use strict";

    return function (id) {

        var params = {'id': id};
        postJSON(window.ajax_uri + 'load_draft/', params, function (r) {
            if (r['success']) {
                window.vm.populateGuiFomJson(r['draft']);
                window.vm.tracker().markCurrentStateAsClean();
            } else {
                alert(r['message']);
            }
        })
    };
});

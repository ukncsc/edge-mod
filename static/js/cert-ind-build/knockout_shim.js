define([], function () {
    "use strict";

    var ko = window.ko;
    if (!ko) {
        // Oh dear.
        throw Error("Knockout not yet defined.");
    }
    return ko;
});

define([
        "../../../../dcl/dcl",
        "ind-build/tests/unit/mock/mock-builder-mode"],
    function (declare, builderMode) {
        return declare(null, {
            constructor: function () {
                this.bm = new builderMode();
            },
            builderMode: function () {
                return this.bm
            }
        });
    });

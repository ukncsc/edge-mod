define(["../../../../dcl/dcl",], function (declare) {
    return declare(null, {
        constructor: function (isBatch) {
            this.isBatch = isBatch;
        },

        isBatchMode: function () {
            return this.isBatch;
        }
    });
});

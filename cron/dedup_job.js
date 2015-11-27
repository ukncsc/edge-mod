/*global ObjectId, db, emit, quit, print, printjson, NumberInt, load */

/**
 * dedup_job.js
 *
 * mongodb map_reduce to de-duplicate indicators, observables and ttps
 */

// see https://docs.mongodb.org/v2.6/core/map-reduce/
// and https://docs.mongodb.org/v2.6/reference/method/db.collection.mapReduce/

(function () {
    "use strict";

    function CertukDedupJob() {

    }

    CertukDedupJob.prototype = {
        map: function () {
            emit(this.data.hash, {
                id: this._id,
                created_on: this.created_on
            });
        },

        reduce: function (/*String*/ key, /*Array*/ values) {
            return values.sort(function (value1, value2) {
                return value1.created_on.getTime() > value2.created_on.getTime();
            }).reduce(function (reducedValue, value) {
                var duplicateIds = reducedValue["duplicateIds"];
                if (!duplicateIds) {
                    duplicateIds = reducedValue["duplicateIds"] = [];
                }
                duplicateIds.push(value.id);
                var sourceDuplicateIds = value["duplicateIds"];
                if (sourceDuplicateIds instanceof Array) {
                    Array.prototype.push.apply(duplicateIds, sourceDuplicateIds);
                }
                return reducedValue;
            });
        },

        finalize: function(/*String*/ key, /*Object*/ reducedValue) {
            // TODO: dedup reducedValue.duplicateIds - see: http://stackoverflow.com/questions/9229645/remove-duplicates-from-javascript-array
            return reducedValue;
        },

        run: function () {
            printjson(db.stix.mapReduce(
                this.map,
                this.reduce,
                {
                    //finalize: this.finalize,
                    out: {
                        inline: 1
                    },
                    //query: {
                    //    "type": "obs"
                    //},
                    scope: this
                }
            ));
        }
    };

    CertukDedupJob.main = function () {
        (new CertukDedupJob()).run();
    };

    CertukDedupJob.main();
})();

define(["knockout"], function (ko) {
    "use strict";

    return Object.freeze({
        createEdges: function (/*String[]*/ids) {
            var PATTERN = {
                namespace: "[a-z][\\w\\d-]+",
                type: "[a-z]+",
                uuid: "[a-f\\d]{8}-[a-f\\d]{4}-[a-f\\d]{4}-[a-f\\d]{4}-[a-f\\d]{12}",
                draft: ":draft:[a-f\\d]{32}"
            };

            var TYPES =
            {
                "campaign": "cam",
                "courseofaction": "coa",
                "et": "tgt",
                "tgt":"tgt" ,
                "coa":"coa",
                "threatactor": "act",
                "incident": "inc",
                "indicator": "ind",
                "observable": "obs",
                "package": "stix",
                "ttp": "ttp"
            };

            function _parseId(/*String*/ id) {
                if (!(typeof id === "string")) {
                    throw new TypeError("Identifier must be a string");
                }
                var pattern = new RegExp(
                    "^(" + PATTERN.namespace + "):(" + PATTERN.type + ")-" + PATTERN.uuid + "(" + PATTERN.draft + ")?$",
                    "i"
                );
                var match = pattern.exec(id);
                if (!match) {
                    throw new Error("Unable to parse id: " + id);
                }
                return match;
            };

            function _findType(parsedId) {
                var type = TYPES[parsedId[2].toLowerCase()];
                if (!type) {
                    throw new TypeError("Unsupported type: " + _parsedId[2]);
                }
                return type;
            }

            var res = [];
            ko.utils.arrayForEach(ids, function (id) {
                res.push({"id_": id, "ty": _findType(_parseId(id))})
            });

            return res;

        }
    });
});


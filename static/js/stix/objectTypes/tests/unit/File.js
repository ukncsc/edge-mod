define([
    "intern!object",
    "intern/chai!assert",
    "stix/objectTypes/StixObjectType",
    "stix/StixPackage",
    "intern/dojo/text!./data/Observable_package_file.json"
], function (registerSuite, assert, StixObjectType, StixPackage, package01) {
    "use strict";

    // statics go here
    var packageData = Object.freeze({
        "purple-secure-systems:observable-b8ece3b4-2260-42bf-80cc-e11a932000a8": Object.freeze(JSON.parse(package01))
    });

    return registerSuite(function () {

        // suite variables go here
        var stixPackage = null;
        var classUnderTest = null;

        function loadPackage(rootId, objectId) {
            stixPackage = new StixPackage(packageData[rootId], objectId || rootId);
            classUnderTest = stixPackage.root;
        }

        return {
            name: "stix/objectTypes/File",
            "with hashes" : {
                setup: function () {
                    loadPackage("purple-secure-systems:observable-b8ece3b4-2260-42bf-80cc-e11a932000a8");
                },
                "is not null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct properties": function () {
                    assert.deepEqual(classUnderTest.properties(), [
                        { "label": "Device Path", "value": "Any device path" },
                        { "label": "File Format", "value": "pdf + dll + pfm" },
                        { "label": "File Name", "value": "pjb.pdf" },
                        { "label": "Size In Bytes", "value": 73379 },
                        { "label": "File Path", "value": "Any file path" },
                        { "label": "File Extension", "value": "pdf" },
                        { "label": "Full Path", "value": "Any full path" },
                        { "label": "MD5", "value": "3dbf4fc0b508d8859f3e1d30651590bb" },
                        { "label": "SHA256", "value": "625da05610003ff4d82bdfcb48bcfc84613a51156f83ea0c28fa52997b128935" },
                        { "label": "SHA1", "value": "2f533cb43ec00fae6363fdc57359ee23deb8a915" }
                    ]);
                }
            },
            "without hashes" : {
                setup: function () {
                    loadPackage(
                        "purple-secure-systems:observable-b8ece3b4-2260-42bf-80cc-e11a932000a8",
                        "certuk:Observable-bbe6cfae-8d71-4e69-87aa-97b642e4b549"
                    );
                },
                "is not null": function () {
                    assert.isNotNull(classUnderTest);
                },
                "has correct properties": function () {
                    assert.deepEqual(classUnderTest.properties(), [
                        { "label": "File Name", "value": "document_521789_pdf.exe" }
                    ]);
                }
            }
        }
    });
});

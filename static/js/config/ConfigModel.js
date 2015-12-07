define([
    "dcl/dcl",
    "common/modal/Modal",
    "config/PublisherConfig",
    "config/RetentionConfig"
], function (declare, Modal, PublisherConfig, RetentionConfig) {
    "use strict";

    return declare(null, {
        declaredClass: "ConfigModel",
        constructor: function () {
            this.publisher = new PublisherConfig();
            this.retention = new RetentionConfig();

            this.publisher.getSites();
            this.retention.getConfig();
        }
    });
});

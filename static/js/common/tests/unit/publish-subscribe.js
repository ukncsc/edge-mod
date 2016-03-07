define([
    "intern!object",
    "intern/chai!assert",
    "knockout",
    "common/publish-subscribe"
], function (registerSuite, assert, ko, PubSub) {
    "use strict";

    // statics go here

    return registerSuite(function () {

        return {
            name: "common/publish-subscribe",
            "subscribe": {
                "subscribe then publish": function () {
                    var pubSub = new PubSub();
                    var callbackCalled = false;
                    pubSub.subscribe("test_topic", function () {
                        callbackCalled = true;
                    });

                    pubSub.publish("test_topic", []);

                    assert.isTrue(callbackCalled);
                },
                "subscribe then publish other topic": function () {
                    var pubSub = new PubSub();
                    var callbackCalled = false;
                    pubSub.subscribe("test_topic", function () {
                        callbackCalled = true;
                    });

                    pubSub.publish("test_topic2", []);

                    assert.isFalse(callbackCalled);
                },

                "subscribe, unsubscribe then publish": function () {
                    var pubSub = new PubSub();
                    var callbackCalled = false;
                    var handle = pubSub.subscribe("test_topic", function () {
                        callbackCalled = true;
                    });

                    var handle2 = pubSub.subscribe("test_topic2", null);

                    pubSub.unsubscribe(handle);
                    pubSub.publish("test_topic", []);

                    assert.isFalse(callbackCalled);
                },


                "publish with no args branch coverage": function () {
                    var pubSub = new PubSub();
                    pubSub.subscribe("test_topic",function(){});
                    pubSub.publish("test_topic", false);
                },

                "subscribe twice branch coverage branch coverage": function () {
                    var pubSub = new PubSub();
                    pubSub.subscribe("test_topic", null);
                    pubSub.subscribe("test_topic", null);
                },

                "subscribe unsubscribe wrongly branch coverage": function () {
                    var pubSub = new PubSub();
                    pubSub.subscribe("test_topic", null);
                    var handle = pubSub.subscribe("test_topic2", function(){});
                    pubSub.unsubscribe(["test_topic", {}]);
                },
            },
        }
    });
});

define([
    "intern!object",
    "intern/chai!assert",
    "common/topic"
], function (registerSuite, assert, topic) {
    "use strict";

    // statics go here
    var TOPICS = Object.freeze({
        A: "first_topic",
        B: "second_topic"
    });
    var MESSAGES = Object.freeze({
        A: "message for A",
        NULL: null,
        OBJECT: {
            message: "unfrozen message"
        },
        FROZEN: Object.freeze({
            message: "frozen message"
        })
    });

    return registerSuite(function () {

        // suite variables go here
        var subscriptions = [];
        function cleanup() {
            while (subscriptions.length > 0) {
                subscriptions.pop().remove();
            }
        }

        return {
            name: "common/topic",
            timeout: 5000,
            "no subscription": {
                "publishing to an unsubscribed topic doesn't throw an error": function () {
                    topic.publish(TOPICS.A, MESSAGES.A);
                }
            },
            "single subscription": {
                afterEach: cleanup,
                "topic A receives message sent to topic A": function () {
                    var dfd = this.async();
                    subscriptions.push(
                        topic.subscribe(TOPICS.A, dfd.callback(function (message) {
                            assert.equal(message, MESSAGES.A);
                        }))
                    );
                    topic.publish(TOPICS.A, MESSAGES.A);
                    return dfd;
                },
                "topic B does not receive message sent to topic A": function () {
                    var dfd = this.async();
                    subscriptions.push(
                        topic.subscribe(TOPICS.A, dfd.resolve),
                        topic.subscribe(TOPICS.B, dfd.reject)
                    );
                    topic.publish(TOPICS.A, MESSAGES.A);
                    return dfd;
                },
                "null message can be sent": function () {
                    var dfd = this.async();
                    subscriptions.push(
                        topic.subscribe(TOPICS.A, dfd.callback(function (message) {
                            assert.equal(message, MESSAGES.NULL);
                        }))
                    );
                    topic.publish(TOPICS.A, MESSAGES.NULL);
                    return dfd;
                },
                "unfrozen object message can be sent": function () {
                    var dfd = this.async();
                    subscriptions.push(
                        topic.subscribe(TOPICS.A, dfd.callback(function (message) {
                            assert.equal(message, MESSAGES.OBJECT);
                            assert.isTrue(Object.isFrozen(message));
                        }))
                    );
                    topic.publish(TOPICS.A, MESSAGES.OBJECT);
                    return dfd;
                },
                "frozen object message can be sent": function () {
                    var dfd = this.async();
                    subscriptions.push(
                        topic.subscribe(TOPICS.A, dfd.callback(function (message) {
                            assert.equal(message, MESSAGES.FROZEN);
                            assert.isTrue(Object.isFrozen(message));
                        }))
                    );
                    topic.publish(TOPICS.A, MESSAGES.FROZEN);
                    return dfd;
                }
            },
            "multiple subscriptions" : {
                afterEach: cleanup,
                "all topic A subscriptions receive message sent to topic A": function () {
                    var dfd = this.async(null, 3);
                    var handler = dfd.callback(function (message) {
                        assert.equal(message, MESSAGES.A);
                    });
                    subscriptions.push(
                        topic.subscribe(TOPICS.A, handler),
                        topic.subscribe(TOPICS.A, handler),
                        topic.subscribe(TOPICS.A, handler),
                        topic.subscribe(TOPICS.B, function (message) {
                            dfd.reject("Did not expect to get: " + message);
                        })
                    );
                    topic.publish(TOPICS.A, MESSAGES.A);
                    return dfd;
                }
            }
        }
    });
});

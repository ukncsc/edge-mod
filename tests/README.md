# Testing with [Intern](https://theintern.github.io/)

## Prerequisites

* `sudo yum install node npm`
* `sudo npm install -g intern`

## Running the tests manually

You can run the unit tests and view coverage from the command line by typing the following in the root of the project directory:

* `intern-client config=tests/intern reporters=Console`

To have coverage information output to an HTML file in a directory in the root of the project named `html-report`:

* `intern-client config=tests/intern reporters=LcovHtml`

To run an individual test rather than the whole suite:

* `intern-client config=tests/intern reporters=Console suites=amd/path/to/test`

## Integration with PyCharm

* install the `NodeJS` plugin
* _optionally install the `Markdown support` plugin to more easily view this document_
* restart PyCharm
* create a `Node.js` run configuration as follows:
    * Configuration
        <table><tbody>
        <tr><td>Node interpreter</td><td><code>/usr/bin/node</code></td></tr>
        <tr><td>Node parameters</td><td><em>leave blank</em></td></tr>
        <tr><td>Working directory</td><td><em>project root (the directory containing the top-level <code>tests</code> directory in which this file sits)</em></td></tr>
        <tr><td>JavaScript file</td><td><code>/usr/bin/intern-client</code></td></tr>
        <tr><td>Application parameters</td><td><code>config=tests/intern reporters=Console</code></td></tr>
        <tr><td>Environment variables</td><td><em>leave blank</em></td></tr>
        </tbody></table>
    * NOTE: the `Application parameters` entry can be changed per the options for running tests manually

## Useful links

* [Intern](https://theintern.github.io/intern/)
    * [User Guide](https://theintern.github.io/intern/)
        * [Writing a unit test](https://theintern.github.io/intern/#writing-unit-test)
        * [Writing a functional test](https://theintern.github.io/intern/#writing-functional-test)
* [Chai Assertion Library](http://chaijs.com)
    * [`assert` API reference](http://chaijs.com/api/assert/)

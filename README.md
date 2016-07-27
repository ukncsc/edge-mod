Copyright (c) 2016 Crown Copyright (CERT-UK)  

Permission is hereby granted, free of charge, to use, copy, modify, merge, distribute and/or sub-licence the software together with any associated documentation provided that it is solely for your own internal use and subject to the following conditions:

(1)   The above copyright notice and this permission notice shall be included in all copies or substantial portions of the software.

(2)   THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT ANY WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN ANY ACTION FOR CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Edge Mod
Edge Mod is a Soltra Edge adapter that contains modifications and enhancements to Soltra Edge. After using Soltra Edge as our core Cyber Threat Intelligence (CTI) Platform we found that the system could do with some tweaks in order to match our current workflow. We worked together with our partners to develop this adapter for the last year around of current requirements.

## Features

- Publishing of STIX objects
  - With data quality checks and redaction of handling caveat information
- Administration features
  - Ageing off of STIX objects
  - Rebuild full text search content
- Visualisation
  - Incident timeline graph
  - Dynamic nodal graphs of STIX objects and relationships
- Data Ingest
  - De=duplicating ingest endpoint
  - Extract IOC from PDF or TXT file
- Data Creation
  - Clone existing object to draft
  - Extensions to object builders
    - Indicator - Batch observable creation, network connection and HTTP session objects, improved validation, kill chain phase
    - Incident - Times, improved validation, external IDs, improved UI

## Status
The adapter is still under active development and as such shouldn't be considered a finished product.

## Installation
The adapter is currently aimed at version 2.8.1 of Soltra Edge. Other versions may work but your mileage may vary. The following is carried out as a Super User on the GUI whilst on the 'Admin > Adapters' page.

1. Upload and install the new adapter
2. Click on 'Restart Services' in the 'Restart Required' box

## Upgrade
Upgrading the adapter requires a few extra steps before following the installation instructions.

1. Click the red X to the right of the 'running' status on the certuk_mod line
2. Status will change to 'removing' but due to a core Edge bug will get stuck
3. Refresh the page
4. Click on 'Restart Services' in the 'Restart Required' box
5. Following the installation instructions

## Thanks
Thanks to the folks at Soltra for building a great platform for us to build these modification on.

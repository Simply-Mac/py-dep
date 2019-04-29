# py-dep
Introduction
============

py-dep is a Python 3.6+ module designed to work with Apple's Device Enrollment Program (DEP) API. It is meant to be used as a means for 
Apple Resellers to be able to enroll their customers' eligible Apple devices into the customer institution's DEP account. Please consult the DEP API documentation ([UAT](https://applecareconnect.apple.com/api-docs/depuat/html/WSStart.html?user=reseller),
[Production](https://applecareconnect.apple.com/api-docs/dep/html/WSReference.html?user=reseller)) for more details.

This is being open-sourced to gather feedback on how to make the module better and benefit the community at large.

**Note**: Before an authorized reseller may begin enrolling devices for their customers, Apple must take both the reseller and the customer
through an onboarding process **AND** sign-off on the reseller's implementation of the DEP API. This is partially detailed in the 
[DEP Design Requirements](https://applecareconnect.apple.com/api-docs/depuat/html/WSImpManual.html?user=reseller&id=1111&lang=EN).
Please contact your Apple representative for more information.


Requirements
============

- Python 3.x or later
- Contents of requirements.txt in your Python environment
- DEP client certs (UAT/PROD) signed by Apple


Usage
=====
To achieve the "Sample REST(JSON) Request" for a Bulk Enroll Devices Request found [here](https://applecareconnect.apple.com/api-docs/depuat/html/WSReference.html?user=reseller&id=1111&lang=EN#requestXmlHdr),
we could use the following code:

#### UAT Example

```python
# Get device details
import os
from datetime import datetime
from py-dep import dep

os.environ['DEP_ENV'] = 'UAT'
os.environ['DEP_SHIPTO'] = '0000052010'
os.environ['DEP_RESELLER_ID'] = '16FCE4A0'
os.environ['DEP_UAT_CERT'] = '/path/to/acc/uat/cert.pem'
os.environ['DEP_UAT_PRIVATE_KEY'] = '/path/to/acc/uat/cert_private_key.pem'

d1 = dep.Device("33645004YAM", "A123456").json()
d2 = dep.Device("33645006YAM", "A123456").json()
devices1 = [d1, d2]

delivery1 = dep.Delivery('D1.2', datetime(2014, 10, 10, 5, 10, 00), devices1).json()
deliveries = [delivery1]

order = dep.Order("ORDER_900123", datetime(2014, 8, 28, 10, 10, 10), "OR", "19827", "PO_12345", deliveries).json()

dep.bulk_enroll_devices("TXN_001122", order)
```


#### PROD Example

```python
# Get device details
import os
from datetime import datetime
from py-dep import dep

os.environ['DEP_ENV'] = 'PROD'
os.environ['DEP_SHIPTO'] = '0000052010'
os.environ['DEP_RESELLER_ID'] = '16FCE4A0'
os.environ['DEP_UAT_CERT'] = '/path/to/acc/uat/cert.pem'
os.environ['DEP_UAT_PRIVATE_KEY'] = '/path/to/acc/uat/cert_private_key.pem'

d1 = dep.Device("33645004YAM", "A123456").json()
d2 = dep.Device("33645006YAM", "A123456").json()
devices1 = [d1, d2]

delivery1 = dep.Delivery('D1.2', datetime(2014, 10, 10, 5, 10, 00), devices1).json()
deliveries = [delivery1]

order = dep.Order("ORDER_900123", datetime(2014, 8, 28, 10, 10, 10), "OR", "19827", "PO_12345", deliveries).json()

dep.bulk_enroll_devices("TXN_001122", order)
```


Credits
=====
- [Meraki Dashboard API for Python](https://github.com/meraki/dashboard-api-python)
- [Python library for communicating with GSX Web Services API](https://github.com/filipp/py-gsxws)

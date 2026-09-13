# Native ACL/RBAC: disabled preview design

The supplied brief names `2026-08-01-preview`. Reconfirm this API version and
source support in [document-level access](https://learn.microsoft.com/azure/search/search-document-level-access-overview)
before building native enforcement. This lab deliberately executes only the GA
security-string path. `python demo.py --preview` prints this boundary without
network calls. A generic flag cannot safely convert an ordinary string-filter index
into a native ACL index; source permission ingestion, schema and delegated token
handling must all be configured together. No invented preview request is supplied.

Production identity must come from validated Entra claims and trusted group
membership, including group-overage handling. Never trust a browser-provided group
array. The Search service credential authorises the application; the GA filter is
application-enforced and does not itself authenticate the end user.

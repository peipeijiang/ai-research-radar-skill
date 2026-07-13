# Source Selection

Choose sources by publication culture, not by copying the template defaults.

| Field | Primary discovery sources | Notes |
| --- | --- | --- |
| Computer science | ArXiv, OpenAlex, selected DBLP venues | DBLP is useful for venue-first conference discovery |
| Banking, fiscal, monetary policy | OpenAlex, central banks, IMF, OECD, World Bank, ADB, EconStor, RePEc free series, ArXiv economics | Official working-paper series often precede journal publication |
| General economics | OpenAlex, ArXiv economics, World Bank, EconStor, IZA, CESifo, RePEc free series | Mark restricted or unavailable NBER full text as abstract-only |
| Biomedical | PubMed/Europe PMC plus OpenAlex | Requires a field-specific source implementation before claiming completeness |

## Economic policy profile

Enable `institutional` with official RSS feeds:

- ECB Working Papers: `https://www.ecb.europa.eu/rss/wppub.html`
- BIS Working Papers: `https://www.bis.org/doclist/bis_fsi_publs.rss`
- Federal Reserve working papers: `https://www.federalreserve.gov/feeds/working_papers.xml`
- Bank of Canada working papers: `https://www.bankofcanada.ca/feed/?content_type=working-papers&post_type%5B0%5D=post&post_type%5B1%5D=page`
- EconStor open-access economics: `https://www.econstor.eu/feed/rss_2.0/site`

Enable `worldbank` with topic terms. The source uses the official Documents API
and restricts results to Policy Research Working Papers. These sources need no
additional API key.

Enable `repec` for configured working-paper series. The source reads the current
year section, requires RePEc's `freedownload=1` marker, and records a verified
direct PDF only when the catalog exposes one. Recommended economic-policy
series include IMF, Bank of England, OECD, ADB, IZA, CESifo, and the New York,
Chicago, San Francisco, St. Louis, and Philadelphia Federal Reserve Banks.
These catalogs require no API key. A free landing page that cannot be resolved
to a PDF must continue through the normal ArXiv/OpenAlex/Unpaywall/CORE chain
and remain abstract-only if recovery fails.

Keep NBER as metadata/abstract discovery unless the user has legitimate full-
text access. Do not treat subscription-restricted PDFs as open access. Retain
the institutional publisher and RePEc catalog as separate provenance fields.

After changing sources, run a short live fetch before the LLM pipeline. Confirm
recent item counts, dates, abstracts, landing links, and PDF provenance. A zero-
result low-frequency source is acceptable; a parser silently returning malformed
records is not.

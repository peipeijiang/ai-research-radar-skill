# Source Selection

Choose sources by publication culture, not by copying the template defaults.

| Field | Primary discovery sources | Notes |
| --- | --- | --- |
| Computer science | ArXiv, OpenAlex, selected DBLP venues | DBLP is useful for venue-first conference discovery |
| Banking, fiscal, monetary policy | OpenAlex, ECB, BIS, Federal Reserve FEDS/IFDP, World Bank, ArXiv economics | Official working-paper series often precede journal publication |
| General economics | OpenAlex, ArXiv economics, World Bank; optional NBER/RePEc metadata | Mark restricted or unavailable NBER full text as abstract-only |
| Biomedical | PubMed/Europe PMC plus OpenAlex | Requires a field-specific source implementation before claiming completeness |

## Economic policy profile

Enable `institutional` with official RSS feeds:

- ECB Working Papers: `https://www.ecb.europa.eu/rss/wppub.html`
- BIS Working Papers: `https://www.bis.org/doclist/bis_fsi_publs.rss`
- Federal Reserve working papers: `https://www.federalreserve.gov/feeds/working_papers.xml`

Enable `worldbank` with topic terms. The source uses the official Documents API
and restricts results to Policy Research Working Papers. These sources need no
additional API key.

Keep NBER as metadata/abstract discovery unless the user has legitimate full-
text access. Do not treat subscription-restricted PDFs as open access. Add IMF,
RePEc, or other providers only through stable official APIs or feeds and retain
source provenance.

After changing sources, run a short live fetch before the LLM pipeline. Confirm
recent item counts, dates, abstracts, landing links, and PDF provenance. A zero-
result low-frequency source is acceptable; a parser silently returning malformed
records is not.

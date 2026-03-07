# Repository API Analysis

## Summary of All 24 Repositories

### ✅ API-Based Repositories (Can use programmatic access)

#### **Dataverse API** (7 repositories)
All use the standard Dataverse API: https://guides.dataverse.org/en/latest/api/

1. **Zenodo** - REST API
   - API: `https://zenodo.org/api/records`
   - Status: ✅ Working scraper exists
   
2. **Syracuse QDR** - Dataverse API
   - API: `https://qdr.syr.edu/api`
   - Status: ✅ Working scraper exists

3. **DANS** - OAI-PMH + Dataverse
   - API: `https://easy.dans.knaw.nl/oai`
   - Status: ✅ Working scraper exists

4. **DataverseNO** - Dataverse API
   - API: `https://dataverse.no/api`
   - Status: ✅ Working scraper exists

5. **ADA (Australian Data Archive)** - Dataverse API
   - API: `https://dataverse.ada.edu.au/api`
   - Status: ⚠️ **NEEDS NEW SCRAPER** (can reuse Dataverse scraper)

6. **Harvard Dataverse** - Dataverse API
   - API: `https://dataverse.harvard.edu/api`
   - Status: ⚠️ **NEEDS NEW SCRAPER** (can reuse Dataverse scraper)

7. **AUSSDA (Austrian)** - Dataverse API
   - API: `https://data.aussda.at/api`
   - Status: ⚠️ **NEEDS NEW SCRAPER** (can reuse Dataverse scraper)

#### **Other APIs** (3 repositories)

8. **Dryad** - REST API v2
   - API: `https://datadryad.org/api/v2`
   - Status: ✅ Working scraper exists

9. **CESSDA** - REST API (OpenAPI)
   - API: `https://api.tech.cessda.eu/`
   - Documentation: https://datacatalogue.cessda.eu/documentation/rest-api.html
   - Status: ⚠️ **NEEDS NEW SCRAPER** (dedicated REST API)

10. **ICPSR** - Metadata Export API
    - API: `https://www.icpsr.umich.edu/web/ICPSR/search/studies`
    - Documentation: https://icpsr.github.io/metadata/icpsr_metadata_api/
    - Status: ⚠️ **NEEDS NEW SCRAPER** (dedicated API)

### 🌐 Web Scraping Required (11 repositories)

11. **UK Data Service**
    - URL: https://datacatalogue.ukdataservice.ac.uk/
    - Status: ✅ Working scraper exists

12. **FSD (Finnish Social Science Data Archive)**
    - Has OAI-PMH endpoint (Kuha server)
    - Status: ⚠️ **NEEDS NEW SCRAPER** (OAI-PMH or web scraping)

13. **SADA (South African Data Archive)**
    - Uses NADA (National Data Archive) system
    - Status: ⚠️ **NEEDS WEB SCRAPER**

14. **Databrary**
    - Has API but requires authentication/access agreement
    - Status: ⚠️ **NEEDS WEB SCRAPER** (restricted access)

15. **Qualidata Network**
    - Status: ✅ Working scraper exists

16. **Qualiservice**
    - Status: ✅ Working scraper exists

17. **QualiBi**
    - Status: ✅ Working scraper exists

18. **IHSN (International Household Survey Network)**
    - Status: ⚠️ **NEEDS WEB SCRAPER**

19. **Open Data Uni Halle**
    - Status: ⚠️ **NEEDS WEB SCRAPER**

20. **CIS Spain**
    - Status: ⚠️ **NEEDS WEB SCRAPER**

21. **Murray Research Archive**
    - Status: ⚠️ **NEEDS WEB SCRAPER**

22. **Columbia Oral History**
    - Status: ⚠️ **NEEDS WEB SCRAPER**

23. **Sikt Norway**
    - Status: ⚠️ **NEEDS WEB SCRAPER**

## Priority Implementation Plan

### Phase 1: Dataverse-based Repositories (HIGH PRIORITY)
- Create generic Dataverse scraper or extend existing one
- Deploy for: ADA, Harvard Dataverse, AUSSDA
- **Estimated effort:** 1-2 days

### Phase 2: Dedicated API Scrapers (MEDIUM PRIORITY)
- CESSDA REST API scraper
- ICPSR Metadata API scraper
- FSD OAI-PMH scraper
- **Estimated effort:** 3-4 days

### Phase 3: Web Scrapers (LOWER PRIORITY)
- SADA, Databrary, IHSN, Open Data Halle, CIS Spain, Murray, Columbia, Sikt
- **Estimated effort:** 5-7 days

## Technical Notes

- **Dataverse API** is standardized across multiple repositories
- **CESSDA** provides OpenAPI documentation
- **ICPSR** has well-documented metadata export API
- **FSD** uses OAI-PMH (Open Archives Initiative Protocol)
- Most web scraping targets will require BeautifulSoup/Selenium


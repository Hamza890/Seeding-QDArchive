# Complete Repository List

## Overview

**Total Repositories**: 24  
**API-Based**: 10 (42%)  
**Web Scraping**: 14 (58%)  
**Implementation Status**: ✅ 100% Complete

---

## API-Based Repositories (10)

### 1. Zenodo
- **URL**: https://zenodo.org/
- **API**: REST API
- **Scraper Class**: `ZenodoScraper`
- **Search URL**: https://zenodo.org/search?q=qdpx
- **Status**: ✅ Complete

### 2. Dryad
- **URL**: http://datadryad.org/
- **API**: REST API v2
- **Scraper Class**: `DryadScraper`
- **Search URL**: https://datadryad.org/search?q=qualitative+research
- **Status**: ✅ Complete

### 3. Syracuse QDR
- **URL**: https://qdr.syr.edu/
- **API**: Dataverse API
- **Scraper Class**: `SyracuseQDRScraper`
- **Search URL**: https://data.qdr.syr.edu/dataverse/main/?q=interview
- **Status**: ✅ Complete

### 4. DANS (Netherlands)
- **URL**: https://dans.knaw.nl/en/
- **API**: OAI-PMH
- **Scraper Class**: `DANSScraper`
- **Search URL**: https://ssh.datastations.nl/dataverse/root?q=qdpx
- **Status**: ✅ Complete

### 5. DataverseNO (Norway)
- **URL**: https://dataverse.no/
- **API**: Dataverse API
- **Scraper Class**: `DataverseScraper`
- **Search URL**: https://dataverse.no/
- **Status**: ✅ Complete

### 6. ADA (Australian Data Archive)
- **URL**: https://dataverse.ada.edu.au/
- **API**: Dataverse API
- **Scraper Class**: `ADAScraper`
- **Search URL**: https://dataverse.ada.edu.au/
- **Status**: ✅ Complete

### 7. Harvard Dataverse
- **URL**: https://dataverse.harvard.edu/
- **API**: Dataverse API
- **Scraper Class**: `HarvardDataverseScraper`
- **Search URL**: https://dataverse.harvard.edu/
- **Status**: ✅ Complete

### 8. AUSSDA (Austrian Social Science Data Archive)
- **URL**: https://data.aussda.at/
- **API**: Dataverse API
- **Scraper Class**: `AUSSDAScraper`
- **Search URL**: https://data.aussda.at/
- **Status**: ✅ Complete

### 9. CESSDA (European Social Science Data Archives)
- **URL**: https://datacatalogue.cessda.eu/
- **API**: REST API (OpenAPI)
- **Scraper Class**: `CESSDAScraper`
- **Search URL**: https://datacatalogue.cessda.eu/?query=qualitative
- **Status**: ✅ Complete

### 10. ICPSR (Inter-university Consortium for Political and Social Research)
- **URL**: https://www.icpsr.umich.edu/
- **API**: Metadata Export API
- **Scraper Class**: `ICSPRScraper`
- **Search URL**: https://www.icpsr.umich.edu/web/ICPSR/search/studies?q=interview
- **Status**: ✅ Complete

---

## Web Scraping Repositories (14)

### 11. UK Data Service
- **URL**: https://ukdataservice.ac.uk/
- **Scraper Class**: `UKDataServiceScraper`
- **Search URL**: https://datacatalogue.ukdataservice.ac.uk/searchresults?search=qualitative+data
- **Status**: ✅ Complete

### 12. Qualidata Network
- **URL**: https://www.qualidatanet.com/
- **Scraper Class**: `QualidataScraper`
- **Status**: ✅ Complete

### 13. Qualiservice
- **URL**: German qualitative data service
- **Scraper Class**: `QualiserviceScraper`
- **Status**: ✅ Complete

### 14. QualiBi
- **URL**: Qualitative data partner network
- **Scraper Class**: `QualiBiScraper`
- **Status**: ✅ Complete

### 15. FSD (Finnish Social Science Data Archive)
- **URL**: https://www.fsd.tuni.fi/
- **Scraper Class**: `FSDScraper`
- **Note**: Has OAI-PMH endpoint (Kuha server)
- **Status**: ✅ Complete

### 16. SADA (South African Data Archive)
- **URL**: http://www.sada.nrf.ac.za/
- **Scraper Class**: `SADAScraper`
- **Note**: Uses NADA (National Data Archive) platform
- **Status**: ✅ Complete

### 17. IHSN (International Household Survey Network)
- **URL**: http://www.ihsn.org/
- **Scraper Class**: `IHSNScraper`
- **Note**: Uses NADA platform
- **Status**: ✅ Complete

### 18. Databrary
- **URL**: https://databrary.org/
- **Scraper Class**: `DatabraryScraper`
- **Search URL**: https://databrary.org/search?q=qualitative&tab=0
- **Note**: ⚠️ Requires authentication for most content
- **Status**: ✅ Complete

### 19. Sikt (Norwegian Agency for Shared Services in Education and Research)
- **URL**: https://sikt.no/en/find-data
- **Scraper Class**: `SiktScraper`
- **Status**: ✅ Complete

### 20. Open Data Uni Halle
- **URL**: https://opendata.uni-halle.de/
- **Scraper Class**: `OpenDataHalleScraper`
- **Status**: ✅ Complete

### 21. CIS Spain (Centro de Investigaciones Sociológicas)
- **URL**: https://www.cis.es/estudios/catalogo-estudios
- **Scraper Class**: `CISSpainScraper`
- **Note**: Supports Spanish search terms
- **Status**: ✅ Complete

### 22. Murray Research Archive (Harvard)
- **URL**: https://www.murray.harvard.edu/
- **Scraper Class**: `MurrayScraper`
- **Status**: ✅ Complete

### 23. Columbia Oral History Archives
- **URL**: https://library.columbia.edu/libraries/ccoh.html
- **Scraper Class**: `ColumbiaOralHistoryScraper`
- **Search URL**: https://guides.library.columbia.edu/oral_history/digital_collections
- **Status**: ✅ Complete

### 24. DataverseNO (Additional Instance)
- Covered by generic `DataverseScraper`
- **Status**: ✅ Complete

---

## Geographic Coverage

- **North America**: 7 repositories (Zenodo, Dryad, Syracuse QDR, Harvard, ICPSR, Murray, Columbia)
- **Europe**: 11 repositories (DANS, DataverseNO, AUSSDA, CESSDA, UK Data Service, Qualidata, Qualiservice, QualiBi, FSD, Sikt, Open Data Halle, CIS Spain)
- **Australia**: 1 repository (ADA)
- **Africa**: 1 repository (SADA)
- **International**: 2 repositories (IHSN, Databrary)

---

## Technical Summary

### API Technologies
- **Dataverse API**: 6 repositories (Syracuse QDR, DANS, DataverseNO, ADA, Harvard, AUSSDA)
- **REST API**: 3 repositories (Zenodo, Dryad, CESSDA)
- **OAI-PMH**: 2 repositories (DANS, FSD)
- **Metadata Export API**: 1 repository (ICPSR)

### Web Scraping Platforms
- **NADA Platform**: 2 repositories (SADA, IHSN)
- **Custom Platforms**: 12 repositories (various)

### Rate Limiting
- All scrapers implement rate limiting (0.5-1 second delays)
- Respects repository terms of service
- User-Agent identification included

### Authentication Requirements
- **Open Access**: 23 repositories
- **Restricted Access**: 1 repository (Databrary - requires authentication for most content)

---

## Usage Examples

### Search All Repositories
```bash
python main.py search --scraper all --max-results 50
```

### Search API-Based Repositories Only
```bash
for scraper in zenodo dryad syracuse_qdr dans ada harvard_dataverse aussda cessda icpsr; do
    python main.py search --scraper $scraper --max-results 50
done
```

### Search Web Scraping Repositories Only
```bash
for scraper in uk_data_service fsd sada ihsn databrary sikt opendata_halle cis_spain murray columbia_oral_history; do
    python main.py search --scraper $scraper --max-results 30
done
```

### Search by Region
```bash
# European repositories
python main.py search --scraper dans --max-results 50
python main.py search --scraper aussda --max-results 50
python main.py search --scraper cessda --max-results 50
python main.py search --scraper fsd --max-results 30
python main.py search --scraper sikt --max-results 30

# North American repositories
python main.py search --scraper zenodo --max-results 100
python main.py search --scraper syracuse_qdr --max-results 50
python main.py search --scraper harvard_dataverse --max-results 50
python main.py search --scraper icpsr --max-results 50
```

---

## Implementation Timeline

- **Original Implementation**: 9 repositories (Zenodo, Dryad, DataverseNO, DANS, Syracuse QDR, UK Data Service, Qualidata, Qualiservice, QualiBi)
- **2024 Expansion Phase 1**: 5 API scrapers (ADA, Harvard, AUSSDA, CESSDA, ICPSR)
- **2024 Expansion Phase 2**: 5 web scrapers (FSD, SADA, IHSN, Databrary, Sikt)
- **2024 Expansion Phase 3**: 4 web scrapers (Open Data Halle, CIS Spain, Murray, Columbia)
- **Total**: 24 repositories (100% complete)

---

## Maintenance Notes

### High Priority for Monitoring
- **Databrary**: Authentication requirements may change
- **Web Scrapers**: Website structure changes may break scrapers
- **API Scrapers**: API version updates may require adjustments

### Recommended Testing Schedule
- **Weekly**: Test API-based scrapers (quick, reliable)
- **Monthly**: Test web scrapers (more prone to breaking)
- **Quarterly**: Full integration test of all 24 repositories

### Known Limitations
- **Databrary**: Most content requires authentication
- **Web Scrapers**: Limited metadata extraction compared to API scrapers
- **CESSDA & ICPSR**: Provide study-level metadata, not always direct file downloads
- **Language**: CIS Spain supports Spanish search terms

---

## Future Expansion Opportunities

Potential repositories to add:
- Additional Dataverse instances worldwide
- National archives in Asia (Japan, South Korea, China)
- Latin American data repositories
- African data repositories beyond SADA
- Specialized oral history archives
- Institutional repositories with QDA files

---

## Support and Documentation

- **Main Documentation**: See `docs/SCRAPERS.md` for detailed scraper documentation
- **API Analysis**: See `docs/REPOSITORY_API_ANALYSIS.md` for technical details
- **Usage Guide**: See `docs/USAGE_GUIDE.md` for comprehensive usage examples
- **Database Schema**: See `docs/DATABASE.md` for metadata structure


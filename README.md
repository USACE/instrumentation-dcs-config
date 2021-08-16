# OpenDCS Editable Database Configurations

OpenDCS can access an XML database that is referred to as an `editable` database.  Functionality exists within the OpenDCS application allowing for importing and exporting XML database components.  This repository is intended to provide a list of `Platforms` to import into the USACE/instrumentation-dcs Docker container.

---

## Filename Format and Participating Districts

Each filename will include a reference to a District using its three letter code:

| District Name | Division Code | District Code | Filename |
| :--- | :---: | :---: | :----- |
| Buffalo District | lrd |  lrb | p.lrd.lrb.xml |
| Chicago District | lrd |  lrc | p.lrd.lrc.xml |
| Huntington District | lrd |  lrh | p.lrd.lrh.xml |
| Nashville District | lrd | lrn | p.lrd.lrn.xml |
| Vicksburg District | mvd | mvk | p.mvd.mvk.xml |
| New Orleans District | mvd | mvn | p.mvd.mvn.xml |
| New England District | nad |  nae | p.nad.nae.xml |
| North West Division, Missouri River | nwd |  nwdm | p.nwd.nwdm.xml |
| Jacksonville District | sad | saj | p.sad.hhd.xml |
| Savannah District | sad | sas | p.sad.sas.xml |
| Mobile District | sad | sam | p.sad.sam.xml |
| Albuquerque District | spd | spa | p.spd.spa.xml |
| Fort Worth District | swd | swf | p.swd.swf.xml
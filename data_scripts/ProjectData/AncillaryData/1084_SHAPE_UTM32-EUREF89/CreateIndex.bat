::@Echo off
:: ----------------------------------------------------------------------------
::  batch file som opretter indext til alle shape filer som findes i
::  et underbibliotek til filen.
::
::  benytter scriptet index.py som forudsætter at ArcGis og python er installet
::  på systemet.
::
::  KMS 23 januar 2009, peter laulund
:: ----------------------------------------------------------------------------

@ECHO opretter index

for /r %%i in (*.shp) do index.py  %%i

pause
## Utils Scripts

### add_uuids.py

- Requirements:
  - p.***division_code***.***district_code***.xml input file must be in original_exports dir
- Example Usage:
  - ``python3 add_uuids.py -i p.lrd.lrh.xml``
  - ``python3 add_uuids.py --overwrite y -i p.lrd.lrn.xml > lrn.log``
- Output XML files will be saved to the root repo
- Output JSON will be saved to \_processing/output/json
- If the output file exists, you will be prompted to overwrite. Using the `` --overwrite y`` will bypass this verification.
- Piping to a log file is not required, but can be helpful to review actions performed by the script.

### json_to_sql.py

- Requirements:
  - p.***division_code***.***district_code***.json input file must be in present in the output/json dir
  - Have the Project UUID already established in database
- Example Usage:
  - ``python3 json_to_sql.py -i p.lrd.lrh.json -p 0000000-0000-0000-0000-4180350dc82a``
  - Output SQL files will be saved to the \_processing/output/sql dir
  - Output file will be overwritten without confirmation

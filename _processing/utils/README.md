## Utils Scripts

### add_uuids.py

- Requirements:
  - platforms.xxx.xml input file must be in original_exports dir
- Example Usage:
  - <code>python3 add_uuids.py -i platforms.lrh.xml</code>
  - <code>python3 add_uuids.py --overwrite y -i platforms.lrn.xml > lrn.log</code>
- Output XML files will be saved to the root repo
- Output JSON will be saved to \_processing/output/json
- If the output file exists, you will be prompted to overwrite. Using the <code> --overwrite y</code> will bypass this verification.
- Piping to a log file is not required, but can be helpful to review actions performed by the script.

### json_to_sql.py

- Requirements:
  - platforms.xxx.json input file must be in present in the output/json dir
- Example Usage:
  - <code>python3 json_to_sql.py -i platforms.lrh.json</code>
  - Output SQL files will be saved to the \_processing/output/sql dir
  - Output file will be overwritten without confirmation

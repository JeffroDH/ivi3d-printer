# Command-map regenerators

[docs/data/stm32_app_commands.csv](../../docs/data/stm32_app_commands.csv) is the table to read: 141 G/M literals the touchscreen app sends, with the function that contains each one.

`strrefs.py` rebuilds `app_string_refs.tsv` from the UI ELF plus a Ghidra function-name list. The ELF in this repo is `firmware/Firmware/firmware`. The function-name list is not published (it is a local Ghidra export).

```
IVI_FNSTR=/path/to/app.fnstr.txt python3 strrefs.py > app_string_refs.tsv
python3 make_csv.py app_string_refs.tsv
```

`make_csv.py` reads a TSV (default `app_string_refs.tsv` in the current directory) and writes `commands.csv` beside it. The checked-in copy of the TSV is [docs/data/app_string_refs.tsv](../../docs/data/app_string_refs.tsv).

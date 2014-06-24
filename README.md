# Zeri e Lode
## Extracting the Zeri photo archive to Linked Open Data

This set of Python scripts aim to convert a FZeri XML catalogue into CIDOC-CRM compliant RDF document.

[CIDOC-CRM v5.0.4](http://www.cidoc-crm.org/official_release_cidoc.html) has been used as reference ([RDFs file](http://www.cidoc-crm.org/rdfs/cidoc_crm_v5.0.4_official_release.rdfs))

## REQUIREMENTS
- Python 2.7

## USAGE

```
usage: fzeri_schedaF_to_owl.py [-h] [--single-entry] [-o OUTPUT_FILE]
                               [-f FORMAT]
                               source_file [source_file ...]

FZeri to CIDOC-CRM catalog conversion script.

positional arguments:
  source_file           FZeri catalog file(s) path

optional arguments:
  -h, --help            show this help message and exit
  --single-entry        Outputs entries in a single file for each one.
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Output file or directory name
  -f FORMAT, --format FORMAT
                        Output format (xml|n3|turtle|nt|pretty-xml|trix)
```

## COPYRIGHT
Copyright (c) 2014 Ciro Mattia Gonano  
Released under MIT LICENSE; see LICENSE.txt for further details.
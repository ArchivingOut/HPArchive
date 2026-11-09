# HPArchive: the wizarding world as a network
An interactive Digital Humanities archive of the Harry Potter novels and films: a 3D network of characters, houses, families, groups, places, objects and film cast, with typed, evidence-labelled relationships.
**Run:** open `index.html` (single file, works offline). **Host:** GitHub Pages (Settings → Pages → main).

## Features
3D network (colour by house/community/type, filter by relationship family, evidence class and book, shortest path, focus mode) · Characters directory (610, filterable) · Family trees · Timeline · Compare two characters · Books & films · Insights (PageRank, communities, house × ancestry) · guided stories · exports for Gephi (GraphML), CSV and Neo4j.

## Evidence classes (every link has one)
- `dataset`: houses and groups from a wiki-derived character JSON (Laboratoria/BOG005-data-lovers, no stated licence; content from the Harry Potter Fandom wiki, CC BY-SA). Kept in `data/source_harry.json`.
- `canon`: relationships we encoded from the novels (family, mentors, enemies, killings, Horcruxes, Hallows, homes), with book numbers. `medium` confidence = verify against the books.
- `film`: cast and directors for the eight films; film numbers only where confident.

## Rebuild
```
pip install networkx numpy
python pipeline/build_hp.py data/source_harry.json data
python pipeline/build_site.py pipeline/template.html data/hp.json index.html
```
## Add verified data
Edit `pipeline/curated.py`: `r("Harry Potter","Sirius Black","GODPARENT_OF","godfather",[3],"high")`, then rebuild.
## Rights
No book or film text, scripts or images are included: only facts and relationships. Unofficial; not affiliated with J.K. Rowling, Warner Bros. or Wizarding World. Code: MIT. Verify the dataset's licence before commercial reuse.
## Known limits
Group links are not time-bound · only 7 novels + 8 films · centrality reflects documentation density, not story importance · minor characters unevenly covered.


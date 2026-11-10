# HPArchive — a fan reference companion

An interactive, static archive about the Harry Potter main series. Browse a searchable character directory, relationship network, family trees, timeline, book and film notes, a seven-book story journey, and searchable spell and potion names.

## Open the public site

https://archivingout.github.io/HPArchive/

## Coverage

- 704 directory records in this build: 598 named-character records and 106 unnamed-relative references. The new data also distinguishes named people from unnamed family references instead of treating every source label as a character.
- Coverage follows the seven novels and eight film adaptations. The source is not an exhaustive census of every Wizarding World character across plays, prequels, games, adaptations, and other publications.
- The Story Journey contains 56 spoiler-heavy, fan-written beats supplied in the project HTML, grouped by novel, with original vector scenes, animated symbolic character tokens, book filters, playback, and clickable cast links. It is a companion, not a substitute for the books or an official adaptation.
- The seven short book overviews remain available alongside the slides. Memory cards and a just-for-fun house quiz use the archive directory.
- The homepage uses an original HPArchive fan mark, not the official Harry Potter film logo. No official character imagery or film stills are used.
- The Spellbook lists names and categories only. Character profiles and story links use the archive's relationship data.

## Use

Open `index.html` for the offline version. The online site deploys from `main` with GitHub Pages whenever the Pages workflow succeeds.

To rebuild data locally, install `networkx` and `numpy`, then run:

```
python pipeline/build_hp.py data/source_harry.json data
python pipeline/build_site.py pipeline/template.html data/hp.json index.html
```

## Sources and rights

The structured character data originates in a wiki-derived dataset associated with [Laboratoria/BOG005-data-lovers](https://github.com/Laboratoria/BOG005-data-lovers). The upstream project's source is based on the [Harry Potter Wiki](https://harrypotter.fandom.com/), whose community text is published under [CC BY-SA](https://harrypotter.fandom.com/wiki/Harry_Potter_Wiki:Copyrights), except where stated otherwise. Attribution and share-alike terms apply to wiki-derived material; review the source notices before reuse.

Relationship curation, code and story summaries are maintained separately. No novel text, film scripts, official stills or official character artwork are included. For licensed encyclopedia content, see the [official Harry Potter Fact Files](https://www.harrypotter.com/fact-file). Unofficial fan project; not affiliated with or endorsed by the rights holders.

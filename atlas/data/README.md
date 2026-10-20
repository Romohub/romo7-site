# Atlas data model

This directory is the source of truth for the Atlas of Stories. Pages should be rendered from structured records, not manually duplicated across HTML files.

## Entity collections

- `traditions.json`: individually addressable cultural traditions and contexts. Do not treat the registry as a complete list of all world traditions.
- `characters.json`: individual figures, with multilingual names and identifiers.
- `narratives.json`: stories, epics, oral narratives, and documented variants.
- `motifs.json`: recurring motifs and narrative patterns.
- `places.json`: real, ritual, literary, and cosmological places, clearly distinguished.
- `sources.json`: bibliographic records and stable source links.
- `relations.json`: typed links between records, with evidence.

## Required editorial principles

1. Every record has a stable, never-recycled ID.
2. Every factual claim should be traceable to a source; citations should identify a page, passage, object ID, or other precise locator when possible.
3. A relation is not a fact merely because two items look alike. Record the relation type and its evidence separately.
4. Distinguish alternate names, versions of one narrative, thematic parallels, documented influence/borrowing, and research hypotheses.
5. Preserve local names and scripts alongside transliterations; identify language, place, time period, and the limits of each claim.
6. Respect the rights, attribution requirements, access protocols, and community preferences for living and Indigenous traditions. Do not publish restricted or sacred material without appropriate authorization.
7. Status values: `planned`, `in_research`, `needs_review`, `reviewed`. “Reviewed” means editorially checked against cited evidence, not universally settled.
8. Keep source metadata and rights metadata separate from the content itself.

## Relationship types

- `alternate_name_of`
- `depicts_or_refers_to`
- `character_in_narrative`
- `variant_of_narrative`
- `thematic_parallel`
- `documented_influence`
- `shared_historical_context`
- `related_place`
- `related_motif`
- `hypothesis_of_connection`

Every relation should include `source_ids`, a short rationale, review status, and a directionality field where relevant.

## Suggested workflow

Researcher adds a draft record → attaches sources and exact locators → records only defensible relations → second-pass review → record becomes visible as reviewed. Draft and unreviewed material must be visibly labelled in the public interface.

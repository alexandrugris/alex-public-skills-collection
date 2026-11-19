# Binaries archive: the complete ag-personal-brand snapshot

The GitHub connector used to build this collection writes text files only.
A binary pushed through it is UTF-8-inflated and corrupted (tested and
measured on 2026-11-19: a 48,223-byte PNG came back as 71,444 bytes, so the
corrupt test file was removed). So that nothing is lost when
github.com/alexandrugris/ag-personal-brand is deleted, its complete
snapshot lives here as base64 text in 11 parts, byte-identical to the
tarball GitHub serves for that repository.

- Snapshot: 79 files, 10 directories, 9.4 MB uncompressed
- Original tarball: ag-personal-brand-main, 7,219,563 bytes
- SHA-256: 148dd36d700b4ddd741f670c52f763533ac09015604cdcc946edaf9508eb2173
- Verification (2026-11-19): all 11 parts were fetched back from this repo,
  concatenated and compared with the original base64: identical.

## Restore

    cat ag-personal-brand-snapshot.tar.gz.b64.part-* \
      | base64 -d > ag-personal-brand-snapshot.tar.gz
    sha256sum ag-personal-brand-snapshot.tar.gz
    # expect: 148dd36d700b4ddd741f670c52f763533ac09015604cdcc946edaf9508eb2173
    tar xzf ag-personal-brand-snapshot.tar.gz    # -> ag-personal-brand-main/

That directory is the full source repo: 17 TTF fonts (Gelasio, Inter,
IBM Plex Mono, all SIL OFL, licenses included), the original reference
gallery (AG Style Guide PDF and cover PNG, sample deck PPTX/PDF, page and
document PNGs, five slides, the distributed toolkit ZIP), the regenerated
outputs (deck, document renders, page screenshot), and all text assets
(which also live, working, one level up in `../`).

## After restoring

Once the binaries are copied to their proper paths, or once you keep a
local clone of the source repo, this archive folder can be deleted from
this repository; the snapshot will have served its purpose. It exists so
the deletion of ag-personal-brand loses nothing.
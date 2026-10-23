# Publishing Checklist

This checklist is for publishing the artifact as
`https://github.com/ono-work/GLB-resources` through the `agent-maria` account.
It contains no credentials and does not authorize an external push by itself.

## 1. Human review

- confirm the repository name and public description;
- confirm that `Hirotaka Ono` is the intended copyright and citation name;
- confirm the MIT License;
- inspect `PAPER_RESULTS.md`, especially the `PARTIAL_STOP` explanation;
- decide whether the camera-ready paper should cite the repository URL, a
  tagged Release URL, or a later DOI.

Suggested GitHub description:

> Computational artifact for a lower bound on the number of partizan games born by day 4.

## 2. Final local check

```console
python scripts/build_checksums.py
python scripts/verify_all.py
```

The expected final integer is

```text
1425933741673169505174021654095740659
```

Run a secret scan before the first push. Do not add local credentials, shell
history, editor state, unselected checkpoints, or files from the private
research tree that are not listed in the provenance policy.

## 3. Create and push the repository

Create an empty public repository named `GLB-resources` under `ono-work`, with
no automatically generated README or license. From this artifact directory,
initialize the `main` branch, make the first commit, add the GitHub remote, and
push while authenticated as `agent-maria`.

Commit authorship records the account performing the packaging operation.
Scientific authorship and citation metadata remain those in `CITATION.cff` and
the accompanying paper.

## 4. Freeze the paper release

Recommended first tag:

```text
gpw26-v1.0
```

Suggested Release title:

```text
GPW 2026 paper artifact v1.0
```

The Release notes should state the exact final bound, the quick verification
command, the meaning of `PARTIAL_STOP`, and that no incomplete candidate
contributes to the bound.

The paper should refer to this immutable tag or Release rather than only to the
moving `main` branch.

## 5. Optional archival DOI

After the GitHub Release is final, the repository can be connected to Zenodo
and the Release archived. If a DOI is minted before the camera-ready deadline,
add it to `CITATION.cff` and cite it in the paper. Otherwise, cite the frozen
GitHub Release and add the DOI later without altering the scientific result.

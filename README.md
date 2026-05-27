# gix

`gix` is a local AI layer for Git that works between `commit` and `push`.
It helps standardize commits, propose safe code fixes, and orchestrate external tools via plugins.

## Czy coś takiego już istnieje?

Częściowo: istnieją narzędzia do AI commit messages, git hooks, albo przepisywania historii commitów.
Brakuje jednak jednego, lokalnego operatora, który:

- prowadzi interakcję z użytkownikiem po commicie,
- proponuje poprawki kodu jako kolejne commity (`fixup!`),
- porządkuje historię przed `push`,
- integruje pluginy przez MCP/REST/CLI/gRPC.

## Kierunek dla `gix`

1. **Local-first i bezpieczne domyślne zachowanie**
   - AI proponuje zmiany, użytkownik zatwierdza.
   - Preferowane są `fixup!` commity zamiast automatycznego nadpisywania historii.

2. **Warstwa hooków Git**
   - `pre-commit`: walidacja polityk i szybkie poprawki.
   - `post-commit`: analiza świeżego commita, propozycje kolejnych patchy.
   - `pre-push`: standaryzacja historii (`autosquash`, nazewnictwo commitów, final checks).

3. **Plugin architecture**
   - Wspólny kontrakt wejście/wyjście (JSON schema).
   - Adaptery pluginów: MCP, REST, CLI shell, gRPC/protobuf.

## Przykład użycia (MVP)

```bash
# 1) inicjalizacja hooków w repo
gix init

# 2) standardowy commit użytkownika
git add -p
git commit -m "wip"

# 3) gix wykrywa problemy i proponuje fixup commit
gix hook post-commit

# 4) przed push gix proponuje porządkowanie historii
gix hook pre-push
```

Przykładowa interakcja:

```text
gix: Znaleziono 2 problemy (null-check, commit message).
gix: Zastosować patch i dodać commit "fixup! ..."? [Y/n]
```

## Plan MVP

- MVP 1: hooki + policy engine + interakcja CLI
- MVP 2: patching + fixup workflow + pre-push autosquash
- MVP 3: stabilne API pluginów i integracje MCP/REST/CLI/gRPC

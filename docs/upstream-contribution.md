# Proposed upstream contributions

These are local review scopes, not opened PRs or promises of future maintenance.
The functional snapshot remains intact under its dated tag. Contribution branches
should be assembled separately from current upstream, with relevant tests and
sanitized observations carried together. Do not rewrite the archival snapshot.

## Evidence and policy to settle first

The Nord tests were performed by the fork owner, not Gaz. This snapshot retains
the existing `verified` write gate to preserve the working runtime. An upstream
submission needs an agreed owner/community-tested write policy. The existing
[Buds 4 PR #2](https://github.com/GazzasaurusRex/oneplus-buds-omarchy/pull/2) proposes
`community_writes_tested` for precisely that distinction. Reuse/coordinate that
approach rather than silently claiming maintainer tests or removing Nord writes.
Do not merge the Buds 4 branch into the snapshot as part of publication cleanup.

## Scope 1 — Nord profile and state corrections

Proposed title: **Add owner-tested Nord Buds 3 Pro profile and ANC/case state fixes**

Include the product-specific profile, English Low/Moderate/High/Auto labels,
verified preset IDs, capability filtering, warm ANC strength reuse, Auto
notification handling and last-known case battery. Carry the parser/profile/
controller tests and relevant device records. Keep writes scoped to measured
products. Explain shared-controller effects on Pro/Pro 2 and ask for their
maintainer hardware regression check; do not infer it from Nord results.

## Scope 2 — Confirmed touch, feature and find controls

Proposed title: **Add verified Nord touch, feature and Find Play/Stop controls**

Build on the accepted profile/policy. Include command parsing, allowlists,
fresh read-back, unknown find-state Stop, one-shot 50-second stop, same-pair
identity checks and reconnect without replay. Carry the tests, UI tooltips and
hardware observation limits together. No new phone-side spatial DSP or generic
unknown-model feature writes are part of this scope.

## Scope 3 — EQ profiles and Omarchy UI

Proposed title: **Add release-to-save EQ curve editing and custom profile management**

Include device-defined curve geometry, slot limits, profile create/rename/delete
with confirmation and original active-profile restoration, identity protection,
KeyboardPanel text entry, themed Dropdown and balanced feature layout. Keep the
QML/export tests and real panel observations. Profile creation limits and returned
IDs must stay model-specific; Pro 2 hardware behaviour needs maintainer checking.

The exact boundaries depend on accepted prerequisites; these scopes are not
independent cherry-pick instructions. Before opening each PR, verify a complete
runnable branch and write its description around final behaviour and evidence.
Each PR should state that it is offered as a one-time owner contribution.
Fork-specific repository metadata, snapshot-only publishing instructions and the
personal backup bundle do not belong in upstream feature commits.

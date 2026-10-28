# Touch controls

Requested by the owner: add touch configuration to the existing plugin panel.
Use the existing Python session/controller/bridge and QML service; no dependencies.

Show each observed gesture for left and right. Read fresh state on panel opening
and offer a refresh action. Editable choices come from the Nord Buds 3 Pro's
decrypted app table, with app action IDs translated to wire IDs. The fixed
noise-control hold gesture is shown without a selector. Call controls remain
fixed and are described separately, as the ordinary gesture query does not
report independent call assignments.

Prefer one-binding writes over replacing the whole table: the command supports
a count and four-byte entries, so unrelated mappings need not be touched. A
whole-table editor would risk overwriting simultaneous phone-app changes.
Validate the model, side, button, action and function before writing. Confirm
every write by a fresh correlated query, showing actual state on disagreement.
Malformed or failed reads must not masquerade as an empty successful result.

Hardware tests save the complete original table and restore it in a finally
block, then compare the complete table. No codec or other feature writes.
Keep the popup's fixed width and bounded scroll area. Preserve upstream paths.

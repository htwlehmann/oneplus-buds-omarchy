# Custom EQ curve editor

Approved conversation design: replace numeric fields with a six-band editable
curve, values above, frequencies below, range -6..+6dB for Nord, theme accent
stroke/handles and a downward fade to transparent. User selected saving on
pointer release, replacing Apply. Retain custom-slot selection and disclosure.

Use a native QML component in the current EQ column; graph adapts to width and
reads band definitions/range/step from the actual entry. Equal horizontal band
spacing follows the app screenshots. Smooth monotone segments avoid overshoot.
Keyboard Up/Down changes the focused band and saves on key release.

Local preview during dragging, exactly one request after changed release, no
request for unchanged/cancelled gestures. Disable editing while a request is
pending, disconnected, collapsed or unsupported. Status polls may refresh a
clean graph but must not reset an ongoing drag. Entry/device changes cancel it.
Settle using fresh readback and show failure rather than implying success.

Implementation choice: Qt Quick Shapes and a small pure JS curve helper,
using existing Color.accent bindings. Existing verified backend wire writes
stay unchanged. Add optional physical-device token to custom-EQ requests to
prevent recovery from redirecting an automatic write to another pair.

Keep this in the installed fork explicitly selected by the user. No Obsidian
edits without consent. Live verification changes one band and restores the
original full curve and selection.

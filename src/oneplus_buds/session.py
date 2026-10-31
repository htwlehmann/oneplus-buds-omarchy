from __future__ import annotations

from dataclasses import asdict
from time import monotonic

from .bluez import Device
from .lifecycle_trace import mark, span
from .models import ControlResult, EqControlResult, EqStatusResult, EventBatch, SafeEvent, StatusResult
from .timing import AncRequestError, PhaseTimer
from .profiles import DeviceProfile, profile_for_product
from .protocol import (
    HELLO,
    NOTIFY_FEATURE_SWITCHES,
    NOTIFY_STATE,
    QUERY_BROADCAST_CODES,
    QUERY_CAPABILITIES,
    QUERY_PRODUCT_ID,
    QUERY_BATTERY,
    QUERY_BASS_ENGINE,
    QUERY_REMOTE_VERSION,
    RESPONSE_PRODUCT_ID,
    RESPONSE_REMOTE_VERSION,
    AncState,
    parse_anc_state,
    parse_product_id,
    parse_remote_version,
    format_firmware_version,
    QUERY_ANC,
    QUERY_EQ,
    QUERY_EQ_ALL,
    QUERY_STATUS,
    SET_ANC,
    SET_EQ,
    SET_EQ_DETAIL,
    SET_BASS_ENGINE,
    SET_FEATURE_SWITCH,
    SET_FIND_MODE,
    BASS_LEVEL_MAX,
    BASS_LEVEL_MIN,
    BASS_LEVEL_NOTICE,
    BASS_LEVEL_RANGE,
    RESPONSE_SET_ANC,
    RESPONSE_BASS_ENGINE,
    RESPONSE_SET_BASS_ENGINE,
    RESPONSE_SET_FEATURE_SWITCH,
    RESPONSE_SET_FIND_MODE,
    REGISTER,
    RESPONSE_ANC,
    RESPONSE_EQ,
    RESPONSE_EQ_ALL,
    RESPONSE_SET_EQ,
    RESPONSE_SET_EQ_DETAIL,
    RESPONSE_BATTERY,
    RESPONSE_STATUS,
    SUBSCRIBE_BROADCAST,
    Frame,
    FEATURE_SWITCH_NAMES,
    EQ_ALL_QUERY_PAYLOAD,
    EqEntry,
    encode_eq_detail_payload,
    parse_anc_state,
    parse_battery,
    parse_broadcast_codes,
    parse_eq_entries,
    parse_eq_id,
    parse_feature_switches,
    parse_set_anc_status,
    parse_set_eq_status,
)
from .transport import RfcommTransport
from .protocol import QUERY_TOUCH, RESPONSE_TOUCH, SET_TOUCH, RESPONSE_SET_TOUCH
from .touch import TouchBinding, parse_touch_bindings, HOLD_CYCLE_QUERY, hold_cycle_mask, parse_hold_cycle


class UnsupportedProductError(RuntimeError):
    def __init__(self, device: Device, product_id: str | None) -> None:
        super().__init__(f"product {product_id or 'unknown'} has no tested device profile")
        self.device = device
        self.product_id = product_id


class OpoSession:
    def __init__(self, device: Device, profile: DeviceProfile,
                 *, transport: RfcommTransport | None = None) -> None:
        self.device = device
        self.profile = profile
        self._transport = transport or RfcommTransport(device.address, connect_attempts=4)
        self._version_pending = False
        self._version_sequence: int | None = None
        self._subscription_pending = False
        self._connected = False
        self._authenticated = False
        self._last_battery_refresh = monotonic()
        self.advertised_event_codes: tuple[int, ...] = ()

    @classmethod
    def bootstrap(cls, device: Device) -> tuple["OpoSession", StatusResult, EventBatch]:
        """Identify, authenticate and read essential state on one owned socket."""
        transport = RfcommTransport(device.address, connect_attempts=4)
        transport.__enter__()
        try:
            # Preserve the existing capability primer and authentication waits.
            transport.query(QUERY_CAPABILITIES)
            with span("query", command=QUERY_PRODUCT_ID):
                product = parse_product_id(transport.request(
                    QUERY_PRODUCT_ID, b"", RESPONSE_PRODUCT_ID))
            profile = profile_for_product(product)
            if profile is None:
                raise UnsupportedProductError(device, product)
            mark("profile_resolved", product_id=product)
            session = cls(device, profile, transport=transport)
            session._connected = True
            initial = session.authenticate(primed=True)
            received: list[Frame] = []
            with span("query", command=QUERY_BATTERY):
                battery = parse_battery(transport.request(
                    QUERY_BATTERY, b"", RESPONSE_BATTERY, on_frames=received.extend))
            if battery is None:
                raise RuntimeError("essential device state is not available")
            if "case_battery" not in profile.capabilities:
                # Only expose case readings for profiles with case support.
                battery = {name: value for name, value in battery.items()
                           if name != "case"}
            with span("query", command=QUERY_ANC):
                anc = parse_anc_state(transport.request(
                    QUERY_ANC, b"\x01\x01", RESPONSE_ANC, on_frames=received.extend), profile.anc)
            if battery is None or anc is None:
                raise RuntimeError("essential device state is not available")
            status = StatusResult(device=device, product_id=product, model=profile.name,
                remote_version=(), firmware_version=None, battery=battery,
                anc=anc.mode, anc_level=anc.level)
            # Essential query responses are newer than setup notifications.
            extra = session._redact(received)
            events = tuple(event for event in initial.events + extra.events
                           if event.kind not in ("battery", "anc"))
            session._version_pending = True
            session._subscription_pending = True
            return session, status, EventBatch(events, initial.ignored_frames + extra.ignored_frames)
        except BaseException:
            transport.__exit__(None, None, None)
            raise

    def __enter__(self) -> "OpoSession":
        self._transport.__enter__()
        self._connected = True
        return self

    def __exit__(self, *args: object) -> None:
        self._connected = False
        self._authenticated = False
        self._transport.__exit__(*args)

    def authenticate_and_subscribe(self, *, primed: bool = False) -> EventBatch:
        authenticated = self.authenticate(primed=primed)
        subscribed = self._subscribe()
        return EventBatch(
            authenticated.events + subscribed.events,
            authenticated.ignored_frames + subscribed.ignored_frames,
        )

    def authenticate(self, *, primed: bool = False) -> EventBatch:
        mark("authentication.begin")
        self._require_connected()
        frames: list[Frame] = []
        if not primed:
            frames.extend(self._transport.query(QUERY_CAPABILITIES))
        frames.extend(self._transport.exchange_raw(HELLO, wait=2.0))
        frames.extend(self._transport.exchange_raw(REGISTER, wait=1.5))
        self._authenticated = True
        mark("authentication.end")
        return self._redact(frames)

    def _subscribe(self) -> EventBatch:
        self._require_connected()
        if not self._authenticated:
            raise RuntimeError("session authentication has not completed")
        mark("subscription.begin")
        frames: list[Frame] = []
        advertised_frames = self._transport.query(QUERY_BROADCAST_CODES, wait=0.5)
        frames.extend(advertised_frames)
        advertised = next(
            (codes for frame in advertised_frames if (codes := parse_broadcast_codes(frame)) is not None),
            b"",
        )
        self.advertised_event_codes = tuple(advertised)
        if advertised:
            payload = bytes((len(advertised),)) + advertised
            frames.extend(self._transport.query(SUBSCRIBE_BROADCAST, payload, wait=0.5))
        mark("subscription.end")
        return self._redact(frames)

    def set_anc(self, mode: str) -> tuple[ControlResult, EventBatch]:
        """Reuse authentication; verify with a fresh, correlated state query.

        SET status alone is never proof of the new state. Auto can be
        confirmed by the selected-mode notification when the query reports
        the concrete intensity chosen by the adaptive mode.
        The caller discards a failed transaction's session before recovery.
        """
        self._require_connected()
        if not self._authenticated:
            raise RuntimeError("session authentication has not completed")
        if not self.profile.verified or mode not in self.profile.anc.write_indices:
            raise ValueError("ANC mode is not supported by a verified profile")
        timer = PhaseTimer()
        events: list[SafeEvent] = []
        ignored = 0
        selected_notification: AncState | None = None

        def collect(frames: list[Frame]) -> None:
            nonlocal ignored, selected_notification
            for frame in frames:
                if frame.command == NOTIFY_STATE and frame.payload[:3] == b"\x03\x01\x01":
                    selected_notification = parse_anc_state(frame, self.profile.anc)
            batch = self._redact(frames)
            events.extend(batch.events)
            # Keep memory bounded even if the peer floods notifications.
            del events[:-64]
            ignored += batch.ignored_frames

        try:
            try:
                acknowledgement = self._transport.request(
                    SET_ANC, self.profile.anc.payload_for(mode), RESPONSE_SET_ANC,
                    sequence=self.profile.anc.sequence_for(mode),
                    on_sent=lambda: timer.elapsed("command_sent_elapsed"), on_frames=collect,
                )
            except TimeoutError:
                # Some firmware omits SET acknowledgement. Never replay SET;
                # verification still needs independent device state.
                acknowledgement = None
            timer.mark("set_response")
            expected_mode = mode if mode in ("off", "transparency", "on") else "on"
            expected_level = None if mode in ("off", "transparency", "on") else mode

            def confirmed_auto() -> AncState | None:
                if (mode == "auto" and selected_notification is not None
                        and selected_notification.mode == "on"
                        and selected_notification.level == "auto"):
                    return selected_notification
                return None

            # SET acknowledgement can precede physical application. A first
            # fresh query may legitimately return the previous mode. Re-query
            # on each response, bounded by both time and count; never replay SET.
            observed = None
            deadline = monotonic() + 2.0
            for query_count in range(1, 33):
                remaining = deadline - monotonic()
                if remaining <= 0:
                    break
                try:
                    state = self._transport.request(
                        QUERY_ANC, b"\x01\x01", RESPONSE_ANC, on_frames=collect,
                        timeout=remaining,
                    )
                except TimeoutError:
                    observed = confirmed_auto()
                    if observed is None:
                        raise
                    break
                observed = parse_anc_state(state, self.profile.anc) if state.payload[:1] == b"\x00" else None
                if observed is not None and observed.mode == expected_mode and (
                    expected_level is None or observed.level == expected_level
                ):
                    break
                adaptive = confirmed_auto()
                if adaptive is not None:
                    observed = adaptive
                    break
            else:
                observed = None
            timer.mark("verify_query")
            if observed is None or observed.mode != expected_mode or (
                expected_level is not None and observed.level != expected_level
            ):
                observed = confirmed_auto()
                if observed is None:
                    raise RuntimeError(
                        "ANC verification failed: fresh state did not match request")
            timer.elapsed("verified_elapsed")
            result = ControlResult(
                name=self.device.name, product_id=self.profile.product_id,
                anc=observed.mode, anc_level=observed.level,
                set_status=parse_set_anc_status(acknowledgement) if acknowledgement else None,
                verified=True,
                timings_ms=timer.finish("session_total"),
                verification_queries=query_count,
            )
            return result, EventBatch(tuple(events), ignored)
        except (OSError, RuntimeError, ValueError) as error:
            timer.mark("failed_phase")
            raise AncRequestError("ANC session request failed: " + str(error),
                                  timer.finish("session_total")) from error

    def eq_status(self) -> tuple[EqStatusResult, EventBatch]:
        self._require_eq_session(write=False)
        frames: list[Frame] = []
        current_frame = self._transport.request(
            QUERY_EQ, b"", RESPONSE_EQ, on_frames=frames.extend,
        )
        entries_frame = self._transport.request(
            QUERY_EQ_ALL, EQ_ALL_QUERY_PAYLOAD, RESPONSE_EQ_ALL, on_frames=frames.extend,
        )
        current_id = parse_eq_id(current_frame)
        entries = parse_eq_entries(entries_frame)
        if current_id is None or entries is None:
            raise RuntimeError("device returned malformed native EQ state")
        return self._eq_result(current_id, entries), self._redact(frames)

    def set_eq(self, preset: str) -> tuple[EqControlResult, EventBatch]:
        """Select one native EQ entry once, then verify with fresh device state."""
        self._require_eq_session(write=True)
        timer = PhaseTimer()
        before, initial = self.eq_status()
        timer.mark("preserve_read")
        target_id, target_name = self._resolve_eq_target(preset, before)
        events = list(initial.events)
        ignored = initial.ignored_frames

        # Some device families select a custom curve by writing it, not with
        # the plain preset command: the plain command only switches the
        # factory presets. Writing the unchanged curve back selects the custom
        # entry without altering the sound.
        custom = next((item for item in before.custom_entries
                       if item.eq_id == target_id), None)
        if custom is not None:
            return self.set_custom_eq(
                custom.eq_id, tuple(band.gain_db for band in custom.bands))

        def collect(frames: list[Frame]) -> None:
            nonlocal ignored
            batch = self._redact(frames)
            events.extend(batch.events)
            del events[:-64]
            ignored += batch.ignored_frames

        try:
            try:
                acknowledgement = self._transport.request(
                    SET_EQ, bytes((target_id,)), RESPONSE_SET_EQ,
                    on_sent=lambda: timer.elapsed("command_sent_elapsed"), on_frames=collect,
                )
            except TimeoutError:
                acknowledgement = None
            timer.mark("set_response")
            observed_id = None
            deadline = monotonic() + 2.0
            for query_count in range(1, 33):
                remaining = deadline - monotonic()
                if remaining <= 0:
                    break
                frame = self._transport.request(
                    QUERY_EQ, b"", RESPONSE_EQ, on_frames=collect, timeout=remaining,
                )
                observed_id = parse_eq_id(frame)
                if observed_id == target_id:
                    break
            timer.mark("verify_query")
            if observed_id != target_id:
                raise RuntimeError("EQ verification failed: fresh state did not match request")
            # Re-read the device-authored catalogue. This independently proves
            # custom definitions were not overwritten by a preset selection.
            verified, batch = self.eq_status()
            events.extend(batch.events)
            ignored += batch.ignored_frames
            if verified.current_id != target_id:
                raise RuntimeError("EQ verification failed: catalogue state did not match request")
            timer.elapsed("verified_elapsed")
            return EqControlResult(
                self.device.name, self.profile.product_id, target_id, target_name,
                before.current_id, before.current_name,
                parse_set_eq_status(acknowledgement) if acknowledgement else None,
                True, timer.finish("session_total"), query_count,
            ), EventBatch(tuple(events), ignored)
        except (OSError, RuntimeError) as error:
            raise RuntimeError("EQ session request failed: " + str(error)) from error

    def set_custom_eq(self, entry_id: int, gains_db: tuple[int, ...]) -> tuple[EqControlResult, EventBatch]:
        """Update an existing device-declared custom curve; never invent a layout."""
        self._require_eq_session(write=True)
        if self.profile.eq is None or not self.profile.eq.custom_write_verified:
            raise ValueError("custom EQ writes are not hardware-verified for this device profile")
        timer = PhaseTimer()
        before, initial = self.eq_status()
        timer.mark("preserve_read")
        entry = next((item for item in before.custom_entries if item.eq_id == entry_id), None)
        if entry is None:
            raise ValueError("custom EQ id was not declared by the connected earbuds")
        payload = encode_eq_detail_payload(entry, gains_db)
        events = list(initial.events)
        ignored = initial.ignored_frames

        def collect(frames: list[Frame]) -> None:
            nonlocal ignored
            batch = self._redact(frames)
            events.extend(batch.events)
            del events[:-64]
            ignored += batch.ignored_frames

        try:
            try:
                acknowledgement = self._transport.request(
                    SET_EQ_DETAIL, payload, RESPONSE_SET_EQ_DETAIL,
                    on_sent=lambda: timer.elapsed("command_sent_elapsed"), on_frames=collect,
                )
            except TimeoutError:
                acknowledgement = None
            timer.mark("set_response")
            verified = None
            deadline = monotonic() + 2.0
            for query_count in range(1, 33):
                remaining = deadline - monotonic()
                if remaining <= 0:
                    break
                frame = self._transport.request(
                    QUERY_EQ_ALL, EQ_ALL_QUERY_PAYLOAD, RESPONSE_EQ_ALL,
                    on_frames=collect, timeout=remaining,
                )
                entries = parse_eq_entries(frame)
                verified = next((item for item in entries or () if item.eq_id == entry_id), None)
                if verified is not None and tuple(band.gain_db for band in verified.bands) == gains_db:
                    break
            timer.mark("verify_query")
            if verified is None or tuple(band.gain_db for band in verified.bands) != gains_db:
                raise RuntimeError("custom EQ verification failed: fresh curve did not match request")
            current = self._transport.request(QUERY_EQ, b"", RESPONSE_EQ, on_frames=collect)
            current_id = parse_eq_id(current)
            if current_id != entry_id:
                raise RuntimeError("custom EQ verification failed: updated entry is not selected")
            timer.elapsed("verified_elapsed")
            return EqControlResult(
                self.device.name, self.profile.product_id, entry_id, verified.name,
                before.current_id, before.current_name,
                parse_set_eq_status(acknowledgement) if acknowledgement else None,
                True, timer.finish("session_total"), query_count,
            ), EventBatch(tuple(events), ignored)
        except (OSError, RuntimeError) as error:
            raise RuntimeError("custom EQ session request failed: " + str(error)) from error

    def _require_eq_session(self, *, write: bool) -> None:
        self._require_connected()
        if not self._authenticated:
            raise RuntimeError("session authentication has not completed")
        if self.profile.eq is None:
            raise ValueError("native EQ is not supported by this device profile")
        if write and (not self.profile.verified or not self.profile.eq.write_verified):
            raise ValueError("native EQ writes are not hardware-verified for this device profile")

    def _eq_result(self, current_id: int, entries: tuple[EqEntry, ...]) -> EqStatusResult:
        eq = self.profile.eq
        if eq is None:
            raise ValueError("native EQ is not supported by this device profile")
        preset = next((item for item in eq.presets if item.eq_id == current_id), None)
        custom = next((item for item in entries if item.eq_id == current_id), None)
        if preset is not None:
            current_name, current_kind = preset.name, "factory"
        elif custom is not None:
            current_name, current_kind = custom.name, "custom"
        else:
            current_name, current_kind = f"Unknown ({current_id})", "unknown"
        presets = tuple({"id": item.eq_id, "key": item.key, "name": item.name}
                        for item in eq.presets)
        return EqStatusResult(
            self.device.name, self.profile.product_id, self.profile.name,
            current_id, current_name, current_kind, presets, entries,
            1 if entries else None,
        )

    def _resolve_eq_target(self, value: str, status: EqStatusResult) -> tuple[int, str]:
        eq = self.profile.eq
        if eq is None:
            raise ValueError("native EQ is not supported by this device profile")
        preset = eq.preset_for(value)
        if preset is not None:
            return preset.eq_id, preset.name
        normalized = value.strip().lower()
        for entry in status.custom_entries:
            if normalized in (f"custom:{entry.eq_id}", entry.name.lower()):
                return entry.eq_id, entry.name
        raise ValueError("EQ target is not a verified preset or device-declared custom entry")

    def poll(self, wait: float = 0.2) -> EventBatch:
        self._require_connected()
        setup = EventBatch((), 0)
        if self._subscription_pending:
            self._subscription_pending = False
            setup = self._subscribe()
        if self._version_pending:
            self._version_pending = False
            self._version_sequence = self._transport.send_query(QUERY_REMOTE_VERSION)
            mark("optional_firmware_sent")
        now = monotonic()
        if "case_battery" in self.profile.capabilities and now - self._last_battery_refresh >= 10:
            self._last_battery_refresh = now
            # Read the response through normal polling, without a blocking
            # query/drain while foreground commands wait for the controller.
            self._transport.send_query(QUERY_BATTERY)
        received = self._redact(self._transport.receive(wait))
        return EventBatch(
            setup.events + received.events,
            setup.ignored_frames + received.ignored_frames,
        )

    def read_hold_cycle(self) -> int:
        self._require_connected()
        if not self.profile.hold_cycle_supported:
            raise ValueError("hold cycle is not supported by this device profile")
        frame = self._transport.request(QUERY_ANC, HOLD_CYCLE_QUERY, RESPONSE_ANC)
        try:
            return parse_hold_cycle(frame)
        except ValueError as error:
            raise RuntimeError(str(error)) from error

    def set_hold_cycle(self, modes: tuple[str, ...]) -> tuple[int | None, int]:
        self._require_connected()
        if not self._authenticated:
            raise RuntimeError("session authentication has not completed")
        if not self.profile.verified or not self.profile.hold_cycle_supported:
            raise ValueError("hold cycle writes are not verified for this device profile")
        mask = hold_cycle_mask(modes)
        self.read_hold_cycle()  # require valid current state before writing
        try:
            ack = self._transport.request(SET_ANC, HOLD_CYCLE_QUERY + bytes((mask,)), RESPONSE_SET_ANC)
            if len(ack.payload) != 1:
                raise RuntimeError("device returned malformed hold cycle acknowledgement")
            status = ack.payload[0]
        except TimeoutError:
            status = None
        return status, self.read_hold_cycle()

    def touch_bindings(self) -> tuple[TouchBinding, ...]:
        self._require_connected()
        if not self.profile.touch_functions:
            raise ValueError("touch controls are not supported by this device profile")
        frame = self._transport.request(QUERY_TOUCH, b"", RESPONSE_TOUCH)
        try:
            return parse_touch_bindings(frame)
        except ValueError as error:
            raise RuntimeError(str(error)) from error

    def set_touch_binding(self, binding: TouchBinding) -> tuple[int | None, tuple[TouchBinding, ...]]:
        self._require_connected()
        if not self._authenticated:
            raise RuntimeError("session authentication has not completed")
        if (not self.profile.verified or binding.device_type not in (1, 2)
                or binding.button != 1
                or binding.function not in self.profile.touch_functions.get(binding.action, ())):
            raise ValueError("touch assignment is not allowed for this device profile")
        if not any(item.key == binding.key for item in self.touch_bindings()):
            raise ValueError("touch gesture was not reported by this device")
        try:
            ack = self._transport.request(SET_TOUCH, binding.write_payload(), RESPONSE_SET_TOUCH)
            if len(ack.payload) != 1:
                raise RuntimeError("device returned malformed touch acknowledgement")
            status = ack.payload[0]
        except TimeoutError:
            status = None
        return status, self.touch_bindings()

    def feature_switches(self, feature_ids: tuple[int, ...]) -> dict[int, bool]:
        """Read the device's feature switches.

        The request carries a count byte followed by the wanted feature ids,
        which is the shape the phone app uses. Unsupported ids come back as
        zero bytes.
        """
        self._require_connected()
        payload = bytes((len(feature_ids),)) + bytes(feature_ids)
        frame = self._transport.request(
            QUERY_STATUS, payload, RESPONSE_STATUS,
        )
        switches = parse_feature_switches(frame)
        if switches is None:
            raise RuntimeError("device returned malformed feature switch state")
        return switches

    def set_feature_switch(self, feature_id: int, enabled: bool) -> tuple[int | None, bool]:
        """Set one feature switch and verify it with a fresh read."""
        self._require_connected()
        if not 0 <= feature_id <= 0xFF:
            raise ValueError("feature id must fit in one byte")
        payload = bytes((feature_id, 1 if enabled else 0))
        try:
            acknowledgement = self._transport.request(
                SET_FEATURE_SWITCH, payload, RESPONSE_SET_FEATURE_SWITCH,
            )
            status = (acknowledgement.payload[0]
                      if acknowledgement.command == RESPONSE_SET_FEATURE_SWITCH
                      and acknowledgement.payload else None)
        except TimeoutError:
            status = None
        verified = self.feature_switches((feature_id,)).get(feature_id)
        return status, status == 0 and verified is enabled

    def find_earbuds(self, ringing: bool = True) -> tuple[int | None, bool]:
        """Start or stop the find-my-earbuds tone."""
        self._require_connected()
        if not self._authenticated:
            raise RuntimeError("session authentication has not completed")
        if not self.profile.verified or "find_earbuds" not in self.profile.capabilities:
            raise ValueError("earbud search is not supported by a verified profile")
        payload = bytes((1 if ringing else 0,))
        try:
            acknowledgement = self._transport.request(
                SET_FIND_MODE, payload, RESPONSE_SET_FIND_MODE,
            )
            status = (acknowledgement.payload[0]
                      if acknowledgement.command == RESPONSE_SET_FIND_MODE
                      and acknowledgement.payload else None)
        except TimeoutError:
            status = None
        return status, True

    def bass_engine_status(self) -> tuple[int, int, int]:
        """Read the bass engine range and current level.

        The answer is [status, min, max, current]; the level is signed, so
        the device reports -10..+10 on the Nord Buds 3 Pro.
        """
        self._require_connected()
        frame = self._transport.request(
            QUERY_BASS_ENGINE, b"", RESPONSE_BASS_ENGINE,
        )
        if len(frame.payload) < 4 or frame.payload[0] != 0:
            raise RuntimeError("device returned malformed bass engine state")
        minimum = frame.payload[1] - 256 if frame.payload[1] > 127 else frame.payload[1]
        maximum = frame.payload[2] - 256 if frame.payload[2] > 127 else frame.payload[2]
        current = frame.payload[3] - 256 if frame.payload[3] > 127 else frame.payload[3]
        return minimum, maximum, current

    def set_bass_level(self, level: int) -> tuple[int | None, bool]:
        """Set the bass engine level ("BassWave"), -10 to +10.

        The phone app sends the allowed range together with the wanted value
        and the device echoes the same three bytes back, which is the only
        proof that the level was accepted.
        """
        self._require_connected()
        if not BASS_LEVEL_MIN <= level <= BASS_LEVEL_MAX:
            raise ValueError(
                f"bass level must be between {BASS_LEVEL_MIN} and {BASS_LEVEL_MAX}"
            )
        payload = BASS_LEVEL_RANGE + bytes((level & 0xFF,))
        try:
            acknowledgement = self._transport.request(
                SET_BASS_ENGINE, payload, RESPONSE_SET_BASS_ENGINE,
            )
            status = parse_set_anc_status(acknowledgement)
        except TimeoutError:
            status = None
        return status, True

    def diagnostic_query(self, command: int, payload: bytes = b"",
                        wait: float = 0.5) -> tuple[dict[str, object], ...]:
        """Local fork: read-only raw query used to discover device capabilities.

        Only query command classes are allowed. Write commands are refused so
        the probe can never change the earbuds' state by accident.
        """
        self._require_connected()
        if not 0x0100 <= command <= 0x02FF:
            raise ValueError(
                "diagnostic queries are limited to the 0x0100-0x02ff command range"
            )
        frames = self._transport.query(command, payload, wait=wait)
        return tuple(
            {
                "command": frame.command,
                "command_hex": f"0x{frame.command:04x}",
                "sequence": frame.sequence,
                "payload": frame.payload.hex(" "),
            }
            for frame in frames
        )

    def _redact(self, frames: list[Frame]) -> EventBatch:
        events: list[SafeEvent] = []
        ignored = 0
        for frame in frames:
            event = self._safe_event(frame)
            if event is None:
                ignored += 1
            else:
                events.append(event)
        return EventBatch(tuple(events), ignored)

    def _safe_event(self, frame: Frame) -> SafeEvent | None:
        if (frame.command == RESPONSE_REMOTE_VERSION
                and self._version_sequence is not None
                and frame.sequence == self._version_sequence):
            records = parse_remote_version(frame)
            if records is not None:
                self._version_sequence = None
                mark("optional_firmware_received")
                return SafeEvent("firmware", {"records": [asdict(record) for record in records],
                    "version": format_firmware_version(records)})
            return None
        if frame.command == RESPONSE_BATTERY:
            battery = parse_battery(frame)
            return SafeEvent("battery", battery) if battery is not None else None
        if frame.command == RESPONSE_ANC:
            state = parse_anc_state(frame, self.profile.anc)
            if state is not None:
                return SafeEvent("anc", {"mode": state.mode, "level": state.level})
            return None
        if (eq_id := parse_eq_id(frame)) is not None:
            return SafeEvent("eq_changed", {"id": eq_id})
        if frame.command == RESPONSE_STATUS:
            switches = parse_feature_switches(frame)
            if switches is None:
                return None
            named = {
                name: switches[feature]
                for feature, name in FEATURE_SWITCH_NAMES.items()
                if feature in switches
            }
            return SafeEvent("feature_switches", named)
        if frame.command == NOTIFY_FEATURE_SWITCHES:
            # The device pushes changed feature switches as
            # [count][feature id, value...]. This is how a change made in the
            # phone app reaches the panel.
            if len(frame.payload) < 2:
                return None
            count = frame.payload[0]
            if len(frame.payload) < 2 + count * 2:
                return None
            named = {}
            for offset in range(count):
                feature = frame.payload[2 + offset * 2]
                value = frame.payload[3 + offset * 2]
                if value not in (0, 1):
                    return None
                name = FEATURE_SWITCH_NAMES.get(feature)
                if name is not None:
                    named[name] = bool(value)
            return SafeEvent("feature_switches", named)
        if frame.command == NOTIFY_STATE and frame.payload:
            # The device pushes the noise mode as [event, type, type, bitmap].
            # Reading it lets the panel follow changes made in the phone app
            # and proves a write that the device answers with a level instead
            # of the requested mode.
            if len(frame.payload) >= 4 and frame.payload[0] == 0x03 \
                    and frame.payload[1] == 0x01 and frame.payload[2] == 0x01:
                state = parse_anc_state(frame, self.profile.anc)
                if state is not None:
                    return SafeEvent("anc", {"mode": state.mode, "level": state.level})
            return SafeEvent("notification", {"event_code": frame.payload[0]})
        if frame.payload[:2] == BASS_LEVEL_NOTICE and len(frame.payload) >= 3:
            # The device echoes the bass engine range and the accepted value.
            value = frame.payload[2]
            level = value - 256 if value > 127 else value
            return SafeEvent("bass_level", {"level": level})
        return None

    def _require_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("session is not connected")

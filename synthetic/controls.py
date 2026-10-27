"""Artificial, host-side control model for the locked manual candidate.

No socket, network client, production identity, real key, or private input.
Logical-clock conditions are not wall-clock, kernel, or independent supervision
proof. This module must not be used as an authorization service.
"""
from __future__ import annotations

import copy
import dataclasses
import hashlib
import hmac
import json
import os
import pathlib
import re
import sys
import signal
import time
from dataclasses import dataclass, field
from typing import Callable


class Denied(Exception):
    """Same outward refusal for missing, foreign, and unauthorized objects."""


def deny() -> None:
    raise Denied("denied")


def require(condition: bool) -> None:
    if not condition:
        deny()


def encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@dataclass
class Clock:
    """Monotonic logical stimulus only; never evidence of elapsed real time."""
    now: float = 0.0

    def advance(self, seconds: float) -> None:
        require(seconds >= 0)
        self.now += seconds


@dataclass(frozen=True)
class Limits:
    artifact: int = 1048576
    case: int = 10485760
    cycle: int = 41943040
    receiver_bytes: int = 1048576
    rate: int = 131072
    connections: int = 8
    grant: float = 30.0
    recheck: float = 1.0
    stop: float = 5.0
    link: float = 30.0
    block: int = 65536

    @classmethod
    def configured(cls) -> Limits:
        mapping = {"artifact": "MAX_FIXTURE_BYTES", "case": "MAX_CASE_BYTES", "cycle": "MAX_CYCLE_BYTES",
                   "receiver_bytes": "MAX_RECEIVER_BYTES", "rate": "MAX_RECEIVER_RATE_BPS",
                   "connections": "MAX_CONNECTIONS", "grant": "MAX_GRANT_SECONDS",
                   "recheck": "MAX_RECHECK_MS", "stop": "MAX_STOP_MS", "link": "MAX_LINK_SECONDS",
                   "block": "MAX_BLOCK_BYTES"}
        expected = cls()
        values = {}
        for name, variable in mapping.items():
            raw = os.environ[variable]
            require(re.fullmatch(r"[0-9]+", raw) is not None)
            value = int(raw) / 1000 if name in ("recheck", "stop") else int(raw)
            # This candidate does not permit silent relaxation of its numerical contract.
            require(value == getattr(expected, name))
            values[name] = value
        return cls(**values)


class Budget:
    """One ledger of retained artificial payloads and their file projections.

    A projection is the same owned artifact, not a second charge. Distinct
    copies/derivatives have distinct IDs. Host logs and kernel memory are outside
    this logical domain; the workflow checks its own total filesystem separately.
    """
    def __init__(self, limits: Limits):
        self.limits = limits
        self._artifacts: dict[str, tuple[str, bytes]] = {}
        self.allowed = {"red-a", "red-b", "blue-a", "blue-b", "cycle-evidence"}

    @property
    def cases(self) -> dict[str, int]:
        totals: dict[str, int] = {}
        for case, data in self._artifacts.values():
            totals[case] = totals.get(case, 0) + len(data)
        return totals

    @property
    def total(self) -> int:
        return sum(len(data) for _, data in self._artifacts.values())

    def read(self, key: str) -> bytes:
        require(key in self._artifacts)
        return self._artifacts[key][1]

    def put_many(self, changes: dict[str, tuple[str, bytes] | None]) -> None:
        proposed = dict(self._artifacts)
        for key, value in changes.items():
            require(isinstance(key, str) and re.fullmatch(r"[A-Za-z0-9_./-]+", key) is not None)
            if value is None:
                require(key in proposed)
                del proposed[key]
                continue
            case, data = value
            require(case in self.allowed and isinstance(data, bytes))
            require(len(data) <= self.limits.artifact)
            require(key not in proposed or proposed[key][0] == case)
            proposed[key] = (case, data)
        totals: dict[str, int] = {}
        for case, data in proposed.values():
            totals[case] = totals.get(case, 0) + len(data)
        require(all(size <= self.limits.case for size in totals.values()))
        require(sum(totals.values()) <= self.limits.cycle)
        # A single replacement follows all validation: denial mutates no balance.
        self._artifacts = proposed

    def preview(self, case: str, size: int, artifact: bool = True) -> None:
        """Capacity question only; no allocation or pretend reservation."""
        require(case in self.allowed and type(size) is int and size >= 0)
        require(not artifact or size <= self.limits.artifact)
        require(self.cases.get(case, 0) + size <= self.limits.case)
        require(self.total + size <= self.limits.cycle)

    def preview_cycle(self, size: int) -> None:
        require(type(size) is int and size >= 0 and self.total + size <= self.limits.cycle)

    def write_owned(self, key: str, case: str, data: bytes, target: pathlib.Path) -> None:
        require(not target.exists() and not target.is_symlink())
        self.put_many({key: (case, data)})
        # Reservation remains conservatively charged on I/O failure; stop rather
        # than pretending a rollback erased partially written evidence.
        with target.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())

    def inventory(self) -> list[dict[str, object]]:
        return [{"artifact": key, "case": case, "bytes": len(data), "sha256": digest(data)}
                for key, (case, data) in sorted(self._artifacts.items())]


class ModelInterrupted(Exception):
    def __init__(self, signum: int):
        self.signum = signum
        super().__init__("interrupted")


class Journal:
    """Immutable bounded attempt/result receipts, including partial failure."""
    def __init__(self, budget: Budget, root: pathlib.Path, candidate: str, fixture: str):
        self.budget, self.root = budget, root
        self.candidate, self.fixture = candidate, fixture
        self.planned, self.attempted, self.matched, self.failed = 674, 0, 0, 0
        self.current: dict[str, object] | None = None
        self.receipt_serial = 0
        self.emit({"kind": "header", "observed": "PREPARING"})

    def counts(self) -> dict[str, int]:
        return {"planned": self.planned, "attempted": self.attempted,
                "pass": self.matched, "fail": self.failed,
                "not_executed": self.planned - self.attempted,
                "incomplete": self.attempted - self.matched - self.failed}

    def emit(self, event: dict[str, object]) -> None:
        self.receipt_serial += 1
        record = {"schema": "artificial-receipt-v2", "candidate": self.candidate,
                  "fixture_sha256": self.fixture, "count_scope": "logical-model-only-not-native-acceptance",
                  "counts": self.counts(), **event}
        name = "condition-" + str(self.receipt_serial).zfill(5) + ".json"
        self.budget.write_owned("evidence/" + name, "cycle-evidence", encoded(record),
                                self.root / "evidence" / name)

    def begin(self, group: str, identifier: str, refused: bool) -> None:
        require(self.current is None and self.attempted < self.planned)
        self.attempted += 1
        self.current = {"group": group, "condition": identifier,
                        "expected": "deny" if refused else "allow"}
        self.emit({"kind": "attempt", "observed": "STARTED", **self.current})

    def finish(self, matched: bool, error: BaseException | None = None) -> None:
        require(self.current is not None)
        event = dict(self.current)
        if matched:
            self.matched += 1
        else:
            self.failed += 1
        self.current = None
        self.emit({"kind": "result", "observed": "MATCHED_MODEL" if matched else "FAILED_MODEL",
                   "error_type": type(error).__name__ if error else None, **event})

    def failure(self, error: BaseException) -> None:
        if self.current is not None:
            self.finish(False, error)
        self.emit({"kind": "termination", "observed": "ERROR_OR_INTERRUPT",
                   "error_type": type(error).__name__, "evidence_after_host_loss": "NOT_PROVEN"})


@dataclass(frozen=True)
class Grant:
    token: str
    case: str
    version: int
    purpose: str
    subject: str
    approver: str
    custodian: str
    operations: tuple[str, ...]
    surfaces: tuple[str, ...]
    expires: float
    seal: str = ""


class Policy:
    # Public artificial seal for tampering stimuli; not a real cryptographic key.
    _artificial_seal = b"public-artificial-fixture-seal-not-a-secret"

    def __init__(self, clock: Clock, limits: Limits):
        self.clock, self.limits = clock, limits
        self.versions = {case: 1 for case in ("red-a", "red-b", "blue-a", "blue-b")}
        self.revoked: dict[str, float] = {}
        self.serial = 0

    def seal(self, grant: Grant) -> str:
        fields = dataclasses.asdict(grant)
        fields.pop("seal")
        return hmac.new(self._artificial_seal, encoded(fields), hashlib.sha256).hexdigest()

    def issue(self, case: str, subject: str = "actor-exec", approver: str = "actor-approve",
              custodian: str = "actor-store", purpose: str = "artificial-review",
              operations: tuple[str, ...] = ("read", "list", "search", "count", "edit", "export"),
              surfaces: tuple[str, ...] = ("objects", "metadata", "logs", "indexes", "keys", "backups"),
              lifetime: float = 30.0) -> Grant:
        require(case in self.versions and purpose == "artificial-review")
        require(len({subject, approver, custodian}) == 3)
        require(approver == "actor-approve" and custodian == "actor-store")
        require(0 < lifetime <= self.limits.grant)
        self.serial += 1
        grant = Grant("fixture-token-" + str(self.serial), case, self.versions[case], purpose,
                      subject, approver, custodian, operations, surfaces, self.clock.now + lifetime)
        return dataclasses.replace(grant, seal=self.seal(grant))

    def check(self, grant: Grant | None, subject: str, case: str, operation: str,
              surface: str, purpose: str = "artificial-review") -> None:
        require(isinstance(grant, Grant))
        require(hmac.compare_digest(self.seal(grant), grant.seal))
        require(grant.token not in self.revoked and self.clock.now < grant.expires)
        require(case in self.versions and grant.case == case)
        require(grant.version == self.versions[case] and grant.purpose == purpose)
        require(subject == grant.subject and operation in grant.operations and surface in grant.surfaces)
        require(len({grant.subject, grant.approver, grant.custodian}) == 3)

    def revoke(self, grant: Grant) -> None:
        self.revoked[grant.token] = self.clock.now


class Store:
    """Policy and one shared artifact ledger precede every content mutation."""
    def __init__(self, policy: Policy, budget: Budget, fixture: dict[str, str]):
        self.policy, self.budget = policy, budget
        require(set(fixture) == set(policy.versions))
        self.records = {(case, surface): "store/" + case + "/" + surface
                        for case in policy.versions
                        for surface in ("objects", "metadata", "logs", "indexes", "keys", "backups")}
        budget.put_many({key: (case, fixture[case].encode())
                         for (case, _), key in self.records.items()})

    def request(self, grant: Grant | None, subject: str, case: str, operation: str,
                surface: str) -> object:
        self.policy.check(grant, subject, case, operation, surface)
        require((case, surface) in self.records)
        key = self.records[case, surface]
        value = self.budget.read(key)
        if operation == "count":
            return 1
        if operation in ("list", "search"):
            return (case,)
        if operation == "edit":
            self.budget.put_many({key: (case, value + b"-EDITED")})
            return "edited"
        return value


class Receiver:
    """Logical rolling-one-second limit; no socket or wall-time guarantee."""
    def __init__(self, clock: Clock, limits: Limits, budget: Budget, namespace: str):
        self.clock, self.limits, self.budget, self.namespace = clock, limits, budget, namespace
        self.active: set[str] = set()
        self.bindings: dict[str, str] = {}
        self.job_keys: dict[str, str] = {}
        self.recent: list[tuple[float, int]] = []
        self.last_accept = clock.now
        self.receipt_key = namespace + "/receipts"

    @property
    def receipts(self) -> list[dict[str, object]]:
        if self.receipt_key not in self.budget._artifacts:
            return []
        return json.loads(self.budget.read(self.receipt_key))

    def connect(self, identifier: str, destination: str = "local-artificial", case: str = "red-a") -> None:
        require(destination == "local-artificial" and case in self.budget.allowed and case != "cycle-evidence")
        require(identifier not in self.active and len(self.active) < self.limits.connections)
        self.active.add(identifier)
        self.bindings[identifier] = case

    def disconnect(self, identifier: str) -> None:
        self.active.discard(identifier)
        self.bindings.pop(identifier, None)

    def accept(self, identifier: str, job: str, block: bytes) -> None:
        require(identifier in self.active and isinstance(block, bytes))
        require(len(block) <= self.limits.block and self.clock.now >= self.last_accept)
        case = self.bindings[identifier]
        key = self.job_keys.get(job, self.namespace + "/job/" + job)
        previous = self.budget.read(key) if key in self.budget._artifacts else b""
        require(len(previous) + len(block) <= self.limits.receiver_bytes)
        recent = [(stamp, size) for stamp, size in self.recent if self.clock.now - stamp < 1.0]
        require(sum(size for _, size in recent) + len(block) <= self.limits.rate)
        receipts = self.receipts + [{"job": job, "case": case, "bytes": len(block),
                                     "sha256": digest(block), "logical_time": self.clock.now}]
        self.budget.put_many({key: (case, previous + block),
                              self.receipt_key: ("cycle-evidence", encoded(receipts))})
        self.job_keys[job] = key
        self.recent = recent + [(self.clock.now, len(block))]
        self.last_accept = self.clock.now


@dataclass(frozen=True)
class Link:
    recipient: str
    category: str
    expires: float
    grant: Grant


class Delivery:
    def __init__(self, policy: Policy, receiver: Receiver):
        self.policy, self.receiver = policy, receiver

    def issue(self, grant: Grant, lifetime: float = 30.0) -> Link:
        require(0 < lifetime <= self.policy.limits.link)
        self.policy.check(grant, grant.subject, grant.case, "export", "objects")
        return Link("receiver-artificial", "approved-derived", self.policy.clock.now + lifetime, grant)

    def send(self, link: Link, recipient: str, category: str, block: bytes) -> None:
        require(recipient == link.recipient and category == link.category)
        require(self.policy.clock.now < link.expires)
        self.policy.check(link.grant, link.grant.subject, link.grant.case, "export", "objects")
        self.receiver.accept("export-connection", link.grant.token, block)


class Activity:
    """Logical queue/start/block model; real propagation/stop remains unproven."""
    def __init__(self, policy: Policy, grant: Grant, receiver: Receiver):
        self.policy, self.grant, self.receiver = policy, grant, receiver
        self.state = "new"
        self.last_check = policy.clock.now

    def move(self, phase: str) -> None:
        require(phase in ("before-queue", "queue", "start", "active", "read-block", "prepared-export", "active-export"))
        try:
            require(self.policy.clock.now - self.last_check <= self.policy.limits.recheck)
            self.policy.check(self.grant, self.grant.subject, self.grant.case, "read", "objects")
        except Denied:
            self.state = "stopped"
            self.receiver.disconnect("activity")
            revoked_at = self.policy.revoked.get(self.grant.token)
            if revoked_at is not None and self.policy.clock.now - revoked_at > self.policy.limits.stop:
                raise RuntimeError("logical stop criterion exceeded")
            raise
        self.last_check = self.policy.clock.now
        self.state = phase


class Quarantine:
    def __init__(self, budget: Budget):
        self.budget = budget
        original = encoded({"classification": "ARTIFICIAL", "items": [
            {"id": "item-a", "category": "approved", "text": "artificial-alpha"},
            {"id": "item-b", "category": "third-party", "text": "artificial-beta"},
            {"id": "item-c", "category": "attachment", "text": "artificial-gamma"},
            {"id": "item-d", "category": "out-of-scope", "text": "artificial-delta"},
            {"id": "item-e", "category": "deleted-marker", "text": "artificial-epsilon"}]})
        budget.put_many({"incidental/source": ("red-a", original), "incidental/copy": ("red-a", bytes(bytearray(original)))})
        self.original_hash, self.version, self.allowed = digest(original), 1, {"approved"}

    @property
    def original(self) -> bytes:
        return self.budget.read("incidental/source")

    @property
    def working_copy(self) -> bytes:
        return self.budget.read("incidental/copy")

    def triage(self, actor: str) -> tuple[str, ...]:
        require(actor == "actor-triage")
        return tuple(item["category"] for item in json.loads(self.original)["items"])

    def derive(self, actor: str) -> bytes:
        require(actor == "actor-triage")
        data = encoded([item for item in json.loads(self.working_copy)["items"] if item["category"] in self.allowed])
        self.budget.put_many({"incidental/derived": ("red-a", data)})
        return self.budget.read("incidental/derived")

    def expand(self, category: str, approver: str, version: int) -> None:
        require(approver == "actor-approve" and version == self.version + 1)
        self.version, self.allowed = version, self.allowed | {category}


class Lifecycle:
    def __init__(self, clock: Clock, budget: Budget):
        self.clock, self.budget = clock, budget
        self.live_ids = {case: "lifecycle/live/" + case for case in ("red-a", "blue-a")}
        self.backup_ids = {case: "lifecycle/backup/" + case for case in self.live_ids}
        changes = {key: (case, b"artificial-" + case.encode()) for case, key in self.live_ids.items()}
        changes.update({key: (case, bytes(bytearray(changes[self.live_ids[case]][1]))) for case, key in self.backup_ids.items()})
        budget.put_many(changes)
        self.holds, self.tombstones, self.revoked = {"red-a"}, set(), set()
        self.staging_ids: set[str] = set()

    @property
    def live(self) -> dict[str, bytes]:
        return {case: self.budget.read(key) for case, key in self.live_ids.items()}

    def discard(self, case: str) -> None:
        require(self.clock.now >= 60 and case not in self.holds and case in self.live_ids)
        self.budget.put_many({self.live_ids[case]: None})
        self.tombstones.add(case)
        del self.live_ids[case]

    def release(self, case: str, actor: str) -> None:
        require(actor == "actor-approve" and self.clock.now >= 90)
        self.holds.discard(case)

    def restore(self) -> dict[str, bytes]:
        staging = {case: self.budget.read(key) for case, key in self.backup_ids.items()
                   if case not in self.tombstones and case not in self.revoked}
        changes = {key: None for key in self.staging_ids}
        changes.update({"lifecycle/staging/" + case: (case, data) for case, data in staging.items()})
        self.budget.put_many(changes)
        self.staging_ids = {"lifecycle/staging/" + case for case in staging}
        return staging


class ArtificialKeys:
    def __init__(self, budget: Budget):
        self.budget = budget
        self.generations = {"red-a": 1, "blue-a": 1}

    @staticmethod
    def authorize(requester: str, approvals: tuple[str, ...]) -> None:
        require(len(approvals) == 2 and len(set(approvals)) == 2)
        require(set(approvals) == {"actor-approve", "actor-store"} and requester not in approvals)

    def rotate(self, case: str, requester: str, approvals: tuple[str, ...]) -> str:
        self.authorize(requester, approvals)
        require(case in self.generations)
        generation = self.generations[case] + 1
        fingerprint = digest(encoded(["ARTIFICIAL", case, generation]))
        self.budget.put_many({"keys/" + case: (case, fingerprint.encode())})
        self.generations[case] = generation
        return fingerprint

    def recover(self, case: str, requester: str, approvals: tuple[str, ...]) -> str:
        self.authorize(requester, approvals)
        require(case in self.generations)
        fingerprint = digest(encoded(["ARTIFICIAL", case, self.generations[case]]))
        self.budget.put_many({"key-recovery/" + case: (case, fingerprint.encode())})
        return fingerprint

    def emergency(self, requester: str, approvals: tuple[str, ...]) -> str:
        self.authorize(requester, approvals)
        return "artificial-scoped-decision-only"


class Suite:
    def __init__(self, limits: Limits, budget: Budget, journal: Journal, fixture: dict[str, str]):
        self.limits, self.budget, self.journal, self.fixture = limits, budget, journal, fixture
        self.receiver_serial = 0
        self.events: list[dict[str, object]] = []
        self.identifiers: set[str] = set()
        self.chains: list[dict[str, object]] = []

    def new_receiver(self, clock: Clock) -> Receiver:
        self.receiver_serial += 1
        return Receiver(clock, self.limits, self.budget, "receiver-" + str(self.receiver_serial))

    def observe(self, group: str, identifier: str, operation: Callable[[], object],
                refused: bool = False, predicate: Callable[[object], bool] | None = None) -> None:
        require(identifier not in self.identifiers)
        self.identifiers.add(identifier)
        self.journal.begin(group, identifier, refused)
        try:
            try:
                result = operation()
            except Denied as error:
                if not refused or str(error) != "denied":
                    raise RuntimeError("unexpected artificial refusal") from error
            else:
                if refused or (predicate is not None and not predicate(result)):
                    raise RuntimeError("artificial expectation contradicted")
        except BaseException as original:
            try:
                self.journal.finish(False, original)
            except BaseException as evidence_error:
                print("evidence_error=" + type(evidence_error).__name__, file=sys.stderr)
            raise
        self.events.append({"group": group, "id": identifier,
                            "expectation": "deny" if refused else "allow", "outcome": "MODEL_CONDITION_MATCHED"})
        self.journal.finish(True)

    def isolation(self) -> None:
        policy = Policy(Clock(), self.limits)
        store = Store(policy, self.budget, self.fixture)
        for origin in policy.versions:
            grant = policy.issue(origin)
            for target in policy.versions:
                for surface in ("objects", "metadata", "logs", "indexes", "keys", "backups"):
                    for operation in ("read", "list", "search", "count", "edit", "export"):
                        key = "/".join(("isolation", origin, target, surface, operation))
                        self.observe("isolation", key,
                                     lambda g=grant, t=target, o=operation, s=surface:
                                     store.request(g, "actor-exec", t, o, s), refused=origin != target,
                                     predicate=lambda value, o=operation, t=target:
                                     value == 1 if o == "count" else value == (t,) if o in ("list", "search")
                                     else value == "edited" if o == "edit"
                                     else isinstance(value, bytes) and value.startswith(b"ARTIFICIAL-" + t.encode()))
            self.observe("isolation", "missing/" + origin,
                         lambda g=grant: store.request(g, "actor-exec", "absent-case", "read", "objects"), True)

    def authority(self) -> None:
        clock, limits = Clock(), self.limits
        policy = Policy(clock, limits)
        grant = policy.issue("red-a")
        check = lambda g, actor="actor-exec", purpose="artificial-review": policy.check(
            g, actor, "red-a", "read", "objects", purpose)
        self.observe("authority", "grant-valid", lambda: check(grant))
        self.observe("authority", "login-only", lambda: check(None), True)
        self.observe("authority", "admin-no-grant", lambda: check(grant, "actor-admin"), True)
        self.observe("authority", "custodian-no-content", lambda: check(grant, "actor-store"), True)
        self.observe("authority", "wrong-purpose", lambda: check(grant, purpose="other-purpose"), True)
        self.observe("authority", "self-approval", lambda: policy.issue("red-a", subject="actor-approve"), True)
        self.observe("authority", "tampered-grant", lambda: check(dataclasses.replace(grant, case="blue-a")), True)
        policy.versions["red-a"] += 1
        self.observe("authority", "old-version", lambda: check(grant), True)
        valid = policy.issue("red-a")
        clock.advance(30)
        self.observe("authority", "expired-grant", lambda: check(valid), True)
        self.observe("authority", "overlong-grant", lambda: policy.issue("red-a", lifetime=31), True)

    def revocation(self) -> None:
        phases = ("before-queue", "queue", "start", "active", "read-block", "prepared-export", "active-export")
        for phase in phases:
            clock, limits = Clock(), self.limits
            policy, receiver = Policy(clock, limits), self.new_receiver(clock)
            grant = policy.issue("red-a")
            activity = Activity(policy, grant, receiver)
            receiver.connect("activity")
            self.observe("revocation", phase + "/positive", lambda: activity.move(phase))
            policy.revoke(grant)
            clock.advance(0.5)
            self.observe("revocation", phase + "/revoked", lambda: activity.move(phase), True)
            self.observe("revocation", phase + "/closed", lambda: (activity.state, receiver.active),
                         predicate=lambda x: x == ("stopped", set()))
        clock, limits = Clock(), self.limits
        policy = Policy(clock, limits)
        receiver = self.new_receiver(clock)
        activity = Activity(policy, policy.issue("red-a"), receiver)
        clock.advance(1.01)
        self.observe("revocation", "stale-recheck", lambda: activity.move("start"), True)

    def incidental(self) -> None:
        quarantine = Quarantine(self.budget)
        original = quarantine.original
        self.observe("incidental", "unauthorized-triage", lambda: quarantine.triage("actor-admin"), True)
        self.observe("incidental", "minimal-triage", lambda: quarantine.triage("actor-triage"),
                     predicate=lambda x: "third-party" in x)
        derived = quarantine.derive("actor-triage")
        self.chains.append({"kind": "artificial-minimization", "source": digest(original),
                            "copy": digest(quarantine.working_copy), "derived": digest(derived),
                            "policy_version": quarantine.version, "method": "category-filter-v1"})
        self.observe("incidental", "minimized-report", lambda: json.loads(derived),
                     predicate=lambda x: len(x) == 1 and x[0]["category"] == "approved")
        self.observe("incidental", "no-broad-export", lambda: quarantine.derive("actor-exec"), True)
        self.observe("incidental", "unapproved-expansion",
                     lambda: quarantine.expand("attachment", "actor-exec", 2), True)
        self.observe("incidental", "stale-expansion",
                     lambda: quarantine.expand("attachment", "actor-approve", 1), True)
        self.observe("incidental", "approved-new-version",
                     lambda: quarantine.expand("attachment", "actor-approve", 2))
        self.observe("incidental", "expanded-minimum", lambda: json.loads(quarantine.derive("actor-triage")),
                     predicate=lambda x: {item["category"] for item in x} == {"approved", "attachment"})
        self.observe("incidental", "original-preserved", lambda: quarantine.original,
                     predicate=lambda x: x == original and digest(x) == quarantine.original_hash)

    def lifecycle(self) -> None:
        clock = Clock()
        lifecycle = Lifecycle(clock, self.budget)
        other = lifecycle.live["blue-a"]
        clock.advance(60)
        self.observe("lifecycle", "hold-denies-discard", lambda: lifecycle.discard("red-a"), True)
        self.observe("lifecycle", "early-release", lambda: lifecycle.release("red-a", "actor-approve"), True)
        clock.advance(30)
        self.observe("lifecycle", "unauthorized-release", lambda: lifecycle.release("red-a", "actor-exec"), True)
        self.observe("lifecycle", "release", lambda: lifecycle.release("red-a", "actor-approve"))
        self.observe("lifecycle", "discard", lambda: lifecycle.discard("red-a"))
        self.observe("lifecycle", "restore-tombstone", lifecycle.restore,
                     predicate=lambda x: "red-a" not in x and x["blue-a"] == other)
        lifecycle.revoked.add("blue-a")
        self.observe("lifecycle", "restore-revocation", lifecycle.restore, predicate=lambda x: not x)
        self.observe("lifecycle", "live-other-intact", lambda: lifecycle.live["blue-a"],
                     predicate=lambda x: x == other)

    def destinations_and_quotas(self) -> None:
        limits, clock = self.limits, Clock()
        receiver = self.new_receiver(clock)
        for destination in ("ipv4-simulated", "ipv6-simulated", "dns-simulated", "proxy-simulated",
                            "redirect-simulated", "metadata-simulated"):
            self.observe("destinations", destination,
                         lambda d=destination: receiver.connect("rejected", d), True)
        for index in range(8):
            self.observe("quotas", "connection-" + str(index), lambda i=index: receiver.connect("c" + str(i)))
        self.observe("quotas", "ninth-connection", lambda: receiver.connect("ninth"), True)
        block = b"a" * limits.block
        self.observe("quotas", "block-positive", lambda: receiver.accept("c0", "job-a", block))
        self.observe("quotas", "block-too-large", lambda: receiver.accept("c0", "job-a", block + b"a"), True)
        receiver.accept("c0", "job-a", block)
        self.observe("quotas", "rate-exceeded", lambda: receiver.accept("c0", "job-a", b"a"), True)
        for index in range(7):
            clock.advance(1)
            receiver.accept("c0", "job-a", block)
            receiver.accept("c0", "job-a", block)
        clock.advance(1)
        self.observe("quotas", "job-byte-exceeded", lambda: receiver.accept("c0", "job-a", b"a"), True)
        budget = self.budget
        self.observe("quotas", "artifact-positive", lambda: budget.preview("red-a", limits.artifact))
        self.observe("quotas", "artifact-exceeded", lambda: budget.preview("red-a", limits.artifact + 1), True)
        self.observe("quotas", "case-exceeded", lambda: budget.preview("red-a", limits.case + 1, False), True)
        self.observe("quotas", "cycle-exceeded", lambda: budget.preview_cycle(limits.cycle + 1), True)

    def export_and_keys(self) -> None:
        clock, limits = Clock(), self.limits
        policy, receiver = Policy(clock, limits), self.new_receiver(clock)
        grant = policy.issue("red-a")
        receiver.connect("export-connection")
        delivery = Delivery(policy, receiver)
        link = delivery.issue(grant)
        self.observe("export", "recipient-denied",
                     lambda: delivery.send(link, "wrong", "approved-derived", b"a"), True)
        self.observe("export", "category-denied",
                     lambda: delivery.send(link, "receiver-artificial", "raw-original", b"a"), True)
        self.observe("export", "allowed-block",
                     lambda: delivery.send(link, "receiver-artificial", "approved-derived", b"ARTIFICIAL"))
        self.observe("export", "overlong-link", lambda: delivery.issue(grant, 31), True)
        policy.revoke(grant)
        self.observe("export", "revoked-before-block",
                     lambda: delivery.send(link, "receiver-artificial", "approved-derived", b"a"), True)
        renewed = delivery.issue(policy.issue("red-a"), lifetime=1)
        clock.advance(1)
        self.observe("export", "expired-link",
                     lambda: delivery.send(renewed, "receiver-artificial", "approved-derived", b"a"), True)
        self.observe("export", "receipt", lambda: receiver.receipts,
                     predicate=lambda x: len(x) == 1 and x[0]["bytes"] == len(b"ARTIFICIAL"))
        keys = ArtificialKeys(self.budget)
        for operation in ("rotate", "recover"):
            method = getattr(keys, operation)
            self.observe("keys", operation + "/single",
                         lambda m=method: m("red-a", "actor-exec", ("actor-approve",)), True)
            self.observe("keys", operation + "/duplicate",
                         lambda m=method: m("red-a", "actor-exec", ("actor-store", "actor-store")), True)
            self.observe("keys", operation + "/beneficiary",
                         lambda m=method: m("red-a", "actor-store", ("actor-approve", "actor-store")), True)
            self.observe("keys", operation + "/dual",
                         lambda m=method: m("red-a", "actor-exec", ("actor-approve", "actor-store")))
        self.observe("keys", "other-key-unchanged", lambda: keys.generations["blue-a"], predicate=lambda x: x == 1)
        self.observe("keys", "unilateral-emergency",
                     lambda: keys.emergency("actor-exec", ("actor-store",)), True)
        self.observe("keys", "dual-emergency",
                     lambda: keys.emergency("actor-exec", ("actor-approve", "actor-store")))
        self.chains.append({"kind": "artificial-delivery", "receipts": receiver.receipts})

    def provenance(self) -> None:
        original = b"ARTIFICIAL ORIGINAL: selected=alpha; excluded=beta"
        working = bytes(bytearray(original))
        derived = b"ARTIFICIAL DERIVED: selected=alpha"
        self.budget.put_many({"provenance/source": ("red-a", original),
                              "provenance/copy": ("red-a", working), "provenance/derived": ("red-a", derived)})
        chain = []
        parent = None
        for stage, content in (("original", original), ("copy", working), ("derived", derived)):
            chain.append({"stage": stage, "sha256": digest(content), "parent": parent,
                          "method": "artificial-transform-v1", "fixture_time": "2030-01-01T00:00:00Z"})
            parent = chain[-1]["sha256"]
        def verify(content: bytes, expected: str) -> None:
            require(hmac.compare_digest(digest(content), expected))
        self.observe("provenance", "copy-integrity", lambda: verify(working, chain[0]["sha256"]))
        self.observe("provenance", "tampering-denied", lambda: verify(working + b"changed", chain[0]["sha256"]), True)
        self.observe("provenance", "parent-chain", lambda: chain,
                     predicate=lambda x: x[1]["parent"] == x[0]["sha256"] and x[2]["parent"] == x[1]["sha256"])
        self.observe("provenance", "original-intact", lambda: original,
                     predicate=lambda x: digest(x) == chain[0]["sha256"])
        self.chains.append({"kind": "artificial-provenance", "entries": chain})

    def run(self) -> dict[str, object]:
        for scenario in (self.isolation, self.authority, self.revocation, self.incidental,
                         self.lifecycle, self.destinations_and_quotas, self.export_and_keys, self.provenance):
            scenario()
        groups = {event["group"] for event in self.events}
        require(len(groups) == 10 and len(self.events) == 674)
        return self.report()

    def report(self) -> dict[str, object]:
        return {"schema": "artificial-controls-v2", "scope": "host-side-logical-model",
                "clock": "logical-not-wall-time", "conditions": self.events,
                "planned_conditions": 674, "condition_count": len(self.events), "counts": self.journal.counts(),
                "budget_inventory_before_final_report": self.budget.inventory(),
                "chains": self.chains,
                "FACT": "Only local artificial model conditions are represented",
                "INFERENCE": "Model agreement cannot establish kernel or product security",
                "NOT_PROVEN": ["host fail-close", "independent guardian", "network boundary",
                               "wall-clock revocation", "custody after host loss", "provider retention"],
                "independent_review": "REQUIRED_NOT_EXECUTED", "operational_readiness": "BLOCKED"}


def main() -> int:
    # These context checks are not a security boundary or operational authority.
    require(os.environ.get("GITHUB_ACTIONS") == "true")
    require(os.environ.get("MODEL_DRIVER_ALLOWED") == "manual-locked-candidate")
    require(os.environ.get("CANDIDATE_SHA_INPUT") == os.environ.get("GITHUB_SHA"))
    require(os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch" and len(sys.argv) == 2)
    root = pathlib.Path(sys.argv[1])
    expected = pathlib.Path(os.environ["RUNNER_TEMP"]) / os.environ["OWNED_PREFIX"]
    require(root == expected and not root.is_symlink() and root.is_dir())
    require((root / "evidence").is_dir() and not (root / "evidence").is_symlink())
    require(re.fullmatch(r"synthetic-[0-9]+-[0-9]+", root.name) is not None)
    limits = Limits.configured()
    budget = Budget(limits)
    fixture = {case: "ARTIFICIAL-" + case for case in ("red-a", "red-b", "blue-a", "blue-b")}
    fixture_bytes = encoded({"classification": "ARTIFICIAL", "cases": fixture})
    fixture_hash = digest(fixture_bytes)
    journal = Journal(budget, root, os.environ["GITHUB_SHA"], fixture_hash)
    suite = None
    original: BaseException | None = None
    evidence_error: BaseException | None = None
    started = time.monotonic()
    previous_handlers = {}
    def interrupted(signum: int, frame: object) -> None:
        raise ModelInterrupted(signum)
    for signum in (signal.SIGINT, signal.SIGTERM):
        previous_handlers[signum] = signal.signal(signum, interrupted)
    try:
        budget.write_owned("fixtures/package", "cycle-evidence", fixture_bytes, root / "fixtures" / "fixtures.json")
        budget.write_owned("evidence/fixture-sha256", "cycle-evidence",
                           (fixture_hash + "  ../fixtures/fixtures.json\n").encode(), root / "evidence" / "fixture.sha256")
        suite = Suite(limits, budget, journal, fixture)
        suite.run()
    except BaseException as error:
        original = error
    finally:
        try:
            if original is not None:
                journal.failure(original)
            report = suite.report() if suite is not None else {"counts": journal.counts(), "conditions": []}
            report.update({"candidate": os.environ["GITHUB_SHA"], "fixture_sha256": fixture_hash,
                           "status": "ERROR_OR_INTERRUPT" if original else "MODEL_COMPLETE",
                           "original_error_type": type(original).__name__ if original else None,
                           "real_model_seconds": time.monotonic() - started,
                           "operational_readiness": "BLOCKED", "evidence_after_host_loss": "NOT_PROVEN"})
            budget.write_owned("evidence/final-report", "cycle-evidence", encoded(report),
                               root / "evidence" / "artificial-controls.json")
        except BaseException as error:
            evidence_error = error
            print("evidence_loss=" + type(error).__name__, file=sys.stderr)
        finally:
            for signum, handler in previous_handlers.items():
                signal.signal(signum, handler)
    if original is not None:
        raise original
    if evidence_error is not None:
        raise evidence_error
    print("artificial_model_recorded=true; operational_readiness=BLOCKED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ModelInterrupted as error:
        raise SystemExit(128 + error.signum)
    except Denied:
        raise SystemExit("artificial model refused; inspect owned evidence")

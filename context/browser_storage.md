# Browser sandbox contract v1

**State:** Phase 0 design freeze; implementation and real multi-tab/browser tests are Phase 3. No saved progress is claimed by the live Phase 1 preview.

## Authority and key

Use IndexedDB database `learngraph-ai-v1`, version 1, object store `sandboxes`, keyPath `key`. One record contains acknowledged events, optional pending event, versions, sandbox UUID, monotonic revision, and a matching cached analysis. No localStorage read-modify-write lock. One readwrite transaction on this store reads the record, checks expected UUID/revision/pending state, and writes the replacement atomically. Resolve mutation promises only after transaction completion; request success alone is not a committed write.

Key is `learngraph:v1:` plus compact JSON of the ordered array `[profile_id, release_id, release_hash, seed_id, seed_version, graph_version, catalog_version, model_version]`. Origin isolation is provided by the browser. Different versions/profiles never reuse a record or reinterpret its answers. Stable strings are ASCII IDs; do not hash or prepare event data asynchronously inside an active transaction.

Records contain only synthetic history, maximum 200 total visitor events including pending; serialized record ≤1 MiB and request ≤256 KiB. The cached bundle may be omitted first if the record reaches its cap; never silently drop acknowledged events. Reject corrupt or structurally/version-invalid records before using them. Preserve the raw record in place for an explicit reset/export decision; do not send it to a live endpoint or silently accept the last valid prefix.

`pending` is a PendingSubmission containing the immutable event, requested focus concept, requested trigger UUID/null, and request revision. Together with the record's acknowledged prefix/versions/UUID, these fields reconstruct the exact request after refresh; never substitute the newly selected UI focus. AnalysisBundle separately echoes requested_trigger_event_id and the resolved diagnosis trigger. Cached bundle metadata stores its input revision/digest, which must describe the acknowledged prefix even if staging a new pending answer has since increased the record revision.

## State transitions

| Action | Preconditions and atomic result |
| --- | --- |
| Initialize | No matching record: new sandbox UUID, revision 0, acknowledged=[], pending=null, cache=null. |
| Stage | UI observed revision r and UUID s, no pending. Prepare event and bytes first. Readwrite compare-and-swap writes pending event and revision r+1; acknowledged prefix unchanged. Commit before network submission. |
| Submit/retry | Outside storage transaction, send acknowledged+pending using exactly the staged event IDs/values and snapshot revision. At most one in-flight call per tab; zero automatic POST retries. |
| Acknowledge | Echoed profile/versions/focus/sandbox/revision, accepted event count, and recomputed semantic digest match the staged request; record still has that pending UUID/revision. Append once by ID, clear pending, increment revision, save complete bundle with its input revision and event digest. |
| Analyze acknowledged prefix | No pending; matching current record/digest required. Cache-only replacement does not increment the history revision. Store the bundle's input revision separately. |
| Retryable failure | Preserve pending bytes and acknowledged prefix. 429 honors Retry-After; network/503 exposes manual retry after at least 1 second. No fabricated acknowledgement or static-example substitution. |
| 409/422 | Preserve history/pending; explain version/conflict/validation failure. No unchanged automatic retry. Explicit discard/reset is required where correction cannot preserve the event's identity. |
| Discard pending | Explicit visitor action with matching revision/UUID: remove only pending, increment revision. Future event receives a new UUID and the next sequence after acknowledged events. |
| Reset | Explicit visitor action and compare-and-swap: new sandbox UUID, revision r+1, empty visitor history/pending/cache. Same canonical seed, no server mutation. |

Cached results are labeled saved/prerecorded until a successful live reanalysis of the restored prefix. On refresh, load the complete committed record. If pending exists, display it as pending and offer retry of the same snapshot; do not append a replacement answer or claim it was accepted. Acknowledged history and cached result are updated in the same transaction. Compute/validate hashes before opening the acknowledgement transaction; then recheck revision/UUID inside it.

## Concurrent tabs and late responses

IndexedDB readwrite scheduling serializes overlapping store transactions. Both tabs may read revision r, but only one compare-and-swap can stage a new answer; the other sees r+1 and stops with “updated in another tab.” Never silently merge conflicting answers, renumber them, or use last-write-wins.

Use BroadcastChannel `learngraph-v1` only as a notification hint with `{key,sandbox_id,revision}`—no event/answer payload. Re-read the authoritative record on a hint, focus/visibility restoration, and before every mutation. If BroadcastChannel is unavailable, those reads and transactional checks still preserve correctness. No timer keepalive or leader service is needed.

A late response is ignored if the active profile/key, sandbox UUID, revision, pending UUID, input digest, or versions changed. Abort fetch where useful, but aborting is not the correctness mechanism. Reset's new UUID prevents old in-flight responses from repopulating an empty record. Two tabs retrying the same persisted pending request may consume two quotas; semantic replay still admits that event once and only one acknowledgement transaction succeeds.

## Storage/version failures

- IndexedDB denied/unavailable, quota exceeded, aborted/failed commit: do not send an unstored answer. Offer explicit “Continue in this tab only,” then use a separate in-memory sandbox UUID and clearly label session-only persistence. A failed write must not erase the existing stored record.
- Session-only mode has per-tab isolation and no refresh/cross-tab persistence promise. Restoring persistent access requires explicit conflict resolution/import; never silently overwrite the older stored record.
- A new compatible-release tuple creates a different key. Offer a clean seed/reset while keeping incompatible old records untouched. P0 has **no automatic history migration**.
- Never wrap a revision counter. At 2^53−1, reject ordinary mutations; explicit reinitialization can replace the record with a new sandbox UUID and revision 0 in one transaction. The changed UUID invalidates all old responses.
- Handle IndexedDB `versionchange` by closing the connection; show a close-other-tabs/reload notice for blocked upgrades. Browser storage eviction/clearing can remove history; no nonexistent server backup can restore it.
- The browser controls these synthetic inputs. This is not authentication, cross-device synchronization, or proof of trusted student attempts.

## Verification obligations

Phase 3 must test actual browser transactions: two tabs stage from the same revision, duplicate retry/ack, refresh with pending work, reset while a response is in flight, profile/version switches, corrupt records, write failure, storage-denied mode, no BroadcastChannel, and blocked database upgrade. [State-transition fixtures](../contracts/fixtures/storage-transitions.json) specify expected outcomes; they do not constitute an implemented browser store.

Primary references: [IndexedDB transaction scheduling](https://w3c.github.io/IndexedDB/#transaction-scheduling) and [BroadcastChannel](https://html.spec.whatwg.org/multipage/web-messaging.html#broadcasting-to-other-browsing-contexts). IndexedDB is the authority; messaging is advisory.

# Worked example: missing transcript traced end-to-end

A compact real incident demonstrating every rule from `query-discipline.md` in order. Service names are generalised to roles; the method transfers.

The incident: a tenant reported a dictation session that produced no transcript for any of its three recordings, sourced from a Slack thread ("look into this"). No ids in the report — they were fetched from the thread's linked service context (Step 1) — giving one **interaction id**, three **recording ids**, a user id, an api_client id, and the tenant namespace for Loki.

## Step 1-2: inputs and stream discovery

- Tenant namespace label confirmed from label inventory (`k8s_namespace_name="medatixx"`); datasource uid found to be the central Loki used for that cluster.
- Inventory of services in that namespace (count_over_time per `service_name` over an hour): dictation-entry service (websocket gateway + audio publishing), transcription service, quality-assessment service, facts service, consumer/rendering service, storage/vault service.
- Stage map (from the repos, cross-checked with observed services): client → gateway/transcoder → Kafka → (transcription, quality) → transcript/facts/quality outputs → client; storage sidecar retains raw uploads.

## Step 3: bounded id sweep results (interaction id)

| Service (role) | Hits | First evidence |
|---|---|---|
| gateway (bridge) | ~2512 lines | websocket streams call, balance, routing, transcoder start |
| transcription | ~944 lines | chunk receipts, tick outputs, completion record |
| quality-assessment | ~633 lines | chunk receipts, tracker/completion records |
| voice-command / corrector / facts | some | downstream delivery history |

## Step 4: per-hop receipts (the decisive table)

| Stage | Receipt checked | Observed | Class |
|---|---|---|---|
| gateway received session | streams-request + routing lines | 3 recordings, 2-channel webm validated, transcode clean | VERIFIED |
| transcription received ALL audio | receipt occurrences (count) | 121/392/81 = 119/390/79 chunks + 2 empty stream-boundary messages, exact in every recording | VERIFIED |
| — parity | accumulated seconds at transcription == stored-seconds at vault | 35.64/116.94/23.64 both sides, 10ms precision | VERIFIED |
| transcription produced words | completion record of the transcription service | one per recording: "0 words" with dedicated anchored query (`s audio, 0 words,`) | VERIFIED |
| transcription invoked ASR engine | engine-response receipt line — emitted unconditionally per batch (source check, deployed version reconciled) | zero occurrences for this session | VERIFIED (negative) |
| quality saw speech | its completion record's `vad_duration_seconds` field | 0.0s for all three; same-hour comparison: it measures healthy sessions fine (e.g. 254s audio → 237s speech) | VERIFIED |
| quality event emitted downward | its completion record + output payload field | one `SPEECH_TO_LONG_SILENCE` per recording, at the 10s threshold, never recovered | VERIFIED |
| vault retained raw uploads | vault's stored/retention lines | three recordings retained, ids mapped | VERIFIED |

Two method moments worth calling out explicitly:

1. **The misread that taught the rule.** The transcription service's repeating "outputting 1 transcription segments" lines were initially read as VAD firings. Reading the source showed they are *silence-clock ticks* — a periodic marker emitted precisely when the VAD has detected no speech (its own docstring names long silences as the use case). The correction turned "speech-like energy" into "no speech at all" — the difference between two root-cause candidates. Lesson: an output-count indicator does not prove the thing it seems to count; read the producer's source.
2. **Nothing-was-sent proof.** "No transcript" could mean failed ASR or nothing submitted. The engine-response receipt line in the transcription service fires unconditionally per batch (verified in local source, then reconciled against the deployed version via a distinctive word-order and line numbers). Zero occurrences during the whole session = nothing was ever submitted and no responses returned — negative evidence accepted.

## Id-less attribution instance (Step 5 routine)

The quality service's tracker-event lines ("Long silence event: SPEECH_TO_LONG_SILENCE at 10000ms.") carry neither the session nor the interaction id (in the deployed version its update() call omits the logging extras). Attribution was done twice over:

- **Adjacency sandwich** — the id-less line sits between the owning session's receipt line and its worker send line, within 2ms, in each of the three recordings (e.g. .648/.650/.650 for the 116.94s recording).
- **Start-instant uniqueness** — at each event's implied start (event time −10s), exactly one session's first audio is found in a ±0.7s window; and the 10000ms timestamp itself fingerprints zero prior speech.
- (Other sessions' events in the same windows carry timestamps like 431984ms — the fingerprint alone excludes them as candidates.)

Also logged here: the query wrapper flaked twice on the tight windows (once returning stale-window content, twice empty) — the wider-window re-runs provided the evidence; the flake rule then entered the discipline reference.

## Verdict and boundary (Step 6)

Stage table populated: every hop VERIFIED to the audio level; the first stage whose expected behavior is missing is **ASR content itself** — audio arrived byte-complete across all services, but contained no recognizable speech (no VAD, no ASR words, one 10s long-silence event per recording, never recovered). The pipeline is healthy; the audio is not.

Unknown: whether the captured audio was pure digital silence (muting) or a faint signal. Settling it requires the retained raw files, which live in prod-side storage unreachable from a dev kubeconfig — stated as the next action for someone with prod access, rather than asserted.

The report against the template in SKILL.md Step 6 came out as the short-form file the reporter could paste into the original Slack thread (without posting automatically: approval first).

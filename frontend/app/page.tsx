"use client";

import { useEffect, useMemo, useState } from "react";
import {
  createProject,
  generateMusic,
  generateMusicPlan,
  listProjects,
  listPromptPresets,
  type MusicGenerateRequest,
  type MusicGenerateResponse,
  type MusicPlanResponse,
  type Project,
  type ProjectCreate,
  type PromptPreset,
} from "@/lib/api";

const DEFAULT_REQUEST: MusicGenerateRequest = {
  mode: "lyrics_only",
  lyricsVersion: "",
  promptPresetId: "",
  songStructure: "chorus_only",
  genre: "emotional pop ballad",
  bpm: 85,
  key: "C minor",
  duration: 45,
  seed: 1234,
  count: 1,
  instrumentalOnly: false,
  noAdditionalVocals: false,
  preserveMelody: false,
};

const DEFAULT_PROJECT_FORM: ProjectCreate = {
  title: "",
  theme: "",
  language: "en",
};

function formatCount(value: number, label: string) {
  return `${value} ${label}${value === 1 ? "" : "s"}`;
}

function formatAssetText(label: string | null | undefined, filename: string | null | undefined) {
  if (label && filename) {
    return `${label} · ${filename}`;
  }
  return label ?? filename ?? "Untitled asset";
}

export default function Page() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [presets, setPresets] = useState<PromptPreset[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [request, setRequest] = useState<MusicGenerateRequest>(DEFAULT_REQUEST);
  const [musicPlan, setMusicPlan] = useState<MusicPlanResponse | null>(null);
  const [musicResult, setMusicResult] = useState<MusicGenerateResponse | null>(null);
  const [busy, setBusy] = useState<"idle" | "spec" | "music">("idle");
  const [projectBusy, setProjectBusy] = useState<"idle" | "creating">("idle");
  const [projectForm, setProjectForm] = useState<ProjectCreate>(DEFAULT_PROJECT_FORM);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    void (async () => {
      try {
        const [loadedProjects, loadedPresets] = await Promise.all([listProjects(), listPromptPresets()]);
        setProjects(loadedProjects);
        setPresets(loadedPresets);

        const defaultPresetId = loadedPresets.find((preset) => preset.id === "default")?.id ?? loadedPresets[0]?.id ?? "";

        if (loadedProjects[0]) {
          setSelectedProjectId(loadedProjects[0].id);
          setRequest((current) => ({
            ...current,
            lyricsVersion: loadedProjects[0].selectedLyricsVersion ?? current.lyricsVersion,
            promptPresetId: loadedProjects[0].selectedPromptPreset ?? defaultPresetId ?? current.promptPresetId,
            genre: loadedProjects[0].genre ?? current.genre,
            bpm: loadedProjects[0].bpm ?? current.bpm,
            key: loadedProjects[0].key ?? current.key,
          }));
        } else {
          setRequest((current) => ({
            ...current,
            promptPresetId: defaultPresetId,
          }));
        }

        setMusicPlan(null);
        setMusicResult(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      }
    })();
  }, []);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectId) ?? null,
    [projects, selectedProjectId],
  );

  useEffect(() => {
    if (!selectedProject) {
      return;
    }

    setRequest((current) => ({
      ...current,
      lyricsVersion: current.lyricsVersion || selectedProject.selectedLyricsVersion || selectedProject.assets.lyricsVersions[0]?.id || "",
      promptPresetId:
        current.promptPresetId ||
        selectedProject.selectedPromptPreset ||
        presets.find((preset) => preset.id === "default")?.id ||
        presets[0]?.id ||
        "",
      genre: current.genre || selectedProject.genre || "",
      bpm: current.bpm || selectedProject.bpm || 85,
      key: current.key || selectedProject.key || "C minor",
    }));
  }, [selectedProject, presets]);

  const selectedPreset = useMemo(
    () => presets.find((preset) => preset.id === request.promptPresetId) ?? null,
    [presets, request.promptPresetId],
  );

  const assetCounts = useMemo(() => {
    if (!selectedProject) {
      return null;
    }

    return [
      { label: "Lyrics", count: selectedProject.assets.lyricsVersions.length },
      { label: "Plans", count: selectedProject.assets.musicPlans.length },
      { label: "Audio", count: selectedProject.assets.audioFiles.length },
      { label: "LRC", count: selectedProject.assets.lrcFiles.length },
      { label: "Jobs", count: selectedProject.assets.jobIds.length },
    ];
  }, [selectedProject]);

  async function handleCreateProject() {
    if (!projectForm.title.trim()) {
      setError("Project title is required");
      return;
    }

    setProjectBusy("creating");
    setError("");
    try {
      const created = await createProject({
        title: projectForm.title.trim(),
        theme: projectForm.theme?.trim() || null,
        language: projectForm.language || "en",
      });

      setProjects((current) => [created, ...current]);
      setSelectedProjectId(created.id);
      setProjectForm(DEFAULT_PROJECT_FORM);
      setMusicPlan(null);
      setMusicResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    } finally {
      setProjectBusy("idle");
    }
  }

  async function handleGenerateSpec() {
    if (!selectedProjectId) {
      return;
    }

    setBusy("spec");
    setError("");
    try {
      const nextPlan = await generateMusicPlan(selectedProjectId, request);
      setMusicPlan(nextPlan);
      setMusicResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate music plan");
    } finally {
      setBusy("idle");
    }
  }

  async function handleGenerateMusic() {
    if (!selectedProjectId) {
      return;
    }

    setBusy("music");
    setError("");
    try {
      const nextResult = await generateMusic(selectedProjectId, request);
      setMusicResult(nextResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate music");
    } finally {
      setBusy("idle");
    }
  }

  const recentLyricsVersions = selectedProject?.assets.lyricsVersions.slice(-4).reverse() ?? [];
  const recentPlans = selectedProject?.assets.musicPlans.slice(-4).reverse() ?? [];
  const recentAudioFiles = selectedProject?.assets.audioFiles.slice(-4).reverse() ?? [];
  const recentJobs = selectedProject?.assets.jobIds.slice(-6).reverse() ?? [];

  return (
    <main className="workspace">
      <div className="workspace-glow workspace-glow-left" />
      <div className="workspace-glow workspace-glow-right" />

      <div className="workspace-shell">
        <header className="hero workspace-hero">
          <div className="hero-copy">
            <p className="eyebrow">Local-only music workshop</p>
            <h1>Local AI Song Studio</h1>
            <p>
              가사, 프리셋, 스펙, 음악 생성, 결과 확인을 한 화면에 묶은 개인 작업실입니다.
              흐름은 왼쪽에서 오른쪽으로, 위에서 아래로 자연스럽게 이어집니다.
            </p>
          </div>

          <div className="hero-pills">
            <span className="pill">Dark mode only</span>
            <span className="pill">One-page workflow</span>
            <span className="pill">Studio desk layout</span>
          </div>
        </header>

        {error ? (
          <section className="banner error-banner">
            <strong>Error</strong>
            <span>{error}</span>
          </section>
        ) : null}

        <section className="status-strip">
          <div className="status-chip">
            <span>Active project</span>
            <strong>{selectedProject?.title ?? "Create a project"}</strong>
          </div>
          <div className="status-chip">
            <span>Prompt preset</span>
            <strong>{selectedPreset?.label ?? "None"}</strong>
          </div>
          <div className="status-chip">
            <span>Structure</span>
            <strong>{request.songStructure}</strong>
          </div>
          <div className="status-chip">
            <span>Generation</span>
            <strong>{busy === "idle" ? "Ready" : busy}</strong>
          </div>
        </section>

        <div className="studio-grid">
          <aside className="rail stack">
            <section className="card workspace-card">
              <div className="section-head">
                <p className="eyebrow">Shelf</p>
                <h2>Create project</h2>
                <p>새 프로젝트를 이 화면에서 바로 만들고 바로 작업 흐름에 넣습니다.</p>
              </div>

              <div className="stack">
                <div className="field">
                  <label>Title</label>
                  <input
                    value={projectForm.title ?? ""}
                    onChange={(event) => setProjectForm((current) => ({ ...current, title: event.target.value }))}
                    placeholder="Still In The Rain"
                  />
                </div>

                <div className="field">
                  <label>Theme</label>
                  <textarea
                    value={projectForm.theme ?? ""}
                    onChange={(event) => setProjectForm((current) => ({ ...current, theme: event.target.value }))}
                    placeholder="밤이 조용할수록 잊은 줄 알았던 목소리가 더 선명해진다"
                  />
                </div>

                <div className="field">
                  <label>Language</label>
                  <select
                    value={projectForm.language ?? "en"}
                    onChange={(event) => setProjectForm((current) => ({ ...current, language: event.target.value }))}
                  >
                    <option value="en">English</option>
                    <option value="ko">Korean</option>
                    <option value="mixed">Mixed</option>
                  </select>
                </div>

                <button className="button primary" onClick={handleCreateProject} disabled={projectBusy !== "idle"}>
                  {projectBusy === "creating" ? "Creating..." : "Create Project"}
                </button>
              </div>
            </section>

            <section className="card workspace-card">
              <div className="section-head">
                <p className="eyebrow">Shelf</p>
                <h2>Project selector</h2>
                <p>현재 작업 중인 프로젝트를 바꾸면 아래 작업대가 그대로 따라갑니다.</p>
              </div>

              <div className="stack">
                <div className="field">
                  <label>Project</label>
                  <select value={selectedProjectId} onChange={(event) => setSelectedProjectId(event.target.value)}>
                    <option value="">Select a project</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="project-summary">
                  <div className="project-title">{selectedProject?.title ?? "No project selected"}</div>
                  <div className="muted">{selectedProject?.theme ?? "Create or select a project to continue."}</div>
                  <div className="meta-grid">
                    <div>
                      <span>Language</span>
                      <strong>{selectedProject?.language ?? "-"}</strong>
                    </div>
                    <div>
                      <span>Genre</span>
                      <strong>{selectedProject?.genre ?? "-"}</strong>
                    </div>
                    <div>
                      <span>BPM</span>
                      <strong>{selectedProject?.bpm ?? "-"}</strong>
                    </div>
                    <div>
                      <span>Key</span>
                      <strong>{selectedProject?.key ?? "-"}</strong>
                    </div>
                  </div>
                </div>

                <div className="mini-grid">
                  {(assetCounts ?? []).map((entry) => (
                    <div key={entry.label} className="metric-card">
                      <span>{entry.label}</span>
                      <strong>{entry.count}</strong>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="card workspace-card">
              <div className="section-head">
                <p className="eyebrow">Shelf</p>
                <h2>Recent assets</h2>
                <p>선택된 프로젝트에 저장된 소재를 빠르게 훑습니다.</p>
              </div>

              <div className="stack">
                <div className="asset-block">
                  <div className="asset-block-head">
                    <strong>Lyrics</strong>
                    <span>{selectedProject?.assets.lyricsVersions.length ?? 0}</span>
                  </div>
                  <div className="asset-list">
                    {recentLyricsVersions.length ? (
                      recentLyricsVersions.map((asset) => (
                        <div key={asset.id} className="asset-row">
                          <span className="asset-name">{asset.id}</span>
                          <span className="muted">{formatAssetText(asset.label, asset.filename)}</span>
                        </div>
                      ))
                    ) : (
                      <div className="muted">No lyric versions yet.</div>
                    )}
                  </div>
                </div>

                <div className="asset-block">
                  <div className="asset-block-head">
                    <strong>Plans</strong>
                    <span>{selectedProject?.assets.musicPlans.length ?? 0}</span>
                  </div>
                  <div className="asset-list">
                    {recentPlans.length ? (
                      recentPlans.map((asset) => (
                        <div key={asset.id} className="asset-row">
                          <span className="asset-name">{asset.id}</span>
                          <span className="muted">{formatAssetText(asset.label, asset.filename)}</span>
                        </div>
                      ))
                    ) : (
                      <div className="muted">No music plans yet.</div>
                    )}
                  </div>
                </div>

                <div className="asset-block">
                  <div className="asset-block-head">
                    <strong>Audio</strong>
                    <span>{selectedProject?.assets.audioFiles.length ?? 0}</span>
                  </div>
                  <div className="asset-list">
                    {recentAudioFiles.length ? (
                      recentAudioFiles.map((asset) => (
                        <div key={asset.id} className="asset-row">
                          <span className="asset-name">{asset.id}</span>
                          <span className="muted">{formatAssetText(asset.label, asset.filename)}</span>
                        </div>
                      ))
                    ) : (
                      <div className="muted">No audio files yet.</div>
                    )}
                  </div>
                </div>

                <div className="asset-block">
                  <div className="asset-block-head">
                    <strong>Jobs</strong>
                    <span>{selectedProject?.assets.jobIds.length ?? 0}</span>
                  </div>
                  <div className="asset-list compact">
                    {recentJobs.length ? (
                      recentJobs.map((jobId) => (
                        <div key={jobId} className="asset-row">
                          <span className="asset-name mono">{jobId}</span>
                        </div>
                      ))
                    ) : (
                      <div className="muted">No jobs yet.</div>
                    )}
                  </div>
                </div>
              </div>
            </section>
          </aside>

          <section className="workbench stack">
            <section className="card workspace-card workbench-card">
              <div className="section-head">
                <p className="eyebrow">Workbench</p>
                <h2>Generation controls</h2>
                <p>
                  가사 버전과 프리셋을 고르고, 쇼츠용 구조를 정한 뒤 스펙과 오디오를 차례대로 만듭니다.
                </p>
              </div>

              <div className="control-grid">
                <div className="field">
                  <label>Prompt preset</label>
                  <select
                    value={request.promptPresetId ?? ""}
                    onChange={(event) => setRequest((current) => ({ ...current, promptPresetId: event.target.value }))}
                  >
                    {presets.map((preset) => (
                      <option key={preset.id} value={preset.id}>
                        {preset.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="field">
                  <label>Lyrics version</label>
                  <select
                    value={request.lyricsVersion ?? ""}
                    onChange={(event) => setRequest((current) => ({ ...current, lyricsVersion: event.target.value }))}
                  >
                    <option value="">Select a lyrics version</option>
                    {selectedProject?.assets.lyricsVersions.map((version) => (
                      <option key={version.id} value={version.id}>
                        {version.id} - {version.label ?? version.filename ?? "Untitled"}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="field">
                  <label>Song structure</label>
                  <select
                    value={request.songStructure}
                    onChange={(event) => setRequest((current) => ({ ...current, songStructure: event.target.value }))}
                  >
                    <option value="chorus_only">Chorus only, 30-60s</option>
                    <option value="short_song">Short song</option>
                    <option value="full_song">Full song</option>
                  </select>
                </div>

                <div className="field">
                  <label>Mode</label>
                  <select
                    value={request.mode}
                    onChange={(event) => setRequest((current) => ({ ...current, mode: event.target.value }))}
                  >
                    <option value="lyrics_only">Lyrics only</option>
                    <option value="vocal_to_bgm">Vocal to BGM</option>
                    <option value="instrumental">Instrumental</option>
                    <option value="reference_audio">Reference audio</option>
                  </select>
                </div>

                <div className="field">
                  <label>Genre</label>
                  <input
                    value={request.genre ?? ""}
                    onChange={(event) => setRequest((current) => ({ ...current, genre: event.target.value }))}
                    placeholder="emotional pop ballad"
                  />
                </div>

                <div className="field">
                  <label>BPM</label>
                  <input
                    type="number"
                    value={request.bpm ?? ""}
                    onChange={(event) =>
                      setRequest((current) => ({ ...current, bpm: event.target.value ? Number(event.target.value) : null }))
                    }
                  />
                </div>

                <div className="field">
                  <label>Key</label>
                  <input
                    value={request.key ?? ""}
                    onChange={(event) => setRequest((current) => ({ ...current, key: event.target.value }))}
                    placeholder="C minor"
                  />
                </div>

                <div className="field">
                  <label>Duration</label>
                  <input
                    type="number"
                    value={request.duration}
                    onChange={(event) => setRequest((current) => ({ ...current, duration: Number(event.target.value) }))}
                  />
                </div>

                <div className="field">
                  <label>Seed</label>
                  <input
                    type="number"
                    value={request.seed ?? ""}
                    onChange={(event) =>
                      setRequest((current) => ({ ...current, seed: event.target.value ? Number(event.target.value) : null }))
                    }
                  />
                </div>

                <div className="field">
                  <label>Count</label>
                  <input
                    type="number"
                    value={request.count}
                    onChange={(event) => setRequest((current) => ({ ...current, count: Number(event.target.value) }))}
                  />
                </div>
              </div>

              <div className="toggle-row">
                <label className={`toggle-chip ${request.instrumentalOnly ? "active" : ""}`}>
                  <input
                    type="checkbox"
                    checked={Boolean(request.instrumentalOnly)}
                    onChange={(event) => setRequest((current) => ({ ...current, instrumentalOnly: event.target.checked }))}
                  />
                  Instrumental only
                </label>
                <label className={`toggle-chip ${request.noAdditionalVocals ? "active" : ""}`}>
                  <input
                    type="checkbox"
                    checked={Boolean(request.noAdditionalVocals)}
                    onChange={(event) => setRequest((current) => ({ ...current, noAdditionalVocals: event.target.checked }))}
                  />
                  No additional vocals
                </label>
                <label className={`toggle-chip ${request.preserveMelody ? "active" : ""}`}>
                  <input
                    type="checkbox"
                    checked={Boolean(request.preserveMelody)}
                    onChange={(event) => setRequest((current) => ({ ...current, preserveMelody: event.target.checked }))}
                  />
                  Preserve melody
                </label>
              </div>

              <div className="action-bar">
                <button className="button ghost" onClick={handleGenerateSpec} disabled={busy !== "idle"}>
                  {busy === "spec" ? "Generating spec..." : "Generate spec"}
                </button>
                <button className="button primary" onClick={handleGenerateMusic} disabled={busy !== "idle"}>
                  {busy === "music" ? "Generating music..." : "Generate music"}
                </button>
              </div>
            </section>

            <section className="card workspace-card">
              <div className="section-head">
                <p className="eyebrow">Workbench</p>
                <h2>Blueprint and prompt</h2>
                <p>선택한 프리셋이 스펙과 최종 생성 프롬프트에 어떻게 반영되는지 바로 확인합니다.</p>
              </div>

              {selectedPreset ? (
                <div className="preset-sheet">
                  <div className="preset-banner">
                    <div>
                      <strong>{selectedPreset.label}</strong>
                      <div className="muted mono">
                        match: {selectedPreset.matchGenres.join(", ") || "default"} · default: {selectedPreset.defaultBpm ?? "-"} BPM /{" "}
                        {selectedPreset.defaultKey ?? "-"} / {selectedPreset.defaultDuration ?? "-"}s
                      </div>
                    </div>
                    <div className="pill-row">
                      <span className="pill">Spec first</span>
                      <span className="pill">Short-form first</span>
                    </div>
                  </div>

                  <div className="guidance-grid">
                    <div className="guidance-card">
                      <span>Blueprint guidance</span>
                      <ul>
                        {selectedPreset.blueprintGuidance.length ? (
                          selectedPreset.blueprintGuidance.map((line) => <li key={line}>{line}</li>)
                        ) : (
                          <li>None</li>
                        )}
                      </ul>
                    </div>
                    <div className="guidance-card">
                      <span>Generation guidance</span>
                      <ul>
                        {selectedPreset.generationGuidance.length ? (
                          selectedPreset.generationGuidance.map((line) => <li key={line}>{line}</li>)
                        ) : (
                          <li>None</li>
                        )}
                      </ul>
                    </div>
                    <div className="guidance-card">
                      <span>Avoid guidance</span>
                      <ul>
                        {selectedPreset.avoidGuidance.length ? (
                          selectedPreset.avoidGuidance.map((line) => <li key={line}>{line}</li>)
                        ) : (
                          <li>None</li>
                        )}
                      </ul>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="muted">프리셋을 불러오는 중이거나 선택된 프리셋이 없습니다.</div>
              )}
            </section>

            <section className="card workspace-card">
              <div className="section-head">
                <p className="eyebrow">Workbench</p>
                <h2>Latest blueprint</h2>
                <p>스펙 생성 결과를 먼저 보고, 그 다음 오디오를 밀어 넣는 순서로 작업합니다.</p>
              </div>

              {musicPlan ? (
                <div className="result-stack">
                  <div className="result-grid">
                    <div className="result-card">
                      <span>Plan id</span>
                      <strong className="mono">{musicPlan.musicPlanFileId ?? "-"}</strong>
                    </div>
                    <div className="result-card">
                      <span>Engine</span>
                      <strong className="mono">{musicPlan.engine}</strong>
                    </div>
                    <div className="result-card">
                      <span>BPM</span>
                      <strong>{musicPlan.bpm ?? request.bpm ?? "-"}</strong>
                    </div>
                    <div className="result-card">
                      <span>Key</span>
                      <strong>{musicPlan.key ?? request.key ?? "-"}</strong>
                    </div>
                  </div>

                  <div className="story-sheet">
                    <div className="field">
                      <label>Caption</label>
                      <div className="story-box">{musicPlan.caption}</div>
                    </div>
                    <div className="field">
                      <label>Lyrics</label>
                      <pre className="pre result-pre">{musicPlan.lyrics}</pre>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <strong>Blueprint will appear here.</strong>
                  <span>Generate a music spec first to capture the blueprint before rendering audio.</span>
                </div>
              )}
            </section>

            <section className="card workspace-card">
              <div className="section-head">
                <p className="eyebrow">Workbench</p>
                <h2>Latest audio</h2>
                <p>생성된 오디오와 작업 메타데이터를 확인합니다.</p>
              </div>

              {musicResult ? (
                <div className="result-stack">
                  <div className="result-grid">
                    <div className="result-card">
                      <span>Job</span>
                      <strong className="mono">{musicResult.jobId}</strong>
                    </div>
                    <div className="result-card">
                      <span>Mode</span>
                      <strong className="mono">{musicResult.mode}</strong>
                    </div>
                    <div className="result-card">
                      <span>Engine</span>
                      <strong className="mono">{musicResult.engine}</strong>
                    </div>
                    <div className="result-card">
                      <span>Audio files</span>
                      <strong>{formatCount(musicResult.audioFileIds.length, "file")}</strong>
                    </div>
                  </div>

                  <div className="story-sheet">
                    <div className="field">
                      <label>Prompt</label>
                      <div className="story-box">{musicResult.prompt}</div>
                    </div>
                    <div className="field">
                      <label>Audio file ids</label>
                      <div className="chip-row">
                        {musicResult.audioFileIds.map((audioFileId) => (
                          <span key={audioFileId} className="chip mono">
                            {audioFileId}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="field">
                      <label>Raw result</label>
                      <pre className="pre result-pre">{JSON.stringify(musicResult, null, 2)}</pre>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <strong>Audio output will appear here.</strong>
                  <span>Run music generation after the blueprint is locked.</span>
                </div>
              )}
            </section>
          </section>

          <aside className="rail stack">
            <section className="card workspace-card">
              <div className="section-head">
                <p className="eyebrow">Drawer</p>
                <h2>Preset rack</h2>
                <p>현재 프리셋이 어떤 방향성을 강제하는지 빠르게 읽습니다.</p>
              </div>

              {selectedPreset ? (
                <div className="stack">
                  <div className="preset-summary">
                    <div className="preset-summary-title">{selectedPreset.label}</div>
                    <div className="muted mono">preset: {selectedPreset.id}</div>
                  </div>
                  <div className="meta-grid">
                    <div>
                      <span>Default BPM</span>
                      <strong>{selectedPreset.defaultBpm ?? "-"}</strong>
                    </div>
                    <div>
                      <span>Default Key</span>
                      <strong>{selectedPreset.defaultKey ?? "-"}</strong>
                    </div>
                    <div>
                      <span>Duration</span>
                      <strong>{selectedPreset.defaultDuration ?? "-"}</strong>
                    </div>
                    <div>
                      <span>Match</span>
                      <strong>{selectedPreset.matchGenres.length}</strong>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="muted">No preset selected.</div>
              )}
            </section>

            <section className="card workspace-card">
              <div className="section-head">
                <p className="eyebrow">Drawer</p>
                <h2>Project status</h2>
                <p>선택된 프로젝트의 구조와 최근 자산을 요약합니다.</p>
              </div>

              <div className="stack">
                <div className="meta-grid">
                  <div>
                    <span>Lyrics versions</span>
                    <strong>{selectedProject?.assets.lyricsVersions.length ?? 0}</strong>
                  </div>
                  <div>
                    <span>Music plans</span>
                    <strong>{selectedProject?.assets.musicPlans.length ?? 0}</strong>
                  </div>
                  <div>
                    <span>Audio files</span>
                    <strong>{selectedProject?.assets.audioFiles.length ?? 0}</strong>
                  </div>
                  <div>
                    <span>Video files</span>
                    <strong>{selectedProject?.assets.videoFiles.length ?? 0}</strong>
                  </div>
                </div>

                <div className="asset-block">
                  <div className="asset-block-head">
                    <strong>Recent jobs</strong>
                    <span>{selectedProject?.assets.jobIds.length ?? 0}</span>
                  </div>
                  <div className="asset-list compact">
                    {recentJobs.length ? (
                      recentJobs.map((jobId) => (
                        <div key={jobId} className="asset-row">
                          <span className="asset-name mono">{jobId}</span>
                        </div>
                      ))
                    ) : (
                      <div className="muted">No jobs yet.</div>
                    )}
                  </div>
                </div>
              </div>
            </section>
          </aside>
        </div>
      </div>
    </main>
  );
}

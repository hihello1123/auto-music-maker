"use client";

import { useEffect, useMemo, useState } from "react";
import {
  API_BASE,
  createProject,
  deleteProject,
  generateMusic,
  generateMusicPlan,
  listProjects,
  listPromptPresets,
  previewLyrics,
  saveLyrics,
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
};

const KEY_MODE_OPTIONS = [
  { value: "major", label: "Major" },
  { value: "minor", label: "Minor" },
];

const KEY_TONIC_OPTIONS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"];

function formatCount(value: number, label: string) {
  return `${label} ${value}개`;
}

function formatAssetText(label: string | null | undefined, filename: string | null | undefined) {
  if (label && filename) {
    return `${label} · ${filename}`;
  }
  return label ?? filename ?? "이름 없음";
}

function formatProjectDate(value: string | undefined) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("ko-KR", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function createRandomSeed() {
  return Math.floor(Math.random() * 2_147_483_647) + 1;
}

function parseKeyValue(value: string | null | undefined) {
  const normalized = (value ?? "C minor").trim();
  const [tonic = "C", mode = "minor"] = normalized.split(/\s+/, 2);
  return {
    tonic: KEY_TONIC_OPTIONS.includes(tonic) ? tonic : "C",
    mode: (mode === "major" ? "major" : "minor") as "major" | "minor",
  };
}

export default function Page() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [presets, setPresets] = useState<PromptPreset[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [request, setRequest] = useState<MusicGenerateRequest>(DEFAULT_REQUEST);
  const [musicPlan, setMusicPlan] = useState<MusicPlanResponse | null>(null);
  const [musicResult, setMusicResult] = useState<MusicGenerateResponse | null>(null);
  const [busy, setBusy] = useState<"idle" | "spec" | "music">("idle");
  const [lyricsBusy, setLyricsBusy] = useState<"idle" | "generating" | "saving">("idle");
  const [projectBusy, setProjectBusy] = useState<"idle" | "creating">("idle");
  const [deletingProjectId, setDeletingProjectId] = useState<string>("");
  const [projectForm, setProjectForm] = useState<ProjectCreate>(DEFAULT_PROJECT_FORM);
  const [lyricsDraft, setLyricsDraft] = useState<string>("");
  const [lyricsLanguage, setLyricsLanguage] = useState<string>("en");
  const [lyricsInstruction, setLyricsInstruction] = useState<string>("short singable chorus-first lyrics for a 30-60 second short video");
  const [lyricsLabel, setLyricsLabel] = useState<string>("manual_edit");
  const [error, setError] = useState<string>("");
  const [keyTonic, setKeyTonic] = useState<string>("C");
  const [keyMode, setKeyMode] = useState<"major" | "minor">("minor");

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
      setError(err instanceof Error ? err.message : "데이터를 불러오지 못했습니다");
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

    const parsedKey = parseKeyValue(selectedProject.key || request.key || "C minor");
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
      key: `${parsedKey.tonic} ${parsedKey.mode}`,
    }));
    setKeyTonic(parsedKey.tonic);
    setKeyMode(parsedKey.mode);
  }, [selectedProject, presets]);

  const selectedPreset = useMemo(
    () => presets.find((preset) => preset.id === request.promptPresetId) ?? null,
    [presets, request.promptPresetId],
  );

  const assetCounts = useMemo(() => {
    if (!selectedProject) {
      return [];
    }

    return [
      { label: "가사", count: selectedProject.assets.lyricsVersions.length },
      { label: "스펙", count: selectedProject.assets.musicPlans.length },
      { label: "오디오", count: selectedProject.assets.audioFiles.length },
      { label: "LRC", count: selectedProject.assets.lrcFiles.length },
      { label: "작업", count: selectedProject.assets.jobIds.length },
    ];
  }, [selectedProject]);

  function selectProject(project: Project) {
    const parsedKey = parseKeyValue(project.key || request.key || "C minor");
    setSelectedProjectId(project.id);
    setRequest((current) => ({
      ...current,
      lyricsVersion: project.selectedLyricsVersion || project.assets.lyricsVersions[0]?.id || "",
      promptPresetId:
        project.selectedPromptPreset ||
        current.promptPresetId ||
        presets.find((preset) => preset.id === "default")?.id ||
        presets[0]?.id ||
        "",
      genre: project.genre || current.genre || "",
      bpm: project.bpm || current.bpm || 85,
      key: `${parsedKey.tonic} ${parsedKey.mode}`,
    }));
    setKeyTonic(parsedKey.tonic);
    setKeyMode(parsedKey.mode);
    setMusicPlan(null);
    setMusicResult(null);
    setLyricsLanguage(project.language || "en");
  }

  async function refreshProjects(nextSelectedProjectId: string) {
    const loadedProjects = await listProjects();
    setProjects(loadedProjects);
    const nextSelectedProject = loadedProjects.find((project) => project.id === nextSelectedProjectId);
    if (nextSelectedProject) {
      selectProject(nextSelectedProject);
    }
  }

  async function reloadProjects() {
    const loadedProjects = await listProjects();
    setProjects(loadedProjects);
  }

  async function handleCreateProject() {
    if (!projectForm.title.trim()) {
      setError("프로젝트 제목이 필요합니다");
      return;
    }

    setProjectBusy("creating");
    setError("");
    try {
      const created = await createProject({
        title: projectForm.title.trim(),
        theme: projectForm.theme?.trim() || null,
      });

      setProjects((current) => [created, ...current]);
      selectProject(created);
      setProjectForm(DEFAULT_PROJECT_FORM);
    } catch (err) {
      setError(err instanceof Error ? err.message : "프로젝트를 만들지 못했습니다");
    } finally {
      setProjectBusy("idle");
    }
  }

  async function handleDeleteProject(project: Project) {
    const confirmed = window.confirm(`"${project.title}" 프로젝트를 삭제할까요? 로컬 저장 파일도 함께 삭제됩니다.`);
    if (!confirmed) {
      return;
    }

    setDeletingProjectId(project.id);
    setError("");
    try {
      await deleteProject(project.id);

      const remainingProjects = projects.filter((item) => item.id !== project.id);
      setProjects(remainingProjects);

      if (selectedProjectId === project.id) {
        const nextProject = remainingProjects[0];
        if (nextProject) {
          selectProject(nextProject);
        } else {
          setSelectedProjectId("");
          setMusicPlan(null);
          setMusicResult(null);
          setRequest((current) => ({
            ...current,
            lyricsVersion: "",
          }));
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "프로젝트를 삭제하지 못했습니다");
    } finally {
      setDeletingProjectId("");
    }
  }

  async function handleGenerateLyrics() {
    if (!selectedProject) {
      return;
    }

    setLyricsBusy("generating");
    setError("");
    try {
      const preview = await previewLyrics(selectedProject.id, {
        theme: selectedProject.theme,
        language: lyricsLanguage || selectedProject.language,
        style: request.genre || selectedProject.genre || "감성 팝 발라드",
        instruction: lyricsInstruction,
        versionCount: 1,
      });
      setLyricsDraft(preview.content);
    } catch (err) {
      setError(err instanceof Error ? err.message : "가사를 생성하지 못했습니다");
    } finally {
      setLyricsBusy("idle");
    }
  }

  async function handleSaveLyrics() {
    if (!selectedProject || !lyricsDraft.trim()) {
      setError("저장할 가사 내용이 필요합니다");
      return;
    }

    setLyricsBusy("saving");
    setError("");
    try {
      const record = await saveLyrics(selectedProject.id, {
        content: lyricsDraft.trim(),
        label: lyricsLabel.trim() || "manual_edit",
      });
      setLyricsDraft("");
      await refreshProjects(selectedProject.id);
      setRequest((current) => ({ ...current, lyricsVersion: record.id }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "가사를 저장하지 못했습니다");
    } finally {
      setLyricsBusy("idle");
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
      setError(err instanceof Error ? err.message : "곡 스펙을 생성하지 못했습니다");
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
      await reloadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "음악을 생성하지 못했습니다");
    } finally {
      setBusy("idle");
    }
  }

  const recentLyricsVersions = selectedProject?.assets.lyricsVersions.slice(-5).reverse() ?? [];
  const recentPlans = selectedProject?.assets.musicPlans.slice(-5).reverse() ?? [];
  const recentAudioFiles = selectedProject?.assets.audioFiles.slice(-5).reverse() ?? [];
  const recentJobs = selectedProject?.assets.jobIds.slice(-8).reverse() ?? [];

  return (
    <main className="admin-page">
      <aside className="admin-sidebar">
        <div className="admin-brand">
          <strong>음악 작업실</strong>
          <span>로컬 대시보드</span>
        </div>

        <details className="admin-create">
          <summary>새 프로젝트</summary>
          <div className="admin-create-form">
            <label>
              <span>제목</span>
              <input
                value={projectForm.title ?? ""}
                onChange={(event) => setProjectForm((current) => ({ ...current, title: event.target.value }))}
                placeholder="비 오는 밤의 블루스"
              />
            </label>
            <label>
              <span>감정선 / 테마</span>
              <textarea
                value={projectForm.theme ?? ""}
                onChange={(event) => setProjectForm((current) => ({ ...current, theme: event.target.value }))}
                placeholder="밤이 조용할수록 잊은 줄 알았던 목소리가 더 선명해진다"
              />
            </label>
            <button className="button primary admin-create-button" onClick={handleCreateProject} disabled={projectBusy !== "idle"}>
              {projectBusy === "creating" ? "생성 중..." : "생성"}
            </button>
          </div>
        </details>

        <div className="admin-sidebar-title">
          <span>프로젝트</span>
          <strong>{projects.length}</strong>
        </div>

        <div className="admin-projects">
          {projects.length ? (
            projects.map((project) => {
              const isSelected = project.id === selectedProjectId;
              return (
                <div key={project.id} className={`admin-project-row ${isSelected ? "selected" : ""}`}>
                  <button className="admin-project-main" onClick={() => selectProject(project)} type="button">
                    <span className="admin-project-title">{project.title}</span>
                    <span className="admin-project-meta">
                      가사 {project.assets.lyricsVersions.length} · 오디오 {project.assets.audioFiles.length}
                    </span>
                  </button>
                  <button
                    className="admin-project-delete"
                    onClick={() => void handleDeleteProject(project)}
                    type="button"
                    disabled={Boolean(deletingProjectId)}
                    title={`${project.title} 삭제`}
                  >
                    {deletingProjectId === project.id ? "..." : "×"}
                  </button>
                </div>
              );
            })
          ) : (
            <div className="admin-empty">프로젝트 없음</div>
          )}
        </div>
      </aside>

      <section className="admin-main">
        <header className="admin-topbar">
          <div>
            <p className="admin-kicker">프로젝트 상세</p>
            <h1>{selectedProject?.title ?? "선택된 프로젝트 없음"}</h1>
            <p>{selectedProject?.theme ?? "왼쪽에서 프로젝트를 만들거나 선택하세요."}</p>
          </div>
          <div className="admin-actions">
            <button
              className="button ghost"
              onClick={handleGenerateSpec}
              disabled={busy !== "idle" || !selectedProjectId || !request.lyricsVersion}
            >
              {busy === "spec" ? "스펙 생성 중..." : "곡 스펙 생성"}
            </button>
          </div>
        </header>

        {error ? (
          <section className="admin-alert">
            <strong>오류</strong>
            <span>{error}</span>
          </section>
        ) : null}

        <section className="admin-summary-grid">
          <div className="admin-stat">
            <span>생성일</span>
            <strong className="admin-stat-small">{formatProjectDate(selectedProject?.createdAt)}</strong>
          </div>
          <div className="admin-stat">
            <span>수정일</span>
            <strong className="admin-stat-small">{formatProjectDate(selectedProject?.updatedAt)}</strong>
          </div>
          {assetCounts.map((entry) => (
            <div key={entry.label} className="admin-stat">
              <span>{entry.label}</span>
              <strong>{entry.count}</strong>
            </div>
          ))}
          {!assetCounts.length ? (
            <div className="admin-stat">
              <span>상태</span>
              <strong>비어 있음</strong>
            </div>
          ) : null}
        </section>

        <div className="workflow-grid">
          <section className="admin-panel workflow-column">
            <div className="admin-panel-head">
              <h2>가사 작업공간</h2>
              <span>{selectedProject?.selectedLyricsVersion ?? "저장본 없음"}</span>
            </div>

            <div className="admin-lyrics-layout">
              <div className="admin-lyrics-controls">
                <label>
                  <span>가사 언어</span>
                  <select value={lyricsLanguage} onChange={(event) => setLyricsLanguage(event.target.value)}>
                    <option value="en">영어</option>
                    <option value="ko">한국어</option>
                    <option value="mixed">혼합</option>
                  </select>
                </label>
                <label>
                  <span>생성 지시문</span>
                  <textarea
                    value={lyricsInstruction}
                    onChange={(event) => setLyricsInstruction(event.target.value)}
                    placeholder="쇼츠용으로 부르기 쉬운 후렴 중심 가사"
                  />
                </label>
                <button
                  className="button ghost"
                  onClick={handleGenerateLyrics}
                  disabled={lyricsBusy !== "idle" || !selectedProject}
                  type="button"
                >
                  {lyricsBusy === "generating" ? "가사 생성 중..." : "가사 생성"}
                </button>
              </div>

              <div className="admin-lyrics-controls">
                <label>
                  <span>검수 및 수정할 가사</span>
                  <textarea
                    value={lyricsDraft}
                    onChange={(event) => setLyricsDraft(event.target.value)}
                    placeholder="[후렴]\n비 내리는 밤에 네 목소리가 들려..."
                  />
                </label>
                <label>
                  <span>저장 라벨</span>
                  <input value={lyricsLabel} onChange={(event) => setLyricsLabel(event.target.value)} placeholder="직접수정" />
                </label>
                <button className="button primary" onClick={handleSaveLyrics} disabled={lyricsBusy !== "idle" || !selectedProject} type="button">
                  {lyricsBusy === "saving" ? "가사 저장 중..." : "검수한 가사 저장"}
                </button>
              </div>
            </div>

            <div className="admin-table-list">
              <div className="admin-table-head">
                <span>보관본</span>
                <span>라벨</span>
                <span>파일</span>
                <span>생성일</span>
              </div>
              {recentLyricsVersions.length ? (
                recentLyricsVersions.map((asset) => (
                  <button
                    key={asset.id}
                    className={`admin-table-row ${request.lyricsVersion === asset.id ? "selected" : ""}`}
                    onClick={() => setRequest((current) => ({ ...current, lyricsVersion: asset.id }))}
                    type="button"
                  >
                    <span>{asset.id}</span>
                    <span>{asset.label ?? "-"}</span>
                    <span>{asset.filename ?? "-"}</span>
                    <span>{formatProjectDate(asset.createdAt)}</span>
                  </button>
                ))
              ) : (
                <div className="admin-empty">저장된 가사 없음</div>
              )}
            </div>
          </section>

          <section className="admin-panel workflow-column">
            <div className="admin-panel-head">
              <h2>음악 생성 작업공간</h2>
              <span>{busy === "idle" ? "대기 중" : busy}</span>
            </div>

            <div className="admin-form-grid">
              <label>
                <span>프롬프트 프리셋</span>
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
              </label>

              <label>
                <span>사용할 가사</span>
                <select
                  value={request.lyricsVersion ?? ""}
                  onChange={(event) => setRequest((current) => ({ ...current, lyricsVersion: event.target.value }))}
                >
                  <option value="">가사 선택</option>
                  {selectedProject?.assets.lyricsVersions.map((version) => (
                    <option key={version.id} value={version.id}>
                      {version.id} - {version.label ?? version.filename ?? "이름 없음"}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                <span>곡 구조</span>
                <select
                  value={request.songStructure}
                  onChange={(event) => setRequest((current) => ({ ...current, songStructure: event.target.value }))}
                >
                  <option value="chorus_only">후렴 중심, 30-60초</option>
                  <option value="short_song">짧은 곡</option>
                  <option value="full_song">전체 곡</option>
                </select>
              </label>

              <label>
                <span>생성 모드</span>
                <select value={request.mode} onChange={(event) => setRequest((current) => ({ ...current, mode: event.target.value }))}>
                  <option value="lyrics_only">가사 기반</option>
                  <option value="vocal_to_bgm">보컬 기반 반주</option>
                  <option value="instrumental">반주만</option>
                  <option value="reference_audio">레퍼런스 오디오</option>
                </select>
              </label>

              <label>
                <span>장르</span>
                <input
                  value={request.genre ?? ""}
                  onChange={(event) => setRequest((current) => ({ ...current, genre: event.target.value }))}
                  placeholder="감성 팝 발라드"
                />
              </label>

              <label>
                <span>BPM</span>
                <input
                  type="number"
                  value={request.bpm ?? ""}
                  onChange={(event) =>
                    setRequest((current) => ({ ...current, bpm: event.target.value ? Number(event.target.value) : null }))
                  }
                />
              </label>

              <label>
                <span>키</span>
                <div className="key-row">
                  <select
                    value={keyTonic}
                    onChange={(event) => {
                      const nextTonic = event.target.value;
                      setKeyTonic(nextTonic);
                      setRequest((current) => ({ ...current, key: `${nextTonic} ${keyMode}` }));
                    }}
                  >
                    {KEY_TONIC_OPTIONS.map((tonic) => (
                      <option key={tonic} value={tonic}>
                        {tonic}
                      </option>
                    ))}
                  </select>
                  <select
                    value={keyMode}
                    onChange={(event) => {
                      const nextMode = event.target.value as "major" | "minor";
                      setKeyMode(nextMode);
                      setRequest((current) => ({ ...current, key: `${keyTonic} ${nextMode}` }));
                    }}
                  >
                    {KEY_MODE_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </label>

              <label>
                <span>길이</span>
                <input
                  type="number"
                  value={request.duration}
                  onChange={(event) => setRequest((current) => ({ ...current, duration: Number(event.target.value) }))}
                />
              </label>

              <label>
                <span>시드</span>
                <div className="seed-row">
                  <input
                    type="number"
                    value={request.seed ?? ""}
                    onChange={(event) =>
                      setRequest((current) => ({ ...current, seed: event.target.value ? Number(event.target.value) : null }))
                    }
                  />
                  <button
                    className="button ghost seed-random-button"
                    onClick={() => setRequest((current) => ({ ...current, seed: createRandomSeed() }))}
                    type="button"
                  >
                    랜덤
                  </button>
                </div>
              </label>

              <label>
                <span>생성 개수</span>
                <input
                  type="number"
                  value={request.count}
                  onChange={(event) => setRequest((current) => ({ ...current, count: Number(event.target.value) }))}
                />
              </label>
            </div>

            <div className="admin-toggle-row">
              <label>
                <input
                  type="checkbox"
                  checked={Boolean(request.instrumentalOnly)}
                  onChange={(event) => setRequest((current) => ({ ...current, instrumentalOnly: event.target.checked }))}
                />
                반주만 생성
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={Boolean(request.noAdditionalVocals)}
                  onChange={(event) => setRequest((current) => ({ ...current, noAdditionalVocals: event.target.checked }))}
                />
                추가 보컬 없음
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={Boolean(request.preserveMelody)}
                  onChange={(event) => setRequest((current) => ({ ...current, preserveMelody: event.target.checked }))}
                />
                멜로디 유지
              </label>
            </div>

            <div className="admin-action-row">
              <button
                className="button primary"
                onClick={handleGenerateMusic}
                disabled={busy !== "idle" || !selectedProjectId || !request.lyricsVersion}
                type="button"
              >
                {busy === "music" ? "음악 생성 중..." : "음악 생성"}
              </button>
            </div>

            <div className="inline-panel">
              <div className="admin-panel-head">
                <h2>프롬프트 프리셋</h2>
                <span>{selectedPreset?.id ?? "없음"}</span>
              </div>
              {selectedPreset ? (
                <div className="admin-note-list">
                  <strong>{selectedPreset.label}</strong>
                  <span>
                    {selectedPreset.defaultBpm ?? "-"} BPM · {selectedPreset.defaultKey ?? "-"} ·{" "}
                    {selectedPreset.defaultDuration ?? "-"}s
                  </span>
                  <ul>
                    {selectedPreset.generationGuidance.slice(0, 4).map((line) => (
                      <li key={line}>{line}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <div className="admin-empty">선택된 프리셋 없음</div>
              )}
            </div>

            <div className="inline-panel">
              <div className="admin-panel-head">
                <h2>최근 곡 스펙</h2>
                <span>{musicPlan?.musicPlanFileId ?? "아직 없음"}</span>
              </div>
              {musicPlan ? (
                <div className="admin-result">
                  <div className="admin-result-metrics">
                    <span>엔진: {musicPlan.engine}</span>
                    <span>BPM: {musicPlan.bpm ?? request.bpm ?? "-"}</span>
                    <span>키: {musicPlan.key ?? request.key ?? "-"}</span>
                    <span>길이: {musicPlan.duration ?? request.duration}s</span>
                  </div>
                  <p>{musicPlan.caption}</p>
                  <pre>{musicPlan.lyrics}</pre>
                </div>
              ) : (
                <div className="admin-empty">생성된 곡 스펙 없음</div>
              )}
            </div>
          </section>

          <section className="admin-panel workflow-column">
            <div className="admin-panel-head">
              <h2>결과물 확인 및 작업공간</h2>
              <span>{musicResult?.engine ?? "아직 없음"}</span>
            </div>

            {musicResult ? (
              <div className="admin-result compact">
                <div className="admin-result-metrics">
                  <span>작업: {musicResult.jobId}</span>
                  <span>모드: {musicResult.mode}</span>
                  <span>{formatCount(musicResult.audioFileIds.length, "파일")}</span>
                </div>
                <div className="admin-chip-row">
                  {musicResult.audioFileIds.map((audioFileId) => (
                    <span key={audioFileId}>{audioFileId}</span>
                  ))}
                </div>
                <div className="admin-audio-list">
                  {recentAudioFiles.length ? (
                    recentAudioFiles.map((asset) => {
                      const audioUrl = `${API_BASE}/projects/${selectedProjectId}/audio/${asset.id}`;
                      return (
                        <div key={asset.id} className="admin-audio-item">
                          <div className="admin-audio-meta">
                            <strong>{asset.label ?? asset.id}</strong>
                            <span>{asset.filename ?? "오디오 파일"}</span>
                          </div>
                          <audio controls src={audioUrl} />
                        </div>
                      );
                    })
                  ) : (
                    <div className="admin-empty">재생할 오디오가 아직 없습니다</div>
                  )}
                </div>
              </div>
            ) : (
              <div className="admin-empty">생성된 오디오 없음</div>
            )}

            <div className="admin-asset-columns">
              <div>
                <strong>가사</strong>
                {recentLyricsVersions.length ? (
                  recentLyricsVersions.map((asset) => <span key={asset.id}>{formatAssetText(asset.label ?? asset.id, asset.filename)}</span>)
                ) : (
                  <span>가사 없음</span>
                )}
              </div>
              <div>
                <strong>스펙</strong>
                {recentPlans.length ? (
                  recentPlans.map((asset) => <span key={asset.id}>{formatAssetText(asset.label ?? asset.id, asset.filename)}</span>)
                ) : (
                  <span>스펙 없음</span>
                )}
              </div>
              <div>
                <strong>오디오</strong>
                {recentAudioFiles.length ? (
                  recentAudioFiles.map((asset) => <span key={asset.id}>{formatAssetText(asset.label ?? asset.id, asset.filename)}</span>)
                ) : (
                  <span>오디오 없음</span>
                )}
              </div>
              <div>
                <strong>작업</strong>
                {recentJobs.length ? recentJobs.map((jobId) => <span key={jobId}>{jobId}</span>) : <span>작업 없음</span>}
              </div>
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

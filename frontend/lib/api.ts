export type ProjectAssetRecord = {
  id: string;
  label?: string | null;
  filename?: string | null;
  originalFilename?: string | null;
  path?: string | null;
  metadataPath?: string | null;
  createdAt?: string;
  updatedAt?: string;
};

export type Project = {
  id: string;
  title: string;
  theme?: string | null;
  language: string;
  genre?: string | null;
  bpm?: number | null;
  key?: string | null;
  selectedLyricsVersion?: string | null;
  selectedPromptPreset?: string | null;
  selectedMusicPlan?: string | null;
  selectedAudioFile?: string | null;
  selectedLrcFile?: string | null;
  assets: {
    lyricsVersions: ProjectAssetRecord[];
    promptFiles: ProjectAssetRecord[];
    musicPlans: ProjectAssetRecord[];
    vocalFiles: ProjectAssetRecord[];
    audioFiles: ProjectAssetRecord[];
    lrcFiles: ProjectAssetRecord[];
    videoFiles: ProjectAssetRecord[];
    jobIds: string[];
  };
};

export type ProjectCreate = {
  title: string;
  theme?: string | null;
  language?: string;
};

export type PromptPreset = {
  id: string;
  label: string;
  matchGenres: string[];
  blueprintGuidance: string[];
  generationGuidance: string[];
  avoidGuidance: string[];
  defaultBpm?: number | null;
  defaultKey?: string | null;
  defaultDuration?: number | null;
};

export type MusicGenerateRequest = {
  mode: string;
  lyricsVersion?: string | null;
  promptPresetId?: string | null;
  songStructure?: string;
  genre?: string | null;
  bpm?: number | null;
  key?: string | null;
  duration: number;
  seed?: number | null;
  count: number;
  instrumentalOnly?: boolean;
  noAdditionalVocals?: boolean;
  preserveMelody?: boolean;
};

export type MusicPlanResponse = {
  musicPlanFileId?: string | null;
  promptPresetId?: string | null;
  promptPresetLabel?: string | null;
  sourcePrompt: string;
  caption: string;
  lyrics: string;
  genre?: string | null;
  bpm?: number | null;
  key?: string | null;
  duration?: number | null;
  timeSignature?: string | null;
  language?: string | null;
  engine: string;
  createdAt: string;
};

export type MusicGenerateResponse = {
  jobId: string;
  prompt: string;
  mode: string;
  seed?: number | null;
  promptFileId?: string | null;
  musicPlanFileId?: string | null;
  promptPresetId?: string | null;
  audioFileIds: string[];
  engine: string;
  createdAt: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:12000";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function listProjects(): Promise<Project[]> {
  return requestJson<Project[]>("/projects");
}

export async function createProject(body: ProjectCreate): Promise<Project> {
  return requestJson<Project>("/projects", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function listPromptPresets(): Promise<PromptPreset[]> {
  return requestJson<PromptPreset[]>("/prompt-presets");
}

export async function generateMusicPlan(projectId: string, body: MusicGenerateRequest): Promise<MusicPlanResponse> {
  return requestJson<MusicPlanResponse>(`/projects/${projectId}/music/spec/generate`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function generateMusic(projectId: string, body: MusicGenerateRequest): Promise<MusicGenerateResponse> {
  return requestJson<MusicGenerateResponse>(`/projects/${projectId}/music/generate`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

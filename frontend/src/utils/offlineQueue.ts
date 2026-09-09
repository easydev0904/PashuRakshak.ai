import type { ObservationInput } from "@/types/api";

const STORAGE_KEY = "pashurakshak.offline_observations";

export interface QueuedObservation {
  id: string;
  animalId: string;
  payload: ObservationInput;
  createdAt: string;
}

function readAll(): QueuedObservation[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as QueuedObservation[]) : [];
  } catch {
    return [];
  }
}

function writeAll(items: QueuedObservation[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch {
    // If storage is full or unavailable, the draft is lost silently --
    // acceptable for this prototype's offline support, not a crash.
  }
}

export const offlineQueue = {
  list(): QueuedObservation[] {
    return readAll();
  },
  listForAnimal(animalId: string): QueuedObservation[] {
    return readAll().filter((item) => item.animalId === animalId);
  },
  enqueue(animalId: string, payload: ObservationInput): QueuedObservation {
    const entry: QueuedObservation = {
      id: `draft-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      animalId,
      payload,
      createdAt: new Date().toISOString(),
    };
    writeAll([...readAll(), entry]);
    return entry;
  },
  remove(id: string): void {
    writeAll(readAll().filter((item) => item.id !== id));
  },
  count(): number {
    return readAll().length;
  },
};

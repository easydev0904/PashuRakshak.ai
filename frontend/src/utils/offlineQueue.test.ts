import { beforeEach, describe, expect, it } from "vitest";

import { offlineQueue } from "@/utils/offlineQueue";
import type { ObservationInput } from "@/types/api";

const SAMPLE: ObservationInput = {
  appetite: "normal",
  activity: "normal",
  water_intake: "normal",
  respiratory_sign: "none",
  dung_sign: "normal",
};

describe("offlineQueue", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("starts empty", () => {
    expect(offlineQueue.count()).toBe(0);
    expect(offlineQueue.list()).toEqual([]);
  });

  it("enqueues a draft with a generated id and timestamp", () => {
    const entry = offlineQueue.enqueue("animal-1", SAMPLE);
    expect(entry.id).toBeTruthy();
    expect(entry.animalId).toBe("animal-1");
    expect(entry.payload).toEqual(SAMPLE);
    expect(offlineQueue.count()).toBe(1);
  });

  it("lists only drafts for the requested animal", () => {
    offlineQueue.enqueue("animal-1", SAMPLE);
    offlineQueue.enqueue("animal-2", SAMPLE);
    expect(offlineQueue.listForAnimal("animal-1")).toHaveLength(1);
    expect(offlineQueue.listForAnimal("animal-2")).toHaveLength(1);
    expect(offlineQueue.listForAnimal("animal-3")).toHaveLength(0);
  });

  it("removes a draft by id", () => {
    const entry = offlineQueue.enqueue("animal-1", SAMPLE);
    offlineQueue.remove(entry.id);
    expect(offlineQueue.count()).toBe(0);
  });

  it("persists across separate calls (backed by localStorage)", () => {
    offlineQueue.enqueue("animal-1", SAMPLE);
    expect(offlineQueue.count()).toBe(1);
    expect(offlineQueue.list()[0].animalId).toBe("animal-1");
  });
});

import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";

import { animalKeys } from "@/hooks/useAnimals";
import { animalService } from "@/services/animalService";
import { offlineQueue } from "@/utils/offlineQueue";

/**
 * Flushes any locally-queued observation drafts to the server. Mounted
 * once at the app shell level so a draft saved from one screen still
 * syncs even if the farmer has since navigated away -- and so it
 * retries automatically the moment connectivity returns, not only when
 * the farmer happens to revisit the observation form.
 */
export function useOfflineSync() {
  const queryClient = useQueryClient();
  const [pendingCount, setPendingCount] = useState(() => offlineQueue.count());
  const [isSyncing, setIsSyncing] = useState(false);

  const flush = useCallback(async () => {
    if (!navigator.onLine) return;
    const items = offlineQueue.list();
    if (items.length === 0) return;

    setIsSyncing(true);
    for (const item of items) {
      try {
        await animalService.submitObservation(item.animalId, item.payload);
        offlineQueue.remove(item.id);
        queryClient.invalidateQueries({ queryKey: animalKeys.observations(item.animalId) });
        queryClient.invalidateQueries({ queryKey: animalKeys.detail(item.animalId) });
        queryClient.invalidateQueries({ queryKey: animalKeys.all });
      } catch {
        // Leave it queued -- could be offline again, or a transient
        // server error. It will retry on the next flush.
        break;
      }
    }
    setPendingCount(offlineQueue.count());
    setIsSyncing(false);
  }, [queryClient]);

  useEffect(() => {
    // Attempt a flush on mount, then again every time the browser regains
    // connectivity -- both cases are "sync with an external system"
    // (network state + the localStorage queue), not derived render state.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void flush();
    window.addEventListener("online", flush);
    return () => window.removeEventListener("online", flush);
  }, [flush]);

  return { pendingCount, isSyncing, flush };
}

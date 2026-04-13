import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

import { configureApiAuthCallbacks } from "../api/client";

/**
 * Clears React Query cache when the API returns 401 (handled in axios interceptor).
 */
export function QueryClientAuthBridge() {
  const qc = useQueryClient();
  useEffect(() => {
    configureApiAuthCallbacks({
      onUnauthorized: () => {
        qc.clear();
      },
    });
    return () => configureApiAuthCallbacks({});
  }, [qc]);
  return null;
}

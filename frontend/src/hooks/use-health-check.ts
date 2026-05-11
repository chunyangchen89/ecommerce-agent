"use client";

import { useState, useEffect } from "react";
import { getHealth } from "@/lib/api-client";
import type { HealthResponse } from "@/lib/types";

export function useHealthCheck(intervalMs = 30000) {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    let mounted = true;

    async function check() {
      try {
        const data = await getHealth();
        if (mounted) setHealth(data);
      } catch {
        if (mounted) setHealth(null);
      }
    }

    check();
    const id = setInterval(check, intervalMs);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, [intervalMs]);

  return health;
}

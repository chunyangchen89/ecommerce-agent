"use client";

import { useState } from "react";
import { postQuery } from "@/lib/api-client";
import type { QueryResponse } from "@/lib/types";

interface QueryState {
  loading: boolean;
  error: string | null;
  data: QueryResponse | null;
}

export function useQueryAgent() {
  const [state, setState] = useState<QueryState>({
    loading: false,
    error: null,
    data: null,
  });

  async function submit(query: string, topK = 10) {
    setState({ loading: true, error: null, data: null });
    try {
      const data = await postQuery({ query, top_k: topK });
      setState({ loading: false, error: null, data });
    } catch (err) {
      setState({
        loading: false,
        error: err instanceof Error ? err.message : "Unknown error",
        data: null,
      });
    }
  }

  function reset() {
    setState({ loading: false, error: null, data: null });
  }

  return { ...state, submit, reset };
}

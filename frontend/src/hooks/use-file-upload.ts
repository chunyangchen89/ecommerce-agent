"use client";

import { useState, useCallback } from "react";

export function useFileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectFile = useCallback((f: File | null) => {
    setFile(f);
    setProgress(0);
    setError(null);
  }, []);

  const upload = useCallback(async () => {
    if (!file) return;
    setUploading(true);
    setProgress(0);
    setError(null);

    // TODO: Replace with actual API call when backend endpoint exists
    for (let i = 0; i <= 100; i += 10) {
      await new Promise((r) => setTimeout(r, 200));
      setProgress(i);
    }

    setUploading(false);
    setProgress(100);
  }, [file]);

  const reset = useCallback(() => {
    setFile(null);
    setProgress(0);
    setUploading(false);
    setError(null);
  }, []);

  return { file, progress, uploading, error, selectFile, upload, reset };
}

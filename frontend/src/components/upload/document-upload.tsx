"use client";

import { useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useFileUpload } from "@/hooks/use-file-upload";
import { Upload, File, X, CheckCircle } from "lucide-react";

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function DocumentUpload() {
  const { file, progress, uploading, selectFile, upload, reset } =
    useFileUpload();
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null;
    if (f && f.size > 10 * 1024 * 1024) {
      return;
    }
    selectFile(f);
  }

  return (
    <Card className="rounded-3xl border-hairline-soft bg-canvas">
      <CardContent className="p-6">
        <h4 className="mb-1 text-lg font-bold text-ink-deep">
          Upload Document
        </h4>
        <p className="mb-4 text-sm text-steel">
          Upload a document for embedding and analysis
        </p>

        {!file ? (
          <label className="block cursor-pointer">
            <div className="rounded-2xl border-2 border-dashed border-hairline p-10 text-center transition-colors hover:border-cobalt/40">
              <Upload className="mx-auto mb-2 h-8 w-8 text-stone" />
              <span className="text-sm text-steel">
                Click to select or drag and drop
              </span>
              <span className="mt-1 block text-xs text-stone">
                PDF, TXT, CSV (max 10MB)
              </span>
            </div>
            <input
              ref={inputRef}
              type="file"
              className="hidden"
              onChange={handleFileChange}
              accept=".pdf,.txt,.csv,.docx"
            />
          </label>
        ) : (
          <div>
            <div className="flex items-center gap-3 rounded-xl bg-surface-soft p-3">
              <File className="h-5 w-5 text-steel" />
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-bold text-ink-deep">
                  {file.name}
                </div>
                <div className="text-xs text-stone">
                  {formatFileSize(file.size)}
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={reset}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {uploading && (
              <div className="mt-3">
                <Progress
                  value={progress}
                  className="h-2 rounded-full"
                />
                <span className="mt-1 block text-xs text-steel">
                  {progress}% uploaded
                </span>
              </div>
            )}

            {!uploading && progress < 100 && (
              <Button
                className="mt-3 w-full rounded-full bg-cobalt text-white hover:bg-cobalt-deep"
                onClick={upload}
              >
                Upload
              </Button>
            )}

            {progress === 100 && !uploading && (
              <div className="mt-3 flex items-center gap-1 text-sm font-bold text-meta-success">
                <CheckCircle className="h-4 w-4" />
                Upload complete
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

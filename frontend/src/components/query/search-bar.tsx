"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

interface SearchBarProps {
  onSubmit: (query: string) => void;
  loading: boolean;
}

export function SearchBar({ onSubmit, loading }: SearchBarProps) {
  const [query, setQuery] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto flex max-w-2xl gap-2">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-steel" />
        <Input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about your data..."
          className="h-12 rounded-full border-hairline bg-surface-soft pl-10 pr-4 text-ink placeholder:text-stone focus-visible:border-cobalt focus-visible:ring-cobalt/20"
          disabled={loading}
        />
      </div>
      <Button
        type="submit"
        disabled={loading || !query.trim()}
        className="h-12 rounded-full px-6 font-bold cursor-pointer shadow-none hover:shadow-[0_0_0_3px_rgba(0,100,224,0.3)]"
      >
        Ask
      </Button>
    </form>
  );
}

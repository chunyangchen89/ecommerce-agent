"use client";

import { SearchBar } from "@/components/query/search-bar";
import { QueryLoading } from "@/components/query/query-loading";
import { ResultsPanel } from "@/components/results/results-panel";
import { Card, CardContent } from "@/components/ui/card";
import { useQueryAgent } from "@/hooks/use-query-agent";

export default function Home() {
  const { loading, error, data, submit } = useQueryAgent();

  return (
    <main className="flex-1">
      <div className="mx-auto max-w-5xl px-5">
        <section className="pb-8 pt-20 text-center">
          <h1 className="mb-1 text-3xl font-medium text-ink-deep">
            Ecommerce Data Agent
          </h1>
          <p className="mb-8 text-base text-steel">
            Ask questions about your data in natural language
          </p>
          <SearchBar onSubmit={submit} loading={loading} />
        </section>

        {loading && <QueryLoading />}

        {error && (
          <div className="mx-auto max-w-3xl">
            <Card className="rounded-3xl border-meta-critical/30 bg-canvas">
              <CardContent className="p-6">
                <p className="text-sm font-bold text-meta-critical">
                  Error: {error}
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {data && <ResultsPanel data={data} />}
      </div>
    </main>
  );
}

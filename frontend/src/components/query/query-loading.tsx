import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function QueryLoading() {
  return (
    <div className="mx-auto mt-6 max-w-3xl">
      <Card className="rounded-3xl border-hairline-soft">
        <CardContent className="p-8">
          <div className="mb-5 flex items-center gap-2">
            <Skeleton className="h-6 w-20 rounded-full" />
            <span className="text-sm text-steel">Analyzing your query...</span>
          </div>
          <Skeleton className="mb-2 h-4 w-full rounded-lg" />
          <Skeleton className="mb-2 h-4 w-3/4 rounded-lg" />
          <Skeleton className="h-4 w-1/2 rounded-lg" />
        </CardContent>
      </Card>
    </div>
  );
}

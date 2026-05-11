import { Card, CardContent } from "@/components/ui/card";
import ReactMarkdown from "react-markdown";

interface AnswerCardProps {
  answer: string;
}

export function AnswerCard({ answer }: AnswerCardProps) {
  return (
    <Card className="rounded-3xl border-hairline-soft bg-canvas">
      <CardContent className="p-8">
        <h3 className="mb-3 text-xl font-medium text-ink-deep">Answer</h3>
        <div className="prose max-w-none leading-relaxed text-ink [&_h1]:text-2xl [&_h1]:font-semibold [&_h1]:text-ink-deep [&_h1]:mt-6 [&_h1]:mb-2 [&_h2]:text-xl [&_h2]:font-semibold [&_h2]:text-ink-deep [&_h2]:mt-5 [&_h2]:mb-2 [&_h3]:text-lg [&_h3]:font-semibold [&_h3]:text-ink-deep [&_h3]:mt-4 [&_h3]:mb-2 [&_p]:mb-3 [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:mb-3 [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:mb-3 [&_li]:mb-1 [&_strong]:text-ink-deep [&_table]:w-full [&_th]:border [&_th]:border-hairline-soft [&_th]:px-3 [&_th]:py-2 [&_th]:bg-surface-soft [&_th]:text-left [&_th]:text-sm [&_th]:font-bold [&_th]:text-steel [&_td]:border [&_td]:border-hairline-soft [&_td]:px-3 [&_td]:py-2 [&_td]:text-sm [&_code]:rounded [&_code]:bg-surface-soft [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:text-sm [&_code]:text-charcoal [&_pre]:rounded-xl [&_pre]:bg-surface-soft [&_pre]:p-4 [&_pre]:overflow-x-auto [&_blockquote]:border-l-4 [&_blockquote]:border-cobalt [&_blockquote]:pl-4 [&_blockquote]:text-charcoal [&_blockquote]:italic">
          <ReactMarkdown>{answer}</ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  );
}

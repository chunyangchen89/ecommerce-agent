import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card } from "@/components/ui/card";

interface DataTableProps {
  data: Record<string, unknown>[];
}

export function DataTable({ data }: DataTableProps) {
  if (!data || data.length === 0) return null;

  const columns = Object.keys(data[0]);

  return (
    <Card className="overflow-hidden rounded-3xl border-hairline-soft">
      <div className="px-4 pb-1 pt-4">
        <span className="text-sm font-bold text-ink-deep">Query Results</span>
        <span className="ml-1 text-sm text-steel">
          ({data.length} row{data.length !== 1 ? "s" : ""})
        </span>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-surface-soft hover:bg-surface-soft">
              {columns.map((col) => (
                <TableHead
                  key={col}
                  className="text-xs font-bold text-steel"
                >
                  {col}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, i) => (
              <TableRow key={i} className="border-b border-hairline-soft">
                {columns.map((col) => (
                  <TableCell key={col} className="text-sm text-ink">
                    {String(row[col] ?? "")}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  );
}

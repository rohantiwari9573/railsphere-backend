import { useNavigate } from "react-router-dom";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

export interface DataTableColumn<T> {
  header: string;
  accessor: (row: T) => React.ReactNode;
  className?: string;
}

interface Props<T> {
  columns: DataTableColumn<T>[];
  data: T[];
  getRowKey: (row: T) => string | number;
  getRowHref?: (row: T) => string;
}

export function DataTable<T>({
  columns,
  data,
  getRowKey,
  getRowHref,
}: Props<T>) {
  const navigate = useNavigate();

  return (
    <div className="overflow-hidden rounded-xl border border-border bg-card">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              {columns.map((column) => (
                <TableHead key={column.header} className={column.className}>
                  {column.header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, i) => (
              <TableRow
                key={getRowKey(row)}
                className={cn(
                  "animate-in fade-in slide-in-from-bottom-1 fill-mode-both duration-300",
                  getRowHref && "cursor-pointer"
                )}
                style={{ animationDelay: `${Math.min(i * 25, 300)}ms` }}
                onClick={() =>
                  getRowHref && navigate(getRowHref(row))
                }
              >
                {columns.map((column) => (
                  <TableCell key={column.header} className={column.className}>
                    {column.accessor(row)}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

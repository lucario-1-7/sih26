import { useEffect, useState } from "react";

import type { PaginatedResponse } from "@/types/api";

/**
 * Accumulates pages from a cursor-paginated endpoint, with an explicit
 * `loadMore()` action rather than auto-fetching — the backend never uses
 * offset/page-number pagination (see server/app/core/pagination.py), and
 * this hook mirrors that opaque-cursor contract.
 *
 * Usage:
 *   const pagination = useCursorPagination<Thing>();
 *   const query = useThingsList({ cursor: pagination.queryCursor });
 *   useEffect(() => { if (query.data) pagination.consume(query.data); }, [query.data]);
 *   <button onClick={pagination.loadMore} disabled={!pagination.hasNext}>Load more</button>
 */
export function useCursorPagination<T>() {
  const [queryCursor, setQueryCursor] = useState<string | undefined>(undefined);
  const [items, setItems] = useState<T[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);

  function consume(page: PaginatedResponse<T>) {
    setItems((prev) => (queryCursor === undefined ? page.items : [...prev, ...page.items]));
    setNextCursor(page.next_cursor);
  }

  function loadMore() {
    if (nextCursor) setQueryCursor(nextCursor);
  }

  function reset() {
    setQueryCursor(undefined);
    setItems([]);
    setNextCursor(null);
  }

  return { queryCursor, items, hasNext: nextCursor !== null, consume, loadMore, reset };
}

/** Convenience effect wrapper: syncs a query's `data` into the pagination accumulator. */
export function useSyncCursorPage<T>(
  pagination: ReturnType<typeof useCursorPagination<T>>,
  data: PaginatedResponse<T> | undefined,
) {
  useEffect(() => {
    if (data) pagination.consume(data);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);
}

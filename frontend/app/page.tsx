"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  RotateCcw,
  Search,
  SlidersHorizontal,
} from "lucide-react";

import Sidebar from "@/components/Sidebar";

type Relevance = {
  final_score?: number;
  classification?: string;
  keyword_score?: number;
  semantic_score?: number;
  matched_keywords?: string[];
  matched_phrases?: string[];
  best_capability?: string | null;
};

type Tender = {
  id: string;
  source?: string;
  tender_number?: string;
  title?: string;
  organization?: string;
  advertised_date?: string;
  closing_date?: string;
  status?: string;
  tender_url?: string;
  relevance?: Relevance;
};

export default function HomePage() {
  const router = useRouter();

  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedCapability, setSelectedCapability] =
    useState("All Capabilities");

  const [selectedSource, setSelectedSource] =
    useState("All Sources");

  const [selectedRelevance, setSelectedRelevance] =
    useState("All");

  const [selectedStatus, setSelectedStatus] =
    useState("All Statuses");

  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    async function loadTenders() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch("/api/tenders");

        if (!response.ok) {
          throw new Error("Failed to fetch tenders.");
        }

        const data = await response.json();

        if (!Array.isArray(data)) {
          throw new Error("Invalid tender data.");
        }

        setTenders(data);
      } catch (err) {
        console.error(err);
        setError("Unable to load tender data.");
      } finally {
        setLoading(false);
      }
    }

    loadTenders();
  }, []);

  const capabilities = useMemo(() => {
    const capabilitySet = new Set<string>();

    tenders.forEach((tender) => {
      const capability =
        tender.relevance?.best_capability;

      if (
        capability &&
        typeof capability === "string"
      ) {
        capabilitySet.add(capability);
      } else {
        capabilitySet.add("Unassigned");
      }
    });

    return Array.from(capabilitySet).sort(
      (a, b) => a.localeCompare(b)
    );
  }, [tenders]);

  const capabilityCounts = useMemo(() => {
    const counts: Record<string, number> = {};

    tenders.forEach((tender) => {
      const capability =
        tender.relevance?.best_capability;

      if (
        capability &&
        typeof capability === "string"
      ) {
        counts[capability] =
          (counts[capability] || 0) + 1;
      } else {
        counts.Unassigned =
          (counts.Unassigned || 0) + 1;
      }
    });

    return counts;
  }, [tenders]);

  const sources = useMemo(() => {
    const sourceSet = new Set<string>();

    tenders.forEach((tender) => {
      if (
        tender.source &&
        typeof tender.source === "string"
      ) {
        sourceSet.add(tender.source);
      }
    });

    return Array.from(sourceSet).sort(
      (a, b) => a.localeCompare(b)
    );
  }, [tenders]);

  const sourceCounts = useMemo(() => {
    const counts: Record<string, number> = {};

    tenders.forEach((tender) => {
      const source = tender.source;

      if (
        source &&
        typeof source === "string"
      ) {
        counts[source] =
          (counts[source] || 0) + 1;
      }
    });

    return counts;
  }, [tenders]);

  const statuses = useMemo(() => {
    const statusSet = new Set<string>();

    tenders.forEach((tender) => {
      if (
        tender.status &&
        typeof tender.status === "string"
      ) {
        statusSet.add(tender.status);
      }
    });

    return Array.from(statusSet).sort(
      (a, b) => a.localeCompare(b)
    );
  }, [tenders]);

  const filteredTenders = useMemo(() => {
    const query = searchQuery
      .trim()
      .toLowerCase();

    return tenders.filter((tender) => {
      const matchesCapability =
        selectedCapability ===
          "All Capabilities" ||
        (selectedCapability === "Unassigned"
          ? !tender.relevance?.best_capability
          : tender.relevance?.best_capability ===
            selectedCapability);

      const matchesSource =
        selectedSource === "All Sources" ||
        tender.source === selectedSource;

      const matchesRelevance =
        selectedRelevance === "All" ||
        tender.relevance?.classification ===
          selectedRelevance;

      const matchesStatus =
        selectedStatus === "All Statuses" ||
        tender.status === selectedStatus;

      const searchableText = [
        tender.tender_number,
        tender.title,
        tender.organization,
        tender.source,
        tender.status,
        tender.relevance?.best_capability,
        ...(tender.relevance?.matched_keywords ||
          []),
        ...(tender.relevance?.matched_phrases ||
          []),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      const matchesSearch =
        !query ||
        searchableText.includes(query);

      return (
        matchesCapability &&
        matchesSource &&
        matchesRelevance &&
        matchesStatus &&
        matchesSearch
      );
    });
  }, [
    tenders,
    selectedCapability,
    selectedSource,
    selectedRelevance,
    selectedStatus,
    searchQuery,
  ]);

  const sortedFilteredTenders = useMemo(
    () =>
      [...filteredTenders].sort((a, b) => {
        const dateA = a.advertised_date
          ? Date.parse(a.advertised_date)
          : 0;
        const dateB = b.advertised_date
          ? Date.parse(b.advertised_date)
          : 0;

        return dateB - dateA;
      }),
    [filteredTenders]
  );

  function clearFilters() {
    setSelectedCapability("All Capabilities");
    setSelectedSource("All Sources");
    setSelectedRelevance("All");
    setSelectedStatus("All Statuses");
    setSearchQuery("");
  }

  const filtersActive =
    selectedCapability !== "All Capabilities" ||
    selectedSource !== "All Sources" ||
    selectedRelevance !== "All" ||
    selectedStatus !== "All Statuses" ||
    searchQuery.trim() !== "";

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar
        capabilities={capabilities}
        capabilityCounts={capabilityCounts}
        selectedCapability={selectedCapability}
        onCapabilityChange={
          setSelectedCapability
        }
        sources={sources}
        sourceCounts={sourceCounts}
        selectedSource={selectedSource}
        onSourceChange={setSelectedSource}
      />

      <main className="min-w-0 flex-1">
        <header className="border-b border-gray-200 bg-white">
          <div className="flex min-h-20 items-center justify-between gap-6 px-8">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Tender Dashboard
              </h1>

              <p className="mt-1 text-sm text-gray-500">
                Relevant government procurement
                opportunities
              </p>
            </div>

            <div className="text-sm text-gray-500">
              {loading
                ? "Loading..."
                  : `${sortedFilteredTenders.length} tenders`}
            </div>
          </div>
        </header>

        <section className="border-b border-gray-200 bg-white px-8 py-5">
          <div className="flex flex-col gap-4 xl:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />

              <input
                type="text"
                value={searchQuery}
                onChange={(event) =>
                  setSearchQuery(
                    event.target.value
                  )
                }
                placeholder="Search tenders, organizations, keywords..."
                className="h-11 w-full rounded-lg border border-gray-300 bg-white pl-10 pr-4 text-sm text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <div className="relative">
                <SlidersHorizontal className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />

                <select
                  value={selectedRelevance}
                  onChange={(event) =>
                    setSelectedRelevance(
                      event.target.value
                    )
                  }
                  className="h-11 min-w-40 appearance-none rounded-lg border border-gray-300 bg-white pl-10 pr-8 text-sm text-gray-700 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  <option value="All">
                    All Relevance
                  </option>

                  <option value="HIGH">
                    High
                  </option>

                  <option value="MEDIUM">
                    Medium
                  </option>

                  <option value="LOW">
                    Low
                  </option>
                </select>
              </div>

              <select
                value={selectedStatus}
                onChange={(event) =>
                  setSelectedStatus(
                    event.target.value
                  )
                }
                className="h-11 min-w-40 rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-700 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              >
                <option value="All Statuses">
                  All Statuses
                </option>

                {statuses.map((status) => (
                  <option
                    key={status}
                    value={status}
                  >
                    {status}
                  </option>
                ))}
              </select>

              {filtersActive && (
                <button
                  type="button"
                  onClick={clearFilters}
                  className="flex h-11 items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 text-sm font-medium text-gray-600 transition hover:border-gray-400 hover:bg-gray-50 hover:text-gray-900"
                >
                  <RotateCcw className="h-4 w-4" />
                  Clear
                </button>
              )}
            </div>
          </div>
        </section>

        <section className="px-8 py-6">
          {!loading && !error && (
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Showing{" "}
                <span className="font-medium text-gray-700">
                  {filteredTenders.length}
                </span>{" "}
                of{" "}
                <span className="font-medium text-gray-700">
                  {tenders.length}
                </span>{" "}
                tenders
              </p>
            </div>
          )}

          {loading && (
            <div className="rounded-xl border border-gray-200 bg-white px-6 py-16 text-center">
              <p className="text-sm text-gray-500">
                Loading tenders...
              </p>
            </div>
          )}

          {!loading && error && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-6 py-16 text-center">
              <h2 className="text-base font-semibold text-red-800">
                Unable to load tenders
              </h2>

              <p className="mt-2 text-sm text-red-600">
                {error}
              </p>
            </div>
          )}

          {!loading &&
            !error &&
            sortedFilteredTenders.length === 0 && (
              <div className="rounded-xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center">
                <h2 className="text-base font-semibold text-gray-900">
                  No tenders found
                </h2>

                <p className="mt-2 text-sm text-gray-500">
                  Try changing your search or
                  filters.
                </p>

                {filtersActive && (
                  <button
                    type="button"
                    onClick={clearFilters}
                    className="mt-5 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
                  >
                    <RotateCcw className="h-4 w-4" />
                    Clear Filters
                  </button>
                )}
              </div>
            )}

          {!loading &&
            !error &&
            sortedFilteredTenders.length > 0 && (
              <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white">
                <table className="min-w-full divide-y divide-gray-200 text-left">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Tender
                      </th>
                      <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Source
                      </th>
                      <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Capability
                      </th>
                      <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Advertised
                      </th>
                      <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Closing
                      </th>
                      <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Relevance
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-gray-100">
                    {sortedFilteredTenders.map((tender) => (
                      <tr
                        key={tender.id}
                        onClick={() =>
                          router.push(
                            `/tenders/${encodeURIComponent(
                              tender.id
                            )}`
                          )
                        }
                        className="cursor-pointer transition hover:bg-blue-50"
                      >
                        <td className="max-w-md px-5 py-4">
                          <p className="font-semibold text-gray-900">
                            {tender.title || "Untitled Tender"}
                          </p>
                          {tender.tender_number && (
                            <p className="mt-1 text-xs text-gray-500">
                              {tender.tender_number}
                            </p>
                          )}
                        </td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm text-gray-600">
                          {tender.source || "Unknown Source"}
                        </td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm text-gray-600">
                          {tender.relevance?.best_capability || "Unassigned"}
                        </td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm font-medium text-gray-700">
                          {tender.advertised_date || "-"}
                        </td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm text-gray-600">
                          {tender.closing_date || "-"}
                        </td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm font-semibold text-gray-700">
                          {tender.relevance?.classification || "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
        </section>
      </main>
    </div>
  );
}
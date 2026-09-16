"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  ExternalLink,
} from "lucide-react";
import type { ReactNode } from "react";

type Relevance = {
  final_score?: number;
  classification?: string;
  keyword_score?: number;
  semantic_score?: number;
  matched_keywords?: string[];
  matched_phrases?: string[];
  best_capability?: string | null;
  capability_matches?: {
    capability: string;
    score: number;
  }[];
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
  other?: Record<string, unknown>;
};

function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "—";
  }

  if (
    typeof value === "object" &&
    value !== null
  ) {
    try {
      return JSON.stringify(
        value,
        null,
        2
      );
    } catch {
      return "—";
    }
  }

  return String(value);
}

function FieldRow({
  label,
  value,
}: {
  label: string;
  value: ReactNode;
}) {
  return (
    <div className="grid grid-cols-[190px_20px_minmax(0,1fr)] border-b border-gray-100 py-4 last:border-b-0">
      <div className="text-sm font-semibold text-gray-700">
        {label}
      </div>

      <div className="text-sm font-semibold text-gray-400">
        :
      </div>

      <div className="min-w-0 whitespace-pre-wrap break-words text-sm leading-6 text-gray-600">
        {typeof value === "string" ||
        typeof value === "number" ? (
          value
        ) : (
          value
        )}
      </div>
    </div>
  );
}

function Value({
  value,
}: {
  value: unknown;
}) {
  return <>{formatValue(value)}</>;
}

export default function TenderDetailPage() {
  const params = useParams();
  const router = useRouter();

  const id = Array.isArray(params.id)
    ? params.id[0]
    : params.id;

  const [tender, setTender] =
    useState<Tender | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    async function loadTender() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          "/api/tenders"
        );

        if (!response.ok) {
          throw new Error(
            "Failed to fetch tender data."
          );
        }

        const data =
          await response.json();

        if (!Array.isArray(data)) {
          throw new Error(
            "Invalid tender data."
          );
        }

        const foundTender = data.find(
          (item: Tender) =>
            item.id === id
        );

        if (!foundTender) {
          setError("Tender not found.");
          return;
        }

        setTender(foundTender);
      } catch (err) {
        console.error(err);

        setError(
          "Unable to load tender details."
        );
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      loadTender();
    }
  }, [id]);

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50">
        <div className="mx-auto max-w-5xl px-8 py-10">
          <div className="rounded-xl border border-gray-200 bg-white px-6 py-16 text-center">
            <p className="text-sm text-gray-500">
              Loading tender details...
            </p>
          </div>
        </div>
      </main>
    );
  }

  if (error || !tender) {
    return (
      <main className="min-h-screen bg-gray-50">
        <div className="mx-auto max-w-5xl px-8 py-10">
          <button
            type="button"
            onClick={() => router.back()}
            className="mb-6 flex items-center gap-2 text-sm font-medium text-gray-600 transition hover:text-blue-600"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to tenders
          </button>

          <div className="rounded-xl border border-red-200 bg-red-50 px-6 py-16 text-center">
            <h1 className="text-base font-semibold text-red-800">
              Tender not found
            </h1>

            <p className="mt-2 text-sm text-red-600">
              {error ||
                "The requested tender could not be found."}
            </p>
          </div>
        </div>
      </main>
    );
  }

  const relevance =
    tender.relevance || {};

  const score =
    relevance.final_score ?? 0;

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-5xl px-8 py-5">
          <button
            type="button"
            onClick={() => router.back()}
            className="flex items-center gap-2 text-sm font-medium text-gray-600 transition hover:text-blue-600"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to tenders
          </button>
        </div>
      </header>

      {/* Main content */}
      <div className="mx-auto max-w-5xl px-8 py-8">
        <div className="rounded-xl border border-gray-200 bg-white px-8 py-7">

          {/* Tender Name */}
          <div className="mb-6 border-b border-gray-200 pb-6">
            <p className="mb-2 text-xs font-bold uppercase tracking-wider text-blue-600">
              Tender Name
            </p>

            <h1 className="text-2xl font-semibold leading-8 text-gray-900">
              {tender.title ||
                "Untitled Tender"}
            </h1>
          </div>

          {/* Tender Information */}
          <div>
            <FieldRow
              label="Capability"
              value={
                <Value
                  value={
                    relevance.best_capability
                  }
                />
              }
            />

            <FieldRow
              label="Publish Date"
              value={
                <Value
                  value={
                    tender.advertised_date
                  }
                />
              }
            />

            <FieldRow
              label="Closing Date"
              value={
                <Value
                  value={
                    tender.closing_date
                  }
                />
              }
            />

            <FieldRow
              label="Tender Number"
              value={
                <Value
                  value={
                    tender.tender_number
                  }
                />
              }
            />

            <FieldRow
              label="Organization"
              value={
                <Value
                  value={
                    tender.organization
                  }
                />
              }
            />

            <FieldRow
              label="Source"
              value={
                <Value
                  value={tender.source}
                />
              }
            />

            <FieldRow
              label="Status"
              value={
                <Value
                  value={tender.status}
                />
              }
            />
          </div>

          {/* Tender Details */}
          <div className="mt-8 border-t border-gray-200 pt-6">
            <p className="mb-1 text-xs font-bold uppercase tracking-wider text-blue-600">
              Tender Details
            </p>

            <div className="mt-3">
              <FieldRow
                label="Details"
                value={
                  <Value
                    value={tender.title}
                  />
                }
              />
            </div>
          </div>

          {/* Relevance */}
          <div className="mt-8 border-t border-gray-200 pt-6">
            <p className="mb-1 text-xs font-bold uppercase tracking-wider text-blue-600">
              Relevance
            </p>

            <div className="mt-3">
              <FieldRow
                label="Relevance Score"
                value={`${(
                  score * 100
                ).toFixed(1)}%`}
              />

              <FieldRow
                label="Classification"
                value={
                  relevance.classification ||
                  "—"
                }
              />

              <FieldRow
                label="Keyword Score"
                value={
                  relevance.keyword_score !==
                  undefined
                    ? `${(
                        relevance.keyword_score *
                        100
                      ).toFixed(1)}%`
                    : "—"
                }
              />

              <FieldRow
                label="Semantic Score"
                value={
                  relevance.semantic_score !==
                  undefined
                    ? `${(
                        relevance.semantic_score *
                        100
                      ).toFixed(1)}%`
                    : "—"
                }
              />

              <FieldRow
                label="Matched Keywords"
                value={
                  relevance.matched_keywords
                    ?.join(", ") || "—"
                }
              />

              <FieldRow
                label="Matched Phrases"
                value={
                  relevance.matched_phrases
                    ?.join(", ") || "—"
                }
              />
            </div>
          </div>

          {/* Other Details */}
          {tender.other &&
            Object.keys(tender.other)
              .length > 0 && (
              <div className="mt-8 border-t border-gray-200 pt-6">
                <p className="mb-1 text-xs font-bold uppercase tracking-wider text-blue-600">
                  Other Details
                </p>

                <div className="mt-3">
                  {Object.entries(
                    tender.other
                  ).map(
                    ([key, value]) => (
                      <FieldRow
                        key={key}
                        label={key
                          .replace(
                            /_/g,
                            " "
                          )
                          .replace(
                            /\b\w/g,
                            (char) =>
                              char.toUpperCase()
                          )}
                        value={
                          <Value
                            value={value}
                          />
                        }
                      />
                    )
                  )}
                </div>
              </div>
            )}

          {/* Original Tender */}
          {tender.tender_url && (
            <div className="mt-8 border-t border-gray-200 pt-6">
              <FieldRow
                label="Original Tender"
                value={
                  <a
                    href={
                      tender.tender_url
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 font-medium text-blue-600 hover:text-blue-700 hover:underline"
                  >
                    Open Tender
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                }
              />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
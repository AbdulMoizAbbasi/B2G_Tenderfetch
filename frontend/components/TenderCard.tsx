import {
  CalendarDays,
  ExternalLink,
  FileText,
  MapPin,
} from "lucide-react";

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

type TenderCardProps = {
  tender: Tender;
  onClick: () => void;
};

function getClassificationClasses(
  classification?: string
) {
  switch (classification) {
    case "HIGH":
      return "border-red-200 bg-red-50 text-red-700";

    case "MEDIUM":
      return "border-amber-200 bg-amber-50 text-amber-700";

    default:
      return "border-gray-200 bg-gray-50 text-gray-600";
  }
}

export default function TenderCard({
  tender,
  onClick,
}: TenderCardProps) {
  const classification =
    tender.relevance?.classification || "MEDIUM";

  const score =
    tender.relevance?.final_score ?? 0;

  const scorePercentage = score * 100;

  return (
    <article
      onClick={onClick}
      className="group cursor-pointer rounded-xl border border-gray-200 bg-white p-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-blue-300 hover:shadow-lg"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-5">
        <div className="min-w-0 flex-1">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center rounded-md bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
              {tender.source || "Unknown Source"}
            </span>

            <span
              className={`inline-flex items-center rounded-md border px-2.5 py-1 text-xs font-semibold ${getClassificationClasses(
                classification
              )}`}
            >
              {classification}
            </span>
          </div>

          <h3 className="line-clamp-2 text-[17px] font-semibold leading-6 text-gray-900 transition-colors group-hover:text-blue-700">
            {tender.title || "Untitled Tender"}
          </h3>
        </div>

        {/* Score */}
        <div className="shrink-0 text-right">
          <p className="text-[11px] font-medium uppercase tracking-wide text-gray-400">
            Relevance
          </p>

          <p className="mt-0.5 text-xl font-bold text-gray-900">
            {scorePercentage.toFixed(0)}%
          </p>
        </div>
      </div>

      {/* Tender number */}
      {tender.tender_number && (
        <div className="mt-5 flex items-center gap-2">
          <FileText className="h-4 w-4 shrink-0 text-gray-400" />

          <span className="text-sm font-medium text-gray-700">
            {tender.tender_number}
          </span>
        </div>
      )}

      {/* Organization */}
      {tender.organization && (
        <div className="mt-3 flex items-start gap-2">
          <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-gray-400" />

          <span className="line-clamp-2 text-sm leading-5 text-gray-600">
            {tender.organization}
          </span>
        </div>
      )}

      {/* Dates */}
      <div className="mt-5 grid gap-3 border-t border-gray-100 pt-4 sm:grid-cols-2">
        {tender.advertised_date && (
          <div>
            <div className="flex items-center gap-1.5 text-xs text-gray-400">
              <CalendarDays className="h-3.5 w-3.5" />
              <span>Published</span>
            </div>

            <p className="mt-1 text-sm font-medium text-gray-700">
              {tender.advertised_date}
            </p>
          </div>
        )}

        {tender.closing_date && (
          <div>
            <div className="flex items-center gap-1.5 text-xs text-gray-400">
              <CalendarDays className="h-3.5 w-3.5" />
              <span>Closing</span>
            </div>

            <p className="mt-1 text-sm font-semibold text-gray-800">
              {tender.closing_date}
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-5 flex min-h-8 items-center justify-between gap-4">
        <div className="min-w-0">
          {tender.relevance?.best_capability && (
            <span className="inline-flex max-w-full items-center truncate rounded-md bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600">
              {tender.relevance.best_capability}
            </span>
          )}
        </div>

        <div className="flex shrink-0 items-center gap-1.5 text-xs font-semibold text-blue-600 opacity-70 transition-all group-hover:translate-x-0.5 group-hover:opacity-100">
          <span>View details</span>
          <ExternalLink className="h-3.5 w-3.5" />
        </div>
      </div>
    </article>
  );
}
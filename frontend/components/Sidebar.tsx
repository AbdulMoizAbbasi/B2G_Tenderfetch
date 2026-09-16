"use client";

import {
  Filter,
  Globe,
  X,
} from "lucide-react";

type SidebarProps = {
  capabilities: string[];
  capabilityCounts: Record<string, number>;
  selectedCapability: string;
  onCapabilityChange: (capability: string) => void;

  sources: string[];
  sourceCounts: Record<string, number>;
  selectedSource: string;
  onSourceChange: (source: string) => void;
};

export default function Sidebar({
  capabilities,
  capabilityCounts,
  selectedCapability,
  onCapabilityChange,
  sources,
  sourceCounts,
  selectedSource,
  onSourceChange,
}: SidebarProps) {
  return (
    <aside className="w-72 shrink-0 border-r border-gray-200 bg-white">
      <div className="sticky top-0 h-screen overflow-y-auto">
        <div className="border-b border-gray-200 px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
              <Globe className="h-5 w-5 text-white" />
            </div>

            <div>
              <h2 className="text-sm font-semibold text-gray-900">
                Tender Intelligence
              </h2>

              <p className="text-xs text-gray-500">
                Procurement monitoring
              </p>
            </div>
          </div>
        </div>

        <div className="px-4 py-5">
          <div className="mb-3 px-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              Capabilities
            </p>
          </div>

          <div className="space-y-1">
            <button
              type="button"
              onClick={() =>
                onCapabilityChange("All Capabilities")
              }
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition ${
                selectedCapability === "All Capabilities"
                  ? "bg-blue-50 font-medium text-blue-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              <Filter
                className={`h-4 w-4 ${
                  selectedCapability ===
                  "All Capabilities"
                    ? "text-blue-600"
                    : "text-gray-400"
                }`}
              />

              <span>All Capabilities</span>

              <span className="ml-auto text-xs text-gray-400">
                {Object.values(capabilityCounts).reduce(
                  (total, count) => total + count,
                  0
                )}
              </span>
            </button>

            {capabilities.map((capability) => {
              const isSelected =
                selectedCapability === capability;

              return (
                <button
                  key={capability}
                  type="button"
                  onClick={() =>
                    onCapabilityChange(capability)
                  }
                  className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition ${
                    isSelected
                      ? "bg-blue-50 font-medium text-blue-700"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  }`}
                >
                  <span
                    className={`h-2 w-2 shrink-0 rounded-full ${
                      isSelected
                        ? "bg-blue-600"
                        : "bg-gray-300"
                    }`}
                  />

                  <span className="min-w-0 flex-1 truncate">
                    {capability}
                  </span>

                  <span
                    className={`text-xs ${
                      isSelected
                        ? "text-blue-600"
                        : "text-gray-400"
                    }`}
                  >
                    {capabilityCounts[capability] || 0}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="border-t border-gray-200 px-4 py-5">
          <div className="mb-3 px-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              Procurement Sources
            </p>
          </div>

          <div className="space-y-1">
            <button
              type="button"
              onClick={() =>
                onSourceChange("All Sources")
              }
              className={`flex w-full items-center rounded-lg px-3 py-2.5 text-left text-sm transition ${
                selectedSource === "All Sources"
                  ? "bg-gray-100 font-medium text-gray-900"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              <span className="flex-1">
                All Sources
              </span>

              <span className="text-xs text-gray-400">
                {Object.values(sourceCounts).reduce(
                  (total, count) => total + count,
                  0
                )}
              </span>
            </button>

            {sources.map((source) => {
              const isSelected =
                selectedSource === source;

              return (
                <button
                  key={source}
                  type="button"
                  onClick={() =>
                    onSourceChange(source)
                  }
                  className={`flex w-full items-center rounded-lg px-3 py-2.5 text-left text-sm transition ${
                    isSelected
                      ? "bg-gray-100 font-medium text-gray-900"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  }`}
                >
                  <span className="flex-1 truncate">
                    {source}
                  </span>

                  <span className="text-xs text-gray-400">
                    {sourceCounts[source] || 0}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="border-t border-gray-200 px-5 py-4">
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <X className="h-3.5 w-3.5" />

            <span>
              All loaded tenders included
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
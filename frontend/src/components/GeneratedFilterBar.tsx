"use client";

import React from "react";

import type { GeneratedJsonObject } from "../lib/api/client";
import {
  selectGeneratedFilterOption,
  type GeneratedFilterView,
} from "../lib/projections/screen-renderers";

export interface GeneratedFilterBarProps {
  readonly filters: readonly GeneratedFilterView[];
  readonly onFilterChange?: (filter: GeneratedJsonObject, option: GeneratedJsonObject) => void;
}

/** Renders server-defined filter choices and returns the original generated values on selection. */
export function GeneratedFilterBar({ filters, onFilterChange }: GeneratedFilterBarProps): JSX.Element | null {
  if (filters.length === 0) return null;
  return <section aria-label="Generated filters" className="generated-filter-bar">
    {filters.map((filter) => <label key={filter.id}>
      <span>{filter.label}</span>
      <select
        aria-label={filter.label}
        defaultValue={filter.options[0]?.value}
        disabled={onFilterChange === undefined}
        onChange={(event): void => {
          const option = selectGeneratedFilterOption(filter, event.currentTarget.value);
          if (option !== undefined) onFilterChange?.(filter.source, option);
        }}
      >
        {filter.options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
    </label>)}
  </section>;
}

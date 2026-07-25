import type {
  GeneratedActionReference,
  GeneratedJsonObject,
  GeneratedJsonValue,
} from "../api/client";

export type GeneratedOpaqueReference = GeneratedJsonObject;
export type GeneratedEvidenceReference = GeneratedJsonObject;

export interface ProjectionView<TField extends string = string> {
  readonly fields: Readonly<Partial<Record<TField, GeneratedJsonValue>>>;
}

export interface OpaqueReferenceView {
  readonly id: string;
  readonly label: string;
  readonly source: GeneratedOpaqueReference;
}

export interface ActionReferenceView extends OpaqueReferenceView {
  readonly eligible: boolean;
  readonly freshnessCritical?: boolean;
  readonly irreversible?: boolean;
  readonly kind?: string;
  readonly source: GeneratedActionReference;
}

export interface EvidenceReferenceView extends OpaqueReferenceView {
  readonly presentation: ProjectionView;
  readonly source: GeneratedEvidenceReference;
}

/** Maps generated projections into explicit, presence-only renderer inputs. */
export class ProjectionMapper {
  public map<TField extends string>(
    projection: GeneratedJsonObject,
    allowedFields: readonly TField[],
  ): ProjectionView<TField> {
    const fields: Partial<Record<TField, GeneratedJsonValue>> = {};
    for (const field of allowedFields) {
      const value = projection[field];
      if (Object.hasOwn(projection, field) && value !== undefined) fields[field] = value;
    }
    return { fields: Object.freeze(fields) };
  }

  public hasField<TField extends string>(
    projection: ProjectionView<TField>,
    field: TField,
  ): boolean {
    return Object.hasOwn(projection.fields, field);
  }

  public mapOpaqueReference(reference: GeneratedOpaqueReference): OpaqueReferenceView | null {
    const identity = mapReferenceIdentity(reference);
    return identity === null ? null : { ...identity, source: reference };
  }

  public mapActionReference(reference: GeneratedActionReference): ActionReferenceView | null {
    const identity = mapReferenceIdentity(reference);
    const eligible = optionalBoolean(reference.eligible);
    if (identity === null || eligible === undefined) return null;
    const freshnessCritical = optionalBoolean(reference.freshness_critical);
    const irreversible = optionalBoolean(reference.irreversible);
    const kind = optionalString(reference.kind);
    return {
      ...identity,
      eligible,
      ...(freshnessCritical === undefined ? {} : { freshnessCritical }),
      ...(irreversible === undefined ? {} : { irreversible }),
      ...(kind === undefined ? {} : { kind }),
      source: reference,
    };
  }

  public mapEvidenceReference<TField extends string>(
    reference: GeneratedEvidenceReference,
    presentationFields: readonly TField[],
  ): EvidenceReferenceView | null {
    const identity = mapReferenceIdentity(reference);
    return identity === null ? null : { ...identity, presentation: this.map(reference, presentationFields), source: reference };
  }
}

function mapReferenceIdentity(reference: GeneratedJsonObject): Pick<OpaqueReferenceView, "id" | "label"> | null {
  const id = optionalString(reference.id);
  const label = optionalString(reference.label);
  return id === undefined || label === undefined ? null : { id, label };
}

function optionalString(value: GeneratedJsonValue | undefined): string | undefined {
  return typeof value === "string" ? value : undefined;
}

function optionalBoolean(value: GeneratedJsonValue | undefined): boolean | undefined {
  return typeof value === "boolean" ? value : undefined;
}

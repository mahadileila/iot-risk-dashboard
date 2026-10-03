export interface FactorRating {
  factor_name: string;
  rating: number;
}

export interface DataSample {
  data_value: string;
  captured_at: string;
}

export interface RawAttributes {
  data_nature: string;
  identifiability_level: string;
  location_scope: string;
  collection_frequency: string;
  access_scope: string;
  sharing_scope: string;
}

export interface CollectionInstance {
  id_instance: string;
  data_description: string | null;
  normalized_score: number | null;
  classification: { label: string; color: string } | null;
  raw_attributes: RawAttributes;
  factor_ratings: FactorRating[];
  data_samples: DataSample[];
}
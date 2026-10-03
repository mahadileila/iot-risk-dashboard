export interface DashboardDeviceSummary {
  id_device: string;
  name: string;
  subsystem_name: string | null;
  active_instances_count?: number;
  normalized_score: number;
  classification: { label: string; color: string };
}

export interface SubsystemRisk {
  subsystem_name: string;
  average_score: number;
  classification: { label: string; color: string };
}

export interface DashboardSummary {
  total_devices: number;
  no_active_collection_count: number;
  subsystems_count: number;
  high_risk_devices_count: number;
  average_score: number;
  risk_by_subsystem: SubsystemRisk[];
  devices_requiring_attention: DashboardDeviceSummary[];
  devices_by_risk: DashboardDeviceSummary[];
}

export interface RiskTrendPoint {
  date: string;
  avg_score: number;
}

export interface Crime {
  id: string;
  type: 'furto' | 'assedio' | 'violencia_domestica' | 'outros';
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  date: string;
  time: string;
  victimGender: 'feminino' | 'masculino' | 'nao_informado';
  description?: string;
  reputation: number; // 1-5 stars
  isAnonymous: boolean;
  isCrowdsourced: boolean;
}

export interface Filter {
  timeRange: 'day' | 'week' | 'month' | 'custom';
  crimeTypes: string[];
  showCrowdsourced: boolean;
  customDateRange?: {
    start: Date;
    end: Date;
  };
}

export interface DenunciaForm {
  type: string;
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  victimGender: string;
  description: string;
}

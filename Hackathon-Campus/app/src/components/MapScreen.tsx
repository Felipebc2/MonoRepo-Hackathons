
import React, { useState } from 'react';
import { MapPin, Filter, X, Star, Clock, MapPinIcon } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Crime, Filter as FilterType } from '@/types';

// Mock data for demonstration
const mockCrimes: Crime[] = [
  {
    id: '1',
    type: 'furto',
    location: {
      latitude: -15.7797,
      longitude: -47.9297,
      address: 'Asa Norte, Brasília - DF'
    },
    date: '2024-06-18',
    time: '14:30',
    victimGender: 'feminino',
    description: 'Furto de celular próximo ao comércio local',
    reputation: 4,
    isAnonymous: true,
    isCrowdsourced: false
  },
  {
    id: '2',
    type: 'assedio',
    location: {
      latitude: -15.7747,
      longitude: -47.9337,
      address: 'SQN 110, Asa Norte - DF'
    },
    date: '2024-06-17',
    time: '20:15',
    victimGender: 'feminino',
    description: 'Assédio verbal em transporte público',
    reputation: 5,
    isAnonymous: true,
    isCrowdsourced: true
  }
];

const MapScreen = () => {
  const [selectedCrime, setSelectedCrime] = useState<Crime | null>(null);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [crimes] = useState<Crime[]>(mockCrimes);
  const [filter, setFilter] = useState<FilterType>({
    timeRange: 'week',
    crimeTypes: ['furto', 'assedio', 'violencia_domestica', 'outros'],
    showCrowdsourced: true
  });

  const getCrimeColor = (type: string) => {
    switch (type) {
      case 'furto': return 'bg-yellow-500';
      case 'assedio': return 'bg-red-500';
      case 'violencia_domestica': return 'bg-purple-600';
      default: return 'bg-gray-500';
    }
  };

  const getCrimeLabel = (type: string) => {
    switch (type) {
      case 'furto': return 'Furto';
      case 'assedio': return 'Assédio';
      case 'violencia_domestica': return 'Violência Doméstica';
      default: return 'Outros';
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        size={16}
        className={i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}
      />
    ));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-lg p-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">Mapa de Segurança</h1>
          <p className="text-sm text-gray-600">Asa Norte, Brasília - DF</p>
        </div>
        <Button
          onClick={() => setShowFilterModal(true)}
          className="bg-purple-600 hover:bg-purple-700"
        >
          <Filter size={20} />
        </Button>
      </div>

      {/* Map Container */}
      <div className="relative h-96 bg-gray-200 m-4 rounded-lg overflow-hidden shadow-lg">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-100 to-green-100 flex items-center justify-center">
          <div className="text-center">
            <MapPinIcon size={48} className="text-purple-600 mx-auto mb-2" />
            <p className="text-gray-700 font-medium">Mapa Interativo</p>
            <p className="text-sm text-gray-500">Região da Asa Norte</p>
          </div>
        </div>

        {/* Crime Markers */}
        {crimes.map((crime, index) => (
          <div
            key={crime.id}
            className={`absolute w-6 h-6 rounded-full ${getCrimeColor(crime.type)} 
                       border-2 border-white shadow-lg cursor-pointer transform hover:scale-110 
                       transition-transform duration-200`}
            style={{
              left: `${30 + index * 15}%`,
              top: `${40 + index * 10}%`
            }}
            onClick={() => setSelectedCrime(crime)}
          />
        ))}
      </div>

      {/* Legend */}
      <div className="mx-4 mb-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Legenda</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {[
                { type: 'furto', color: 'bg-yellow-500', label: 'Furto' },
                { type: 'assedio', color: 'bg-red-500', label: 'Assédio' },
                { type: 'violencia_domestica', color: 'bg-purple-600', label: 'Violência Doméstica' },
                { type: 'outros', color: 'bg-gray-500', label: 'Outros' }
              ].map((item) => (
                <div key={item.type} className="flex items-center space-x-2">
                  <div className={`w-4 h-4 rounded-full ${item.color}`} />
                  <span className="text-sm text-gray-700">{item.label}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Crime Details Modal */}
      {selectedCrime && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-end z-50">
          <div className="bg-white rounded-t-3xl p-6 min-h-96 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">
                {getCrimeLabel(selectedCrime.type)}
              </h2>
              <Button
                onClick={() => setSelectedCrime(null)}
                variant="ghost"
                size="sm"
              >
                <X size={20} />
              </Button>
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Clock size={16} className="text-gray-500" />
                <div className="text-gray-700">
                  {selectedCrime.date} às {selectedCrime.time}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <MapPin size={16} className="text-gray-500" />
                <div className="text-gray-700 flex-1">
                  {selectedCrime.location.address}
                </div>
              </div>

              <div>
                <div className="font-semibold text-gray-800 mb-2">Reputação da Denúncia</div>
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    {renderStars(selectedCrime.reputation)}
                  </div>
                  <div className="text-gray-600">
                    ({selectedCrime.reputation}/5)
                  </div>
                </div>
              </div>

              {selectedCrime.description && (
                <div>
                  <div className="font-semibold text-gray-800 mb-2">Descrição</div>
                  <div className="text-gray-700">{selectedCrime.description}</div>
                </div>
              )}

              <div className="flex space-x-2">
                {selectedCrime.isAnonymous && (
                  <Badge variant="secondary">Denúncia Anônima</Badge>
                )}
                {selectedCrime.isCrowdsourced && (
                  <Badge variant="outline">Validada pela Comunidade</Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filter Modal */}
      {showFilterModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Filtros</h2>
              <Button
                onClick={() => setShowFilterModal(false)}
                variant="ghost"
                size="sm"
              >
                <X size={20} />
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <div className="font-semibold mb-2">Período</div>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'day', label: '24h' },
                    { value: 'week', label: '7 dias' },
                    { value: 'month', label: '30 dias' },
                    { value: 'custom', label: 'Personalizado' }
                  ].map((option) => (
                    <Button
                      key={option.value}
                      variant={filter.timeRange === option.value ? "default" : "outline"}
                      className="text-sm"
                      onClick={() => setFilter({...filter, timeRange: option.value as any})}
                    >
                      {option.label}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <div className="font-semibold mb-2">Tipos de Crime</div>
                <div className="space-y-2">
                  {[
                    { value: 'furto', label: 'Furto' },
                    { value: 'assedio', label: 'Assédio' },
                    { value: 'violencia_domestica', label: 'Violência Doméstica' },
                    { value: 'outros', label: 'Outros' }
                  ].map((crime) => (
                    <div key={crime.value} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={filter.crimeTypes.includes(crime.value)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFilter({
                              ...filter,
                              crimeTypes: [...filter.crimeTypes, crime.value]
                            });
                          } else {
                            setFilter({
                              ...filter,
                              crimeTypes: filter.crimeTypes.filter(t => t !== crime.value)
                            });
                          }
                        }}
                        className="w-4 h-4"
                      />
                      <div className="text-gray-700">{crime.label}</div>
                    </div>
                  ))}
                </div>
              </div>

              <Button
                onClick={() => setShowFilterModal(false)}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                Aplicar Filtros
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapScreen;

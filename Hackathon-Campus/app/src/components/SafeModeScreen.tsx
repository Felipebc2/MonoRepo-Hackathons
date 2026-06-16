
import React, { useState } from 'react';
import { Shield, Map, AlertTriangle, Phone } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface SafeModeScreenProps {
  onNavigateToMap: () => void;
  onNavigateToDenuncia: () => void;
}

const SafeModeScreen: React.FC<SafeModeScreenProps> = ({
  onNavigateToMap,
  onNavigateToDenuncia
}) => {
  const handleEmergencyCall = (number: string) => {
    if (window.confirm(`Deseja ligar para ${number}?`)) {
      alert(`Conectando... Ligando para ${number}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 via-60% to-purple-900 p-4 font-sans">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <div className="p-2 bg-white/10 rounded-2xl backdrop-blur-sm animate-glow">
            <Shield className="text-white" size={28} />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-white tracking-tight">Modo Seguro</h1>
            <p className="text-purple-200 text-sm font-light">Protegida e conectada</p>
          </div>
        </div>
      </div>

      {/* Status Card */}
      <Card className="mb-8 bg-white/5 border-white/10 backdrop-blur-md shadow-xl rounded-2xl">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-white font-medium text-lg">Status de Segurança</div>
              <div className="text-green-300 text-sm font-light">Sistema ativo</div>
            </div>
            <Badge className="bg-green-500/20 text-green-300 border-green-500/30 px-4 py-2 rounded-full font-medium">
              Protegida
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Main Actions */}
      <div className="space-y-6 mb-8">
        <Button
          onClick={onNavigateToMap}
          className="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 py-6 text-lg rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]"
        >
          <div className="flex items-center space-x-4">
            <div className="p-2 bg-white/20 rounded-xl">
              <Map size={24} />
            </div>
            <div className="text-left">
              <div className="font-semibold text-white">Mapa de Segurança</div>
              <div className="text-purple-200 text-sm font-light">Ver ocorrências na região</div>
            </div>
          </div>
        </Button>

        <Button
          onClick={onNavigateToDenuncia}
          className="w-full bg-gradient-to-r from-pink-600 to-pink-700 hover:from-pink-700 hover:to-pink-800 py-6 text-lg rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]"
        >
          <div className="flex items-center space-x-4">
            <div className="p-2 bg-white/20 rounded-xl">
              <AlertTriangle size={24} />
            </div>
            <div className="text-left">
              <div className="font-semibold text-white">Nova Denúncia</div>
              <div className="text-pink-200 text-sm font-light">Reportar ocorrência anônima</div>
            </div>
          </div>
        </Button>
      </div>

      {/* Emergency Section */}
      <Card className="bg-red-900/10 border-red-500/20 backdrop-blur-md rounded-2xl shadow-xl">
        <CardHeader>
          <CardTitle className="text-red-300 flex items-center space-x-3 text-lg">
            <div className="p-2 bg-red-500/20 rounded-xl">
              <Phone size={20} />
            </div>
            <span>Emergência</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Button
              onClick={() => handleEmergencyCall('190')}
              variant="destructive"
              className="bg-red-600/80 hover:bg-red-600 border-0 rounded-xl py-4 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
            >
              <div className="text-center">
                <div className="font-bold text-white text-lg">190</div>
                <div className="text-xs text-red-200 font-light">Polícia</div>
              </div>
            </Button>
            
            <Button
              onClick={() => handleEmergencyCall('180')}
              variant="destructive"
              className="bg-red-600/80 hover:bg-red-600 border-0 rounded-xl py-4 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
            >
              <div className="text-center">
                <div className="font-bold text-white text-lg">180</div>
                <div className="text-xs text-red-200 font-light">Mulher</div>
              </div>
            </Button>
            
            <Button
              onClick={() => handleEmergencyCall('192')}
              variant="destructive"
              className="bg-red-600/80 hover:bg-red-600 border-0 rounded-xl py-4 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
            >
              <div className="text-center">
                <div className="font-bold text-white text-lg">192</div>
                <div className="text-xs text-red-200 font-light">SAMU</div>
              </div>
            </Button>
            
            <Button
              onClick={() => handleEmergencyCall('193')}
              variant="destructive"
              className="bg-red-600/80 hover:bg-red-600 border-0 rounded-xl py-4 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
            >
              <div className="text-center">
                <div className="font-bold text-white text-lg">193</div>
                <div className="text-xs text-red-200 font-light">Bombeiros</div>
              </div>
            </Button>
          </div>
          
          <p className="text-red-300 text-xs text-center font-light">
            Toque duas vezes rapidamente em qualquer botão para ligar imediatamente
          </p>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="mt-8 grid grid-cols-3 gap-4">
        <Card className="bg-white/5 border-white/10 backdrop-blur-md rounded-xl shadow-lg">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-white">24</div>
            <div className="text-xs text-purple-200 font-light">Ocorrências esta semana</div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/5 border-white/10 backdrop-blur-md rounded-xl shadow-lg">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-white">89%</div>
            <div className="text-xs text-purple-200 font-light">Área segura</div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/5 border-white/10 backdrop-blur-md rounded-xl shadow-lg">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-white">127</div>
            <div className="text-xs text-purple-200 font-light">Usuárias ativas</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SafeModeScreen;

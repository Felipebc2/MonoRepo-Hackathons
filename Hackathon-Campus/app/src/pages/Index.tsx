
import React, { useState } from 'react';
import SafeModeScreen from '@/components/SafeModeScreen';
import MapScreen from '@/components/MapScreen';
import DenunciaScreen from '@/components/DenunciaScreen';
import { Home, Map, AlertTriangle } from 'lucide-react';

type AppScreen = 'safe-mode' | 'map' | 'denuncia';

const Index = () => {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>('safe-mode');

  const renderScreen = () => {
    switch (currentScreen) {
      case 'safe-mode':
        return (
          <SafeModeScreen
            onNavigateToMap={() => setCurrentScreen('map')}
            onNavigateToDenuncia={() => setCurrentScreen('denuncia')}
          />
        );
      case 'map':
        return <MapScreen />;
      case 'denuncia':
        return <DenunciaScreen />;
      default:
        return (
          <SafeModeScreen
            onNavigateToMap={() => setCurrentScreen('map')}
            onNavigateToDenuncia={() => setCurrentScreen('denuncia')}
          />
        );
    }
  };

  return (
    <div className="min-h-screen font-sans">
      {renderScreen()}
      
      {/* Navigation Bar */}
      {(currentScreen === 'map' || currentScreen === 'denuncia') && (
        <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-gray-200/50 px-6 py-3 shadow-lg">
          <div className="flex justify-around max-w-md mx-auto">
            <button
              onClick={() => setCurrentScreen('safe-mode')}
              className="flex flex-col items-center py-3 px-4 text-gray-600 hover:text-purple-600 transition-all duration-200 transform hover:scale-105"
            >
              <div className={`p-2 rounded-2xl mb-1 transition-all duration-200 ${
                currentScreen === 'safe-mode' 
                  ? 'bg-purple-600 text-white shadow-lg' 
                  : 'bg-gray-100 text-gray-600'
              }`}>
                <Home size={20} />
              </div>
              <span className="text-xs font-medium">Início</span>
            </button>
            
            <button
              onClick={() => setCurrentScreen('map')}
              className={`flex flex-col items-center py-3 px-4 transition-all duration-200 transform hover:scale-105 ${
                currentScreen === 'map' ? 'text-purple-600' : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              <div className={`p-2 rounded-2xl mb-1 transition-all duration-200 ${
                currentScreen === 'map' 
                  ? 'bg-purple-600 text-white shadow-lg' 
                  : 'bg-gray-100 text-gray-600'
              }`}>
                <Map size={20} />
              </div>
              <span className="text-xs font-medium">Mapa</span>
            </button>
            
            <button
              onClick={() => setCurrentScreen('denuncia')}
              className={`flex flex-col items-center py-3 px-4 transition-all duration-200 transform hover:scale-105 ${
                currentScreen === 'denuncia' ? 'text-purple-600' : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              <div className={`p-2 rounded-2xl mb-1 transition-all duration-200 ${
                currentScreen === 'denuncia' 
                  ? 'bg-purple-600 text-white shadow-lg' 
                  : 'bg-gray-100 text-gray-600'
              }`}>
                <AlertTriangle size={20} />
              </div>
              <span className="text-xs font-medium">Denúncia</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Index;

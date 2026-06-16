
import React, { useState } from 'react';
import { MapPin, Send } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { DenunciaForm } from '@/types';

const DenunciaScreen = () => {
  const [form, setForm] = useState<DenunciaForm>({
    type: '',
    location: {
      latitude: -15.7797,
      longitude: -47.9297,
      address: ''
    },
    victimGender: '',
    description: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleLocationPress = () => {
    // Simulate getting current location
    setForm({
      ...form,
      location: {
        ...form.location,
        address: 'Asa Norte, Brasília - DF (Localização Atual)'
      }
    });
  };

  const handleSubmit = async () => {
    if (!form.type || !form.victimGender) {
      alert('Por favor, preencha os campos obrigatórios.');
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      if (window.confirm('Sua denúncia foi enviada com sucesso e será analisada pela comunidade.')) {
        // Reset form
        setForm({
          type: '',
          location: {
            latitude: -15.7797,
            longitude: -47.9297,
            address: ''
          },
          victimGender: '',
          description: ''
        });
      }
    } catch (error) {
      alert('Não foi possível enviar a denúncia. Tente novamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 p-4">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Nova Denúncia</h1>
        <p className="text-gray-600">Reporte de forma anônima e segura</p>
      </div>

      {/* Form */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg text-purple-700">Informações da Ocorrência</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Crime Type */}
          <div>
            <Label htmlFor="crime-type" className="text-sm font-semibold text-gray-700">
              Tipo de Crime *
            </Label>
            <Select value={form.type} onValueChange={(value) => setForm({...form, type: value})}>
              <SelectTrigger className="w-full mt-1">
                <SelectValue placeholder="Selecione o tipo de crime" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="furto">Furto</SelectItem>
                <SelectItem value="assedio">Assédio</SelectItem>
                <SelectItem value="violencia_domestica">Violência Doméstica</SelectItem>
                <SelectItem value="outros">Outros</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Location */}
          <div>
            <Label className="text-sm font-semibold text-gray-700">Localização</Label>
            <div className="flex space-x-2 mt-1">
              <Input
                value={form.location.address}
                onChange={(e) => setForm({
                  ...form,
                  location: {...form.location, address: e.target.value}
                })}
                placeholder="Digite o endereço ou use localização atual"
                className="flex-1"
              />
              <Button
                onClick={handleLocationPress}
                variant="outline"
                className="px-3"
              >
                <MapPin size={16} />
              </Button>
            </div>
          </div>

          {/* Victim Gender */}
          <div>
            <Label className="text-sm font-semibold text-gray-700">
              Sexo da Vítima *
            </Label>
            <Select value={form.victimGender} onValueChange={(value) => setForm({...form, victimGender: value})}>
              <SelectTrigger className="w-full mt-1">
                <SelectValue placeholder="Selecione" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="feminino">Feminino</SelectItem>
                <SelectItem value="masculino">Masculino</SelectItem>
                <SelectItem value="nao_informado">Prefiro não informar</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Description */}
          <div>
            <Label htmlFor="description" className="text-sm font-semibold text-gray-700">
              Descrição (Opcional)
            </Label>
            <Textarea
              id="description"
              value={form.description}
              onChange={(e) => setForm({...form, description: e.target.value})}
              placeholder="Descreva brevemente o que aconteceu..."
              className="mt-1 min-h-24"
              maxLength={500}
            />
            <p className="text-xs text-gray-500 mt-1">
              {form.description.length}/500 caracteres
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Notice */}
      <Card className="mb-6 border-blue-200 bg-blue-50">
        <CardContent className="p-4">
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-blue-800 mb-1">Sua privacidade está protegida</h3>
              <p className="text-sm text-blue-700">
                Esta denúncia é completamente anônima. Nenhuma informação pessoal será armazenada 
                ou compartilhada. A localização é aproximada para preservar sua segurança.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Submit Button */}
      <Button
        onClick={handleSubmit}
        disabled={isSubmitting}
        className="w-full bg-purple-600 hover:bg-purple-700 py-3 text-lg font-semibold"
      >
        {isSubmitting ? (
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            <span>Enviando...</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2">
            <Send size={20} />
            <span>Enviar Denúncia</span>
          </div>
        )}
      </Button>

      {/* Emergency Button */}
      <Card className="mt-6 border-red-200 bg-red-50">
        <CardContent className="p-4">
          <div className="text-center">
            <h3 className="font-semibold text-red-800 mb-2">Emergência?</h3>
            <p className="text-sm text-red-700 mb-3">
              Se você está em perigo imediato, ligue agora:
            </p>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="destructive"
                className="font-bold"
                onClick={() => alert('Conectando com 190...')}
              >
                190 - Polícia
              </Button>
              <Button
                variant="destructive"
                className="font-bold"
                onClick={() => alert('Conectando com 180...')}
              >
                180 - Mulher
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DenunciaScreen;

# Desafio: Digits

## Descrição

Desafio matemático onde é necessário gerar expressões usando apenas um dígito específico (0-9) para representar um número alvo. Por exemplo, usar apenas o dígito `7` para formar expressões que resultem em valores como `42`, `100`, etc.

## Abordagem

O script utiliza:
- Geração de expressões usando apenas um dígito repetido
- Operações matemáticas básicas (+, -, *, /)
- Concatenação de dígitos para formar números maiores
- Comunicação via socket com o servidor

## Arquivos

- `digits_solver.py`: Solver principal que gera expressões com um único dígito
- `digits_dificil.py`: Versão para desafios mais difíceis

## Solução

O algoritmo:
1. Conecta ao servidor e aguarda o enunciado
2. Recebe o dígito permitido e o número alvo
3. Gera expressões usando apenas aquele dígito através de:
   - Concatenação (ex: `77` = dois setes)
   - Operações básicas (ex: `7+7+7+7+7+7` = 42)
   - Frações quando necessário
4. Envia a expressão e aguarda confirmação
5. Repete para múltiplos desafios

A chave está em gerar eficientemente expressões válidas usando apenas um dígito, o que requer criatividade matemática e otimização de busca.

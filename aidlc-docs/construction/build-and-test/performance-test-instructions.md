# Performance Test Instructions

## Status: N/A para as histórias #14 e #16

Conforme `requirements.md` (Non-Functional Requirements) e `execution-plan.md` (NFR Requirements marcado SKIP), essas histórias não definem metas de performance/carga próprias — são telas de CRUD simples adicionadas a um projeto acadêmico sem infraestrutura de produção definida (sem load balancer, sem auto-scaling, sem ambiente de carga configurado no repositório). A extensão Resiliency Baseline foi escopada apenas às regras de nível de código de aplicação (ver `requirements.md`), e nenhuma delas exige teste de performance formal para essas mudanças.

## Se testes de performance vierem a ser necessários no futuro (referência)

### Performance Requirements (a definir com o time, se aplicável)
- **Response Time**: não definido
- **Throughput**: não definido
- **Concurrent Users**: não definido
- **Error Rate**: não definido

### Sugestão de abordagem leve (opcional, fora do escopo desta história)
```bash
# Exemplo com uma ferramenta simples, caso o time decida medir no futuro:
# ab -n 100 -c 10 http://localhost:8000/doacoes/nova/
```

## Overall Status desta história
- **Performance Tests**: N/A — não aplicável a uma única tela de formulário CRUD sem metas de NFR definidas

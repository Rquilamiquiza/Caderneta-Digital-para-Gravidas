from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import json
from .models import Gravida, Consulta, Exame
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
    GravidaSerializer,
    ConsultaSerializer,
    ExameSerializer
)

def index(request):
    """View para a página inicial"""
    return render(request, 'caderneta/index.html')

# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Registro de novo usuário"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Usuário criado com sucesso',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login de usuário"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login realizado com sucesso',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout de usuário"""
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout realizado com sucesso'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Perfil do usuário autenticado"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_joined': user.date_joined,
    })

# Gravidas Views (com autenticação)
class GravidaListCreateView(generics.ListCreateAPIView):
    serializer_class = GravidaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Gravida.objects.all()

class GravidaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GravidaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Gravida.objects.all()

# Consultas Views (com autenticação)
class ConsultaListCreateView(generics.ListCreateAPIView):
    serializer_class = ConsultaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        gravida_id = self.kwargs['gravida_id']
        return Consulta.objects.filter(gravida_id=gravida_id)

    def perform_create(self, serializer):
        gravida_id = self.kwargs['gravida_id']
        gravida = get_object_or_404(Gravida, id=gravida_id)
        serializer.save(gravida=gravida)

# Exames Views (com autenticação)
class ExameListCreateView(generics.ListCreateAPIView):
    serializer_class = ExameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        gravida_id = self.kwargs['gravida_id']
        return Exame.objects.filter(gravida_id=gravida_id)

    def perform_create(self, serializer):
        gravida_id = self.kwargs['gravida_id']
        gravida = get_object_or_404(Gravida, id=gravida_id)
        serializer.save(gravida=gravida)

# Views antigas (mantidas para compatibilidade)
@csrf_exempt
def api_gravidas_list(request):
    """API para listar todas as grávidas ou criar uma nova"""
    if request.method == 'GET':
        gravidas = Gravida.objects.all()
        data = []
        for gravida in gravidas:
            gravida_dict = model_to_dict(gravida)
            # Converter datas para string para serialização JSON
            gravida_dict['data_nascimento'] = gravida.data_nascimento.strftime('%Y-%m-%d')
            gravida_dict['data_ultima_menstruacao'] = gravida.data_ultima_menstruacao.strftime('%Y-%m-%d')
            gravida_dict['data_provavel_parto'] = gravida.data_provavel_parto.strftime('%Y-%m-%d') if gravida.data_provavel_parto else None
            gravida_dict['data_cadastro'] = gravida.data_cadastro.strftime('%Y-%m-%d %H:%M:%S')
            data.append(gravida_dict)
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            gravida = Gravida.objects.create(
                nome=data['nome'],
                data_nascimento=data['data_nascimento'],
                cpf=data['cpf'],
                endereco=data['endereco'],
                telefone=data['telefone'],
                email=data.get('email'),
                data_ultima_menstruacao=data['data_ultima_menstruacao']
            )
            return JsonResponse({'status': 'success', 'id': gravida.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def api_gravida_detail(request, gravida_id):
    """API para obter, atualizar ou excluir uma grávida específica"""
    gravida = get_object_or_404(Gravida, id=gravida_id)
    
    if request.method == 'GET':
        gravida_dict = model_to_dict(gravida)
        # Converter datas para string para serialização JSON
        gravida_dict['data_nascimento'] = gravida.data_nascimento.strftime('%Y-%m-%d')
        gravida_dict['data_ultima_menstruacao'] = gravida.data_ultima_menstruacao.strftime('%Y-%m-%d')
        gravida_dict['data_provavel_parto'] = gravida.data_provavel_parto.strftime('%Y-%m-%d') if gravida.data_provavel_parto else None
        gravida_dict['data_cadastro'] = gravida.data_cadastro.strftime('%Y-%m-%d %H:%M:%S')
        return JsonResponse(gravida_dict)
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            gravida.nome = data.get('nome', gravida.nome)
            gravida.data_nascimento = data.get('data_nascimento', gravida.data_nascimento)
            gravida.cpf = data.get('cpf', gravida.cpf)
            gravida.endereco = data.get('endereco', gravida.endereco)
            gravida.telefone = data.get('telefone', gravida.telefone)
            gravida.email = data.get('email', gravida.email)
            gravida.data_ultima_menstruacao = data.get('data_ultima_menstruacao', gravida.data_ultima_menstruacao)
            gravida.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    elif request.method == 'DELETE':
        gravida.delete()
        return JsonResponse({'status': 'success'})

@csrf_exempt
def api_consultas_list(request, gravida_id):
    """API para listar todas as consultas de uma grávida ou criar uma nova"""
    gravida = get_object_or_404(Gravida, id=gravida_id)
    
    if request.method == 'GET':
        consultas = Consulta.objects.filter(gravida=gravida)
        data = []
        for consulta in consultas:
            consulta_dict = model_to_dict(consulta)
            consulta_dict['data'] = consulta.data.strftime('%Y-%m-%d')
            consulta_dict['data_registro'] = consulta.data_registro.strftime('%Y-%m-%d %H:%M:%S')
            data.append(consulta_dict)
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            consulta = Consulta.objects.create(
                gravida=gravida,
                data=data['data'],
                local=data['local'],
                profissional=data['profissional'],
                peso=data['peso'],
                pressao_arterial=data['pressao_arterial'],
                altura_uterina=data.get('altura_uterina'),
                batimentos_cardiacos_fetais=data.get('batimentos_cardiacos_fetais'),
                observacoes=data.get('observacoes')
            )
            return JsonResponse({'status': 'success', 'id': consulta.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def api_exames_list(request, gravida_id):
    """API para listar todos os exames de uma grávida ou criar um novo"""
    gravida = get_object_or_404(Gravida, id=gravida_id)
    
    if request.method == 'GET':
        exames = Exame.objects.filter(gravida=gravida)
        data = []
        for exame in exames:
            exame_dict = model_to_dict(exame)
            exame_dict['data'] = exame.data.strftime('%Y-%m-%d')
            exame_dict['data_registro'] = exame.data_registro.strftime('%Y-%m-%d %H:%M:%S')
            data.append(exame_dict)
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            exame = Exame.objects.create(
                gravida=gravida,
                data=data['data'],
                tipo=data['tipo'],
                resultado=data['resultado']
            )
            return JsonResponse({'status': 'success', 'id': exame.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# Relatórios Views
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relatorio_estatisticas_gerais(request):
    """Relatório com estatísticas gerais do sistema"""
    try:
        # Estatísticas básicas
        total_gravidas = Gravida.objects.count()
        total_consultas = Consulta.objects.count()
        total_exames = Exame.objects.count()
        
        # Estatísticas por mês (últimos 6 meses)
        hoje = timezone.now().date()
        seis_meses_atras = hoje - timedelta(days=180)
        
        gravidas_por_mes = []
        consultas_por_mes = []
        exames_por_mes = []
        
        for i in range(6):
            inicio_mes = hoje.replace(day=1) - timedelta(days=30*i)
            fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            gravidas_mes = Gravida.objects.filter(
                data_cadastro__date__gte=inicio_mes,
                data_cadastro__date__lte=fim_mes
            ).count()
            
            consultas_mes = Consulta.objects.filter(
                data__gte=inicio_mes,
                data__lte=fim_mes
            ).count()
            
            exames_mes = Exame.objects.filter(
                data__gte=inicio_mes,
                data__lte=fim_mes
            ).count()
            
            gravidas_por_mes.append({
                'mes': inicio_mes.strftime('%Y-%m'),
                'total': gravidas_mes
            })
            
            consultas_por_mes.append({
                'mes': inicio_mes.strftime('%Y-%m'),
                'total': consultas_mes
            })
            
            exames_por_mes.append({
                'mes': inicio_mes.strftime('%Y-%m'),
                'total': exames_mes
            })
        
        # Estatísticas de consultas
        media_consultas_por_gravida = Consulta.objects.values('gravida').annotate(
            total=Count('id')
        ).aggregate(media=Avg('total'))['media'] or 0
        
        # Tipos de exames mais comuns
        tipos_exames = Exame.objects.values('tipo').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        # Grávidas com partos próximos (próximos 30 dias)
        proximos_30_dias = hoje + timedelta(days=30)
        partos_proximos = Gravida.objects.filter(
            data_provavel_parto__gte=hoje,
            data_provavel_parto__lte=proximos_30_dias
        ).count()
        
        return Response({
            'estatisticas_gerais': {
                'total_gravidas': total_gravidas,
                'total_consultas': total_consultas,
                'total_exames': total_exames,
                'media_consultas_por_gravida': round(media_consultas_por_gravida, 2),
                'partos_proximos_30_dias': partos_proximos
            },
            'tendencias': {
                'gravidas_por_mes': list(reversed(gravidas_por_mes)),
                'consultas_por_mes': list(reversed(consultas_por_mes)),
                'exames_por_mes': list(reversed(exames_por_mes))
            },
            'tipos_exames_mais_comuns': list(tipos_exames),
            'data_geracao': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relatorio_gravidas_por_periodo(request):
    """Relatório de grávidas cadastradas por período"""
    try:
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        
        if not data_inicio or not data_fim:
            # Se não especificado, usar últimos 30 dias
            hoje = timezone.now().date()
            data_fim = hoje
            data_inicio = hoje - timedelta(days=30)
        else:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        gravidas = Gravida.objects.filter(
            data_cadastro__date__gte=data_inicio,
            data_cadastro__date__lte=data_fim
        ).order_by('-data_cadastro')
        
        # Estatísticas do período
        total_periodo = gravidas.count()
        
        # Grávidas por dia
        gravidas_por_dia = gravidas.extra(
            select={'dia': 'date(data_cadastro)'}
        ).values('dia').annotate(
            total=Count('id')
        ).order_by('dia')
        
        # Idades das grávidas
        idades = []
        for gravida in gravidas:
            idade = (timezone.now().date() - gravida.data_nascimento).days // 365
            idades.append(idade)
        
        idade_media = sum(idades) / len(idades) if idades else 0
        idade_min = min(idades) if idades else 0
        idade_max = max(idades) if idades else 0
        
        return Response({
            'periodo': {
                'data_inicio': data_inicio.isoformat(),
                'data_fim': data_fim.isoformat()
            },
            'estatisticas': {
                'total_gravidas': total_periodo,
                'idade_media': round(idade_media, 1),
                'idade_minima': idade_min,
                'idade_maxima': idade_max
            },
            'gravidas_por_dia': list(gravidas_por_dia),
            'gravidas': [
                {
                    'id': g.id,
                    'nome': g.nome,
                    'data_nascimento': g.data_nascimento.isoformat(),
                    'data_cadastro': g.data_cadastro.isoformat(),
                    'data_provavel_parto': g.data_provavel_parto.isoformat() if g.data_provavel_parto else None
                }
                for g in gravidas
            ]
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relatorio_consultas_por_periodo(request):
    """Relatório de consultas realizadas por período"""
    try:
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        
        if not data_inicio or not data_fim:
            # Se não especificado, usar últimos 30 dias
            hoje = timezone.now().date()
            data_fim = hoje
            data_inicio = hoje - timedelta(days=30)
        else:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        consultas = Consulta.objects.filter(
            data__gte=data_inicio,
            data__lte=data_fim
        ).select_related('gravida').order_by('-data')
        
        # Estatísticas do período
        total_consultas = consultas.count()
        
        # Consultas por profissional
        consultas_por_profissional = consultas.values('profissional').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Consultas por local
        consultas_por_local = consultas.values('local').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Peso médio por mês de gestação (aproximado)
        pesos = []
        for consulta in consultas:
            if consulta.peso:
                pesos.append(float(consulta.peso))
        
        peso_medio = sum(pesos) / len(pesos) if pesos else 0
        
        return Response({
            'periodo': {
                'data_inicio': data_inicio.isoformat(),
                'data_fim': data_fim.isoformat()
            },
            'estatisticas': {
                'total_consultas': total_consultas,
                'peso_medio': round(peso_medio, 2),
                'consultas_por_profissional': list(consultas_por_profissional),
                'consultas_por_local': list(consultas_por_local)
            },
            'consultas': [
                {
                    'id': c.id,
                    'gravida_nome': c.gravida.nome,
                    'data': c.data.isoformat(),
                    'profissional': c.profissional,
                    'local': c.local,
                    'peso': float(c.peso) if c.peso else None,
                    'pressao_arterial': c.pressao_arterial
                }
                for c in consultas[:100]  # Limitar a 100 registros
            ]
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relatorio_exames_por_tipo(request):
    """Relatório de exames agrupados por tipo"""
    try:
        # Exames por tipo
        exames_por_tipo = Exame.objects.values('tipo').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Exames dos últimos 30 dias
        hoje = timezone.now().date()
        trinta_dias_atras = hoje - timedelta(days=30)
        
        exames_recentes = Exame.objects.filter(
            data__gte=trinta_dias_atras
        ).values('tipo').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Detalhes por tipo
        detalhes_por_tipo = {}
        for tipo_info in exames_por_tipo:
            tipo = tipo_info['tipo']
            exames_tipo = Exame.objects.filter(tipo=tipo).select_related('gravida')
            
            detalhes_por_tipo[tipo] = {
                'total': tipo_info['total'],
                'exames_recentes': [
                    {
                        'id': e.id,
                        'gravida_nome': e.gravida.nome,
                        'data': e.data.isoformat(),
                        'resultado': e.resultado[:100] + '...' if len(e.resultado) > 100 else e.resultado
                    }
                    for e in exames_tipo.order_by('-data')[:5]
                ]
            }
        
        return Response({
            'resumo': {
                'total_tipos': len(exames_por_tipo),
                'total_exames': sum(item['total'] for item in exames_por_tipo)
            },
            'exames_por_tipo': list(exames_por_tipo),
            'exames_recentes_por_tipo': list(exames_recentes),
            'detalhes_por_tipo': detalhes_por_tipo
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relatorio_partos_proximos(request):
    """Relatório de partos previstos para os próximos dias"""
    try:
        dias = int(request.GET.get('dias', 30))  # Padrão: próximos 30 dias
        
        hoje = timezone.now().date()
        data_limite = hoje + timedelta(days=dias)
        
        gravidas_parto_proximo = Gravida.objects.filter(
            data_provavel_parto__gte=hoje,
            data_provavel_parto__lte=data_limite
        ).order_by('data_provavel_parto')
        
        # Agrupar por semana
        partos_por_semana = {}
        for gravida in gravidas_parto_proximo:
            # Calcular semana do ano
            semana = gravida.data_provavel_parto.isocalendar()[1]
            ano = gravida.data_provavel_parto.year
            chave_semana = f"{ano}-W{semana:02d}"
            
            if chave_semana not in partos_por_semana:
                partos_por_semana[chave_semana] = []
            
            # Calcular idade gestacional aproximada
            semanas_gestacao = (gravida.data_provavel_parto - gravida.data_ultima_menstruacao).days // 7
            
            partos_por_semana[chave_semana].append({
                'id': gravida.id,
                'nome': gravida.nome,
                'data_provavel_parto': gravida.data_provavel_parto.isoformat(),
                'telefone': gravida.telefone,
                'email': gravida.email,
                'semanas_gestacao_atual': semanas_gestacao,
                'dias_para_parto': (gravida.data_provavel_parto - hoje).days
            })
        
        return Response({
            'periodo': {
                'data_inicio': hoje.isoformat(),
                'data_fim': data_limite.isoformat(),
                'dias': dias
            },
            'estatisticas': {
                'total_partos_previstos': gravidas_parto_proximo.count(),
                'partos_esta_semana': len([g for g in gravidas_parto_proximo if (g.data_provavel_parto - hoje).days <= 7]),
                'partos_proximo_mes': len([g for g in gravidas_parto_proximo if (g.data_provavel_parto - hoje).days <= 30])
            },
            'partos_por_semana': partos_por_semana,
            'lista_completa': [
                {
                    'id': g.id,
                    'nome': g.nome,
                    'data_provavel_parto': g.data_provavel_parto.isoformat(),
                    'telefone': g.telefone,
                    'email': g.email,
                    'dias_para_parto': (g.data_provavel_parto - hoje).days
                }
                for g in gravidas_parto_proximo
            ]
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Views para a página da grávida
from .models import PaginaGravida, ConsultaAgendada, ControleGestacao, LembreteGravida
from .serializers import (
    PaginaGravidaSerializer, 
    PaginaGravidaDetailSerializer,
    ConsultaAgendadaSerializer,
    ControleGestacaoSerializer,
    LembreteGravidaSerializer
)
from django.utils import timezone
from datetime import datetime, timedelta

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def pagina_gravida_view(request):
    """View para gerenciar a página da grávida"""
    try:
        # Tenta encontrar a página da grávida para o usuário atual
        pagina_gravida = PaginaGravida.objects.get(usuario=request.user)
    except PaginaGravida.DoesNotExist:
        if request.method == 'POST':
            # Se não existe, cria uma nova associação
            gravida_id = request.data.get('gravida_id')
            if not gravida_id:
                return Response({'error': 'gravida_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                gravida = Gravida.objects.get(id=gravida_id)
                pagina_gravida = PaginaGravida.objects.create(
                    gravida=gravida,
                    usuario=request.user
                )
            except Gravida.DoesNotExist:
                return Response({'error': 'Grávida não encontrada'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Página da grávida não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PaginaGravidaDetailSerializer(pagina_gravida)
        return Response(serializer.data)
    
    return Response({'message': 'Página da grávida criada com sucesso'}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def consultas_agendadas_view(request):
    """View para gerenciar consultas agendadas"""
    try:
        pagina_gravida = PaginaGravida.objects.get(usuario=request.user)
    except PaginaGravida.DoesNotExist:
        return Response({'error': 'Página da grávida não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        consultas = ConsultaAgendada.objects.filter(pagina_gravida=pagina_gravida)
        
        # Filtros opcionais
        status_filter = request.GET.get('status')
        if status_filter:
            consultas = consultas.filter(status=status_filter)
        
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        if data_inicio and data_fim:
            consultas = consultas.filter(
                data_consulta__date__gte=data_inicio,
                data_consulta__date__lte=data_fim
            )
        
        serializer = ConsultaAgendadaSerializer(consultas, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ConsultaAgendadaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(pagina_gravida=pagina_gravida)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def consulta_agendada_detail_view(request, consulta_id):
    """View para detalhes de uma consulta específica"""
    try:
        pagina_gravida = PaginaGravida.objects.get(usuario=request.user)
        consulta = ConsultaAgendada.objects.get(id=consulta_id, pagina_gravida=pagina_gravida)
    except (PaginaGravida.DoesNotExist, ConsultaAgendada.DoesNotExist):
        return Response({'error': 'Consulta não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ConsultaAgendadaSerializer(consulta)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ConsultaAgendadaSerializer(consulta, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        consulta.delete()
        return Response({'message': 'Consulta excluída com sucesso'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def controle_gestacao_view(request):
    """View para gerenciar controles de gestação"""
    try:
        pagina_gravida = PaginaGravida.objects.get(usuario=request.user)
    except PaginaGravida.DoesNotExist:
        return Response({'error': 'Página da grávida não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        controles = ControleGestacao.objects.filter(pagina_gravida=pagina_gravida)
        
        # Filtros opcionais
        tipo_filter = request.GET.get('tipo')
        if tipo_filter:
            controles = controles.filter(tipo_registro=tipo_filter)
        
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        if data_inicio and data_fim:
            controles = controles.filter(
                data_registro__date__gte=data_inicio,
                data_registro__date__lte=data_fim
            )
        
        serializer = ControleGestacaoSerializer(controles, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ControleGestacaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(pagina_gravida=pagina_gravida)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def controle_gestacao_detail_view(request, controle_id):
    """View para detalhes de um controle específico"""
    try:
        pagina_gravida = PaginaGravida.objects.get(usuario=request.user)
        controle = ControleGestacao.objects.get(id=controle_id, pagina_gravida=pagina_gravida)
    except (PaginaGravida.DoesNotExist, ControleGestacao.DoesNotExist):
        return Response({'error': 'Controle não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ControleGestacaoSerializer(controle)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ControleGestacaoSerializer(controle, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        controle.delete()
        return Response({'message': 'Controle excluído com sucesso'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lembretes_view(request):
    """View para gerenciar lembretes"""
    try:
        pagina_gravida = PaginaGravida.objects.get(usuario=request.user)
    except PaginaGravida.DoesNotExist:
        return Response({'error': 'Página da grávida não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        lembretes = LembreteGravida.objects.filter(pagina_gravida=pagina_gravida)
        
        # Filtros opcionais
        ativo_filter = request.GET.get('ativo')
        if ativo_filter is not None:
            lembretes = lembretes.filter(ativo=ativo_filter.lower() == 'true')
        
        concluido_filter = request.GET.get('concluido')
        if concluido_filter is not None:
            lembretes = lembretes.filter(concluido=concluido_filter.lower() == 'true')
        
        serializer = LembreteGravidaSerializer(lembretes, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = LembreteGravidaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(pagina_gravida=pagina_gravida)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def lembrete_detail_view(request, lembrete_id):
    """View para detalhes de um lembrete específico"""
    try:
        pagina_gravida = PaginaGravida.objects.get(usuario=request.user)
        lembrete = LembreteGravida.objects.get(id=lembrete_id, pagina_gravida=pagina_gravida)
    except (PaginaGravida.DoesNotExist, LembreteGravida.DoesNotExist):
        return Response({'error': 'Lembrete não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = LembreteGravidaSerializer(lembrete)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = LembreteGravidaSerializer(lembrete, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        lembrete.delete()
        return Response({'message': 'Lembrete excluído com sucesso'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_gravida_view(request):
    """View para o dashboard da grávida com informações resumidas"""
    try:
        pagina_gravida = PaginaGravida.objects.get(usuario=request.user)
    except PaginaGravida.DoesNotExist:
        return Response({'error': 'Página da grávida não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    hoje = timezone.now().date()
    proximos_7_dias = hoje + timedelta(days=7)
    
    # Estatísticas do dashboard
    dashboard_data = {
        'gravida': {
            'nome': pagina_gravida.gravida.nome,
            'data_provavel_parto': pagina_gravida.gravida.data_provavel_parto,
            'semanas_gestacao': None,  # Calcular baseado na DUM
        },
        'consultas': {
            'total_agendadas': pagina_gravida.consultas_agendadas.filter(
                status__in=['agendada', 'confirmada']
            ).count(),
            'proxima_consulta': None,
            'consultas_proximos_7_dias': pagina_gravida.consultas_agendadas.filter(
                data_consulta__date__gte=hoje,
                data_consulta__date__lte=proximos_7_dias,
                status__in=['agendada', 'confirmada']
            ).count(),
        },
        'lembretes': {
            'total_pendentes': pagina_gravida.lembretes.filter(
                ativo=True, 
                concluido=False
            ).count(),
            'lembretes_hoje': pagina_gravida.lembretes.filter(
                data_lembrete__date=hoje,
                ativo=True,
                concluido=False
            ).count(),
        },
        'controles': {
            'total_registros': pagina_gravida.controles_gestacao.count(),
            'ultimo_peso': None,
            'ultima_pressao': None,
        }
    }
    
    # Calcular semanas de gestação
    if pagina_gravida.gravida.data_ultima_menstruacao:
        dias_gestacao = (hoje - pagina_gravida.gravida.data_ultima_menstruacao).days
        semanas_gestacao = dias_gestacao // 7
        dashboard_data['gravida']['semanas_gestacao'] = semanas_gestacao
    
    # Próxima consulta
    proxima_consulta = pagina_gravida.consultas_agendadas.filter(
        data_consulta__gte=timezone.now(),
        status__in=['agendada', 'confirmada']
    ).first()
    if proxima_consulta:
        dashboard_data['consultas']['proxima_consulta'] = ConsultaAgendadaSerializer(proxima_consulta).data
    
    # Último peso registrado
    ultimo_peso = pagina_gravida.controles_gestacao.filter(
        tipo_registro='peso'
    ).first()
    if ultimo_peso:
        dashboard_data['controles']['ultimo_peso'] = {
            'valor': ultimo_peso.valor_numerico,
            'unidade': ultimo_peso.unidade,
            'data': ultimo_peso.data_registro
        }
    
    # Última pressão registrada
    ultima_pressao = pagina_gravida.controles_gestacao.filter(
        tipo_registro='pressao'
    ).first()
    if ultima_pressao:
        dashboard_data['controles']['ultima_pressao'] = {
            'valor': ultima_pressao.descricao,
            'data': ultima_pressao.data_registro
        }
    
    return Response(dashboard_data)


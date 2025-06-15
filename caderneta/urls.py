from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # Authentication URLs
    path('api/auth/register/', views.register_user, name='register'),
    path('api/auth/login/', views.login_user, name='login'),
    path('api/auth/logout/', views.logout_user, name='logout'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', views.user_profile, name='user_profile'),
    
    # Relatórios URLs
    path('api/relatorios/estatisticas-gerais/', views.relatorio_estatisticas_gerais, name='relatorio_estatisticas_gerais'),
    path('api/relatorios/gravidas-por-periodo/', views.relatorio_gravidas_por_periodo, name='relatorio_gravidas_por_periodo'),
    path('api/relatorios/consultas-por-periodo/', views.relatorio_consultas_por_periodo, name='relatorio_consultas_por_periodo'),
    path('api/relatorios/exames-por-tipo/', views.relatorio_exames_por_tipo, name='relatorio_exames_por_tipo'),
    path('api/relatorios/partos-proximos/', views.relatorio_partos_proximos, name='relatorio_partos_proximos'),
    
    # API URLs com autenticação (novas)
    path('api/v2/gravidas/', views.GravidaListCreateView.as_view(), name='api_v2_gravidas_list'),
    path('api/v2/gravidas/<int:pk>/', views.GravidaDetailView.as_view(), name='api_v2_gravida_detail'),
    path('api/v2/gravidas/<int:gravida_id>/consultas/', views.ConsultaListCreateView.as_view(), name='api_v2_consultas_list'),
    path('api/v2/gravidas/<int:gravida_id>/exames/', views.ExameListCreateView.as_view(), name='api_v2_exames_list'),
    
    # API URLs antigas (mantidas para compatibilidade)
    path('api/gravidas/', views.api_gravidas_list, name='api_gravidas_list'),
    path('api/gravidas/<int:gravida_id>/', views.api_gravida_detail, name='api_gravida_detail'),
    path('api/gravidas/<int:gravida_id>/consultas/', views.api_consultas_list, name='api_consultas_list'),
    path('api/gravidas/<int:gravida_id>/exames/', views.api_exames_list, name='api_exames_list'),
    
    # URLs para a página da grávida
    path('api/pagina-gravida/', views.pagina_gravida_view, name='pagina_gravida'),
    path('api/pagina-gravida/dashboard/', views.dashboard_gravida_view, name='dashboard_gravida'),
    
    # URLs para consultas agendadas
    path('api/pagina-gravida/consultas/', views.consultas_agendadas_view, name='consultas_agendadas'),
    path('api/pagina-gravida/consultas/<int:consulta_id>/', views.consulta_agendada_detail_view, name='consulta_agendada_detail'),
    
    # URLs para controle de gestação
    path('api/pagina-gravida/controles/', views.controle_gestacao_view, name='controle_gestacao'),
    path('api/pagina-gravida/controles/<int:controle_id>/', views.controle_gestacao_detail_view, name='controle_gestacao_detail'),
    
    # URLs para lembretes
    path('api/pagina-gravida/lembretes/', views.lembretes_view, name='lembretes'),
    path('api/pagina-gravida/lembretes/<int:lembrete_id>/', views.lembrete_detail_view, name='lembrete_detail'),
]


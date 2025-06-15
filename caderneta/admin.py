from django.contrib import admin
from .models import Gravida, Consulta, Exame

@admin.register(Gravida)
class GravidaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'data_ultima_menstruacao', 'data_provavel_parto')
    search_fields = ('nome', 'cpf')

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('gravida', 'data', 'local', 'profissional')
    list_filter = ('data', 'local')
    search_fields = ('gravida__nome', 'profissional')

@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    list_display = ('gravida', 'data', 'tipo')
    list_filter = ('data', 'tipo')
    search_fields = ('gravida__nome', 'tipo')


# Admin para os novos modelos da página da grávida
from .models import PaginaGravida, ConsultaAgendada, ControleGestacao, LembreteGravida

@admin.register(PaginaGravida)
class PaginaGravidaAdmin(admin.ModelAdmin):
    list_display = ('gravida', 'usuario', 'data_criacao')
    search_fields = ('gravida__nome', 'usuario__username')
    list_filter = ('data_criacao',)

@admin.register(ConsultaAgendada)
class ConsultaAgendadaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'pagina_gravida', 'data_consulta', 'tipo_consulta', 'status')
    list_filter = ('tipo_consulta', 'status', 'data_consulta')
    search_fields = ('titulo', 'pagina_gravida__gravida__nome', 'local', 'profissional')
    date_hierarchy = 'data_consulta'

@admin.register(ControleGestacao)
class ControleGestacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'pagina_gravida', 'tipo_registro', 'data_registro', 'importante')
    list_filter = ('tipo_registro', 'importante', 'data_registro')
    search_fields = ('titulo', 'pagina_gravida__gravida__nome', 'descricao')
    date_hierarchy = 'data_registro'

@admin.register(LembreteGravida)
class LembreteGravidaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'pagina_gravida', 'tipo_lembrete', 'data_lembrete', 'ativo', 'concluido')
    list_filter = ('tipo_lembrete', 'ativo', 'concluido', 'data_lembrete')
    search_fields = ('titulo', 'pagina_gravida__gravida__nome', 'descricao')
    date_hierarchy = 'data_lembrete'


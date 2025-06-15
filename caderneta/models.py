from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Gravida(models.Model):
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=20, unique=True, verbose_name="Número do BI")
    endereco = models.TextField()
    telefone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    data_ultima_menstruacao = models.DateField()
    data_provavel_parto = models.DateField(blank=True, null=True)
    data_cadastro = models.DateTimeField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        # Cálculo da data provável do parto (DPP) - 40 semanas após a DUM
        if self.data_ultima_menstruacao and not self.data_provavel_parto:
            from datetime import timedelta
            self.data_provavel_parto = self.data_ultima_menstruacao + timedelta(days=280)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nome

class Consulta(models.Model):
    gravida = models.ForeignKey(Gravida, on_delete=models.CASCADE, related_name='consultas')
    data = models.DateField()
    local = models.CharField(max_length=100)
    profissional = models.CharField(max_length=100)
    peso = models.DecimalField(max_digits=5, decimal_places=2)  # em kg
    pressao_arterial = models.CharField(max_length=10)  # formato: 120/80
    altura_uterina = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)  # em cm
    batimentos_cardiacos_fetais = models.IntegerField(blank=True, null=True)  # em bpm
    observacoes = models.TextField(blank=True, null=True)
    data_registro = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Consulta de {self.gravida.nome} em {self.data}"

class Exame(models.Model):
    gravida = models.ForeignKey(Gravida, on_delete=models.CASCADE, related_name='exames')
    data = models.DateField()
    tipo = models.CharField(max_length=100)
    resultado = models.TextField()
    data_registro = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Exame {self.tipo} de {self.gravida.nome} em {self.data}"


# Novos modelos para a página da grávida
class PaginaGravida(models.Model):
    """Modelo para armazenar informações específicas da página da grávida"""
    gravida = models.OneToOneField(Gravida, on_delete=models.CASCADE, related_name='pagina_gravida')
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pagina_gravida')
    data_criacao = models.DateTimeField(default=timezone.now)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Página de {self.gravida.nome}"

class ConsultaAgendada(models.Model):
    """Modelo para consultas agendadas pela grávida"""
    TIPO_CONSULTA_CHOICES = [
        ('prenatal', 'Pré-natal'),
        ('ultrassom', 'Ultrassom'),
        ('exame', 'Exame'),
        ('emergencia', 'Emergência'),
        ('rotina', 'Consulta de Rotina'),
    ]
    
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('confirmada', 'Confirmada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('remarcada', 'Remarcada'),
    ]
    
    pagina_gravida = models.ForeignKey(PaginaGravida, on_delete=models.CASCADE, related_name='consultas_agendadas')
    titulo = models.CharField(max_length=200)
    tipo_consulta = models.CharField(max_length=20, choices=TIPO_CONSULTA_CHOICES, default='prenatal')
    data_consulta = models.DateTimeField()
    local = models.CharField(max_length=200)
    profissional = models.CharField(max_length=100, blank=True, null=True)
    telefone_contato = models.CharField(max_length=15, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendada')
    lembrete_enviado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(default=timezone.now)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['data_consulta']
    
    def __str__(self):
        return f"{self.titulo} - {self.data_consulta.strftime('%d/%m/%Y %H:%M')}"

class ControleGestacao(models.Model):
    """Modelo para informações de controle da gestação registradas pela grávida"""
    TIPO_REGISTRO_CHOICES = [
        ('peso', 'Peso'),
        ('pressao', 'Pressão Arterial'),
        ('sintomas', 'Sintomas'),
        ('medicamentos', 'Medicamentos'),
        ('alimentacao', 'Alimentação'),
        ('exercicios', 'Exercícios'),
        ('humor', 'Humor/Bem-estar'),
        ('movimento_fetal', 'Movimento Fetal'),
        ('outros', 'Outros'),
    ]
    
    pagina_gravida = models.ForeignKey(PaginaGravida, on_delete=models.CASCADE, related_name='controles_gestacao')
    tipo_registro = models.CharField(max_length=20, choices=TIPO_REGISTRO_CHOICES)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    valor_numerico = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Para peso, pressão, etc.
    unidade = models.CharField(max_length=20, blank=True, null=True)  # kg, mmHg, etc.
    data_registro = models.DateTimeField()
    importante = models.BooleanField(default=False)  # Para marcar registros importantes
    data_criacao = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-data_registro']
    
    def __str__(self):
        return f"{self.titulo} - {self.data_registro.strftime('%d/%m/%Y')}"

class LembreteGravida(models.Model):
    """Modelo para lembretes personalizados da grávida"""
    TIPO_LEMBRETE_CHOICES = [
        ('medicamento', 'Medicamento'),
        ('consulta', 'Consulta'),
        ('exame', 'Exame'),
        ('exercicio', 'Exercício'),
        ('alimentacao', 'Alimentação'),
        ('vitamina', 'Vitamina/Suplemento'),
        ('outros', 'Outros'),
    ]
    
    pagina_gravida = models.ForeignKey(PaginaGravida, on_delete=models.CASCADE, related_name='lembretes')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    tipo_lembrete = models.CharField(max_length=20, choices=TIPO_LEMBRETE_CHOICES, default='outros')
    data_lembrete = models.DateTimeField()
    repetir = models.BooleanField(default=False)
    intervalo_repeticao = models.IntegerField(blank=True, null=True)  # em horas
    ativo = models.BooleanField(default=True)
    concluido = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['data_lembrete']
    
    def __str__(self):
        return f"{self.titulo} - {self.data_lembrete.strftime('%d/%m/%Y %H:%M')}"


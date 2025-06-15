from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Gravida, Consulta, Exame

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Credenciais inválidas.')
            if not user.is_active:
                raise serializers.ValidationError('Conta de usuário desativada.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Deve incluir "username" e "password".')

class GravidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gravida
        fields = '__all__'

class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = '__all__'

class ExameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exame
        fields = '__all__'


# Serializers para os novos modelos da página da grávida
from .models import PaginaGravida, ConsultaAgendada, ControleGestacao, LembreteGravida

class PaginaGravidaSerializer(serializers.ModelSerializer):
    gravida_nome = serializers.CharField(source='gravida.nome', read_only=True)
    gravida_data_provavel_parto = serializers.DateField(source='gravida.data_provavel_parto', read_only=True)
    
    class Meta:
        model = PaginaGravida
        fields = '__all__'
        read_only_fields = ('usuario', 'data_criacao', 'data_atualizacao')

class ConsultaAgendadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultaAgendada
        fields = '__all__'
        read_only_fields = ('pagina_gravida', 'data_criacao', 'data_atualizacao')

class ControleGestacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControleGestacao
        fields = '__all__'
        read_only_fields = ('pagina_gravida', 'data_criacao')

class LembreteGravidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LembreteGravida
        fields = '__all__'
        read_only_fields = ('pagina_gravida', 'data_criacao')

class PaginaGravidaDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado com informações relacionadas"""
    gravida = GravidaSerializer(read_only=True)
    consultas_agendadas = ConsultaAgendadaSerializer(many=True, read_only=True)
    controles_gestacao = ControleGestacaoSerializer(many=True, read_only=True)
    lembretes = LembreteGravidaSerializer(many=True, read_only=True)
    
    # Estatísticas úteis
    total_consultas_agendadas = serializers.SerializerMethodField()
    proxima_consulta = serializers.SerializerMethodField()
    lembretes_pendentes = serializers.SerializerMethodField()
    
    class Meta:
        model = PaginaGravida
        fields = '__all__'
    
    def get_total_consultas_agendadas(self, obj):
        return obj.consultas_agendadas.filter(status__in=['agendada', 'confirmada']).count()
    
    def get_proxima_consulta(self, obj):
        from django.utils import timezone
        proxima = obj.consultas_agendadas.filter(
            data_consulta__gte=timezone.now(),
            status__in=['agendada', 'confirmada']
        ).first()
        if proxima:
            return ConsultaAgendadaSerializer(proxima).data
        return None
    
    def get_lembretes_pendentes(self, obj):
        return obj.lembretes.filter(ativo=True, concluido=False).count()


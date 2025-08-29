"""
Serviço de Importação e Exportação de Planilhas
"""
import pandas as pd
import json
from datetime import datetime, date
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from models.sales_models import Cliente, Contrato, ContaAdicional, ImportLog
import logging

logger = logging.getLogger(__name__)

class ImportExportService:
    def __init__(self):
        pass
    
    def import_from_excel(self, file_path: str, db: Session, user_id: str) -> Dict[str, Any]:
        """Importar dados de planilha Excel/CSV"""
        try:
            # Ler planilha
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            else:
                df = pd.read_excel(file_path)
            
            logger.info(f"Planilha carregada: {len(df)} linhas")
            
            # Mapear colunas da planilha para o modelo
            column_mapping = {
                'CustId': 'cust_id',
                'Nickname': 'nickname', 
                'Nome principal': 'nome_principal',
                'Status': 'status',
                'Tempo': 'tempo_ativo',
                'Inicio': 'data_inicio',
                'Valor': 'valor_mensal',
                'Final': 'data_final',
                'Dias a Vencer': 'dias_a_vencer',
                'Status do Contrato': 'status_contrato',
                'Ciclo': 'ciclo_atual',
                'Duração Ciclo 1': 'duracao_ciclo_1',
                'Duração Ciclo 2': 'duracao_ciclo_2', 
                'Duração Ciclo 3': 'duracao_ciclo_3',
                'Duração Ciclo 4': 'duracao_ciclo_4',
                'Duração Ciclo 5': 'duracao_ciclo_5',
                'Jornada Iniciada': 'jornada_iniciada',
                'LTV': 'ltv_meses',
                'LTV $': 'ltv_valor',
                'DATA ATUAL': 'data_atual'
            }
            
            # Renomear colunas
            df = df.rename(columns=column_mapping)
            
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Processar cada linha
                    cliente_data = self._process_row(row, index)
                    
                    if cliente_data:
                        self._save_cliente(cliente_data, db)
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f"Linha {index + 1}: Dados insuficientes")
                        
                except Exception as e:
                    error_count += 1
                    errors.append(f"Linha {index + 1}: {str(e)}")
                    logger.error(f"Erro ao processar linha {index + 1}: {e}")
            
            # Salvar log da importação
            import_log = ImportLog(
                filename=file_path.split('/')[-1],
                total_rows=len(df),
                success_rows=success_count,
                error_rows=error_count,
                user_id=user_id,
                status="success" if error_count == 0 else ("partial" if success_count > 0 else "error"),
                errors_detail=json.dumps(errors) if errors else None
            )
            
            db.add(import_log)
            db.commit()
            
            return {
                "success": True,
                "total_rows": len(df),
                "success_rows": success_count,
                "error_rows": error_count,
                "errors": errors,
                "import_id": import_log.id
            }
            
        except Exception as e:
            logger.error(f"Erro na importação: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_rows": 0,
                "success_rows": 0,
                "error_rows": 0
            }
    
    def _process_row(self, row: pd.Series, index: int) -> Dict[str, Any]:
        """Processar uma linha da planilha"""
        try:
            # Verificar se tem dados mínimos necessários
            if pd.isna(row.get('cust_id')) and pd.isna(row.get('nickname')):
                return None
            
            # Processar valores monetários
            valor_mensal = self._parse_money(row.get('valor_mensal'))
            ltv_valor = self._parse_money(row.get('ltv_valor'))
            
            # Processar datas
            data_inicio = self._parse_date(row.get('data_inicio'))
            data_final = self._parse_date(row.get('data_final'))
            jornada_iniciada = self._parse_date(row.get('jornada_iniciada'))
            data_atual = self._parse_date(row.get('data_atual'))
            
            # Detectar plataforma
            plataforma = "ML"  # Default
            if "shopee" in str(row.get('nickname', '')).lower():
                plataforma = "Shopee"
            
            cliente_data = {
                'cust_id': str(row.get('cust_id', '')).strip() if not pd.isna(row.get('cust_id')) else None,
                'nickname': str(row.get('nickname', '')).strip() if not pd.isna(row.get('nickname')) else None,
                'nome_principal': str(row.get('nome_principal', '')).strip() if not pd.isna(row.get('nome_principal')) else None,
                'status': str(row.get('status', '')).strip() if not pd.isna(row.get('status')) else None,
                'tempo_ativo': int(row.get('tempo_ativo', 0)) if not pd.isna(row.get('tempo_ativo')) else None,
                'data_inicio': data_inicio,
                'jornada_iniciada': jornada_iniciada,
                'ltv_meses': int(row.get('ltv_meses', 0)) if not pd.isna(row.get('ltv_meses')) else None,
                'ltv_valor': ltv_valor,
                'data_atual': data_atual,
                'contrato': {
                    'plataforma': plataforma,
                    'valor_mensal': valor_mensal,
                    'data_inicio': data_inicio,
                    'data_final': data_final,
                    'dias_a_vencer': int(row.get('dias_a_vencer', 0)) if not pd.isna(row.get('dias_a_vencer')) else None,
                    'status_contrato': str(row.get('status_contrato', '')).strip() if not pd.isna(row.get('status_contrato')) else None,
                    'ciclo_atual': str(row.get('ciclo_atual', '')).strip() if not pd.isna(row.get('ciclo_atual')) else None,
                    'duracao_ciclo_1': int(row.get('duracao_ciclo_1', 0)) if not pd.isna(row.get('duracao_ciclo_1')) else None,
                    'duracao_ciclo_2': int(row.get('duracao_ciclo_2', 0)) if not pd.isna(row.get('duracao_ciclo_2')) else None,
                    'duracao_ciclo_3': int(row.get('duracao_ciclo_3', 0)) if not pd.isna(row.get('duracao_ciclo_3')) else None,
                    'duracao_ciclo_4': int(row.get('duracao_ciclo_4', 0)) if not pd.isna(row.get('duracao_ciclo_4')) else None,
                    'duracao_ciclo_5': int(row.get('duracao_ciclo_5', 0)) if not pd.isna(row.get('duracao_ciclo_5')) else None,
                }
            }
            
            return cliente_data
            
        except Exception as e:
            logger.error(f"Erro ao processar linha {index + 1}: {e}")
            raise e
    
    def _parse_money(self, value) -> float:
        """Converter string de dinheiro para float"""
        if pd.isna(value):
            return None
        
        value_str = str(value).replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            return float(value_str)
        except:
            return None
    
    def _parse_date(self, value) -> date:
        """Converter string para data"""
        if pd.isna(value):
            return None
        
        try:
            if isinstance(value, (date, datetime)):
                return value.date() if isinstance(value, datetime) else value
            
            value_str = str(value).strip()
            if not value_str or value_str == '-':
                return None
            
            # Tentar diferentes formatos
            formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']
            
            for fmt in formats:
                try:
                    return datetime.strptime(value_str, fmt).date()
                except:
                    continue
            
            return None
        except:
            return None
    
    def _save_cliente(self, cliente_data: Dict[str, Any], db: Session):
        """Salvar cliente no banco"""
        try:
            # Verificar se cliente já existe
            existing_cliente = None
            if cliente_data['cust_id']:
                existing_cliente = db.query(Cliente).filter_by(cust_id=cliente_data['cust_id']).first()
            
            if existing_cliente:
                # Atualizar cliente existente
                for key, value in cliente_data.items():
                    if key != 'contrato' and value is not None:
                        setattr(existing_cliente, key, value)
                existing_cliente.updated_at = datetime.utcnow()
                cliente = existing_cliente
            else:
                # Criar novo cliente
                cliente = Cliente(**{k: v for k, v in cliente_data.items() if k != 'contrato'})
                db.add(cliente)
                db.flush()  # Para obter o ID
            
            # Salvar contrato se tiver dados
            contrato_data = cliente_data.get('contrato')
            if contrato_data and contrato_data.get('valor_mensal'):
                contrato = Contrato(
                    cliente_id=cliente.id,
                    **contrato_data
                )
                db.add(contrato)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao salvar cliente: {e}")
            raise e
    
    def export_to_excel(self, db: Session, filters: Dict[str, Any] = None) -> str:
        """Exportar dados para Excel"""
        try:
            # Query base
            query = db.query(Cliente).join(Contrato, isouter=True)
            
            # Aplicar filtros
            if filters:
                if filters.get('status'):
                    query = query.filter(Cliente.status == filters['status'])
                if filters.get('data_inicio'):
                    query = query.filter(Cliente.data_inicio >= filters['data_inicio'])
                if filters.get('data_final'):
                    query = query.filter(Cliente.data_inicio <= filters['data_final'])
            
            clientes = query.all()
            
            # Preparar dados para export
            export_data = []
            for cliente in clientes:
                for contrato in cliente.contratos or [None]:
                    row = {
                        'CustId': cliente.cust_id,
                        'Nickname': cliente.nickname,
                        'Nome principal': cliente.nome_principal,
                        'Status': cliente.status,
                        'Tempo': cliente.tempo_ativo,
                        'Inicio': cliente.data_inicio.strftime('%d/%m/%Y') if cliente.data_inicio else '',
                        'Valor': f"R$ {contrato.valor_mensal:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if contrato and contrato.valor_mensal else '',
                        'Final': contrato.data_final.strftime('%d/%m/%Y') if contrato and contrato.data_final else '',
                        'Dias a Vencer': contrato.dias_a_vencer if contrato else '',
                        'Status do Contrato': contrato.status_contrato if contrato else '',
                        'Ciclo': contrato.ciclo_atual if contrato else '',
                        'Duração Ciclo 1': contrato.duracao_ciclo_1 if contrato else '',
                        'Duração Ciclo 2': contrato.duracao_ciclo_2 if contrato else '',
                        'Duração Ciclo 3': contrato.duracao_ciclo_3 if contrato else '',
                        'Duração Ciclo 4': contrato.duracao_ciclo_4 if contrato else '',
                        'Duração Ciclo 5': contrato.duracao_ciclo_5 if contrato else '',
                        'Jornada Iniciada': cliente.jornada_iniciada.strftime('%d/%m/%Y') if cliente.jornada_iniciada else '',
                        'LTV': cliente.ltv_meses,
                        'LTV $': f"R$ {cliente.ltv_valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if cliente.ltv_valor else '',
                        'DATA ATUAL': cliente.data_atual.strftime('%d/%m/%Y') if cliente.data_atual else ''
                    }
                    export_data.append(row)
            
            # Criar DataFrame e salvar
            df = pd.DataFrame(export_data)
            filename = f"clientes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = f"temp/{filename}"
            
            # Criar diretório se não existir
            import os
            os.makedirs("temp", exist_ok=True)
            
            df.to_excel(filepath, index=False)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Erro no export: {e}")
            raise e

# Instância global do serviço
import_export_service = ImportExportService()
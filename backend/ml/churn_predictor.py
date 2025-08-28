# A importação correta para a biblioteca imbalanced-learn é 'imblearn'
from imblearn.over_sampling import SMOTE

# Corrigindo para importações absolutas a partir da raiz do projeto (backend)
from backend.core.utils import load_model, save_model
from backend.core.database import get_db

from sqlalchemy.orm import Session
from fastapi import Depends
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
import logging

logger = logging.getLogger(__name__)

class ChurnMLService:
    """Serviço de Machine Learning para previsão de churn."""

    def __init__(self, db: Session = Depends(get_db)):
        """
        Inicializa o serviço, carregando o modelo e o scaler.
        """
        self.db = db
        self.model_path = "models/churn_model.joblib"
        self.scaler_path = "models/churn_scaler.joblib"
        self.model = load_model(self.model_path)
        self.scaler = load_model(self.scaler_path)
        if self.model is None or self.scaler is None:
            logger.warning("Modelo ou scaler não encontrado. Treinamento é necessário.")

    def train_model(self) -> dict:
        """
        Treina um modelo de previsão de churn com os dados do banco de dados.

        Retorna:
            dict: Um dicionário com a acurácia do modelo e a matriz de confusão.
        """
        logger.info("Iniciando o processo de treinamento do modelo de churn...")
        try:
            # Carregar dados do banco de dados
            query = "SELECT * FROM clientes_hub"  # Substitua pelo nome real da sua tabela
            df = pd.read_sql(query, self.db.bind)
            logger.info(f"{len(df)} registros carregados do banco de dados.")

            # Pré-processamento simples
            # (Esta parte deve ser adaptada à sua estrutura de dados real)
            df = self._preprocess_data(df)

            # Definir features (X) e target (y)
            features = ['feature1', 'feature2', '...'] # Adapte para suas colunas
            target = 'churn' # Adapte para sua coluna alvo
            
            X = df[features]
            y = df[target]

            # Divisão em treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            # Balanceamento de classes com SMOTE
            logger.info("Aplicando SMOTE para balanceamento de classes...")
            smote = SMOTE(random_state=42)
            X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

            # Padronização das features
            logger.info("Padronizando as features...")
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train_res)
            X_test_scaled = self.scaler.transform(X_test)

            # Treinamento do modelo (Regressão Logística como exemplo)
            logger.info("Treinando o modelo de Regressão Logística...")
            self.model = LogisticRegression(random_state=42, class_weight='balanced')
            self.model.fit(X_train_scaled, y_train_res)

            # Avaliação
            logger.info("Avaliando o modelo...")
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            cm = confusion_matrix(y_test, y_pred)

            logger.info(f"Acurácia do modelo: {accuracy:.4f}")

            # Salvar modelo e scaler
            logger.info("Salvando o modelo e o scaler...")
            save_model(self.model, self.model_path)
            save_model(self.scaler, self.scaler_path)

            return {
                "message": "Treinamento concluído com sucesso!",
                "accuracy": accuracy,
                "confusion_matrix": cm.tolist(),
            }

        except Exception as e:
            logger.error(f"Erro durante o treinamento do modelo: {e}", exc_info=True)
            raise

    def predict(self, input_data: pd.DataFrame) -> np.ndarray:
        """
        Realiza a previsão de churn para novos dados.

        Args:
            input_data (pd.DataFrame): DataFrame com os dados de entrada para previsão.

        Returns:
            np.ndarray: Array com as previsões (0 ou 1).
        """
        if self.model is None or self.scaler is None:
            raise RuntimeError("Modelo não treinado. Execute o treinamento primeiro.")
        
        logger.info(f"Realizando previsão para {len(input_data)} registros.")
        
        try:
            # Pré-processamento dos dados de entrada
            # (Deve ser consistente com o treinamento)
            processed_data = self._preprocess_data(input_data)
            
            # Padronização
            scaled_data = self.scaler.transform(processed_data)

            # Previsão
            predictions = self.model.predict(scaled_data)
            return predictions

        except Exception as e:
            logger.error(f"Erro durante a previsão: {e}", exc_info=True)
            raise

    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Função de pré-processamento de dados.
        Esta é uma função placeholder e deve ser implementada com a lógica real.
        """
        logger.debug("Iniciando pré-processamento...")
        # Exemplo: Converter colunas categóricas em numéricas, tratar valores ausentes, etc.
        # df['categorical_column'] = df['categorical_column'].astype('category').cat.codes
        # df = df.fillna(0)
        # Por enquanto, apenas retorna o dataframe como está, supondo que os dados já estão prontos.
        logger.warning("A função `_preprocess_data` é um placeholder. Implemente a lógica real.")
        # Supondo que as features necessárias já existem no df
        # Esta parte precisa ser robusta para garantir que todas as colunas usadas no treino existam
        return df

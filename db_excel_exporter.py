# db_excel_exporter.py

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import pandas as pd
from typing import Optional, Union, List, Dict, Any
from contextlib import contextmanager
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLExporter:
    """
    Biblioteca para executar queries PostgreSQL e exportar resultados para Excel.

    Exemplo de uso:
        exporter = PostgreSQLExporter(
            host='localhost',
            database='meu_db',
            user='usuario',
            password='senha'
        )

        # Executar query e retornar DataFrame
        df = exporter.execute_query("SELECT * FROM pacientes")

        # Exportar diretamente para Excel
        exporter.query_to_excel(
            "SELECT * FROM pacientes WHERE idade > 18",
            "pacientes_maiores.xlsx"
        )
    """

    def __init__(
            self,
            host: str,
            database: str,
            user: str,
            password: str,
            port: int = 5432,
            min_conn: int = 1,
            max_conn: int = 10
    ):
        """
        Inicializa a conexão com PostgreSQL usando pool de conexões.

        Args:
            host: Endereço do servidor PostgreSQL
            database: Nome do banco de dados
            user: Usuário do banco
            password: Senha do usuário
            port: Porta do PostgreSQL (padrão: 5432)
            min_conn: Mínimo de conexões no pool
            max_conn: Máximo de conexões no pool
        """
        self.connection_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }

        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                min_conn,
                max_conn,
                **self.connection_params
            )
            logger.info(f"Pool de conexões criado com sucesso para {database}@{host}")
        except Exception as e:
            logger.error(f"Erro ao criar pool de conexões: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager para obter conexão do pool."""
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)

    def execute_query(
            self,
            query: str,
            params: Optional[tuple] = None,
            as_dict: bool = True
    ) -> pd.DataFrame:
        """
        Executa uma query SELECT e retorna os resultados em DataFrame.

        Args:
            query: Query SQL a ser executada
            params: Parâmetros para query parametrizada (opcional)
            as_dict: Se True, usa DictCursor para colunas nomeadas

        Returns:
            DataFrame do pandas com os resultados
        """
        try:
            with self.get_connection() as conn:
                cursor_factory = RealDictCursor if as_dict else None

                with conn.cursor(cursor_factory=cursor_factory) as cursor:
                    logger.info(f"Executando query: {query[:100]}...")
                    cursor.execute(query, params)

                    # Buscar resultados
                    results = cursor.fetchall()

                    # Obter nomes das colunas
                    if as_dict:
                        columns = results[0].keys() if results else []
                        data = [dict(row) for row in results]
                    else:
                        columns = [desc[0] for desc in cursor.description]
                        data = results

                    # Criar DataFrame
                    df = pd.DataFrame(data, columns=columns)
                    logger.info(f"Query executada com sucesso. Linhas retornadas: {len(df)}")

                    return df

        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            raise

    def query_to_excel(
            self,
            query: str,
            output_file: str,
            params: Optional[tuple] = None,
            sheet_name: str = 'Dados',
            include_index: bool = False,
            auto_adjust_columns: bool = True,
            freeze_header: bool = True
    ) -> str:
        """
        Executa query e salva resultado diretamente em arquivo Excel.

        Args:
            query: Query SQL a ser executada
            output_file: Caminho do arquivo Excel de saída
            params: Parâmetros para query parametrizada
            sheet_name: Nome da aba do Excel
            include_index: Incluir índice do DataFrame no Excel
            auto_adjust_columns: Ajustar largura das colunas automaticamente
            freeze_header: Congelar primeira linha (cabeçalho)

        Returns:
            Caminho do arquivo gerado
        """
        try:
            # Executar query
            df = self.execute_query(query, params)

            # Salvar em Excel
            return self.dataframe_to_excel(
                df,
                output_file,
                sheet_name,
                include_index,
                auto_adjust_columns,
                freeze_header
            )

        except Exception as e:
            logger.error(f"Erro ao exportar para Excel: {e}")
            raise

    def dataframe_to_excel(
            self,
            df: pd.DataFrame,
            output_file: str,
            sheet_name: str = 'Dados',
            include_index: bool = False,
            auto_adjust_columns: bool = True,
            freeze_header: bool = True
    ) -> str:
        """
        Salva DataFrame em arquivo Excel com formatação.

        Args:
            df: DataFrame a ser salvo
            output_file: Caminho do arquivo de saída
            sheet_name: Nome da aba
            include_index: Incluir índice
            auto_adjust_columns: Ajustar largura das colunas
            freeze_header: Congelar cabeçalho

        Returns:
            Caminho do arquivo gerado
        """
        try:
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=include_index
                )

                workbook = writer.book
                worksheet = writer.sheets[sheet_name]

                # Formato para cabeçalho
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4472C4',
                    'font_color': 'white',
                    'border': 1
                })

                # Aplicar formato ao cabeçalho
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num + (1 if include_index else 0), value, header_format)

                # Ajustar largura das colunas
                if auto_adjust_columns:
                    for i, col in enumerate(df.columns):
                        col_idx = i + (1 if include_index else 0)
                        max_length = max(
                            df[col].astype(str).apply(len).max(),
                            len(str(col))
                        )
                        worksheet.set_column(col_idx, col_idx, min(max_length + 2, 50))

                # Congelar primeira linha
                if freeze_header:
                    worksheet.freeze_panes(1, 0)

            logger.info(f"Arquivo Excel criado com sucesso: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Erro ao criar arquivo Excel: {e}")
            raise

    def multiple_queries_to_excel(
            self,
            queries: Dict[str, str],
            output_file: str,
            params: Optional[Dict[str, tuple]] = None
    ) -> str:
        """
        Executa múltiplas queries e salva cada uma em uma aba diferente do Excel.

        Args:
            queries: Dicionário {nome_aba: query_sql}
            output_file: Caminho do arquivo Excel
            params: Dicionário opcional {nome_aba: parametros}

        Returns:
            Caminho do arquivo gerado
        """
        try:
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                for sheet_name, query in queries.items():
                    query_params = params.get(sheet_name) if params else None
                    df = self.execute_query(query, query_params)

                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                    # Formatação básica
                    worksheet = writer.sheets[sheet_name]
                    header_format = writer.book.add_format({
                        'bold': True,
                        'bg_color': '#4472C4',
                        'font_color': 'white'
                    })

                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)

            logger.info(f"Arquivo Excel com múltiplas abas criado: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Erro ao criar Excel com múltiplas abas: {e}")
            raise

    def close(self):
        """Fecha todas as conexões do pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Pool de conexões fechado")


# Função auxiliar para uso rápido
def quick_export(
        query: str,
        output_file: str,
        host: str,
        database: str,
        user: str,
        password: str,
        port: int = 5432
) -> str:
    """
    Função de conveniência para exportação rápida sem criar instância.

    Args:
        query: Query SQL
        output_file: Arquivo Excel de saída
        host, database, user, password, port: Credenciais PostgreSQL

    Returns:
        Caminho do arquivo gerado
    """
    exporter = PostgreSQLExporter(host, database, user, password, port)
    try:
        return exporter.query_to_excel(query, output_file)
    finally:
        exporter.close()

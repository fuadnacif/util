# exemplo_uso.py

from db_excel_exporter import PostgreSQLExporter, quick_export


# ========== EXEMPLO 1: Uso básico ==========
def exemplo_basico():
    exporter = PostgreSQLExporter(
        host='localhost',
        database='dicom',
        user='postgres',
        password='sua_senha'
    )

    try:
        # Executar query simples
        df = exporter.execute_query("SELECT * FROM pacientes LIMIT 100")
        print(f"Dados carregados: {len(df)} linhas")
        print(df.head())

        # Exportar para Excel
        exporter.query_to_excel(
            "SELECT * FROM pacientes",
            "pacientes.xlsx"
        )

    finally:
        exporter.close()


# ========== EXEMPLO 2: Query parametrizada ==========
def exemplo_parametrizado():
    exporter = PostgreSQLExporter(
        host='localhost',
        database='dicom',
        user='postgres',
        password='sua_senha'
    )

    try:
        query = """
            SELECT 
                patient_id,
                patient_name,
                study_date,
                modality
            FROM dicom_studies
            WHERE study_date BETWEEN %s AND %s
                AND modality = %s
        """

        exporter.query_to_excel(
            query,
            "estudos_ct_janeiro.xlsx",
            params=('2025-01-01', '2025-01-31', 'CT'),
            sheet_name='Estudos CT'
        )

    finally:
        exporter.close()


# ========== EXEMPLO 3: Múltiplas abas ==========
def exemplo_multiplas_abas():
    exporter = PostgreSQLExporter(
        host='localhost',
        database='dicom',
        user='postgres',
        password='sua_senha'
    )

    try:
        queries = {
            'Pacientes': "SELECT * FROM pacientes",
            'Estudos': "SELECT * FROM dicom_studies",
            'Séries': "SELECT * FROM dicom_series",
            'Estatísticas': """
                SELECT 
                    modality,
                    COUNT(*) as total_estudos,
                    COUNT(DISTINCT patient_id) as total_pacientes
                FROM dicom_studies
                GROUP BY modality
            """
        }

        exporter.multiple_queries_to_excel(
            queries,
            "relatorio_completo.xlsx"
        )

    finally:
        exporter.close()


# ========== EXEMPLO 4: Exportação rápida ==========
def exemplo_rapido():
    quick_export(
        query="SELECT * FROM pacientes WHERE idade > 18",
        output_file="pacientes_maiores.xlsx",
        host='localhost',
        database='dicom',
        user='postgres',
        password='sua_senha'
    )


if __name__ == '__main__':
    # Executar exemplos
    exemplo_basico()
    # exemplo_parametrizado()
    # exemplo_multiplas_abas()
    # exemplo_rapido()

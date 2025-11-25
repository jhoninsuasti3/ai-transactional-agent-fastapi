#!/usr/bin/env python3
"""Script simple para probar conexión con psycopg (sync driver)."""

import sys

try:
    import psycopg
except ImportError:
    print("❌ psycopg no está instalado")
    print("Ejecuta: uv pip install psycopg[binary]")
    sys.exit(1)

def test_connection():
    """Prueba conexión con psycopg (sync)."""
    print("=" * 60)
    print("🔍 Probando conexión a PostgreSQL con psycopg")
    print("=" * 60)

    conn_string = "postgresql://postgres:postgres@localhost:5432/transactional_agent"
    print(f"Connection string: {conn_string}\n")

    try:
        print("⏳ Conectando...")
        with psycopg.connect(conn_string) as conn:
            print("✅ Conexión exitosa!\n")

            # Test query
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                print(f"📊 Versión: {version.split(',')[0]}\n")

                # List tables
                cur.execute("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY tablename;
                """)
                tables = cur.fetchall()
                print(f"📋 Tablas encontradas ({len(tables)}):")
                for table in tables:
                    cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cur.fetchone()[0]
                    print(f"  • {table[0]:20s} ({count} registros)")

        print("\n" + "=" * 60)
        print("✅ Prueba completada exitosamente")
        print("=" * 60)

    except psycopg.OperationalError as e:
        print(f"\n❌ Error de conexión: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {type(e).__name__}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
